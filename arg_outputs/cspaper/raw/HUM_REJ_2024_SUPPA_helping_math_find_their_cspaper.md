# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper presents an empirical study of multilingual mathematical reasoning across 26 languages using three datasets (MGSM, MSVAMP, AfriMGSM) and six instruction-tuned LLMs (three closed, three open). It evaluates several prompting-based reasoning strategies (simple, CoT, Cross-Lingual Thought/XLT) and introduces a variant, XL-TEN, which asks the model to act as an English reasoning expert while retelling the query in English. The authors also compare six translation systems (Google Translate, NLLB variants, MADLAD variants) to measure translation quality impacts on downstream math reasoning. Key findings are: English instructions generally help even when questions are in other languages; XL-TEN often outperforms XLT, especially for low-resource settings; translation quality strongly affects accuracy, with Google Translate outperforming the open models in this setup. The paper also briefly analyzes tokenizer effects for GPT-4 versus GPT-4o.

## Summary Of Strengths
- Breadth and diversity: A large-scale evaluation covering 26 languages including 16 African languages, many of which are extremely low-resource or unresourced in CommonCrawl (Table 2). This scope is valuable to the multilingual NLP community.
- Clear, reproducible prompting setups: The study defines six concrete prompting strategies with explicit prompts (Table 3), aiding comparability and reuse.
- Systematic comparison of translation models: The translation layer analysis across six MT systems is rarely presented this comprehensively for multilingual math reasoning; the findings that MT quality heavily influences performance are actionable (Table 5).
- Insightful cross-lingual bias observations: The consistent advantage of English instructions over original-language instructions across datasets and models (Table 4) reinforces and quantifies English-centered bias in current LLMs.
- XL-TEN as a practical tweak: While simple, XL-TEN is easy to adopt and shows consistent average improvements over XLT on several settings (Table 4), which can serve practitioners working with low-resource languages.
- Figures and tables support the narrative: Figure 2 usefully summarizes the experimental pipeline from the original problem through translation or cross-lingual prompting to the final answer, clarifying how reasoning and translation are orchestrated in the experiments.

## Summary Of Weaknesses
1) Novelty and conceptual contribution are modest.  
- XL-TEN is a small prompt modification to XLT. The paper positions it as a “new baseline,” yet Table 4 shows mixed results: e.g., for MGSM, closed models already do very well and gains from XL-TEN over CoT-EN are small or inconsistent; for MSVAMP, CoT-ORIG achieves the highest average across models (76.82) while XL-TEN averages 70.23, lower than several alternatives. The claimed “new baseline” status needs a more nuanced claim and stronger evidence.

2) Lack of deeper analysis and diagnostics, especially where results are surprising or mixed.  
- Table 4 indicates that XL-TEN underperforms CoT-ORIG on MSVAMP on average and is only marginally above SIMPLE-EN in some settings. The paper does not investigate why XL-TEN helps in AfriMGSM but not in MSVAMP, nor does it examine per-language breakdowns that could illuminate linguistic factors (morphology, numeral systems, tokenization effects). Without this, it is hard to generalize the recommendation.

3) Missing or weak consideration of stronger reasoning baselines.  
- The evaluation focuses on zero-shot prompting variants. It omits widely used inference-time methods that are known to significantly improve math reasoning and may interact with language bias, such as self-consistency decoding, best-of-N CoT, majority voting, verifier reranking, or more recent structured reasoning prompts. As a result, the study may underestimate what is achievable in non-English settings and overstate the relative benefit of XL-TEN.

4) Statistical rigor and significance testing are absent.  
- Reported improvements are typically small-to-moderate and may be within variance. The paper does not report confidence intervals, bootstrap CIs, or significance tests for Table 4 or Table 5. For example, differences of 1–2 points are repeatedly interpreted as meaningful patterns without variance estimates.

5) Translation evaluation lacks quality controls and error analysis.  
- Table 5 shows anomalously low performance for T-NLLB-3.3B due to apparent decoding issues that produced degenerate outputs. This suggests a setup problem rather than an inherent model deficit. The paper reports the issue but still keeps these values in the main comparison, skewing the impression of NLLB family performance. In addition, only downstream accuracy is reported; there is no MT quality analysis (e.g., COMET/BLEU or targeted error probes) or qualitative error breakdowns to contextualize how MT errors propagate into reasoning failures.

