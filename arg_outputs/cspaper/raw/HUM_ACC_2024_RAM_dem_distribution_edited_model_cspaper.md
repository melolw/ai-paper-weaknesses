# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes Distribution Edited Models (DEM) for training instruction-tuned LLMs with multiple heterogeneous data sources. Instead of joint data mixing with tuned sampling weights, the authors fine-tune a base model separately on each dataset, extract per-source parameter deltas (distribution vectors), and form a final model via a weighted combination of these vectors added to the base (Equation 2). A variant also averages the fine-tuned models directly (Equation 3). The method aims to reduce compute cost while improving downstream performance. Experiments with OpenLLaMA models of sizes 3B, 7B, and 13B compare DEM with standard data mixing and concatenation across InstructEval (MMLU, BBH, DROP) and HELM tasks, show layerwise and vector-similarity analyses, and report substantial training cost reductions. The paper concludes that DEM is an efficient alternative to data mixing, with better downstream scores and lower compute.

## Summary Of Strengths
- Conceptual simplicity with clear mathematical formulation. Equation 2 generalizes model interpolation by composing per-dataset parameter deltas, providing an intuitive mechanism to control each data source’s contribution.
- Strong, consistent empirical gains over data mixing across multiple sizes and benchmarks. In Table 2, at 7B, DEM improves over data mixing by +2.97 MMLU, +4.18 BBH, and +5.25 DROP. Table 4 shows similar trends at 3B and 13B, indicating scalability. Table 3 shows DEM outperforming data mixing in five of six HELM clusters.
- Compute efficiency is compelling and carefully quantified. Table 8 reports a total of 966 GPU-hours for DEM versus 11,650 GPU-hours for data mixing, aligning with the theoretical cost reduction in Section 4.3 and Equation 4.
- Useful qualitative and structural analyses that help interpret why DEM behaves well:
  - Figure 2 (t-SNE) visually demonstrates that the training datasets form largely distinct clusters, which supports the low cosine similarities among most distribution vectors in Table 7 and helps rationalize why simple vector composition can work with limited interference.
  - Figure 3 (layer-wise distance heatmap) indicates most changes concentrate in the first few transformer layers while embeddings and most deeper layers remain relatively stable. This observation supports the feasibility of vector combination, and also hints at avenues for parameter pruning or layer-selective merging.
  - Table 6 and Table 7 quantify distances and alignments, showing DEM remains closer to the base than a strong data mixing model, and that vectors are often near-orthogonal, which helps avoid destructive interference.
- Clear ablation on incremental composition. Table 5 shows monotonic improvements as vectors from more sources are added with a shared coefficient, which illustrates modularity and maintainability for evolving data pipelines.
- The paper is well written, methodologically coherent, and includes transparent training and evaluation descriptions, with extensive appendices.

## Summary Of Weaknesses
1) Missing comparisons to strong, directly relevant model-merging baselines.  
   - Although the paper cites task arithmetic, TIES-merging, model soups, and Fisher merging, it does not experimentally compare DEM against these. Since DEM-Interpolation is essentially a simple average in Equation 3, it is important to compare against Fisher-weighted averaging (Matena and Raffel, 2022) and TIES-merging (Yadav et al., 2023) directly under the same setup. Without these baselines, it is harder to attribute the gains to the DEM formulation rather than to the general benefit of post-hoc merging. This is especially critical given the strong claims in Section 6.1 and the sizeable gains in Table 2.
2) Fairness of the compute-cost comparison is under-discussed.  
   - Table 8 reports 50 data-mixing runs versus only 10 validation passes for DEM. However, the data-mixing baseline could employ more efficient weight search schemes like DoReMi or Online Data Mixing, which the paper mentions but does not implement. As a result, the 11× reduction number is an upper bound tied to a particular brute-force baseline. The paper should clarify whether more sample-efficient data-mixing search would significantly narrow the gap.
3) Weight selection protocol may not align with downstream targets.  
   - Section 5.3 and Appendix B choose DEM weights by minimizing average validation loss on the five training datasets, not by optimizing held-out task performance. This opens the possibility that DEM’s weight selection might overfit to training-domain validation losses and not best correlate with MMLU, BBH, DROP, or HELM. Table 10 hints at sensitivity: a small search over per-vector coefficients improves DROP by roughly 3 points. The paper should report a held-out development set or a multi-objective validation that better reflects downstream goals, and quantify how strongly validation losses correlate with the target metrics.
