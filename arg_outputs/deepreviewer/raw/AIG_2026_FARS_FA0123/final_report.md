## Summary
# Final Review Report

## Summary

This paper investigates the "repetition advantage" in long chain-of-thought (CoT) supervised fine-tuning (SFT), specifically addressing a potential compute confound identified in prior work (Kopiczko et al., 2026). The authors introduce **token-budget matching**, a methodological intervention that isolates the effect of data repetition by ensuring that the token count in the repetition condition matches that of the data scaling baseline. 

The study compares three conditions: (A) Data Scaling (unique data), (B) Step-Matched Repetition (the original confounded setup), and (C) Token-Matched Repetition (the proposed controlled setup). The central finding is that the repetition advantage not only persists but is significantly amplified (6.33× ratio on aggregate Pass@k) under token-matched conditions, definitively refuting the hypothesis that the advantage is a mere artifact of extra compute. The authors further identify a behavioral mechanism: repetition training drastically improves the model's termination rate (87–91% vs. 29–48%), causing models to produce complete, decisive reasoning chains rather than just more accurate partial chains.

The paper is well-motivated, cleanly executed, and provides a strong methodological contribution to the evaluation of SFT protocols. While there are minor issues regarding the completeness of the FLOPs proxy, causal overclaims regarding the termination mechanism, and scope limitations (single model size), the core findings are robust and significant.

## Strengths
1. **Strong, Well-Motivated Research Question:** The paper correctly identifies a subtle but critical confound in prior work (Kopiczko et al., 2026). The observation that step-matching in long-CoT SFT inherently involves a token-count mismatch is insightful and directly impacts the validity of previous "repetition advantage" claims.

2. **Clean Methodological Intervention:** The introduction of token-budget matching via early stopping is a simple, elegant, and rigorously executed solution. The authors verify this matching not just via token counts (0.50% deviation) but also via a FLOPs proxy ($\Sigma L^2$, 0.56% deviation), demonstrating high attention to experimental control.

3. **Significant and Surprising Empirical Findings:** The discovery that controlling for compute actually *amplifies* the repetition advantage (6.33×) is a highly non-trivial result. It shifts the narrative from "repetition is just a compute hack" to "repetition fundamentally alters learning dynamics."

4. **Deep Mechanistic Analysis:** The decomposition of accuracy into Termination Rate and Conditional Accuracy (Table 4) is a standout contribution. It provides a concrete, falsifiable explanation for *why* repetition works (teaching the model to finish its reasoning rather than just reasoning better) and challenges the intuition that repetition improves answer quality.

5. **High Reproducibility Standards:** The paper clearly specifies the model (Qwen2.5-1.5B), data (NuminaMath-CoT, specific splits), hyperparameters, and evaluation metrics. The inclusion of multi-seed variance reporting (mean ± std over 3 seeds) is a positive step toward statistical reliability.

## Weaknesses
1. **Incomplete FLOPs Proxy for Compute Matching (Major):** While the authors introduce a FLOPs proxy based on the sum of squared sequence lengths ($\Sigma L^2$), this metric only captures the self-attention compute for the response tokens. It ignores the cross-attention compute between the response tokens and the prompt tokens. Since the prompt lengths are constant, this might seem like a minor confound, but the interaction term ($2 \times L_{prompt} \times L_{response}$) scales linearly with response length and is a significant portion of total attention FLOPs. By ignoring the prompt-response interaction, the FLOPs proxy is technically incomplete. A more robust proxy would use $\Sigma (L_{prompt} + L_{response})^2$.

2. **Causal Overclaim Regarding Termination Mechanism (Major):** The paper claims that repetition training "teaches models to produce complete, decisive reasoning chains" and that the advantage "operates entirely through improved termination behavior." This is a causal claim supported only by a correlation (higher termination, lower conditional accuracy). An alternative hypothesis is that early stopping at the token budget (Condition C) inherently selects for samples that are easier to memorize/terminate, or that the specific 1,600 samples happen to have a distribution of lengths that aligns well with the budget. Without an ablation that varies the token budget or uses different curated subsets, the causal link between "repetition" and "termination skill" is not fully isolated.

