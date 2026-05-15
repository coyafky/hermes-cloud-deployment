#!/usr/bin/env python3
"""Validate the 有膜有漾 sales-agent knowledge assets."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "knowledge-base" / "ymyy-sales-agent" / "ymyy-service-manual.jsonl"

REQUIRED_FILES = [
    ROOT / "hermes-profile" / "SOUL.md",
    ROOT / "hermes-profile" / "MEMORY.md",
    ROOT / "skills" / "recommend-film-product" / "SKILL.md",
    ROOT / "skills" / "handle-film-objections" / "SKILL.md",
    ROOT / "skills" / "write-sales-followup" / "SKILL.md",
    ROOT / "skills" / "ask-with-mom-test" / "SKILL.md",
    ROOT / "skills" / "ask-with-mom-test" / "references" / "good-bad-car-film-questions.md",
    ROOT / "skills" / "ask-with-mom-test" / "references" / "car-film-customer-question-bank.md",
    ROOT / "skills" / "ask-with-mom-test" / "references" / "mom-test-vs-spin.md",
    ROOT / "skills" / "diagnose-with-spin-selling" / "SKILL.md",
    ROOT / "skills" / "diagnose-with-spin-selling" / "references" / "car-film-spin-question-bank.md",
    ROOT / "skills" / "diagnose-with-spin-selling" / "references" / "spin-framework-for-ymyy.md",
    ROOT / "skills" / "answer-customer-faq-transparently" / "SKILL.md",
    ROOT / "skills" / "answer-customer-faq-transparently" / "references" / "big-5-car-film-faq.md",
    ROOT / "skills" / "answer-customer-faq-transparently" / "references" / "transparent-answer-templates.md",
    ROOT / "skills" / "answer-customer-faq-transparently" / "references" / "assignment-selling-for-car-film.md",
    ROOT / "skills" / "answer-customer-faq-transparently" / "references" / "skill-collaboration-flow.md",
    ROOT / "skills" / "strengthen-sales-wording-with-influence" / "SKILL.md",
    ROOT / "skills" / "strengthen-sales-wording-with-influence" / "references" / "influence-principles-for-car-film.md",
    ROOT / "skills" / "strengthen-sales-wording-with-influence" / "references" / "sales-wording-enhancement-templates.md",
    ROOT / "skills" / "strengthen-sales-wording-with-influence" / "references" / "ethical-boundaries-and-banned-wording.md",
    ROOT / "skills" / "strengthen-sales-wording-with-influence" / "references" / "skill-collaboration-flow.md",
    ROOT / "skills" / "negotiate-with-tactical-empathy" / "SKILL.md",
    ROOT / "skills" / "negotiate-with-tactical-empathy" / "references" / "tactical-empathy-for-car-film.md",
    ROOT / "skills" / "negotiate-with-tactical-empathy" / "references" / "price-negotiation-templates.md",
    ROOT / "skills" / "negotiate-with-tactical-empathy" / "references" / "calibrated-questions-bank.md",
    ROOT / "skills" / "negotiate-with-tactical-empathy" / "references" / "ethical-boundaries.md",
    KB_PATH,
    ROOT / "knowledge-base" / "ymyy-sales-agent" / "README.md",
    ROOT / "knowledge-base" / "ymyy-sales-agent" / "source-audit.md",
    ROOT / "knowledge-base" / "ymyy-sales-agent" / "queries.md",
    ROOT / "docs" / "ymyy-sales-agent-implementation.md",
]

REQUIRED_IDS = {
    "ymyy-brand-profile",
    "ymyy-ppf-ym60",
    "ymyy-solar-chunfen-k7-c15",
    "ymyy-aftercare-ppf-color-change",
    "ymyy-sales-script-price-policy",
}

REQUIRED_CATEGORIES = {
    "brand_profile",
    "product_ppf",
    "product_solar_film",
    "product_color_change",
    "aftercare_sop",
    "sales_script",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail(f"missing files: {', '.join(missing)}")

    records = []
    seen_ids = set()
    for line_number, line in enumerate(KB_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON on line {line_number}: {exc}")

        for key in ["id", "title", "category", "source", "source_page", "audience", "guardrails"]:
            if key not in record:
                fail(f"record on line {line_number} missing required key {key!r}")

        if record["id"] in seen_ids:
            fail(f"duplicate id: {record['id']}")
        seen_ids.add(record["id"])
        records.append(record)

    if len(records) < 20:
        fail(f"expected at least 20 knowledge records, found {len(records)}")

    missing_ids = REQUIRED_IDS - seen_ids
    if missing_ids:
        fail(f"missing required ids: {', '.join(sorted(missing_ids))}")

    categories = {record["category"] for record in records}
    missing_categories = REQUIRED_CATEGORIES - categories
    if missing_categories:
        fail(f"missing categories: {', '.join(sorted(missing_categories))}")

    ym60 = next(record for record in records if record["id"] == "ymyy-ppf-ym60")
    if ym60["specs"].get("质保期") != "3年":
        fail("YM-60 warranty must be 3年")
    if ym60["source_page"] != 8:
        fail("YM-60 source_page must be 8")

    chunfen = next(record for record in records if record["id"] == "ymyy-solar-chunfen-k7-c15")
    if "K7" not in chunfen["specs"] or "C15" not in chunfen["specs"]:
        fail("春分套餐 must include K7 and C15 specs")
    if chunfen["source_page"] != 18:
        fail("春分套餐 source_page must be 18")

    aftercare = next(record for record in records if record["id"] == "ymyy-aftercare-ppf-color-change")
    if "三天内不要高速行驶" not in aftercare["summary"]:
        fail("aftercare entry must mention no high-speed driving within three days")

    print(f"OK: validated {len(records)} records across {len(categories)} categories")


if __name__ == "__main__":
    main()
