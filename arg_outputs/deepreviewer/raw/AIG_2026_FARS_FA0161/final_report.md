## Summary
This paper proposes Speaker-Attested Grounding (SAG), a minimal intervention that restricts the evidence corpus to user turns only during memory filtering in agent memory systems. The core insight is that when the full dialogue serves as evidence, assistant-originated statements can "self-verify," allowing false memories to pass verification despite lacking user attestation. SAG addresses this by filtering candidate memories against user-turn evidence only, while keeping extraction over the full dialogue.

Evaluated on the HaluMem-Medium benchmark (5-user subset, 343 sessions), SAG (relaxed) improves False Memory Resistance (FMR) by +11.94 percentage points (58.76% → 70.70%) with a recall tradeoff (−7.20pp). Per-source analysis claims that 100% of gains come from assistant-only interference memories. An ablation study isolates 47.5% of gains to the speaker restriction mechanism and 52.5% to reduced evidence length. The paper is well-structured, with clear problem formulation, clean single-variable design, and honest error analysis. The primary concerns are: (1) a numerical inconsistency in the F1 metric calculation, (2) a discrepancy between weighted subgroup gains and the overall +11.94pp FMR improvement, (3) the omission of MemIR (Jin et al., 2026) from related work, and (4) the limited evaluation scope (5-user subset) which constrains generalizability claims.

## Strengths
1. **Clear, well-motivated core insight:** The identification of "assistant-originated self-verification" as a source-monitoring failure in memory filtering is a memorable and precise conceptual contribution. The mechanism is clearly explained and directly motivates the SAG design.

2. **Clean single-variable experimental design:** By keeping the extraction model, filtering model, prompt templates, and temperature settings identical between SAG and Dialogue-Wide, the authors enable clean causal attribution of FMR improvements to the speaker restriction mechanism. This methodological discipline is commendable.

3. **Smart ablation study:** The Token-Matched baseline effectively isolates the speaker restriction effect (47.5%) from evidence length effects (52.5%), directly addressing the most plausible alternative hypothesis. This level of mechanistic isolation is often missing in empirical papers.

4. **Honest error analysis and bounded claims:** The error analysis correctly identifies "semantic overlap" as an irreducible error floor for speaker-based filtering alone. The distinction between extraction errors (87% of false negatives) and genuine recall losses (13%) provides useful diagnostic transparency.

5. **Well-structured narrative:** The paper follows a clear arc from problem → root cause → hypothesis → method → validation → ablation → error analysis. The writing is generally concise and the contribution claims are appropriately scoped.

## Weaknesses
1. **F1 Metric Calculation Inconsistency (Major):** The paper states that F1 is "the harmonic mean of Recall and FMR." However, calculating this for the Dialogue-Wide baseline yields $2 \times (53.14 \times 58.76) / (53.14 + 58.76) = 55.61$, yet Table 1 reports F1 = 66.63. This discrepancy is consistent across all methods (e.g., Extract-Only yields ~55.0 vs. reported 66.79). The F1 values appear to be calculated at the instance level or using a different formula, but this is not documented. Without clarification, readers cannot verify the aggregate performance claims.

2. **Numerical Discrepancy in Per-Source Analysis (Major):** The text claims "100% of SAG's overall FMR improvement comes from the assistant-only subgroup." A simple weighted calculation of subgroup gains suggests a discrepancy: assistant-only (70.9%) gains +4.6pp → weighted contribution ≈ +3.26pp; user-repeated (27.8%) gains 0pp → 0pp. Even if the "neither" category (1.4%) contributes maximally, the weighted sum is far short of the reported overall +11.94pp gain. Either the overall FMR is not a weighted average of subgroup FMRs, or the claim is misleading. This inconsistency undermines confidence in the central mechanism claim.

3. **Omission of Conceptually Adjacent Prior Work (Major):** Related work omits MemIR (Jin et al., 2026), which addresses "provenance-role collapse" by structuring memory into typed atoms that separate evidence from claims. While MemIR operates at a different level (structural memory representation vs. speaker-level filtering), both approaches restrict evidence scope to prevent contamination. Acknowledging and differentiating from such work strengthens novelty positioning.

