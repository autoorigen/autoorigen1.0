# Arquitectura — Autoorigen IA

## Objetivo

Crear una estación local de producción de contenido a partir del trabajo real del taller.

### Entrada

- MP4
- MOV
- MKV
- AVI
- WAV
- MP3
- M4A

### Procesamiento

1. Validar archivo.
2. Extraer audio si es video.
3. Transcribir con faster-whisper.
4. Conservar segmentos y timestamps.
5. Crear TXT, SRT, VTT y JSON.
6. Limpiar errores básicos de formato.
7. Preparar contexto para IA generativa.
8. Crear contenido específico de Autoorigen.

### Salidas

- `transcripcion.txt`
- `subtitulos.srt`
- `subtitulos.vtt`
- `transcripcion.json`
- `contenido.md`
- guion corto
- descripción
- títulos
- ideas de publicación
- hashtags

## Filosofía

El sistema debe partir del material real del taller.

Ejemplo:

Diagnóstico real
→ explicación técnica
→ historia del vehículo
→ reparación
→ antes/después
→ publicación.

## Separación de componentes

`core/transcriber.py`
- transcripción.

`core/content.py`
- generación estructurada sin depender de Internet.

`core/ollama.py`
- integración opcional con un modelo local.

`web.py`
- interfaz web local.

`cli.py`
- interfaz por terminal.

## Evolución prevista

### V1
Transcripción.

### V2
Content Studio.

### V3
Clasificación automática del material.

### V4
Generación de guiones y publicaciones mediante Ollama.

### V5
TTS / voz.

### V6
Integración con Autoorigen Web/App.

### V7
Base de datos de vehículos, trabajos, clientes y contenido.
