#!/usr/bin/env bash
# =========================================================
# AUTOORIGEN — Subir el proyecto a GitHub
# Uso:  bash subir-github.sh
# Cuando pida "Password", pega el TOKEN (ghp_...), no tu contraseña.
# =========================================================
set -e
cd "$(dirname "$0")"
REPO_URL="${REPO_URL:-https://github.com/autoorigen/autoorigen.git}"

# 1. Identidad para los commits (solo se pregunta la primera vez)
if [ -z "$(git config --global user.name)" ]; then
  read -rp "Tu nombre para GitHub: " NOMBRE
  git config --global user.name "$NOMBRE"
fi
if [ -z "$(git config --global user.email)" ]; then
  read -rp "Tu correo de GitHub: " CORREO
  git config --global user.email "$CORREO"
fi

# 2. Iniciar el repositorio local (solo la primera vez)
if [ ! -d .git ]; then
  echo "▶ Iniciando repositorio git..."
  git init -q -b main
fi

# 3. Conectar con GitHub (solo la primera vez)
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$REPO_URL"
fi

# 4. Guardar los cambios en un commit
git add .
if git diff --cached --quiet; then
  echo "▶ No hay cambios nuevos para guardar."
else
  git commit -q -m "Autoorigen V1.1: preloader, animaciones, docs y estructura del repo"
  echo "▶ Cambios guardados en un commit."
fi

# 5. Subir a GitHub
echo "▶ Subiendo a $REPO_URL ..."
echo "  Username: tu usuario de GitHub"
echo "  Password: pega el TOKEN ghp_... (no se ve al pegarlo, es normal)"
if git push -u origin main; then
  echo ""
  echo "✅ Listo: el proyecto está en GitHub."
else
  echo ""
  echo "❌ GitHub rechazó la subida. Toma foto de este mensaje y mándala."
  echo "   (Lo más común: el repositorio ya tenía archivos, o el token no tiene permiso 'repo'.)"
  exit 1
fi
