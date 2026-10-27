## Summary
This paper investigates how to allocate a fixed verification budget when using world models to verify irreversible actions (e.g., checkout in web shopping agents). The authors identify a counterintuitive failure mode: increasing the verification budget under a sequential verify-and-retry protocol can paradoxically reduce task success due to "trajectory drift"—where verification rejection triggers unguided re-browsing that leads agents to select worse products. To address this, they propose chunked budget allocation (spending the entire budget in one parallel chunk, $M=1$) and demonstrate a 25× improvement (21.50% vs 0.86%) over sequential verification on WebShop. They further show that consensus aggregation provides no benefit due to the world model's severe miscalibration (predicting failure for 98.4% of cycles).

The core contributions are: (1) identifying trajectory drift as a dominant failure mode in sequential verification, (2) demonstrating the efficacy of chunked budget allocation, and (3) revealing the degeneration of consensus under poor calibration. The paper is well-structured, provides clear empirical evidence (including bootstrap CIs and temperature ablations), and offers practical guidance for deploying world-model verification in irreversible-action settings.

Key strengths include a novel framing of the verification budget allocation problem and rigorous empirical validation. Key weaknesses include limited generalization (single benchmark, single world model), modest absolute success rates, and the lack of a deeper discussion on why the world model is so poorly calibrated. Overall, this is a valuable contribution that highlights a critical structural pitfall in agentic verification.

## Strengths
1. **Novel Problem Framing:** The identification of "trajectory drift" as a failure mode caused by sequential verification structures provides valuable new knowledge. The insight that verification rejections trigger unguided re-browsing which degrades the agent's state is a non-trivial discovery that shifts focus from verifier accuracy to verification protocol design.
2. **Strong Empirical Validation:** The paper is methodologically sound. The use of 600 episodes (200 tasks × 3 seeds), paired bootstrap confidence intervals, and multi-temperature ablations demonstrates rigor. The temperature=0 ablation effectively isolates the structural benefit of chunking from stochastic diversity.
3. **Counter-Intuitive Finding on Consensus:** The discovery that consensus aggregation provides *no benefit* (and is even worse than single-rollout pass-through) over poorly calibrated world models is highly informative. The calibration analysis (Brier score 0.28, 98.4% predicting failure while 27.5% succeed) provides a clear mechanism for this degeneration.
4. **Actionable Practical Guidance:** The finding that $M=1$ (spending all budget upfront) consistently outperforms sequential allocations offers clear, actionable guidance for practitioners deploying world models for irreversible actions.
5. **Clear and Concise Narrative:** The paper tells a coherent story from problem to solution to mechanism analysis. The introduction clearly sets up the tension between the promise of verification and the reality of sequential drift.

## Weaknesses
1. **Limited Generalization (Single Benchmark, Single World Model):** The findings are evaluated exclusively on WebShop using a fine-tuned Qwen2.5-7B world model and Gemini-2.5-Flash as the acting agent. It remains unclear if the trajectory drift phenomenon and the superiority of chunked allocation hold in other domains (e.g., WebArena, Mind2Web) or with different world models that might be better calibrated.
2. **Modest Absolute Performance:** While chunked verification provides a 25x improvement over sequential verification, the absolute success rate (21.50%) remains modest. This suggests that the chunked budget allocation, while preventing non-monotonic regressions, does not solve the fundamental reliability issues of world models for irreversible actions.
3. **Superficial Analysis of Calibration Failure:** Section 4.6 correctly identifies that the world model is poorly calibrated (Brier score 0.28, 98.4% predicting failure). However, the paper stops at reporting this observation and does not investigate the root cause. Is this due to a mismatch between the world model's training distribution and the WebShop environment? Is it an inherent limitation of next-token prediction objectives when used as binary outcome predictors? A deeper analysis here would significantly increase the paper's scientific value.
4. **Implicit Budget-Exhaustion Fallback:** The experimental protocol includes a fallback where the agent automatically passes checkout after $M$ cycles (budget exhaustion). This means chunked verification ($M=1$) benefits from a single, immediate fallback pass-through if verification fails. The manuscript should more explicitly articulate that the primary mechanism of chunking is not just avoiding re-browsing, but forcing a budget-exhausted checkout on the originally found product, rather than enabling multiple sequential re-browsing attempts.
5. **Lenient Threshold Justification:** The use of $\tau=0.1$ for the chunked consensus condition means only 1 out of 10 rollouts needs to predict success for the checkout to pass. Given the world model's poor calibration, this threshold is extremely lenient. The paper briefly mentions it minimizes false negatives, but a sensitivity analysis (e.g., comparing $\tau=0.1$ vs $\tau=0.3$) would strengthen the robustness of the chunked consensus finding.
6. **Partial Overlap in Related Work:** While the specific trigger (verification rejection) is novel, the phenomenon of "trajectory drift"—where agent states degrade during retry or rollback—has related literature in error recovery (e.g., WebRollback) and hallucination propagation (e.g., AgentDrift). The paper should more explicitly distinguish its contribution from these existing drift/error propagation studies.

