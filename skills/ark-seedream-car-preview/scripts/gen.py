#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wrap_preview.models import WrapPreviewRequest
from wrap_preview.service import generate_wrap_preview


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate realistic vehicle wrap preview images via OpenAI-compatible provider failover.")
    ap.add_argument("--provider", default=os.environ.get("IMAGE_PROVIDER", "auto"), help="Provider id or auto. Provider details come from WRAP_PROVIDER_CHAIN / IMAGE_RELAY_BASE_URL.")
    ap.add_argument("--base-url", default=os.environ.get("IMAGE_RELAY_BASE_URL", ""), help="OpenAI-compatible base URL, for example https://4sapi.com/v1.")
    ap.add_argument("--prompt", default="", help="Explicit prompt. When omitted, a strict car-wrap preview prompt is built from the structured fields.")
    ap.add_argument("--model", default="", help="Image model id. Defaults to gpt-image-2.")
    ap.add_argument("--vehicle-ref", action="append", default=[], help="Customer vehicle image path or URL. Can be repeated.")
    ap.add_argument("--color-ref", action="append", default=[], help="Color-card image path or URL. Can be repeated.")
    ap.add_argument("--ref", action="append", default=[], help="Extra reference image path or URL. Can be repeated.")
    ap.add_argument("--asset-id", default="", help="Lookup a color asset by serial/code/name from references/color_assets.json.")
    ap.add_argument("--asset-library", default="", help="Color asset library JSON path. Defaults to references/color_assets.json.")
    ap.add_argument("--color-name", default="", help="Target wrap color name.")
    ap.add_argument("--color-code", default="", help="Color code / swatch id.")
    ap.add_argument("--color-value", default="", help="Auxiliary color label, usually the HEX written on the color card. The preview swatch image is the primary color reference.")
    ap.add_argument("--finish", default="", help="Finish like matte, gloss, metallic, pearl.")
    ap.add_argument("--description", default="", help="Extra descriptive text for the color.")
    ap.add_argument("--size", default="", help="Output size, for example auto, 1024x1024, 1536x1024, 1024x1536.")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"], help="Image generation quality.")
    ap.add_argument("--response-format", default="b64_json", choices=["url", "b64_json"], help="Provider response format. b64_json avoids protected temporary URL download failures.")
    ap.add_argument("--out-dir", default="", help="Output directory. Default: ./tmp/ark-seedream-car-preview-<ts>")
    ap.add_argument("--dry-run", action="store_true", default=False, help="Resolve assets and print the final prompt payload without calling the image provider.")
    return ap.parse_args()


def request_from_args(args: argparse.Namespace) -> WrapPreviewRequest:
    return WrapPreviewRequest(
        provider=args.provider,
        base_url=args.base_url,
        prompt=args.prompt,
        model=args.model,
        vehicle_refs=args.vehicle_ref,
        color_refs=args.color_ref,
        extra_refs=args.ref,
        asset_id=args.asset_id,
        asset_library=args.asset_library,
        color_name=args.color_name,
        color_code=args.color_code,
        color_value=args.color_value,
        finish=args.finish,
        description=args.description,
        size=args.size,
        quality=args.quality,
        response_format=args.response_format,
        out_dir=Path(args.out_dir).expanduser() if args.out_dir else None,
        dry_run=args.dry_run,
    )


def main() -> int:
    result = generate_wrap_preview(request_from_args(parse_args()))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as err:
        print(str(err), file=sys.stderr)
        raise SystemExit(1)
