## Summary
QuoteVerify proposes an inference-time pipeline for verifying citations in LLM-generated deep research reports by requiring structured citation triples containing explicit evidence quotes, then applying multistage verification: source fetching, substring-based quote validity checking, NLI entailment gating, and a repair-or-drop mechanism. The method is evaluated on a pilot subset of 20 ReportBench prompts using GPT-4o and Gemini-2.5-Pro, showing statistically significant match rate improvements over a standard baseline (+18.7pp and +12.5pp respectively). The analysis reveals that the structured citation format itself drives the majority of gains, while the verification pipeline primarily trades coverage for per-citation precision. Quote validity (18-28% for valid quotes) is identified as the primary bottleneck, reflecting that LLMs tend to paraphrase rather than produce verbatim quotes.

The paper is clearly written and addresses a timely problem: citation hallucination in deep research agents. However, three validity-critical issues limit the current contribution's defensibility: (1) the structured prompt baseline outperforms the full pipeline on the primary metric, yet this is not adequately framed as a core finding rather than a side observation; (2) the pilot uses only 20 prompts, severely limiting statistical power and generalizability; (3) related work omits several directly relevant methods (FRONT, CiteGuard) that readers will expect to see differentiated. These issues are fixable with targeted revision.

## Strengths
- Clear problem formulation and well-motivated research question
- Clean 5-stage pipeline design that is easy to understand and reproduce
- Honest error analysis identifying quote validity as the primary bottleneck
- Statistical significance testing with bootstrap resampling

## Weaknesses
- Structured prompt baseline outperforms full pipeline on Match Rate, undermining the core contribution claim
- Evaluation uses only 20 prompts, limiting statistical power and generalizability
- Related work omits FRONT and CiteGuard, weakening novelty positioning
- Coverage tradeoff (62-66% reference recall drop) is acknowledged but not adequately analyzed

## Key Issues
- Contribution C2 claims significant gains but omits that Prompt-Only outperforms full QuoteVerify
- Small sample size (20 prompts) limits generalizability of statistical claims
- Gap claim is too broad and omits adjacent prior work (FRONT, CiteGuard)

## Actionable Suggestions
**P0 — Reframe the core contribution around the precision-coverage tradeoff.** The current C2 claims "statistically significant improvement over standard baselines" but omits that Prompt-Only outperforms full QuoteVerify on Match Rate. Reposition the contribution to emphasize that QuoteVerify produces *verified* citations (higher per-citation reliability, auditability) at the cost of coverage. See the revised contribution wording in the PDF annotations.

**P0 — Acknowledge the pilot sample limitation explicitly.** Add a limitations subsection (or integrate into Section 4.2) stating that the evaluation uses only 20 prompts, which limits statistical power and generalizability. Frame the pilot as method validation rather than comprehensive benchmarking, and recommend scaling to the full ReportBench dataset.

**P1 — Expand related work with FRONT and CiteGuard.** Add 2-3 sentences in Section 2 contrasting QuoteVerify from: (a) FRONT (Huang et al., 2024), which teaches fine-grained grounded citations via training, and (b) CiteGuard (Choi et al., 2025), which performs retrieval-augmented citation validation. This strengthens the novelty positioning by explicitly differentiating inference-time no-training verification from training-based and evaluation-only approaches.

**P1 — Strengthen the ablation interpretation.** Section 4.3 shows that No-Entailment actually achieves a higher Match Rate (58.8%) than full QuoteVerify (53.1%), suggesting the NLI gate may be overly conservative. Add a brief analysis: what is the precision-recall tradeoff of the NLI gate? Are there false negatives where valid quote-statement pairs are rejected? This would help readers understand whether the gate is too strict or appropriately cautious.

**P2 — Add a brief NLI justification.** Add one sentence explaining why the evidence quote is used as premise and the statement as hypothesis, and whether the reverse direction was considered.

