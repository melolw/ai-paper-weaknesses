# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper examines whether socio-demographic prompting reliably elicits cultural variation in LLM outputs or whether observed effects are indistinguishable from a “placebo” induced by arbitrary prompt tokens. The authors probe four models (Llama‑3‑8B‑Instruct, Mistral‑7B‑Instruct‑v0.2, GPT‑3.5‑Turbo, GPT‑4) on datasets intended to be culturally neutral (MMLU, ETHICS-commonsense) or culturally sensitive (CALI, EtiCor). They design nine proxies, four “cultural” (Country, Name, Food, Kinship) and five “non-cultural” (Disease, Hobby, Programming Language, Planet, House Number), with five lexical prompt variants each. They propose a sensitivity statistic based on the variance of answer distributions across cues (Section 3.4) and report large, inconsistent variations across models and proxies, including for non-cultural proxies. GPT‑4 shows the least variation and the most dataset-consistent behavior. The paper argues that many past cultural-probing results risk conflating true cultural conditioning with placebo-like perturbations.

## Summary Of Strengths
- Clear and timely problem framing: the placebo analogy and the need for stronger controls in socio-demographic prompting are well motivated in the Introduction and formalized in Section 2 with explicit notation and two common bias formulations via Equations (1) and (2). This helps sharpen what should count as appropriate controls.
- Breadth of evaluation: four models, four datasets spanning intended cultural neutrality/sensitivity, nine proxies with 30 cues and five lexical variants each, totaling 270k inferences per model. Table 1 concisely introduces the proxies and provides concrete cue examples; Tables 6–14 make the lexical prompt variants transparent.
- Useful visualization and analysis:
  - Figure 1 compares Llama’s accuracy heatmaps for Food vs. Kinship cues on MMLU and illustrates how proxy choice induces unsystematic geographic variation, directly supporting the central claim that cue effects can be unstable.
  - Figure 3 shows label-flip counts from the null prompt to Food and Country on MMLU for Llama, where flips should ideally be rare; flips up to 15/50 emphasize the placebo concern.
  - Figure 4 aggregates “cultural” vs “non-cultural” variance across datasets and models. GPT‑4 is lowest and relatively stable, whereas other models exhibit high, similar variance for both cultural and non-cultural proxies.
  - Figure 6’s cross-model scatter/KDE views reveal that points cluster near the origin for some items, but otherwise lack diagonal structure, arguing against dataset-intrinsic difficulty as the sole cause and highlighting model-specific instability.
  - Figures 5 and 7–12 provide per-proxy breakdowns and correlation heatmaps that make it easy to audit specific claims.
- Qualitative insights: Section 5 gives grounded examples of how models inappropriately weave cues into reasoning for non-cultural proxies (e.g., ETHICS example with “Groovy” leading to contradictory rationales) and how Llama often inserts overt cultural markers at the start of generations, potentially amplifying instability.
- The work is likely to influence evaluation design by insisting on placebo-style controls and by demonstrating, with concrete figures and tables, that naive socio-demographic prompting can lead to misinterpretation.

## Summary Of Weaknesses
1) Statistical design and reporting are underdeveloped.
- There is no systematic uncertainty quantification. The paper repeatedly compares variances and label-flip counts, but I did not find confidence intervals, effect sizes, or hypothesis tests. For instance, Figure 4’s differences could partly reflect sample noise since only 50 items per dataset are used (Section 3.2). With m=50, observed differences in per-cue accuracy and label flips can be volatile, especially on 4-way MCQ (MMLU). Please provide bootstrap CIs over items and/or permutation tests over cue assignments to quantify the reliability of observed gaps in variance and label flips.
- Power analysis is missing. Given the small per-dataset sample size, it is unclear whether the setup can reliably detect the expected “cultural > non-cultural” separation, if it existed. This directly affects the strength of the main conclusion.

2) Sensitivity metric definition in Section 3.4 raises comparability concerns.
- v_{i,l} averages the per-option variances over a 30×O count matrix A, where rows are cues and columns are options with row sums fixed to 5 due to five lexical variants. This mixes dependence on the number of options O and induced class imbalance. As a result, v_{i,l} is not scale-comparable across datasets with different O (2, 3, 4). At minimum, normalize by the maximum possible variance or adopt an information-theoretic metric that is invariant to O, such as mutual information I(Cue;Answer), normalized mutual information, or Cramér’s V. Without normalization, cross-dataset comparisons in Figures 4–5 may exaggerate or attenuate effects.
- Because A[j][o] is a small count (≤5), variance estimates are coarse and discretized. Please consider aggregating across items first or using hierarchical modeling to stabilize estimates.

