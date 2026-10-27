## Summary
This paper proposes Execution-Signature Recycling (ESR), a training-free test-time scaling method for code generation that clusters candidates by their execution signatures (failing test IDs and error types) and conditions subsequent generations on a deduplicated failure bank. ESR is evaluated on HumanEval+ using Qwen2.5-Coder-7B-Instruct under a fixed 16-generation budget. The authors report a negative result: ESR achieves the highest mean Pass@1 (87.60%) but does not significantly outperform the simpler Self-Debug baseline (86.99%), with a 95% confidence interval of [−0.81, 2.24] that includes zero.

The paper is notable for its honest reporting of a null finding and its rigorous statistical evaluation with paired bootstrap confidence intervals. However, the novelty is incremental—ESR adapts the Recycling Search Experience (RSE) framework from Wang et al. (2026) to code generation by replacing semantic deduplication with execution-grounded signatures. The research value lies in testing a widely assumed hypothesis (that cross-sample feedback aggregation helps) and finding it does not hold under this setting, though the single-benchmark, single-model scope limits generalizability.

## Strengths
1. **Honest reporting of a negative result.** The authors transparently report that ESR does not significantly outperform the baseline, including confidence intervals that include zero. This intellectual honesty is commendable and contributes valuable knowledge about the limits of cross-sample feedback aggregation.

2. **Rigorous statistical evaluation.** The use of paired bootstrap confidence intervals across three random seeds, with pre-registered decision rules, provides a statistically sound evaluation framework that goes beyond simple point-estimate comparisons.

3. **Clear and reproducible method.** ESR is well-defined with explicit hyperparameters (N=16, K=2, M=3, 900-token budget). The execution signature formulation (Eq. 1) is mathematically clear, and the two-round procedure is easy to implement.

4. **Insightful analysis of the null result.** The signature statistics (68% all-pass tasks, median unique signatures = 1.0) and variance analysis provide concrete evidence supporting the conclusion that failure modes are already diverse enough for per-sample methods.

5. **Fair budget-matched baselines.** Both ESR and Self-Debug operate under the same 16-generation budget, ensuring a fair comparison of information efficiency rather than raw compute advantage.

## Weaknesses
1. **Incremental novelty relative to RSE (Wang et al., 2026).** ESR's core mechanism—recycling cross-sample failure information via a shared bank—is directly inspired by RSE's experience recycling. The primary adaptation is replacing semantic trajectory deduplication with deterministic execution signatures for code generation. This is a valid domain transfer but constitutes an incremental rather than fundamental contribution. The novelty claim should be more precisely bounded.

2. **Informational asymmetry in baseline comparison.** Self-Debug provides individualized feedback to each of its 8 candidates (error type and traceback for up to 3 failing tests), while ESR's Round 2 receives a shared failure bank (top-3 clusters, K=2 examples each, ~900 tokens). Self-Debug's per-candidate feedback may be informationally richer per candidate than ESR's aggregated view, potentially giving Self-Debug an unfair advantage. This asymmetry is not explicitly discussed.

3. **Single-benchmark, single-model scope.** All experiments use only HumanEval+ with Qwen2.5-Coder-7B-Instruct. The conclusion that "per-sample self-debugging may be sufficient" is therefore bounded to this specific model and benchmark. The claim does not generalize to harder benchmarks (e.g., LiveCodeBench, MBPP), weaker models, or different coding tasks.

4. **Higher inter-seed variance for ESR.** ESR exhibits std=1.27 compared to Self-Debug's std=0.70 and Best-of-16's std=0.50. This higher variance is a practical reliability concern that should be more prominently connected to the paper's conclusion about preferring simpler approaches.

5. **Missing discussion of exact-match clustering limitation.** The exact signature equality criterion is strict; candidates failing on overlapping but non-identical test sets may share common root causes. This design trade-off is not discussed, and fuzzy signature matching is only mentioned in future work.

