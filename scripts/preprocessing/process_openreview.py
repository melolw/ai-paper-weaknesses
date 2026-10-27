"""
process_openreview.py
=====================
Parses Agents4Science openreview JSON files and writes preprocessed JSON
to parsed/preprocessed.json.

Input format (produced by download_openreview_hah.py):
    {
      "paper_id": "HAH_2025_...",
      "reviews": [
        {
          "reviewer_id": "Reviewer_Cw2t",
          "review_type": "human",
          "summary": "...",
          "strengths_and_weaknesses": "plain text...",
          "questions": "...",
          "rating": "...",
          "confidence": "..."
        },
        {
          "reviewer_id": "Reviewer_AIRev1",
          "review_type": "ai",
          ...
        }
      ]
    }

Only human reviewers (review_type == "human") are extracted.
Sections extracted: strengths_and_weaknesses, questions

Usage:
    python process_openreview.py

    Reads from  ../../arg_outputs/openreview/raw/
    Writes to   ../../arg_outputs/openreview/parsed/preprocessed.json
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from review_point_utils import extract_points

SCRIPT_DIR   = Path(__file__).parent
REVIEWER_DIR = (SCRIPT_DIR / "../../arg_outputs/openreview").resolve()
RAW_DIR      = REVIEWER_DIR / "raw"
PARSED_DIR   = REVIEWER_DIR / "parsed"

EXTRACT_FIELDS = ["summary", "strengths_and_weaknesses", "weaknesses", "questions"]


def parse_file(data: dict) -> dict:
    paper_id = data["paper_id"]
    result   = {}

    for review in data.get("reviews", []):
        if review.get("review_type") == "ai":
            continue

        reviewer_id = review.get("reviewer_id", "unknown")
        points = []

        sw = review.get("strengths_and_weaknesses", "").strip()
        q  = review.get("questions", "").strip()

        if sw and sw != "N/A" and sw != ".":
            points.extend(extract_points(sw))
        if q and q != "N/A" and q != ".":
            points.extend(extract_points(q))

        # Only use summary as fallback if no content elsewhere
        if not points:
            summary = review.get("summary", "").strip()
            if summary and summary != "N/A":
                points.extend(extract_points(summary))

        if points:
            result[reviewer_id] = points

    return {paper_id: result}


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
    skipped_ai = 0

    for fpath in json_files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON error in {fpath.name}: {e}")
            continue

        if not data.get("reviews"):
            skipped_empty += 1
            continue

        parsed = parse_file(data)
        n_ai = sum(1 for r in data["reviews"] if r.get("review_type") == "ai")
        skipped_ai += n_ai

        for paper_id, reviewers in parsed.items():
            output.setdefault(paper_id, {}).update(reviewers)

        print(f"  {fpath.name}")
        for paper_id, reviewers in parsed.items():
            for rev_id, points in reviewers.items():
                print(f"    {rev_id}: {len(points)} points")
                for i, pt in enumerate(points):
                    print(f"      [{i:02d}] {pt[:90]}{'…' if len(pt) > 90 else ''}")
        print()

    out_path = PARSED_DIR / "preprocessed.json"
    out_path.write_text(
        json.dumps(to_indexed(output), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✓  Written → {out_path}")
    print(f"   AI reviewers skipped: {skipped_ai}")


if __name__ == "__main__":
    main()