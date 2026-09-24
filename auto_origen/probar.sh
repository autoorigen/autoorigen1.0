#!/usr/bin/env bash
# =========================================================
# AUTOORIGEN — Probar la web en la red local
# Uso:  bash probar.sh
# Detener el servidor: Ctrl + C
# =========================================================
set -e
cd "$(dirname "$0")"

# 1. Crear el entorno virtual (solo la primera vez)
if [ ! -d venv ]; then
  echo "▶ Creando entorno virtual (venv)..."
  python3 -m venv venv
fi

# 2. Activarlo e instalar Flask
source venv/bin/activate
echo "▶ Instalando dependencias..."
pip install -q -r requirements.txt

# 3. Mostrar las direcciones para entrar
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "================================================="
echo "  AUTOORIGEN corriendo"
echo "  En esta torre:        http://localhost:5000"
echo "  Desde otro equipo:    http://$IP:5000"
echo "  Para detener:         Ctrl + C"
echo "================================================="
echo ""

# 4. Arrancar el servidor (Flask + Socket.IO) escuchando en toda la red local
python app.py
