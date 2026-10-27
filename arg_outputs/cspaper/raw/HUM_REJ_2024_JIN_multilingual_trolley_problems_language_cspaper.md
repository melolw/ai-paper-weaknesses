# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper introduces MULTITP, a multilingual benchmark to probe LLM moral judgments using parametrically controlled trolley-problem–style dilemmas adapted from the Moral Machine Experiment. The authors generate 1K English text vignettes that vary key attributes (species, number of characters, age, gender, fitness, social status), translate them into 106 languages via Google Translate, and query several GPT-family models (primarily GPT‑3/3.5/4). Model preferences are summarized along six axes and compared to human preferences aggregated from Moral Machine’s 40M judgments across 130 countries using a country–language mapping. The paper reports language-dependent alignment differences, characterizes reasons that models cite (e.g., utilitarianism vs fairness), and analyzes “meta-behaviors” such as capability and consistency across languages.

## Summary Of Strengths
- Resource scope and framing
  - The paper offers a large multilingual evaluation suite grounded in a well-known moral-psychology paradigm with controlled parameterization, directly enabling cross-lingual, cross-attribute comparisons. Table 1 clearly positions MULTITP relative to prior moral-evaluation datasets, highlighting its multilingual and controlled-variation advantages.
- Careful axis-level analysis and visualizations
  - Figure 2 (AMCE-like preference comparison in English) cleanly juxtaposes GPT‑4 vs human preferences for each axis, making effect directions and magnitudes immediately interpretable.
  - Figure 3 further decomposes character-level preferences for GPT‑4, following Awad et al. (2018), which is useful for diagnosing where model judgments become extreme (e.g., strong dispreference for harming cats/dogs vs criminals vs large adults).
  - Figure 4’s world map is a compelling high-level summary of alignment gaps across geographies after language-to-country mapping.
  - Figures 7 and 8 highlight non-trivial meta-properties: cross-language capability variance and order-invariance consistency.
- Explanatory analysis
  - The qualitative reason taxonomy (Table 2, expanded in Table 5) and its distributions (Figure 5 for GPT‑3→3.5→4; Figure 6 for German/Chinese/Swahili) provide an interpretable narrative for shifts from predominantly utilitarian arguments (GPT‑3) to stronger fairness emphasis (GPT‑3.5/4).
- Relevance to ACL
  - Directly addresses multilinguality, evaluation, ethics, bias/fairness, and human-centered analysis of LLMs. The setup links NLP to social and moral psychology in a controlled, analyzable way.
- Reproducibility transparency
  - Models and decoding settings are specified (Section 4, Table 3), and a prompt template is provided (Table 6). Reporting of instruction-tuned model refusals and prompts to force a choice is candid and useful for replication.

## Summary Of Weaknesses
1) Translation quality and construct validity
- The dataset relies exclusively on automatic translation (Section 4.1) without native-speaker validation, back-translation checks, or language-specific prompt calibration. This is critical because small wording shifts in moral dilemmas can strongly bias responses across languages. Absent any quality assessment, the cross-lingual differences reported could partly reflect translation artifacts rather than genuine model “language inequality.”
- The paper reports capability issues in several languages (Section 6.1, Figure 7), but these are not disentangled from translation errors or tokenization/orthographic issues. A minimal human validation study on a subset of languages would greatly strengthen claims.

2) Country–language mapping and alignment metric
- The mapping in Appendix B.2 is many-to-many and sometimes idiosyncratic (e.g., language codes that do not match the country’s linguistic landscape or dialectal reality). The decision to aggregate alignment via population-weighted language shares (Appendix D) is sensible, but the main paper does not quantify sensitivity of Figure 4 to alternative mapping or weighting schemes. This weakens the claim that darker regions on the map reflect genuine misalignment in “that country” versus artifacts of language-population mismatches.
- The human dataset is country-indexed, while the model evaluation is language-indexed. The bridging step is central but under-analyzed in the main paper; without explicit robustness checks or ablations (e.g., excluding countries with high linguistic heterogeneity), it is hard to interpret the world map’s darker regions as substantive.