4. **Limited Evaluation Scope (Minor):** Evaluating on a 5-user subset (343 sessions) limits the generalizability of results. While the volume is reasonable, the diversity of user personas, domains, and conversation styles is constrained. The paper does not discuss how SAG might perform across different dialogue types, longer contexts (HaluMem-Long), or different LLM backends.

5. **Missing Error Analysis Sample Size (Minor):** The claim that "100% of false positives exhibit semantic overlap" is strong but does not report the manual inspection sample size. If based on a small sample, the 100% figure may lack statistical reliability.

## Key Issues
1. **F1 Metric Verification (Severity: Major, Validity Risk: High):** The reported F1 values in Table 1 are inconsistent with the stated definition ("harmonic mean of Recall and FMR"). For the Dialogue-Wide baseline, the aggregate harmonic mean is ~55.6, while the table reports 66.63. This gap is consistent across all methods, suggesting F1 is likely computed instance-level. However, this is not stated. **Impact:** Readers cannot reproduce the F1 scores or trust the aggregate performance narrative. **Fix:** Explicitly document the F1 calculation method (e.g., "F1 is computed instance-level across all memory points, then averaged") or correct the reported values.

2. **Per-Source Gain Arithmetic Closure (Severity: Major, Validity Risk: High):** The central claim that "100% of FMR gains come from assistant-only interference" is undermined by a numerical gap. Weighted subgroup gains (+4.6pp on 70.9% of data ≈ +3.26pp overall) do not sum to the reported overall +11.94pp improvement. **Impact:** If this arithmetic does not close, the "precisely targeted" mechanism claim loses its quantitative foundation. **Fix:** Provide a detailed breakdown showing how subgroup FMR gains aggregate to the overall FMR gain, or clarify if the +11.94pp is measured differently from the subgroup deltas.

3. **Missing Related Work: Provenance-Aware Memory (Severity: Major, Novelty Risk: Medium):** The related work omits MemIR (Jin et al., 2026), which mitigates "provenance-role collapse" by structuring memory into typed atoms that restrict factual authorization. While MemIR is structural (typed atoms) and SAG is operational (speaker filtering), they address the same root problem: evidence contamination from non-user sources. **Impact:** Omission weakens the novelty positioning and may lead reviewers to question whether the authors surveyed the field adequately. **Fix:** Add MemIR to Section 2.2 with a one-sentence differentiation explaining how SAG's speaker-level filtering complements rather than duplicates structural provenance tracking.

4. **Evaluation Scope Boundaries (Severity: Minor, Generalizability Risk: Medium):** Results are based on a 5-user subset (343 sessions) of HaluMem-Medium. The diversity of user personas, topics, and dialogue styles is limited. **Impact:** Limits the external validity of the "+11.94pp improvement" claim. **Fix:** Bound the conclusion explicitly to the tested setting and discuss (even briefly) what additional validation (e.g., HaluMem-Long, other LLM backends) would strengthen the claim.

## Actionable Suggestions
1. **Clarify F1 Calculation Method (Must):** Add one sentence in Section 4.1 (Experimental Setup) explicitly stating how F1 is computed. If it is instance-level, write: "F1 is computed as the instance-level harmonic mean of Recall and FMR across all evaluation memory points, then averaged across sessions." This allows readers to reproduce the Table 1 values.

2. **Verify and Document Subgroup Gain Aggregation (Must):** In Section 4.3, provide a compact appendix table or inline breakdown showing how the assistant-only (+4.6pp), user-repeated (0pp), and neither (unknown) subgroup FMRs mathematically aggregate to the overall +11.94pp gain. If overall FMR is instance-level and the "100% of gains" refers to the count of rejected instances rather than the weighted percentage-point delta, explicitly state this distinction to resolve the numerical gap.

3. **Add MemIR to Related Work (Must):** In Section 2.2, add a sentence acknowledging provenance-aware memory systems: "More recently, MemIR (Jin et al., 2026) mitigates provenance-role collapse by structuring memory into typed atoms that separate evidence from claims. Our work complements this structural approach with a simpler, speaker-level intervention that requires no new memory representation formats."

4. **Bound Conclusion to Tested Scope (Must):** In the Conclusion (Section 5), add a scope qualifier: "Our results demonstrate improved FMR on the evaluated HaluMem-Medium subset; broader claims require validation on larger, more diverse user corpora and longer-context benchmarks."