## Key Issues
1. **Mechanism Clarity: Budget Exhaustion as the True Driver (Major)**
   The primary mechanism by which chunked verification ($M=1$) prevents trajectory drift is the budget-exhaustion fallback. When the single chunked verification cycle fails, the budget is consumed, and the agent automatically proceeds to checkout on its originally found product. In contrast, sequential verification ($M=10$) allows the budget to be spent across multiple cycles, each triggering a re-browse if rejected. The manuscript states that chunked verification "avoids this by spending the entire budget upfront" but does not explicitly highlight that the fallback pass-through on the *original* product is the key.
   *Impact:* Without this clarity, readers might incorrectly assume chunked verification enables a better re-selection strategy, rather than simply forcing a checkout on the first choice after consuming the verification budget.

2. **Root Cause of World Model Miscalibration (Major)**
   The paper reports that the world model predicts failure ($\hat{p}=0$) for 98.4% of cases, with a Brier score of 0.28 and ECE of 0.28. This extreme miscalibration is the reason why consensus aggregation fails. However, the paper does not investigate *why* this occurs.
   *Impact:* This limits the paper's contribution to a phenomenological observation. Understanding if this miscalibration stems from the training objective (next-token prediction vs. outcome prediction) or data distribution mismatch would provide actionable guidance for future world model development.

3. **Differentiation from General Agent Drift Literature (Minor)**
   The concept of "trajectory drift"—where an agent's state degrades during retry or recovery—shares similarities with existing work on error propagation in agents (e.g., Zhang et al., 2025; Wu et al., 2026).
   *Impact:* The novelty of the "trajectory drift" claim is partially overlapped by these general drift studies. The manuscript must explicitly differentiate its specific trigger (verification rejection of an irreversible atomic action) from general multi-step hallucination or error propagation.

## Actionable Suggestions
1. **Clarify the Budget-Exhaustion Mechanism (Method Section 3.2)**
   Explicitly state that the budget-exhaustion fallback is the primary mechanism preventing drift in the $M=1$ setting.
   *Suggestion:* Add a sentence in Section 3.2: "Under the $M=1$ chunked setting, a verification failure exhausts the budget immediately, causing the agent to proceed to checkout on its originally proposed product via the fallback pass-through. This prevents the unguided re-browsing steps that characterize sequential verification."

2. **Investigate Calibration Root Causes (Section 4.6)**
   Perform a qualitative analysis on the 84 cases where the world model predicted failure ($\hat{p}=0$) but the purchase actually succeeded. 
   *Suggestion:* Include a small table or list of 3-5 examples showing the user intent, the product selected, and the world model's reasoning (if accessible). Determine if the false negatives stem from overly strict criteria (e.g., price within 10% vs exact match) or hallucinated constraints.

3. **Expand Related Work Positioning (Section 2)**
   Strengthen the differentiation from general error propagation.
   *Suggestion:* In the "Error Recovery in Agents" or a new paragraph, explicitly state: "While prior work studies general error propagation during retry (Zhang et al., 2025) or hallucination in multi-step workflows (Wu et al., 2026), our work isolates the specific penalty of trajectory drift triggered by the binary rejection of a single irreversible atomic action."

4. **Add Threshold Sensitivity Analysis (Section 4)**
   Justify the choice of $\tau=0.1$ and show that the result is not solely an artifact of this extremely lenient threshold.
   *Suggestion:* Report success rates for $M=1, K=10$ under $\tau=0.3$ and $\tau=0.5$. Even if success drops, if it remains significantly higher than sequential verification, the core conclusion holds.

5. **Refine Abstract and Introduction Scope**
   Ensure the "25× improvement" claim is properly bounded to the specific dataset and setting to avoid over-generalization.
   *Suggestion:* Update the abstract to: "On the WebShop benchmark, chunked verification ($M=1$) achieves 21.50% task success versus 0.86% for sequential..."

