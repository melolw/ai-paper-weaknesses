# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper presents HAI-Coaching, a human–AI collaboration pipeline to create an expert-annotated dataset for nutrition counseling. The authors crowdsource 2,448 real struggles about diet and lifestyle, design four categories of “supportive text” with nutrition experts (reflection, comfort, reframing, suggestion), prompt ChatGPT (GPT‑3.5, late 2022–early 2023) to generate 97,920 candidate supportive statements, and have 13 experts annotate safety and quality. The dataset is analyzed quantitatively and qualitatively; notable risks are identified in sensitive topics such as mental health. The authors also benchmark multiple open LLMs and classical models on three tasks derived from the dataset: struggle classification, safety classification, and supportive text generation.

## Summary Of Strengths
- Clear resource contribution and problem framing. The paper identifies a real, under-explored NLP application, positions it against counseling and medical NLG literature, and defines a practical schema with four supportive-text categories. Figure 1 concisely communicates the intended counseling pipeline and is easy to follow.
- Substantial expert involvement. Two groups of experts contribute to taxonomy design, topic refinement, prompt engineering, and large-scale safety annotation. This is stronger than typical LLM-generated datasets that lack domain-expert oversight.
- Transparency about prompt engineering and evolving safety definition. Section 6 details a multi-iteration process to reduce harmful outputs; the final safety definition is explicit and is supported by inter-annotator agreement analysis (Table 4).
- Dataset scale and breadth. ~2.4K real struggles and ~97K model-generated candidates with expert safety labels is nontrivial for this domain. Table 3 breaks down safety by cluster and text type, making cluster-level patterns visible. Notably, mental health is clearly identified as challenging, which aligns with the qualitative analysis and ethical stance.
- Balanced quantitative and qualitative evaluation. Figure 2 shows that experts rated outputs positively on clarity/fluency/human-likeness across categories, while Table 5 provides targeted failure cases that matter clinically. This dual view is valuable for readers.
- Downstream baselines are honest and multi-faceted. The classification results (Table 6 and Table 7) and generation metrics (Table 8), plus comparisons in Table 9, make it clear that state-of-the-art open LLMs still struggle, especially without fine-tuning. Confusion matrices in Figure 3 add diagnostic value by highlighting topic confusability.
- Ethical discussion and limitations are forthright. The paper is explicit that ChatGPT is proprietary and evolving, that English-only collection limits generalization, and that mental/physical health clusters are small.

Specific figure- and table-grounded strengths:
- Figure 2: The stacked bars make the quality distribution interpretable at a glance. The predominance of “Often/Always” for clarity, fluency, and human-likeness supports the claim that surface-form quality is high even when usefulness or safety can lag.
- Figure 3: The confusion matrices show meaningful misclassifications between ENERGY_EFFORT_CONVENIENCE and MOTIVATION or SITUATIONAL, supporting the authors’ argument that boundary cases are semantically ambiguous, not just model deficiencies.
- Table 3: Provides a careful cluster-by-cluster breakdown, clearly surfacing mental health as the lowest-performing topic across all categories, which ties directly to the qualitative cautionary notes.
- Table 6 and Table 7: The contrast between zero-/few-shot and fine-tuned LLMs is instructive; fine-tuning narrows the gap, but balanced accuracy shows safety classification remains challenging under class imbalance.
- Table 9: Side-by-side qualitative outputs for generation demonstrate that fine-tuned Phi-3 mini learns the target style but tends toward generic phrasing, echoing the authors’ critique of repetitiveness.

## Summary Of Weaknesses
1) Safety labeling construct and maturation may encode biases, and its scope is under-specified. While Section 6.1 provides a useful final definition, the iterative, consensus-based process inevitably bakes in specific counseling philosophies. The paper acknowledges this qualitatively but does not analyze how “safe” vs “unsafe” varies by expert background or school of thought. Since Table 4’s Fleiss κ is only moderate for some categories (e.g., 0.38 for reframing), deeper analysis of disagreement patterns would improve validity. For example, a per-topic, per-expert confusion analysis, or reporting Krippendorff’s α with confidence intervals, would help.

2) Safety labels are binary despite nuanced risks. The domain has gradations of risk depending on user context, co-morbidities, and cultural norms. The current binary labeling can flatten important distinctions. In Table 5 Example 1, outputs are “safe but useless,” which the experts acknowledge is common. Yet such cases inflate the 85% “safe” rate reported in Table 3 and obscure downstream utility. A ternary or scalar risk/usefulness scheme, with explicit “safe-but-useless,” would be more actionable for practitioners and modelers.

3) Potential circularity and narrowness of language signal. The dataset’s supportive texts are entirely LLM-generated from one model family and one time window. This creates a single-style target for generation/fine-tuning and for safety classification. The authors partly mitigate with expert labels, but the risk remains that downstream models learn ChatGPT idiosyncrasies more than counseling best practices. The paper should quantify how often experts contributed their own counter-examples per topic (the “Exp” column in Table 3 is low overall), and consider injecting diverse human-written positives and negatives to balance the style distribution.

