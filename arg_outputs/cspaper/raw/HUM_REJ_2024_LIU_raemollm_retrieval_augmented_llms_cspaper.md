# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes RAEmoLLM, a retrieval-augmented framework that uses affective information (sentiment and emotion) to support in-context learning for cross-domain misinformation detection. The system has three modules: (i) index construction, which uses EmoLLaMA-chat-7B to derive affective embeddings and explicit affect labels; (ii) a retrieval module that selects top-K source-domain examples most similar to a target item in an affect-embedding space; and (iii) an inference module that prompts LLMs with these retrieved examples to classify the target as legitimate/fake (AMTCele), non-rumour/rumour (PHEME), or related/conspiracy (COCO). Experiments across several open and commercial LLMs show improvements over zero-shot prompting and random few-shot examples, with the best open model being Mistral-7B. The paper also includes affective analyses (e.g., t-tests over label groups), ablations over which affective signals to retrieve on, and small studies on the number and dimensionality of embeddings for retrieval.

## Summary Of Strengths
- Clear and timely problem framing: cross-domain misinformation detection is challenging, and minimizing fine-tuning cost is valuable for practice.
- Simple, modular pipeline: a clean RAG-style setup using affective embeddings and ICL, straightforward to understand and potentially reuse. Figure 1 helps here by clearly depicting the three stages and data flow.
- Empirical gains over zero-shot and random few-shot prompting across multiple LLMs and datasets. In Table 4, the RAEmoLLM variants consistently improve F1 over zero-shot for several model/dataset pairs, with large relative gains for weaker base models (e.g., Vicuna-7B on COCO: 0.3382 to 0.7293 when using Vreg).
- Systematic exploration of affect types: Figure 2 shows per-dataset sensitivity to which affect signal underpins retrieval, providing actionable guidance (e.g., Vreg works well for AMTCele; Ec and Vreg strong on PHEME; Eloc often stronger than EIreg on COCO).
- Statistical exploration of affect differences between label groups. Table 2 provides t-tests that consistently show significant differences in several affective dimensions, aligning with the design motivation.
- Practical efficiency analysis: PCA dimensionality reduction for retrieval and a time–F1 trade-off are explored; Figure 12 is useful for practitioners deciding on embedding dimensionality.

## Summary Of Weaknesses
1) Potential target-domain leakage in index/PCA construction
- Section 3.1.3 states that the retrieval database is built after obtaining embeddings for “all domain corpora,” and PCA is then trained to reduce dimensionality. In cross-domain evaluation, using target-domain data to learn the retrieval projection (even unsupervised) can inflate performance. Algorithm 1 uses R(D_T) and R(D_S), suggesting R (the PCA mapping) is shared and prefit. Please clarify whether PCA was trained only on source domains for each cross-domain split. If PCA used any target data, re-run with PCA fit on source-only data and re-report. This is central to claims of cross-domain generalization.

2) Missing, critical baselines for retrieval and ICL selection
- The core claim is that affect-guided retrieval improves cross-domain ICL. However, the paper compares mainly to zero-shot and random few-shot. It omits strong, standard retrieval baselines:
  - Semantic retrieval using non-affective encoders (e.g., SBERT, E5, Contriever; even TF-IDF). Without these, it is unclear if affect adds value beyond semantic similarity.
  - Non-affective LLM-derived embeddings (e.g., vanilla LLaMA/Mistral sentence embeddings) as the retrieval space.
  - A “mixed” retrieval that combines semantic and affect similarity.  
  These baselines are necessary to isolate the contribution of affectivity versus simply retrieving semantically similar examples. This gap affects the paper’s main causal narrative.

3) Statistical methodology around Table 3
- The t-tests on “top-K cosine similarities” are unusual and may not measure what the paper needs. Selecting top-K per-row and then testing differences across within-class vs cross-class pairs biases the sample toward the extreme tail and inflates separability. There is no correction for multiple comparisons, and p-values are reported as 0.000 in several places, which is not statistically sound reporting. A more conventional analysis would examine full-pair distributions, AUC/ROC for nearest-neighbour classification, or retrieval precision@K across classes. As it stands, Table 3 over-claims separability and could mislead readers.

4) Inconsistency about COCO labeling and task setup
- Appendix A.1 says Unrelated is removed for cross-domain tests. Appendix A.2 then says the instruction keeps Unrelated “to test robustness.” Table 1 shows only Related and Conspiracy counts, suggesting 2-class. Table 4 reports single F1 per dataset without clarifying whether COCO is 2-class or 3-class in inference. This inconsistency undermines result interpretability. Please state the exact label set used in each experiment and ensure consistency across tables and prompts.

5) Over-reliance on a single affective encoder, no ablation on the encoder itself
- EmoLLaMA-chat-7B is used to produce both implicit embeddings and explicit affect labels. There is no sensitivity analysis to alternative affect encoders. If the gains arise from EmoLLaMA’s general semantic capacity rather than “affectiveness,” that would change conclusions. An ablation with a comparable non-affective LLM/sentence encoder would strengthen claims.

