# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies where to fine-tune a single transformer layer for model editing. It proposes GradRatio-Select, which scores each layer by the ratio of squared gradient norms between an edit objective and a retain objective, S(ℓ) = ||g_edit(ℓ)||^2 / ||g_retain(ℓ)||^2 (Equation 4). An adaptive lower-bound on allowable layers, ℓ_min = max(3, ⌈0.15L⌉) (Equation 5), is used to exclude early “structurally critical” layers. The final choice is the highest-scoring eligible layer (Equation 6). Experiments on Qwen2.5-7B-Instruct and LLaMA-3-8B-Instruct, editing ZsRE facts and evaluating with the WILD protocol, show that the method selects the same layer as a heuristic baseline for Qwen and an adjacent layer for LLaMA. Performance matches the heuristic on Qwen but degrades capability by 5.26 percentage points on LLaMA, largely due to GSM8K. The authors conclude gradient-based selection automates layer choice but does not outperform tuned heuristics.

## Summary Of Strengths
- Clear problem framing: the paper targets a concrete and relevant pain point in fine-tuning-based editing, namely automated layer selection across architectures.
- Simple, interpretable metric: the ratio in Equation 4 is easy to compute and reason about, requiring only two gradient passes; this is attractive for practitioners.
- Sensible safety mechanism: the adaptive threshold (Equation 5) addresses a real failure mode where early layers spuriously dominate due to small retain gradients. 
- Reproducible reporting of main choices: the paper specifies models, dataset (ZsRE), metrics, and basic training hyperparameters, enabling partial reproduction.
- Useful diagnostics: Figure 2 visualizes GradRatio scores and illustrates why early layers are excluded; the ablation in Section 3.5 clarifies why the cosine term was removed.
- Concrete, honest findings: Table 1 and Table 2 make it clear that the method does not beat careful heuristics and can underperform on some architectures, which is a valuable negative result for the community.

Specific figure/table strengths:
- Figure 1 effectively lays out the pipeline from gradient scoring to localized fine-tuning and evaluation, making the method easy to follow. It clearly maps where gradients are computed, where the threshold is applied, and what is fine-tuned afterward.
- Table 2 pinpoints that nearly all of the LLaMA-3-8B capability drop comes from GSM8K, which is a focused and actionable diagnostic.

## Summary Of Weaknesses
1) Limited novelty and connection to prior work on gradient-guided selection. The core idea, ranking layers by gradient magnitude or related criteria, is conceptually close to existing gradient-based parameter/layer-selection literature. The paper’s Related Work (Section 4) omits several directly relevant works that either solve a near-identical “where to edit” problem or study gradient-driven selections. This makes it hard to position the contribution and can overstate originality.

2) Weak empirical scope and missing comparisons. Only two model families are tested with one dataset of edits (ZsRE). There is no comparison to other automatic selection strategies that a practitioner might actually use, such as Fisher-based importance (EWC-style probes), other gradient statistics (e.g., GPS-like), or locate-then-edit methods adapted to layer choice. As a result, it is unclear whether GradRatio-Select is competitive beyond simple heuristics.

3) Underwhelming outcomes relative to baseline. As shown in Table 1, GradRatio-Select matches heuristics on Qwen but is substantially worse on LLaMA-3-8B, with −5.26pp Capability. The method’s practical value is therefore questionable unless it offers broad automation that reliably matches heuristics across models, which is not demonstrated here.

4) Adaptive threshold is ad hoc and not validated across conditions. Equation 5 hard-codes ℓ_min = max(3, ⌈0.15L⌉). There is no principled derivation or sensitivity analysis for this threshold. Figure 2 shows it avoids disastrous early layers, but the rule could be brittle across other models or datasets. A study of varying ℓ_min, or data-adaptive criteria beyond a fixed function of L, is needed.

5) Limited analysis of the LLaMA failure mode. Table 2 shows the capability drop is dominated by GSM8K (−23.86pp), with high variance. The paper states one seed is especially low, but does not provide deeper analysis, for example:
- whether GSM8K uses attention-heavy reasoning layers that the method inadvertently perturbs,
- whether the selected layer’s MLP weights correlate with known arithmetic or chain-of-thought features,
- or whether GradRatio scores change meaningfully if computed from math-focused retain data.
Without this, the central negative result remains mostly observational.

6) Restriction to MLP down-projections only, with no justification. Section 2.3 follows prior claims that factual knowledge lives in MLPs, and thus restricts candidates to W_down. Yet the capability loss on LLaMA is plausibly tied to reasoning circuits involving attention as well. At minimum, an ablation comparing selection among attention vs MLP, or showing why attention is not competitive under the same metric, would strengthen the claim.

7) Stability of the scoring step is not evaluated. The method uses 32 edit samples and 256 retain sequences to compute gradients (Section 3.1). There is no study of whether S(ℓ) is stable under different minibatches, different retain corpora, or different seeds. Especially given the GSM8K variance, showing the variance of S(ℓ) across draws would be important to trust the ranking.

