## Summary
This paper proposes Citation-Consistent Voting (CCV), a training-free inference-time method for improving RAG permutation robustness. The core insight is that correct answers tend to cite the same underlying document across different document orderings, while incorrect answers exhibit higher citation variance. CCV prompts the generator to produce structured outputs (answer, document index, supporting quote), maps citations to permutation-invariant document IDs, and selects answers with the highest citation-consistency score. Evaluated on NaturalQuestions with Qwen3-8B and Contriever retrieval, CCV achieves 46.37% SubEM at K=20 permutations, improving upon majority voting by +0.19 points.

**Key strengths:** The method is conceptually simple, training-free, and compatible with any RAG system that produces structured citations. The diagnostic analysis confirms that citation consistency correlates with answer correctness. The K-scaling behavior provides theoretical support for the aggregation mechanism.

**Key weaknesses:** The absolute performance of CCV (46.37% SubEM) is below standard Vanilla RAG (48.98% SubEM), meaning the method does not improve upon the strongest baseline in absolute terms. The Related Work omits explicit discussion of Mixture-of-Intervention (MOI), a key inference-time prior that also uses multi-permutation inference scaling. The citation hallucination risk is not discussed, despite being a known failure mode of LLM-generated citations. The diagnostic analysis reports statistical significance but omits effect size, leaving the practical discriminative power of the citation signal unclear.

## Strengths
1. **Conceptual simplicity and practicality:** CCV is a training-free, inference-time method that requires no access to model weights, no fine-tuning data, and no architectural modifications. It can be applied to any RAG system that produces structured citations, making it broadly applicable to existing deployment pipelines.
2. **Clear mechanism insight:** The paper identifies a novel aggregation signal—document-ID citation consistency across permutations—that complements traditional answer-frequency voting. The diagnostic analysis provides empirical support for the claim that citation agreement correlates with answer correctness ($p = 1.14 \times 10^{-5}$), validating the core hypothesis.
3. **K-scaling behavior:** The monotonic improvement of CCV over majority voting as K increases (from -0.01 at K=5 to +0.19 at K=20) provides theoretical support for the aggregation mechanism. This scaling suggests that the document-ID voting mechanism benefits from larger sample sizes to identify consistent citation patterns.
4. **Transparent limitations acknowledgment:** The authors honestly acknowledge the modest absolute improvement, single-dataset evaluation, and computational cost trade-off. This candor improves the paper's credibility and sets a clear agenda for future work.

## Weaknesses
1. **Performance gap to strongest baseline:** CCV achieves 46.37% SubEM at K=20, which is +0.19 points above majority voting under the JSON citation format. However, standard Vanilla RAG (without JSON constraints) achieves 48.98% SubEM. This means CCV is still 2.61 points below the unconstrained baseline, raising questions about its practical utility. The framing consistently compares CCV to the weaker majority-voting baseline without acknowledging the stronger standard RAG performance ceiling.

2. **Incomplete positioning against key prior work:** The Related Work cites Mixture-of-Intervention (MOI) by Lee et al. (2024) but never explicitly differentiates CCV from MOI. Both methods use multi-permutation inference scaling to mitigate position bias. Without clear differentiation, the novelty of CCV relative to MOI is unclear. Stable-RAG (Zhang et al., 2026) is discussed but the comparison focuses on training requirements rather than mechanism differences.

3. **Citation hallucination risk unaddressed:** The method assumes that LLMs produce accurate document citations, but prior work (Buchmann et al., 2025; Chen et al., 2026) demonstrates that LLMs frequently hallucinate citations or produce incorrect document indices. If the model cites the wrong document for a correct answer, or generates spurious citations, the aggregation signal is noisy. The paper does not discuss this known failure mode or how the method is robust to it.

4. **Diagnostic analysis lacks effect size:** The diagnostic analysis reports a statistically significant difference between correct (3.04) and incorrect (2.85) mean agreement scores ($p = 1.14 \times 10^{-5}$). However, the effect size is very small (difference of 0.19 on a scale up to K=20), which may be statistically significant due to the large sample size but practically weak. Without reporting effect size, the discriminative power of the citation signal is unclear.

5. **Limited evaluation scope:** Evaluation is restricted to a single dataset (NaturalQuestions), a single model (Qwen3-8B), and a single retriever (Contriever). NaturalQuestions is a simple single-hop QA dataset; the method's effectiveness on multi-hop reasoning tasks (e.g., HotpotQA) or conversational QA is unknown. Cross-model generalization is also untested.