6) Potential confounds in fairness of MT comparisons and omissions.  
- Google Translate is reported as not supporting Wolof, and those items were skipped, yet conclusions are generalized across the full set. While the authors estimate the effect is small, a more principled handling is needed (e.g., imputations or per-language macro-averages, and clearly reporting language coverage per MT system). The paper also does not consider the reverse translation path (English → target language answers) or bilingual prompting that might reduce MT-induced losses.

7) Tokenization analysis is underdeveloped and only loosely tied to accuracy.  
- Table 6 shows GPT-4o uses fewer tokens than GPT-4 for the same inputs, roughly matching external claims. However, the paper speculates that tokenizer compression may explain GPT-4o multilingual gains without correlating token counts to accuracy changes on the same items. Without linking Figure/Table-based reasoning accuracy to token savings, the section reads as anecdotal.

8) Limited detail on answer extraction and evaluation.  
- The paper admits fragility in numeric extraction (Section 9), handled via a “multi-step regex.” Yet no exact patterns, normalization rules, or failure rates are reported, and there is no manual audit. Given numbers can be embedded in different scripts or phrased forms, the risk of evaluation artifact is material, especially in extremely low-resource languages.

9) Reproducibility gaps.  
- Code and data are promised “after review.” Per-language results, prompts in all target languages (for SIMPLE-ORIG and CoT-ORIG), MT decoding parameters, system prompts, and complete seeds are not fully included. These omissions reduce immediate reproducibility and complicate scrutiny of edge cases (e.g., T-NLLB-3.3B behavior).

10) Claims not always aligned with figures.  
- Figure 1 is a stylized schematic bar chart asserting that “multi-step reasoning” is best for low-resource languages. However, Table 4 paints a more nuanced picture where CoT-EN, XLT, and XL-TEN trade places depending on dataset and model. The figure risks overgeneralization relative to the quantitative evidence.

11) Dataset usage choices and subsampling rationale could be clearer.  
- Table 1 states MSVAMP provides 1,000 problems per language but the study uses 500 to “be in line with prior work” and to control cost. While understandable, this choice could bias comparability and increases uncertainty; a sensitivity check on sample size would be helpful.

12) Missing important, closely related recent work on multilingual math reasoning and multilingual reasoning-trace control.  
- The Related Work section is quite focused but omits several directly relevant recent analyses and benchmarks that would help position the contribution and potentially provide stronger baselines and discussion (see “Potentially Missing Related Work”).

Explicit references to figures/tables:
- Figure 2 clearly depicts the experimental flow: original low-resource question, either translation into English or cross-lingual reasoning prompt (including XL-TEN), model execution, and answer extraction. This helps readers understand how translation and prompting are isolated in the pipeline.  
- Figure 1, while intuitive, overstates a uniform ranking where “multi-step reasoning > translated to English > original question.” In Table 4, CoT-ORIG beats XL-TEN on MSVAMP on average, and XLT can underperform CoT-EN; thus, the visual should be revised or caveated to match the nuanced results.  
- Table 4 is central to the paper’s claims. It shows that English-based instructions (SIMPLE-EN, CoT-EN) typically outperform their original-language variants across datasets, supporting Section 5.2. It also reveals that XL-TEN’s advantage over XLT is not universal and is dataset- and model-dependent.  
- Table 5 supports the conclusion that MT quality dominates downstream accuracy; T-Google leads across MGSM/MSVAMP/AfriMGSM. Yet the degenerate outputs in T-NLLB-3.3B call for a diagnostic appendix and perhaps excluding those runs or fixing decoding.  
- Table 6 demonstrates token compression in GPT-4o relative to GPT-4, but it does not connect token savings to accuracy improvements on the same items; hence causal claims should be tempered.

## Potentially Missing Related Work
1) Luo et al., “MMATH: A Multilingual Benchmark for Mathematical Reasoning,” 2025 — Introduces a multilingual math benchmark with deeper analysis of language disparities and off-target generation. Directly relevant to Section 3 (Data) and Section 5 (Reasoning). Should be discussed in Related Work and potentially used to validate XL-TEN beyond MGSM/MSVAMP/AfriMGSM.

2) Ogundepo et al., “Improving Multilingual Math Reasoning for African Languages,” 2025 — Focuses on African languages with data/adaptation strategies. Highly relevant to Section 3.1 and Section 5.3. Should be cited, compared in Discussion, and may offer complementary baselines for AfriMGSM.

3) Qi et al., “When Models Reason in Your Language: Controlling Thinking Trace Language Comes at the Cost of Accuracy,” 2025 — Analyzes how enforcing reasoning-trace language affects accuracy, directly linked to CoT-ORIG vs CoT-EN and XLT/XL-TEN decisions (Sections 5.1–5.3). Should be discussed after Table 4 to contextualize trade-offs.

