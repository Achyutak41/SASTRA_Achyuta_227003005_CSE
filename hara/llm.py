import os, requests
def ollama_available():
    try: return requests.get(os.getenv("OLLAMA_BASE_URL","http://localhost:11434").rstrip("/")+"/api/tags",timeout=2).ok
    except requests.RequestException: return False
def generate_with_ollama(prompt):
    base=os.getenv("OLLAMA_BASE_URL","http://localhost:11434").rstrip("/")
    model=os.getenv("OLLAMA_MODEL","phi")
    r=requests.post(base+"/api/generate",json={"model":model,"prompt":prompt,"stream":False,"options":{"temperature":0}},timeout=int(os.getenv("OLLAMA_TIMEOUT_SECONDS","300")))
    r.raise_for_status(); return r.json().get("response","No response returned.")
