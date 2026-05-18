# Thesis Pipeline: Evaluating Automatic Reviewers on AI-Generated Manuscripts

**Author:** Mélissa Loew — TU Darmstadt, UKP Lab  
**Supervisor:** Prof. Dr. Iryna Gurevych  
**Thesis:** *Evaluating Automatic Reviewers on Diverse AI-Generated Manuscripts*

---

## Overview

This repository supports the full evaluation pipeline for the thesis. It contains:
- A multi-category corpus of research papers (AI-generated, human-AI hybrid, human-authored)
- Manual annotation infrastructure for ground-truth error labeling
- Scripts for automated pre-checks and ARG deployment
- Evaluation scripts for computing Recall and Precision per ARG

---

## Repository Structure

```
thesis-pipeline/
│
├── corpus/                         # All collected research papers (PDFs)
│   ├── ai_generated/
│   │   ├── curated/                # FARS dataset papers (human-approved before release)
│   │   └── uncurated/              # Raw AI-Researcher outputs (locally generated)
│   ├── human_ai_hybrid/            # Agents for Science conference papers
│   └── human/
│       ├── accepted/               # Accepted human-authored papers
│       └── rejected/               # Rejected human-authored papers
│
├── annotations/                    # Ground truth and rubric
│   ├── ground_truth/               # Per-paper annotation CSVs
│   └── rubric/                     # Error taxonomy and severity scale definitions
│
├── arg_outputs/                    # ARG-generated reviews
│   ├── deepreviewer/
│   │   ├── raw/                    # Raw text output from DeepReviewer
│   │   └── parsed/                 # Standardized JSON for evaluation
│   ├── reviewagents/
│   │   ├── raw/
│   │   └── parsed/
│   └── paperaudit_review/
│       ├── raw/
│       └── parsed/
│
├── scripts/
│   ├── preprocessing/              # LanguageTool, TextStat, SciCoQa runners
│   ├── arg_runners/                # Scripts to feed papers into each ARG
│   └── evaluation/                 # Recall, Precision, and analysis scripts
│
├── results/
│   ├── tables/                     # CSV/Excel result tables
│   └── plots/                      # Generated figures
│
└── docs/                           # Additional documentation and notes
```

---

## Paper Naming Convention

All PDFs should follow this naming scheme to ensure consistent cross-referencing:

```
{AUTHORSHIP_CODE}_{SOURCE_CODE}_{YEAR}_{FIRST_AUTHOR_LASTNAME}.pdf
```

| Authorship Code | Meaning                          |
|-----------------|----------------------------------|
| `AIG_CUR`       | AI-generated, curated (FARS)     |
| `AIG_UNC`       | AI-generated, uncurated (local)  |
| `HAH`           | Human-AI hybrid (Agents4Science) |
| `HUM_ACC`       | Human-authored, accepted         |
| `HUM_REJ`       | Human-authored, rejected         |

**Example:** `AIG_CUR_2025_yamada.pdf`

---

## Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Run automated pre-checks on all papers
python scripts/preprocessing/run_all_checks.py --corpus_dir corpus/

# Run a specific ARG on a paper category
python scripts/arg_runners/run_deepreviewer.py --input_dir corpus/ai_generated/uncurated/

# Evaluate ARG outputs against ground truth
python scripts/evaluation/compute_recall_precision.py \
    --ground_truth annotations/ground_truth/ \
    --arg_outputs arg_outputs/deepreviewer/parsed/ \
    --arg_name deepreviewer
```

---

## Annotation Workflow

1. Run automated pre-checks (`scripts/preprocessing/`) — outputs flag candidates
2. Open the relevant paper's annotation CSV in `annotations/ground_truth/`
3. Validate flagged errors and add manually identified ones using the rubric in `annotations/rubric/`
4. Confirm severity score for each logged error

See [`annotations/rubric/README.md`](annotations/rubric/README.md) for the full taxonomy.

---

## Dependencies

See `requirements.txt`. Key packages:
- `language-tool-python` — syntactic error detection
- `textstat` — readability and word-length metrics
- `pandas`, `scikit-learn` — data handling and evaluation metrics
- `PyMuPDF` (`fitz`) — PDF text extraction
