# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies persona attribute extraction from dialogue when transferring from a “real-world” chit-chat training domain (PersonaChat-derived PersonaExt) to a different narrative setting (the fantasy LIGHT world). It fine-tunes a BART-based seq2seq extractor on a relabeled dataset, PersonaExt-PeaCoK, that maps PersonaExt relations to PeaCoK’s relation schema. The main contribution is two post-hoc, persona-centric NLI-based procedures applied to the extractor’s outputs in the new domain: (1) NLI Re-Rank, which generates multiple candidate triplets and re-ranks by entailment scores from a Persona-NLI model; and (2) Neutral Removed, which filters out candidates not entailed by the utterance. On LIGHT, the authors use intrinsic, non-reference metrics and small-scale human evaluation to show that Neutral Removed reduces false positives and yields a higher acceptance ratio of extracted triplets than baselines. Figures 1–3 illustrate the setting and the NLI post-hoc workflow; Tables 1, 14, and 15 report the main results.

## Summary Of Strengths
- Clear and relevant problem: adapting persona extraction to out-of-narrative settings is practical and underexplored. The focus on reducing hallucinations via NLI is well-motivated.
- Post-hoc design: both NLI Re-Rank and Neutral Removed can be added to existing generators without retraining them, which is valuable for deployment and for future datasets.
- Careful positioning of PeaCoK relations: mapping PersonaExt to PeaCoK makes the extracted outputs more generalizable across narratives.
- Figures support understanding:
  - Figure 2 concretely illustrates a domain-transfer failure where a chit-chat–trained extractor hallucinates “Prince” as the musician rather than a royal title; the panel also shows how the NLI Re-Ranking corrects this failure.
  - Figure 3 provides a step-by-step schematic of candidate generation, NLI scoring, and Neutral Removed filtering; it makes the proposed post-hoc pipeline easy to follow and shows how non-entailed candidates are crossed out.
  - Figure 1 demonstrates a downstream use-case by visualizing a PeaCoK-style persona knowledge graph for LIGHT characters, highlighting that extracted triplets can populate a structured resource.
- Measurable impact in human study: In Table 1, the Diverse Beam + Neutral Removed configuration yields the highest “Ratio Accepted” (0.60) by human judges, suggesting that entailment-based filtering improves precision in the new domain.
- In-domain extractor is competitive: On PersonaExt-PeaCoK (Table 4 and Table 7), the authors’ BART extractor outperforms PAED when fine-tuned on the relabeled dataset, giving a solid in-domain baseline before applying NLI post-hoc steps.

## Summary Of Weaknesses
1) Evaluation design and scale on LIGHT is limited and may bias conclusions.
- The human evaluation uses only 10 characters and 2 annotators, one being an author (Section 5.2, Appendix D), which risks bias. Inter-annotator agreement is only moderate (Krippendorff’s α=0.65 for overall Yes/No and 0.54 for fine-grained labels, Table 1 and Table 14). This small sample makes it hard to claim robust gains in new domains. A larger, fully external annotation with pre-registered protocols would strengthen claims.

2) Ambiguity and issues in the Persona-NLI training/results.
- Section 4.1 states: “Persona-NLI achieved a macro-F1 of 0.60 … which is a large increase compared to the base model (without fine-tuning) with an F1 of 1.0.” An F1 of 1.0 is perfect and cannot be improved; this is likely a mistake. If the base model indeed scored 1.0, fine-tuning to 0.60 is a severe degradation. If this is a typo, the correct numbers must be reported. Since Persona-NLI underpins the main contribution, this inconsistency undermines confidence in the post-hoc methods.

3) Limited baselines for the core out-of-narrative adaptation claim.
- Beyond the authors’ own extractor with and without NLI post-hoc, there is no comparison to alternative adaptation techniques that do not rely on NLI, such as: prompt- or instruction-tuned LLM extractors, domain-adaptive fine-tuning of the extractor using weak labels from LIGHT descriptions, or prior persona extraction methods applied zero-shot to the new setting. The paper removes Beam Search comparisons and focuses on Greedy vs. Diverse Beam, which are decoding choices rather than adaptation baselines. This makes it hard to isolate the benefit of NLI versus other, possibly simpler, adaptation strategies.

4) Intrinsic metrics are not clearly predictive of human acceptance, but the paper does not reconcile this gap.
- Section 5.3 notes the “lack of clear relationship between the intrinsic, quantitative metrics and the manual annotations.” For instance, Table 15 shows similar coverage and “first person” across methods, while Table 1 and Table 14 show modest differences in acceptance ratios. The paper should better analyze why intrinsic metrics fail to correlate, propose improved diagnostics, or adjust the metrics to better reflect content precision and usefulness.

5) Neutral Removed trades recall for precision, but gains are modest and sometimes ambiguous.
- Table 1: Persona Recall drops from 0.34 (Baseline) to 0.25 (Neutral Removed, Diverse Beam), with acceptance increasing from 0.57 to 0.60. The relative improvement in accepted ratio is small compared to the large drop in coverage and total extractions (from 67.09 to 37.66 persona per character on average). For Greedy, the acceptance ratio even decreases (0.56 to 0.55). Without statistical tests, it is unclear if these differences are reliable.

