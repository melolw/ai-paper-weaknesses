# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies multilingual mental-health severity prediction using LLMs. Starting from two English social-media datasets (DEP-RED for four-way depression severity; SUI-TWI for three-way suicide risk), the authors translate posts into six additional languages with GPT‑3.5 and then prompt the same model to predict severity in each language. Results are reported per class and averaged across languages (Tables 3–4), with qualitative analyses on selected examples (Figures 4–6) and boxplots summarizing cross-language F1 distributions (Figures 2–3). The paper claims that performance varies across languages, that Turkish is consistently weakest, and that clinician oversight is necessary when deploying such systems. The authors also intend to release the translated multilingual dataset.

## Summary Of Strengths
- Topicality and relevance: Multilingual mental-health NLP is underexplored relative to English-only research; evaluating cross-language behavior of LLMs on severity prediction is of interest to the ACL community (resources and evaluation; multilinguality; ethics).
- Low-cost, scalable pipeline: The translate-then-classify workflow with a single general-purpose LLM is simple and inexpensive (Section 5.3), potentially lowering barriers for preliminary multilingual studies where resources are scarce.
- Clear, readable presentation: The paper is easy to follow overall and provides concrete prompts (Table 2), per-class metrics (Tables 3–4), and qualitative error analyses that highlight clinically meaningful confusions (Figures 4–6).
- Useful observations: 
  - DEP-RED is highly imbalanced (Table 1); the paper correctly notes that four-level depression is harder than three-level suicide ideation (§5.2.1).
  - The example-driven discussion in Figure 4 distinguishes anxiety/panic versus depression, a subtle but clinically salient point about label conflation.
- Figures bolster the central message:
  - Figure 1 gives a concise overview of the pipeline from English post to translation to prediction and evaluation, aiding reproducibility of the experimental flow.
  - Figures 2 and 3 visualize cross-language variability in F1 by class; they support the claim that language choice affects model behavior and that extremes (non-suicidal; severe depression) can either be easiest or most volatile depending on class distribution.

## Summary Of Weaknesses
1) Limited novelty and scientific depth of the core contribution
- The primary “dataset” contribution is translating two existing English datasets with GPT‑3.5. There is no human validation of translations, no measurement of translation quality, no inter-annotator agreement, and no assessment of label preservation across languages. As presented, this is closer to a convenience augmentation than a principled resource creation effort. The scientific advance is largely observational.

2) Evaluation design relies on a single proprietary model and one prompting setup
- Only GPT‑3.5‑turbo is used both for translation and classification (§5). This entwines translation and classification errors and precludes conclusions about whether weaknesses stem from translation quality, classification ability, or both. There are no comparisons to: 
  - alternative LLMs, open-source baselines, or multilingual encoders (e.g., XLM‑R, mT5),
  - classical supervised models on English or translated data,
  - two-pass designs (e.g., external MT + classifier).
- Without such baselines, the empirical findings are hard to contextualize.

3) Metric choices and reporting are confusing and risk biasing results
- Tables 3–4 report “Accuracy” per class, which is an uncommon notion; per-class accuracy is undefined unless clarified as recall or one-vs-rest accuracy. The text does not define how “class accuracy” is computed. This makes interpretation difficult.
- The “Average F1” is described as “weighted average” (Table 3 caption), but the weighting scheme is not specified. Reporting macro-F1 alongside weighted-F1 would better reflect performance on rare classes in DEP‑RED.
- Critically, the Limitations section states that when the LLM output does not contain a detectable label, the system forces class 0 (“minimum” or “not suicidal”). This introduces a systematic bias toward class 0, especially harmful for imbalanced DEP‑RED and for safety-critical positive classes in SUI‑TWI. The effect size of this decision is not quantified.

4) Dataset construction and documentation are insufficient for a resource paper
- The paper lacks fundamental details that would let others use the dataset responsibly:
  - No statistics per language (token counts, class distributions after translation, language-specific artifacts).
  - No information about cleaning, normalization, or handling of slang, emoji, or hyperlinks.
  - No quality control procedures, sampling audits, or validation by native speakers.
  - No documentation on how platform terms and user-privacy constraints are respected in redistribution; no licensing or data-sharing protocol beyond “will be available upon acceptance.”
