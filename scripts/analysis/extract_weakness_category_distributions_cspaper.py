"""
extract_weakness_category_distributions_cspaper.py

Same as extract_weakness_category_distributions.py, but for the cspaper
automated-reviewer source instead of human reviews. cspaper is an LLM-based
paper-audit tool, not a human reviewer -- this script exists to check whether
the weakness-category patterns found in human reviews (Distribution by
origin / Statistical Comparison) are confirmed, contradicted, or diverge
under an automated reviewer applied uniformly across all four origins.

Data source: cspaper only (all four origins: AIG, HA_COL, HUM_ACC, HUM_REJ).

Output: results/tables/weakness_category_distributions_per_review_cspaper.csv
  columns: paper_id, reviewer_id, origin, n_points, <16 category columns>

Usage:
    python scripts/analysis/extract_weakness_category_distributions_cspaper.py
"""

import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent.parent
ARG_DIR = REPO_ROOT / "arg_outputs"
OUTPUT_CSV = REPO_ROOT / "results/tables/weakness_category_distributions_per_review_cspaper.csv"

CSPAPER_FOLDERS = {"cspaper"}

LU_CATEGORIES = [
    "Ablation", "Analysis", "Comparison", "Contribution", "Data/Task",
    "DDDDEI", "Evaluation", "Experiment", "IJMV", "Methodology",
    "Novelty", "Presentation", "Related Work", "Result", "Significance", "Theory",
]

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


def get_origin(paper_id: str) -> str:
    p = paper_id.upper()
    if p.startswith("AIG"):
        return "AIG"
    if p.startswith("HAH"):
        return "HA_COL"
    if "HUM_ACC" in p:
        return "HUM_ACC"
    if "HUM_REJ" in p:
        return "HUM_REJ"
    return "OTHER"


def main():
    rows = []
    for path in sorted(ARG_DIR.glob("*/parsed/classified.json")):
        folder = path.parent.parent.name
        if folder not in CSPAPER_FOLDERS:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for paper_id, reviewers in data.items():
            origin = get_origin(paper_id)
            if origin == "OTHER":
                continue
            for rev_id, points in reviewers.items():
                total = len(points)
                if total == 0:
                    continue
                cat_counts = {cat: 0 for cat in LU_CATEGORIES}
                for entry in points.values():
                    seen = set()
                    for asp in entry.get("aspects", []):
                        label = ASPECT_TO_DISPLAY.get(asp)
                        if label and label not in seen:
                            cat_counts[label] += 1
                            seen.add(label)
                row = {
                    "paper_id": paper_id,
                    "reviewer_id": rev_id,
                    "origin": origin,
                    "n_points": total,
                }
                for cat in LU_CATEGORIES:
                    row[cat] = cat_counts[cat] / total
                rows.append(row)

    df = pd.DataFrame(rows)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Wrote {len(df)} reviews to {OUTPUT_CSV}")
    print(df.groupby("origin").size().rename("n_reviews"))


if __name__ == "__main__":
    main()