## Storyline Options + Writing Outlines
### (a) Abstract Outline (Complete)
*Target: Compact 5-sentence logic.*

- **S1 (Problem & Domain):** World models that predict environment dynamics are increasingly used as pre-execution verifiers for agents performing irreversible actions.
- **S2 (Challenge):** However, a standard sequential verify-and-retry protocol can paradoxically degrade task success as verification budget increases due to unguided re-browsing after false-negative rejections.
- **S3 (Gap & Method):** To address this, we propose chunked budget allocation: spending a fixed verification budget in fewer parallel cycles rather than many sequential ones, thereby eliminating the feedback loop that causes trajectory drift.
- **S4 (Key Result):** On WebShop, chunked verification ($M=1$) achieves a 25× improvement in success rate (21.50% vs 0.86%) over sequential verification at the same budget, with temperature ablations confirming this gain is structural rather than stochastic.
- **S5 (Implication):** Surprisingly, we find that consensus aggregation provides no benefit over single-rollout acceptance due to severe world model miscalibration, demonstrating that budget allocation structure is more critical than aggregation sophistication.

### (b) Introduction Outline (Complete)
*Target: 4-5 paragraphs, clear Big Picture -> Gap -> Solution -> Evidence arc.*

- **P1 (Big Picture & Motivation):** Establish the promise of world models for agent decision-making, specifically as pre-execution verifiers for irreversible actions (e.g., purchases, emails). Cite foundational world model and web agent verification work (e.g., Li et al. 2025; Gu et al. 2025).
- **P2 (The Gap/Problem):** Introduce the counterintuitive failure mode observed in prior work: increasing the verification budget can actually reduce success. Define the core mechanism—trajectory drift—where a verification rejection triggers unguided re-browsing, leading the agent to select a worse product. Highlight the lack of understanding regarding how verification *structure* (sequential vs parallel) impacts this drift.
- **P3 (Proposed Solution):** Present the chunked budget allocation framework. Explain the intuition: by concentrating the budget in fewer, parallel cycles ($M=1$), we consume the budget upfront and trigger a budget-exhaustion fallback that forces checkout on the original product, bypassing the drift-inducing re-browsing steps inherent in sequential verification ($M=10$).
- **P4 (Evidence & Additional Findings):** Preview the empirical results on WebShop (25x improvement). Mention the temperature ablation proving the structural nature of the gain. Introduce the surprising secondary finding: consensus aggregation fails to help because the world model is severely miscalibrated (predicting failure 98.4% of the time).
- **P5 (Contributions):** Explicitly list the 4 contributions: (1) Identification of trajectory drift, (2) Demonstration of chunked allocation's efficacy, (3) Analysis of consensus degeneration, (4) Practical guidance on $M=1$ allocation.

## Priority Revision Plan
The following revision plan is ordered by priority (P0: Critical for validity/clarity, P1: High impact, P2: Nice-to-have).

