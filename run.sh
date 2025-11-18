#!/bin/bash

# Run Python backend with uv env activation

set -e

VENV_DIR=".venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please run setup_venv.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Run the Flask app
echo "🚀 Starting Flask server..."
cd backend
python app.py