## Key Issues
| Priority | Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit |
|----------|-------|------------|------------|-----------------|------------------|
| P0 | Novelty positioning vs RSE (Wang et al., 2026) | Major | ESR's core mechanism (cross-sample failure recycling) is directly adapted from RSE's semantic deduplication; the domain transfer to code generation is incremental | Reposition ESR as a domain-specific adaptation of RSE, emphasizing test-grounded signatures as the design innovation | Accurate novelty framing that prevents reviewer rejection for insufficient contribution |
| P0 | Informational asymmetry in baseline comparison | Major | Self-Debug provides richer per-candidate feedback than ESR's shared bank; this asymmetry could partially explain the null result | Add feedback-content quantification and a matched-feedback ablation | Validates that the null result reflects mechanism limits rather than baseline advantage |
| P1 | Single-benchmark, single-model scope | Major | All experiments use HumanEval+ with Qwen2.5-Coder-7B-Instruct only | Add evaluation on at least one additional benchmark (e.g., MBPP or LiveCodeBench) | Supports generalizability claims and bounds the conclusion's scope |
| P1 | Higher inter-seed variance for ESR | Minor | Cross-sample aggregation may introduce instability not present in per-sample approaches | Explicitly connect variance finding to practical reliability conclusion | Strengthens the argument for preferring simpler, more stable approaches |
| P2 | Exact-match clustering limitation | Minor | Strict signature equality misses near-miss failure patterns that could share root causes | Discuss design trade-off and suggest fuzzy matching as future work | Improves method transparency and completeness |

## Actionable Suggestions
1. **Reposition novelty vs RSE (P0).** In Section 2.4 (Design Rationale) and Section 4 (Related Work), explicitly position ESR as a domain adaptation of RSE (Wang et al., 2026). State that the core concept of recycling cross-sample failure information is inspired by RSE, and that ESR's innovation is the use of deterministic, test-grounded execution signatures suited for code generation. This prevents the novelty claim from appearing overstated.

2. **Quantify baseline feedback asymmetry (P0).** In Section 3.1, add a paragraph quantifying the average token count and informational content of Self-Debug's per-candidate feedback vs. ESR's shared failure bank. If possible, add a matched-feedback ablation where ESR's bank is expanded to match Self-Debug's per-candidate detail level, to isolate whether the null result reflects mechanism limits or baseline advantage.

3. **Expand evaluation scope (P1).** Add evaluation on at least one additional benchmark (e.g., MBPP for simpler tasks or LiveCodeBench for harder, contamination-resistant tasks) and/or one additional model family (e.g., Llama-3-8B-Instruct). This strengthens the generalizability of the conclusion or helps bound its scope.

4. **Connect variance to conclusion (P1).** In Section 3.3 (Discussion), add one sentence explicitly linking ESR's higher inter-seed variance (std=1.27) to the practical recommendation for preferring simpler approaches. This strengthens the argument that ESR's instability makes it less attractive even when mean performance is comparable.

5. **Disclose exact-match clustering limitation (P2).** In Section 2.2, add one sentence discussing the trade-off of exact signature matching: it ensures determinism and compactness but may miss near-miss failure patterns that share root causes. Suggest fuzzy or set-similarity-based matching as future work.

6. **Move automated-generation disclaimer (P2).** Remove the "WARNING: This paper was generated by an automated research system" from the Abstract and move it to a footnote or appendix. This keeps the abstract clean and professional for peer review.

## Storyline Options + Writing Outlines
### Current Storyline Diagnosis

The current paper follows a straightforward arc: background -> gap -> method -> null result -> analysis. However, the negative result is front-loaded too early (appearing in the Abstract and Introduction before method details), which can cause reader disengagement. The "research value" of the null finding is implicit rather than explicit.

### Recommended Storyline: "Insight-Driven Null Result"

Reposition the paper from "we tried something and it didn't work" to "we tested a widely assumed hypothesis about cross-sample feedback and found it does not hold under these conditions, revealing that per-sample feedback is already sufficient for strong models." This framing emphasizes the *insight* gained, not the *failure*.

### Abstract Outline (complete)

