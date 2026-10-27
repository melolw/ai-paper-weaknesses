# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes QuoteVerify, an inference-time pipeline for verifying citations in long-form “deep research” reports produced by LLMs. The key idea is to force the generator to emit structured citation triples consisting of (statement, source_id, evidence_quote), then to: fetch sources, verify the evidence substring in the source (exact/fuzzy match), apply an NLI entailment check from quote to statement, and finally attempt single-pass repair or drop unsupported triples. On a 20-prompt pilot subset of ReportBench using GPT-4o and Gemini-2.5-Pro as base models, the authors report improvements in cited-statement match rate over a “Standard” citation baseline and analyze failure modes. They find that the structured triple requirement drives most of the gains, while quote validity is a major bottleneck because models tend to paraphrase rather than copy verbatim text.

## Summary Of Strengths
- Clear, modular, and training-free wrapper: The 5-stage pipeline is straightforward to understand and to attach to arbitrary report generators. Figure 1 usefully diagrams the data flow and verifies what is checked where, improving reproducibility and transparency.
- Operational clarity and measurable criteria: The quote validity stage is explicitly defined as substring or 90% trigram overlap after normalization, and Equation (1) formalizes the triple that powers the rest of the pipeline.
- Useful empirical observation: Prompting the model to output structured triples with quotes appears to be a strong procedural control; in Table 1, Prompt-Only already gives large improvements over Standard (e.g., +22.5pp on GPT-4o), a practical lesson for practitioners.
- Sensible semantic safeguard: The NLI gate targets the “irrelevant quote” failure mode. In Table 2, removing the entailment gate increases the overall Match Rate but lowers the Entail Pass, which aligns with the claim that the gate filters semantically weak matches.
- Diagnostic visualization: Figure 2a and 2b make failure modes and source-type effects tangible. In particular, Figure 2b shows that high fetch success for arXiv (e.g., 89–100%) does not translate into high overall pass rates, spotlighting quote validity as the key bottleneck.
- Open implementation signal: The paper claims public code and an audit log output format (JSONL), which, if provided as stated, improves practical value.

## Summary Of Weaknesses
1) Narrow and underpowered evaluation scope
- The experiments use only a 20-prompt “pilot” subset of ReportBench (Section 4.1), which is quite small given the reported variance and the complexity of the task. Statistical significance is reported (paired bootstrap, 10K resamples), but the sample size, prompt diversity, and per-domain breakdown are insufficient for strong claims. For instance, Table 1 differences between Prompt-Only and QuoteVerify are small to negative on GPT-4o; with N=20 prompts, confidence intervals or per-task variance are essential. Without that, conclusions about generality are tentative.

2) Ambiguity and possible mismatch of evaluation metric vs. pipeline goals
- “Match Rate” is adopted from ReportBench but is not defined in sufficient detail in this paper. It is notable that Table 2 shows No-Entailment yields higher Match Rate than Full QuoteVerify (58.8% vs 53.1%) while simultaneously having lower Entail Pass (24.5% vs 31.8%). If Match Rate is the primary metric, this raises the question of whether the entailment stage is mainly reducing coverage without delivering better “match” under the official metric. The paper asserts the entailment gate is needed to stop irrelevant quotes, yet the main headline metric favors removing the gate. Reconciling this contradiction is crucial, and requires clear definitions and analyses of what “Match Rate” rewards or penalizes.

3) Limited novelty relative to prior citation and verification pipelines
- The combination of structured evidence, substring/fuzzy verification, and NLI gating resembles established designs in citation-grounded QA and RAG verification (e.g., GopherCite’s verbatim-quote demand; post-generation verification like RARR/Self-RAG; NLI-based verification common in attribution work). The paper’s value is primarily in packaging this as an inference-time wrapper for “deep research” reports. That is useful, but the paper should make a stronger and more explicit case for what is substantively new beyond the synthesis of known components, ideally via comparisons to close variants that also verify evidence with NLI.