4) Automatic clustering is weak and the final taxonomy is partly manual. Section 5 and Appendix D show that HDBSCAN+UMAP yielded 60 noisy clusters with skewed sizes (Figure 9), which were then manually merged into 12 topics with experts. While this is defensible for a nascent domain, it makes the struggle-label ground truth partly subjective. Releasing multiple alternative labels or validation studies on the 12-topic taxonomy would strengthen the benchmark’s construct validity. Also, Figure 10’s n-gram summaries are a start, but semantic drift within clusters is not fully quantified.

5) Evaluation metrics are sometimes insufficiently aligned with task properties. For safety classification with pronounced class imbalance (~85% safe per Table 3), better metrics like PR-AUC for the unsafe class, calibration plots, and cost-sensitive analysis are needed alongside balanced accuracy. Table 7 only reports aggregate metrics and omits per-category or per-topic breakdowns; yet the error costs are topic-dependent, especially for MENTAL_HEALTH and PHYS_HEALTH_CONDITION.

6) Limited robustness checks on inter-rater alignment and sampling. The IAA analysis in Table 4 is based on a 400-sample overlap, which is modest relative to ~98K candidates. It is unclear whether these 400 were stratified by topic and category or sampled uniformly. Without stratification and per-topic κ, we cannot assess where the label noise is concentrated. This matters, since Figure 3 shows topic confusability, and Table 3 shows topic difficulty heterogeneity.

7) Over-reliance on automatic text metrics for generation. Table 8 reports BLEU, BLEURT, and perplexity, but as the authors note, these correlate poorly with human judgments on supportive counseling quality. Given the resource’s main value proposition is expert safety and perceived quality, even a modest human eval on a representative subset would make the generation section far more convincing. As written, Table 9 is informative but anecdotal.

8) Ethical pay and demographic representativeness need tighter handling. Appendix C indicates crowdworkers were paid ~$2 for a 10-minute task, which is below common best-practice rates. Furthermore, Figure 4 shows notable demographic skews. Both limitations are acknowledged, but because the dataset is intended for high-stakes counseling tasks, the paper should discuss how these factors could shape struggles’ content and, in turn, prompt-conditioned generations.

9) Missing ablations for prompt variants and instruction slots. Section 6 mentions testing chain-of-thought and impersonation; Appendix G shows initial and final prompts with “slots.” However, there is little quantitative evidence about how individual prompt elements, or the “slot” strategy, affected safety rates or usefulness across categories. Given that Table 3 reveals meaningful differences by category and topic, a compact ablation or at least a per-iteration trend plot would provide concrete insight for others reusing the prompts.

10) Dataset usability details could be clearer for replicability. While the repository is referenced, the main text should specify exact splits used for each task (Section 8 does, but briefly), data card elements (license, PII audit outcome beyond self-report), and whether multiple annotator labels per item are stored. For example, will users have access to raw individual expert votes on the 400 IaA items or only majority labels?

Figure- and table-specific critiques:
- Figure 2: “Usefulness” ratings lag notably behind “Clarity/Fluency/Human-likeness” for all categories. This discrepancy is central to the claim that “safe but useless” outputs are common, but the paper does not quantify how often usefulness ≤ “Rarely” among items labeled safe in Table 3. A cross-tabulation between safety and usefulness ratings would directly substantiate experts’ qualitative concerns.
- Table 6 and Figure 3: The confusion between ENERGY_EFFORT_CONVENIENCE and MOTIVATION/SITUATIONAL is recurrent. A per-cluster data size effect is mentioned, yet Table 6 lacks per-class F1 or support. Adding these would clarify whether errors are primarily due to small-sample topics or inherent ambiguity.
- Table 7: Reporting only macro/micro F1 and BA makes it hard to see if models are simply defaulting to “safe.” Unsafe recall and precision should be called out explicitly. As is, the conclusion “fine-tuning helps, but far from ideal” is qualitatively correct but not operationally precise for practitioners.
- Table 9: The comparison shows the fine-tuned model mimics style but sometimes drifts category-wise (e.g., folding normalization into suggestions). A small, blinded expert panel rating on adherence-to-category and safety for generated outputs would reinforce this observation.

## Potentially Missing Related Work
1) Li et al., “When LLMs Can’t Help: Real-World Evaluation of LLMs in Nutrition” (2025) — evaluates LLM-augmented nutrition support in real usage. It is directly relevant to the paper’s safety and downstream impact framing. Recommend discussing in Related Work and in Section 9 as a complementary external validity perspective.

2) Onay et al., “Artificial Intelligence in Clinical Nutrition: A Descriptive Comparison of ChatGPT- and Dietitian-Planned Diets for Chronic Disease Scenarios” (2025) — compares LLM and human diet plans in clinical contexts. Should be discussed in Section 2 and contrasted with the counseling focus here.

3) “Comparison of ChatGPT and Dietitians in Formulating Diet Plans and Recommendations for Patients with Cardiometabolic Diseases” (2026) — head-to-head evaluation with dietitians for disease-specific plans; relevant to the cautionary stance on LLM counseling, to be cited in Section 2 and the Discussion.

