## Summary
This paper investigates Draft-and-Continue Self-Consistency (DCS), a two-stage approach that attempts to improve token efficiency in LLM reasoning by sampling short draft chains, voting on interim answers, and selectively continuing high-vote branches with additional tokens. Evaluated on MATH-500 with Qwen2.5-Math-7B-Instruct, DCS achieves 76.8% accuracy—matching baselines—but uses 19.6% more tokens than standard self-consistency and 109% more than CGES-LNS. The key finding is that ~96% of drafts complete within the 1024-token limit, causing the continuation mechanism to rarely activate. The authors honestly report this negative result and analyze the underlying mechanism.

The paper is well-structured, transparent about limitations, and provides a clear diagnostic explanation for the failure. However, two critical issues limit its scientific rigor: (1) the experimental design compares DCS (~10 API calls, ~10,240 tokens) against 5-sample baselines without budget matching, confounding the efficiency conclusion, and (2) several claims about the gap in prior work and the mechanism of failure lack direct empirical verification. With these fixes, the paper could provide a valuable boundary condition for adaptive compute allocation research.

## Strengths
1. **Honest and transparent reporting of a negative result**: The authors clearly state that DCS fails to improve efficiency and provide a detailed diagnostic explanation (96.3% draft completion rate). This transparency is commendable and aligns with best practices for scientific integrity.

2. **Clear and well-structured methodology**: The DCS algorithm is clearly defined with explicit stages (Draft Sampling, Vote Histogram, Continuation Allocation), concrete hyperparameters (B=7, k=3, T_draft=1024, T_cont=1024), and a thoughtful hedge allocation strategy. The method is easy to understand and reproduce.

3. **Insightful failure mechanism analysis**: The identification of draft completion rate as the key diagnostic metric is a strong analytical contribution. The observation that continuation rarely activates when drafts complete naturally provides a concrete boundary condition for two-stage adaptive reasoning approaches.

4. **Reproducible experimental protocol**: Multi-seed evaluation (3 seeds), variance reporting (mean ± std), and clear baseline definitions (Greedy CoT, Uniform SC, CGES-LNS) support reproducibility.

5. **Candid limitations section**: The authors acknowledge evaluation on a single dataset/model, limited hyperparameter tuning, and generalization boundaries. This honesty improves scientific credibility.

## Weaknesses
1. **Baseline budget mismatch confounds efficiency conclusions (Major)**: DCS uses ~10 API calls and ~10,240 tokens per problem, while Uniform SC uses only $n=5$ samples and CGES-LNS uses $b_{max}=5$. Comparing a 10-call method against 5-sample baselines without a budget-matched control means the efficiency disadvantage is partly an artifact of higher compute budget, not purely algorithmic inefficiency. A Uniform SC ($n=10$) or token-matched baseline is needed to isolate the mechanism's efficiency.

2. **Imprecise gap claim about prior work discarding partial reasoning (Major)**: The introduction states that early-stopping methods "fundamentally discard partial reasoning." This is inaccurate: methods like ESC and CGES stop generating *new* chains when confidence is high, but retain all already-generated chains for voting. The true gap is whether *incomplete* (truncated mid-generation) chains carry signal worth continuing. Tightening this distinction is essential for scientific precision.

3. **Claim that 'continuation provides no additional benefit' lacks direct verification (Minor)**: The analysis states that continuing completed drafts provides no benefit, but does not provide empirical evidence for this assertion. A direct check on the 3.7% of incomplete drafts (e.g., how often does continuation change the final answer vs. the interim answer?) would strengthen this claim from inference to verified fact.

4. **Vague contribution statement C2 (Minor)**: "We conduct rigorous experiments" is a generic template rather than a specific claim. It does not specify what makes the experiments rigorous (e.g., multi-seed evaluation, matched protocols, variance reporting).

5. **Single dataset and model evaluation (Minor)**: Evaluation is limited to MATH-500 with Qwen2.5-Math-7B-Instruct. While acknowledged as a limitation, the generalization claim ("simpler early-stopping methods dominate") would be stronger with at least one additional benchmark (e.g., GSM8K) or model.

6. **Hyperparameter typo in $T_{cont}$ (Minor)**: The text contains "$T_{cont} = \mathrm{i024}$" instead of "1024," which undermines reproducibility and professionalism.

7. **Pareto dominance claim needs scoping (Minor)**: The claim that CGES-LNS "Pareto-dominates" DCS is technically correct under the tested single setting but could be misread as universal dominance. Explicit scoping to "under tested settings" would improve defensibility.