3) Use of “causal effect” language without clarity
- The paper repeatedly uses the term “average causal effect” (ACE/AMCE) and cites Awad et al. (2018), but the main text does not present the exact statistical model or identification strategy used to compute AMCEs for models vs humans (Appendix D is referenced but not summarized). In Figure 2, bars are labeled as causal effects, yet the paper neither specifies the experimental design assumptions that justify causal terminology for model outputs, nor shows the regression specification and controls. For ACL readers, a brief, explicit equation or schematic is needed to justify the “causal” label; otherwise, “marginal effect” or “preference proportion” would be more accurate.

4) Selection and measurement artifacts in English analyses
- Table 4 shows GPT‑4 at 100% for several axes (e.g., Humans>Animals, Young>Old, Fit>Unfit, More>Less), which looks implausibly categorical compared to Figure 2’s more graded AMCE depiction and to the text claiming GPT‑4 is “more extreme.” The discrepancy between Figure 2 and Table 4 is not reconciled. Is Table 4 based on a different subset or question format? If Table 4 uses deterministic prompts forcing a choice, this needs to be explained, and confidence intervals should be reported. Otherwise, readers cannot assess variance or stability.
- Gender shows “—” for GPT‑4 in Table 4, but the text attributes this to RLHF producing a 50–50 answer. If so, why is the cell not “50.0”? The missing data here hampers interpretation and suggests incomplete reporting.

5) Model coverage and benchmarking scope
- The main results focus on GPT models from specific 2023 checkpoints, with limited inclusion of open multilingual LLMs that are widely used and culturally diverse. The paper notes refusal from some safety-tuned models, but does not report broader results on alternatives that answer the questions. Given the multilingual focus, omitting comparative baselines (e.g., strong open multilingual models) limits generality of language-inequality claims.
- The study size is 1K vignettes per language, but it is unclear how these are sampled from the full combinatorial space and whether sampling is stratified to stabilize AMCE estimates across axes. Without details, it is difficult to assess whether Table 4 and Figure 2/3/9 are robust to resampling.

6) Reason taxonomy and coding reliability
- The reason categories (Table 2; expanded examples in Table 5) are sensible and grounded in the literature, but the creation process is only briefly described as manual clustering of 100 responses. There is no inter-annotator agreement, coder training description, or multilingual sampling procedure. Yet a key claim of the paper is the shift in moral reasoning from utilitarianism to fairness across model generations and languages (Figures 5–6). This claim would be much more convincing with annotation protocol details and reliability metrics.

7) Prompt design and forced-choice implications
- The prompt forces a single choice (“it should save...”), which likely increases apparent extremity and may produce the categorical results seen in Table 4. It also reduces comparability to human Moral Machine data if humans were allowed to express uncertainty or choose “no preference.” The design decision is reasonable to avoid refusals, but it should be discussed explicitly as a limitation and stress-tested (e.g., with a variant allowing principled abstention) to ensure it is not the main driver of “extreme” model preferences.
- The paper notes removing “swerving” due to bias. While sensible, this is exactly the kind of wording where translation quality and local norms matter. A short sensitivity test with alternative neutral phrasings would strengthen claims.

8) Statistical reporting
- No confidence intervals or statistical tests accompany Figure 2, Figure 3, or Table 4 in the main paper. Given the centrality of differences between models and humans, uncertainty quantification is necessary. For example, bootstrapped CIs for AMCEs and distances, or tests of difference-in-proportions, would let readers assess whether observed gaps are substantial or within noise.
- For Figure 4, reporting a per-country alignment score without uncertainty obscures whether some dark regions are strongly supported or fragile.

9) Ethical claims vs evidence
- Section “Ethical Considerations” flags “language inequality,” but mitigation steps are largely aspirational. Given the strong claims in Figures 4, 7, and 8, the analysis would benefit from at least one concrete mitigation experiment (e.g., paraphrase-augmentation or back-translation for low-capability languages; or English-in-the-loop prompting) to demonstrate how much of the inequality is alleviable by better prompt engineering or translation pipelines.

