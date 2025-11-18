# Google Search + Embedding Similarity + Gemini

간단한 개념 증명: Google 검색 결과를 임베딩 유사도로 필터링하여 Gemini에게 질문하는 예제

## 🎯 개념

이 예제는 다음 4단계를 보여줍니다:

1. **질문 입력**: 프론트엔드에서 사용자 질문 받기
2. **Google 검색**: Google Custom Search API로 검색
3. **임베딩 필터링**: 검색 결과와 질문의 임베딩 유사도 계산하여 관련성 높은 결과만 선택
4. **Gemini 답변**: 큐레이션된 검색 결과를 컨텍스트로 Gemini 2.0 Flash에 질문

## 📁 프로젝트 구조

```
JERRY_ADDED_SOURCE/
├── backend/
│   └── app.py              # Flask API 서버
├── frontend/
│   └── index.html          # 간단한 웹 UI
├── requirements.txt        # Python 의존성
├── setup_venv.sh          # 가상환경 설정 스크립트
├── run.sh                 # 실행 스크립트
├── env.example            # 환경 변수 샘플 파일
├── .gitignore             # Git 제외 파일 목록
└── README.md              # 이 파일
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# uv가 설치되어 있는지 확인
uv --version

# 가상환경 생성 및 패키지 설치
chmod +x setup_venv.sh
./setup_venv.sh
```

### 2. 환경 변수 설정

`.env` 파일을 생성하여 환경 변수를 설정합니다:

```bash
# 샘플 파일 복사
cp env.example .env

# .env 파일 편집
nano .env  # 또는 원하는 편집기 사용
```

#### `.env` 파일 설정 내용:

**Option 1: Vertex AI 사용 (권장)**
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
```

```bash
GEMINI_API_KEY=your-gemini-api-key
```

**Google Custom Search API 설정 (필수)**

Google Custom Search API를 사용하려면:

1. [Google Cloud Console](https://console.cloud.google.com/)에서 Custom Search API 활성화
2. API 키 생성
3. [Programmable Search Engine](https://programmablesearchengine.google.com/)에서 검색 엔진 생성
4. `.env` 파일에 추가:

```bash
GOOGLE_SEARCH_API_KEY=your-custom-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

**참고**: Google Custom Search API 없이도 코드는 실행되지만, 실제 검색 기능은 작동하지 않습니다.

### 3. 실행

```bash
chmod +x run.sh

# 기본 포트(5003)로 실행
./run.sh

# 또는 원하는 포트 지정
./run.sh 8080
```

서버가 시작되면 브라우저에서 접속:
```
http://localhost:5003
```

## 🔍 작동 방식

### Backend (Flask API)

```python
# Step 1: Google Search
search_results = google_search(question, api_key, engine_id)

# Step 2: Embedding Similarity Filtering
curated_results = filter_results_by_similarity(question, search_results)

# Step 3: Ask Gemini with Context
answer = ask_gemini_with_context(question, curated_results)
```

### 주요 함수

- **`google_search()`**: Google Custom Search API 호출
- **`get_embedding()`**: Gemini의 text-embedding-005 모델로 임베딩 생성
- **`filter_results_by_similarity()`**: 코사인 유사도로 검색 결과 필터링 (threshold: 0.3)
- **`ask_gemini_with_context()`**: 필터링된 결과를 컨텍스트로 Gemini에 질문

### Frontend (HTML)

간단한 단일 페이지 애플리케이션:
- 질문 입력 폼
- 4단계 프로세스 시각화
- 답변 및 출처 표시
- 각 출처의 관련도 점수 표시

## 📊 예제

**질문**: "2024년 파리 올림픽에서 한국은 몇 개의 금메달을 땄나요?"

**처리 과정**:
1. Google 검색으로 10개 결과 수집
2. 임베딩 유사도로 5개의 관련 결과 필터링 (similarity > 0.3)
3. Gemini에게 필터링된 결과와 함께 질문
4. 출처 인용이 포함된 답변 반환

## 🛠️ 기술 스택

- **Backend**: Flask, Google GenAI SDK
- **Frontend**: Pure HTML/CSS/JavaScript
- **AI Models**:
  - Gemini 2.0 Flash Exp (답변 생성)
  - text-embedding-005 (임베딩)
- **API**: Google Custom Search API

## 📝 주의사항

1. Google Custom Search API는 **무료 할당량이 하루 100회**입니다
2. 임베딩 API 호출이 많아 비용이 발생할 수 있습니다
3. 실제 프로덕션에서는 캐싱과 배치 처리를 고려하세요
4. 임베딩 유사도 threshold(0.3)는 사용 사례에 맞게 조정하세요

## 🔗 참고 자료

- [Gemini API 문서](https://ai.google.dev/gemini-api/docs)
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- [Vertex AI Embeddings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)

## 📄 라이선스

Apache License 2.0
