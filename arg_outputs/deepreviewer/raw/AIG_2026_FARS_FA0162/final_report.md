## Summary
This paper proposes GWR Linear, a training-free approach to sparse attention routing that predicts bucket-level attention mass via closed-form ordinary least squares (OLS) regression. The method achieves 72.6% attention-mass recall@32 on Qwen2.5-7B, closing 63.6% of the gap between symmetric k-means (51.3%) and a learned MLP router (84.8%). The paper also reports a negative result: gauge-coupled whitening (geometric moment matching) provides no improvement over symmetric k-means, leading to the insight that routing depends on attention-mass prediction rather than distribution alignment.

**Core contribution claims:** (1) Negative result on geometric moment matching, revealing distribution alignment is not the right objective for routing. (2) GWR Linear achieves substantial gap closure to learned routing via closed-form OLS. (3) GWR Linear generalizes across budgets and heads.

**Key concerns:** The novelty positioning requires tighter differentiation against Expected Attention (Devoto et al., 2025), which also uses closed-form attention scoring training-free. The experimental setup lacks explicit calibration/evaluation split protocol, raising data leakage risk. The multi-head generalization uses 6 selected heads without stated selection criteria. The causal claim that "routing depends on attention-mass prediction" is over-strong given the limited scope of tested methods. No downstream task evaluation is reported—recall@ℓ is a proxy metric, not an end-to-end LM performance measure.

## Strengths
1. **Clear and clean technical method:** The OLS-based routing approach (GWR Linear) is mathematically simple and elegant. The closed-form solution W* = (QᵀQ + εI)^{-1}QᵀY is a single matrix solve with no iterative optimization, which directly addresses the deployment barrier of per-head training in learned routers.

2. **Valuable negative result:** The finding that gauge-coupled whitening provides no improvement over symmetric k-means is a useful negative result that challenges the common assumption that query-key distribution alignment is the right objective for routing. This insight can guide future sparse attention research away from distribution-matching approaches.

3. **Well-structured experiments:** The budget sweep (ℓ = 4 to 128) and multi-head evaluation provide useful ablation evidence. The consistent improvement over symmetric k-means across all tested budgets and heads strengthens the core claim.

4. **Reproducible calibration:** The method requires only one-time calibration with full attention computation, which takes seconds on a single CPU for typical settings. This is a practical advantage over learned routers that require per-head training.

5. **Honest gap reporting:** The paper clearly reports the remaining 12.2 percentage point gap to the learned MLP router, avoiding the common pitfall of overstating training-free performance.

## Weaknesses
1. **Novelty overlap with prior closed-form training-free methods (Major, Research-Value Impact):** Expected Attention (Devoto et al., 2025) already demonstrates closed-form attention scoring for KV cache compression training-free. Both methods use calibration data and closed-form statistics without iterative training. The manuscript does not currently differentiate GWR Linear's routing objective from Expected Attention's pruning objective, making the contribution appear partially overlapping. Fixability: High—add explicit differentiation sentence.

2. **Missing calibration/evaluation split protocol (Major, Validity Risk):** The experimental setup does not state whether calibration data is disjoint from evaluation data. If the OLS predictor is calibrated on the same data used for evaluation, the recall results could be inflated by data leakage. Additionally, Saap-MLP reports zero variance (±0.000), making the "non-overlapping confidence intervals" claim unverifiable. Fixability: Medium—requires clarifying the data split and re-running if needed.

3. **Multi-head selection criteria unstated (Major, Generalization Risk):** The 6 attention heads evaluated (L2-H0, L7-H0, L14-H0, L14-H14, L21-H0, L26-H0) are selected without criteria. If these heads were chosen to show strong improvement, the generalization claim is weakened. Fixability: High—state selection protocol or expand evaluation to more heads.

4. **No downstream task evaluation (Major, Research-Value Impact):** Recall@ℓ is a proxy metric that measures how much attention mass is captured by selected buckets. The manuscript does not report downstream task performance (e.g., perplexity, benchmark accuracy) to validate that improved recall translates to improved generation quality. Fixability: Medium—requires running at least one downstream benchmark.

5. **Causal claim overreach (Minor, Objectivity):** The claim that "routing quality depends on predicting attention mass, not on distribution alignment" is based on a single comparison (one alignment method vs. one prediction method). Alternative alignment methods (optimal transport, higher-order moment matching) and other prediction paradigms are not explored. Fixability: High—soften causal language.

