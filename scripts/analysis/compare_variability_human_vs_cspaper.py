"""
compare_variability_human_vs_cspaper.py

Compares the variability (mean, standard deviation) of weakness-category
proportions between human reviews and cspaper (automated LLM-auditor)
reviews, for all 16 Lu et al. (2025) COARSE categories.

Motivation: cspaper produces far longer reviews than human reviewers, with
a much tighter spread of review lengths (an LLM filling a fixed review
template thoroughly and consistently each time, versus human reviewers who
vary widely in effort and thoroughness). This script checks whether that
same pattern -- lower variability under cspaper -- holds for the
weakness-category proportions themselves, not just review length.

Reads:
  - results/tables/weakness_category_distributions_per_review.csv (human)
  - results/tables/weakness_category_distributions_per_review_cspaper.csv

Writes:
  - results/tables/variability_human_vs_cspaper.csv

Usage:
    python scripts/analysis/compare_variability_human_vs_cspaper.py
"""

import os

import pandas as pd

HUMAN_CSV = "results/tables/weakness_category_distributions_per_review.csv"
CSPAPER_CSV = "results/tables/weakness_category_distributions_per_review_cspaper.csv"
OUTPUT_CSV = "results/tables/variability_human_vs_cspaper.csv"

LU_CATEGORIES = [
    "Ablation", "Analysis", "Comparison", "Contribution", "Data/Task",
    "DDDDEI", "Evaluation", "Experiment", "IJMV", "Methodology",
    "Novelty", "Presentation", "Related Work", "Result", "Significance", "Theory",
]


def main():
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(repo_root)

    human = pd.read_csv(HUMAN_CSV)
    cspaper = pd.read_csv(CSPAPER_CSV)

    rows = []
    for cat in LU_CATEGORIES:
        h_mean, h_std = human[cat].mean(), human[cat].std()
        c_mean, c_std = cspaper[cat].mean(), cspaper[cat].std()
        rows.append({
            "category": cat,
            "human_mean": round(h_mean, 4),
            "human_std": round(h_std, 4),
            "cspaper_mean": round(c_mean, 4),
            "cspaper_std": round(c_std, 4),
            "std_ratio_cspaper_over_human": round(c_std / h_std, 3) if h_std else None,
            "cspaper_lower_std": c_std < h_std,
        })

    results_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    results_df.to_csv(OUTPUT_CSV, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("Category-proportion variability: human review vs. cspaper\n")
    print(results_df.to_string(index=False))

    n_lower = results_df["cspaper_lower_std"].sum()
    n_total = len(results_df)
    mean_h_std = human[LU_CATEGORIES].std().mean()
    mean_c_std = cspaper[LU_CATEGORIES].std().mean()
    print(f"\ncspaper has lower std than human review in {n_lower}/{n_total} categories.")
    print(f"Mean std across all 16 categories -- human: {mean_h_std:.4f}, cspaper: {mean_c_std:.4f}")

    print("\nReview length (n_points) -- mean and std:")
    print(f"  human:   mean={human['n_points'].mean():.2f}, std={human['n_points'].std():.2f}, "
          f"relative variability={human['n_points'].std() / human['n_points'].mean():.1%}")
    print(f"  cspaper: mean={cspaper['n_points'].mean():.2f}, std={cspaper['n_points'].std():.2f}, "
          f"relative variability={cspaper['n_points'].std() / cspaper['n_points'].mean():.1%}")

    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