## Key Issues
1. **Baseline budget mismatch (Major validity risk)**: DCS (~10 API calls, ~10,240 tokens) is compared against 5-sample baselines (Uniform SC, CGES-LNS) without a budget-matched control. This means the "negative result" — that DCS uses more tokens — is partially an artifact of DCS generating more chains, not purely a failure of the two-stage mechanism. Adding a Uniform SC ($n=10$) baseline would isolate whether the two-stage overhead is algorithmically inefficient or simply a consequence of higher compute.

2. **Imprecise gap claim (Major precision risk)**: The introduction states early-stopping methods "fundamentally discard partial reasoning." This is inaccurate: ESC and CGES retain completed chains for voting; they stop generating *new* chains. The actual gap concerns whether *truncated mid-generation* chains carry signal worth continuing. This distinction matters because it clarifies exactly what DCS exploits and prevents reviewers from challenging the premise.

3. **Unverified continuation-benefit claim (Minor evidence risk)**: The assertion that "continuing completed drafts provides no additional benefit" is a plausible inference but lacks direct empirical verification. A simple ablation on the 3.7% of incomplete drafts (does continuation change the final answer?) would transform this from speculation to evidence.

4. **Single-setting evaluation (Minor generalization risk)**: Evaluation on MATH-500 with one model limits the scope of the generalization claim. While acknowledged, adding one additional benchmark (e.g., GSM8K) would strengthen the boundary condition finding.

