"""
extract_fars_and_rename.py
==========================
1. Reads fars_selected_45.json + existing 5 AIG_CUR papers
2. Finds their FA codes in ~/fars-a-reviews
3. Renames all paper IDs from AIG_CUR_2026_FARS_<slug> → AIG_2026_FARS_<FACODE>
4. Extracts PDFs → corpus/ai/<paper_id>.pdf
5. Extracts human reviews → arg_outputs/fars_human_reviews/raw/<paper_id>_fars_human_reviews.json
6. Extracts paperreview.ai reviews → arg_outputs/paperreview_ai/raw/<paper_id>_paperreview_ai.json
   (replaces existing files for the 5 already present)
7. Updates corpus/corpus_metadata.json
8. Renames files in arg_outputs/cspaper/raw/, preprocessed.json, classified.json
9. Updates data/manual_review_log.csv

Usage:
    python scripts/data_collection/extract_fars_and_rename.py
"""

import csv
import json
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT  = (SCRIPT_DIR / "../..").resolve()
FARS_DIR   = Path.home() / "fars-a-reviews" / "data"

# Paths
METADATA_PATH     = REPO_ROOT / "corpus" / "corpus_metadata.json"
PDF_DIR           = REPO_ROOT / "corpus" / "ai"
HUMAN_REV_DIR     = REPO_ROOT / "arg_outputs" / "fars_human_reviews" / "raw"
PR_AI_DIR         = REPO_ROOT / "arg_outputs" / "paperreview_ai" / "raw"
CSPAPER_RAW_DIR   = REPO_ROOT / "arg_outputs" / "cspaper" / "raw"
REVIEW_LOG_PATH   = REPO_ROOT / "data" / "manual_review_log.csv"
SELECTED_45_PATH  = REPO_ROOT / "data" / "fars_selected_45.json"
OLD_PDF_DIR       = REPO_ROOT / "corpus" / "ai_generated" / "curated"

# ---------------------------------------------------------------------------
# Existing 5: old_id → gitlab_url mapping
# ---------------------------------------------------------------------------
EXISTING_5 = {
    "AIG_CUR_2026_FARS_chunked_budget_allocation":    "https://gitlab.com/fars-a/worldmodel-consensus-verification",
    "AIG_CUR_2026_FARS_citation_consistent_voting":   "https://gitlab.com/fars-a/latent-mode-voting-rag",
    "AIG_CUR_2026_FARS_draft_and_continue":           "https://gitlab.com/fars-a/aletheia-adaptive-branch-allocation",
    "AIG_CUR_2026_FARS_isolated_solve_then_judge":    "https://gitlab.com/fars-a/isolated-solve-then-judge-injection",
    "AIG_CUR_2026_FARS_token_balanced":               "https://gitlab.com/fars-a/token-balanced-cpt-brain-rot",
}

# ---------------------------------------------------------------------------
# Load FARS dataset index: gitlab_url → FA code, title → FA code
# ---------------------------------------------------------------------------

def build_fars_index(fars_dir: Path) -> tuple[dict, dict]:
    """Index by title only — gitlabUrl not present in FARS JSON files."""
    url_to_fa   = {}
    title_to_fa = {}
    for proj in sorted(fars_dir.glob("FA*")):
        fpath = proj / "human_review.json"
        if not fpath.exists():
            continue
        try:
            data  = json.loads(fpath.read_text(encoding="utf-8"))
            paper = data.get("paper", {})
            title = (paper.get("title", "") or "").strip().lower()
            if title:
                title_to_fa[title] = proj.name
        except Exception:
            continue
    return url_to_fa, title_to_fa


# ---------------------------------------------------------------------------
# Build rename map: old_id → new_id
# ---------------------------------------------------------------------------

def build_rename_map(existing_5: dict, selected_45: list,
                     url_to_fa: dict, title_to_fa: dict) -> dict:
    rename = {}

    # Existing 5 — match by title (gitlabUrl not in FARS JSON)
    existing_5_titles = {
        "AIG_CUR_2026_FARS_chunked_budget_allocation":
            "chunked budget allocation prevents non-monotonic regressions in world-model verification",
        "AIG_CUR_2026_FARS_citation_consistent_voting":
            "citation-consistent voting for permutation-robust retrieval-augmented generation",
        "AIG_CUR_2026_FARS_draft_and_continue":
            "draft-and-continue self-consistency: an empirical study of two-stage branch budgeting for llm reasoning",
        "AIG_CUR_2026_FARS_isolated_solve_then_judge":
            "isolated solve-then-judge: a simple defense against candidate-response prompt injection for multimodal llm judges",
        "AIG_CUR_2026_FARS_token_balanced":
            "token-balanced continual pretraining eliminates brain rot degradation",
    }
    for old_id, title in existing_5_titles.items():
        fa = title_to_fa.get(title)
        if fa:
            new_id = f"AIG_2026_FARS_{fa}"
            rename[old_id] = new_id
            print(f"  {old_id} → {new_id}")
        else:
            print(f"  [WARN] {old_id} — FA code not found by title")

    # 45 new papers (already have FA codes)
    for p in selected_45:
        fa     = p["id"]
        new_id = f"AIG_2026_FARS_{fa}"
        rename[fa] = new_id  # identity-ish but normalised

    return rename


