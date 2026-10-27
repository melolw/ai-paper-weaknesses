# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes TEAM-PHI, a multi-agent framework for automatically evaluating and selecting PHI de-identification systems without relying heavily on gold-standard annotations. Multiple LLM-based de-identification (De-id) models produce structured PHI outputs for clinical notes; then several LLM “Evaluation Agents” independently judge the correctness of predicted entities and output structured counts. An LLM-based majority voting mechanism aggregates these judgments in two modes (independent and cross-informed) to yield a single ranking. Experiments on 100 fully annotated notes mask the gold labels during primary evaluation and later compare TEAM-PHI rankings with supervised evaluation and a small human study. The authors report that Llama-70B consistently emerges as the top De-id model under TEAM-PHI and that this agrees with gold-standard F1 and human preferences.

## Summary Of Strengths
- Problem relevance and framing: Automatic evaluation and model selection for PHI de-identification is an important and underexplored setting, where labels are scarce and sensitive. The paper targets a clear need in clinical NLP evaluation.
- Methodological structure: The framework separates De-id modeling from evaluation and uses multiple Evaluation Agents with structured, machine-readable outputs. Equation (4) articulates the aggregation idea clearly, and Figure 1 provides an accessible schematic of the pipeline from clinical notes through De-id models to multi-agent evaluation and LLM majority vote.
- Empirical evidence for alignment with ground truth: Table 8 shows that Llama-70B has the highest overall F1 (0.62 ± 0.01), matching the framework’s selection via LLM-based voting (Table 7), which supports the claim that TEAM-PHI can approximate supervised rankings.
- Concrete, per-entity analyses: Tables 1–6 provide entity-level assessments (e.g., PERSON, DATE/TIME). The paper discusses that PERSON is relatively robust while DATE/TIME varies more by evaluator, which is a useful insight for practitioners.
- Practicality: The design encourages standardized JSON outputs for both De-id models and evaluators, which can facilitate reproducibility and auditing in regulated settings.

Specific figure/table comments:
- Figure 1: The diagram clearly conveys the end-to-end process and helps the reader understand where evaluator heterogeneity enters and how it is aggregated. It supports the paper’s claim of modularity and “black-box” treatment of De-id models and evaluators.
- Table 7: Both independent and cross-informed voting select Llama-70B most often. This concretely supports the robustness claim about aggregation improving evaluator stability.
- Table 8: Ground-truth F1 confirms Llama-70B as best overall, lending external validation to the agent-based selection result.
- Tables 1–6: Although absolute numbers vary by Evaluation Agent, the relative ranking consistency of higher-capacity models is visible across tables, lending evidence for evaluator diversity yet stable conclusions.