10) Minor clarity issues
- “June 13, 2023 checkpoints” (Section 4.2) is helpful, but model identifiers could be standardized; Table 3 uses “gpt-4-0613” whereas the text uses prose. Minor inconsistencies like GPT‑4 gender “—” in Table 4 reduce clarity.

Figure- and table-specific comments
- Figure 2: The large gap between GPT‑4 bars and human circles on “More vs Fewer” and “Young vs Elderly” directly supports the paper’s “more extreme than humans” claim; however, no variance or sample size is shown. Please add CIs and state the exact computation of AMCE here rather than deferring to the appendix.
- Figure 3: Pregnant woman and female doctor are the most preferred characters for GPT‑4. The negative preference scores for dog/cat/criminal are very strong. This sharp ranking is informative, but again requires uncertainty bands and a note clarifying whether scores are normalized relative to “a single generic human” as in Awad et al. (2018).
- Figure 4: The map is persuasive as a narrative device, but the language-to-country mapping and speaker-weighting assumptions should be tested for robustness. A sensitivity panel or table would help.
- Figures 5–6: The reason sunburst plots communicate shifts in high-level categories well. Still, without coding reliability, claims about “dominant” reasons per model/language remain tentative.
- Figures 7–8: The histograms compellingly show that most languages are fine, with a tail of low-capability or low-consistency languages (e.g., Amharic/Mongolian). Please quantify the exact thresholds and provide the per-language sample size used to compute “eligible answers” and “consistency rates.”
- Table 4: This is the only place with side-by-side numeric percentages across models and humans, and it is central. The categorical 100% entries for GPT‑4 and the missing gender cell deserve reconciliation with Figure 2 and explanations about evaluation protocol differences. Confidence intervals are needed.

## Potentially Missing Related Work
1) Vida et al., “Decoding Multilingual Moral Preferences: Unveiling LLM’s Biases Through the Moral Machine Experiment,” 2024 — Directly evaluates LLMs on Moral Machine across multiple languages. Should be discussed in Related Work and compared in Section 5/6 regarding scale, language coverage, and alignment metrics. If feasible, include as a baseline reference for cross-lingual trends.
2) Ahmad et al., “Large-scale moral machine experiment on large language models,” 2025 — Tests a wide sweep of LLMs on Moral Machine dilemmas. Add to Related Work and contrast with your model selection; helpful to contextualize your findings about model extremity and axis-specific differences.
3) Takemoto et al., “Scaling Laws for Moral Machine Judgment in Large Language Models,” 2026 — Explores scaling effects on Moral Machine alignment. Cite in Related Work and discuss whether your language inequality observations persist after controlling for model size.
4) Aksoy et al., “Whose morality do they speak? Unraveling cultural bias in multilingual language models,” 2025 — Uses Moral Foundations Questionnaire across languages. Discuss in Section 2 as a complementary methodology to trolley problems; helpful for interpreting cultural vs linguistic effects.
5) Hämmerl et al., “Speaking Multiple Languages Affects the Moral Bias of Language Models,” 2023 — Probes moral directions in multilingual PLMs and shows cross-lingual divergence not tracking human opinions. Should be cited in Related Work and compared to your conclusions about language inequality.
6) Arunasalam et al., “Implicit Values Embedded in How Humans and LLMs Complete Subjective Everyday Tasks,” 2025 — Audits implicit values in everyday tasks; relevant to your “reason decomposition” narrative. Cite and compare in Section 5.3 as a broader validation that models’ stated reasons align with implicit value signals.

## Comments Suggestions And Typos
Actionable suggestions
- Translation validation
  - Add a small, stratified human validation for 8–12 languages (high-resource and low-resource) that checks (i) translation adequacy and (ii) perceived neutrality of critical phrases. Report agreement and typical corrections, and re-run a sensitivity check on a subset to estimate how much translation artifacts may affect Figures 2, 4, 7, and 8.
