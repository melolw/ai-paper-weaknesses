"""
run_deepreviewer.py

Feeds PDFs into DeepReviewer and saves raw outputs to arg_outputs/deepreviewer/raw/.
Then parses the raw output into a standardized JSON format in arg_outputs/deepreviewer/parsed/.

Usage:
    python scripts/arg_runners/run_deepreviewer.py --input_dir corpus/ai_generated/uncurated/
    python scripts/arg_runners/run_deepreviewer.py --input_dir corpus/ --all

Standardized parsed JSON format (one file per paper):
{
    "paper_id": "AIG_UNC_2025_yamada",
    "arg": "deepreviewer",
    "critiques": [
        {
            "critique_id": "AIG_UNC_2025_yamada_DR_001",
            "section": "Section 4",
            "description": "The reported accuracy contradicts Table 3.",
            "raw_text": "..."
        },
        ...
    ]
}

NOTE: This script provides the integration scaffold. Replace the placeholder
`call_deepreviewer_api()` function with the actual DeepReviewer API/CLI call
once access is confirmed. See: https://arxiv.org/abs/2503.08569
"""

import argparse
import json
import os
import sys

import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RAW_OUTPUT_DIR   = "arg_outputs/deepreviewer/raw"
PARSED_OUTPUT_DIR = "arg_outputs/deepreviewer/parsed"


# ---------------------------------------------------------------------------
# DeepReviewer integration (replace placeholder with real call)
# ---------------------------------------------------------------------------

def call_deepreviewer_api(paper_text: str, paper_id: str) -> str:
    """
    Call the DeepReviewer model and return raw review text.

    TODO: Replace this placeholder with the actual DeepReviewer API or CLI call.
    Reference implementation: https://arxiv.org/abs/2503.08569
    (Zhu et al., 2025 — DeepReview: Improving LLM-based Paper Review
    with Human-like Deep Thinking Process)

    Expected return: raw review string as produced by DeepReviewer.
    """
    raise NotImplementedError(
        "DeepReviewer integration not yet implemented. "
        "Replace this function body with the actual API/CLI call."
    )


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_raw_review(raw_text: str, paper_id: str) -> dict:
    """
    Parse raw DeepReviewer output into the standardized critique JSON format.

    This is a best-effort line-based parser. Adapt the parsing logic once
    you have seen real DeepReviewer output structure.
    """
    critiques = []
    current_critique = []
    critique_index = 1

    for line in raw_text.splitlines():
        stripped = line.strip()
        # Heuristic: new critique starts with a numbered point or "Weakness"/"Issue"
        if stripped and (
            stripped[0].isdigit() and stripped[1:3] in (". ", ") ")
            or stripped.lower().startswith(("weakness", "issue", "concern", "error", "problem"))
        ):
            if current_critique:
                text = " ".join(current_critique).strip()
                critiques.append({
                    "critique_id": f"{paper_id}_DR_{critique_index:03d}",
                    "section": "",      # To be filled during evaluation if determinable
                    "description": text,
                    "raw_text": text,
                })
                critique_index += 1
                current_critique = []
            current_critique.append(stripped)
        elif stripped and current_critique:
            current_critique.append(stripped)

    # Flush last critique
    if current_critique:
        text = " ".join(current_critique).strip()
        critiques.append({
            "critique_id": f"{paper_id}_DR_{critique_index:03d}",
            "section": "",
            "description": text,
            "raw_text": text,
        })

    return {
        "paper_id": paper_id,
        "arg": "deepreviewer",
        "critiques": critiques,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)


def infer_paper_id(pdf_path: str) -> str:
    return os.path.splitext(os.path.basename(pdf_path))[0]


def collect_pdfs(input_dir: str) -> list[str]:
    pdfs = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, f))
    return sorted(pdfs)


def process_pdf(pdf_path: str) -> None:
    paper_id = infer_paper_id(pdf_path)
    print(f"  Processing: {paper_id}")

    paper_text = extract_text(pdf_path)

    # --- Call ARG ---
    raw_review = call_deepreviewer_api(paper_text, paper_id)

    # --- Save raw output ---
    os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
    raw_path = os.path.join(RAW_OUTPUT_DIR, f"{paper_id}.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_review)
    print(f"    Raw output saved: {raw_path}")

    # --- Parse and save structured output ---
    os.makedirs(PARSED_OUTPUT_DIR, exist_ok=True)
    parsed = parse_raw_review(raw_review, paper_id)
    parsed_path = os.path.join(PARSED_OUTPUT_DIR, f"{paper_id}.json")
    with open(parsed_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    print(f"    Parsed output saved: {parsed_path} ({len(parsed['critiques'])} critique(s))")


def main():
    parser = argparse.ArgumentParser(description="Run DeepReviewer on corpus PDFs.")
    parser.add_argument("--input_dir", required=True, help="Directory of PDFs to process.")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: '{args.input_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    pdfs = collect_pdfs(args.input_dir)
    if not pdfs:
        print(f"No PDFs found in '{args.input_dir}'.")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDF(s). Running DeepReviewer...\n")
    for pdf_path in pdfs:
        try:
            process_pdf(pdf_path)
        except NotImplementedError as e:
            print(f"    SKIPPED — {e}")
        except Exception as e:
            print(f"    ERROR processing {pdf_path}: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