5. **Report Error Analysis Sample Size (Nice-to-have):** In Section 4.5, specify the number of false positives manually inspected when stating "100% exhibit semantic overlap." E.g., "Among the [N] false positives manually reviewed..."

6. **Clarify Ablation Variant and Truncation Strategy (Nice-to-have):** In Section 4.4, specify that the 47.5%/52.5% split refers to the SAG (strict) variant relative to Dialogue-Wide. Briefly describe how the Token-Matched baseline truncates the dialogue (e.g., "preserving the first N tokens chronologically").

## Storyline Options + Writing Outlines
### Abstract Outline (Complete 4-5 Sentence Plan)
*   **S1 (Problem & Domain):** Agent memory systems extract and store user information across conversations, but are susceptible to false memory storage when assistant-generated content enters persistent memory without user confirmation.
*   **S2 (Significance/Challenge):** Existing systems use the full dialogue as verification evidence, allowing assistant-originated statements to "self-verify" and pass filtering—a source-monitoring failure we term assistant-originated self-verification.
*   **S3 (Method):** We propose Speaker-Attested Grounding (SAG), a minimal intervention that restricts the filtering evidence corpus to user turns only while maintaining full-dialogue extraction.
*   **S4 (Key Result):** On the HaluMem-Medium benchmark (5-user subset), SAG improves False Memory Resistance by +11.94 percentage points with a recall tradeoff (−7.20pp).
*   **S5 (Mechanism Attribution):** Per-source analysis and ablation studies confirm that gains are precisely targeted at assistant-only interference memories, isolating 47.5% of the improvement to the speaker restriction mechanism itself.

### Introduction Outline (Paragraph-by-Paragraph Plan)
*   **P1 (Big Picture & Bridge):** Agent memory systems enable long-term personalization by storing user information, yet they are primarily optimized for coverage rather than source verification. *Transition:* Add a bridging half-sentence foreshadowing the reliability gap to flow into the specific problem.
*   **P2 (Concrete Gap & Problem Definition):** These systems suffer from false memory storage, specifically "interference memories" (operational definition needed: facts mentioned by the assistant but never confirmed by the user). Cite HaluMem (Chen et al., 2026) as the benchmark revealing this frequency.
*   **P3 (Root Cause Insight):** Identify assistant-originated self-verification as the root cause. When the full dialogue is evidence, assistant statements support themselves. *Transition:* Frame this as a "source-monitoring failure" to ground it in cognitive psychology and strengthen the scientific framing.
*   **P4 (Hypothesis & Solution):** Restricting evidence to user turns only targets assistant-originated false memories while preserving user-attested memories. Introduce Speaker-Attested Grounding (SAG) as a single-variable intervention (keeping model, prompts, and temperature constant to ensure causal attribution).
*   **P5 (Contributions):** List the four contributions with precise scope qualifiers (e.g., "+11.94pp on HaluMem-Medium 5-user subset," "47.5% of the SAG-strict gain").

## Priority Revision Plan
### P0: Critical Validity & Evidence Repairs (Must complete)
1.  **Fix F1 Metric Documentation:** Explicitly define the F1 calculation method (instance-level vs. aggregate) in Section 4.1. *Effort: Low (1 sentence).* *Impact: Resolves major factual inconsistency.*
2.  **Close Per-Source Gain Arithmetic:** Provide an appendix table or inline explanation showing how the weighted subgroup FMR gains sum to the overall +11.94pp, or clarify the aggregation method. *Effort: Medium (requires data audit).* *Impact: Validates the core mechanism claim.*
3.  **Add MemIR to Related Work:** Acknowledge MemIR (Jin et al., 2026) in Section 2.2 and differentiate SAG's speaker-level filtering from structural memory typing. *Effort: Low (1-2 sentences).* *Impact: Strengthens novelty positioning.*

