## Summary
This paper investigates whether AR-order RL post-training (specifically JustGRPO) compromises the order robustness of diffusion language models (dLLMs). The authors compare three models—LLaDA-8B-Instruct (diffusion base), LLaDA-Instruct-JustGRPO (AR-order RL trained), and Qwen2.5-7B-Instruct (AR anchor)—on ReasonOrderQA and GSM8K under both CoT-First and Answer-First prompt conditions. Key findings include: JustGRPO reduces the robustness ratio by 0.192 on ReasonOrderQA and 0.138 on GSM8K; degradation is concentrated at medium difficulty levels (D2-D3); and an accuracy-robustness trade-off emerges where CoT-First accuracy improves (+19.6pp) while Answer-First performance declines.

The research question is timely and addresses a genuine gap: as RL post-training becomes standard for dLLMs, its side effects on order flexibility remain understudied. The experimental design is clean and the findings are empirically reproducible under deterministic settings. However, the manuscript has two critical weaknesses: (1) a pervasive citation error misattributing JustGRPO to Ou et al. (2025) instead of Ni et al. (2026), which undermines factual credibility; and (2) causal interpretations that exceed the evidence provided, such as claiming AR-order RL "internalizes sequential generation bias" without mechanism-level validation.

## Strengths
1. **Timely and well-motivated research question:** The paper addresses a genuine gap at the intersection of RL post-training and diffusion language model properties. As JustGRPO and similar methods gain traction, understanding their effects on order robustness is both scientifically interesting and practically relevant for dLLM deployment.

2. **Clean experimental design:** The three-model comparison (diffusion base vs. AR-order RL vs. AR anchor) cleanly isolates the effect of interest. Using both CoT-First and Answer-First prompts on two benchmarks (ReasonOrderQA, GSM8K) provides reasonable generalization across task types.

3. **Granular per-difficulty analysis:** The finding that robustness degradation concentrates at medium difficulty levels (D2-D3) is scientifically insightful. This granularity helps future work understand boundary conditions where AR-order RL has the largest impact.

4. **Canvas length ablation:** The analysis of how generation length modulates robustness degradation (gap ratio = 0.756 at L=64 vs. L=512) provides useful context and suggests that longer generation contexts amplify the effect, which is a meaningful practical insight.

5. **Deterministic evaluation discipline:** The commitment to deterministic generation (temperature=0.0) and bitwise verification for ReasonOrderQA outputs eliminates sampling variance as a confounder, which is an experimental rigor strength in an era where many RL studies rely on single-seed evaluations.

## Weaknesses
1. **Pervasive citation error (Critical/Factual):** JustGRPO is consistently misattributed to "Ou et al. (2025)" throughout the manuscript. JustGRPO is the method from Ni et al. (2026) [arXiv 2601.15165, "The Flexibility Trap"]. Ou et al. (2025) [arXiv 2512.03759] proposes ESPO, a different sequence-level RL method. This error appears in the Abstract, Introduction, Related Work, and Model Comparison sections. This is a critical factual defect that undermines credibility and must be corrected globally before submission.

2. **Causal over-interpretation (Major):** The claim that AR-order RL "partially internalizes the sequential generation bias characteristic of autoregressive models" (Page 4, Main Results) is a strong mechanistic interpretation unsupported by direct evidence. The paper shows correlation (robustness degradation after RL training) but does not provide an ablation isolating generation order from other RL effects (e.g., overfitting to CoT-First patterns, reward hacking, model capacity changes). Without a matched-control experiment (e.g., RL with order-agnostic rewards), causal attribution is speculative.

3. **Missing statistical rigor (Major):** While deterministic evaluation eliminates sampling variance, the paper does not address dataset-level variance. Results on two benchmarks (ReasonOrderQA, GSM8K) are presented without confidence intervals, significance tests, or robustness checks across problem subsets. The decision threshold (Δr ≥ 0.10) is stated without justification. This limits the confidence in generalizing findings beyond the specific problem instances tested.

