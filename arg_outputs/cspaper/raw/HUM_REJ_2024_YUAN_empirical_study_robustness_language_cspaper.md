# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper conducts an empirical analysis of robustness and shortcut learning in NLI models by decoupling representation and classifier effects. It examines five PLMs (BERT, RoBERTa, BART, ELECTRA, DeBERTa) on MNLI and HANS. The study uses t-SNE visualizations and DIRECTPROBE to assess linear separability, then computes cosine similarities between cluster centers across datasets/labels to explain why robustness remains limited. Finally, it proposes a “probing tool” that retrains only the classifier with debiasing methods (re-weighting and product-of-experts) while freezing the encoder, interpreting performance gaps as evidence for the relative roles of representations versus classifiers. Results suggest: (i) representations are often linearly separable, (ii) opposite-semantics clusters can be highly similar, and (iii) debiasing sometimes mainly helps by producing a better classifier rather than better representations.

## Summary Of Strengths
- Topical and relevant: The paper focuses on an important robustness question for NLI, a core ACL topic, and examines widely used PLMs.
- Cross-model comparative analysis: The study evaluates 10 encoder variants (base/large for 5 PLMs), which helps separate architecture effects from training dynamics. Table 1 provides a useful joint view of representation clusters versus in- and out-of-distribution accuracy.
- Clear experimental pipeline for decoupling: The two-phase workflow (fine-tune end-to-end, then freeze the encoder and retrain the classifier with the same or different debiasing setups) is simple and replicable, and Tables 3–4 plus Figures 3–4 make the comparison easy to follow.
- Useful negative/nuanced result: The finding that debiasing gains can largely arise from the classifier rather than improved encodings, especially for BERT, is noteworthy for practitioners who often rely on off-the-shelf debiasing pipelines.
- Concrete figure- and table-based evidence: 
  - Figure 1 and Figure 2 show t-SNE projections of [CLS] and [MEAN], visually supporting the claim that better ID/OOD performance correlates with clearer boundaries. 
  - Table 1 explicitly reports DIRECTPROBE clusters and accuracy side by side, supporting the linear-separability-yet-still-weak-OOD observation.
  - Figures 3 and 4 show that on HANS the “head retraining with debiasing” can match or exceed end-to-end debiasing for BERT across learning rates, reinforcing the classifier-driven gains narrative.
  - Table 2 and Table 11 quantify cross-dataset/label similarities and are tied to the central claim that opposite-semantics clusters remain similar.

## Summary Of Weaknesses
1) Interpretation risk due to anisotropy in cosine similarity:
- Section 4.3 and Table 2 hinge on cosine similarity between cluster centers to argue that HANS-Entailment and HANS-Not-Entailment are “similar” to MNLI-Entailment, and even to each other. However, contextual embeddings are known to occupy a narrow cone (anisotropy; cited Ethayarajh, 2019). Without mean-centering, whitening, or anisotropy-correction (e.g., removing top PCs or using CSLS), high cosine values can be an artifact rather than evidence of semantic indistinguishability. This directly affects the claimed explanation for difficulty improving robustness. The paper should at minimum repeat the similarity analysis with debiased similarity measures or layer-normalized, centered embeddings to validate the conclusion. Please specify the layer used and whether any centering/normalization beyond unit L2 was applied.

2) Overreach from linear separability to “classifiers limit performance”:
- Section 4.2 and Table 1 show that representations can be clustered into as few as 2–3 clusters, yet OOD accuracy on HANS remains far from perfect. The paper concludes that the “low robustness is not due to inseparability” and suggests classifiers are limiting. This is not fully justified: linear separability measured on aggregates or via DIRECTPROBE may not capture:
  - local decision boundary fragility,
  - calibration/uncertainty under distribution shift,
  - coverage of rare or compositional cases.
  In other words, “separable clusters” does not imply that a shallow classifier should achieve strong OOD generalization. The paper should temper claims and consider alternative explanations, or add complementary metrics (e.g., margin distributions, within-cluster variance, neighborhood purity, or robustness probes that vary lexical heuristics).

3) Limited novelty and positioning relative to recent shortcut/spurious correlation literature:
- The core message that debiasing may help through the classifier rather than representations is interesting but incremental; related recent analyses of shortcut behavior, concept-level spuriousness, and robustness under post-training are not discussed. Several directly relevant recent works are missing (see “Potentially Missing Related Work”). This makes it difficult to situate the contribution’s distinct insights.

4) t-SNE interpretation pitfalls and missing details:
- Figures 1–2 and 5–6 are heavily used to draw conclusions about “clearer boundaries,” but t-SNE is known to distort global structure and is sensitive to perplexity, initialization, and random seeds. The paper acknowledges limitations in 4.2 but still relies on these visuals. Please report t-SNE hyperparameters, seeds, and consider complementary projections (UMAP with trustworthiness metrics, PCA explained variance, or supervised projections) to reduce over-interpretation.