### P1: High-Value Clarifications (Should complete)
4.  **Scope-Bound Abstract & Conclusion:** Add the "5-user subset, 343 sessions" scope qualifier to the Abstract and explicitly bound the conclusion to the tested setting. *Effort: Low.* *Impact: Improves scientific objectivity and prevents overclaiming.*
5.  **Clarify Ablation Variant:** Specify that the 47.5%/52.5% split refers to the SAG (strict) variant and describe the Token-Matched truncation strategy (e.g., chronological first-N tokens). *Effort: Low.* *Impact: Ensures reproducibility of the ablation study.*

### P2: Polish & Robustness (Nice-to-have)
6.  **Report Error Inspection Sample Size:** Add the number of manually inspected false positives in Section 4.5. *Effort: Low.*
7.  **Fix LaTeX Notation Artifacts:** Correct the double-brace syntax error in the role set definition (`$r_i \in \{\text{user}, \text{assistant}\}$`) in Section 3.1. *Effort: Low.*

```text
ASCII Diagram — Revision Strategy Roadmap
[F1 Discrepancy] -> [Document instance-level F1 in Sec 4.1] -> [Trust in metrics restored]
[Subgroup Gap] -> [Audit data + add appendix table] -> [Mechanism claim validated]
[Related Work] -> [Add MemIR + differentiate] -> [Novelty claim robust]
[Scope Bounds] -> [Add 5-user qualifier to Abstract/Conclusion] -> [Objectivity improved]
```

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| Exp 1 | SAG (user-only evidence) improves False Memory Resistance compared to dialogue-wide filtering. | HaluMem-Medium (5-user, 343 sessions). Extract-Only, Dialogue-Wide vs SAG (relaxed/strict). GPT-4o-mini. | Recall, FMR, F1, Avg Memories | SAG (relaxed): FMR 70.70% (+11.94pp). SAG (strict): 74.42% (+15.66pp). | SAG improves FMR | 5-user scope; F1 metric definition inconsistency |
| Exp 2 | SAG gains specifically target assistant-only interference memories. | Per-source breakdown of 645 interference memories (assistant-only, user-repeated, neither). | FMR per source type | SAG gains +4.6pp on assistant-only; 0pp on user-repeated. | Targeted mechanism validated | Numerical gap between weighted subgroup gains and overall +11.94pp delta |
| Exp 3 | Speaker restriction, not just shorter evidence length, drives FMR gains. | Token-Matched baseline (truncated dialogue-wide) vs Dialogue-Wide vs SAG (strict). | Recall, FMR, ΔFMR | Token-Matched captures 52.5% of gain; SAG captures remaining 47.5% with better recall. | Mechanism isolated | Unclear which SAG variant the 47.5% refers to; truncation strategy not fully specified |

### (b) Research-Theme Gap Diagnosis
The core research value of this paper lies in **new knowledge** (the concept of assistant-originated self-verification as a source-monitoring failure) and **reproducibility** (a simple, single-variable intervention). The current limitation is the **impact on practice/understanding**: because the evaluation is confined to a 5-user subset of one benchmark (HaluMem-Medium) and one LLM backend (GPT-4o-mini), it is unclear whether speaker-attested grounding is a universally robust strategy for memory systems or an artifact of specific dialogue dynamics. Additionally, the recall tradeoff (−7.20pp) is significant; the paper does not explore whether the rejected "false negatives" are truly less valuable to the user.

### (c) Proposed Research Experiments

1. **Exp P1-1: Backend Generalization (Priority: P1)**
   - *Target Claim:* SAG provides robust FMR improvements across different language models.
   - *Hypothesis:* The speaker-restriction mechanism is model-agnostic.
   - *Minimal Design:* Re-run Exp 1 using an open-weight model (e.g., Llama 3.1 70B or Mistral Large) and a different closed model (e.g., Claude 3.5 Sonnet) as the extraction/filtering backend.
   - *Controls/Baselines:* Same Dialogue-Wide and Extract-Only baselines.
   - *Metrics:* FMR, Recall, F1.
   - *Success Criterion:* FMR improves by ≥10pp across all backends.
   - *Estimated Cost:* Low.
   - *Expected Gain:* Validates generalizability of the core mechanism beyond GPT-4o-mini.