## Key Issues
1. **[Major] Performance framing risk (Page 1 - Abstract, Page 5 - Main Results):** The paper frames the contribution as "+0.19 SubEM improvement over majority voting," but standard Vanilla RAG achieves 48.98% SubEM, which is higher than CCV's 46.37%. This means the method does not improve upon the strongest reported baseline in absolute terms. The comparison baseline should be explicitly bounded, and the JSON-citation format's performance ceiling should be acknowledged. If unchanged, reviewers may perceive the contribution as overstated or incremental.

2. **[Major] Missing differentiation from Mixture-of-Intervention (MOI) (Page 2 - Related Work):** MOI (Lee et al., 2024) is a key inference-time prior that also uses multi-permutation inference scaling to mitigate position bias. The Related Work cites MOI but never differentiates CCV's mechanism from MOI's utility-modeling approach. Without this comparison, the novelty positioning is incomplete, and readers cannot assess the residual novelty of CCV. This should be addressed by adding an explicit mechanism-level comparison in Related Work or the Introduction.

3. **[Minor] Citation hallucination robustness gap (Page 3 - Method 3.2):** The method assumes models produce accurate document citations, but LLMs frequently hallucinate citations (Buchmann et al., 2025; Chen et al., 2026). The paper does not discuss this known failure mode or how the aggregation mechanism handles noisy citation signals. Adding a brief discussion of citation hallucination risk and how multi-permutation voting naturally mitigates this noise would strengthen the robustness argument.

4. **[Minor] Missing effect size in diagnostic analysis (Page 6 - Diagnostic Analysis):** The diagnostic analysis reports statistical significance ($p = 1.14 \times 10^{-5}$) but omits effect size. The small mean difference (3.04 vs. 2.85) may be statistically significant due to the large sample but practically weak. Reporting effect size (e.g., Cohen's h or Cliff's delta) would provide a more complete picture of the citation signal's discriminative power.

5. **[Minor] Limited evaluation scope (Page 6 - Conclusion):** Evaluation on a single dataset (NaturalQuestions), single model (Qwen3-8B), and single retriever (Contriever) limits the generalizability of the claims. Expanding to multi-hop QA datasets (e.g., HotpotQA) and cross-model evaluation would strengthen the external validity of the findings.

## Actionable Suggestions
1. **Bound the performance claim (Must, Page 1 & Page 5):**
   * **Action:** In the Abstract and Main Results, explicitly state that CCV's +0.19 SubEM gain is relative to majority voting under the *same JSON citation prompt*. Add a sentence acknowledging that standard Vanilla RAG (unconstrained prompt) achieves higher SubEM (48.98%), indicating that the citation format imposes a performance ceiling.
   * **Expected impact:** Prevents overclaim perception and frames the contribution accurately as an improvement within the constrained citation format setting.

2. **Differentiate from Mixture-of-Intervention (MOI) (Must, Page 2):**
   * **Action:** In Related Work (Section 2.3 or 2.4), add a paragraph explicitly contrasting CCV with MOI (Lee et al., 2024). For example: "While MOI models passage utility through explicit debiasing equations using multiple forward passes, our approach leverages the inherent citation structure of RAG outputs, requiring no white-box access to model internals."
   * **Expected impact:** Clarifies the residual novelty of CCV and strengthens the research positioning against the closest inference-time prior.

3. **Discuss citation hallucination robustness (Nice-to-have, Page 3):**
   * **Action:** In Section 3.2 or 3.4, add 1-2 sentences acknowledging that LLMs can hallucinate citations (Buchmann et al., 2025; Chen et al., 2026) and explain how the multi-permutation voting mechanism acts as an error-correction filter for noisy citation signals.
   * **Expected impact:** Demonstrates awareness of known failure modes and provides a mechanistic argument for robustness.

4. **Report effect size in diagnostic analysis (Nice-to-have, Page 6):**
   * **Action:** Add the effect size metric (e.g., Cohen's h ≈ 0.03 or Cliff's delta) alongside the p-value in Section 4.5. Interpret the practical significance: a modest effect size suggests that citation consistency serves as a complementary signal to answer frequency.
   * **Expected impact:** Provides a more complete and objective picture of the citation signal's discriminative power.

