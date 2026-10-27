"""
generate_rq1_chart.py
=====================
Charts for RQ1 (weaknesses in AI-generated papers), built from the real data.

Charts produced:
  1. rq1_profile.png          -- weakness profile of AIG papers, two panels that
                                 share the category axis:
                                   left : mean share of critique points per review
                                   right: share of reviews that raise the category
                                 The two largest categories are highlighted.
  2. rq1_ratings.png          -- distribution of review ratings for AIG papers.
  3. rq1_cooccurrence.png     -- how often two categories are assigned to the
                                 same critique point (counts, lower triangle).
  4. rq1_marker_correlations.png -- Spearman correlation of each linguistic
                                 marker with the AIG review scores and with the
                                 share of critique devoted to Presentation.

Data sources:
  results/tables/weakness_category_distributions_per_review.csv
  arg_outputs/fars_human_reviews/raw/*.json
  arg_outputs/fars_human_reviews/parsed/classified.json

Output: data/figures/

Usage:
    python scripts/evaluation/generate_rq1_chart.py
"""

import glob
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams.update({
    "pdf.fonttype": 42,   # embed TrueType fonts so text stays selectable and sharp
    "font.size": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 12,
    "axes.titlesize": 12,
    "axes.labelsize": 12,
})

REPO_ROOT = Path(__file__).parent.parent.parent
OUT_DIR = REPO_ROOT / "data/figures"
HUMAN_CSV = REPO_ROOT / "results/tables/weakness_category_distributions_per_review.csv"
FARS_RAW = REPO_ROOT / "arg_outputs/fars_human_reviews/raw"
CLASSIFIED_JSON = REPO_ROOT / "arg_outputs/fars_human_reviews/parsed/classified.json"
RATING_CORR_CSV = REPO_ROOT / "results/tables/aig_rating_correlations.csv"
PRESENTATION_CORR_CSV = REPO_ROOT / "results/tables/presentation_ratio_correlations.csv"

CATEGORIES = [
    "Ablation", "Analysis", "Comparison", "Contribution", "Data/Task",
    "DDDDEI", "Evaluation", "Experiment", "IJMV", "Methodology",
    "Novelty", "Presentation", "Related Work", "Result", "Significance", "Theory",
]

ACCENT = "#2f5d8a"     # highlighted bars (two largest categories)
MUTED = "#b7c4d6"      # all other bars
GRID = "#e6e6e6"
EDGE = "#b8b8b8"
TEXT = "#333333"
N_HIGHLIGHT = 2


def load_profile():
    h = pd.read_csv(HUMAN_CSV)
    h = h[h["origin"] == "AIG"]
    df = pd.DataFrame({
        "share": h[CATEGORIES].mean(),
        "prevalence": (h[CATEGORIES] > 0).mean(),
    }).sort_values("share", ascending=False)
    return df, len(h)