4. **Missing related work coverage (Moderate):** The Related Work section omits several directly relevant papers: d1 (Zhao et al., 2025) [arXiv 2504.12216], the first policy-gradient RL for masked dLLMs (diffu-GRPO), and DCoLT (Huang et al., 2025) [arXiv 2505.10446], which optimizes diffusion reasoning trajectories. These omissions weaken the novelty positioning and related-work coverage.

5. **Overstated "first" claim (Minor):** "We provide the first empirical investigation of this question" (Page 1, Intro) is too broad. While the specific angle (JustGRPO's effect on order robustness) may be novel, related work has already studied order robustness in diffusion models (Yu et al., 2026) and RL effects on dLLMs. The claim should be scope-precise: "first empirical investigation of how AR-order RL post-training specifically affects order robustness in diffusion LMs."

6. **Deterministic verification scope mismatch (Minor):** The claim "all experimental results are fully deterministic" (Page 6) is technically inaccurate. The 4,000-output bitwise verification covers ReasonOrderQA only (2 models × 2 conditions × 1,000 problems). GSM8K (1,319 problems) is excluded. This overstatement should be corrected to match the actual verification scope.

## Key Issues
**Issue 1: Global Citation Misattribution of JustGRPO (Severity: Major/Factual)**
- **Anchor:** Appears on Page 1 (Intro P2), Page 2 (Related Work), Page 3 (Model Comparison). JustGRPO is cited as "(Ou et al., 2025)" throughout.
- **Verification:** Retrieved literature confirms JustGRPO is from Ni et al. (2026) [arXiv 2601.15165]. Ou et al. (2025) [arXiv 2512.03759] proposes ESPO, a different method.
- **Impact:** Undermines factual credibility and reviewer confidence. Suggests the automated research pipeline may have conflated two related papers.
- **Acceptance Criteria:** Replace all instances of "Ou et al., 2025" referring to JustGRPO with "Ni et al., 2026" and verify globally.

**Issue 2: Causal Attribution Without Mechanism Evidence (Severity: Major)**
- **Anchor:** Page 4, Main Results paragraph: "This suggests that AR-order RL training partially internalizes the sequential generation bias characteristic of autoregressive models."
- **Verification:** No matched-control ablation isolates generation order from other RL effects (capacity, reward structure, overfitting). Alternative explanations are not ruled out.
- **Impact:** Over-interpreted causal claims risk rejection as speculative.
- **Acceptance Criteria:** Replace with evidence-consistent wording ("consistent with") and add a note on what ablation would be needed for causal attribution.

**Issue 3: Deterministic Verification Scope Overstatement (Severity: Major/Verification)**
- **Anchor:** Page 6, "Deterministic Verification": claims "all experimental results are fully deterministic" with 4,000 outputs verified.
- **Verification:** 4,000 = 2 models × 2 conditions × 1,000 problems (ReasonOrderQA only). GSM8K (1,319 problems) is excluded.
- **Impact:** Overstatement of reproducibility guarantees.
- **Acceptance Criteria:** Correct the scope statement to match the actual verified subset.

## Actionable Suggestions
**1. Correct JustGRPO Citation Globally (P0 — Must)**
- **Action:** Replace all instances of "JustGRPO (Ou et al., 2025)" with "JustGRPO (Ni et al., 2026)" throughout the manuscript. Verify in Abstract, Introduction, Related Work, and Model Comparison sections. Update the reference list accordingly.
- **Expected impact:** Restores factual credibility and prevents reviewer confusion.

**2. Bound Causal Claims in Main Results (P0 — Must)**
- **Action:** Replace "This suggests that AR-order RL training partially internalizes the sequential generation bias" with "This pattern is consistent with AR-order RL training promoting sequential generation characteristics, though matched ablations are needed for causal attribution."
- **Expected impact:** Makes claims evidence-consistent and reviewer-resistant.

**3. Add Missing RL Related Work (P1 — Should)**
- **Action:** Add d1 (Zhao et al., 2025) [arXiv 2504.12216] and DCoLT (Huang et al., 2025) [arXiv 2505.10446] to the Related Work section. d1 is the first policy-gradient RL for masked dLLMs; DCoLT optimizes diffusion reasoning trajectories.
- **Expected impact:** Improves related-work coverage and novelty positioning.

**4. Justify Decision Threshold (P1 — Should)**
- **Action:** Add one sentence explaining why Δr ≥ 0.10 is chosen: e.g., "We adopt Δr ≥ 0.10 as our decision threshold, corresponding to a 10 percentage-point drop in relative order performance that exceeds typical evaluation variance in single-seed settings."
- **Expected impact:** Prevents threshold arbitrariness challenges.

**5. Correct Deterministic Verification Scope (P1 — Should)**
- **Action:** Revise the claim from "all experimental results are fully deterministic" to specify that the 4,000-output verification covers ReasonOrderQA only, and that GSM8K uses the same deterministic settings but was not separately re-run.
- **Expected impact:** Aligns reproducibility claims with actual verification scope.

**6. Add Practical Motivation in Intro P1 (P2 — Nice-to-have)**
- **Action:** Add one sentence in the first introduction paragraph explaining why order flexibility matters practically (e.g., schema-constrained outputs, API responses, structured generation).
- **Expected impact:** Strengthens reader engagement and real-world relevance.

**7. Scope the "First" Claim (P2 — Nice-to-have)**
- **Action:** Tighten "We provide the first empirical investigation of this question" to "We provide the first empirical investigation of how AR-order RL post-training specifically affects order robustness in diffusion LMs."
- **Expected impact:** Makes the novelty claim defensible and precise.

## Storyline Options + Writing Outlines
### Current Storyline Assessment
The current narrative follows a clear arc: Big Picture (dLLMs vs AR) → Gap (RL post-training effect unknown) → Solution (three-model comparison) → Evidence (Table 1, per-difficulty, canvas ablation) → Conclusion (trade-off identified). This structure is logically sound and reader-friendly.

### Recommended Abstract Outline (4-5 sentences)
- **S1 (Problem/Domain):** Diffusion language models (dLLMs) offer order robustness—the ability to solve reasoning problems regardless of output order—but the dominant RL post-training paradigm uses autoregressive-order (AR-order) rewards.
- **S2 (Gap/Significance):** It remains unknown whether AR-order RL training compromises this unique order flexibility, which is critical for schema-constrained generation tasks.
- **S3 (Method):** We investigate this question by comparing LLaDA-8B-Instruct (diffusion base), LLaDA-Instruct-JustGRPO (AR-order RL trained), and Qwen2.5-7B-Instruct (AR anchor) on ReasonOrderQA and GSM8K under CoT-First and Answer-First prompts.
- **S4 (Key Result):** JustGRPO significantly reduces the robustness ratio by 0.192 on ReasonOrderQA and 0.138 on GSM8K, with degradation concentrated at medium difficulty levels requiring multi-step reasoning.
- **S5 (Implication):** While AR-order RL improves CoT-First accuracy by up to 19.6 percentage points, this reveals an accuracy-robustness trade-off in dLLM post-training under the evaluated settings.

### Recommended Introduction Outline (Paragraph-by-Paragraph)
- **P1 (Big Picture + Practical Stakes):** Introduce dLLMs as an alternative to AR models, define order robustness, and add one sentence on practical relevance (e.g., schema-constrained outputs, API responses where answer-first ordering is required).
- **P2 (Gap + Research Question):** State that RL post-training with AR-order rewards (JustGRPO) is dominant for improving dLLM performance, but its effect on order robustness is unstudied. Pose the central question: Does AR-order RL compromise order robustness?
- **P3 (Method + Contributions):** Describe the three-model comparison design and list four explicit contributions: (1) robustness reduction quantified, (2) intermediate positioning between diffusion base and AR anchor, (3) difficulty-level granularity, (4) accuracy-robustness trade-off identified.
- **P4 (Transition):** Briefly preview the experimental setup and evaluation metrics (robustness ratio, decision threshold).

### Storyline Improvement Tips
- Replace absolute claims ("fundamentally absent in AR models") with bounded wording ("significantly degraded in AR models").
- Ensure "first empirical investigation" is scope-precise to avoid overclaiming.
- Maintain causal caution: use "consistent with" instead of "demonstrates that RL internalizes bias" until matched ablations are added.

## Priority Revision Plan
| Priority | Action | Target Section | Effort | Expected Impact |
|---|---|---|---|---|
| **P0 (Must)** | Correct JustGRPO citation globally to Ni et al. (2026) | Abstract, Intro, Related Work, Model Comp | Low (Global Find/Replace) | Restores factual credibility |
| **P0 (Must)** | Replace causal claims ("internalizes bias") with evidence-consistent wording ("consistent with") | Page 4, Main Results | Low (Rewrite) | Makes central claim reviewer-resistant |
| **P0 (Must)** | Correct deterministic verification scope to match 4,000 outputs (ReasonOrderQA only) | Page 6, Verification | Low (Rewrite) | Aligns reproducibility claims with actual scope |
| **P1 (Should)** | Add missing RL related work (d1, DCoLT) to Related Work | Related Work | Medium (Add ~2 paras) | Improves coverage and novelty positioning |
| **P1 (Should)** | Add justification for Δr ≥ 0.10 decision threshold | Page 2, Problem Formulation | Low (1 sentence) | Prevents threshold arbitrariness challenges |
| **P1 (Should)** | Scope the "first empirical investigation" claim to AR-order RL effect | Intro P3 | Low (Rewrite) | Makes novelty claim defensible |
| **P2 (Nice)** | Add practical motivation for order flexibility in Intro P1 | Intro P1 | Low (1-2 sentences) | Strengthens reader engagement and stakes |
| **P2 (Nice)** | Acknowledge denominator effect in per-difficulty analysis | Page 5, Per-Difficulty | Low (1 sentence) | Prevents alternative explanation pushback |

### Revision Sequence
1. **Day 1:** Execute P0 citation and scope corrections globally. These are low-effort but critical for factual defensibility.
2. **Day 2:** Execute P0/P1 causal wording and threshold fixes in the Main Results and Problem Formulation sections.
3. **Day 3:** Add missing Related Work (P1) and verify the related-work taxonomy aligns with the paper's positioning.

### ASCII Diagram — Revision Strategy Roadmap
```text
[Problem: Citation errors + Causal overreach]
    -> [Action: Fix citations to Ni et al. (2026)]
    -> [Action: Bound claims ("consistent with")]
    -> [Expected impact: Factual integrity restored]
    -> [Action: Add missing RL related work (d1, DCoLT)]
    -> [Expected impact: Novelty positioning solidified]
```

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Main robustness comparison | ReasonOrderQA (1k), GSM8K (1.3k); 3 models; CF vs AF prompts | Acc(CF), Acc(AF), r, Gap | JustGRPO drops r by 0.192 (ROQA) / 0.138 (GSM8K) | Robustness reduction claim | No statistical significance / subset variance |
| E2 | Per-difficulty breakdown | ReasonOrderQA D1-D4; same 3 models | r per difficulty | Degradation concentrated at D2-D3 | Difficulty-level claim | Denominator effect not controlled |
| E3 | Canvas length ablation | ReasonOrderQA; L=64 vs L=512; 2 diffusion models | r, gap ratio | Gap attenuates at L=64 (ratio=0.756) | Context-length effect | Only 2 canvas lengths tested |
| E4 | Deterministic verification | ReasonOrderQA; re-run 2 models × 2 conditions × 1k problems | Bitwise identity | 4,000 outputs identical | Determinism claim | GSM8K not included in verification |

### (b) Research-Theme Gap Diagnosis
The core research-value claim—that AR-order RL post-training reduces order robustness in dLLMs—is partially proven but lacks two critical evidence dimensions: (1) causal isolation (no matched ablation ruling out alternative explanations such as CoT-First overfitting or capacity changes), and (2) statistical robustness (no confidence intervals, significance tests, or subset stability checks). The accuracy-robustness trade-off claim is empirically observed but not yet established as a general property across RL methods, model families, or reasoning tasks.

### (c) Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|---|---|---|---|---|---|---|---|
| Causal attribution of robustness drop | AR-order reward structure, not general RL, causes order bias | Train LLaDA with order-agnostic RL (e.g., random mask order rewards) vs. AR-order RL | Base model, AR-order RL (JustGRPO) | r, Acc(CF), Acc(AF) | Order-agnostic RL preserves r while improving accuracy | ~2-3 days GPU | Isolates causal mechanism |
| Statistical robustness | Robustness deltas are stable across problem subsets | Random subset sampling (5 splits × 200 problems each) on ROQA and GSM8K | Same 3 models | Mean±std of Δr, significance test | Δr significant across all 5 subsets | ~1 day CPU | Validates generalizability |
| Cross-model generalization | Effect holds beyond LLaDA | Evaluate JustGRPO-style RL on Dream-7B or another dLLM | Diffusion base, AR-order RL, AR anchor | r, Acc(CF), Acc(AF) | Similar robustness degradation pattern | ~2 days GPU | Generalizes the finding |
| Capacity control | Robustness drop is not due to parameter/epoch effects | Compare JustGRPO vs. SFT fine-tuning of LLaDA with matched params | Base, SFT-only, JustGRPO | r, Acc(CF), Acc(AF) | SFT also reduces r (confounder) or not (supports AR-order cause) | ~1 day GPU | Rules out capacity confound |

### ASCII Diagram — Experiment Upgrade Plan
```text
Stage 1 (today): Citation fixes + claim bounding (P0)
Stage 2 (this week): Subset variance analysis + capacity control (E-stat, E-capacity)
Stage 3 (before submission): Order-agnostic RL ablation + cross-model eval (E-causal, E-generalization)
```

## Novelty Verification & Related-Work Matrix
### 9A. Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | JustGRPO significantly reduces order robustness in diffusion LMs | [1], [2] | partially_overlapping | Yu et al. (2026) [2] established order robustness; this paper extends it to RL post-training effects. The specific RL-effect angle is new, but the underlying phenomenon is built on [2]. | High | Scope to "first analysis of AR-order RL effect on order robustness" |
| C2 | JustGRPO's robustness profile sits between diffusion base and AR anchor (~53% gap) | [1], [2] | supported | No prior work quantifies the intermediate positioning of RL-trained dLLMs relative to AR anchors on order robustness. | Medium | Bound to evaluated settings; note that one RL method is tested |
| C3 | Degradation concentrated at medium difficulty (D2-D3) | [2] | partially_overlapping | Yu et al. (2026) [2] already studied per-difficulty robustness. This paper extends the analysis to post-RL models, which is incremental. | Medium | Frame as "RL-induced difficulty-level sensitivity" |

### 9B. Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: Order in Language Generation | Branch 1: dLLM Order Properties | Leaf 1.1: Inherent order robustness [2] | MDLMs naturally stabilize simpler tokens first | This paper studies how RL modifies this property | Low risk (complementary angle) |
| Root: Order in Language Generation | Branch 2: RL for dLLMs | Leaf 2.1: AR-constrained RL (JustGRPO) [1] | Constraining to AR order improves reasoning | This paper evaluates the cost of that constraint | Low risk (self-consistent) |
| Root: Order in Language Generation | Branch 2: RL for dLLMs | Leaf 2.2: Policy-gradient RL (d1/diffu-GRPO) [3] | Sequence-level or token-level policy gradients | Not evaluated in this paper; missing comparison | Moderate risk |
| Root: Order in Language Generation | Branch 3: Non-monotonic Generation | Leaf 3.1: Insertion/Levenshtein Transformers [4][5] | Flexible token insertion improves quality | Different paradigm; not directly comparable | Low risk |

### 9C. Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] | AR-order RL for dLLMs (JustGRPO) | Standard GRPO under AR constraints | Uses JustGRPO as the test subject | [1] claims AR constraint improves reasoning; this paper measures the order-robustness cost | Complementary findings; not contradictory |
| [2] | Order robustness benchmark (ReasonOrderQA) | CoT-First vs Answer-First evaluation | Provides the evaluation protocol and baseline dLLM results | [2] measures inherent property; this paper measures post-RL change | Extends [2]'s findings; incremental |
| [3] | Policy-gradient RL for masked dLLMs (d1) | diffu-GRPO with random masking | RL post-training for dLLMs | Different RL method; not evaluated here | Missing comparison limits generalization |

### Contribution-level Novelty Conclusion
C1 (robustness reduction): **partially_overlapping** — builds on Yu et al. (2026) [2] which established the order robustness phenomenon; the RL-effect angle is new but incremental. C2 (intermediate positioning): **supported** — no prior work quantifies this specific metric. C3 (difficulty-level concentration): **partially_overlapping** — extends per-difficulty analysis to post-RL models. Overall novelty is solidly within-scope but should be bounded to avoid overclaiming as a general RL property.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)
```text
Order in Language Generation (Root)
├── Branch 1: dLLM Order Properties
│   └── Leaf 1.1: Inherent order robustness [2]
│       (This paper extends this baseline to post-RL evaluation)
├── Branch 2: RL Post-Training for dLLMs
│   ├── Leaf 2.1: AR-constrained RL (JustGRPO) [1]
│   │   (Test subject of this paper; cost-benefit trade-off)
│   └── Leaf 2.2: Policy-gradient RL (d1, diffu-GRPO) [3]
│       (Not evaluated; missing comparison limits generalization)
└── Branch 3: Non-monotonic Generation Paradigms
    ├── Leaf 3.1: Insertion Transformer [4]
    └── Leaf 3.2: Levenshtein Transformer [5]
        (Different paradigm; provides broader context)

This Paper Positioning:
→ Sits at the intersection of Branch 1 (order robustness measurement) and Branch 2.1 (JustGRPO effect).
→ Core value: quantifying the order-robustness cost of the dominant RL paradigm.
→ Value gap: causal mechanism not yet isolated; missing cross-RL-method validation.
```

