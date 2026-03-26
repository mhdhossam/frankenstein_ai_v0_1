# router.py
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .boosters.gemini_text import gemini_text
from .boosters.hf_code import hf_generate_code
from .boosters.sd_image import hf_generate_image
from .search.duckduckgo import instant_answer
import json, hashlib

CACHE_FILE = "cache.json"
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        CACHE = json.load(f)
else:
    CACHE = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(CACHE, f, indent=2)

OFFLINE_MODE = os.getenv("OFFLINE_MODE","").lower() in ("1","true","yes")

# ---------------------- Classification ----------------------
def classify_intent(prompt: str):
    p = prompt.lower()
    if any(k in p for k in ["generate image","draw","sd:","stable diffusion"]):
        return ["image"]
    if any(k in p for k in ["code","python","script","function","bug","class"]):
        return ["code","text"]
    if any(k in p for k in ["search","latest","news","who is","what is","lookup"]):
        return ["search","text"]
    return ["text"]

# ---------------------- Caching ----------------------
def cache_key(kind, prompt):
    return hashlib.sha256(f"{kind}:{prompt}".encode("utf-8")).hexdigest()

def run_tool(kind, prompt):
    key = cache_key(kind, prompt)
    if key in CACHE:
        cached = CACHE[key]
        cached["from_cache"] = True
        return {"kind": kind, "result": cached}

    if OFFLINE_MODE:
        if kind == "text":
            result = gemini_text(prompt)
        elif kind == "code":
            result = hf_generate_code(prompt)
        elif kind == "image":
            result = hf_generate_image(prompt)
        elif kind == "search":
            result = {"text": f"(offline) Search stub: {prompt}", "images": [], "provider": "stub-duckduckgo"}
        else:
            result = {"ok": False, "text": "", "meta": {}}
    else:
        if kind == "text":
            result = gemini_text(prompt)
        elif kind == "code":
            result = hf_generate_code(prompt)
        elif kind == "image":
            result = hf_generate_image(prompt)
        elif kind == "search":
            result = instant_answer(prompt)
        else:
            result = {"ok": False, "text": "", "meta": {}}

    result["from_cache"] = False
    CACHE[key] = result
    return {"kind": kind, "result": result}


def route_and_run(prompt: str, num_images: int = 1):
    kinds = classify_intent(prompt)
    if "text" not in kinds:
        kinds.append("text")

    out = []
    with ThreadPoolExecutor(max_workers=len(kinds)) as ex:
        futs = [ex.submit(run_tool, k, prompt) for k in kinds]
        for f in as_completed(futs):
            out.append(f.result())

    # Handle search images automatically
    search_results = [r for r in out if r["kind"] == "search"]
    for sr in search_results:
        for img in sr["result"].get("images", []):
            out.append({"kind": "image", "result": {"url": img.get("url"), "prompt": img.get("title")}})

    # Save cache once after all threads are done
    save_cache()

    return out


# ---------------------- Main Router ----------------------
def route_and_run(prompt: str, num_images: int = 1):
    kinds = classify_intent(prompt)
    if "text" not in kinds:
        kinds.append("text")

    out = []
    with ThreadPoolExecutor(max_workers=len(kinds)) as ex:
        futs = [ex.submit(run_tool, k, prompt) for k in kinds]
        for f in as_completed(futs):
            out.append(f.result())

    # Handle search images automatically
    search_results = [r for r in out if r["kind"] == "search"]
    for sr in search_results:
        for img in sr["result"].get("images", []):
            out.append({"kind": "image", "result": {"path": img.get("url"), "prompt": img.get("title")}})

    save_cache()
    return out

