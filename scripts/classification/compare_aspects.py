"""
compare_aspects.py
==================
Compares Lu et al. (2025) aspect predictions (from classified.json files)
against manual category tags in the review log CSV.

Only includes short human reviews (human_reviews and openreview folders).
cspaper reviews are excluded: they are too long and comprehensive for
binary presence/absence comparison to be meaningful — Lu et al. predicts
every category at least once across 38+ points, making lu_bin always 1.

For each matched (paper_id, reviewer) pair it:
  1. Collects the predicted Lu et al. COARSE aspects across all critique points
  2. Maps them to the manual taxonomy via the crosswalk
  3. Computes per-category binary Cohen's Kappa across all pairs,
     restricted to the 7 categories shared by both taxonomies

Reads:
  - ../../data/manual_review_log.csv
  - ../../arg_outputs/human_reviews/parsed/classified.json
  - ../../arg_outputs/openreview/parsed/classified.json

Writes:
  - ../../data/aspect_comparison.csv

Usage:
    python scripts/classification/compare_aspects.py
"""

import csv
import json
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR  = Path(__file__).parent
DATA_DIR    = (SCRIPT_DIR / "../../data").resolve()
ARG_DIR     = (SCRIPT_DIR / "../../arg_outputs").resolve()
REVIEW_LOG  = DATA_DIR / "manual_review_log.csv"
OUTPUT_PATH = DATA_DIR / "aspect_comparison.csv"

# Only load classified.json from these folders — cspaper excluded
SHORT_REVIEW_FOLDERS = {"human_reviews", "openreview"}

# ---------------------------------------------------------------------------
# Crosswalk: Lu et al. COARSE aspect → manual taxonomy category
# ---------------------------------------------------------------------------
LU_TO_MINE = {
    "Experiment":   ["experimentation"],
    "Ablation":     ["experimentation"],
    "Data/Task":    ["experimentation"],
    "Methodology":  ["methodology/theory"],
    "Theory":       ["methodology/theory"],
    "Intuition/Justification/Motivation/Validation": ["methodology/theory"],
    "Novelty":      ["methodology/theory"],
    "Contribution": ["methodology/theory"],
    "Comparison":   ["comparison"],
    "Evaluation":   ["evaluation"],
    "Result":       ["evaluation"],
    "Analysis":     ["analysis"],
    "Presentation": ["notation/typos"],
    "Related Work": ["related work"],
    # No manual equivalent — excluded from Kappa:
    "Significance": [],
    "Definition/Description/Detail/Discussion/Explanation/Interpretation": [],
    "-": [],
}

