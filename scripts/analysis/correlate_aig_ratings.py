"""
correlate_aig_ratings.py

Correlates AIG papers' human-review scores (overall rating, plus soundness,
presentation, contribution, confidence sub-scores, averaged across reviewers)
against their linguistic markers (from linguistic_markers_summary.csv).

Rationale: with only 3/50 AIG papers clearing the actual ICLR-aligned
acceptance threshold (rating >= 6, no integrity flags), a binary accept/reject
group comparison isn't statistically meaningful for this subset. Continuous
correlation avoids that problem entirely and mirrors the methodology used in
Jung et al. and Vincent-Lamarre & Lariviere.

Note: papers with >=1 reviewer flagging integrityIssuesFound are EXCLUDED by
default (see EXCLUDE_INTEGRITY_FLAGGED), since integrity fabrication and
writing-quality/linguistic markers are different constructs and mixing them
would confound the correlation. Set to False to include everyone.

Usage:
    python scripts/analysis/correlate_aig_ratings.py
"""

import glob
import json
import os
import statistics

import pandas as pd
from scipy import stats

REVIEWS_DIR = "arg_outputs/fars_human_reviews/raw"
MARKERS_CSV = "results/tables/linguistic_markers_summary.csv"
OUTPUT_CSV = "results/tables/aig_rating_correlations.csv"

EXCLUDE_INTEGRITY_FLAGGED = False

SCORE_DIMENSIONS = ["rating", "soundness", "presentation", "contribution", "confidence"]

MARKER_COLUMNS = [
    "ttr", "avg_sentence_length", "flesch_reading_ease", "dale_chall_score",
    "flesch_kincaid_grade", "gunning_fog", "difficult_word_ratio", "polysyllable_count",
]


def load_review_scores() -> pd.DataFrame:
    rows = []
    for path in glob.glob(os.path.join(REVIEWS_DIR, "*.json")):
        with open(path) as f:
            d = json.load(f)
        paper_id = d.get("paper_id") or os.path.splitext(os.path.basename(path))[0]
        reviews = d.get("reviews", [])
        any_flag = any(r.get("integrityIssuesFound") for r in reviews)

        row = {"paper_id": paper_id, "integrity_flagged": any_flag, "n_reviews": len(reviews)}
        for dim in SCORE_DIMENSIONS:
            values = [r["scores"].get(dim) for r in reviews if "scores" in r and r["scores"].get(dim) is not None]
            row[f"mean_{dim}"] = statistics.mean(values) if values else None
        rows.append(row)
    return pd.DataFrame(rows)


def holm_bonferroni(pvals):
    """Return Holm-corrected p-values, same order as input."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    corrected = [None] * n
    running_max = 0.0
    for rank, idx in enumerate(order):
        adj = (n - rank) * pvals[idx]
        running_max = max(running_max, adj)
        corrected[idx] = min(running_max, 1.0)
    return corrected


def main():
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(repo_root)

    reviews_df = load_review_scores()
    markers_df = pd.read_csv(MARKERS_CSV)
    # Only pull paper_id + the linguistic marker columns from the markers CSV -- it
    # now also carries its own review-score/integrity columns (added by
    # run_linguistic_markers.py), which would otherwise collide on merge with the
    # ones computed fresh here by load_review_scores().
    aig_markers = markers_df.loc[markers_df["category"] == "AIG", ["paper_id"] + MARKER_COLUMNS]

    merged = aig_markers.merge(reviews_df, on="paper_id", how="inner")
    print(f"Merged {len(merged)} AIG papers with review scores "
          f"(out of {len(aig_markers)} in markers CSV, {len(reviews_df)} in reviews)")

    if EXCLUDE_INTEGRITY_FLAGGED:
        n_before = len(merged)
        merged = merged[~merged["integrity_flagged"]]
        print(f"Excluded {n_before - len(merged)} integrity-flagged papers "
              f"-> {len(merged)} remaining for correlation")

    score_cols = [f"mean_{dim}" for dim in SCORE_DIMENSIONS]

    results = []
    for score_col in score_cols:
        for marker_col in MARKER_COLUMNS:
            sub = merged[[score_col, marker_col]].dropna()
            if len(sub) < 3:
                continue
            pearson_r, pearson_p = stats.pearsonr(sub[score_col], sub[marker_col])
            spearman_r, spearman_p = stats.spearmanr(sub[score_col], sub[marker_col])
            results.append({
                "score_dimension": score_col.replace("mean_", ""),
                "marker": marker_col,
                "n": len(sub),
                "pearson_r": round(pearson_r, 3),
                "pearson_p": round(pearson_p, 4),
                "spearman_r": round(spearman_r, 3),
                "spearman_p": round(spearman_p, 4),
            })

    results_df = pd.DataFrame(results)

    # Holm-Bonferroni correction across the whole family of tests run in this
    # analysis (all score-dimension x marker combinations), same procedure used
    # for every other pairwise/correlation table in this thesis. Corrected
    # independently for Pearson and Spearman p-values.
    results_df["pearson_p_holm"] = [round(p, 4) for p in holm_bonferroni(results_df["pearson_p"].tolist())]
    results_df["spearman_p_holm"] = [round(p, 4) for p in holm_bonferroni(results_df["spearman_p"].tolist())]
    results_df["significant_both_holm"] = (
        (results_df["pearson_p_holm"] < 0.05) & (results_df["spearman_p_holm"] < 0.05)
    )

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_rows", None)
    print(f"\nWrote {len(results_df)} correlation rows to {OUTPUT_CSV}\n")
    print("Correlations with overall rating:")
    print(results_df[results_df["score_dimension"] == "rating"].to_string(index=False))

    print("\nAll significant correlations (p < 0.05, either test, RAW/uncorrected):")
    sig = results_df[(results_df["pearson_p"] < 0.05) | (results_df["spearman_p"] < 0.05)]
    print(sig.to_string(index=False) if len(sig) else "(none)")

    print(f"\nAll significant correlations after Holm-Bonferroni correction "
          f"(p_holm < 0.05, BOTH tests, n={len(results_df)} total comparisons):")
    sig_holm = results_df[results_df["significant_both_holm"]]
    print(sig_holm.to_string(index=False) if len(sig_holm) else "(none)")


if __name__ == "__main__":
    main()
