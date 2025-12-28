#!/usr/bin/env python3
import os
import requests
from typing import List, Optional, Dict, Any


class GrokClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "grok-2-latest"):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set XAI_API_KEY in env or pass api_key=...")
        self.model = model
        self.base_url = "https://api.x.ai/v1/chat/completions"

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()