6) Risk of domain artifacts and confounds not controlled
- AMTCele contains crowd-generated fake items and legit news from mainstream outlets; PHEME is short event tweets; COCO is topic-filtered COVID-19 data. Differences in style, length, and topicality potentially correlate with affect and with class. Without controls (e.g., content-only vs affect-only retrieval; partial text masking; semantic parity checks), improvements could be driven by confounded retrieval (topic/event cues). Appendix B figures and the PCA plots (Figures 9 and 10) visualize separability, but they do not control for these confounds.

7) Limited analysis of failure cases and class imbalance
- Table 5 and Section 4.3.3 discuss some “special cases,” but the explanation often points to data imbalance without quantitative analysis (e.g., per-class retrieval purity, confusion matrices, calibration shifts). Given cross-domain settings with skew, a deeper error analysis would be valuable.

8) Reproducibility gaps
- Important implementation details are missing: prompt templates are partially shown, but hyperparameters (temperature, top_p), stopping, and API versions for proprietary models are not fully specified. The retrieval threshold (0.2) in Algorithm 1 and K selection process are not described for all experiments. The paper references code “in Software,” but the main text contains no Software section, and no explicit link or DOI is provided. For a pipeline hinging on retrieval and prompting, these omissions affect reproducibility.

9) Evaluation framing and metrics
- The paper states weighted Accuracy/Precision/Recall/F1 are used, but discussion focuses almost entirely on F1. This is acceptable, yet some claims (e.g., “significant improvements”) would be more convincing if supported by variance estimates, confidence intervals, or pairwise significance tests on F1 across seeds/runs. For deterministic API calls, report multiple runs or bootstrapped CIs if possible.

10) Interpretation of Figure 2 without significance testing
- Figure 2 shows meaningful bars by affect dimension and “+addexpl,” but no statistical test supports differences between bars. Given the paper’s key narrative that some affect signals are better per dataset, simple paired tests across items would increase confidence.

Specific figure/table engagement
- Figure 1: The architecture diagram is clear and supports comprehension, but it also reveals a methodological ambiguity: the “Index Construction” box ingests “All domain corpus.” For a cross-domain split, this implies target-domain text helps define the index/PCA space used for retrieval. This should be source-only to avoid leakage, or at least rigorously justified.
- Figure 2: On COCO, the Eloc-based retrieval with “-addexpl” dominates almost every other affect signal, while EIreg-anger-addexpl underperforms. This pattern suggests the model may benefit from coarse-grained emotion intensity in that dataset. However, without a semantic-retrieval baseline, we cannot tell if Eloc is learning emotion or topic/stance proxies in COCO. Add a semantic-retrieval curve to this figure to ground the interpretation.
- Table 4: This is the central evidence. For Mistral-7B on AMTCele, F1 improves from 0.7127 (zs) to 0.7767 (Vreg-addexpl). On PHEME, the best RAEmoLLM variant is 0.6942–0.6935 range, still below fine-tuned BERT/RoBERTa (0.7208/0.7204), which is acknowledged in the text. On COCO, Vreg and Vreg-addexpl achieve 0.7667 and 0.7725, which is a strong gain over zs (0.5391). These are promising but would be more compelling with the retrieval baselines noted in Weakness 2 and with clarified label setup for COCO (Weakness 4).
- Table 2 and Table 3: Table 2’s t-tests support affect differences across classes, but Table 3’s “top-K similarity” statistics are methodologically problematic as noted above and should be replaced by retrieval precision/recall metrics.

## Potentially Missing Related Work
1) Liu et al., RAAR: Retrieval Augmented Agentic Reasoning for Cross-Domain Misinformation Detection, 2026 — Directly targets cross-domain misinformation using retrieval with multi-agent reasoning. Compare methodological differences and, if feasible, include as a baseline or discussion point in Sections 2.1/4.3; contrast agentic reasoning vs single-LLM ICL.

2) EmoGRL: Emotion-Guided Graph Representation Learning for Cross-Domain Rumor Detection, 2026 — Uses emotion guidance but via graph representation learning. Discuss in Section 2.1 as an alternative way to encode affect for cross-domain transfer; consider adding a graph-based baseline or at least a conceptual comparison.

3) Li et al., A Multi-Agent Framework with Automated Decision Rule Optimization for Cross-Domain Misinformation Detection, 2025 — Presents an LLM-based multi-agent pipeline for cross-domain detection. Add to Related Work (2.1/2.2) and discuss trade-offs with RAEmoLLM’s simpler single-LLM ICL.

4) Wang et al., A Graph-Enhanced Defense Framework for Explainable Fake News Detection with LLM, 2026 — Combines RAG with claim-centered graphs for explainability. Discuss in Section 2 regarding retrieval choices and explainability; consider including graph-based evidence retrieval as a future direction (ties to your Conclusion).

5) Harris et al., Multimodal misinformation detection across diverse languages using RAG and LLMs, 2026 — Multilingual/multimodal RAG for misinformation. Add to Related Work and Future Work sections; it directly connects to your proposed multimodal extension.

