#!/usr/bin/env bash
# Run cad-server directly with a local Python venv -- no Docker required.
# This is entirely original code (not the Svetlana-DAO-LLC/cad-agent
# project), so you can run it the same way you'd run any other local
# dev server you trust: reviewed once, then started yourself.
#
# Usage:
#   chmod +x run_local.sh
#   ./run_local.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "Starting cad-server on http://127.0.0.1:8123 (Ctrl+C to stop)"
python3 server.py
