# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper studies how extractive rationalization interacts with label prediction in few-shot prompting of large language models. Using GPT-4 variants across five datasets with human-annotated rationales (MultiRC, SciFact, WikiAttack, Evidence Inference, HealthFC), the authors compare multiple prompting regimes: zero-/few-shot without rationalization, predict-then-explain, explain-then-predict, providing ground-truth rationales (with or without the full document), and occluding the human rationales. They report correlations between rationale F1 and label correctness, analyze whether errors stem from missing evidence versus misinterpretation, and claim that errors are more often due to misinterpretation or extra evidence than missing evidence. The paper also presents contingency analyses to attribute error sources and observes that supplying human rationales often improves label accuracy, while occluding them hurts performance.

## Summary Of Strengths
- Topical relevance and timeliness: The work targets interpretability and analysis of LLMs via extractive rationales in few-shot settings, an active area in the ACL community.
- Multi-dataset analysis: Evaluates five datasets spanning QA, fact verification, attack detection, and evidence-based medical QA, which helps probe the generality of observations beyond a single benchmark.
- Clear experimental factors: The prompting conditions are well-defined at a high level (zero-/few-shot, explain-then-predict vs predict-then-explain, rationale provided/occluded), enabling structured comparisons.
- Useful empirical observations:
  - Table 1 and Figure 3 show strong association between rationale F1 and label correctness for SciFact, WikiAttack, and Evidence Inference; this supports an empirical tie between extractive rationalization quality and accuracy.
  - Table 2 indicates order effects, with predict-then-explain modestly outperforming explain-then-predict on several datasets.
  - Table 3 demonstrates that providing gold rationales can improve accuracy while occluding them degrades it, which is informative for system design.
- Thoughtful error attribution framing: The contingency tables (Tables 4–5) explicitly decompose error sources into missing evidence vs misinterpretation/extra evidence and necessity/sufficiency of human rationales. This framing is constructive for interpretability workflows and downstream verification protocols.
- Figure-based insight: Figure 2 illustrates a representative SciFact item where the model fails with the full document but succeeds when shown the gold evidence alone, concretely motivating the separation of retrieval and interpretation.

## Summary Of Weaknesses
1) Insufficient specification of rationale evaluation protocol
- The paper reports rationale F1/precision/recall but does not specify how spans are tokenized or matched, how partial overlaps are handled, whether evaluation is sentence-level or token-level across datasets, or how multiple predicted spans are aggregated. This is central to Tables 1–2 and Figure 3. Without these details, it is hard to assess the validity of the rationale metrics and the strength of the reported correlations.

2) Variance and stability under random exemplar sampling and stochastic decoding
- Few-shot exemplars are “randomly sampled and shuffled… separately and independently for each item” with temperature 0.7 (Section 5). However, the paper does not report variance over multiple sampling runs or decoding seeds. Given that key claims depend on relative differences across conditions (Tables 1–3), the absence of run-to-run variability and CIs weakens confidence in the conclusions. Please quantify sensitivity to exemplar choice, order, and temperature.

3) Heterogeneous model backends across datasets
- The use of gpt-4-0613, gpt-4o-2024-05-13, and gpt-4-turbo for different datasets (Section 5) introduces a confound when comparing effects across datasets (e.g., the presence/absence of correlation in Table 1 or relative gains in Table 3). The paper should either fix a single model or at least replicate key claims with a common model to show robustness.

4) HealthFC re-labeling procedure risks and incomplete reporting
- Section 3 describes re-labeling HealthFC with GPT-4 and subsequent manual review. This alters the dataset distribution and label semantics relative to the original work, which could affect both measured accuracy and rationale alignment. The re-labeling protocol, quality control, inter-annotator agreement, and final mapping are not provided. Since HealthFC drives several contrasting conclusions (e.g., Table 1 shows no significant rationale–label association; Table 3 shows large gains with gold rationales), transparency here is essential.

5) Ambiguity in “evidence-only” vs “document-plus-rationale” settings
- Figure 2B and Table 3’s “Explanation given w/o document” setting raise interpretational questions. For WikiAttack, accuracy is higher when given the rationale without the full document (0.917) than when given both (0.823), suggesting that the gold rationale may function as a label proxy. The paper should analyze whether gold rationales contain label-indicative phrasing or artifacts and quantify this effect (e.g., training a simple classifier over rationales alone as a baseline).

