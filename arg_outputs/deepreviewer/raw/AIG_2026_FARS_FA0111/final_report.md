## Summary
This paper proposes a label-free method for calibrating Adaptive Parallel Encoding (APE) hyperparameters (temperature and scale) by minimizing KL divergence between sequential-teacher and parallel-encoded next-token distributions. 

**Core Findings:**
- KL-tuned APE (multi-token, K=8) achieves F1=48.09 on LongBench 2WikiMultihopQA, outperforming the label-tuned baseline (F1=46.23) by +1.86 points.
- KL calibration avoids the overfitting risk inherent in small-sample (N=32) label-based tuning.
- Temperature dominates the KL landscape with higher sensitivity and selection stability than scale.
- The KL-F1 correlation is weak ($\rho=0.295$), explaining the gap to the default configuration.

**Overall Verdict:**
The paper presents a clean, well-motivated empirical analysis of distributional matching as a label-free proxy for parallel context encoding. The methodology is sound and the results are reproducible. The primary value lies in exposing the brittleness of small-sample label tuning and providing a robust, practical alternative. The main scientific limitation is the weak proxy-task correlation, which the authors honestly report, and the limited scope (single dataset and task), which warrants further multi-dataset validation.

## Strengths
1. **Clear and Quantified Motivation:** The paper effectively identifies a practical and well-understood pain point (the cost and overfitting risk of label-based hyperparameter tuning). Quantifying the overfitting penalty (-2.76 F1 points on held-out data for the label-tuned baseline) makes the motivation very compelling.
2. **Clean Methodological Design:** Using KL divergence between sequential-teacher and parallel-encoded distributions is a natural, theoretically grounded choice. The multi-token averaging mechanism to address the T=1.0 degeneracy is a novel and useful technical insight.
3. **Honest and Rigorous Analysis:** The authors do not shy away from reporting the weak KL-F1 correlation ($\rho=0.295$). This honesty significantly strengthens the paper's credibility. The ablation study showing temperature dominance and the bootstrap stability analysis provide actionable practical insights for practitioners.
4. **High Reproducibility:** The experimental setup is clearly documented, including dataset splits, context regime (C4000×20), model versions (Llama-3.1-8B-Instruct), and greedy decoding. The code is publicly available.
5. **Concise and Well-Structured Narrative:** The paper is tightly written, with each section fulfilling a clear role. The abstract and introduction effectively frame the problem, and the conclusion honestly bounds the claims.

## Weaknesses
1. **Limited Experimental Scope (Major):** The entire evaluation is conducted on a single dataset (LongBench 2WikiMultihopQA) with a single model (Llama-3.1-8B-Instruct). While this provides a deep dive into one setting, it severely limits the generalizability claims. Different tasks (e.g., summarization, QA, coding) and model architectures might exhibit different KL-F1 correlations and hyperparameter sensitivities. Multi-dataset validation is essential to establish the method's practical utility.
2. **Misleading "Oracle" Terminology (Moderate):** The paper repeatedly refers to the label-tuned baseline as a "label-tuned oracle." In scientific literature, an "oracle" typically implies an optimal upper bound or a configuration with access to full information. Here, the "oracle" actually *underperforms* the default configuration due to overfitting. This terminology is paradoxical and potentially confusing. It should be renamed to "label-tuned baseline" or "validation-optimized configuration."
3. **Weak Proxy-Task Correlation (Major Scientific Limitation):** The KL-F1 correlation is weak and statistically insignificant ($\rho=0.295, p=0.15$). This means that minimizing KL divergence does not reliably predict better downstream performance. While the authors honestly report this, it fundamentally limits the theoretical guarantee of the method. The method works empirically because it avoids overfitting, not because KL is a strong proxy for F1. This distinction should be more prominently framed.
4. **Lack of Justification for Forward KL (Minor):** The paper uses forward KL divergence but does not justify why this choice is preferred over reverse KL, Jensen-Shannon divergence, or other distributional distances. Forward KL is zero-avoiding, which may be desirable for next-token matching, but this intuition is not stated.
5. **Missing Baseline Comparison (Moderate):** The paper compares KL-tuned APE against the default APE and a label-tuned baseline. However, it does not compare against other label-free calibration methods or proxy objectives (e.g., perplexity minimization, entropy matching). Establishing that KL is better than other potential proxies would strengthen the novelty claim.