**P2 — Improve abstract self-containment.** Add one sentence bounding the practical significance alongside the statistical gains. Explicitly state that absolute match rates remain modest (~53%) and that verification alone does not fully solve the citation problem if base models struggle to generate verbatim quotes.

**P2 — Clean up Eq. (1) notation.** Rewrite the triple definition with clean field names ($s_i$, $u_i$, $q_i$) and explicit type annotations to improve reproducibility and readability.

## Storyline Options + Writing Outlines
### Abstract Outline (Complete)

**S1 (Problem & Domain):** Deep research agents that synthesize long-form reports with citations are increasingly deployed, yet citation quality remains problematic: models frequently hallucinate references, fabricate quotes, or cite sources that do not support claimed statements.
*Role:* Establish the practical context and core problem. *Evidence anchor:* Page 1, Abstract line 1.

**S2 (Significance/Challenge):** In high-stakes research settings, readers need to verify that specific claims are supported by their cited sources, but standard generation provides no mechanism for auditable provenance.
*Role:* Establish why this problem matters and what is currently missing. *Evidence anchor:* Page 1, Introduction line 1.

**S3 (Prior Gap):** Prior approaches either require training data, focus on short-form QA, or evaluate citations without correcting them.
*Role:* Position the gap relative to existing work. *Evidence anchor:* Page 1, Introduction line 2 + Related Work.

**S4 (Proposed Method):** We propose QuoteVerify, an inference-time pipeline that verifies citations through quote-backed evidence. The pipeline prompts the model to generate structured citation triples with explicit evidence quotes, then applies multistage verification: source fetching, quote validity checking via substring matching, and NLI-based entailment gating.
*Role:* Present the solution at a high level. *Evidence anchor:* Page 1, Abstract lines 2-3.

**S5 (Key Result + Bounded Implication):** Experiments on a ReportBench pilot demonstrate that requiring structured citation triples substantially improves citation match rates (+18.7pp on GPT-4o, p = 0.019), though absolute match rates remain modest (~53%). Analysis reveals that quote validity is the primary bottleneck—LLMs produce valid quotes only 18–28% of the time—indicating that combining verification with improved quote generation fidelity is a promising direction.
*Role:* State key results with bounded practical significance. *Evidence anchor:* Page 1, Abstract line 4; Page 5, Table 1.

### Introduction Outline (Complete)

**P1 (Big Picture & Stakes):** Large language models are increasingly deployed as deep research agents that browse the web, read papers, and synthesize long-form reports with citations. In these settings, correctness extends beyond producing coherent narratives to providing auditable provenance: readers need to verify that specific claims are supported by the cited sources. However, recent evaluations reveal that even state-of-the-art systems exhibit substantial citation inconsistency, with cited-statement match rates ranging from 27% to 79% depending on the model and evaluation protocol.
*Role:* Establish territory, stakes, and severity. *Transition:* "This raises the question of how to verify citations at inference time without retraining models." *Evidence:* Page 1, Intro line 1.

**P2 (Gap in Prior Work):** Prior work on evidence-grounded generation has addressed related problems but with different focuses. WebGPT and GopherCite train models to cite sources when answering questions, while RARR and Self-RAG retrofit attribution through retrieval and revision. More recently, FRONT teaches models to generate fine-grained grounded citations via fine-tuning, and CiteGuard validates citations through retrieval-augmented alignment. However, these approaches either require training data, operate on short-form QA, or focus on evaluation rather than correction. Inference-time verification and repair for long-form research reports—where citations point to external documents and claims span multiple sources—remains underexplored.
*Role:* Identify concrete gap by contrasting with strongest adjacent methods. *Transition:* "We address this gap with a modular, no-training verification pipeline." *Evidence:* Page 1, Intro lines 2 + Related Work.

