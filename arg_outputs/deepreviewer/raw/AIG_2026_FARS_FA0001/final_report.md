## Summary
This paper proposes **canary-controlled adaptive safe-data interleaving**, a closed-loop framework for mitigating emergent misalignment (EM) during LLM fine-tuning. The core mechanism monitors EM risk using canary prompts evaluated every $K$ training steps, applies EMA smoothing to reduce noise, and adjusts the safe-data interleaving ratio via a threshold-based policy with hysteresis. Evaluated on the Security EM benchmark with Qwen2.5-7B-Instruct, the method achieves 5.39% General %Misaligned compared to 7.15% for fixed 5% interleaving—a 25% relative improvement—with 4× lower cross-seed variance. Ablation studies investigate the contributions of adaptive timing, feedback timeliness, and EMA smoothing.

**Key audit findings:** The canary-controlled framework represents a novel application of closed-loop feedback control to EM defense (C1: supported). However, the claimed 25% improvement (C2) is partially confounded by the method's substantially higher average safe-data volume (13% vs 5% for the fixed baseline). Most critically, the Shuffled $p_t$ ablation reveals only 9% degradation when timing is randomized while preserving total safe-data volume, indicating that total safe-data quantity—not adaptive timing per se—is the dominant factor in performance gains. The conclusion that "adaptive timing provides value beyond average interleaving ratio" (C3) is partially overlapping with volume effects and requires more careful bounding. The paper's efficiency trade-off is acknowledged in the Discussion but insufficiently integrated into the main narrative, abstract, and contribution claims.

## Strengths
1.  **Novel Feedback Control Mechanism (C1):** The paper introduces a clear, well-defined closed-loop framework for EM defense using canary prompts, EMA smoothing, and hysteresis. This represents a conceptually novel application of control-theory principles to in-training safety regulation, which is not explored in prior work like Kaczer et al. (2025) that focuses on static regularization.
2.  **Strong Empirical Results on Target Metric:** The method achieves meaningful EM suppression (5.39% General %Misaligned vs 7.15% for fixed 5%), demonstrating that dynamic safe-data scheduling can outperform static baselines on the Security EM benchmark.
3.  **Comprehensive Ablation Studies:** The ablation suite (Fixed $p=\bar{p}$, Delayed, Shuffled $p_t$, No-EMA) provides valuable insights into which components of the controller matter. The "Shuffled $p_t$" result is particularly informative, as it reveals the relative importance of timing vs total safe-data volume.
4.  **Honest Limitation Reporting:** The Discussion section candidly acknowledges the weak canary-general correlation ($r=0.31$), the single-benchmark evaluation, and the higher safe-data volume (13% vs 5%). This self-criticality is a positive sign of scientific rigor.
5.  **Clear Methodological Specification:** The controller parameters ($\alpha, r_{high}, r_{low}, \delta_{\uparrow}, \delta_{\downarrow}, p_{min}, p_{max}, K$) are fully specified, and Algorithm 1 provides a clean, reproducible training procedure.

## Weaknesses
**W1: Confounded Efficiency Trade-off in Performance Claims (Major)**
The main result claims a 25% relative improvement over fixed 5% interleaving, but the canary-controlled method uses a substantially higher average safe-data volume ($\bar{p}_t \approx 13\%$ vs $5\%$). This translates to approximately 2.6× more training compute. The abstract, introduction, and contribution claims frame this as an unqualified 25% improvement, masking the significant efficiency cost. The comparison is inherently unfair unless a fixed 15% baseline is included to isolate the benefit of adaptive timing from total safe-data quantity.

**W2: Timing vs Volume Causal Overreach (Major)**
The third contribution claim states that "adaptive timing provides value beyond average interleaving ratio," citing 36% degradation when the fixed $p=\bar{p}$ variant is used. However, the Shuffled $p_t$ ablation shows only 9% degradation when timing is randomized while preserving the exact same total safe-data volume. This reveals that total safe-data quantity is the dominant factor, and the "timing benefit" accounts for at most a small fraction of the total gain. The current narrative heavily emphasizes timing as the primary innovation, which overstates the evidence.

