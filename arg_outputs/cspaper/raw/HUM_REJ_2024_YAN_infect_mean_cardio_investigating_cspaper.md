# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper presents S-MedQA, a version of MedQA annotated with 15 clinical specialties using GPT-3.5 plus majority voting across five prompts and expert validation. The dataset is released in three variants controlling the accuracy versus coverage trade-off (3+, 4+, 5 votes). Using S-MedQA, the authors probe two hypotheses about the role of instruction-tuning data for medical LLMs: H1, that gains are not from knowledge injection, and H2, that gains mostly reflect learning style or format. They conduct cross-specialty fine-tuning and testing on six major specialties with several 7B–13B open models, and a corruption test where training answers are randomized. Results show that fine-tuning improves accuracy, combined multi-specialty training helps most, single-specialty training often transfers best to other specialties, and learning with wrong answers collapses performance to near random. The paper argues that instruction data is necessary and its effect is not explained solely by style or format.

## Summary Of Strengths
- Resource contribution with pragmatic specialty annotation pipeline:
  - Figure 1 clearly lays out the data construction workflow, including five-prompt majority voting and expert verification, which increases transparency.
  - Table 1 succinctly quantifies the accuracy–coverage trade-off across 3+, 4+, and 5-vote thresholds, offering users a controllable choice.
  - Table 3 details per-specialty training counts under different vote quorums, which is helpful for downstream experimental design.
- Empirical evaluation addressing timely questions on instruction tuning for medical QA:
  - Cross-specialty matrices in Table 2 and Appendix Tables 5–7 provide a comprehensive view of transfer patterns, including combined-specialty training.
  - The simple but informative “wrong answers” corruption test directly interrogates the “style only” hypothesis and shows large degradations toward random.
- Attention to evaluation bias:
  - Section 3.2 and Figure 3 describe moving beyond first-token probability and string matching by building a classifier to map free-form outputs to options, which is aligned with recent findings on selection bias in multiple choice QA.
- Clarity:
  - The paper is generally readable, with explicit prompts provided in the appendix and key hyperparameters summarized, supporting replicability.

## Summary Of Weaknesses
1) Causal interpretation of cross-specialty transfer is not sufficiently supported.  
- In Section 4 and Table 2, the claim that “improvements cannot be solely explained as extra knowledge injection” relies on the observation that the best single-specialty fine-tuning for a test set is often a different specialty. This does not rule out knowledge transfer, nor does it isolate confounders such as sample-size disparities, question-type overlap across specialties, or shared general medical reasoning. Table 3 shows sizeable training-size differences across specialties, and Table 2 confirms the combined dataset is best on average, which strongly suggests data volume and diversity effects. A stricter test would match training sizes across specialties, control for question difficulty, and analyze content overlap. Without such controls, the inference about knowledge injection is weak.

2) The corruption experiment entangles “style vs content” with catastrophic forgetting and label-noise training dynamics.  
- Table 2 “Wrong answers” shows collapse to near 25%. However, this setup trains the model to map questions to systematically wrong labels, which is expected to harm any knowledge the model had and does not isolate style learning. A better control would preserve correct labels but perturb only stylistic features, or use style-transfer prompts on correct data. As written, the experiment does not conclusively address whether instruction tuning primarily teaches style.

3) Limited model coverage and missing medical-specialized baselines.  
- The main results focus on Llama2-Chat 7B/13B and Mistral 7B v0.1/v0.2. There are no comparisons to medical-pretrained open models beyond a citation to BioMistral. Including medical LLMs or clinical-aligned adapters would substantively strengthen the conclusions about specialty transfer and the role of instruction data.

4) No statistical significance analysis or variance reporting.  
- Section 3.2 introduces shuffling and a classifier to reduce instability, which is good, but Table 2 and Appendix Tables 5–7 report only point estimates. Differences across single-specialty trainings are modest and could be within noise. Without confidence intervals or tests, the “5 out of 6 best not same-specialty” narrative could be explained by variance.

5) Potential measurement error from the classifier-based evaluation is not quantified for impact on conclusions.  
- Section 3.2 reports 96.5% accuracy for the answer-mapping classifier trained on 600 responses. Figure 3 visualizes the approach. However, there is no sensitivity analysis showing how a 3.5% mapping error affects Table 2 conclusions, especially when per-cell differences are a few points. A calibration on a larger, independent human-labeled set or per-specialty error rates would increase trust.

