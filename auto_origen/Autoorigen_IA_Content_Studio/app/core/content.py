from pathlib import Path
import re

def clean_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    return text

def build_content(transcript, filename):
    text = clean_text(transcript)
    short = text[:700] + ("..." if len(text) > 700 else "")
    title_base = Path(filename).stem.replace("_", " ").replace("-", " ").strip()

    return f"""# AUTOORIGEN — Contenido generado

## Fuente
{filename}

## Transcripción limpia
{text}

## Título sugerido
¿Qué estaba pasando realmente con este vehículo?

## Hook para Reel
Este vehículo llegó al taller con un problema que no siempre es lo que parece.

## Guion corto
Hoy te mostramos un caso real de Autoorigen.
{short}

Primero entendemos el problema, después diagnosticamos y finalmente ejecutamos la reparación.
La idea no es cambiar piezas por cambiar: es encontrar la causa.

## Descripción
Caso real trabajado en Autoorigen. Documentamos el proceso para mostrar qué encontramos, cómo lo diagnosticamos y qué solución aplicamos.

## CTA
¿Tienes una falla similar? Escríbenos y cuéntanos qué está pasando con tu vehículo.

## Hashtags
#Autoorigen #Mecanica #DiagnosticoAutomotriz #Autos #TallerAutomotriz #MecanicaAutomotriz #Colombia
"""

def save_content(transcript, filename, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{Path(filename).stem}_contenido.md"
    out.write_text(build_content(transcript, filename), encoding="utf-8")
    return str(out)
