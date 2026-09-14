from __future__ import annotations

from threading import Lock
from time import monotonic

from core.config.settings import ApiKeyConfig


class ApiKeyManager:
    def __init__(self, keys: tuple[ApiKeyConfig, ...], cooldown_seconds: float):
        self._keys = keys
        self._cooldown_seconds = cooldown_seconds
        self._blocked_until = {key.slot: 0.0 for key in keys}
        self._cursor = 0
        self._lock = Lock()

    def next_key(self) -> ApiKeyConfig:
        with self._lock:
            now = monotonic()
            for offset in range(len(self._keys)):
                index = (self._cursor + offset) % len(self._keys)
                key = self._keys[index]
                if self._blocked_until[key.slot] <= now:
                    self._cursor = (index + 1) % len(self._keys)
                    return key
        raise RuntimeError("All Groq API keys are temporarily unavailable")

    def mark_failed(self, key: ApiKeyConfig) -> None:
        with self._lock:
            self._blocked_until[key.slot] = monotonic() + self._cooldown_seconds