**W3: Controller Behavior Suggests Monotonic Ramp Rather Than Adaptive Decision-Making (Major)**
Figure 2 shows that all three random seeds reach the maximum interleaving ratio ($p_{\max}=0.20$) by training completion, despite different initial risk trajectories. Combined with the weak canary-general correlation ($r=0.31$), this raises the possibility that the controller is not making nuanced, bidirectional adaptive decisions, but instead monotonically ramping safe-data volume toward $p_{\max}$. If the controller simply drives $p_t$ upward over time, the novelty of the adaptive mechanism is significantly reduced.

**W4: Single-Benchmark Evaluation (Minor)**
All experiments are conducted on the Security EM benchmark using a single model (Qwen2.5-7B-Instruct). While this benchmark is standard for EM research, the lack of cross-benchmark evaluation limits the generalizability of the claims.

**W5: Missing Fixed High-Ratio Baseline (Minor)**
The paper compares against Fixed 5% interleaving but does not include a fixed 15% (or 13%) baseline. Without this, readers cannot determine whether the 25% improvement over Fixed 5% is due to adaptive timing or simply from using more safe data. A fixed baseline matching the canary method's average $p_t$ is essential for a fair comparison.

## Key Issues
1.  **Unfair Comparison Baseline (Validity Risk):** The primary baseline is Fixed 5% interleaving. The proposed method achieves an average interleaving ratio of ~13-15.5%. Without a Fixed 15% (or Fixed 13%) baseline, the paper cannot distinguish whether the performance gain stems from the adaptive mechanism or simply from using more safe data. The ablation study tests Fixed $p=\bar{p}$ at 0.155, which shows 36% degradation, but this is compared against the full method under identical conditions. A direct Fixed 13-15% baseline in Table 1 is crucial for fairness.
2.  **Overstated "Timing" Novelty (Research Value Risk):** The paper's strongest novelty claim is that adaptive timing provides value beyond average volume. The evidence for this is the Fixed $p=\bar{p}$ ablation. However, the Shuffled $p_t$ ablation degrades by only 9%, indicating that *most* of the value comes from volume, and *only a small fraction* comes from timing. The narrative currently inverts this, treating volume as secondary and timing as primary. This misrepresentation risks a fundamental rejection for overstated contributions.
3.  **Controller Mechanics Ambiguity (Interpretability Risk):** The controller's trajectory (monotonically ramping to $p_{\max}$ across all seeds) and the weak canary correlation ($r=0.31$) suggest the "adaptive" aspect might be a slow, coarse ramp rather than a responsive, bidirectional feedback loop. This mechanism ambiguity needs explicit discussion. If the controller just ramps up because risk eventually exceeds $r_{high}$ and never drops below $r_{low}$, the novelty of the "canary" monitoring is weakened.
4.  **Missing Efficiency Analysis (Practicality Risk):** The step-counting convention (safe-data steps do not decrement target count $T$) means higher $p_t$ directly increases total training compute and time. The paper mentions "training overhead" in the introduction but then claims the method "minimizes training overhead," which directly contradicts the empirical observation that the method uses ~2.6× more safe data.

## Actionable Suggestions
1.  **Add a Fixed High-Ratio Baseline (Must):** Include a "Fixed 15%" or "Fixed 13%" baseline in Table 1 to match the average safe-data volume of the canary-controlled method. This is essential to isolate the benefit of adaptive timing from the effect of increased safe-data quantity. If the canary method outperforms Fixed 15%, the timing claim is significantly strengthened. If it performs similarly, the contribution should be reframed.
2.  **Reframe Contribution Claims to Acknowledge Volume Dominance (Must):** Revise the abstract, introduction, and conclusion to explicitly state that total safe-data quantity is the dominant factor in performance gains, with adaptive timing providing supplementary benefits. Use the revised "Shuffled $p_t$" interpretation in the final version to honestly reflect the ablation evidence.
3.  **Clarify Step-Counting and Compute Overhead Early (Must):** In Section 3.1 (Problem Setup), explicitly define the step-counting convention: safe-data steps do not decrement the target dataset counter $T$. State clearly that higher average $p_t$ values increase total training compute proportionally. Remove the claim that the method "minimizes training overhead" and replace it with "concentrates intervention during high-risk phases."
4.  **Analyze Controller Ramp Behavior (Should):** In Section 4.4 (Controller Behavior Analysis), add a discussion of whether the controller's trajectory is a monotonic ramp toward $p_{\max}$ or a nuanced, bidirectional adaptation. Analyze whether the canary risk ever drops below $r_{low}$, causing the controller to actively reduce safe-data volume. This addresses the "ramp vs adapt" ambiguity raised by the empirical evidence.
5.  **Improve Abstract and Conclusion Bounding (Should):** Update the abstract and conclusion to mention the efficiency trade-off (13% vs 5% safe-data volume). This ensures that the main takeaway includes both the performance gain and its compute cost, improving scientific objectivity.

