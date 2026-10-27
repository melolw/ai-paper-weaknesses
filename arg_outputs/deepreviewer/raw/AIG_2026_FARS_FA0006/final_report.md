## Summary
This paper proposes view-disagreement escalation, a training-free framework for improving the robustness of LLM-based trajectory judges against CoT manipulation attacks. The core insight is that CoT manipulation asymmetrically affects judgments: View1 (with CoT) is susceptible to manipulation while View2 (without CoT) is relatively stable. Disagreement between views serves as a trigger to selectively escalate uncertain cases to strict evidence-anchored evaluation.

On AgentRewardBench, the method achieves a 63% relative reduction in attack sensitivity (Δ-FPR: 4.31% vs. 11.71% for View1-only) while maintaining competitive F1 (72.13%) and achieving the best recall (77.63%). The 2.15× disagreement enrichment under attack (16.4% vs. 7.6% on unmodified failures) validates the mechanistic hypothesis.

**Core evaluation**: The paper presents an elegant, conceptually clean approach that breaks the robustness-accuracy trade-off in CoT manipulation defense. The mechanistic hypothesis is well-motivated and empirically validated. However, the Related Work section omits important recent papers on judge consistency and rationalization bias, and some claims (e.g., "View2 remains stable") should be more precisely bounded. The strict rubric design also needs more specification for reproducibility.

## Strengths
1. **Elegant Conceptual Mechanism**: The core insight—that CoT manipulation asymmetrically affects judgments, with View1 (with CoT) shifting toward false positives while View2 (without CoT) remains relatively stable—is intuitive, testable, and mechanistically grounded. This is a genuinely novel trigger signal compared to prior work that uses model confidence or reasoning path consistency.

2. **Effective Trade-off Resolution**: The method successfully breaks the robustness-accuracy trade-off. By selectively escalating only ~10% of cases, it achieves substantial attack sensitivity reduction (63% relative) while preserving competitive F1 and best recall. This is a meaningful practical advance over CoT-only and CoT-agnostic baselines.

3. **Solid Empirical Validation**: The experiments on AgentRewardBench are well-designed, with clear baselines (View1-only, View2-only, Strict-always, Random Escalation) and a matched-cost ablation. The 2.15× disagreement enrichment under attack provides direct mechanistic validation of the hypothesis.

4. **Training-Free and Deployable**: The framework requires no model fine-tuning, relying only on prompt-level interventions. This makes it highly practical for real-world deployment, as it can be applied to any existing LLM judge with minimal engineering overhead.

5. **Clear Experimental Setup**: The use of the Progress Fabrication attack from Khalifa et al. (2026) on all 811 failure trajectories provides a rigorous and reproducible evaluation protocol. The deterministic decoding (temperature=0) ensures that disagreements reflect view differences rather than sampling noise.

## Weaknesses
1. **Related Work Coverage Gap (Major)**: The Related Work section omits important recent papers on judge consistency and rationalization bias. Specifically, ConsJudge (Liu et al., 2025) explores judge-consistency across evaluation dimensions, and Faithful or Fabricated (Tapwal et al., 2026) investigates cue-invariance in judge rationalizations using PROOF-BEFORE-PREFERENCE protocols. These works address overlapping themes of judge reliability and evidence-anchored prompting. Their absence weakens the novelty positioning and may lead reviewers to question whether the approach is truly distinct from prior judge-consistency methods.

2. **Underspecified Strict Rubric Design (Major)**: The strict evidence-anchored rubric prompt $P_{\text{strict}}$ is described by its characteristics (excludes CoT, requires evidence citation, uses checklist, outputs machine-parseable judgment), but the actual rubric construction is not specified. How are the "structured checklist of task requirements" derived? Are they from task definitions, manually crafted, or automatically generated? This underspecification threatens reproducibility.

