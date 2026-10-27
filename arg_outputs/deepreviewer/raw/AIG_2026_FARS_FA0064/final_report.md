## Summary
Paper proposes NLL-guided layer selection for SWAA, showing strong results on LongMemEval with Qwen3-4B but limited by single-model evaluation and some novelty overclaims.

## Strengths
- Conceptually clear and well-motivated NLL-based scoring approach
- Strong empirical gains over LightTransfer and periodic baselines on LongMemEval
- Useful de-confounding analysis validating the long-range specificity of the NLL signal

## Weaknesses
- Single model/benchmark evaluation limits generalizability claims
- Leave-one-out scoring may be confounded by downstream representation propagation
- Missing BOSCH and KL-Guided citations weaken novelty positioning
- Overconfident claims about unsolved problem and Pareto frontier advancement

## Key Issues
- Per-layer NLL scoring confound: early layers may appear more important due to downstream propagation effects
- Borderline p-value (0.069) in de-confounding analysis treated as 'confirmation' rather than suggestion
- Missing variance reporting on calibration stability downstream accuracy

## Actionable Suggestions
- Add at least one additional model family and benchmark for cross-model validation
- Discuss and mitigate the downstream propagation confound in layer scoring
- Add BOSCH and KL-Guided citations with explicit differentiation
- Bound novelty and efficiency claims to tested settings
- Report multi-seed variance on downstream accuracy and calibration stability

## Storyline Options + Writing Outlines
- Training-free layer selection using NLL degradation signal for hybrid attention adaptation
- Direct loss-based scoring outperforms attention heuristics for identifying FA layers in SWAA

## Priority Revision Plan
The following revision plan is prioritized by impact on scientific validity and paper acceptance probability.

## P0 — Critical Revisions (Must complete before resubmission)

| Priority | Issue | Action | Expected Impact |
|----------|-------|--------|-----------------|
| P0-1 | Novelty overclaim: "remains unsolved" | Rewrite Abstract/Intro to acknowledge SWAA, LightTransfer, BOSCH, KL-Guided as existing approaches. Frame gap as limitation of existing signals, not unsolved problem. | Restores credibility; prevents immediate desk-reject for misrepresenting the field. |
| P0-2 | Missing BOSCH citation | Add Section 2.3 paragraph on BOSCH (Ghaddar et al., 2026) with explicit differentiation: layer-level vs head-level selection, practical deployment trade-offs. | Closes novelty gap; positions paper relative to strongest recent competitor. |
| P0-3 | Per-layer scoring confound | Add discussion in Section 3.2 acknowledging that toggling one layer to FA propagates to downstream layers, potentially biasing early layers upward. Suggest matched-control baseline as future work. | Addresses validity concern; shows methodological awareness. |
| P0-4 | Single-model generalizability claim | Bound all "fundamentally better signal" claims to "on LongMemEval with Qwen3-4B." Add explicit limitation paragraph in Section 5. | Prevents overreach; aligns claims with evidence scope. |

## P1 — Important Revisions (Strongly recommended)

| Priority | Issue | Action | Expected Impact |
|----------|-------|--------|-----------------|
| P1-1 | De-confounding p-value language | Change "confirms" to "suggests" regarding Spearman ρ = 0.306, p = 0.069. Explain non-zero short-prompt Δ-NLL. | More defensible statistical interpretation. |
| P1-2 | Variance reporting | Add mean±std over ≥3 seeds for downstream accuracy in calibration stability analysis (Section 4.6). | Strengthens reliability of calibration recommendations. |
| P1-3 | Contribution restructuring | Merge deployment claim into conclusion; restructure contributions to emphasize conceptual/methodological contributions over engineering details. | Improves perceived scientific impact. |
| P1-4 | Calibration throughput details | Report forward-pass throughput (passes/sec) and rough scaling estimate for deeper models. | Improves reproducibility and practical assessment. |

## P2 — Nice-to-Have (Quality improvement)

