"""
boot_match.py
=============
Computes boot-match agreement (Marchal et al., COLING 2022) between
manual review tags and Lu et al. (2025) RAP classifier predictions.

Boot-match is recommended for multi-label annotation agreement where
multiple labels can simultaneously be true. It bootstraps expected
agreement from each annotator's empirical label distribution, correcting
for the inflated chance agreement inherent in multi-label settings.

Usage:
    python scripts/classification/boot_match.py
"""

import json
import random
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR   = (SCRIPT_DIR / "../../data").resolve()
ARG_DIR    = (SCRIPT_DIR / "../../arg_outputs").resolve()

REVIEW_LOG  = DATA_DIR / "manual_review_log.csv"

SHORT_REVIEW_FOLDERS = {"human_reviews", "openreview"}

N_SIMULATIONS = 1000

SHARED_CATEGORIES = [
    "experimentation",
    "methodology/theory",
    "comparison",
    "evaluation",
    "analysis",
    "notation/typos",
    "related work",
]

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
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

import csv

def load_review_log(path):
    log = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            pid = row["paper_id"].strip()
            rid = row["reviewer"].strip()
            if not pid or not rid:
                continue
            qa  = {c.strip().lower() for c in row.get("quality-altering points","").split(",") if c.strip()}
            ref = {c.strip().lower() for c in row.get("refining points","").split(",") if c.strip()}
            log[(pid, rid)] = qa | ref
    return log

def load_short_classified(arg_dir):
    classified = {}
    for path in sorted(arg_dir.glob("*/parsed/classified.json")):
        folder = path.parent.parent.name
        if folder not in SHORT_REVIEW_FOLDERS:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for pid, reviewers in data.items():
            for rid, points in reviewers.items():
                freq = Counter()
                for entry in points.values():
                    for asp in entry.get("aspects", []):
                        if asp and asp != "-":
                            freq[asp] += 1
                aspects_set = {LU_TO_YOURS[a] for a in freq if a in LU_TO_YOURS}
                classified[(pid, rid)] = aspects_set & set(SHARED_CATEGORIES)
    return classified

# ---------------------------------------------------------------------------
# Boot-match
# ---------------------------------------------------------------------------

def boot_match(pairs_yours, pairs_lu, n_sim=N_SIMULATIONS, seed=42):
    """
    pairs_yours: list of frozensets — your label sets per item
    pairs_lu:    list of frozensets — Lu et al. label sets per item
    Returns: observed, expected, adjusted (boot-match)
    """
    random.seed(seed)
    n = len(pairs_yours)

    # Observed agreement: proportion of items with non-empty intersection
    observed = sum(
        1 for y, l in zip(pairs_yours, pairs_lu) if y & l
    ) / n

    # Marginal distributions
    # For each annotator: P(category) and distribution of label count per item
    def marginals(label_sets):
        cat_counts = Counter()
        size_counts = Counter()
        total_items = len(label_sets)
        for s in label_sets:
            size_counts[len(s)] += 1
            for c in s:
                cat_counts[c] += 1
        # Normalize
        total_labels = sum(cat_counts.values())
        cat_probs  = {c: v/total_labels for c, v in cat_counts.items()} if total_labels else {}
        size_probs = {k: v/total_items for k, v in size_counts.items()}
        return cat_probs, size_probs

    def sample_labels(cat_probs, size_probs):
        """Sample a random label set from the marginal distribution."""
        cats = list(cat_probs.keys())
        probs = [cat_probs[c] for c in cats]
        # Sample number of labels
        sizes = list(size_probs.keys())
        size_weights = [size_probs[s] for s in sizes]
        n_labels = random.choices(sizes, weights=size_weights, k=1)[0]
        if n_labels == 0 or not cats:
            return frozenset()
        # Sample labels without replacement (up to n_labels)
        n_draw = min(n_labels, len(cats))
        drawn = random.choices(cats, weights=probs, k=n_draw)
        return frozenset(drawn)

    yours_cat_probs, yours_size_probs = marginals(pairs_yours)
    lu_cat_probs,    lu_size_probs    = marginals(pairs_lu)

    # Bootstrap expected agreement
    sim_agreements = []
    for _ in range(n_sim):
        sim_intersections = sum(
            1 for _ in range(n)
            if sample_labels(yours_cat_probs, yours_size_probs) &
               sample_labels(lu_cat_probs, lu_size_probs)
        )
        sim_agreements.append(sim_intersections / n)

    expected = sum(sim_agreements) / n_sim
    adjusted = (observed - expected) / (1 - expected) if expected < 1 else 0

    return observed, expected, adjusted

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    review_log = load_review_log(REVIEW_LOG)
    classified  = load_short_classified(ARG_DIR)

    common = sorted(set(review_log.keys()) & set(classified.keys()))
    print(f"Matched pairs: {len(common)}\n")

    pairs_yours = []
    pairs_lu    = []

    for pid, rid in common:
        yours = review_log[(pid, rid)] & set(SHARED_CATEGORIES)
        lu    = classified[(pid, rid)]
        pairs_yours.append(frozenset(yours))
        pairs_lu.append(frozenset(lu))

    # Overall boot-match
    observed, expected, adjusted = boot_match(pairs_yours, pairs_lu)

    print("Boot-match agreement (Marchal et al., COLING 2022)")
    print(f"  Observed agreement : {observed:.3f}")
    print(f"  Expected agreement : {expected:.3f}  (bootstrapped, n={N_SIMULATIONS} simulations)")
    print(f"  Adjusted (boot-κ)  : {adjusted:.3f}")
    print()
    print("Interpretation (Landis & Koch 1977 scale):")
    if adjusted < 0:      interp = "poor (worse than chance)"
    elif adjusted < 0.20: interp = "slight"
    elif adjusted < 0.40: interp = "fair"
    elif adjusted < 0.60: interp = "moderate"
    elif adjusted < 0.80: interp = "substantial"
    else:                 interp = "almost perfect"
    print(f"  {interp}")
    print()
    print("Note: cspaper reviews excluded (long reviews → Lu always predicts all categories)")
    print("      reproducibility, Significance, DDDDEI excluded (no equivalent in shared taxonomy)")

if __name__ == "__main__":
    main()
