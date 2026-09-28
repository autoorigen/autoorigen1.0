# AUTOORIGEN IA — Content Studio

Herramienta local para convertir videos del taller en material de contenido.

## Flujo

VIDEO/AUDIO
→ extracción de audio con FFmpeg
→ transcripción local con faster-whisper
→ TXT + SRT + VTT + JSON
→ limpieza del texto
→ generación de piezas para Autoorigen
→ opcionalmente Ollama para resumen/guion/ideas
→ opcionalmente TTS en una fase posterior.

## Importante

Este paquete NO contiene los pesos de los modelos de IA ni los entornos virtuales del computador original.
Los modelos pueden ocupar cientos de MB o varios GB y se descargan en el primer uso.

La instalación está diseñada para Linux x86_64 y Python 3.10+.
Tu instalación original estaba en `~/IA` y utilizaba FFmpeg, Python, faster-whisper y posteriormente MeloTTS/OpenVoice.

## Instalación rápida

```bash
cd Autoorigen_IA_Content_Studio
chmod +x scripts/install.sh scripts/run.sh
./scripts/install.sh
./scripts/run.sh
```

Luego abre:

http://127.0.0.1:7860

## Modo terminal

```bash
source .venv/bin/activate
python -m app.cli video.mp4 --model small
```

También puedes usar:

```bash
python -m app.cli video.mp4 --model medium
```

`small` suele ser un buen punto de partida en CPU. En equipos con GPU compatible puede configurarse CUDA.

## Ollama

Si Ollama está instalado, puedes activar generación de contenido local:

```bash
export AUTOORIGEN_OLLAMA_MODEL=qwen2.5:7b
```

El sistema detecta Ollama automáticamente.

## Estructura

- `app/` código de la aplicación
- `config/` configuración
- `input/` videos de entrada
- `output/` resultados
- `models/` caché/modelos
- `scripts/` instalación y ejecución
- `docs/` documentación

## Próximas fases

1. Transcripción robusta.
2. Identificación automática de vehículo, falla, reparación y piezas.
3. Guiones para Reels/TikTok/Shorts.
4. Títulos, descripciones y hashtags.
5. Subtítulos automáticos.
6. Integración con Ollama.
7. Generación de voz.
8. Integración con el ecosistema web/app de Autoorigen.