6) The “silver” recall definition may inflate or obscure conclusions.
- The “Persona Recall” metric uses description sentences as silver references but computes recall using dialogue-extracted triplets without NLI post-hoc on the description side (Section 5.2). Given the mapping from free-form description sentences to PeaCoK-style triplets is nontrivial, it is unclear how well this approximates true recall. Also, because description sentences all contain persona, not filtering on that side could bias comparisons.

7) Limited analysis of failure cases and error types for the NLI steps.
- While Figure 2 and Figure 3 give qualitative insights, there is no systematic error taxonomy for where NLI Re-Rank helps or hurts, nor for typical Neutral Removed false negatives. For example, are most removals due to lexical mismatch, tail paraphrases, or relation mismatches? A confusion analysis would help users decide when to use strict filtering.

8) No statistical significance testing.
- The human acceptance ratios and intrinsic metrics are presented without confidence intervals or significance tests. Given the modest deltas and small-scale human evaluation, it is hard to assert meaningful superiority.

9) Reproducibility gaps around data transformation and NLI training protocol.
- The PersonaExt-to-PeaCoK label mapping (Appendix B.1, Table 11) is described but code is not released, and some tails are synthetically formed phrase fragments (Tail Phrase Creation), which may affect quality. The NLI augmentation (Section 4.1) adds negative examples by permuting relation types; further details on sampling, class balance, and whether hard negatives or lexical hardening were used would benefit reproduction.

10) Scope of narrative generalization is narrow.
- Only LIGHT is tested as the out-of-narrative domain. The claims about “new narrative settings” would be stronger with at least one more distinct narrative dataset (e.g., KOTOR, Torchlight II, or a prose-to-dialogue converted dataset) to demonstrate breadth.

Engagement with Figures and Tables
- Figure 2: Strong illustration of a precise failure mode (domain-specific polysemy “Prince”) and the corrective effect of NLI re-ranking. It supports the main claim that post-hoc entailment can reduce egregious hallucinations.
- Figure 3: The three-stage pipeline diagram clarifies how candidates are generated (left), scored (center), and filtered (right). It directly supports Sections 4.2 and 4.3, operationalizing the post-hoc methods.
- Figure 1: The knowledge graph snapshot shows that extracted triplets can populate multi-character graphs. While it is a qualitative showcase, it helps readers see the downstream artifact the methods aim to improve.
- Table 1 and Table 15: They present aggregate metrics over characters and overall extractions. Table 1’s “Ratio Accepted” is crucial because it is the only human-grounded quality indicator. The improvements are small and not uniform; Greedy + Neutral Removed lags its own baseline. The authors should quantify variance and significance.
- Table 4 and Table 7: They establish the extractor’s in-domain competitiveness and the impact of different prompts/templates. This is useful context, but the main claim rests on Table 1 and Table 14.

## Potentially Missing Related Work
1) Han et al., “Persona Extraction Through Semantic Similarity for Emotional Support Conversation Generation,” 2024 — Proposes an automatic persona extraction framework (PESS) emphasizing persona completeness and consistency via semantic similarity losses. Directly relevant as a competing pipeline for improving persona extraction quality; should be discussed in Related Work (Section 2) and, if feasible, adapted as a baseline for out-of-narrative evaluation in Section 5.

2) Hong et al., “Dialogue Language Model with Large-Scale Persona Data Engineering,” 2025 — Introduces PPDS, including a dedicated persona extraction system to build large-scale persona-grounded datasets. Highly relevant to automated persona construction; should be added to Section 2 and contrasted to NLI post-hoc refinement. If code or outputs are available, include as a baseline or at least a discussion point in Section 5.

3) Li et al., “Hello Again! LLM-powered Personalized Agent for Long-term Dialogue,” 2025 — Presents dynamic persona modeling with explicit extraction modules for long-term agents. While focused on long-term sessions, its extraction techniques are a pertinent alternative to NLI filtering; compare in Section 2 and discuss applicability to narrative shifts in Section 6.

4) Lee et al., “P5: Plug-and-Play Persona Prompting for Personalized Response Selection,” 2023 — Offers a plug-and-play zero-shot approach that achieves personalization without explicit extraction. Although it addresses response selection, it serves as an alternative paradigm for adapting to new settings; cite in Section 2 and mention in Section 6 as an alternative to extraction-first pipelines.

5) “Extracting user profile via large language models and ontologies,” 2022 — Presents a multi-step method to convert dialog into structured profiles using ontologies and LLMs. Conceptually aligned with turning conversation into structured attributes; include in Section 2 and contrast the ontology-based validation with NLI-based filtering in Section 4.

6) “Zero-Shot Dialogue Relation Extraction by Relating Explainable Triggers and Relation Names,” 2023 — Frames dialogue relation extraction via an NLI-style approach. Methodologically similar to your NLI-based validation; discuss in Section 2 and connect to the entailment framing in Section 4, possibly as a pre-reranking scoring alternative.