3. **Overstated View2 Stability Claim (Moderate)**: The paper repeatedly states that "View2 remains stable" under CoT manipulation, but the 7.6% baseline disagreement rate on unmodified failures indicates that View2 is not perfectly stable. The assumption should be bounded to "View2 is relatively stable with respect to manipulation-induced shifts" rather than absolute stability. This clarification is important for correctly interpreting the disagreement signal's specificity.

4. **Single-Model and Single-Attack Evaluation Scope (Moderate)**: The method is evaluated on a single judge model (Llama-3.3-70B-Instruct) and a single attack type (Progress Fabrication). The generalization to other judge models (e.g., GPT-4, Claude) and other attack strategies (e.g., style-based manipulations from Khalifa et al.) is not tested, limiting the claims about robustness breadth.

5. **Contribution List Over-Indexing on Metrics (Minor)**: The third contribution claim mixes conceptual framing with performance numbers ("63% relative reduction", "best recall"), making it read more like a results summary than a conceptual contribution. Reframing to emphasize the trade-off resolution as the core methodological contribution would strengthen the paper's conceptual positioning.

## Key Issues
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit | Priority |
|-------|------------|------------|-----------------|------------------|----------|
| Related work omits ConsJudge (Liu et al., 2025) and Faithful or Fabricated (Tapwal et al., 2026) | Major | Incomplete literature review on judge consistency/rationalization | Add citations and explicit differentiation in Related Work | Strengthens novelty positioning; prevents reviewer skepticism | P0 |
| Strict rubric design is underspecified | Major | Method section describes characteristics but not construction process | Specify how checklist items are derived (task definitions/manual/auto) | Enables faithful reproduction; addresses reproducibility concerns | P0 |
| "View2 remains stable" claim overstated | Moderate | 7.6% baseline disagreement shows View2 is not perfectly stable | Reframe to "View2 is relatively stable w.r.t. manipulation-induced shifts" | Improves conceptual rigor and claim defensibility | P1 |
| Single-model, single-attack evaluation scope | Moderate | Only Llama-3.3-70B-Instruct and Progress Fabrication tested | Add evaluation on at least one additional judge model and/or attack type | Broadens robustness claims; demonstrates generalization | P1 |
| Contribution C3 over-indexes on metrics | Minor | Mixes conceptual framing with performance numbers | Reframe to emphasize trade-off resolution as core contribution | Improves conceptual positioning over engineering-level framing | P2 |

## Actionable Suggestions
1. **Add Missing Related Work (P0 - Must)**: In the "Robustness of LLM Judges" paragraph, add a sentence citing ConsJudge (Liu et al., 2025) and Faithful or Fabricated (Tapwal et al., 2026). Explicitly differentiate your approach: ConsJudge uses dimension-wise judge consistency for training data selection, while Faithful or Fabricated uses PROOF-BEFORE-PREFERENCE for cue-invariance. Your method uniquely targets the asymmetric effects of CoT manipulation via counterfactual view disagreement.

2. **Specify Strict Rubric Construction (P0 - Must)**: In Section 3.3, add 2-3 sentences explaining how the "structured checklist of task requirements" is derived. For example: "The checklist is constructed from the benchmark's ground-truth success criteria as provided in AgentRewardBench. For tasks without explicit criteria, we use a generic rubric requiring the agent to achieve the stated goal without side effects. The full rubric template is provided in Appendix A." If an appendix does not exist, add one.

3. **Reframe "View2 Stability" Language (P1 - Must)**: Replace "View2 remains stable" with "View2 predictions remain relatively stable with respect to manipulation-induced shifts" in Sections 3.2 and 4.3. Add a brief discussion acknowledging that the 7.6% baseline disagreement on unmodified failures reflects inherent judgment variability from CoT removal, and that the method leverages asymmetric disagreement rather than assuming perfect stability.

4. **Bound Abstract Claims (P1 - Must)**: In the abstract, clarify that "63% relative reduction" is compared to standard CoT-inclusive judging (View1-only), and that View2-only and Strict-always achieve zero Δ-FPR at the cost of F1. This prevents misleading readers into thinking this is the maximum achievable robustness.

