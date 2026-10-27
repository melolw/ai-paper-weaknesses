# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies adaptive compute allocation in two-stage video–text retrieval. In a retrieve-then-rerank setup using a VideoLLaMA3-7B backbone and a VidVec-style EOL prompting recipe, the authors propose to estimate per-query difficulty by measuring cross-layer ranking disagreement. Concretely, they compute the Jaccard distance between the top-m candidate sets produced by intermediate layers (anchor layer 24 vs. layers 20 and 27), and map the resulting score to one of three reranking budgets K ∈ {10, 60, 100}. The method is training-free and aims to cut reranking compute while retaining or improving quality. On MSR-VTT 1k-A and DiDeMo, the proposed 3-tier routing reportedly improves R@1 over a margin-based routing baseline at a matched average budget near 30, and on MSR-VTT even slightly surpasses fixed K=100 R@1 while using about 70% fewer reranker passes.

## Summary Of Strengths
- Conceptual clarity and simplicity: Using cross-layer agreement as a confidence proxy is intuitive and leverages widely observed phenomena about intermediate layers encoding strong signals. The formulation in Equation (1) is clear and easy to implement.
- Training-free and model-agnostic pitch: The routing relies only on scores from a few intermediate layers and simple set-similarity computations, which can be appealing for practitioners.
- Three-tier routing design: The explicit use of a middle tier (K=60) is a practical refinement over binary routing, and the paper motivates it convincingly.
- Empirical benefits at matched cost: Table 1 shows consistent R@1 gains over margin-based routing on MSR-VTT (+0.9) and DiDeMo (+1.5) at similar avg-K, suggesting the signal is meaningful.
- Robustness hints: Table 2 ablations show the disagreement signal remains competitive under layer swaps and with Kendall τ in place of Jaccard; the “Union pool” variant even improves coverage.
- Figure 1 effectively communicates the end-to-end pipeline, emphasizing how disagreement funnels queries into the 3-tier budget; the legend and the easy/medium/hard decomposition help readers understand the routing logic.

## Summary Of Weaknesses
1) Limited experimental scope and missing key baselines  
- Only two benchmarks (MSR-VTT and DiDeMo) and a single model family (VideoLLaMA3-7B) are tested. For a claims space that touches efficient retrieval and adaptive reranking, broader coverage is expected.  
- Several state-of-the-art two-stage rerankers and query-adaptive retrieval approaches are absent as baselines, despite being directly relevant to the proposed compute–quality tradeoff. See “Potentially Missing Related Work” for concrete items that should be compared or at least discussed. The lack of these comparisons weakens claims that disagreement routing is an overall superior signal for adaptive compute across modern reranking regimes.

2) Over-interpretation of surpassing full reranking  
- The claim “Exceeds full reranking with 70% fewer passes” in Section 4.2 is made based on a +0.7 R@1 over fixed K=100 on MSR-VTT. This result, if real, is important, but the paper does not provide statistical significance testing, confidence intervals, or repeated runs to show it is robust rather than variance or thresholding luck.  
- More critically, the setup appears to compare adaptive K over a candidate pool potentially altered by union pooling or layer diversity (Table 2), which can change candidate coverage beyond simple budget effects. Without a carefully controlled study that holds candidate pools constant, it is hard to accept the causal story that selective reranking “avoids noise” introduced by deep K alone.

3) Evaluation breadth and metrics are thin for an efficiency paper  
- The paper reports avg-K as a proxy for compute, but offers no latency, throughput, FLOPs, or energy measurements for either stage of the pipeline. Since the proposed method adds two extra layer forward hooks and multiple ranking computations, the claim of “negligible overhead” should be quantified.  
- The reranker’s details are abstracted as “MLLM-head calibrated likelihood scoring,” which is under-specified for replication and for measuring costs; exact tokenization, prompt templates, generation vs. scoring path, sequence lengths, and batch sizing matter for runtime.

