"""
test_weakness_category_differences.py

Significance testing for the weakness-category distribution comparison
(AIG vs HA_COL vs HUM_ACC vs HUM_REJ) shown in the "Distribution by origin"
figure. Uses the per-review category proportions produced by
extract_weakness_category_distributions.py.

For each of Lu et al.'s (2025) 16 COARSE categories, runs an omnibus test
across the four origins:
  - One-way ANOVA (parametric)
  - Kruskal-Wallis H-test (non-parametric, rank-based -- the primary test
    here, since these are bounded [0,1] proportions with many zeros, not
    normally distributed)

Same pattern as test_category_differences.py (used for the linguistic
markers), applied here to weakness-category proportions instead.

A significant omnibus result only tells you "at least one origin differs
somewhere" for that category; it does not say which pair. See
pairwise_weakness_category_tests.py for the pairwise follow-up.

Usage:
    python scripts/analysis/test_weakness_category_differences.py
"""

import os

import pandas as pd
from scipy import stats

DISTRIBUTIONS_CSV = "results/tables/weakness_category_distributions_per_review.csv"
OUTPUT_CSV = "results/tables/weakness_category_significance_tests.csv"

ORIGINS = ["AIG", "HA_COL", "HUM_ACC", "HUM_REJ"]

LU_CATEGORIES = [
    "Ablation", "Analysis", "Comparison", "Contribution", "Data/Task",
    "DDDDEI", "Evaluation", "Experiment", "IJMV", "Methodology",
    "Novelty", "Presentation", "Related Work", "Result", "Significance", "Theory",
]


def main():
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(repo_root)

    df = pd.read_csv(DISTRIBUTIONS_CSV)
    df = df[df["origin"].isin(ORIGINS)]

    results = []
    for cat in LU_CATEGORIES:
        groups = [df.loc[df["origin"] == o, cat].dropna() for o in ORIGINS]
        ns = [len(g) for g in groups]

        f_stat, anova_p = stats.f_oneway(*groups)
        h_stat, kw_p = stats.kruskal(*groups)

        results.append({
            "category": cat,
            "n_per_origin": ",".join(f"{o}={n}" for o, n in zip(ORIGINS, ns)),
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
    print(f"Omnibus test across {ORIGINS} for each of Lu et al.'s 16 categories "
          f"(n: {results[0]['n_per_origin']})\n")
    print(results_df.drop(columns=["n_per_origin"]).to_string(index=False))

    n_sig = results_df["significant_both"].sum()
    print(f"\n{n_sig}/{len(results_df)} categories show a significant origin difference "
          f"under BOTH ANOVA and Kruskal-Wallis (p < 0.05).")
    print("\nNote: this only tells you THAT origins differ for a category, not WHICH "
          "pair(s) drive it -- that needs the pairwise post-hoc test.")
    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