4) Limited exploration of negative interference and failure modes.  
   - Section 6.4 observes near-orthogonality for most vector pairs, and Figure 2 shows largely separated clusters, which supports success in this setting. However, the approach’s behavior on datasets that are strongly conflicting is not deeply probed. Appendix B briefly hypothesizes degradation when vectors are negatively correlated, but no concrete experiment stresses DEM under such conditions. This limits the generality of the claims.
5) Evaluation coverage could be broader on mixing strategies.  
   - The baselines include data mixing with tuned weights and a naive concatenation baseline, but do not include other simple and commonly used multi-source sampling policies, such as temperature-based sampling or example-difficulty-aware schedules. Including one or two such variants would strengthen the generality of the conclusion that post-hoc vector merging beats data-mixing training.
6) Potential confounds in HELM Math degradation.  
   - Table 3 shows DEM and data mixing both underperform the pretrained model on the Math cluster, with the explanation that formatting mistakes hurt HELM scoring. While plausible, this is a material result on an important category. It would be helpful to add simple formatting fixes or a constrained answer extraction to verify whether the issue is purely formatting or reflects a real regression in mathematical reasoning.
7) Lack of parameter-efficient variants and storage tradeoffs.  
   - Section Limitations mentions storage cost of keeping multiple distribution vectors. Since LoRA or other PEFT approaches can produce lightweight updates, it would be valuable to show at least one experiment where the vectors are trained as adapters and then merged. This would make the method more practically appealing and address a key limitation.
8) Limited analysis of robustness across data sizes and domains.  
   - Table 5 uses a fixed coefficient of 0.25 when progressively adding vectors, which is informative but simplistic. Further analysis on sensitivity to coefficients across diverse domain mixes and varying dataset sizes would help practitioners select alphas more robustly and understand when uniform weights suffice or fail.
9) Clarity issues in Equation 4 and units.  
   - Equation 4 typesets “3600” with spaces as “3 6 0 0,” which is presumably a formatting error. Table 8 mixes steps and examples informally and notes that steps are not equal to number of examples. It would help to standardize units and add a short note on how early stopping affects per-run variance.

Figure- and table-specific comments:
- Figure 1 is a clear conceptual diagram of the DEM pipeline. It effectively communicates how per-dataset fine-tuned checkpoints are converted into vectors and recombined. This supports the core claim that simple vector arithmetic can stand in for more expensive joint training.
- Figure 2 provides a persuasive visualization: the proximity between CoT and MathQA clusters helps explain their relatively higher cosine similarity in Table 7, which is a useful mechanistic link between input-space task similarity and weight-space vector similarity.
- Figure 3’s heatmap shows most change concentrates in the first two or three layers and that embeddings are stable. This supports the claim that DEM can merge without catastrophic overwriting. It also suggests a concrete follow-up: restricting merging to a small layer subset.
- Table 2 and Table 4 substantiate the main claims on downstream quality and scaling. Table 2 directly supports the asserted gains over data mixing at 7B, and Table 4 shows that the advantage holds at 3B and 13B, which is important for generality.
- Table 8 underpins the compute claim, but would benefit from a matched hyperparameter search strategy across methods or a discussion of how alternative search strategies for data mixing change the conclusion.

## Potentially Missing Related Work
1) Yang et al., “Model Merging in LLMs, MLLMs, and Beyond: Methods, Theories, Applications and Opportunities,” 2024 — comprehensive survey that situates DEM-style merging within a broader taxonomy. Should be cited in Related Work to contextualize DEM’s position and to motivate choice of merging baselines.
2) Fu et al., “Training-free LLM Merging for Multi-task Learning,” 2025 — proposes hierarchical, iterative merging algorithms that are close in spirit to DEM’s post-hoc combination. Compare in Section 2 and consider as an additional baseline in Section 6.1 where DEM-Interpolation is evaluated.
3) Ueda et al., “Merging Continual Pretraining Models for Domain-Specialized LLMs: A Case Study in Finance,” 2025 — case study of merging CPT experts with multiple algorithms, including task arithmetic and TIES. Should be discussed in Section 2 and mentioned near Table 2 to highlight differences in domain focus and methodology.
4) Cao et al., “ParamΔ for Direct Weight Mixing: Post-Train Large Language Model at Zero Cost,” 2025 — explores direct use of weight-difference vectors for transferring post-training across bases, conceptually similar to DEM’s distribution vectors. Cite in Related Work and discuss around Equation 2.
5) Song et al., “OptiMer: Optimal Distribution Vector Merging Is Better than Data Mixing for Continual Pre-Training,” 2026 — extracts per-dataset distribution vectors and optimizes their combination, paralleling DEM’s core idea. Compare in Section 2 and mention in Section 6 as a natural baseline where available.
6) Wang et al., “To Mix or To Merge: Toward Multi-Domain Reinforcement Learning for Large Language Models,” 2026 — directly studies mix-versus-merge in a different training paradigm (RL). Useful for broadening the Discussion and adding perspective in Section 7.
7) Zhu et al., “Multi-task Code LLMs: Data Mix or Model Merge?,” 2026 — an empirical look at mixing vs merging on code tasks. Could be briefly discussed in Related Work to scope DEM’s likely effectiveness on coding domains and motivate future experiments.