3. **Limited Scope of Model and Data Evaluation (Minor):** The study is conducted entirely on a single model size (Qwen2.5-1.5B) and a single domain (competition mathematics via NuminaMath). While the findings are compelling, the "repetition advantage" might be size-dependent (e.g., diminishing for larger models that have better in-context learning) or domain-specific (e.g., less relevant for coding or natural language inference). Generalizing these results to "long-CoT SFT" broadly is premature without at least one additional model size or domain.

4. **Lack of Comparison to Alternative Data-Mixing Strategies (Minor):** The paper compares data repetition against uniform data scaling. However, recent work (e.g., DoReMi, PRO) shows that re-weighting data mixtures can be highly effective. It is unclear if the repetition advantage persists when compared against an optimized data mixture of the 51,200 samples. This limits the practical takeaway: is repetition the best use of compute, or is smart data selection (without repetition) potentially superior?

## Key Issues
1. **FLOPs Proxy Validity (Methodological Rigor):** The current FLOPs proxy $\Sigma L_t^2$ only accounts for auto-regressive attention on the generated tokens. In standard decoder-only SFT, the attention mechanism also attends to the prompt tokens. If $P$ is the prompt length and $R$ is the response length, the attention complexity per step is proportional to $(P+R)^2 = P^2 + 2PR + R^2$. The authors only track $R^2$. Since $P$ is constant across conditions, $P^2$ cancels out in relative comparisons, but the cross-term $2PR$ does not. If Condition C has a different distribution of response lengths compared to Condition A (even if total tokens match), the $2PR$ term could introduce a residual compute confound.
*Impact:* This slightly weakens the claim of "tight compute control."
*Fix:* Update the FLOPs proxy to use $\Sigma (P_t + L_t)^2$ or explicitly argue why the $2PR$ term is negligible (e.g., if average $R$ is very large compared to $P$).

2. **Causal Attribution of Termination Gain (Validity Risk):** The paper attributes the performance gain to repetition "teaching" termination. However, Condition C is early-stopped at a specific token budget. It is possible that this budget coincidentally aligns with the completion points of the 1,600 high-quality samples, effectively creating a "length-matched" memorization task. Without testing different budget thresholds or random subsets of size 1,600, we cannot rule out that the gain comes from the specific alignment between the budget and the dataset rather than the repetition mechanism itself.
*Impact:* Reduces confidence in the mechanistic interpretation.
*Fix:* Add a control condition: train on a random 1,600-sample subset with the same token budget to see if termination rates still spike.

3. **Generalizability of Claims (Scope Overreach):** The conclusion states that "data curation and repetition genuinely outperform data scaling for long-CoT SFT." This is a universal claim based on a single model (1.5B) and a single math dataset. It is well-known in ML that scaling behaviors change with model size.
*Impact:* Overclaiming limits the scientific defensibility of the conclusion.
*Fix:* Bound the claims explicitly to the tested setting (e.g., "for sub-3B models on competition math...") and add at least one larger model (e.g., 7B) to check for trend inversion.

## Actionable Suggestions
1. **Refine the FLOPs Proxy Calculation:**
   *Action:* Update the compute verification in Section 3.3 to include the full attention complexity. Calculate the FLOPs proxy as $\sum_{t} (L_{prompt, t} + L_{response, t})^2$.
   *Mentor Revised Version for Section 3.3:* "Second, we compute a more comprehensive FLOPs proxy that accounts for the full self-attention complexity, including cross-attention between prompts and responses: $\sum_{t} (P_t + L_t)^2$, where $P_t$ is the prompt length and $L_t$ is the response length at step $t$. This captures the fact that longer contexts require disproportionately more compute. Under this stricter metric, Condition C's FLOPs proxy deviates by only [X]% from Condition A, confirming tight compute matching even when accounting for prompt-response interactions."