| Priority | Issue | Action | Expected Benefit |
|---|---|---|---|
| **P0** | Mechanism Clarity: Budget Exhaustion | Rewrite Section 4.4 failure analysis to explicitly state that chunked verification prevents drift via the budget-exhaustion fallback on the *original* product, not via a better re-selection strategy. | Resolves a critical conceptual ambiguity; ensures readers correctly understand the causal mechanism. |
| **P0** | Calibration Root Cause | Add 1-2 paragraphs in Section 4.6 analyzing *why* the world model is so miscalibrated (e.g., qualitative examples of false negatives, training objective mismatch). | Deepens scientific insight beyond phenomenological observation. |
| **P1** | Related Work Differentiation | Add explicit comparison to general agent drift/rollback literature (WebRollback, AgentDrift) in Section 2. | Strengthens novelty claim by clearly delineating the specific irreversible-action setting. |
| **P1** | Threshold Sensitivity | Report success rates for $M=1$ under $\tau=0.3$ and $\tau=0.5$ to show the chunked advantage is not solely an artifact of the extremely lenient $\tau=0.1$. | Increases robustness and defensibility of the main empirical finding. |
| **P2** | Abstract/Intro Scope Bounds | Add "on WebShop" to the abstract and introduction result sentences to prevent over-generalization of the 25× improvement claim. | Improves scientific precision and prevents reviewer criticism of hype. |
| **P2** | Bootstrap Procedure Details | Clarify bootstrap resampling method (e.g., 1000 resamples of tasks) in Section 4.1. | Improves reproducibility. |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Chunked budget allocation outperforms sequential verify-and-retry at fixed budget B=10. | WebShop, 600 episodes (200 tasks x 3 seeds), Conditions A/B/C. B=10. | Task success rate, 95% bootstrap CI. | C (No-Agg, M=1) achieves 21.50% vs A (Seq, M=10) at 0.86%. 25x improvement. | C2 (Chunked allocation efficacy) | Absolute success rate modest (21.50%). |
| E2 | Reducing verification cycles (M) monotonically improves success. | Vary M in {1, 2, 5, 10}, fixed B=10. | Task success rate, 95% bootstrap CI. | M=1 achieves 20.0%, M=10 achieves 0.83%. Non-monotonic pattern in intermediates. | C4 (Practical guidance M=1) | Intermediate non-monotonicity requires threshold justification. |
| E3 | Chunked advantage is structural, not due to stochastic diversity. | Temperature ablation: temp=0.7 vs temp=0.0. M=2, K=5, τ=0.5. | Task success rate, B-A advantage. | Advantage persists and increases at temp=0 (+9.67 pp). | Mechanism isolation (structural benefit) | Uses M=2 config, not the main M=1 finding. |
| E4 | Consensus aggregation fails due to world model miscalibration. | Condition B (M=1, K=10). Report Brier score, ECE, $\hat{p}$ distribution. | Brier score, ECE, success rate at $\hat{p}=0$. | 98.4% predict $\hat{p}=0$. Actual success at $\hat{p}=0$ is 27.5%. Brier=0.28, ECE=0.28. | C3 (Consensus degeneration) | Lacks qualitative analysis of *why* miscalibration occurs. |
| E5 | Identify failure patterns in sequential verification. | Analyze 81 episodes where B succeeded but A failed. | Failure pattern counts/percentages. | Trajectory drift accounts for 60.5% of failures. | C1 (Trajectory drift identification) | Qualitative analysis limited to 81 cases. |

### (b) Research-Theme Gap Diagnosis
The core research-value claim—that budget allocation structure matters more than aggregation sophistication—is strongly supported by the current experiments. However, three gaps remain:
1. **Generalizability:** The findings are limited to a single benchmark (WebShop) and a single world model (Qwen2.5-7B). It is unknown if trajectory drift occurs in other domains or with better-calibrated models.
2. **Root-Cause Analysis of Calibration:** The paper identifies miscalibration but does not diagnose it. Understanding the root cause (e.g., training objective mismatch) would provide actionable guidance for world model development.
3. **Threshold Sensitivity:** The chunked consensus result relies on an extremely lenient threshold ($\tau=0.1$). It is unclear if the structural advantage holds under more standard consensus thresholds.

### (c) Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Expected Gain |
|---|---|---|---|---|---|---|---|
| C2 (Generalizability) | Chunked allocation outperforms sequential verification across diverse benchmarks. | Evaluate Conditions A/C on WebArena or Mind2Web subset. | Sequential (A), Chunked (C). B=10. | Task success rate. | C significantly outperforms A on at least one new benchmark. | Medium (2-3 days) | Validates generalizability; major quality boost. |
| C3 (Calibration Root Cause) | False negatives stem from overly strict criteria or hallucinated constraints. | Qualitative analysis of 20-30 cases where $\hat{p}=0$ but purchase succeeded. | None (diagnostic). | Categorization of failure modes (e.g., price mismatch, attribute hallucination). | Clear pattern identified (e.g., 60% due to price tolerance). | Low (1 day) | Deepens scientific insight; actionable for WM training. |
| C2 (Threshold Sensitivity) | Chunked advantage persists even under stricter consensus thresholds. | Evaluate Condition C under $\tau \in \{0.1, 0.3, 0.5\}$. | Sequential (A) as baseline. | Task success rate vs $\tau$. | C($\tau=0.3$) still significantly outperforms A. | Low (0.5 day) | Increases robustness of main finding. |

### (d) ASCII Diagram — Experiment Upgrade Plan

