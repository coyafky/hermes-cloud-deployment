from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import WrapPreviewRequest
from .paths import default_asset_library
from .text import lookup_key


def load_color_asset(asset_library: str, asset_id: str) -> tuple[dict[str, Any], Path]:
    library_path = Path(asset_library).expanduser().resolve() if asset_library else default_asset_library()
    if not library_path.is_file():
        raise FileNotFoundError(f"Color asset library not found: {library_path}")

    payload = json.loads(library_path.read_text(encoding="utf-8"))
    needle = lookup_key(asset_id)
    if not needle:
        raise ValueError("--asset-id was provided but empty")

    fuzzy_matches = []
    for asset in payload.get("assets", []):
        names = asset.get("names", {}) if isinstance(asset, dict) else {}
        candidates = [
            asset.get("id", ""),
            asset.get("serial", ""),
            names.get("zh", ""),
            names.get("en", ""),
            *(names.get("aliases", []) or []),
        ]
        normalized = [lookup_key(str(candidate)) for candidate in candidates if candidate]
        if needle in normalized:
            return asset, library_path
        if any(needle and (needle in candidate or candidate in needle) for candidate in normalized):
            fuzzy_matches.append(asset)

    if len(fuzzy_matches) == 1:
        return fuzzy_matches[0], library_path
    if fuzzy_matches:
        matches = ", ".join(item.get("id", "") for item in fuzzy_matches[:10])
        raise ValueError(f"Color asset lookup is ambiguous for {asset_id!r}. Matches: {matches}")
    raise ValueError(f"Color asset not found: {asset_id}")


def apply_color_asset(request: WrapPreviewRequest) -> dict[str, Any] | None:
    if not request.asset_id:
        return None

    asset, library_path = load_color_asset(request.asset_library, request.asset_id)
    prompt_fields = asset.get("prompt", {})
    if not request.color_name:
        request.color_name = prompt_fields.get("color_name", "") or asset.get("names", {}).get("zh", "")
    if not request.color_code:
        request.color_code = prompt_fields.get("color_code", "") or asset.get("serial", "")
    if not request.color_value:
        hex_value = asset.get("color", {}).get("hex", "")
        lab = asset.get("color", {}).get("lab", {})
        lab_value = ""
        if lab:
            lab_value = f"Lab(L={lab.get('L')}, a={lab.get('a')}, b={lab.get('b')})"
        request.color_value = prompt_fields.get("color_value", "") or hex_value or lab_value
    if not request.finish:
        request.finish = prompt_fields.get("finish", "") or asset.get("finish", {}).get("prompt_label", "")
    if not request.description:
        request.description = prompt_fields.get("description", "")

    swatch = asset.get("images", {}).get("swatch")
    swatch_path = None
    if swatch:
        swatch_path = (library_path.parent / swatch).resolve()
        if swatch_path.is_file() and swatch_path.as_posix() not in request.color_refs:
            request.color_refs.append(swatch_path.as_posix())

    return {
        "id": asset.get("id"),
        "serial": asset.get("serial"),
        "name": asset.get("names", {}).get("zh"),
        "hex": asset.get("color", {}).get("hex"),
        "lab": asset.get("color", {}).get("lab"),
        "swatch": swatch,
        "swatch_path": swatch_path.as_posix() if swatch_path and swatch_path.is_file() else None,
        "reference_strategy": "vehicle_image_plus_preview_swatch_image",
        "library": library_path.as_posix(),
    }

