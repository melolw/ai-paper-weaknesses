"""
process_paperaudit_reviews.py
==============================
Parses PaperAudit AuditAgent review_output JSON files and writes
preprocessed JSON to parsed/preprocessed.json.

PaperAudit raw layout (per paper, nested — mirrors the staged review tree):
    raw/<paper_id>/reviews/paper_audit/<model>/paper_origin/review_output_<tag>.json

The file's "final_review" field (== "reviews" field) is AuditAgent's refined,
final review text. Its system prompt fixes the section order exactly:
    1) Summary
    2) Strengths
    3) Weaknesses
    4) Suggestions for Improvement
    5) Score

Sections extracted: Weaknesses, Suggestions for Improvement.
Reviewer ID: "paperaudit"

Known model-output quirks this parser works around (all confirmed against
real generations, not hypothetical):

  1) Section headers are sometimes glued directly onto the end of the
     previous sentence with no whitespace ("...EM metrics.2) Strengths"),
     and sometimes rendered as real markdown headers ("### Strengths")
     instead of the "N) Title" style the prompt asked for. HEADER_RE
     matches both, non-anchored to line start.

  2) Top-level bullets are sometimes glued onto the end of the previous
     bullet's last sentence with no newline between them
     (e.g. "...domains.- **Limited Scope of Experimental Validation**"),
     and the bullet marker itself varies between '-', '*', and '•'.
     BULLET_START_RE finds bullet-start positions anywhere in the text
     (not anchored to line start) and splits on those directly.

  3) A side effect of (2): a sub-point that itself opens with inline bold
     text (e.g. "- **Table 2(a)** shows...") looks identical to a real
     top-level bullet once newline/indentation context is gone, so it gets
     wrongly split off as its own item — leaving the preceding chunk as a
     bare "**Title**" with no body. A real top-level bullet always has
     explanatory prose after its title, so any chunk that's *only* a bare
     title is merged forward into the next chunk instead of kept as its
     own point.

Sanity check: AuditAgent's own prompt requires the number of Suggestions to
match the number of Weaknesses 1:1. If a paper's counts don't match after
running this, it's worth a manual look — either the model deviated from its
own instructions for that paper, or there's a formatting quirk this parser
still doesn't handle.

Output format:
    {
      "<paper_id>": {
        "paperaudit": {
          "0": "First critique point.",
          ...
        }
      }
    }

Usage:
    python process_paperaudit_reviews.py

    Reads from  ../../arg_outputs/paperaudit_review/raw/
    Writes to   ../../arg_outputs/paperaudit_review/parsed/preprocessed.json
"""

import json
import re
import sys
from pathlib import Path

REVIEWER_ID = "paperaudit"

SCRIPT_DIR   = Path(__file__).parent
REVIEWER_DIR = (SCRIPT_DIR / "../../arg_outputs/paperaudit_review").resolve()
RAW_DIR      = REVIEWER_DIR / "raw"
PARSED_DIR   = REVIEWER_DIR / "parsed"

SECTION_TITLES   = ["Summary", "Strengths", "Weaknesses", "Suggestions for Improvement", "Score"]
EXTRACT_SECTIONS = ["Weaknesses", "Suggestions for Improvement"]

# Matches either "N) Title" (numbered, possibly glued to prior text) or
# "### Title" / "## Title" (markdown-style headers).
HEADER_RE = re.compile(
    r"(?:\d+\)\s*|#{1,4}\s*)(" + "|".join(re.escape(t) for t in SECTION_TITLES) + r")\b"
)

# Matches a bullet-start (any of -, *, • followed by a bold-title open),
# anywhere in the text — not anchored to line start, since the model
# doesn't reliably insert a newline before a new bullet.
BULLET_START_RE = re.compile(r"[-*•]\s*\*\*")

# A chunk that's *only* a bold title with nothing else — never a real
# point, always a sub-bullet's inline bold wrongly split off (see quirk 3).
BARE_TITLE_RE = re.compile(r"^\*\*[^*]+\*\*$")


