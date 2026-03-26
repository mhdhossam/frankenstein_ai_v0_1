import os
import google.generativeai as genai
from ..config import GEMINI_API_KEY  # make sure config.py has your key

def gemini_text(prompt: str):
    if not GEMINI_API_KEY or os.getenv("OFFLINE_MODE","").lower() in ("1","true","yes"):
        return {"ok": True, "text": f"(offline stub) Answer to: {prompt}", "provider": "stub-gemini"}
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")  # you can use gemini-1.5-pro too
        response = model.generate_content(prompt)
        return {"ok": True, "text": response.text, "provider": "gemini"}
    except Exception as e:
        return {"ok": False, "text": f"(error) {str(e)}", "provider": "gemini"}
