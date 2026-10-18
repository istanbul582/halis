#!/usr/bin/env bash
set -euo pipefail
TOOLS_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
python3 -m venv "$TOOLS_DIR/.venv"
"$TOOLS_DIR/.venv/bin/python" -m pip install --no-cache-dir --disable-pip-version-check -r "$TOOLS_DIR/requirements.lock.txt"
"$TOOLS_DIR/.venv/bin/python" -m pip --no-cache-dir check
printf '%s\n' 'Hazır. Komutlar ve veri sınırları için README_TR.md dosyasını okuyun.'