- **S1 (Problem/Domain):** Test-time scaling improves code generation by sampling multiple candidates and using execution feedback to guide refinement.
- **S2 (Challenge):** When multiple candidates fail for similar reasons, providing redundant feedback may waste the model's context, motivating cross-sample feedback aggregation.
- **S3 (Prior Gap/Hypothesis):** While experience recycling has shown benefits in mathematical reasoning (Wang et al., 2026), it is unclear whether deduplicated failure feedback provides measurable gains in code generation, where failure modes may already be diverse.
- **S4 (Method):** We propose Execution-Signature Recycling (ESR), which clusters candidates by test-grounded execution signatures and conditions subsequent generations on a compact, deduplicated failure bank.
- **S5 (Key Result + Bounded Implication):** ESR does not significantly outperform per-sample self-debugging on HumanEval+ (CI includes zero), suggesting that for strong models, failure mode diversity makes cross-sample aggregation redundant.

### Introduction Outline (complete)

- **P1 (Big Picture + Best-of-N):** Test-time scaling via best-of-N sampling substantially improves code generation. However, best-of-N treats candidates independently, potentially generating redundant solutions.
- **P2 (Execution Feedback Landscape):** Execution feedback (self-debugging, Reflexion) improves code generation. Per-sample methods refine each candidate independently; episodic-memory methods maintain high-level failure summaries. Neither systematically deduplicates failure information across candidates in a test-grounded manner.
- **P3 (Hypothesis + Motivation):** We hypothesize that failure modes cluster across candidates, so deduplicated feedback could reduce redundant exploration. Testing this hypothesis is valuable because it directly probes whether cross-sample feedback aggregation—a widely assumed benefit—actually provides measurable gains.
- **P4 (Method Preview):** ESR clusters candidates by execution signatures and conditions Round 2 generations on a deduplicated failure bank.
- **P5 (Result Preview + Insight):** ESR achieves comparable mean performance to Self-Debug but with higher variance. The null result reveals that for strong models, per-sample feedback captures sufficient signal, and the validated takeaway is that execution feedback remains valuable but need not be aggregated.
- **P6 (Contributions):** (1) ESR method with test-grounded signatures, (2) rigorous evaluation with bootstrap CIs, (3) evidence that cross-sample aggregation provides limited marginal value under this setting.

## Priority Revision Plan
### Stage 1: Immediate Text & Novelty Repositioning (Today)
- **Task 1.1:** Move the automated-generation disclaimer from the Abstract to a footnote or Acknowledgement section.
- **Task 1.2:** Rewrite the Introduction to delay the detailed result preview until after the method preview, framing the null result as an insight about feedback efficiency rather than a method failure.
- **Task 1.3:** Update Section 2.4 (Design Rationale) and Section 4 (Related Work) to explicitly position ESR as a domain adaptation of RSE (Wang et al., 2026), bounding the novelty claim to the use of deterministic, test-grounded execution signatures.
- **Task 1.4:** Refine the third contribution claim to articulate the knowledge gained from the null result (i.e., that failure modes in strong code models are diverse enough to render cross-sample aggregation redundant).

### Stage 2: Methodological Clarifications & Analysis Deepening (This Week)
- **Task 2.1:** Add a discussion on the exact signature matching limitation in Section 2.2, acknowledging the trade-off between determinism and missing near-miss patterns.
- **Task 2.2:** Quantify the informational asymmetry in the baseline comparison (Section 3.1), discussing how Self-Debug's per-candidate feedback compares to ESR's shared bank.
- **Task 2.3:** Strengthen the Discussion (Section 3.3) by explicitly linking ESR's higher inter-seed variance to the practical reliability argument for simpler methods.
- **Task 2.4:** Polish the Conclusion to include a validated positive takeaway (that execution feedback is valuable, but per-sample forms suffice for strong models).

### Stage 3: Experimental Expansion (Before Submission)
- **Task 3.1 (Optional but Recommended):** Evaluate ESR on a second benchmark (e.g., MBPP or LiveCodeBench) to test generalizability.
- **Task 3.2 (Optional but Recommended):** Run a matched-feedback ablation where ESR's failure bank is expanded to match the detail level of Self-Debug's per-candidate feedback, isolating mechanism limits from baseline advantages.

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory (full coverage)
| Exp ID | Objective/Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|----------------------|-------|---------|--------------|-----------------|-------------------|
| E1 | Cross-sample feedback aggregation improves code generation | HumanEval+, Qwen2.5-Coder-7B-Instruct, N=16 seeds=3 | Pass@1, 95% CI | ESR (87.60%) vs Self-Debug (86.99%), CI includes 0 | Feedback helps (vs Best-of-16), but aggregation provides no significant gain over per-sample | Single model/benchmark; higher variance for ESR |
| E2 | Failure modes cluster across candidates | Table 2 signature stats across seeds | All-pass rate, unique signatures | 68% all-pass, median unique sig = 1.0 | Validates clustering premise but shows limited scope for deduplication | Descriptive only, no causal link to performance |

