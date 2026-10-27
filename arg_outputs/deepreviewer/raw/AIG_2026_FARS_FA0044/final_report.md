## Summary
This paper proposes Selective Self-Reference (SSR-Judge), a method that uses self-consistency among multiple sampled solutions to gate the use of self-reference in LLM-as-a-Judge evaluation. The core insight is that when a judge model consistently produces the same answer across k=5 temperature samples, that answer is more likely correct and can safely serve as a reference. When agreement is low, the method falls back to no-reference judging to avoid error propagation from incorrect self-answers.

On MMLU-Pro pairwise preference judgment, SSR-Judge achieves 58.93% accuracy, outperforming No-Reference (52.07%, +6.86pp) and Always Self-Reference (58.21%, +0.72pp). The method's selective routing successfully preserves self-reference benefits on high-agreement items while avoiding error propagation on uncertain items.

The paper makes a clean, well-motivated contribution to LLM-as-a-Judge evaluation. The error propagation analysis across agreement slices provides valuable diagnostic insights, and the SSR-Judge method is simple yet effective. However, the novelty of the self-consistency calibration property itself is well-established in prior work (Wang et al., 2022; Kadavath et al., 2022), and the error propagation risk was already noted by Lin et al. (2025). The true contribution lies in applying these known properties to the specific problem of conditional self-reference gating. Additionally, the compute-cost tradeoff of k=5 sampling is not fully addressed in the comparison framing, and evaluation is limited to a single model and benchmark.

## Strengths
- Clear problem formulation and well-motivated method design
- Quantitative error propagation analysis across agreement slices provides diagnostic value
- Clean experimental setup with compute-matched baselines (Always Self-Ref vs SSR-Judge)

## Weaknesses
- Contribution C1 overlaps with Lin et al. (2025) who already identified error propagation risk
- No-Reference baseline is not compute-matched (1 inference vs 6), overstating +6.86pp gain
- Self-consistency calibration is a known property from Wang et al. (2022); novelty is incremental
- Evaluation limited to single model (Qwen2.5-72B) and single benchmark (MMLU-Pro)

## Key Issues
- No-Reference baseline compute mismatch misleads value interpretation
- Contribution claims need repositioning to differentiate from prior work
- Conclusion omits category-level limitations and single-model constraint

## Actionable Suggestions
- Reposition C1 to emphasize quantitative slice analysis rather than problem identification
- Clarify compute-cost differences in baseline comparisons
- Expand conclusion with domain-specific limitations and model generalizability constraints
- Consider adding one additional judge model for robustness validation

## Storyline Options + Writing Outlines
- Paper makes a clean, incremental contribution to LLM-as-a-Judge reliability through conditional self-reference gating
- Self-consistency calibration is a known property; novelty is in applying it to self-reference gating
- Compute-cost tradeoff and single-model evaluation limit generalizability claims

## Priority Revision Plan
| Priority | Action | Effort | Expected Impact | Target Section |
|----------|--------|--------|-----------------|----------------|
| P0 | Reposition contribution claims: C1 should emphasize quantitative slice analysis (not problem identification); C2 should highlight novelty of applying self-consistency to gating; C3 should add conceptual value beyond accuracy numbers | Low | High: resolves novelty overlap with Lin et al. (2025) | Introduction §1 |
| P0 | Clarify compute-cost framing: explicitly state that No-Reference uses 1/6th the compute of SSR-Judge; add text bounding the +6.86pp gain interpretation | Low | High: prevents misleading efficiency claims | Section 4.1 |
| P1 | Expand Conclusion limitations: add category-level underperformance on math/chemistry and single-model evaluation constraint | Low | Medium: improves claim scope honesty | Section 5 |
| P1 | Add brief discussion of binary gate vs soft gating design choice in Method section | Low | Medium: preempts reviewer questions on design alternatives | Section 3.4 |
| P2 | Evaluate SSR-Judge on a second judge model (e.g., Llama-3-70B) to demonstrate cross-model generalizability | Medium | Medium: strengthens external validity | Section 4 |
| P2 | Report variance over multiple random seeds for all three baselines | Medium | Medium: improves statistical reliability | Section 4 |

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|------|-----------------|-----------------|--------------------------|
| 1 | 5 | Covered | — |
| 2 | 2 | Covered | — |
| 3 | 2 | Covered | — |
| 4 | 1 | Covered | — |
| 5 | 1 | Covered | — |
| 6 | 1 | Covered | — |

