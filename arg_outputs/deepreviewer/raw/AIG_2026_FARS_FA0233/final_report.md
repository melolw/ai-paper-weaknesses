## Summary
This paper investigates whether output-dissimilarity monitoring on canary prompts can enable selective defense against emergent misalignment—triggering KL regularization only for malicious fine-tuning while preserving benign task learning. The authors propose PhaseGuard-KL, an event-triggered method that monitors Jensen-Shannon divergence on a fixed set of safety probes and activates KL regularization when divergence exceeds a threshold. Using rigorous pre-registered success criteria, the experiments demonstrate that the trigger fires identically at step 20 for both malicious (Security EM) and benign (OpSwap) fine-tuning, activating KL for ~94% of training and degrading benign task performance from 54.6% to 22.8%. No KL coefficient simultaneously satisfies both safety and utility criteria.

The core contribution is a well-executed negative result that rules out a class of output-level monitoring approaches for selective defense. The paper is honest about its findings and the experimental design is clean. However, the manuscript would benefit from stronger framing of the negative result's scientific value, more extensive connection to broader literature on the safety-capability trade-off, and additional multi-seed validation for the benign task. The work provides a useful cautionary finding for the emergent misalignment defense community and motivates future exploration of gradient-level or representation-level monitoring alternatives.

## Strengths
1. **Honest and rigorous negative result:** The paper honestly reports that its core hypothesis is refuted, providing clear pre-registered success criteria and transparent lambda sweep analysis. This is commendable and contributes valuable negative knowledge to the emergent misalignment defense literature.

2. **Clean experimental design:** The use of pre-registered success criteria (Security EM ≤24.3%, OpSwap ≥43.7%) enables unambiguous hypothesis testing. The lambda sweep across five coefficient values provides comprehensive evidence that no setting simultaneously satisfies both criteria.

3. **Clear root cause analysis:** The paper correctly identifies that the trigger mechanism detects distribution shift magnitude but not shift intent, and both tasks cause similar JS divergence increases (0.28–0.33) within the first 5 training steps. This explanation is well-grounded in the reported data.

4. **Well-motivated research question:** The selective defense problem—blocking malicious behavioral changes while preserving benign learning—is a genuinely important open challenge for safe LLM fine-tuning. Testing output-dissimilarity monitoring as a potential solution addresses a natural and well-motivated hypothesis.

5. **Accessible method description:** The PhaseGuard-KL architecture is clearly described with three well-defined components (canary prompt set, dissimilarity monitor, threshold-based trigger), and the truncated JS divergence formulation is computationally practical and well-explained.

## Weaknesses
1. **OpSwap single-seed validation limits robustness of trigger-timing claim (Major):** The benign OpSwap task uses only 1 seed, while Security EM uses 3. The core finding—that the trigger fires identically at step 20 for both tasks—cannot be assessed for stability across random seeds. If trigger timing varies significantly across seeds, the "identical triggering" conclusion is less robust. Multi-seed reporting for OpSwap is needed to validate trigger stability and report variance.

2. **Insufficient connection to broader safety-capability literature (Major):** The Root Cause Analysis does not connect the negative result to theoretical work on the safety-capability trade-off (Chen et al., 2025) or to gradient-based/representation-level alternatives (GradShield, GRASP). This leaves the reader without a clear understanding of where this finding fits in the broader research landscape and what concrete alternatives remain.

3. **Under-justified method hyperparameters (Minor):** Key design choices—24 canary prompts, k=256 top-k truncation, threshold τ=0.15, 2 consecutive monitoring points, monitoring every 5 steps—lack explicit justification or sensitivity analysis. While the negative result likely holds across reasonable hyperparameter ranges, the absence of any rationale makes the method appear somewhat arbitrary.

4. **Contribution framing over-emphasizes the failed method design (Minor):** The first contribution bullet frames the PhaseGuard-KL method design as a "principled" contribution without qualifying that it ultimately fails its core purpose. This can confuse readers about what is actually being contributed. The real contribution is the experimental framework and the empirical evidence ruling out output-level monitoring.

