#!/usr/bin/env bash
# Bootstrap local development environment for ProductFlow.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> ProductFlow setup"

if [ ! -f "$ROOT_DIR/.env" ]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "Created .env from .env.example"
fi

echo "==> Backend virtual environment"
python -m venv "$ROOT_DIR/.venv"
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/backend/requirements.txt"

echo "==> Frontend dependencies"
cd "$ROOT_DIR/frontend"
npm install

echo ""
echo "Setup complete."
echo "  Backend:  source .venv/bin/activate && uvicorn app.main:app --reload --app-dir backend"
echo "  Frontend: cd frontend && npm run dev"
