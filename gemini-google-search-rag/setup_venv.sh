#!/bin/bash

# Setup Python virtual environment with uv (idempotent)
# Assumes uv is already installed
# Default env directory is .venv

set -e

VENV_DIR=".venv"

echo "🔧 Setting up Python virtual environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Please install uv first: https://docs.astral.sh/uv/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    uv venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists"
fi

# Install/update dependencies
echo "📥 Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create one from the sample file:"
    echo "  cp env.example .env"
    echo "  nano .env  # Edit with your credentials"
    echo ""
fi

echo "To activate the virtual environment:"
echo "  source $VENV_DIR/bin/activate"
