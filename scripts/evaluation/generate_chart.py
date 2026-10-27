"""
generate_chart.py
=================
Generates 5 aspect frequency distribution charts from all classified.json files.

Charts produced:
  1. By paper type — cspaper reviews only
  2. AIG deep dive — cspaper vs paperreview.ai vs FARS human reviews
  3. HUM_ACC vs HUM_REJ — cspaper reviews only
  4. By paper type — human reviews only
  5. By paper type — cspaper + human reviews combined

Output: data/figures/chart_1_cspaper.png ... chart_5_combined.png

Usage:
    python scripts/evaluation/generate_chart.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({
    "pdf.fonttype": 42,   # embed TrueType fonts, as in generate_rq1_chart.py
})

SCRIPT_DIR = Path(__file__).parent
ARG_DIR    = (SCRIPT_DIR / "../../arg_outputs").resolve()
OUT_DIR    = (SCRIPT_DIR / "../../data/figures").resolve()

# ---------------------------------------------------------------------------
# Lu et al. 16 COARSE categories
# ---------------------------------------------------------------------------
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

# Folder categories
CSPAPER_FOLDERS       = {"cspaper"}
PAPERREVIEW_FOLDERS   = {"paperreview_ai"}
PAPERAUDIT_FOLDERS    = {"paperaudit_review"}
DEEPREVIEWER_FOLDERS  = {"deepreviewer"}
FARS_HUMAN_FOLDERS    = {"fars_human_reviews"}
HUMAN_FOLDERS         = {"human_reviews", "fars_human_reviews", "openreview"}
ALL_FOLDERS           = (CSPAPER_FOLDERS | HUMAN_FOLDERS | PAPERREVIEW_FOLDERS
                          | PAPERAUDIT_FOLDERS | DEEPREVIEWER_FOLDERS)

PAPER_TYPES = ["AIG", "HAH", "HUM_ACC", "HUM_REJ"]
TYPE_LABELS = {
    "AIG":     "AIG\n(AI-generated)",
    "HAH":     "HA_COL\n(human-AI collaborative)",
    "HUM_ACC": "HUM_ACC\n(human accepted)",
    "HUM_REJ": "HUM_REJ\n(human rejected)",
}
# "HAH" is the internal paper-ID prefix (get_paper_type); HA_COL is the
# corpus name used in the thesis — this maps the former to the latter for
# anything displayed on the chart (e.g. the legend).
DISPLAY_SHORT = {"HAH": "HA_COL"}
TYPE_COLORS = {
    "AIG":     "#d4a843",   # muted yellow
    "HAH":     "#6b8cba",   # muted blue
    "HUM_ACC": "#6aaa7a",   # muted green
    "HUM_REJ": "#c97070",   # muted pink/red
}

# ---------------------------------------------------------------------------
# Paper type detection
# ---------------------------------------------------------------------------

def get_paper_type(paper_id: str) -> str:
    p = paper_id.upper()
    if p.startswith("AIG"):
        return "AIG"
    if p.startswith("HAH"):
        return "HAH"
    if "HUM_ACC" in p:
        return "HUM_ACC"
    if "HUM_REJ" in p:
        return "HUM_REJ"
    return "OTHER"

# ---------------------------------------------------------------------------
# Load classified.json files
# ---------------------------------------------------------------------------

def load_classified(arg_dir: Path, allowed_folders: set) -> dict:
    """
    Returns {(paper_id, reviewer_id, folder): {display_label: proportion}}
    """
    all_units = {}
    for path in sorted(arg_dir.glob("*/parsed/classified.json")):
        folder = path.parent.parent.name
        if folder not in allowed_folders:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for paper_id, reviewers in data.items():
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
                all_units[(paper_id, rev_id, folder)] = {
                    cat: cat_counts.get(cat, 0) / total for cat in LU_CATEGORIES
                }
    return all_units

# ---------------------------------------------------------------------------
# Aggregate by paper type
# ---------------------------------------------------------------------------

def aggregate_by_type(units: dict) -> dict:
    """Returns {paper_type: {cat: avg_proportion, n: int}}"""
    type_units = defaultdict(list)
    for (paper_id, _, _), props in units.items():
        ptype = get_paper_type(paper_id)
        if ptype in PAPER_TYPES:
            type_units[ptype].append(props)
    result = {}
    for ptype in PAPER_TYPES:
        u = type_units.get(ptype, [])
        result[ptype] = {
            "values": [sum(p[c] for p in u)/len(u) if u else 0 for c in LU_CATEGORIES],
            "n": len(u),
            "short": ptype,
        }
    return result

# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------

def grouped_bar_chart(ax, groups: dict, title: str, subtitle: str = "", hatches: list = None,
                       orientation: str = "horizontal"):
    """
    Grouped bar chart, horizontal or vertical.

    Horizontal: categories run down the y-axis (no rotated labels needed,
    reads fine at thesis page width), values extend along x.
    Vertical: categories run along the x-axis (rotated labels), values
    extend up the y-axis -- useful for slides/wide layouts.

    groups: {label: {"values": [float x 16], "n": int, "color": str}}
    hatches: optional list of hatch patterns per group (e.g. ['/', '\\', '.', 'o'])
    orientation: "horizontal" or "vertical"
    """
    import matplotlib.colors as mcolors

    n_cats   = len(LU_CATEGORIES)
    n_groups = len(groups)
    bar_w    = 0.8 / n_groups
    pos      = np.arange(n_cats)
    offsets  = np.linspace(-(n_groups-1)/2, (n_groups-1)/2, n_groups) * bar_w

    for i, (label, data) in enumerate(groups.items()):
        rgb = mcolors.to_rgb(data["color"])
        darker = tuple(max(0, c * 0.7) for c in rgb)
        hatch = hatches[i] if hatches else None
        if orientation == "horizontal":
            ax.barh(pos + offsets[i], data["values"], height=bar_w,
                    color=data["color"], edgecolor=darker,
                    linewidth=0.5, hatch=hatch, zorder=3)
        else:
            ax.bar(pos + offsets[i], data["values"], width=bar_w,
                   color=data["color"], edgecolor=darker,
                   linewidth=0.5, hatch=hatch, zorder=3)

    all_vals = [v for d in groups.values() for v in d["values"]]
    val_max = max(all_vals) * 1.15 if all_vals else 0.5

    if orientation == "horizontal":
        ax.set_yticks(pos)
        ax.set_yticklabels(LU_CATEGORIES, fontsize=11)
        ax.invert_yaxis()  # first category (Ablation) at top, matches list order
        ax.set_xlabel("Avg proportion of critique points", fontsize=11)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
        ax.set_xlim(0, val_max)
        ax.tick_params(axis="x", labelsize=10)
        ax.set_ylim(n_cats - 0.5, -0.5)
        ax.grid(axis="x", color="#e1e0d9", linewidth=0.8, zorder=0)
    else:
        ax.set_xticks(pos)
        ax.set_xticklabels(LU_CATEGORIES, fontsize=11, rotation=45, ha="right")
        ax.set_ylabel("Avg proportion of critique points", fontsize=11)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
        ax.set_ylim(0, val_max)
        ax.tick_params(axis="y", labelsize=10)
        ax.set_xlim(-0.5, n_cats - 0.5)
        ax.grid(axis="y", color="#e1e0d9", linewidth=0.8, zorder=0)

    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#c3c2b7")

    handles = [
        mpatches.Patch(color=d["color"],
                       label=f"{d['short']}  (n={d['n']})")
        for lbl, d in groups.items()
    ]
    # Upper-right corner, inside the axes, for both orientations.
    ax.legend(handles=handles, loc="upper right",
              fontsize=10, frameon=True, framealpha=0.85, edgecolor="#c3c2b7")

    full_title = title + (f"\n{subtitle}" if subtitle else "")
    ax.set_title(full_title, fontsize=11, fontweight="normal", pad=12, loc="left")


def save_chart(fig, path):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {path.name}")


def make_both_orientations(groups: dict, title: str, subtitle: str, out_path_stem, hatches: list = None):
    """
    Renders and saves both a horizontal and a vertical version of the same
    chart. `out_path_stem` is a Path without extension; horizontal is saved
    as "<stem>.png" (unchanged filename, so existing references still work)
    and vertical as "<stem>_vertical.png".
    """
    fig_h, ax_h = plt.subplots(figsize=(6.3, 7.5))
    grouped_bar_chart(ax_h, groups, title, subtitle, hatches=hatches, orientation="horizontal")
    save_chart(fig_h, out_path_stem.with_suffix(".png"))

    fig_v, ax_v = plt.subplots(figsize=(11.2, 4.8))
    grouped_bar_chart(ax_v, groups, title, subtitle, hatches=hatches, orientation="vertical")
    vertical_path = out_path_stem.with_name(out_path_stem.name + "_vertical").with_suffix(".png")
    save_chart(fig_v, vertical_path)

# ---------------------------------------------------------------------------
# Chart 1 — By paper type, cspaper only
# ---------------------------------------------------------------------------

def chart_1(arg_dir):
    units  = load_classified(arg_dir, CSPAPER_FOLDERS)
    dist   = aggregate_by_type(units)
    groups = {
        TYPE_LABELS[t]: {"values": dist[t]["values"], "n": dist[t]["n"],
                         "color": TYPE_COLORS[t], "short": DISPLAY_SHORT.get(t, t)}
        for t in PAPER_TYPES
    }
    make_both_orientations(groups,
        "Critique aspect distribution by paper type",
        "cspaper reviewer only",
        OUT_DIR / "chart_1_cspaper")

# ---------------------------------------------------------------------------
# Chart 2 — AIG deep dive: cspaper vs paperreview.ai vs FARS human
# ---------------------------------------------------------------------------

def chart_2(arg_dir):
    reviewer_groups = {
        "cspaper":           (CSPAPER_FOLDERS,      "#5a7db5"),
        "paperreview.ai":    (PAPERREVIEW_FOLDERS,  "#a07cc5"),
        "paperaudit":        (PAPERAUDIT_FOLDERS,   "#c47f5a"),
        "deepreviewer":      (DEEPREVIEWER_FOLDERS, "#d19a3e"),
        "FARS human reviews":(FARS_HUMAN_FOLDERS,   "#5aab7f"),
    }
    groups = {}
    for label, (folders, color) in reviewer_groups.items():
        units = {k: v for k, v in load_classified(arg_dir, folders).items()
                 if get_paper_type(k[0]) == "AIG"}
        if not units:
            continue
        props_list = list(units.values())
        values = [sum(p[c] for p in props_list)/len(props_list) for c in LU_CATEGORIES]
        groups[label] = {"values": values, "n": len(props_list), "color": color, "short": label}

    make_both_orientations(groups,
        "AIG papers — critique aspects by reviewer type",
        "AI-generated papers (AIG) only",
        OUT_DIR / "chart_2_aig_deepdive")

# ---------------------------------------------------------------------------
# Chart 3 — HUM_ACC vs HUM_REJ, cspaper only
# ---------------------------------------------------------------------------

def chart_3(arg_dir):
    units = load_classified(arg_dir, CSPAPER_FOLDERS)
    dist  = aggregate_by_type(units)
    groups = {
        TYPE_LABELS[t]: {"values": dist[t]["values"], "n": dist[t]["n"],
                         "color": TYPE_COLORS[t], "short": DISPLAY_SHORT.get(t, t)}
        for t in ["HUM_ACC", "HUM_REJ"]
    }
    make_both_orientations(groups,
        "Accepted vs rejected human papers — critique aspect distribution",
        "cspaper reviewer only",
        OUT_DIR / "chart_3_hum_acc_vs_rej")

# ---------------------------------------------------------------------------
# Chart 4 — By paper type, human reviews only
# ---------------------------------------------------------------------------

def chart_4(arg_dir):
    units  = load_classified(arg_dir, HUMAN_FOLDERS)
    dist   = aggregate_by_type(units)
    groups = {
        TYPE_LABELS[t]: {"values": dist[t]["values"], "n": dist[t]["n"],
                         "color": TYPE_COLORS[t], "short": DISPLAY_SHORT.get(t, t)}
        for t in PAPER_TYPES
    }
    make_both_orientations(groups,
        "Critique aspect distribution by paper type",
        "human reviews only (FARS, OpenReview, NLPeer)",
        OUT_DIR / "chart_4_human_reviews")

# ---------------------------------------------------------------------------
# Chart 5 — By paper type, cspaper + human reviews combined
# ---------------------------------------------------------------------------

def chart_5(arg_dir):
    units  = load_classified(arg_dir, CSPAPER_FOLDERS | HUMAN_FOLDERS)
    dist   = aggregate_by_type(units)
    groups = {
        TYPE_LABELS[t]: {"values": dist[t]["values"], "n": dist[t]["n"],
                         "color": TYPE_COLORS[t], "short": DISPLAY_SHORT.get(t, t)}
        for t in PAPER_TYPES
    }
    make_both_orientations(groups,
        "Critique aspect distribution by paper type",
        "cspaper + human reviews combined",
        OUT_DIR / "chart_5_combined")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating charts...")
    chart_1(ARG_DIR)
    chart_2(ARG_DIR)
    chart_3(ARG_DIR)
    chart_4(ARG_DIR)
    chart_5(ARG_DIR)
    print(f"\nAll charts saved to {OUT_DIR}")

if __name__ == "__main__":
    main()