2. **Add a Random Subset Control to Validate Mechanism:**
   *Action:* Train a "Condition D" using a randomly selected 1,600 samples from the 51,200 set, matched to the same token budget as Condition C. Compare the termination rates. If Condition D does not show the same termination spike, it strongly supports the claim that the *curation/repetition* of high-quality traces is the causal driver, not just the token budget alignment.
   *Suggestion:* Add a paragraph in Section 4.4: "To ensure this effect is driven by repetition of high-quality data rather than budget alignment, we train a random 1,600-sample subset under the same token budget (Condition D). Condition D achieves only [X]% termination, comparable to Condition A, confirming that the termination advantage is specific to the curated repetition protocol."

3. **Bound Generalization Claims in the Conclusion:**
   *Action:* Revise the Conclusion to explicitly acknowledge the scope limitations (model size and domain) to improve scientific defensibility.
   *Mentor Revised Version for Conclusion:* "These findings establish that, for sub-2B models on competition mathematics, data curation and repetition genuinely outperform data scaling for long-CoT SFT. Future work should investigate whether this advantage persists in larger models and across diverse reasoning domains."

4. **Clarify the Definition of "Termination":**
   *Action:* In Section 3.5, explicitly define how "termination" is measured. Does it require a specific formatting token (e.g., `<answer>`), or is it simply generating within the max length limit?
   *Suggestion:* "Termination rate measures the fraction of generations that produce a parseable final answer block (e.g., enclosed in specific tags) within the maximum generation token limit, distinguishing complete reasoning from truncated outputs."

## Storyline Options + Writing Outlines
### Abstract Outline (Complete 4-5 Sentence Plan)
*Goal: Tighten the logic flow from Problem -> Gap -> Method -> Result -> Mechanism.*

- **S1 (Problem & Domain):** Recent work demonstrates that repeating a small, curated dataset significantly outperforms training on vastly larger unique datasets in long chain-of-thought (CoT) supervised fine-tuning (SFT).
- **S2 (The Gap/Confound):** However, step-matched comparisons in long-CoT settings inherently introduce a compute confound, as the repetition condition processes more total tokens due to longer average response lengths in curated data.
- **S3 (Proposed Method):** We introduce token-budget matching, a methodological intervention that isolates the true repetition effect by early-stopping the repetition condition to precisely match the baseline's cumulative response tokens.
- **S4 (Key Result):** Under these strictly compute-matched conditions, we show that the repetition advantage is not only preserved but amplified, definitively refuting the compute artifact hypothesis.
- **S5 (Mechanism & Implication):** Mechanistic analysis reveals that repetition training dramatically improves model termination rates (87–91% vs. 29–48%), teaching models to produce complete reasoning chains rather than incrementally better partial answers.

### Introduction Outline (Paragraph-by-Paragraph Plan)
*Goal: Ensure the "Big Picture -> Gap -> Solution -> Evidence" arc is crisp and the contribution is bounded.*

- **P1 (Big Picture):** Establish the importance of long-CoT reasoning for complex problem-solving and the standard reliance on SFT with curated demonstrations.
- **P2 (Prior Finding & The Hook):** Introduce the surprising finding from Kopiczko et al. (2026) that data repetition beats data scaling. Highlight why this challenges conventional scaling wisdom.
- **P3 (The Critical Gap):** Explicitly define the "compute confound." Explain that because curated responses are longer, matching optimizer steps inadvertently gives the repetition condition more training tokens (~2.85%). Pose the central question: Is the advantage real, or just a compute artifact?
- **P4 (Proposed Solution):** Introduce token-budget matching. Explain the intuition: to fairly compare data quality vs. quantity, we must match the fundamental compute unit (tokens), not the optimizer step count.
- **P5 (Main Results):** Preview the amplification effect. State clearly that controlling for compute makes the repetition advantage *stronger* (6.33× ratio), which is a counter-intuitive and significant finding.
- **P6 (Mechanism Preview):** Briefly mention the termination rate discovery. This hooks the reader into the "why" behind the result.
- **P7 (Contributions List):** List the three contributions (Methodology, Empirical Refutation, Mechanism) as done in the current draft, but ensure they are bounded to the tested setting to avoid overclaiming.