3) Confounds in prompt design and lexical variants.
- Some lexical variants are not semantically inert. For example, in Table 7 (Kinship), “A man refers to his spouse as {kinship}” versus “He uses the term {kinship} for his wife” introduce gender and role presuppositions and vary in length and specificity, likely triggering different instruction-following behavior unrelated to culture. Similarly, Country prompts in Table 9 oscillate between “from” and “living in,” potentially conflating identity with residence. These differences should be controlled by length- and syntax-matched variants, and ideally by nonsense-word controls of equal length.
- Non-cultural proxies are not aligned across cues while cultural proxies are (Page 4 states alignment only for cultural proxies). This asymmetry complicates the placebo comparison: cue salience and familiarity vary widely for programming languages, diseases, and planets, which can differentially affect perplexity or elicit topical reasoning. Consider matched, length-controlled, frequency-controlled nonsense tokens or shuffled cultural cues as stronger placebos.

4) Answer-extraction pipeline may bias results.
- Section 3.3 uses GPT‑3.5 to parse Llama/Mistral free-form outputs into final options and validates only 50 samples with 3 mismatches. A 6 percent mismatch rate can materially distort label-flip counts and variance for 270k inferences per model. Please either increase the audit set massively, publish inter-rater reliability, or avoid a cross-model dependency by constraining all models to output a single token among A/B/C/D via logit bias or stop sequences. Otherwise, we cannot separate placebo effects from extraction noise.

5) Dataset choices and repurposing introduce ambiguity.
- CALI has ground truth for only two regions and was reduced to a 3-way MCQ; ETHICS-commonsense is argued to be “universal,” but Section 5.1 itself shows culturally laden dilemmas among the most variable GPT‑4 items. This makes it hard to assert that observed flips are necessarily undesirable. The paper partially acknowledges this, but the headline claims lean on a clean dichotomy between culturally neutral and sensitive datasets.
- Conversion to MCQ for CALI, EtiCor, and ETHICS may alter task semantics. Please quantify whether multiple-choice formatting changes baseline accuracies relative to published numbers, and report inter-annotator agreement or class balance post-repurposing.

6) Limited exploration of decoding, seeds, and formats.
- All open-source model runs use temperature 0 and top_p=1 (Appendix C). With instruction tuning artifacts and different chat templates, outputs can be brittle. The paper partially mitigates this with lexical variants, but does not report robustness across different decoding settings or random seeds for closed-source models. Given the sensitivity claims, it is important to rule out decoding idiosyncrasies.

7) Interpretation occasionally outpaces evidence.
- The conclusion that “most LLMs are not yet ready for building culture-specific applications just through prompt-designing” is plausible but broad. Some culture-sensitive tasks may benefit from constrained prompting styles or retrieval; the current setup evaluates only a specific family of personas and templates. Consider qualifying the scope to “persona-style prompting for black-box cultural probing” rather than all prompt-only applications.

8) Figures support claims but also reveal open questions.
- In Figure 5, Llama’s largest sensitivity appears on Disease for MMLU and Programming Language for EtiCor/ETHICS, which is counterintuitive and consistent with the placebo thesis. However, the plot could be influenced by the unnormalized metric and extraction pipeline. Please replot with normalized or information-theoretic metrics and confirm trends with a parsing-free format to fortify the core claim.
- Figure 6’s scatter plots are persuasive, but the diagonal KDE panels suggest modality differences across proxies and datasets (e.g., bimodality for Mistral on EtiCor with Food). These deserve targeted qualitative analysis; otherwise we risk underexplaining model-specific behaviors.

9) Missing ablations and controls.
- Stronger controls would include: randomized shuffles that break alignment between country/name/food/kinship; length-matched pseudo-words; cue-removed versions keeping identical prompt length with masks; and counterfactual prompts that place cues exclusively in comments not visible to the model (to test surface sensitivity). These will help separate semantics from formatting.

10) Release plan and reuse.
- The Abstract promises releasing datasets and model responses, but no concrete details or commitment are in the main paper beyond a statement of intent. Given the paper’s empirical nature, code and responses are essential for reproducibility.

## Potentially Missing Related Work
1) Schäfer et al., “Which Demographics do LLMs Default to During Annotation?” (2025) — examines default demographic assumptions and contrasts demographic vs. placebo-style prompts in annotation tasks; relevant to Sections 1–2 on placebo framing and should be discussed in Related Work and compared conceptually after Eq. (2).
2) Saha et al., “All Norms and No Nuance Make LLMs Dull Cultural Simulators” (2025) — critiques robustness of socio-demographic prompting and proposes inverse SDP; add to Section 6 and contrast with your lexical-variant and placebo approach.
3) Masoud et al., “Cultural Alignment in Large Language Models Using Soft Prompt Tuning” (2025) — proposes a training-time alternative that might avoid placebo sensitivity; cite in Section 6 and discuss as a complementary path in Conclusion.
4) Luther et al., “The cultural alignment of Large Language Models and the effects of prompt language and cultural prompting” (2025) — studies language of the prompt and cultural prompting; link with your findings on lexical sensitivity in Sections 3.1 and 5.2.
5) Münker et al., “Evaluating AI Agents through Moral Questionnaires” (2025) — shows homogenization of moral diversity; relevant to your ETHICS findings; discuss in Section 5.1 and Related Work.
6) Khan et al., “Randomness, Not Representation: The Unreliability of Evaluating Cultural Alignment in LLMs” (2025) — closely echoes your thesis about instability; position alongside your placebo analysis in the Introduction and Section 7.
7) Pham et al., “CultureInstruct: Curating Multi‑Cultural Instructions at Scale” (2025) — provides a data-centric alignment baseline; discuss in Conclusion as an alternative to prompt-only conditioning.
8) “Demographic Background Prompting Does Not Affect Linguistic Features on LLM-Generated News Texts” (2025) — task-specific negative result for demographic prompting, pertinent to your placebo argument; add to Section 6.
9) “Demographic Prompting Fails to Bridge the Individual Variability Gap…” (2025) — shows demographic prompts capture averages not individuals; discuss in Section 1 and 6 as converging evidence.
10) CAReDiO (2026): “Enhancing Cultural Alignment of LLM via Representativeness and Distinctiveness Guided Data Optimization” — a data optimization route for cultural alignment; mention in Section 7 as a training-time alternative to reduce placebo sensitivity.

