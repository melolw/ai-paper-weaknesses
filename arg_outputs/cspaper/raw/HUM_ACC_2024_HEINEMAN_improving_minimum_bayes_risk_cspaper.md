# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes multi-prompt MBR decoding for conditional generation with instruction-tuned LLMs. Instead of sampling candidates from a single prompt, the method builds a hypothesis set by sampling from a bank of human- and LLM-written prompts, then applies MBR with a trained utility metric to select the final output. The authors study prompt selection strategies (usage-based sampling with top-p truncation and embedding-based selection), evaluate on three tasks (text simplification, machine translation, code generation), and report consistent gains across models, metrics, and candidate set sizes. Figures 1, 3–7 and Tables 1–3 summarize improvements and ablations; Table 6 examines cross-metric generalization.

## Summary Of Strengths
- Clear and broadly applicable idea: leveraging prompt diversity to enrich the MBR hypothesis set. The method is conceptually simple, general, and immediately usable across tasks.
- Comprehensive empirical scope:
  - Three distinct generation tasks: SIMPEVAL simplification, WMT’22 EN→CS translation, HumanEval code generation.
  - Multiple model families and sizes (e.g., Llama 2, ALMA, CodeLLaMA, GPT-3.5/4), with consistent improvements shown in Table 2 and Figure 5.
  - Cross-metric evaluation showing that multi-prompt selected with one metric usually improves most other metrics (Table 3; full numbers in Table 6).
- Well-supported empirical claims with explicit analyses:
  - Figure 3a convincingly shows that multi-prompt sampling explores different “modes” in the quality–likelihood space as temperature varies; Figure 3b shows no single prompt dominates per instance; Figure 3c shows dataset-level gains over single-prompt MBR.
  - Figure 4 systematically connects diversity (novel bi-grams) to quality (LENS) across temperatures, highlighting where multi-prompt helps most.
  - Figure 6 compares efficient MBR variants, offering a practical perspective on computation-performance trade-offs.
- Practical prompt-bank strategies:
  - Prompt sampling with usage-based probabilities plus top-p truncation (Equations 4–5) is simple and effective (Table 1 top).
  - When a train split is unavailable, embedding-based selection heuristics and k-NN clustering provide reasonable alternatives (Table 1 bottom).
- Clarity and organization: the paper is well structured, with helpful figures and tables, precise equations for MBR (Eq. 1–3), and careful task setup descriptions.

## Summary Of Weaknesses
1) Limited comparison to relevant MBR variants and alternative multi-prompt ensembling:
   - The paper compares single- vs multi-prompt MBR but does not empirically compare against recent MBR advances that explicitly manage diversity or expectation estimation (e.g., diversity-aware or model-based MBR), or against token-probability-level multi-prompt ensembling. This makes it hard to isolate the benefit of prompt-induced diversity versus more principled MBR modifications.
   - Why it matters: Without these baselines, it is unclear whether multi-prompt is the most efficient or most robust way to exploit diversity in MBR.
   - Actionable: Add baselines such as diversity-aware MBR or model-based MBR (see “Potentially Missing Related Work”) and a prompt-ensemble decoding baseline that averages token probabilities across prompts.

2) Heavy reliance on automatic metrics with limited human evaluation:
   - Most key conclusions rely on trained metrics (LENS, COMET, etc.). Table 3 and Table 6 show cross-metric gains, but no direct human judgments are presented for at least a representative subset.
   - Why it matters: For simplification and translation, metric–human correlation can vary with domain and language; trained metrics may favor certain stylistic biases. A few hours of targeted human assessment would greatly strengthen claims of quality improvements.
   - Actionable: Include small-scale human evaluations on SIMPEVAL and WMT’22 EN–CS to validate that the multi-prompt improvements reflect perceived quality and adequacy.

3) Prompt-bank construction and potential bias are under-explored:
   - Prompts are largely GPT-4-generated paraphrases seeded by a small human-written set (Section 4.2; Appendix A), but there is limited analysis of how bank size, paraphrase quality, or prompt-format variations affect results beyond the heuristics in Section 3.2 and Table 1.
   - Why it matters: The method’s gains hinge on a well-constructed prompt bank. Biases or artifacts in LLM-generated prompts could skew the hypothesis space.
   - Actionable: Provide sensitivity analyses varying bank size, paraphrase “diversity strength,” and formatting styles; report coverage measures and an error taxonomy of failure prompts.

4) Efficiency concerns remain substantial:
   - Although Section 5.5 explores efficient MBR alternatives, Figure 6 shows mixed results and the cost for reference-based utilities remains quadratic in n. There is no runtime or FLOPs accounting to characterize trade-offs; the paper notes this as a limitation but leaves open how to scale in practice.
   - Why it matters: For real deployments, 100 candidates per input with learned metrics is expensive. Readers need clearer guidance on the practical compute envelope.
   - Actionable: Report wall-clock times and metric-call counts per method, include a cost–quality curve, and consider integrating recent low-rank or pruning approaches into multi-prompt MBR.

