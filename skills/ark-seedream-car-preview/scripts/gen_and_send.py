#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate a vehicle wrap preview and send it back through OpenClaw.")
    ap.add_argument("--target", required=True, help="Recipient target for openclaw message send.")
    ap.add_argument("--channel", default="openclaw-weixin", help="OpenClaw channel for status + final delivery.")
    ap.add_argument("--account", default="", help="Optional channel account id for multi-account delivery.")
    ap.add_argument("--message", default="这是基于实车图和色卡生成的车膜预览图", help="Caption sent with the final image.")
    ap.add_argument(
        "--status-message",
        default="已收到你的需求，正在生成车膜预览图，完成后会直接把图片发给你。",
        help="Immediate confirmation message sent before generation starts.",
    )
    ap.add_argument("--skip-status-message", action="store_true", default=False, help="Do not send an immediate confirmation message.")
    ap.add_argument("--provider", default="", help="Provider id or auto. Provider details come from WRAP_PROVIDER_CHAIN / IMAGE_RELAY_BASE_URL.")
    ap.add_argument("--base-url", default="", help="OpenAI-compatible base URL.")
    ap.add_argument("--prompt", default="", help="Explicit prompt override.")
    ap.add_argument("--model", default="")
    ap.add_argument("--vehicle-ref", action="append", default=[])
    ap.add_argument("--color-ref", action="append", default=[])
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--asset-id", default="")
    ap.add_argument("--asset-library", default="")
    ap.add_argument("--color-name", default="")
    ap.add_argument("--color-code", default="")
    ap.add_argument("--color-value", default="")
    ap.add_argument("--finish", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--size", default="")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"], help="Image generation quality.")
    ap.add_argument("--response-format", default="b64_json", choices=["url", "b64_json"])
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--dry-run", action="store_true", default=False, help="Resolve refs and prompt without calling the image provider.")
    ap.add_argument("--dry-run-send", action="store_true", default=False, help="Print planned OpenClaw send commands without sending messages.")
    return ap.parse_args()


def build_send_cmd(
    *,
    channel: str,
    target: str,
    account: str,
    message: str,
    media_path: str = "",
) -> list[str]:
    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        channel,
        "--target",
        target,
    ]
    if account:
        cmd.extend(["--account", account])
    if message:
        cmd.extend(["--message", message])
    if media_path:
        cmd.extend(["--media", media_path])
    return cmd


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parent
    gen_script = skill_dir / "gen.py"

    status_cmd = build_send_cmd(
        channel=args.channel,
        target=args.target,
        account=args.account,
        message=args.status_message,
    )
    if not args.skip_status_message and args.status_message and not args.dry_run_send:
        status_proc = subprocess.run(
            status_cmd,
            capture_output=True,
            text=True,
        )
        if status_proc.returncode != 0:
            sys.stderr.write(f"[warn] status message send failed: {status_proc.stderr or status_proc.stdout}\n")

    cmd = [
        sys.executable,
        gen_script.as_posix(),
    ]
    if args.provider:
        cmd.extend(["--provider", args.provider])
    if args.base_url:
        cmd.extend(["--base-url", args.base_url])
    if args.model:
        cmd.extend(["--model", args.model])
    if args.size:
        cmd.extend(["--size", args.size])
    if args.quality:
        cmd.extend(["--quality", args.quality])
    if args.response_format:
        cmd.extend(["--response-format", args.response_format])
    if args.dry_run or args.dry_run_send:
        cmd.append("--dry-run")
    if args.prompt:
        cmd.extend(["--prompt", args.prompt])
    if args.out_dir:
        cmd.extend(["--out-dir", args.out_dir])
    if args.asset_id:
        cmd.extend(["--asset-id", args.asset_id])
    if args.asset_library:
        cmd.extend(["--asset-library", args.asset_library])
    for name, value in (
        ("--color-name", args.color_name),
        ("--color-code", args.color_code),
        ("--color-value", args.color_value),
        ("--finish", args.finish),
        ("--description", args.description),
    ):
        if value:
            cmd.extend([name, value])
    for ref in args.vehicle_ref:
        cmd.extend(["--vehicle-ref", ref])
    for ref in args.color_ref:
        cmd.extend(["--color-ref", ref])
    for ref in args.ref:
        cmd.extend(["--ref", ref])

    gen_proc = subprocess.run(cmd, capture_output=True, text=True)
    if gen_proc.returncode != 0:
        sys.stderr.write(gen_proc.stderr or gen_proc.stdout)
        return gen_proc.returncode

    result = json.loads(gen_proc.stdout)
    if args.dry_run or args.dry_run_send:
        send_cmd = build_send_cmd(
            channel=args.channel,
            target=args.target,
            account=args.account,
            message=args.message,
            media_path="<generated image path>",
        )
        print(
            json.dumps(
                {
                    "dry_run_send": args.dry_run_send,
                    "channel": args.channel,
                    "target": args.target,
                    "generated": result,
                    "status_cmd": status_cmd,
                    "send_cmd": send_cmd,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    media_path = result["files"][0]
    send_cmd = build_send_cmd(
        channel=args.channel,
        target=args.target,
        account=args.account,
        message=args.message,
        media_path=media_path,
    )
    send_proc = subprocess.run(send_cmd, capture_output=True, text=True)
    if send_proc.returncode != 0:
        sys.stderr.write(send_proc.stderr or send_proc.stdout)
        return send_proc.returncode

    print(
        json.dumps(
            {
                "channel": args.channel,
                "target": args.target,
                "generated": result,
                "send_stdout": send_proc.stdout.strip(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
