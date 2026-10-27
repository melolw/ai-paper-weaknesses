"""
run_rap.py
==========
Adapter script for the RAP (Review Aspect Prediction) pipeline from:

    Lu et al. (2025) "Identifying Aspects in Peer Reviews"
    EMNLP Findings. https://github.com/UKPLab/emnlp2025-aspects-in-reviews

This script uses their exact prompt, parameters, and output format from
notebook-azure.ipynb (few_coarse RAP section), with the only adaptation
being the use of openai.OpenAI instead of openai.AzureOpenAI.

Setup:
    1. Clone their repo somewhere on your machine:
           git clone https://github.com/UKPLab/emnlp2025-aspects-in-reviews.git

    2. Set API KEY and LU_ET_AL_REPO in your terminal using EXPORT.

    3. Run from your repo root:
           python scripts/preprocessing/run_rap.py

Reads  : arg_outputs/cspaper/parsed/preprocessed.json
Writes : arg_outputs/cspaper/parsed/classified.json
"""

import json
import os
import sys
import time
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths (relative to this script's location)
# ---------------------------------------------------------------------------
SCRIPT_DIR   = Path(__file__).parent

# !! SET THIS before running !!
# Name of the reviewer/ARG folder inside arg_outputs/ to process.
# Options so far:
#   "cspaper"        — cspaper Markdown reviews
#   "human_reviews"  — nlpeer human reviews (HUM_ACC / HUM_REJ)
#   "openreview"     — Agents4Science openreview (HAH), human only
#   "paperreview_ai"  — paperreview.ai ARG reviews
#   "fars_human_reviews" — FARS human reviews (AIG_CUR papers)
REVIEWER = sys.argv[1] if len(sys.argv) > 1 else "openreview"
REVIEWER_DIR = (SCRIPT_DIR / f"../../arg_outputs/{REVIEWER}").resolve()

INPUT_PATH   = REVIEWER_DIR / "parsed" / "preprocessed.json"
OUTPUT_PATH  = REVIEWER_DIR / "parsed" / "classified.json"

# ---------------------------------------------------------------------------
# Verify their repo exists (we don't import anything, but document the dep)
# ---------------------------------------------------------------------------

_repo_env     = os.environ.get("LU_ET_AL_REPO")
LU_ET_AL_REPO = Path(_repo_env).expanduser() if _repo_env else None

if not LU_ET_AL_REPO.exists():
    raise SystemExit(
        f"Lu et al. repo not found at {LU_ET_AL_REPO}\n"
        f"Clone it with:\n"
        f"  git clone https://github.com/UKPLab/emnlp2025-aspects-in-reviews.git"
    )

# ---------------------------------------------------------------------------
# Their exact prompt — few_coarse, from notebook-azure.ipynb, RAP section
# Copied verbatim; no modifications.
# ---------------------------------------------------------------------------
PROMPT_FEW_COARSE = (
    'Identify the aspect(s) that the given review sentence focuses on. '
    'Aspects: Ablation, Analysis, Comparison, Contribution, Data/Task, '
    'Definition/Description/Detail/Discussion/Explanation/Interpretation, '
    'Evaluation, Experiment, '
    'Intuition/Justification/Motivation/Validation, '
    'Methodology, Novelty, Presentation, Related Work, Result, Significance, Theory. '
    'If a review sentence does not express any of the listed aspects, mark "-". '
    'If the review sentence contains multiple aspects, select all applicable aspects. '
    'Format the output in a json dictionary: {"Aspects": [...]}. '
    'Here are some examples:\n\n'
    'INPUT: The evaluation shows that the proposed method can improve the intrigue and coherence of a generated story.\n'
    'OUTPUT: {"Aspects": ["Evaluation", "Methodology"]}\n\n'
    'INPUT: So if I have language A that receives a perplexity of 10 according to LM0, and another language B that receives a perplexity of 3 (and thus much higher average probability per token), and LM0 assigns its own language a perplexity of 2, then we\'ll get scores of (10-2)/2 = 4 for A and (3-2)/2 = 0.5 for B, making A look more similar.\n'
    'OUTPUT: {"Aspects": ["Evaluation"]}\n\n'
    'INPUT: On Abstractive Summarization BeamSearch is used and again outperform MLE and UT.\n'
    'OUTPUT: {"Aspects": ["Evaluation", "Result"]}\n\n'
    'INPUT: It is also strange that the multi-cluster approach, which discards inter-cluster (word and language) semantic information performs the best with respect to the extrinsic metrics.\n'
    'OUTPUT: {"Aspects": ["Evaluation", "Methodology", "Result"]}\n\n'
    'INPUT: The overall problem is framed as a judgment question, further enhancing the method\'s Uniqueness and Efficiency.\n'
    'OUTPUT: {"Aspects": ["Methodology"]}\n\n'
    'INPUT: One of the main novelties with respect to previous text-to-clip models is the use of co-attention schemes at the level of words and frames.\n'
    'OUTPUT: {"Aspects": ["Methodology", "Novelty"]}\n\n'
    'INPUT: The proposed method shows promising privacy-utility trade-off empirically.\n'
    'OUTPUT: {"Aspects": ["Methodology"]}\n\n'
    'INPUT: - Significance: The paper makes a substantial contribution to the field of molecular discovery.\n'
    'OUTPUT: {"Aspects": ["Significance", "Contribution"]}\n\n'
    'INPUT: However, authors do not compare their methods against any of the previous works.\n'
    'OUTPUT: {"Aspects": ["Comparison", "Related Work"]}\n\n'
    'INPUT: There are many related works on iterative retrieval in the open-domain QA that have not been mentioned and compared, such as:    [1] Guo, Xiaoxiao, et al. "Learning to query, reason, and answer questions on ambiguous texts."\n'
    'OUTPUT: {"Aspects": ["Related Work"]}\n\n'
    'INPUT: I agree with all of your points about what is lacking, but in my mind, the novelty was enough to still give a 7.\n'
    'OUTPUT: {"Aspects": ["Novelty"]}\n\n'
    'INPUT: Given the emergent of cutting-edge large language models and their decent in-context performance, the technique proposed in this paper seems to be redundant and outdated.\n'
    'OUTPUT: {"Aspects": ["Methodology", "Novelty"]}\n\n'
    'INPUT: Please bring the table closer to its reference.\n'
    'OUTPUT: {"Aspects": ["Related Work", "Presentation"]}\n\n'
    'INPUT: * (clarity) The "Return" metric is not defined or referenced in the results section.\n'
    'OUTPUT: {"Aspects": ["Evaluation", "Result", "Presentation"]}\n\n'
    'INPUT: p2 LTMS -> LSTM p3 For Self-attention -> Self-attention p5 following Vaswani -> follows Vaswani\n'
    'OUTPUT: {"Aspects": ["Presentation"]}\n\n'
    'INPUT: In fact, other example tasks should be selected to better highlight the advantages of the proposed method.\n'
    'OUTPUT: {"Aspects": ["Data/Task", "Methodology"]}\n\n'
    'INPUT: Why do the authors use the Quora dataset in particular?\n'
    'OUTPUT: {"Aspects": ["Data/Task"]}\n\n'
    'INPUT: Mostly empirical analysis based on OpenAI playground.\n'
    'OUTPUT: {"Aspects": ["Analysis"]}\n\n'
    'INPUT: Furthermore, the paper lacks visual or interpretable analyses that incorporate concrete natural language statements.\n'
    'OUTPUT: {"Aspects": ["Analysis", "Definition/Description/Detail/Discussion/Explanation/Interpretation"]}\n\n'
    'INPUT: The authors take time to implement and evaluate several prominent baselines.\n'
    'OUTPUT: {"Aspects": ["Comparison", "Evaluation", "Methodology"]}\n\n'
    'INPUT: - No actual comparisons to weight norm?\n'
    'OUTPUT: {"Aspects": ["Comparison"]}\n\n'
    'INPUT: It is not fair to discount this computational effort completely when comparing with the performance of other solvers that do not make LLM calls.\n'
    'OUTPUT: {"Aspects": ["Comparison"]}\n\n'
    'INPUT: I didn\'t see any significance measurements and it would be important to add them.\n'
    'OUTPUT: {"Aspects": ["Result"]}\n\n'
    'INPUT: - The proposed method is intuitive and easy to understand.\n'
    'OUTPUT: {"Aspects": ["Intuition/Justification/Motivation/Validation", "Methodology"]}\n\n'
    'INPUT: Despite good empirical efforts, the motivation of this paper seems somewhat unclear.\n'
    'OUTPUT: {"Aspects": ["Intuition/Justification/Motivation/Validation"]}\n\n'
    'INPUT: Since this is not addressed at all in the paper, it makes the results in general a bit difficult to interpret.\n'
    'OUTPUT: {"Aspects": ["Definition/Description/Detail/Discussion/Explanation/Interpretation", "Result"]}\n\n'
    'INPUT: Also, the meaning of vector v in weight calculation is not clearly discussed.\n'
    'OUTPUT: {"Aspects": ["Definition/Description/Detail/Discussion/Explanation/Interpretation"]}\n\n'
    'INPUT: In general, I find Experiments II to be much weaker than Experiment I.\n'
    'OUTPUT: {"Aspects": ["Comparison", "Experiment"]}\n\n'
    'INPUT: Testing for the true role of language will require many more experiments, which may be somewhat out of scope for this paper given the space constraints for a single paper.\n'
    'OUTPUT: {"Aspects": ["Experiment"]}\n\n'
    'INPUT: - I don\'t see why your theory does not generalize to a masked language modeling (MLM).\n'
    'OUTPUT: {"Aspects": ["Methodology", "Theory"]}\n\n'
    'INPUT: Firstly, in the last paragraph of Section 2, the authors claim that the role matrix R would be invertible.\n'
    'OUTPUT: {"Aspects": ["Theory"]}\n\n'
    'INPUT: + The ablation studies are quite comprehensive, and most of my questions about the methods was addressed.\n'
    'OUTPUT: {"Aspects": ["Methodology", "Ablation"]}\n\n'
    'INPUT: It would be better if a comprehensive ablation study was conducted, to understand which traditional features contribute the most.\n'
    'OUTPUT: {"Aspects": ["Methodology", "Ablation"]}\n\n'
    'INPUT: Such gaps make the main contribution questionable and make it as a pure empirical paper on its value.\n'
    'OUTPUT: {"Aspects": ["Contribution"]}\n\n'
    'INPUT: Considering the contributions of this paper, it is more suitable as a technical report than a paper to be published.\n'
    'OUTPUT: {"Aspects": ["Contribution"]}\n\n'
)

VALID_LABELS = {
    "Ablation", "Analysis", "Comparison", "Contribution", "Data/Task",
    "Definition/Description/Detail/Discussion/Explanation/Interpretation",
    "Evaluation", "Experiment",
    "Intuition/Justification/Motivation/Validation",
    "Methodology", "Novelty", "Presentation", "Related Work",
    "Result", "Significance", "Theory", "-",
}

# ---------------------------------------------------------------------------
# Their exact API params — from notebook-azure.ipynb, RAP inference cell
# Only change: OpenAI() instead of AzureOpenAI()
# ---------------------------------------------------------------------------
API_PARAMS = dict(
    model="gpt-4o",
    temperature=0,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={"type": "json_object"},
    seed=2266,
)

import re as _re
 
def _retry_after(error_message: str) -> float:
    """Parse wait time from a 429 message, e.g. 'try again in 3.248s' or '86ms'."""
    m = _re.search(r"try again in ([0-9.]+)(ms|s)", error_message)
    if m:
        value, unit = float(m.group(1)), m.group(2)
        return (value / 1000) if unit == "ms" else value
    return 5.0  # safe fallback

def classify_point(client: OpenAI, text: str, retries: int = 5) -> list[str]:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": PROMPT_FEW_COARSE},
                    {"role": "user",   "content": text},
                ],
                **API_PARAMS,
            )
            raw     = response.choices[0].message.content
            aspects = json.loads(raw).get("Aspects", ["-"])
            if aspects == "-":
                aspects = ["-"]
            valid   = [a for a in aspects if a in VALID_LABELS]
            unknown = [a for a in aspects if a not in VALID_LABELS]
            if unknown:
                print(f"    [WARN] unknown labels dropped: {unknown}")
            return valid if valid else ["-"]
        except Exception as e:
            wait = _retry_after(str(e)) + 1.0
            print(f"    [ERROR] attempt {attempt + 1}: {e}. retrying in {wait}s…")
            time.sleep(wait)
    return ["-"]


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Error: OPENAI_API_KEY environment variable not set.")
    if not INPUT_PATH.exists():
        raise SystemExit(f"Error: input not found: {INPUT_PATH}")

    preprocessed = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    # Load existing output if present — skip already-classified papers
    if OUTPUT_PATH.exists():
        output = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        already_done = {
            (paper_id, rev_id)
            for paper_id, reviewers in output.items()
            for rev_id in reviewers
        }
        print(f"Resuming — {len(already_done)} (paper, reviewer) pair(s) already classified, skipping.\n")
    else:
        output = {}
        already_done = set()

    total = sum(
        len(pts)
        for paper_id, reviewers in preprocessed.items()
        for rev_id, pts in reviewers.items()
        if (paper_id, rev_id) not in already_done
    )
    print(f"Running Lu et al. (2025) RAP on {total} critique points ({REVIEWER})…\n")

    client = OpenAI(api_key=api_key)

    for paper_id, reviewers in preprocessed.items():
        output.setdefault(paper_id, {})
        for reviewer_id, points in reviewers.items():
            if (paper_id, reviewer_id) in already_done:
                print(f"[SKIP] {paper_id} / {reviewer_id}")
                continue
            output[paper_id][reviewer_id] = {}
            print(f"[{paper_id} / {reviewer_id}]")
            for idx, text in tqdm(points.items()):
                aspects = classify_point(client, text)
                output[paper_id][reviewer_id][idx] = {
                    "text":    text,
                    "aspects": aspects,
                }
                time.sleep(2.0)

            # Save after each paper so progress isn't lost on interruption
            OUTPUT_PATH.write_text(
                json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
            )

    print(f"\n✓  Written → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