5. **Hypothesis asymmetry assumption lacks grounding (Minor):** The hypothesis that "malicious fine-tuning should cause detectable shifts... while benign fine-tuning should not—or should shift less" is not supported by prior theory or empirical evidence. Without explaining why this asymmetry was expected, the hypothesis feels ad hoc rather than grounded in the literature.

## Key Issues
| Priority | Issue | Root Cause | Risk Level | Impact on Paper |
|----------|-------|------------|------------|-----------------|
| P0 | OpSwap single-seed prevents trigger stability verification | Only 1 seed used for benign task vs. 3 for malicious task | Major | Core "identical triggering at step 20" claim cannot be validated for stability; reader cannot assess variance in trigger timing |
| P1 | Root Cause Analysis isolated from broader literature | No connection to theoretical safety-capability trade-off work or gradient/representation-based alternatives | Major | Negative result's scientific value under-appreciated; reader lacks concrete alternative research directions |
| P2 | Method hyperparameters lack justification | 24 canaries, k=256, τ=0.15, 2 consecutive points, every-5-steps monitoring have no stated rationale | Minor | Method appears arbitrary; sensitivity of trigger to these choices is unknown |
| P3 | Contribution bullets over-frame failed method as "principled design" | First bullet does not qualify that the method fails its core purpose | Minor | Readers may be confused about what is actually contributed; negative result value diluted |
| P4 | Hypothesis asymmetry assumption lacks prior grounding | No theoretical or empirical basis stated for why malicious fine-tuning should cause larger shifts than benign | Minor | Hypothesis feels ad hoc; reduces perceived plausibility of the tested idea |

## Actionable Suggestions
**P0: Validate trigger stability with multi-seed OpSwap runs (Must)**
- Run the OpSwap benign fine-tuning on at least 2 additional seeds (seeds 123 and 456 to match Security EM).
- Report mean ± std for both OpSwap exact match rate and trigger step in Table 1.
- If trigger step variance is large (e.g., ±10+ steps), explicitly discuss this in Section 4.4 as a limitation. If variance is small (±2-3 steps), add a sentence: "Trigger timing is stable across 3 seeds (step 20 ± 2), reinforcing the conclusion that benign fine-tuning reliably exceeds the divergence threshold."

**P1: Expand Root Cause Analysis with literature connections (Must)**
- Add 2-3 sentences in Section 4.4 connecting the finding to theoretical safety-capability trade-off work (Chen et al., 2025) and gradient/representation-level alternatives (GradShield, GRASP).
- Include a short paragraph: "Gradient-based filtering [1] and representation-level spurious correlation removal [2] have demonstrated the ability to distinguish harmful from benign fine-tuning signals at a more granular level. These approaches operate on the optimization trajectory rather than output distributions, suggesting they may offer the discriminative power that PhaseGuard-KL lacks."
- References:
[1] GradShield: Alignment Preserving Finetuning 2605.14194
[2] Unsupervised Identification and Removal of Spurious Correlations During Fine-Tuning 2605.27676

**P2: Justify key method hyperparameters (Nice-to-have)**
- Add 2-3 sentences in Section 3.2 explaining the choice of 24 canary prompts, k=256 top-k truncation, threshold τ=0.15, and monitoring frequency.
- Example: "The canary set size of 24 balances detection sensitivity with computational overhead per monitoring step. The threshold τ=0.15 was calibrated on preliminary runs to distinguish meaningful distribution shifts from training noise. We monitor every 5 steps to balance detection latency with compute cost."

**P3: Reframe contribution bullets to emphasize negative knowledge (Nice-to-have)**
- Reposition the first bullet to highlight the experimental framework rather than the failed method design.
- Strengthen the third bullet to explicitly state the broader implication: ruling out output-level monitoring as a class of selective defense approaches.
- See the revised contribution bullets in the PDF annotation for Page 2.

**P4: Add grounding to the hypothesis asymmetry assumption (Nice-to-have)**
- In Introduction Paragraph 3, add one sentence explaining the intuition behind the asymmetry: "The intuition is that malicious fine-tuning, which targets safety-relevant behavioral changes, should cause disproportionately large shifts on safety probes, while benign fine-tuning should cause smaller or more localized shifts."

## Storyline Options + Writing Outlines
### Abstract Outline (Complete)