## Key Issues
**1. "Label-Tuned Oracle" Terminology Paradox (Major)**
*   **Evidence:** The abstract and Section 4.2 refer to the label-based baseline as a "label-tuned oracle." Table 1 shows this configuration (F1=46.23) underperforms the default configuration (F1=48.99) by 2.76 points.
*   **Impact:** The term "oracle" implies an upper-bound or optimal performance, which is misleading. The method is actually a victim of overfitting. This paradox undermines the clarity of the experimental narrative.
*   **Action:** Rename "label-tuned oracle" to "label-tuned baseline" or "validation-set optimized configuration" throughout the manuscript.

**2. Weak KL-F1 Proxy Correlation (Major)**
*   **Evidence:** Section 4.5 reports a Spearman correlation of $\rho=0.295$ with $p=0.15$, which is statistically insignificant.
*   **Impact:** This indicates that minimizing KL divergence is not a reliable direct proxy for maximizing downstream F1. The method's success is a side-effect of avoiding overfitting rather than a strong predictive correlation.
*   **Action:** Frame this explicitly as a trade-off: the method sacrifices potential peak performance (the gap to default) for calibration robustness in the absence of labels.

**3. Limited Scope of Empirical Validation (Moderate)**
*   **Evidence:** The evaluation is restricted to a single task (LongBench 2WikiMultihopQA) and a single model (Llama-3.1-8B-Instruct).
*   **Impact:** It is unclear if the KL-F1 correlation and temperature dominance hold for other tasks (e.g., summarization, coding) or model families.
*   **Action:** Acknowledge this limitation strongly in the conclusion and frame multi-dataset validation as the critical P0 next step.

**4. Forward KL Justification (Minor)**
*   **Evidence:** Equation 2 uses forward KL divergence but lacks justification for why it is preferred over reverse KL or symmetric variants (e.g., JS divergence).
*   **Impact:** Reproducibility is unaffected, but methodological rigor is slightly weakened.
*   **Action:** Add a brief sentence noting that forward KL penalizes the student distribution for missing high-probability teacher tokens (zero-avoiding), which is desirable for preserving core semantic predictions.

## Actionable Suggestions
1. **Fix "Label-Tuned Oracle" Terminology (Must, P0):** Replace "label-tuned oracle" with "label-tuned baseline" or "validation-optimized baseline" in the Abstract, Section 4.2, and Section 5. This resolves the paradoxical implication that the underperforming baseline is an "oracle."
2. **Expand Experimental Scope (Must, P0):** Add at least one more dataset from LongBench (e.g., Qasper for summarization, or MultiFieldQA-en for multi-domain QA). This is critical to demonstrate that the KL calibration method generalizes beyond 2WikiMultihopQA and that the temperature dominance/stability findings are not task-specific.
3. **Frame the KL-F1 Trade-off Explicitly (Must, P1):** In Section 4.5 and the Conclusion, explicitly reframe the narrative: the method does not guarantee peak performance (as shown by the weak $\rho=0.295$), but it guarantees *reliable performance* in the absence of labels by avoiding the overfitting trap of small-sample validation. The gap to default is the "cost" of label-free calibration; the gain over label-tuning is the "benefit."
4. **Justify Forward KL Divergence (Nice-to-have, P2):** Add a brief sentence in Section 3.2 explaining the choice of forward KL. For example: "We use forward KL divergence because it is zero-avoiding, penalizing the APE distribution heavily for assigning low probability to tokens that the sequential teacher favors, thus ensuring high-probability teacher predictions are well-matched."
5. **Add a Baseline Proxy Comparison (Nice-to-have, P1):** To strengthen the claim that KL is a good proxy, compare KL-tuned APE against a simple alternative label-free proxy, such as minimizing APE next-token perplexity, or maximizing APE output entropy. This shows that KL provides a specific advantage over other naive distributional metrics.

## Storyline Options + Writing Outlines
### Abstract Outline (S1-S5)
*   **S1: Problem & Domain:** Long-context LLMs utilize parallel context encoding (e.g., APE) to reduce latency, but APE's performance critically depends on two hyperparameters that typically require labeled validation data for tuning.
*   **S2: Significance & Challenge:** In label-scarce production settings, small-sample label tuning is brittle and prone to severe overfitting (demonstrated by a -2.76 F1 drop on held-out data), making robust calibration a significant bottleneck.
*   **S3: Proposed Method:** We propose a label-free calibration method that aligns APE hyperparameters by minimizing the KL divergence between a sequential-teacher and the parallel-encoded student's next-token distributions, requiring zero ground-truth labels.
*   **S4: Key Technical Insight:** We introduce multi-token KL averaging to resolve single-token degeneracy, revealing that temperature is the dominant, selection-stable hyperparameter for distributional alignment.
*   **S5: Key Result & Bounded Implication:** On LongBench 2WikiMultihopQA, KL-tuned APE outperforms the label-tuned baseline by +1.86 F1 points, providing a robust, label-free calibration alternative despite a weak proxy-task correlation ($\rho=0.295$).

