"""
arg_human_category_overlap.py

RQ3: Do ARGs (automated review generators) detect the same weakness
categories that human reviewers detect in AIG papers?

For each AIG paper, the human review(s) and a given ARG's review are each
reduced to a set of Lu et al. (2025) COARSE categories touched on by at
least one critique point. Overlap between the two sets is measured with
plain recall / precision / F1, per paper, then averaged (macro) across all
AIG papers that have both a human review and a review from that ARG.

    recall(paper)    = |human_categories ∩ arg_categories| / |human_categories|
    precision(paper) = |human_categories ∩ arg_categories| / |arg_categories|
    f1(paper)        = harmonic mean of the two

Human reviews for AIG papers come from the FARS human review pipeline
(fars_human_reviews). Where a paper has multiple human reviewers, their
categories are unioned into a single "what humans flagged for this paper"
set before comparison.

Reads:
  - arg_outputs/fars_human_reviews/parsed/classified.json
  - arg_outputs/{cspaper,paperreview_ai,paperaudit_review,deepreviewer}/parsed/classified.json

Writes:
  - results/tables/arg_human_category_overlap_by_paper.csv   (per paper, per ARG)
  - results/tables/arg_human_category_overlap_summary.csv    (macro-averaged, per ARG)

Usage:
    python scripts/analysis/arg_human_category_overlap.py
"""

import json
import os
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent.parent
ARG_DIR = REPO_ROOT / "arg_outputs"
OUT_BY_PAPER = REPO_ROOT / "results/tables/arg_human_category_overlap_by_paper.csv"
OUT_SUMMARY = REPO_ROOT / "results/tables/arg_human_category_overlap_summary.csv"

HUMAN_FOLDER = "fars_human_reviews"

ARG_FOLDERS = {
    "cspaper": "cspaper",
    "paperreview.ai": "paperreview_ai",
    "paperaudit": "paperaudit_review",
    "deepreviewer": "deepreviewer",
}

ASPECT_TO_DISPLAY = {
    "Ablation": "Ablation", "Analysis": "Analysis", "Comparison": "Comparison",
    "Contribution": "Contribution", "Data/Task": "Data/Task",
    "Definition/Description/Detail/Discussion/Explanation/Interpretation": "DDDDEI",
    "Evaluation": "Evaluation", "Experiment": "Experiment",
    "Intuition/Justification/Motivation/Validation": "IJMV",
    "Methodology": "Methodology", "Novelty": "Novelty", "Presentation": "Presentation",
    "Related Work": "Related Work", "Result": "Result",
    "Significance": "Significance", "Theory": "Theory",
}


def get_paper_type(paper_id: str) -> str:
    return "AIG" if paper_id.upper().startswith("AIG") else "OTHER"


def load_category_sets_by_paper(folder_name: str) -> dict[str, set[str]]:
    """
    Returns {paper_id: set_of_categories}, unioning across all reviewers
    found for that paper within this folder. AIG papers only.
    """
    path = ARG_DIR / folder_name / "parsed" / "classified.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))

    paper_sets: dict[str, set[str]] = {}
    for paper_id, reviewers in data.items():
        if get_paper_type(paper_id) != "AIG":
            continue
        cats: set[str] = set()
        for points in reviewers.values():
            for entry in points.values():
                for asp in entry.get("aspects", []):
                    label = ASPECT_TO_DISPLAY.get(asp)
                    if label:
                        cats.add(label)
        if cats:
            paper_sets.setdefault(paper_id, set()).update(cats)

    return paper_sets


def safe_divide(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator > 0 else 0.0


def compute_f1(recall: float, precision: float) -> float:
    denom = recall + precision
    return round(2 * recall * precision / denom, 4) if denom > 0 else 0.0


def main():
    human_sets = load_category_sets_by_paper(HUMAN_FOLDER)
    print(f"Human (FARS) reviews with categorized weaknesses: {len(human_sets)} AIG papers")

    per_paper_rows = []
    summary_rows = []

    for arg_label, folder_name in ARG_FOLDERS.items():
        arg_sets = load_category_sets_by_paper(folder_name)
        common_papers = sorted(set(human_sets) & set(arg_sets))

        recalls, precisions, f1s = [], [], []

        for paper_id in common_papers:
            h_cats = human_sets[paper_id]
            a_cats = arg_sets[paper_id]
            intersection = h_cats & a_cats

            r = safe_divide(len(intersection), len(h_cats))
            p = safe_divide(len(intersection), len(a_cats))
            f1 = compute_f1(r, p)

            recalls.append(r)
            precisions.append(p)
            f1s.append(f1)

            per_paper_rows.append({
                "arg": arg_label,
                "paper_id": paper_id,
                "human_categories": ",".join(sorted(h_cats)),
                "arg_categories": ",".join(sorted(a_cats)),
                "n_human_categories": len(h_cats),
                "n_arg_categories": len(a_cats),
                "n_overlap": len(intersection),
                "recall": r,
                "precision": p,
                "f1": f1,
            })

        n = len(common_papers)
        mean_recall = round(sum(recalls) / n, 4) if n else 0.0
        mean_precision = round(sum(precisions) / n, 4) if n else 0.0
        mean_f1 = round(sum(f1s) / n, 4) if n else 0.0

        summary_rows.append({
            "arg": arg_label,
            "n_papers": n,
            "mean_recall": mean_recall,
            "mean_precision": mean_precision,
            "mean_f1": mean_f1,
        })

        print(f"\n=== {arg_label} ===")
        print(f"  Matched AIG papers: {n}")
        print(f"  Mean recall    : {mean_recall:.2%}  (share of human-flagged categories the ARG also flagged)")
        print(f"  Mean precision : {mean_precision:.2%}  (share of ARG-flagged categories humans also flagged)")
        print(f"  Mean F1        : {mean_f1:.4f}")

    by_paper_df = pd.DataFrame(per_paper_rows)
    summary_df = pd.DataFrame(summary_rows)

    os.makedirs(OUT_BY_PAPER.parent, exist_ok=True)
    by_paper_df.to_csv(OUT_BY_PAPER, index=False)
    summary_df.to_csv(OUT_SUMMARY, index=False)

    print(f"\nWrote {OUT_BY_PAPER}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
