"""
presentation_weakness_analysis.py

For each paper, using HUMAN reviews only, flags whether any reviewer's critique
points were classified with the "Presentation" aspect (from the existing weakness
taxonomy/classification already run over human reviews -- NOT the cspaper/LLM-auditor
data, which is a separate automated critique tool, not a human review).

Sources (all already human-review-only):
  - arg_outputs/fars_human_reviews/parsed/classified.json   (AIG)
  - arg_outputs/human_reviews/parsed/classified.json        (HUM_ACC, HUM_REJ -- NLPeer,
    split by paper_id prefix)
  - arg_outputs/openreview/parsed/classified.json           (HA_COL / HAH -- Agents4Science;
    this file already contains only the human reviewer's critiques per paper, the AI
    reviewers were excluded at classification time)

A paper is flagged has_presentation_weakness=True if ANY critique point from ANY human
reviewer for that paper carries "Presentation" in its aspects list.

Then: merges this flag with linguistic_markers_summary.csv and, WITHIN each of the four
corpus categories separately, compares linguistic markers between papers with vs. without
a presentation weakness (Mann-Whitney U + Welch's t-test, Holm-Bonferroni corrected across
the 10 markers within each category).

Usage:
    python scripts/analysis/presentation_weakness_analysis.py
"""

import json
import os

import pandas as pd
from scipy import stats

MARKERS_CSV = "results/tables/linguistic_markers_summary.csv"
OUTPUT_CSV = "results/tables/presentation_weakness_tests.csv"
OUTPUT_FLAGS_CSV = "results/tables/presentation_weakness_flags.csv"

CLASSIFIED_SOURCES = [
    "arg_outputs/fars_human_reviews/parsed/classified.json",
    "arg_outputs/human_reviews/parsed/classified.json",
    "arg_outputs/openreview/parsed/classified.json",
]

CATEGORIES = ["AIG", "HA_COL", "HUM_ACC", "HUM_REJ"]

MARKER_COLUMNS = [
    "n_tokens", "n_types", "ttr", "avg_sentence_length",
    "flesch_reading_ease", "dale_chall_score", "flesch_kincaid_grade",
    "gunning_fog", "difficult_word_ratio", "polysyllable_count",
]


def paper_id_to_category(paper_id: str) -> str:
    if paper_id.startswith("AIG"):
        return "AIG"
    if paper_id.startswith("HAH"):
        return "HA_COL"
    if paper_id.startswith("HUM_ACC"):
        return "HUM_ACC"
    if paper_id.startswith("HUM_REJ"):
        return "HUM_REJ"
    return "UNKNOWN"


def has_presentation_weakness(reviews_for_paper: dict) -> bool:
    for _reviewer, critiques in reviews_for_paper.items():
        for _cid, c in critiques.items():
            if "Presentation" in c.get("aspects", []):
                return True
    return False


def presentation_reviewer_ratio(reviews_for_paper: dict) -> tuple:
    """Fraction of reviewers (not critique points) who raised >=1 Presentation
    critique for this paper. E.g. 2 of 3 reviewers mention it -> 0.667, vs a
    different paper where only 1 of 3 does -> 0.333: the binary flag treats these
    identically, this doesn't. Returns (ratio, n_reviewers_flagging, n_reviewers)."""
    n_reviewers = len(reviews_for_paper)
    if n_reviewers == 0:
        return None, 0, 0
    n_flagging = 0
    for _reviewer, critiques in reviews_for_paper.items():
        if any("Presentation" in c.get("aspects", []) for c in critiques.values()):
            n_flagging += 1
    return n_flagging / n_reviewers, n_flagging, n_reviewers


