"""
process_paperreview_ai.py
=========================
Parses FARS paperreview.ai-format JSON review files and writes preprocessed
JSON to parsed/preprocessed.json.

FARS paperreview.ai format:
    {
      "paper_id": "<ID>",
      "success": true,
      "sections": {
        "weaknesses": "plain text...",
        "detailed_comments": "plain text...",
        "questions": "plain text...",
        ...
      },
      "numerical_score": 5.2,
      ...
    }

Sections extracted: weaknesses, detailed_comments, questions
Reviewer ID: "paperreview.ai"

Output format:
    {
      "<paper_id>": {
        "paperreview.ai": {
          "0": "First critique point.",
          ...
        }
      }
    }

Usage:
    python process_paperreview_ai.py

    Reads from  ../../arg_outputs/paperreview_ai/raw/
    Writes to   ../../arg_outputs/paperreview_ai/parsed/preprocessed.json
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from review_point_utils import extract_points

SCRIPT_DIR   = Path(__file__).parent
REVIEWER_DIR = (SCRIPT_DIR / "../../arg_outputs/paperreview_ai").resolve()
RAW_DIR      = REVIEWER_DIR / "raw"
PARSED_DIR   = REVIEWER_DIR / "parsed"

EXTRACT_FIELDS = ["weaknesses", "detailed_comments", "questions"]
REVIEWER_ID    = "paperreview.ai"


def parse_file(data: dict) -> dict:
    paper_id = data["paper_id"]
    sections = data.get("sections", {})
    points   = []

    for field in EXTRACT_FIELDS:
        text = sections.get(field, "")
        if text and text.strip():
            points.extend(extract_points(text))

    return {paper_id: {REVIEWER_ID: points}}


def to_indexed(parsed: dict) -> dict:
    out = {}
    for paper_id, reviewers in parsed.items():
        out[paper_id] = {}
        for reviewer_id, points in reviewers.items():
            out[paper_id][reviewer_id] = {str(i): pt for i, pt in enumerate(points)}
    return out


def main():
    if not RAW_DIR.exists():
        print(f"Error: {RAW_DIR} does not exist.")
        sys.exit(1)

    PARSED_DIR.mkdir(exist_ok=True)

    json_files = sorted(RAW_DIR.glob("*.json"))
    if not json_files:
        print(f"No .json files found in {RAW_DIR}")
        sys.exit(0)

    output: dict = {}

    for fpath in json_files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON error in {fpath.name}: {e}")
            continue

        if not data.get("success", False):
            print(f"  [SKIP] {fpath.name} — review not successful")
            continue

        parsed = parse_file(data)
        for paper_id, reviewers in parsed.items():
            output.setdefault(paper_id, {}).update(reviewers)

        print(f"  {fpath.name}")
        for paper_id, reviewers in parsed.items():
            for reviewer_id, points in reviewers.items():
                print(f"    {reviewer_id}: {len(points)} points")
                for i, pt in enumerate(points):
                    print(f"      [{i:02d}] {pt[:90]}{'…' if len(pt) > 90 else ''}")
        print()

    out_path = PARSED_DIR / "preprocessed.json"
    out_path.write_text(
        json.dumps(to_indexed(output), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✓  Written → {out_path}")


if __name__ == "__main__":
    main()
