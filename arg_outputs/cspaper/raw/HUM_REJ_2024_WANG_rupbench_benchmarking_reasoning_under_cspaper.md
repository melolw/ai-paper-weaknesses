# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces RUPBench, a robustness benchmark for LLMs focused on “reasoning under perturbations.” It aggregates 15 widely used reasoning datasets (commonsense, arithmetic, logical, knowledge-intensive) and applies nine textual perturbations spanning lexical (homophones, typos, leetspeak), syntactic (It-cleft, Wh-cleft, compound variations), and semantic (red herrings, CheckList items, StressTest statements). The authors evaluate multiple LLMs (GPT-4o, Llama3, Phi-3, Gemma) under original and perturbed settings and measure robustness via accuracy and Performance Drop Rate (PDR). The paper reports that larger models tend to be more robust; it also provides manual error analyses cataloging common failure modes by task type.

## Summary Of Strengths
- Scope and coverage. The benchmark spans 15 reasoning datasets with nine linguistically motivated perturbations, covering a wide swath of the reasoning space. Table 1 (Page 5) gives a clear overview of domain coverage, answer formats, and perturbed sample counts; this breadth is useful for stress-testing multiple reasoning dimensions rather than a single niche.
- Clear data construction pipeline. Figure 1 (Page 3) effectively communicates the end-to-end process: starting from original datasets, applying three families of perturbations, followed by expert review. The explicit separation of lexical, syntactic, and semantic transformations is linguistically motivated and helps isolate where robustness breaks.
- Consolidated, multi-model evaluation. Table 2 (Page 7) reports raw accuracy and PDR across a useful lineup of contemporary models with different sizes. The table highlights expected and informative trends, e.g., GPT-4o and Llama3-70B have lower PDRs than small models; arithmetic tasks show distinct sensitivity.
- Task- and perturbation-level insights. Figure 2 (Page 7) and Figure 3 (Page 8) provide aggregated robustness patterns: lexical and cleft-style syntactic perturbations impose larger drops than simple compound variations, and commonsense/arithmetic are more fragile than logical/knowledge-intensive tasks. These trends will be valuable to practitioners prioritizing defenses.
- Error taxonomy. Appendix Tables 3 and 4, and Section 4.2.3, provide interpretable categories of reasoning failures (e.g., context misinterpretation, literalism, calculation error), which can guide targeted mitigations.
- Datasheet and limitations. The inclusion of a datasheet (Appendix C) and a Limitations section (Page 9) demonstrates responsible dataset release practices and transparency.

## Summary Of Weaknesses
1) Sampling reductions and representativeness threaten validity of reported robustness.
- Section 4.1 (Page 6) samples 300 instances per dataset (and 50 per MMLU subject). For several datasets with heterogeneous item difficulty, this small per-task sample may amplify variance and does not guarantee representativeness of the original distribution. Table 2 reports averages over “three runs” with temperature 0 greedy decoding, which typically yields deterministic results for fixed prompts; the choice of “three runs” is not explained. Without confidence intervals or bootstrap variance estimates per dataset, it is hard to assess stability or significance of differences among models and across perturbations.

2) Possible label drift and readability concerns for perturbations; quality controls are under-specified.
- Although human experts approve ≥60% (Section 3.3, Page 6), the criteria are coarse. Several perturbation examples in Table 3 (Page 13) appear to degrade grammaticality or legibility substantially. For instance:
  - Leetspeak for Social IQA introduces severe symbol noise (“0/”, “ID!<I<ā, ~I)”) that can plausibly alter intended emphasis or even the perceived content.
  - Typos for PIQA create heavily corrupted tokens (“beedn gOlued”), which may move beyond “plausible user mistakes.” 
  - Compound Variation for RiddleSense example is malformed (“If What is always slow to come , , but never actually happens ?”).
  These issues question whether the final answer truly remains invariant and whether perturbations reflect realistic user inputs. The paper would benefit from inter-annotator agreement statistics, finer-grained quality categories, and a stricter accept/rewrite protocol. The 60% approval threshold seems low for a resource paper standard.

