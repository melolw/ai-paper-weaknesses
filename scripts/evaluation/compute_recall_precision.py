"""
compute_recall_precision.py

Computes Recall and Precision for an ARG by comparing its parsed critiques
against the ground truth annotations. Results are broken down by authorship type.

Recall  = (# verified errors caught by ARG) / (# total verified errors)
Precision = (# ARG critiques matching a verified error) / (# total ARG critiques)

Matching is done via keyword overlap between the ARG critique description
and the ground truth error description (configurable threshold).
For more reliable matching, consider semantic similarity via sentence-transformers.

Usage:
    python scripts/evaluation/compute_recall_precision.py \
        --ground_truth annotations/ground_truth/ \
        --arg_outputs arg_outputs/deepreviewer/parsed/ \
        --arg_name deepreviewer \
        --output_dir results/tables/

Output:
    results/tables/deepreviewer_recall_precision.csv
    results/tables/deepreviewer_recall_precision_by_authorship.csv
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MATCH_THRESHOLD = 0.25   # Cosine similarity threshold for a critique-error match
FIELDNAMES_OVERALL = ["arg", "total_errors", "errors_caught", "recall",
                       "total_critiques", "critiques_matched", "precision", "f1"]
FIELDNAMES_BY_AUTH = ["arg", "authorship_type", "total_errors", "errors_caught", "recall",
                       "total_critiques", "critiques_matched", "precision", "f1"]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_ground_truth(gt_dir: str) -> pd.DataFrame:
    """Load all annotation CSVs into a single DataFrame, skipping the template."""
    frames = []
    for fname in os.listdir(gt_dir):
        if fname.endswith(".csv") and fname != "TEMPLATE.csv":
            path = os.path.join(gt_dir, fname)
            try:
                df = pd.read_csv(path)
                frames.append(df)
            except Exception as e:
                print(f"  Warning: could not load {path}: {e}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_arg_outputs(parsed_dir: str) -> dict[str, list[dict]]:
    """Load all parsed ARG JSON files. Returns {paper_id: [critiques]}."""
    outputs = {}
    for fname in os.listdir(parsed_dir):
        if fname.endswith(".json"):
            path = os.path.join(parsed_dir, fname)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            paper_id = data.get("paper_id", fname.replace(".json", ""))
            outputs[paper_id] = data.get("critiques", [])
    return outputs


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def match_critiques_to_errors(
    critiques: list[dict],
    errors: pd.DataFrame,
    threshold: float = MATCH_THRESHOLD,
) -> tuple[set, set]:
    """
    For a single paper, determine which ground truth errors were caught
    and which critiques matched a verified error.

    Returns:
        caught_error_ids   : set of error_ids from ground truth that were matched
        matched_critique_ids: set of critique_ids from ARG that matched an error
    """
    if errors.empty or not critiques:
        return set(), set()

    error_texts    = errors["description"].fillna("").tolist()
    critique_texts = [c["description"] for c in critiques]
    critique_ids   = [c["critique_id"] for c in critiques]
    error_ids      = errors["error_id"].tolist()

    all_texts = error_texts + critique_texts
    try:
        vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
        tfidf = vectorizer.fit_transform(all_texts)
    except ValueError:
        return set(), set()

    n_errors   = len(error_texts)
    error_vecs = tfidf[:n_errors]
    crit_vecs  = tfidf[n_errors:]

    sim_matrix = cosine_similarity(crit_vecs, error_vecs)  # shape: (n_critiques, n_errors)

    caught_error_ids    = set()
    matched_critique_ids = set()

    for c_idx, row in enumerate(sim_matrix):
        best_score = row.max()
        best_error_idx = row.argmax()
        if best_score >= threshold:
            caught_error_ids.add(error_ids[best_error_idx])
            matched_critique_ids.add(critique_ids[c_idx])

    return caught_error_ids, matched_critique_ids


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def safe_divide(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator > 0 else 0.0


def compute_f1(recall: float, precision: float) -> float:
    denom = recall + precision
    return round(2 * recall * precision / denom, 4) if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_metrics(
    gt_df: pd.DataFrame,
    arg_outputs: dict[str, list[dict]],
    arg_name: str,
) -> tuple[list[dict], list[dict]]:
    """
    Compute overall and per-authorship-type metrics.

    Returns:
        overall_rows    : list of one dict (overall metrics)
        by_auth_rows    : list of dicts per authorship type
    """
    # Only consider errors that have been validated (needs_review == False)
    if "needs_review" in gt_df.columns:
        verified = gt_df[gt_df["needs_review"].astype(str).str.lower() != "true"].copy()
    else:
        verified = gt_df.copy()

    # Aggregate per paper
    stats_overall = defaultdict(int)
    stats_by_auth = defaultdict(lambda: defaultdict(int))

    paper_ids = verified["paper_id"].unique()

    for paper_id in paper_ids:
        paper_errors = verified[verified["paper_id"] == paper_id]
        authorship   = paper_errors["authorship_type"].iloc[0] if not paper_errors.empty else "unknown"
        critiques    = arg_outputs.get(paper_id, [])

        caught, matched = match_critiques_to_errors(critiques, paper_errors)

        n_errors    = len(paper_errors)
        n_caught    = len(caught)
        n_critiques = len(critiques)
        n_matched   = len(matched)

        stats_overall["total_errors"]      += n_errors
        stats_overall["errors_caught"]     += n_caught
        stats_overall["total_critiques"]   += n_critiques
        stats_overall["critiques_matched"] += n_matched

        stats_by_auth[authorship]["total_errors"]      += n_errors
        stats_by_auth[authorship]["errors_caught"]     += n_caught
        stats_by_auth[authorship]["total_critiques"]   += n_critiques
        stats_by_auth[authorship]["critiques_matched"] += n_matched

    # Overall
    te, ec, tc, cm = (
        stats_overall["total_errors"],
        stats_overall["errors_caught"],
        stats_overall["total_critiques"],
        stats_overall["critiques_matched"],
    )
    recall    = safe_divide(ec, te)
    precision = safe_divide(cm, tc)
    overall_rows = [{
        "arg": arg_name, "total_errors": te, "errors_caught": ec, "recall": recall,
        "total_critiques": tc, "critiques_matched": cm, "precision": precision,
        "f1": compute_f1(recall, precision),
    }]

    # By authorship type
    by_auth_rows = []
    for auth, s in stats_by_auth.items():
        r = safe_divide(s["errors_caught"], s["total_errors"])
        p = safe_divide(s["critiques_matched"], s["total_critiques"])
        by_auth_rows.append({
            "arg": arg_name, "authorship_type": auth,
            "total_errors": s["total_errors"], "errors_caught": s["errors_caught"], "recall": r,
            "total_critiques": s["total_critiques"], "critiques_matched": s["critiques_matched"],
            "precision": p, "f1": compute_f1(r, p),
        })

    return overall_rows, by_auth_rows


def write_results(rows: list[dict], path: str, fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compute Recall and Precision for an ARG.")
    parser.add_argument("--ground_truth", required=True, help="Path to ground truth directory.")
    parser.add_argument("--arg_outputs",  required=True, help="Path to parsed ARG output directory.")
    parser.add_argument("--arg_name",     required=True, help="ARG identifier (e.g. 'deepreviewer').")
    parser.add_argument("--output_dir",   default="results/tables/", help="Where to save result CSVs.")
    parser.add_argument(
        "--threshold", type=float, default=MATCH_THRESHOLD,
        help=f"Cosine similarity threshold for matching (default: {MATCH_THRESHOLD}).",
    )
    args = parser.parse_args()

    print(f"Loading ground truth from {args.ground_truth}...")
    gt_df = load_ground_truth(args.ground_truth)
    if gt_df.empty:
        print("No ground truth annotations found. Exiting.")
        sys.exit(1)
    print(f"  {len(gt_df)} annotation rows loaded.")

    print(f"Loading ARG outputs from {args.arg_outputs}...")
    arg_outputs = load_arg_outputs(args.arg_outputs)
    print(f"  {len(arg_outputs)} paper review(s) loaded.")

    print("Computing metrics...")
    overall_rows, by_auth_rows = compute_metrics(gt_df, arg_outputs, args.arg_name)

    os.makedirs(args.output_dir, exist_ok=True)
    write_results(
        overall_rows,
        os.path.join(args.output_dir, f"{args.arg_name}_recall_precision.csv"),
        FIELDNAMES_OVERALL,
    )
    write_results(
        by_auth_rows,
        os.path.join(args.output_dir, f"{args.arg_name}_recall_precision_by_authorship.csv"),
        FIELDNAMES_BY_AUTH,
    )

    # Print summary to terminal
    print(f"\n=== {args.arg_name.upper()} — Overall ===")
    for row in overall_rows:
        print(f"  Recall:    {row['recall']:.2%}  ({row['errors_caught']}/{row['total_errors']} errors caught)")
        print(f"  Precision: {row['precision']:.2%}  ({row['critiques_matched']}/{row['total_critiques']} critiques matched)")
        print(f"  F1:        {row['f1']:.4f}")

    print(f"\n=== {args.arg_name.upper()} — By Authorship Type ===")
    for row in sorted(by_auth_rows, key=lambda r: r["authorship_type"]):
        print(f"  {row['authorship_type']:<30} R={row['recall']:.2%}  P={row['precision']:.2%}  F1={row['f1']:.4f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
