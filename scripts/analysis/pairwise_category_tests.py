"""
pairwise_category_tests.py

Follow-up to test_category_differences.py. The omnibus tests there (ANOVA +
Kruskal-Wallis) showed that all 10 linguistic markers differ significantly SOMEWHERE
among AIG / HA_COL / HUM_ACC / HUM_REJ, but not which pair(s) of categories drive it.
This script runs the actual pairwise comparisons.

For each marker, for each of the 6 category pairs (AIG-HA_COL, AIG-HUM_ACC, ...):
  - Mann-Whitney U test (rank-based, non-parametric -- the primary test here, since
    the omnibus step already showed variances differ a lot across categories)
  - Welch's t-test (parametric, unequal-variance version) as a secondary check

Running 6 pairwise tests per marker inflates the false-positive rate (the more
comparisons you run, the more likely one looks "significant" by chance), so p-values
are corrected within each marker's 6 comparisons using the Holm-Bonferroni method.
Report the Holm-corrected p-value, not the raw one, when deciding significance.

Usage:
    python scripts/analysis/pairwise_category_tests.py
"""

import itertools
import os

import pandas as pd
from scipy import stats

MARKERS_CSV = "results/tables/linguistic_markers_summary.csv"
OUTPUT_CSV = "results/tables/pairwise_category_tests.csv"

CATEGORIES = ["AIG", "HA_COL", "HUM_ACC", "HUM_REJ"]

MARKER_COLUMNS = [
    "n_tokens", "n_types", "ttr", "avg_sentence_length",
    "flesch_reading_ease", "dale_chall_score", "flesch_kincaid_grade",
    "gunning_fog", "difficult_word_ratio", "polysyllable_count",
]


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

    df = pd.read_csv(MARKERS_CSV)
    df = df[df["category"].isin(CATEGORIES)]
    pairs = list(itertools.combinations(CATEGORIES, 2))

    all_rows = []
    for marker in MARKER_COLUMNS:
        marker_rows = []
        for cat_a, cat_b in pairs:
            a = df.loc[df["category"] == cat_a, marker].dropna()
            b = df.loc[df["category"] == cat_b, marker].dropna()

            u_stat, mwu_p = stats.mannwhitneyu(a, b, alternative="two-sided")
            t_stat, tt_p = stats.ttest_ind(a, b, equal_var=False)

            marker_rows.append({
                "marker": marker,
                "pair": f"{cat_a} vs {cat_b}",
                f"mean_{cat_a}": round(a.mean(), 3),
                f"mean_{cat_b}": round(b.mean(), 3),
                "mannwhitney_p_raw": mwu_p,
                "welch_ttest_p_raw": tt_p,
            })

        raw_ps = [r["mannwhitney_p_raw"] for r in marker_rows]
        holm_ps = holm_bonferroni(raw_ps)
        for r, hp in zip(marker_rows, holm_ps):
            r["mannwhitney_p_holm"] = round(hp, 5)
            r["mannwhitney_p_raw"] = round(r["mannwhitney_p_raw"], 5)
            r["welch_ttest_p_raw"] = round(r["welch_ttest_p_raw"], 5)
            r["significant_after_correction"] = hp < 0.05
        all_rows.extend(marker_rows)

    results_df = pd.DataFrame(all_rows)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    for marker in MARKER_COLUMNS:
        sub = results_df[results_df["marker"] == marker]
        print(f"\n=== {marker} ===")
        cols = ["pair", "mannwhitney_p_raw", "mannwhitney_p_holm", "welch_ttest_p_raw", "significant_after_correction"]
        print(sub[cols].to_string(index=False))

    n_sig = results_df["significant_after_correction"].sum()
    n_total = len(results_df)
    print(f"\n{n_sig}/{n_total} pairwise comparisons remain significant after Holm-Bonferroni "
          f"correction (p_holm < 0.05).")
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
