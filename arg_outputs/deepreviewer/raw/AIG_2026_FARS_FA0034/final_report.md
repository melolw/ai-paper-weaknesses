## Summary
This paper proposes **VidVec-RouteK**, a training-free method for adaptive reranking budget allocation in video-text retrieval. The core idea is to use **cross-layer ranking disagreement** (measured via Jaccard distance between top-k candidate sets across transformer layers) as a per-query confidence signal. A 3-tier routing architecture maps disagreement scores to reranking budgets K ∈ {10, 60, 100}, allocating more compute to ambiguous queries. Evaluated on MSR-VTT and DiDeMo, the method achieves +0.9 and +1.5 R@1 over margin-based routing at matched avg-K ≈ 30, while reducing reranker forward passes by ~70% compared to fixed K=100.

**Research Value**: The paper addresses a practical efficiency-quality trade-off in two-stage retrieve-then-rerank pipelines. The contribution is incremental but useful: it adapts cross-layer representation insights (previously used for early exit in classification or feature enrichment) to retrieval routing. The training-free nature makes it immediately deployable as a drop-in enhancement to VidVec.

**Primary Concerns**: (1) Novelty is partially overlapped with cross-model disagreement approaches; explicit differentiation is needed. (2) Key causal claims (e.g., "noise from deep candidates") are unverified. (3) Missing variance reporting and reproducibility details (hyperparameter ablation for m=20, margin baseline specification) weaken decision confidence. (4) Single-model, two-benchmark evaluation limits generalization claims.

## Strengths
1. **Practical efficiency gains**: The method achieves a ~70% reduction in reranker forward passes (avg-K≈30 vs K=100) with minimal performance degradation. This is a practically valuable contribution for deployment scenarios where MLLM inference cost is a bottleneck.

2. **Training-free design**: Unlike learned routing policies that require labeled data or additional training, the cross-layer disagreement signal is computed from the model's existing forward pass. This makes the method immediately deployable as a drop-in enhancement to VidVec without retraining overhead.

3. **Sound methodological intuition**: The insight that agreement across transformer layers reflects model confidence is well-motivated. The use of Jaccard distance on top-k candidate sets provides a simple, interpretable, and computationally cheap disagreement metric.

4. **3-tier routing provides nuanced allocation**: The ablation showing that 3-tier routing (K∈{10,60,100}) outperforms binary routing (K∈{10,100}) by +0.4 to +0.9 R@1 demonstrates that the medium tier captures meaningful query difficulty granularity that binary schemes miss.

5. **Clear empirical evidence on standard benchmarks**: Results on MSR-VTT and DiDeMo provide direct comparisons against a fixed-K upper bound and margin-based routing baseline, establishing a clear performance-efficiency trade-off curve.

## Weaknesses
1. **Novelty overlap with cross-model disagreement**: The core mechanism (using inter-model/inter-layer disagreement as a confidence signal for routing) is conceptually similar to Cross-Model Disagreement (Gorbett & Jana, 2026), which uses a second verifier model's surprise (perplexity/entropy) to detect incorrect predictions. While the current method uses intra-model cross-layer disagreement (avoiding the second model cost), this conceptual overlap is not acknowledged, making C1 appear more novel than it actually is. **Impact**: Moderate novelty risk; reviewers familiar with cross-model approaches may view this as a straightforward adaptation.

2. **Unverified causal claim about "noise from deep candidates"**: The paper states that "reranking irrelevant candidates deep in the retrieval list can introduce noise, and selective reranking avoids this issue" (Page 5). This causal explanation is presented as the reason why avg-K≈30 outperforms K=100 on MSR-VTT, but no empirical analysis supports it. Alternative explanations include score calibration issues, candidate diversification effects, or better query-classification. **Impact**: Major validity risk; presenting an unverified mechanism as fact weakens scientific defensibility.

3. **Missing variance reporting and statistical significance**: All results are reported as point estimates without mean±std over multiple seeds. With gains of 0.9 and 1.5 points on ~1000 queries, stability across random seeds is essential for decision confidence. **Impact**: Major reliability risk; without variance, gains could be seed-dependent artifacts.

4. **Incomplete ablation of key hyperparameter m=20**: The top-m parameter for Jaccard computation is set to 20 "by default" without ablation or justification. This is a critical design choice that determines the sensitivity of the disagreement signal. **Impact**: Minor reproducibility risk; authors should provide at least a sensitivity analysis.

