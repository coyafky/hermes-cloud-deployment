#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
XINGHU_BASE_URL = "https://xinghuapi.com/v1"
DEFAULT_ARK_MODEL = "doubao-seedream-4-5-251128"
DEFAULT_XINGHU_MODEL = "gpt-image-2"
DEFAULT_ARK_SIZE = "2K"
DEFAULT_XINGHU_SIZE = "auto"


def default_out_dir() -> Path:
    now = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base = Path.cwd() / "tmp"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"ark-seedream-car-preview-{now}"


def skill_base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


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


def profile_base_dir() -> Path | None:
    skill_dir = skill_base_dir()
    if skill_dir.parent.name == "skills":
        return skill_dir.parent.parent
    return None


def candidate_env_files() -> list[Path]:
    skill_dir = skill_base_dir()
    files = [skill_dir / ".env"]
    profile_dir = profile_base_dir()
    if profile_dir:
        files.append(profile_dir / ".env")
    return files


def load_skill_local_api_key(provider: str) -> str:
    skill_dir = skill_base_dir()

    # Prefer a skill-local JSON file so new conversations do not depend on
    # shell session state or external OpenClaw auth profiles.
    local_json = skill_dir / ".local.json"
    if local_json.is_file():
        try:
            payload = json.loads(local_json.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        if provider == "xinghu":
            keys = ("xinghu_api_key", "xinghuapi_api_key", "chatgpt_image_api_key", "gpt_image_api_key")
        else:
            keys = ("ark_api_key", "api_key", "volcano_engine_api_key")
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    if provider == "xinghu":
        env_names = {"XINGHU_API_KEY", "XINGHUAPI_API_KEY", "XINGHU_CLOUD_API_KEY", "CHATGPT_IMAGE_API_KEY", "GPT_IMAGE_API_KEY"}
    else:
        env_names = {"ARK_API_KEY", "VOLCANO_ENGINE_API_KEY"}
    for env_path in candidate_env_files():
        values = read_env_file(env_path)
        for name in env_names:
            value = values.get(name, "")
            if value:
                return value

    return ""


def load_api_key(provider: str) -> str:
    provider = normalize_provider(provider)
    if provider == "xinghu":
        env_names = ("XINGHU_API_KEY", "XINGHUAPI_API_KEY", "XINGHU_CLOUD_API_KEY", "CHATGPT_IMAGE_API_KEY", "GPT_IMAGE_API_KEY")
    else:
        env_names = ("ARK_API_KEY", "VOLCANO_ENGINE_API_KEY")

    for env_name in env_names:
        value = (os.environ.get(env_name) or "").strip()
        if value:
            return value

    value = load_skill_local_api_key(provider)
    if value:
        return value

    if provider == "xinghu":
        return ""

    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            config = {}
        profiles = config.get("auth", {}).get("profiles", {})
        for profile in profiles.values():
            provider = (profile.get("provider") or "").strip().lower()
            if provider in {"volcengine", "volcengine-plan", "doubao"}:
                api_key = (profile.get("apiKey") or profile.get("api_key") or "").strip()
                if api_key:
                    return api_key

    volc_config = Path.home() / ".volcengine" / "config.json"
    if volc_config.is_file():
        try:
            payload = json.loads(volc_config.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        for key in ("ark_api_key", "api_key", "apikey"):
            value = (payload.get(key) or "").strip() if isinstance(payload.get(key), str) else ""
            if value:
                return value
    return ""


def normalize_provider(provider: str) -> str:
    value = (provider or "").strip().lower()
    if value in {"xinghu", "xinghuapi", "chatgpt-image2", "chatgpt-image-2", "gpt-image-2"}:
        return "xinghu"
    return "ark"


def default_model_for(provider: str) -> str:
    return DEFAULT_XINGHU_MODEL if normalize_provider(provider) == "xinghu" else DEFAULT_ARK_MODEL


def default_size_for(provider: str) -> str:
    return DEFAULT_XINGHU_SIZE if normalize_provider(provider) == "xinghu" else DEFAULT_ARK_SIZE


def normalize_base_url(base_url: str) -> str:
    return (base_url or XINGHU_BASE_URL).rstrip("/")


def is_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https", "data"}


def path_to_data_url_base64(path_str: str) -> str:
    import base64

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


def normalize_text(value: str) -> str:
    return " ".join((value or "").split()).strip()


def default_asset_library() -> Path:
    return skill_base_dir() / "references" / "color_assets.json"


def lookup_key(value: str) -> str:
    return "".join(ch.lower() for ch in normalize_text(value) if ch.isalnum())


def load_color_asset(asset_library: str, asset_id: str) -> tuple[dict, Path]:
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


def apply_color_asset(args: argparse.Namespace) -> dict | None:
    if not args.asset_id:
        return None

    asset, library_path = load_color_asset(args.asset_library, args.asset_id)
    prompt_fields = asset.get("prompt", {})
    if not args.color_name:
        args.color_name = prompt_fields.get("color_name", "") or asset.get("names", {}).get("zh", "")
    if not args.color_code:
        args.color_code = prompt_fields.get("color_code", "") or asset.get("serial", "")
    if not args.color_value:
        hex_value = asset.get("color", {}).get("hex", "")
        lab = asset.get("color", {}).get("lab", {})
        lab_value = ""
        if lab:
            lab_value = f"Lab(L={lab.get('L')}, a={lab.get('a')}, b={lab.get('b')})"
        args.color_value = prompt_fields.get("color_value", "") or hex_value or lab_value
    if not args.finish:
        args.finish = prompt_fields.get("finish", "") or asset.get("finish", {}).get("prompt_label", "")
    if not args.description:
        args.description = prompt_fields.get("description", "")

    swatch = asset.get("images", {}).get("swatch")
    if swatch:
        swatch_path = (library_path.parent / swatch).resolve()
        if swatch_path.is_file() and swatch_path.as_posix() not in args.color_ref:
            args.color_ref.append(swatch_path.as_posix())

    return {
        "id": asset.get("id"),
        "serial": asset.get("serial"),
        "name": asset.get("names", {}).get("zh"),
        "hex": asset.get("color", {}).get("hex"),
        "lab": asset.get("color", {}).get("lab"),
        "swatch": swatch,
        "swatch_path": swatch_path.as_posix() if swatch and swatch_path.is_file() else None,
        "reference_strategy": "vehicle_image_plus_preview_swatch_image",
        "library": library_path.as_posix(),
    }


def validate_reference_images(args: argparse.Namespace, raw_refs: list[str]) -> None:
    if not args.vehicle_ref:
        raise ValueError("Missing --vehicle-ref. The car-wrap workflow must use the customer's vehicle image as the first reference.")
    if not args.color_ref:
        raise ValueError("Missing preview color-card image. Use --asset-id with an asset that has images.swatch, or pass --color-ref. HEX/Lab-only generation is disabled.")
    if len(raw_refs) < 2:
        raise ValueError("The car-wrap workflow requires two image references: customer vehicle image + preview color-card image.")


def build_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return normalize_text(args.prompt)

    color_name = args.color_name or "客户选定车膜颜色"
    color_code = args.color_code or "未提供"
    color_value = args.color_value or "未提供"
    finish = args.finish or "未提供"
    description = args.description or "无"
    color_value_label = "HEX 辅助标注" if color_value.startswith("#") else "色值辅助标注"

    parts = [
        "请以客户提供的实车照片和 preview 色卡图为基础进行高真实度效果图生成，并严格采用图像参考完成车膜改色。",
        "任务目标：将客户所选车膜颜色，真实、自然地呈现在客户车辆上，输出一张接近实拍效果的贴膜预览图，方便客户确认上车后的视觉效果。",
        "图像参考使用规则：客户车辆照片是唯一车辆主体参考；preview 色卡图是目标车膜颜色和膜面视觉效果的主要颜色参考。不要只根据文字、HEX 或 Lab 猜测颜色，也不要用 Lab 重新换算目标颜色。",
        "执行要求：以客户车辆原图为唯一主体基础，保持车辆品牌、车型、车身结构、轮毂、车灯、车窗、角度、透视关系、拍摄场景、背景环境完全不变。",
        f"严格参考随输入图像提供的 preview 色卡图进行贴膜效果呈现，以色卡图的可见颜色为主，色号和数值只用于辅助识别。目标车膜颜色：{color_name}。色卡编号：{color_code}。{color_value_label}：{color_value}。材质说明：{finish}。补充描述：{description}。",
        "仅修改需要贴膜覆盖的区域颜色与材质表现，不要改变未贴膜区域。",
        "保留原车照片中的真实光影、反射、高光、阴影、金属质感、环境倒影，使结果看起来像真实施工后的实拍照片。",
        "如果该膜属于哑光、亮光、金属、珠光、变色龙等材质，请准确体现对应膜面质感。",
        "不要改变车辆外观套件，不要修改车牌、轮胎、玻璃、门把手、车灯、内饰，不要新增或删除任何部件。",
        "不要美化成概念图，不要插画风，不要海报风，不要夸张渲染，必须是写实商业修图效果。",
        "输出结果需干净、高清、自然，适合作为给客户确认的施工预览图。",
        "约束重点：只换膜色，不换车。只做真实贴膜效果，不做重设计。保持原图构图、背景、光线、细节一致。",
        "最终效果必须像同一辆车在同一地点贴完膜后重新拍摄的照片。",
        "Same vehicle, same location, same composition, same camera angle, same lens perspective, same background, same lighting direction, same reflections, same wheel position, same trim details. Only the wrap-covered painted panels may change color and finish. Everything else must remain identical to the original photo. Realistic automotive photography, no extra text.",
    ]
    return " ".join(parts)


def post_json(url: str, api_key: str, payload: dict, provider_label: str) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=body,
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{provider_label} image generation failed ({err.code}): {detail}") from err


def request_ark_images(
    api_key: str,
    model: str,
    prompt: str,
    refs: list[str],
    size: str,
    watermark: bool,
    response_format: str,
) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "response_format": response_format,
        "stream": False,
        "watermark": watermark,
        "sequential_image_generation": "disabled",
    }
    if refs:
        payload["image"] = refs

    return post_json(ARK_API_URL, api_key, payload, "Ark")


def request_xinghu_images(
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    refs: list[str],
    size: str,
    quality: str,
    response_format: str,
) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "response_format": response_format,
    }
    if refs:
        # Xinghu's GPTImage-2 relay follows an OpenAI-compatible path, while its
        # reference-image docs accept image URLs or base64 data. Keep the same
        # two-image order used by the Hermes skill: vehicle first, swatch second.
        payload["image"] = refs

    url = f"{normalize_base_url(base_url)}/images/generations"
    return post_json(url, api_key, payload, "Xinghu GPTImage-2")