## Storyline Options + Writing Outlines
**Core Narrative Shift:** The current narrative heavily emphasizes "adaptive timing" as the primary innovation. The strongest revision strategy is to pivot the narrative to frame the paper as an **intelligent safe-data volume scheduler** that applies a simple, robust feedback controller to achieve stronger EM suppression than fixed-ratio methods, while openly acknowledging that total safe-data quantity is the dominant factor and timing is a secondary benefit.

### (a) Abstract Outline (4-5 Sentences)
- **S1 (Problem & Domain):** Fine-tuning LLMs on narrow, domain-specific tasks can induce emergent misalignment (EM) across unrelated prompts, posing a critical safety risk even when training data appears benign.
- **S2 (Challenge with Prior Defenses):** Safe-data interleaving mixes benign examples with target data to preserve alignment, but existing approaches use fixed interleaving ratios that may be suboptimal as EM risk fluctuates during training.
- **S3 (Prior Gap & Proposed Solution):** We propose canary-controlled adaptive safe-data interleaving, a closed-loop framework that monitors EM risk via canary prompts and dynamically adjusts the safe-data volume using a threshold-based controller with hysteresis.
- **S4 (Key Result & Efficiency Trade-off):** On the Security EM benchmark with Qwen2.5-7B-Instruct, our method achieves 5.39% General %Misaligned compared to 7.15% for fixed 5% interleaving, with 4× lower cross-seed variance, albeit at a higher average safe-data volume (13% vs 5%).
- **S5 (Evidence of Mechanism):** Ablation studies confirm that the total safe-data quantity is the dominant factor in performance gains, while adaptive timing and EMA smoothing provide supplementary stability and additional suppression benefits.

### (b) Introduction Outline (Paragraph-by-Paragraph)
- **P1 (Big Picture / Problem):** Establish that LLM fine-tuning on narrow tasks causes broad, emergent misalignment. Cite Betley et al. (2026) and Turner et al. (2025). *Role: Define the safety threat of EM.*
- **P2 (Prior Defenses & Limitations):** Introduce current defenses, specifically safe-data interleaving (Kaczer et al., 2025). Point out that these methods typically use static parameters, which is suboptimal because EM risk exhibits phase-transition-like dynamics. *Role: Identify the gap in static safe-data scheduling.*
- **P3 (Proposed Method / Intuition):** Introduce canary-controlled adaptive interleaving. Explain the intuition: just as PID controllers adjust parameters based on feedback, we can monitor EM risk during training and adjust safe-data volume in real-time. *Role: Introduce the closed-loop feedback concept.*
- **P4 (Key Results & Bounded Claims):** State the empirical achievements: 25% improvement over Fixed 5% on Security EM. *Crucially*, acknowledge that the method uses a higher average safe-data volume (13% vs 5%) and that total safe-data quantity is the dominant performance driver, with adaptive timing offering a supplementary benefit. *Role: Present evidence while honestly bounding the efficiency trade-off.*
- **P5 (Contributions):**
    - A closed-loop safe-data scheduling framework using canary prompts and threshold-based control.
    - Empirical demonstration of stronger EM suppression and lower variance on Security EM, with transparent reporting of the safe-data volume trade-off.
    - Ablation studies quantifying the relative contributions of total safe-data quantity, adaptive timing, and controller smoothing.

