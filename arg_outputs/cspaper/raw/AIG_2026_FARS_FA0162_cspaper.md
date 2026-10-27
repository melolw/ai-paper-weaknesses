# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies training-free routing for inference-time sparse attention. Keys are clustered by spherical k-means into C buckets, and a router selects ℓ buckets per query to approximate full attention while saving compute/memory. The authors first test a “gauge-coupled whitening” transform that aligns second moments between queries and keys while preserving dot products (Equation 2 and Equation 3), finding no gain over symmetric k-means routing. Motivated by this, they propose GWR Linear: compute a closed-form ordinary least squares predictor (Equation 5) that maps queries to per-bucket attention mass estimates, then route to the top-ℓ predicted buckets. On Qwen2.5-7B with 32k contexts and C=1024 buckets, they report Recall@32 improvements over symmetric k-means and partial gap closure toward a learned 2-layer MLP router.

## Summary Of Strengths
- Clear problem formulation and metric: The paper defines bucket-level attention mass and recall@ℓ cleanly (Equation 1), aligning with prior inference-time sparse attention work.
- Simple, closed-form method: GWR Linear reduces routing to a single regularized least-squares solve (Equation 5). The design is easy to implement and incurs no extra inference-time cost relative to centroid-similarity routing.
- Insightful negative result: The gauge-coupled whitening construction (Equations 2–3) and its failure to improve routing are interesting and useful to practitioners who might otherwise attempt distribution alignment.
- Empirical gains over strong training-free baseline: Table 1 shows a sizable improvement of GWR Linear over symmetric k-means (0.726 vs 0.513 Recall@32) at fixed selectivity, with CIs reported.
- Analysis across budgets and heads:
  - Figure 2a shows consistent gains across routing budgets, and Figure 2b indicates monotonic growth in “gap closure” up to ~80% for ℓ=128.
  - Table 2 and Figure 3 demonstrate improvements across multiple heads and layers, with large gap-closure variability highlighted and discussed.
- Exposition is mostly clear: Figure 1 provides a helpful end-to-end diagram contrasting symmetric k-means, the learned Saap-MLP router, and the proposed OLS-based router.

## Summary Of Weaknesses
1) Limited evaluation scope and external validity
- Only one model family is evaluated (Qwen2.5-7B) and most detailed numbers are for a single head (Layer 14, Head 0) and one budget (ℓ=32) in the main table. Although Table 2 samples 6 heads and Figure 2 sweeps ℓ, the study remains narrow: one backbone, one dataset type (PG19), one clustering configuration (C=1024) and one head dimension (d_h=128). This restricts claims of generality to broader LLMs and tasks.
- No downstream task or end-to-end metrics are reported. The core claim is stronger routing quality, yet there are no perplexity, accuracy, or generation quality results under sparse attention, nor any speedup or wall-clock measurements to demonstrate practical impact.

2) Calibration data, data splits, and possible leakage
- Section 4.1 states ~134k long-range queries are used; however, it is not specified how calibration examples for computing W (Equation 5) are separated from evaluation examples. If the same passages or similar context segments contribute to both Q^TQ/Q^TY and testing, this may inflate reported recall. Please clarify the exact split between calibration and evaluation, number of calibration samples n, and how different heads use or share calibration data.

3) Incomplete baselines for training-free sparse attention
- The comparisons exclude several closely related training-free or minimally trained sparse-attention methods that also target token/bucket selection quality and report recall or equivalent metrics. The absence of those limits the positioning of GWR Linear (see “Potentially Missing Related Work” for concrete items). Claims like “first to achieve substantial gap closure via a closed-form approach” are hard to assess without these baselines.

4) Metric-only evidence without compute/latency accounting
- While recall@ℓ is a standard proxy, practitioners care about speed-memory trade-offs. Table 1 reports selectivity but provides no timing. Figure 2 shows recall vs. ℓ, but not throughput. The paper should include actual decode-time speedups against exact attention and against symmetric k-means/learned routers under an identical implementation.

5) Statistical reporting and variance
- Table 1 shows Saap-MLP with “±0.000,” which is implausible under typical sampling unless it is a single run or averaged over deterministic batches; please clarify how CIs are computed and why they are zero. For other entries, it would be valuable to report the number of runs, bootstrap details, and whether contexts/heads are re-sampled.
- Figure 2a lacks confidence intervals or error bands, which would be important to assess monotonicity claims and separation between methods across budgets.