5. **Selective result framing on DiDeMo**: The abstract and main results highlight +1.5 R@1 on DiDeMo over margin routing but do not mention that the method still underperforms fixed K=100 by 0.8 points (53.3 vs. 54.1). This asymmetry risks misleading readers about the scope of the contribution. **Impact**: Minor objectivity issue; balanced reporting strengthens credibility.

6. **Single-model, two-benchmark evaluation**: The method is evaluated only on VideoLLaMA3-7B and two benchmarks (MSR-VTT, DiDeMo). It is unclear whether the disagreement signal generalizes to other MLLM architectures (e.g., LLaVA, InternVideo2) or larger video retrieval datasets (e.g., ActivityNet, DiDeMo 10k). **Impact**: Moderate generalization risk; broader evaluation is needed before claiming methodological robustness.

## Key Issues
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit | Priority |
|-------|------------|------------|-----------------|------------------|----------|
| Unverified causal claim: "noise from deep candidates" causes K=100 to underperform | Major | No empirical analysis supports the stated mechanism; alternative explanations exist (score calibration, diversification effects) | Frame as hypothesis; add reranker score distribution analysis across candidate ranks | Improves scientific defensibility of the central finding | P0 |
| Novelty overlap with Cross-Model Disagreement (Gorbett & Jana, 2026) not acknowledged | Major | Related Work omits key prior work on disagreement-based routing signals | Add explicit differentiation paragraph in Related Work and Introduction | Strengthens novelty positioning by showing landscape awareness | P0 |
| Missing variance reporting (no mean±std over ≥3 seeds) | Major | Results reported as point estimates only | Add multi-seed variance reporting for all main results | Enables assessment of result stability and statistical reliability | P0 |
| Hyperparameter m=20 lacks ablation or justification | Minor | m is critical for disagreement sensitivity but not analyzed in Table 2 | Add m-ablation (e.g., m∈{5,10,20,30}) in Table 2 | Improves reproducibility and hyperparameter transparency | P1 |
| DiDeMo result selectively framed (underperformance vs K=100 omitted) | Minor | Abstract/main results emphasize margin gains but not K=100 trade-off | Balanced reporting in abstract and results | Improves objectivity and reader trust | P1 |
| Single-model evaluation limits generalization claims | Moderate | Method only tested on VideoLLaMA3-7B | Evaluate on at least one additional MLLM architecture | Validates method generality | P2 |