4) Vatsal et al., “Multilingual Prompt Engineering in Large Language Models: A Survey Across NLP Tasks,” 2025 — Offers a taxonomy of multilingual prompting strategies, relevant for framing Section 5 and for situating XL-TEN within broader multilingual prompting literature.

5) Son et al., “Linguistic Generalizability of Test-Time Scaling in Mathematical Reasoning,” 2025 — Evaluates test-time scaling across many languages, relevant to missing stronger inference-time baselines in Section 5 (e.g., self-consistency). Should be discussed as potential future comparisons and to calibrate expectations for gains outside English.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide per-language breakdowns for Tables 4–5 in an appendix and include confidence intervals or bootstrap CIs. This will help interpret where XL-TEN truly helps and where it does not, particularly across morphological/orthographic typologies.
- Strengthen baselines: add self-consistency CoT, majority voting, best-of-N sampling, and optionally a lightweight verifier reranking. This will contextualize whether XL-TEN is competitive against commonly used reasoning-boosting techniques.
- Diagnose MT anomalies: for T-NLLB-3.3B, verify decoding and pre/post-processing, and re-run if usage errors are found. Add a small MT quality evaluation (e.g., COMET or a focused human audit on a sample) to attribute accuracy changes to specific translation pathologies.
- Report evaluation details for numeric extraction: provide exact regex rules, normalization pipeline, language-specific edge cases, failure rates, and a small manual audit quantifying extraction errors. Consider safer answer formatting like enforced JSON schema to reduce evaluation noise.
- Calibrate claims and figures: temper the “new baseline” language for XL-TEN and revise Figure 1 to reflect the nuanced outcomes in Table 4. Consider adding ablations isolating each instruction element in XL-TEN to clarify which part drives gains.

Typos and minor issues:
- Page 3/Table 2: language code “ib” for Igbo should be “ig” (consistent with text elsewhere).  
- Page 3: “list of of languages” → “list of languages.”  
- Section 6.1: “the aid the of” → “the aid of.”  
- Prompts in Table 3: minor spacing/punctuation (e.g., quotes) are inconsistent; consider standardizing exact prompts for reproducibility.  
- Section 7: “the MSGM benchmark” → “the MGSM benchmark.”

Criteria that could raise my score:
- Inclusion of stronger reasoning baselines (self-consistency etc.) and clear statistical analysis showing XL-TEN’s consistent benefits where claimed.
- Fixing the NLLB-3.3B anomaly, adding MT quality diagnostics, and providing per-language analyses that reveal linguistic correlates of success/failure.
- Releasing code and detailed evaluation scripts at rebuttal time, including exact prompts for all languages and answer-extraction logic.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure overall, but I did not verify all experimental details and there are many moving parts in multilingual setups.

## Soundness
3: Acceptable — The study supports its main claims at a high level, but lacks statistical testing, deeper diagnostics, and stronger baselines. Some MT results appear confounded by usage issues.

## Excitement
2.5: Between potentially interesting and interesting — The breadth and African-language focus are valuable, and the translation-layer analysis is useful, but the methodological novelty is small and results are mixed.

## Overall Assessment
3: Findings — The paper could be accepted to the Findings of the ACL. It offers a broad and useful empirical study with actionable lessons about English bias, translation quality, and a small but practical prompt variant. However, limited novelty, lack of statistical rigor, missing stronger baselines, and underdeveloped diagnostics make it fall short of the main conference bar.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges limitations around sample sizes and evaluation robustness. Additional points to discuss:  
- Risk of over-reliance on English as a “crutch,” which could inadvertently deprioritize native-language reasoning capability and perpetuate linguistic inequities.  
- Potential harms if MT pipelines introduce systematic biases or numeric distortions in low-resource languages that go unchecked.  
- Accessibility concerns: if top performance depends on proprietary MT/LLMs, this may disadvantage researchers/practitioners in regions where access is limited.  
Encourage a clearer failure-mode analysis by language and script, and a discussion of equitable pathways for building native-language reasoning rather than always pivoting to English.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible — The prompts and model choices are described; however, code is not yet released, per-language results and full extraction details are missing, and MT decoding specifics are thin.

## Datasets
1: No usable datasets submitted — The paper does not introduce a new dataset; it uses MGSM, MSVAMP, and AfriMGSM.

## Software
3: Potentially useful — If released, the evaluation scripts and prompt templates could be useful to others. Currently unavailable in the submission.