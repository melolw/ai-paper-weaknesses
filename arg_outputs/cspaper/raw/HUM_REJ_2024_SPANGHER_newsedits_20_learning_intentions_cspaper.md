# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies how and why news articles update over time and whether signals inside the text can predict which facts will change. Part 1 introduces NewsEdits 2.0, a taxonomy of edit intentions for news revisions, with 4 coarse and 20 fine-grained labels, annotated by professional journalists over 9.2k sentence-revision pairs. A sequence-to-sequence LED-based ensemble model is trained to tag edit intentions and then used to silver-label a very large revisions corpus. Part 2 frames a prediction task: given an old draft sentence (with local or global context), estimate whether it will later undergo a factual update. Models achieve moderate performance and reveal linguistic cues (e.g., temporality, statistics). Part 3 demonstrates a use case: improving LLM abstention in RealTimeQA-like settings when the retriever surfaces outdated passages. Using predicted update-likelihood bins to warn GPT‑4 increases correct abstention, approaching an oracle condition.

## Summary Of Strengths
- Problem framing and scope
  - Timely and well-motivated: identifying likely-to-change facts in news and using this to guide abstention speaks directly to QA over dynamic corpora and RAG safety.
  - Clear three-part structure (Figure 2) that connects taxonomy creation, prediction, and application.

- Resource and taxonomy
  - A well-defined, journalism-oriented edit-intention schema (Figure 3), developed with domain experts, fills a gap left by Wikipedia- or education-focused schemas.
  - Annotation interface and protocol are described; inter-annotator agreement threshold is reported (κ > .6); coarse/fine-grained definitions are provided (Section 3.1 and Appendix C.1).
  - The reprocessing of NewsEdits with better SBD and sentence matching is a practical contribution; reported link F1 improves to ~95 (Appendix A.2).

- Modeling and analysis
  - The tagging model achieves reasonable micro-F1 (Table 1). Ablations with discourse/argumentation/quote/event/NLI features are thoughtful and domain-appropriate.
  - Exploratory analyses are informative: distributions by syntactic edit types and news sections (Tables 2–3), and coarse/fine confusion matrices (Figures 6–7) are useful diagnostics.

- Predicting factual updates and linguistic cues
  - The factual-update prediction task is clearly defined (Equation 2). The study contrasts sentence-only vs contextual variants and zero-shot vs finetuned (Table 4).
  - Manual cue analysis (Table 5) is insightful; it connects model behavior to interpretable phenomena (e.g., “Recent/Developing Event,” “Statistic,” “Opinion/Analysis”).

- Application to abstention
  - The abstention demonstration (Table 7), design, and evaluation show that providing the model’s update-likelihood bins to GPT‑4 yields near-oracle abstention rates (Tables 8–9).
  - Figure 4 offers a concrete precision–recall–F1 profile as the decision threshold tightens, illustrating how the method can be used as a high-precision abstention trigger.

- Figure- and table-grounded clarity
  - Figure 1 effectively illustrates how edits differ by intention on a concrete example.
  - Figure 2 helps the reader keep track of the pipeline and the role of each part.

## Summary Of Weaknesses
1) Reliance on silver labels and unclear upper bounds
   - A large portion of the training data for Part 2 (factual-update prediction) is silver-labeled by the Part 1 tagging model, which itself has modest macro-F1 (Table 1). This compounds noise and makes it hard to interpret the true ceiling. While a human upper bound is reported later, more systematic measurement of label quality and task difficulty is needed to anchor claims.

2) Limited robustness and generalizability evidence
   - The prediction experiments are narrowed to articles with ≥10% additions and ≥5% deletions (Section 4.1), which biases toward highly dynamic news. It is unclear how models perform on typical, less-revised articles, or across outlets/languages. Without this, applicability to general RAG scenarios is uncertain.

3) Inconsistencies and possible errors in reported metrics
   - Table 4 contains values that appear inconsistent or implausible. For example, “FT Longformer, Direct Context” lists a Macro F1 of 87.8 while Fact F1 is 22.3 and Not-Fact F1 is 93.0; a two-class macro-F1 of 87.8 is inconsistent with those per-class F1s. Also, “Full Article” variants sometimes underperform “Direct Context” by a large margin without explanation. These issues should be audited and clarified.
   - In Table 2, “Addition: Style = 104” looks like a unit mismatch (vs six-figure counts in other cells). If this is a sampling artifact, specify; if not, likely a typo.

