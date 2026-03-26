# Corrector placeholder
import re
import ast

def simple_correct(text:str)->str:
    t = text.strip()
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'([!?.,])\1{2,}', r'\1', t)
    if len(t)>1 and t[0].islower():
        t = t[0].upper() + t[1:]
    if "def " in t or "print(" in t or "class " in t:
        try:
            ast.parse(t)
        except Exception as e:
            t += f"\n# (note) possible syntax issue detected: {e}"
    return t