5. **Expand Conclusion Limitations (P2 - Nice-to-have)**: In the Conclusion, expand the limitation discussion to mention: (a) evaluation on a single attack type (Progress Fabrication), (b) use of a single judge model (Llama-3.3-70B-Instruct), and (c) the 2.1× inference cost. This honest scope bounding improves credibility.

## Storyline Options + Writing Outlines
### Current Storyline Assessment
The current introduction follows a clear arc: (1) LLM-as-a-judge for web agent evaluation, (2) CoT manipulation vulnerability, (3) proposed solution (view-disagreement escalation), (4) contributions. The problem alignment is strong, and the transition from problem to solution is logical.

### Recommended Revision: Strengthen the Gap Statement
The main improvement is to make the research gap more explicit. The current introduction identifies the trade-off (robustness vs. accuracy) but does not explicitly state why existing methods cannot solve it. Adding a sentence that positions the paper's unique contribution—selective escalation via counterfactual view disagreement—would strengthen the narrative.

### Abstract Outline (Complete)
- **S1 (Problem & Domain):** LLM-based judges are widely used to evaluate web agent trajectories, but they are vulnerable to manipulation through unfaithful chain-of-thought (CoT) reasoning.
- **S2 (Significance/Challenge):** CoT manipulation can inflate false positive rates by up to 90%, threatening the reliability of automated evaluation systems used for benchmarking and training data selection.
- **S3 (Prior Work Limitation/Gap):** Existing mitigations face a fundamental trade-off: removing CoT eliminates the vulnerability but sacrifices accuracy, while always-on strict evaluation increases cost and reduces recall.
- **S4 (Proposed Method):** We propose view-disagreement escalation, a training-free framework that compares judgments from two counterfactual input views—one with CoT and one without—to detect unreliable predictions and selectively escalate to strict evidence-anchored evaluation.
- **S5 (Key Result & Bounded Implication):** On AgentRewardBench, our method achieves a 63% relative reduction in attack sensitivity compared to standard CoT-inclusive judging, while maintaining competitive F1 and achieving the best recall. The 2.15× disagreement enrichment under attack validates our mechanistic hypothesis.

### Introduction Outline (Complete)
- **P1 (Big Picture & Stakes):** LLM-as-a-judge enables scalable web agent evaluation, but false positives are costly (label noise, reward hacking). Current evaluation approaches do not distinguish between trustworthy and manipulated judgments.
- **P2 (Core Vulnerability & Trade-off):** CoT manipulation inflates FPR by up to 90% (Khalifa et al., 2026). Existing mitigations face a trade-off: removing CoT sacrifices accuracy; always-on strict evaluation increases cost. To break this trade-off, we need a method that selectively applies strict evaluation only when manipulation is likely.
- **P3 (Proposed Solution & Mechanism):** We propose view-disagreement escalation. Our key insight is that CoT manipulation asymmetrically affects judgments: View1 (with CoT) is susceptible, while View2 (without CoT) is relatively stable. Disagreement between views serves as a mechanistically motivated trigger for selective escalation.
- **P4 (Contributions):** (1) A mechanistically-motivated framework using counterfactual input views to detect unreliable predictions. (2) Empirical validation of disagreement enrichment under attack. (3) Demonstration on AgentRewardBench of a 63% relative reduction in attack sensitivity with competitive F1 and best recall, showing that selective escalation achieves a robustness-accuracy balance that neither CoT-only nor CoT-agnostic baselines achieve.

## Priority Revision Plan
### Stage 1: Critical Fixes (P0 - Must complete before submission)
1. **Add Missing Related Work**: Insert citations to ConsJudge (Liu et al., 2025) and Faithful or Fabricated (Tapwal et al., 2026) in the "Robustness of LLM Judges" paragraph. Add 2-3 sentences differentiating the current approach from these methods. (Effort: 1-2 hours)
2. **Specify Strict Rubric Construction**: Add 2-3 sentences in Section 3.3 explaining how the "structured checklist of task requirements" is derived (from benchmark definitions, manually crafted, or auto-generated). Reference an appendix if the full template is provided there. (Effort: 1-2 hours)
3. **Bound Abstract Claims**: Clarify that "63% relative reduction" is compared to View1-only, and acknowledge that View2-only/Strict-always achieve zero Δ-FPR at the cost of F1. (Effort: 30 minutes)