## Priority Revision Plan
### P0: Methodological Rigor & Validity (Must Fix)
1. **Update FLOPs Proxy Calculation (Effort: Low, Impact: High)**
   - **Action:** Recompute the compute verification metrics using the full attention complexity formula $\Sigma (P_t + L_t)^2$ instead of just $\Sigma L_t^2$.
   - **Goal:** Eliminate reviewer concerns that the cross-attention term introduces a residual compute confound. Update Section 3.3 and Table 3 accordingly.
   - **Acceptance Criterion:** FLOPs deviation remains low (< 1-2%) under the stricter metric, or the authors explicitly quantify and justify the residual gap.

2. **Add Random Subset Control (Effort: Medium, Impact: High)**
   - **Action:** Run one additional experiment (Condition D) training on a randomly selected 1,600 samples matched to the same token budget.
   - **Goal:** Isolate the causal mechanism. If Condition D does not show the termination spike seen in Condition C, it proves the effect relies on the specific curation/repetition of high-quality traces.
   - **Acceptance Criterion:** Add a paragraph in Section 4.4 comparing Condition C and Condition D termination rates to solidify the mechanistic claim.

### P1: Robustness & Scope Expansion (Highly Recommended)
3. **Evaluate on a Larger Model Size (Effort: High, Impact: Medium-High)**
   - **Action:** Replicate the core comparison (A vs. C) on a 7B parameter model (e.g., Qwen2.5-7B).
   - **Goal:** Verify that the repetition advantage does not invert at larger scales. Larger models may have different scaling dynamics or better in-context learning that diminishes the repetition benefit.
   - **Acceptance Criterion:** If the advantage diminishes, update the claims to be size-bounded. If it persists, it significantly strengthens the paper's contribution.

4. **Compare Against Data Re-weighting (Effort: Medium, Impact: Medium)**
   - **Action:** Briefly compare the repetition baseline against a data re-weighting method (e.g., DoReMi or a simple loss-based filtering) on the 51,200 samples.
   - **Goal:** Position the repetition advantage in the broader landscape of data optimization. Is repetition better than simply selecting the "best" unique data?
   - **Acceptance Criterion:** A short discussion in Related Work or Conclusion acknowledging how repetition compares to other data-efficiency techniques.

### P2: Writing, Clarity, & Bounding (Nice-to-have)
5. **Refine Conclusion Bounding (Effort: Low, Impact: Low)**
   - **Action:** Add explicit scope qualifiers to the conclusion (e.g., "for models up to X parameters" and "on competition mathematics").
   - **Goal:** Prevent reviewers from rejecting the paper for overclaiming generalization to all LLMs or all reasoning domains.

6. **Clarify "Termination" Definition (Effort: Low, Impact: Low)**
   - **Action:** In Section 3.5, provide the exact parsing logic used to measure termination rates. Does it rely on regex matching of specific tags?
   - **Goal:** Improve reproducibility and ensure readers understand the metric is measuring complete reasoning traces, not just length limits.

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (Data/Split/Protocol) | Metrics | Main Outcome | Claim Supported | Current Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** (Baseline) | Establish data scaling performance baseline. | 51.2k unique NuminaMath-CoT samples; 1 epoch; Qwen2.5-1.5B. | Acc@k, Pass@k, Term% | Baseline accuracy and moderate termination (~30-48%). | N/A | Standard setup. |
| **B** (Step-Match) | Replicate prior repetition advantage; identify confound. | 1.6k curated samples x 32 epochs; matched optimizer steps to A. | Acc@k, Pass@k, Term% | Outperforms A, but has +2.85% token surplus. | Repetition works (step-match). | Compute confound present. |
| **C** (Token-Match) | Test repetition advantage under strict compute control. | 1.6k curated samples; early-stopped to match A's token budget. | Acc@k, Pass@k, Term% | Outperforms B (6.33x gain ratio); high termination (~87-91%). | Repetition works (token-match). | Single model/seed/dataset. |
| **Dyn** (Appendix) | Analyze memorization dynamics across conditions. | Track training loss and token accuracy over steps. | Loss, Token Acc | Repetition conditions (B, C) reach >99% token accuracy; A plateaus at ~74%. | Repetition drives memorization. | Correlative evidence only. |

