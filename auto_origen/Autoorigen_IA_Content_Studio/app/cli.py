import argparse
from pathlib import Path
from .core.transcriber import AutoorigenTranscriber, save_outputs
from .core.content import save_content
from .core.ollama import available, generate

def main():
    p = argparse.ArgumentParser(description="Autoorigen IA — transcripción y contenido")
    p.add_argument("media")
    p.add_argument("--model", default="small")
    p.add_argument("--language", default="es")
    p.add_argument("--device", default="cpu")
    p.add_argument("--compute-type", default="int8")
    p.add_argument("--output", default="output")
    p.add_argument("--ollama", action="store_true")
    p.add_argument("--ollama-model", default="qwen2.5:7b")
    args = p.parse_args()

    media = Path(args.media)
    if not media.exists():
        raise SystemExit(f"No existe: {media}")

    print(f"Transcribiendo: {media}")
    engine = AutoorigenTranscriber(args.model, args.device, args.compute_type)
    data = engine.transcribe(media, args.language)

    paths = save_outputs(data, args.output, media.stem)
    text = "\n".join(s["text"] for s in data["segments"])
    content_path = save_content(text, media.name, args.output)

    print("\nArchivos creados:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print(f"  contenido: {content_path}")

    if args.ollama and available():
        prompt = f"""Eres el asistente de contenido de Autoorigen, un taller automotriz.
Analiza esta transcripción y crea:
1. resumen
2. 5 hooks
3. guion de Reel de 45-60 segundos
4. título para YouTube
5. descripción
6. CTA
7. 10 hashtags.
No inventes reparaciones, piezas, vehículos o datos que no estén presentes.

TRANSCRIPCIÓN:
{text}"""
        generated = generate(prompt, args.ollama_model)
        out = Path(args.output) / f"{media.stem}_ollama.md"
        out.write_text(generated, encoding="utf-8")
        print(f"  ollama: {out}")

if __name__ == "__main__":
    main()