4) Incomplete baseline coverage and missing closely related work
- Beyond WebGPT, GopherCite, RARR, Self-RAG, and several evaluation papers, multiple directly relevant works are not discussed or compared (see “Potentially Missing Related Work”). In particular, recent frameworks that parse and verify citations in deep research settings, or that perform rigorous verification inside RAG pipelines (e.g., VeriCite), appear directly relevant. Their absence weakens positioning and makes it difficult to judge whether the observed gains are competitive with the current state of the art.

5) Fragile verification criteria and potential bias against legitimate paraphrases
- The quote validity criterion relies on exact or near-exact substring matching with trigram overlap ≥90% (Section 3.5). This is strict and likely penalizes valid paraphrases or quotes with minor normalization issues. The authors acknowledge this in the conclusion but do not provide alternative matching experiments (e.g., approximate text alignment, quote-anchored retrieval, semantic span alignment) or sensitivity analyses to show robustness. Figure 2b visually demonstrates how the pipeline bottlenecks at quote validity, but the paper stops short of testing more tolerant yet precise methods.

6) NLI gate suitability for scientific claims is not validated
- The NLI model is DeBERTa-v3-large fine-tuned on MNLI (Section 3.6). MNLI is not designed for scientific or multi-sentence claim verification, and it is unclear whether the gate’s precision-recall properties are appropriate in this domain. No ablation with a scientific NLI model, threshold calibration, or human validation of entailment decisions is presented. This is material because Table 2 shows the gate reduces Match Rate.

7) Repair step underspecified and appears to add marginal value
- The “Repair-or-Drop” stage is presented as a key component, yet Table 2 shows Drop-Only performs essentially as well as Full QuoteVerify on Match Rate (53.6% vs 53.1%). The prompting, iteration limits, and decision rules for repair are not described in enough detail to reproduce or to understand why it underperforms. If the gate and quote matching are brittle, repair may need more than one pass or stronger retrieval constraints. Without detail or a sensitivity study, it is unclear how to improve this step.

8) Coverage regression and practical utility not fully interrogated
- Table 1 shows large reductions in Reference Recall and number of cited statements (#Cited) compared to Standard. The paper acknowledges a quality-coverage tradeoff, but there is no user- or task-level analysis to determine when such drops are acceptable. For research reports, reduced coverage can be a serious issue; the paper would benefit from qualitative analyses of dropped statements and whether they were low- or high-importance for the report’s thesis.

9) Statistical reporting is thin
- The paper claims statistical significance for improvements over Standard with p<0.02, but does not report confidence intervals, per-domain breakdowns, or effect sizes for other comparisons (e.g., vs Prompt-Only). Given small N and the directional, sometimes negative differences in Table 1 and Table 2, stronger statistical reporting is needed.

10) Reproducibility details missing in key components
- The source fetcher is central but underdescribed: how are redirects, robots.txt, paywalls, dynamic pages, PDF parsing failure modes, and deduplication handled? What are timeouts and content-length limits? How often do parsers disagree? Without such details, reproducing Table 1/2 precisely will be difficult even with public code. Similarly, prompts, system messages, and exact API parameters for all stages, including repair, should be fully enumerated.

11) Figure-level concerns that merit clarification
- Figure 2a indicates a dominant “Quote+Entailment Fail” bucket for GPT-4o (55.7%). This seems at odds with the relatively high Entail Pass reported for QuoteVerify on GPT-4o in Table 1 (31.8%), unless distribution is computed over all attempted triples rather than surviving ones. Please clarify the denominator for each bar segment and add confidence intervals. 
- Figure 2b compares fetch and overall pass by source type. While it supports the “validity bottleneck” claim, the figure uses small sample bars without uncertainty estimates, making it hard to judge whether differences like 89% vs 100% fetch rates are meaningful on this dataset.

