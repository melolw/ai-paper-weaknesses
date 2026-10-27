## Summary
This paper investigates the "repetition advantage" in long chain-of-thought (CoT) supervised fine-tuning (SFT), where training for multiple epochs on a small dataset outperforms single-epoch training on a larger dataset. The authors propose a diagnostic framework decomposing accuracy into ParseRate (fraction of parseable outputs) and Acc|Parse (accuracy conditional on parsing). Their key finding is that on AIME benchmarks, the accuracy gap between repetition and data-scaling conditions reverses when conditioning on successful parsing (mediation fractions exceeding 1.0), suggesting that termination behavior—rather than improved reasoning—drives much of the repetition advantage. They also propose Termination-Aware SFT, which increases loss weight on termination tokens, recovering only 14% of the repetition advantage.

The paper presents a valuable diagnostic lens and interesting empirical observations. However, the main claims are over-stated: the conclusion that the repetition advantage is "primarily a termination effect" is not uniformly supported (GPQA mediation is only 0.69), and the proposed intervention recovers only 14% of the effect, leaving 86% unexplained. The evaluation relies on single-seed results without variance reporting, which is a significant concern given that reasoning benchmarks are highly sensitive to implementation details. The confounding between optimization depth (1 vs 32 epochs) and data diversity is not adequately controlled or discussed.

## Strengths
1. **Valuable Diagnostic Framework:** The ParseRate/Acc|Parse decomposition is a clean and interpretable tool for disentangling termination behavior from reasoning quality in long-CoT SFT. This framework provides a practical way to diagnose a key confound in reasoning benchmark evaluation.

2. **Compelling Empirical Observation:** The gap reversal on AIME benchmarks (mediation fractions > 1.0) is a strong empirical finding that challenges the assumption that data repetition necessarily improves reasoning. This observation alone is a significant contribution to understanding training dynamics.

3. **Well-Designed Ablation:** The ablation study of TA-SFT components (EOS-only, think-only, no-cap) is informative, revealing synergistic effects between token types and suggesting that upweighting reasoning boundary tokens may improve reasoning quality beyond termination alone.

4. **Benchmark-Dependent Analysis:** The paper correctly identifies that the mediation effect varies across benchmarks (strong on AIME, weaker on GPQA), indicating that termination behavior may not be the universal driver of the repetition advantage.

## Weaknesses
1. **Overclaiming the Termination Effect (Major):** The paper repeatedly states that the repetition advantage is "primarily a termination effect" or "entirely from termination behavior." However, GPQA shows a mediation fraction of only 0.69 (meaning termination explains <70% of the gap), and TA-SFT recovers only 14% of the advantage. This leaves ~86% of the effect unexplained. The strong causal language is not supported by the evidence and risks undermining credibility.

2. **Single-Seed Evaluation Without Variance (Major):** All results are reported from a single random seed. Hochlehnert et al. (2025) demonstrate that AIME benchmarks are highly sensitive to decoding parameters, seeds, and implementation details. Without variance estimates (e.g., mean ± std over ≥3 seeds), the reported 17.6pp gap and 2.0pp TA-SFT improvement cannot be assessed for statistical reliability.

3. **Uncontrolled Confounding Between Optimization Depth and Data Diversity (Major):** The comparison between Condition A (1 epoch on 51.2k unique samples) and Condition B (32 epochs on 1.6k samples) conflates data diversity with optimization depth. Ren et al. (2026) show a "dip-and-recovery" pattern in SFT generalization, suggesting that 1-epoch checkpoints may simply be under-optimized rather than representing the true potential of data scaling.

4. **Non-Standard Mediation Terminology (Minor):** The "mediation fraction" formula $M = 1 - \Delta_{cond} / \Delta_{uncond}$ is not standard causal mediation terminology. When $M > 1.0$, it indicates a "gap reversal" rather than a standard mediated proportion. This terminology may confuse readers familiar with causal mediation analysis.

5. **Related Work Gaps (Minor):** The related work section misses key papers on SFT training dynamics, including Ren et al. (2026) on dip-and-recovery patterns, Hochlehnert et al. (2025) on benchmark sensitivity, and Goyal et al. (2021) on selective loss computation. These would strengthen the positioning of the contribution.

