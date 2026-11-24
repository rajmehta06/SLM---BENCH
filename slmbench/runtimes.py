"""Runtime adapter contract and real Ollama / explicitly synthetic demo backends."""
from __future__ import annotations
from abc import ABC, abstractmethod
import time
import requests

class RuntimeAdapter(ABC):
    name: str
    mode: str
    @abstractmethod
    def generate(self, model: str, prompt: str, max_tokens: int = 128) -> dict: ...
    @abstractmethod
    def available(self) -> tuple[bool, str]: ...

class OllamaAdapter(RuntimeAdapter):
    name, mode = "Ollama", "real"
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
    def available(self):
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=2); r.raise_for_status()
            return True, "Ollama API reachable"
        except requests.RequestException as exc: return False, str(exc)
    def models(self):
        try: return [m["name"] for m in requests.get(f"{self.base_url}/api/tags", timeout=2).json().get("models", [])]
        except (requests.RequestException, ValueError): return []
    def generate(self, model, prompt, max_tokens=128):
        start = time.perf_counter(); first = None; pieces = []
        try:
            with requests.post(f"{self.base_url}/api/generate", json={"model":model,"prompt":prompt,"stream":True,"options":{"num_predict":max_tokens,"num_gpu":0}}, stream=True, timeout=(5,180)) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line: continue
                    import json
                    item=json.loads(line); piece=item.get("response", "")
                    if piece and first is None: first=time.perf_counter()
                    pieces.append(piece)
            elapsed=time.perf_counter()-start; answer="".join(pieces); tokens=len(answer.split())
            return {"text":answer,"ttft_s":first-start if first else None,"latency_s":elapsed,"tokens":tokens,"tps":tokens/elapsed if elapsed else None,"error":None}
        except Exception as exc:
            return {"text":"","ttft_s":None,"latency_s":time.perf_counter()-start,"tokens":0,"tps":None,"error":str(exc)}

class DemoAdapter(RuntimeAdapter):
    name, mode = "Demo (synthetic)", "synthetic"
    def available(self): return True, "Synthetic responses; metrics are illustrative, not model measurements"
    def generate(self, model, prompt, max_tokens=128):
        start=time.perf_counter(); lower=prompt.lower()
        if "17 + 25" in prompt: answer="42"
        elif "9 multiplied by 8" in prompt: answer="72"
        elif "100 minus 37" in prompt: answer="63"
        elif "how many sides" in lower: answer="6"
        elif "4 pens" in lower: answer="12 dollars"
        elif "red rose" in lower: answer="Yes."
        elif "tomorrow" in lower: answer="Wednesday"
        elif "kyoto" in lower: answer="Kyoto"
        elif "2026-12-05" in lower: answer="2026-12-05"
        elif "colors mentioned" in lower: answer="blue, white, green"
        elif "renewable energy" in lower: answer="Solar energy"
        else: answer="Plants convert sunlight into energy and release oxygen."
        elapsed=max(time.perf_counter()-start,0.025); tokens=len(answer.split())
        return {"text":answer,"ttft_s":elapsed*0.35,"latency_s":elapsed,"tokens":tokens,"tps":tokens/elapsed,"error":None}