5) Statistical testing is limited and sometimes thin:
   - Table 3 includes bootstrap significance (b = 10^3) for cross-metric gains, but other central results rely on 5 bootstrap iterations (e.g., Figure 5 caption and Figure 7), which may be too small to stabilize confidence intervals, especially for non-normal score distributions.
   - Why it matters: Stability and generalization claims would be stronger with more resampling or replicated runs.
   - Actionable: Increase bootstrap iterations for all primary plots to b ≥ 10^3, or provide repeated runs with different seeds.

6) Uneven treatment across tasks and candidate set sizes:
   - Code generation uses n = 20, while simplification and translation use n = 100 (Table 2 and throughout); the rationale is not fully justified. Some conclusions about scaling with n might be task-dependent.
   - Why it matters: Comparability across tasks and guidance for practitioners require a clearer rationale for n and how to select it per task.
   - Actionable: Add an analysis justifying n by plotting quality vs n until saturation for all tasks, ideally normalizing by cost.

7) Metric dependence and utility–evaluation mismatch:
   - Section 5.4 acknowledges the MBR-with-metric equals evaluation-with-same-metric concern; while Table 3/Table 6 help, some cases still show disagreements and the paper does not deeply analyze why certain metrics favor multi-prompt more than others.
   - Why it matters: If gains are mostly metric-specific, applicability may be narrower than claimed.
   - Actionable: Provide per-metric qualitative analyses and error cases where multi-prompt helps or hurts to ground the cross-metric observations.

8) Figure- and table-specific concerns and questions:
   - Figure 3a provides a compelling visualization that multiple prompts occupy different regions in the LENS vs log p(y|x,ρ) space. However, axes scaling and density overlays are not fully explained. For example, why do some prompts have similar likelihoods but widely varying LENS scores at τ=0.5? Is there any confound from decoding hyperparameters?
   - Figure 4 shows novel bigrams vs LENS across temperatures; although it supports the diversity→quality intuition, an explicit correlation coefficient per τ would quantify the relationship.
   - Table 1 bottom indicates “Closest Similarity” can outperform “Random Selection” in LENS; this is unintuitive given the diversity hypothesis. The paper should reconcile this with the core argument.
   - Table 2: The comparison to prior SOTA is informative, but for translation the absolute gains over strong systems are small (+0.35 to +0.50 COMET), and confidence intervals are not shown. Clarify variance and practical significance.

9) Missing direct head-to-head with beam-search MBR at matched compute:
   - Figure 7 includes beam-search baselines, but not in a cost-controlled way. Since beam search can be cheaper at small n, a compute-matched comparison would be informative.
   - Actionable: Add a cost-matched plot contrasting multi-prompt sampling vs beam-search MBR.

10) Reproducibility and release details:
   - The paper says code/data/prompts will be released, but the main text uses an anonymized URL. Some metric models are large and may require non-trivial setup; the exact prompt lists for each task and all hyperparameters per figure/table should be guaranteed to be released for reproducibility.
   - Actionable: Ensure a comprehensive release that includes prompt banks, selection/sampling scripts, metric versions and seeds, and scripts to reproduce Figures 1, 3–7 and Tables 1–3, 6.

Figure-specific positive note:
- Figure 5 is strong: it shows Δ improvements from single- to multi-prompt across architectures and scales with 95% CIs. This directly supports the claim of robustness across models.
- Figure 6 is also valuable: it makes concrete that more efficient variants sometimes match or outperform vanilla MBR in translation, suggesting practical paths forward.

Table-specific positive note:
- Table 1 clearly demonstrates that usage-weighted, top-p prompt sampling is better than random, validating the proposed prompt-bank strategies.
- Table 2 shows consistent gains across many models, particularly large gains in code generation (e.g., GPT-4: +14 pass@1), which is compelling.

## Potentially Missing Related Work
1) Jinnai et al., “Generating Diverse and High-Quality Texts by Minimum Bayes Risk Decoding,” 2024 — introduces diversity-promoting MBR variants (DMBR, KMBR) that explicitly balance quality and diversity; directly relevant to Section 3 and should be discussed and, if possible, compared in Section 5.2 or 5.5 as alternative ways to induce diversity within MBR.

2) Jinnai et al., “Model-Based Minimum Bayes Risk Decoding for Text Generation,” 2024 — proposes MBMBR that uses model probabilities for expectation; compare as an alternative to sampling-based MBR in Section 2 or 5.5.

3) Deguchi et al., “mbrs: A Library for Minimum Bayes Risk Decoding,” 2024 — provides an MBR toolkit; citing it in Section 4 or 7 would ground implementation choices and facilitate reproducibility.