All substantive paragraphs in Abstract, Introduction, Method, Experiments, and Conclusion have been covered by at least one annotation.

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|----------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | SSR-Judge improves over No-Reference and Always Self-Reference baselines | MMLU-Pro (N=1,400), Qwen2.5-72B-Instruct, k=5, τ=4/5, T=0.7 | PreferenceAcc, SliceAcc, Gate-On Rate, Gate Precision | SSR-Judge: 58.93% vs No-Ref: 52.07%, Always: 58.21% | C3 supported | No-Reference not compute-matched; single model/benchmark |
| E2 | Error propagation analysis: SSR-Judge selectively matches best baseline per slice | 4 slices: Unanimous+Correct, Unanimous+Wrong, Non-unan.+Correct, Non-unan.+Wrong | Slice-level PreferenceAcc | SSR-Judge matches Always on unanimous slices, No-Ref on non-unanimous slices | C1, C2 supported | Matching is by design (conditional routing), not emergent |
| E3 | Calibration analysis: self-consistency correlates with correctness | Agreement levels 3/5, 4/5, 5/5 | Majority correctness rate | Monotonic: 35.5% (3/5), 57.7% (4/5), 78.7% (5/5) | Supports gate validity | Known property from prior work (Wang et al., 2022) |
| E4 | Per-category analysis: domain-specific performance | 14 MMLU-Pro categories | PreferenceAcc per category | SSR-Judge wins on 13/14 vs No-Ref, 10/14 vs Always | Method robustness partially supported | Does not explain why math/chemistry favor Always Self-Ref |

### (b) Research-Theme Gap Diagnosis

The core research-value claims are:
1. **New knowledge**: Error propagation in self-reference judging is quantified across agreement slices. This is partially supported but overlaps with Lin et al. (2025) who already noted the risk.
2. **Reproducibility**: Method is clearly specified and code is publicly available. This claim is strong.
3. **Impact on practice**: SSR-Judge provides a simple, effective gating mechanism. However, the 5x compute overhead and single-model evaluation limit practical deployment claims.

The weakest-supported claim is generalizability: evaluation is limited to one judge model (Qwen2.5-72B-Instruct) and one benchmark (MMLU-Pro), with no variance reporting across seeds.

### (c) Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|--------------|-----------|----------------|-------------------|---------|------------------|---------------------|----------------------------|
| C3 (generalizability) | SSR-Judge improves over baselines across multiple judge models | Evaluate on Llama-3-70B-Instruct and Mixtral-8x7B-Instruct under identical protocol | No-Ref, Always Self-Ref, SSR-Judge | PreferenceAcc | SSR-Judge wins on ≥2/3 models | 1-2 days GPU time | High: strengthens external validity |
| C3 (statistical reliability) | Gains are stable across random seeds | Run all 3 methods over 3 seeds | Same baselines | Mean±std PreferenceAcc | std < 2pp, gain persists | 1-2 days GPU time | Medium: improves statistical confidence |
| C2 (soft gating) | Soft gating (weighting by agreement) improves over binary gate | Compare binary gate vs. agreement-weighted reference | Binary SSR-Judge | PreferenceAcc, Gate metrics | Soft gate wins by ≥0.5pp | 0.5 days GPU time | Medium: addresses design choice question |
| C1 (OOD robustness) | SSR-Judge reduces error propagation on harder items | Evaluate on a subset of MMLU-Pro with low base accuracy | Same baselines | Slice-level accuracy | Larger gains on hard items | 0.5 days analysis | Low: strengthens error propagation narrative |

### Traceability Rule