6) Zhou et al., Graph-prompted explainable fake news detection with multimodal LLMs, 2026 — Integrates propagation graphs with LVLMs via prompts. Discuss as an alternative prompting/retrieval strategy in Section 2.2 and potential extension path.

7) Wang et al., Are Rationales Necessary and Sufficient? Tuning LLMs for Explainable Misinformation Detection, 2026 — Focuses on rationale quality for misinformation classification. Discuss alongside your Template 2 results; explicit affect may interact with rationale generation. Consider evaluating explanation faithfulness as an auxiliary metric.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Control leakage in PCA/indexing: Rebuild the retrieval database per cross-domain split with PCA trained on source-only data. Report revised Table 4 and Figure 2. If you already do this, please state it clearly and move the statement to Section 3.1.3 and Figure 1 caption, and add a short ablation showing no material difference when including/excluding target data for PCA fit.
- Add semantic-retrieval baselines: At minimum, SBERT-base/e5-base/Contriever and TF-IDF retrieval for few-shot ICL, holding K and the prompt constant. Also try a combination score: α·cos(affect) + (1−α)·cos(semantic), with α tuned on source-only validation. This will isolate the real contribution of affective retrieval.
- Replace or complement Table 3 with retrieval metrics: Compute class-conditional retrieval precision@K and NDCG@K for within-class vs cross-class neighbors, or report a simple k-NN classification accuracy in affect-embedding space. This is more informative and avoids biased “top-K-of-top-K” testing.
- Clarify COCO label protocol: State explicitly whether COCO is 2-class or 3-class in all experiments. If different choices are made in different sections, align them or report results for both. Update Table 4 captions and Appendix A.2 to be consistent.
- Encoder ablation: Compare EmoLLaMA embeddings to non-affective LLM sentence embeddings for retrieval, and (optionally) to a smaller affect encoder. This will show the specific value of affect signals beyond general sentence similarity.
- Detailed failure analysis: Provide per-class F1, confusion matrices, and retrieval purity plots for imbalanced domains (e.g., PHEME’s small “prince/gurlitt/ebola”) to diagnose when and why RAEmoLLM underperforms zero-shot.
- Reproducibility: Report all prompt hyperparameters (temperature, top_p), API versions, and decoding parameters. Provide the exact prompts for each dataset in the main paper or a stable appendix. Include the retrieval threshold (0.2) choice and sensitivity. If code is available, include the anonymous link in the paper body.

Typos and minor issues:
- Throughout: report p-values with precision (e.g., p < 1e−6) instead of “0.000.”  
- Section 3.2 Algorithm 1: “score == cosine(…)” suggests equality checking; should be assignment “score ← cosine(…).”
- Table 1 caption: “Statistic of datasets” → “Statistics of datasets.” “Prince Toronto” should be checked against PHEME event names. Also “realted” typo appears in Table 5 (“realted joy ==0”).
- Section 4.3.1: “largest increase in PHEME is llama3-8b (+23.94%)” — verify the absolute F1 change in Table 4; please provide absolute and relative changes consistently.

Criteria for score increase
- If you (a) eliminate the PCA/index leakage risk with clear source-only training, (b) add strong semantic-retrieval baselines and show RAEmoLLM is competitive or better, and (c) clarify the COCO label protocol, I would raise to Findings (3.0) or Borderline Conference (3.5) depending on results. A clean retrieval-metric replacement for Table 3 and an encoder ablation would further support a Conference recommendation.

## Confidence
3: Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5: Between Poor and Acceptable — The approach is sensible and results are promising, but the potential leakage, missing baselines, and statistical issues in Table 3 weaken the support for the strongest claims.

## Excitement
2.5: Between potentially interesting and interesting — The affect-guided retrieval idea for cross-domain ICL is interesting and practical, but the empirical validation needs tightening before it can be truly compelling.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.  
Justification: The framework is simple and promising, with clear gains over zero-shot and random few-shot, and useful analyses (Figure 2, Table 4). However, methodological concerns (possible leakage, missing semantic retrieval baselines), statistical issues (Table 3), and inconsistencies (COCO label setup) prevent a confident acceptance in the main track at this time. With the suggested fixes and added baselines, this could become a solid Findings paper and potentially a borderline main-track candidate.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper includes a Limitations section acknowledging issues with class imbalance and short-text domains. It could further discuss:
  - Bias amplification: Affect signals learned from social media may encode cultural or demographic biases; retrieval on such signals may disadvantage certain communities or language styles.
  - Domain shift over time: Affective expressions evolve; models may drift and misclassify benign content as conspiratorial if affect norms change.
  - Dual use: The same pipeline could be adapted to curate emotionally charged exemplars for manipulation.  
Mitigations to discuss: periodic re-calibration with bias audits, transparent reporting of failure modes, and guardrails for responsible deployment.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many details are present, but key implementation specifics (hyperparameters, exact prompts for all models, PCA fitting scope, and an explicit code link) are missing; proprietary API usage adds variance.

## Datasets
1: No usable datasets submitted. — The work reuses public datasets; no new dataset contribution.

## Software
2: Documentary. — The paper claims code availability but does not provide a concrete link or sufficient detail in the main text; pending an actual release, usefulness is limited.