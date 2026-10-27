## Summary
## Novelty Verification & Related-Work Matrix

### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | First rigorous test of Tiny-LR proxy hypothesis for SFT dataset ranking, finding it does not improve transfer. | [1], [6] | supported | [1] establishes Tiny-LR in pretraining; no prior paper explicitly tests Tiny-LR for SFT dataset ranking. The negative result is a novel empirical finding in the SFT post-training regime. | High | Scope explicitly to "SFT dataset ranking" rather than general proxy data selection. |
| C2 | Standard-LR Proxy SFT provides reliable ranking signals (PDA=0.712) and correctly identifies the best dataset. | [2], [3], [5] | partially_overlapping | Prior work (e.g., [2], [5]) uses proxy signals (LLM scorers, perplexity, influence metrics) for SFT data selection. This paper shows standard-LR fine-tuning proxy works, which is consistent with existing proxy practices but adds a specific LR-focused validation. | Medium | Frame as "LR-calibrated proxy validation" rather than a new proxy method. |
| C3 | Benchmark-specific behavior: Tiny-LR preserves signals on MATH-500 but fails on GSM8K, revealing evaluation-method dependency. | [4], [5] | supported | The observation that proxy ranking transfer is evaluation-method-dependent (content-based vs. exact-match) is a novel empirical pattern. [4] discusses SFT score biases but does not analyze LR-specific benchmark divergence. | High | Bound claim to "consistent with evaluation-method dependency" without asserting unverified surface-length causality. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Data Selection for LLMs | Proxy-based Ranking | [1], [5] | Proxy model performance correlates with target model performance; transfer depends on proxy training settings. | This paper tests LR effects specifically for SFT ranking, whereas [1] focuses on pretraining and [5] uses perplexity proxies. | Low risk: SFT-specific LR testing is clearly differentiated. |
| Data Selection for LLMs | Metric-based Scoring | [2], [3] | Automatic quality/diversity/complexity metrics can predict dataset value for SFT without full fine-tuning. | Uses trained proxy models rather than training-free scorers or LLM-as-judge metrics. | Low risk: proxy-SFT evaluation is a distinct paradigm. |
| Optimization Dynamics | Learning Rate as Regularizer | [6], [7] | LR mediates stability-plasticity tradeoff in SFT; smaller LR preserves pretrained features but may limit adaptation. | This paper applies LR variation to proxy ranking transfer rather than target model capability preservation. | Medium risk: conceptual overlap with LR regularization, but application to proxy ranking is novel. |
| Proxy Transfer Reliability | SFT Score Biases | [4] | High SFT scores do not reliably predict downstream (e.g., RL) outcomes; scores can be biased toward simple/homogeneous data. | This paper finds Tiny-LR proxy rankings are biased by evaluation methodology (exact-match vs. content-based). | Low risk: [4] discusses SFT-RL transfer; this paper discusses proxy-target ranking transfer. |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | Pretraining data recipe assessment | Tiny-LR proxy training to prevent hyperparameter-dependent ranking flips | Core Tiny-LR mechanism (small LR preserves ranking order) | Pretraining regime (random-feature assumption) vs. SFT regime (structured features) | Confirms C1 novelty: Tiny-LR tested in a fundamentally different training regime. |
| [2] | Automatic SFT data selection | DEITA: complexity/quality/diversity scoring with LLM-as-judge | Proxy-based evaluation for SFT data value | Training-free LLM scorers vs. fine-tuned small proxy models | Differentiates C2: this paper uses proxy fine-tuning rather than training-free metrics. |
| [5] | Pretraining checkpoint selection for SFT | Perplexity and learning-to-compare proxies to predict SFT outcomes | Proxy metrics predicting SFT effectiveness | Proxy models during pretraining vs. proxy models during SFT | Reinforces C1 novelty: focuses on pretraining-to-SFT prediction, not SFT-to-SFT transfer. |
| [4] | SFT-RL post-training transfer | SFT scores as proxies for RLVR outcomes; proposes generalization loss proxies | Proxy score biases and transfer failure modes | SFT-to-RL transfer vs. proxy-to-target SFT transfer | Complements C3: both find proxy scores are biased, but this paper isolates LR and evaluation-method effects. |
| [6] | Catastrophic overtraining in SFT | LR acts as implicit regularizer; small LR preserves features, large LR causes forgetting | LR dynamics during SFT | Target model capability preservation vs. proxy ranking transfer | Contextualizes C3: supports the idea that LR dynamics are fundamentally different in SFT vs. pretraining. |

