#!/bin/bash

# Run Python backend with uv env activation
# Usage: ./run.sh [PORT]
# Default port: 5003

set -e

VENV_DIR=".venv"
DEFAULT_PORT=5003

# Get port from command line argument or use default
PORT=${1:-$DEFAULT_PORT}

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please run setup_venv.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "The app will use default/environment variables"
    echo "To create .env file:"
    echo "  cp env.example .env"
    echo "  nano .env  # Edit with your credentials"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Set PORT environment variable
export PORT=$PORT

# Run the Flask app
echo "🚀 Starting Flask server on port $PORT..."
cd backend
python app.py