- Figures 4–6 are informative, but they are a handful of cherry-picked examples; a systematic quality analysis (e.g., human judgments of translation adequacy/fluency and label preservation) is missing.

5) Data splits and evaluation protocol are unclear for SUI‑TWI
- Table 1 indicates “SUI‑TWI, Subset: Full, #Instances 1300,” suggesting the full set is used. The paper does not describe a standard split, cross-validation, or any held-out protocol for tuning vs. testing. Using the full dataset for evaluation without a dedicated test set risks overfitting via prompt iteration or post-hoc analysis. At minimum, a clear, leak-free evaluation protocol is needed.

6) Lack of statistical testing and variance estimates
- Results in Tables 3–4 and Figures 2–3 lack confidence intervals or statistical tests. Given the stochasticity of LLMs, even at temperature 0, API versioning and minor prompt changes can alter outputs. No robustness checks are presented (e.g., paraphrased prompts, few-shot exemplars, or multiple runs).

7) Overinterpretation of language effects without controlling for confounds
- The paper attributes Turkish underperformance to limited domain resources (p. 5–6), but no evidence is provided about the LLM’s training exposure or the MT quality into Turkish. Since GPT‑3.5 performs both MT and classification, confounds abound. Similarly, attributing German/French strength to “richer resources” is speculative without translation- and classification-disentangling experiments.

8) Prompting details are incomplete
- Table 2 lists English prompts only. It is unclear whether predictions in target languages use translated prompts or English prompts fed alongside translated posts. If prompts are localized, their exact wording per language is needed to reproduce results. If not localized, that choice should be justified, since instruction-following reliability differs by language.

9) Safety-critical annotation mismatches are treated informally
- In Figure 5, the authors suggest the ground-truth label “was probably not correctly assigned” and that the LLM “corrected this error.” This is conjecture without clinical adjudication. For mental-health severity and suicide risk, asserting that the model corrected the label is risky and should be backed by expert re-annotation or adjudication protocols.

10) Ethical and legal aspects are underdeveloped
- The paper acknowledges risks (Limitations), but several key points are missing:
  - Whether redistribution of translated user posts complies with original platform policies and dataset licenses.
  - De-identification and re-identification risks after translation.
  - Clear guidance for researchers on harm mitigation, content warnings, or restricted access.
  - A Responsible NLP checklist summary in the main text is absent.

11) Figures and tables could better connect to claims
- Figures 2–3 are useful, but they aggregate across languages without revealing per-language distributions or outliers; scatter or per-language violin plots could support the “best in Greek/German, worst in Turkish” claims more directly.
- Table 3 shows class-level “Accuracy” 0.98 for “MINIMUM” in English but an F1 of 0.25, which is counterintuitive unless “accuracy” is effectively specificity on an imbalanced set. This discrepancy warrants an explicit definition and discussion.

12) Reproducibility risks
- No code is provided; prompts per language are not included; the exact API model version, rate limits, and output parsing rules are underspecified; no seeds/checkpoints/app versions are recorded. Reproducing the exact label-parsing logic, including the “default-to-class-0” fall-back, is essential for faithful replication.

Overall, the study raises a timely question and offers some informative qualitative insights, but the experimental design and reporting do not yet meet the rigor expected for a main-track ACL paper. With stronger baselines, clearer evaluation, proper data documentation, and ethical grounding, this could become a solid Findings paper centered on analysis rather than performance claims.

