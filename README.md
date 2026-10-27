# Weaknesses in AI-generated and Human Papers

Code and data for the Bachelor's thesis *Weaknesses in AI-generated and Human Papers: A Comparative Analysis of Weaknesses Across Authorship Types*
(Mélissa Loew, Ubiquitous Knowledge Processing Lab, TU Darmstadt, 2026; reviewers: Prof. Dr. Iryna Gurevych, Serwar Basch).

The thesis compares the weaknesses that reviewers raise in four groups of papers and asks three research questions:

1. **RQ1** – How are weaknesses in AI-generated papers distributed across established weakness categories?
2. **RQ2** – How do these weaknesses differ from those in human-AI collaborative, accepted human, and rejected human papers?
3. **RQ3** – To what extent do automatic review generators (ARGs) find the weaknesses that human reviewers find in AI-generated papers?

Every critique point in a review is classified into the 16 coarse aspect categories of
[Lu et al. (2025)](https://github.com/UKPLab/emnlp2025-aspects-in-reviews).

## Corpus

| Origin (thesis) | File prefix | n | Source | Folder |
|---|---|---|---|---|
| `AIG` – AI-generated | `AIG_2026_FARS_` | 50 | FARS (Analemma) | `corpus/ai/` |
| `HA_COL` – human-AI collaborative | `HAH_2025_` | 48 | Agents4Science (accepted) | `corpus/human_ai_hybrid/` |
| `HUM_ACC` – human, accepted | `HUM_ACC_2024_` | 50 | NLPeerv2, ARR 2024 | `corpus/human/accepted/` |
| `HUM_REJ` – human, rejected | `HUM_REJ_2024_` | 50 | NLPeerv2, ARR 2024 | `corpus/human/rejected/` |

`corpus/corpus_metadata.json` lists every paper with its metadata.

## Repository structure

```
corpus/                   papers (PDF), see table above
arg_outputs/              reviews, one folder per review source
  fars_human_reviews/       human reviews of AIG papers (FARS release)
  openreview/               human reviews of HA_COL papers (Agents4Science, OpenReview)
  human_reviews/            human reviews of HUM_ACC / HUM_REJ papers (NLPeerv2)
  cspaper/                  CSPaper reviews of all four origins
  paperreview_ai/           paperreview.ai reviews of AIG papers
  deepreviewer/             DeepReviewer-v2 reviews of AIG papers
  paperaudit_review/        PaperAudit Review reviews of AIG papers
    raw/                      reviews as collected
    parsed/preprocessed.json  critique points extracted per paper and reviewer
    parsed/classified.json    critique points with their aspect categories
data/                     manual annotation and paper selection
  manual_review_log.csv     manual weakness annotation (Section 3.3.1)
  aspect_comparison.csv     manual vs. automatic categories
scripts/
  preprocessing/          extracting critique points from each review format
  classification/         aspect classification and its validation
  analysis/               statistics for RQ1-RQ3 and the linguistic markers
  figures/                thesis figures
results/
  tables/                 all result tables (CSV)
  figures/                all figures (PDF and PNG)
```

## Pipeline

Run all scripts from the repository root.

The CSPaper, DeepReviewer-v2 and PaperAudit reviews were produced with the respective tools (Section 3.2.2 of the thesis) and are stored in `arg_outputs/*/raw/`.

**1. Preprocessing** (`scripts/preprocessing/process_*.py`) – one parser per review source; writes `arg_outputs/<source>/parsed/preprocessed.json`.

**2. Classification** (`scripts/classification/`)

| Script | Purpose | Thesis |
|---|---|---|
| `run_rap.py` | classify critique points with GPT-4o (adapted few-shot prompt of Lu et al.); writes `classified.json` | 3.3.2, App. A.2 |
| `boot_match.py` | agreement between manual and automatic categorization (boot-match) | 3.3.3 |
| `compare_aspects.py` | per-review comparison of manual and automatic categories | 3.3.3 |

`run_rap.py` needs an OpenAI API key (`OPENAI_API_KEY`) and a local clone of the Lu et al. repository (`LU_ET_AL_REPO`).

**3. Analysis** (`scripts/analysis/`) – writes to `results/tables/`.

| Script | Output | Thesis |
|---|---|---|
| `extract_weakness_category_distributions.py` (`_cspaper`) | `weakness_category_distributions_per_review*.csv` | 4.1, 5.1 |
| `test_weakness_category_differences.py` (`_cspaper`) | `weakness_category_significance_tests*.csv` (omnibus tests) | 5.2, 5.3, App. C.1 |
| `pairwise_weakness_category_tests.py` (`_cspaper`) | `weakness_category_pairwise_tests*.csv` | 5.2, 5.3, App. C.2–C.3 |
| `compare_variability_human_vs_cspaper.py` | `variability_human_vs_cspaper.csv` | 3.2.3 |
| `run_linguistic_markers.py` (uses `linguistic_markers.py`) | `linguistic_markers_summary.csv` | 3.5 |
| `correlate_aig_ratings.py` | `aig_rating_correlations.csv` | 4.2, App. B.1 |
| `presentation_weakness_analysis.py` | `presentation_weakness_*.csv`, `presentation_ratio_correlations.csv` | 4.2 |
| `test_category_differences.py`, `pairwise_category_tests.py` | `category_significance_tests.csv`, `pairwise_category_tests.csv` (linguistic markers) | 5.4, App. C.4 |
| `arg_human_category_overlap.py` | `arg_human_category_overlap_*.csv` | 6.1–6.3 |
| `arg_overlap_baselines.py` | `arg_human_overlap_baselines.csv`, `arg_human_overlap_vs_chance.csv` | 6.1, App. D.1 |

**4. Figures** (`scripts/figures/`) – writes to `results/figures/`.

| Script | Figures |
|---|---|
| `generate_rq1_chart.py` | `rq1_profile`, `rq1_cooccurrence` (Figures 4.1, 4.2) and further RQ1 figures |
| `generate_chart.py` | `chart_4_human_reviews` (Figure 5.1) and additional distribution charts |

## Installation

```bash
pip install -r requirements.txt
```

## License

Code: MIT (see `LICENSE`). The papers and reviews in `corpus/` and `arg_outputs/` come from FARS, Agents4Science/OpenReview and NLPeerv2 and remain under the licenses of their original sources.