4) Weaknesses in the abstention evaluation design
   - The abstention evaluation relies primarily on GPT‑4 self-evaluation (Section 5.1, “Abstention Rate Evaluations”). While a small human spot-check is mentioned (kappa > .74 on 100 items), a larger, independent human evaluation is needed, especially since the improvement claims hinge on this section.
   - The baseline space omits competitive abstention strategies (e.g., conformal prediction, explicit uncertainty estimation, confidence calibration, selective prediction objectives). Comparing to only “No Warning” and a generic “Uniform Warning” is too limited to claim practical superiority.

5) Causal interpretation and selection effects
   - The paper suggests that predicted update-likelihood causally improves abstention. However, questions are generated from old and new sentences (Section 5.1), and the final evaluation only considers instances with an actual update. The selection and construction of question types (No/Maybe/Likely-Conflict) are driven by the same pipeline, which risks favorable coupling. A held-out, independently authored question set would make the claim stronger.

6) Limited analysis of LLM failure modes
   - Table 6 and Tables 12–13 list sentences in high/low update-likelihood regions, but there is little error analysis focused on why GPT‑4 fails to detect likely updates without the hints, or how prediction errors translate to over/under-abstention. For instance, Figure 4 shows strong precision gains at high thresholds, but how many questions are then left unanswered unnecessarily?

7) Scope of claims vs. moderate core task results
   - Factual-update prediction performance is modest (e.g., human ≈ 41.2 Fact F1 vs finetuned longformer ≈ 25.4 Fact F1 in Table 4), and LLM zero-shot performance is weak. The conclusion that “this important capability is not emergent during pretraining” would benefit from broader model sweeps, ablation of prompt formats, and multiple LLM families before generalizing.

8) Clarity and reproducibility details
   - More details are needed to reproduce the tagging model and the factual-update predictor: exact train/dev/test splits for all parts, label distributions pre/post balancing, hyperparameters, and decoding formats for the seq2seq labeling. Appendix B.1 gives a template, but crucial parameters are missing.

9) Missing related work and stronger baselines in abstention
   - The abstention literature is now sizable, including taxonomies and decision-theoretic frameworks. The paper would benefit from engaging with contemporary approaches and adopting at least one principled baseline (e.g., conformal abstention or calibrated selective prediction) for Part 3.

10) Figure- and table-specific critiques
   - Figure 6 (coarse confusion matrix) and Figure 7 (fine-grained confusion matrix) are helpful, but the paper under-leverages them. For example, the large off-diagonal mass for Narrative vs Style suggests systematic confusion that could be mitigated by specialized heads or hierarchical decoding. This design iteration is not explored.
   - Figure 4 shows that high thresholds substantially improve precision at the cost of recall. This is exactly the regime used in Part 3, which is good, but the paper should quantify how many real QA instances are filtered out by these thresholds and the end-to-end trade-off in a retrieval budget.

## Potentially Missing Related Work
1) Wen et al., “Know Your Limits: A Survey of Abstention in Large Language Models,” 2024 — Comprehensive survey of abstention methods, evaluation protocols, and risk-aware prompting. Should be discussed in Section 2 and used to situate Part 3 among contemporary abstention strategies; at minimum, cite when introducing abstention as the downstream use case.

2) Ouyang et al., “HoH: A Dynamic Benchmark for Evaluating the Impact of Outdated Information on Retrieval-Augmented Generation,” 2025 — Introduces a benchmark directly targeting outdated retrieval. Should be compared in Section 5 as an alternative evaluation suite; include discussion of how NewsEdits-derived predictions could integrate with or complement such dynamic QA tests.

3) Kirichenko et al., “AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions,” 2025 — Provides a broad, challenging abstention benchmark. Use it in Section 5 to contextualize the presented improvements, and to motivate adding principled abstention baselines.

4) Verma et al., “The MediaSpin Dataset: Post-Publication News Headline Edits Annotated for Media Bias,” 2026 — Another large revision dataset in the news domain. Add to Section 2 as complementary related work and contrast the intention schema and downstream tasks.

5) Machcha et al., “Knowing When to Abstain: Medical LLMs Under Clinical Uncertainty,” 2026 — Domain-specific but methodologically relevant work on abstention under uncertainty. Cite in Section 5 as an example of selective prediction protocols and metrics worth adapting.

6) Presacan et al., “When silence is safer: a review and decision-theoretic framework for LLM abstention in healthcare,” 2026 — Offers decision-theoretic framing of abstention trade-offs; relevant to designing optimal abstention thresholds and costs. Reference in Section 5 to motivate threshold selection and risk calibration.