**P3 (Proposed Solution & Key Insight):** We propose QuoteVerify, an inference-time pipeline that verifies citations through quote-backed evidence. The key insight is that many citation failures are mechanical and thus cheap to detect: bad URLs, fabricated quotes, or citing nearby-but-not-equal claims. QuoteVerify makes these failures detectable by requiring each cited statement to carry an evidence quote that is (1) verifiable as present in the cited document via substring matching, and (2) checked for semantic entailment to prevent cases where a verbatim quote is present but does not actually support the claimed statement.
*Role:* Present the method intuition and core mechanism. *Transition:* "The pipeline consists of five stages, which we describe next." *Evidence:* Page 1, Intro line 3.

**P4 (Contribution Summary):** Our contributions are: (1) a modular inference-time citation verification pipeline that operates as a wrapper around any base report generator, requiring no additional training; (2) empirical evaluation on ReportBench showing that inference-time verification improves citation precision, with the structured citation format driving the majority of gains; (3) analysis revealing that quote validity is the primary bottleneck, with LLMs producing valid quotes only 18–28% of the time; (4) ablation studies demonstrating that the entailment gate prevents semantically irrelevant quotes while the repair step provides marginal coverage recovery.
*Role:* Explicitly list contributions with accurate framing. *Evidence:* Page 2, Contributions lines 1-5.

## Priority Revision Plan
| Priority | Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit |
|---|---|---|---|---|---|
| P0 | Contribution C2 claims significant gains but omits that Prompt-Only outperforms full QuoteVerify | High | Overclaiming pipeline value; under-reporting baseline performance | Reframe contribution to emphasize precision-coverage tradeoff and per-citation auditability | Restores scientific defensibility; aligns claims with actual evidence |
| P0 | Small sample size (20 prompts) limits generalizability | High | Pilot evaluation design without explicit scope bounding | Add a limitations subsection acknowledging sample size and framing results as method validation | Prevents overinterpretation; clarifies practical scope of findings |
| P0 | Gap claim is too broad and omits adjacent prior work (FRONT, CiteGuard) | Medium | Incomplete literature positioning | Expand Section 2 with 2-3 sentences contrasting inference-time verification from training-based grounding and evaluation-only methods | Strengthens novelty positioning; anticipates reviewer comparisons |
| P1 | Structured format finding is framed as a side observation rather than core insight | Medium | Narrative misalignment between results and discussion | Restructure Section 4.2 to directly address what this means for method positioning | Improves narrative coherence; highlights the true primary mechanism |
| P1 | Coverage tradeoff (62-66% reference recall drop) is acknowledged but not analyzed | Medium | Lack of depth on the precision-recall implications of the pipeline | Add analysis of when this tradeoff is acceptable (e.g., high-stakes vs. comprehensive review) | Provides practical guidance for deployment contexts |
| P2 | NLI premise-hypothesis direction choice lacks explicit justification | Low | Missing design rationale | Add one sentence explaining the quote-as-premise rationale | Improves method transparency and reproducibility |
| P2 | Abstract lacks practical significance bounding | Low | Over-emphasis on statistical gains without absolute context | Add one sentence stating absolute match rates remain modest (~53%) | Prevents overestimation of practical readiness |
| P2 | Eq. (1) notation is ambiguous | Low | PDF extraction artifacts / unclear field boundaries | Clean up triple notation with explicit field names and type annotations | Improves readability and implementation clarity |