4) Calibration protocol and threshold selection are under-specified  
- Equation (2) uses thresholds τ1 and τ2 “calibrated on a validation set to achieve avg-K ≈ 30,” but the paper does not describe: the validation split, optimization criteria (only matching average K or also optimizing quality), and whether thresholds generalize across datasets or need per-dataset tuning.  
- Section 4.4 states similar easy/medium/hard proportions across datasets; however, without reporting the actual τ values and the mapping function learned on which set, it is unclear how portable or stable these thresholds are.

5) Fragility to choice of m, top-k pooling, and gallery size  
- Equation (1) computes Jaccard over top-m lists with m=20. There is no sensitivity analysis showing how m affects routing quality across different gallery sizes or distributions. If m is too small, the disagreement may be dominated by tie behaviors; if too large, it may wash out topical differences.  
- Neither Figure 1 nor Section 3.3 discusses normalization or bias when galleries differ in size or contain many near-duplicates, which can distort set overlap measures.

6) Insufficient clarity on the reranker and end-to-end system  
- Section 3.1 references “EOL prompting with dual-softmax (DSM) calibration” and a “calibrated likelihood scorer,” but does not specify the probability normalization, length penalty, or how scores are aggregated across frames/tokens. Given the centrality of the reranker, these missing details impede reproducibility and raise questions about fairness in comparisons.
- The paper does not specify whether the reranker uses vision tokens per candidate, which affects the dominant runtime. If the scoring path uses video features again, the extra cost could overshadow the apparent savings from smaller K.

7) Weakness in significance reporting and variance  
- Table 1 shows small absolute differences (e.g., +0.9 R@1 on MSR-VTT). Without multiple seeds, confidence intervals, or at least a bootstrap over the 1k test queries, it is impossible to assess stability. This is crucial when using thresholded routing rules that can be sensitive to tuning.

8) Missing or under-discussed related work directly targeting adaptive or uncertainty-aware retrieval  
- Several highly relevant reranking systems and uncertainty-adaptive methods are not discussed or compared; see the next section. The current Related Work leans heavily on MLLM intermediate-layer observations and early-exit in NLP, but under-emphasizes existing adaptive text–video retrieval approaches and modern rerankers.

9) Limited interpretability beyond Figure 1, no qualitative analysis  
- The paper offers no qualitative examples of “easy” vs “hard” queries or failure cases. Visualizations of per-query D(q), top-20 overlaps across layers, and counterexamples where disagreement is high but reranking fails would enhance understanding.  
- An additional figure illustrating how thresholds partition the empirical D(q) distribution would substantiate the routing design.

10) Minor structural and clarity issues  
- The introduction cites several 2025–2026 works that are not widely recognized yet; this is acceptable but increases the onus to cross-check baselines and methods used in practice, which the paper does not do.  
- The “training-free” claim is accurate with respect to routing but risks being overstated if the extra layer hooks are non-trivial in certain implementations; the paper should quantify overhead.

Figure- and table-grounded comments:  
- Figure 1: The figure nicely diagrams three blocks (Stage 1 multi-layer embedding retrieval, routing decision, Stage 2 adaptive reranking). However, the figure’s legend suggests a clean mapping from disagreement to K via “percentile thresholds,” yet τ1, τ2 are not reported anywhere. A histogram of D(q) with percentile cutoffs overlaid would make the figure’s decision boundaries concrete.  
- Table 1: The gains over margin routing are small and there is a tradeoff on other metrics. For MSR-VTT, “Disagreement 3-tier” improves R@1 to 53.2, but R@5 drops slightly versus Fixed K=100 and margin; MnR is better than margin but worse than full K. On DiDeMo, R@1 improves over margin but is well below Fixed K=100 on R@5/R@10/MnR. The paper should contextualize that disagreement routing helps top-1 but may hurt broader recall.  
- Table 2: The “Union pool” configuration achieves the best R@1=53.1 in binary routing, which complicates the causal story that the disagreement signal alone drives gains. By expanding candidate coverage via union across layers, the method alters the input to the reranker. If the main claim is about routing quality rather than candidate set engineering, the paper should clearly separate these effects (e.g., fix a candidate set and compare routing only).

