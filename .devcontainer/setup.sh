#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-codespaces.txt
mkdir -p models .runtime
echo "Setup complete. Upload your trusted best-4.pt model into models/ to enable detection."
