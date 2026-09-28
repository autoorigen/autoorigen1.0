#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "=== AUTOORIGEN IA — instalación ==="

if ! command -v python3 >/dev/null 2>&1; then
  echo "Falta Python 3. Instálalo con el gestor de paquetes de tu Linux."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "FFmpeg no está instalado."
  echo "En Ubuntu/Mint: sudo apt update && sudo apt install -y ffmpeg"
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt

echo
echo "Instalación terminada."
echo "El modelo de Whisper se descargará automáticamente al primer procesamiento."
echo "Ejecuta: ./scripts/run.sh"
