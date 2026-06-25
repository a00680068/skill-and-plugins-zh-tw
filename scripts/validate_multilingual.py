from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LOCALES = {
    "zh-TW": {
        "html": "index.html",
        "lang": "zh-Hant",
        "json": "data/skills-and-connectors.zh-TW.json",
        "csv": "data/skills-and-connectors.zh-TW.csv",
    },
    "zh-CN": {
        "html": "index.zh-CN.html",
        "lang": "zh-Hans",
        "json": "data/skills-and-connectors.zh-CN.json",
        "csv": "data/skills-and-connectors.zh-CN.csv",
    },
    "en": {
        "html": "index.en.html",
        "lang": "en",
        "json": "data/skills-and-connectors.en.json",
        "csv": "data/skills-and-connectors.en.csv",
    },
    "ja": {
        "html": "index.ja.html",
        "lang": "ja",
        "json": "data/skills-and-connectors.ja.json",
        "csv": "data/skills-and-connectors.ja.csv",
    },
}

REQUIRED_READMES = ["README.md", "README.zh-CN.md", "README.en.md", "README.ja.md"]
REQUIRED_FIELDS = [
    "d",
    "g",
    "gd",
    "t",
    "en",
    "zh",
    "de",
    "resource_kind",
    "translation_type",
    "review_status",
    "mode_review_status",
    "type_reference_url",
    "type_reference_label",
    "mode_primary",
    "mode_confidence",
    "localization_locale",
    "localization_status",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def read_json(path: str) -> list[dict]:
    full = ROOT / path
    if not full.exists():
        fail(f"missing JSON: {path}")
    data = json.loads(full.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail(f"JSON is not a list: {path}")
    return data


def extract_embedded_data(html: str, file_name: str) -> list[dict]:
    match = re.search(r"const DATA=(\[.*?\]);\n\nlet activeDomain", html, re.S)
    if not match:
        fail(f"cannot find embedded DATA block: {file_name}")
    data = json.loads(match.group(1))
    if not isinstance(data, list):
        fail(f"embedded DATA is not a list: {file_name}")
    return data


def check_locale(locale: str, spec: dict, base_names: list[str]) -> None:
    html_path = ROOT / spec["html"]
    if not html_path.exists():
        fail(f"missing HTML: {spec['html']}")
    html = html_path.read_text(encoding="utf-8")

    if f'<html lang="{spec["lang"]}">' not in html:
        fail(f"wrong html lang for {locale}")
    if html.count('class="language-switcher"') != 1:
        fail(f"language switcher count is not 1 for {locale}")
    if html.count('aria-current="page"') != 1:
        fail(f"aria-current count is not 1 for {locale}")
    for target in ["index.html", "index.zh-CN.html", "index.en.html", "index.ja.html"]:
        if target not in html:
            fail(f"missing language link {target} in {spec['html']}")

    embedded = extract_embedded_data(html, spec["html"])
    file_data = read_json(spec["json"])
    if len(file_data) != 650:
        fail(f"{locale} JSON row count is {len(file_data)}, expected 650")
    if len(embedded) != 650:
        fail(f"{locale} embedded DATA row count is {len(embedded)}, expected 650")
    if [row["en"] for row in file_data] != base_names:
        fail(f"{locale} JSON English-name sequence differs from zh-TW")
    if [row["en"] for row in embedded] != base_names:
        fail(f"{locale} embedded English-name sequence differs from zh-TW")

    for index, row in enumerate(file_data):
        for field in REQUIRED_FIELDS:
            if not str(row.get(field, "")).strip():
                fail(f"{locale} row {index} missing field: {field}")
        if row.get("localization_locale") != locale:
            fail(f"{locale} row {index} has wrong localization_locale")
        if not str(row.get("localization_status", "")).strip():
            fail(f"{locale} row {index} missing localization_status")

    csv_path = ROOT / spec["csv"]
    if not csv_path.exists():
        fail(f"missing CSV: {spec['csv']}")
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) != 651:
        fail(f"{locale} CSV row count including header is {len(rows)}, expected 651")
    if len(rows[0]) < 20:
        fail(f"{locale} CSV header has too few columns")
    if any(len(row) != len(rows[0]) for row in rows[1:]):
        fail(f"{locale} CSV has ragged rows")

    print(f"PASS {locale}: 650 JSON rows, 650 embedded rows, 650 CSV data rows")


def main() -> int:
    for readme in REQUIRED_READMES:
        if not (ROOT / readme).exists():
            fail(f"missing README file: {readme}")

    cache_path = ROOT / "data" / "i18n-translation-cache.json"
    if not cache_path.exists():
        fail("missing i18n translation cache")
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    if len(cache.get("en", {})) < 2100:
        fail("English translation cache is incomplete")
    if len(cache.get("ja", {})) < 2100:
        fail("Japanese translation cache is incomplete")

    base = read_json(LOCALES["zh-TW"]["json"])
    if len(base) != 650:
        fail("zh-TW base row count is not 650")
    base_names = [row["en"] for row in base]

    for locale, spec in LOCALES.items():
        check_locale(locale, spec, base_names)

    generator = ROOT / "scripts" / "generate_multilingual.py"
    if not generator.exists():
        fail("missing generator script")

    print("PASS all multilingual validation checks")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