### Execution Timeline
- **Stage 1 (Today):** Complete P0 claim reframing and limitation acknowledgment. These are text-only revisions that directly address the core validity risks.
- **Stage 2 (This Week):** Execute P1 narrative restructuring and coverage tradeoff analysis. Requires careful rewriting of Section 4.2 and 4.3 to ensure coherent argument flow.
- **Stage 3 (Before Submission):** Address P2 technical clarifications (NLI rationale, abstract bounding, notation cleanup) and expand Related Work. These are incremental but improve overall scientific rigor.

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | QuoteVerify improves citation match rate over standard baselines | ReportBench pilot (20 prompts, 10 domains); GPT-4o, Gemini-2.5-Pro; Baselines: Standard, Prompt-Only | Match Rate, p-value | +18.7pp (GPT-4o, p=0.019), +12.5pp (Gemini, p=0.011) | Partially (Prompt-Only outperforms QuoteVerify) | Small N=20 limits statistical power |
| E2 | Pipeline components contribute differentially to performance | GPT-4o; Variants: Full, No-Entailment, Drop-Only | Match Rate, Quote Valid, Entail Pass | No-Entailment +5.7pp Match Rate; Drop-Only +0.4pp | Entailment gate filters irrelevant quotes; Repair has marginal value | Drop-Only has higher Entail Pass, questioning repair utility |
| E3 | Failure mode analysis by pipeline stage and model | Figure 2a (outcomes), 2b (source type) | Fetch Rate, Pass Rate by category | Quote validity is primary bottleneck (18-28%); high fetch success (89-100%) | Bottleneck analysis supported | Analysis relies on same small N=20 |

### Research-Theme Gap Diagnosis
The core research-value claims (improved citation verifiability in long-form reports) are partially supported but weakly bounded. The claim that "inference-time verification meaningfully improves citation quality" is statistically valid on the pilot but practically limited: absolute match rates remain modest, and the structured prompt baseline outperforms the full pipeline on the primary metric. The reproducibility is strong (pipeline is modular and code is public), but the impact on practice depends on whether the precision-coverage tradeoff is acceptable in downstream applications.

### Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| C2: Verification improves citation quality | Scaling to the full ReportBench dataset (50+ prompts) will preserve or amplify the match rate gains | Run QuoteVerify and Prompt-Only on full dataset | Standard, Prompt-Only, QuoteVerify | Match Rate, Quote Valid, Ref Recall | Match Rate gains statistically significant (p < 0.05) with larger N | Medium (1-2 weeks API cost) | Strengthens empirical validity and generalizability |
| C1: NLI gate prevents irrelevant quotes | The NLI gate reduces semantically mismatched citations, even if it lowers Match Rate | Compare NLI gate precision: sample 50 rejected triples and manually verify if quote supports statement | No-Entailment vs Full | Precision of NLI rejections, Manual verification accuracy | >70% of NLI rejections are true negatives (irrelevant quotes) | Low (1 week manual effort) | Validates the semantic filter's utility despite Match Rate drop |
| C3: Quote validity bottleneck | Retrieval-augmented prompting (RAG) for quote generation increases valid quote rate | Provide LLM with fetched source text chunks during Stage 1 generation | Standard generation, RAG-augmented generation | Quote Valid rate, Match Rate | Quote Valid rate increases from ~20% to >40% | Medium (1 week implementation) | Directly addresses the core bottleneck and improves pipeline utility |