### Stage 2: Important Clarifications (P1 - Should complete)
4. **Reframe "View2 Stability" Language**: Replace "View2 remains stable" with "View2 is relatively stable w.r.t. manipulation-induced shifts" in Sections 3.2 and 4.3. Add a brief discussion acknowledging the 7.6% baseline disagreement. (Effort: 1 hour)
5. **Expand Conclusion Limitations**: Add 1-2 sentences mentioning single attack type, single judge model, and inference cost constraints. (Effort: 30 minutes)

### Stage 3: Quality Improvements (P2 - Nice-to-have)
6. **Reframe Contribution C3**: Reframe the third contribution to emphasize trade-off resolution rather than just performance numbers. (Effort: 30 minutes)
7. **Add Multi-Model Evaluation**: If feasible, evaluate on one additional judge model (e.g., GPT-4o or Claude) to demonstrate generalization. (Effort: 1-2 days)

### Expected Impact After Fixes
- **Novelty positioning**: Strengthened by explicit differentiation from ConsJudge and Faithful or Fabricated.
- **Reproducibility**: Improved by specifying rubric construction details.
- **Claim defensibility**: Enhanced by bounding View2 stability and abstract claims.
- **Credibility**: Improved by honest limitation discussion.

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1: Main Comparison | View-disagreement escalation reduces attack sensitivity while maintaining accuracy | AgentRewardBench (1,106 trajs); Progress Fabrication attack on 811 failures; Llama-3.3-70B-Instruct; Baselines: View1-only, View2-only, Strict-always, Random Escalation | Prec., Recall, F1, FPR_unmod, FPR_attacked, Δ-FPR | Ours: 63% relative Δ-FPR reduction (4.31% vs 11.71%), best recall (77.63%), competitive F1 (72.13%) | Robustness-accuracy trade-off resolution | Single judge model; single attack type |
| E2: Mechanistic Validation | CoT manipulation causes disproportionate view disagreement | Same setup as E1; disagreement rates computed per trajectory class | Disagreement rate (%) | Attacked failures: 16.4% disagreement vs. 7.6% on unmodified failures (2.15× enrichment) | Mechanistic hypothesis validated | Does not test disagreement on successful trajectories or other attack types |
| E3: Ablation - Random Escalation | Disagreement signal (not escalation itself) provides robustness | Randomly escalate 10% of trajectories to strict rubric | F1, Δ-FPR, Esc. Rate | Δ-FPR=11.34% (not reduced) vs. 4.31% for targeted escalation | Confirms signal-specificity of view disagreement | Rate matching is approximate (10% vs 10.4%) |
| E4: Ablation - Matched-Cost Control | Counterfactual view contrast is essential for both accuracy and robustness | Two View2 calls at different temperatures instead of View1+View2 | F1, Δ-FPR, Esc. Rate | Low Δ-FPR (0.12%) but degraded F1 (68.97% vs 72.13%) | Shows CoT-agnostic approaches sacrifice accuracy | Does not test other temperature or prompting variations |

