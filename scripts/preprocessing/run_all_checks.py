"""
run_all_checks.py

Runs automated pre-checks (LanguageTool, TextStat) on all PDFs in the corpus.
Outputs a flagged candidates CSV per paper in annotations/ground_truth/.

Usage:
    python scripts/preprocessing/run_all_checks.py --corpus_dir corpus/
    python scripts/preprocessing/run_all_checks.py --corpus_dir corpus/ai_generated/uncurated/
"""

import argparse
import csv
import datetime
import os
import sys

import fitz  # PyMuPDF
import language_tool_python
import textstat


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

AUTHORSHIP_MAP = {
    "curated":        "ai_generated_curated",
    "uncurated":      "ai_generated_uncurated",
    "human_ai_hybrid":"human_ai_hybrid",
    "accepted":       "human_accepted",
    "rejected":       "human_rejected",
}

SOURCE_MAP = {
    "curated":        "fars",
    "uncurated":      "ai_researcher",
    "human_ai_hybrid":"agents4science",
    "accepted":       "human",
    "rejected":       "human",
}

OUTPUT_DIR = "annotations/ground_truth"

FIELDNAMES = [
    "paper_id", "authorship_type", "source", "error_id", "error_type",
    "severity_label", "severity_score", "section", "page", "description",
    "automated_flag", "flag_source", "needs_review", "annotator", "annotation_date",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_text(pdf_path: str) -> list[tuple[int, str]]:
    """Return list of (page_number, page_text) tuples."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, start=1):
        pages.append((i, page.get_text()))
    return pages


def infer_metadata(pdf_path: str) -> tuple[str, str, str]:
    """Infer paper_id, authorship_type, and source from file path."""
    parts = pdf_path.replace("\\", "/").split("/")
    filename = os.path.splitext(parts[-1])[0]  # e.g. AIG_UNC_2025_yamada

    # Determine authorship type from parent directory name
    parent = parts[-2] if len(parts) >= 2 else "unknown"
    authorship = AUTHORSHIP_MAP.get(parent, "unknown")
    source = SOURCE_MAP.get(parent, "unknown")

    return filename, authorship, source


def run_languagetool(pages: list[tuple[int, str]]) -> list[dict]:
    """Run LanguageTool and return flagged issues."""
    tool = language_tool_python.LanguageTool("en-US")
    flags = []
    for page_num, text in pages:
        if not text.strip():
            continue
        matches = tool.check(text)
        for m in matches:
            # Skip purely stylistic/whitespace rules to reduce noise
            if m.ruleId in {"WHITESPACE_RULE", "COMMA_PARENTHESIS_WHITESPACE"}:
                continue
            flags.append({
                "page": page_num,
                "description": f"[LanguageTool:{m.ruleId}] {m.message} — context: '{m.context[:80]}'",
                "flag_source": "LanguageTool",
                "error_type": "LIN",
                "severity_label": "minor",
                "severity_score": 1,
            })
    tool.close()
    return flags


def run_textstat(pages: list[tuple[int, str]]) -> list[dict]:
    """Compute readability metrics; flag sections below threshold."""
    flags = []
    full_text = " ".join(t for _, t in pages)
    fk_grade = textstat.flesch_kincaid_grade(full_text)
    flesch = textstat.flesch_reading_ease(full_text)

    if flesch < 20:
        flags.append({
            "page": 0,
            "description": (
                f"[TextStat] Very low Flesch Reading Ease ({flesch:.1f}). "
                f"Flesch-Kincaid Grade: {fk_grade:.1f}. "
                "Document may be exceptionally dense — consider reviewing for clarity."
            ),
            "flag_source": "TextStat",
            "error_type": "LIN",
            "severity_label": "minor",
            "severity_score": 1,
        })
    return flags


def build_rows(
    paper_id: str,
    authorship_type: str,
    source: str,
    flags: list[dict],
    start_index: int = 1,
) -> list[dict]:
    """Convert raw flags into annotation CSV rows."""
    rows = []
    today = datetime.date.today().isoformat()
    for i, flag in enumerate(flags, start=start_index):
        error_id = f"{paper_id}_{i:03d}"
        rows.append({
            "paper_id":       paper_id,
            "authorship_type":authorship_type,
            "source":         source,
            "error_id":       error_id,
            "error_type":     flag["error_type"],
            "severity_label": flag["severity_label"],
            "severity_score": flag["severity_score"],
            "section":        "",          # To be filled manually
            "page":           flag.get("page", ""),
            "description":    flag["description"],
            "automated_flag": True,
            "flag_source":    flag["flag_source"],
            "needs_review":   True,        # All auto-flags need human validation
            "annotator":      "",
            "annotation_date":today,
        })
    return rows


def write_csv(output_path: str, rows: list[dict]) -> None:
    """Write rows to CSV, appending if file already exists."""
    file_exists = os.path.exists(output_path)
    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_pdf(pdf_path: str) -> None:
    print(f"  Processing: {pdf_path}")
    paper_id, authorship_type, source = infer_metadata(pdf_path)
    pages = extract_text(pdf_path)

    flags = []
    flags += run_languagetool(pages)
    flags += run_textstat(pages)

    if not flags:
        print(f"    No flags raised.")
        return

    output_path = os.path.join(OUTPUT_DIR, f"{paper_id}.csv")
    rows = build_rows(paper_id, authorship_type, source, flags)
    write_csv(output_path, rows)
    print(f"    {len(flags)} flag(s) written to {output_path}")


def collect_pdfs(corpus_dir: str) -> list[str]:
    pdfs = []
    for root, _, files in os.walk(corpus_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, f))
    return sorted(pdfs)


def main():
    parser = argparse.ArgumentParser(description="Run automated pre-checks on corpus PDFs.")
    parser.add_argument(
        "--corpus_dir", required=True,
        help="Path to corpus directory (or subdirectory) to process."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.corpus_dir):
        print(f"Error: '{args.corpus_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdfs = collect_pdfs(args.corpus_dir)

    if not pdfs:
        print(f"No PDFs found in '{args.corpus_dir}'.")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDF(s). Running checks...\n")
    for pdf_path in pdfs:
        process_pdf(pdf_path)

    print("\nDone. Review flagged CSVs in annotations/ground_truth/ before annotating.")


if __name__ == "__main__":
    main()
