from huggingface_hub import InferenceClient
import time
import os

def hf_generate_image(prompt: str):
    try:
        client = InferenceClient(
            "stabilityai/stable-diffusion-xl-base-1.0",
            token=""
        )
        image = client.text_to_image(prompt)

        fname = f"artifact_{int(time.time())}.png"
        path = os.path.abspath(fname)
        image.save(path)

        print(f"[DEBUG] Image saved at {path}")  # 👈 add this
        return {"ok": True, "text": "image generated", "path": path, "provider": "hf-sd"}
    except Exception as e:
        return {"ok": False, "text": f"(error) {e}", "path": None, "provider": "hf-sd"}
