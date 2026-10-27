"""
select_fars_papers.py
=====================
Scans the downloaded FARS dataset at ~/fars-a-reviews, checks which of
the 5 existing AIG_CUR papers have human reviews, and selects 45 more
papers that:
  - have both a human review and a paperreview.ai LLM review
  - are topically relevant to NLP/LLM research

Usage:
    python scripts/data_collection/select_fars_papers.py
"""

import json
from pathlib import Path

FARS_DIR = Path.home() / "fars-a-reviews" / "data"

EXISTING_TITLES = {
    "Chunked Budget Allocation Prevents Nonmonotonic Regressions in World-Model Verification",
    "Citation-Consistent Voting for Permutation-Robust Retrieval-Augmented Generation",
    "Draft-and-Continue Self-Consistency: An Empirical Study of Two-Stage Branch Budgeting for LLM Reasoning",
    "Isolated Solve-Then-Judge: A Simple Defense Against Candidate-Response Prompt Injection for Multimodal LLM Judges",
    "Token-Balanced Continual Pretraining Eliminates Brain Rot Degradation",
}

# Excluded — off-topic or too niche
EXCLUDED_IDS = {
    "FA0226",  # EEG decoding (neuroscience)
    "FA0003",  # LLM-driven alpha mining (finance/quant)
    "FA0290",  # HNSW index leakage (vector DB security)
    "FA0036",  # Kalman policy optimization (niche RL)
    "FA0056",  # Kalman-filtered importance ratios (niche RL)
    "FA0115",  # OCR reranking (vision)
    "FA0076",  # dense video caption evaluation  
    "FA0235",  # chart QA visual degradations
    "FA0012",  # spatial revision in VLMs
}

RELEVANT_KEYWORDS = [
    "large language model", "llm", "language model", "transformer",
    "retrieval", "rag", "chain of thought", "reasoning",
    "prompt", "in-context", "fine-tun", "instruction tun",
    "alignment", "rlhf", "reward",
    "agent", "agentic", "multi-agent",
    "hallucination", "factual", "factuality",
    "evaluation", "benchmark", "judge",
    "continual", "pretraining", "continual learning",
    "calibration", "uncertainty",
    "context", "long context", "memory",
    "summarization", "question answering", "qa",
    "knowledge", "grounding", "retrieval augmented",
    "safety", "alignment", "jailbreak",
    "efficiency", "quantization", "compression",
    "code generation", "coding",
    "test-time", "inference", "scaling",
    "multimodal", "vision language",
    "embedding", "representation",
    "lora", "adapter", "peft",
]


def is_relevant(title: str, abstract: str) -> bool:
    text = (title + " " + abstract).lower()
    return any(kw in text for kw in RELEVANT_KEYWORDS)


def load_project(project_dir: Path) -> dict | None:
    human_path = project_dir / "human_review.json"
    pr_path    = project_dir / "paperreview.json"

    if not human_path.exists() or not pr_path.exists():
        return None

    try:
        human = json.loads(human_path.read_text(encoding="utf-8"))
        pr    = json.loads(pr_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not human.get("reviews") or len(human["reviews"]) == 0:
        return None
    if not pr.get("success", False):
        return None

    paper    = human.get("paper", {})
    title    = paper.get("title", "") or pr.get("title", "")
    abstract = paper.get("abstract", "")

    return {
        "id":         project_dir.name,
        "title":      title,
        "abstract":   abstract,
        "n_reviews":  len(human["reviews"]),
        "llm_score":  pr.get("numerical_score"),
        "gitlab_url": paper.get("gitlabUrl", ""),
    }


def main():
    if not FARS_DIR.exists():
        raise SystemExit(f"FARS dataset not found at {FARS_DIR}")

    projects   = sorted(FARS_DIR.glob("FA*"))
    all_papers = []
    title_to_id = {}

    for proj in projects:
        data = load_project(proj)
        if data:
            all_papers.append(data)
            title_to_id[data["title"].strip().lower()] = data["id"]

    print(f"Papers with both human + LLM reviews: {len(all_papers)}\n")

    # Check existing 5
    print("=" * 60)
    print("Existing 5 AIG_CUR papers:")
    print("=" * 60)
    found_ids = set()
    for title in EXISTING_TITLES:
        match = title_to_id.get(title.strip().lower())
        if match:
            print(f"  ✓ FOUND  [{match}]  {title[:70]}")
            found_ids.add(match)
        else:
            print(f"  ✗ NOT FOUND  {title[:70]}")
    print()

    # Select 45
    candidates = [
        p for p in all_papers
        if p["id"] not in found_ids
        and p["id"] not in EXCLUDED_IDS
        and is_relevant(p["title"], p["abstract"])
    ]
    candidates.sort(key=lambda x: (-x["n_reviews"], -(x["llm_score"] or 0)))
    selected = candidates[:45]

    print("=" * 60)
    print("Selected 45 papers:")
    print("=" * 60)
    for i, p in enumerate(selected, 1):
        score = f"{p['llm_score']:.2f}" if p["llm_score"] else "N/A"
        print(f"  [{i:02d}] {p['id']}  reviews={p['n_reviews']}  llm_score={score}")
        print(f"        {p['title']}")

    out = [{"id": p["id"], "title": p["title"], "gitlab_url": p["gitlab_url"],
            "n_reviews": p["n_reviews"], "llm_score": p["llm_score"]}
           for p in selected]

    out_path = Path(__file__).parent.parent.parent / "data" / "fars_selected_45.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n✓  Written → {out_path}")
    print(f"Total relevant candidates: {len(candidates)}")


if __name__ == "__main__":
    main()