2. **Exp P1-2: HaluMem-Long Evaluation (Priority: P1)**
   - *Target Claim:* SAG scales effectively to longer context lengths.
   - *Hypothesis:* Restricting evidence corpus becomes even more beneficial as context grows (since noise scales with assistant turns).
   - *Minimal Design:* Run Exp 1 on HaluMem-Long (2.6k turns, 1M+ tokens).
   - *Controls/Baselines:* Dialogue-Wide.
   - *Metrics:* FMR, Recall, Average tokens per evidence corpus.
   - *Success Criterion:* FMR improvement is maintained or increases (+12pp or more).
   - *Estimated Cost:* Low (computationally heavier but same pipeline).
   - *Expected Gain:* Demonstrates that SAG is particularly valuable for long-horizon memory systems.

3. **Exp P2-1: User-Perceived Value of Recall Tradeoff (Priority: P2)**
   - *Target Claim:* The memories rejected by SAG (false negatives) are of lower practical value to the user.
   - *Hypothesis:* User-implied memories (13% of false negatives) are less critical than explicitly stated ones.
   - *Minimal Design:* Random sample of 50 rejected memories evaluated by human annotators on a 1-5 relevance scale.
   - *Controls:* Compare with 50 correctly retained memories.
   - *Metrics:* Average relevance score.
   - *Success Criterion:* Rejected memories have significantly lower relevance scores (e.g., <3.0).
   - *Expected Gain:* Justifies the recall tradeoff by showing SAG acts as a quality filter.

### (d) Traceability Rule
Exp P1-1 and P1-2 map directly to the **generalizability limitation** of the single-user, single-model setup. Exp P2-1 maps to the **recall tradeoff issue**, providing justification for the FMR-Recall balance.

```text
ASCII Diagram — Experiment Upgrade Plan
[Current: P0 Data Fixes (F1 & Subgroup arithmetic)]
      -> [P1 Generalization (Exp P1-1: Llama/Claude)]
      -> [P1 Scale (Exp P1-2: HaluMem-Long)]
      -> [P2 Value Justification (Exp P2-1: Human relevance rating)]
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Identify assistant-originated self-verification as a root cause of false memory storage. | [1], [2] | partially_overlapping | MemIR [2] addresses "provenance-role collapse" via structured typing, which is conceptually adjacent (both prevent non-user evidence contamination). The framing of "assistant self-verification" as a source-monitoring failure is novel. | High | Differentiate from structural provenance tracking in related work. |
| C2 | Propose Speaker-Attested Grounding (SAG): restrict filtering evidence to user turns only. | [1], [2] | supported | No prior method implements speaker-role filtering at the evidence corpus level. MemIR [2] uses memory atoms, not speaker turns. SAG is a distinct, simpler intervention. | High | None; claim is well-supported. |
| C3 | Ablation isolating speaker restriction (47.5%) from evidence length effects (52.5%). | — | supported | The Token-Matched baseline is a novel diagnostic control for this setting. | Medium | None; claim is internally validated. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| **Root: Agent Memory Reliability** | | | | | |
| ├── Branch 1: Structural Memory Representation | | | | | |
| │   ├── Leaf 1.1: Typed Atom Memory | [2] | Memory can be structured into evidence/claim/cue atoms. | SAG operates at the filtering input level, not memory structure. | Low |
| │   └── Leaf 1.2: Heterogeneous Type Isolation | [3] | Different memory types should not contaminate each other. | SAG isolates by speaker, not by functional memory type. | Low |
| ├── Branch 2: Evidence & Grounding | | | | | |
| │   ├── Leaf 2.1: RAG Fact Verification | [4] | LLM outputs can be checked against grounding docs. | SAG restricts evidence source to user turns; MiniCheck uses arbitrary documents. | Low |
| │   └── Leaf 2.2: Consensus Validation | [5] | Multiple validators reduce false positives. | SAG is single-pass; A-MemGuard is multi-agent consensus. | Low |
| └── Branch 3: Benchmark & Diagnosis | | | | | |
|     └── Leaf 3.1: Operation-Level Hallucination Benchmarks | [1] | Memory operations can be evaluated stage-wise. | HaluMem provides the evaluation protocol used by SAG. | None (SAG builds on this benchmark) |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] HaluMem (Chen et al., 2026) | Memory hallucination in agents; operation-level evaluation. | Benchmark with interference memory points. | Provides the HaluMem-Medium dataset and FMR metric used by SAG. | HaluMem is a benchmark; SAG is a method. | Neutral: SAG uses the benchmark but does not overlap methodologically. |
| [2] MemIR (Jin et al., 2026) | Provenance-role collapse in long-term agents. | Typed memory atoms separating evidence, cues, claims. | Both prevent non-user evidence from contaminating memory verification. | MemIR uses structural typing; SAG uses speaker-role filtering. | Low: SAG is simpler and complementary, not redundant. |
| [3] MemGuard (Ha et al., 2026) | Heterogeneous memory contamination. | Type-aware memory framework preserving functional boundaries. | Both isolate memory sources to prevent contamination. | MemGuard isolates by memory function; SAG by speaker role. | Low: Different isolation axis. |
| [5] A-MemGuard (Wei et al., 2025) | Adversarial memory manipulation. | Consensus-based validation + dual-memory structures. | Both filter false memories before storage. | A-MemGuard targets attacks; SAG targets organic false memories. | Low: Different threat model. |
| [4] MiniCheck (Tang et al., 2024) | Efficient fact-checking against grounding docs. | Small-model verification of LLM claims. | Both use evidence-based grounding. | MiniCheck uses arbitrary grounding docs; SAG uses user turns. | Low: Different evidence source. |

### Contribution-level Novelty Conclusion

C1 (identifying assistant self-verification) is **partially_overlapping** because MemIR [2] addresses a similar provenance contamination problem at the structural level. The "assistant self-verification" framing is novel, but the broader problem of source monitoring in memory is not unique to this paper. C2 (SAG method) is **supported** as no prior work implements speaker-role filtering at the evidence corpus level. C3 (ablation isolating speaker vs. length effects) is **supported** as a novel diagnostic experiment. Overall, the paper makes a legitimate, distinct contribution via a simple operational intervention, though it should acknowledge and differentiate from structural provenance approaches like MemIR.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Agent Memory Reliability (Root)
├── Structural Memory Representation
│   ├── Typed Atom Memory [2] (MemIR): structural source monitoring
│   └── Type Isolation [3] (MemGuard): functional boundary preservation
│       -> Manuscript position: SAG complements these with operational speaker filtering
├── Evidence & Grounding
│   ├── RAG Verification [4] (MiniCheck): arbitrary document grounding
│   └── Consensus Validation [5] (A-MemGuard): multi-agent attack defense
│       -> Manuscript position: SAG uses user turns as the sole grounding source
└── Benchmark & Diagnosis
    └── Operation-Level Evaluation [1] (HaluMem): stage-wise hallucination metrics
        -> Manuscript position: SAG is evaluated on this benchmark
```