3) Use of GPT-4o to generate Red Herrings risks evaluation leakage or favoritism.
- Section 3.2.3 (Page 5) uses GPT-4o to generate RHs, then evaluates GPT-4o on those same perturbed instances (Table 2). Even if answers remain unchanged, perturbation style, discourse structure, and token distribution could favor the generator model family. This is especially relevant given the finding that GPT-4o often has the lowest PDR. A stronger design would:
  - Use a different model family to generate RHs, or
  - Cross-generate RHs (e.g., for half of instances with a model unrelated to the evaluated one) and release per-generator subsets so readers can analyze any bias.

4) PDR definition and normalization are not fully specified; figures are hard to interpret precisely.
- Section 4.1 references “PDR following (Zhu et al., 2023),” but exact formula, normalization, and sign conventions are not restated. Figure 2 shows “Normalized PDR (%)” but the normalization method is not described in the main text. Without explicit equations, readers cannot reproduce per-perturbation bars or compare across papers. Please include the exact PDR formula and normalization in Section 4.1 and clarify whether negative PDR values are clipped when normalized.

5) Prompting design and ablations are thin for a robustness paper.
- Section 4.1 uses 5-shot CoT for arithmetic and 5-shot standard prompting elsewhere, but there is no analysis of how robustness depends on prompt format, shot count, or CoT vs no-CoT for non-math tasks. Robustness is known to be prompt-sensitive; a benchmark claiming to assess reasoning robustness should show at least one prompt ablation per category to establish that conclusions are not artifacts of a particular prompt.

6) Incomplete reporting granularity limits the utility for the community.
- Table 2 conflates all nine perturbations into an average PDR. Practitioners need per-perturbation per-task breakdowns to target defenses. Figure 2 aggregates over datasets and models, which is useful for a single high-level view, but the benchmark’s value would be clearer with:
  - Per-perturbation tables per dataset family, and
  - Additional qualitative examples per perturbation illustrating typical failure modes.
  As-is, the main quantitative artifact is one large summary table plus two aggregate figures, which undersells the richness of the benchmark.

7) Inconsistent counts and minor factual issues.
- The paper states “resulting in a total of 365,580 perturbed samples” (Page 2), but Table 1 (Page 5) entry for ETHICS is 35,676 while Appendix (Page 14) states 36,676; this discrepancy should be reconciled. Please also double check LogiQA2.0 perturbed count in Table 1 (47,880 vs 47,800 in Appendix).
- The paper reports “The results are averaged over three runs” in Table 2 (Page 7) while using greedy decoding with temperature 0. If seeds or API sampling randomness affect outputs, explain why; otherwise, three runs may be redundant or misleading.

8) Construct validity for NumerSense and formatting-sensitive tasks.
- NumerSense is cloze-style with a constrained label set. The perturbations may alter surface structure around <mask>, URLs, or inserted noise (Table 3 example) in ways that interact with instruction templates or tokenization. The paper should document special handling to ensure the intended “mask” cue and label mapping are preserved across perturbations and models.

9) Limited fairness and statistical rigor in claims comparing model families.
- Claims like “larger models are more robust” are broadly consistent with Table 2, but without statistical tests, CIs, or effect sizes across heterogeneous datasets, it is hard to assess the strength of the conclusion. Given downsampled evaluation, please report uncertainty per dataset and per-perturbation to underpin cross-model comparisons.

10) Ethical, licensing, and redistribution clarity could be strengthened.
- The paper states the benchmark is self-contained and will be publicly released (Appendix C), but the source datasets have varied licenses and constraints (e.g., MMLU terms; exam question copyright; ETHICS moral statements). The paper should explicitly list licenses and redistribution permissions for all included materials and provide a clear plan for releasing perturbed items in compliance with originals.