5. **Specify tie-breaking rule (Nice-to-have, Page 3-4):**
   * **Action:** In Section 3.3, specify what happens when two different answers have the same citation-consistency score AND the same raw frequency. A simple deterministic fallback (e.g., random selection or confidence-based scoring) should be stated.
   * **Expected impact:** Improves method reproducibility and completeness.

## Storyline Options + Writing Outlines
### Abstract Outline
The abstract should follow a compact 5-sentence logic: Problem -> Significance -> Prior Gap -> Method -> Bounded Result.
* **S1 (Problem):** RAG systems are sensitive to the ordering of retrieved documents, with language models exhibiting position bias that causes inconsistent outputs across different document permutations.
* **S2 (Significance):** This permutation sensitivity undermines the reliability of RAG in practical deployments, where the retrieval order is often arbitrary.
* **S3 (Prior Gap):** While existing inference-time methods (e.g., majority voting) aggregate responses based on answer frequency, they ignore the rich citation structure that modern RAG systems produce.
* **S4 (Method):** We propose Citation-Consistent Voting (CCV), a training-free method that maps citations to permutation-invariant document identifiers and selects answers based on document-ID agreement rather than answer frequency.
* **S5 (Result & Bounded Implication):** On NaturalQuestions with Qwen3-8B and Contriever retrieval, CCV outperforms majority voting by +0.19 SubEM at K=20 permutations under the same JSON citation format. Diagnostic analysis confirms that citation agreement correlates significantly with answer correctness ($p = 1.14 \times 10^{-5}$), and the improvement scales monotonically with K.

### Introduction Outline
The introduction should follow a clear 4-paragraph arc: Problem Context -> Prior Work & Gap -> Core Insight -> Method & Contributions.
* **P1 (Problem Context & Motivation):** 
  * *Role:* Establish the critical vulnerability of RAG systems (permutation sensitivity).
  * *Target Claim:* Position bias affects both long-context ("lost in the middle") and short-context retrieval scenarios, directly impacting factual accuracy.
  * *Transition Logic:* Move from the general phenomenon to the specific regime of Top-5 short-context retrieval, which is common in practice.
  * *Required Evidence:* Cite Liu et al. (2023) for long-context and Zhang et al. (2026) for short-context permutation sensitivity.
* **P2 (Prior Work & Gap):** 
  * *Role:* Categorize and critique existing solutions.
  * *Target Claim:* Training-based methods (e.g., Stable-RAG) require access to model weights, while inference-time methods (e.g., MoA, MOI) rely on answer frequency or explicit utility modeling, overlooking the inherent citation structure.
  * *Transition Logic:* Identify the underutilized signal: when models cite evidence, the document citation provides a more stable signal than the answer text itself.
  * *Required Evidence:* Cite Stable-RAG, MoA, and explicitly MOI (Lee et al., 2024) to show what is missing (citation-level aggregation).
* **P3 (Core Insight):** 
  * *Role:* Present the novel observation motivating the method.
  * *Target Claim:* Correct answers tend to cite the same underlying document across different permutations, while incorrect answers exhibit higher citation variance.
  * *Transition Logic:* This observation motivates a new aggregation strategy that votes on document-ID agreement.
  * *Required Evidence:* Preview the diagnostic finding (correlation between citation consistency and answer correctness).
* **P4 (Method & Contributions):** 
  * *Role:* Introduce CCV and list the concrete contributions.
  * *Target Claim:* CCV is a training-free, permutation-robust aggregation method that exploits citation structure.
  * *Transition Logic:* Clearly list 3 contributions: (1) the CCV method itself, (2) empirical demonstration of K-scaling and SubEM improvement over majority voting, (3) validation of citation consistency as a meaningful quality signal.
  * *Required Evidence:* Reference the main result (+0.19 SubEM at K=20) and the diagnostic p-value.