### Introduction Outline (Paragraph-by-Paragraph)
*   **P1: Big Picture & Stakes:** Establish the importance of long-context LLMs for RAG and ICL. Quantify the prefill-phase bottleneck (17 seconds for 128K tokens on H100) and introduce parallel context encoding (APE) as the leading efficiency-quality trade-off.
*   **P2: The Gap (APE Tuning Bottleneck):** Explain that APE introduces two sensitive hyperparameters (temperature T and scaling factor S) and that standard practice requires labeled validation data to tune them via grid search.
*   **P3: The Problem (Label-Tuning Brittleness):** Quantify the failure mode of label-based tuning. State that optimizing on small calibration sets (e.g., 32 samples) leads to overfitting, resulting in a 2.76-point F1 underperformance compared to the default configuration on held-out data. This motivates a robust, label-free alternative.
*   **P4: The Proposed Solution (KL Calibration):** Introduce the core insight: APE aims to align parallel encoding with sequential encoding. We leverage KL divergence between the sequential-teacher and APE next-token distributions as a label-free proxy for hyperparameter selection.
*   **P5: Methodological Refinement (Multi-Token Averaging):** Describe the single-token KL degeneracy (always selecting T=1.0) and introduce multi-token KL averaging as the mechanism to capture cumulative generation effects and recover better hyperparameters (e.g., T=0.95).
*   **P6: Contributions Summary:** Bullet point the key empirical results: KL outperforms the overfit label-tuned baseline, the temperature dominance and stability insights, and the practical value of the label-free approach for deployment.

## Priority Revision Plan
### Priority 0 (Must Complete - Scientific Validity & Terminology)
*   **Fix "Oracle" Terminology:** Globally search and replace "label-tuned oracle" with "label-tuned baseline" (Abstract, Section 4.2, Section 5).
*   **Add Second Dataset Validation:** Replicate the KL calibration procedure on at least one other LongBench task (e.g., Qasper or MultiFieldQA-en). If KL-tuned outperforms the label-tuned baseline here as well, the paper's core value is significantly elevated. Update Table 1 to be a multi-task table.
*   **Explicitly Frame the KL-F1 Trade-off:** Revise Section 4.5 to clearly state that the KL proxy does not guarantee peak F1 (weak correlation), but it reliably avoids the overfitting trap of label-based tuning, providing a robust floor for label-scarce deployment.

### Priority 1 (Highly Recommended - Robustness & Comparison)
*   **Add Baseline Proxy Comparison:** Add a simple label-free baseline for comparison, such as tuning T and S to minimize APE's next-token perplexity on the unlabeled calibration set. This demonstrates the specific value of distributional matching (KL) over other naive metrics.
*   **Report Variance:** Report the mean ± standard deviation for all F1 scores over at least 3 random seeds (or calibration set splits) to ensure the +1.86 point gain is statistically significant.

### Priority 2 (Nice-to-Have - Methodological Polish)
*   **Justify Forward KL:** Add a sentence in Section 3.2 explaining the choice of forward KL (zero-avoiding nature, preserving high-probability teacher tokens).
*   **Clarify Multi-Token KL Computational Cost:** Explicitly mention that K=8 is a practical choice; briefly note if K=16 or K=32 provides further gains, or if K=8 is the sweet spot for computation-quality trade-off.

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | KL-tuned APE outperforms label-tuned baseline and avoids overfitting. | LongBench 2WikiMultihopQA (32 cal / 168 test), Llama-3.1-8B, C4000×20, greedy decoding. Baselines: Default APE, Label-tuned APE. | Test F1, Mean KL | KL-tuned (K=8) F1=48.09, beating Label-tuned F1=46.23 by +1.86. | KL is a more robust signal than small-sample labels. | Limited to a single dataset and single model. |
| E2 | Multi-token KL averaging breaks single-token degeneracy (T*=1.0). | Same setup. Compare single-token KL (K=1) vs multi-token KL (K=8). | Test F1, Mean KL | Multi-token selects T*=0.95, improving F1 by +0.25 over single-token T*=1.0. | Cumulative generation effects matter for alignment. | Does not test larger K values (e.g., K=16, 32). |
| E3 | Temperature (T) dominates scale (S) in KL sensitivity and selection. | T-only vs S-only KL calibration ablations. 25 grid configurations. | Test F1, KL Range | T-only F1=47.84, S-only F1=46.26. T has 2.6× higher KL sensitivity. | S dimension contributes minimal information; T is the primary driver. | Does not explain *why* S is less informative theoretically. |
| E4 | KL-based T selection is stable across different calibration samples. | Bootstrap resampling (10 resamples, different seeds). | Mode, 95% CI Width | T selection is perfectly stable (CI width=0.0), S is unstable (CI width=0.38). | Practical deployment can rely on KL for T selection. | 10 resamples is a low number for robust statistical claims. |
| E5 | KL divergence is a weak proxy for downstream F1. | Correlation analysis across 25 grid points. | Spearman ρ, p-value | ρ=0.295, p=0.15 (not statistically significant). | Explains why KL-tuned does not match the default performance. | Weak correlation limits the predictive power of the proxy. |