12) Limited discussion of broader impacts and ethics
- The system crawls and processes external content. There is no discussion of compliance with websites’ terms, robots.txt, or potential harm from aggressive fetching. There is also no discussion of biases introduced by dropping hard-to-verify sources, which could systematically skew citations away from certain venues, regions, or publication types.

## Potentially Missing Related Work
1) Onweller et al., “Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents,” 2026 — Directly targets citation verification in deep research outputs. Should be discussed in Related Work (Section 2) and considered as an external evaluation protocol complementing ReportBench in Section 4.

2) Venkit et al., “DeepTRACE: Auditing Deep Research AI Systems for Tracking Reliability Across Citations and Evidence,” 2025 — Proposes an audit framework for statement-level citation reliability. Add to Section 2 and consider as an additional evaluation or diagnostic in Section 4.

3) Wang et al., “LiveResearchBench: A Live Benchmark for User-Centric Deep Research in the Wild,” 2025 — A realistic benchmark for long-form, web-grounded reports with metrics on coverage and citation accuracy. Discuss in Section 2 and consider for future evaluation plans in Section 5.

4) Du et al., “DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents,” 2025 — Large-scale benchmark with citation-oriented metrics relevant to your task. Cite in Section 2 and compare to your pilot dataset in Section 4.

5) Huang et al., “MMDeepResearch-Bench: A Benchmark for Multimodal Deep Research Agents,” 2026 — Extends citation fidelity to multimodal settings. Mention in Section 2 and discuss extension of QuoteVerify to image-grounded quotes in Section 5.

6) Huang et al., “DeepFact: Co-Evolving Benchmarks and Agents for Deep Research Factuality,” 2026 — Dynamic factuality benchmarks and document-level verification strategies. Compare conceptual differences in Section 2, and discuss as complementary evaluation in Section 4/5.

7) Qian et al., “VeriCite: Towards Reliable Citations in Retrieval-Augmented Generation via Rigorous Verification,” 2025 — Multi-stage verification in RAG that includes NLI-like checks; highly relevant to your pipeline design. Compare design choices and results in Section 2 and consider as a strong baseline in Section 4.

8) Seetha Ram et al., “Citation Drift: Measuring Reference Stability in Multi-Turn LLM Conversations,” 2025 — Measures how citations mutate over time; useful to evaluate whether QuoteVerify stabilizes citations across iterative research workflows. Add to Section 2 and discuss as an evaluation angle in Section 5.

## Comments Suggestions And Typos
Actionable questions and suggestions that can change my evaluation:
- Clarify the main metric and reconcile contradictions:
  - Precisely define ReportBench “Match Rate” as used here, including whether it relies on model-generated text span extraction, human judgement, or heuristic matching. Why does No-Entailment in Table 2 increase Match Rate if the entailment gate is supposed to reduce irrelevant quotes? Please add confidence intervals and per-domain breakdowns for Table 1 and Table 2, and report effect sizes beyond p-values.
- Expand evaluation beyond a 20-prompt pilot:
  - Run on the full ReportBench or at least a substantially larger, stratified subset. Include per-domain and per-source-type results with uncertainty. Consider an additional benchmark (e.g., LiveResearchBench or DeepResearch Bench) to reduce dependence on a single protocol.
- Strengthen baselines and ablations:
  - Add a comparison to a RAG verifier like VeriCite and to a quote-demanding generator such as a GopherCite-style prompting setup optimized for verbatim copying. Include an ablation where the NLI gate uses a scientific-domain NLI model or a calibrated threshold, and report PR curves for entailment gating.
- Improve the repair stage or justify its design:
  - Provide full prompts, decision rules, and any iteration limits. Try multi-pass repair and/or retrieval-anchored quote selection. Report how often repair changes the source versus the quote and whether the new source is actually more appropriate.