## Potentially Missing Related Work
1) Dai et al., “Fine-grained Text-Video Retrieval with Frozen Image Encoders,” 2023 — Two-stage retrieval with strong reranking using multi-grained cross-attention over top-K candidates, directly comparable in pipeline and cost-quality tradeoff. Should be discussed in Related Work and considered as a baseline or at least contrasted in Section 4.2 when claiming superior adaptivity.

2) Dai et al., “Text–video retrieval re-ranking via multi-grained cross attention and frozen image encoders,” 2024 — A refined reranker building on the above with detailed efficiency analysis. Discuss in Section 2 and compare or justify why results are not directly comparable in Table 1 if reproducibility is a concern.

3) Fang et al., “UATVR: Uncertainty-Adaptive Text-Video Retrieval,” 2023 — Explicitly addresses uncertainty in alignment for text–video retrieval. Highly relevant to the paper’s use of disagreement as a proxy for uncertainty. Contrast in Section 2 and discuss integration or differences after Equation (1).

4) Ji et al., “CRET: Cross-Modal Retrieval Transformer for Efficient Text-Video Retrieval,” 2022 — Focuses on efficient transformer architectures for text–video retrieval, providing FLOPs/latency baselines. Discuss in Section 2 and use to contextualize the paper’s efficiency claims; consider reporting comparable runtime metrics.

5) Ma et al., “Query-Adaptive Late Fusion for Hierarchical Fine-Grained Video-Text Retrieval,” 2024 — Adjusts retrieval behavior based on query characteristics, echoing the per-query adaptive theme. Cite in Section 2 and compare design philosophies of adaptivity.

6) Skow et al., “RANKVIDEO: Reasoning Reranking for Text-to-Video Retrieval,” 2026 — A reasoning-based reranker in a two-stage pipeline. Even if not directly comparable, this should be discussed as an alternative high-compute reranker and how disagreement routing might handle such expensive second-stage models.

7) Jang et al., “CoreCaption: Core Caption based Text-to-Video Retrieval,” 2026 — Efficient representations and robustness via distilled core captions. Discuss in Section 2 as a complementary strategy to reduce compute in the first stage.

8) Chen et al., “EagleNet: Energy-Aware Fine-Grained Relationship Learning Network for Text-Video Retrieval,” 2026 — Explicit focus on energy/efficiency in modeling. Compare conceptual approaches to compute efficiency in Section 2 and possibly reference in Section 4.3’s complexity analysis.

9) “DeHub: Learning Hub-Resistant Representations for Text-Video Retrieval,” 2026 — Tackles hubness in high-dimensional retrieval. Discuss in Section 2 as complementary to ranking stability; highlight that disagreement routing may interact with hubness phenomena.

## Comments Suggestions And Typos
Actionable suggestions:
- Add significance tests and report variability. Provide confidence intervals or bootstrap ranges for R@1/R@5/R@10/MnR, especially for the key claims in Table 1 that surpass or match full K=100. If improvements are not statistically reliable, tone down the conclusions.  
- Provide end-to-end efficiency metrics. Report latency, FLOPs, or energy for: (i) single-layer retrieval, (ii) multi-layer retrieval with hooks, (iii) reranking per candidate, and (iv) overall pipeline at avg-K≈30 vs. K=100. This is essential for an efficiency-focused contribution.  
- Clarify the reranker setup. Detail the exact prompt templates, tokenization, scoring path (generation vs. log-prob scoring), calibration steps, any length normalization, and how per-frame features are integrated. This is necessary for reproducibility and fair comparison.  
- Threshold calibration protocol. Describe the validation split, whether thresholds are tuned to a target avg-K or jointly optimize quality, and whether the same τ1, τ2 are reused across datasets. Report the actual τ values. Include a sensitivity study varying τ and m.  
- Isolate the effects of routing vs. candidate coverage. Re-run the main comparisons while holding the candidate pool fixed (e.g., anchor-layer top-100) to show the effect of routing alone; then separately analyze “Union pool” benefits. This will substantiate the causal claims about disagreement as a routing signal.  
- Add qualitative and diagnostic analysis. Provide examples of easy/medium/hard queries and visualize the D(q) distribution with τ cutoffs. Include failure cases where high disagreement does not help, and discuss when margin-based routing might still be preferable.  
- Expand datasets and model backbones. Add at least one more standard benchmark (e.g., LSMDC, VATEX) and one different backbone or reranker to test generality. Consider comparing with one modern two-stage reranker from Missing Related Work to contextualize the tradeoffs.  
- If possible, include a small user-study or human audit of retrieved results to corroborate that improved R@1 reflects perceived relevance, especially where R@5/R@10 trade off.

