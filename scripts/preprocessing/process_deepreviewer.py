"""
process_deepreviewer.py
========================
Parses DeepReviewer-v2 final_report.md files and writes preprocessed JSON
to parsed/preprocessed.json.

Raw layout (flat, one folder per paper):
    raw/<paper_id>/final_report.md

Top-level sections are bounded by exactly '## ' headers (Summary, Strengths,
Weaknesses, Key Issues, Actionable Suggestions, ...). Weaknesses and
Actionable Suggestions themselves render in one of three formats depending
on the paper/run:
    1) '### ' sub-headers, one per item, each followed by a paragraph
    2) plain dash-bulleted lines, no blank lines between them
    3) bold-titled paragraphs, separated by blank lines, no real headers
extract_items() detects which format a given section body uses (checking
in that priority order) before splitting it into points.

IMPORTANT: the section splitter matches '##' but NOT '###' as a boundary —
matching any header level would treat the nested '### W1. ...' sub-headers
as new top-level sections, truncating Weaknesses to empty before any content
is captured. (This was the actual bug behind papers coming back with 0 points
despite having complete, well-formed reviews.)

Sections extracted: Weaknesses, Actionable Suggestions (critique + suggested
fixes; "Key Issues" is skipped since it mostly restates Weaknesses from a
risk-category angle).
Reviewer ID: "deepreviewer"

Output format:
    {
      "<paper_id>": {
        "deepreviewer": {
          "0": "First critique point.",
          ...
        }
      }
    }

Usage:
    python process_deepreviewer.py

    Reads from  ../../arg_outputs/deepreviewer/raw/
    Writes to   ../../arg_outputs/deepreviewer/parsed/preprocessed.json
"""

import json
import re
import sys
from pathlib import Path

REVIEWER_ID = "deepreviewer"

SCRIPT_DIR   = Path(__file__).parent
REVIEWER_DIR = (SCRIPT_DIR / "../../arg_outputs/deepreviewer").resolve()
RAW_DIR      = REVIEWER_DIR / "raw"
PARSED_DIR   = REVIEWER_DIR / "parsed"

# Exactly two '#' — deliberately excludes '###' so nested sub-headers inside
# a section (e.g. '### W1. ...') don't get mistaken for new top-level sections.
SECTION_HEADER_RE = re.compile(r"^##(?!#)\s+(.+?)\s*$", re.MULTILINE)
SUBHEADER_RE      = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
NUMBERED_RE       = re.compile(r"^(\d+)\.\s+(.+)$")
DASH_LINE_RE      = re.compile(r"^\s*[-*•]\s+(.+)$", re.MULTILINE)

EXTRACT_SECTIONS = ["Weaknesses", "Actionable Suggestions"]


def split_markdown_sections(text: str) -> dict:
    """Split on '##' (exactly) headers into {section_title: body}."""
    matches = list(SECTION_HEADER_RE.finditer(text))
    sections = {}
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.setdefault(title, text[start:end].strip())
    return sections


def extract_items(body: str) -> list:
    """
    Detects which of three formats this section body uses and extracts
    accordingly, checked in priority order:
      1) '### ' sub-headers (2+)   -> header text + its paragraph = one point
      2) numbered lines (2+)       -> each numbered item = one point
      3) dash-bulleted lines (2+)  -> each line = one point
      4) fallback: blank-line-separated paragraphs = one point each
    """
    subheader_matches = list(SUBHEADER_RE.finditer(body))
    if len(subheader_matches) >= 2:
        points = []
        for i, m in enumerate(subheader_matches):
            title = m.group(1).strip()
            start = m.end()
            end = subheader_matches[i + 1].start() if i + 1 < len(subheader_matches) else len(body)
            para = " ".join(body[start:end].split())
            points.append(f"{title} {para}".strip() if para else title)
        return points

    numbered_count = sum(1 for line in body.splitlines() if NUMBERED_RE.match(line.strip()))
    if numbered_count >= 2:
        points, current = [], []

        def flush():
            if current:
                points.append(" ".join(current))
            current.clear()

        for raw in body.splitlines():
            line = raw.strip()
            m = NUMBERED_RE.match(line)
            if m:
                flush()
                current.append(m.group(2).strip())
                continue
            if line and current:
                current.append(line)
        flush()
        return [p for p in points if p]

    dash_lines = DASH_LINE_RE.findall(body)
    if len(dash_lines) >= 2:
        return [d.strip() for d in dash_lines if d.strip()]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    return [" ".join(p.split()) for p in paragraphs]


def main():
    if not RAW_DIR.exists():
        print(f"Error: {RAW_DIR} does not exist.")
        sys.exit(1)

    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    paper_dirs = sorted(d for d in RAW_DIR.iterdir() if d.is_dir())
    if not paper_dirs:
        print(f"No paper folders found in {RAW_DIR}")
        sys.exit(0)

    output = {}

    for paper_dir in paper_dirs:
        paper_id = paper_dir.name
        md_path = paper_dir / "final_report.md"
        if not md_path.exists():
            print(f"  [SKIP] {paper_id} — no final_report.md")
            continue

        text = md_path.read_text(encoding="utf-8")
        sections = split_markdown_sections(text)

        points = []
        for section_title in EXTRACT_SECTIONS:
            body = sections.get(section_title, "")
            if body:
                points.extend(extract_items(body))

        output[paper_id] = {REVIEWER_ID: {str(i): pt for i, pt in enumerate(points)}}

        print(f"  {paper_id}  ({len(points)} points)")
        for i, pt in enumerate(points):
            preview = pt[:95] + ("…" if len(pt) > 95 else "")
            print(f"    [{i:02d}] {preview}")
        print()

    out_path = PARSED_DIR / "preprocessed.json"
    out_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✓  Written → {out_path}")


if __name__ == "__main__":
    main()