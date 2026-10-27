"""
process_human_reviews.py
========================
Parses nlpeer-format human review JSON files and writes preprocessed JSON
to parsed/preprocessed.json in the same reviewer folder.

Filename convention:
    <PAPER_ID>_human_reviews.json

Sections extracted: weaknesses, questions
All reviewers in the file are included (all are human in nlpeer format).

Output format:
    {
      "<paper_id>": {
        "<reviewer_id>": {
          "0": "First critique point.",
          ...
        }
      }
    }

Usage:
    python process_human_reviews.py

    Reads from  ../../arg_outputs/human_reviews/raw/
    Writes to   ../../arg_outputs/human_reviews/parsed/preprocessed.json
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from review_point_utils import extract_points

SCRIPT_DIR   = Path(__file__).parent
REVIEWER_DIR = (SCRIPT_DIR / "../../arg_outputs/human_reviews").resolve()
RAW_DIR      = REVIEWER_DIR / "raw"
PARSED_DIR   = REVIEWER_DIR / "parsed"

EXTRACT_FIELDS = ["weaknesses", "questions", "limitations"]


def parse_review_json(data: dict) -> dict:
    paper_id = data["paper_id"]
    result   = {}
    for review in data.get("reviews", []):
        reviewer_id = review.get("reviewer_id", "unknown")
        points = []
        for field in EXTRACT_FIELDS:
            text = review.get(field, "")
            if text and text.strip():
                points.extend(extract_points(text))
        if points:
            result.setdefault(paper_id, {})[reviewer_id] = points
    return {paper_id: result.get(paper_id, {})}


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

        parsed = parse_review_json(data)
        for paper_id, reviewers in parsed.items():
            output.setdefault(paper_id, {}).update(reviewers)

        print(f"  {fpath.name}")
        for paper_id, reviewers in parsed.items():
            for reviewer_id, points in reviewers.items():
                print(f"    {reviewer_id}: {len(points)} points")
                for i, pt in enumerate(points):
                    print(f"      [{i:02d}] {pt[:90]}{'…' if len(pt)>90 else ''}")
        print()

    out_path = PARSED_DIR / "preprocessed.json"
    out_path.write_text(
        json.dumps(to_indexed(output), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✓  Written → {out_path}")


if __name__ == "__main__":
    main()