def extract_image_urls(payload: dict, required: bool = True) -> list[str]:
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

    def walk(value: object, key_hint: str = "") -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in base64_keys and isinstance(item, str) and item.strip():
                    values.append(item.strip())
                else:
                    walk(item, key)
        elif isinstance(value, list):
            for item in value:
                walk(item, key_hint)

    walk(payload)
    return values


def mime_to_extension(mime: str) -> str:
    if mime == "image/jpeg":
        return ".jpg"
    if mime == "image/webp":
        return ".webp"
    return ".png"


def parse_data_url(data_url: str) -> tuple[str, bytes]:
    import base64

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
    import base64

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


def save_generated_images(response: dict, out_dir: Path) -> tuple[list[Path], list[str], int]:
    urls = extract_image_urls(response, required=False)
    files = save_remote_images(urls, out_dir) if urls else []
    base64_values = extract_image_base64s(response)
    if base64_values:
        files.extend(save_base64_images(base64_values, out_dir, start_index=len(files) + 1))
    if not files:
        raise RuntimeError(f"Provider returned no downloadable image data. Response keys: {sorted(response.keys())}")
    return files, urls, len(base64_values)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate realistic vehicle wrap preview images via Ark Seedream or Xinghu GPTImage-2.")
    ap.add_argument("--provider", default=os.environ.get("IMAGE_PROVIDER", "xinghu"), choices=["ark", "xinghu"], help="Image provider. Defaults to xinghu for the ChatGPT Image2 relay.")
    ap.add_argument("--base-url", default=os.environ.get("XINGHU_BASE_URL", XINGHU_BASE_URL), help="Xinghu OpenAI-compatible base URL.")
    ap.add_argument("--prompt", default="", help="Explicit prompt. When omitted, a strict car-wrap preview prompt is built from the structured fields.")
    ap.add_argument("--model", default="", help="Image model id. Defaults to provider model.")
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
    ap.add_argument("--size", default="", help="Output size, for example auto, 1024x1024, 1536x1024, 1024x1536, 2K.")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"], help="Xinghu GPTImage-2 quality.")
    ap.add_argument("--response-format", default="url", choices=["url", "b64_json"], help="Provider response format.")
    ap.add_argument("--watermark", action="store_true", default=False, help="Request provider watermark.")
    ap.add_argument("--out-dir", default="", help="Output directory. Default: ./tmp/ark-seedream-car-preview-<ts>")
    ap.add_argument("--dry-run", action="store_true", default=False, help="Resolve assets and print the final prompt payload without calling the image provider.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    args.provider = normalize_provider(args.provider)
    args.model = args.model or default_model_for(args.provider)
    args.size = args.size or default_size_for(args.provider)
    cwd = Path.cwd().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else default_out_dir().resolve()
    color_asset = apply_color_asset(args)
    prompt = build_prompt(args)
    raw_refs = args.vehicle_ref + args.color_ref + args.ref
    validate_reference_images(args, raw_refs)

    if args.dry_run:
        result = {
            "dry_run": True,
            "provider": args.provider,
            "base_url": normalize_base_url(args.base_url) if args.provider == "xinghu" else ARK_API_URL,
            "prompt": prompt,
            "model": args.model,
            "size": args.size,
            "quality": args.quality if args.provider == "xinghu" else None,
            "response_format": args.response_format,
            "refs": raw_refs,
            "reference_strategy": "vehicle_image_plus_preview_swatch_image",
            "out_dir": out_dir.as_posix(),
            "color_asset": color_asset,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    api_key = load_api_key(args.provider)
    if not api_key:
        if args.provider == "xinghu":
            print("Missing XINGHU_API_KEY / XINGHUAPI_API_KEY / CHATGPT_IMAGE_API_KEY. Add the relay key to the profile .env or skill .env.", file=sys.stderr)
        else:
            print("Missing ARK_API_KEY / VOLCANO_ENGINE_API_KEY and no Volcengine key found in ~/.openclaw/openclaw.json", file=sys.stderr)
        return 2

    refs = normalize_refs(raw_refs)

    if args.provider == "xinghu":
        response = request_xinghu_images(
            api_key=api_key,
            base_url=args.base_url,
            model=args.model,
            prompt=prompt,
            refs=refs,
            size=args.size,
            quality=args.quality,
            response_format=args.response_format,
        )
    else:
        response = request_ark_images(
            api_key=api_key,
            model=args.model,
            prompt=prompt,
            refs=refs,
            size=args.size,
            watermark=args.watermark,
            response_format=args.response_format,
        )

    files, urls, base64_count = save_generated_images(response, out_dir)
    relative_files = [relative_path_string(path, cwd) for path in files]
    result = {
        "provider": args.provider,
        "base_url": normalize_base_url(args.base_url) if args.provider == "xinghu" else ARK_API_URL,
        "prompt": prompt,
        "model": args.model,
        "size": args.size,
        "quality": args.quality if args.provider == "xinghu" else None,
        "files": [path.as_posix() for path in files],
        "relative_files": relative_files,
        "media_tokens": [f"MEDIA:{path}" for path in relative_files],
        "out_dir": out_dir.as_posix(),
        "color_asset": color_asset,
        "response_keys": sorted(response.keys()),
        "image_urls": urls,
        "base64_images": base64_count,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as err:
        print(str(err), file=sys.stderr)
        raise SystemExit(1)
