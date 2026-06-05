from __future__ import annotations

import base64
import urllib.request
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse


ImageDimensions = tuple[int, int]


def read_image_dimensions(ref: str) -> ImageDimensions | None:
    try:
        from PIL import Image

        parsed = urlparse(ref)
        if parsed.scheme == "data":
            _, encoded = ref.split(",", 1)
            with Image.open(BytesIO(base64.b64decode(encoded))) as image:
                return image.size
        if parsed.scheme in {"http", "https"}:
            with urllib.request.urlopen(ref, timeout=30) as resp:
                with Image.open(BytesIO(resp.read())) as image:
                    return image.size
        path = Path(ref).expanduser().resolve()
        if not path.is_file():
            return None
        with Image.open(path) as image:
            return image.size
    except Exception:
        return None


def read_file_dimensions(path: Path) -> ImageDimensions | None:
    return read_image_dimensions(path.as_posix())


def read_files_dimensions(files: list[Path]) -> list[ImageDimensions | None]:
    return [read_file_dimensions(path) for path in files]


def aspect_ratio(dimensions: ImageDimensions) -> float:
    width, height = dimensions
    return width / height


def aspect_ratio_matches(actual: ImageDimensions | None, target: ImageDimensions | None, tolerance: float = 0.01) -> bool:
    if not actual or not target:
        return True
    actual_width, actual_height = actual
    target_width, target_height = target
    if actual_width <= 0 or actual_height <= 0 or target_width <= 0 or target_height <= 0:
        return False
    return abs(aspect_ratio(actual) - aspect_ratio(target)) <= tolerance


def assert_output_aspect_ratios(files: list[Path], target: ImageDimensions | None) -> list[ImageDimensions | None]:
    dimensions = read_files_dimensions(files)
    if not target:
        return dimensions
    mismatches = [
        (path.as_posix(), actual)
        for path, actual in zip(files, dimensions)
        if not aspect_ratio_matches(actual, target)
    ]
    if mismatches:
        details = "; ".join(f"{path}: {actual or 'unknown'}" for path, actual in mismatches)
        raise RuntimeError(
            f"Generated image aspect ratio does not match customer vehicle image. "
            f"Expected aspect ratio from {target[0]}x{target[1]}; got {details}. "
            "Do not send this result to the customer or Feishu."
        )
    return dimensions
