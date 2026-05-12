"""LLM clients with two backends.

LMStudioClient  — native /api/v1/chat endpoint, captures full stats object.
OpenAICompatClient — standard /v1/chat/completions via openai SDK (remote APIs).

make_client() auto-selects: localhost base URL → LMStudioClient, else OpenAICompatClient.
Override with EMPCOMP_BACKEND=lmstudio|openai.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

import httpx
from openai import OpenAI

from .presets import Preset, get_preset


@dataclass
class LLMResponse:
    text: str
    elapsed_s: float
    model: str
    # Field names mirror the LM Studio native API stats object exactly.
    input_tokens: int | None = None
    total_output_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    tokens_per_second: float | None = None
    time_to_first_token_seconds: float | None = None
    thinking_text: str | None = None
    stop_reason: str | None = None


class LMStudioClient:
    """Calls LM Studio native /api/v1/chat to get richer stats."""

    def __init__(
        self,
        model: str,
        host: str,           # e.g. "http://127.0.0.1:1234"
        preset: Preset,
        api_key: str = "lm-studio",
        timeout_s: float = 600.0,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.preset = preset
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._timeout = timeout_s

    @property
    def base_url(self) -> str:
        return f"{self.host}/api/v1"

    def chat(self, system: str, user: str) -> LLMResponse:
        payload: dict = {
            "model": self.model,
            "input": user,
            "system_prompt": system,
        }
        if self.preset.temperature is not None:
            payload["temperature"] = self.preset.temperature
        payload["reasoning"] = "on" if self.preset.thinking else "off"

        t0 = time.perf_counter()
        r = httpx.post(
            f"{self.host}/api/v1/chat",
            json=payload,
            headers=self._headers,
            timeout=self._timeout,
        )
        elapsed = time.perf_counter() - t0
        r.raise_for_status()
        body = r.json()

        output_items = body.get("output", [])
        text = next(
            (item["content"] for item in output_items if item.get("type") == "message"), ""
        )
        thinking_text = next(
            (item["content"] for item in output_items if item.get("type") == "reasoning"), None
        )

        stats = body.get("stats") or {}
        return LLMResponse(
            text=text,
            elapsed_s=elapsed,
            model=body.get("model_instance_id", self.model),
            input_tokens=stats.get("input_tokens"),
            total_output_tokens=stats.get("total_output_tokens"),
            reasoning_output_tokens=stats.get("reasoning_output_tokens"),
            tokens_per_second=stats.get("tokens_per_second"),
            time_to_first_token_seconds=stats.get("time_to_first_token_seconds"),
            thinking_text=thinking_text,
        )


class OpenAICompatClient:
    """OpenAI-compatible /v1/chat/completions client (for remote APIs)."""

    def __init__(
        self,
        model: str,
        base_url: str,       # must include /v1 suffix for the SDK
        preset: Preset,
        api_key: str = "none",
        timeout_s: float = 600.0,
    ):
        self.model = model
        self.base_url = base_url
        self.preset = preset
        self._client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout_s)

    def chat(self, system: str, user: str) -> LLMResponse:
        t0 = time.perf_counter()
        kwargs: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if self.preset.temperature is not None:
            kwargs["temperature"] = self.preset.temperature
        resp = self._client.chat.completions.create(**kwargs)
        elapsed = time.perf_counter() - t0
        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        details = getattr(usage, "completion_tokens_details", None)
        return LLMResponse(
            text=text,
            elapsed_s=elapsed,
            model=self.model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            total_output_tokens=getattr(usage, "completion_tokens", None),
            reasoning_output_tokens=getattr(details, "reasoning_tokens", None),
            stop_reason=resp.choices[0].finish_reason,
        )


def _is_local(url: str) -> bool:
    return any(h in url for h in ("localhost", "127.0.0.1", "::1"))


def make_client(
    preset: Preset | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    backend: str | None = None,
    timeout_s: float = 600.0,
) -> LMStudioClient | OpenAICompatClient:
    """Factory: returns LMStudioClient for localhost URLs, OpenAICompatClient otherwise.

    Override auto-detection with EMPCOMP_BACKEND=lmstudio|openai.
    """
    if preset is None:
        preset = get_preset("default")
    model = model or os.environ.get("EMPCOMP_MODEL", "qwen3.6-35b-a3b")
    base_url = base_url or os.environ.get("EMPCOMP_BASE_URL", "http://127.0.0.1:1234")
    api_key = api_key or os.environ.get("EMPCOMP_API_KEY", "lm-studio")
    backend = backend or os.environ.get("EMPCOMP_BACKEND", "auto")

    use_lmstudio = backend == "lmstudio" or (backend == "auto" and _is_local(base_url))

    if use_lmstudio:
        host = base_url.rstrip("/")
        if host.endswith("/v1"):
            host = host[:-3]
        return LMStudioClient(
            model=model, host=host, preset=preset, api_key=api_key, timeout_s=timeout_s
        )
    else:
        compat_url = base_url.rstrip("/")
        if not compat_url.endswith("/v1"):
            compat_url += "/v1"
        return OpenAICompatClient(
            model=model, base_url=compat_url, preset=preset, api_key=api_key, timeout_s=timeout_s
        )
