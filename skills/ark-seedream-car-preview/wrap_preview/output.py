from __future__ import annotations

import base64
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def extract_image_urls(payload: dict[str, Any], required: bool = True) -> list[str]:
    candidates = payload.get("data")
    urls: list[str] = []

    if isinstance(candidates, list):
        for item in candidates:
            if isinstance(item, str) and item.startswith(("http://", "https://", "data:")):
                urls.append(item)
            elif isinstance(item, dict):
                for key in ("url", "image_url"):
                    value = item.get(key)
                    if isinstance(value, str) and value:
                        urls.append(value)
    elif isinstance(candidates, dict):
        for key in ("url", "image_url"):
            value = candidates.get(key)
            if isinstance(value, str) and value:
                urls.append(value)
        for key in ("urls", "images", "image_urls"):
            value = candidates.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item:
                        urls.append(item)
                    elif isinstance(item, dict):
                        for nested_key in ("url", "image_url"):
                            nested_value = item.get(nested_key)
                            if isinstance(nested_value, str) and nested_value:
                                urls.append(nested_value)
    for key in ("url", "image_url", "output_url"):
        value = payload.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://", "data:")):
            urls.append(value)
    if urls or not required:
        return urls
    raise RuntimeError(f"Provider returned no image URLs. Response keys: {sorted(payload.keys())}")


def extract_image_base64s(payload: object) -> list[str]:
    values: list[str] = []
    base64_keys = {"b64_json", "base64", "image_base64"}

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in base64_keys and isinstance(item, str) and item.strip():
                    values.append(item.strip())
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return values


def mime_to_extension(mime: str) -> str:
    if mime == "image/jpeg":
        return ".jpg"
    if mime == "image/webp":
        return ".webp"
    return ".png"


def parse_data_url(data_url: str) -> tuple[str, bytes]:
    header, encoded = data_url.split(",", 1)
    mime = "image/png"
    if header.startswith("data:"):
        mime = header[5:].split(";", 1)[0] or mime
    return mime, base64.b64decode(encoded)


def download_file(url: str, out_path: Path) -> None:
    with urllib.request.urlopen(url, timeout=300) as resp:
        out_path.write_bytes(resp.read())


def relative_path_string(path: Path, cwd: Path) -> str:
    try:
        rel = path.relative_to(cwd)
        return f"./{rel.as_posix()}"
    except ValueError:
        return path.as_posix()


def save_remote_images(urls: list[str], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for index, url in enumerate(urls, start=1):
        ext = ".png"
        if url.startswith("data:"):
            mime, content = parse_data_url(url)
            ext = mime_to_extension(mime)
            filename = out_dir / f"image-{index}{ext}"
            filename.write_bytes(content)
            files.append(filename)
            continue
        parsed = urllib.parse.urlparse(url)
        suffix = Path(parsed.path).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            ext = suffix
        filename = out_dir / f"image-{index}{ext}"
        download_file(url, filename)
        files.append(filename)
    return files


def save_base64_images(values: list[str], out_dir: Path, start_index: int = 1) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for offset, value in enumerate(values):
        index = start_index + offset
        if value.startswith("data:"):
            mime, content = parse_data_url(value)
            ext = mime_to_extension(mime)
        else:
            content = base64.b64decode(value)
            ext = ".png"
        filename = out_dir / f"image-{index}{ext}"
        filename.write_bytes(content)
        files.append(filename)
    return files


def save_generated_images(response: dict[str, Any], out_dir: Path) -> tuple[list[Path], list[str], int]:
    urls = extract_image_urls(response, required=False)
    files = save_remote_images(urls, out_dir) if urls else []
    base64_values = extract_image_base64s(response)
    if base64_values:
        files.extend(save_base64_images(base64_values, out_dir, start_index=len(files) + 1))
    if not files:
        raise RuntimeError(f"Provider returned no downloadable image data. Response keys: {sorted(response.keys())}")
    return files, urls, len(base64_values)