6) Specialty annotation choice is single-label only, which the authors acknowledge as a limitation, but the ramifications for evaluation are underexplored.  
- The dataset omits ambiguous or multi-specialty cases. This could bias cross-specialty conclusions by removing real-world overlaps. It would be useful to report how many omitted items would otherwise alter class distributions and whether transfer patterns persist if such items are included with multi-labels.

7) Construction reuses MedQA questions rather than introducing new items specifically designed to disentangle reasoning versus knowledge.  
- While practical, this constrains the ability to probe the central hypotheses. For example, without structured reasoning artifacts per specialty or diagnostics about which medical subskills are being exercised, it is hard to attribute transfer to knowledge, format, or reasoning templates. The paper would benefit from error analyses by question category, reasoning type, and specialty overlap.

8) Lack of controls on training size and curriculum.  
- The six selected specialties have different numbers of training samples (Table 3). Matching per-specialty training sizes or training on controlled random subsets would remove volume confounds. The combined dataset results in Table 2 are consistent with the volume hypothesis, yet the paper does not directly test volume-matched scenarios.

9) Missing ablations on the majority-vote threshold used during annotation when downstream tuning and evaluation are conducted.  
- Table 1 shows a strong accuracy–coverage trade-off, but experiments are presented only for the 3+ variant. It would be informative to report model performance and cross-specialty transfer patterns across the 4+ and 5 variants to test whether annotation noise shifts the conclusions.

10) Minor but noticeable exposition issues:  
- Appendix Table 6 has a row “Neuroy,” likely a typo, and Section A.7 has hyperparameters but omits some critical details such as optimizer and number of training steps per experiment. A concise threat-to-validity paragraph in the main paper would help contextualize all constraints of the evaluation.

Explicit engagement with figures and tables:  
- Figure 1 is a strength for transparency. That said, its left-to-right flow hides a crucial detail: only a single specialty label is retained per instance. Readers would benefit from a panel or caption note quantifying how many items were discarded due to multi-specialty ambiguity and how that shapes specialty distributions used later.  
- Figure 2 shows a long-tail specialty distribution. The decision to focus on only the top 15 specialties, then restrict experiments to 6, ought to be justified with a concrete analysis of whether these 6 are representative across dimensions beyond sample size.  
- Figure 3 introduces the classifier evaluation. While it motivates moving beyond first-token probability, the figure and accompanying text do not provide per-specialty or per-model error breakdowns. Given that the main findings hinge on small deltas in Table 2, a per-cell error bar or a confusion analysis for the classifier would meaningfully support the claims.  
- Table 2 is central to the argument. Several cross-specialty entries differ within a few absolute points, which, absent statistical testing, might not indicate a real transfer preference. For example, on Cardio, Infect at 57.0 vs Cardio at 55.8 is a slim margin that could be within noise, so using these margins to question knowledge injection requires caution.  
- Appendix Tables 5–7 reveal that Mistral v0.1 displays a different pattern than v0.2, sometimes favoring same-specialty training. This heterogeneity weakens any global conclusion about instruction data’s role and deserves front-and-center discussion.

## Potentially Missing Related Work
1) Solomou et al., “Enhancing Medical Specialty Assignment to Patients using NLP Techniques,” 2023 — directly relevant to specialty classification strategies; discuss in Section 2.1 as alternative modeling choices and evaluation comparisons for label quality.  
2) Ray et al., “Do Clinical Question Answering Systems Really Need Specialised Medical Fine Tuning?,” 2026 — very close to the paper’s thesis; compare empirical designs and conclusions in Section 4 and the Introduction, and consider as an external point of reference for the knowledge injection claim.  
3) Guo et al., “Structured Outputs Enable General-Purpose LLMs to be Medical Experts,” 2025 — propose structured outputs that could influence cross-specialty transfer; add to Related Work and consider as an additional baseline or discussion point in Section 4.  
4) Vladika et al., “MedREQAL: Examining Medical Knowledge Recall of Large Language Models via Question Answering,” 2024 — complements the knowledge-injection question; cite in Introduction and discuss how S-MedQA could be used to measure recall vs transfer.  
5) Yagnik et al., “MedLM: Exploring Language Models for Medical Question Answering Systems,” 2024 — broad baselines across medical QA; integrate into Related Work and consider comparisons in Table 2 setup.  
6) Moukheiber et al., “EchoQA: A Large Collection of Instruction Tuning Data for Echocardiogram Reports,” 2025 — a single-specialty dataset useful to contrast with multi-specialty S-MedQA; discuss in Section 2 and suggest evaluation on EchoQA as a cardiology stress test.  
7) Vladika et al., “Facts Fade Fast: Evaluating Memorization of Outdated Medical Knowledge in Large Language Models,” 2025 — relevant to what instruction tuning injects and retains; add to Section 5 as future work and a complementary analysis dimension.  
8) Xiao et al., “Beyond MedQA: Towards Real-world Clinical Decision Making in the Era of LLMs,” 2025 — critiques MedQA and motivates richer evaluation; cite in Introduction and Limitations to position S-MedQA within the path to more realistic clinical tasks.  
9) Thapa et al., “Disentangling Reasoning and Knowledge in Medical Large Language Models,” 2025 — directly addresses the paper’s central dichotomy; discuss in Section 4 and consider applying their taxonomy to S-MedQA.  
10) Avnat et al., “Performance of large language models in numerical vs. semantic medical knowledge,” 2024 — informs analyses by knowledge type; consider in Section 4 for error analysis suggestions.