def holm_bonferroni(pvals):
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

    rows = []
    for path in CLASSIFIED_SOURCES:
        d = json.load(open(path, encoding="utf-8"))
        for paper_id, reviews in d.items():
            flag = has_presentation_weakness(reviews)
            ratio, n_flagging, n_reviewers = presentation_reviewer_ratio(reviews)
            rows.append({
                "paper_id": paper_id,
                "category": paper_id_to_category(paper_id),
                "has_presentation_weakness": flag,
                "n_reviewers_flagging_presentation": n_flagging,
                "n_reviewers": n_reviewers,
                "presentation_reviewer_ratio": ratio,
            })

    flags_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUTPUT_FLAGS_CSV), exist_ok=True)
    flags_df.to_csv(OUTPUT_FLAGS_CSV, index=False)

    print("Papers flagged with a human-reviewer presentation weakness, by category:")
    print(flags_df.groupby("category")["has_presentation_weakness"].agg(["sum", "count"]))

    markers_df = pd.read_csv(MARKERS_CSV)
    merged = markers_df.merge(
        flags_df[["paper_id", "has_presentation_weakness", "presentation_reviewer_ratio", "n_reviewers"]],
        on="paper_id", how="inner",
    )
    print(f"\nMerged {len(merged)} papers with markers + presentation-weakness flag "
          f"(out of {len(markers_df)} in markers CSV, {len(flags_df)} classified).")

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", None)

    print("\nMeans by category x has_presentation_weakness:")
    print(merged.groupby(["category", "has_presentation_weakness"])[MARKER_COLUMNS].mean().round(3).T)

    results = []
    for cat in CATEGORIES:
        sub = merged[merged["category"] == cat]
        with_w = sub[sub["has_presentation_weakness"]]
        without_w = sub[~sub["has_presentation_weakness"]]

        raw_ps = []
        cat_rows = []
        for marker in MARKER_COLUMNS:
            a = with_w[marker].dropna()
            b = without_w[marker].dropna()
            u_stat, mwu_p = stats.mannwhitneyu(a, b, alternative="two-sided")
            t_stat, tt_p = stats.ttest_ind(a, b, equal_var=False)
            cat_rows.append({
                "category": cat,
                "marker": marker,
                "n_with_weakness": len(a),
                "n_without_weakness": len(b),
                "mean_with_weakness": round(a.mean(), 3),
                "mean_without_weakness": round(b.mean(), 3),
                "mannwhitney_p_raw": mwu_p,
                "welch_ttest_p_raw": round(tt_p, 5),
            })
            raw_ps.append(mwu_p)

        holm_ps = holm_bonferroni(raw_ps)
        for row, hp in zip(cat_rows, holm_ps):
            row["mannwhitney_p_raw"] = round(row["mannwhitney_p_raw"], 5)
            row["mannwhitney_p_holm"] = round(hp, 5)
            row["significant_after_correction"] = hp < 0.05
        results.extend(cat_rows)

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False)

    for cat in CATEGORIES:
        sub = results_df[results_df["category"] == cat]
        print(f"\n=== {cat} (n_with_weakness={sub['n_with_weakness'].iloc[0]}, "
              f"n_without_weakness={sub['n_without_weakness'].iloc[0]}) ===")
        cols = ["marker", "mean_with_weakness", "mean_without_weakness", "mannwhitney_p_holm", "significant_after_correction"]
        print(sub[cols].to_string(index=False))

    n_sig = results_df["significant_after_correction"].sum()
    print(f"\n{n_sig}/{len(results_df)} within-category binary comparisons significant after Holm-Bonferroni correction.")

    # --- Proportional version: correlate presentation_reviewer_ratio (fraction of
    # reviewers per paper who raised it, not just any/none) against each marker,
    # within each category. Note: HA_COL always has exactly 1 human reviewer per
    # paper, so its ratio is always 0 or 1 -- identical to the binary flag there,
    # not a genuine proportion. HUM_REJ is mostly 1 reviewer too (46/50), so limited
    # variation. AIG (2-3 reviewers for 48/50 papers) and HUM_ACC (2-3 for 23/50)
    # are where this measure actually adds information over the binary flag.
    print("\n" + "=" * 70)
    print("PROPORTIONAL VERSION: correlating presentation_reviewer_ratio vs markers")
    print("=" * 70)

    corr_results = []
    for cat in CATEGORIES:
        sub = merged[merged["category"] == cat]
        n_variable = sub["n_reviewers"].gt(1).sum()
        raw_ps = []
        cat_rows = []
        for marker in MARKER_COLUMNS:
            pair = sub[["presentation_reviewer_ratio", marker]].dropna()
            pearson_r, pearson_p = stats.pearsonr(pair["presentation_reviewer_ratio"], pair[marker])
            spearman_r, spearman_p = stats.spearmanr(pair["presentation_reviewer_ratio"], pair[marker])
            cat_rows.append({
                "category": cat, "marker": marker, "n": len(pair),
                "pearson_r": round(pearson_r, 3), "pearson_p": pearson_p,
                "spearman_r": round(spearman_r, 3), "spearman_p": round(spearman_p, 5),
            })
            raw_ps.append(pearson_p)
        holm_ps = holm_bonferroni(raw_ps)
        for row, hp in zip(cat_rows, holm_ps):
            row["pearson_p"] = round(row["pearson_p"], 5)
            row["pearson_p_holm"] = round(hp, 5)
            row["significant_both_raw"] = (row["pearson_p"] < 0.05) and (row["spearman_p"] < 0.05)
        corr_results.extend(cat_rows)

        print(f"\n=== {cat} (n_papers_with_>1_reviewer={n_variable}/{len(sub)}) ===")
        print(pd.DataFrame(cat_rows)[["marker", "n", "pearson_r", "pearson_p", "pearson_p_holm", "spearman_r", "spearman_p", "significant_both_raw"]].to_string(index=False))

    corr_df = pd.DataFrame(corr_results)
    corr_out = "results/tables/presentation_ratio_correlations.csv"
    corr_df.to_csv(corr_out, index=False)

    print(f"\nWrote {OUTPUT_FLAGS_CSV}, {OUTPUT_CSV}, and {corr_out}")


if __name__ == "__main__":
    main()
