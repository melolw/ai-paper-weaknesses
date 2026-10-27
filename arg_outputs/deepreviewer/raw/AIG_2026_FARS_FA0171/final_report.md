## Summary
This paper proposes SourceJS-LoRA, a method for learning LoRA merge coefficients by minimizing Jensen-Shannon (JS) divergence between the merged model's predictions and each task expert's predictions. The core motivation is that existing adaptive merging methods (e.g., AdaMerging) use reference-free entropy minimization, which can produce overconfident incorrect predictions and unstable coefficients. The paper demonstrates on 8 GLUE tasks with T5-base that SourceJS-LoRA achieves 83.10% average accuracy, outperforming DO-Merging by +2.29 points and entropy-based learning by +5.55 points, while producing balanced positive coefficients where entropy minimization yields extreme negative values.

The paper makes three contributions: (1) identifying the failure mode of entropy-based coefficient learning, (2) proposing JS divergence as a teacher-anchored objective, and (3) demonstrating empirical gains with stable coefficients. However, retrieval reveals that the core idea of teacher-anchored divergence minimization for merge coefficients overlaps with recent work (SAMerging, Dalili & Mahdavi, 2025), which uses KL divergence for the same purpose. The novelty is narrower than claimed: using JS divergence (symmetric, bounded) instead of KL divergence (asymmetric, potentially unbounded). The paper needs to explicitly differentiate from SAMerging and provide stronger causal evidence for the "confidently wrong" diagnosis.

## Strengths
1. **Clear problem motivation and diagnosis:** The paper effectively identifies a concrete failure mode of entropy-based coefficient learning—producing overconfident incorrect predictions and unstable negative coefficients. The empirical evidence that entropy minimization performs worse than simple uniform merging (77.55% vs 79.76%) is a strong, surprising finding that motivates the need for source-referenced objectives.

2. **Compelling coefficient stability analysis:** Section 4.4 provides the strongest analytical contribution. Visualizing learned coefficients across methods clearly shows that entropy minimization collapses toward extreme negative values while SourceJS-LoRA produces balanced positive coefficients. This stability evidence directly supports the methodological claim and provides a mechanistic explanation for performance differences.

3. **Practical and parameter-efficient:** The method requires only 128 unlabeled examples per task and learns only merge coefficients (8-576 parameters depending on granularity), keeping the base model and LoRA adapters frozen. This makes the approach practical for scenarios where labeled data is scarce.

4. **Clean experimental setup:** The evaluation on 8 GLUE tasks with T5-base, averaged over three seeds, provides a solid empirical baseline. The ablation study on task-wise vs layer-wise coefficients, while showing marginal gains for layer-wise, demonstrates methodological transparency.

## Weaknesses
1. **Novelty overlap with SAMerging (2512.21288):** The core idea of using teacher-anchored divergence minimization (minimizing divergence between merged model and expert predictions) to learn merge coefficients is already present in SAMerging, which uses KL divergence for the same purpose. The paper's related work section does not cite SAMerging, and the contribution statement does not differentiate JS divergence from KL divergence. This significantly narrows the novelty of C2 from "a new teacher-anchored objective" to "using JS divergence instead of KL divergence for teacher anchoring."

2. **Missing variance reporting and statistical significance:** Table 1 reports mean accuracy over three seeds but does not include standard deviations. Given that some gains are marginal (+2.29 vs DO-Merging, +0.41 for layer-wise vs task-wise), the statistical reliability of these improvements cannot be assessed. This weakens confidence in the reported rankings.

3. **Contradiction between main text and Appendix:** Section 3.5 states "The optimization converges in approximately 300 steps" while Appendix A states "cosine schedule over 1000 steps." This inconsistency needs resolution for reproducibility.

4. **Misleading SOTA comparison framing:** DO-Merging is a data-free method, while SourceJS-LoRA uses unlabeled data for coefficient learning. Comparing them as direct SOTA competitors is misleading because they operate under different data assumptions. The paper should compare against data-driven baselines or explicitly frame the comparison as cross-paradigm.

5. **Marginal layer-wise benefit with high parameter cost:** The ablation shows that layer-wise coefficients (576 parameters) only gain +0.41 points over task-wise (8 parameters), a 72x parameter increase for a marginal gain. Furthermore, layer-wise with matched hyperparameters actually underperforms (82.01% vs 82.69%), requiring "optimized hyperparameters" to achieve the best result. The computational cost justification for layer-wise is missing.