**Contribution-level Novelty Conclusion:**
C1 is supported: no prior work explicitly tests the Tiny-LR proxy hypothesis in the SFT dataset ranking setting; Wang et al. (2025) [1] is limited to pretraining data curation. C2 is partially overlapping: proxy-based SFT data selection is an active area (e.g., DEITA [2], perplexity proxies [5]), but the specific validation of standard-LR proxy fine-tuning as a reliable ranking signal is a distinct, complementary finding. C3 is supported: the benchmark-specific pattern (MATH-500 success vs. GSM8K failure under Tiny-LR) is a novel empirical observation that highlights evaluation-method dependency in proxy ranking transfer. No claim requires substantial repositioning, though C3's mechanism interpretation should be bounded to avoid over-claiming.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
LLM Data Selection & Proxy Evaluation (Root)
├── Branch 1: Proxy-Based Ranking
│   ├── Leaf 1.1: Pretraining Proxy Methods [1] (Tiny-LR for pretraining recipes)
│   └── Leaf 1.2: SFT Proxy Methods [This Paper] (Tiny-LR test for SFT ranking)
├── Branch 2: Training-Free Scoring Metrics
│   ├── Leaf 2.1: LLM-as-Judge Scorers [2] (DEITA, complexity/quality metrics)
│   └── Leaf 2.2: Perplexity/Compression Proxies [5] (Pretraining checkpoint prediction)
├── Branch 3: Optimization Dynamics in SFT
│   ├── Leaf 3.1: LR as Implicit Regularizer [6] (Stability-plasticity in SFT)
│   └── Leaf 3.2: Massive SFT Empirical Analysis [7] (Data/layer/training factors)
└── Branch 4: Proxy Transfer Reliability
    ├── Leaf 4.1: SFT-to-RL Transfer Biases [4] (SFT score biases for RL outcomes)
    └── Leaf 4.2: SFT-to-SFT Ranking Transfer [This Paper] (Proxy-target ranking transfer)