The current abstract clearly reports the negative result but lacks explicit hypothesis framing and scientific-value articulation. The following 5-sentence blueprint provides a cleaner narrative arc:

| Sentence | Role | Key Claim | Evidence Anchor | Draft Guidance |
|----------|------|-----------|-----------------|----------------|
| S1 | Problem & Domain | Emergent misalignment challenges safe fine-tuning of LLMs | Betley et al. (2026); Turner et al. (2025) | "Emergent misalignment poses a critical challenge for safe fine-tuning, as narrow task adaptation can induce broad safety degradation." |
| S2 | Gap / Challenge | Existing defenses cannot selectively block malicious learning while preserving benign task performance | Kaczer et al. (2025) trade-off | "Existing defenses either prevent all learning via always-on KL regularization or fail to mitigate harmful behavioral shifts through inference-time interventions alone." |
| S3 | Hypothesis & Method | Output-dissimilarity monitoring on canary prompts may enable selective defense via event-triggered KL regularization | PhaseGuard-KL design | "We investigate whether monitoring Jensen-Shannon divergence on a fixed set of safety canaries during fine-tuning can distinguish malicious from benign distribution shifts, thereby enabling selective KL regularization." |
| S4 | Core Result (Negative) | Trigger fires identically at step 20 for both malicious and benign tasks; no lambda satisfies both criteria | Table 1, Table 2, trigger step 20 | "Our experiments refute this hypothesis: the trigger fires identically at step 20 for both Security EM and OpSwap fine-tuning, activating KL for ~94% of training. No KL coefficient simultaneously satisfies our pre-registered safety (≤24.3% misalignment) and utility (≥43.7% exact match) criteria." |
| S5 | Broader Implication | Output-level monitoring cannot achieve selectivity; motivates gradient/representation-level alternatives | Chen et al. (2025); GradShield; GRASP | "This negative result demonstrates that output-distribution monitoring cannot discriminate the intent of fine-tuning-induced distribution shifts, identifying a fundamental limitation of output-level selective defense and motivating gradient-level or representation-level alternatives." |

### Introduction Outline (Complete)

The current introduction is well-structured but can be tightened with clearer paragraph roles and stronger gap-to-hypothesis transitions. The following paragraph-by-paragraph plan provides executable revision guidance:

| Paragraph | Role | Target Claim | Transition Logic | Required Evidence |
|-----------|------|-------------|------------------|-------------------|
| P1 (Current P1) | Big Picture / Problem Definition | Emergent misalignment is a newly discovered phenomenon where narrow fine-tuning induces broad safety degradation; this challenges safe LLM deployment | Establish stakes and real-world relevance | Betley et al. (2026); Turner et al. (2025); concrete examples of EM |
| P2 (Current P2) | Gap Identification | Current defenses fall into two categories: always-on KL (prevents all learning) and inference-time (less effective). Other gradient/representation methods exist but require prior safety knowledge or are imperfect. | Identify the specific gap: selective defense without pre-identified safety directions | Kaczer et al. (2025); He et al. (2024); explicit mention of gradient filtering, data interleaving, and representation anchoring as partial solutions |
| P3 (Current P3) | Hypothesis Statement | Output-dissimilarity monitoring could provide selectivity because malicious fine-tuning targets safety-relevant behaviors, which may intuitively cause larger shifts on safety probes than benign tasks | Explain the intuition behind the asymmetry assumption; set up testable hypothesis | Add one sentence grounding the intuition: "The intuition is that malicious fine-tuning, which targets safety-relevant behavioral changes, should cause disproportionately large shifts on safety probes..." |
| P4 (Current P4) | Method Preview | PhaseGuard-KL: event-triggered KL regularization via JS divergence monitoring on canary prompts with threshold-based activation | Bridge from hypothesis to concrete method | Method name, core mechanism, canary set, JS divergence, threshold trigger |
| P5 (Contribution Bullets) | Contribution Summary | (1) Experimental framework with pre-registered criteria; (2) Negative result ruling out output-level monitoring; (3) Broader implication for selective defense research | Consolidate paper's value as negative knowledge | Revised contribution bullets emphasizing experimental rigor and negative knowledge contribution |

### Recommended Storyline Arc