### (b) Research-Theme Gap Diagnosis
The core research value—**a robust, label-free proxy for hyperparameter tuning**—is partially proven. The reproducibility is high, but the generalizability (impact on practice) is weakly supported due to the single-dataset evaluation. The weak KL-F1 correlation gap means the method is practically useful for avoiding overfitting, but theoretically it lacks a strong guarantee that lower KL equals better F1.

### (c) Proposed Research Experiments
| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|---|---|---|---|---|---|---|---|
| KL calibration generalizes beyond 2WikiMultihopQA. | KL-tuned APE consistently outperforms label-tuned APE across different QA and summarization tasks. | Evaluate KL calibration on two additional LongBench tasks (e.g., Qasper, MultiFieldQA-en). | Default APE, Label-tuned APE. | Test F1 | KL-tuned beats Label-tuned by a statistically significant margin (p < 0.05 over 3 seeds). | ~4 hours | Significantly elevates the practical impact and generalizability. |
| Forward KL is superior to Reverse KL / JS Divergence. | Forward KL penalizes low probability on high-probability teacher tokens, leading to better F1 than other divergences. | Compare Forward KL, Reverse KL, and JS divergence as calibration proxies. | Standard KL-tuned baseline. | Test F1, Mean KL | Forward KL yields the highest F1 and/or lowest KL. | ~2 hours | Justifies the methodological choice and increases scientific rigor. |
| Multi-token KL (K>8) provides further gains. | Increasing K captures more generation dynamics, improving calibration up to a sweet spot. | Evaluate K = 1, 4, 8, 16, 32 on the calibration set. | K=8 baseline. | Test F1, Calibration Time | K=8 or K=16 is the optimal trade-off; diminishing returns at K=32. | ~3 hours | Validates the K=8 choice or improves the default configuration. |

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board
| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Label-free KL calibration method for APE hyperparameters using model-internal signals. | APE (Yang et al., 2025) | `supported` | While APE introduces the hyperparameters, it does not propose a label-free calibration method. KL divergence is a standard metric, but its application here for *teacher-student distributional matching in parallel context encoding* is a novel practical intervention. | High | Frame clearly as a calibration strategy for parallel encoding. |
| C2 | KL-tuned APE outperforms small-sample label-tuned optimization. | APE (Yang et al., 2025) | `supported` | The paper empirically demonstrates that label-tuning on 32 samples leads to overfitting, and KL calibration provides a more robust baseline. This highlights a specific failure mode in current practices. | High | Rename "label-tuned oracle" to "label-tuned baseline" to avoid paradox. |
| C3 | Temperature dominates KL landscape sensitivity and selection stability. | APE (Yang et al., 2025) | `supported` | The ablation and bootstrap stability analyses provide new empirical insights into the behavior of APE's hyperparameters, offering practical deployment guidance. | High | None. |

### (9B) Related-Work Taxonomy Matrix
| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Parallel Context Encoding | Parallel Windows (PCW) | Ratner et al., 2022 | Independent segment encoding, linear scaling. | Lacks adaptive temperature/scale alignment; suffers from CoT deterioration. | Low (foundational, not overlapping). |
| Parallel Context Encoding | Cross-Encoder Expansion (CEPE) | Yen et al., 2024 | Uses a small encoder + cross-attention to extend context. | Requires training/fine-tuning; does not address the specific hyperparameter tuning problem. | Low. |
| Parallel Context Encoding | Adaptive Alignment (APE) | Yang et al., 2025 | Introduces T and S to align parallel/sequential distributions. | APE provides the mechanism; this paper provides the *label-free calibration* for it. | Residual novelty is high (calibration focus). |
| Distributional Matching | Teacher-Student Self-Supervision | Q-Match (Mulc & Dwibedi, 2023) | Uses queues for distribution matching without labels. | Focuses on tabular data embeddings, not attention hyperparameter tuning. | Low. |
| Distributional Matching | Sparse Attention Correction | Delta Attention (Willette et al., 2025) | Identifies distributional shift in sparse attention. | Corrects distributional shift via delta correction, not via hyperparameter tuning via KL. | Low. |

