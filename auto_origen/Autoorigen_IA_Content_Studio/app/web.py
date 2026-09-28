from pathlib import Path
import os
from flask import Flask, request, render_template_string, send_from_directory
from .core.transcriber import AutoorigenTranscriber, save_outputs
from .core.content import save_content
from .core.ollama import available, generate

BASE = Path(__file__).resolve().parent.parent
INPUT = BASE / "input"
OUTPUT = BASE / "output"
INPUT.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

app = Flask(__name__)

HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Autoorigen IA</title>
<style>
body{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px;background:#111;color:#eee}
.card{background:#1d1d1d;padding:24px;border-radius:16px;margin-bottom:20px}
input,select,button{padding:12px;margin:6px 0;border-radius:8px}
button{cursor:pointer}.result{white-space:pre-wrap;background:#080808;padding:18px;border-radius:10px}
a{color:#8ab4ff}
</style></head>
<body>
<h1>AUTOORIGEN IA</h1>
<p>Video → transcripción → contenido.</p>
<div class="card">
<form method="post" enctype="multipart/form-data">
<input type="file" name="media" required><br>
<label>Modelo:</label>
<select name="model"><option>small</option><option>base</option><option>medium</option></select><br>
<button type="submit">Procesar</button>
</form></div>
{% if result %}
<div class="card"><h2>Resultado</h2><div class="result">{{result}}</div></div>
{% endif %}
</body></html>"""

@app.route("/", methods=["GET","POST"])
def index():
    result = None
    if request.method == "POST":
        f = request.files.get("media")
        if not f or not f.filename:
            result = "No se seleccionó archivo."
        else:
            safe = Path(f.filename).name
            path = INPUT / safe
            f.save(path)
            model = request.form.get("model","small")
            engine = AutoorigenTranscriber(model, "cpu", "int8")
            data = engine.transcribe(path, "es")
            paths = save_outputs(data, OUTPUT, path.stem)
            transcript = "\n".join(s["text"] for s in data["segments"])
            content = save_content(transcript, safe, OUTPUT)
            result = "Archivos creados:\\n" + "\\n".join(paths.values()) + f"\\n{content}"
    return render_template_string(HTML, result=result)

@app.route("/files/<path:name>")
def files(name):
    return send_from_directory(OUTPUT, name, as_attachment=True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=False)