def style_axes(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(EDGE)
    ax.set_axisbelow(True)


def save(fig, name):
    """Save as vector PDF (sharp text in LaTeX) and as high-resolution PNG."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(name).stem
    fig.savefig(OUT_DIR / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_DIR / f"{stem}.png", dpi=500, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {stem}.pdf, {stem}.png")


def profile_chart(df):
    cats = list(df.index)
    pos = list(range(len(cats)))
    colors = [ACCENT if i < N_HIGHLIGHT else MUTED for i in pos]

    fig, (a1, a2) = plt.subplots(
        1, 2, figsize=(8.6, 6.2), sharey=True,
        gridspec_kw={"width_ratios": [1, 1], "wspace": 0.06},
    )

    panels = [
        (a1, df["share"], 0.40, "Share of critique points",
         "mean proportion per review"),
        (a2, df["prevalence"], 1.12, "Reviews raising the category",
         "share of all reviews"),
    ]
    for ax, values, xmax, title, sub in panels:
        ax.barh(pos, values, height=0.68, color=colors, zorder=3)
        for i, v in zip(pos, values):
            ax.text(v + xmax * 0.012, i, f"{v * 100:.0f}%" if xmax > 1 else f"{v * 100:.1f}%",
                    va="center", ha="left", fontsize=11, color=TEXT)
        ax.set_xlim(0, xmax)
        ax.set_xticks([])
        ax.set_title(f"{title}\n", fontsize=12, loc="left", pad=6)
        ax.text(0, 1.0, sub, transform=ax.transAxes, fontsize=10, color="#777777",
                va="bottom", ha="left")
        style_axes(ax)
        ax.spines["bottom"].set_visible(False)

    a1.set_yticks(pos)
    a1.set_yticklabels(cats)
    a1.invert_yaxis()
    a1.tick_params(axis="y", length=0)
    a2.tick_params(axis="y", length=0)
    a2.spines["left"].set_visible(False)

    fig.tight_layout()
    return fig


def load_ratings():
    ratings = []
    for p in glob.glob(str(FARS_RAW / "*.json")):
        d = json.load(open(p))
        for r in d.get("reviews", []):
            if r.get("scores", {}).get("rating") is not None:
                ratings.append(r["scores"]["rating"])
    return ratings


def ratings_chart():
    ratings = load_ratings()
    counts = Counter(ratings)
    levels = sorted(counts)
    fig, ax = plt.subplots(figsize=(5.6, 3.9))

    ax.bar([str(l) for l in levels], [counts[l] for l in levels], width=0.62,
           color=ACCENT, zorder=3)
    for i, l in enumerate(levels):
        ax.text(i, counts[l] + 1, f"{counts[l]}\n({counts[l] / len(ratings):.0%})",
                ha="center", fontsize=11, color=TEXT)
    ax.set_ylim(0, max(counts.values()) * 1.28)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of reviews")
    ax.yaxis.grid(True, color=GRID, zorder=0)
    style_axes(ax)
    fig.tight_layout()
    return fig


SHORT_NAMES = {
    "Definition/Description/Detail/Discussion/Explanation/Interpretation": "DDDDEI",
    "Intuition/Justification/Motivation/Validation": "IJMV",
}


def load_cooccurrence(order):
    """Count critique points that carry both categories, for every category pair."""
    data = json.load(open(CLASSIFIED_JSON))
    idx = {c: i for i, c in enumerate(order)}
    mat = np.zeros((len(order), len(order)), dtype=int)
    for reviews in data.values():
        for points in reviews.values():
            for p in points.values():
                cats = {SHORT_NAMES.get(a, a) for a in p["aspects"]}
                cats = sorted(c for c in cats if c in idx)
                for a, b in combinations(cats, 2):
                    mat[idx[a], idx[b]] += 1
                    mat[idx[b], idx[a]] += 1
    return mat


def cooccurrence_chart(df):
    order = list(df.index)
    full = load_cooccurrence(order)
    # Lower triangle without the empty first row and last column.
    rows, cols = order[1:], order[:-1]
    mat = full[1:, :-1]
    m = len(rows)
    masked = np.ma.masked_where(np.triu(np.ones((m, m), dtype=bool), k=1), mat)
    cmap = LinearSegmentedColormap.from_list("blue", ["#f1f4f8", ACCENT])
    cmap.set_bad("white")

    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    ax.imshow(masked, cmap=cmap, vmin=0, vmax=mat.max())
    for i in range(m):
        for j in range(i + 1):
            v = mat[i, j]
            if v > 0:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=7.5,
                        color="white" if v > 0.55 * mat.max() else TEXT)
    ax.set_xticks(range(m))
    ax.set_yticks(range(m))
    ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=9.5)
    ax.set_yticklabels(rows, fontsize=9.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, m, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, m, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    fig.tight_layout()
    return fig


MARKERS = [
    ("ttr", "Type-token ratio"),
    ("avg_sentence_length", "Avg. sentence length"),
    ("flesch_reading_ease", "Flesch Reading Ease"),
    ("dale_chall_score", "Dale-Chall score"),
    ("flesch_kincaid_grade", "Flesch-Kincaid grade"),
    ("gunning_fog", "Gunning Fog"),
    ("difficult_word_ratio", "Difficult-word ratio"),
    ("polysyllable_count", "Polysyllable count"),
]
SCORE_DIMS = [
    ("rating", "Rating"),
    ("soundness", "Soundness"),
    ("presentation", "Presentation\nscore"),
    ("contribution", "Contri-\nbution"),
    ("confidence", "Confidence"),
]


def marker_correlation_chart():
    """Spearman correlation of each linguistic marker with the AIG review scores.

    No cell is significant after Holm-Bonferroni correction.
    The last column is the share of a paper's critique devoted to Presentation.
    """
    rate = pd.read_csv(RATING_CORR_CSV)
    pres = pd.read_csv(PRESENTATION_CORR_CSV)
    pres = pres[pres["category"] == "AIG"].set_index("marker")

    keys = [k for k, _ in MARKERS]
    rho = np.full((len(keys), len(SCORE_DIMS) + 1), np.nan)
    raw_sig = np.zeros_like(rho, dtype=bool)
    # Only corrected results are shown: nothing is highlighted, because no
    # correlation is significant after Holm-Bonferroni correction.
    for j, (dim, _) in enumerate(SCORE_DIMS):
        sub = rate[rate["score_dimension"] == dim].set_index("marker")
        for i, k in enumerate(keys):
            rho[i, j] = sub.loc[k, "spearman_r"]
    last = len(SCORE_DIMS)
    for i, k in enumerate(keys):
        rho[i, last] = pres.loc[k, "spearman_r"]

    # Leave a thin gap before the Presentation-critique column.
    cols = np.insert(rho, last, np.nan, axis=1)
    sig = np.insert(raw_sig, last, False, axis=1)
    labels = [l for _, l in SCORE_DIMS] + [""] + ["Share of\nPresentation\ncritique"]

    cmap = LinearSegmentedColormap.from_list("div", ["#c47f5a", "#ffffff", ACCENT])
    cmap.set_bad("white")
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    im = ax.imshow(np.ma.masked_invalid(cols), cmap=cmap, vmin=-0.5, vmax=0.5, aspect="auto")
    for i in range(cols.shape[0]):
        for j in range(cols.shape[1]):
            v = cols[i, j]
            if np.isnan(v):
                continue
            text = "0.00" if abs(v) < 0.005 else f"{v:+.2f}".replace("-", "−")
            ax.text(j, i, text, ha="center", va="center", fontsize=9.5, color=TEXT,
                    fontweight="bold" if sig[i, j] else "normal", zorder=6)
            if sig[i, j]:
                ax.add_patch(plt.Rectangle((j - 0.46, i - 0.46), 0.92, 0.92, fill=False,
                                           edgecolor=TEXT, linewidth=2.0, zorder=5))
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([n for _, n in MARKERS], fontsize=10.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(keys), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", length=0)

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label("Spearman ρ", fontsize=10)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(labelsize=9, length=0)
    fig.tight_layout()
    return fig


def main():
    print("Generating RQ1 charts...")
    df, n_h = load_profile()
    save(profile_chart(df), "rq1_profile.png")
    save(ratings_chart(), "rq1_ratings.png")
    save(cooccurrence_chart(df), "rq1_cooccurrence.png")
    save(marker_correlation_chart(), "rq1_marker_correlations.png")
    print(f"\nAll charts saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