## Key Issues
### Issue 1: Overclaiming the Termination Effect
**Problem:** The paper repeatedly asserts that the repetition advantage is "primarily a termination effect" (Abstract, Introduction, Conclusion) or "entirely from termination behavior" (Section 4.2).
**Cause:** This conclusion is drawn from the gap reversal on AIME benchmarks (M > 1.0) without adequately weighing contradictory evidence: GPQA shows only partial mediation (M = 0.69), and the proposed targeted intervention (TA-SFT) recovers merely 14% of the total accuracy gap.
**Risk:** If the reader verifies the GPQA row in Table 2 or the limited 14% recovery in Table 1, the strong causal language appears unjustified, undermining the paper's scientific credibility.
**Actionable Fix:** Replace definitive causal language ("is primarily a termination effect") with bounded, evidence-consistent wording ("substantially mediates the advantage on AIME, though additional mechanisms likely contribute"). Explicitly acknowledge the ~86% of the effect that remains unexplained by the proposed intervention.

### Issue 2: Single-Seed Evaluation Without Variance Reporting
**Problem:** All reported metrics (Acc@n, ParseRate, Acc|Parse) appear to be from a single random seed. No standard deviations or confidence intervals are provided.
**Cause:** Omission of multi-seed evaluation.
**Risk:** As demonstrated by Hochlehnert et al. (2025), mathematical reasoning benchmarks like AIME are highly sensitive to decoding parameters, random seeds, and implementation details. Without variance estimates, the reported 17.6pp gap and 2.0pp TA-SFT improvement cannot be assessed for statistical reliability. The findings may be seed-specific artifacts.
**Actionable Fix:** Re-run all three conditions (A, B, C) over at least 3 random seeds. Report mean ± std for Acc@n, ParseRate, and Acc|Parse. If compute is constrained, explicitly acknowledge this limitation and downgrade strong claims to "suggestive evidence."

### Issue 3: Uncontrolled Confounding Between Optimization Depth and Data Diversity
**Problem:** The comparison between Condition A (1 epoch on 51.2k samples) and Condition B (32 epochs on 1.6k samples) conflates two variables: data diversity and optimization depth.
**Cause:** Holding total gradient steps constant (51,200) while varying epochs means Condition A is trained for only 1 epoch, while Condition B benefits from 32 epochs of optimization.
**Risk:** Ren et al. (2026) reveal "dip-and-recovery" patterns in SFT generalization, suggesting that early checkpoints (1-epoch) may underperform due to under-optimization rather than lack of diversity. If the repetition advantage is partially an artifact of optimization depth, the conclusion that termination behavior is the driver becomes less credible.
**Actionable Fix:** Acknowledge this confounder explicitly in the Method section. Ideally, add a control condition: "Condition A-multi-epoch" that trains on 51.2k samples for multiple epochs (with a reduced learning rate or adjusted steps) to isolate the diversity effect from the epoch-count effect. If new experiments are not feasible, discuss this limitation and its implications in the Discussion/Conclusion.

## Actionable Suggestions
1. **Rewrite Overclaim Language:** Replace "primarily a termination effect" and "entirely from termination behavior" with bounded, evidence-consistent phrasing such as "substantially mediates the advantage on AIME benchmarks, though additional mechanisms likely contribute to the remaining gap." (See Annotations on Page 1, Page 2, Page 5, Page 6, Page 7.)

2. **Add Variance Reporting:** Re-run Conditions A, B, and C over at least 3 random seeds. Report mean ± std for Acc@n, ParseRate, and Acc|Parse in Table 1. This is essential for establishing the statistical reliability of the reported gaps. (See Annotation on Page 5.)

3. **Control for Optimization Depth:** Add a "Condition A-multi-epoch" that trains on 51.2k samples for multiple epochs (adjusting learning rate/steps) to isolate data diversity from epoch count. If not feasible, explicitly discuss this confounder in Section 3.2 and Section 5. (See Annotation on Page 3.)

4. **Update Related Work:** Integrate key papers on SFT training dynamics (Ren et al. 2026 on dip-and-recovery patterns; Hochlehnert et al. 2025 on benchmark sensitivity; Goyal et al. 2021 on selective loss computation) to strengthen positioning and demonstrate awareness of prior work. (See Annotation on Page 2.)

5. **Rename "Mediation Fraction":** Replace the non-standard "mediation fraction" terminology with "gap-reversal indicator" or "parseability-adjusted gap ratio," and explain that M > 1.0 means the conditional gap reverses sign rather than using causal mediation language. (See Annotation on Page 4.)