### (b) Research-Theme Gap Diagnosis
1.  **Causal Mechanism Isolation (Validity):** The current evidence links repetition to termination rates but does not rule out that the specific token budget aligns with the length distribution of the curated data. Without a random subset control, the "teaching termination" claim is correlational.
2.  **Model Size Scaling (Generalizability):** The study relies solely on a 1.5B model. It is unknown if the repetition advantage persists, diminishes, or inverts for larger models (e.g., 7B+), which may have different scaling properties.
3.  **Domain Robustness (Scope):** Evaluation is limited to competition mathematics. The mechanism (termination vs. accuracy) might not apply to domains like code generation or natural language inference.

### (c) Proposed Research Experiments

| Priority | Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Quality Gain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | Mechanism Isolation | The termination gain is due to curation/repetition, not just budget alignment. | Train on a **random 1,600-sample subset** matched to Condition C's token budget. | Condition C (Curated); Condition A (Scaling). | Term%, Pass@k | Condition D (Random) has low Term% (~30%), matching A. | 1 GPU Day | **High:** Validates causal mechanism. |
| **P0** | Compute Validity | The FLOPs proxy holds even when accounting for prompt-response cross-attention. | Recalculate FLOPs proxy using **$\Sigma (P_t + L_t)^2$**. | Condition A vs. C. | FLOPs Deviation | Deviation remains < 1-2%. | Negligible | **High:** Eliminates method critique. |
| **P1** | Size Generalization | Repetition advantage persists or scales with model size. | Replicate A vs. C on **Qwen2.5-7B-Instruct**. | 7B Scaling vs. 7B Repetition. | Pass@k | Advantage ratio $\ge$ 1.0 (or bounded explanation if < 1.0). | 2-3 GPU Days | **Medium:** Extends scope. |
| **P2** | Domain Transfer | Termination mechanism applies to code reasoning. | Replicate A vs. C on **HumanEval+** (coding tasks). | Code Scaling vs. Code Repetition. | Pass@1, Term% | Similar trend in termination/accuracy. | 2 GPU Days | **Low-Med:** Increases broad appeal. |

### (d) Traceability
- **Exp P0 (Random Subset)** maps to **Weakness 2 (Causal Overclaim)** and validates the core mechanistic finding.
- **Exp P0 (FLOPs)** maps to **Key Issue 1 (Proxy Validity)** and strengthens the methodological rigor.
- **Exp P1 (7B Model)** maps to **Weakness 3 (Limited Scope)** and supports broader claims.
- **Exp P2 (Coding)** maps to **Weakness 3 (Limited Scope)** and tests domain robustness.

```text
ASCII Diagram — Experiment Upgrade Plan (P0/P1/P2 Sequencing)
[P0: Core Validity Fixes]
  ├──> Experiment: Random Subset Control (Condition D)
  │     └──> Goal: Isolate Curation/Repetition from Budget Alignment
  └──> Experiment: Full FLOPs Proxy (Σ(P+L)²)
        └──> Goal: Eliminate Residual Compute Confound Critique

[P1: Robustness & Scope Expansion]
  ├──> Experiment: 7B Model Evaluation
  │     └──> Goal: Verify Advantage Persists at Larger Scale
  └──> Experiment: Coding Domain (HumanEval+)
        └──> Goal: Test Domain Transferability

[P2: Polish & Bounding]
  └──> Action: Bound Conclusion Claims
        └──> Goal: Align Claims with Verified Scope
```