### Research-Theme Gap Diagnosis
The core research question—whether aggregating execution feedback across candidates provides value beyond per-sample self-debugging—is directly tested (E1), but the experimental scope is too narrow to support a generalizable conclusion. The claim that "per-sample self-debugging may be sufficient for strong code generation models" is currently bounded to HumanEval+ and Qwen2.5-Coder-7B. Furthermore, the informational asymmetry between ESR's shared bank and Self-Debug's individualized feedback introduces a confounder that prevents clean causal attribution.

### Proposed Research Experiments (P0/P1/P2)
| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Expected Gain |
|--------------|------------|----------------|--------------------|---------|-------------------|-----------|---------------|
| C3 (per-sample sufficiency) | ESR null result holds across models/tasks | Evaluate ESR on MBPP and a weaker model (e.g., Llama-3-8B) | Self-Debug, Best-of-N on same setup | Pass@1, 95% CI | Consistent null result across settings | 1 GPU day | Generalizability of the null insight |
| C1 (aggregation mechanism) | Null result reflects mechanism limits, not baseline advantage | Matched-feedback ablation: expand ESR bank to match Self-Debug's per-candidate detail | Self-Debug with identical token budget | Pass@1, 95% CI | ESR closes gap or gap narrows significantly | 0.5 GPU day | Isolates mechanism vs asymmetry |
| C1 (exact matching limit) | Fuzzy signature matching captures near-miss patterns | Use Jaccard similarity on failing test sets instead of exact equality | Exact-match ESR | Pass@1, sig distribution | Higher pass@1 or more diverse sig clusters | 0.5 GPU day | Tests design trade-off assumption |

```text
ASCII Diagram — Experiment Upgrade Plan
Stage 1 (Text/Novelty Fix): Reposition ESR vs RSE, delay result preview
Stage 2 (Baseline Clarification): Quantify feedback asymmetry, add matched ablation
Stage 3 (Generalizability): MBPP/Llama-3 evaluation, fuzzy matching test
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board
| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|---------------------------|---------------------|---------------------|-----|------------|----------------------|
| C1 | ESR method: aggregate execution feedback via signature-based clustering | [1] | partially_overlapping | Core mechanism (recycling cross-sample failure info) overlaps with RSE [1]; novelty is the domain transfer to code using test-grounded signatures | High | Position as RSE adaptation for code; emphasize deterministic signatures as the design innovation |
| C2 | Rigorous evaluation with pre-registered rules and bootstrap CIs | — | supported | Statistical evaluation discipline (bootstrap CIs, pre-registered decision rules) is well-executed and defensible | High | None needed |
| C3 | Negative result: ESR does not significantly outperform Self-Debug | [2], [3] | partially_overlapping | Insight aligns with prior findings that self-repair gains are modest [2] and context-dependent [3]; novelty is the specific cross-sample aggregation test | Medium | Emphasize the specific hypothesis tested (cross-sample vs per-sample) rather than the result itself |

### (9B) Related-Work Taxonomy Matrix
| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|----------------|-------------|----------------------|--------------------|------------------------|--------------------|
| Test-Time Scaling | Parallel Sampling | Brown et al. (2024) | More samples = better coverage | ESR adds sequential Round 2 conditioned on failures | Low |
| Test-Time Scaling | Experience Recycling | [1] | Cross-sample info reuse reduces redundancy | ESR uses test-grounded sigs instead of semantic dedup | Medium (core overlap) |
| Feedback-Based Refinement | Per-Sample Self-Debug | [3] | Individualized feedback improves repair | ESR aggregates across samples | Low |
| Feedback-Based Refinement | Episodic Memory | Shinn et al. (2023) | High-level failure summaries guide future attempts | ESR uses deterministic sigs, not semantic summaries | Low |

### (9C) Head-to-Head Comparison Matrix
| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|-----------------|-------------|------------------------|-------------------|-------------------------|
| [1] | Math reasoning test-time scaling | Semantic experience bank for positive/negative recycling | Cross-sample failure recycling concept | RSE uses semantic dedup; ESR uses test-grounded exact signatures | Limits C1 novelty to domain adaptation |
| [3] | Code generation self-debugging | Per-candidate error feedback for iterative repair | Execution feedback for code improvement | Self-Debug is per-sample; ESR aggregates across samples | Provides strong baseline that ESR must beat |
| [2] | Code generation self-repair limits | Cost-adjusted analysis of self-repair efficacy | Self-repair benefits are modest and context-dependent | [2] analyzes cost-effectiveness; ESR tests aggregation hypothesis | Supports C3 framing; null result is consistent with prior |

**Contribution-level Novelty Conclusion:** C1 is `partially_overlapping` with RSE [1]; the core recycling concept is shared, and ESR's innovation is the use of deterministic execution signatures for code. C2 is `supported` as a methodological strength. C3 is `partially_overlapping` with prior findings [2][3] that self-repair/self-debug benefits are modest. The paper should reposition C1 as a domain adaptation and emphasize the specific hypothesis tested in C3.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Test-Time Scaling for Code (Root)
├── Branch 1: Parallel Scaling
│   └── Leaf 1.1: Best-of-N Sampling [Brown et al. 2024]
├── Branch 2: Feedback-Based Refinement
│   ├── Leaf 2.1: Per-Sample Self-Debug [3] (strong baseline)
│   ├── Leaf 2.2: Episodic Memory [Shinn et al. 2023]
│   └── Leaf 2.3: Self-Repair Analysis [2] (limits of repair)
└── Branch 3: Experience Recycling (Cross-Sample Aggregation)
    ├── Leaf 3.1: Semantic Dedup (Math) [1] RSE (overlaps C1)
    └── Leaf 3.2: Execution Signatures (Code) [This Paper] ESR
```

