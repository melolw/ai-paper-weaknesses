# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper argues that the classification ability of LLMs is overstated because standard evaluations always include the correct label among choices. The authors introduce CLASSIFY-W/O-GOLD, a setting where the gold label is intentionally removed, and propose KNOW-NO, a benchmark consisting of subsets of BANK-77 and MC-TEST and a new task, EQUINFER, built from LaTeX equations in NLP papers with LLM-generated hard negatives. They also define OMNIACCURACY, the average of accuracy when the gold label is present and the expected accuracy across several prompts when it is absent. Experiments with five LLMs and humans show large drops when the gold label is missing and humans remain robust. The paper advocates OMNIACCURACY as a better summary of discriminative competence in classification.

## Summary Of Strengths
- Timely framing: highlights a real failure mode, namely forced-choice bias and lack of abstention when no option is correct. The CLASSIFY-W/O-GOLD lens is simple and resonant for practitioners evaluating LLMs in multiple-choice-like interfaces.
- New task construction: EQUINFER is an interesting, domain-relevant task that requires reading scientific context and discriminating among closely related LaTeX equations. Figure 2 provides a clear qualitative example with plausible decoys.
- Empirical breadth: evaluates closed-source and open-source LLMs and includes a small human study. Table 3 reports w/ gold, three w/o-gold prompting styles, E[A_w/o], and OMNIACCURACY, allowing several comparisons; Table 4 ablates adding a “none-of-them” option even when gold is present.
- Clear evidence displays: 
  - Figure 1 compellingly contrasts a simple MC example where GPT-4o answers correctly when gold is present but still picks a wrong option when the gold is removed, while humans abstain.
  - Figure 3 (human vs LLM box/point plot) shows that human accuracy remains high across prompting styles, while LLM-max drops sharply under No-Hint.
  - Figure 4 (stacked bars) usefully decomposes No-Hint outputs into wrong option vs generated right/wrong, revealing model-specific behaviors.

## Summary Of Weaknesses
1) Metric design is arbitrary and under-justified.
- OMNIACCURACY in Equation (1) simply averages “w/ gold” accuracy and E[A_w/o]. The 0.5–0.5 weighting has no principled rationale linked to real deployment prevalence or risk asymmetry between false acceptance and false abstention. There is no sensitivity analysis to alternative weightings or to different mixes of w/o-gold prompts. Equation (2) averages over three prompts, yet prompt choice materially affects E[A_w/o] (Table 3). This makes the metric fragile and susceptible to prompt selection.
- Missing discussion of calibration- or abstention-aware metrics commonly used in selective classification, such as coverage-conditional accuracy, AUROC for abstain detection, or utility-weighted scoring.

2) Incomplete baselines and analysis for the “none-of-them” dimension.
- The study does not compare to straightforward abstention or confidence-thresholding strategies (e.g., returning “none-of-them” if option logit gaps or self-judged confidence are small), or to simple rule-based mappers that enforce abstention when extraction fails. These are necessary to contextualize E[A_w/o] scores and would make Table 3 more diagnostic.
- Table 3 should include chance levels for each setting to help interpret absolute numbers, particularly for BANK-77 where E[A_w/o] is ~3–4% and may be near chance under their scoring.

3) EQUINFER construction risks bias toward or against particular models.
- Negative options are generated and filtered by GPT-4/Turbo (Page 4, steps iii–iv). This design may advantage or disadvantage models depending on stylistic similarities to GPT-4; more importantly, the same model family is used both to create and to filter decoys. Although the authors add human filtering, quantitative inter-annotator agreement and the share of LLM-crafted negatives ultimately discarded are not reported. This weakens claims that EQUINFER fairly challenges all models.
- The human filtering description lacks detail about annotator expertise and protocol. Without detailed reliability statistics and examples of discarded/retained negatives, the final dataset quality is hard to assess.

4) Limited and uneven human evaluation.
- Human evaluation is only conducted for MC-TEST (Table 3 and Figure 3), the simplest dataset. The main claims involve “human-like discrimination” across tasks, but there are no human results for BANK-77 or EQUINFER, precisely where LLMs struggle most and where label scope differs. This makes the central human-vs-LLM contrast incomplete.

5) Potential contamination and leakage not fully controlled.
- The paper observes likely exposure of BANK-77 to Llama 3 and proposes an underscore-to-dash trick (Page 8, Q4), which is suggestive but not conclusive. The study does not implement contamination checks across all models/datasets, nor does it quantify the impact of potential leakage on OMNIACCURACY. A broader contamination audit would increase confidence in Table 3.
- For EQUINFER, training data overlap with arXiv corpus is plausible for some models; this is not analyzed.

6) Sample selection and representativeness.
- The authors subsample BANK-77 (1k of 13k) and MC-TEST (1k of 2.64k questions) “due to budget” (Page 3). There is no report of sampling variance or confidence intervals for Table 3, despite running three shuffles. It is unclear if the selected subsets are representative, especially for BANK-77’s 77-way label distribution.
- EQUINFER originally had 3,877 instances; only 1,049 survive multiple filters. The attrition rate is substantial; the characteristics of the dropped instances are not analyzed, raising selection bias concerns.