### (b) Research-Theme Gap Diagnosis
1. **Generalization to Other Judge Models (Validity)**: The method is evaluated on Llama-3.3-70B-Instruct only. It is unclear whether the disagreement signal generalizes to other judge models (e.g., GPT-4, Claude) or different model sizes.
2. **Generalization to Other Attack Types (Robustness)**: Only Progress Fabrication attacks are tested. Style-based manipulations (from Khalifa et al., 2026) or other attack strategies (e.g., prompt injection) are not evaluated.
3. **Disagreement on Successful Trajectories (Mechanism)**: The mechanistic analysis focuses on failures. It is unclear what the disagreement rate is on successful trajectories and whether the escalation trigger has asymmetric precision-recall properties.
4. **Cost-Efficiency Variants (Practicality)**: The 2.1× inference cost is noted as a limitation. No cost-efficient variants (e.g., early exit, smaller judge models for Stage 1) are explored.

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|---|---|---|---|---|---|---|---|
| Multi-model generalization | Disagreement signal generalizes across judge models | Evaluate on GPT-4o or Claude; same attack/setup | View1-only, View2-only per model | Δ-FPR, F1, Recall | Δ-FPR reduction maintained | 1-2 days | Broadens robustness claims |
| Additional attack types | Method works against style-based manipulations | Apply style-based attacks from Khalifa et al. | Same baselines under new attacks | Δ-FPR, F1, Recall | Robustness maintained | 2-3 days | Demonstrates attack-agnostic robustness |
| Disagreement on successes | Disagreement rates differ between attacked and clean trajectories | Compute disagreement rates on successful trajectories | Compare with failure rates | Disagreement rate, precision of escalation | Clarifies signal specificity | 1 day | Strengthens mechanistic understanding |
| Cost-efficient variant | Early-exit or smaller model reduces cost without losing robustness | Use smaller model for Stage 1; escalate only if disagreeing | Baseline with full model | Δ-FPR, F1, cost multiplier | Cost reduction with minimal accuracy loss | 2-3 days | Addresses practical deployment concerns |

### (d) Traceability
- **E1/E2** → Core claims of robustness improvement and mechanistic validation.
- **Proposed: Multi-model** → Addresses generalization gap (Weakness 4).
- **Proposed: Additional attacks** → Addresses attack scope limitation (Weakness 4).
- **Proposed: Disagreement on successes** → Strengthens mechanistic understanding (Weakness 3).

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Mechanistically-motivated framework using counterfactual input views (with/without CoT) to detect unreliable predictions and selectively escalate to strict evidence-anchored judgment | [1][2][5] | partially_overlapping | Overlaps with ConsJudge [1] on using judge consistency for reliability and Faithful or Fabricated [2] on cue-invariance. The counterfactual view disagreement mechanism is distinct, but the general idea of using disagreement as a reliability signal has precedent. | High | Explicitly differentiate from ConsJudge (dimension-wise consistency for training) and Faithful or Fabricated (PROOF-BEFORE-PREFERENCE for cue-invariance) in Related Work. |
| C2 | Empirical validation that view disagreement is enriched under CoT manipulation attacks (2.15× higher), confirming the mechanistic hypothesis | [5] | supported | The specific finding that View1/View2 disagreement is enriched under CoT manipulation (16.4% vs 7.6%) has not been reported in prior work. Gaming the Judge [5] identifies the vulnerability but does not propose or test a disagreement-based detection mechanism. | High | None required. |
| C3 | 63% relative reduction in attack sensitivity while maintaining competitive F1 and best recall, demonstrating the trade-off resolution | [5][6] | partially_overlapping | The trade-off resolution is novel in the context of CoT manipulation defense, but selective escalation for reliability has precedent (e.g., conformal prediction [3], rubric-grounded evaluation [6]). The specific combination (view disagreement + strict rubric) is new but incremental. | Medium | Reposition C3 to emphasize the specific methodological combination rather than just performance gains. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Branch | Judge Consistency & Rationalization | - | - | - | Medium |
| Leaf | Dimension-wise judge consistency | ConsJudge [1] | Judge consistency across dimensions indicates reliability | Uses consistency for training data selection; this paper uses view disagreement as an inference-time trigger | Low risk: different mechanism and use case |
| Leaf | Cue-invariance & rationalization bias | Faithful or Fabricated [2] | PROOF-BEFORE-PREFERENCE improves cue invariance | Focuses on summarization/dialogue evaluation; this paper targets web agent trajectory evaluation | Low risk: different task and mechanism |
| Branch | Uncertainty-Aware Selective Prediction | - | - | - | Low |
| Leaf | Conformal prediction for judge intervals | [3] | Prediction intervals quantify judge uncertainty | Provides coverage guarantees; this paper uses mechanistic disagreement as a trigger | Low risk: different uncertainty quantification approach |
| Leaf | Conformalized selective regression | [4] | Selective regression improves reliability | General ML method; not LLM-specific or CoT-aware | Low risk: different domain |
| Branch | CoT Manipulation & Robust Defense | - | - | - | Medium |
| Leaf | CoT manipulation attacks & prompt mitigations | Gaming the Judge [5] | Prompt-based mitigations reduce but do not eliminate vulnerability | Identifies the problem; this paper proposes a selective escalation solution | Low risk: this paper builds on [5] |
| Leaf | Rubric-grounded evaluation | Rubric-Grounded RL [6] | Structured rubrics improve reward signal | Uses rubrics for RL training; this paper uses rubrics for inference-time escalation | Low risk: different use case |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] ConsJudge | RAG evaluation reliability | Judge-consistency across evaluation dimensions for DPO training | Uses consistency as a reliability signal | Consistency for training; view disagreement for inference-time escalation | Low impact: different mechanism and deployment stage |
| [2] Faithful or Fabricated | Summarization/dialogue evaluation | PROOF-BEFORE-PREFERENCE for cue-invariance | Addresses judge rationalization bias | General cue-invariance; this paper targets CoT manipulation specifically | Low impact: different task and threat model |
| [5] Gaming the Judge | Web agent trajectory evaluation | Identifies CoT manipulation vulnerability; tests prompt mitigations | Same attack setting and benchmark | Problem identification; this paper provides a selective escalation solution | Medium impact: this paper is a direct defense to [5]'s identified problem |

