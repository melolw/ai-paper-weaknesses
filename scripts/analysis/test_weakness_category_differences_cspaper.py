"""
test_weakness_category_differences_cspaper.py

Same omnibus procedure as test_weakness_category_differences.py, run on the
cspaper automated-reviewer data instead of human reviews. Used to check
whether the human-review significance pattern (Statistical Comparison)
holds, fails, or diverges under an automated reviewer applied uniformly
across all four origins.

Usage:
    python scripts/analysis/test_weakness_category_differences_cspaper.py
"""

import os

import pandas as pd
from scipy import stats

DISTRIBUTIONS_CSV = "results/tables/weakness_category_distributions_per_review_cspaper.csv"
OUTPUT_CSV = "results/tables/weakness_category_significance_tests_cspaper.csv"

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
    print(f"Omnibus test (cspaper) across {ORIGINS} for each of Lu et al.'s 16 categories "
          f"(n: {results[0]['n_per_origin']})\n")
    print(results_df.drop(columns=["n_per_origin"]).to_string(index=False))

    n_sig = results_df["significant_both"].sum()
    print(f"\n{n_sig}/{len(results_df)} categories show a significant origin difference "
          f"under BOTH ANOVA and Kruskal-Wallis (p < 0.05).")
    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