The recommended introduction narrative follows: **Big Picture → Gap → Hypothesis (with intuition) → Method Preview → Contribution Summary.** This arc ensures that:
- Readers immediately understand why the problem matters (P1).
- The specific gap is explicit and contextualized within existing work (P2).
- The hypothesis feels grounded rather than ad hoc (P3).
- The method is positioned as a concrete test of the hypothesis (P4).
- The negative result's scientific value is clearly framed (P5).

## Priority Revision Plan
```text
Stage 1 (today — ~2 hours):
[P0] Rewrite Abstract using 5-sentence blueprint (S1-S5) from Storyline section.
[P3] Reframe contribution bullets (Page 2) to emphasize experimental framework and negative knowledge.
[P4] Add one sentence grounding hypothesis asymmetry assumption (Introduction P3).

Stage 2 (this week — ~1 day compute + 2 hours writing):
[P0] Run OpSwap on 2 additional seeds (123, 456); report mean±std for exact match and trigger step.
[P2] Add 2-3 sentences in Section 3.2 justifying key hyperparameters (canary count, k, τ, monitoring frequency).

Stage 3 (before submission — ~2 hours writing):
[P1] Expand Section 4.4 Root Cause Analysis with 2-3 sentences connecting to theoretical safety-capability trade-off (Chen et al., 2025) and gradient/representation-level alternatives (GradShield, GRASP).
[P1] Add 2-3 sentences to Conclusion framing broader implications and referencing concrete future directions.
```