```text
ASCII Diagram — Experiment Upgrade Plan
Stage 1 (Immediate): Scale to full ReportBench (E1-ext) -> validates generalizability
    |
Stage 2 (Validation): NLI gate precision audit (E2-ext) -> proves semantic filter value
    |
Stage 3 (Enhancement): RAG-augmented quote generation (E3) -> addresses validity bottleneck
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Modular inference-time citation verification pipeline operating as wrapper around any base report generator, requiring no additional training | [1], [2], [3] | partially_overlapping | FRONT [1] uses training for fine-grained quotes; CiteGuard [2] does retrieval-augmented validation. QuoteVerify's no-training inference-time wrapper is distinct but adjacent to these approaches. | High | Emphasize the no-training, inference-time, post-hoc verification aspect as the key differentiator |
| C2 | Empirical evaluation showing statistically significant improvement over standard baselines on ReportBench | [3] | partially_overlapping | ReportBench [3] provides the evaluation framework. The improvement is real but primarily driven by structured prompting (Prompt-Only), not the verification pipeline itself. | High | Reframe: the pipeline produces *verified* citations (higher precision, auditability) at the cost of coverage, not simply *more* matching citations |
| C3 | Analysis revealing quote validity as primary bottleneck (18-28% valid quotes) | [1], [4] | supported | This finding is novel and directly measurable. It highlights that LLMs paraphrase rather than verbatim quote, a phenomenon not previously quantified at this scale for long-form reports. | High | No repositioning needed; strengthen by explicitly linking to GopherCite's training-based verbatim quote generation challenge |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Evidence-Based Text Generation | Branch: Training-Based Grounding | | Models are fine-tuned to generate citations/quotes | QuoteVerify requires no training | Low overlap risk |
| | Leaf: Verbatim Quote Training | [1] | Fine-tuning improves quote fidelity | FRONT trains for fine-grained quotes; QuoteVerify verifies post-hoc | Medium: different paradigm (training vs inference) |
| Root: Evidence-Based Text Generation | Branch: Inference-Time Verification | | Verification occurs during/after generation without retraining | This paper's core paradigm | Low overlap risk |
| | Leaf: Retrieval-Augmented Validation | [2] | External retrieval improves citation grounding | CiteGuard validates citations via retrieval; QuoteVerify uses substring + NLI | Medium: different verification mechanism |
| Root: Evidence-Based Text Generation | Branch: Evaluation Benchmarks | | Benchmarks assess citation quality | ReportBench provides the evaluation framework | Low: evaluation vs method |
| | Leaf: Deep Research Agent Evaluation | [3], [4] | Automated metrics assess report quality | These papers evaluate agents; QuoteVerify is a verification method | Low overlap risk |
| Root: Evidence-Based Text Generation | Branch: Evidence Taxonomy | | Systematic classification of evidence-based methods | Survey covers 134 papers across 7 dimensions | Low: survey vs method |
| | Leaf: Unified Evidence Taxonomy | [5] | Fragmented terminology needs unification | Provides context for where QuoteVerify fits | Low overlap risk |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] FRONT | Attributed LLMs, fine-grained citation generation | Two-stage training: quote grounding + response generation via fine-tuning | Both use evidence quotes for citation grounding | FRONT requires training; QuoteVerify is inference-time and no-training | Partial overlap; strengthens QuoteVerify's no-training positioning |
| [2] CiteGuard | Citation validation for scientific writing | Retrieval-augmented agent framework for citation attribution alignment | Both validate citations at inference time | CiteGuard focuses on alignment; QuoteVerify uses substring + NLI pipeline | Partial overlap; different verification mechanism |
| [3] ReportBench | Deep research agent evaluation | Automated benchmark for citation quality and statement faithfulness | Provides the evaluation framework for QuoteVerify | ReportBench is a benchmark; QuoteVerify is a method | Low overlap; complementary |
| [4] DeepResearch Bench | Deep research agent evaluation | Multi-task benchmark with adaptive criteria | Alternative evaluation framework | Different benchmark design and task scope | Low overlap; complementary |
| [5] Survey | Evidence-based text generation taxonomy | Analysis of 134 papers, 300 metrics across 7 dimensions | Contextualizes QuoteVerify within the field | Survey vs method; different contribution type | Low overlap; provides positioning context |

### Contribution-level Novelty Conclusion

C1 (pipeline novelty) is **partially_overlapping**: the no-training, inference-time verification wrapper is distinct from training-based approaches like FRONT [1], but the verification concept is adjacent to retrieval-augmented validation methods like CiteGuard [2]. Repositioning should emphasize the modular, post-hoc, no-training aspect as the key differentiator. C2 (empirical gains) is **partially_overlapping**: the improvement is real but primarily driven by structured prompting rather than the verification pipeline. Reframe to emphasize precision-coverage tradeoff. C3 (bottleneck analysis) is **supported**: the finding that LLMs paraphrase rather than verbatim quote (18-28% valid quotes) is a novel, measurable insight that highlights a fundamental limitation in current LLM citation behavior.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Evidence-Based Text Generation (Root)
├── Branch: Training-Based Grounding
│   ├── Leaf: Verbatim Quote Training [1] -> FRONT: fine-tunes for grounded quotes
│   └── Leaf: Evidence-Conditioned Generation -> methods that condition on retrieved evidence
├── Branch: Inference-Time Verification
│   ├── Leaf: Retrieval-Augmented Validation [2] -> CiteGuard: retrieval-based citation alignment
│   └── Leaf: Quote-Backed Verification (THIS PAPER) -> QuoteVerify: substring + NLI pipeline, no-training
├── Branch: Evaluation Benchmarks
│   ├── Leaf: Deep Research Agent Evaluation [3][4] -> ReportBench, DeepResearch Bench
│   └── Leaf: Evidence Taxonomy [5] -> systematic classification of 134 papers
└── Value Positioning: QuoteVerify solves the inference-time, no-training verification gap
    for long-form research reports, trading coverage for per-citation auditability
```