# ---------------------------------------------------------------------------
# Extract files from FARS dataset
# ---------------------------------------------------------------------------

def extract_paper(fa_code: str, new_id: str,
                  fars_dir: Path,
                  pdf_dir: Path,
                  human_rev_dir: Path,
                  pr_ai_dir: Path) -> dict | None:
    proj = fars_dir / fa_code
    if not proj.exists():
        print(f"  [SKIP] {fa_code} — project dir not found")
        return None

    # PDF
    pdf_src = proj / f"{fa_code}.pdf"
    if pdf_src.exists():
        pdf_dst = pdf_dir / f"{new_id}.pdf"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_src, pdf_dst)
        pdf_rel = f"corpus/ai/{new_id}.pdf"
    else:
        pdf_rel = None
        print(f"  [WARN] {fa_code} — no paper.pdf")

    # Human review
    human_src = proj / "human_review.json"
    if human_src.exists():
        human_rev_dir.mkdir(parents=True, exist_ok=True)
        human_data = json.loads(human_src.read_text(encoding="utf-8"))
        # Inject paper_id into the file
        human_data["paper_id"] = new_id
        dst = human_rev_dir / f"{new_id}_fars_human_reviews.json"
        dst.write_text(json.dumps(human_data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(f"  [WARN] {fa_code} — no human_review.json")

    # paperreview.ai review
    pr_src = proj / "paperreview.json"
    if pr_src.exists():
        pr_ai_dir.mkdir(parents=True, exist_ok=True)
        pr_data = json.loads(pr_src.read_text(encoding="utf-8"))
        pr_data["paper_id"] = new_id
        # Keep their format — just update the paper_id
        dst = pr_ai_dir / f"{new_id}_paperreview_ai.json"
        dst.write_text(json.dumps(pr_data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(f"  [WARN] {fa_code} — no paperreview.json")

    # Metadata from human_review.json
    if human_src.exists():
        paper = human_data.get("paper", {})
        return {
            "paper_id":        new_id,
            "authorship_type": "ai_generated_curated",
            "source":          "fars",
            "title":           paper.get("title", ""),
            "venue":           None,
            "year":            2026,
            "pdf":             pdf_rel,
            "github_url":      None,
            "review_url":      None,
            "fa_code":         fa_code,
        }
    return None


# ---------------------------------------------------------------------------
# Update cspaper files
# ---------------------------------------------------------------------------

def rename_in_cspaper(rename: dict, cspaper_raw_dir: Path):
    """Rename raw .md files in arg_outputs/cspaper/raw/"""
    if not cspaper_raw_dir.exists():
        return
    for old_id, new_id in rename.items():
        for f in cspaper_raw_dir.glob(f"{old_id}_*.md"):
            suffix = f.name[len(old_id):]
            new_name = f.parent / f"{new_id}{suffix}"
            f.rename(new_name)
            print(f"  renamed {f.name} → {new_name.name}")


def rename_in_json(path: Path, rename: dict):
    """Replace all old IDs with new IDs in a JSON file."""
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for old_id, new_id in rename.items():
        text = text.replace(old_id, new_id)
    path.write_text(text, encoding="utf-8")
    print(f"  updated {path}")


def rename_in_csv(path: Path, rename: dict):
    """Replace old IDs in the paper_id column of a CSV."""
    if not path.exists():
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) if rows else []
    for row in rows:
        if row.get("paper_id") in rename:
            row["paper_id"] = rename[row["paper_id"]]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  updated {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building FARS index...")
    url_to_fa, title_to_fa = build_fars_index(FARS_DIR)
    print(f"  {len(url_to_fa)} URLs, {len(title_to_fa)} titles indexed\n")

    # Load selected 45 and clean up any double-prefixed IDs from previous runs
    selected_45 = json.loads(SELECTED_45_PATH.read_text(encoding="utf-8"))
    for p in selected_45:
        while p["id"].startswith("AIG_2026_FARS_"):
            p["id"] = p["id"].replace("AIG_2026_FARS_", "", 1)
    # Save the cleaned version
    SELECTED_45_PATH.write_text(json.dumps(selected_45, indent=2, ensure_ascii=False), encoding="utf-8")

    # Build rename map
    print("Building rename map...")
    rename = build_rename_map(EXISTING_5, selected_45, url_to_fa, title_to_fa)
    print()

    # Load existing metadata
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    existing_ids = {p["paper_id"]: i for i, p in enumerate(metadata["papers"])}

    # Extract all papers
    print("Extracting papers...")
    new_entries  = []
    current_ids  = {p["paper_id"]: i for i, p in enumerate(metadata["papers"])}

    # Existing 5 — rename and replace in metadata
    for old_id, new_id in rename.items():
        if old_id not in EXISTING_5:
            continue
        fa_code = new_id.replace("AIG_2026_FARS_", "")
        entry = extract_paper(fa_code, new_id, FARS_DIR, PDF_DIR, HUMAN_REV_DIR, PR_AI_DIR)
        if not entry:
            continue
        if new_id in current_ids:
            # Already renamed in a previous run — update in-place
            metadata["papers"][current_ids[new_id]] = entry
            print(f"  ↻ {new_id} (updated)")
        elif old_id in current_ids:
            # First run — replace old entry
            metadata["papers"][current_ids[old_id]] = entry
            print(f"  ✓ {old_id} → {new_id}")
        else:
            new_entries.append(entry)
            print(f"  ✓ {new_id} (new)")

    # 45 new papers
    for p in selected_45:
        fa_code = p["id"]
        # Strip prefix in case JSON was already updated by a previous run
        if fa_code.startswith("AIG_2026_FARS_"):
            fa_code = fa_code.replace("AIG_2026_FARS_", "")
        new_id  = f"AIG_2026_FARS_{fa_code}"
        entry = extract_paper(fa_code, new_id, FARS_DIR, PDF_DIR, HUMAN_REV_DIR, PR_AI_DIR)
        if not entry:
            continue
        if new_id in current_ids:
            # Already present — update in-place (re-extract files but don't duplicate)
            metadata["papers"][current_ids[new_id]] = entry
            print(f"  ↻ {new_id} (updated)")
        else:
            new_entries.append(entry)
            print(f"  ✓ {new_id} (new)")

    metadata["papers"].extend(new_entries)

    # Remove any remaining old AIG_CUR entries (only present on first run)
    old_ids = set(EXISTING_5.keys())
    metadata["papers"] = [
        p for p in metadata["papers"]
        if p["paper_id"] not in old_ids
    ]

    # Save metadata
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n✓  corpus_metadata.json updated ({len(metadata['papers'])} papers)")

    # Rename in cspaper raw files
    print("\nRenaming cspaper raw files...")
    rename_in_cspaper(rename, CSPAPER_RAW_DIR)

    # Rename in JSON files (NOT fars_selected_45.json — FA codes must not be renamed)
    print("\nUpdating JSON files...")
    for path in [
        REPO_ROOT / "arg_outputs" / "cspaper" / "parsed" / "preprocessed.json",
        REPO_ROOT / "arg_outputs" / "cspaper" / "parsed" / "classified.json",
    ]:
        rename_in_json(path, rename)

    # Rename in CSV
    print("\nUpdating CSV files...")
    rename_in_csv(REVIEW_LOG_PATH, rename)
    rename_in_csv(REPO_ROOT / "data" / "aspect_comparison.csv", rename)

    # Move old PDFs if they exist
    print("\nMoving old PDFs...")
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for old_id, new_id in rename.items():
        if old_id in EXISTING_5:
            old_pdf = OLD_PDF_DIR / f"{old_id}.pdf"
            if old_pdf.exists():
                new_pdf = PDF_DIR / f"{new_id}.pdf"
                if not new_pdf.exists():
                    shutil.copy2(old_pdf, new_pdf)
                    print(f"  moved {old_id}.pdf → {new_id}.pdf")

    print("\nDone.")
    print(f"  {len(rename)} papers renamed")
    print(f"  {len(new_entries)} new papers added")
    print(f"  PDFs → {PDF_DIR}")
    print(f"  Human reviews → {HUMAN_REV_DIR}")
    print(f"  ARG reviews → {PR_AI_DIR}")


if __name__ == "__main__":
    main()
