#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate
python - <<'PY'
from faster_whisper import WhisperModel
print("OK: faster-whisper importado")
try:
    import flask
    print("OK: Flask")
except Exception as e:
    print("ERROR Flask:", e)
PY
ffmpeg -version | head -n 1