## References
[1] Learning Fine-Grained Grounded Citations for Attributed Large Language Models 2408.04568

[2] CiteGuard: Faithful Citation Attribution for LLMs via Retrieval-Augmented Validation 2510.17853

[3] ReportBench: Evaluating Deep Research Agents via Academic Survey Tasks 2508.15804

[4] DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents 2506.11763

[5] Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with Large Language Models 2508.15396

[6] Teaching language models to support answers with verified quotes 2203.11147

[7] GhostCite: A Large-Scale Analysis of Citation Validity in the Age of Large Language Models 2602.06718

[8] When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs 2406.01297

## Scores
**Final Score: 5.5/10**

This score reflects a paper with a valid, well-designed method and a genuine research insight (the quote validity bottleneck at 18-28%), but penalized for three validity-critical issues that limit current defensibility: (1) the structured prompt baseline outperforms the full pipeline on the primary metric, yet the contribution narrative overclaims pipeline value; (2) the evaluation uses only 20 prompts, severely limiting statistical power and generalizability; (3) related work omits directly relevant methods (FRONT, CiteGuard) that weaken novelty positioning. The core method is sound, code is public, and the bottleneck analysis is valuable—but the contribution framing and evaluation scope need substantial revision before the paper can be considered publication-ready.

**Post-Revision Target: [7, 8]/10**

If the authors successfully (a) reframe the contribution around the precision-coverage tradeoff and per-citation auditability, (b) explicitly bound the pilot-sample limitation, (c) expand related work with FRONT and CiteGuard, and (d) optionally scale evaluation to the full ReportBench dataset, the paper would present a defensible and valuable contribution. The method itself does not require fundamental rework; the primary revision path is narrative reframing and explicit scope bounding.

```text
ASCII Diagram — Paper Structure & Evidence Map
[Problem: Citation hallucination in deep research agents]
    -> [Gap: No inference-time, no-training verification for long-form reports]
    -> [Solution: QuoteVerify 5-stage pipeline (structured triples + substring + NLI + repair)]
    -> [Evidence: +18.7pp Match Rate on GPT-4o (p=0.019), 20 prompts]
    -> [Key Finding: Structured format drives most gains; quote validity is bottleneck]
    -> [Risk: Prompt-Only outperforms full pipeline; contribution overclaims pipeline value]
    -> [Fix: Reframe contribution around precision-coverage tradeoff + auditability]
    -> [Expected impact: Defensible positioning; clearer practical guidance]

ASCII Diagram — Revision Strategy Roadmap
| Priority | Low Effort | High Effort |
|---|---|---|
| High Impact | Reframe contribution C2 + bound sample limitation | Scale evaluation to full ReportBench |
| Medium Impact | Expand Related Work with FRONT/CiteGuard | NLI gate precision audit (manual verification) |
| Low Impact | Clean Eq. (1) notation + add NLI rationale | Add compute/memory cost analysis |
```