## Summary Of Weaknesses
1) Metric definitions and their validity without ground truth need stronger justification and clarity. In Appendix B.3, Coverage_d is defined as the sum of predictions normalized by total tokens, which is not a recognized proxy for coverage of true PHI mentions. This quantity mixes model verbosity with note length and may create per-note length bias. Similarly, RecallProxy_d divides CorrectCount by N_avg, where N_avg is the average number of PHI predictions across all agents. This assumes the average predictions approximate the total true PHI count, which is tenuous and risks rewarding overextraction if evaluators inconsistently validate. These choices drive core claims, so the paper should analyze their calibration and failure modes in depth and compare with more principled estimators.
2) Ambiguity in evaluator behavior and calibration. Section 3.4 says evaluators “validate predictions” and output only the Number of Correct Pairs as a strict JSON, yet Tables 1–6 report additional metrics like “Precision,” “Coverage,” and category scores. It is not explicit which elements come from evaluator outputs versus post-processing, and how evaluators decide span matching, boundary tolerance, and partial matches. Without clear, shared matching rules, individual agent bias may be conflated with model quality. Please specify exact span matching criteria and normalization procedures used by all Evaluation Agents, ideally with worked examples.
3) Inconsistencies across sections and results presentation. The LLM voting description in Section 3.4 refers to independent versus cross-informed voting over Evaluation Agents’ tables; however, Table 7 lists models as rows and shows both voting modes returning different single-winner assignments per model row, which is confusing. A cleaner presentation would aggregate votes across agents once and report the final winner(s) per mode. As written, Table 7 is hard to interpret and invites concerns about reproducibility of the voting step.
4) Limited size and diversity of evaluation data. The main analysis uses only 100 clinical notes from a single U.S. hospital (Section 4.1). While understandable given PHI, this small, single-institution sample limits external validity. The method’s reliance on LLM evaluators suggests that text style and domain characteristics could meaningfully affect judgments. This constrains claims on generalizability and robustness; additional datasets, even synthetic or adversarial ones, would strengthen the empirical case.
5) Lack of sensitivity analyses for Evaluation Agents. The main claim rests on “majority voting improves robustness,” but the paper does not probe sensitivity to the composition of the evaluator pool, prompt perturbations, or alternative aggregation functions. For example, how stable are rankings if some evaluators share training data or systematic blind spots? An ablation on evaluator subsets, prompts, or aggregation strategies (median, Borda count, rank aggregation) would substantiate the reliability claim.
6) Limited comparison with conventional baselines. The De-id candidates are predominantly LLMs. Prior PHI de-id work also includes strong transformer NER baselines and ensemble/rule-augmented systems. It would be informative to include some classic or rule-leaning baselines to test whether evaluators systematically favor LLM outputs or verbosity patterns.
7) Human evaluation design is underspecified. In Table 9, Q1/Q2/Q3 scales are not defined in Section 5.2, so the meaning of “0.18” or “4.20” is unclear. Without explicit scales, inter-rater agreement, and sampling protocol, it is difficult to interpret these numbers and align them with the framework’s automatic metrics.
8) Overreliance on cross-agent agreement as a correctness proxy. The approach assumes multiple evaluators reduce bias (Section 3.4), but shared biases across LLMs are plausible, particularly for sparse or ambiguous PHI categories. The Limitations (Appendix C) allude to this but the main experiments lack stress tests where evaluators are known to struggle (e.g., rare PHI types, templated versus narrative notes). This is central, since such shared bias could misrank systems with better recall on difficult entities.
9) Reproducibility gaps. The paper mentions unified prompts and JSON formats but does not include the actual prompts or detailed evaluator instructions in the main body; Appendix B references “more details” but the prompts themselves do not appear. Given the sensitivity to prompt phrasing (acknowledged in Appendix C), providing exact prompts and formatting constraints in the paper would materially aid reproducibility.
10) “AI Agent Setup” inconsistency. The paper states “we used OpenAI’s GPT-5 model as the sole AI agent” for the research workflow, while the experimental sections consistently discuss GPT-3.5 and GPT-4o as models and evaluators. This creates confusion about which models actually judged or wrote code, raises anonymity and provenance concerns, and does not match the earlier Methods. Clarify whether GPT-5 was used, and if so, how; otherwise, this section undermines clarity and trust.
11) Figure/Table-specific concern: Table 1–6 variability is very large, especially for Recall-Proxy under different evaluators (e.g., GPT-3.5’s Recall-Proxy ranges from 0.2667 in Table 3 to 0.8719 in Table 6). The paper attributes this to evaluator differences but does not quantify agreement (e.g., Kendall’s tau over model rankings, or correlation with gold F1 in Table 8). Reporting correlation between each evaluator’s ranking and gold-standard F1 would strengthen the case that the evaluators, while noisy, are directionally correct.

Why these issues matter: the framework’s contribution is an evaluation methodology that claims to be reliable without gold labels. To be convincing for high-stakes clinical NLP, the proxy metrics must be carefully validated, the voting aggregation must be transparent and reproducible, and sensitivity to evaluator composition and prompt choices must be empirically demonstrated. Otherwise, rankings may reflect evaluator bias or verbosity artifacts rather than true PHI detection quality.

## Potentially Missing Related Work
1) Posada et al., “SHIELD: A Diverse Clinical Note Dataset and Distilled Small Language Models for Enterprise-Scale De-identification,” 2026 — Introduces a diverse de-id dataset and strong distilled baselines. Directly relevant for benchmarking and could be used to stress-test evaluator generalization. Should be discussed in Related Work (Section 2) and considered in future evaluation comparisons.
2) ASQ-PHI: “An adversarial synthetic data benchmark for clinical de-identification and search utility,” 2026 — Builds adversarial test cases probing PHI leakage and over-redaction. Highly pertinent for testing evaluator robustness. Discuss in Section 2 and propose as a stress-test dataset in Section 5.
3) Cornelius et al., “Measuring the gap: correlating synthetic-to-real drift with PHI de-identification performance,” 2026 — Quantifies the synthetic-to-real drift impact, relevant since the paper includes LPPA hybrids trained on synthetic notes. Compare in Section 2 and discuss implications for evaluator reliability in Section 5.3.
4) Morris et al., “DIRI: Adversarial Patient Reidentification with Large Language Models for Evaluating Clinical Text Anonymization,” 2025 — Introduces re-identification risk as an evaluation dimension, complementary to span accuracy. Should be positioned in Section 2 and considered as an additional safety metric in Section 5.2 or as future work.
5) Shimoji et al., “Bridging the performance gap: systematic optimization of local LLMs for Japanese medical PHI extraction,” 2026 — Non-English PHI de-id; relevant to discuss multilingual generalization and evaluator portability. Cite in Section 2 and discuss extension plans in Conclusion/Future Work.
6) Gunay et al., “LLMs-in-the-Loop Part 2: Expert Small AI Models for Anonymization and De-identification of PHI Across Multiple Languages,” 2024 — Multilingual small-model de-id with GPT-4o baselines; could enrich the candidate pool and cross-lingual evaluation. Add to Section 2 and mention as potential baselines in Section 4.
7) “Automating Evaluation of AI Text Generation in Healthcare with an LLM-as-a-Judge,” 2025 — Directly related to LLM-as-judge reliability and bias in clinical text; should inform evaluator calibration and bias mitigation. Discuss in Section 2 and cite near Section 3.4 regarding judge design.
8) “Evaluation of Vision-Language Models for Detection and Deidentification of Medical Images with Burned-In PHI,” 2025 — Less central but useful for future multimodal extensions. Mention in Related Work as broader de-id evaluation context and future scope (Conclusion).