**Expected Impact After Fixes:**
- P0 multi-seed validation directly strengthens the core "identical triggering" claim from a single-point observation to a statistically robust finding.
- P1 literature connections elevate the paper from a single-method negative result to a well-positioned contribution in the broader safety-capability trade-off research area.
- P2-P4 writing improvements improve readability, defensibility, and contribution clarity without requiring additional experiments.

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective / Hypothesis | Setup (data / split / protocol / baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|------------------------|---------------------------------------------|---------|--------------|-----------------|--------------------|
| E1: Security EM (No-Defense) | Baseline measurement of EM under standard SFT | Qwen2.5-7B, Security EM dataset, LoRA r=32, 3 seeds | Misaligned rate | 48.61% ± 7.08% | Baseline for safety degradation established | — |
| E2: Security EM (Always-on KL) | Test if KL prevents EM at cost of utility | Qwen2.5-7B, Security EM dataset, LoRA r=32, λ=0.1, 3 seeds | Misaligned rate | 0.00% ± 0.00% | Always-on KL eliminates EM | Does not report utility cost on Security EM task itself |
| E3: Security EM (PhaseGuard-KL) | Test if event-triggered KL prevents EM | Qwen2.5-7B, Security EM dataset, LoRA r=32, λ=0.03, 3 seeds | Misaligned rate, Trigger step | 20.83% ± 7.22%, Step 20 | Passes Safety EM criterion (≤24.3%) | — |
| E4: OpSwap (No-Defense) | Baseline measurement of benign task performance | Qwen2.5-7B, OpSwap Tier 2, LoRA r=32, 1 seed | Exact match rate | 54.63% | Baseline for utility established | Single seed prevents variance reporting |
| E5: OpSwap (Always-on KL) | Test if KL prevents benign learning | Qwen2.5-7B, OpSwap Tier 2, LoRA r=32, λ=0.1, 1 seed | Exact match rate | 0.00% | Always-on KL destroys benign task | Single seed |
| E6: OpSwap (PhaseGuard-KL) | Test if event-triggered KL preserves benign learning | Qwen2.5-7B, OpSwap Tier 2, LoRA r=32, λ=0.03, 1 seed | Exact match rate, Trigger step | 22.78%, Step 20 | Fails OpSwap criterion (≥43.7%); Trigger identical to EM | Single seed |
| E7: Lambda Sweep (EM) | Test safety across λ values | Qwen2.5-7B, Security EM, λ ∈ {0.01, 0.02, 0.025, 0.03, 0.1}, 3 seeds | Misaligned rate | 36.11% → 0.00% | No λ simultaneously satisfies criteria | — |
| E8: Lambda Sweep (OpSwap) | Test utility across λ values | Qwen2.5-7B, OpSwap, λ ∈ {0.01, 0.02, 0.025, 0.03, 0.1}, 1 seed | Exact match rate | 54.44% → 0.19% | Sharp cliff at λ ∈ [0.02, 0.03] | Single seed |
| E9: Inference-time baselines (EM) | Compare PhaseGuard-KL to inference-time interventions | Qwen2.5-7B, Security EM, No-Defense fine-tuned | Misaligned rate | System Prompt: 29.17%, Best-of-8: 41.67% | Training-time defense outperforms inference-time | Single seed not reported |

### (b) Research-Theme Gap Diagnosis

The core research-theme claim—**"Output-dissimilarity monitoring cannot achieve selective defense for emergent misalignment"**—is empirically validated but lacks multi-seed stability verification for the benign task (OpSwap). Without this, the central finding of "identical triggering at step 20" is anchored on a single random seed for OpSwap, which reduces reproducibility confidence. Additionally, the paper does not evaluate alternative canary sets or JS divergence truncation parameters, leaving open whether the failure is specific to this monitoring configuration or general to all output-distribution-based methods.

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls / Baselines | Metrics | Success Criterion | Est. Cost | Expected Paper-Quality Gain |
|--------------|------------|----------------|---------------------|---------|-------------------|-----------|-----------------------------|
| Trigger stability across seeds (P0) | PhaseGuard-KL fires early for both malicious and benign tasks regardless of initialization | Run OpSwap on 2 additional seeds (123, 456); match setup with Security EM | None (replicate existing E6) | OpSwap exact match rate, Trigger step | Variance in trigger step ≤ ±5 steps; utility remains <43.7% | ~1 day compute (1x A100) | Validates core "identical triggering" finding; closes major reproducibility gap |
| Canary set sensitivity (P1) | Trigger timing and utility degradation vary significantly with different canary prompt sets | Evaluate 2 alternative canary sets (e.g., 10 prompts, 50 prompts) on OpSwap | Original 24-prompt canary set | JS divergence at step 5, Trigger step, OpSwap EM | Divergent trigger timing or preserved utility with alternative canaries | ~2 days compute | Tests if failure is specific to canary set size/composition |
| λ timing dynamics (P2) | Delayed trigger activation (e.g., step 50 instead of step 20) preserves more benign utility | Modify PhaseGuard-KL to trigger at later step (manual override); evaluate on OpSwap | Original step 20 trigger | OpSwap EM, Security EM misaligned rate | Later trigger achieves >43.7% OpSwap EM while maintaining <24.3% Security EM | ~0.5 day compute | Tests if trigger timing (not just trigger mechanism) is the bottleneck |

### (d) Traceability Rule Compliance
- P0 maps directly to Key Issue P0 (OpSwap single-seed limitation) and strengthens the "identical triggering" claim.
- P1 maps to Weakness 3 (under-justified hyperparameters) and tests the generalizability of the negative result.
- P2 maps to the Root Cause Analysis and provides deeper mechanistic insight into why trigger timing matters.

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|-------------------|-----|------------|----------------------|
| C1 | Principled method design with canary monitoring, JS divergence, and threshold-based triggering for event-triggered KL regularization | Kaczer et al. [1] (systematic in-training defense evaluation); Ponkshe et al. [2] (safety subspaces not linearly distinct) | `partially_overlapping` | Kaczer et al. already demonstrate that KL regularization impairs benign learning, establishing the safety-capability trade-off. The event-triggered monitoring design is a novel attempt to achieve selectivity, but the core mechanism (KL triggered by output divergence) overlaps with prior KL-based defense work. | High | Reposition as "experimental test of a specific selective defense hypothesis" rather than "novel method design" |
| C2 | Pre-registered success criteria enabling rigorous hypothesis testing of selective defense | Davies et al. [3] (limitations of pointwise defenses); Chen et al. [4] (theoretical safety-capability trade-offs) | `supported` | The use of pre-registered dual criteria (safety ≤24.3%, utility ≥43.7%) for unambiguous hypothesis testing is a clean experimental design choice not explicitly replicated in prior negative-result papers on selective defense. | Medium | No repositioning needed; maintain as a methodological strength |
| C3 | Comprehensive experiments refuting the hypothesis that output-dissimilarity monitoring can selectively distinguish malicious from benign fine-tuning | Davies et al. [3] (fundamental limits of pointwise detection); Chen et al. [4] (safety-capability trade-offs); Wilhelm et al. [5] (activation-based monitoring shows discriminative potential) | `partially_overlapping` | The negative result itself is novel for output-level JS divergence monitoring. However, Davies et al. [3] already demonstrate fundamental limitations of pointwise detection for fine-tuning misuse, and Chen et al. [4] provide theoretical grounding for the safety-capability entanglement. The finding is consistent with these prior works. | High | Frame as "empirical evidence for a specific monitoring modality" consistent with broader theoretical predictions |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch / Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|----------------|--------------|----------------------|-------------------|------------------------|-------------------|
| Root: Emergent Misalignment Defenses | | | | | |
| ├── Branch 1: In-Training Regularization | | | | | |
| │   ├── Leaf 1.1: Always-on KL Regularization | Kaczer et al. [1] | KL divergence penalty applied uniformly throughout training | This paper tests event-triggered (conditional) KL instead of always-on | Low risk; KL trade-off well-established |
| │   ├── Leaf 1.2: Data Interleaving | Kaczer et al. [1] | Mixing safety data with fine-tuning data preserves alignment | This paper does not use data-level interventions | Moderate risk; interleaving achieves better trade-off |
| │   └── Leaf 1.3: Gradient Filtering | He et al. [6] | Harmful training data has distinct gradient signatures | This paper uses output-distribution signals, not gradients | Low risk; orthogonal signal modality |
| ├── Branch 2: Representation-Level Defenses | | | | | |
| │   ├── Leaf 2.1: Safe Subspace Projection | Hsu et al. [7]; Ponkshe et al. [2] | Safety alignment resides in identifiable weight-space subspaces | This paper operates at output level, not weight space | Moderate risk; Ponkshe shows subspaces not linearly distinct |
| │   └── Leaf 2.2: Spurious Correlation Removal | Gilligan-Lee et al. [8] | Fine-tuning acquires spurious correlations with latent factors | This paper does not address representation-level correlations | Low risk; different abstraction level |
| └── Branch 3: Detection & Monitoring Methods | | | | | |
|     ├── Leaf 3.1: Pointwise Input Detection | Davies et al. [3] | Individual training samples can be flagged as harmful | This paper monitors aggregate output distribution, not per-sample | Low risk; Davies shows pointwise detection has fundamental limits |
|     └── Leaf 3.2: Activation-Based Monitoring | Wilhelm et al. [5] | Internal activations distinguish reward-hacking from benign behavior | This paper uses output logits, not internal activations | Moderate risk; Wilhelm shows internal signals ARE discriminative |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem / Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|-------------------|-------------|------------------------|------------------|-------------------------|
| [1] Kaczer et al. (2025) | In-training defenses for EM; 4 malicious tasks + 1 benign task | KL regularization, L2 feature distance, SafeLoRA, data interleaving | Establishes KL safety-capability trade-off on same benchmarks (OpSwap) | Evaluates always-on methods; does not test event-triggered conditional KL | Contextualizes C1; does not overlap the event-triggered novelty |
| [3] Davies et al. (2025) | Fundamental limits of pointwise fine-tuning API defenses | Entropy-based covert attacks evading per-sample detection | Demonstrates that output-level monitoring has fundamental detection limits | Focuses on inference-time pointwise detection, not training-time monitoring | Supports C3's negative finding; strengthens broader implication |
| [4] Chen et al. (2025) | Theoretical safety-capability trade-offs in fine-tuning | Mathematical analysis of data similarity, context overlap, loss landscape | Provides theoretical grounding for why output-level signals cannot achieve selectivity | Theoretical; does not provide empirical monitoring evaluation | Provides theoretical context for C3's empirical finding |
| [5] Wilhelm et al. (2026) | Activation-based monitoring for reward hacking detection | Sparse autoencoders on residual stream activations | Contrasts output-level (this paper) with activation-level monitoring | Shows internal activations CAN distinguish malicious from benign behavior | Highlights that the negative result is specific to output-level, not all monitoring |
| [8] Gilligan-Lee et al. (2026) | Unsupervised spurious correlation removal during fine-tuning | GRASP: gradient projection of associated spurious patterns | Gradient-level signals distinguish harmful correlations | Operates at gradient level; shows gradient-based methods preserve task utility | Demonstrates alternative approach that achieves better trade-off |

**Contribution-level Novelty Conclusion:** C1 (event-triggered KL design) is `partially_overlapping` with prior KL-based defense work, as Kaczer et al. [1] already establish the fundamental trade-off. C2 (pre-registered experimental framework) is `supported` as a methodological contribution. C3 (negative result for output-level monitoring) is `partially_overlapping` because Davies et al. [3] and Chen et al. [4] provide prior evidence for the limitations of output-level detection, while Wilhelm et al. [5] and Gilligan-Lee et al. [8] demonstrate that gradient/activation-level signals retain discriminative power. The residual novelty lies in the specific empirical evaluation of JS divergence monitoring on canary prompts as a selective defense mechanism.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)

