"""
process_cspaper_reviews.py
==========================
Parses cspaper-format Markdown review files and writes preprocessed JSON
to parsed/preprocessed.json in the same reviewer folder.

Filename convention:
    <PAPER_ID>_cspaper.md
    e.g. HUM_REJ_2024_LU_proactive_agent_cspaper.md
         → paper_id = HUM_REJ_2024_LU_proactive_agent

Section strategies
------------------
"Summary Of Weaknesses" and "Limitations And Societal Impact":
    Numbered items (1), 2)…) are topic headers — skipped.
    Dash bullets (- …) are the actual critique points — extracted.

"Potentially Missing Related Work":
    Numbered items are the critique points — extracted as-is.

"Comments Suggestions And Typos":
    Numbered items are critique points; their indented sub-bullets are
    merged into the parent. Typo bullets (- …) after intro labels are
    also extracted. "What could change my score:" block is skipped.

Output format:
    {
      "<paper_id>": {
        "cspaper": {
          "0": "First critique point.",
          "1": "Second critique point.",
          ...
        }
      }
    }

Usage:
    python process_cspaper_reviews.py

    Reads from  ../../arg_outputs/cspaper/raw/
    Writes to   ../../arg_outputs/cspaper/parsed/preprocessed.json
"""

import json
import re
import sys
from pathlib import Path

REVIEWER_ID = "cspaper"

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------

# Top-level numbered item: "1) …", "2. …" at column 0
NUMBERED_RE  = re.compile(r"^\d+[\.\)]\s+(.+)$")
# Top-level dash bullet at column 0
DASH_RE      = re.compile(r"^[-*•]\s+(.+)$")
# Indented sub-item (2+ spaces or tab, then optional bullet)
SUB_RE       = re.compile(r"^[ \t]{2,}[-*•]?\s*(.+)$")
# Label lines: short line ending in ":" with no sentence content
LABEL_RE     = re.compile(r"^[^:]{1,60}:\s*$")
# Block to cut at in Comments section
SCORE_CUT_RE = re.compile(r"^What could change my score", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Per-section extractors
# ---------------------------------------------------------------------------

def extract_dash_bullets(body: str) -> list[str]:
    """
    Extract only top-level dash bullets, ignoring numbered headers.
    Used for: Summary Of Weaknesses, Limitations And Societal Impact.
    Each bullet is one point; continuation lines are merged in.
    """
    points: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            points.append(" ".join(current))
        current.clear()

    for raw in body.splitlines():
        line = raw.rstrip()

        if SCORE_CUT_RE.match(line):
            break

        # Skip numbered header lines
        if NUMBERED_RE.match(line):
            flush()
            continue

        m = DASH_RE.match(line)
        if m:
            flush()
            current.append(m.group(1).strip())
            continue

        sub = SUB_RE.match(line)
        if sub and current:
            current.append(sub.group(1).strip())
            continue

        # Empty line or label — don't flush, just skip
        # (sub-bullets can be separated by blank lines in some reviews)

    flush()
    return [p for p in points if p]


def extract_numbered_items(body: str) -> list[str]:
    """
    Extract numbered items as critique points, merging sub-bullets into parent.
    Used for: Potentially Missing Related Work.
    """
    points: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            points.append(" ".join(current))
        current.clear()

    for raw in body.splitlines():
        line = raw.rstrip()

        m = NUMBERED_RE.match(line)
        if m:
            flush()
            current.append(m.group(1).strip())
            continue

        sub = SUB_RE.match(line)
        if sub and current:
            current.append(sub.group(1).strip())
            continue

        # Dash bullet at column 0 with no open numbered item → standalone
        d = DASH_RE.match(line)
        if d and not current:
            points.append(d.group(1).strip())
            continue

        # Continuation for an open item
        if current and line.strip() and not LABEL_RE.match(line):
            current.append(line.strip())

    flush()
    return [p for p in points if p]


def extract_comments(body: str) -> list[str]:
    """
    Extract critique points from Comments Suggestions And Typos.
    - Numbered items (1), 2)…) are critique points; sub-bullets merged in.
    - Dash bullets after an intro label are also critique points.
    - Everything from "What could change my score:" onward is dropped.
    """
    points: list[str] = []
    current: list[str] = []
    in_skip_block = False

    def flush():
        if current:
            points.append(" ".join(current))
        current.clear()

    for raw in body.splitlines():
        line = raw.rstrip()

        # Stop at score block
        if SCORE_CUT_RE.match(line):
            break

        m_num = NUMBERED_RE.match(line)
        if m_num:
            flush()
            current.append(m_num.group(1).strip())
            continue

        m_dash = DASH_RE.match(line)
        if m_dash:
            if current:
                # Sub-bullet elaborating the open numbered item — merge in
                current.append(m_dash.group(1).strip())
            else:
                # Standalone typo/minor bullet
                points.append(m_dash.group(1).strip())
            continue

        sub = SUB_RE.match(line)
        if sub and current:
            current.append(sub.group(1).strip())
            continue

        # Label line (e.g. "Actionable suggestions:", "Typos and minor issues:")
        if LABEL_RE.match(line):
            flush()   # close any open item before the label
            continue

        # Continuation text for open item
        if current and line.strip():
            current.append(line.strip())

    flush()
    return [p for p in points if p]


# ---------------------------------------------------------------------------
# Section dispatcher
# ---------------------------------------------------------------------------

SECTION_EXTRACTORS = {
    "summary of weaknesses":            extract_dash_bullets,
    "potentially missing related work":  extract_numbered_items,
    "comments suggestions and typos":    extract_comments,
    "limitations and societal impact":   extract_dash_bullets,
}


def parse_cspaper_md(md_text: str) -> list[str]:
    section_re = re.compile(r"^#{2,3}\s+(.+)$", re.MULTILINE)
    parts = section_re.split(md_text)
    # parts = [preamble, heading1, body1, heading2, body2, …]

    all_points: list[str] = []

    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].strip().lower()
        body    = parts[i + 1].strip()

        extractor = SECTION_EXTRACTORS.get(heading)
        if extractor:
            all_points.extend(extractor(body))

    return all_points


# ---------------------------------------------------------------------------
# Filename → paper_id
# ---------------------------------------------------------------------------

def paper_id_from_filename(path: Path) -> str:
    stem = path.stem
    suffix = f"_{REVIEWER_ID}"
    return stem[: -len(suffix)] if stem.endswith(suffix) else stem


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(reviewer_folder: Path):
    raw_dir    = reviewer_folder / "raw"
    parsed_dir = reviewer_folder / "parsed"

    if not raw_dir.exists():
        print(f"Error: {raw_dir} does not exist.")
        sys.exit(1)

    parsed_dir.mkdir(exist_ok=True)

    md_files = sorted(raw_dir.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {raw_dir}")
        sys.exit(0)

    output: dict = {}

    for fpath in md_files:
        paper_id = paper_id_from_filename(fpath)
        points   = parse_cspaper_md(fpath.read_text(encoding="utf-8"))
        indexed  = {str(i): pt for i, pt in enumerate(points)}
        output[paper_id] = {REVIEWER_ID: indexed}

        print(f"  {fpath.name}  →  {paper_id}  ({len(points)} points)")
        for i, pt in enumerate(points):
            preview = pt[:95] + ("…" if len(pt) > 95 else "")
            print(f"    [{i:02d}] {preview}")
        print()

    out_path = parsed_dir / "preprocessed.json"
    out_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✓  Written → {out_path}")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    reviewer_folder = script_dir / "../../arg_outputs/cspaper"
    main(reviewer_folder.resolve())