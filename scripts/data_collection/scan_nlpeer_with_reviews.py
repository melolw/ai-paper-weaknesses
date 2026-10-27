"""
scan_nlpeer_with_reviews.py

Like scan_nlpeer.py but only returns papers where v1/reviews.json is non-empty.
Reads reviews.json inline to check, still without extracting the full archive.

Usage:
    python3 scan_nlpeer_with_reviews.py --zip ~/nlpeer.zip --output nlpeer_candidates_reviewed.json
    python3 scan_nlpeer_with_reviews.py --zip ~/nlpeer.zip --output nlpeer_candidates_reviewed.json --max_accepted 20 --max_rejected 20
"""

import argparse
import json
import re
import zipfile


RELEVANT_KEYWORDS = [
    "large language model", "llm", "language model", "transformer",
    "retrieval augmented", "rag", "chain of thought", "reasoning",
    "prompt", "in-context learning", "fine-tuning", "pretraining",
    "continual pretraining", "instruction tuning", "alignment",
    "agent", "agentic", "autonomous", "multi-agent",
    "hallucination", "factuality", "evaluation", "benchmark",
    "self-consistency", "test-time", "scaling", "inference", "decoding",
    "reward model", "llm judge", "peer review", "scientific",
]

def is_relevant(title: str, abstract: str) -> bool:
    text = (title + " " + abstract).lower()
    return any(kw in text for kw in RELEVANT_KEYWORDS)

def parse_decision(meta: dict) -> tuple[str, str]:
    if "not_accepted_at" in meta:
        return "rejected", meta["not_accepted_at"]
    if "accepted_at" in meta:
        return "accepted", meta["accepted_at"]
    return "unknown", ""

def scan(zip_path: str, max_accepted: int | None, max_rejected: int | None) -> dict:
    accepted, rejected = [], []
    meta_pattern = re.compile(r"data/([^/]+)/v1/meta\.json$")

    with zipfile.ZipFile(zip_path, "r") as zf:
        all_names = set(zf.namelist())
        meta_files = [n for n in all_names if meta_pattern.match(n)]
        print(f"Found {len(meta_files)} v1/meta.json files. Scanning...")

        done_accepted = max_accepted is not None and len(accepted) >= max_accepted
        done_rejected = max_rejected is not None and len(rejected) >= max_rejected

        for path in meta_files:
            if done_accepted and done_rejected:
                break

            try:
                meta = json.loads(zf.read(path))
            except Exception:
                continue

            title    = meta.get("title", "")
            abstract = meta.get("abstract", "")
            authors  = meta.get("authors", [])

            if not title or not is_relevant(title, abstract):
                continue

            decision, venue = parse_decision(meta)
            if decision == "unknown":
                continue
            if decision == "accepted" and done_accepted:
                continue
            if decision == "rejected" and done_rejected:
                continue

            # Check reviews.json is non-empty
            paper_hash = meta_pattern.match(path).group(1)
            reviews_path = f"data/{paper_hash}/v1/reviews.json"
            if reviews_path not in all_names:
                continue
            try:
                reviews_raw = json.loads(zf.read(reviews_path))
                if not reviews_raw:  # empty list or dict
                    continue
            except Exception:
                continue

            entry = {
                "hash":         paper_hash,
                "title":        title,
                "authors":      authors,
                "decision":     decision,
                "venue":        venue,
                "abstract":     abstract[:300] + "..." if len(abstract) > 300 else abstract,
                "pdf_path":     f"data/{paper_hash}/v1/paper.pdf",
                "reviews_path": reviews_path,
                "n_reviews":    len(reviews_raw) if isinstance(reviews_raw, list) else 1,
            }

            if decision == "accepted":
                accepted.append(entry)
                if max_accepted and len(accepted) >= max_accepted:
                    done_accepted = True
            else:
                rejected.append(entry)
                if max_rejected and len(rejected) >= max_rejected:
                    done_rejected = True

    return {"accepted": accepted, "rejected": rejected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip",          required=True)
    parser.add_argument("--output",       default="nlpeer_candidates_reviewed.json")
    parser.add_argument("--max_accepted", type=int, default=None)
    parser.add_argument("--max_rejected", type=int, default=None)
    args = parser.parse_args()

    results = scan(args.zip, args.max_accepted, args.max_rejected)

    print(f"\nResults with non-empty reviews:")
    print(f"  Accepted : {len(results['accepted'])}")
    print(f"  Rejected : {len(results['rejected'])}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