Specific references to figures/tables:
- Figure 1 clearly diagrams the pipeline. However, it also makes explicit that the same LLM handles both MT and classification; this design choice should be tested against alternatives to isolate error sources.
- Figures 2–3 visualize F1 across classes; they support the class-wise variability claim, but do not reveal which languages drive the variance. A per-language overlay or small multiples would better substantiate the language-variance narrative in §5.2.2–5.2.3.
- Table 3’s per-class “Accuracy” vs. F1 inconsistencies for DEP‑RED require definition; otherwise the 0.98/0.25 pairing for MINIMUM in English is misleading and undermines interpretability.
- Table 4 shows Greek and English competitive on SUI‑TWI, partially supporting §5.2.2. Still, the large drop for “NEARLY RELATED” in some languages suggests label ambiguity; a confusion-matrix analysis would strengthen this point.
- Figures 4–6 provide valuable qualitative error cases, especially Figure 4’s anxiety-vs-depression confusion and Figure 6’s cross-language inconsistency between “Potential attempt” and “Ideation.” Turning these into systematic error taxonomies with counts would materially increase the paper’s analytical value.

## Potentially Missing Related Work
1) Raihan et al., “Large Language Models for Mental Health: A Multilingual Evaluation,” 2026 — Directly relevant multilingual evaluation of LLMs on mental-health datasets. Should be discussed in Related Work and compared experimentally where feasible; helps position this study’s translate-then-classify approach and language-variance findings.

2) Bucur et al., “A Survey on Multilingual Mental Disorders Detection from Social Media Data,” 2025 — Comprehensive survey framing multilingual mental-health NLP. Cite in Section 2 and use to situate the dataset/resource claims and open gaps.

3) Ge et al., “A Survey of Large Language Models in Mental Health Disorder Detection on Social Media,” 2025 — Survey on LLMs for mental-health detection, including prompting and evaluation practices. Discuss in Related Work to contextualize the single-model prompting design and to motivate baseline choices.

4) Mankarious et al., “MindSET: Advancing Mental Health Benchmarking through Large-Scale Social Media Data,” 2025 — Large Reddit benchmark for mental-health classification. While monolingual, it is a strong modern reference for label design, scale, and evaluation protocols; discuss in Section 2 and contrast with this paper’s translated resource.

5) Zhang et al., “Menta: A Small Language Model for On-Device Mental Health Prediction,” 2026 — Multi-task social-media classifier with deployment considerations. Relevant for comparing single-LLM prompting against compact specialized models; mention in Related Work and Discussion.

6) “GPT is an effective tool for multilingual psychological text analysis,” 2024 — Evaluates GPT for multilingual psychological assessments. Directly pertinent to claims about cross-language reliability; cite in Section 2 and discuss alongside Figures 2–3.

7) “Comparing traditional NLP and large language models for mental health status classification: a multi-model evaluation,” 2025 — Comparative framework across classical and LLM methods; motivates adding non-LLM and fine-tuned baselines; cite in Section 5 and add as baseline guidance.

8) Xie et al., “Explainable AI for Mental Health Detection from Social Media: A Comparative Study of Traditional ML and a Large Language Model,” 2026 — Highlights interpretability and comparative evaluation; cite in Discussion and consider adding explainability or error taxonomy analyses.

## Comments Suggestions And Typos
Actionable suggestions to strengthen the work:
1) Disentangle translation vs. classification errors.
- Replace or complement GPT‑3.5 MT with a strong MT system (e.g., NLLB or commercial MT) and hold GPT‑3.5 only for classification; conversely, keep GPT‑3.5 for MT and evaluate multiple classifiers (XLM‑R, mT5, smaller LLMs).
- Add an English-only control with back-translation to quantify label drift induced purely by translation.
- Report per-language translation quality with human judgments (adequacy/fluency) and a label-preservation audit on a stratified sample.

2) Fix the evaluation protocol and metrics.
- Define “per-class accuracy” precisely; add macro-F1, micro-F1, and class-wise recall/precision. Include confusion matrices for both datasets.
- Remove the “default to class 0” fall-back. Instead, enforce structured output via constrained decoding or robust parsing; report rejection rates if the model fails to comply.
- For SUI‑TWI, specify train/dev/test splits or k-fold CV; ensure no leakage and report variance across folds. Add statistical significance tests.