6) Practicality of calibration and storage
- Equation 5 requires Y = A H_k, i.e., constructing full attention to collect bucket-level masses for calibration. The paper calls it “seconds on a single CPU” for typical sizes (Section 3.5), which seems optimistic, especially when n≈1e5, C=1024, and d_h=128. Please detail the exact implementation, batch sizes, and hardware used. Also quantify the per-model storage of W per head (d_h×C) for all layers and the total memory budget relative to KV cache savings.
- How frequently does W need to be recomputed across domains or prompts? If it is per-head and per-corpus, what is the sensitivity to domain shift?

7) Missing or minimal ablations
- No sensitivity study on the regularization ε in Equation 5, nor on the number of calibration samples n and the effect on recall. Similarly, no analysis of bucket count C and clustering quality (e.g., using different seeds, numbers of k-means iterations, or alternative partitioners) is included.
- There is no ablation on using projected queries (e.g., PCA/ZCA of Q before OLS) or simple ridge/lasso variants that might improve stability. Section 3.4 asserts OLS suffices, but the negative geometric result does not preclude that other lightweight modeling choices could matter.

8) Interpretation of the geometric negative result
- The failure of moment matching is interesting, but Section 3.3 stops at second moments. If the thesis is that “attention mass prediction matters, not distribution alignment,” an experiment controlling for higher-order moments or local structure could strengthen the argument. For instance, what happens if OLS is trained on features derived from closest centroids or cross-moments, testing whether the signal is predominantly linear in q?

9) Reproducibility details
- Clustering settings are under-specified: number of k-means restarts, max iterations, convergence tolerance, and whether centroids are updated per layer/head or shared. 
- The pre-processing pipeline “de-RoPE for routing but RoPE for attention weights” (Section 4.1) warrants more precise documentation to avoid mismatch and ensure replicability by others.

10) Figure- and table-specific observations
- Figure 1: The pipeline diagram is clear and supports the claim that the proposed method is training-free with closed-form W, but it would help to annotate where calibration cost occurs (computing Y = A H_k), since that step effectively runs full attention offline.
- Figure 2: Panels (a) and (b) substantiate the monotone improvement with budget and growing gap closure. However, the absence of uncertainty bands hinders interpretation about the robustness of trends, especially at small ℓ where variance is typically larger.
- Table 1: The main result table is the primary evidence. Given that “Whitening-Only” is so weak (0.25 recall), it validates the point in Section 4.3 that dot-product preservation is crucial, lending credibility to the protective role of the gauge coupling. Still, please confirm whether Whitening-Only also uses the same C=1024 partition and whether RoPE handling is identical across conditions.
- Table 2 and Figure 3: These clearly show large between-head variability. It would be valuable to analyze correlates (e.g., head sparsity, distance preference) to predict where linear routing excels.

Overall, the core idea is appealing and the empirical gains over symmetric k-means are meaningful, but the study is not yet broad or rigorous enough for the main track. With added baselines, stronger experimental breadth, clear calibration/evaluation splits, and end-to-end speedups, this could become a solid empirical contribution.

## Potentially Missing Related Work
1) Zhang et al., “SpargeAttention: Accurate and Training-free Sparse Attention Accelerating Any Model Inference,” 2025 — proposes a training-free mechanism that predicts and filters attention maps online to skip matmuls. Directly relevant to training-free routing quality and should be compared to in Section 2 and experimentally if possible; cite near the discussion of training-free methods and contrast in Section 4.2.

2) Yang et al., “Less Is More: Fast and Accurate Reasoning with Cross-Head Unified Sparse Attention,” 2025 — a training-free cross-head token-importance strategy. Discuss in Related Work (Section 2) and contrast its global cross-head routing to per-head bucket mass prediction; mention in conclusions as complementary.

3) Luo et al., “Attention Sparsity is Input-Stable: Training-Free Sparse Attention for Video Generation via Offline Sparsity Profiling and Online QK Co-Clustering,” 2026 — shows training-free sparse routing via offline profiling and online co-clustering, reporting recall vs. speedup. Should be discussed in Section 2 and used as a conceptual comparator to your coarser bucket selection.

4) Sun et al., “You Only Index Once: Cross-Layer Sparse Attention with Shared Routing,” 2026 — introduces a shared routing index reused across layers, amortizing routing overhead. Relevant to Section 3.5 on complexity and to broader routing design; cite in Related Work and discuss potential integration with GWR Linear.

5) Ahmad et al., “SpotAttention: Plug-In Block-Sparse Routing for Pretrained Long-Context Transformers,” 2026 — learned selector estimating attention distributions via distillation for top-K keys. Compare as a strong learned baseline in Section 2 and position your training-free OLS approach relative to its learned selection.