6. **Deepen Ablation Interpretation:** Discuss why EOS-only underperforms baseline (24.2% vs 25.2%), hypothesizing that it causes premature sequence termination. Highlight the finding that think-only achieves the highest Acc|Parse (58.2%) as evidence that reasoning boundary tokens may improve reasoning quality beyond termination alone. (See Annotation on Page 7.)

7. **Fix Title Typo:** Correct "ISA" to "IS A" in the title. (See Annotation on Page 1.)

## Storyline Options + Writing Outlines
### Abstract Outline (complete)
- **S1 (Problem & Context):** Recent work shows that in long chain-of-thought (CoT) supervised fine-tuning (SFT), training for many epochs on a small dataset outperforms single-epoch training on a larger dataset—a counterintuitive "repetition advantage." 
- **S2 (Significance/Challenge):** This phenomenon challenges standard machine learning intuition and raises the question of whether repetition genuinely improves reasoning or merely enhances output format compliance.
- **S3 (Prior Gap):** While the repetition advantage has been empirically observed, no diagnostic framework exists to disentangle termination behavior from reasoning quality.
- **S4 (Method):** We propose a diagnostic decomposition of accuracy into ParseRate (fraction of parseable outputs) and Acc|Parse (accuracy conditional on parsing), alongside a mediation analysis. We also introduce Termination-Aware SFT (TA-SFT), which increases loss weight on termination tokens as a targeted intervention.
- **S5 (Key Result & Bounded Implication):** On AIME benchmarks, conditioning on successful parsing reverses the accuracy gap between repetition and scaling conditions (gap-reversal indicator > 1.0), suggesting termination substantially mediates the advantage. However, weaker effects on GPQA and limited TA-SFT recovery (14%) indicate that additional mechanisms likely contribute to the repetition advantage.

### Introduction Outline (complete)
- **P1 (Big Picture & Phenomenon):** Introduce long-CoT SFT as a critical technique for reasoning models. Present the "repetition advantage" (Kopiczko et al., 2026) where multi-epoch training on small data beats single-epoch scaling. Frame this as a concrete practitioner dilemma: should resources be invested in data diversity or training repetition?
- **P2 (Competing Hypotheses):** Propose two hypotheses: (1) repeated exposure enables deeper learning of reasoning patterns, or (2) the advantage stems from improved output termination and format compliance rather than reasoning quality.
- **P3 (Diagnostic Framework & Evidence):** Introduce the ParseRate/Acc|Parse decomposition. State that the analysis reveals a gap reversal on AIME benchmarks when conditioning on parsing, providing evidence consistent with a termination effect, though benchmark-dependent variations (e.g., GPQA) suggest additional factors.
- **P4 (Proposed Intervention & Residual Gap):** Introduce Termination-Aware SFT (TA-SFT) as a targeted loss-reweighting intervention. Report that it improves accuracy by 2.0pp but recovers only 14% of the repetition advantage, highlighting that termination learning through repetition involves mechanisms beyond simple loss reweighting.
- **P5 (Contribution Summary):** List three contributions with bounded, evidence-consistent claims: (1) a diagnostic framework for disentangling termination from reasoning, (2) a mediation analysis showing substantial but incomplete mediation of the accuracy gap, and (3) TA-SFT as a partial recovery intervention and diagnostic tool.