- Robustness of mapping and metrics
  - Provide sensitivity analyses for the country–language mapping and population weighting underlying Figure 4: e.g., (a) exclude highly multilingual countries; (b) alternative weighting schemes; (c) report per-language alignment without mapping. Add uncertainty intervals or bootstrapped ranges.
- Statistical reporting
  - Report confidence intervals for AMCE/preference percentages in Figure 2, Figure 3, Table 4, and for per-country alignment in Figure 4. Clarify the statistical model used to compute AMCE, with at least one explicit equation and a brief description of controls.
- Prompt and choice framing
  - Include an ablation with a “principled abstain” option and a soft-choice variant to quantify how much forced-choice inflates extremity (this directly bears on Table 4 vs Figure 2 discrepancies).
- Reason coding reliability
  - Document the annotation protocol for reason categorization, sample sizes per language/model, coder training, and inter-annotator agreement. If coding is English-only, state that clearly; if multilingual, explain how you normalized across languages.
- Model breadth
  - Add at least a few open multilingual LLMs that do not refuse to answer, to probe whether language inequality is a GPT-specific artifact or a broader phenomenon. If refusals prevent direct comparison, discuss a principled workaround (e.g., slightly reframed prompts consistent across models).
- Figures/tables and minor fixes
  - Table 4: explain the “—” in GPT‑4 gender; report sample counts per axis and CIs; reconcile with Figure 2.
  - Clarify in Section 4.2 whether “GPT‑3” refers to text-davinci or base models; in Table 3 standardize identifiers (e.g., gpt‑4‑0613).
  - Typos: “break failure” → “brake failure” (multiple occurrences); “can sometimes fail at languages such as the Slavic” → “can sometimes fail in certain Slavic languages” (Section 6.1); remove duplicated phrase “swap the order the order” (Section 6.2).

What could change my evaluation
- If the rebuttal provides (i) concrete uncertainty quantification for AMCE and per-country scores, (ii) at least a small-scale human translation validation with measurable impact on results, and (iii) a clarification of Table 4 vs Figure 2 inconsistencies plus reliability metrics for reason coding, I would be inclined to raise the overall score.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: Empirical setup is thoughtful and well-motivated, but key methodological details (AMCE computation, uncertainty estimates, translation validation, mapping robustness) need strengthening.

## Excitement
3.5 Between interesting and exciting: The multilingual moral-evaluation angle at scale is timely and relevant, and the reason decomposition is engaging, but methodological caveats temper the excitement.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The resource and analyses are valuable, the figures compelling, and the moral-psychology grounding apt for ACL’s multilingual and ethics themes. To reach a higher bar, the paper needs stronger statistical reporting, translation validation, and robustness analyses for the language–country linkage.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper acknowledges “language inequality,” but stronger evidence is needed to separate true model capability gaps from translation or prompt artifacts. Future versions should test simple mitigations (e.g., paraphrase-robust prompting, back-translation, or bilingual priming) to reduce harm for underrepresented languages.
- The evaluation frames high-stakes dilemmas as forced-choice binaries. While aligned with Moral Machine, this may oversimplify human moral reasoning and encourage overconfident model behavior; adding abstention or expressing uncertainty would better reflect responsible AI behavior.
- Country-level aggregation risks stereotyping or essentializing diverse populations. The authors should emphasize that the alignment scores are exploratory indicators rather than definitive value judgments about cultures or languages.

## Ethical concerns
- None beyond those already acknowledged, provided the paper adds stronger caveats about translation artifacts and country–language aggregation. The human data used are anonymized and released for follow-up research per Moral Machine’s license.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Prompts, model IDs, decoding settings, and axes are described; code/data are promised. However, AMCE calculation details and translation validation are insufficiently documented in the main paper, and uncertainty reporting is missing.

## Datasets
4 Useful: The multilingual trolley-problem dataset, even machine-translated, will be useful for evaluating cross-lingual moral behavior, provided the paper includes clear release notes on translation limitations and recommended usage.

## Software
3 Potentially useful.: Release of scripts for generation, translation, prompting, and scoring would be useful. Value increases significantly if accompanied by tools for mapping sensitivity and confidence interval computation.