7) Evaluation inconsistencies under No-Hint.
- Page 5 states No-Hint requires manual review because model outputs lack a fixed format; yet Table 3 reports No-Hint numbers for all models across multiple datasets without describing who judged them, how consistency was ensured, and what criteria mapped free-form outputs to “none-of-them” vs option choices. Absent clear policies (e.g., strict regex vs rubric), reproducibility is at risk.
- Figure 4 categorizes outputs for MC-TEST, but analogous distributions are not reported for BANK-77 or EQUINFER, where No-Hint parsing might be even harder.

8) Missing related and closely aligned work on MCQA evaluation, “None of the Above,” and answer mapping.
- The Related Work section focuses on LLMs’ classification results and reasoning faithfulness, but omits recent analyses specifically targeting MCQA evaluation reliability, NA/NOTA options, and robust answer extraction, which directly speak to the paper’s core claims and could offer methods/baselines (see “Potentially Missing Related Work”).

9) Interpretation of surprising behaviors not fully grounded.
- The authors attribute Llama-3’s strong HINT-AS-OPTION score on EQUINFER to “data bias” (Page 6), but do not probe alternatives (e.g., prompt formatting preferences, tokenization idiosyncrasies, training with NA labels). Table 4 shows open-source models degrade when “None” is added in w/G, but the analysis remains speculative.

10) Metric external validity and deployment implications.
- OMNIACCURACY is reported per dataset, but there is no discussion on how to aggregate across tasks or calibrate to deployment contexts where absence-of-gold frequency varies widely. Without such guidance, OMNIACCURACY may encourage apples-to-oranges comparisons across problems with different abstention priors.

Figure- and table-specific comments:
- Figure 1: Strong qualitative illustration supporting the central thesis; however, including a harder example from EQUINFER alongside would prevent readers inferring the effect arises only in toy settings.
- Figure 2: The correct option B depends on context that mentions combining CE and contrastive losses. Options A/C/D are standard CE forms; the figure is effective but the paper should explain why B is preferred in this context (ties to x and z inputs), to preempt claims that multiple forms could be “arguably correct.” Such explanation is crucial because EQUINFER hinges on semantic alignment, not surface similarity.
- Figure 3: The box/point visualization is persuasive: human variability is small and means remain near 100, while LLM max dips under No-Hint. Adding confidence intervals for LLM max across seeds would improve comparability.
- Figure 4: The breakdown by output type for MC-TEST is insightful and supports Q3. A similar plot for BANK-77/EQUINFER would substantiate claims about differing behaviors across difficulty levels.
- Table 3: Central to the paper. It would benefit from adding chance levels and standard deviations over three shuffles. The reported human 97.67% OMNIACCURACY is only available for MC-TEST; readers could misinterpret this as a global human reference. Clarify per-dataset human lines or report “N/A.”
- Table 4: The w/G vs w/G+None ablation is valuable. It substantiates that open-source models are more disrupted by a None option. Reporting per-model deltas and statistical tests would make the claim more rigorous.

## Potentially Missing Related Work
1) Gupta et al., “Improving Model Evaluation using SMART Filtering of Benchmark Datasets,” 2025 — Directly concerned with reducing benchmark inflation in MCQA by filtering easy/contaminated items. Discuss in Related Work (Section 2) and compare in Section 4 as an orthogonal way to obtain harder MCQA subsets where OMNIACCURACY might be especially diagnostic.

2) Molfese et al., “Right Answer, Wrong Score: Uncovering the Inconsistencies of LLM Evaluation in Multiple-Choice Question Answering,” 2025 — Shows evaluation scores vary widely with answer-extraction strategy. Highly relevant to No-Hint scoring and Table 3 parsing. Cite in Section 2 and discuss after Table 3; consider adopting their robust extraction baselines.

3) Stroligo et al., “An Evaluation of Classifiers for Mapping Generative LLM Responses to Answer Options of Multiple-choice Questionnaires,” 2026 — Proposes encoder-based and rule-based mappers for aligning free-form outputs to discrete options. Integrate into Section 3.2/4 to reduce manual evaluation under No-Hint and to standardize scoring.

4) Tam et al., “None of the Above, Less of the Right: Parallel Patterns between Humans and LLMs on Multi-Choice Question Answering,” 2025 — Studies NA options and human–LLM differences, directly aligned with HINT-AS-OPTION/HINT-IN-INSTRU settings. Discuss in Section 2 and compare outcomes with Table 3; consider using their NA formulations as additional prompts.

5) Balepur et al., “Which of These Best Describes Multiple Choice Evaluation with LLMs? A) Forced B) Flawed C) Fixable D) All of the Above,” 2025 — Critiques MCQA formats and proposes alternatives. Add to Section 2 to connect this paper’s critique with broader concerns and to motivate future extensions of KNOW-NO beyond MC multiple-choice.