Each proposed experiment maps to at least one unresolved core claim:
- Multi-model evaluation → C3 generalizability gap
- Multi-seed variance → C3 statistical reliability gap
- Soft gating comparison → C2 design choice justification
- OOD analysis → C1 error propagation scope bounding

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|---------------------|-----|------------|----------------------|
| C1 | Identify error propagation problem in self-reference judging | [1], [2] | partially_overlapping | Lin et al. (2025) already noted error propagation risk when self-answer is wrong; this paper adds quantitative slice analysis | High | Reposition to emphasize quantitative characterization across agreement slices rather than problem identification |
| C2 | Propose SSR-Judge: self-consistency as confidence gate for conditional self-reference | [1], [3], [4] | partially_overlapping | Self-consistency calibration is established (Wang et al., 2022); novelty is applying it to self-reference gating in judging | High | Clarify that novelty lies in the application to conditional gating, not in the calibration property itself |
| C3 | SSR-Judge achieves 58.93% on MMLU-Pro, outperforming baselines | [1], [2] | supported | Empirical result is novel; no prior paper reports SSR-Judge performance on MMLU-Pro pairwise judgment | High | Add conceptual value beyond raw accuracy (e.g., compute-aware gain interpretation) |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|--------------------------|-------------------|-------------------------|-------------------|
| Root: LLM-as-a-Judge | Branch 1: Self-Reference Methods | Leaf 1.1: Self-reference evaluation [1] | Judge generates own answer before judging | Lin et al. always use self-reference; this paper conditions it | Medium: C1 overlaps |
| Root: LLM-as-a-Judge | Branch 2: Self-Consistency Methods | Leaf 2.1: Self-consistency for correctness [3][4] | Agreement among samples correlates with correctness | Prior work uses self-consistency for answer selection, not for gating self-reference in judging | Medium: C2 application is incremental |
| Root: LLM-as-a-Judge | Branch 3: Judge Reliability | Leaf 3.1: Self-inconsistency [5] | Judges exhibit intra-rater variability | Addresses different failure mode (inconsistency vs error propagation) | Low: complementary |
| Root: LLM-as-a-Judge | Branch 3: Judge Reliability | Leaf 3.2: Probabilistic scoring [6] | Discrete scoring loses information | TrustJudge addresses score-comparison inconsistency; SSR-Judge addresses reference anchoring | Low: complementary |
| Root: LLM-as-a-Judge | Branch 4: Reference Quality | Leaf 4.1: Human-grounded references [2] | Human references are more reliable than synthetic | Krumdick et al. recommend human references; SSR-Judge uses self-generated references conditionally | Low: different reference strategy |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---------|----------------|-------------|------------------------|-----------------|-------------------------|
| [1] Lin et al. (2025) | LLM-as-a-Judge, self-reference evaluation | Judge solves task first, uses own answer as reference | Error propagation risk is noted in both papers | Lin et al. always use self-reference; SSR-Judge conditions it on agreement | Medium: C1 needs repositioning |
| [2] Krumdick et al. (2025) | LLM-as-a-Judge correctness grading | Judge struggles without correct reference; recommend human-written references | Both identify judge failure on hard items | Krumdick et al. advocate human references; SSR-Judge uses conditional self-references | Low: different approach |
| [3] Wang et al. (2022) | Self-consistency for reasoning | Agreement among samples correlates with answer correctness | Self-consistency calibration property | Wang et al. use for answer selection; SSR-Judge uses for gating self-reference | Medium: C2 is application-level novelty |
| [5] Haldar & Hockenmaier (2025) | LLM judge self-inconsistency | Judges exhibit high intra-rater variability | Both study judge reliability | Addresses inconsistency, not error propagation from wrong references | Low: complementary |
| [6] Wang et al. (2025) | TrustJudge: probabilistic scoring | Reduces score-comparison and transitivity inconsistencies | Both improve judge reliability | TrustJudge addresses scoring framework; SSR-Judge addresses reference anchoring | Low: complementary |

### Contribution-level Novelty Conclusion

C1 (error propagation identification): **partially_overlapping**. Lin et al. (2025) already identified the error propagation risk. This paper's addition is the quantitative slice analysis, which should be emphasized as the primary contribution rather than problem identification.

C2 (SSR-Judge method): **partially_overlapping**. Self-consistency calibration is a known property (Wang et al., 2022). The novelty lies in applying it to conditional self-reference gating in the judging setting, which is an incremental but useful application.

