"""
extract_weakness_category_distributions.py

Builds a per-review table of category proportions using Lu et al.'s (2025) 16
COARSE aspect categories, for the four paper origins (AIG, HA_COL, HUM_ACC,
HUM_REJ). Unit of analysis is the individual review, not the paper -- this
matches the descriptive distribution shown in the "Distribution by origin"
figure (generate_chart.py's chart_4 / print_distributions.py's CHART 4).

Data source: human reviews only.
  fars_human_reviews -> AIG
  openreview          -> HA_COL
  human_reviews        -> HUM_ACC / HUM_REJ

For each review, computes: (# critique points touching category X) / (total
critique points in that review), for each of the 16 categories. A critique
point counts toward a category only once even if the classifier tagged it
with that category more than once (same "seen" dedup logic already used in
generate_chart.py / print_distributions.py).

Output: results/tables/weakness_category_distributions_per_review.csv
  columns: paper_id, reviewer_id, origin, n_points, <16 category columns>

Usage:
    python scripts/analysis/extract_weakness_category_distributions.py
"""

import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent.parent
ARG_DIR = REPO_ROOT / "arg_outputs"
OUTPUT_CSV = REPO_ROOT / "results/tables/weakness_category_distributions_per_review.csv"

HUMAN_FOLDERS = {"human_reviews", "fars_human_reviews", "openreview"}

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
        if folder not in HUMAN_FOLDERS:
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