```text
ASCII Diagram — Paper Structure & Evidence Map
[Intro: Cross-sample feedback hypothesis]
    -> [Method: ESR with exact sig clustering]
        -> [Exp: HumanEval+ vs Self-Debug]
            -> [Result: No significant gain (CI includes 0)]
                -> [Gap: Single benchmark/model scope]
                -> [Gap: Baseline feedback asymmetry]
                -> [Fix: Reposition vs RSE, add MBPP/Llama eval, matched ablation]
```

```text
ASCII Diagram — Revision Strategy Roadmap
[P0: Reposition novelty vs RSE]
    -> [Evidence: RSE shares core recycling concept]
    -> [Fix: Explicit domain-adaptation framing]
[P0: Quantify baseline asymmetry]
    -> [Evidence: Self-Debug per-candidate info > ESR shared bank]
    -> [Fix: Add matched-feedback ablation]
[P1: Expand evaluation scope]
    -> [Evidence: Single benchmark limits generalizability]
    -> [Fix: Add MBPP or LiveCodeBench]
[P1: Connect variance to conclusion]
    -> [Evidence: ESR std=1.27 vs Self-Debug std=0.70]
    -> [Fix: Link to reliability argument]
```

## References
[1] Do Not Waste Your Rollouts: Recycling Search Experience for Efficient Test-Time Scaling 2601.21684

[2] Is Self-Repair a Silver Bullet for Code Generation? 2306.09896

[3] Teaching Large Language Models to Self-Debug 2304.05128

## Scores
Final Score: 5.5/10

This score reflects the paper's strengths in honest negative-result reporting, rigorous statistical evaluation, and clear methodology, offset by incremental novelty relative to RSE (Wang et al., 2026), single-benchmark/scope limitations, and an unresolved baseline feedback asymmetry. The research value lies in testing a widely assumed hypothesis and finding it does not hold under this setting, but the current evidence base is too narrow to support a generalizable conclusion.

Post-Revision Target: [6.5, 7.5]/10

This target assumes the authors successfully reposition the novelty claim as a domain adaptation of RSE, address the baseline asymmetry with a matched-feedback ablation or quantification analysis, and expand evaluation to at least one additional benchmark or model. With these fixes, the paper would present a defensible, well-bounded contribution with clear research value.