#!/usr/bin/env bash
# Setup script: install Python deps and copy .env
set -euo pipefail

echo "🔧 Setting up Entropy..."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ Created .env from .env.example – please fill in your secrets."
fi

pip install -e ".[dev]"
echo "✅ Python dependencies installed."

echo "🚀 Run 'make docker-up' to start infrastructure services."
echo "🚀 Run 'make dev' to start the backend."
