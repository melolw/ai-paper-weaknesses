"""
arg_overlap_baselines.py
========================
Chance baselines for the category-level overlap between ARG reviews and human
reviews (RQ3).

Why: the human reviews of an AIG paper together cover most of the 16 Lu et al.
categories, so recall and precision are close to saturated for any system that
names many categories. This script computes what trivial systems would score
on exactly the same papers, so that the ARG scores can be read against them.

Systems compared, per ARG (all macro-averaged per paper, like the main table):
  actual            -- the ARG's own category set
  all_categories    -- a system that names all 16 categories
  random_weighted   -- picks as many categories as the ARG, at random, with
                       probability proportional to how many papers' human
                       reviews raise each category
  random_uniform    -- same, but every category equally likely

Also reports, per ARG, the paired difference in per-paper F1 between the actual
ARG and random_weighted with a bootstrap 95% confidence interval over papers.

Input : results/tables/arg_human_category_overlap_by_paper.csv
Output: results/tables/arg_human_overlap_baselines.csv
        results/tables/arg_human_overlap_vs_chance.csv

Usage:
    python scripts/analysis/arg_overlap_baselines.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parent.parent.parent
IN_CSV = REPO_ROOT / "results/tables/arg_human_category_overlap_by_paper.csv"
OUT_BASELINES = REPO_ROOT / "results/tables/arg_human_overlap_baselines.csv"
OUT_VS_CHANCE = REPO_ROOT / "results/tables/arg_human_overlap_vs_chance.csv"

CATEGORIES = [
    "Ablation", "Analysis", "Comparison", "Contribution", "DDDDEI", "Data/Task",
    "Evaluation", "Experiment", "IJMV", "Methodology", "Novelty", "Presentation",
    "Related Work", "Result", "Significance", "Theory",
]
N_DRAWS = 1000        # random draws per paper and ARG
N_BOOTSTRAP = 10000   # bootstrap resamples of papers
SEED = 42


def overlap_scores(n_overlap, n_human, n_pred):
    """Per-draw recall, precision, F1 (arrays or scalars)."""
    recall = n_overlap / n_human
    precision = n_overlap / n_pred
    denom = recall + precision
    f1 = np.where(denom > 0, 2 * recall * precision / np.where(denom > 0, denom, 1), 0.0)
    return recall, precision, f1


def random_baseline(rng, human, k, probs, n_draws):
    """Expected per-paper recall, precision, F1 when naming k random categories."""
    idx = {c: i for i, c in enumerate(CATEGORIES)}
    human_mask = np.zeros(len(CATEGORIES), dtype=bool)
    for c in human:
        human_mask[idx[c]] = True
    overlaps = np.empty(n_draws)
    for d in range(n_draws):
        pick = rng.choice(len(CATEGORIES), size=k, replace=False, p=probs)
        overlaps[d] = human_mask[pick].sum()
    r, p, f = overlap_scores(overlaps, len(human), k)
    return r.mean(), p.mean(), f.mean()


def bootstrap_ci(values, rng, n_boot=N_BOOTSTRAP):
    values = np.asarray(values)
    means = np.array([rng.choice(values, size=len(values), replace=True).mean()
                      for _ in range(n_boot)])
    return np.percentile(means, [2.5, 97.5])


def main():
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(IN_CSV)
    df["human_set"] = df["human_categories"].apply(lambda s: set(s.split(",")))

    # Human category prevalence (number of papers whose human reviews raise it).
    human_by_paper = df.drop_duplicates("paper_id").set_index("paper_id")["human_set"]
    prevalence = np.array([sum(c in s for s in human_by_paper) for c in CATEGORIES], float)
    weights = prevalence / prevalence.sum()
    uniform = np.full(len(CATEGORIES), 1 / len(CATEGORIES))

    print(f"Papers: {len(human_by_paper)}; "
          f"mean human categories per paper: "
          f"{np.mean([len(s) for s in human_by_paper]):.2f} of {len(CATEGORIES)}")

    rows, chance_rows = [], []
    for arg, g in df.groupby("arg"):
        g = g.reset_index(drop=True)
        n_h = g["n_human_categories"].to_numpy()
        n_a = g["n_arg_categories"].to_numpy()
        n_o = g["n_overlap"].to_numpy()

        # actual
        r, p, f = overlap_scores(n_o, n_h, n_a)
        rows.append((arg, "actual", r.mean(), p.mean(), f.mean()))

        # all categories
        r_all, p_all, f_all = overlap_scores(n_h.astype(float), n_h, len(CATEGORIES))
        rows.append((arg, "all_categories", r_all.mean(), p_all.mean(), f_all.mean()))

        # random baselines, size-matched to this ARG
        per_paper = {"random_weighted": [], "random_uniform": []}
        for i, row in g.iterrows():
            per_paper["random_weighted"].append(
                random_baseline(rng, row["human_set"], int(n_a[i]), weights, N_DRAWS))
            per_paper["random_uniform"].append(
                random_baseline(rng, row["human_set"], int(n_a[i]), uniform, N_DRAWS))
        for name, vals in per_paper.items():
            arr = np.array(vals)
            rows.append((arg, name, arr[:, 0].mean(), arr[:, 1].mean(), arr[:, 2].mean()))

        # paired difference in per-paper F1: actual minus random_weighted
        f_rand = np.array(per_paper["random_weighted"])[:, 2]
        diff = f - f_rand
        lo, hi = bootstrap_ci(diff, rng)
        chance_rows.append((arg, f.mean(), f_rand.mean(), diff.mean(), lo, hi))

    base = pd.DataFrame(rows, columns=["arg", "system", "mean_recall", "mean_precision", "mean_f1"])
    chance = pd.DataFrame(chance_rows, columns=[
        "arg", "f1_actual", "f1_random_weighted", "f1_difference",
        "difference_ci_low", "difference_ci_high"])

    base.round(4).to_csv(OUT_BASELINES, index=False)
    chance.round(4).to_csv(OUT_VS_CHANCE, index=False)

    print("\nBaselines (macro-averaged per paper):")
    print(base.round(3).to_string(index=False))
    print("\nActual vs. random_weighted, per-paper F1 (95% bootstrap CI of the difference):")
    print(chance.round(3).to_string(index=False))
    print(f"\nSaved:\n  {OUT_BASELINES}\n  {OUT_VS_CHANCE}")


if __name__ == "__main__":
    main()
