from huggingface_hub import InferenceClient
from ..config import HF_API_TOKEN

def hf_generate_code(prompt: str):
    if not HF_API_TOKEN or os.getenv("OFFLINE_MODE","").lower() in ("1","true","yes"):
        sample = f"# Stubbed code for: {prompt}\nprint('Hello from Frankenstein AI v0.1')"
        return {"ok": True, "text": sample, "provider":"stub-hf-code"}
    
    client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.2", token=HF_API_TOKEN)
    response = client.text_generation(prompt, max_new_tokens=200)
    return {"ok": True, "text": response, "provider":"hf-code"}