Manuscript Positioning:
- Novelty Axis: SFT Proxy Methods (Leaf 1.2) + SFT-to-SFT Ranking Transfer (Leaf 4.2)
- Value Solved: Demonstrates that Tiny-LR pretraining insights do not transfer to SFT; identifies evaluation-method dependency in proxy ranking reliability.
```

## Strengths
1. **Clear and testable hypothesis:** The paper directly tests a concrete, falsifiable hypothesis (Tiny-LR improves proxy ranking transfer in SFT) motivated by recent theoretical and empirical work in pretraining. The experimental design is straightforward and the results are unambiguous.

2. **Benchmark-specific discovery:** The finding that Tiny-LR performs well on MATH-500 but fails on GSM8K is a novel and practically informative observation. It suggests that proxy ranking behavior is evaluation-method-dependent, which is a valuable insight for practitioners selecting proxy strategies.

3. **Practical guidance:** The paper provides clear, actionable advice for practitioners: use standard learning rates for proxy-based SFT dataset ranking. This conclusion is well-supported by the reported PDA and statistical significance results.

4. **Transparent limitations:** The authors honestly acknowledge key scope boundaries (single model family, single domain, limited LR values), which improves credibility and guides future research directions.

5. **Reproducible experimental setup:** The paper reports detailed hyperparameters (LoRA rank 16, alpha 32, batch size 16, cosine schedule, warmup 0.1), multiple seeds, and clear evaluation benchmarks. The code is publicly available, supporting reproducibility.

## Weaknesses
1. **Unverified mechanism hypothesis (Major):** The paper proposes that Tiny-LR "amplifies sensitivity to surface-level features such as response length" as the explanation for GSM8K failure. This is presented with near-factual certainty in the Discussion, but the paper provides no direct evidence: no length-controlled ablation, no statistical correlation between average response length and Tiny-LR ranking bias, and no representation-level analysis. Without these, the mechanism claim remains a plausible but unverified hypothesis.

2. **Step-count asymmetry between conditions (Major):** Standard-LR Proxy uses 500 steps while Tiny-LR Proxy uses 1000 steps. This means the total training budget is not equal, introducing a confound: Tiny-LR may fail because it trains for 2x steps on insufficient LR, not purely because of LR effects. A matched-step comparison is needed to isolate the learning rate effect.

3. **Overstated severity of GSM8K result (Minor):** The paper repeatedly states that Tiny-LR "fails completely" on GSM8K (PDA = 0.515). This is only marginally above chance (0.500) and statistically insignificant (p = 0.846). The wording "fails completely" inflates the severity and misrepresents the empirical finding.

4. **Missing theoretical bridge for negative result (Major):** The Introduction does not articulate why the Tiny-LR theory from pretraining might fail in SFT. The random-feature model assumption underlying Wang et al. (2025) does not hold for instruction-tuned models operating on structured pretrained weights. Without this theoretical framing, the negative result reads as empirically interesting but conceptually unmotivated.

5. **Limited benchmark scope for benchmark-specific claim (Minor):** The benchmark-specific claim (Tiny-LR works for content-based evaluation, fails for exact-match) is based on only two benchmarks (GSM8K, MATH-500). Extending to additional benchmarks would clarify whether this pattern generalizes.

6. **Conflation of PEFT and LR mechanisms in Related Work (Minor):** Section 2.3 conflates parameter-efficient fine-tuning (LoRA, which restricts *which* parameters update) with learning rate reduction (which restricts update *magnitude*). These are distinct mechanisms and should be separated conceptually.

7. **Missing ranking fidelity discussion (Minor):** Section 4.1 reports PDA = 0.712 for Standard-LR but does not discuss that ~29% of pairwise relationships remain inverted. Additionally, the Training-Free NLL baseline (PDA = 0.636) is not discussed in terms of practical cost-benefit trade-off.

## Key Issues
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit | Priority |
|---|---|---|---|---|---|
| Unverified mechanism hypothesis (surface-level amplification) | Major | No length-controlled ablation, no correlation analysis, no representation-level evidence | Add a length-correlation analysis (response length vs. Tiny-LR ranking delta); bound mechanism claim to "hypothesis" language | Improves scientific defensibility of the core interpretive claim | P1 |
| Step-count asymmetry confound (500 vs. 1000 steps) | Major | Standard-LR and Tiny-LR use different training budgets, confounding LR effect with step count | Run a matched-step ablation (e.g., both at 500 steps or both at 1000 steps) | Isolates the pure learning rate effect; strengthens negative result claim | P1 |
| Overstated severity of GSM8K result ("fails completely" for PDA=0.515) | Minor | Wording inflates a marginally-above-random, statistically insignificant result | Replace "fails completely" with "performs at chance level" (PDA=0.515, p=0.846) | Aligns claim strength with evidence; improves objectivity | P2 |
| Missing theoretical bridge explaining why Tiny-LR may fail in SFT | Major | Introduction does not contrast pretraining (random-feature) vs. SFT (structured-feature) assumptions | Add 1-2 sentences on the random-feature assumption gap; cite SFT-specific optimization literature | Makes the negative result theoretically motivated rather than purely empirical | P1 |
| Conflation of PEFT (parameter restriction) and LR reduction (magnitude restriction) in Related Work | Minor | Section 2.3 treats LoRA/PEFT and LR reduction as equivalent mechanisms | Separate the two mechanisms conceptually; add implicit regularization framing | Improves theoretical precision and motivation clarity | P2 |
| Limited benchmark scope (two benchmarks for benchmark-specific claim) | Minor | MATH-500 and GSM8K are the only evaluation targets | Acknowledge scope limitation; propose additional benchmarks (e.g., MMLU, ARC) as future work | Bounds the claim appropriately; reduces overgeneralization risk | P2 |
| Missing ranking fidelity discussion (29% inverted pairs; NLL cost-benefit) | Minor | Section 4.1 reports PDA but does not interpret practical implications | Add a sentence on ranking fidelity and cost-benefit trade-off between NLL and Standard-LR | Provides practical context for practitioners deciding between proxy strategies | P2 |

## Actionable Suggestions
1. **Add a matched-step ablation (P1, Must).** Run Tiny-LR and Standard-LR with identical step counts (e.g., both at 500 steps or both at 1000 steps) to isolate the learning rate effect from total training budget. Report the resulting PDAs alongside the current results. This directly addresses the step-count confound and strengthens the negative result claim.

2. **Perform a length-correlation analysis (P1, Must).** Compute the average response length for each of the 12 datasets under Tiny-LR proxy fine-tuning, then compute the Pearson/Spearman correlation between response length and the Tiny-LR ranking delta (Tiny-LR rank minus target rank). A significant positive correlation would support the surface-length amplification hypothesis. Report this analysis in Section 4.3.

3. **Bound the mechanism hypothesis language (P1, Must).** Throughout the Discussion and Abstract, replace definitive mechanism claims ("The mechanism appears to be that...") with hypothesis-consistent language ("We hypothesize that...", "These results are consistent with the hypothesis that..."). Add a sentence acknowledging that representation-level analysis would be needed to confirm the "robust representations" claim.

4. **Add theoretical framing for SFT vs. Pretraining differences (P1, Must).** In the Introduction (after paragraph 2), add 1-2 sentences explaining why the Tiny-LR theory from pretraining may not transfer to SFT. Specifically, note that Wang et al. (2025) relies on random-feature model assumptions, whereas SFT operates on structured pretrained weights. This makes the negative result theoretically motivated rather than purely empirical.

5. **Separate PEFT and LR mechanisms in Related Work (P2, Must).** In Section 2.3, explicitly distinguish between parameter-efficient fine-tuning (LoRA, which restricts *which* parameters are updated) and learning rate reduction (which restricts update *magnitude* across all trainable parameters). Add one sentence framing LR as an implicit regularizer in SFT, citing Rofin et al. (2026) [2604.13627].

6. **Add benchmark scope acknowledgment (P2, Must).** In Section 5.2 (Limitations), add a limitation noting that the benchmark-specific claim is based on only two evaluation benchmarks. Propose extending to additional benchmarks (e.g., MMLU, ARC, GSM8K-Hard) as a future direction.

7. **Fix formatting artifacts (P2, Nice-to-have).** Correct the LR notation artifact in the Introduction ($1 \times \mathrm { \bar { 1 0 } ^ { - 5 } }$ should be $1 \times 10^{-5}$) and the double-parenthesis in Section 4.1 ($0 . 0 4 2 )$ )).

## Storyline Options + Writing Outlines
**Core Narrative Arc:**
The current narrative follows a clear arc: Problem (SFT data selection is expensive) → Gap (Proxy rankings may not transfer) → Motivation (Tiny-LR works in pretraining) → Test (Does Tiny-LR work in SFT?) → Result (Tiny-LR fails; Standard-LR works; benchmark-specific pattern emerges). This structure is solid. The primary improvement needed is to add a theoretical bridge explaining *why* pretraining insights might not apply to SFT, and to soften the mechanism claims.

## Priority Revision Plan
**P0 — Must (publication-critical):**
1. **Matched-step ablation:** Run Tiny-LR Proxy at 500 steps (matching Standard-LR) and report PDA/Spearman. This isolates the pure learning rate effect from the step-count confound. Estimated cost: ~1-2 days GPU time using the existing training script.
2. **Scope-bound the mechanism hypothesis:** Replace definitive mechanism language in Abstract, Section 4.3, and Section 5.1 with hypothesis-consistent wording ("consistent with the hypothesis that...", "we hypothesize that..."). Add a sentence acknowledging that representation-level analysis is needed to confirm the "robust representations" claim. Estimated cost: ~1 day writing.

**P1 — Should (quality-critical):**
3. **Add theoretical bridge in Introduction:** After paragraph 2, insert 1-2 sentences contrasting the random-feature assumptions of Wang et al. (2025) with the structured-feature nature of SFT. This makes the negative result theoretically motivated. Estimated cost: ~0.5 day writing.
4. **Length-correlation analysis (low-cost proxy):** Compute average response length per dataset under Tiny-LR fine-tuning, then correlate with Tiny-LR ranking delta. A significant correlation would provide indirect support for the surface-length hypothesis. Estimated cost: ~0.5 day analysis.
5. **Separate PEFT and LR mechanisms in Related Work:** Rewrite Section 2.3 to distinguish parameter restriction (LoRA) from magnitude restriction (LR), and add implicit regularization framing. Estimated cost: ~0.5 day writing.

**P2 — Nice-to-have (improvement):**
6. **Add benchmark scope limitation:** Extend Section 5.2 to note the two-benchmark scope limit and propose additional benchmarks as future work. Estimated cost: ~0.25 day writing.
7. **Fix formatting artifacts:** Correct LR notation ($1 \times \mathrm { \bar { 1 0 } ^ { - 5 } }$ → $1 \times 10^{-5}$) and double-parenthesis in Section 4.1. Estimated cost: ~15 minutes.
8. **Add ranking fidelity discussion:** In Section 4.1, add a sentence noting that PDA=0.712 means ~29% inverted pairs, and discuss the practical cost-benefit between NLL (free) and Standard-LR (training cost). Estimated cost: ~0.25 day writing.

```text
ASCII Diagram — Revision Strategy Roadmap
[Step-count confound (P0)]
    -> Run matched-step ablation (500 steps both)
    -> Report delta PDA
    -> Expected gain: isolate pure LR effect

