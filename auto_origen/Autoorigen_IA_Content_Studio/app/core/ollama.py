import requests

def available(base_url="http://127.0.0.1:11434"):
    try:
        r = requests.get(base_url.rstrip("/") + "/api/tags", timeout=2)
        return r.ok
    except Exception:
        return False

def generate(prompt, model="qwen2.5:7b", base_url="http://127.0.0.1:11434"):
    r = requests.post(
        base_url.rstrip("/") + "/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    return r.json().get("response", "")
