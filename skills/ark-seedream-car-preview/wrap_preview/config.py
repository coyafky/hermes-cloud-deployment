from __future__ import annotations

import json
import os
from pathlib import Path

from .models import ProviderConfig
from .paths import profile_base_dir, skill_base_dir


DEFAULT_OPENAI_COMPATIBLE_MODEL = "gpt-image-2"
DEFAULT_OPENAI_COMPATIBLE_SIZE = "auto"


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            values[name.strip()] = value.strip().strip("\"'")
    except Exception:
        return {}
    return values


def merged_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for env_path in candidate_env_files():
        values.update(read_env_file(env_path))
    values.update({key: value for key, value in os.environ.items() if isinstance(value, str)})
    values.update(read_local_json())
    return values


def candidate_env_files() -> list[Path]:
    files = [
        skill_base_dir() / ".env",
        skill_base_dir() / ".env.local",
    ]
    profile_dir = profile_base_dir()
    if profile_dir:
        files.extend(
            [
                profile_dir / ".env",
                profile_dir / ".env.local",
            ]
        )
    return files


def read_local_json() -> dict[str, str]:
    local_json = skill_base_dir() / ".local.json"
    if not local_json.is_file():
        return {}
    try:
        payload = json.loads(local_json.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {str(key).upper(): value for key, value in payload.items() if isinstance(value, str)}


def env_lookup(values: dict[str, str], *names: str) -> str:
    for name in names:
        value = (values.get(name) or "").strip()
        if value and not is_placeholder_value(value):
            return value
    return ""


def is_placeholder_value(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("replace-with-") or lowered in {"todo", "changeme", "your-api-key"}


def normalize_provider_name(name: str) -> str:
    value = (name or "").strip().lower()
    aliases = {
        "": "auto",
        "relay": "auto",
        "openai-compatible": "auto",
        "openai_compatible": "auto",
        "chatgpt-image2": "auto",
        "chatgpt-image-2": "auto",
        "gpt-image-2": "auto",
    }
    return aliases.get(value, value)


def default_model_for(provider: str = "auto") -> str:
    return DEFAULT_OPENAI_COMPATIBLE_MODEL


def default_size_for(provider: str = "auto") -> str:
    return DEFAULT_OPENAI_COMPATIBLE_SIZE


def load_provider_configs(
    *,
    provider: str,
    base_url: str,
    model: str,
) -> list[ProviderConfig]:
    values = merged_env()
    provider = normalize_provider_name(provider)
    model = model or env_lookup(values, "IMAGE_RELAY_MODEL", "OPENAI_COMPATIBLE_MODEL") or default_model_for(provider)

    if base_url:
        api_key = env_lookup(
            values,
            "IMAGE_RELAY_API_KEY",
            "OPENAI_COMPATIBLE_API_KEY",
            "GPT_IMAGE_API_KEY",
            "CHATGPT_IMAGE_API_KEY",
            "APIYI_API_KEY",
            "4S_API_KEY",
            "FOURS_API_KEY",
            "XINGHU_API_KEY",
            "XINGHUAPI_API_KEY",
            "XINGHU_CLOUD_API_KEY",
        )
        return [
            ProviderConfig(
                name=provider if provider != "auto" else "cli",
                base_url=base_url.rstrip("/"),
                api_key=api_key,
                model=model,
                auth_scheme=env_lookup(values, "IMAGE_RELAY_AUTH_SCHEME", "OPENAI_COMPATIBLE_AUTH_SCHEME") or "bearer",
            )
        ]

    chain = env_lookup(values, "WRAP_PROVIDER_CHAIN", "IMAGE_PROVIDER_CHAIN")
    names = [item.strip() for item in chain.split(",") if item.strip()] if chain else []
    configs = [load_named_provider(values, name, model) for name in names]
    configs = [config for config in configs if config is not None]
    if configs:
        return configs

    fallback_base_url = env_lookup(values, "IMAGE_RELAY_BASE_URL", "OPENAI_COMPATIBLE_BASE_URL")
    fallback_key = env_lookup(
        values,
        "IMAGE_RELAY_API_KEY",
        "OPENAI_COMPATIBLE_API_KEY",
        "GPT_IMAGE_API_KEY",
        "CHATGPT_IMAGE_API_KEY",
    )
    if fallback_base_url:
        return [
            ProviderConfig(
                name="default",
                base_url=fallback_base_url.rstrip("/"),
                api_key=fallback_key,
                model=model,
                auth_scheme=env_lookup(values, "IMAGE_RELAY_AUTH_SCHEME", "OPENAI_COMPATIBLE_AUTH_SCHEME") or "bearer",
            )
        ]
    return []


def load_named_provider(values: dict[str, str], name: str, default_model: str) -> ProviderConfig | None:
    prefix = f"WRAP_PROVIDER_{name.upper()}_"
    base_url = env_lookup(values, prefix + "BASE_URL", *legacy_provider_base_url_names(name))
    if not base_url:
        return None
    return ProviderConfig(
        name=name,
        base_url=base_url.rstrip("/"),
        api_key=env_lookup(values, prefix + "API_KEY", *legacy_provider_api_key_names(name)),
        model=env_lookup(values, prefix + "MODEL", *legacy_provider_model_names(name)) or default_model,
        auth_scheme=env_lookup(values, prefix + "AUTH_SCHEME") or "bearer",
    )


def legacy_provider_base_url_names(name: str) -> tuple[str, ...]:
    normalized = name.lower().replace("-", "_")
    if "apiyi" in normalized:
        return ("APIYI_BASE_URL",)
    if "4s" in normalized or "fours" in normalized:
        return ("FOURS_BASE_URL", "4S_BASE_URL")
    if "xinghu" in normalized:
        return ("XINGHU_BASE_URL", "XINGHUAPI_BASE_URL")
    return ()


def legacy_provider_api_key_names(name: str) -> tuple[str, ...]:
    normalized = name.lower().replace("-", "_")
    if "apiyi" in normalized:
        return ("APIYI_API_KEY",)
    if "4s" in normalized or "fours" in normalized:
        return ("4S_API_KEY", "FOURS_API_KEY")
    if "xinghu" in normalized:
        return ("XINGHU_API_KEY", "XINGHUAPI_API_KEY", "XINGHU_CLOUD_API_KEY")
    return ()


def legacy_provider_model_names(name: str) -> tuple[str, ...]:
    normalized = name.lower().replace("-", "_")
    if "apiyi" in normalized:
        return ("APIYI_MODEL",)
    if "4s" in normalized or "fours" in normalized:
        return ("FOURS_MODEL", "4S_MODEL")
    if "xinghu" in normalized:
        return ("XINGHU_MODEL", "XINGHUAPI_MODEL")
    return ()