[Mechanism over-claim (P0)]
    -> Soften wording to "hypothesis"
    -> Add length-correlation analysis (P1)
    -> Expected gain: defensible interpretation

[Theoretical framing (P1)]
    -> Add random-feature vs structured-feature gap
    -> Cite SFT optimization literature
    -> Expected gain: motivated negative result

[Related Work precision (P1)]
    -> Separate PEFT (parameter restriction) from LR (magnitude restriction)
    -> Add implicit regularization framing
    -> Expected gain: conceptual clarity

[Scope bounding (P2)]
    -> Acknowledge 2-benchmark limit
    -> Fix formatting artifacts
    -> Add ranking fidelity discussion
    -> Expected gain: reduced overgeneralization risk
```

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Tiny-LR improves proxy ranking transfer in SFT | 12 math datasets, 50K each; Qwen2.5-1.5B proxy, Qwen2.5-7B target; GSM8K + MATH-500 evaluation; 3 seeds | PDA, Spearman ρ, Top-1 match | Tiny-LR fails (PDA=0.500); Standard-LR succeeds (PDA=0.712, p=0.042) | Refutation of Tiny-LR in SFT | Step-count asymmetry (500 vs. 1000) confounds LR effect |
| E2 | Benchmark-specific behavior of Tiny-LR | Same setup as E1; per-benchmark analysis (MATH-500 vs. GSM8K) | PDA, Spearman ρ per benchmark | Tiny-LR succeeds on MATH-500 (PDA=0.818), fails on GSM8K (PDA=0.515) | Benchmark-specific pattern | Only two benchmarks; no controlled length analysis |
| E3 | Training-Free NLL as a cost-free baseline | Same setup; compute NLL of each dataset under base model | PDA, Spearman ρ | NLL intermediate (PDA=0.636), not significant (p=0.236) | NLL is weaker than Standard-LR for ranking | No compute-cost comparison reported |

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | First rigorous test of Tiny-LR proxy hypothesis for SFT dataset ranking, finding it does not improve transfer. | [1], [6] | supported | [1] establishes Tiny-LR in pretraining; no prior paper explicitly tests Tiny-LR for SFT dataset ranking. The negative result is a novel empirical finding in the SFT post-training regime. | High | Scope explicitly to "SFT dataset ranking" rather than general proxy data selection. |
| C2 | Standard-LR Proxy SFT provides reliable ranking signals (PDA=0.712) and correctly identifies the best dataset. | [2], [3], [5] | partially_overlapping | Prior work (e.g., [2], [5]) uses proxy signals (LLM scorers, perplexity, influence metrics) for SFT data selection. This paper shows standard-LR fine-tuning proxy works, which is consistent with existing proxy practices but adds a specific LR-focused validation. | Medium | Frame as "LR-calibrated proxy validation" rather than a new proxy method. |
| C3 | Benchmark-specific behavior: Tiny-LR preserves signals on MATH-500 but fails on GSM8K, revealing evaluation-method dependency. | [4], [5] | supported | The observation that proxy ranking transfer is evaluation-method-dependent (content-based vs. exact-match) is a novel empirical pattern. [4] discusses SFT score biases but does not analyze LR-specific benchmark divergence. | High | Bound claim to "consistent with evaluation-method dependency" without asserting unverified surface-length causality. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Data Selection for LLMs | Proxy-based Ranking | [1], [5] | Proxy model performance correlates with target model performance; transfer depends on proxy training settings. | This paper tests LR effects specifically for SFT ranking, whereas [1] focuses on pretraining and [5] uses perplexity proxies. | Low risk: SFT-specific LR testing is clearly differentiated. |
| Data Selection for LLMs | Metric-based Scoring | [2], [3] | Automatic quality/diversity/complexity metrics can predict dataset value for SFT without full fine-tuning. | Uses trained proxy models rather than training-free scorers or LLM-as-judge metrics. | Low risk: proxy-SFT evaluation is a distinct paradigm. |
| Optimization Dynamics | Learning Rate as Regularizer | [6], [7] | LR mediates stability-plasticity tradeoff in SFT; smaller LR preserves pretrained features but may limit adaptation. | This paper applies LR variation to proxy ranking transfer rather than target model capability preservation. | Medium risk: conceptual overlap with LR regularization, but application to proxy ranking is novel. |
| Proxy Transfer Reliability | SFT Score Biases | [4] | High SFT scores do not reliably predict downstream (e.g., RL) outcomes; scores can be biased toward simple/homogeneous data. | This paper finds Tiny-LR proxy rankings are biased by evaluation methodology (exact-match vs. content-based). | Low risk: [4] discusses SFT-RL transfer; this paper discusses proxy-target ranking transfer. |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | Pretraining data recipe assessment | Tiny-LR proxy training to prevent hyperparameter-dependent ranking flips | Core Tiny-LR mechanism (small LR preserves ranking order) | Pretraining regime (random-feature assumption) vs. SFT regime (structured features) | Confirms C1 novelty: Tiny-LR tested in a fundamentally different training regime. |
| [2] | Automatic SFT data selection | DEITA: complexity/quality/diversity scoring with LLM-as-judge | Proxy-based evaluation for SFT data value | Training-free LLM scorers vs. fine-tuned small proxy models | Differentiates C2: this paper uses proxy fine-tuning rather than training-free metrics. |
| [5] | Pretraining checkpoint selection for SFT | Perplexity and learning-to-compare proxies to predict SFT outcomes | Proxy metrics predicting SFT effectiveness | Proxy models during pretraining vs. proxy models during SFT | Reinforces C1 novelty: focuses on pretraining-to-SFT prediction, not SFT-to-SFT transfer. |
| [4] | SFT-RL post-training transfer | SFT scores as proxies for RLVR outcomes; proposes generalization loss proxies | Proxy score biases and transfer failure modes | SFT-to-RL transfer vs. proxy-to-target SFT transfer | Complements C3: both find proxy scores are biased, but this paper isolates LR and evaluation-method effects. |
| [6] | Catastrophic overtraining in SFT | LR acts as implicit regularizer; small LR preserves features, large LR causes forgetting | LR dynamics during SFT | Target model capability preservation vs. proxy ranking transfer | Contextualizes C3: supports the idea that LR dynamics are fundamentally different in SFT vs. pretraining. |

**Contribution-level Novelty Conclusion:**
C1 is supported: no prior work explicitly tests the Tiny-LR proxy hypothesis in the SFT dataset ranking setting; Wang et al. (2025) [1] is limited to pretraining data curation. C2 is partially overlapping: proxy-based SFT data selection is an active area (e.g., DEITA [2], perplexity proxies [5]), but the specific validation of standard-LR proxy fine-tuning as a reliable ranking signal is a distinct, complementary finding. C3 is supported: the benchmark-specific pattern (MATH-500 success vs. GSM8K failure under Tiny-LR) is a novel empirical observation that highlights evaluation-method dependency in proxy ranking transfer. No claim requires substantial repositioning, though C3's mechanism interpretation should be bounded to avoid over-claiming.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
LLM Data Selection & Proxy Evaluation (Root)
├── Branch 1: Proxy-Based Ranking
│   ├── Leaf 1.1: Pretraining Proxy Methods [1] (Tiny-LR for pretraining recipes)
│   └── Leaf 1.2: SFT Proxy Methods [This Paper] (Tiny-LR test for SFT ranking)
├── Branch 2: Training-Free Scoring Metrics
│   ├── Leaf 2.1: LLM-as-Judge Scorers [2] (DEITA, complexity/quality metrics)
│   └── Leaf 2.2: Perplexity/Compression Proxies [5] (Pretraining checkpoint prediction)
├── Branch 3: Optimization Dynamics in SFT
│   ├── Leaf 3.1: LR as Implicit Regularizer [6] (Stability-plasticity in SFT)
│   └── Leaf 3.2: Massive SFT Empirical Analysis [7] (Data/layer/training factors)
└── Branch 4: Proxy Transfer Reliability
    ├── Leaf 4.1: SFT-to-RL Transfer Biases [4] (SFT score biases for RL outcomes)
    └── Leaf 4.2: SFT-to-SFT Ranking Transfer [This Paper] (Proxy-target ranking transfer)

Manuscript Positioning:
- Novelty Axis: SFT Proxy Methods (Leaf 1.2) + SFT-to-SFT Ranking Transfer (Leaf 4.2)
- Value Solved: Demonstrates that Tiny-LR pretraining insights do not transfer to SFT; identifies evaluation-method dependency in proxy ranking reliability.
```