### Contribution-level Novelty Conclusion
C1 is `partially_overlapping`: the counterfactual view disagreement mechanism is distinct from prior judge-consistency methods, but the general idea of using disagreement as a reliability signal has precedent. C2 is `supported`: the empirical validation of disagreement enrichment under CoT manipulation is a novel finding. C3 is `partially_overlapping`: the trade-off resolution is novel in context but incremental in mechanism. Overall, the paper makes a meaningful but incremental contribution to LLM judge robustness. Explicit differentiation from ConsJudge [1] and Faithful or Fabricated [2] in Related Work is required to strengthen the novelty positioning.

### ASCII Diagram A — Paper Structure & Evidence Map
```text
[Problem: CoT manipulation inflates FPR by up to 90%]
    -> [Evidence: Khalifa et al. (2026) attack setting]
    -> [Gap: Existing mitigations face robustness-accuracy trade-off]
    -> [Solution: View-disagreement escalation]
        -> [Mechanism: View1 (with CoT) vs View2 (without CoT)]
        -> [Trigger: Disagreement signals potential manipulation]
        -> [Action: Selective escalation to strict evidence-anchored rubric]
    -> [Evidence: 2.15x disagreement enrichment (16.4% vs 7.6%)]
    -> [Outcome: 63% relative delta-FPR reduction, competitive F1, best recall]
    -> [Limitation: 2.1x cost, single model, single attack type]
```

### ASCII Diagram B — Revision Strategy Roadmap
```text
[P0: Add missing Related Work (ConsJudge, Faithful or Fabricated)]
    -> [Action: Differentiate from judge-consistency and cue-invariance methods]
    -> [Expected gain: Strengthens novelty positioning]

[P0: Specify strict rubric construction]
    -> [Action: Explain how checklist items are derived]
    -> [Expected gain: Enables faithful reproduction]

[P1: Reframe "View2 stability" language]
    -> [Action: Use "relatively stable w.r.t. manipulation-induced shifts"]
    -> [Expected gain: Improves conceptual rigor]

[P2: Expand conclusion limitations]
    -> [Action: Mention single attack, single model, cost constraints]
    -> [Expected gain: Honest scope bounding improves credibility]
```