| Priority | Issue | Action | Expected Impact |
|----------|-------|--------|-----------------|
| P2-1 | Cross-model validation | Add one additional model (e.g., LLaMA-3-8B) and one additional benchmark (e.g., RULER). | Dramatically strengthens generalizability. |
| P2-2 | Related work depth | Expand Section 2.3 to discuss Flux Attention and HySparse as additional context for hybrid attention design choices. | Richer scholarly positioning. |

```text
ASCII Diagram — Revision Strategy Roadmap
[Overclaim: 'unsolved problem']
    -> [Fix: acknowledge SWAA/LightTransfer/BOSCH/KL-Guided]
    -> [Impact: credibility restored]

[Missing BOSCH citation]
    -> [Fix: add Section 2.3 paragraph + differentiation]
    -> [Impact: novelty gap closed]

[Scoring confound: downstream propagation]
    -> [Fix: add discussion + matched-control suggestion]
    -> [Impact: validity concern addressed]

[Single-model claim overreach]
    -> [Fix: bound claims to 'on LongMemEval with Qwen3-4B']
    -> [Impact: overreach prevented]

[Borderline p-value language]
    -> [Fix: 'confirms' -> 'suggests', explain short-prompt residual]
    -> [Impact: defensible statistics]

[Missing variance]
    -> [Fix: multi-seed std on calibration stability]
    -> [Impact: reliability strengthened]
```

## Experiment Inventory & Research Experiment Plan
## (a) Completed Experiment Inventory (Full Coverage)

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|--------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | NLL-guided FA layer selection outperforms periodic and heuristic baselines | LongMemEval 24k, Qwen3-4B-Thinking-2507, SWAA config (window=2048, keep-first=10, FA decode). Baselines: Full FA, 1/2-FA Periodic, 1/4-FA Periodic, LightTransfer 1/4-FA, Naive SWA | Accuracy (%) | NLL-Guided 1/4-FA: 64.6%, matching 1/2-FA Periodic (65.0%), +10.4pp over 1/4-FA Periodic, +26.4pp over LightTransfer | NLL scoring provides better layer selection signal than fixed patterns and attention heuristics on this setting | Single model/benchmark; no variance reporting; no statistical significance tests |
| E2 | Per-task breakdown validates NLL-guided selection across task types | Same setup as E1, broken down by 6 LongMemEval task types | Accuracy (%) per task | NLL-Guided outperforms LightTransfer on all 6 tasks, largest gains on single-session-user (+37.1pp) and temporal-reasoning (+33.9pp) | Task-specific sensitivity to FA layer selection | No analysis of why certain tasks benefit more; no per-task variance |
| E3 | De-confounding: NLL signal captures long-range attention needs, not generic sensitivity | Compare long-prompt (16k-32k) vs short-prompt (1.5k) calibration rankings | Spearman ρ, Jaccard overlap, Δ-NLL magnitude ratio | ρ=0.306 (p=0.069), Jaccard=0.2, 85.6× magnitude difference | NLL signal is specific to long-range attention needs | Borderline p-value; short-prompt residual Δ-NLL not explained |
| E4 | Calibration stability across calibration set sizes | Vary calibration examples: 16 vs 64, using 16k-32k token prompts | Jaccard similarity, downstream accuracy | 16 examples: Jaccard=0.64, accuracy=62.2%; 64 examples: accuracy=64.6% | Method is reasonably stable with small calibration sets | No multi-seed variance; only two calibration sizes tested |

## (b) Research-Theme Gap Diagnosis

**New Knowledge Gap:** The paper demonstrates that NLL-based scoring is effective for FA layer selection on LongMemEval, but does not establish whether this is a general principle. Cross-model and cross-benchmark validation is missing.

**Reproducibility Gap:** Calibration procedure is described but lacks key reproducibility details: forward-pass throughput, exact GPU memory usage, multi-seed variance, and calibration data distribution characteristics.