- Test more robust quote matching:
  - Beyond 90% trigram overlap, evaluate sequence alignment or semantic span alignment methods that can tolerate light paraphrase while remaining precise. Re-compute Figure 2b and Table 1 using a relaxed but principled matching criterion and report how this affects coverage and accuracy.

Additional minor comments and typos:
- Page 1: “statistically significant improvements over standard baselines” — add exact confidence intervals for the +18.7pp and +12.5pp gains in Table 1.
- Page 5, Table 2 caption: It says “Results show entailment gate prevents semantically irrelevant quotes (↓7.4pp entailment pass without gate),” but the table shows Entail Pass 31.8% (Full) vs 24.5% (No-Entailment), which matches a 7.3pp drop. Please correct the wording/rounding for consistency.
- Page 5, “Quality-coverage tradeoff”: provide concrete examples in an appendix-like section or a figure showing which kinds of statements get dropped.
- Figures 2a and 2b: add error bars or bootstrapped CIs and specify denominators. 
- Section 3.4–3.7: please include exact fetcher settings (timeouts, retries), parsing order for PDFs, and precise prompts for triple generation and repair.
- References: “Wang et al., 2020” is cited for DeBERTa-v3-large but looks like a summarization evaluation citation in the references. Verify the citation for DeBERTa v3 and fix if misattributed.

Criteria for score increase:
- Run a larger-scale evaluation with proper uncertainty reporting; add at least one strong, modern verification baseline (e.g., VeriCite-like), and clarify the Match Rate definition and its interaction with entailment gating. Demonstrating that the entailment gate improves a metric aligned with human judgement (even if Match Rate stays similar) would strengthen the case.

## Confidence
4: Quite sure after careful checking — I checked the key claims, tables, and figures carefully. Some details of the external benchmark and code are not fully verifiable from the paper alone.

## Soundness
3: Acceptable — The approach is methodologically reasonable and the pipeline is clearly described, but the evaluation is small-scale, certain metric-method mismatches are unresolved, and baseline coverage is incomplete.

## Excitement
2.5: Between potentially interesting and interesting — The packaging as an inference-time wrapper is useful, and the structured-quote lesson is practical, but novelty is moderate and the evaluation leaves questions.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is practical and the pipeline is clear, with informative figures and some positive results. However, the small evaluation, unclear alignment between the primary metric and the entailment gate, missing related work and baselines, and limited statistical reporting weigh it down. With stronger experiments and clearer reconciliation of metrics versus safeguards, this could rise to Findings or better.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
- Limitations are partially acknowledged, especially the quote validity bottleneck. However, more discussion is needed on:
  - The risk of biasing reports by dropping statements and sources that are hard to verify with strict substring criteria. This could skew literature coverage across venues, regions, and document formats.
  - The use of an MNLI-tuned NLI model for scientific claims without calibration or domain adaptation, including potential false positives/negatives and their downstream effects on what gets cited.
  - Web and PDF fetching ethics: compliance with robots.txt, rate limiting, handling of paywalled or copyrighted content, and the implications of caching large amounts of third-party text.
  - Dual use: pipelines that “clean” citations could be used to legitimize weak content by retaining only easy-to-verify snippets, giving an illusion of rigor.

Constructive suggestion: add an ethics/impact subsection discussing crawl policies, data handling, and bias from coverage reduction, along with mitigations such as adjustable precision-recall tradeoffs, opt-in source whitelists, or human-in-the-loop review for dropped high-importance statements.

## Ethical concerns
Potential concerns around web scraping compliance, copyright, and biased coverage due to aggressive dropping are not fully addressed. None appear disqualifying, but they should be discussed more explicitly.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The pipeline stages and core models are identified, and the paper claims code release. Important operational details of fetching, parsing, and prompts need to be fully enumerated to reach a 5.

## Datasets
1 No usable datasets submitted.

## Software
4 Useful.: If the claimed code and audit-log outputs are indeed released, they would be practically useful to others building research agents or verifiers.