## References
[1] Can Small Training Runs Reliably Guide Data Curation? Rethinking Proxy-Model Practice 2512.24503

[2] What Makes Good Data for Alignment? A Comprehensive Study of Automatic Data Selection in Instruction Tuning 2312.15685

[3] A Survey on Data Selection for LLM Instruction Tuning 2402.05123

[4] Quagmires in SFT-RL Post-Training: When High SFT Scores Mislead and What to Use Instead 2510.01624

[5] Can Pre-training Indicators Reliably Predict Fine-tuning Outcomes of LLMs? 2504.12491

[6] (How) Learning Rates Regulate Catastrophic Overtraining 2604.13627

[7] Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and Training Factors Shape LLM Alignment Quality 2506.14681

## Scores
**Final Score:** 6.0/10

This paper presents a clear and valuable empirical refutation of the Tiny-LR proxy hypothesis in the SFT setting, with a novel benchmark-specific discovery (MATH-500 success vs. GSM8K failure). The experimental design is straightforward, the setup is well-documented, and the practical guidance is actionable. However, the score is reduced by two primary validity concerns: (1) the step-count asymmetry (500 vs. 1000 steps) confounds the pure learning rate effect, and (2) the mechanism hypothesis (surface-length amplification) is presented with near-factual certainty despite lacking controlled evidence. Additionally, the Introduction lacks a theoretical bridge explaining why the Tiny-LR insight from pretraining might not transfer to SFT, which reduces the conceptual motivation of the negative result. These issues are fixable but materially affect the current scientific defensibility.

**Post-Revision Target:** [7.0, 8.0]/10

If the authors address the P0 issues (matched-step ablation to isolate LR effect, and scope-bounding of the mechanism hypothesis), the paper's scientific defensibility would improve significantly. The core empirical finding (Tiny-LR refutation in SFT) is robust and novel. The benchmark-specific discovery is practically informative. With a matched-step control and a length-correlation analysis, the paper could achieve a strong publication-ready quality level, as the research value is high and the methodological concerns are resolvable with moderate additional work.