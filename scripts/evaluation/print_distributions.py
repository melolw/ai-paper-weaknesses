"""
print_distributions.py
=======================
Prints aspect frequency distributions in a readable format for analysis.

Usage:
    python scripts/evaluation/print_distributions.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ARG_DIR    = (SCRIPT_DIR / "../../arg_outputs").resolve()

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

PAPER_TYPES = ["AIG", "HAH", "HUM_ACC", "HUM_REJ"]

def get_paper_type(paper_id):
    p = paper_id.upper()
    if p.startswith("AIG"):   return "AIG"
    if p.startswith("HAH"):   return "HAH"
    if "HUM_ACC" in p:        return "HUM_ACC"
    if "HUM_REJ" in p:        return "HUM_REJ"
    return "OTHER"

def load_and_aggregate(arg_dir, allowed_folders):
    type_units = defaultdict(list)
    for path in sorted(arg_dir.glob("*/parsed/classified.json")):
        folder = path.parent.parent.name
        if folder not in allowed_folders:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for paper_id, reviewers in data.items():
            ptype = get_paper_type(paper_id)
            if ptype not in PAPER_TYPES:
                continue
            for rev_id, points in reviewers.items():
                total = len(points)
                if total == 0:
                    continue
                cat_counts = Counter()
                for entry in points.values():
                    seen = set()
                    for asp in entry.get("aspects", []):
                        label = ASPECT_TO_DISPLAY.get(asp)
                        if label and label not in seen:
                            cat_counts[label] += 1
                            seen.add(label)
                type_units[ptype].append(
                    {cat: cat_counts.get(cat, 0) / total for cat in LU_CATEGORIES}
                )

    result = {}
    for ptype in PAPER_TYPES:
        units = type_units.get(ptype, [])
        result[ptype] = {
            cat: sum(u[cat] for u in units) / len(units) if units else 0
            for cat in LU_CATEGORIES
        }
        result[ptype]["_n"] = len(units)
    return result


def print_table(dist, title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    header = f"{'Category':<18}" + "".join(f"{t:>10}" for t in PAPER_TYPES)
    print(header)
    print("-" * 70)
    for cat in LU_CATEGORIES:
        row = f"{cat:<18}"
        vals = [dist[t][cat] for t in PAPER_TYPES]
        max_val = max(vals)
        for t, v in zip(PAPER_TYPES, vals):
            marker = " ◄" if v == max_val and max_val > 0 else ""
            row += f"{v:>9.1%}{marker if marker else ' '}"
        print(row)
    print("-" * 70)
    ns = "  ".join(f"{t}:n={dist[t]['_n']}" for t in PAPER_TYPES)
    print(f"  {ns}")


def main():
    print_table(
        load_and_aggregate(ARG_DIR, {"cspaper"}),
        "CHART 1 — cspaper only"
    )
    print_table(
        load_and_aggregate(ARG_DIR, {"human_reviews", "fars_human_reviews", "openreview"}),
        "CHART 4 — human reviews only"
    )
    print_table(
        load_and_aggregate(ARG_DIR, {"cspaper", "human_reviews", "fars_human_reviews", "openreview"}),
        "CHART 5 — cspaper + human combined"
    )

    # Chart 2 — AIG reviewer breakdown
    print(f"\n{'='*70}")
    print("  CHART 2 — AIG papers by reviewer type")
    print(f"{'='*70}")
    reviewer_configs = {
        "cspaper":       {"cspaper"},
        "paperreview.ai":{"paperreview_ai"},
        "FARS human":    {"fars_human_reviews"},
    }
    reviewers = list(reviewer_configs.keys())
    header = f"{'Category':<18}" + "".join(f"{r:>16}" for r in reviewers)
    print(header)
    print("-" * 70)
    dists = {}
    for label, folders in reviewer_configs.items():
        d = load_and_aggregate(ARG_DIR, folders)
        dists[label] = d.get("AIG", {})
    for cat in LU_CATEGORIES:
        row = f"{cat:<18}"
        vals = [dists[r].get(cat, 0) for r in reviewers]
        max_val = max(vals) if vals else 0
        for r, v in zip(reviewers, vals):
            marker = " ◄" if v == max_val and max_val > 0 else ""
            row += f"{v:>15.1%}{marker if marker else ' '}"
        print(row)
    ns = "  ".join(f"{r}:n={dists[r].get('_n',0)}" for r in reviewers)
    print(f"\n  {ns}")


if __name__ == "__main__":
    main()