C3 (empirical performance): **supported**. The MMLU-Pro pairwise preference results are novel empirical findings. However, the claim should be bounded by acknowledging the single-model, single-benchmark evaluation constraint.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
LLM-as-a-Judge Reliability (Root)
├── Branch 1: Self-Reference Evaluation
│   └── Leaf 1.1: Always self-reference [1]
│       └── Difference: no gating, unconditional reference
├── Branch 2: Self-Consistency & Confidence Estimation
│   ├── Leaf 2.1: Self-consistency for answer selection [3][4]
│   └── Leaf 2.2: Confidence gating for judging (SSR-Judge, this paper)
│       └── Value: applies calibration to conditional reference routing
├── Branch 3: Judge Reliability & Consistency
│   ├── Leaf 3.1: Self-inconsistency measurement [5]
│   ├── Leaf 3.2: Probabilistic scoring frameworks [6]
│   └── Leaf 3.3: Confidence-driven judging [Tian et al.]
└── Branch 4: Reference Quality Strategies
    └── Leaf 4.1: Human-grounded references [2]
        └── Difference: advocates external gold references vs self-generated
```

```text
ASCII Diagram — Paper Structure & Evidence Map
[Problem: self-reference can propagate errors when self-answer is wrong]
    -> [Evidence: Table 2 slice analysis shows 13.25pp drop on Non-unanimous+Wrong]
    -> [Method: SSR-Judge gates self-reference on k=5 agreement >= 4/5]
    -> [Evidence: 78.66% correctness at 5/5 agreement vs 35.51% at 3/5]
    -> [Result: 58.93% acc on MMLU-Pro, +0.72pp over Always Self-Ref]
    -> [Gap: single model/benchmark, no variance reporting, compute-cost framing unclear]
```

```text
ASCII Diagram — Revision Strategy Roadmap
[P0: Reposition contribution claims]
    -> [Action: C1 emphasize quantitative slice analysis; C2 clarify application novelty]
    -> [Expected gain: resolves overlap with Lin et al. (2025)]
[P0: Clarify compute-cost framing]
    -> [Action: state No-Ref uses 1/6th compute; bound +6.86pp interpretation]
    -> [Expected gain: prevents misleading efficiency claims]
[P1: Expand limitations]
    -> [Action: add category underperformance and single-model constraint]
    -> [Expected gain: improves claim scope honesty]
[P2: Multi-model evaluation]
    -> [Action: evaluate on Llama-3-70B and Mixtral]
    -> [Expected gain: strengthens external validity]
```

## References
[1] Do Before You Judge: Self-Reference as a Pathway to Better LLM Evaluation 2509.19880

[2] No Free Labels: Limitations of LLM-as-a-Judge Without Human Grounding 2503.05061

[3] Self-consistency improves chain of thought reasoning in language models 2203.11171

[4] Language models (mostly) know what they know 2207.05221

[5] Rating Roulette: Self-Inconsistency in LLM-As-A-Judge Frameworks 2510.27106

[6] TrustJudge: Inconsistencies of LLM-as-a-Judge and How to Alleviate Them 2509.21117

## Scores
**Final Score:** 5.5/10

This score reflects a paper with a clean, well-motivated methodological contribution that addresses a real problem in LLM-as-a-Judge evaluation. The SSR-Judge method is simple, effective, and well-experimentally validated. However, the novelty is incremental: the error propagation risk was already identified by Lin et al. (2025), and the self-consistency calibration property is well-established (Wang et al., 2022). The true contribution—applying self-consistency to conditional self-reference gating—is useful but application-level rather than foundational. Additionally, the compute-cost framing issue (No-Reference baseline uses 1/6th the compute of SSR-Judge) and the single-model/single-benchmark evaluation constraint limit the strength of the empirical claims.

The paper would benefit significantly from: (a) repositioning contribution claims to emphasize quantitative slice analysis and application novelty, (b) clarifying compute-cost differences in baseline comparisons, and (c) expanding the evaluation to include at least one additional judge model. With these revisions, the paper would be much stronger.

**Post-Revision Target:** [6.5, 7.5]/10

If the authors address the P0 items (contribution repositioning, compute-cost clarification) and add one additional judge model for cross-model validation, the paper would present a more defensible novelty claim and stronger empirical evidence, warranting a score in the mid-range.