## Key Issues
| Priority | Issue | Severity | Research-Value Impact | Validity Risk | Fixability | Confidence |
|---|---|---|---|---|---|---|
| P0 | Novelty overlap with SAMerging (2512.21288): teacher-anchored divergence minimization for merge coefficients is not novel | Major | High (narrows C2 novelty significantly) | Moderate (claim may be rejected as incremental) | Medium (requires explicit differentiation + citation) | High |
| P1 | Missing variance reporting prevents assessing statistical significance of marginal gains (+2.29, +0.41) | Major | Moderate (weakens result reliability) | High (ranking may not be significant) | Low (requires re-running experiments with std reporting) | High |
| P2 | Contradiction between "300 steps" (Sec 3.5) and "1000 steps" (Appendix A) | Minor | Low (reproducibility confusion) | Low (ambiguous hyperparameters) | Low (clarification only) | High |
| P3 | Misleading SOTA framing vs DO-Merging (different data assumptions: data-free vs data-driven) | Major | Moderate (comparison validity risk) | Moderate (misleading benchmarking) | Low (rewrite comparison framing) | High |
| P4 | Marginal layer-wise benefit (+0.41) with 72x parameter increase lacks cost justification | Minor | Low (methodological transparency) | Low (questionable design choice) | Low (add cost analysis paragraph) | Medium |

## Actionable Suggestions
1. **Address SAMerging overlap (P0 - Must):** Cite SAMerging (Dalili & Mahdavi, 2025, arXiv:2512.21288) in the Related Work section and explicitly differentiate JS divergence from KL divergence. Add a paragraph explaining why JS divergence is theoretically preferable: (a) symmetric treatment of expert and merged distributions, avoiding KL's asymmetry bias; (b) bounded in [0, log 2], providing more stable gradients during coefficient optimization; (c) avoiding the potentially unbounded penalty of KL divergence when distributions have zero-probability mismatches. Reposition C2 to emphasize "JS divergence as a stable, symmetric alternative to KL divergence for teacher-anchored merge coefficient learning."

2. **Report variance and add significance tests (P1 - Must):** Re-run experiments to obtain standard deviations over the three seeds. Report mean ± std in Table 1. For the key comparisons (SourceJS-LoRA vs DO-Merging, SourceJS-LoRA vs Entropy Coeff), add paired significance tests (e.g., paired t-test across tasks) to confirm that gains are statistically reliable.

3. **Resolve step-count contradiction (P2 - Must):** Clarify in Section 3.5 whether the optimization runs for 300 or 1000 steps. If it converges at 300 steps but uses a 1000-step cosine schedule, state this explicitly: "We use a cosine learning rate schedule over 1000 steps, with early stopping typically triggered around 300 steps when validation loss plateaus."

4. **Reframe comparison baseline (P3 - Must):** Add a paragraph clarifying that DO-Merging is a data-free method while SourceJS-LoRA uses unlabeled data for coefficient learning. Frame the comparison as: "SourceJS-LoRA outperforms both data-free methods (DO-Merging, +2.29) and data-driven adaptive methods (Entropy Coeff, +5.55), demonstrating the advantage of source-referenced objectives over both heuristics and reference-free learning."

5. **Add computational cost analysis for layer-wise (P4 - Nice-to-have):** Report the wall-clock time or GPU hours for task-wise vs layer-wise coefficient optimization. If the 72x parameter increase does not significantly increase computation time (e.g., because coefficients are optimized via lightweight forward passes), this would justify the layer-wise approach. If the cost is substantial, consider emphasizing the task-wise variant as the primary recommendation.

## Storyline Options + Writing Outlines
### Current Storyline vs Alternatives

The current introduction follows: Big Picture (LoRA) -> Existing Merging Methods -> AdaMerging Entropy Critique -> SourceJS-LoRA Proposal -> Contributions. This is a solid arc, but the transition should explicitly bridge the "reference-free" gap to the "teacher-anchored" solution and differentiate from prior distillation-based merging.

**Selected Best Storyline:** Practical Stakes -> The Reference-Free Pitfall -> Teacher-Anchored Distillation Gap -> JS Divergence Stability -> Evidence Preview -> Contribution Summary.

**Alignment Checks:**
- (a) Problem alignment: The stated challenge (entropy minimization collapses to extreme coefficients) matches the proposed solution (JS divergence anchors to expert predictions).
- (b) Variable alignment: Core concepts (expert predictions, divergence minimization, merge coefficients) appear as key method variables in Sections 3.3-3.5.
- (c) Contribution-evidence alignment: C1 (failure mode) is supported by Table 1 (entropy < uniform); C2 (SourceJS method) is supported by Method 3.3; C3 (performance + stability) is supported by Table 1 and Figure 2.

