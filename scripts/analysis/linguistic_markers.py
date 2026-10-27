"""
Linguistic markers for paper-weakness analysis.

Computes the set of "one-liner" linguistic markers discussed in the related-work
section (readability, sentence length, vocabulary diversity, vocabulary complexity)
for a piece of text. Designed to be called once per full document, and again per
individual section, so that document-level aspects (e.g. presentation) and
section-level aspects (e.g. related work completeness) can use the same function.

Requires:
    pip install textstat

Sources for each metric (for citing in the methodology section):
    - Flesch Reading Ease (FRE):      Flesch (1948); as used in Vincent-Lamarre & Lariviere (2021)
    - New Dale-Chall (NDC):           Chall & Dale (1995); as used in Vincent-Lamarre & Lariviere (2021)
    - Flesch-Kincaid Grade (FKG):     Kincaid et al. (1975); as used in Jung et al. (2025/2026)
    - Gunning Fog Index:              Gunning (1952); as used in Jung et al. (2025/2026)
    - Type-Token Ratio (TTR):         Vincent-Lamarre & Lariviere (2021); Jung et al. call the
                                       same computation "vocabulary diversity"
    - Average sentence length:        Jung et al. (2025/2026)
    - Vocabulary complexity proxy:    Dale-Chall "difficult words" list (textstat), and
                                       polysyllable count (Gunning Fog's underlying signal)
"""

import re
import textstat


def clean_text(text: str) -> str:
    """
    Light cleanup before computing linguistic markers.

    Vincent-Lamarre & Lariviere (2021) excluded methods/results sections entirely
    because formulas, equations, and variables made the text "unsuitable for
    textual analysis." Since our section-level approach still needs to compute
    markers on sections that may contain some inline math or citation clutter,
    this strips the most common contaminants instead of dropping the section.

    Adjust/extend the regexes below once you see what your section-segmented
    corpus actually looks like -- this is a starting point, not a finished filter.
    """
    # Remove inline citation markers like (Smith et al., 2020) or [12]
    text = re.sub(r"\([A-Z][a-zA-Z.,&\s]*\d{4}\)", " ", text)
    text = re.sub(r"\[\d+(,\s*\d+)*\]", " ", text)
    # Remove LaTeX-style inline math ($...$) and display math ($$...$$)
    text = re.sub(r"\$\$?.*?\$\$?", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_markers(text: str, clean: bool = True) -> dict:
    """
    Compute all linguistic markers for a single piece of text
    (either a full paper or a single section).

    Returns a flat dict so results can be dropped straight into a
    pandas DataFrame row, one row per (paper_id, section_name) pair.
    """
    if clean:
        text = clean_text(text)

    n_tokens = textstat.lexicon_count(text, removepunct=True)
    n_sentences = textstat.sentence_count(text)

    # Type-Token Ratio / "vocabulary diversity" (Vincent-Lamarre & Lariviere 2021;
    # same computation as what Jung et al. 2025/2026 call "vocabulary diversity")
    words = re.findall(r"\b\w+\b", text.lower())
    n_types = len(set(words))
    ttr = n_types / n_tokens if n_tokens > 0 else float("nan")

    return {
        "n_tokens": n_tokens,
        "n_types": n_types,
        "ttr": ttr,

        # Sentence length (Jung et al. 2025/2026)
        "avg_sentence_length": n_tokens / n_sentences if n_sentences > 0 else float("nan"),

        # Readability -- report all three, since the related-work section shows
        # a single formula isn't a stable enough signal on its own
        "flesch_reading_ease": textstat.flesch_reading_ease(text),          # FRE
        "dale_chall_score": textstat.dale_chall_readability_score(text),    # NDC
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),        # FKG
        "gunning_fog": textstat.gunning_fog(text),                         # Gunning Fog

        # Vocabulary complexity proxies
        "difficult_word_count": textstat.difficult_words(text),            # not on Dale-Chall's ~3000-word list
        "difficult_word_ratio": (
            textstat.difficult_words(text) / n_tokens if n_tokens > 0 else float("nan")
        ),
        "polysyllable_count": textstat.polysyllabcount(text),               # words with 3+ syllables
    }


def compute_markers_by_section(sections: dict, clean: bool = True) -> dict:
    """
    Same as compute_markers(), but for a dict of {section_name: section_text}.

    Returns {section_name: {metric_name: value, ...}, ...} plus a "full_document"
    entry computed over all sections concatenated, so document-level aspects
    (e.g. presentation) and section-level aspects (e.g. related work
    completeness) can both be read from the same output.

    Example
    -------
    sections = {
        "introduction": "...",
        "related_work": "...",
        "methods": "...",
        "results": "...",
    }
    results = compute_markers_by_section(sections)
    results["related_work"]["flesch_reading_ease"]
    results["full_document"]["ttr"]
    """
    results = {name: compute_markers(text, clean=clean) for name, text in sections.items()}
    full_text = " ".join(sections.values())
    results["full_document"] = compute_markers(full_text, clean=clean)
    return results


def section_presence_and_length(sections: dict) -> dict:
    """
    Section presence/length as its own signal, independent of linguistic content
    (e.g. "does this paper even have a Limitations section, and how long is it
    relative to the paper as a whole?").

    `sections` should map expected section names to their text, or to an empty
    string / None if that section is absent from the paper.
    """
    lengths = {
        name: textstat.lexicon_count(text, removepunct=True) if text else 0
        for name, text in sections.items()
    }
    total = sum(lengths.values())
    return {
        name: {
            "present": bool(text),
            "n_tokens": lengths[name],
            "proportion_of_document": (lengths[name] / total) if total > 0 else float("nan"),
        }
        for name, text in sections.items()
    }


if __name__ == "__main__":
    # Minimal smoke test
    example = (
        "Playing games has always been thought to be important to the development "
        "of well-balanced and creative children; however, what part, if any, they "
        "should play in the lives of adults has never been researched that deeply."
    )
    from pprint import pprint
    pprint(compute_markers(example))