Emergent Misalignment Defenses (Root)
├── Branch 1: In-Training Regularization
│   ├── Leaf 1.1: Always-on KL [1] — establishes safety-capability trade-off
│   ├── Leaf 1.2: Data Interleaving [1] — preserves utility via safety data mixing
│   └── Leaf 1.3: Gradient Filtering [6] — identifies harmful data via gradient signatures
├── Branch 2: Representation-Level Defenses
│   ├── Leaf 2.1: Safe Subspace Projection [2][7] — safety subspaces (shown non-distinct)
│   └── Leaf 2.2: Spurious Correlation Removal [8] — gradient projection preserves utility
└── Branch 3: Detection & Monitoring Methods
    ├── Leaf 3.1: Pointwise Input Detection [3] — fundamental limits of per-sample monitoring
    └── Leaf 3.2: Activation-Based Monitoring [5] — internal signals ARE discriminative
    └── [THIS PAPER] Output-Level JS Monitoring — refutes selectivity for output distributions
```

## References
[1] In-Training Defenses against Emergent Misalignment in Language Models 2508.06249

[2] Safety Subspaces are Not Linearly Distinct: A Fine-Tuning Case Study 2505.14185

[3] Fundamental Limitations in Pointwise Defences of LLM Finetuning APIs 2502.14828

[4] Fundamental Safety-Capability Trade-offs in Fine-tuning Large Language Models 2503.20807

[5] Monitoring Emergent Reward Hacking During Generation via Internal Activations 2603.04069

[6] What is in Your Safe Data? Identifying Benign Data that Breaks Safety 2404.01099

[7] Safe lora: the silver lining of reducing safety risks when fine-tuning large language models 2405.16833

[8] Unsupervised Identification and Removal of Spurious Correlations During Fine-Tuning 2605.27676

[9] GradShield: Alignment Preserving Finetuning 2605.14194

## Scores
Final Score: 5.5/10

**Scoring Rationale (Research Value + Novelty + Validity):**
The paper makes a valuable negative contribution by rigorously testing and refuting the hypothesis that output-dissimilarity monitoring can enable selective defense against emergent misalignment. The experimental design is clean, pre-registered criteria are unambiguous, and the root cause analysis is logically sound. However, the score is reduced due to three factors: (1) the OpSwap benign task uses only a single seed, leaving the core "identical triggering at step 20" claim vulnerable to seed-dependent variance (P0 issue); (2) the novelty of the negative result partially overlaps with prior theoretical and empirical work on pointwise detection limits and safety-capability trade-offs, though the specific evaluation of JS divergence on canary prompts provides useful domain-specific evidence; and (3) the manuscript under-frames the broader scientific value of this negative result and lacks connections to gradient-level/representation-level alternatives that remain promising.

Post-Revision Target: [6.5, 7.5]/10
**Achievable if:** (a) P0 multi-seed OpSwap validation is completed, confirming trigger timing stability; (b) Root Cause Analysis and Conclusion are expanded to explicitly connect to Chen et al. [4], Davies et al. [3], and gradient/representation alternatives [5][8][9]; (c) Contribution bullets and Abstract are reframed to emphasize the negative knowledge value rather than the failed method design. These targeted fixes would significantly improve reproducibility confidence, literature positioning, and contribution framing without requiring fundamentally new experiments.