5) DIRECTPROBE configuration is under-specified:
- The paper repeatedly relies on DIRECTPROBE for “number of clusters” as a key diagnostic (Table 1) but does not provide the necessary configuration details: metric used, thresholding, stopping criteria, layer choice, and sensitivity to hyperparameters. Without these, reproducing the cluster counts is difficult, and their stability across seeds remains unclear.

6) The “probing tool” is more a protocol than a method, and evaluation is narrow:
- The proposed “probing tool” is a straightforward decoupled training protocol rather than a new algorithm. Its value would be clearer with:
  - application beyond MNLI/HANS, or at least multiple OOD suites (SNLI-hard, Adversarial NLI, etc.),
  - ablations for other debiasing families (confidence-based, adversarial, robust optimization),
  - statistical significance tests across the multiple seeds already trained.

7) Statistical reporting and variability:
- Most results are averages over 3 seeds, but no standard deviations or confidence intervals are reported. For Figures 3–4 and Tables 3–4, where improvements are sometimes modest, uncertainty bars would help assess robustness and whether gains are within run-to-run noise.

8) Scope limited to NLI and one primary OOD set:
- While HANS is a classic diagnostic dataset, modern evaluations often include multiple challenge suites and fine-grained taxonomies of spurious correlations. The current scope limits the generality of the conclusions, especially for the classifier-versus-encoder attribution.

9) Potential confound in the bias-only model design:
- Appendix A trains the bias-only model on a small random subset for 3 epochs. There is limited analysis on how the subset size, training epochs, or architecture affect which samples are treated as “biased” and hence how sensitive the downstream conclusions are to this design choice. For instance, does the classifier-driven gain still hold when the bias-only model is stronger, weaker, or trained by an alternative heuristic?

10) Minor issues in exposition and precision:
- Section 4.4 claims “debiasing methods distort the representation” for BERT based on Figures 3–4 and Tables 3–4. This is plausible but not directly measured on representations; it would be more convincing to show representational drift (e.g., CKA, SVCCA) or the change in DIRECTPROBE clusters pre- and post-debiasing.

Figure- and table-specific comments
- Figure 1 (t-SNE of [CLS]): Supports a correlation between MNLI/HANS accuracy reported on the figure titles and tighter visual clusters. However, without legends clarifying which colors map to which labels, and without hyperparameters, the strength of the claim is limited. It is still useful as qualitative evidence but should be framed cautiously.
- Figure 2 (t-SNE of [MEAN]): The claim that [MEAN]-fed classifiers approach [CLS]-fed performance is interesting; Table 7 in Appendix C indeed shows close numbers. It would strengthen the paper to quantify the exact performance gap in the main text and report whether classifiers were re-initialized or reused when swapping inputs.
- Table 1 (clusters vs. accuracy): Central to the “linearly separable yet OOD gap” claim. It would be valuable to add a column with the standard deviation of cluster counts across seeds, or at least indicate if the counts were stable.
- Tables 3–4 and Figures 3–4: Nicely demonstrate that retraining just the classifier with debiasing on the frozen “raw” encoder yields most of the gains on HANS for BERT. This is the paper’s crispest quantitative support for the classifier-centered explanation. Consider adding a variant where you swap classifiers across models (e.g., classifier trained on debiased encoder plugged into raw encoder) to probe transferability.
- Table 2 (cosine similarity across centers): As noted, the interpretation is fragile given anisotropy. Re-running with mean-centering or top-PC removal is recommended.

## Potentially Missing Related Work
1) Yuan et al., “Do LLMs Overcome Shortcut Learning? An Evaluation of Shortcut Challenges in Large Language Models,” 2024 — Systematic evaluation of shortcut behavior in modern LMs. It provides complementary testbeds and metrics that could broaden Section 4.4’s evaluation and contextualize the findings beyond MNLI/HANS. Suggest citing in Related Work and considering additional evaluations or discussion in Section 5–6.

2) Zhou et al., “Explore Spurious Correlations at the Concept Level in Language Models for Text Classification,” 2024 — Concept-level analyses and mitigation of spurious correlations. Directly relevant to Section 4.3’s representation-level similarity analysis; discuss alongside DIRECTPROBE in Sections 2.1 and 5.

3) Shuieh et al., “Assessing Robustness to Spurious Correlations in Post-Training Language Models,” 2025 — Examines SFT/DPO/KTO effects on robustness. Relevant for Section 4.4’s decoupled protocol and could motivate testing additional post-training regimes; cite in Related Work and discuss evaluation design choices.

4) Lee et al., “Continual debiasing: A bias mitigation framework for natural language understanding systems,” 2025 — Addresses balancing OOD robustness and ID performance via debiasing objectives. Compare to your EBD approach in Section 2.2 and discuss trade-offs in Section 4.4.

5) Zhou et al., “Boosting Resilience of Large Language Models through Causality-Driven Robust Optimization,” 2025 — Causal robust optimization to mitigate spurious correlations. Useful contrast to classifier-focused debiasing in Section 4.4; cite and discuss after Eq. (2) as an alternative objective.