6) Taylor et al., “Directional Routing in Transformers,” 2026 — not training-free, but focuses on routing as a dominant computational pathway. Useful for contextualizing what linear OLS aims to approximate; cite in Related Work for a broader routing perspective.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Calibration/evaluation protocol: Specify the exact calibration set size n, how it is disjoint from evaluation, and whether you perform any domain or prompt holdout. If calibration equals evaluation, please re-run with a proper split and report generalization.
- End-to-end speedups: Provide wall-clock decoding throughput and memory usage under identical kernels for symmetric k-means, GWR Linear, and Saap-MLP at several ℓ values, on a common GPU. Report speed/quality trade-offs to substantiate the practical impact.
- Baselines: Add or at least discuss modern training-free and lightweight-routing baselines listed above, and explain conceptual differences. If experiments cannot include all, select at least one representative approach to benchmark recall and, if feasible, task metrics.
- Ablations: 
  - Vary ε in Equation 5 and report stability/recall; show how recall scales with calibration size n.
  - Vary C and show the effect on recall and compute; include different k-means init seeds and iteration budgets. 
  - Test a simple ridge or lasso regularization and possibly a PCA+OLS variant to probe whether modest feature engineering helps.
- Broaden evaluation: Beyond PG19, include a code or math-heavy long-context set (e.g., Code or GovReport/BookSum long passages) and at least one reasoning-oriented setting to check robustness.
- Statistical reporting: Provide the number of runs, confidence interval computation details, and add uncertainty bands to Figure 2. Clarify the “±0.000” in Table 1 for Saap-MLP.
- Memory footprint: Quantify total storage for W across all heads (28 layers × 28 heads × 128×1024 parameters) and discuss compression (e.g., low-rank W) if needed.
- Interpretability: Analyze why some heads favor linear routing (e.g., head sparsity, attention distance distribution). Consider correlating head-level improvements with structural properties.

Typos and minor issues:
- Page 1, Abstract: “achieves 72.6% attention-mass recall@32” — consider including the head/layer context here for precision.
- Table 2 caption: “Mean: 69.8%” — specify whether this mean is simple average across heads or weighted by tokens.
- Section 4.3: “50.7% ≈ 51.3%” — fine as text, but adding CIs here would strengthen the claim of no improvement.

Criteria to change my evaluation:
- Add strong end-to-end results (speedup vs. accuracy/perplexity) demonstrating practical gains beyond recall.
- Provide a rigorous calibration/evaluation split with clear generalization across prompts/domains and show sensitivity/ablation studies.
- Include at least one additional modern training-free baseline and, if feasible, a learned non-MLP router, to contextualize the claimed “gap closure.”

## Confidence
3: Reasonably confident but not fully verified — I verified the main equations and read figures/tables carefully, but broader novelty and empirical coverage could still affect conclusions.

## Soundness
3: Acceptable — The method is technically sound and the negative result is interesting, but the evaluation breadth, calibration protocol clarity, and lack of end-to-end metrics limit the strength of evidence.

## Excitement
2.5: Between potentially interesting and interesting — A clean, closed-form take on routing with nice empirical gains over symmetric k-means, but the study feels preliminary without practical speed/accuracy results and broader baselines.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The closed-form OLS router is a neat idea with encouraging recall gains and a useful negative result on moment matching. However, the experimental scope is narrow, calibration/evaluation splits are unclear, several closely related training-free baselines are missing, and there are no end-to-end speed or task-quality measurements. With the suggested additions and clarifications, this work could become a solid Findings paper and possibly main-track material later.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper does not include a dedicated limitations or impact discussion. It should add:
  - Limitations: dependence on full-attention calibration to compute Y; per-head W storage; sensitivity to bucketization and domain shift; lack of non-linear modeling for complex heads; evaluation limited to one model family and one dataset type.
  - Societal impact: sparse attention can reduce energy and cost for long-context inference, improving accessibility; conversely, speedups may increase model deployment scale and associated environmental footprint. Consider bias propagation if routing under-selects minority or rare-content tokens; routing errors could disproportionately harm minority dialects or domain-specific jargon in long documents.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Equations and setup are described, but several critical details are missing (calibration split, clustering hyperparameters, timing setup), and end-to-end results are absent.

## Datasets
1 No usable datasets submitted.

## Software
2 Documentary.: The method is straightforward to implement and the paper implies code availability, but the paper itself does not provide all necessary experimental details for plug-and-play replication without further clarification.