"""
test_category_differences.py

Significance testing for the main per-category linguistic-markers comparison table
(AIG vs HA_COL vs HUM_ACC vs HUM_REJ) produced by run_linguistic_markers.py.

For each marker, runs an omnibus test across all four categories:
  - One-way ANOVA (parametric, assumes equal variances -- often violated here, e.g.
    n_tokens std ranges from 361 (AIG) to 3354 (HUM_ACC), so treat with caution)
  - Kruskal-Wallis H-test (non-parametric, rank-based, robust to unequal variances
    and non-normality -- the more trustworthy test given the variance differences)

A significant omnibus result only tells you "at least one category differs somewhere";
it does not say which pair. If you want to know which specific categories differ for
a given marker, that's a separate pairwise post-hoc step (e.g. Tukey HSD or pairwise
Mann-Whitney with a multiple-comparisons correction) -- not run here, flag if wanted.

Usage:
    python scripts/analysis/test_category_differences.py
"""

import os

import pandas as pd
from scipy import stats

MARKERS_CSV = "results/tables/linguistic_markers_summary.csv"
OUTPUT_CSV = "results/tables/category_significance_tests.csv"

CATEGORIES = ["AIG", "HA_COL", "HUM_ACC", "HUM_REJ"]

MARKER_COLUMNS = [
    "n_tokens", "n_types", "ttr", "avg_sentence_length",
    "flesch_reading_ease", "dale_chall_score", "flesch_kincaid_grade",
    "gunning_fog", "difficult_word_ratio", "polysyllable_count",
]


def main():
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(repo_root)

    df = pd.read_csv(MARKERS_CSV)
    df = df[df["category"].isin(CATEGORIES)]

    results = []
    for marker in MARKER_COLUMNS:
        groups = [df.loc[df["category"] == c, marker].dropna() for c in CATEGORIES]
        ns = [len(g) for g in groups]

        f_stat, anova_p = stats.f_oneway(*groups)
        h_stat, kw_p = stats.kruskal(*groups)

        results.append({
            "marker": marker,
            "n_per_category": ",".join(f"{c}={n}" for c, n in zip(CATEGORIES, ns)),
            "anova_F": round(f_stat, 3),
            "anova_p": round(anova_p, 5),
            "kruskal_H": round(h_stat, 3),
            "kruskal_p": round(kw_p, 5),
            "significant_both": (anova_p < 0.05) and (kw_p < 0.05),
        })

    results_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print(f"Omnibus test across {CATEGORIES} for each marker "
          f"(n: {results[0]['n_per_category']})\n")
    print(results_df.drop(columns=["n_per_category"]).to_string(index=False))

    n_sig = results_df["significant_both"].sum()
    print(f"\n{n_sig}/{len(results_df)} markers show a significant category difference "
          f"under BOTH ANOVA and Kruskal-Wallis (p < 0.05).")
    print("\nNote: this only tells you THAT categories differ for a marker, not WHICH "
          "pair(s) drive it -- that needs a separate pairwise post-hoc test.")
    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