8) Evaluation breadth is narrow for editing. Only ZsRE is used. Many editing papers evaluate across multiple relation types or include out-of-distribution paraphrases and counterfactuals. The WILD capability suite is helpful, but the editing dimension would benefit from at least one additional edit dataset to check robustness.

9) Missing details hinder reproducibility. While many hyperparameters are given, the retain data source is unspecified in Section 3.1 beyond “general text.” The origin, sampling method, and any filtering of the 256 retain sequences are not described. Given that Equation 4 depends critically on g_retain, this omission is material.

10) No evidence that cosine conflict is always uninformative. Section 3.5 shows low cosines for the two tested models, then removes the term. However, it is plausible that other models or edit domains produce meaningful conflict signals. A broader check, or at least a warning about scope, would make the conclusion less sweeping.

11) Limited discussion of compute and efficiency vs. layer sweeps. The paper claims efficiency because only two gradient passes are needed, but does not contrast wall-clock cost vs. alternatives like Aletheia-style lightweight probes or small sweeps, nor report actual timings. The practical value proposition is therefore not quantified.

12) Figure 2 partly contradicts the selection narrative. In the LLaMA panel, several early layers have extremely high scores due to tiny retain gradients; the threshold masks this, but it also suggests that the ratio alone can be misleading. A more principled normalization, for instance clipping or reweighting by Fisher or layerwise preconditioning, might overcome the artifact. The current paper does not explore such remedies.

13) Statistical testing is minimal. The paper reports mean ± std over three seeds. Given the large GSM8K variance for LLaMA, statistical comparisons or confidence intervals would help substantiate claims of “statistically indistinguishable” performance on Qwen and clarify whether the LLaMA drop is significant beyond noise.

Figure/table-specific critiques:
- Figure 1 is clear, but it encodes a key design decision — restricting selection to W_down — without empirical justification in the figure or text that follows. A small inset or pointer to an ablation would help.
- Figure 2 strongly motivates the need for thresholds, but it also exposes a limitation of the core metric. The paper leans heavily on masking the problem rather than improving the score itself.
- Table 1 reports Capability drops for LLaMA despite selecting a layer only one block away from the heuristic. This undercuts the premise that the ratio reliably pinpoints a near-optimal layer; the authors should probe why adjacent layers diverge so much under identical fine-tuning.
- Table 2 shows GSM8K dominates the aggregate difference. The paper should include a per-layer GSM8K ablation around layers 20–24 to test whether the degradation is localized and whether the ratio ordering aligns with GSM8K preservation.

## Potentially Missing Related Work
1) Mishra et al., “Correcting Language Model Outputs by Editing Salient Layers,” 2024 — Proposes a data-driven, gradient-based layer selection mechanism for editing, directly overlapping with this paper’s goal. Should be discussed in Section 4 and compared empirically as a baseline alternative to GradRatio scoring.

2) Gu et al., “Editing Large Language Models via Adaptive Gradient Guidance,” 2025 — Uses module-wise gradient differences to guide edits. Relevant to Section 2 as an alternative gradient-driven criterion; add discussion and, if feasible, a comparison to GradRatio layer choices.

3) Gupta et al., “Editing Common Sense in Transformers,” 2023 — Studies layer-localized edits and capability effects for commonsense; useful for positioning and for analyzing capability trade-offs in Section 3.3.

4) Yang et al., “Learning Where to Edit Vision Transformers,” 2024 — Although in vision, it explicitly separates where-to-edit from how-to-edit via masks. Cite in Section 4 to situate the locate-then-edit framing and discuss differences in modality and transferability of selection criteria.

5) Kumar et al., “AdaGradSelect: An adaptive gradient-guided layer selection method for efficient fine-tuning of SLMs,” 2025 — Gradient-guided dynamic block selection highly relevant to Section 2; compare to a static ratio like Equation 4.

6) Zhang et al., “Gradient-based Parameter Selection for Efficient Fine-Tuning,” 2024 — GPS selects parameters to tune using gradient signals; conceptually close to GradRatio. Add to Section 4 and discuss how layer-level vs parameter-level selection trade off in editing.

7) Saket et al., “Aletheia: Gradient-Guided Layer Selection for Efficient LoRA Fine-Tuning Across Architectures,” 2026 — Cross-architecture, gradient-probe-based layer selection for LoRA. Should be discussed and possibly used as a baseline for automated layer choice in Section 3.

8) Kumar et al., “Training-free layer selection for partial fine-tuning of language models,” 2026 — Two-stage, training-free scoring for selecting layers; closely aligned with this paper’s goal. Include in Section 4 and contrast selection metrics.

