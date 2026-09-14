from __future__ import annotations

from typing import Any

import httpx

from core.config.settings import Settings
from .base import LLMProvider
from .key_manager import ApiKeyManager
from .response import AIResponse
from .tool_call import ToolCall
from .usage import Usage


class GroqProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self._settings = settings
        self._keys = ApiKeyManager(
            settings.api_keys,
            settings.temporary_failure_cooldown_seconds,
        )

    def generate(
        self,
        prompt: str,
        history=None,
        tool_result=None,
        system_prompt=None,
        tools=None,
    ) -> AIResponse:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history or [])
        if tool_result is not None:
            messages.append(tool_result)
        else:
            messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self._settings.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        last_error: Exception | None = None
        attempts = min(self._settings.max_api_attempts, len(self._settings.api_keys))
        for _ in range(attempts):
            key = self._keys.next_key()
            try:
                response = httpx.post(
                    f"{self._settings.base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key.key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self._settings.timeout,
                )
                response.raise_for_status()
                return self._parse_response(response.json())
            except (httpx.HTTPError, ValueError, KeyError) as error:
                last_error = error
                self._keys.mark_failed(key)

        raise RuntimeError("Groq request failed after all available key attempts") from last_error

    @staticmethod
    def _parse_response(data: dict[str, Any]) -> AIResponse:
        choice = data["choices"][0]
        message = choice.get("message", {})
        calls = []
        for call in message.get("tool_calls", []) or []:
            function = call.get("function", {})
            calls.append(
                ToolCall(
                    id=call.get("id", ""),
                    name=function.get("name", ""),
                    arguments=function.get("arguments", {}),
                )
            )
        raw_usage = data.get("usage", {})
        usage = Usage(
            prompt_tokens=raw_usage.get("prompt_tokens", 0),
            completion_tokens=raw_usage.get("completion_tokens", 0),
            total_tokens=raw_usage.get("total_tokens", 0),
        )
        return AIResponse(
            content=message.get("content"),
            model=data.get("model", ""),
            usage=usage,
            finish_reason=choice.get("finish_reason"),
            tool_calls=calls,
        )
