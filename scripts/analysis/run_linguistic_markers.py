"""
run_linguistic_markers.py

Main linguistic-markers analysis: computes readability (FRE, NDC, FK Grade,
Gunning Fog), TTR/vocabulary diversity, average sentence length, and
vocabulary complexity (difficult-word ratio, polysyllable count) over the
FULL TEXT of every PDF in the four corpus folders.

This is the whole-document version -- section-level computation was dropped
in favor of keeping scope manageable; see section_presence_summary.py for the
smaller, separate "does this paper have a Limitations section" side-analysis.

Usage:
    python scripts/analysis/run_linguistic_markers.py
"""

import csv
import glob
import json
import os
import re
import statistics
import sys

import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(__file__))
from linguistic_markers import compute_markers  # noqa: E402


CORPUS_DIRS = {
    "AIG": "corpus/ai",
    "HUM_ACC": "corpus/human/accepted",
    "HUM_REJ": "corpus/human/rejected",
    "HA_COL": "corpus/human_ai_hybrid",
}

OUTPUT_CSV = "results/tables/linguistic_markers_summary.csv"

# AIG papers additionally get their human-review scores attached as extra columns
# (blank for every other category, since only AIG has this review data). This keeps
# AIG as a normal category for the main cross-category comparison below, while still
# carrying the score data needed for the separate AIG-only correlation analysis in
# correlate_aig_ratings.py.
REVIEWS_DIR = "arg_outputs/fars_human_reviews/raw"
SCORE_DIMENSIONS = ["rating", "soundness", "presentation", "contribution", "confidence"]

FIELDNAMES = [
    "paper_id", "category",
    "n_tokens", "n_types", "ttr", "avg_sentence_length",
    "flesch_reading_ease", "dale_chall_score", "flesch_kincaid_grade", "gunning_fog",
    "difficult_word_count", "difficult_word_ratio", "polysyllable_count",
    "extraction_error",
] + [f"mean_{dim}" for dim in SCORE_DIMENSIONS] + ["n_reviews", "integrity_flagged"]


def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)


def load_aig_review_scores() -> dict:
    """paper_id -> dict of mean_<dim> scores, n_reviews, integrity_flagged (AIG only)."""
    scores_by_paper = {}
    for path in glob.glob(os.path.join(REVIEWS_DIR, "*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        paper_id = d.get("paper_id") or os.path.splitext(os.path.basename(path))[0]
        reviews = d.get("reviews", [])
        row = {
            "n_reviews": len(reviews),
            "integrity_flagged": any(r.get("integrityIssuesFound") for r in reviews),
        }
        for dim in SCORE_DIMENSIONS:
            values = [r["scores"].get(dim) for r in reviews if "scores" in r and r["scores"].get(dim) is not None]
            row[f"mean_{dim}"] = round(statistics.mean(values), 3) if values else None
        scores_by_paper[paper_id] = row
    return scores_by_paper


def main():
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(repo_root)

    aig_scores = load_aig_review_scores()
    print(f"Loaded human-review scores for {len(aig_scores)} AIG papers from {REVIEWS_DIR}")

    rows = []

    for category, rel_dir in CORPUS_DIRS.items():
        if not os.path.isdir(rel_dir):
            print(f"WARNING: {rel_dir} not found, skipping {category}")
            continue

        pdf_files = sorted(f for f in os.listdir(rel_dir) if f.lower().endswith(".pdf"))
        print(f"{category}: {len(pdf_files)} PDFs in {rel_dir}")

        for fname in pdf_files:
            paper_id = os.path.splitext(fname)[0]
            path = os.path.join(rel_dir, fname)

            row = {"paper_id": paper_id, "category": category, "extraction_error": ""}
            try:
                text = extract_text(path)
                metrics = compute_markers(text)
                row.update(metrics)
            except Exception as e:
                print(f"  ERROR on {fname}: {e}")
                row["extraction_error"] = str(e)

            if category == "AIG" and paper_id in aig_scores:
                row.update(aig_scores[paper_id])

            rows.append(row)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")

    # Full per-category summary table -- transposed and with display options
    # widened so nothing gets truncated in the terminal.
    try:
        import pandas as pd
        pd.set_option("display.width", 200)
        pd.set_option("display.max_columns", None)
        df = pd.read_csv(OUTPUT_CSV)
        numeric_cols = [
            "n_tokens", "n_types", "ttr", "avg_sentence_length",
            "flesch_reading_ease", "dale_chall_score", "flesch_kincaid_grade",
            "gunning_fog", "difficult_word_ratio", "polysyllable_count",
        ]
        print("\nPer-category means:")
        print(df.groupby("category")[numeric_cols].mean().round(3).T)
        print("\nPer-category std dev:")
        print(df.groupby("category")[numeric_cols].std().round(3).T)

        # Separate AIG-only table: review scores are a different kind of variable
        # (continuous, only exist for AIG) so they don't belong in the cross-category
        # comparison above. This is just a quick look at the score distribution --
        # the actual score-vs-marker correlations are in correlate_aig_ratings.py /
        # results/tables/aig_rating_correlations.csv.
        score_cols = [f"mean_{dim}" for dim in ["rating", "soundness", "presentation", "contribution", "confidence"]]
        aig_df = df[df["category"] == "AIG"].copy()
        n_with_scores = aig_df["mean_rating"].notna().sum()
        print(f"\nAIG review-score summary ({n_with_scores}/{len(aig_df)} AIG papers have review scores):")
        print(aig_df[score_cols].describe().round(3).T)

        # Within-AIG breakdown: same linguistic-marker table as above, but instead of
        # AIG/HA_COL/HUM_ACC/HUM_REJ as columns, the columns are AIG papers split into
        # quartiles of their own mean_rating. Lets you see whether markers trend with
        # score within AIG specifically, in the same means/std format as the main
        # cross-category table (complements, doesn't replace, the correlation table).
        scored = aig_df.dropna(subset=["mean_rating"]).copy()
        scored["rating_quartile"] = pd.qcut(scored["mean_rating"], q=4, duplicates="drop")
        print(f"\nAIG papers by rating quartile ({len(scored)} scored papers, "
              f"{scored['rating_quartile'].nunique()} bins):")
        print(scored.groupby("rating_quartile", observed=True)["paper_id"].count().rename("n_papers").to_frame().T)
        print("\nLinguistic markers by AIG rating quartile -- means:")
        print(scored.groupby("rating_quartile", observed=True)[numeric_cols].mean().round(3).T)
        print("\nLinguistic markers by AIG rating quartile -- std dev:")
        print(scored.groupby("rating_quartile", observed=True)[numeric_cols].std().round(3).T)

        print("\n(For continuous score-vs-linguistic-marker correlations, run correlate_aig_ratings.py "
              "-> results/tables/aig_rating_correlations.csv)")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