## Priority Revision Plan
| Priority | Action | Location | Effort | Expected Impact |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | **Bound performance claim:** Add sentence in Abstract and Main Results acknowledging that CCV (46.37% SubEM) is relative to majority voting under the JSON citation format, and that standard Vanilla RAG achieves higher SubEM (48.98%). Frame the +0.19 gain as an improvement within the constrained citation setting. | Page 1 (Abstract), Page 5 (Section 4.2) | Low (1-2 sentences) | High: Prevents overclaim perception and aligns claims with available evidence. |
| **P0** | **Differentiate from MOI:** Add explicit comparison with Mixture-of-Intervention (Lee et al., 2024) in Related Work. Contrast CCV's citation-level aggregation with MOI's utility-modeling approach. | Page 2 (Section 2.3 or 2.4) | Low-Medium (1 paragraph) | High: Resolves the most significant novelty-positioning gap. |
| **P1** | **Clarify short-context scope:** In Introduction P1, explicitly bound the permutation sensitivity problem to short-context retrieval (Top-5) and explain why this regime is practically important for deployment. | Page 1 (Section 1, P1) | Low (1 sentence) | Medium: Improves motivation clarity and problem-solution alignment. |
| **P1** | **Discuss citation hallucination risk:** Acknowledge known LLM citation failure modes (Buchmann et al., 2025; Chen et al., 2026) and explain how multi-permutation voting naturally mitigates noisy citation signals. | Page 3 (Section 3.2 or 3.4) | Low (1-2 sentences) | Medium: Strengthens robustness argumentation and demonstrates literature awareness. |
| **P1** | **Report diagnostic effect size:** Add effect size metric (e.g., Cohen's h or Cliff's delta) alongside the p-value in Section 4.5, and interpret its practical significance. | Page 6 (Section 4.5) | Low (1 sentence) | Medium: Provides a complete picture of the citation signal's discriminative power. |
| **P2** | **Specify tie-breaking fallback:** Clarify the deterministic tie-breaking rule in Section 3.3 when citation-consistency scores and raw frequencies are identical. | Page 3-4 (Section 3.3) | Very Low (1 sentence) | Low: Improves method completeness and reproducibility. |
| **P2** | **Expand limitations scope:** In the Conclusion, specify that NaturalQuestions is a single-hop dataset and that multi-hop/conversational generalization remains untested. | Page 6 (Section 5) | Low (1-2 sentences) | Low-Medium: Improves external validity transparency. |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory
| Exp ID | Objective/Hypothesis | Setup (Data/Split/Protocol/Baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| E1: Main Results | CCV improves over MoA under JSON citation format | NaturalQuestions (3610 test), Qwen3-8B, Contriever Top-5. Baselines: Vanilla (Std/JSON), MoA (K=5, K=20) | SubEM, F1 | CCV achieves 46.37% SubEM (+0.19 over MoA K=20) | CCV outperforms majority voting | Standard Vanilla (48.98%) outperforms CCV; lacks variance for K=20 |
| E2: K-Scaling | CCV gains scale monotonically with K | K $\in \{5, 10, 15, 20\}$. Compares MoA vs CCV SubEM | SubEM, $\Delta$ | Gains from -0.01 (K=5) to +0.19 (K=20) | Mechanism benefits from larger samples | K=5 provides no benefit; practical K-threshold is ~10 |
| E3: Quote Ablation | Relaxing quote constraint improves coverage/performance | K=5. With vs Without verbatim quote match | SubEM, Citation Path (%), Avg Valid Runs | No-quote achieves 46.37% (vs 45.73% with quote), 99.70% coverage | Doc-ID agreement is more important than strict quotes | Does not explore middle-ground (e.g., semantic similarity of quotes) |
| E4: Diagnostics | Citation agreement correlates with answer correctness | Correct vs Incorrect predictions across test set | Mean agreement score, Mann-Whitney p-value | Correct (3.04) > Incorrect (2.85), p = 1.14e-5 | Citation consistency is a quality signal | Effect size (0.19 diff) is small; practical discriminative power unclear |

### (b) Research-Theme Gap Diagnosis
The current experimental validation strongly supports the *mechanism insight* (citation consistency correlates with correctness and improves over majority voting at K=20). However, the *research value* and *external validity* are constrained by the narrow evaluation scope. The single-dataset (NaturalQuestions), single-model (Qwen3-8B), and single-retriever (Contriever) setup leaves open whether CCV generalizes to multi-hop reasoning or larger models. Furthermore, the lack of multi-seed variance reporting for K=20 and CCV makes it difficult to assess the statistical reliability of the modest +0.19 SubEM gain.

### (c) Proposed Research Experiments
| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0: Statistical Reliability** | The +0.19 SubEM gain is robust across random seeds, not an artifact of a single permutation set. | Run CCV (K=20) and MoA (K=20) with 3 different random seeds for permutation sampling. | MoA (K=20) | SubEM mean $\pm$ std, F1 mean $\pm$ std | Standard error < 0.05; gain remains positive across seeds | Low (3x inference time) | High: Solidifies validity of main claim. |
| **P1: Multi-hop Generalization** | CCV improves over MoA on multi-hop QA by leveraging document-level evidence agreement. | Evaluate on HotpotQA (test split) using same generator/retriever. | MoA (K=10, 20), Vanilla RAG | SubEM, F1 | CCV outperforms MoA at K=15+ on SubEM | Medium (new dataset eval) | Medium: Demonstrates practical utility beyond single-hop. |
| **P2: Cross-model Robustness** | Citation hallucination rates vary by model size, but the aggregation benefit holds. | Evaluate on Llama-3-8B or Mistral-7B on NaturalQuestions. | MoA (K=20) | SubEM, Citation Path (%) | Performance trend matches Qwen3-8B | Medium (new model eval) | Low-Medium: Strengthens external validity. |

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | CCV: training-free inference-time method for permutation-robust RAG exploiting citation structure for answer aggregation. | [1], [2] | `partially_overlapping` | Overlaps with MOI [2] and Stable-RAG [1] which use multi-permutation inference. Residual novelty: uses *doc-ID citation agreement* rather than answer frequency or hidden-state clustering. | High | Explicitly differentiate from MOI [2] in Related Work to clarify the aggregation signal distinction. |
| **C2** | CCV improves SubEM by +0.19 over majority voting on NaturalQuestions at K=20, scaling monotonically with K. | [2], [3] | `supported` | No prior work evaluates this specific citation-based K-scaling behavior against majority voting under JSON citation constraints. | High | Bound the claim to the JSON citation format and acknowledge standard Vanilla RAG baseline. |
| **C3** | Document-ID agreement correlates significantly with answer correctness ($p = 1.14 \times 10^{-5}$). | [1], [2] | `supported` | First work to validate document-level citation consistency as an explicit quality signal across permutations. | High | Report effect size to contextualize the practical significance of the statistical correlation. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Branch 1: Permutation-Robust RAG** | | | | | |
| Leaf 1.1: Training-based Robustness | Stable-RAG [1] | Assumes access to model weights; uses hidden-state clustering across permutations. | Uses citation structure (training-free, inference-time). | Low: distinct paradigms. |
| Leaf 1.2: Inference-time Aggregation | MOI [2], MoA [3] | Uses answer frequency (MoA) or explicit utility modeling (MOI) across permutations. | Uses doc-ID citation agreement instead of utility/answer frequency. | **High:** MOI is the closest prior; must be explicitly differentiated. |
| **Branch 2: Citation Reliability in RAG** | | | | | |
| Leaf 2.1: Citation Verification | VeriCite [4] | Uses NLI to pre-verify evidence before generation. | Uses multi-permutation voting for aggregation, not pre-generation verification. | Low: distinct objectives. |
| Leaf 2.2: Citation Failure Mitigation | Citention [5] | Addresses models failing to cite complete evidence. | Assumes citations are present but noisy across permutations. | Low: distinct objectives. |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [1] Stable-RAG (Zhang et al., 2026) | Permutation-induced hallucinations in RAG (Top-5) | Spectral clustering of hidden states, cluster-center decoding | Uses multi-permutation inference to improve consistency | Requires training (preference optimization); CCV is training-free. | Low risk to novelty. |
| [2] MOI (Lee et al., 2024) | Generator bias / position bias in RAG | Inference scaling across permuted contexts to estimate debiased passage utility | Uses multi-permutation inference to debias | Models explicit utility equations; CCV uses doc-ID citation agreement. | **High risk** if not differentiated; CCV is a complementary signal. |
| [3] MoA (Wang et al., 2024) | General LLM capability enhancement | Majority voting across multiple agent outputs | Uses multi-output aggregation | Votes on answer frequency; CCV votes on citation consistency. | Low risk; CCV is a direct improvement for citation-enabled RAG. |

### Contribution-level Novelty Conclusion
CCV's core method (C1) is `partially_overlapping` with Mixture-of-Intervention [2], which also uses multi-permutation inference scaling to mitigate position bias. The residual novelty of CCV lies in leveraging the permutation-invariant document IDs embedded in structured citations, providing a training-free aggregation signal that complements rather than replaces utility modeling. The empirical K-scaling demonstration (C2) and diagnostic validation of citation consistency (C3) are `supported` as new contributions. To strengthen the manuscript, Related Work must explicitly differentiate CCV from MOI [2], and the performance claims should be bounded to the specific JSON citation setting.

## References
[1] Stable-RAG: Mitigating Retrieval-Permutation-Induced Hallucinations in Retrieval-Augmented Generation 2601.02993

[2] Inference Scaling for Bridging Retrieval and Augmented Generation 2412.10684

[3] Mixture-of-agents enhances large language model capabilities 2406.04692

[4] VeriCite: Towards Reliable Citations in Retrieval-Augmented Generation via Rigorous Verification 2510.11394

[5] Citation Failure: Definition, Analysis and Efficient Mitigation 2510.20303

## Scores
**Final Score:** 5/10

**Post-Revision Target:** [6, 7]/10

**Justification:**
* **Research Value & Novelty (Medium):** The core idea of leveraging document-ID citation consistency across permutations is a clear, novel mechanism insight. It provides a training-free aggregation signal that complements existing methods like majority voting. However, the practical research value is currently dampened by the modest absolute performance gain (+0.19 SubEM over majority voting) and the fact that the method still underperforms standard unconstrained Vanilla RAG (-2.61 SubEM).
* **Validity & Soundness (Medium-High):** The mathematical formulation of CCV is sound, and the K-scaling analysis provides good theoretical backing for the mechanism. The diagnostic analysis validates the core hypothesis, though the small effect size warrants more nuanced interpretation. Multi-seed variance reporting for the main claim is currently missing.
* **Objectivity & Positioning (Low-Medium):** The paper's novelty positioning is incomplete due to the omission of Mixture-of-Intervention (MOI) in the Related Work, despite MOI being a key inference-time prior that also uses multi-permutation scaling. The performance framing risks overclaiming by focusing solely on the majority-voting baseline.
* **Reproducibility (High):** The method is well-specified and requires no training data, making it broadly applicable. Minor clarifications on tie-breaking and citation hallucination handling would further improve reproducibility.

**Verdict:** The paper is currently on the borderline. With the P0 revisions—bounding the performance claims to the specific JSON citation setting, explicitly differentiating from MOI in Related Work, and adding multi-seed variance reporting—the paper would be significantly stronger and more defensible, warranting a higher score.

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
| :--- | :--- | :--- | :--- |
| Page 1 | 3 | Covered | |
| Page 2 | 2 | Covered | |
| Page 3 | 2 | Covered | |
| Page 4 | 1 | Covered | |
| Page 5 | 2 | Covered | |
| Page 6 | 2 | Covered | |
| **Total** | **12** | **All substantive pages covered** | |

### ASCII Diagram — Paper Structure & Evidence Map

```text
[Problem: RAG position bias]
    -> [Prior Gap: Majority voting ignores citation structure; MOI uses utility modeling]
    -> [Idea: Correct answers cite the same doc-ID across permutations]
    -> [Method: Citation-Consistent Voting (CCV) aggregates by doc-ID agreement]
    -> [Evidence: +0.19 SubEM over MoA at K=20; p=1.14e-5 diagnostic correlation]
    -> [Gap: Absolute performance (46.37%) < Vanilla RAG (48.98%); limited eval scope]
```

### ASCII Diagram — Revision Strategy Roadmap

```text
[P0: Bound Performance Claim]
    -> [Action: Add Vanilla RAG (48.98%) as ceiling in Abstract/Results]
    -> [Impact: Aligns claims with absolute evidence, prevents overclaim]

[P0: Differentiate from MOI]
    -> [Action: Add MOI comparison in Related Work]
    -> [Impact: Clarifies residual novelty (citation vs. utility modeling)]

[P1: Robustness & Diagnostics]
    -> [Action: Discuss citation hallucination; report effect size]
    -> [Impact: Strengthens validity and mechanistic understanding]
```

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Permutation-Robust RAG (Root)
├── Branch 1: Training-based Methods
│   └── Leaf 1.1: Preference Optimization / Hidden-State Clustering [1]
│
├── Branch 2: Inference-time Methods
│   ├── Leaf 2.1: Answer-Frequency Voting (MoA) [3]
│   ├── Leaf 2.2: Utility Modeling (MOI) [2] <-- CLOSEST PRIOR
│   └── Leaf 2.3: Citation-Consistency Voting (CCV) [THIS PAPER]
│
└── Branch 3: Citation Reliability
    ├── Leaf 3.1: Pre-generation Verification (VeriCite) [4]
    └── Leaf 3.2: Citation Failure Mitigation (Citention) [5]
```