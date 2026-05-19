"""
convert_nlpeer_reviews.py

Converts NLPeer v1/reviews.json files into the standardized human review JSON
format used in arg_outputs/human_reviews/.

Usage:
    python3 convert_nlpeer_reviews.py --extracted_dir ~/nlpeer_extracted/data/ --output_dir arg_outputs/human_reviews/

One output JSON per paper, named {paper_id}_human_reviews.json.
"""

import argparse
import json
import os


def convert_review(raw: dict, index: int) -> dict:
    """Convert a single NLPeer review entry to standardized format."""
    report = raw.get("report", {})
    scores = raw.get("scores", {})
    meta   = raw.get("meta", {})

    return {
        "reviewer_id":  f"Reviewer_{index + 1}",
        "review_type":  "human",
        "summary":      report.get("paper_summary", ""),
        "strengths":    report.get("summary_of_strengths", ""),
        "weaknesses":   report.get("summary_of_weaknesses", ""),
        "questions":    report.get("comments_suggestions_and_typos", ""),
        "rating":       scores.get("overall_assessment", ""),
        "confidence":   meta.get("confidence", ""),
        "soundness":    scores.get("soundness", ""),
        "raw_note_id":  raw.get("note_id", ""),
    }


def process_paper(paper_dir: str, output_dir: str) -> None:
    paper_id      = os.path.basename(paper_dir)
    reviews_path  = os.path.join(paper_dir, "v1", "reviews.json")
    meta_path     = os.path.join(paper_dir, "v1", "meta.json")

    if not os.path.exists(reviews_path):
        print(f"  SKIP {paper_id} — no reviews.json")
        return

    with open(reviews_path, encoding="utf-8") as f:
        raw_reviews = json.load(f)

    if not raw_reviews:
        print(f"  SKIP {paper_id} — empty reviews.json")
        return

    # Load title from meta if available
    title = ""
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", "")

    reviews = [convert_review(r, i) for i, r in enumerate(raw_reviews)]

    output = {
        "paper_id":   paper_id,
        "source":     "nlpeer",
        "review_url": None,
        "venue":      "emnlp24",
        "title":      title,
        "reviews":    reviews,
    }

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{paper_id}_human_reviews.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  {paper_id} — {len(reviews)} review(s) → {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extracted_dir", required=True, help="Path to nlpeer_extracted/data/")
    parser.add_argument("--output_dir",    default="arg_outputs/human_reviews/")
    args = parser.parse_args()

    paper_dirs = [
        os.path.join(args.extracted_dir, d)
        for d in os.listdir(args.extracted_dir)
        if os.path.isdir(os.path.join(args.extracted_dir, d))
        and (d.startswith("HUM_REJ") or d.startswith("HUM_ACC"))
    ]

    if not paper_dirs:
        print(f"No HUM_REJ_* or HUM_ACC_* folders found in {args.extracted_dir}")
        return

    print(f"Found {len(paper_dirs)} paper(s). Converting...\n")
    for paper_dir in sorted(paper_dirs):
        process_paper(paper_dir, args.output_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