### Abstract Outline (Complete)

- **S1 (Problem):** Merging task-specific LoRA adapters simplifies deployment but introduces parameter interference.
- **S2 (Significance):** Adaptive coefficient learning mitigates interference, yet existing methods rely on reference-free objectives that can produce overconfident incorrect predictions.
- **S3 (Prior Gap):** Reference-free optimization collapses toward extreme negative coefficients, misaligning confidence with correctness.
- **S4 (Method):** We propose SourceJS-LoRA, minimizing Jensen-Shannon divergence between the merged model and each task expert's predictions for a symmetric, bounded teacher-anchored objective.
- **S5 (Result):** On 8 GLUE tasks, SourceJS-LoRA achieves 83.10% average accuracy and produces stable positive coefficients where entropy minimization yields extreme negative values.

### Introduction Outline (Complete)

- **P1 (Practical Motivation):** LoRA enables efficient adaptation; organizations need to consolidate multiple adapters.
- **P2 (Merging Landscape):** Data-free methods (Task Arithmetic, TIES-Merging, DO-Merging) use fixed coefficients that cannot adapt to interference patterns.
- **P3 (Reference-Free Failure Mode):** AdaMerging's entropy minimization is reference-free; empirical evidence shows it underperforms uniform merging and yields unstable negative coefficients.
- **P4 (SourceJS Intuition & JS vs KL):** SourceJS-LoRA anchors optimization to task experts using JS divergence. JS is symmetric and bounded, providing more stable gradients than KL divergence used in prior distillation-based merging.
- **P5 (Evidence & Contributions):** Preview main results and list three explicit contributions.

### Copy-Ready Introduction Revision (P3 -> P4 Bridge)

*Mentor Revised Version:* "Under LoRA interference, this can produce overconfident incorrect outputs and unstable coefficients. Our experiments confirm this risk: entropy-based coefficient learning achieves only 77.55% average accuracy on GLUE, performing worse than simple uniform merging (79.76%), and yields extreme negative coefficients (range: −3.04 to +2.50).

To address this, we propose SourceJS-LoRA, which learns merge coefficients by minimizing Jensen-Shannon (JS) divergence between the merged model's predictions and each task expert's predictions. Unlike entropy minimization, this source-referenced objective anchors optimization to verified task knowledge. Furthermore, unlike prior distillation-based merging methods that use asymmetric KL divergence, JS divergence provides a symmetric, bounded objective in [0, log 2], which ensures stable gradient signals and naturally produces balanced, positive coefficients."

## Priority Revision Plan
### P0: Critical Novelty & Positioning Repairs (Must before resubmission)
1. **Cite and differentiate from SAMerging (arXiv 2512.21288):**
   - Add SAMerging to Related Work (Adaptive Merging paragraph).
   - In Method Section 3.3, explicitly discuss the theoretical advantages of JS divergence over KL divergence (symmetry, boundedness, gradient stability).
   - Reposition Contribution C2 from "a new teacher-anchored objective" to "using symmetric, bounded JS divergence for stable, coefficient-level distillation optimization."
2. **Reframe SOTA comparison:**
   - Clarify that DO-Merging is data-free while SourceJS-LoRA uses unlabeled data. Frame the comparison as cross-paradigm rather than direct SOTA.

### P1: Empirical Rigor & Reproducibility Repairs (Must)
1. **Add variance reporting:** Re-run experiments over the three seeds to obtain standard deviations. Update Table 1 with `mean ± std` format.
2. **Add statistical significance:** Include paired significance tests (e.g., t-test across 8 GLUE tasks) for the key claims: SourceJS-LoRA vs DO-Merging, and SourceJS-LoRA vs Entropy Coeff.
3. **Resolve step-count contradiction:** Unify the "300 steps" (Sec 3.5) and "1000 steps" (Appendix A) by stating the cosine schedule length and the early stopping criterion explicitly.

### P2: Analysis Depth & Transparency Improvements (Strongly Recommended)
1. **Confidence-accuracy analysis:** Provide a direct calibration plot or confidence vs accuracy correlation for Entropy Coeff vs SourceJS-LoRA to validate the "confidently wrong" hypothesis beyond average accuracy drops.
2. **Layer-wise cost analysis:** Report the wall-clock time or GPU hours for task-wise vs layer-wise coefficient optimization. If the 72x parameter increase is computationally negligible, state this to justify the design choice.
3. **Supervised baseline clarification:** Specify the exact training setup for the Supervised Coeff baseline (loss function, data source, split ratio).

