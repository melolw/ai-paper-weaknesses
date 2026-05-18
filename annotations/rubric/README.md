# Annotation Rubric

This document defines the error taxonomy and severity scale used for manual annotation.
It should be piloted on the first 1–2 AI-generated manuscripts and refined before being
applied to the full corpus.

---

## Error Taxonomy

| Error Type Code | Category              | Description                                                                                  |
|-----------------|-----------------------|----------------------------------------------------------------------------------------------|
| `CIT`           | Citation Error        | Missing citation, citation to a non-existent or misattributed source, or incorrect metadata  |
| `CTM`           | Code-Text Mismatch    | Reported results, figures, or statistics do not match the accompanying code output           |
| `MATH`          | Mathematical Error    | Incorrect formula, faulty derivation, or inconsistent numerical result                       |
| `LOG`           | Logical Error         | Faulty reasoning, unsupported conclusion, or invalid inference from evidence                 |
| `LIN`           | Linguistic Error      | Grammar, spelling, or readability issue that impairs comprehension                           |
| `HALL_I`        | Intrinsic Hallucination | Claim directly contradicts empirical data present in the paper                             |
| `HALL_E`        | Extrinsic Hallucination | Unverifiable claim not supported or contradicted by the paper's source material            |
| `CON`           | Consistency Bug       | The paper contradicts its own previously stated hypothesis, method, or result               |
| `REP`           | Reproducibility Issue | Missing detail (hyperparameter, dataset split, seed, etc.) that prevents reproduction       |

> **Note:** This taxonomy is a starting point derived from the exposé. Expand or merge
> categories during the piloting phase as needed. Document any changes in `changelog.md`.

---

## Severity Scale

| Score | Label      | Definition                                                                 |
|-------|------------|----------------------------------------------------------------------------|
| 1     | `minor`    | Does not affect scientific validity; cosmetic or stylistic issue           |
| 2     | `moderate` | Weakens a supporting claim but does not undermine the core contribution    |
| 3     | `major`    | Undermines a core contribution or central experimental result              |
| 4     | `fatal`    | Renders the paper irreproducible or scientifically invalid                 |

---

## Annotation Guidelines

- **Be concrete and verifiable.** Every logged error must point to a specific location
  in the paper (section, page, figure, equation number).
- **One row per error instance.** If the same error type recurs in multiple places,
  log each occurrence separately.
- **Err toward logging.** If uncertain whether something is an error, log it with a
  note and flag it for review (`needs_review = True`).
- **Do not rely solely on automated flags.** Automated tools (LanguageTool, SciCoQa)
  serve as a first pass only. Manual reading is required to catch logical and
  consistency errors.
- **Severity is about scientific impact**, not how obvious the error is. A subtle
  code-text mismatch that invalidates a key result is `fatal`, not `minor`.

---

## Inter-Annotator Agreement

For papers annotated by more than one annotator, compute Cohen's Kappa on the
severity scores. Target κ ≥ 0.6 before proceeding to full-corpus annotation.
See `scripts/evaluation/compute_iaa.py`.
