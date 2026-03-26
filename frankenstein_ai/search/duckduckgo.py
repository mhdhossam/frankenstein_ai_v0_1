from ddgs import DDGS

def instant_answer(query: str, max_images: int = 3):
    text_res = ""
    images = []

    # Strip any accidental !g
    if query.startswith("!g "):
        query = query[3:].strip()

    try:
        with DDGS() as ddg:
            results = list(ddg.text(query, max_results=3))
            text_res = "\n".join([f"- {r.get('title','')}: {r.get('href','')}" for r in results])
            
            img_results = list(ddg.images(query, max_results=max_images))
            for img in img_results:
                images.append({
                    "title": img.get("title", query),
                    "url": img.get("image"),
                    "provider": "duckduckgo"
                })

        return {"text": text_res or "(no results found)", "images": images, "provider": "duckduckgo"}

    except Exception as e:
        return {"text": f"(error) {e}", "images": [], "provider": "duckduckgo"}
