import json, os, hashlib

CACHE_FILE = "cache.json"

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        CACHE = json.load(f)
else:
    CACHE = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(CACHE, f, indent=2)

def cache_key(kind, prompt):
    return hashlib.sha256(f"{kind}:{prompt}".encode("utf-8")).hexdigest()