## Comments Suggestions And Typos
Actionable suggestions:
- Clarify and correct metrics:
  - Audit Table 4 for inconsistencies (e.g., Macro F1 = 87.8 vs per-class F1s). Provide exact formulas, class priors, and whether macro is computed over gold labels or predicted bins. Recheck Table 2 “Style = 104” for Addition.
  - Report confidence intervals or bootstrap CIs for Tables 4, 8, and 9; the abstention improvements are meaningful but need uncertainty estimates.

- Strengthen abstention baselines and evaluation:
  - Include at least one principled selective prediction baseline (e.g., conformal prediction on answer likelihood, calibrated uncertainty thresholds, entropy-based abstention) and a non-news set to probe generality.
  - Expand human evaluation beyond 100 items and clearly separate data authorship from evaluation to mitigate pipeline coupling. Consider a held-out, independently authored set of questions per sentence.

- Reduce silver-label dependency:
  - Provide a larger human-labeled set for Part 2 or semi-supervised denoising (e.g., confidence-based filtering) to quantify gains when silver-label noise is reduced. Report performance deltas when training only on gold subsets.

- Modeling improvements:
  - Given confusion patterns in Figure 6/7, try hierarchical labeling (coarse first, then fine), or separate heads for Factual/Style/Narrative. Compare to a discriminative classifier baseline to check whether the generative LED is indeed the best choice.
  - For Part 2, analyze why “Full Article” underperforms “Direct Context” in several rows of Table 4. Provide length statistics, truncation behavior, and attention maps.

- End-to-end impact:
  - Quantify the retrieval-stage effects explicitly: how often do predicted high-likelihood-update sentences appear among top‑k retrieved passages? Report the proportion of QA instances for which the warning is triggered vs abstention is correct/incorrect, and how thresholds (Figure 4) trade off utility and caution.

Typos and minor issues:
- “acnkowledge” → “acknowledge” (Page 6, Section 4.1).
- “we are observe concord” → “we observe concord” (Page 8).
- “Discourse & Arg. (Best model, Fact)” in Table 1: ensure consistent naming and units; consider adding standard deviations.
- Capitalization: “edit” vs “Edit” in Table 2 and Table 11 headers should be consistent.
- Footnotes and superscripts (e.g., 2, 3) occasionally have trailing punctuation/spaces; standardize.

Criteria to raise my score:
- Fix the Table 4 inconsistencies and add stronger abstention baselines with expanded human evaluation. If the core results remain strong under these controls, I would move to 4.0 (conference).
- Demonstrate robustness across a more representative slice of news (not preselected for high change), or across outlets, and quantify noise sensitivity when reducing silver-label reliance.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5: Between Acceptable and Strong — Solid framing and execution; however, reliance on silver labels, metric inconsistencies (Table 4), and limited abstention baselines temper the strength.

## Excitement
3.5: Between interesting and exciting — The overall direction is useful and the abstention application is compelling, but current evaluation leaves some questions.

## Overall Assessment
3.5 Borderline Conference: Close to acceptable for the main conference but with notable weaknesses. The taxonomy and dataset curation, plus the abstention demonstration, are valuable. Before a confident accept, the paper should correct metric inconsistencies, strengthen abstention baselines and human evaluation, and better quantify robustness and noise sensitivity.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper discusses limitations (Section 7.3), including language coverage and potential misuse to disparage media outlets. Additional points to consider:
- Selection bias from focusing on highly dynamic articles may overstate downstream gains; in calmer news cycles, abstention triggers may be rare.
- Over-abstention harms utility: Table 9 shows the “Uniform Warning” baseline over-abstains in No-Conflict, while the proposed approach mitigates this. It would be useful to frame abstention with explicit costs and benefits, potentially using decision-theoretic thresholds.
- Annotator demographics skew to US-based professionals; this can shape what counts as “background,” “analysis,” or “sensitivity,” affecting cross-cultural generalization. Note this in the Limitations and suggest future multilingual and cross-market annotation.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Many details and templates are provided, code/data promised, but more hyperparameter/training specifics and exact splits are needed to make it turnkey.

## Datasets
4: Useful — The silver-labeled large corpus and cleaned linkage pipeline should be useful to others; the journalist-annotated set is particularly valuable.

## Software
4: Useful — If released as stated, the tagging models, preprocessing, and visualization tools would aid follow-up work and replication.