7) “Personalizing Task-oriented Dialog Systems via Zero-shot Generalizable Reward Function,” 2022 — A contrasting personalization approach that avoids explicit extraction. Add to Section 2 as an alternative personalization strategy and discuss in Section 6 why explicit persona extraction plus validation is preferable for narrative-domain transfer.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify the Persona-NLI performance discrepancy in Section 4.1. The statement that fine-tuned Persona-NLI obtains macro-F1 0.60, which is “a large increase” over base F1=1.0, is contradictory. Provide correct numbers and explain the domain-shift effects. Since Persona-NLI underpins your main methods, please include a detailed calibration and an analysis of error types.
- Report significance: For Table 1 and Table 14, add confidence intervals or bootstrap significance tests over characters and items. Given small human eval size and moderate agreement, quantify uncertainty before drawing conclusions.
- Expand human evaluation: Increase the number of characters, ensure both annotators are independent (no authors), and report per-category precision/recall against a richer, adjudicated gold. Also include a stratified analysis by character type and by relation category (e.g., “characteristic” vs “goal_plan”).
- Add baselines that speak directly to the adaptation claim: Examples include (a) domain-adaptive fine-tuning of the extractor using weak supervision mined from LIGHT descriptions; (b) prompting a strong LLM to extract PeaCoK triplets zero-shot; (c) training an NLI model that incorporates dialogue-specific negatives and lexical paraphrases as hard negatives; and (d) a calibration-only reranker without NLI, to isolate the unique contribution of entailment.
- Improve intrinsic metrics: Given the weak correlation with human acceptance, consider precision-oriented proxies, e.g., NLI-validated precision@k, contradiction rate, or entailment confidence histograms per method. You could also add a small, adjudicated gold subset of LIGHT utterances to enable reference-based precision/recall for at least a diagnostic slice.

Typos and minor issues:
- Section 4.1: “Persona-NLI achieved a macro-F1 of 0.60 … a large increase compared to the base model (without fine-tuning) with an F1 of 1.0.” This is inconsistent; please correct.
- Section 3.2: “Evaluation … shown in our results as ‘Triplet’.” Consider standardizing capitalization and naming conventions across tables.
- Table formatting: Some tables lack explicit units or clearer captions explaining “Coverage (unique)” and “Overall Ratio Accepted.” Consider harmonizing column names between Tables 1 and 15.
- Appendix B.1: Tail phrase creation sometimes yields ungrammatical tails; note this limitation earlier in the main text where training data is first introduced (Section 3.1).

Criteria that could raise my score:
- Correct and clarify the Persona-NLI performance reporting, and provide a more rigorous evaluation of Persona-NLI itself (including ablations on negative sampling and hard negatives).
- Expand human evaluation with independent annotators, larger sample size, and significance tests; demonstrate consistent gains for Neutral Removed or NLI Re-Rank.
- Add competitive adaptation baselines and, if feasible, results on another narrative dataset. If your approach still wins (or is clearly more precision-friendly), I would be inclined to elevate to Findings (3.0) or main conference (3.5–4.0) depending on strength.
- Provide code and data release, including the mapping scripts for PersonaExt-to-PeaCoK, generation and NLI scoring code, and the processed LIGHT subset.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure about the evaluation, but some ambiguity remains due to the NLI performance inconsistency and limited human eval details.

## Soundness
3: Acceptable — The study supports its main claims to a reasonable degree, but stronger baselines, corrected NLI reporting, broader human evaluation, and significance tests are needed.

## Excitement
2.5: Between potentially interesting and interesting — The post-hoc NLI angle is sensible and practically useful, but the empirical gains are modest and the current evaluation does not fully convince.

## Overall Assessment
2.5 Borderline Findings — The core idea of entailment-based post-hoc filtering for persona extraction in new narrative settings is practical and relevant, and the paper is close to Findings quality. However, issues with Persona-NLI reporting, modest and sometimes ambiguous gains, limited human evaluation, and missing adaptation baselines prevent a higher recommendation at this time. With corrected NLI results, stronger and broader evaluation, and added baselines, this could move to Findings or borderline main conference.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper lists main limitations, chiefly the assumption of access to dialogue and the risk of impersonation. Additional aspects to discuss:
- Bias and stereotyping: Persona extraction and NLI filters trained on PersonaChat-style data may encode social biases; failures in new narratives could disproportionately misclassify certain roles or identities. Consider bias probes or toxicity screening over extracted tails.
- Domain overreach: Aggressive filtering may disproportionately remove valid but stylistically distant persona attributes in specialized narratives (e.g., archaic or magical terminology); a failure analysis by lexical novelty would be helpful.
- Dual use: While intended for fictional characters, similar pipelines can be applied to real users; outline consent, privacy, and opt-out mechanisms in potential deployments.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many details are provided, but code and data mappings are not yet released; NLI augmentation details and mapping scripts are needed for straightforward reproduction.

## Datasets
3: Potentially useful — PersonaExt-PeaCoK is a useful relabeling; if released with scripts and mappings, it could be valuable.

## Software
3: Potentially useful — If released, the pipeline for candidate generation, NLI scoring, and filtering would be helpful to practitioners seeking post-hoc quality control.