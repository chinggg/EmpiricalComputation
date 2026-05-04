"""OpenAI-compatible chat client. The single point at which the model is fixed.

Swapping models means changing the constructor arguments — no problem code
needs to be touched.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass

from openai import OpenAI


@dataclass
class LLMResponse:
    text: str
    elapsed_s: float
    tokens_in: int | None
    tokens_out: int | None
    model: str


class LLMClient:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout_s: float = 120.0,
    ):
        self.model = model or os.environ.get("EMPCOMP_MODEL", "gemma-4-e4b")
        self.base_url = base_url or os.environ.get(
            "EMPCOMP_BASE_URL", "http://127.0.0.1:1234/v1"
        )
        self.api_key = api_key or os.environ.get("EMPCOMP_API_KEY", "lm-studio")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = OpenAI(
            base_url=self.base_url, api_key=self.api_key, timeout=timeout_s
        )

    def chat(self, system: str, user: str) -> LLMResponse:
        t0 = time.perf_counter()
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        elapsed = time.perf_counter() - t0
        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        return LLMResponse(
            text=text,
            elapsed_s=elapsed,
            tokens_in=getattr(usage, "prompt_tokens", None),
            tokens_out=getattr(usage, "completion_tokens", None),
            model=self.model,
        )
