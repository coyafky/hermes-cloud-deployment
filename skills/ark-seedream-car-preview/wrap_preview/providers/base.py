from __future__ import annotations

from typing import Protocol

from ..models import ProviderConfig


class ImageProvider(Protocol):
    config: ProviderConfig

    def generate(
        self,
        *,
        prompt: str,
        refs: list[str],
        size: str,
        quality: str,
        response_format: str,
    ) -> dict:
        ...

