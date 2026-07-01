"""
Quality-altering critiques by paper type — normalized version.

Fixes the issue where raw counts conflate (a) more papers of one type,
and (b) more reviews-per-paper of one type (e.g. AIG_CUR currently has
ARG reviews but no human reviews yet), with an actual difference in
error rates.

Produces THREE views so you can compare and decide which is most honest
to present given current (incomplete) review coverage:
  1. Raw counts (same as before, kept for reference)
  2. Avg critiques per PAPER (normalizes for #papers per type)
  3. Avg critiques per REVIEW (normalizes for #papers AND #reviews per paper)

Also prints a coverage diagnostic table (papers x reviews per type) so
imbalance is visible before interpreting any chart.
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Load data ---
df = pd.read_csv("review_log.csv")

# --- 2. Classify paper type from paper_id prefix ---
def get_paper_type(paper_id):
    if paper_id.startswith("HUM_ACC"):
        return "Human (accepted)"
    elif paper_id.startswith("HUM_REJ"):
        return "Human (rejected)"
    elif paper_id.startswith("AIG_CUR"):
        return "AI-generated (curated)"
    elif paper_id.startswith("HAH"):
        return "Human-AI hybrid"
    return "Unknown"

df["paper_type"] = df["paper_id"].apply(get_paper_type)
df = df[df["paper_type"] != "Unknown"]

# --- 3. Coverage diagnostic: papers and reviews logged per type ---
coverage = df.groupby("paper_type").agg(
    n_reviews=("reviewer", "count"),
    n_papers=("paper_id", "nunique"),
)
coverage["reviews_per_paper"] = (coverage["n_reviews"] / coverage["n_papers"]).round(2)
print("=== Coverage diagnostic (check for imbalance before trusting any chart) ===")
print(coverage)
print()

# --- 4. Explode the comma-separated quality-altering column ---
df["quality-altering points"] = df["quality-altering points"].fillna("")
df["category"] = df["quality-altering points"].str.split(",")
df_exp = df.explode("category").reset_index(drop=True)
df_exp["category"] = df_exp["category"].str.strip().str.lower()
df_exp = df_exp[df_exp["category"] != ""]

order = ["methodology/theory", "evaluation", "experimentation", "comparison", "analysis"]
colors = {
    "Human (accepted)": "#2a78d6",
    "Human (rejected)": "#d62a2a",
    "AI-generated (curated)": "#1baf7a",
    "Human-AI hybrid": "#eda100",
}

def make_chart(summary, title, filename, ylabel):
    summary = summary.reindex(order).fillna(0)
    cols = [c for c in colors if c in summary.columns]
    ax = summary[cols].plot(
        kind="bar", figsize=(9, 5),
        color=[colors[c] for c in cols], width=0.75,
    )
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(title="")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()
    print(f"Saved {filename}")

# --- 5a. RAW counts (kept for reference / comparison) ---
raw = pd.crosstab(df_exp["category"], df_exp["paper_type"])
print("=== Raw counts ===")
print(raw.reindex(order).fillna(0).astype(int))
print()
make_chart(raw, "Quality-altering critiques by paper type (raw count)",
           "quality_by_paper_type_raw.png", "Count")

# --- 5b. Per PAPER (normalizes for number of papers per type) ---
raw_counts = pd.crosstab(df_exp["category"], df_exp["paper_type"])
n_papers = coverage["n_papers"]
per_paper = raw_counts.reindex(columns=n_papers.index).div(n_papers, axis=1)
print("=== Avg critiques per paper ===")
print(per_paper.reindex(order).round(2))
print()
make_chart(per_paper, "Quality-altering critiques per paper, by paper type",
           "quality_by_paper_type_per_paper.png", "Avg count per paper")

# --- 5c. Per REVIEW (normalizes for number of papers AND reviews/paper) ---
n_reviews = coverage["n_reviews"]
per_review = raw_counts.reindex(columns=n_reviews.index).div(n_reviews, axis=1)
print("=== Avg critiques per review ===")
print(per_review.reindex(order).round(2))
print()
make_chart(per_review, "Quality-altering critiques per review, by paper type",
           "quality_by_paper_type_per_review.png", "Avg count per review")