## References
[1] HaluMem: Evaluating Hallucinations in Memory Systems of Agents 2511.03506

[2] Mitigating Provenance-Role Collapse in Long-Term Agents via Typed Memory Representation 2605.25869

[3] MemGuard: Preventing Memory Contamination in Long-Term Memory-Augmented Large Language Models 2605.28009

[4] Minicheck: Efficient fact-checking of llms on grounding documents (Tang et al., 2024) — no arXiv ID available from paper_search

[5] A-memguard: A proactive defense framework for llm-based agent memory 2510.02373

## Scores
**Final Score:** 6/10

**Post-Revision Target:** [7, 8]/10

**Rationale:**
This paper presents a well-motivated, conceptually clear, and methodologically clean intervention for a recognized problem in agent memory systems. The identification of "assistant-originated self-verification" as a source-monitoring failure provides a sharp, memorable framing, and SAG (Speaker-Attested Grounding) is an elegant, minimal solution that is validated with a smart single-variable design and a strong ablation study.

The score is tempered by major factual inconsistencies—specifically, the F1 metric calculation does not match the stated definition, and the per-source gain arithmetic does not close, which undermines confidence in the core "+11.94pp" claim. Additionally, the evaluation is limited to a 5-user subset, and the related work omits conceptually adjacent provenance-tracking methods like MemIR.

These issues are highly fixable (clarifying metrics, adding one related work citation, bounding the scope) and do not invalidate the core research value. Once these repairs are made, the paper should easily reach a 7-8/10, representing a solid, defensible contribution to the field of reliable agent memory.