## Actionable Suggestions
1. **Add variance reporting (P0 - Must)**: Run all main experiments with at least 3 random seeds. Report mean±std for R@1, R@5, R@10, and MnR in Table 1. Add a paired significance test (e.g., McNemar's test or bootstrap CI) comparing 3-tier routing against margin routing and fixed K=100. This directly addresses the statistical reliability concern and is the single highest-impact revision.

2. **Frame the "noise" claim as a hypothesis (P0 - Must)**: In Section 4.2, replace the definitive statement "reranking irrelevant candidates deep in the retrieval list can introduce noise" with "We hypothesize that reranking irrelevant candidates deep in the retrieval list may introduce score noise." Then add one analysis paragraph or figure showing the reranker's score distribution across different candidate ranks (e.g., box plot of reranker log-likelihood for top-10 vs. top-11-100 candidates). If the tail candidates show wider score variance or systematic bias, this would support the hypothesis.

3. **Acknowledge Cross-Model Disagreement in Related Work (P0 - Must)**: Add a paragraph in the "Adaptive Inference" subsection discussing Cross-Model Disagreement (Gorbett & Jana, 2026) and explicitly differentiate: "Unlike cross-model disagreement which requires an additional verifier model, our intra-model cross-layer approach requires no extra model overhead." Also cite CALM (Schuster et al., 2022) and CATs (Schuster et al., 2021) for layer-wise consistency in early exit, and HVP-Net (Zhang et al., 2026) for multi-layer features in video retrieval.

4. **Add m-ablation to Table 2 (P1 - Nice-to-have)**: Add a row to Table 2 testing m∈{10, 20, 30} with the default layer set. This costs minimal computation but significantly improves reproducibility. If performance is stable across m values, it also demonstrates the method's robustness to this hyperparameter.

5. **Balance DiDeMo result framing (P1 - Nice-to-have)**: In the abstract and Section 4.2, explicitly state that on DiDeMo, the method trades 0.8 R@1 points against fixed K=100 for a 70% compute reduction. This balanced framing improves scientific objectivity and reader trust.

6. **Specify Margin Routing implementation details (P1 - Nice-to-have)**: In Section 4.1, clearly state how the margin is computed (e.g., "margin = cos(e_q, v_top1) - cos(e_q, v_top2) at Layer 24") and how its thresholds are calibrated (percentile-based or validation-optimized). This ensures the baseline is reproducible.

## Storyline Options + Writing Outlines
### Abstract Outline (complete)

*Current abstract follows a standard 4-part structure but lacks budget anchoring and selective framing. The following S1-S5 plan provides a more balanced and transparent rewrite.*

- **S1 (Problem + Domain):** "Two-stage retrieve-then-rerank pipelines are standard for video-text retrieval but face a fundamental efficiency-quality trade-off: the reranking budget K directly determines both accuracy and computational cost, as each query requires K independent forward passes through an expensive reranker." (Role: Establish stakes; Evidence: Intro P1; Anchor: K=100 baseline)
- **S2 (Significance/Challenge):** "Not all queries require the same reranking effort—some are 'easy' and some are 'hard'—yet existing adaptive methods rely on embedding similarity margins that fail to capture underlying model uncertainty." (Role: Identify gap; Evidence: Intro P2; Anchor: Margin routing limitation)
- **S3 (Prior Gap):** "Prior work has explored cross-model disagreement for routing but requires additional verifier models, while intra-model cross-layer signals have been used for feature enrichment rather than adaptive budget allocation." (Role: Differentiate novelty; Evidence: Related Work; Anchor: Cross-Model Disagreement vs. HVP-Net)
- **S4 (Proposed Method):** "We propose VidVec-RouteK, a training-free method that uses cross-layer ranking disagreement—measured via Jaccard distance between top-k candidate sets across transformer layers—as a lightweight per-query confidence signal, routing queries to one of three reranking budgets." (Role: Method intuition; Evidence: Method Sec 3; Anchor: Eq. 1, 3-tier routing)
- **S5 (Key Result + Bounded Implication):** "On MSR-VTT and DiDeMo, our method achieves +0.9 and +1.5 R@1 over margin-based routing at matched avg-K ≈ 30, reducing reranker forward passes by approximately 70% compared to fixed K=100, while maintaining competitive performance on evaluated benchmarks." (Role: Scoped claim; Evidence: Table 1; Anchor: R@1 deltas at avg-K≈30)

### Introduction Outline (complete)

*Current introduction has 4 substantive paragraphs. The following P1-P5 plan improves narrative flow, adds concrete stakes, and explicitly answers the three core questions.*

- **P1 (Big Picture + Stakes):** Define the two-stage retrieve-then-rerank paradigm for video-text retrieval, citing VidVec as the current state-of-the-art. Quantify the compute cost: each query requires K forward passes through a 7B-parameter MLLM, making reranking the dominant latency bottleneck. Explicitly state the efficiency-quality trade-off. (Role: Territory + Stakes; Transition: "While effective, this approach faces a fundamental efficiency-quality trade-off...")
- **P2 (Concrete Gap + Motivation):** Introduce the insight that queries have varying difficulty. Critique the existing margin-based confidence signal: it captures only top-1 vs. top-2 ranking, not underlying representation uncertainty. Provide a qualitative failure example (e.g., "a query with a large margin may still have an incorrect top-1 candidate if the embedding representation is globally biased"). (Role: Gap + Failure mode; Transition: "This motivates the need for a more principled confidence signal...")
- **P3 (Solution Intuition):** Propose cross-layer ranking disagreement as a training-free confidence signal. Ground the intuition in prior work: Skean et al. (2025) show intermediate layers encode rich representations; Bolya et al. (2025) find best visual embeddings in intermediate layers. Explain the mechanism: when layers agree, the model is confident; when they disagree, the query is ambiguous. Explicitly differentiate from cross-model disagreement (Gorbett & Jana, 2026) by noting the intra-model, zero-overhead advantage. (Role: Idea + Differentiation; Transition: "Our contributions are as follows:")
- **P4 (Contribution Summary):** List 3 explicit contributions. (1) Cross-layer ranking disagreement as a training-free confidence signal, measuring Jaccard distance between top-k sets. (2) 3-tier routing architecture mapping disagreement to K∈{10,60,100}. (3) Empirical demonstration of +0.9/+1.5 R@1 over margin routing at matched avg-K≈30, with 70% compute reduction. (Role: Contribution claim; Anchor: Abstract/Method)
- **P5 (Evidence Preview):** Briefly preview the main experimental findings: evaluation on MSR-VTT and DiDeMo, ablation showing robustness to layer choices and metrics, and query distribution analysis demonstrating generalizable difficulty stratification. (Role: Roadmap/Preview; Transition: "Section 2 reviews related work...")

## Priority Revision Plan
### P0 — Publication-Critical Revisions (Must complete before resubmission)

| # | Action | Effort | Expected Impact |
|---|--------|--------|-----------------|
| 1 | Run all main experiments with ≥3 random seeds; report mean±std for R@1, R@5, R@10, MnR in Table 1; add paired significance test vs. margin routing and fixed K=100 | Medium (1-2 days compute) | Enables assessment of result stability; directly addresses major validity concern |
| 2 | Frame the "noise from deep candidates" explanation as a hypothesis; add one analysis (e.g., reranker score distribution box plot across candidate ranks) to support or refute the claim | Low-Medium (1 day analysis) | Improves scientific defensibility of the central finding; removes unverified causal claim |
| 3 | Add explicit discussion of Cross-Model Disagreement (Gorbett & Jana, 2026), CALM (Schuster et al., 2022), CATs (Schuster et al., 2021), and HVP-Net (Zhang et al., 2026) in Related Work; differentiate intra-model vs. cross-model and retrieval vs. classification | Low (writing only) | Strengthens novelty positioning by showing landscape awareness; mitigates overlap risk |

### P1 — Quality Improvement Revisions (Recommended)

| # | Action | Effort | Expected Impact |
|---|--------|--------|-----------------|
| 4 | Add m-ablation to Table 2 (test m∈{10, 20, 30}) | Low (1 day compute) | Improves reproducibility and hyperparameter transparency |
| 5 | Balance DiDeMo result framing: explicitly state the 0.8 R@1 trade-off vs. fixed K=100 | Low (writing only) | Improves objectivity and reader trust |
| 6 | Specify Margin Routing implementation details: how margin is computed and how thresholds are calibrated | Low (writing only) | Ensures baseline reproducibility |
| 7 | Quantify the relative overhead of 3-layer embedding extraction vs. single-layer in Section 3.5 | Low (writing only) | Improves complexity analysis rigor |

### P2 — Stretch Goals (Optional, for stronger paper)

| # | Action | Effort | Expected Impact |
|---|--------|--------|-----------------|
| 8 | Evaluate on one additional MLLM architecture (e.g., LLaVA) to validate method generality | Medium-High (3-5 days) | Strengthens generalization claims |
| 9 | Evaluate on a third benchmark (e.g., ActivityNet or DiDeMo 10k) | Medium (2-3 days) | Broadens empirical coverage |
| 10 | Add a query-level error analysis: categorize misrouted queries (easy→hard, hard→easy) and analyze disagreement score distributions per category | Medium (1-2 days analysis) | Provides deeper insight into routing mechanism effectiveness |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory (full coverage)

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|---------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | Main comparison: 3-tier routing vs. margin routing vs. fixed K=100 | MSR-VTT 1k-A & DiDeMo, VideoLLaMA3-7B, VidVec setup | R@1, R@5, R@10, MnR, avg-K | 3-tier best among adaptive methods; +0.9/+1.5 R@1 over margin; exceeds K=100 on MSR-VTT | Method achieves efficiency-quality gains | No variance reported (single seed); DiDeMo underperforms K=100 |
| E2 | 3-tier vs. binary routing comparison | MSR-VTT & DiDeMo, same setup | R@1, avg-K | 3-tier outperforms binary by +0.4 (MSR-VTT) and +0.9 (DiDeMo) | Medium tier (K=60) provides value | No analysis of why medium tier helps specifically |
| E3 | Ablation: alternative layer sets | MSR-VTT, binary routing, layers {18,24,27} vs. {20,24,27} | R@1, avg-K | Alternative layers perform slightly worse (52.0 vs. 52.8) | Method is somewhat sensitive to layer choice | Only one alternative set tested |
| E4 | Ablation: alternative disagreement metric (Kendall τ) | MSR-VTT, binary routing, Jaccard vs. Kendall τ | R@1, avg-K | Kendall τ (52.5) slightly worse than Jaccard (52.8) | Jaccard is a reasonable default | Only one alternative metric tested |
| E5 | Ablation: union pool variant | MSR-VTT, binary routing, rerank union of top-K across layers | R@1, avg-K | Union pool achieves 53.1 R@1 (close to 3-tier's 53.2) | Cross-layer diversity contributes to gains | Raises question of whether routing vs. diversification is the primary driver |
| E6 | Query distribution analysis | Both datasets, 3-tier routing | % easy/medium/hard queries | Consistent ~63%/32%/5% distribution across datasets | Threshold calibration generalizes | Distribution is by design (percentile-based), not an emergent property |

### (b) Research-Theme Gap Diagnosis

Three core research-value claims are weakly supported:
1. **New Knowledge (Causal Mechanism)**: The claim that selective reranking avoids "noise from deep candidates" is a key insight but lacks direct empirical support. Without reranker score distribution analysis or controlled ablation, the causal mechanism remains speculative.
2. **Reproducibility (Hyperparameter & Baseline Details)**: The top-m hyperparameter (m=20) lacks sensitivity analysis. The margin routing baseline lacks implementation specification. These gaps hinder independent reproduction.
3. **Impact on Practice (Generalization)**: Evaluation is limited to a single MLLM architecture (VideoLLaMA3-7B) and two benchmarks. Whether the disagreement signal transfers to other models or datasets is an open question.

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|--------------|------------|----------------|-------------------|---------|-------------------|---------------------|----------------------------|
| Variance & Statistical Reliability (P0) | Gains are stable across random seeds | Run all main experiments (E1) with 3-5 different random seeds; report mean±std | Fixed K=100, Margin Routing, 3-tier Routing | R@1, R@5, R@10, MnR, avg-K (±std) | std < 0.5 across seeds; p-value < 0.05 for 3-tier vs. margin | 1-2 days compute | Major validity improvement |
| Causal Mechanism: "Noise from Deep Candidates" (P0) | Reranker scores for deep candidates (rank >10) show wider variance or systematic bias | Plot reranker log-likelihood distributions for top-10 vs. top-11-100 candidates; compute score variance and mean shift | Reranker outputs on same candidate pool | Score variance, mean score, ranking error rate per rank bin | Deeper candidates show measurably higher score variance or error rate | 1 day analysis | Major defensibility improvement |
| Hyperparameter m Sensitivity (P1) | Disagreement signal is robust to reasonable m choices | Test m∈{5, 10, 20, 30} on MSR-VTT with 3-tier routing | Default m=20 as reference | R@1, R@5, avg-K | R@1 within 1.0 point across all m values | 1 day compute | Moderate reproducibility improvement |
| Generalization to Another MLLM (P2) | Cross-layer disagreement generalizes across MLLM architectures | Evaluate on LLaVA-7B or Qwen2.5-VL-7B using same routing protocol | VidVec baseline on new model | R@1, avg-K | Comparable efficiency-quality trade-off on new model | 3-5 days compute | Major generalization claim support |

### (d) Traceability

- Variance experiment → Weakness #3 (Missing variance) → Major validity risk
- Causal mechanism analysis → Weakness #2 (Unverified causal claim) → Major defensibility risk
- m-ablation → Weakness #4 (Hyperparameter gap) → Minor reproducibility risk
- Generalization experiment → Weakness #6 (Single-model evaluation) → Moderate generalization risk

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|---------------------|-----|------------|----------------------|
| C1 | Cross-layer ranking disagreement as a novel confidence signal for adaptive reranking, measuring Jaccard distance between top-k sets across transformer layers | [1], [3], [4], [5] | `partially_overlapping` | Cross-model disagreement [1] uses inter-model surprise for routing; CALM [4] and CATs [5] use layer-wise consistency for early exit. Residual novelty: intra-model cross-layer disagreement specifically for *retrieval reranking budget allocation* (not classification early exit). | High | Differentiate from cross-model approaches and clarify retrieval-specific novelty axis |
| C2 | 3-tier routing architecture mapping disagreement scores to K∈{10,60,100} for fine-grained allocation | [7] | `partially_overlapping` | Adaptive retrieval thresholds exist (e.g., pEBR [7] for probabilistic retrieval). Residual novelty: the specific 3-tier K-budget mapping driven by cross-layer disagreement rather than confidence thresholds. | Medium | Position as a practical design contribution rather than a conceptual breakthrough |
| C3 | Training-free method achieving +0.9/+1.5 R@1 over margin routing at ~70% compute reduction on MSR-VTT/DiDeMo | — | `supported` | No directly comparable prior paper reports this specific efficiency-quality trade-off for MLLM-based video-text retrieval routing under matched avg-K constraints. | Medium-High | Bound claims to tested settings (VideoLLaMA3-7B, MSR-VTT, DiDeMo); do not generalize beyond evaluated scope |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|----------------|-------------|----------------------|-------------------|-------------------------|-------------------|
| Root: Adaptive Computation for ML Models | Branch: Early Exit / Dynamic Depth | Leaf: Confidence-based early exit [4], [5], [6] | Layer-wise classifiers or consistency thresholds control exit depth | Those methods use layer outputs for classification early exit; this paper uses layer rankings for *reranking budget routing* in retrieval | Moderate overlap in mechanism (layer signals), different task setting |
| Root: Adaptive Computation for ML Models | Branch: Disagreement-based Routing | Leaf: Cross-model disagreement [1] | A second verifier model measures surprise/uncertainty | This paper uses *intra-model* cross-layer disagreement, avoiding second-model overhead | Moderate conceptual overlap; intra-model advantage is a clear differentiator |
| Root: Video-Text Retrieval | Branch: Multi-layer Feature Methods | Leaf: HVP-Net [3], VidVec [2] | Intermediate layers encode useful retrieval semantics | Those methods use multi-layer features for *representation enrichment*; this paper uses layer rankings for *routing decisions* | Low overlap in core purpose |
| Root: Adaptive Retrieval | Branch: Dynamic Threshold Methods | Leaf: pEBR [7], Adaptive Table Retrieval [8] | Query difficulty affects optimal retrieval depth | Those methods adapt retrieval size via probabilistic or threshold mechanisms; this paper uses cross-layer disagreement signal | Low overlap in signal design |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|-----------------|-------------------------|
| [1] Cross-Model Disagreement | LLM routing, general NLP tasks | Verifier model's perplexity/entropy as correctness signal | Using disagreement as a training-free routing signal for efficiency | Requires a second model; this paper is intra-model and zero-overhead | C1 must explicitly differentiate; does not invalidate core novelty |
| [2] VidVec | Video-text retrieval using MLLM intermediate layers | Layer-wise embedding extraction + MLLM head reranking | Same base retrieval pipeline; same model architecture | VidVec uses fixed K=100; this paper adds adaptive routing | This paper is a natural extension of VidVec; novelty is in the routing mechanism |
| [3] HVP-Net | Video-text retrieval with hierarchical features | Multi-layer feature extraction for representation enrichment | Using intermediate layer information for video retrieval | HVP-Net fuses features; this paper measures ranking disagreement | Different purpose; low direct overlap risk |
| [4] CALM | Adaptive LLM inference | Layer-wise representation consistency for per-token early exit | Using intra-model layer signals for adaptive computation | CALM targets token-level exit for generation; this paper targets query-level routing for retrieval | Different task; mechanism is similar but setting is distinct |
| [5] CATs | Adaptive Transformer inference | Conformal prediction for confident early exit | Training prediction heads on intermediate layers for exit | CATs adds training components; this paper is entirely training-free | Training-free nature is a clear advantage |
| [7] pEBR | Probabilistic embedding-based retrieval | Dynamic cosine threshold via conditional item distribution | Adapting retrieval size per query | Uses probabilistic modeling; this paper uses cross-layer disagreement | Different signal mechanism; complementary approaches |

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Adaptive Computation & Video-Text Retrieval (Root)
├── Branch 1: Early Exit / Dynamic Depth
│   ├── Leaf 1.1: Confidence-based exit [4][5][6]
│   │   └── Mechanism: layer-wise classifiers or consistency thresholds
│   └── Leaf 1.2: Conformal prediction exit [5]
│       └── Mechanism: statistical guarantees on exit consistency
├── Branch 2: Disagreement-based Routing
│   ├── Leaf 2.1: Cross-model disagreement [1]
│   │   └── Mechanism: verifier model surprise → routing decision
│   └── Leaf 2.2: Intra-model cross-layer disagreement [THIS PAPER]
│       └── Mechanism: Jaccard distance across layer rankings → K budget
├── Branch 3: Multi-layer Feature Methods for Video Retrieval
│   ├── Leaf 3.1: Representation enrichment [3]
│   │   └── Mechanism: fuse multi-layer features for better embeddings
│   └── Leaf 3.2: Layer-wise embedding extraction [2]
│       └── Mechanism: intermediate layers → retrieval + reranking
└── Branch 4: Adaptive Retrieval Thresholds
    ├── Leaf 4.1: Probabilistic dynamic thresholds [7]
    │   └── Mechanism: conditional item distribution → K per query
    └── Leaf 4.2: Adaptive table retrieval [8]
        └── Mechanism: threshold-based table selection per query
```

### Contribution-level Novelty Conclusion

**C1 (Cross-layer disagreement signal):** `partially_overlapping`. The concept of using disagreement as a routing signal overlaps with Cross-Model Disagreement [1], but the intra-model cross-layer approach for retrieval budget allocation is a genuine residual novelty. Repositioning: explicitly acknowledge Cross-Model Disagreement and differentiate on the zero-overhead, retrieval-specific axis.

**C2 (3-tier routing architecture):** `partially_overlapping`. Multi-tier adaptive allocation is a practical design contribution rather than a conceptual breakthrough. Repositioning: frame as an engineering contribution that unlocks the disagreement signal's value by avoiding the binary routing trap.

**C3 (Empirical results):** `supported`. The specific efficiency-quality trade-off (avg-K≈30 with +0.9/+1.5 R@1 over margin routing, 70% compute reduction) has no directly comparable prior report. Bound claims to tested settings.

## References
[1] Cross-Model Disagreement as a Label-Free Correctness Signal 2603.25450

[2] VidVec: Unlocking Video MLLM Embeddings for Video-Text Retrieval 2602.08099

[3] Delving Deeper: Hierarchical Visual Perception for Robust Video-Text Retrieval 2601.12768

[4] Confident Adaptive Language Modeling 2207.07061

[5] Consistent Accelerated Inference via Confident Adaptive Transformers 2104.08803

[6] Adaptive Neural Networks for Efficient Inference 1702.07811

[7] pEBR: A Probabilistic Approach to Embedding Based Retrieval 2410.19349

[8] Retrieve Only Relevant Tables Whether Few or Many: Adaptive Table Retrieval Method 2605.18766

## Scores
Final Score: 5.5/10

The paper presents a practical, training-free method for adaptive reranking budget allocation in video-text retrieval, with genuine efficiency gains (~70% compute reduction with competitive accuracy). The cross-layer disagreement signal is a sound intuition, and the 3-tier routing architecture provides meaningful granularity over binary schemes.

However, the score is held back by three major concerns:
1. **Novelty overlap**: The concept of disagreement-based routing is not fully novel (cross-model disagreement exists), and the manuscript does not acknowledge or differentiate this overlap, creating a credibility risk.
2. **Unverified causal claims**: The "noise from deep candidates" explanation for exceeding K=100 performance is presented as fact without empirical support, weakening scientific defensibility.
3. **Missing statistical rigor**: Results lack variance reporting (no multi-seed mean±std), making it impossible to assess whether the 0.9-1.5 point gains are statistically reliable.

The paper has solid practical value and a clear contribution axis. If the P0 revisions (variance reporting, causal hypothesis framing, related-work differentiation) are completed, the paper would be substantially stronger.

Post-Revision Target: [7, 8]/10

This interval assumes all P0 items are addressed: multi-seed variance is reported, the causal hypothesis is properly framed and partially supported by analysis, and the novelty positioning is strengthened through explicit related-work differentiation. The score would improve because the core empirical contribution (efficiency gains with training-free routing) remains valid and practically useful.