**Impact on Practice Gap:** The 15-minute calibration claim is promising but unverified for larger models (80+ layers) or larger calibration sets. The break-even analysis (1,354 inference requests) lacks a sensitivity analysis with respect to prompt length and hardware configuration.

## (c) Proposed Research Experiments (P0/P1/P2)

| Priority | Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Quality Gain |
|----------|-------------|-----------|----------------|-------------------|---------|-------------------|---------------|----------------------|
| P0-1 | NLL scoring generalizes across models | NLL-guided selection will outperform periodic and LightTransfer on at least one additional model family | Evaluate on LLaMA-3-8B on LongMemEval or RULER | Same baselines as E1 | Accuracy (%) | NLL-Guided outperforms 1/4-FA Periodic by ≥5pp on at least one additional model | 2-3 days on 4-8 GPUs | Major: validates cross-model transferability |
| P0-2 | Variance and statistical reliability | Results are stable across random seeds | Repeat E1 and E3 with ≥3 seeds | Same setups | Mean±std accuracy, paired significance tests | std < 2pp; p < 0.05 vs strongest baseline | 1-2 days on 4 GPUs | Major: establishes statistical confidence |
| P1-1 | Cross-benchmark generalization | NLL scoring works on non-memory benchmarks too | Evaluate on RULER or LongBench with same model | Same baselines | Accuracy (%) or benchmark-specific metrics | Outperforms periodic baseline on at least one additional benchmark | 2-3 days on 4-8 GPUs | Medium: broadens claim scope |
| P1-2 | Scaling to deeper models | Calibration scales linearly with model depth; method remains effective | Evaluate on a 72+ layer model (e.g., LLaMA-3-70B if feasible) | Same baselines | Accuracy, calibration time | Calibration < 1 hour; accuracy within 3pp of 1/2-FA | 3-5 days on 8 GPUs | Medium: validates practical scalability |
| P2-1 | Matched-control scoring | Matched-control baseline reduces early-layer bias in Δ-NLL estimates | Compare leave-one-out scoring vs scoring on a mixed FA/SWA baseline | Same setups | Layer ranking correlation, downstream accuracy | If rankings change significantly, confound is validated | 1-2 days on 4 GPUs | Low-Medium: methodological improvement |

```text
ASCII Diagram — Experiment Upgrade Plan
P0 Stage (this week):
  ├── P0-1: Cross-model validation (LLaMA-3-8B + LongMemEval)
  └── P0-2: Multi-seed variance reporting (≥3 seeds, E1+E3)
P1 Stage (before submission):
  ├── P1-1: Cross-benchmark (RULER or LongBench)
  └── P1-2: Deeper model scaling (72+ layers)
P2 Stage (nice-to-have):
  └── P2-1: Matched-control confound test
```

## (d) Traceability Mapping

| Proposed Experiment | Unresolved Core Claim | Quality Improvement |
|--------------------|----------------------|--------------------|
| P0-1 | "NLL-based scoring provides a fundamentally better signal" (p.4, para 2) | Validates cross-model generalizability |
| P0-2 | "64.6% accuracy" without variance (p.4, Table 1) | Establishes statistical reliability |
| P1-1 | Implied broad applicability of NLL scoring | Bounds claim scope with cross-benchmark evidence |
| P1-2 | "15 minutes calibration" claim for 36-layer model (p.4, Sec 3.4) | Validates practical scalability |
| P2-1 | Per-layer scoring confound (p.3, Sec 3.2) | Addresses validity concern about early-layer bias |