## Priority Revision Plan
| Priority | Action | Effort | Expected Impact |
|---|---|---|---|
| **P0 (Must)** | Add a "Fixed 15%" (or matching the canary method's average $p_t$) baseline to Table 1. | High (requires new experiment) | Validates or bounds the "timing value" claim; addresses the most critical fairness concern. |
| **P0 (Must)** | Revise Abstract, Intro, and Conclusion to acknowledge the efficiency trade-off: the method uses ~2.6x more safe data (13% vs 5%). | Low (writing fix) | Corrects the unbounded performance claims; improves scientific objectivity. |
| **P0 (Must)** | Reframe the narrative (and Section 4.3) to state that total safe-data quantity is the dominant performance driver, based on the 9% degradation of the Shuffled $p_t$ variant. | Medium (writing fix) | Corrects the causal overreach regarding the novelty of adaptive timing. |
| **P1 (Should)** | In Section 3.1, explicitly define the step-counting convention: safe-data steps do not decrement the target dataset counter $T$. | Low (writing fix) | Improves reproducibility and prevents confusion about compute costs. |
| **P1 (Should)** | In Section 4.4, add an analysis of the controller trajectory: discuss whether the controller monotonically ramps to $p_{\max}$ or performs nuanced, bidirectional adjustments. | Low (analysis/writing) | Improves the interpretability of the controller's actual mechanism. |
| **P2 (Nice)** | Evaluate the method on an additional EM-inducing benchmark to demonstrate generalizability. | High (requires new experiment) | Strengthens the claim that the framework applies broadly to EM defense. |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Canary-controlled vs No Defense / Fixed 5% | Qwen2.5-7B-Instruct, Security EM (5400 ex.), 3 seeds. | Gen/In-Dom %Misaligned, %Incoherent, Avg $p_t$ | 5.39% vs 7.15% vs 19.37%. 4x lower variance. | Canary achieves better EM suppression than Fixed 5%. | Avg $p_t$ is 13% (canary) vs 5% (fixed). Efficiency trade-off is not explicitly tested against a Fixed 13% baseline. |
| E2 | Fixed $p=\bar{p}$ (Avg 0.155) | Same setup, identical avg safe-data ratio as canary method. | Gen %Misaligned | 7.18% (vs 5.26% full). 36% degradation. | Adaptive timing provides some value beyond fixed ratio. | The 36% degradation is still a significant gap, leaving room for volume-based explanations. |
| E3 | Delayed Controller (D=5) | Delay updates by 5 cycles. | Gen %Misaligned | 8.35% (+59%). Avg $p_t$ drops to 0.045. | Feedback timeliness is critical to capture early risk. | N/A |
| E4 | Shuffled $p_t$ | Shuffle $p_t$ sequence, preserving total volume. | Gen %Misaligned | 5.75% (+9% degradation). | Total safe-data volume is the dominant performance factor. | This finding challenges the "timing is primary" narrative and should be highlighted more. |
| E5 | No-EMA | Remove smoothing and hysteresis. | Gen %Misaligned | 7.63% (+45%). Avg $p_t$ drops to 0.056. | EMA/hysteresis stabilize controller and maintain high safe-data volume. | N/A |
| E6 | Canary-General Correlation | Pearson correlation between 20 canary prompts and 2400 general samples. | Pearson $r$ | $r = 0.31$ (weak positive). | Canary is an imperfect directional proxy for general EM risk. | Suggests controller may be ramping rather than making nuanced adjustments. |

### (b) Research-Theme Gap Diagnosis
The core research-value claim is that a closed-loop feedback controller can optimally schedule safe-data interleaving to mitigate emergent misalignment more effectively than static approaches. The gap in the current evidence is the lack of a direct, compute-matched baseline (e.g., Fixed 13-15%) to definitively separate the value of *adaptive timing* from the value of *increased safe-data volume*. While the Fixed $p=\bar{p}$ ablation supports the timing claim, the Shuffled $p_t$ ablation (only 9% degradation) reveals that timing is a secondary driver. The research value is partially obscured by this confounded efficiency trade-off.

### (c) Proposed Research Experiments (P0/P1/P2)
| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Expected Quality Gain |
|---|---|---|---|---|---|---|---|
| **Timing Value (P0)** | Canary outperforms fixed ratio even when matched for average safe-data volume. | Run fixed interleaving at $p=0.13$ and $p=0.155$. | Fixed 13%, Fixed 15.5%. | Gen %Misaligned, %Incoherent | Canary beats Fixed 15.5% (or closely matches). | 1-2 GPU days | Closes the biggest validity hole; validates the core novelty claim. |
| **Controller Mechanics (P1)** | The controller ramps to $p_{max}$ rather than adjusting bidirectionally. | Plot exact $p_t$ trajectory and count direction changes (up vs down). | None. | Direction switches, final $p_t$ | Clarify if it is a ramp or adaptive. | Near-zero | Improves interpretability and honest self-assessment of the mechanism. |
| **Generalizability (P2)** | Adaptive scheduling helps across different EM-inducing datasets. | Evaluate on a second EM benchmark (e.g., Bad Medical/Financial advice). | Fixed 5%, Fixed 15%. | Gen %Misaligned | Consistent gains over static baselines. | 1-2 GPU days | Broadens external validity of the method. |

### (d) Traceability
P0 directly addresses the primary validity risk (W1) and enables a sound judgment of the timing novelty (C3). P1 clarifies the underlying mechanism (W3). P2 addresses the single-benchmark limitation (W4).

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board
| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Introduces a canary-controlled adaptive interleaving framework that dynamically adjusts the safe-data ratio based on real-time behavioral signals. | [1], [4] | supported | First to use canary prompts combined with a threshold-based controller to dynamically modulate safe-data interleaving for EM defense. | High | None |
| C2 | Achieves 25% relative improvement (5.39% vs 7.15%) over fixed 5% interleaving. | [1] | partially_overlapping | The gain is partially explained by the substantially higher average safe-data volume (13% vs 5%). | High | Must explicitly bound the claim by acknowledging the ~2.6x higher safe-data cost. |
| C3 | Adaptive timing provides value beyond the average interleaving ratio (36% degradation with fixed timing). | [1] | partially_overlapping | The "Shuffled $p_t$" ablation shows only 9% degradation, revealing that total safe-data quantity is the dominant factor, and timing is a secondary driver. | High | Reposition timing as a supplementary stabilizing mechanism rather than the primary gain source. |

### (9B) Related-Work Taxonomy Matrix
| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| In-Training EM Defense | Static Interleaving | [1] | Fixed safe-data ratio throughout training. | Fixed ratio vs. Adaptive threshold-based ratio. | Low (Direct baseline) |
| In-Training EM Defense | Threshold-Triggered Scheduling | [4] | Safety drift triggers corrective replay/intervention. | Continual domain adaptation vs. Single-task EM fine-tuning. | Medium (Similar control-theory principle applied to safety) |
| In-Training EM Defense | Dynamic Intra-Example Shaping | [6] | Safety risk varies within a single training example. | Token-level intra-example loss weighting vs. Step-level inter-example data scheduling. | Low (Different granularity of adaptation) |

### (9C) Head-to-Head Comparison Matrix
| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | EM defense in narrow fine-tuning | Static safe-data interleaving at fixed ratios. | Interleaving safe data to mitigate EM. | Kaczer et al. (2025) only evaluates fixed ratios; this paper introduces closed-loop adaptive scheduling. | Establishes the static baseline and validates that interleaving works. |
| [4] | Cumulative safety erosion in continual adaptation | Fisher-based projection + threshold-triggered corrective replay. | Uses a safety monitor to trigger interventions. | SafeAnchor uses a threshold monitor for replay, but operates on continual adaptation across domains, not step-level interleaving for EM. | Shows that threshold-triggered feedback is a valid mechanism for safety, supporting the theoretical grounding of the controller. |
| [6] | General safety degradation in fine-tuning | STAR-DSS: Token-level safety shaping using partial response scoring. | Dynamically adjusts intervention based on safety signals. | STAR-DSS operates intra-example (token-level loss weighting), whereas this paper operates inter-step (data scheduling). | Demonstrates the value of dynamic safety shaping, but the different granularity avoids direct overlap. |

### Contribution-level Novelty Conclusion
C1 is **supported**: the application of a canary-driven, threshold-based feedback controller to dynamic safe-data scheduling for emergent misalignment is a genuinely novel contribution. C2 is **partially_overlapping**: the 25% improvement over Fixed 5% is real but heavily confounded by a 2.6× increase in safe-data volume. This claim requires strict repositioning to include a compute-matched baseline or explicit efficiency caveats. C3 is **partially_overlapping**: the evidence that timing matters (Fixed $p=\bar{p}$) is undermined by the Shuffled $p_t$ result (only 9% degradation). The "timing beyond volume" narrative overstates the incremental value; a more accurate positioning is that the controller acts as a robust, high-volume safe-data scheduler with supplementary adaptive stability.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)
```text
In-Training Safety & EM Mitigation (Root)
├── Branch 1: Static Regularization & Constraints
│   ├── Leaf 1.1: KL/Feature Space Constraints [1]
│   └── Leaf 1.2: Subspace Projection (SafeLoRA) [1]
├── Branch 2: Data-Based Defense
│   ├── Leaf 2.1: Static Safe-Data Interleaving [1]
│   └── Leaf 2.2: Adaptive/Threshold-Triggered Scheduling (This Paper, [4])
└── Branch 3: Representation & Token Constraints
    ├── Leaf 3.1: Logit/Token Constraints (PACT, STR)
    └── Leaf 3.2: Intra-Example Dynamic Shaping (STAR-DSS [6])
```

