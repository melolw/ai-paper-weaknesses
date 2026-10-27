# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes UIEFID, a factual inconsistency detection framework for summarization that steers LLMs away from free-form NLI-style judging toward structured comparison via Universal Information Extraction (UIE). The method has three phases: Subject Alignment (SA) using NER and similarity to reconcile entity mentions between document and summary; Key-value Analysis (KVA) that extracts subject–predicate–object triplets from the summary, masks values to form a schema, then guides an LLM to extract corresponding values from the document; and Factuality Evaluation that aggregates inconsistencies into a factuality score (Equation 5). Experiments on AGGREFACT report new SOTA balanced accuracy compared with NLI-, QA-, and prior LLM-based baselines, and ablations attribute gains to both SA and KVA. The authors also claim large reductions in inference cost compared with other LLM evaluators.

## Summary Of Strengths
- Problem framing and intuition are clear. Decoupling UIE-style extraction from NLI-style reasoning is sensible and aligns with the intuition that structured matching restricts search space and improves explainability.
- Method design is concrete and easy to follow. Figure 3 gives a readable pipeline of SA → KVA → scoring, including the revision loop and where the LLM is used. Figure 4 provides a worked example that demonstrates how a masked schema constrains extraction and surfaces a contradiction (“two-year” vs “one-year” contract).
- Quantitative results are competitive. Table 1 shows UIEFID_base outperforming strong metrics like AlignScore and SummaC-Conv across AGGREFACT partitions, with the LLM-only variant ranking second. Table 2 ablations provide incremental evidence that SA and KVA each contribute, and their combination is substantially stronger than a zero-shot NLI baseline.
- Claimed efficiency. Figure 5 indicates a substantially smaller “inference cost” than several ChatGPT-style prompting baselines, consistent with the paper’s argument that schema-guided extraction is cheaper than unconstrained reasoning.
- Clarity and positioning. The paper’s core idea is consistently motivated across Sections 1 and 3 with explicit formalism (Equations 1–5) and an architecture diagram (Figure 3), which helps reproducibility and adoption.

## Summary Of Weaknesses
1) Underspecified UIE training and prompts. Section 4.2 states that a LLaMA3-8B model is “fine-tuned” for UIE, but the paper omits crucial details: training data sources, split strategy, epochs, LR, batch size, prompt templates, decoding parameters, and whether any AGGREFACT documents or summaries leak into UIE fine-tuning. Without this, the reported gains in Table 1 are hard to attribute or reproduce.

2) Factuality score definition and calibration are unclear. Equation 5 combines entity-level and key–value consistency with weights w1 and w2. The paper does not specify actual values, how they are set, or whether they are tuned per dataset. It is not clear how partial credit is assigned when a subject is realigned in SA but later fails KVA. The normalization by |sbj| and |kv_sbj_i| can bias toward summaries with many shallow attributes versus a few deep ones. This ambiguity undermines comparability across models and datasets.

3) Efficiency metric is confusing and possibly misleading. Figure 5 labels the y-axis as “Average document output character count” while the caption claims “inference cost.” It is unclear what is being measured: output tokens, input tokens, wall-clock time, or API cost. The dashed upper bound line suggests average document length rather than cost. Since UIEFID uses additional passes for SA and KVA, a token-based or time-based accounting is necessary to justify the 24–31% cost claim.

4) Subject Alignment is brittle and under-evaluated. Algorithm 1 hinges on NER accuracy, similarity thresholds, and a coreference step that is only named “Coreference” in Section 4.2 with no model version or evaluation. The “misplacement” error type is defined in Section 3.2.1 but it is not measured or exemplified. How are homonyms and cross-sentence aliases handled? What happens if SA “repairs” a summary with a wrong entity substitution, which could later mask errors in KVA? No ablation isolates SA failures or their impact.

5) Incomplete experimental reporting and significance. Table 1 likely aggregates results collected from different sources and implementations, yet the paper does not state whether all baselines were rerun in the same environment, whether thresholds were tuned per split, or whether differences are statistically significant. Table 2 reports ± values but does not specify the number of runs or seeds. Claims of SOTA would be stronger with matched conditions and significance tests.

6) Limited evaluation scope and generality. The method is validated only on AGGREFACT news datasets. The paper argues UIE benefits long documents, but presents no long-document benchmark outside AGGREFACT nor domain transfer (e.g., biomedical or dialogue). The framework’s reliance on subject–key–value triplets may struggle with highly abstractive summaries that compress relational structure, as the authors briefly acknowledge, but this is not empirically investigated.