### ASCII Diagram C — Related-Work Taxonomy Tree (Layered)
```text
LLM-as-a-Judge Reliability (Root)
├── Branch 1: Judge Consistency & Rationalization
│   ├── Leaf 1.1: Dimension-wise judge consistency [1]
│   │   └── ConsJudge: uses consistency for training data selection
│   └── Leaf 1.2: Cue-invariance & rationalization bias [2]
│       └── Faithful or Fabricated: PROOF-BEFORE-PREFERENCE for cue-invariance
├── Branch 2: Uncertainty-Aware Selective Prediction
│   ├── Leaf 2.1: Conformal prediction for judge intervals [3]
│   │   └── Statistical coverage guarantees for LLM scoring
│   └── Leaf 2.2: Conformalized selective regression [4]
│       └── Model-specific confidence for selective prediction
└── Branch 3: CoT Manipulation & Robust Defense
    ├── Leaf 3.1: CoT manipulation attacks & prompt mitigations [5]
    │   └── Gaming the Judge: identifies vulnerability, tests prompt defenses
    └── Leaf 3.2: Rubric-grounded evaluation [6]
        └── Rubric-Grounded RL: structured rubrics for reward optimization

[This Paper Positioning]
└── Between Leaf 1.1/1.2 and Leaf 3.1: uses view disagreement as inference-time
    trigger for selective escalation to strict rubric, targeting CoT manipulation
    specifically in web agent trajectory evaluation.
```

### ASCII Diagram D — Experiment Upgrade Plan
```text
Stage 1 (Week 1): Multi-model generalization
    -> Evaluate on GPT-4o or Claude under same attack setup
    -> Expected: Delta-FPR reduction maintained across models

Stage 2 (Week 2): Additional attack types
    -> Apply style-based manipulations from Khalifa et al. (2026)
    -> Expected: Robustness maintained against diverse attack strategies

Stage 3 (Week 2-3): Disagreement on successful trajectories
    -> Compute disagreement rates on successful trajectories
    -> Expected: Clarifies signal specificity and false positive rate

Stage 4 (Week 3-4): Cost-efficient variants (optional)
    -> Early-exit or smaller model for Stage 1 judging
    -> Expected: Cost reduction with minimal accuracy loss
```

## References
[1] Judge as A Judge: Improving the Evaluation of Retrieval-Augmented Generation through the Judge-Consistency of Large Language Models 2502.18817

[2] Faithful or Fabricated? A Causal Framework for Rationalization Bias in LLM Judges 2605.23970

[3] Analyzing Uncertainty of LLM-as-a-Judge: Interval Evaluations with Conformal Prediction 2509.18658

[4] Conformalized Selective Regression 2402.16300

[5] Gaming the Judge: Unfaithful Chain-of-Thought Can Undermine Agent Evaluation 2601.14691

[6] Rubric-Grounded RL: Structured Judge Rewards for Generalizable Reasoning 2605.08061

## Scores
Final Score: 5.5/10

This score reflects a paper with a genuinely elegant conceptual mechanism (view-disagreement escalation) and solid empirical validation on AgentRewardBench. The method effectively breaks the robustness-accuracy trade-off in CoT manipulation defense, achieving a 63% relative reduction in attack sensitivity while maintaining competitive F1 and best recall. However, the score is constrained by: (1) the Related Work omission of ConsJudge (Liu et al., 2025) and Faithful or Fabricated (Tapwal et al., 2026), which weakens novelty positioning; (2) the underspecified strict rubric design, which threatens reproducibility; (3) the overstated "View2 stability" claim, which reduces conceptual rigor; and (4) the limited evaluation scope (single judge model, single attack type).

Post-Revision Target: [7.0, 8.0]/10

If the authors add the missing related work citations with explicit differentiation, specify the strict rubric construction, reframe the View2 stability language, and expand the conclusion limitations, the paper would present a much stronger and more defensible contribution. The core mechanism is novel enough to warrant a strong acceptance once the supporting evidence and literature context are properly addressed.