### (9C) Head-to-Head Comparison Matrix
| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| Yang et al., 2025 (APE) | Efficient long-context via parallel encoding. | Introduces T and S to align distributions. | Provides the foundational model and the problem of hyperparameter tuning. | Does not solve the tuning problem in a label-free way. | Establishes the baseline; this paper is a direct complementary calibration extension. |
| Mulc & Dwibedi, 2023 (Q-Match) | Self-supervised learning via distribution matching. | Matches student/teacher distributions using a queue. | Uses label-free distribution matching. | Different domain (tabular vs. attention mechanisms); different objective. | No novelty risk; distinct application of distribution matching. |
| Willette et al., 2025 (Delta Attention) | Sparse attention distributional shift. | Delta correction to realign sparse attention to full attention. | Addresses distributional mismatch in attention. | Uses post-processing correction, not hyperparameter selection. | Complementary insight into distributional shifts; no overlap. |

**Contribution-level Novelty Conclusion:**
The core contributions are well-supported. C1 is novel in its application of KL divergence as a label-free proxy for parallel context encoding calibration. C2 is empirically validated, highlighting a practical failure mode of label-based tuning. C3 provides useful empirical insights into APE's internal mechanics. The main novelty risk is minimal, as the paper sits cleanly in the gap between the APE mechanism and practical deployment calibration.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)
```text
Parallel Context Encoding & Calibration (Root)
├── Branch 1: Parallel Encoding Mechanisms
│   ├── Leaf 1.1: Parallel Context Windows (PCW) [Ratner et al.]
│   │   └── Independent segment encoding, linear scaling.
│   ├── Leaf 1.2: Cross-Encoder Expansion (CEPE) [Yen et al.]
│   │   └── Cross-attention for richer segment interactions.
│   └── Leaf 1.3: Adaptive Alignment (APE) [Yang et al., 2025]
│       └── Introduces T and S to align distributions. [MANUSCRIPT BASELINE]
├── Branch 2: Distributional Matching & Calibration
│   ├── Leaf 2.1: Teacher-Student Self-Supervision [Q-Match]
│   │   └── Queue-based matching for tabular embeddings.
│   └── Leaf 2.2: Sparse Attention Correction [Delta Attention]
│       └── Delta correction for sparse attention shifts.
└── Branch 3: Attention Hyperparameter Calibration (Target Niche)
    └── Leaf 3.1: Label-Free KL Calibration [This Paper]
        └── Minimizes KL divergence between sequential and parallel distributions.
```

## References
[1] APE: Faster and Longer Context-Augmented Generation via Adaptive Parallel Encoding 2502.05431

[2] Revisiting Parallel Context Windows: A Frustratingly Simple Alternative and Chain-of-Thought Deterioration 2305.15262

[3] Long-Context Language Modeling with Parallel Context Encoding 2402.16617

[4] Q-Match: Self-Supervised Learning by Matching Distributions Induced by a Queue 2302.05444

[5] Delta Attention: Fast and Accurate Sparse Attention Inference by Delta Correction 2505.11254

[6] Longbench: A bilingual, multitask benchmark for long context understanding 2308.14508

[7] Tuning Sequential Monte Carlo Samplers via Greedy Incremental Divergence Minimization 2503.15704

[8] Hyperparameter Selection for Imitation Learning 2105.12034

## Scores
**Final Score:** 7.0/10
*Justification: The paper presents a clean, well-motivated empirical analysis of distributional matching for parallel context encoding. The methodology is sound, the results are reproducible, and the honesty regarding the weak KL-F1 correlation significantly strengthens credibility. The score is held back from a higher level primarily due to the limited empirical scope (single dataset/task evaluation) and the need for clearer terminology ("label-tuned oracle").*

**Post-Revision Target:** [8.0, 8.5]/10
*Condition: Achievable if the authors validate the method on at least one additional LongBench task (e.g., Qasper or MultiFieldQA-en) to establish generalizability, and if they explicitly frame the KL-F1 trade-off as a robust floor vs. peak performance trade-off.*