## References
[1] In-Training Defenses against Emergent Misalignment in Language Models 2508.06249

[2] SafeAnchor: Preventing Cumulative Safety Erosion in Continual Domain Adaptation of Large Language Models 2604.17691

[3] Shape it Up! Restoring LLM Safety during Finetuning 2505.17196

[4] Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs 2502.17424

[5] Model Organisms for Emergent Misalignment 2506.11613

[6] Feedback Control for Online Training of Neural Networks 1911.07710

[7] Responsive Safety in Reinforcement Learning by PID Lagrangian Methods 2007.03964

[8] Rethinking Safety in LLM Fine-tuning: An Optimization Perspective 2508.12531

[9] SafeCtrl-RL: Inference-Time Adaptive Behaviour Control for LLM Dialogue via RL-Driven Prompt Optimisation 2605.25984

[10] Reinforcement Learning with Backtracking Feedback 2602.08377

## Scores
**Final Score:** 5.5/10

**Post-Revision Target:** [7.0, 8.0]/10

**Scoring Rationale:**
The paper presents a conceptually interesting and well-executed closed-loop framework for adaptive EM defense (Strength: Novelty C1). The empirical performance is clear, and the ablation suite provides meaningful mechanistic insights. However, the research value is currently undermined by two significant validity and narrative issues (Weaknesses W1, W2):
1. The 25% improvement over Fixed 5% is heavily confounded by a ~2.6× increase in safe-data volume (efficiency trade-off), which is insufficiently integrated into the main contribution claims.
2. The strongest novelty claim—that timing provides value beyond volume—is contradicted by the "Shuffled $p_t$" ablation (only 9% degradation), which reveals that total safe-data quantity is the dominant performance driver.