## Priority Revision Plan
| Priority | Issue | Action | Expected Impact |
|---|---|---|---|
| **P0** | Single-seed evaluation without variance (Major) | Re-run Conditions A, B, C over ≥3 seeds; report mean ± std for Acc@n, ParseRate, Acc|Parse in Table 1. | Establishes statistical reliability of the 17.6pp gap and 2.0pp TA-SFT gain; prevents rejection for irreproducibility. |
| **P0** | Overclaiming the termination effect (Major) | Systematically replace "primarily/entirely a termination effect" with bounded phrasing ("substantially mediates on AIME, though ~86% remains unexplained"). Apply to Abstract, Intro, Section 4.2, and Conclusion. | Improves scientific credibility and defensibility against reviewer scrutiny of GPQA data (M=0.69). |
| **P0** | Uncontrolled confounder: optimization depth vs diversity (Major) | Explicitly acknowledge the 1-epoch vs 32-epoch confounder in Section 3.2 and Discussion. Ideally, add a "Condition A-multi-epoch" control. | Clarifies that the repetition advantage may be partially driven by under-optimization in the single-epoch baseline, strengthening the causal argument. |
| **P1** | Related work gaps (Minor/Major) | Integrate Ren et al. (2026) on dip-and-recovery, Hochlehnert et al. (2025) on benchmark sensitivity, and Goyal et al. (2021) on selective loss computation. Reposition Section 2 to highlight decision-relevant axes. | Demonstrates command of the field; contextualizes the TA-SFT approach within prior token-level loss methods. |
| **P1** | Non-standard "mediation fraction" terminology (Minor) | Rename $M = 1 - \Delta_{cond} / \Delta_{uncond}$ to "gap-reversal indicator" and clarify that $M > 1.0$ means the conditional gap reverses sign. | Prevents confusion among readers familiar with causal mediation analysis; aligns terminology with empirical behavior. |
| **P1** | Shallow ablation interpretation (Minor) | Discuss why EOS-only underperforms (potential premature termination) and why think-only achieves the highest Acc|Parse (reasoning boundary tokens may improve reasoning quality). | Turns an empirical observation into a meaningful mechanistic insight; strengthens the discussion. |
| **P2** | Title typo ("ISA" → "IS A") (Minor) | Correct the title to "THE REPETITION ADVANTAGE IN LONG-COT SFT IS A TERMINATION EFFECT". | Fixes a basic error that could affect indexing and initial impression. |

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1: Main Comparison | Data repetition (B) vs data scaling (A) under fixed update budget | OLMo-3-7B, DOLCI-think, 51.2k steps. A: 1 epoch on 51.2k; B: 32 epochs on 1.6k | Acc@n, ParseRate, Acc|Parse on AIME'24, AIME'25, GPQA | B outperforms A by 17.6pp aggregate; gap reverses on Acc|Parse | Termination mediates the repetition advantage | Single seed; optimization-depth confounder |
| E2: TA-SFT Intervention | Loss reweighting on termination tokens recovers some repetition advantage | Condition C: 1 epoch on 51.2k with α=10 weight on `` + EOS; loss cap=50 | Acc@n, ParseRate, Acc|Parse | +2.0pp Acc@n over A; ParseRate +5.6pp (+14% of A-B gap) | Termination learning can be partially addressed without repetition | Only 14% recovery; single seed |
| E3: Mediation Analysis | Quantify parseability's role in the accuracy gap | Compute Δ_uncond, Δ_cond, M across benchmarks | Uncond gap, cond gap, mediation fraction | M=1.33 (AIME'24), M=1.56 (AIME'25), M=0.69 (GPQA) | Gap reversal on AIME; benchmark-dependent effects | Non-standard terminology; single seed |
| E4: Ablation Study | Identify which TA-SFT components contribute | EOS-only (α=50), think-only (α≈50), no-cap (α≈37.3) vs full method (α=10) | Acc@n, ParseRate, Acc|Parse | EOS-only underperforms; think-only best Acc|Parse; no-cap underperforms | Synergistic token types; moderate α optimal | No seed variance; limited α sweep |

### Research-Theme Gap Diagnosis
The core research-value claims (new knowledge about repetition advantage mechanisms, reproducibility of training dynamics, and practical guidance for reasoning SFT) are weakly supported because: (1) the primary diagnostic finding is based on single-seed results, (2) the intervention recovers only 14% of the effect, leaving the primary mechanism unexplained, and (3) the optimization-depth confounder is not controlled. These gaps prevent strong causal conclusions.

### Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| Repetition advantage reliability | The 17.6pp gap is stable across random seeds | Re-run A, B, C over 3 seeds (seeds 0, 42, 123) | Same protocol; report mean ± std | Acc@n, ParseRate, Acc|Parse per seed | Std < 3pp for Acc@n gaps | ~3x current compute | Establishes statistical validity; prevents rejection |
| Optimization-depth confounder | Multi-epoch training on diverse data recovers the advantage | Add "Condition A-8epoch": 8 epochs on 51.2k (reduced LR) | Compare with A (1 epoch) and B (32 epochs) | Acc@n, ParseRate, Acc|Parse | If A-8epoch ≈ B, then epoch count, not repetition, drives the effect | ~8x A's compute | Isolates diversity vs repetition; strengthens causal claim |
| Unexplained 86% mechanism | Memorization-induced structure learning or gradient concentration explains residual gap | Analyze training token accuracy curves across epochs; measure gradient norm concentration on repeated samples | Compare with Ren et al. (2026) dip-and-recovery analysis | Token accuracy, gradient norms, loss landscapes | Correlates with performance gains across epochs | Analysis-only; low cost | Provides mechanistic explanation for the residual effect |
| GPQA mediation difference | Multiple-choice format reduces termination sensitivity | Evaluate ParseRate/Acc|Parse on a 4th benchmark (e.g., MMLU-STEM) | Same A/B/C conditions | Acc@n, ParseRate, Acc|Parse | Consistent mediation < 0.7 on multiple-choice tasks | ~1x current compute | Explains benchmark-dependent variation; improves generalizability |

## Novelty Verification & Related-Work Matrix
### 9A. Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| **C1** | Diagnostic framework (ParseRate/Acc|Parse) decomposing long-CoT accuracy to reveal termination effects | [1], [6], [11] | `partially_overlapping` | Decomposing accuracy into termination and reasoning quality is conceptually novel in the long-CoT SFT context. However, the general idea of analyzing failure modes (truncation vs reasoning error) appears in related training dynamics literature. | High | Bound claim to the specific long-CoT SFT setting; acknowledge general diagnostic precedents. |
| **C2** | Mediation analysis showing parseability over-explains the accuracy gap (gap reversal on AIME) | [1], [6] | `supported` | The specific application of a mediation/gap-reversal analysis to quantify the repetition advantage is novel. The empirical observation of M > 1.0 on AIME benchmarks is a new finding. | High | None; this is a distinct empirical contribution. |
| **C3** | Termination-Aware SFT (TA-SFT) improving accuracy via termination token loss reweighting | [6], [8] | `partially_overlapping` | The specific target (`` + EOS for long-CoT) is novel. However, token-level loss reweighting and selective loss masking for SFT have been explored in other contexts (e.g., TALR [8], SED-SFT [6]). | Medium | Explicitly contrast TA-SFT with prior token-level loss methods (TALR, SED-SFT, Token Cleaning) to highlight the specific contribution. |

### 9B. Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| **Branch 1: Data Scaling & Repetition in SFT** | Leaf 1.1: Repetition Advantage | [1] | Fixed gradient-update budget; long-CoT data | [1] discovers the phenomenon; this paper diagnoses its mechanism (termination). | Low risk; complementary contribution. |
| | Leaf 1.2: Data Efficiency / Less-is-More | [10], [13] | High-quality data beats quantity | Focus on data curation/selection, not multi-epoch repetition. | No risk. |
| **Branch 2: Training Dynamics & Generalization** | Leaf 2.1: Generalization in Reasoning SFT | [11] | SFT vs RL generalization; extended training | [11] reveals dip-and-recovery patterns in extended SFT, suggesting under-optimization artifacts. This paper's 1-epoch baseline may suffer from this. | Medium risk; highlights confounder. |
| | Leaf 2.2: Benchmark Sensitivity | [9] | Benchmarks sensitive to seeds/decoding | [9] shows AIME is highly sensitive to implementation; this paper lacks seed variance. | Low risk to novelty; high risk to validity. |
| **Branch 3: Token-Level Loss & Data Selection** | Leaf 3.1: Token-Level Loss Reweighting | [6], [8] | Token-level signals improve SFT | [6] (SED-SFT) masks tokens for diversity; [8] (TALR) reweights tokens to prevent forgetting. TA-SFT reweights for termination. | Medium risk; requires differentiation in text. |
| | Leaf 3.2: Selective Loss Computation | [15] | Modifying loss computation steers behavior | [15] removes high/low loss tokens to tune summarization. Conceptually precedes TA-SFT. | Low risk; historical precedent. |

### 9C. Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] Kopiczko et al. (2026) | Long-CoT SFT, data scaling vs repetition | Multi-epoch training on small data | Identical phenomenon (repetition advantage) | [1] reports the effect and uses token accuracy as a stopping criterion; this paper diagnoses *why* (termination vs reasoning). | Foundational paper; this work is a diagnostic follow-up. |
| [8] Lin et al. (2025) | Domain-specific SFT, general capability loss | Token-Adaptive Loss Reweighting (TALR) | Token-level loss reweighting in SFT | TALR reweights to balance domain adaptation vs generalization; TA-SFT reweights specific structure/termination tokens. | Requires explicit differentiation in Related Work. |
| [11] Ren et al. (2026) | Reasoning SFT generalization | Conditional analysis on optimization/data | Training dynamics of long-CoT SFT | [11] shows dip-and-recovery in out-of-domain performance; this paper shows gap reversal conditional on parsing. | Highlights optimization-depth confounder in this paper's design. |
| [6] Chen et al. (2026) | SFT diversity for RL | SED-SFT (selective entropy regularization) | Token-level masking/reweighting in SFT | SED-SFT masks high-confidence tokens to encourage diversity; TA-SFT upweights low-frequency termination tokens. | Different objective (diversity vs termination); clarify distinction. |

### Contribution-level Novelty Conclusion
The manuscript makes a novel empirical contribution by diagnosing the "repetition advantage" as partially driven by termination behavior (C1, C2). The gap reversal observation on AIME benchmarks (M > 1.0) is a new finding. However, C3 (TA-SFT) partially overlaps with prior work on token-level loss reweighting (TALR [8], SED-SFT [6]). To strengthen the novelty claim, the authors should explicitly contrast TA-SFT with these prior methods and acknowledge that the general idea of token-level loss modification is established, while the specific application to long-CoT termination is new.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Long-CoT SFT Research (Root)
├── Branch 1: Data Scaling & Repetition
│   ├── Leaf 1.1: Repetition Advantage (Kopiczko et al. [1]) -> Foundation of this paper
│   └── Leaf 1.2: Data Efficiency / Curation (LIMA [10], LIMO [13]) -> Quality over quantity
├── Branch 2: Training Dynamics & Generalization
│   ├── Leaf 2.1: Generalization in Reasoning SFT (Ren et al. [11]) -> Dip-and-recovery patterns
│   └── Leaf 2.2: Benchmark Sensitivity (Hochlehnert et al. [9]) -> Seed/decoding sensitivity
└── Branch 3: Token-Level Loss & Data Selection
    ├── Leaf 3.1: Token-Level Loss Reweighting (TALR [8], SED-SFT [6]) -> Prior reweighting methods
    └── Leaf 3.2: Selective Loss Computation (Goyal et al. [15]) -> Historical precedent
```

## References
[1] Data Repetition Beats Data Scaling in Long-CoT Supervised Fine-Tuning 2602.11149

[6] SED-SFT: Selectively Encouraging Diversity in Supervised Fine-Tuning 2602.07464

[8] SFT Doesn't Always Hurt General Capabilities: Revisiting Domain-Specific Fine-Tuning in LLMs 2509.20758

[9] A Sober Look at Progress in Language Model Reasoning: Pitfalls and Paths to Reproducibility 2504.07086

[10] LIMO: Less is More for Reasoning 2502.03387

[11] Rethinking Generalization in Reasoning SFT: A Conditional Analysis on Optimization, Data, and Model Capability 2604.06628

[13] Lima: Less is More for Alignment 2305.11206

[15] Training Dynamics for Text Summarization Models 2110.08370

## Scores
**Final Score: 5.5/10**

This paper presents a novel and valuable diagnostic lens (ParseRate/Acc|Parse decomposition) for analyzing the "repetition advantage" in long-CoT SFT. The empirical observation of a gap reversal on AIME benchmarks is a compelling, non-obvious finding that advances our understanding of training dynamics. However, the score is reduced due to three primary validity concerns: (1) strong overclaiming of a "termination effect" that is only partially supported (GPQA mediation is 0.69, intervention recovers only 14%), (2) single-seed evaluation without variance reporting, which is a critical omission given the known sensitivity of reasoning benchmarks, and (3) an uncontrolled confounding between optimization depth (1 vs 32 epochs) and data diversity. If these issues are addressed, the paper's research value would be significantly higher.

**Post-Revision Target: [7.5, 8.5]/10**

Achieving this target requires: (1) adding multi-seed variance reporting to establish statistical reliability, (2) explicitly acknowledging and ideally controlling for the optimization-depth confounder, and (3) consistently downgrading overconfident causal language to bounded, evidence-consistent claims throughout the Abstract, Introduction, Results, and Conclusion.