6. **Budget sweep ceiling effects not controlled (Minor, Interpretation):** The interpretation that "linear structure dominates at higher sparsity levels" ignores that ceiling effects compress performance ranges at high budgets. All methods approach their limits, making gaps appear smaller. Fixability: High—add caveat or normalized metric.

7. **Conclusion lacks limitations (Minor, Completeness):** The conclusion does not mention key limitations: single model evaluation (Qwen2.5-7B), single dataset (PG19), proxy-only metric (recall@ℓ), and calibration data requirement. Fixability: High—add limitations paragraph.

## Key Issues
**Issue 1: Novelty Differentiation Against Expected Attention (Page 1 - Abstract)**
The abstract and introduction claim GWR Linear as a novel training-free closed-form approach for predicting attention mass. However, Expected Attention (Devoto et al., 2025) already demonstrates that closed-form expected attention scores can be computed training-free by leveraging the distributional properties of LLM activations. Both methods operate without iterative training and use calibration data with closed-form statistics. The manuscript does not differentiate GWR Linear's per-bucket routing objective from Expected Attention's per-KV-pair pruning objective.

**Issue 2: Calibration/Evaluation Data Leakage Risk (Page 5 - Experimental Setup)**
The setup does not state whether calibration data (queries and their true attention weights) is disjoint from evaluation data. If the OLS predictor is trained and evaluated on overlapping data, recall results are inflated. Additionally, Table 1 reports Saap-MLP variance as ±0.000, making the "non-overlapping confidence intervals" claim unverifiable.

**Issue 3: Cherry-Picking Risk in Multi-Head Evaluation (Page 6 - Multi-Head Generalization)**
The 6 attention heads are selected without stated criteria. If these heads were chosen to demonstrate strong improvement, the generalization claim is weakened. A more representative evaluation would report mean results across all heads in sampled layers or explicitly state the selection protocol.

## Actionable Suggestions
1. **Differentiate GWR Linear from Expected Attention in Abstract and Introduction:**
Add 1-2 sentences explicitly distinguishing GWR Linear's per-bucket routing objective from Expected Attention's per-KV-pair pruning objective. Expected Attention computes importance scores for tokens to decide which KV pairs to drop; GWR Linear regresses from query embeddings to bucket-level attention distributions to decide which buckets a query should attend to. These are complementary (pruning vs. routing), and clarifying this elevates the novelty perception.

2. **State Calibration/Evaluation Split Protocol Explicitly:**
In Section 4.1, add one sentence stating whether calibration data (queries and attention weights) is disjoint from evaluation data. If they overlap, re-run the evaluation with a strict split (e.g., calibrate on 4 prompts, evaluate on 2) to rule out data leakage.

3. **Clarify Saap-MLP Variance Reporting:**
Table 1 reports Saap-MLP variance as ±0.000. Clarify if this is a single-run value or a deterministic outcome. If single-run, report the mean ± std over ≥3 seeds to make the "non-overlapping confidence intervals" claim in Section 4.2 verifiable.

4. **State Head Selection Criteria in Multi-Head Evaluation:**
In Section 4.5, add one sentence stating how the 6 attention heads were chosen (e.g., "We sampled one head from each of layers 2, 7, 14, 21, 26"). If these were cherry-picked, acknowledge this limitation and consider expanding the evaluation to more heads.

5. **Soften Causal Claims About Routing Dependencies:**
Replace definitive causal language ("routing quality depends on predicting attention mass, not on distribution alignment") with evidence-consistent wording ("routing quality is consistent with depending on attention-mass prediction; second-moment alignment does not improve routing in our setting"). This bounds the claim to the tested methods.

6. **Add a Limitations Paragraph in the Conclusion:**
List key limitations explicitly: single model (Qwen2.5-7B), single dataset (PG19), proxy-only metric (recall@ℓ without downstream task validation), and calibration data requirement. This improves transparency and guides future work.