SHARED_CATEGORIES = [
    "experimentation",
    "methodology/theory",
    "comparison",
    "evaluation",
    "analysis",
    "notation/typos",
    "related work",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_cats(cell: str) -> set[str]:
    if not cell or not cell.strip():
        return set()
    return {c.strip().lower() for c in cell.split(",") if c.strip()}


def map_to_mine(aspects_set: set[str]) -> set[str]:
    result = set()
    for asp in aspects_set:
        result.update(LU_TO_MINE.get(asp, []))
    return result


def cohen_kappa(y1: list[int], y2: list[int]) -> float | None:
    n = len(y1)
    if n == 0:
        return None
    p_obs = sum(a == b for a, b in zip(y1, y2)) / n
    p1    = sum(y1) / n
    p2    = sum(y2) / n
    p_exp = (p1 * p2) + ((1 - p1) * (1 - p2))
    if p_exp == 1.0:
        return None
    return (p_obs - p_exp) / (1 - p_exp)


def kappa_label(k: float | None) -> str:
    if k is None:  return "undefined"
    if k < 0:      return "poor (worse than chance)"
    if k < 0.20:   return "slight"
    if k < 0.40:   return "fair"
    if k < 0.60:   return "moderate"
    if k < 0.80:   return "substantial"
    return "almost perfect"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_review_log(path: Path) -> dict:
    log = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            paper_id = row["paper_id"].strip()
            reviewer = row["reviewer"].strip()
            if not paper_id or not reviewer:
                continue
            qa  = parse_cats(row.get("quality-altering points", ""))
            ref = parse_cats(row.get("refining points", ""))
            log[(paper_id, reviewer)] = {
                "paper_type": row.get("paper_type", "").strip(),
                "qa_cats":    qa,
                "ref_cats":   ref,
                "all_cats":   qa | ref,
            }
    return log


def load_short_classified(arg_dir: Path) -> dict:
    classified = {}
    for path in sorted(arg_dir.glob("*/parsed/classified.json")):
        folder = path.parent.parent.name
        if folder not in SHORT_REVIEW_FOLDERS:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for paper_id, reviewers in data.items():
            for rev_id, points in reviewers.items():
                freq = Counter()
                for entry in points.values():
                    for asp in entry.get("aspects", []):
                        if asp and asp != "-":
                            freq[asp] += 1
                classified[(paper_id, rev_id)] = {
                    "aspects_freq": freq,
                    "aspects_set":  set(freq.keys()),
                    "point_count":  len(points),
                }
    return classified


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not REVIEW_LOG.exists():
        raise SystemExit(f"Review log not found: {REVIEW_LOG}")

    review_log = load_review_log(REVIEW_LOG)
    classified = load_short_classified(ARG_DIR)

    common   = sorted(set(review_log.keys()) & set(classified.keys()))
    only_log = sorted(set(review_log.keys()) - set(classified.keys()))

    print(f"Review log entries       : {len(review_log)}")
    print(f"Short review pairs loaded: {len(classified)}")
    print(f"Matched pairs            : {len(common)}")
    if only_log:
        print(f"In log only              : {len(only_log)}")
        for k in only_log:
            print(f"  {k}")
    print()

    rows = []
    kappa_labels = {cat: {"mine": [], "lu": []} for cat in SHARED_CATEGORIES}

    for (paper_id, reviewer) in common:
        log = review_log[(paper_id, reviewer)]
        cls = classified[(paper_id, reviewer)]

        mine_all  = log["all_cats"]
        lu_mapped = map_to_mine(cls["aspects_set"])
        lu_no_equiv = {a for a in cls["aspects_set"] if not LU_TO_MINE.get(a)}

        per_cat = {}
        for cat in SHARED_CATEGORIES:
            y = int(cat in mine_all)
            l = int(cat in lu_mapped)
            kappa_labels[cat]["mine"].append(y)
            kappa_labels[cat]["lu"].append(l)
            per_cat[cat] = (y, l)

        top_aspects = ", ".join(
            f"{a}({n})" for a, n in cls["aspects_freq"].most_common(8)
        )
        cat_agreement = "; ".join(
            f"{cat}:{'✓' if y==l else '✗'}(y={y},lu={l})"
            for cat, (y, l) in per_cat.items()
        )

        rows.append({
            "paper_id":           paper_id,
            "paper_type":         log["paper_type"],
            "reviewer":           reviewer,
            "n_points":           cls["point_count"],
            "mine_qa_cats":       ", ".join(sorted(log["qa_cats"])),
            "mine_ref_cats":      ", ".join(sorted(log["ref_cats"])),
            "mine_all_cats":      ", ".join(sorted(mine_all)),
            "lu_aspects_top8":    top_aspects,
            "lu_mapped_to_mine": ", ".join(sorted(lu_mapped)),
            "in_mine_not_lu":    ", ".join(sorted(
                (mine_all - lu_mapped) & set(SHARED_CATEGORIES)
            )),
            "in_lu_not_mine":    ", ".join(sorted(lu_mapped - mine_all)),
            "lu_no_equiv":        ", ".join(sorted(lu_no_equiv)),
            "per_cat_agreement":  cat_agreement,
        })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "paper_id", "paper_type", "reviewer", "n_points",
        "mine_qa_cats", "mine_ref_cats", "mine_all_cats",
        "lu_aspects_top8", "lu_mapped_to_mine",
        "in_mine_not_lu", "in_lu_not_mine", "lu_no_equiv",
        "per_cat_agreement",
    ]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✓  Written → {OUTPUT_PATH}\n")

    # Kappa summary
    print(f"Per-category Cohen's Kappa  (human/openreview only, n={len(common)} pairs)")
    print(f"{'Category':<25} {'Mine=1':>8} {'Lu=1':>6} {'Kappa':>7}  Interpretation")
    print("-" * 68)
    kappas = []
    for cat in SHARED_CATEGORIES:
        y_list = kappa_labels[cat]["mine"]
        l_list = kappa_labels[cat]["lu"]
        k = cohen_kappa(y_list, l_list)
        kappas.append(k)
        k_str = f"{k:.3f}" if k is not None else "  N/A"
        y1 = sum(y_list)
        l1 = sum(l_list)
        print(f"  {cat:<23} {y1:>7}/{len(y_list)}  {l1:>4}/{len(l_list)} {k_str:>7}  {kappa_label(k)}")

    valid = [k for k in kappas if k is not None]
    if valid:
        print("-" * 68)
        print(f"  {'Mean':<23} {sum(valid)/len(valid):>7.3f}")

    print()
    print("Excluded from Kappa:")
    print("  cspaper reviews    — too long, Lu et al. predicts all categories")
    print("  'reproducibility'  — no equivalent in Lu et al. taxonomy")
    print("  'Significance'     — no equivalent in manual taxonomy")
    print("  'DDDDEI'           — no equivalent in manual taxonomy")


if __name__ == "__main__":
    main()