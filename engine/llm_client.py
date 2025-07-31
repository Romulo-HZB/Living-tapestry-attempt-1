import json
from pathlib import Path
from typing import List, Dict
from urllib import request


class LLMClient:
    """Simple connector to an OpenAI-compatible endpoint."""

    def __init__(self, config_path: Path):
        with open(config_path, "r") as f:
            cfg = json.load(f)
        self.endpoint = cfg.get("endpoint")
        self.model = cfg.get("model")
        self.max_context = cfg.get("max_context", -1)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if self.max_context != -1:
            payload["max_tokens"] = self.max_context
        req = request.Request(
            self.endpoint,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"]

    def parse_command(self, user_input: str, system_prompt: str) -> Dict[str, str]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        reply = self.chat(messages)
        try:
            return json.loads(reply)
        except json.JSONDecodeError:
            return {}

