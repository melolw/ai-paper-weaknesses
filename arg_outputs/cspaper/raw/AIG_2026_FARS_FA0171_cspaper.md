# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies how to merge multiple task-specific LoRA adapters into a single multi-task adapter for a shared base model. It argues that entropy-minimization–based adaptive merging is reference-free and can drive “confidently wrong” behavior, especially under LoRA interference. The proposed SourceJS-LoRA learns merge coefficients by minimizing Jensen–Shannon (JS) divergence between the merged model’s predictions and each task expert’s predictions on unlabeled inputs from that task. Layer-wise coefficients are also explored. Experiments on 8 GLUE tasks with T5-base show average performance improvements over uniform merging, DO-Merging, and an entropy-based coefficient learner. The paper reports more stable, balanced coefficients and provides a brief ablation on coefficient granularity.

## Summary Of Strengths
- Clear and focused problem framing: consolidating several task-specific LoRAs into a single adapter while mitigating interference.
- Teacher-anchored objective: The JS divergence loss in Equation 3 is a natural and principled way to “reference” task experts, addressing the stated failure mode of reference-free entropy minimization.
- Practicality: Uses only unlabeled samples per task and optimizes a small number of coefficients, keeping computational demands modest. Section 3.5 gives concrete optimization settings.
- Empirical improvements: In Table 1, the proposed method outperforms DO-Merging by +2.29 points on average and entropy-based learning by +5.55 points. The MNLI gain is notable.
- Stability evidence: Figure 2 shows SourceJS-LoRA yields non-negative, less extreme coefficients with lower variance than the entropy baseline, matching the stated motivation.
- Presentation: Figure 1 is an effective high-level diagram of the three-stage pipeline; core equations (1–7) are concise and readable.

Specific, figure- and table-grounded strengths:
- Figure 1 clearly maps the pipeline from task expert inference to coefficient optimization and the JS objective. This concretely illustrates how “teacher anchoring” is enforced at optimization time rather than as a heuristic post-process.
- Table 1 provides a broad comparison across 8 GLUE tasks, with consistent gains in the average metric and especially strong numbers on MNLI and RTE, supporting the central empirical claims.
- Table 2’s ablation on task-wise versus layer-wise coefficients is informative, demonstrating that naive scaling of parameterization can hurt without proper tuning, and that tuned layer-wise coefficients yield a modest further gain.
- Figure 2 quantitatively supports the narrative around stability: the entropy baseline produces negative and highly variable coefficients, whereas SourceJS-LoRA concentrates on balanced, positive weights.

## Summary Of Weaknesses
1) Limited scope of evaluation and generality
- The entire study is on T5-base with GLUE (Sections 4.1–4.2). There is no evidence the approach transfers to other architectures, larger models, generative tasks, or non-classification language tasks. This narrows the paper’s significance for ACL’s diverse audience.

2) Incomplete and potentially unfair baseline coverage
- While Table 1 includes DO-Merging and an entropy objective, several competitive or conceptually close baselines are omitted. In particular, recent divergence- or expert-alignment–based merging methods are not compared. Without them, it is hard to isolate the specific benefit of JS anchoring versus other principled weighting schemes.
- The implementation details of the entropy baseline are under-specified. AdaMerging variants often include temperature scaling, confidence clipping, or regularization to avoid coefficient collapse. The paper attributes poor results to “reference-free” entropy but does not examine whether standard fixes would mitigate this issue.

3) Metric reporting and averaging on GLUE
- Table 1 reports a single “Avg” across tasks and repeatedly refers to “accuracy,” yet GLUE mixes task-specific metrics (e.g., MRPC commonly reports F1/Acc, STS-B is correlation). The paper should explicitly define which metrics are used for each task and how the average is computed. As presented, it is ambiguous and hinders reproducibility and fair comparison.

4) Data splits and potential leakage ambiguity
- Appendix A states 128 “unlabeled examples per task from the validation split” are used for coefficient learning and a “separate held-out portion” for evaluation, but the exact split protocol is unclear. Given that GLUE test labels are not publicly available, many works evaluate on dev. Please clarify precisely how dev data are partitioned for coefficient learning versus evaluation, and confirm there is no leakage between tuning and reporting.

5) Details of label-space probabilistic modeling
- Equation 5 defines qθ over a label set via verbalizers and prompting, but details are thin. For text-to-text models like T5, verbalizer choices, multi-token verbalizations, normalization across label strings, decoding temperature, and prompt templates significantly affect probability calibration. Without these specifics, the “teacher” and “merged” distributions in Equations 3–4 are under-determined.

6) Coefficient constraints and optimization choices
- The method adds L2 regularization toward uniform coefficients (Equation 7) but does not constrain coefficients to be non-negative or to lie on a simplex. Figure 2 reports SourceJS-LoRA happens to produce positive coefficients, but this is not guaranteed by the objective. Negative or oversized weights could reappear on other domains; a constrained optimization ablation would strengthen the stability claim.

