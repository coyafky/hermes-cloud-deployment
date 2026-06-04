from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WrapPreviewRequest:
    provider: str = "auto"
    base_url: str = ""
    prompt: str = ""
    model: str = ""
    vehicle_refs: list[str] = field(default_factory=list)
    color_refs: list[str] = field(default_factory=list)
    extra_refs: list[str] = field(default_factory=list)
    asset_id: str = ""
    asset_library: str = ""
    color_name: str = ""
    color_code: str = ""
    color_value: str = ""
    finish: str = ""
    description: str = ""
    size: str = ""
    quality: str = "high"
    response_format: str = "url"
    out_dir: Path | None = None
    dry_run: bool = False

    @property
    def raw_refs(self) -> list[str]:
        return self.vehicle_refs + self.color_refs + self.extra_refs


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    api_key: str
    model: str = "gpt-image-2"
    auth_scheme: str = "bearer"
    timeout_seconds: int = 300


@dataclass(frozen=True)
class ProviderAttempt:
    provider: str
    ok: bool
    error: str = ""


@dataclass
class ProviderResult:
    provider: str
    model: str
    response: dict[str, Any]
    attempts: list[ProviderAttempt] = field(default_factory=list)
