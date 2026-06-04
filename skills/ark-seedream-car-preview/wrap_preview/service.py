from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .assets import apply_color_asset
from .config import default_model_for, default_size_for, load_provider_configs, normalize_provider_name
from .models import WrapPreviewRequest
from .output import relative_path_string, save_generated_images
from .paths import default_out_dir
from .prompt import build_prompt
from .providers.router import ProviderRouter
from .refs import normalize_refs
from .validation import validate_reference_images


def generate_wrap_preview(request: WrapPreviewRequest) -> dict[str, Any]:
    request.provider = normalize_provider_name(request.provider)
    request.model = request.model or default_model_for(request.provider)
    request.size = request.size or default_size_for(request.provider)
    cwd = Path.cwd().resolve()
    out_dir = request.out_dir.resolve() if request.out_dir else default_out_dir().resolve()

    color_asset = apply_color_asset(request)
    prompt = build_prompt(request)
    validate_reference_images(request)

    configs = load_provider_configs(
        provider=request.provider,
        base_url=request.base_url,
        model=request.model,
    )
    provider_summary = [
        {
            "name": config.name,
            "base_url": config.base_url,
            "model": config.model,
            "auth_scheme": config.auth_scheme,
            "has_api_key": bool(config.api_key),
        }
        for config in configs
    ]

    if request.dry_run:
        return {
            "dry_run": True,
            "provider": request.provider,
            "providers": provider_summary,
            "prompt": prompt,
            "model": request.model,
            "size": request.size,
            "quality": request.quality,
            "response_format": request.response_format,
            "refs": request.raw_refs,
            "reference_strategy": "vehicle_image_plus_preview_swatch_image",
            "out_dir": out_dir.as_posix(),
            "color_asset": color_asset,
        }

    refs = normalize_refs(request.raw_refs)
    provider_result = ProviderRouter(configs).generate(
        prompt=prompt,
        refs=refs,
        size=request.size,
        quality=request.quality,
        response_format=request.response_format,
    )
    files, urls, base64_count = save_generated_images(provider_result.response, out_dir)
    relative_files = [relative_path_string(path, cwd) for path in files]
    return {
        "provider": provider_result.provider,
        "provider_attempts": [asdict(attempt) for attempt in provider_result.attempts],
        "prompt": prompt,
        "model": provider_result.model,
        "size": request.size,
        "quality": request.quality,
        "files": [path.as_posix() for path in files],
        "relative_files": relative_files,
        "media_tokens": [f"MEDIA:{path}" for path in relative_files],
        "out_dir": out_dir.as_posix(),
        "color_asset": color_asset,
        "response_keys": sorted(provider_result.response.keys()),
        "image_urls": urls,
        "base64_images": base64_count,
    }
