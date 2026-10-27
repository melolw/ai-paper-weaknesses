"""
pairwise_weakness_category_tests_cspaper.py

Same pairwise procedure as pairwise_weakness_category_tests.py, run on the
cspaper automated-reviewer data instead of human reviews.

Usage:
    python scripts/analysis/pairwise_weakness_category_tests_cspaper.py
"""

import itertools
import os

import pandas as pd
from scipy import stats

DISTRIBUTIONS_CSV = "results/tables/weakness_category_distributions_per_review_cspaper.csv"
OUTPUT_CSV = "results/tables/weakness_category_pairwise_tests_cspaper.csv"

ORIGINS = ["AIG", "HA_COL", "HUM_ACC", "HUM_REJ"]

LU_CATEGORIES = [
    "Ablation", "Analysis", "Comparison", "Contribution", "Data/Task",
    "DDDDEI", "Evaluation", "Experiment", "IJMV", "Methodology",
    "Novelty", "Presentation", "Related Work", "Result", "Significance", "Theory",
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

    df = pd.read_csv(DISTRIBUTIONS_CSV)
    df = df[df["origin"].isin(ORIGINS)]
    pairs = list(itertools.combinations(ORIGINS, 2))

    all_rows = []
    for cat in LU_CATEGORIES:
        cat_rows = []
        for origin_a, origin_b in pairs:
            a = df.loc[df["origin"] == origin_a, cat].dropna()
            b = df.loc[df["origin"] == origin_b, cat].dropna()

            u_stat, mwu_p = stats.mannwhitneyu(a, b, alternative="two-sided")
            t_stat, tt_p = stats.ttest_ind(a, b, equal_var=False)

            cat_rows.append({
                "category": cat,
                "pair": f"{origin_a} vs {origin_b}",
                f"mean_{origin_a}": round(a.mean(), 4),
                f"mean_{origin_b}": round(b.mean(), 4),
                "mannwhitney_p_raw": mwu_p,
                "welch_ttest_p_raw": tt_p,
            })

        raw_ps = [r["mannwhitney_p_raw"] for r in cat_rows]
        holm_ps = holm_bonferroni(raw_ps)
        for r, hp in zip(cat_rows, holm_ps):
            r["mannwhitney_p_holm"] = round(hp, 5)
            r["mannwhitney_p_raw"] = round(r["mannwhitney_p_raw"], 5)
            r["welch_ttest_p_raw"] = round(r["welch_ttest_p_raw"], 5)
            r["significant_after_correction"] = hp < 0.05
        all_rows.extend(cat_rows)

    results_df = pd.DataFrame(all_rows)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    for cat in LU_CATEGORIES:
        sub = results_df[results_df["category"] == cat]
        print(f"\n=== {cat} ===")
        cols = ["pair", "mannwhitney_p_raw", "mannwhitney_p_holm", "welch_ttest_p_raw", "significant_after_correction"]
        print(sub[cols].to_string(index=False))

    n_sig = results_df["significant_after_correction"].sum()
    n_total = len(results_df)
    print(f"\n{n_sig}/{n_total} pairwise comparisons remain significant after Holm-Bonferroni "
          f"correction (p_holm < 0.05).")
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