9) Li et al., “NLL-Guided Full-Attention Layer Selection for Training-Free Sliding-Window Adaptation,” 2026 — Uses validation NLL to select layers for attention budgets; relevant to the general problem of layer selection. Cite in Section 4 and discuss whether NLL-driven selection could serve as an alternative to Equation 4 for editing.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Add direct comparisons to at least one automated selection baseline beyond heuristics (e.g., SaLEM, AGRADE, Aletheia, GPS-like parameter selection aggregated to layers, or a Fisher/EWC-style importance probe). This will establish whether GradRatio is competitive as an automated method rather than just matching a hand-tuned rule on one model.
- Report the source and sampling strategy for the retain set used to compute g_retain. Since Equation 4 is sensitive to the denominator, changing the retain distribution could change layer rankings. Please specify corpus, tokenization, filtering, and randomization; include a sensitivity study where you vary the retain corpus and size.
- Probe the LLaMA GSM8K failure: run a local sweep around layers 19–24 and report GSM8K-only capability, along with corresponding GradRatio scores restricted to math-like retain data. If the ranking changes and better preserves GSM8K, that would substantiate the hypothesis that the retain objective should be task-aligned.
- Test whether considering attention modules changes outcomes, at least on LLaMA-3-8B where capability drops. A small ablation selecting among attention vs MLP vs both could identify whether attention-layer edits better preserve mathematical reasoning.
- Replace or augment the fixed threshold (Equation 5) with a data-adaptive criterion, for instance:
  - clip or reweight by an estimate of layer importance (e.g., Fisher);
  - require a minimum absolute edit gradient norm and a minimum retain norm to avoid spurious ratios;
  - normalize by per-layer parameter count or preconditioning.
  Provide a sensitivity plot akin to Figure 2 showing how selected layers change under these normalizations.

Typos or clarity issues:
- Page 1: “These results suggest that while gradient-based selection can automate layer identification, it does not improve upon carefully-tuned heuristics.” This sentence appears both at the end of Page 1 and beginning of Page 2; consider removing redundancy.
- Page 3, Section 2.2: When mentioning the cosine-augmented score, explicitly number it as an equation for easier cross-reference with Section 3.5.
- Page 4, Table 1 caption: Consider adding “Capability is the average across MMLU, NQ-Open, SST-2, WMT16 en-de, and GSM8K” for self-containment.
- Page 5, Table 2: The WMT16 standard deviation for LLaMA heuristic is very large (±4.57) relative to others; a brief remark on decoding variability or small-sample effects would help.
- References: Some entries are incomplete or lack venues; e.g., Meng et al., 2022a; 2022b. Please standardize formatting and include venues where appropriate.

Criteria that could raise my score:
- Add at least one strong automated selection baseline with a fair comparison and show that GradRatio-Select is competitive or clearly identify when it fails and why.
- Provide a careful analysis of the LLaMA/GSM8K degradation and demonstrate a mitigation (e.g., retain distribution aligned to math, attention vs MLP selection, or an improved normalization of Equation 4) that narrows the gap.
- Clarify and ablate the retain corpus choice; include a stability analysis of S(ℓ) across batches and seeds.
- Expand the evaluation to at least one additional edit dataset and one more model family.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully, including results in Tables 1–2 and Figures 1–2. It’s unlikely, though conceivable, that I missed something material.

## Soundness
2.5: Between Poor and Acceptable — The method is clear and produces coherent results, but the empirical scope is narrow, comparisons to closely related automated selectors are missing, and key design choices (thresholding, MLP-only) are insufficiently justified. The negative LLaMA result is observed but not deeply analyzed.

## Excitement
2.0: Potentially Interesting — Automating layer choice is a relevant problem and the ratio is simple, but the current evidence does not show advantages over heuristics and reveals a notable failure mode.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the idea is simple and practical, the study is underpowered in scope, lacks comparisons to directly relevant automated baselines, and shows a significant degradation on LLaMA without sufficient diagnosis or mitigation. With stronger baselines, broader evaluation, and analysis that turns the LLaMA failure into insight or a fix, this could become a useful Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not include a dedicated limitations or impact section. Important limitations to acknowledge:
- Generality: validated on only two models and one edit dataset; performance varies by architecture.
- Metric dependence: Equation 4 can overvalue layers with tiny retain gradients; fixed thresholding may not generalize.
- Module restriction: only MLP down-projections considered; attention may matter for reasoning.
- Retain distribution sensitivity: unspecified corpus could materially change g_retain and the ranking.

Societal impact is limited since this is a methods paper on editing. Potentially relevant points:
- Model editing can be dual-use, enabling rapid insertion of misinformation if misapplied.
- Capability degradation in safety-relevant tasks could have downstream risks if unnoticed.
Encouraged to include a brief discussion and recommend guardrails, e.g., automatic post-edit capability checks before deployment.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many details are present, but the retain corpus specification and stability analyses of the scoring are missing. Including the exact retain data source and sampling, and reporting per-seed S(ℓ), would raise this to 4.

## Datasets
1: No usable datasets submitted. The work uses existing datasets; none are newly released.

## Software
3: Potentially useful. If the code referenced in the paper is available and runnable, it could be useful to others; however, the paper itself does not fully quantify efficiency or provide ablations that would make the software immediately compelling.