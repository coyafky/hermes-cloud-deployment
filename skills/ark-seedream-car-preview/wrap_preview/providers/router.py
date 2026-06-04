from __future__ import annotations

from ..models import ProviderAttempt, ProviderConfig, ProviderResult
from .errors import AllProvidersFailed, ProviderError
from .openai_compatible import OpenAICompatibleProvider


class ProviderRouter:
    def __init__(self, configs: list[ProviderConfig]):
        self.configs = configs

    def generate(
        self,
        *,
        prompt: str,
        refs: list[str],
        size: str,
        quality: str,
        response_format: str,
    ) -> ProviderResult:
        attempts: list[ProviderAttempt] = []
        if not self.configs:
            raise AllProvidersFailed("No image providers configured. Set WRAP_PROVIDER_CHAIN or IMAGE_RELAY_BASE_URL.")

        for config in self.configs:
            provider = OpenAICompatibleProvider(config)
            try:
                response = provider.generate(
                    prompt=prompt,
                    refs=refs,
                    size=size,
                    quality=quality,
                    response_format=response_format,
                )
                attempts.append(ProviderAttempt(provider=config.name, ok=True))
                return ProviderResult(provider=config.name, model=config.model, response=response, attempts=attempts)
            except ProviderError as err:
                attempts.append(ProviderAttempt(provider=config.name, ok=False, error=str(err)))

        errors = "; ".join(f"{attempt.provider}: {attempt.error}" for attempt in attempts)
        raise AllProvidersFailed(f"All image providers failed. {errors}")