4) Trabelsi et al., “Efficient Minimum Bayes Risk Decoding using Low-Rank Matrix Completion Algorithms,” 2024 — offers a principled way to cut O(n^2) metric costs; should be discussed in Section 5.5 and possibly integrated into multi-prompt MBR.

5) Kamigaito et al., “Theoretical Aspects of Bias and Diversity in Minimum Bayes Risk Decoding,” 2024 — provides a bias–diversity framework and MAMBR; useful for interpreting Figure 4 and Section 3 claims about diversity.

6) Kamigaito et al., “Theoretical Guarantees for Minimum Bayes Risk Decoding,” 2025 — relevant for discussing approximation quality and efficiency trade-offs; cite in Section 5.5/6.

7) Tonolini et al., “Bayesian Prompt Ensembles: Model Uncertainty Estimation for Black-Box Large Language Models,” 2024 — closely aligned with prompt ensembling; compare in Section 6, and discuss whether their Bayesian weighting could inform your prompt sampling (Section 3.1).

8) Wang et al., “One Prompt is not Enough: Automated Construction of a Mixture-of-Expert Prompts,” 2024 — directly relevant to prompt-bank construction; cite in Section 4.2 and discuss synergy with your k-NN/usage-based selection.

9) Guo et al., “M-Ped: Multi-Prompt Ensemble Decoding for Large Language Models,” 2025 — introduces a probabilistic multi-prompt ensemble at the token level; compare empirically or discuss in Section 5.1/6 as a complementary baseline to your MBR-based selection.

## Comments Suggestions And Typos
Actionable suggestions that could raise my evaluation:
- Add comparisons to at least one diversity-aware MBR variant and one token-level multi-prompt ensemble baseline. Even a limited study on a subset of SIMPEVAL and HumanEval would substantially strengthen the evidence that prompt-induced diversity within MBR is preferable at similar cost.
- Include a small-scale human evaluation for SIMPEVAL and EN–CS to validate that multi-prompt improvements align with human judgments of adequacy, simplicity, and fluency. Report inter-annotator agreement and significance.
- Provide cost analyses: wall-clock time, number of metric calls, GPU-hours for Figures 1, 4–7. Add cost-matched baselines vs beam MBR, and extend efficient MBR comparisons to include low-rank matrix completion or pruning approaches.
- Expand prompt-bank analyses: show performance as a function of bank size; analyze sensitivity to paraphrase diversity and to formatting perturbations; include failure modes and prompt-quality diagnostics.
- Strengthen statistical analysis: increase bootstrap iterations for Figures 5 and 7 beyond five resamples and report confidence intervals or significance in Tables 1–2 where appropriate.

Minor comments/typos:
- Section 3, p.3: “As shown in Figure 3c, the majority of the 10 human-written prompts fall within a 10-point range of LENS...” Consider adding numeric ranges and variance.
- Section 4.3: report exact decoding hyperparameters per task in the main text or a concise table, not only in appendix.
- Table 1: clarify whether “Closest Similarity” and “Farthest Similarity” are computed to the centroid or pairwise; specify embedding model exactly and normalization.
- Figure 3a: add correlation coefficients between log p(y|x,ρ) and LENS per τ, and clarify kernel/density settings used in overlays.
- Figure 4: label y-axes with exact units for “Novel Bigrams” to avoid ambiguity across datasets of different lengths.

Criteria for score change:
- If the authors add a strong baseline comparison to diversity- or model-based MBR and to a token-level multi-prompt ensemble, plus a small-scale human evaluation validating gains, I would be inclined to raise to 4.5.
- If they also include comprehensive cost analysis with an efficient MBR variant integrated into the multi-prompt pipeline, I would further consider 4.5–5.0 depending on results.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: Empirical support is generally solid across tasks and metrics, with some missing baselines and limited human validation.

## Excitement
3.5 Between interesting and exciting: The idea is simple but useful; the breadth of evaluation and consistent improvements are compelling, especially the analyses around Figures 3–5 and Tables 1–2.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The technique is clear, practical, and broadly validated, though it would benefit from stronger baselines, limited human evaluation, and cost analyses.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The Limitations section acknowledges compute cost and the constrained exploration of prompt formats and selection. It would be useful to discuss the potential for prompt-bank artifacts to encode biases that propagate through MBR selection. This is especially relevant when prompts are generated by powerful LLMs that may encode stylistic or cultural biases.
- Consider potential risks of over-optimization to automatic metrics which may miss adequacy or fairness issues in simplification and translation. A short note about responsible use and the importance of human oversight would be appropriate.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The methodology is described in detail with equations, figures, and ablations. A full code/prompt release as promised would make it near-fully reproducible.

## Datasets
3 Potentially useful: The prompt banks and splits will be useful for replication, though they are not a primary dataset contribution.

## Software
4 Useful.: The code for multi-prompt MBR, sampling/selection, and evaluation would be useful to other researchers and practitioners.