#!/usr/bin/env python3
"""키워드가 제목 또는 본문에 포함된 보고서 장을 CSV로 저장한다."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "장데이터.json"
INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def output_name(keyword: str) -> str:
    safe_keyword = INVALID_FILENAME_CHARS.sub("_", keyword).strip(" .")
    return f"결과_{safe_keyword or '검색'}.csv"


def load_chapters(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig") as file:
        chapters = json.load(file)
    if not isinstance(chapters, list):
        raise ValueError("장데이터.json의 최상위 값은 배열이어야 합니다.")
    required = {"장", "제목", "본문"}
    if any(not isinstance(row, dict) or not required <= row.keys() for row in chapters):
        raise ValueError("모든 장은 장, 제목, 본문 필드를 포함해야 합니다.")
    return chapters


def main() -> int:
    parser = argparse.ArgumentParser(description="보고서 장을 키워드로 검색해 CSV로 저장합니다.")
    parser.add_argument("keyword", help="제목 또는 본문에서 찾을 키워드")
    args = parser.parse_args()
    keyword = args.keyword.strip()
    if not keyword:
        parser.error("키워드는 공백일 수 없습니다.")

    try:
        chapters = load_chapters(DATA_PATH)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"[ERROR] 장데이터를 읽을 수 없습니다: {error}", file=sys.stderr)
        return 1

    query = keyword.casefold()
    matches = [
        row for row in chapters
        if query in str(row["제목"]).casefold() or query in str(row["본문"]).casefold()
    ]
    output_path = Path.cwd() / output_name(keyword)
    try:
        with output_path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["장", "제목", "본문"])
            writer.writeheader()
            writer.writerows(matches)
    except OSError as error:
        print(f"[ERROR] CSV를 저장할 수 없습니다: {error}", file=sys.stderr)
        return 1

    print(f"[OK] {len(matches)}건 저장 → {output_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