## Actionable Suggestions
1. **Add a budget-matched baseline (Must, P0)**: Include Uniform SC with $n=10$ samples (matching DCS's ~10 total calls) to fairly compare algorithmic efficiency. Report accuracy and tokens for this baseline alongside the existing $n=5$ comparison. This directly addresses the confounding effect of sample-count disparity.

2. **Rewrite the gap claim in Introduction (Must, P0)**: Replace "these approaches fundamentally discard partial reasoning" with a more precise statement: "these approaches determine how many chains to generate, but do not investigate whether partially generated chains—those truncated before completion—carry signal worth selectively continuing." This prevents reviewer challenges about the premise.

3. **Add a continuation-benefit ablation (Nice-to-have, P1)**: On the 3.7% of drafts that are incomplete, compare the final answer after continuation vs. the interim draft answer. Report the percentage of cases where continuation changes the answer. This transforms an inference into verified evidence.

4. **Tighten contribution C2 (Must, P1)**: Replace "We conduct rigorous experiments" with specific details: "We provide a multi-seed evaluation on MATH-500 with Qwen2.5-Math-7B-Instruct, comparing DCS against greedy decoding, uniform self-consistency, and confidence-guided early stopping under matched protocols."

5. **Fix hyperparameter typo (Must, P2)**: Correct "$T_{cont} = \mathrm{i024}$" to "$T_{cont} = 1024$" in Section 2.3.

6. **Scope the Pareto claim (Nice-to-have, P2)**: Add "under tested settings" or "on MATH-500" when claiming CGES-LNS Pareto-dominates DCS, to avoid implying universal dominance.

7. **Consider adding GSM8K evaluation (Nice-to-have, P2)**: A second benchmark would strengthen the generalization claim that "simpler early-stopping methods dominate when draft budgets are sufficient." Even a compact result table would add credibility.

## Storyline Options + Writing Outlines
### Abstract Outline (complete)
*Goal: Frame the negative result as a valuable boundary condition for adaptive compute research.*

- **S1 (Problem/Domain):** Self-consistency improves LLM reasoning but incurs high token costs from generating multiple complete solutions.
- **S2 (Challenge):** Recent early-stopping methods reduce costs by deciding when to stop sampling, but they do not investigate whether partially generated chains carry signal worth selectively continuing.
- **S3 (Method):** We propose Draft-and-Continue Self-Consistency (DCS), a two-stage approach that samples short drafts, votes on interim answers, and extends high-vote branches with additional tokens.
- **S4 (Key Result):** On MATH-500 with Qwen2.5-Math-7B-Instruct, DCS matches baseline accuracy (76.8%) but uses significantly more tokens than both standard self-consistency and confidence-guided early stopping.
- **S5 (Implication):** Analysis reveals that ~96% of drafts complete within the token limit, causing the continuation mechanism to rarely activate. Our finding establishes a boundary condition: when draft budgets are sufficient for most problems, simpler early-stopping methods dominate two-stage branch budgeting.

### Introduction Outline (complete)
*Goal: Improve precision of the gap claim and strengthen contribution specificity.*

- **P1 (Big Picture + Cost):** Scaling test-time compute via self-consistency improves accuracy but is expensive. (Keep current text, add foundational CoT citation).
- **P2 (Prior Work + Precise Gap):** Early-stopping methods (CGES, ESC, Slim-SC) reduce cost by determining how many chains to generate. *Revised Gap:* These approaches stop generating *new* chains when confidence is high, but do not investigate whether *incomplete* chains—truncated mid-generation—carry signal worth selectively continuing. This raises the question: can we focus continuation budget on promising branches?
- **P3 (Proposed Solution):** Introduce DCS with concrete hyperparameters (B=7, k=3, T_draft=1024, T_cont=1024) and the hedge allocation strategy. (Keep current text, fix notation).
- **P4 (Results Preview + Contributions):** DCS fails to improve efficiency because ~96% of drafts complete naturally.
    - C1: Introduce DCS as a two-stage branch continuation approach.
    - C2: Provide multi-seed evaluation on MATH-500 comparing DCS against greedy, uniform, and confidence-guided baselines under matched protocols.
    - C3: Identify a boundary condition for adaptive reasoning: high draft completion rates undermine continuation mechanisms, suggesting simpler early-stopping dominates when draft budgets are sufficient.

## Priority Revision Plan
### P0 — Critical Validity Fixes (Must do before submission)
1. **Add Budget-Matched Baseline**: Run Uniform SC with $n=10$ samples to match DCS's ~10 total calls. Add a row in Table 1 and update the text to compare DCS against this matched baseline. This isolates whether the efficiency gap is algorithmic or simply due to sample count.
2. **Rewrite Gap Claim in Introduction**: Update the paragraph citing early-stopping methods to precisely state the gap: they stop generating *new* chains but do not investigate whether *truncated mid-generation* chains carry signal worth continuing. (See Actionable Suggestion #2 and Mentor Revised Version).
3. **Tighten Contribution C2**: Replace the vague "rigorous experiments" with specific details about the evaluation protocol (multi-seed, matched baselines, variance reporting).

### P1 — High-Impact Quality Improvements (Strongly recommended)
1. **Verify Continuation Benefit**: On the 3.7% of incomplete drafts, check how often continuation changes the final answer compared to the interim draft answer. Add one sentence to Section 3.3 with this finding.
2. **Scope Pareto Claim**: Add "under tested settings" or "on MATH-500" to the Pareto dominance claim to prevent overgeneralization.
3. **Fix Hyperparameter Typo**: Correct $T_{cont} = \mathrm{i024}$ to $T_{cont} = 1024$.

### P2 — Optional Strengthening (Nice-to-have)
1. **Add Second Benchmark**: Run DCS and baselines on GSM8K to strengthen the generalization of the "draft completion rate" boundary condition.
2. **Expand Related Work**: Add brief citations to recent efficiency trade-off studies (e.g., Reasoning in Token Economies, Reflective Confidence) to better position the negative result.

### Page Coverage Audit
| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| Page 1 | 4 | Covered | Abstract, Intro context, gap claim, method intro |
| Page 2 | 2 | Covered | Contributions, Problem setup/Equation |
| Page 3 | 2 | Covered | Hyperparameters (typo), Setup (baseline mismatch) |
| Page 4 | 2 | Covered | Results analysis, Diagnostic analysis |
| Page 5 | 0 | Skipped | Discussion/Related Work/Conclusion are synthesis; key defects already annotated in Methods/Experiments |

```text
ASCII Diagram — Paper Structure & Evidence Map
[Problem: Self-consistency is expensive]
    -> [Gap: Early stopping decides 'how many', not 'which partial chains to continue']
    -> [Method: DCS (Draft -> Vote -> Continue)]
    -> [Experiment: MATH-500, Qwen2.5-Math-7B]
    -> [Result: 76.8% accuracy, but 19.6% more tokens than SC-5, 109% more than CGES]
    -> [Key Evidence: 96.3% draft completion rate -> continuation rarely activates]
    -> [Risk: Baseline mismatch (SC-5 vs DCS-10 calls) confounds efficiency claim]
    -> [Fix: Add SC-10 baseline + rewrite gap claim]

ASCII Diagram — Revision Strategy Roadmap
| Priority | Low Effort | High Effort |
|---|---|---|
| High Impact | Rewrite gap claim, tighten C2 | Add SC-10 baseline |
| Medium Impact | Fix T_cont typo, scope Pareto claim | Verify continuation benefit ablation |
| Low Impact | Add second benchmark (GSM8K) | Expand related work citations |
```

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| Exp 1: Main Results | Test if two-stage continuation improves token efficiency over standard SC and early stopping. | MATH-500, Qwen2.5-Math-7B. DCS (B=7, k=3) vs Greedy CoT, Uniform SC (n=5), CGES-LNS. | Accuracy (%), Avg Tokens, Avg Calls, Efficiency | DCS matches accuracy (76.8%) but uses ~4115 tokens (+19.6% vs SC) and ~10 calls. | DCS does not improve efficiency. | **Budget mismatch**: DCS (~10 calls) vs SC-5/CGES-5. No token-matched baseline to isolate algorithmic overhead. |
| Exp 2: Diagnostics | Explain failure mechanism via draft completion metrics. | Analyze DCS runs (seeds 42, 123, 456). | Fallback (%), Draft Complete (%) | 96.3% of drafts complete within 1024 tokens. Fallback is 3.73%. | High draft completion undermines continuation. | Claim "continuation provides no benefit" is asserted without direct check on the 3.7% incomplete drafts. |

### (b) Research-Theme Gap Diagnosis
- **Validity Risk**: The negative efficiency result is partially an artifact of comparing a 10-call budget against 5-call baselines. The core claim (DCS is inefficient) is valid only if algorithmic overhead is isolated.
- **Evidence Gap**: The assertion that continuing incomplete chains adds no value is inferred from the high completion rate, not directly measured.
- **Generalization Gap**: Single benchmark (MATH-500) and single model (Qwen2.5-Math-7B) limit the scope of the "boundary condition" claim.

### (c) Proposed Research Experiments (P0/P1/P2)

| Priority | Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Expected Gain |
|---|---|---|---|---|---|---|---|---|
| **P0** | DCS is algorithmically less efficient than standard SC. | With matched API calls ($n=10$), SC should match or beat DCS in accuracy/tokens, isolating the two-stage overhead. | Run Uniform SC with $n=10$ on MATH-500 (3 seeds). | DCS (B=7+k=3). | Accuracy, Tokens, Calls | DCS does not Pareto-dominate SC-10. | 1 GPU-hour | Resolves baseline confounding. |
| **P1** | Continuation provides no additional benefit on incomplete drafts. | For the 3.7% of drafts that do not complete, continuing them rarely changes the final answer. | Analyze existing DCS outputs. Compare interim answer vs. final continued answer for incomplete drafts. | N/A | Answer flip rate (%) | Flip rate < 10% on incomplete set. | 0 (analysis only) | Verifies mechanism claim. |
| **P2** | Boundary condition generalizes to other benchmarks. | High draft completion rate also undermines DCS on GSM8K. | Run DCS and baselines on GSM8K. | SC-5, CGES-LNS. | Accuracy, Completion Rate | Consistent failure pattern. | 2-3 GPU-hours | Strengthens generalization. |

```text
ASCII Diagram — Experiment Upgrade Plan
Stage 1 (P0 - Today): Add Uniform SC (n=10) baseline to isolate algorithmic efficiency.
Stage 2 (P1 - Today): Analyze incomplete drafts (3.7%) to verify continuation benefit.
Stage 3 (P2 - Next Week): Run GSM8K benchmark to generalize boundary condition finding.
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Introduce DCS: two-stage draft-and-continue approach for SC efficiency. | [1], [2], [3], [4] | partially_overlapping | DCS's two-stage vote-then-continue mechanism shares conceptual overlap with Reflective Confidence [1] (online self-correction of partial reasoning) and Draft-Thinking [2] (concise draft-style reasoning). The specific vote-histogram + hedge allocation is a novel instantiation, but the core idea of exploiting partial chains is not new. | High | Position as a specific instantiation of partial-chain exploitation, with explicit differentiation from reflection-based approaches. |
| C2 | Multi-seed evaluation comparing DCS against greedy, uniform SC, and CGES-LNS on MATH-500. | [3], [5] | supported | The specific experimental comparison under this protocol is directly reported. | High | None. |
| C3 | High draft completion rates undermine continuation; simpler early-stopping dominates. | [5], [6], [7] | partially_overlapping | The boundary condition finding aligns with "Reasoning in Token Economies" [5] (complex strategies often don't beat simple SC when budgets are matched) and "Answer Convergence" [6] (models converge to stable answers early). The specific quantitative diagnosis (96.3% completion) is a new empirical observation. | Medium | Frame as a quantitative boundary condition rather than a general theorem. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Efficient Self-Consistency | Branch 1: Early Stopping | [3], [4], [8] | Confidence/entropy signals indicate when to stop sampling. | Stop *new* chains; retain completed chains. DCS attempts to *continue* partial chains. | Low risk: Different mechanism (stop vs. continue). |
| Root | Branch 2: Partial Chain Exploitation | [1], [2], [9] | Incomplete reasoning traces may carry signal worth leveraging. | Reflective Confidence [1] uses low-confidence signals for reflection. DCS uses vote histograms for selection. | Medium risk: Overlapping goal (exploit partial chains). |
| Root | Branch 3: Budget-Aware Evaluation | [5], [6], [7] | Efficiency must be evaluated under matched compute budgets. | Prior work shows simple SC often wins when budgets are matched. DCS's negative result is consistent with this. | Low risk: Supports the conclusion. |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] Reflective Confidence | Math reasoning, self-consistency | Low-confidence triggers reflection prompts for online correction. | Exploiting incomplete reasoning paths instead of discarding them. | Reflection-based (semantic) vs. Vote-based (syntactic) continuation. | Lowers C1 novelty to partially_overlapping. |
| [2] Draft-Thinking | Long-CoT reasoning efficiency | Learn concise draft-style reasoning via curriculum learning. | Two-stage reasoning with draft phase. | Learning-based (training) vs. Inference-time (no training). | Low direct overlap; different paradigm. |
| [5] Reasoning in Token Economies | LLM reasoning strategy efficiency | Matched-budget evaluation reveals simple SC often wins. | Complex strategies often don't beat simple baselines. | General budget analysis vs. Specific continuation mechanism. | Supports C3 conclusion. |
| [6] Answer Convergence | Early stopping via answer consistency | Models converge early; use convergence signal to stop. | Draft completion as a signal. | Convergence-based stopping vs. Vote-based continuation. | Low direct overlap. |

### Contribution-level Novelty Conclusion
C1 is **partially_overlapping**: the specific vote-histogram + hedge allocation mechanism is a novel instantiation, but the broader idea of exploiting partial chains overlaps with Reflective Confidence and Draft-Thinking. C2 is **supported** as a specific empirical contribution. C3 is **partially_overlapping**: the 96.3% completion finding is a new empirical observation, but the broader conclusion aligns with prior budget-aware evaluation work. The paper should reposition C1 to emphasize its specific mechanism rather than claiming general novelty in partial-chain exploitation.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
Efficient Self-Consistency (Root)
├── Branch 1: Early Stopping (stop new chains when confident)
│   ├── Leaf 1.1: Confidence-based stopping [3]
│   ├── Leaf 1.2: Entropy-based stopping [4]
│   └── Leaf 1.3: Answer convergence stopping [6]
├── Branch 2: Partial Chain Exploitation (leverage incomplete chains)
│   ├── Leaf 2.1: Reflection-based correction [1]
│   ├── Leaf 2.2: Draft-style learning [2]
│   └── Leaf 2.3: Vote-based continuation (DCS, this paper)
└── Branch 3: Budget-Aware Evaluation (matched compute comparison)
    ├── Leaf 3.1: Token economy analysis [5]
    └── Leaf 3.2: Adaptive compute allocation [7]
```

## References
[1] Reflective Confidence: Correcting Reasoning Flaws via Online Self-Correction 2512.18605

[2] Draft-Thinking: Learning Efficient Reasoning in Long Chain-of-Thought LLMs 2603.00578

[3] CGES: Confidence-Guided Early Stopping for Efficient and Accurate Self-Consistency abs/2511.02603

[4] Escape Sky-high Cost: Early-stopping Self-Consistency for Multi-step Reasoning 2401.10480

[5] Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies 2406.06461

[6] Answer Convergence as a Signal for Early Stopping in Reasoning 2506.02536

[7] Trade-offs in Large Reasoning Models: An Empirical Analysis of Deliberative and Adaptive Reasoning over Foundational Capabilities 2503.17979

[8] Optimal Self-Consistency for Efficient Reasoning with Large Language Models abs/2511.12309

[9] CoDE-Stop: Early Stopping for Large Reasoning Models via Confidence Dynamics 2604.04930

## Scores
**Final Score: 5.0/10**

The paper provides a clear, transparent, and honest analysis of a negative result. The diagnostic finding (96.3% draft completion rate) is insightful and valuable for adaptive reasoning research. The method is well-defined and the writing is generally clear.

However, the scientific rigor is limited by two major factors:
1. **Baseline budget mismatch**: Comparing a 10-call method (DCS) against 5-sample baselines (SC, CGES) without a matched budget control confounds the efficiency conclusion, making it unclear whether the overhead is algorithmic or simply due to higher compute.
2. **Imprecise gap framing**: The claim that prior work "discards partial reasoning" is inaccurate, which weakens the motivation for the proposed method.

These issues are fixable (P0: add SC-10 baseline, rewrite gap claim). Once resolved, the paper would reach a significantly higher quality tier.

**Post-Revision Target: [6.5, 7.5]/10**