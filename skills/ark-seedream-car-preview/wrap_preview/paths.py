from __future__ import annotations

import datetime as dt
from pathlib import Path


def skill_base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def profile_base_dir() -> Path | None:
    skill_dir = skill_base_dir()
    if skill_dir.parent.name == "skills":
        return skill_dir.parent.parent
    return None


def default_asset_library() -> Path:
    return skill_base_dir() / "references" / "color_assets.json"


def default_out_dir() -> Path:
    now = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base = Path.cwd() / "tmp"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"ark-seedream-car-preview-{now}"

