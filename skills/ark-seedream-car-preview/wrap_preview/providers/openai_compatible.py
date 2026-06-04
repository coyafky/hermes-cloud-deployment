from __future__ import annotations

import json
import urllib.error
import urllib.request

from ..models import ProviderConfig
from .errors import ProviderConfigurationError, ProviderError


class OpenAICompatibleProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config

    def generate(
        self,
        *,
        prompt: str,
        refs: list[str],
        size: str,
        quality: str,
        response_format: str,
    ) -> dict:
        if not self.config.api_key:
            raise ProviderConfigurationError(f"Missing API key for provider {self.config.name!r}")

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "response_format": response_format,
        }
        if refs:
            payload["image"] = refs
        return self._post_json(f"{self.config.base_url.rstrip('/')}/images/generations", payload)

    def _post_json(self, url: str, payload: dict) -> dict:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.config.auth_scheme == "raw":
            headers["Authorization"] = self.config.api_key
        else:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        req = urllib.request.Request(url, method="POST", headers=headers, data=body)
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")
            raise ProviderError(f"{self.config.name} image generation failed ({err.code}): {detail}") from err
        except Exception as err:
            raise ProviderError(f"{self.config.name} image generation failed: {err}") from err