```text
ASCII Diagram — Paper Structure & Evidence Map
[Intro: Repetition Advantage Claim]
      ↓
[Gap: Compute Confound in Step-Matching (Kopiczko et al.)]
      ↓
[Method: Token-Budget Matching (Condition C)]
      ↓
[Result: Advantage Amplified 6.33x under Token-Match]
      ↓
[Mechanism: High Termination Rates (87-91%) vs Accuracy]
      ↓
[Limit: Single Model (1.5B) and Domain (Math)]
```

```text
ASCII Diagram — Revision Strategy Roadmap
[Issue: Incomplete FLOPs Proxy] 
    -> [Fix: Recalculate using Σ(P+L)²] 
    -> [Expected Gain: Methodological Rigor]

[Issue: Causal Overclaim on Termination] 
    -> [Fix: Add Random Subset Control (Condition D)] 
    -> [Expected Gain: Mechanism Validity]

[Issue: Scope Overreach (Single Model)] 
    -> [Fix: Add 7B Model Eval or Bound Claims] 
    -> [Expected Gain: Scientific Defensibility]
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | Token-budget matching as a methodology for fair compute-controlled comparisons in long-CoT SFT. | [1], [4], [6] | `supported` | While compute-optimal scaling [4] and repetition scaling laws [6] exist for pretraining, applying strict response-token matching via early stopping to long-CoT SFT is a novel methodological contribution. | High | None. |
| **C2** | The repetition advantage is preserved and amplified 6.33× under token-matched conditions. | [1] | `supported` | Prior work [1] shows repetition beats scaling under step-matching, but the *amplification* when controlling for tokens is a new, counter-intuitive empirical finding. | High | None. |
| **C3** | Mechanism: repetition improves termination rates (87-91%) rather than conditional accuracy. | [1], [2], [5] | `partially_overlapping` | Memorization dynamics [1] and repetition overfitting [5] are known; however, the explicit decomposition of CoT gains into termination vs. accuracy is a novel mechanistic insight. | Medium | Soften "teaching" causal claims; acknowledge selection effects. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Root: LLM Scaling & Training Dynamics** | **Branch 1: Compute-Optimal Scaling** | | Focus on pretraining regimes and large-scale token budgets. | This paper applies compute-matching to small-scale SFT. | Low. |
| | Leaf 1.1: Standard Scaling Laws | [4] | Performance depends on total compute ($C = 6ND$). | Focuses on pretraining; ignores SFT specific response-length confounds. | None. |
| | Leaf 1.2: Data-Constrained Laws | [6] | Repetition introduces an additive overfitting penalty. | Models repetition theoretically; does not isolate the behavioral termination mechanism. | None. |
| **Root: LLM Scaling & Training Dynamics** | **Branch 2: Data Repetition & SFT** | | SFT benefits from high-quality, curated data. | Directly addresses the long-CoT SFT repetition advantage. | Low. |
| | Leaf 2.1: Step-Matched Repetition | [1] | Repetition advantage exists under fixed optimizer steps. | This paper refutes the compute confound in [1] via token-matching. | None. |
| | Leaf 2.2: Pretraining Repetition | [5] | Multi-epoch pretraining leads to overfitting/degradation. | Focuses on general pretraining; does not study the specific termination mechanism in CoT reasoning. | None. |
| **Root: LLM Scaling & Training Dynamics** | **Branch 3: CoT Reasoning Mechanisms** | | Long-CoT improves reasoning via intermediate steps. | Explores what drives CoT gains (data quantity vs. memorization). | Low. |
| | Leaf 3.1: Small Data CoT SFT | [2] | High-quality expert CoT traces unlock reasoning. | Focuses on data source quality; does not study data repetition effects. | None. |
| | Leaf 3.2: CoT Mechanics | [3] | SFT simplifies RL and stabilizes CoT length. | Focuses on SFT vs. RL; not on data repetition dynamics. | None. |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [1] | Long-CoT SFT on Math | Repetition (1.6k x 32 epochs) vs Scaling (51.2k x 1 epoch) | Core motivation; this paper isolates the compute confound in [1]. | [1] uses step-matching; this paper uses token-budget matching. | This paper directly builds upon and validates [1], refuting its potential confound. |
| [6] | Data-constrained Pretraining | Scaling laws with additive overfitting penalty | Theoretical modeling of data repetition value. | Pretraining focus; models overfitting, not behavioral termination. | Contextualizes the repetition advantage but does not overlap in SFT mechanism. |
| [5] | Multi-epoch Pretraining | Evaluating degradation from repeated data. | Repetition dynamics. | Pretraining setting; finds degradation, whereas SFT finds advantage. | Reinforces that SFT repetition dynamics differ from pretraining. |

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
LLM Scaling & Training Dynamics (Root)
├── Branch 1: Compute-Optimal Scaling
│   ├── Leaf 1.1: Standard Scaling Laws (Sardana & Frankle, 2024) [4]
│   └── Leaf 1.2: Data-Constrained Laws (Lovelace et al., 2026) [6]
├── Branch 2: Data Repetition & SFT
│   ├── Leaf 2.1: Step-Matched Repetition (Kopiczko et al., 2026) [1]
│   └── Leaf 2.2: Pretraining Repetition (Xue et al., 2023) [5]
└── Branch 3: CoT Reasoning Mechanisms
    ├── Leaf 3.1: Small Data CoT SFT (Du et al., 2025) [2]
    └── Leaf 3.2: CoT Mechanics (Yeo et al., 2025) [3]
```