## Comments Suggestions And Typos
Actionable suggestions for authors:
- Control for training set size and difficulty. Re-run single-specialty fine-tuning with equal numbers of training examples across specialties, sampled multiple times to measure variance. Report confidence intervals in Table 2. This will clarify whether the observed cross-specialty maxima are robust or volume-driven.
- Add a style-only control. Keep correct answers fixed while altering only stylistic surface features or response formats in training prompts. Alternatively, distill style from corrupted data into a small adapter while freezing the base model, then re-enable learning with correct labels to disentangle style from content.
- Provide a sensitivity analysis for the classifier-based evaluation in Figure 3. Calibrate on a larger human-labeled set and report per-specialty accuracy of the classifier and how its error could shift Table 2 conclusions. Consider sampling a subset of model outputs for direct human adjudication and compare.
- Explore the annotation threshold in downstream results. Train models on 3+, 4+, and 5-vote variants and report whether cross-specialty patterns and “wrong answers” effects persist as annotation noise decreases.
- Augment analysis with qualitative error breakdowns. For example, bucket questions by reasoning type or by overlapping medical subtopics across specialties. Visualize transfer patterns with respect to these buckets to connect the empirical patterns in Table 2 to interpretable mechanisms.
- Baselines. Include one or two medical-pretrained LLMs and an instruction-tuned variant with structured outputs to test whether such training changes the cross-specialty transfer patterns on S-MedQA.

Typos and minor issues:
- Appendix Table 6: “Neuroy” should be “Neuro.”  
- Section A.7: list optimizer, scheduler, and the exact number of update steps.  
- Section A.6 prompt example: ensure temperature and special characters are normalized and there are no encoding artifacts like “0b0”.

What could change my evaluation:
- Evidence from size-controlled, variance-aware experiments that preserves the cross-specialty maxima patterns.  
- A style-only control that cleanly isolates format learning from content, confirming that content drives gains.  
- Stronger evaluation validation, for example, per-specialty classifier calibration and human adjudication, that shows the main claims stand even under stricter measurement.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
2.5 Between potentially interesting and interesting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.  
Justification: The dataset contribution is useful and the evaluation tackles timely questions. However, key conclusions about knowledge injection versus style are insufficiently isolated, and several confounds remain unaddressed. The classifier-based evaluation needs stronger calibration, and statistical rigor and size-controlled analyses are missing. With the suggested additions, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges domain scope and single-label annotation. Impact discussion could be expanded:  
- Potential harm if specialties are mis-assigned and models are evaluated or deployed based on misleading specialty competence.  
- Risks of teaching models incorrect associations in the corruption experiment, and the message that careless fine-tuning can erase beneficial medical knowledge.  
- Language and regional biases inherited from MedQA and the specialty taxonomy, plus the risk of underrepresenting certain specialties.  
- Consider including a short Responsible Use statement noting that S-MedQA is not a clinical decision tool, and evaluations should not be used to justify deployment without clinical validation.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.  
Reasoning: Prompts, high-level hyperparameters, and dataset variants are provided, but full training details, code for the classifier, and statistical reporting are incomplete.

## Datasets
4 Useful: I would recommend the new datasets to other researchers or developers for their ongoing work.  
The specialty annotations and multiple vote-threshold variants are valuable.

## Software
3 Potentially useful.: Someone might find the new software useful for their work.  
If the classifier and evaluation scripts are released with documentation, this could rise to 4.