from __future__ import annotations


def normalize_text(value: str) -> str:
    return " ".join((value or "").split()).strip()


def lookup_key(value: str) -> str:
    return "".join(ch.lower() for ch in normalize_text(value) if ch.isalnum())