def split_sections(text: str) -> dict:
    """Split AuditAgent's final_review text into {section_title: body}."""
    matches = list(HEADER_RE.finditer(text))
    sections = {}
    for i, m in enumerate(matches):
        title = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def extract_dash_bullets(body: str) -> list:
    """
    Split on bullet-start positions found anywhere in the text (handles the
    glued-bullet quirk), strip each chunk's own leading bullet marker, fold
    any newline-anchored sub-bullet markers into plain text, then merge
    forward any bare "**Title**"-only chunk into the following one (handles
    the inline-bold-sub-bullet quirk).
    """
    starts = [m.start() for m in BULLET_START_RE.finditer(body)]
    if not starts:
        return []
    starts.append(len(body))

    raw_chunks = []
    for i in range(len(starts) - 1):
        chunk = body[starts[i]:starts[i + 1]]
        chunk = re.sub(r"^[-*•]\s*", "", chunk)        # this bullet's own marker
        chunk = re.sub(r"\n\s*[-*•]\s+", " ", chunk)   # newline-anchored sub-bullets -> space
        chunk = " ".join(chunk.split())
        if chunk:
            raw_chunks.append(chunk)

    points, pending = [], None
    for chunk in raw_chunks:
        if pending is not None:
            chunk = pending + " " + chunk
            pending = None
        if BARE_TITLE_RE.match(chunk):
            pending = chunk
            continue
        points.append(chunk)
    if pending is not None:
        points.append(pending)

    return points


def find_review_files(raw_dir: Path) -> list:
    return sorted(raw_dir.glob("**/review_output_*.json"))


def paper_id_from_path(fpath: Path, raw_dir: Path) -> str:
    rel = fpath.relative_to(raw_dir)
    return rel.parts[0]


def main():
    if not RAW_DIR.exists():
        print(f"Error: {RAW_DIR} does not exist.")
        sys.exit(1)

    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    review_files = find_review_files(RAW_DIR)
    if not review_files:
        print(f"No review_output_*.json files found under {RAW_DIR}")
        sys.exit(0)

    output = {}
    mismatches = []

    for fpath in review_files:
        paper_id = paper_id_from_path(fpath, RAW_DIR)

        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON error in {fpath}: {e}")
            continue

        final_review = data.get("final_review") or data.get("reviews") or ""
        if not final_review.strip():
            print(f"  [SKIP] {paper_id} — empty final_review")
            continue

        sections = split_sections(final_review)

        weaknesses  = extract_dash_bullets(sections.get("Weaknesses", ""))
        suggestions = extract_dash_bullets(sections.get("Suggestions for Improvement", ""))
        points = weaknesses + suggestions

        if len(weaknesses) != len(suggestions):
            mismatches.append((paper_id, len(weaknesses), len(suggestions)))

        if paper_id in output:
            print(f"  [WARN] duplicate paper_id {paper_id!r} — overwriting with {fpath}")

        output[paper_id] = {REVIEWER_ID: {str(i): pt for i, pt in enumerate(points)}}

        print(f"  {paper_id}  ({len(weaknesses)} weaknesses + {len(suggestions)} suggestions = {len(points)} points)")
        for i, pt in enumerate(points):
            preview = pt[:95] + ("…" if len(pt) > 95 else "")
            print(f"    [{i:02d}] {preview}")
        print()

    out_path = PARSED_DIR / "preprocessed.json"
    out_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✓  Written → {out_path}")

    if mismatches:
        print(f"\n[SANITY CHECK] {len(mismatches)} paper(s) have weaknesses != suggestions (worth a manual look):")
        for paper_id, w, s in mismatches:
            print(f"  {paper_id}: {w} weaknesses vs {s} suggestions")
    else:
        print("\n[SANITY CHECK] All papers: weaknesses == suggestions. ✓")


if __name__ == "__main__":
    main()