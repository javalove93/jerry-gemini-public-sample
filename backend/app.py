# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Simple example: Google Search + Embedding Similarity + Gemini
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from googleapiclient.discovery import build
import numpy as np

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "")

# Initialize Gemini client
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# For API Key mode (if no GCP project):
# client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def google_search(query, api_key, engine_id, num_results=5):
    """
    Perform Google Custom Search.

    Args:
        query: Search query string
        api_key: Google API key
        engine_id: Custom Search Engine ID
        num_results: Number of results to return

    Returns:
        List of search results with title, link, and snippet
    """
    service = build("customsearch", "v1", developerKey=api_key)
    result = service.cse().list(q=query, cx=engine_id, num=num_results).execute()

    search_results = []
    if "items" in result:
        for item in result["items"]:
            search_results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

    return search_results


def get_embedding(text, model="text-embedding-005"):
    """Get text embedding using Gemini."""
    try:
        response = client.models.embed_content(
            model=model,
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def filter_results_by_similarity(question, search_results, threshold=0.3):
    """
    Filter search results by embedding similarity to question.

    Args:
        question: User's question
        search_results: List of search results
        threshold: Minimum similarity score (0-1)

    Returns:
        Filtered list of relevant results
    """
    question_embedding = get_embedding(question)
    if question_embedding is None:
        return search_results  # Return all if embedding fails

    filtered_results = []

    for result in search_results:
        # Combine title and snippet for better matching
        result_text = f"{result['title']} {result['snippet']}"
        result_embedding = get_embedding(result_text)

        if result_embedding is None:
            continue

        similarity = cosine_similarity(question_embedding, result_embedding)
        result['similarity_score'] = float(similarity)

        if similarity >= threshold:
            filtered_results.append(result)

    # Sort by similarity score (highest first)
    filtered_results.sort(key=lambda x: x['similarity_score'], reverse=True)

    return filtered_results


def ask_gemini_with_context(question, curated_results):
    """
    Ask Gemini with curated search results as context.

    Args:
        question: User's question
        curated_results: Filtered search results

    Returns:
        Gemini's answer
    """
    # Build context from search results
    context = "다음은 관련 검색 결과입니다:\n\n"
    for idx, result in enumerate(curated_results, 1):
        context += f"{idx}. {result['title']}\n"
        context += f"   출처: {result['link']}\n"
        context += f"   내용: {result['snippet']}\n"
        context += f"   관련도: {result['similarity_score']:.2f}\n\n"

    # Create prompt with context
    prompt = f"""{context}

위의 검색 결과를 바탕으로 다음 질문에 답변해주세요:

질문: {question}

답변 시 관련 출처를 [1], [2] 형식으로 인용해주세요."""

    # Call Gemini
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt
    )

    return response.text


@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/ask', methods=['POST'])
def ask():
    """
    Main API endpoint:
    1. Get question from frontend
    2. Search with Google Search API
    3. Check search result links with embedding similarity
    4. Ask Gemini with curated results
    """
    try:
        data = request.json
        question = data.get('question', '')

        if not question:
            return jsonify({'error': '질문이 필요합니다'}), 400

        # Check API credentials
        if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            return jsonify({
                'error': 'Google Search API 자격증명이 필요합니다. README를 참고하세요.',
                'answer': '(Google Search API 없이 테스트) 질문에 대한 답변을 위해서는 Google Custom Search API 키와 검색 엔진 ID가 필요합니다.',
                'sources': []
            }), 200

        # Step 1: Google Search
        print(f"[1/4] Searching Google for: {question}")
        search_results = google_search(
            question,
            GOOGLE_SEARCH_API_KEY,
            GOOGLE_SEARCH_ENGINE_ID,
            num_results=10
        )
        print(f"      Found {len(search_results)} results")

        # Step 2: Filter by embedding similarity
        print(f"[2/4] Filtering results by embedding similarity...")
        curated_results = filter_results_by_similarity(
            question,
            search_results,
            threshold=0.3
        )
        print(f"      Kept {len(curated_results)} relevant results")

        # Step 3: Ask Gemini with curated results
        print(f"[3/4] Asking Gemini with curated context...")
        answer = ask_gemini_with_context(question, curated_results)
        print(f"[4/4] Done!")

        return jsonify({
            'answer': answer,
            'sources': curated_results,
            'total_found': len(search_results),
            'filtered_count': len(curated_results)
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