Potential typos or clarity nits:
- Page 1, Abstract: “achieves +0.9 and +1.5 R@1 improvements over margin-based routing respectively” — specify the datasets inline for clarity.  
- Page 3, Section 3.2: “token position preceding the embedding token” — this is ambiguous; please state the exact token indices and whether CLS- or EOL-token positions are used.  
- Page 4, Table 1 caption: “Best in bold, second-best underlined” — the table does not appear to show underlines; either add them or revise the caption.  
- Page 5, “Exceeds full reranking…” paragraph: the causal explanation is speculative; tone down or support with controlled experiments.  
- References formatting has minor inconsistencies (venue details missing for some entries).

What could change my assessment:
- Adding at least one strong, modern two-stage reranker baseline and reporting end-to-end runtime/FLOPs would significantly strengthen soundness.  
- Providing statistical significance and multi-seed robustness for Table 1 results.  
- Clearer reranker details and controlled experiments isolating routing from candidate coverage.  
- Demonstrating generalization across an additional dataset and a different backbone.

## Confidence
3: Reasonably confident but not fully verified — I am familiar with retrieval and adaptive inference. The idea is clear, but missing details on reranker and efficiency make some claims hard to verify from the text alone.

## Soundness
2.5: Between Poor and Acceptable — The method is plausible and the signal is sensible, but the empirical validation is narrow; claims that exceed full reranking lack statistical support and efficiency is not measured beyond avg-K.

## Excitement
2.5: Between potentially interesting and interesting — The simplicity and training-free nature are appealing, but the scope and depth are limited at present.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The cross-layer disagreement idea is neat and the reported gains over margin routing at fixed avg-K are promising. However, the study is too narrow, lacks key baselines and efficiency measurements, and over-interprets surpassing full reranking without significance tests or controlled analyses. With stronger baselines, runtime/energy reporting, clearer reranker details, and robustness checks, this could reach Findings.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly acknowledges limited scope (one model, two benchmarks) in the conclusion. It does not discuss broader societal impacts. Relevant considerations include:  
- Bias in video datasets and uneven performance across content types; routing mistakes could systematically under-allocate compute to certain linguistic or visual categories.  
- Energy use: while avg-K is reduced, extra layer passes and potential larger candidate pools may change the true energy footprint; empirical measurements would let readers weigh environmental impact.  
- No discussion on dual use. Efficient retrieval can be used for surveillance or privacy-invasive applications; a brief acknowledgement and mitigation notes would be advisable.

## Ethical concerns
None identified from the text beyond the need for a standard discussion of dataset biases and dual use in retrieval applications. The paper prominently notes it was generated by an automated research system; that is fine, but the work should still meet scientific rigor standards.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The main idea and equations are clear, but reranker details, threshold calibration protocol, and runtime specifics are under-specified. The code is claimed to be available, but the paper text alone lacks enough to fully reproduce all results.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If the promised code indeed implements the routing, it could be useful. The paper would benefit from documenting exact configs, prompts, and evaluation scripts.