```text
ASCII Diagram — Experiment Upgrade Plan
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Stage 1 (P0: Immediate, Low Cost)                                  │ Stage 2 (P1: Validation, Medium Cost)   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Qualitative Calibration Analysis                                │ 2. Threshold Sensitivity Sweep          │
│    - Sample 20-30 false-negative cases (p̂=0, success=1)           │    - Test τ ∈ {0.1, 0.3, 0.5} for M=1    │
│    - Categorize failure modes (price mismatch, attribute drift)   │    - Compare against Sequential (A)       │
│    - Root cause hypothesis: training objective mismatch           │    - Success: C(τ=0.3) >> A                │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
│ 3. Generalizability Test (P1)                                      │
│    - Evaluate A vs C on WebArena/Mind2Web subset                  │
│    - Success: Chunked advantage holds on at least one new domain  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| **C1** | Trajectory drift is the dominant failure mode in sequential verify-and-retry, accounting for 60.5% of failures after rejection. | General AgentBench [1], AgentDrift [2] | `partially_overlapping` | General error propagation and context ceilings in sequential scaling are known [1], and multi-turn drift under tool contamination is documented [2]. The specific trigger (verification rejection of an irreversible atomic action) is novel, but the drift phenomenon itself is related. | High | Differentiate explicitly from general agent drift/rollback literature. |
| **C2** | Chunked budget allocation ($M=1$) achieves 25× improvement over sequential verification by eliminating sequential cycles. | Scaling Test-time Compute [3], Benchmark TTS [1] | `supported` | Prior work studies parallel vs sequential scaling for general trajectory completion [1,3]. No prior work isolates the budget allocation structure for a *single irreversible verification decision* and demonstrates that consuming the budget upfront to trigger a fallback pass-through prevents drift. | High | Bound claim to the irreversible-action setting; emphasize the fallback mechanism. |
| **C3** | Consensus aggregation provides no benefit (single-rollout is better) because the world model is poorly calibrated ($\hat{p}=0$ for 98.4% of cycles). | Word2World [4], WebDreamer [5] | `supported` | Word2World [4] and WebDreamer [5] establish world models for verification but do not analyze the calibration degeneration of consensus aggregation under extreme false-negative rates. This is a novel empirical finding. | High | Add brief analysis of *why* calibration fails (training objective mismatch). |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root | Branch 1: Test-Time Scaling & Compute Allocation | | | | |
| | Leaf 1.1: General Agent TTS (Parallel/Sequential) | Scaling Test-time Compute [3], Benchmark TTS [1] | More compute (sampling/revision) generally improves agent outcomes. | This paper shows sequential verification degrades outcomes due to drift; parallel chunking helps. | Low (clear differentiation on irreversible setting). |
| | Leaf 1.2: Asymmetric/Verifier Scaling | Pushing TTS Limits [6] | Verification is easier than generation; budget should shift to verifiers. | This paper keeps verifier budget fixed but studies its *allocation structure* (chunked vs sequential). | Low. |
| Root | Branch 2: World Models for Web Agents | | | | |
| | Leaf 2.1: LLM as Implicit World Model | Word2World [4], WebDreamer [5] | LLMs can simulate environment dynamics for planning/verification. | This paper does not improve world model accuracy; it studies budget allocation given a fixed (poorly calibrated) world model. | Low. |
| | Leaf 2.2: World Model Calibration/Failure | Evaluating World Models [7], ReOI [8] | World models are brittle; calibration/failure analysis is needed. | This paper provides concrete calibration metrics (Brier/ECE) for verification degeneration, which is a specific contribution. | Low. |
| Root | Branch 3: Agent Error Recovery & Drift | | | | |
| | Leaf 3.1: Rollback/Retry Mechanisms | WebRollback [9], Reflexion [10] | Retry from errors improves outcomes; agents can learn from feedback. | This paper shows retry *degrades* outcomes (drift) when the agent treats rejection as a simple block, not feedback. | Medium (requires explicit differentiation). |
| | Leaf 3.2: Multi-Turn Drift/Propagation | AgentDrift [2], AgentHallu [11] | Errors/drift propagate across multi-step trajectories. | This paper isolates drift triggered by a *single binary verification rejection* of an irreversible action. | Medium (requires explicit differentiation). |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [3] Scaling Test-time Compute | General LLM agents (various benchmarks) | Parallel sampling, sequential revision, list-wise verification. | Studies parallel vs sequential scaling for agents. | Focuses on overall trajectory completion, not single irreversible verification decisions. | Supports novelty of C2 by showing the specific verification setting is unexplored. |
| [1] Benchmark TTS | General LLM agents (General AgentBench) | Sequential scaling (context ceiling), Parallel scaling (verification gap). | Identifies sequential scaling limitations (context ceiling). | This paper's "trajectory drift" is a specific, verified failure mode in irreversible settings. | Partially overlaps C1; paper must differentiate "drift from rejection" vs "context ceiling". |
| [4] Word2World | Text-based environments, LLM as world model | Action verification, synthetic trajectory generation. | Uses world models for action verification. | Does not study budget allocation structure or calibration degeneration of consensus. | Supports novelty of C2/C3. |
| [2] AgentDrift | Multi-turn financial dialogues, tool corruption | Information-channel vs memory-channel drift decomposition. | Studies "drift" in agent trajectories. | This paper's drift is triggered by verification rejection, not tool data corruption. | Requires explicit differentiation in Related Work. |
| [5] WebDreamer | Web agents, real-world sites | Model-based planning with LLM world models to avoid backtracking. | Uses world models for irreversible actions. | Focuses on model-based planning *before* action, not budget allocation *of* verification. | Supports novelty by showing complementary focus. |

### Contribution-level Novelty Conclusion
The manuscript's core contributions are largely novel within the specific scope of *irreversible action verification*. 
- **C1 (Trajectory Drift)** is `partially_overlapping` with general agent drift literature; the paper must explicitly differentiate its specific trigger mechanism from general error propagation. 
- **C2 (Chunked Budget Allocation)** is `supported` as novel; no prior work isolates the budget allocation structure for a single verification decision point and demonstrates the superiority of the $M=1$ fallback mechanism. 
- **C3 (Consensus Degeneration)** is `supported` as novel; the empirical finding that consensus collapses under extreme miscalibration is a valuable, previously unreported insight for world model verification.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)
```text
Related Work Taxonomy (Root)
├── Branch 1: Test-Time Scaling & Compute Allocation
│   ├── Leaf 1.1: General Agent TTS (Parallel vs Sequential) [1][3]
│   └── Leaf 1.2: Asymmetric Verification Scaling [6]
├── Branch 2: World Models for Web Agents
│   ├── Leaf 2.1: LLM as Implicit World Model [4][5]
│   └── Leaf 2.2: World Model Calibration & Failure Analysis [7][8]
└── Branch 3: Agent Error Recovery & Drift
    ├── Leaf 3.1: Rollback/Retry Mechanisms [9][10]
    └── Leaf 3.2: Multi-Turn Drift & Error Propagation [2][11]