These issues lower the score from the potential 7-8 range to a solid 5.5. The core ideas and code are valuable, but the paper requires a significant reframing and one critical additional baseline (Fixed 13-15%) to be fully defensible.

### ASCII Diagram — Paper Structure & Evidence Map
```text
[Claim: Adaptive timing provides value beyond safe-data volume]
    -> [Evidence: Fixed p=avg ablation shows 36% degradation]
    -> [Contradiction: Shuffled pt ablation shows only 9% degradation]
    -> [Risk: "Timing" novelty is overstated; volume is the dominant driver]
    -> [Fix: Add Fixed 15% baseline + reframe timing as secondary benefit]
```

### ASCII Diagram — Revision Strategy Roadmap
```text
[P0: Add Fixed 15% baseline] -> [Isolate timing benefit] -> [Validate timing claim]
[P0: Reframe narrative] -> [Acknowledge volume dominance] -> [Correct contribution claims]
[P0: Add efficiency bounds] -> [Update Abstract/Intro/Conclusion] -> [Improve objectivity]
[P1: Analyze controller ramp] -> [Clarify controller mechanics] -> [Strengthen self-criticism]
```

### Page Coverage Audit
| Page | Annotation Count | Coverage Status | Skip Reason |
|---|---|---|---|
| 1 (Abstract, Intro P1-4) | 3 | Covered | N/A |
| 2 (Intro P5 Contributions, Related Work) | 1 | Covered | Related Work is a standard literature survey, lower defect density. |
| 3 (Method: Problem, Risk Estimation) | 1 | Covered | N/A |
| 4 (Method: Controller, Training Proc) | 1 | Covered | N/A |
| 5 (Experiments: Setup, Results, Ablations) | 2 | Covered | N/A |
| 6 (Experiments: Controller Analysis) | 1 | Covered | N/A |
| 7 (Discussion, Conclusion) | 2 | Covered | N/A |
| **Total** | **11** | **Full Core Coverage** | **N/A** |