11) Figure- and table-specific critiques that materially affect the paper’s conclusions:
- Figure 2 (Page 7). The ranking shows Leetspeak and It-/Wh-clefts as the worst offenders. However, given the syntactic corruption in several examples (Table 3), it is not clear whether the drop is due to syntactic variation per se versus degraded well-formedness. A controlled experiment contrasting grammatically correct paraphrases vs minimally corrupted clefts would sharpen the conclusion.
- Figure 3 (Page 8). The PDR bars for arithmetic appear high across models relative to logical tasks. Yet arithmetic datasets were prompted with CoT while others were not. Without a condition where logical tasks also use CoT or arithmetic uses non-CoT, one cannot tell if the prompt style contributes to the relative fragility.
- Table 2 (Page 7). AQuA-RAT shows negative PDR for Gemma-2B and Gemma-7B, which is counterintuitive. This deserves a per-perturbation dissection to see which perturbation(s) improved performance and whether selection bias or surface artifacts inflated the apparent gain.

## Potentially Missing Related Work
1) Singh et al., Robustness of LLMs to Perturbations in Text, 2024 — Evaluates LLMs under a range of natural perturbations not specific to reasoning tasks. This is directly relevant to Section 2.2; cite and contrast with RUPBench by clarifying how reasoning-oriented tasks behave differently from general generation/classification under similar noise.
2) Agrawal et al., Enhancing LLM Robustness to Perturbed Instructions: An Empirical Study, 2025 — Focuses on instruction-level perturbations and mitigation strategies (e.g., self-denoising). Add to Section 5 to discuss defenses that could be evaluated on RUPBench and to guide future robustness improvements.
3) Hoppe et al., Investigating the Robustness of Deductive Reasoning with Large Language Models, 2025 — Proposes a framework for robustness in deductive reasoning with adversarial/counterfactual perturbations. This should be discussed in Section 2.1/2.2 and compared across the logical datasets (ReClor, LogiQA2.0) in Section 4.2.
4) Huang et al., MATH-Perturb: Benchmarking LLMs’ Math Reasoning Abilities against Hard Perturbations, 2025 — Provides a specialized math robustness suite; compare in Section 4.2.1 and consider adding as an additional arithmetic task family in future versions.
5) Chatziveroglou et al., Exploring LLM Reasoning Through Controlled Prompt Variations, 2025 — Systematically studies prompt perturbations for GSM8K; relevant to Section 4.1 and 4.2 for prompt ablations and could be incorporated into RUPBench to better tease apart prompt sensitivity.
6) Alahmari et al., Large language models robustness against perturbation, 2025 — Evaluates similar model families under noise for generation tasks; include in Section 2.2 to situate RUPBench results relative to non-reasoning tasks and to motivate cross-task generalization questions.
7) Bogavelli et al., Evaluating Robustness of Large Language Models in Enterprise Applications: Benchmarks for Perturbation Consistency Across Formats and Languages, 2026 — Suggest discussing in Section 5 for extensions to document-format and multilingual perturbations that complement RUPBench’s textual reasoning focus.
8) Joshi et al., Performance of Large Language Models Under Input Variability in Health Care Applications, 2026 — Domain-specific robustness dataset; reference in Section 5 when proposing domain-focused expansions (healthcare/legal), aligning with the paper’s motivation in the Introduction.
9) Wang et al., General Scales Unlock AI Evaluation with Explanatory and Predictive Power, 2025 — Offers a broader evaluation framework; add to Section 5 to suggest composite metrics that combine RUPBench robustness with other evaluation dimensions.

## Comments Suggestions And Typos
Actionable suggestions:
- Report full PDR formula and normalization. Include variance estimates or 95% CIs for all results in Table 2, and where feasible, provide per-perturbation per-dataset tables in the appendix. This is critical for the benchmark to become a standard reference.
- Strengthen perturbation QA. Raise the accept threshold above 60%, report inter-annotator agreement, and add a “label invariance” verification step sampled per dataset. Provide clearer grammaticality checks, especially for cleft and compound variations.
- Address RH generation bias. Regenerate RHs with a model family different from GPT-4o or create mixed-generator subsets, and analyze whether a model is advantaged by RH style. At minimum, release metadata specifying which generator produced each RH.
- Prompt ablations. Add at least one ablation per category comparing 0-shot vs few-shot vs CoT (and a standardized reasoning template across tasks) to test if robustness claims persist under different prompting methods. For arithmetic, compare with non-CoT; for logical tasks, try concise CoT to check sensitivity.
- Sampling strategy. Either expand the sample size beyond 300 per dataset or provide stratified sampling details and power analysis to justify that reported trends are statistically meaningful. Consider releasing the full perturbed sets, not only a sampled subset, to enable community-wide, high-coverage evaluation.
- Ethics/licensing. Include a table of licenses for all source datasets and an explicit statement that redistribution of perturbed instances complies with each license. For CheckList perturbations that insert URLs/handles, clarify whether these are synthetic placeholders and ensure no inadvertent PII or doxxing risk.
- Table/Figure clarifications.
  - Table 2: Explain “three runs” with greedy decoding. If deterministic, remove the averaging or justify any randomness source.
  - Figure 2: Define “Normalized PDR” in the caption or main text.
  - Figure 3: Note that arithmetic uses CoT while others mostly do not; discuss how this may confound cross-category comparisons.