### Page Coverage Audit
| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| 1 | 4 | covered | Abstract + Introduction P1-P3 annotated |
| 2 | 3 | covered | Introduction P4 + Contributions + Related Work annotated |
| 3 | 3 | covered | Method 3.2 + 3.3 annotated |
| 4 | 2 | covered | Method 3.4-3.5 + Experiment Setup annotated |
| 5 | 1 | covered | Main Results annotated |
| 6 | 2 | covered | Coefficient Analysis + Conclusion annotated |
| 7 | 0 | skipped | References section; non-substantive for core claims |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory (Full Coverage)

| Exp ID | Objective/Hypothesis | Setup (Data/Split/Protocol/Baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| 1 | **Main comparison:** SourceJS outperforms heuristics and entropy learning | GLUE 8 tasks, T5-base, 3 seeds; Baselines: Uniform, DO-Merging, Entropy, Supervised, Single-task | Avg Accuracy | SourceJS 83.10 > DO-Merging 80.81 (+2.29) > Entropy 77.55 | C3 (Performance) | Missing std dev; no significance tests |
| 2 | **Coefficient stability:** Entropy collapses, SourceJS is stable | Same as Exp 1; Analyze learned merge coefficients $\gamma$ | Range, std, negative counts | Entropy: [-3.04, 2.50], std high; SourceJS: [0.06, 0.50], std 0.13 | C1, C2 (Stability) | No explicit calibration analysis |
| 3 | **Ablation:** Task-wise vs Layer-wise coefficients | GLUE, T5-base; Task-wise (8 params) vs Layer-wise (576 params) | Avg Accuracy | Layer-wise optimized 83.10 > Task-wise 82.69 (+0.41) | C2 (Granularity) | Marginal gain; highly hyperparameter sensitive; no cost analysis |
| 4 | **Supervised vs Unsupervised:** Data efficiency comparison | GLUE; Supervised (64 labeled samples) vs SourceJS (128 unlabeled) | Avg Accuracy | SourceJS 83.10 > Supervised 79.79 | Method Efficiency | Supervised setup/loss details unclear |

### (b) Research-Theme Gap Diagnosis
The core research value claims (new knowledge on entropy failure, reproducibility of JS merging, impact on practice) are weakly supported by statistical reliability and direct mechanism validation. Specifically:
- **Validity Risk:** The claim that entropy minimization produces "confidently wrong" predictions is supported only by lower average accuracy, not by direct confidence-accuracy correlation.
- **Novelty Risk:** The JS divergence vs KL divergence distinction is theoretically sound but empirically unisolated; no ablation compares JS against KL within the same SourceJS pipeline.
- **Transparency Risk:** Variance over seeds is missing, making small gains (+0.41 for layer-wise, +2.29 vs DO-Merging) statistically unverifiable.

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| **C3 (Reliability)** | Gains are statistically significant across tasks and seeds. | Report mean $\pm$ std over 3 seeds; add paired t-test across 8 GLUE tasks. | DO-Merging, Entropy Coeff | Accuracy std, p-value | p < 0.05 for SourceJS vs baselines | Low (0.5 GPU hrs) | **High:** Validates core empirical claims. |
| **C1 (Mechanism)** | Entropy method has lower accuracy at high prediction confidence. | Plot accuracy vs top-1 predicted probability for Entropy Coeff and SourceJS. | Uniform merge | Expected Calibration Error (ECE), accuracy at >0.9 confidence | SourceJS maintains higher accuracy at high confidence than Entropy | Low (0.5 GPU hrs) | **High:** Directly proves "confidently wrong" diagnosis. |
| **C2 (Novelty)** | JS divergence yields more stable coefficients and better accuracy than KL divergence. | Replace JS divergence in Eq. (3) with KL divergence; keep all else fixed. | KL-divergence variant | Coeff std, Avg Accuracy, JS loss | KL shows higher coefficient variance or lower accuracy than JS | Low (0.5 GPU hrs) | **High:** Isolates JS vs KL novelty from SAMerging overlap. |
| **C2 (Cost)** | Layer-wise parameter increase does not add significant optimization time. | Measure wall-clock time for coefficient optimization steps. | Task-wise (8 params) | Wall-clock time per step, total time | Layer-wise < 2x time of task-wise | Low (Measurement only) | **Medium:** Justifies layer-wise design choice. |

### (d) Traceability Rule
Every proposed experiment maps to an unresolved core claim:
- Exp 1 (Variance) -> C3 Validity
- Exp 2 (Calibration) -> C1 Mechanism
- Exp 3 (JS vs KL) -> C2 Novelty
- Exp 4 (Cost) -> C2 Methodological Soundness

```text
ASCII Diagram — Experiment Upgrade Plan
[Exp 1: Variance + Significance] --> [Validates C3 Reliability]
[Exp 2: Calibration Plot] --> [Proves C1 "Confidently Wrong" Mechanism]
[Exp 3: JS vs KL Ablation] --> [Isolates C2 Novelty from SAMerging]
[Exp 4: Cost Analysis] --> [Justifies C2 Layer-wise Design]
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Entropy-based coefficient learning fails: produces confidently wrong predictions and unstable coefficients. | [3] AdaMerging (2310.02575) | supported | The failure mode is empirically demonstrated (entropy < uniform on GLUE, negative coefficients). | High | Tighten wording: "overconfident incorrect outputs" instead of "confidently wrong"; add calibration evidence. |
| C2 | SourceJS-LoRA uses JS divergence to task expert predictions as a teacher-anchored objective. | [1] SAMerging (2512.21288) | partially_overlapping | SAMerging also uses teacher-anchored KL divergence for merge coefficient learning. The residual novelty is using JS (symmetric, bounded) instead of KL (asymmetric, unbounded). | High | Explicitly differentiate JS vs KL; cite SAMerging; reposition C2 as "symmetric, bounded JS divergence for stable coefficient optimization." |
| C3 | SourceJS-LoRA achieves 83.10% avg accuracy on GLUE with T5-base, outperforming DO-Merging and entropy learning. | [2] DO-Merging (2505.15875) | supported | Empirical gains are clear but lack variance reporting. The performance claim is valid-within-scope. | Medium | Add std dev; frame comparison carefully (cross-paradigm vs DO-Merging). |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Model Merging | Branch 1: Data-Free Merging | [2] DO-Merging, [4] TIES-Merging, [5] Task Arithmetic | No data required; fixed/heuristic coefficients | SourceJS uses unlabeled data for adaptive learning | Low risk (different paradigm) |
| Root: Model Merging | Branch 2: Entropy-Based Adaptive | [3] AdaMerging | Unlabeled data; reference-free entropy minimization | SourceJS uses reference-based JS divergence | Medium risk (direct predecessor) |
| Root: Model Merging | Branch 2: Distillation-Based Adaptive | [1] SAMerging, [6] ProDistill | Unlabeled data; teacher-anchored divergence/activation distance | SourceJS uses JS divergence (symmetric, bounded) instead of KL | **High risk** (direct overlap) |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] SAMerging (2512.21288) | Multi-task merging with unlabeled data | KL divergence between merged and expert predictions | Teacher-anchored divergence for coefficient learning | Uses KL (asymmetric, unbounded); SourceJS uses JS (symmetric, bounded [0, log 2]) | **Significant:** Narrows C2 novelty to divergence choice, not the overall teacher-anchored concept. |
| [3] AdaMerging (2310.02575) | Multi-task merging with unlabeled data | Entropy minimization for coefficient learning | Reference-free adaptive coefficient optimization | SourceJS directly addresses its failure mode | **Motivational:** Establishes the baseline critique. |
| [6] ProDistill (2502.12706) | Multi-task merging with few-shot data | Layer-wise activation distance distillation | Distillation-based merging coefficients | Uses activation distance (not output distribution); different task setting | **Low:** Different distillation target and setting. |

### Contribution-level Novelty Conclusion

- **C1 (Entropy Failure Mode):** `supported`. The empirical evidence that entropy minimization underperforms uniform merging and produces extreme negative coefficients is novel and well-documented within this manuscript.
- **C2 (SourceJS Method):** `partially_overlapping`. The core concept of teacher-anchored divergence minimization overlaps with SAMerging [1]. The residual novelty is the choice of JS divergence over KL divergence, which provides symmetric, bounded gradients for more stable coefficient optimization. This distinction must be explicitly stated and validated (e.g., via JS vs KL ablation).
- **C3 (Performance & Stability):** `supported` with medium confidence. Empirical gains are clear but require variance reporting and significance tests for full validation.

```text
ASCII Diagram — Paper Structure & Evidence Map
[Claim C1: Entropy fails]
    -> [Evidence: Table 1 (Entropy < Uniform), Fig 2 (negative coeffs)]
    -> [Gap: Needs direct calibration evidence for "confidently wrong"]
[Claim C2: JS divergence method]
    -> [Evidence: Eq 3-5 (JS formulation), Fig 2 (stable coeffs)]
    -> [Overlap: SAMerging [1] uses KL for same teacher-anchored purpose]
    -> [Novelty: JS symmetry + boundedness -> coefficient stability]
    -> [Gap: Missing JS vs KL ablation; missing SAMerging citation]
[Claim C3: Performance gains]
    -> [Evidence: Table 1 (83.10% avg), Table 2 (ablation)]
    -> [Gap: Missing std dev; missing significance tests]

ASCII Diagram — Revision Strategy Roadmap
[P0: Cite SAMerging + JS vs KL differentiation]
    -> [Expected gain: Resolves novelty overlap; strengthens C2 claim]
[P1: Add variance + significance tests]
    -> [Expected gain: Validates C3 reliability; reviewer confidence]
[P2: Calibration plot + JS vs KL ablation]
    -> [Expected gain: Proves C1 mechanism; isolates C2 residual novelty]

ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Model Merging (Root)
├── Branch 1: Data-Free Merging
│   ├── Leaf 1.1: Task Arithmetic / Parameter Averaging [5]
│   └── Leaf 1.2: Interference Resolution [2][4]
├── Branch 2: Data-Driven Adaptive Merging
│   ├── Leaf 2.1: Entropy-Based (Reference-Free) [3]
│   └── Leaf 2.2: Distillation-Based (Teacher-Anchored) [1][6]
│       ├── Sub-leaf 2.2.1: KL Divergence [1] <-- OVERLAP RISK
│       ├── Sub-leaf 2.2.2: Activation Distance [6]
│       └── Sub-leaf 2.2.3: JS Divergence (This Paper) <-- RESIDUAL NOVELTY
└── Branch 3: LoRA-Specific Merging
    ├── Leaf 3.1: Decoupling / Orthogonalization [2]
    └── Leaf 3.2: Parameter Pruning / Clustering
```

## References
[1] Model Merging via Multi-Teacher Knowledge Distillation 2512.21288

[2] Decouple and Orthogonalize: A Data-Free Framework for LoRA Merging 2505.15875

[3] AdaMerging: Adaptive Model Merging for Multi-Task Learning 2310.02575

[4] Scalable Model Merging with Progressive Layer-wise Distillation 2502.12706

[5] Beyond Parameter Arithmetic: Sparse Complementary Fusion for Distribution-Aware Model Merging 2602.11717

## Scores
Final Score: 5.5/10

Post-Revision Target: [6.5, 7.5]/10

**Scoring Rationale (Top-Meat-Bottom):**

**Top (Strengths):** The paper presents a clear and practically valuable method for LoRA merging. The coefficient stability analysis in Section 4.4 is the strongest contribution: demonstrating that entropy minimization collapses to extreme negative coefficients while SourceJS-LoRA produces balanced positive values provides a compelling mechanistic explanation for the observed performance gains. The method is also parameter-efficient and practical, requiring only 128 unlabeled examples per task.

**Meat (Weaknesses & Risks):** However, two issues limit the current score. First, the novelty claim is narrower than presented. Retrieval reveals that SAMerging (Dalili & Mahdavi, 2025) already uses teacher-anchored KL divergence to learn merge coefficients from expert predictions. The residual novelty of this paper lies specifically in using *Jensen-Shannon divergence* (symmetric, bounded) instead of *KL divergence* (asymmetric, unbounded). This crucial distinction is missing from the Related Work and Method sections. Second, the empirical rigor lacks variance reporting and statistical significance tests. Given that gains over DO-Merging (+2.29) and the layer-wise improvement (+0.41) are marginal, the absence of standard deviations and paired tests leaves the statistical reliability of the rankings uncertain. Additionally, a direct contradiction between "300 steps" in the main text and "1000 steps" in the Appendix raises reproducibility concerns.

**Bottom (Constructive Expectations):** The paper can be significantly improved with targeted revisions. The authors should (1) explicitly cite and differentiate from SAMerging by adding a JS vs KL divergence ablation, (2) report mean $\pm$ std over seeds and add significance tests for the key comparisons, and (3) provide a calibration plot to directly validate the "confidently wrong" hypothesis. Addressing these gaps will firmly establish the method's novelty and validate its empirical claims, making it a strong contribution to the model merging literature.