3) Add baselines and ablations.
- Compare to: 
  - English-only supervised baselines (e.g., fine-tuned RoBERTa on DEP‑RED/SUI‑TWI),
  - multilingual encoders (XLM‑R) tested on translated data,
  - few-shot vs. zero-shot prompting, with localized vs. English prompts.
- Report sensitivity to prompt wording and inclusion of label definitions/examples in the target languages.

4) Resource documentation and ethics.
- Provide detailed dataset cards per language: sizes, label distributions, tokenization quirks, handling of links/user mentions/PII, annotation assumptions, and translation procedures.
- Clarify licensing, redistribution permissions, and compliance with platform TOS; describe de-identification and access controls. Include a short summary of the Responsible NLP checklist in the paper.
- Avoid claiming that the LLM “corrected” mislabeled cases (Figure 5) without adjudication; if you suspect label issues, conduct an expert re-annotation study on a sample and report agreement.

5) Strengthen analyses linked to figures/tables.
- For Figures 2–3, add per-language overlays or per-language boxplots to directly support the claims in §5.2.2 about language-specific best/worst performance. 
- For Tables 3–4, add macro-F1 and confidence intervals. Discuss the large discrepancy between “Accuracy” and F1 in Table 3 MINIMUM class. Provide confusion matrices to evidence the “MILD is mishandled” claim.
- Generalize the qualitative insights from Figures 4–6 into a taxonomy with frequencies (e.g., anxiety-vs-depression confusion, indirect ideation phrasing, negation/irony, culture-specific idioms).

Typos and minor issues:
- Table 1 “Minimum” vs. “Minimal” severity naming is inconsistent; pick one.
- Table 2 prompt: “Categorize to 0 if the text is not suicidal, to 1 if the text is almost related to suicidal ideation...” — “almost related” is ambiguous; consider “indicative of suicidal ideation” to match labels.
- Figure 4 Greek text: “Το σεναίσθημα” likely a typo for “Το συναίσθημα.”
- Ensure consistent hyphenation/capitalization for “F1-score,” “F1,” “F1 score.”
- Section numbering: §5.2.x headings are nested under §5.2 but placed after §5.1; double-check consistency.

What could change my score:
- Adding robust baselines (non-LLM and multilingual models), rigorous evaluation splits with statistical testing, removal of the “default class 0” bias, and a human translation/label-preservation audit would significantly improve soundness. If these are addressed with clear gains and thorough documentation, I could raise to 3.0–3.5 (Findings to borderline main).

## Confidence
3.5 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Several methodological and reporting issues (single-model design, unclear metrics, biased fallback to class 0, unclear splits) weaken empirical validity, despite a reasonable analysis direction.

## Excitement
2.5 Between potentially interesting and interesting: The problem is relevant and the cross-language angle is useful, but the current execution limits impact.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The topic is timely and the qualitative analyses and figures are helpful, but substantial methodological, evaluation, and documentation gaps prevent a stronger recommendation.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges risks but should expand on:
- Redistribution ethics and compliance with source-platform terms; translation may modify identifiability.
- Potential harms from misclassification in high-stakes settings, especially false negatives on suicide risk.
- Cultural-linguistic shifts through translation that may distort clinical meaning; propose guardrails such as expert review before dataset release and warnings limiting clinical use.
- Over-reliance on one proprietary model may hide biases or failure modes; encourage diversity of models and public baselines.

## Ethical concerns
The work uses sensitive mental-health content and proposes releasing translated user posts. Ethical handling needs clearer articulation: licensing and TOS compliance, de-identification standards, access controls, and a formal harm-mitigation plan. Claims that the LLM “corrected” dataset labels (Figure 5) should be avoided without expert adjudication. None of these are unresolvable, but they require explicit treatment before release.

## Needs Ethics Review
Yes

## Reproducibility
2 Extremely difficult to reproduce: Critical implementation details (per-language prompts, parsing rules, exact splits/versions) are missing; only one proprietary API is used; dataset not yet available.

## Datasets
2 Documentary: The translated datasets could be useful to study the reported results, but absent validation, documentation, and licensing clarity limit broader utility.

## Software
1 No usable software released.