6) Mehra et al., “How Large Language Models Classify and Semantically Explain Facial Expressions from Valence-Arousal Values,” 2025 — Demonstrates classification plus explanation with potential overconfidence; cite in Section 2 as a cross-domain case for adopting CLASSIFY-W/O-GOLD and OMNIACCURACY, encouraging external validation.

## Comments Suggestions And Typos
Actionable suggestions:
1) Strengthen OMNIACCURACY.
- Provide a principled rationale for the 0.5–0.5 weighting in Equation (1), or replace with a tunable utility-weighted formulation that reflects deployment priors over “gold present vs absent.” Report sensitivity curves varying the weight and prompt mix in Equation (2).
- Complement OMNIACCURACY with calibration-aware metrics from selective classification: coverage–accuracy curves, abstention AUROC, and utility-weighted scores to capture costs of false selection vs false abstention.

2) Expand baselines in Table 3.
- Add simple abstention baselines: e.g., abstain if the model generates any non-letter token; abstain if top-two option log-prob gap < τ; abstain if self-reported confidence < c. Also include deterministic extractors or classifier mappers (as in Stroligo et al.), to reduce manual No-Hint adjudication.
- Include chance performance lines for each dataset/setting and report standard deviations over seeds.

3) Improve dataset construction transparency for EQUINFER.
- Report statistics on negative-equation generation: acceptance rates at each filtering stage, examples of rejected/accepted negatives, inter-annotator agreement, and annotator expertise. Provide a taxonomy of negative types (syntactic variants, wrong conditioning, symbol mismatch).
- Offer a non-LLM negative generation variant or human-authored decoys for a subset to assess potential bias from GPT-4-generated distractors.

4) Bolster human evaluation.
- Add human studies for BANK-77 and EQUINFER with the same prompt conditions as Table 3. Even small, well-controlled samples with agreement measures would substantiate the human–LLM gap beyond MC-TEST.

5) Address contamination systematically.
- For all datasets and models, run contamination probes (e.g., data signature tests, option-format perturbations beyond underscore/dash, paraphrased intents, masked labels). Quantify impacts on both A_{w/} and E[A_{w/o}], and discuss implications for OMNIACCURACY.

6) Reproducibility and parsing policy.
- Release the exact prompts (Table 2 variants), the adjudication rubric for No-Hint, and the code for answer extraction. State precise rules for mapping free-form model outputs to categories used in Figure 4 and to accuracies in Table 3.

7) Clarify Figure 2’s correctness criteria.
- Add a one-sentence justification explaining why Option B is correct in context and why A/C/D are not. EQUINFER depends on semantic correctness rather than minor normalization differences; codify this in the dataset card.

8) Minor issues and typos.
- Table 3: The column headers are misaligned (“Open-source” appears to cover Llama3 and Gemma; Mistral is split). Please fix the header layout to avoid confusion.
- Table 3 note: “Gemma is much lower … because it cannot follow the instruction and always fail to return the option.” Grammar: “fails.”
- Page 6: “HINTAS-OPTION” should be “HINT-AS-OPTION.”
- Page 11: “KNOW-No” appears; elsewhere “KNOW-NO” is used. Standardize capitalization.

What could change my score:
- A revised metric section with principled weighting and calibration-aware reporting; expanded baselines including extraction/mapping and abstention thresholds; per-dataset human evaluation; and fuller EQUINFER construction transparency would raise Soundness and Reproducibility and could move this to main conference.

## Confidence
4: Quite sure after careful checking — I examined methodology, tables, figures, and equations, but some construction details (e.g., EQUINFER filtering) would require released artifacts to fully verify.

## Soundness
3: Acceptable — The central empirical finding is supported, but the metric is under-justified, baselines are limited, and parts of the evaluation and dataset construction lack rigor or complete transparency.

## Excitement
3.0: Interesting — The framing is relevant and the empirical observations are useful, though not highly surprising; the metric and benchmark need more polish to be impactful.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The work raises a valuable evaluation perspective and presents suggestive evidence, but the metric design, baselines, contamination controls, and dataset transparency should be strengthened before it is ready for the main conference.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges prompt coverage limitations and costs for long-context tasks. Additional points to discuss:
- Dual-use: Showing that LLMs fail under missing-gold conditions could motivate more responsible deployment with abstention, but it could also be misused to overstate LLM unreliability without nuance.
- Language and domain coverage: KNOW-NO is English-only and focused on banking intents, elementary MC reading, and NLP equations; generalization to other domains and languages is untested.
- Human labor: Clarify annotation load and compensation, if any, for EQUINFER filtering and human evaluation.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Prompts are summarized and settings given, but No-Hint adjudication details, EQUINFER filtering specifics, and code are not yet available; manual elements limit exact replication.

## Datasets
3: Potentially useful — EQUINFER could be useful if released with detailed documentation and quality controls; the BANK-77 and MC-TEST subsets are less distinctive but still serviceable in this new evaluation setup.

## Software
2: Documentary — If released as described, scripts for prompting, parsing, and computing OMNIACCURACY will be mainly useful to reproduce reported results and to test other models; broader utility depends on adding robust mappers and abstention baselines.