## Novelty Verification & Related-Work Matrix
## 9A — Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|-------------------|-----|------------|----------------------|
| C1 | NLL-guided layer selection, a training-free method for identifying which layers should retain full attention in hybrid sliding-window models | [1] SWAA, [2] LightTransfer, [3] BOSCH, [4] KL-Guided | partially_overlapping | Loss-based layer selection concept exists in KL-Guided [4] (KL divergence, requires training) and BOSCH [3] (black-box probing, head-level). NLL-based answer-token scoring on a frozen model without student training is a novel scoring mechanism, but the general paradigm of loss-based layer sensitivity detection overlaps with prior work. | High | Frame as a novel scoring signal within the established paradigm of loss-based layer selection, not as solving an "unsolved" problem. |
| C2 | NLL-Guided 1/4-FA achieves 64.6% on LongMemEval, matching 1/2-FA Periodic while halving FA budget, outperforming best 1/4-FA periodic by 10.4pp | [1] SWAA, [2] LightTransfer | supported | This specific empirical result on LongMemEval with Qwen3-4B is novel. No prior work reports NLL-based FA layer selection on this benchmark/model combination. | High | Bound claim to "on LongMemEval with Qwen3-4B"; avoid implying universal superiority. |
| C3 | De-confounding analysis showing NLL signal is specific to long-range attention needs (Spearman ρ=0.306 between long/short-prompt rankings) | None directly | supported | This specific de-confounding experimental design and result is novel. Prior works do not report long-vs-short prompt ranking correlations for layer sensitivity signals. | Medium | Use cautious language ("suggests" not "confirms") given borderline p-value (0.069). |

## 9B — Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|--------------------------|-------------------|-------------------------|-------------------|
| Branch 1: Training Paradigm | Leaf 1.1: Training-free adaptation | [1] SWAA, [2] LightTransfer, [3] BOSCH | Pretrained FA model; no retraining required | This paper uses NLL scoring on frozen model; SWAA uses periodic patterns; LightTransfer uses attention heuristics; BOSCH uses black-box head probing | Low risk for SWAA/LightTransfer differentiation; Medium risk vs BOSCH (also training-free) |
| Branch 1: Training Paradigm | Leaf 1.2: Training-based distillation | [4] KL-Guided | Requires training a student model; KL divergence between teacher/student | This paper is entirely training-free; KL-Guided requires student training and distillation pipeline | Low risk (different paradigm), but conceptual overlap in using loss signals |
| Branch 2: Selection Granularity | Leaf 2.1: Layer-level selection | [1] SWAA, [2] LightTransfer, [4] KL-Guided | FA/SWA assignment per layer | This paper operates at layer level, same as these methods | Low novelty risk (same granularity) |
| Branch 2: Selection Granularity | Leaf 2.2: Head-level selection | [3] BOSCH | FA/SWA assignment per attention head | This paper operates at layer level, which BOSCH argues is suboptimal | Medium risk: BOSCH suggests layer-level is insufficient |
| Branch 3: Scoring Signal | Leaf 3.1: Attention-pattern heuristics | [2] LightTransfer | Attention mass/lazy ratio as proxy for layer importance | This paper uses direct NLL on answer tokens, not attention weights | Clear differentiation |
| Branch 3: Scoring Signal | Leaf 3.2: Loss-based sensitivity | [4] KL-Guided, [3] BOSCH | Loss or probing signal indicates layer importance | KL-Guided uses KL divergence (requires training); BOSCH uses black-box probes (head-level); this paper uses NLL on frozen model (layer-level, training-free) | Partial overlap with both |

## 9C — Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---------|----------------|-------------|------------------------|-----------------|-------------------------|
| [1] SWAA | Training-free SWA adaptation for long-context LLMs | Periodic FA/SWA layer interleaving, sink token preservation, FA decode | Same SWAA framework; same training-free paradigm | SWAA uses fixed periodic patterns; this paper uses NLL-guided data-driven selection | Positions this paper as a layer-selection improvement within SWAA framework |
| [2] LightTransfer | Training-free hybrid adaptation via attention heuristics | "Lazy ratio" attention-mass heuristic to identify layers for streaming attention | Training-free layer selection for FA/SWA hybridization | LightTransfer uses attention weights; this paper uses answer-token NLL | Strong empirical improvement (26.4pp) supports NLL as better signal on this task |
| [3] BOSCH | Training-free head-level SWA selection via black-box optimization | Large Neighborhood Search with layer-importance probing and head-level optimization | Training-free sensitivity detection for FA/SWA assignment | BOSCH operates at head level with black-box search; this paper uses analytical NLL scoring at layer level | Raises question of whether layer-level granularity is sufficient; requires discussion |
| [4] KL-Guided | Distillation-based layer selection for hybrid models | KL divergence between teacher/student outputs to identify critical layers | Loss-based layer importance scoring | KL-Guided requires student model training; this paper is entirely training-free on frozen model | Conceptual overlap in loss-based scoring, but different training requirements create clear differentiation |