6) Multiple-comparison testing and small-cell statistics
- Statistical testing uses two-sided t-tests (Table 1) and McNemar (Table 2) without correction for multiple datasets/metrics. Several cells in Tables 4–5 are small (e.g., WikiAttack low-recall cells), which undermines the reliability of proportions and any inferential claims. Please include exact counts and confidence intervals for all proportions in Tables 4–5 and apply appropriate corrections or Bayesian estimation.

7) Limited generality of claims and potential overreach
- The Discussion states that results “suggest that extractive rationales are an effective way of examining LM behavior… and [that] contemporary LMs are effective at retrieving relevant in-context evidence.” Given the single-vendor setup, heterogeneous models, lack of variance estimates, and partial counterexamples (HealthFC in Table 1; WikiAttack behavior in Table 3), this phrasing feels stronger than what the data support. Tighten claims to match the presented evidence.

8) Missing operational details for key ablations
- Section 5 says exemplars for some conditions are sampled based on “low vs high claim-evidence similarity” and “frontloaded vs back-loaded evidence position,” but the paper does not define the similarity metric, thresholds, or positional binning. Since the paper’s core narrative is about retrieval vs interpretation as a function of evidence characteristics, these definitions should be explicit and reproducible.

9) Limited baselines and lack of non-LLM or smaller-LLM comparisons
- The paper frames errors as retrieval vs interpretation but does not include a retrieval baseline (e.g., sentence selection via BM25/NLI) or smaller open models prompted the same way. Such baselines would better isolate whether observed effects are specific to GPT-4(-o/-turbo) or generalize across architectures and capacities.

10) Figure/table-specific concerns
- Figure 3: The HealthFC boxplots for rationale F1 overlap substantially across correct/incorrect labels, visually undermining the “strong relationship” claim for that dataset. This nuance should be foregrounded earlier in Section 6.1.
- Table 2: Order effects are statistically significant for some datasets, but the magnitudes are small (e.g., MultiRC 0.897 vs 0.861). Please report absolute differences with CIs and discuss practical significance.
- Table 3: The anomalously high “Explanation given w/o document” accuracy on WikiAttack (0.917) vs “Explanation given” (0.823) merits deeper error analysis and perhaps a label-leakage stress test.
- Figure 2: While instructive, the single qualitative example could be complemented with aggregate analysis quantifying how often evidence-only flips incorrect-to-correct vs correct-to-incorrect and why.

11) Reproducibility gaps
- Exact prompts for each dataset/condition are not fully included; JSON schema and the post-processing for extracting evidence spans are not detailed; code, exemplar indices, and re-labeling artifacts are not released. As presented, the work is reproducible only with difficulty.

## Potentially Missing Related Work
1) Marasovic et al., “Few-Shot Self-Rationalization with Natural Language Prompts,” 2022 — Directly studies few-shot self-rationalization and co-variation of explanations and task accuracy. Should be cited in Related Work and compared experimentally or at least conceptually in Section 6, as it bears on the central questions of this paper.

2) Chen et al., “ZARA: Improving Few-Shot Self-Rationalization for Small Language Models,” 2023 — Proposes rationale–answer augmentation to improve few-shot self-rationalization, relevant to your exemplar-based manipulations. Discuss in Section 2 and compare conceptually in Section 6.2 regarding when rationales improve label accuracy.

3) Yeo et al., “Plausible Extractive Rationalization through Semi-Supervised Entailment Signal,” 2024 — Targets extractive rationales with an explain-then-predict architecture on ERASER-style datasets. Add to Section 2 and connect to your rationale faithfulness assessment near Table 1.

4) Yang et al., “Take It Easy: Label-Adaptive Self-Rationalization for Fact Verification and Explanation Generation,” 2024 — Addresses label-dependent explanation behavior and synthetic explanations in few-shot settings for fact verification. Include in Related Work and consider in Section 6.2.1 when interpreting label-specific error modes.

5) Yang et al., “Self-Rationalization in the Wild: A Large-scale Out-of-Distribution Evaluation on NLI-related tasks,” 2025 — Evaluates robustness of explanations and labels under distribution shift. Cite in Related Work and discuss in Limitations/Discussion regarding generality and OOD robustness.

6) Tapwal et al., “Faithful or Fabricated? A Causal Framework for Rationalization Bias in LLM Judges,” 2026 — Provides a causal lens and metrics for rationale–decision alignment. While your work is empirical, referencing this in Section 7 could clarify that your claims are associational rather than causal and point to future causal analyses.

