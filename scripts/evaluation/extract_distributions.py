"""
extract_distributions.py
========================
Reads arg_outputs/cspaper/parsed/classified.json and computes the average
proportion of critique points touching each aspect category, per paper type.
Prints JSON to stdout — paste the output back to build the chart.

Usage:
    python scripts/preprocessing/extract_distributions.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
CLASSIFIED   = (SCRIPT_DIR / "../../arg_outputs/cspaper/parsed/classified.json").resolve()

LU_TO_YOURS = {
    "Experiment":   "experimentation",
    "Ablation":     "experimentation",
    "Data/Task":    "experimentation",
    "Methodology":  "methodology/theory",
    "Theory":       "methodology/theory",
    "Intuition/Justification/Motivation/Validation": "methodology/theory",
    "Novelty":      "methodology/theory",
    "Contribution": "methodology/theory",
    "Comparison":   "comparison",
    "Evaluation":   "evaluation",
    "Result":       "evaluation",
    "Analysis":     "analysis",
    "Presentation": "notation/typos",
    "Related Work": "related work",
    "Significance": "significance",
    "Definition/Description/Detail/Discussion/Explanation/Interpretation": "clarity/detail",
}

CATEGORIES = [
    "experimentation", "methodology/theory", "comparison", "evaluation",
    "analysis", "notation/typos", "related work", "significance", "clarity/detail",
]

def get_paper_type(paper_id: str) -> str:
    parts = paper_id.split("_")
    # e.g. AIG_CUR_... → AIG_CUR, HAH_... → HAH, HUM_ACC_... → HUM_ACC, HUM_REJ_... → HUM_REJ
    if parts[0] == "AIG":
        return "AIG_CUR"
    elif parts[0] == "HAH":
        return "HAH"
    elif parts[0] == "HUM" and parts[1] == "ACC":
        return "HUM_ACC"
    elif parts[0] == "HUM" and parts[1] == "REJ":
        return "HUM_REJ"
    return "OTHER"

def main():
    if not CLASSIFIED.exists():
        raise SystemExit(f"Not found: {CLASSIFIED}")

    data = json.loads(CLASSIFIED.read_text(encoding="utf-8"))

    # {paper_type: [{cat: proportion}, ...]}
    type_papers = defaultdict(list)

    for paper_id, reviewers in data.items():
        ptype = get_paper_type(paper_id)
        for rev_id, points in reviewers.items():
            total = len(points)
            if total == 0:
                continue
            cat_counts = Counter()
            for entry in points.values():
                seen = set()
                for asp in entry.get("aspects", []):
                    mapped = LU_TO_YOURS.get(asp)
                    if mapped and mapped not in seen:
                        cat_counts[mapped] += 1
                        seen.add(mapped)
            type_papers[ptype].append(
                {cat: round(cat_counts.get(cat, 0) / total, 4) for cat in CATEGORIES}
            )

    # Average per paper type
    results = {}
    for ptype in ["AIG_CUR", "HAH", "HUM_ACC", "HUM_REJ"]:
        papers = type_papers.get(ptype, [])
        if not papers:
            continue
        results[ptype] = {
            cat: round(sum(p[cat] for p in papers) / len(papers), 4)
            for cat in CATEGORIES
        }
        results[ptype]["n_papers"] = len(papers)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()