7. **Add a Normalized Metric in the Budget Sweep Analysis:**
When interpreting the budget sweep, acknowledge that ceiling effects may compress performance ranges at high ℓ. Consider adding a rank correlation (e.g., Spearman's ρ) between predicted and true bucket masses as a budget-invariant quality measure.

8. **Clarify OLS Numerical Properties:**
In Section 3.4, mention that OLS predictions may be negative for some buckets, but since routing uses top-ℓ score ranking, the ordering is preserved and negative values do not affect selection. State the exact regularization constant ε used (e.g., ε = 1e-6).

## Storyline Options + Writing Outlines
### Abstract Outline (complete: S1-S5)

| Sentence | Role | Key Claim | Evidence Anchor |
|----------|------|-----------|-----------------|
| S1 | Problem & Domain | Sparse attention routing reduces KV cache access but learned routers require per-head training. | Introduction, Section 3.1 |
| S2 | Significance / Challenge | Training-free alternatives like symmetric k-means achieve limited quality; can we close the gap without training? | Introduction paragraph 2 |
| S3 | Prior Gap / Insight | Geometric moment matching provides no improvement, revealing that distribution alignment is disconnected from attention-mass prediction. | Section 3.3, Table 1 |
| S4 | Proposed Method | GWR Linear predicts bucket-level attention mass via closed-form OLS regression from query embeddings. | Section 3.4, Eq. (5) |
| S5 | Key Result & Bounded Implication | Achieves 72.6% recall@32 on Qwen2.5-7B (63.6% gap closure), generalizing across budgets and heads; differentiation from Expected Attention (pruning vs routing) should be stated. | Table 1, Table 2, Section 4.4-4.5 |

**Drafting note for S5:** Add one phrase distinguishing GWR Linear from prior closed-form KV importance methods: "Unlike prior closed-form KV importance estimators that score individual tokens for pruning, GWR Linear regresses from query embeddings to bucket-level attention distributions, enabling query-dependent routing without training."

### Introduction Outline (complete: P1-P5)

| Paragraph | Role | Target Claim | Transition Logic | Required Evidence |
|-----------|------|-------------|-----------------|-------------------|
| P1 | Big Picture | Long-context inference faces KV cache memory bandwidth bottlenecks, not just FLOP costs. | Connects to sparse attention as solution. | FlashAttention reference; clarify memory-access bottleneck |
| P2 | Problem Context -> Gap | Sparse attention routing is the key challenge; learned routers are high-quality but require training; symmetric k-means is simple but limited. | Foreshadow that distribution mismatch may not be the root cause. | Saap reference; add foreshadowing sentence |
| P3 | Negative Result -> Insight | Gauge-coupled whitening provides no improvement over symmetric k-means, suggesting alignment is not the right objective. | Leads to OLS prediction as alternative. | Table 1 GWR Geometric result; soften causal claim |
| P4 | Solution Proposal | GWR Linear uses closed-form OLS to predict bucket-level attention mass from query embeddings. | Preview empirical results. | Section 3.4; add calibration data requirement sentence |
| P5 | Contribution Summary | Three contributions: (1) negative result on alignment, (2) GWR Linear with 63.6% gap closure, (3) generalization across budgets and heads. | Clear enumerated contributions. | Table 1, Figure 2, Table 2 |

**Revised Introduction Narrative:** Big Picture (KV cache memory bottleneck) -> Gap (routing quality gap between learned and training-free) -> Negative Insight (alignment fails) -> Solution (OLS prediction) -> Evidence Preview (72.6% recall, 63.6% gap closure) -> Contributions (enumerated).

## Priority Revision Plan
| Priority | Item | Root Cause | Recommended Fix | Expected Benefit | Effort |
|----------|------|------------|-----------------|------------------|--------|
| P0 | Novelty differentiation from Expected Attention | Abstract/intro do not distinguish routing objective from pruning objective | Add 1-2 sentences in abstract and intro explicitly differentiating GWR Linear's per-bucket routing from Expected Attention's per-KV-pair pruning | Novelty claim becomes defensible; reviewers see clear positioning | Low |
| P0 | Calibration/evaluation split protocol | Potential data leakage if OLS is trained and evaluated on overlapping data | State split explicitly (e.g., calibrate on 4 prompts, evaluate on 2); re-run if overlap exists | Eliminates validity risk; recall results become trustworthy | Medium |
| P0 | Head selection criteria unstated | 6 heads selected without stated protocol; cherry-picking risk | State selection criteria in Section 4.5; consider expanding to all heads in 2-3 layers | Generalization claim becomes credible | Low-Medium |
| P1 | Saap-MLP variance reporting | Table 1 shows ±0.000; "non-overlapping CI" claim unverifiable | Report mean±std over ≥3 seeds for Saap-MLP | Main result interpretation becomes verifiable | Medium |
| P1 | Causal claim softening | "Routing depends on X" is over-strong for single-method comparison | Replace with "is consistent with depending on X" throughout abstract/intro/conclusion | Objectivity improves; reduces reviewer pushback | Low |
| P1 | Limitations paragraph in Conclusion | Conclusion lacks any limitations discussion | Add 2-3 sentences listing key limitations (single model, single dataset, proxy metric) | Transparency improves; future work guidance clearer | Low |
| P2 | Downstream task evaluation | Recall@ℓ is a proxy; no end-to-end LM performance reported | Run at least one standard benchmark (e.g., Needle-in-a-Haystack or LongBench) with sparse routing enabled | Research value significantly strengthened | High |
| P2 | OLS numerical properties | Negative predictions and ε value not discussed | Add one sentence clarifying that negative values don't affect ranking and state ε used | Reproducibility improves | Low |

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|--------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | Main comparison: GWR Linear vs baselines at ℓ=32 | Qwen2.5-7B, L14-H0, PG19 (6 prompts, 32K ctx), vs Random/Sym-KMeans/GWR-Geom/Saap-MLP/Whitening-Only | Recall@32, Selectivity@32, Gap Closure | GWR Linear: 72.6% recall, 63.6% gap closure | C2 (performance) | No calibration/eval split stated; Saap-MLP variance ±0.000 |
| E2 | Budget sweep: ℓ=4,8,16,32,64,128 | Same setup as E1, varying ℓ | Recall@ℓ, Gap Closure | Gap closure increases 44.3%→80.3% | C3 (generalization) | Ceiling effects not controlled |
| E3 | Multi-head evaluation: 6 heads | L2-H0, L7-H0, L14-H0, L14-H14, L21-H0, L26-H0 | Recall@32 per head, Gap Closure | Mean 69.8% gap closure (28.8%–92.1%) | C3 (generalization) | Head selection criteria unstated |
| E4 | Ablation: Whitening-Only vs GWR Geometric | Independent ZCA whitening without dot-product preservation | Recall@32 | Whitening-Only: 25.0% (vs 50.7% GWR Geom) | C1 (negative result context) | Confirms dot-product preservation is protective |

### (b) Research-Theme Gap Diagnosis

The core research-value claims are: (1) distribution alignment is not the right objective for routing, (2) linear attention-mass prediction is a viable training-free approach, and (3) GWR Linear generalizes across budgets and heads. These are weakly supported by: no downstream task validation (recall is a proxy metric), single-model evaluation (Qwen2.5-7B only), and limited head coverage (6 of 784 heads). The reproducibility claim is also weak due to missing calibration/evaluation split protocol.

### (c) Proposed Research Experiments (P0/P1/P2)

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|-------------|------------|----------------|-------------------|---------|-------------------|----------------|---------------|
| C2 (Performance) | GWR Linear performance holds under strict calibration/eval split | Split PG19 prompts: calibrate on 4, evaluate on 2 | Same baselines, re-run with split | Recall@32, Gap Closure | Gap closure > 50% after split | Low (1-2 hrs) | Eliminates data leakage risk |
| C2 (Performance) | Learned MLP advantage is due to non-linearity, not capacity/optimization | Train linear model iteratively via SGD on same calibration data | Iterative linear vs closed-form OLS | Recall@32 | If iterative linear ≈ OLS, gap is non-linearity | Medium (4-8 hrs) | Isolates non-linearity claim |
| C3 (Generalization) | GWR Linear generalizes to other models | Evaluate on Llama-3-8B or Mistral-7B with same protocol | Sym-KMeans, Saap-MLP | Recall@32 per model | Gap closure > 50% on 2+ models | Medium (8-16 hrs) | Strengthens generalization claim |
| C2 (Research Value) | Improved recall translates to downstream performance | Evaluate on Needle-in-a-Haystack or LongBench with GWR Linear routing enabled | Full attention, Sym-KMeans sparse routing | NIAH accuracy / LongBench score | No degradation vs full attention | High (1-2 days) | Validates end-to-end utility |

### (d) Traceability

E1 → C2: Main performance claim. P0 split experiment closes leakage risk.
E2 → C3: Budget generalization. Ceiling effect caveat improves interpretation.
E3 → C3: Head generalization. P0 head selection protocol + P1 cross-model eval strengthens claim.
Missing → C2 research value: Downstream task experiment (P2) closes proxy-metric gap.

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|-------------------|-----|------------|----------------------|
| C1 | Geometric moment matching provides no improvement over symmetric k-means | — | partially_overlapping | Insight is novel but based on a single alignment method (ZCA whitening); broader negative result not established. | High | Frame as "evidence against second-moment alignment" rather than a general negative result. |
| C2 | GWR Linear achieves 63.6% gap closure to learned routing via closed-form OLS | [1] | partially_overlapping | Expected Attention [1] already demonstrates closed-form training-free attention scoring; GWR Linear's routing objective is complementary but shares the same training-free closed-form paradigm. | High | Explicitly differentiate per-bucket routing from per-KV-pair pruning in abstract and intro. |
| C3 | GWR Linear generalizes across budgets and heads | [2] | supported | Generalization across budgets (44-80% gap closure) and 6 heads is well-demonstrated within the tested scope. | Medium | State head selection criteria; evaluate on additional models for stronger claim. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|----------------|------------|--------------------------|-------------------|------------------------|-------------------|
| Root: Efficient Attention | Branch: Sparse Attention Routing | [2], [3] | Learned or heuristic routing | [2] uses trained MLP; this paper uses closed-form OLS | Low (complementary) |
| Root: Efficient Attention | Branch: KV Cache Compression | [1], [4], [5] | Score-based pruning | [1] computes closed-form expected attention for pruning; this paper uses OLS for routing | Medium (overlap in closed-form training-free paradigm) |
| Root: Efficient Attention | Branch: Linear Attention Approximation | — | Kernel/random feature maps | These approximate full attention; this paper selects sparse subsets | Low (different paradigm) |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|----------|----------------|-------------|------------------------|------------------|-------------------------|
| [1] | KV cache compression for LLMs | Closed-form expected attention scores from future query distributions | Training-free closed-form attention scoring | [1] scores individual KV pairs for pruning; GWR Linear scores buckets for query routing | Partially overlapping C2; requires explicit differentiation |
| [2] | Inference-time sparse attention routing | Learned asymmetric query classifier (Saap-MLP) | Same routing objective (bucket selection) | [2] requires per-head training; GWR Linear is closed-form | Complementary; Saap is the learned baseline |
| [3] | Training-free sparse attention trade-offs | Comparative evaluation of multiple training-free methods | Evaluation protocol similarity | [3] evaluates existing methods; GWR Linear proposes a new method | Low impact; complementary context |

**Contribution-level Novelty Conclusion:** C1 is `partially_overlapping`—the negative result is a useful insight but limited to second-moment alignment. C2 is `partially_overlapping`—the closed-form training-free paradigm overlaps with Expected Attention [1], though the routing objective is distinct from pruning. C3 is `supported` within the tested scope but requires head selection protocol clarification and cross-model evaluation for stronger claims.

## References
[1] Expected Attention: KV Cache Compression by Estimating Attention from Future Queries Distribution 2510.00636

[2] Inference-time sparse attention with asymmetric indexing 2502.08246

[3] The Sparse Frontier: Sparse Attention Trade-offs in Transformer LLMs 2504.17768

[4] H2O: Heavy-hitter oracle for efficient generative inference of large language models 2306.14048

[5] StreamingLLM: Efficient streaming language models with attention sinks 2309.17453

## Scores
**Final Score: 5.5/10**

The paper presents a clean and simple method (GWR Linear) with a valuable negative result on geometric alignment. The closed-form OLS approach is elegant and practically appealing. However, the novelty positioning requires tightening against Expected Attention [1], the experimental setup has data leakage risk due to unstated calibration/evaluation splits, and the absence of downstream task evaluation limits the research value assessment. The multi-head generalization claim is also weakened by unstated head selection criteria. These issues are fixable, and with the P0 revisions (novelty differentiation, data split protocol, head selection criteria), the paper would become substantially stronger.

**Post-Revision Target: [6.5, 8.0]/10**

If the P0 issues are fully addressed (novelty differentiation from Expected Attention, strict calibration/evaluation split with no data leakage, head selection protocol stated, causal claims softened), the score would rise to 6.5-7.0. If additionally downstream task evaluation is added (P2, demonstrating that improved recall translates to actual generation quality), the score could reach 7.5-8.0. The core method is sound and the insight is useful; the main gaps are in experimental rigor and novelty positioning, both of which are fixable with moderate effort.