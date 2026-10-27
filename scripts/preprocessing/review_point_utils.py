"""
Shared point extraction utilities for human review parsers.
"""

import re

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

# Patterns that indicate a line is a bibliography reference, not a critique point
_REF_RE = re.compile(
    r"^\s*(\[\d+\]|\d+\.)\s+[A-Z][a-z]+.*?(CoRR|arXiv|ACL|EMNLP|NAACL|ICLR|NeurIPS|ICML|ACM|IEEE)",
    re.IGNORECASE,
)
_COARXIV_RE  = re.compile(r"^\s*(CoRR|arXiv)\s+abs/", re.IGNORECASE)
_LONE_NUM_RE = re.compile(r"^\d+[\.\)]?\s*$")
_TOO_SHORT   = 15   # characters — shorter than this is noise


def is_noise(text: str) -> bool:
    """Return True if the text is a bibliography entry, stray number, or too short."""
    t = text.strip()
    if not t:
        return True
    if len(t) < _TOO_SHORT:
        return True
    if _REF_RE.match(t):
        return True
    if _COARXIV_RE.match(t):
        return True
    if _LONE_NUM_RE.match(t):
        return True
    return False


# ---------------------------------------------------------------------------
# Inline numbered list splitter
# Handles "1. Question A 2. Question B 3. Question C" on a single line
# ---------------------------------------------------------------------------

_INLINE_NUM_RE = re.compile(r"(?<!\[)\b(\d+)\.\s+(?=[A-Z])")


def split_inline_numbered(text: str) -> list[str] | None:
    """
    If text looks like an inline numbered list ("1. X 2. Y 3. Z"),
    split it and return the items. Otherwise return None.
    """
    matches = list(_INLINE_NUM_RE.finditer(text))
    if len(matches) < 2:
        return None
    parts = []
    for i, m in enumerate(matches):
        start = m.end()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        parts.append(text[start:end].strip())
    return [p for p in parts if p and not is_noise(p)]


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

_TOP_RE = re.compile(r"^\s*(\d+[\.\)]\s+|[-*•]\s+|[A-Z]\d+:\s+)(.*)$")
_SUB_RE = re.compile(r"^[ \t]{2,}[-*•]?\s*(.+)$")


def extract_points(text: str) -> list[str]:
    """
    Extract critique points from a plain text block.
    Handles numbered lists, bullet lists, labelled items (W1:, D1:),
    inline numbered lists, and plain prose.
    Filters out bibliography entries and noise.
    """
    if not text or not text.strip():
        return []

    # Try inline numbered list first (single-line "1. X 2. Y")
    stripped = text.strip()
    if "\n" not in stripped:
        inline = split_inline_numbered(stripped)
        if inline:
            return [p for p in inline if not is_noise(p)]

    lines = stripped.splitlines()

    is_list = sum(1 for l in lines if _TOP_RE.match(l)) >= 2

    points: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            merged = " ".join(p.strip() for p in current if p.strip())
            if merged and not is_noise(merged):
                points.append(merged)
        current.clear()

    if is_list:
        for raw in lines:
            m = _TOP_RE.match(raw)
            if m:
                flush()
                content = m.group(2).strip()
                if content:
                    current.append(content)
                continue
            sub = _SUB_RE.match(raw)
            if sub and current:
                current.append(sub.group(1).strip())
                continue
            if raw.strip() and current:
                current.append(raw.strip())
        flush()
    else:
        for sent in split_sentences(stripped):
            if not is_noise(sent):
                points.append(sent)

    return points


def split_sentences(text: str) -> list[str]:
    abbrev_re = re.compile(
        r"\b(?:Mr|Ms|Dr|Prof|vs|etc|e\.g|i\.e|Fig|Sec|Tab|Eq|al)\."
    )
    protected = abbrev_re.sub(lambda m: m.group().replace(".", "<!DOT!>"), text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\(\[])", protected)
    return [p.replace("<!DOT!>", ".").strip() for p in parts if p.strip()]