Manuscript Positioning:
└── Sits at the intersection of Branch 1 and Branch 3, but scoped specifically to 
    single irreversible verification decisions (a setting not covered by the above leaves).
```

## References
[1] Benchmark Test-Time Scaling of General LLM Agents 2602.18998

[2] AgentDrift: Unsafe Recommendation Drift Under Tool Corruption Hidden by Ranking Metrics in LLM Agents 2603.12564

[3] Scaling Test-time Compute for LLM Agents 2506.12928

[4] From Word to World: Can Large Language Models be Implicit Text-based World Models? 2512.18832

[5] Is Your LLM Secretly a World Model of the Internet? Model-Based Planning for Web Agents 2411.06559

[6] Pushing Test-Time Scaling Limits of Deep Search with Asymmetric Verification 2510.06135

[7] Evaluating World Models with LLM for Decision Making 2411.08794

[8] Reimagination with Test-time Observation Interventions: Distractor-Robust World Model Predictions for Visual Model Predictive Control 2506.16565

[9] AgentHallu: Benchmarking Automated Hallucination Attribution of LLM-based Agents 2601.06818

## Scores
Final Score: 6.5/10
Post-Revision Target: [7.5, 8.5]/10

**Justification:**
The paper presents a valuable and well-executed empirical study that identifies a non-trivial failure mode (trajectory drift) in sequential world-model verification and proposes a simple, effective structural fix (chunked budget allocation). The novelty of the finding that budget allocation structure ($M=1$ fallback) outperforms sequential scaling and sophisticated aggregation (consensus) is strong, and the empirical validation (bootstrap CIs, temperature ablations) is rigorous.

However, the score is constrained by the limited generalizability of the findings (single benchmark WebShop, single world model Qwen2.5-7B), the modest absolute performance of the proposed method (21.50%), and the lack of a deeper root-cause analysis for the severe world model miscalibration. Addressing these weaknesses—specifically by validating on another domain, differentiating from general drift literature, and analyzing *why* the world model miscalibrates—would significantly elevate the paper's scientific impact and defensibility, warranting the post-revision target.