7) Missing or weak comparisons to closely related structured evaluators and recent LLM-based detectors. The related work omits several contemporaneous systems that also constrain LLM context or use structured representations (see Missing Related Work). These are natural baselines or discussion points, especially when the core claim is higher efficiency through constrained extraction.

8) Reproducibility gaps. Beyond training details (weakness 1), several critical choices are absent: the exact prompts used to extract USI from summaries and documents, the JSON schema format, masking rules, failure handling when a key is absent in the document, thresholds for mScore in Equation 4, how ties are broken in MaxSim vs MaxSim-1 in Algorithm 1 lines 11–12, and how w1 and w2 are chosen in Equation 5. Section 4.2 mixes tools (spaCy NER, an unspecified coreference resolver) with an LLM UIE model but does not release code or configurations.

9) Explainability claims are only partially substantiated. Figure 4 is a compelling case study, and Figure 3 makes the pipeline explicit, but there is no user or human study showing that UIEFID’s outputs are indeed easier to interpret or correct than NLI-style rationales. Qualitative analysis is limited to one example, with no error taxonomy or failure case discussion beyond the high-level SA/KVA split.

10) Minor inconsistencies and clarity issues. In Table 1, the “AVG” for ChatGPT-ZS is 55.7, which seems inconsistent with the per-split numbers above 60 on multiple partitions; if the table is borrowed from prior work with different thresholds or sampling, this must be stated. Terminology around “misplacement” and “non-existent” subjects could be tightened, and Algorithm 1’s “Replace enti in summ with entmaxsim” risks silently altering hypotheses during evaluation.

Figure- and Table-specific comments:
- Figure 3: The three-phase diagram clearly shows where structured schemas are created and how inconsistencies are fed back for revision, supporting the claim of procedural explainability. However, the box “Revision” is underspecified, and it is not clear whether revisions are used for evaluation metrics or only for qualitative illustration.
- Figure 4: Strong, grounded example of a contradiction found by the schema; it supports the paper’s position. A second counterexample where the schema fails would strengthen credibility.
- Figure 5: As noted, the axis label and caption are inconsistent, and “cost” seems proxied by character count, which does not isolate model passes or latency, weakening the claimed efficiency advantage.
- Table 1: Demonstrates numerical gains; however, the paper must clarify whether all numbers were obtained under the same threshold-per-dataset policy and consistent preprocessing. 
- Table 2: The ablation supports the benefits of SA and KVA. Still, the “±” notation lacks the number of seeds, and significance is not reported.

## Potentially Missing Related Work
1) Yang et al., “SIFiD: Reassess Summary Factual Inconsistency Detection with LLM” (2024) — uses LLMs with document sentence selection to constrain context, directly comparable to UIEFID’s schema-constrained extraction. Should be discussed in Section 2.1 and considered as an LLM-centric baseline; comparisons in Section 4.3 would clarify whether UIE schemas or NLI-filtered context yield better accuracy-cost tradeoffs.

2) Luo et al., “Factual Consistency Evaluation of Summarisation in the Era of Large Language Models” (2024) — evaluates multiple LLMs as factuality evaluators and introduces TreatFact. Relevant for positioning LLM-based evaluators versus schema-guided approaches; cite in Section 2.1 and discuss after Table 1 to contextualize where UIEFID fits among evaluator prompts.

3) Zhong et al., “Discourse-Driven Evaluation: Unveiling Factual Inconsistency in Long Document Summarization” (2025) — discourse-structured evaluation for long inputs. Add to Section 2 and compare in Section 4.5 as an alternative structured representation to UIE triplets, especially given the paper’s long-document motivation.

4) Zhang et al., “Structured Discourse Representation for Factual Consistency Verification” (FDSpotter, 2025) — combines structured discourse extraction with a classifier. Discuss in Section 2.2 and compare in Section 4.3 or 4.5 regarding structured representations, explainability, and localization granularity.

5) Zhu et al., “Factual Dialogue Summarization via Learning from Large Language Models” (2024) — symbolic knowledge distillation for factuality. Although focused on generation, it is relevant for discussion in Section 5 about iterative revision and how UIEFID outputs could supervise student models.