4) “A Behavioral Science-Informed Agentic Workflow for Personalized Nutrition Coaching: Development and Validation Study” (2025) — presents an agentic, safety-aware coaching system grounded in behavioral science. Useful to compare design choices and safety mechanisms in Sections 3 and 6.

5) Vijaybaskar et al., “Multi-Agent Reasoning in Large Language Models for Nutritions and Dietics” (2026) — proposes multi-agent frameworks for dietary guidance, citing similar safety concerns. Include in Section 8 as a contrasting approach to improve classification and generation with structured agent collaboration.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide a cross-analysis of safety vs usefulness. Since Figure 2 shows usefulness trails other qualities and Table 3 reports high safety rates, a cross-tab would reveal the prevalence of “safe but useless,” especially by category and topic. This will strengthen the practical recommendations and inform dataset filtering for training.
- Expand safety classification evaluation. Report per-class (especially unsafe) precision/recall/PR-AUC, calibration curves, and a cost-sensitive analysis. Include a per-topic breakdown to identify where models systematically fail, mirroring the insights from Figure 3 for struggle classification.
- Deepen IAA analysis. Stratify the overlapping 400 items by topic and category and report per-stratum agreement. If feasible, increase the overlap sample or release item-level multi-annotator votes for research use, especially in contentious areas like reframing and mental health.
- Add a minimal human evaluation for generation. Even a small, stratified expert study on adherence-to-category, perceived usefulness, and safety for Table 9-style comparisons would make Table 8’s automatic metrics less central and provide a clearer signal on practical readiness.
- Clarify dataset packaging. In the main paper, briefly enumerate: license; which labels are included (individual votes vs majority only); the precise train/val/test indices used for each task; and any PII scrubbing beyond instructions. If demographic skew is known (Figure 4), consider including de-identified aggregate descriptors alongside struggles to enable fairness analysis.

Minor notes and typos:
- Section 4: “We analyse ChatGPT’s performance…” consider consistent British/American spelling throughout.
- Section 6 heading: “Prompt engineering and satety annotation” → “safety.”
- Page 4, Table 2 caption: “The unclear safety is a pseudo-label…” consider rephrasing to “We denote as unclear safety those cases with consistent expert disagreement.”
- Table 3 header: Ensure consistent column labels and arrows; e.g., “Highest↑ and lowest↓ values highlighted” but some arrows appear near “Exp” counts. Clarify whether arrows denote maxima/minima for Safe% or for Exp counts.
- Section 8: Footnote markers “^2”, “^3” are interleaved within text; ensure consistent placement.
- Appendix D: “Laureate et al., 2023” in main text appears as “Caitlin Doogan Poet Laureate, Wray Buntine…” in references; verify citation formatting.

Criteria that could change my evaluation:
- Providing the cross-tab safety vs usefulness and expanded per-class metrics that reveal actionable model limitations would raise Soundness.
- Adding a small targeted human evaluation for generation and releasing stratified IAA details would increase confidence in the dataset’s reliability and the conclusions about model performance.
- Evidence that the taxonomy and labels are stable across experts with different backgrounds would mitigate construct-validity concerns.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: The study is generally sound with robust design, expert involvement, and transparent limitations. Some analyses are missing or could be strengthened, especially for safety classification and IAA stratification.

## Excitement
3.0 Interesting: The topic is relevant and the dataset is likely useful to parts of the community; the counseling focus in nutrition is timely but narrowly scoped.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses.
Justification: Strong, well-motivated resource paper with careful expert involvement and useful analyses. The main issues are the binary safety scheme, moderate IAA without stratification, reliance on a single LLM source for all supportive texts, and under-specified evaluation for safety classification and generation. With the suggested analyses and a small human eval for generation, this could solidify as a clear conference accept; as is, it is a strong Findings-level contribution and borderline for the main track.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a thoughtful limitations section and an ethics statement. Additional points to consider:
- Dual-use risk: While safety labels help, the dataset could still be used to train systems that provide overconfident guidance in high-risk cases. Clear licensing and usage guidelines are advisable.
- Demographic skew: Figure 4 suggests imbalances that may bias struggles content and thus the modeled supportive outputs. Encouraging future data collection to diversify demographics and languages is important.
- Compensation and power dynamics: Low pay for crowdworkers and unpaid expert time in some phases deserve reflection, since the dataset targets a high-stakes health domain.
- Mental health sensitivities: The paper rightly flags this; an opt-out policy or automatic gating for mental-health-related use of the dataset is worth considering.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The paper reports prompts, splits, model choices, and training parameters (Table 12). Reproducibility would be improved by explicitly releasing per-item annotator votes, the precise train/val/test indices, and per-iteration prompt ablations.

## Datasets
4 Useful: The dataset should be valuable for safety research, counseling-style text generation, and classification, provided users heed the limitations.

## Software
4 Useful.: The released code and prompts appear sufficient for replication and extension, though more ablations would enhance its value.