## Contribution-level Novelty Conclusion

**C1 (partially_overlapping):** The NLL-guided scoring mechanism is a novel training-free signal for FA layer selection, but the general paradigm of using loss-based sensitivity to identify important layers overlaps with KL-Guided [4] and BOSCH [3]. The paper should frame its contribution as introducing NLL-based answer-token scoring as a new, training-free scoring mechanism within this established paradigm, rather than claiming the layer selection problem is "unsolved."

**C2 (supported):** The empirical result on LongMemEval with Qwen3-4B is novel. No prior work demonstrates NLL-guided layer selection on this benchmark. The claim should be bounded to the tested setting to avoid overgeneralization.

**C3 (supported):** The de-confounding experimental design comparing long-prompt vs short-prompt calibration rankings is novel. The statistical evidence is suggestive but not definitive (p=0.069), so cautious language is recommended.

## ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Hybrid Attention Layer Selection (Root)
├── Branch 1: Training Paradigm
│   ├── Leaf 1.1: Training-Free Adaptation
│   │   ├── SWAA [1]: periodic FA/SWA interleaving
│   │   ├── LightTransfer [2]: attention-mass lazy ratio
│   │   ├── BOSCH [3]: black-box head-level probing
│   │   └── This Paper: NLL-based answer-token scoring (layer-level)
│   └── Leaf 1.2: Training-Based Distillation
│       └── KL-Guided [4]: KL divergence teacher/student scoring
└── Branch 2: Selection Granularity
    ├── Leaf 2.1: Layer-Level Selection
    │   ├── SWAA [1], LightTransfer [2], KL-Guided [4], This Paper
    └── Leaf 2.2: Head-Level Selection
        └── BOSCH [3]

Manuscript Positioning:
  ├── Training-free (Leaf 1.1) + Layer-level (Leaf 2.1)
  ├── Novel scoring signal: answer-token NLL degradation
  ├── Value solved: task-aware, training-free FA layer selection
  └── Gap vs BOSCH: layer-level vs head-level granularity
```

## References
[1] SWAA: Sliding Window Attention Adaptation for Efficient Long-Context LLMs Without Pretraining 2512.10411

[2] LightTransfer: Your Long-Context LLM is Secretly a Hybrid Model with Effortless Adaptation 2410.13846

[3] BOSCH: Black-Box Binary Optimization for Short-Context Attention-Head Selection in LLMs 2604.05942

[4] Distilling to Hybrid Attention Models via KL-Guided Layer Selection 2512.20569

## Scores
Final Score: 5.5/10

The paper presents a conceptually clear and well-motivated method (NLL-guided layer selection for SWAA) with strong empirical gains over existing baselines on LongMemEval. The NLL-based scoring signal is a useful contribution to the training-free hybrid attention adaptation paradigm, and the de-confounding analysis provides suggestive mechanistic evidence.

However, the score is limited by: (a) single-model, single-benchmark evaluation that does not yet support generalizability claims, (b) novelty overclaims that misrepresent the state of the field by omitting BOSCH and KL-Guided as prior work on loss-based layer selection, (c) a leave-one-out scoring strategy that may be confounded by downstream representation propagation, and (d) borderline statistical evidence (p=0.069) treated with overconfident language.

These are fixable issues. With cross-model validation, BOSCH/KL-Guided citations, confound discussion, and bounded claims, the paper could reach a significantly higher score.

Post-Revision Target: [7.0, 8.5]/10