7) Limited analysis of sensitivity and data efficiency
- The paper fixes 128 unlabeled examples per task and a single set of hyperparameters to claim “practicality.” It would be valuable to show how performance and stability vary with the number of unlabeled samples, different λ in Equation 7, optimizer settings, and layer subsets. Table 2 shows that hyperparameters matter, but a more systematic study is missing.

8) Statistical significance and variance reporting
- Results are averaged over three seeds (Section 4.1) but no standard deviations, confidence intervals, or significance tests appear in Tables 1–2. Some improvements are large, others are modest; the reader cannot judge robustness.

9) Relation to representation geometry and interference theory
- The explanation for entropy failure is plausible, but there is minimal connection to existing analyses of LoRA interference or subspace geometry. Without engaging that literature, the mechanistic story is somewhat surface-level.

10) Clarity on supervised coefficients in Table 1
- The “Supervised Coeff” baseline underperforms on several tasks and on average. It is unclear how labels are used, what supervised objective is optimized, and whether it is tuned comparably to the proposed method. This raises questions about the strength of that baseline and the fairness of the comparison.

Figure- and table-grounded weaknesses:
- Figure 2(a) mixes per-task coefficients but does not clarify whether these are task-wise coefficients or an aggregation of layer-wise ones. If the latter, how are they summarized? The interpretation of “negative coefficients” depends on this.
- Table 1 lacks per-task metric definitions and dispersion measures; conclusions drawn from “Avg” are less convincing without that transparency.
- Table 2’s “layer-wise matched” versus “optimized” comparison shows sensitivity to hyperparameters, but the paper does not specify which hyperparameters are “matched” besides LR and λ. Readers cannot replicate or reason about why the big MNLI jump occurs.

## Potentially Missing Related Work
1) Touayouch et al., “DivMerge: A divergence-based model merging method for multi-tasking,” 2026 — Very close in spirit since it also uses divergence to align merged predictions with task models without labels. Should be discussed in Related Work (Section 2) as a directly comparable divergence-based baseline, and, if feasible, added as a baseline in Table 1 or at least contrasted methodologically near Equations 3–4.

2) Liu et al., “The Appeal and Reality of Recycling LoRAs with Adaptive Merging,” 2026 — Offers a large-scale empirical view showing entropy-style adaptive merging often acts as regularization rather than transfer. It directly contextualizes the identified failure mode and should be cited in Section 2, with discussion in Section 4.2 to interpret the entropy baseline’s behavior.

3) Jeong et al., “Preference-Aligned LoRA Merging: Preserving Subspace Coverage and Addressing Directional Anisotropy,” 2026 — Presents an alternative, principled weighting approach with geometry-aware preferences. Add to Section 2 and compare conceptually with SourceJS-LoRA’s stability claims; mention in Section 4.4 when interpreting coefficient distributions.

4) Lee et al., “LoRA on the Go: Instance-level Dynamic LoRA Selection and Merging,” 2025 — Training-free, instance-level selection and merging. While not JS-based, it addresses the same consolidation problem and would be a meaningful baseline or discussion point in Section 2 and possibly in Section 4.2 as a complementary paradigm.

5) Salami et al., “Closed-Form Merging of Parameter-Efficient Modules for Federated Continual Learning,” 2025 — Matches experts’ responses with closed-form or alternating solutions, closely paralleling the “expert-alignment” goal. Should be discussed after Equation 3 to contrast optimization-based JS minimization with closed-form response matching.

6) Shenaj et al., “LoRA.rar: Learning to Merge LoRAs via Hypernetworks for Subject-Style Conditioned Image Generation,” 2025 — Although in vision, it learns coefficients via a hypernetwork, which is relevant to the idea of predicting merge weights rather than optimizing them per se. Cite in Section 2 and discuss as an alternative approach for rapid coefficient generation.

7) Wei et al., “SSR-Merge: Subspace Signal Routing for Training-Free LoRA Merging in Diffusion Models,” 2026 — Presents a theory-backed alternative to parameter-space merging by routing signals in a decorrelated subspace. Include in Section 2 and discuss in Section 4.4 as a contrasting strategy for mitigating interference.

8) Lu et al., “On the Representation Geometry of LoRA Model Merging,” 2026 — Provides geometric analysis that can help interpret when entropy vs JS works. Add to Section 2 and use in Section 4.4 to deepen the explanation of observed coefficient stability.

9) Shen et al., “pFedGPT: Hierarchically Optimizing LoRA Aggregation Weights for Personalized Federated GPT Models,” 2025 — Learns module-specific aggregation weights under data heterogeneity; highly relevant to coefficient learning framing. Cite in Section 2 and connect to your layer-wise weighting (Equation 6).