6) Guo et al., “PlainQAFact: Retrieval-augmented Factual Consistency Evaluation Metric for Biomedical Plain Language Summarization” (2025) — retrieval + QA for specialized domain evaluation. Discuss in Section 2.1 and limitations; could be a target domain for evaluating UIEFID’s generality.

7) Zhiwen et al., “A hallucination detection and mitigation framework for faithful text summarization using LLMs” (2025) — integrated detection and correction pipeline with LLMs. Cite in Section 2 and compare in Section 5’s “Iterative Revision” to clarify how UIEFID’s revision differs and whether it improves downstream summaries.

## Comments Suggestions And Typos
Actionable questions that could change my assessment:
- Provide full UIE fine-tuning details and prompts. Exactly which datasets and splits were used? Any overlap with AGGREFACT sources or domains? Report hyperparameters and training compute.
- Clarify Equation 5. Specify w1 and w2, describe tuning protocol, and justify the normalization. Report sensitivity analysis. Explain how SA repairs are scored in FS, and whether repaired entities mask errors that should count against factuality.
- Define the efficiency metric rigorously. Report input and output tokens, number of LLM calls, and wall-clock time on a fixed hardware setup. Replot Figure 5 accordingly. If character count is used as a proxy, justify why it correlates with inference cost for your pipeline.
- Strengthen baselines and significance. Add SIFiD and at least one discourse-structured baseline. State whether all baselines were rerun under matched preprocessing and thresholds. Report statistical significance for Table 1 and number of seeds for Table 2.
- Expand qualitative analysis. Include at least 5–10 diverse examples across CNN/DM and XSum showing successes and failures. For failures, specify whether the issue lies in SA, KVA extraction, or scoring. This would directly support the explainability claim.

Other comments and minor issues:
- Algorithm 1: variable naming is confusing. Lines 11–12 use MaxSim and MaxSim-1 without a definition of “-1.” Clarify whether this means the argmax element, the next-best candidate, or an index. Define threshold selection procedure.
- Section 3.2.1: “misplacement” needs a precise operational definition and example. If it means incorrect role assignment or entity swap, demonstrate in Figure 4 or add a new figure.
- Table 1: Verify the “AVG” values, especially for ChatGPT-ZS, and ensure consistent threshold-per-dataset tuning across all methods.
- Section 4.2: Specify the exact coreference model and version. “Coreference” is not sufficiently informative for reproduction.
- Typos: 
  - Figure 3 caption: “two phase” → “two phases” elsewhere; keep consistent tense and plurality.
  - Section 4.5: “does't” → “doesn’t”.
  - Section 4.3: “categorized categorized” → “categorized”.
  - Figure 5 caption and y-axis labeling are inconsistent; fix to avoid ambiguity.

Criteria for score increase:
- Add SIFiD and at least one discourse-structured baseline with matched settings and significance reporting.
- Release code and full prompts; document UIE fine-tuning data and hyperparameters; clarify Equation 5 with sensitivity analysis.
- Replace Figure 5 with rigorous cost metrics and include a per-example breakdown of LLM calls.
- Provide a broader qualitative study including failure analysis that maps errors to SA vs KVA vs scoring.

## Confidence
3: Reasonably confident but not fully verified — I checked the method and experiments carefully, but missing training details leave room for uncertainty about fairness and reproducibility.

## Soundness
2.5: Between Poor and Acceptable — The central idea is plausible and the numbers are strong, but underspecified training, scoring, and efficiency measurement weaken the empirical support.

## Excitement
2.5: Between potentially interesting and interesting — The UIE-centric decomposition is appealing and could be useful, but the paper needs stronger evaluation and clarity to be truly compelling.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The structured-UIE angle is interesting and results are promising, but several core aspects are under-specified (UIE fine-tuning, scoring, efficiency), key baselines are missing, and reproducibility is currently limited. With the requested clarifications, stronger baselines, and rigorous cost accounting, this could move toward a stronger outcome.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges uncertainty about the best structured representation and limited coverage of LLM-generated summaries. The paper could further discuss:
- Bias propagation from NER and coreference tools and the risk of incorrect SA replacements that could mask inconsistencies.
- Language coverage. All tools and models are English-centric; multilingual applicability is unclear.
- Dual use. Automated consistency flags might be used to over-trust system outputs without human review; communicating confidence and failure modes is important.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many essential details are missing, but the overall pipeline is described and the benchmark is public.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.