### Contribution-level Novelty Conclusion
The paper successfully establishes **C1** (token-budget matching) as a novel methodological contribution, filling a critical gap left by step-matched comparisons in long-CoT SFT. **C2** (the amplification effect) is strongly supported by the empirical results and stands as a unique finding that shifts the understanding of the repetition advantage. **C3** (the termination mechanism) offers a novel interpretation of the gains, though it partially overlaps with existing memorization dynamics; its causal strength is improved by explicitly bounding the claims. Overall, the manuscript carves out a distinct and valuable niche at the intersection of compute-optimal scaling and SFT data dynamics.

## References
[1] Data Repetition Beats Data Scaling in Long-CoT Supervised Fine-Tuning 2602.11149

[2] The Challenge of Teaching Reasoning to LLMs Without RL or Distillation 2507.09850

[3] Demystifying Long Chain-of-Thought Reasoning in LLMs 2502.03373

[4] Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws 2401.00448

[5] To Repeat or Not To Repeat: Insights from Scaling LLM under Token-Crisis 2305.13230

[6] Prescriptive Scaling Laws for Data Constrained Training 2605.01640

## Scores
Final Score: 7/10. This paper presents a strong, well-motivated methodological contribution (token-budget matching) and delivers a counter-intuitive, highly significant empirical finding (the amplification of the repetition advantage under compute-matched conditions). The mechanistic decomposition of accuracy into termination and conditional accuracy is a standout contribution. However, the current FLOPs proxy is technically incomplete (ignoring cross-attention), and the causal claims regarding the termination mechanism are slightly overreaching without a random subset control. The scope is also tightly bound to a single model size and domain. These issues are fixable and do not invalidate the core contribution, warranting a solid but cautious score.

Post-Revision Target: [8, 9]/10. By updating the FLOPs proxy to $\Sigma (P+L)^2$, adding a simple random-subset control to validate the termination mechanism, and explicitly bounding the generalization claims in the abstract and conclusion, the manuscript can achieve top-tier research quality. The core findings are robust and impactful; the revisions would simply tighten the scientific rigor and expand the defensibility of the conclusions.