from pathlib import Path
import json
from faster_whisper import WhisperModel

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mp3", ".wav", ".m4a", ".flac"}

class AutoorigenTranscriber:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, media_path, language="es"):
        segments, info = self.model.transcribe(
            str(media_path),
            language=language or None,
            vad_filter=True,
            beam_size=5
        )
        result = []
        for s in segments:
            result.append({
                "start": round(float(s.start), 3),
                "end": round(float(s.end), 3),
                "text": s.text.strip()
            })
        return {
            "language": info.language,
            "language_probability": float(info.language_probability),
            "duration": float(info.duration),
            "segments": result
        }

def format_timestamp(seconds, comma=False):
    ms = int(round((seconds - int(seconds))*1000))
    total = int(seconds)
    h, total = divmod(total, 3600)
    m, s = divmod(total, 60)
    sep = "," if comma else "."
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"

def save_outputs(data, output_dir, stem):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt = "\n".join(s["text"] for s in data["segments"])
    (output_dir/f"{stem}.txt").write_text(txt + "\n", encoding="utf-8")

    srt = []
    vtt = ["WEBVTT", ""]
    for i, s in enumerate(data["segments"], 1):
        srt.append(f"{i}\n{format_timestamp(s['start'], True)} --> {format_timestamp(s['end'], True)}\n{s['text']}\n")
        vtt.append(f"{format_timestamp(s['start'])} --> {format_timestamp(s['end'])}")
        vtt.append(s["text"])
        vtt.append("")
    (output_dir/f"{stem}.srt").write_text("\n".join(srt), encoding="utf-8")
    (output_dir/f"{stem}.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (output_dir/f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "txt": str(output_dir/f"{stem}.txt"),
        "srt": str(output_dir/f"{stem}.srt"),
        "vtt": str(output_dir/f"{stem}.vtt"),
        "json": str(output_dir/f"{stem}.json"),
    }
