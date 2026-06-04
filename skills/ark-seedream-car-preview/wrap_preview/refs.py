from __future__ import annotations

import base64
import mimetypes
import urllib.parse
from pathlib import Path


def is_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https", "data"}


def path_to_data_url_base64(path_str: str) -> str:
    path = Path(path_str).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Reference image not found: {path}")
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def normalize_refs(refs: list[str]) -> list[str]:
    normalized = []
    for ref in refs:
        normalized.append(ref if is_url(ref) else path_to_data_url_base64(ref))
    return normalized

