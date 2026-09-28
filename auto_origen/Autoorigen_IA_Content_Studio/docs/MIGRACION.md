# Migración a otro equipo

## 1. Copiar este ZIP

Descomprime:

```bash
unzip Autoorigen_IA_Content_Studio.zip
cd Autoorigen_IA_Content_Studio
```

## 2. Instalar FFmpeg

Ubuntu / Linux Mint:

```bash
sudo apt update
sudo apt install -y ffmpeg python3 python3-venv
```

## 3. Instalar Autoorigen IA

```bash
chmod +x scripts/*.sh
./scripts/install.sh
```

## 4. Ejecutar

```bash
./scripts/run.sh
```

## 5. Primer modelo

El primer procesamiento descargará el modelo elegido de Whisper.

## 6. Recomendación para conservar la instalación

Después de validar el nuevo equipo puedes copiar la carpeta de modelos/cache del usuario si quieres evitar descargar nuevamente los modelos, pero la ruta exacta depende de cómo esté configurado Hugging Face/faster-whisper.

## Qué NO se incluye

No se incluyen:
- vídeos personales
- grabaciones
- pesos de modelos
- claves API
- contraseñas
- el entorno virtual binario del Linux original

Esto hace que el ZIP sea portable y mucho más pequeño.
