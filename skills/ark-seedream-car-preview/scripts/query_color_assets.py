#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


DEFAULT_LIBRARY = Path(__file__).resolve().parents[1] / "references" / "color_assets.json"


def normalize(value: str) -> str:
    return "".join(ch.lower() for ch in " ".join((value or "").split()) if ch.isalnum())


def searchable(asset: dict) -> list[str]:
    names = asset.get("names", {})
    color = asset.get("color", {})
    return [
        asset.get("id", ""),
        asset.get("serial", ""),
        names.get("zh", ""),
        names.get("en", ""),
        *(names.get("aliases", []) or []),
        color.get("family", "") or "",
        asset.get("material", ""),
    ]


def compact(asset: dict) -> dict:
    prompt = asset.get("prompt", {})
    return {
        "id": asset.get("id"),
        "zh": asset.get("names", {}).get("zh"),
        "en": asset.get("names", {}).get("en"),
        "hex": asset.get("color", {}).get("hex"),
        "lab": asset.get("color", {}).get("lab"),
        "family": asset.get("color", {}).get("family"),
        "material": asset.get("material"),
        "swatch": asset.get("images", {}).get("swatch"),
        "prompt_args": {
            "--asset-id": asset.get("id"),
            "--color-name": prompt.get("color_name"),
            "--color-value": prompt.get("color_value"),
            "--finish": prompt.get("finish"),
            "--description": prompt.get("description"),
        },
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Search the vehicle wrap color asset library.")
    ap.add_argument("query", nargs="?", default="", help="Serial, Chinese name, English name, color family, or material.")
    ap.add_argument("--library", default=DEFAULT_LIBRARY.as_posix())
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--full", action="store_true", default=False, help="Print full matching asset records.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    library_path = Path(args.library).expanduser().resolve()
    payload = json.loads(library_path.read_text(encoding="utf-8"))
    needle = normalize(args.query)
    assets = payload.get("assets", [])
    if needle:
        assets = [
            asset
            for asset in assets
            if any(needle in normalize(str(value)) for value in searchable(asset) if value)
        ]
    assets = assets[: max(1, args.limit)]
    print(json.dumps(assets if args.full else [compact(asset) for asset in assets], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