## References
[1] The Flexibility Trap: Why Arbitrary Order Limits Reasoning Potential in Diffusion Language Models 2601.15165

[2] Thinking Out of Order: When Output Order Stops Reflecting Reasoning Order in Diffusion Language Models 2601.22035

[3] d1: Scaling Reasoning in Diffusion Large Language Models via Reinforcement Learning 2504.12216

[4] Insertion Transformer: Flexible Sequence Generation via Insertion Operations 1902.03249

## Scores
**Final Score:** 5.5/10

**Rationale:** The paper addresses a timely and well-motivated research question—evaluating how AR-order RL post-training affects order robustness in diffusion language models. The experimental design is clean (three-model comparison, two benchmarks, CoT-First vs Answer-First), and the findings are empirically reproducible under deterministic settings. The per-difficulty and canvas-length analyses provide meaningful granularity.

However, the score is pulled down by three factors: (1) a pervasive citation error misattributing JustGRPO to Ou et al. (2025) instead of Ni et al. (2026), which severely undermines factual credibility; (2) causal interpretations that exceed the evidence provided (e.g., claiming RL "internalizes sequential bias" without matched-control ablations); and (3) limited statistical rigor (no confidence intervals, significance tests, or subset variance analysis). The novelty is solidly incremental—extending Yu et al. (2026) to post-RL models—but the missing causal isolation and missing cross-RL-method comparisons prevent a stronger contribution verdict.

**Post-Revision Target:** [7.0, 8.0]/10

If the authors correct the citation error globally, bound causal claims to evidence-consistent wording, add at least one matched-control ablation (e.g., order-agnostic RL), and include subset variance analysis, the paper's credibility and contribution would improve substantially. The core empirical finding is valuable and reviewer-resistant if properly bounded and supported.