- Fix count inconsistencies.
  - ETHICS: 35,676 in Table 1 vs 36,676 in Appendix; reconcile.
  - LogiQA2.0: 47,880 in Table 1 vs 47,800 in Appendix; reconcile.
- Minor phrasing/typos:
  - Page 1: “gpt 4o, 2024” should be consistently stylized; capitalize consistently across citations.
  - Page 10: “Ming-Wei Chang Kenton and Lee Kristina Toutanova” author order/format looks garbled; fix to “Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova.”
  - Table 3 examples contain duplicated punctuation and inconsistent spacing; consider standardizing examples for readability.
- What could raise my score:
  - Release full per-perturbation results and uncertainty estimates.
  - Address RH-generation bias and provide a clean ablation demonstrating no advantage for GPT-4o on RHs generated by GPT-4o.
  - Improve perturbation QA with stronger guarantees of label invariance and grammaticality.
  - Provide prompt ablations showing robustness conclusions are stable.

## Confidence
4: Quite sure after careful checking — I checked the key claims, tables, and figures in detail and identified concrete issues.

## Soundness
3: Acceptable — The study supports its main claims at a high level, but several methodological and reporting gaps (sampling, RH generation bias, under-specified PDR normalization, limited ablations) need strengthening.

## Excitement
3.0: Interesting — The benchmark scope is useful and will interest robustness/benchmarking researchers, but the execution and analysis depth need refinement before it stands as a definitive reference.

## Overall Assessment
2.5 Borderline Findings: The paper has value as a robustness benchmark and provides useful initial results, but it requires additional methodological rigor, clearer reporting, and stronger controls (especially around PDR definition, perturbation quality/label invariance, prompt ablations, and RH-generation bias) to meet main-track bar. With these fixes, it could be a strong Findings paper and a solid community resource.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section (Page 9) acknowledges sampling constraints, model and perturbation scope, and prompting limitations. I recommend also discussing:
- Potential dual-use: perturbations could be repurposed for adversarial attacks on deployed systems; mitigation guidance should accompany releases.
- Bias amplification: perturbations, especially RHs and CheckList insertions, might introduce spurious demographic or moral cues (e.g., in ETHICS) that interact with biases. Consider auditing perturbed items for sensitive attribute content shifts.
- Licensing/compliance: redistribute only content allowed by original dataset licenses; clarify handling of any proprietary exam materials in MMLU-like subsets.

## Ethical concerns
Potential but addressable:
- Redistribution and licensing compliance for perturbed versions of third-party datasets must be spelled out.
- CheckList URLs/handles should be synthetic and not inadvertently point to real individuals or sensitive domains.
- Using GPT-4o to generate RHs that are then used to evaluate GPT-4o raises fairness concerns; this should be mitigated or clearly disclosed in the release.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The core idea is clear, but missing explicit PDR formula/normalization, limited prompt details/ablations, and the use of sampled subsets without public seeds or per-perturbation tables impede exact reproduction.

## Datasets
4: Useful — If released with clear licensing, metadata, and stronger QA, the perturbed sets will be valuable for stress-testing reasoning robustness.

## Software
3: Potentially useful — Code for perturbations and evaluation would be helpful; thorough documentation and scripts to regenerate RHs with alternative models would raise this to 4.