## Comments Suggestions And Typos
Actionable suggestions:
- Provide exact prompts and JSON schema for both De-id models and Evaluation Agents in the main paper or an appendix, including span matching policy (case sensitivity, punctuation, partial overlaps, normalized forms). This would directly raise reproducibility and interpretability.
- Revisit metric definitions. Replace Coverage_d with a measure that does not depend on token length, and justify or recalibrate RecallProxy_d against gold labels. At minimum, add an analysis comparing each evaluator’s Recall-Proxy to gold recall in Table 8 and report agreement metrics (e.g., Pearson/Spearman/Kendall on rankings).
- Clarify Table 7. Describe the precise input to the voting LLM, what constitutes a “ballot,” and the decision rule. Present a single, consolidated vote outcome per mode, with tie-breaking rules. Provide seeds and instructions to reproduce the LLM-voting outcome deterministically.
- Add sensitivity analyses: vary the evaluator pool (leave-one-out, use smaller/larger models), perturb prompts, and try alternative aggregations (median of ranks, Borda, Condorcet). Report how often the top-1 model changes. This will substantiate the claim that majority voting stabilizes rankings.
- Expand human evaluation details: define Q1–Q3 scales, report inter-rater agreement, sampling, and how LLM-generated checklists were used. If possible, show correlation between Q3 and gold F1 (Table 8) to triangulate evidence.

Questions for rebuttal:
- Please clarify the “AI Agent Setup” section that mentions GPT-5. Which model versions actually performed evaluation voting, code drafting, and data analysis? How does this relate to evaluators listed in Section 4.2?
- How are boundary mismatches handled by evaluators? For example, “Dr. John Smith” vs. “John Smith.” Are normalizations consistent across all evaluators?
- Do evaluators have access to raw notes and predictions only, or do they also see other models’ outputs? If any cross-model context is visible, could it bias validator strictness?

Typos/clarifications:
- Section 3.3: “The process are described in Eq.(3).” → “The process is described in Eq. (3).”
- Section 5.1: “appearing in the top-2 in 2 of 6 evaluations (≈33%) and in the top-3 in 4 of 6 evaluations (≈67%)” — but later Table 7 suggests stronger consensus. Please reconcile.
- Tables 1–6 column labels: Define whether PERSON and DATE/TIME entries are precisions or some acceptance rate; the text alternates between “recognition rate” and “precision.”

Criteria that could raise my score:
- Clearer, more defensible metric definitions with validation against gold labels, plus rank-correlation analyses; 
- Deterministic, fully specified LLM-voting procedure and sensitivity studies; 
- Resolution of the GPT-5 inconsistency; 
- Inclusion of at least one additional dataset or adversarial/synthetic stress test.

## Confidence
4: Quite sure after careful checking — I checked the core methodology, equations, and tables closely; minor details may still need author clarification.

## Soundness
3: Acceptable — The study supports its main claims in part, but metric design and aggregation transparency need strengthening; additional sensitivity analyses and clarifications are important.

## Excitement
3.0: Interesting — The problem is important and the multi-agent framing is appealing, but execution details limit enthusiasm for main-track acceptance.

## Overall Assessment
2.5 Borderline Findings: The idea is timely and relevant, and there is encouraging alignment with ground truth (Table 8). However, issues in proxy metric design, voting transparency, evaluator calibration, limited data diversity, and the GPT-5 inconsistency reduce my confidence for main-track acceptance at this time. With clearer metrics, sensitivity analyses, and improved presentation, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Appendix C discusses several pertinent limitations: small dataset, potential evaluator bias, prompt sensitivity, compute costs, and fairness/regulatory scope. I encourage adding: 
- Explicit discussion of residual re-identification risk as a complementary metric to span accuracy (e.g., DIRI-style tests).
- A note on data governance: even when using Azure HIPAA-compliant endpoints, outline policies for prompt/response logging and model memory to minimize PHI leakage risks.
- Consider fairness across demographics and clinical subdomains; report whether evaluator judgments vary across note types.

## Ethical concerns
Handling PHI is high-stakes. The paper claims HIPAA-compliant inference and local runs for open-source models. Ethical discussion could be enhanced by clarifying IRB or equivalent oversight, data retention policies, and controls against unintentional PHI re-exposure during evaluation. None of these concerns seem blocking if clarified.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Model links and metrics are provided, but core prompts, exact voting procedure, and dataset access are missing or underspecified. More details would move this toward “mostly reproducible.”

## Datasets
1: No usable datasets submitted — Understandable given PHI constraints, but it limits broader validation.

## Software
3: Potentially useful — The paper references an anonymous repository; however, without prompts, voting scripts, and mock data, independent reproduction may still be challenging. Providing full prompts and deterministic voting code would increase this to 4.