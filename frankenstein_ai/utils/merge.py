import os
import re
import requests
from typing import List, Dict, Any

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

def safe_filename(name: str) -> str:
    """Make a safe filename (alphanumeric + _-)"""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)[:50]

def save_image_from_url(url: str, filename: str) -> str:
    """Download and save image from URL into /images folder"""
    try:
        path = os.path.join(IMAGES_DIR, filename)
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    except Exception as e:
        print(f"⚠️ Failed to save image {url}: {e}")
        return url  # fallback: return URL if download fails

def merge_outputs(prompt: str, recalls: List[dict], results: List[dict]) -> Dict[str, Any]:
    text_parts = []
    sources = []
    artifacts = {}
    image_lines = []

    # Memory recalls
    if recalls:
        recall_txt = "\n".join(
            [f"Q: {r.get('prompt','')[:80]}\nA: {r.get('response','')[:120]}" for r in recalls if isinstance(r, dict)]
        )
        if recall_txt:
            text_parts.append(f"--- Memory Recalls ---\n{recall_txt}")

    # Process each result
    for idx, r in enumerate(results):
        if not isinstance(r, dict):
            r = {"kind": "text", "result": {"text": str(r)}}

        kind = r.get("kind")
        res = r.get("result", {})

        if isinstance(res, str):
            res = {"text": res}
        elif not isinstance(res, dict):
            res = {"text": str(res)}

        if kind == "text":
            text_parts.append(res.get("text", ""))

        elif kind == "code":
            text_parts.append("Code suggestion:\n" + res.get("text", ""))

        elif kind == "image":
            caption = res.get("prompt", f"image_{idx}")
            url = res.get("url")
            path = res.get("path")

            if url:
                filename = f"{safe_filename(caption)}_{idx}.png"
                saved_path = save_image_from_url(url, filename)
                artifacts.setdefault("images", []).append(saved_path)
                image_lines.append(f"- [{caption}] -> {saved_path}")
            elif path:
                artifacts.setdefault("images", []).append(path)
                image_lines.append(f"- [{caption}] -> {path}")

            text_parts.append(res.get("text", "(image)"))

        elif kind == "image_captions" and isinstance(res, list):
            for j, img in enumerate(res):
                if isinstance(img, dict):
                    caption = img.get("caption", f"image_{idx}_{j}")
                    url = img.get("url")
                    path = img.get("path")
                    if url:
                        filename = f"{safe_filename(caption)}_{idx}_{j}.png"
                        saved_path = save_image_from_url(url, filename)
                        artifacts.setdefault("images", []).append(saved_path)
                        image_lines.append(f"- [{caption}] -> {saved_path}")
                    elif path:
                        artifacts.setdefault("images", []).append(path)
                        image_lines.append(f"- [{caption}] -> {path}")

        elif kind == "search":
            if res.get("text"):
                text_parts.append("Search results:\n" + res["text"])
            if res.get("abstract"):
                text_parts.append("Search summary:\n" + res["abstract"])

        sources.append(res.get("provider", "unknown"))

    # Add images section
    if image_lines:
        text_parts.append("--- Images ---\n" + "\n".join(image_lines))

    return {
        "text": "\n\n".join([t for t in text_parts if t]),
        "artifacts": artifacts,
        "sources": list(dict.fromkeys(sources)),  # unique sources
    }