6) Xu et al., “Shortcut Learning in In-Context Learning: A Survey,” 2025 — Organizes shortcut types, datasets, and mitigation methods. Helps position the contribution in Section 1 and Section 5 and motivates extending the evaluation beyond fine-tuning to in-context settings.

7) Miao et al., “How Robust are Large Language Models Against Word-Level Spurious Correlations? A Causal Discovery Approach,” 2026 — Token-level robustness diagnostics aligned with probing. Consider citing in Sections 2.1 and 4.3 as complementary tools to validate representation-level separability and similarity.

8) Shaib et al., “Learning the Wrong Lessons: Syntactic-Domain Spurious Correlations in Language Models,” 2026 — Shows spurious syntax–domain links and new robustness testbeds. Could enrich Section 3.1’s datasets and Section 4.4’s evaluation to cover broader shortcut families.

## Comments Suggestions And Typos
Actionable suggestions
- Revisit cosine similarity analysis (Section 4.3) with anisotropy-aware procedures: mean-center embeddings, remove top principal components, or use CSLS. Report whether your main conclusion about HANS-E vs. HANS-N similarity still holds. Add layer-wise analysis to test stability across layers.
- Provide full DIRECTPROBE details: similarity metric, stopping rules, thresholds, layer used, and sensitivity analyses. Add stability across seeds, and if possible, margin or purity metrics to complement cluster counts.
- Extend evaluation beyond HANS: include at least one more OOD suite (e.g., SNLI-hard, ANLI, Stress Tests) to test whether the “classifier-driven gains” generalize, and to reduce dataset-specific conclusions.
- Strengthen the classifier-versus-encoder attribution: measure representational change under debiasing directly (CKA/SVCCA), and report DIRECTPROBE cluster counts before/after debiasing. Also try a “classifier swap” experiment across encoders and decoupled heads to probe transferability.
- Report uncertainty: add standard deviations or confidence intervals to Tables 1–4 and Figures 3–4; use paired tests where applicable.
- Clarify bias-only model sensitivity: vary subset size (e.g., 1k/5k/10k), epochs, and model capacity; report how these choices affect the performance gaps attributed to classifier improvements.
- t-SNE specifics and complementary projections: list t-SNE hyperparameters and seeds; include UMAP or PCA-based analyses with quantitative metrics (trustworthiness/continuity) to reduce reliance on qualitative visuals in Figures 1–2, 5–6.
- Add label legends to all t-SNE figures and make color mapping consistent across figures to improve readability.
- Minor exposition: In Section 4.4, rephrase “debiasing methods distort representations” to reflect it as a hypothesis supported indirectly by performance behaviors, unless you add direct representational evidence.

Typos and small issues
- Table 2 row label “BART_dirtill” should be “BART_distill.”
- Some figure captions do not explicitly state which colors correspond to which labels; add legends.
- In Section 3.2, the sentence “which can provide contextual word embeddings” is redundant; consider tightening wording.
- Ensure consistent use of “bias-only” vs. “only-bias” across Sections 2.2 and Appendix A.
- Fix minor spacing and punctuation issues around equations (e.g., “softmax” written as “s o f t m a x” in Eq. 2).

Criteria for changing my evaluation after rebuttal
- Provide anisotropy-aware similarity results that either validate or appropriately revise the Section 4.3 conclusions.
- Add DIRECTPROBE configuration and sensitivity results, including stability metrics; ideally, show pre/post-debiasing cluster properties.
- Include at least one additional OOD benchmark showing that the classifier-driven effect generalizes, and add uncertainty reporting.
- If feasible, provide code to back the claims and enable reproduction.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully; it is unlikely, though possible, that I missed something material.

## Soundness
2.5: Between Poor and Acceptable — Good direction and some solid analyses, but key conclusions rely on similarity measures vulnerable to anisotropy, DIRECTPROBE settings are under-specified, and evaluation breadth/statistics are limited.

## Excitement
2.5: Between potentially interesting and interesting — The decoupled analysis is practically useful, but novelty and breadth are limited.

## Overall Assessment
2.5: Borderline Findings — The paper may meet minimal standards but requires improvements before being accepted to Findings. The main contributions are empirical and could be valuable if the similarity analysis is made robust to anisotropy, DIRECTPROBE usage is fully specified with stability checks, and the evaluation goes beyond HANS with uncertainty reporting. In its current form, conclusions about the causes of OOD failures and the role of classifiers versus representations are suggestive but not yet fully supported.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section acknowledges the focus on NLI and a plan to extend to other tasks. The societal impact discussion is brief; given the topic is robustness to spurious correlations, it would help to discuss potential downstream harms when models rely on shortcuts and how classifier-focused debiasing can mitigate or inadvertently hide biases. Encouragingly, the work does not introduce new data and uses standard benchmarks.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many training details are provided, but key missing elements include DIRECTPROBE configuration, t-SNE/UMAP settings, and released code. Reporting variability and seeds for all analyses would also help.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.