## Comments Suggestions And Typos
Actionable suggestions:
- Specify the rationale evaluation protocol in detail: span granularity per dataset, tokenization, overlap criteria, alignment with human spans (e.g., sentence vs token), handling of multiple spans, and how F1/precision/recall are averaged. Provide code or pseudo-code.
- Report variability: repeat all main conditions with multiple random exemplar samplings and decoding seeds; include means, standard deviations, and confidence intervals for Tables 1–3. Consider fixed-temperature ablations (e.g., 0.0 vs 0.7) to isolate stochasticity effects.
- Normalize model choice: rerun a subset of datasets with a single common model, or add an open model for triangulation. Clarify if context-window or cost constraints mandated the heterogeneous choices, and show the key conclusions are invariant.
- HealthFC re-labeling: document the re-labeling protocol, inter-annotator agreement, and release the mapping. Add a sensitivity analysis using only original labels to ensure conclusions do not hinge on re-labeling.
- Clarify the exemplar filters: define the claim–evidence similarity metric, thresholds for “low/high,” and positional binning for “frontloaded/back-loaded.” Provide statistics showing distributions across your sampled exemplars.
- Deeper analysis of “Explanation given w/o document” (Table 3): measure how predictive gold rationales are of labels alone. For example, train a simple classifier on rationales-only and compare. Add qualitative error analysis to assess whether human rationales contain label cues.
- Expand Figure 2 analysis: quantify at scale how often “evidence-only” fixes or flips predictions; connect to the contingency decomposition in Table 4 by measuring evidence-only correction rates.
- Statistical rigor: avoid multiple uncorrected pairwise tests. Use correction or model the full design with mixed-effects where appropriate; provide per-cell counts and CIs in Tables 4–5.
- Tighten claims: soften generalized statements in Section 7 to reflect dataset- and model-dependent results, especially the counter-patterns in HealthFC and WikiAttack.

Typos/clarifications:
- Section 4: “Some rationalization error seem…” → “errors seem”
- Section 5: “introducing the possibility of unfaithful rationales with no actual relationship to the model’s label prediction” — consider briefly noting how often unfaithful rationales were observed empirically (e.g., zero-overlap cases).
- Section 6.2.1: “for two datasets… but only or HealthFC” → “only for HealthFC”
- Section 7: “correct correct label” → “correct label”
- Figure 5 caption says “Annotator Error” while the model predicted False with many correct evidence spans; clarify if this is indeed a dataset issue and, if so, quantify its prevalence.

What could change my evaluation:
- Adding full rationale evaluation details, releasing code/prompts/exemplar IDs/relabeling artifacts, and reporting variability across seeds/exemplar draws would raise Reproducibility and Soundness. 
- Demonstrating robustness with a single, common model or with an additional open model, and resolving the WikiAttack anomaly in Table 3, would strengthen the empirical case and could move my overall assessment to Findings (3.0) or higher.
- A deeper causal or controlled analysis (evidence-only aggregate flips; label-cue control in rationales) would further solidify the interpretation claims.

## Confidence
4: Quite sure after careful checking — I checked the key experimental claims, figures, and tables closely; some details are missing, but I’m confident in the main critiques.

## Soundness
2.5: Between Poor and Acceptable — The general setup is sensible and the high-level findings are interesting, but missing evaluation details, variance, heterogeneous models, and the HealthFC re-labeling ambiguity reduce rigor.

## Excitement
2.5: Between potentially interesting and interesting — The topic is timely and the framing is useful, but the empirical foundation needs tightening before it can be considered for the main track.

## Overall Assessment
2.5: Borderline Findings — The paper has promise and presents a structured, multi-dataset analysis with informative contingency breakdowns, but significant reproducibility and methodological-detail gaps, heterogeneous model confounds, and unresolved anomalies prevent a clear accept. With stronger methodological transparency, variance reporting, and robustness checks, it could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The authors acknowledge limited generality from studying a single vendor’s LLMs on five datasets. This should be expanded to discuss heterogeneous model usage and how it affects cross-dataset comparability.
- Potential societal implications include over-relying on extractive rationales as causal evidence for decisions in high-stakes domains. The paper correctly warns that claims are associational; strengthening this caveat and discussing failure modes (e.g., spurious rationales, label leakage in rationales) would help.
- Consider equity issues in datasets like WikiAttack where mislabeling or domain shifts could propagate harms if rationales are misinterpreted; add a short discussion about biases in evidence selection and how occluding/providing rationales might amplify them.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Key elements are missing (exact rationale evaluation, prompts for all conditions/datasets, multiple-seed results, exemplar IDs, and the HealthFC re-labeling artifact).

## Datasets
1: No usable datasets submitted — The paper does not release new datasets; the HealthFC re-labeling is not made available.

## Software
1: No usable software released — No code or prompts are provided.