## Comments Suggestions And Typos
Actionable suggestions likely to change my evaluation in rebuttal:
- Add one or two strong model-merging baselines beyond simple averaging, such as Fisher merging and TIES-merging, in Table 2 and Table 4. If not feasible to run at all scales, do this at 7B on a representative subset to show whether DEM’s advantage holds against competitive merging methods.
- Provide a fairer compute comparison by including at least one efficient data-mixing search method, or quantify how the 11× figure changes under a more sample-efficient tuning strategy. A sensitivity table that replaces the “50x” data-mixing runs in Table 8 with a bandit-based or proxy-based schedule would greatly strengthen claims.
- Revisit the weight-selection criterion. Report the correlation between training-domain validation losses and downstream metrics across the searched DEM models. If possible, add a small held-out dev set representative of MMLU and BBH types to select weights, and show the effect on Table 2.
- Investigate the HELM Math category. Even a simple answer-formatting post-processor or constrained decoding for numeric answers would clarify whether performance loss is evaluation-format related or indicates real reasoning degradation.
- Include a PEFT version of DEM vectors, such as LoRA-based distribution vectors, and show that merging low-rank adapters reproduces most of the gains while reducing storage. This would also address the limitation noted on storage.

Minor issues and typos:
- Equation 4: write “3600” without spaces.  
- Section 5.3: clarify how batch size by tokens interacts with early stopping and whether the same validation protocol is used across all models.  
- Table 8: explicitly state the early stopping criterion and report variance across repeated runs if available.  
- Figures: add colorbars or numeric ticks for Figure 3 to improve quantitative readability, and a short note in Figure 2 caption about perplexity of t-SNE to aid interpretability.

Criteria to increase score:
- Demonstrate DEM’s advantage over at least one strong merging baseline (e.g., Fisher, TIES) and one efficient data-mixing tuner on 7B.
- Provide evidence that DEM’s weight selection using training-domain validation loss is aligned with held-out metrics, or adopt an improved selection scheme.
- Mitigate the HELM Math regression with format-aware decoding and report the updated scores.

## Confidence
4: Quite sure after careful checking. I read closely and checked claims against figures, tables, and equations.

## Soundness
4: Strong. The method is clear and the empirical support is substantial, though missing some competitive baselines and weight-selection validation.

## Excitement
3.5: Between interesting and exciting. The approach is simple and surprisingly effective. Stronger baselines and broader stress tests would raise this further.

## Overall Assessment
4: Conference. Solid contribution with strong empirical results and clear efficiency benefits. Some missing comparisons and analysis details prevent a higher score, but the paper is above the main-track bar.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper’s Limitations section is candid about storage requirements and architecture generality. The work could further discuss risks of merging specialized models that encode biased or conflicting behaviors, since DEM composes capabilities that may interact nonlinearly. A short note on auditing or gating vectors, and on the risk of amplifying certain biases when combining large instruction datasets, would strengthen the impact discussion.
- The evaluation is English-centric and primarily benchmarks widely used datasets. Discussing multilingual or domain-specific implications would be helpful for broader communities.
- Dual-use: easier composition of abilities can accelerate deployment but also make it simpler to assemble harmful capabilities if vectors are not controlled. The paper could suggest release practices or policies for responsible sharing of vectors.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible. Training details are substantial, datasets are public, and ablations are informative. Public code or a lightweight merging script would push this to 5.

## Datasets
1: No usable datasets submitted. The contribution is methodological and uses public datasets.

## Software
2: Documentary. No explicit software release is stated, but the method is straightforward enough to reimplement and the paper gives useful details.