## Comments Suggestions And Typos
Actionable suggestions and questions:
- Clarify GLUE metrics and averaging: For each task in Table 1, specify the exact metric (e.g., CoLA Matthews, MRPC F1/Acc, STS-B Spearman/Pearson) and how you compute the “Avg.” This is essential for fair comparison and reproducibility.
- Data split protocol: In Appendix A, explicitly detail how the 128 unlabeled dev examples are selected, how the “separate held-out portion” is formed, and confirm there is no overlap between coefficient learning and evaluation. If you re-split dev, provide the randomization protocol and per-task sizes.
- Entropy baseline implementation: Provide temperature settings, any confidence regularization, coefficient constraints, and search ranges. Also report an ablation to test whether simple fixes (e.g., temperature scaling, KL-to-uniform regularization) mitigate coefficient collapse. This will sharpen your central claim about “reference-free” objectives.
- Distribution modeling details for Equation 5: List prompts, verbalizers, handling of multi-token verbalizations, and how probabilities over labels are computed from token-level likelihoods for T5. If you normalize over several verbalizers per label, describe the scheme. Include these in Appendix A or a separate appendix.
- Coefficient constraints: Consider a non-negativity or simplex constraint, or at least an ablation with projected gradient or softmax parameterization. This would make Figure 2’s stability claims principled rather than incidental.
- Sensitivity and data efficiency: Add curves varying the number of unlabeled samples per task and λ in Equation 7. Report stability versus data size and show when entropy starts to fail or when SourceJS-LoRA remains robust.
- Statistical robustness: Report mean ± std over seeds in Tables 1–2 and run a paired significance test for key comparisons, especially the claimed +2.29 average gain over DO-Merging and the large MNLI improvement.
- Expand baselines: Where feasible, include at least one divergence-based or expert-alignment merging baseline and one instance-level selection/merging method. At minimum, add detailed comparisons in text.
- Figure 2 clarity: State whether panel (a) shows task-wise coefficients or aggregates of layer-wise coefficients. If aggregated, describe the aggregation (mean, norm, signed sum) and include confidence intervals.
- Supervised Coeff baseline: Describe the supervised loss, data sampling, and tuning protocol. Its weak average needs explanation; otherwise readers may question fairness.

Typos and minor issues:
- Page 5, Table 1 caption: “Best merging method in bold, second-best underlined.” The table does not visually show underlining. Ensure the formatting is consistent with the caption.
- Multiple places refer to “average accuracy.” GLUE mixes metrics, so “average score” is safer unless all metrics are accuracy, which they are not.
- Section 3.5: “converges in approximately 300 steps” but Appendix A mentions a cosine schedule over 1000 steps. Reconcile these numbers.
- Section 4.1: Please provide exact seed-wise splits and any early-stopping or checkpoint selection policy.

Criteria that could increase my score:
- Add the missing related work with a careful positioning, and incorporate at least one divergence- or expert-alignment–based baseline. 
- Provide complete GLUE metric definitions, averaging protocol, and variance/significance reporting; clarify the split protocol to rule out leakage.
- Strengthen the entropy baseline with standard tricks and ablations; if SourceJS-LoRA still wins, the claim becomes far more convincing.
- Broaden evaluation to at least one additional model family or task type, or include a data-efficiency and sensitivity study that shows stability across regimes.

## Confidence
3: Reasonably confident but not fully verified — I am comfortable with the LoRA-merging literature and adaptive weighting ideas, but details of baseline implementations and GLUE metric choices are not fully specified by the paper, which slightly limits certainty.

## Soundness
3.5: Between Acceptable and Strong — The core idea and objective (Equations 3–4) are sound and the results promising, but baseline breadth, metric transparency, and sensitivity analyses are insufficiently thorough.

## Excitement
3.0: Interesting — The teacher-anchored JS objective is a clean fix to a real failure mode and yields noticeable gains on MNLI and average GLUE, though the scope is narrow and comparisons are missing.

## Overall Assessment
3: Findings — The work is suitable for Findings given sound methodology and reproducibility, but it lacks breadth of baselines, clarity on GLUE metrics and splits, and a broader evaluation that would justify main conference acceptance. With the suggested additions and clarifications, it could be reconsidered for the main track.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper lists limitations on Page 6, noting reliance on access to task adapters and unlabeled data from each task, and evaluation only on T5-base and GLUE. I agree and would add:
  - Potential bias propagation: anchoring to expert predictions inherits any biases from single-task experts. This could systematically reinforce errors or demographic biases present in the task adapters.
  - Dual use: easier consolidation of specialized adapters can accelerate deployment without adequate cross-task validation, possibly causing unintended errors in high-stakes settings if reference experts are themselves miscalibrated.
  - Scope of applicability: the approach is currently tailored to classification-style tasks with compact label spaces and clear verbalizers; generative tasks or structured prediction require careful adaptation of Equation 5.
Authors should discuss these points, and consider lightweight guardrails, such as monitoring JS divergence to multiple experts simultaneously for outlier detection, or integrating bias-aware calibration when computing Equation 5 distributions.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — The objective, optimization, and key hyperparameters are given, but missing specifics on GLUE metrics, verbalizers/prompts, and split protocol reduce reproducibility. Including code and a precise evaluation script would likely raise this to 5.

## Datasets
1: No usable datasets submitted. — GLUE is public, and no new dataset is introduced.

## Software
3: Potentially useful. — If released, a clean implementation of coefficient learning with JS divergence and scripts for T5+GLUE would be valuable to practitioners. The paper suggests code exists; ensuring anonymity-compliant release and a full README would increase this score.