## Comments Suggestions And Typos
Actionable suggestions:
- Quantify uncertainty and power.
  - Report bootstrap CIs for Figures 3–5 and conduct permutation tests over cue assignments. Include per-dataset power analysis for detecting a pre-specified effect size between cultural and non-cultural proxies.
- Revisit the sensitivity metric.
  - Replace or augment v_{i,l} with normalized mutual information I(Cue;Answer)/H(Answer) or Cramér’s V to ensure cross-dataset comparability and reduce dependence on O and small counts. Provide a calibration showing how the current variance measure scales with O and class skew.
- Strengthen placebos and prompt controls.
  - Add length- and frequency-matched pseudo-words, shuffles that break cross-proxy alignment, masked cues with identical token counts, and a “commented-out” cue condition where the cue appears in a syntactic position unlikely to steer the model. Report a new figure analogous to Figure 4 using these stricter controls.
- Eliminate answer-extraction confounds.
  - Constrain all models to return a single token from a closed set without external parsing, or dramatically expand the manual audit of the GPT‑3.5 parser to several thousand random samples per dataset. Report mismatch rates per model and per proxy.
- Clarify dataset repurposing.
  - Document the mapping from original labels to MCQ options, show pre/post accuracy for known baselines, and discuss how MCQ conversion may change task properties. For CALI and ETHICS, consider item-level metadata indicating cultural disputability and reanalyze Figure 4 with those items removed to test robustness.

Typos and minor issues:
- Table 9, line 2: “You are from {rCountryegion}.” appears to contain a placeholder typo.
- Section 3.3: the tag examples <start of answer> / <end of answer> are inconsistently rendered in multiple places. Standardize to avoid any confusion in replication.
- Page markers 20–21 include overlapping or malformed XML-like tags. Please clean for reproducibility.
- Table 1: the Kinship example “Qi” is a Chinese energy concept; confirm that it is truly intended as a kinship term example, or correct if this is a mismatch.

Criteria that could increase my score in rebuttal:
- Provide uncertainty quantification (CIs or tests) and a normalized sensitivity analysis that confirms the main conclusions.
- Add at least one strong placebo control with matched pseudo-words and a shuffled alignment ablation showing similar effects to current non-cultural proxies.
- Report a much larger parsing-audit or move to parser-free extraction and show that key figures (e.g., Figure 4, Figure 5) remain materially unchanged.
- Clarify and justify dataset repurposing choices with diagnostics; optionally add a “disputed” item filter for ETHICS to test claim robustness.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong — Core findings are plausible and well illustrated, but the statistical treatment, metric normalization, and extraction confounds leave room for stronger validation.

## Excitement
3.5 Between interesting and exciting — The placebo framing and comprehensive empirical sweep are timely and likely to influence evaluation practices.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The central claim is compelling and supported by multiple figures (notably Figures 1, 3, 4, and 6), but the work would benefit from stronger statistical treatment, normalized metrics, and stricter controls. With these addressed, the contribution becomes even more solid.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges proxy subjectivity and single-language scope in Limitations. Additional considerations:
- Non-cultural proxies like “disease” may inadvertently stigmatize conditions. Add guidance to avoid reinforcing health-related stereotypes and consider safer neutral placeholders for placebos.
- Persona prompts that encourage dialectal mimicry (Section 5.3 examples) can lead to stereotyping. The paper should emphasize responsible use and recommend guardrails or filters when sharing prompts and generations.
- The argument that prompt-only cultural conditioning is unreliable has positive impact if it prevents overclaiming cultural fidelity, but it could also be misread to dismiss the value of culturally adaptive systems altogether. Clarify that the critique targets black-box persona prompting without robust controls, not culturally aware NLP research more broadly.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: Details are generally sufficient, proxies and lexical variants are enumerated, and hyperparameters are documented. However, reliance on GPT‑3.5 for answer parsing and the lack of released code/responses at submission time reduce reproducibility.

## Datasets
2 Documentary: No new dataset is introduced; the repurposed subsets and item lists would be useful for replication if released, but broader utility is limited.

## Software
3 Potentially useful.: If the probing and analysis scripts are released, they would be useful to others studying placebo-style prompting controls and cue sensitivity.