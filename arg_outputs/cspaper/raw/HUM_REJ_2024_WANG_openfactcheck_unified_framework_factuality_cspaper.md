# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper presents OpenFactCheck, a unified framework for evaluating the factuality of LLM outputs and the reliability of automatic fact-checkers. The system has three modules: (i) CUSTCHECKER, a configurable pipeline with pluggable claim processing, retrieval, and verification; (ii) LLMEVAL, which aggregates seven factuality-focused datasets (FactQA) and evaluates models such as LLaMA‑2 and GPT‑4; and (iii) CHECKEREVAL, which compares multiple automatic checkers (e.g., FactScore, FacTool, Factcheck‑GPT, Perplexity) on human-annotated benchmarks (FactBench) using precision/recall/F1 and also reports latency and cost. The paper reports empirical analyses across these modules, including accuracy trends (Table 3), checker comparisons (Table 4), and cost/time (Table 5), and provides a web interface (Figures 4–7).

## Summary Of Strengths
- Practical unification: The framework cleanly abstracts claim processing, retrieval, and verification into pluggable components with YAML-based configuration and message passing (Section 3.1), lowering the barrier to mixing modules across existing systems. The pseudo-code in Figure 3 makes interfaces concrete.
- Coverage of factuality facets: The FactQA collection (Section 3.2, Table 1) merges seven datasets targeting diverse failure modes (snowballing, self-uncertainty, false premises, time-sensitive queries, long-form answers). This is a useful consolidation for practitioners who want a single entry point for factuality testing.
- Joint evaluation of checkers and LLMs: CHECKEREVAL provides a uniform comparison of popular checkers over human-labeled data (Table 2 for label stats, Table 4 for performance) and adds latency/cost tracking (Table 5), which is often ignored but crucial in real deployments.
- Clear, reproducible reporting format: The paper provides disaggregated metrics (e.g., separate precision/recall on true vs. false classes in Table 4), domain/topic tagging (Appendix B), and descriptive plots that highlight failure modes. For example, Figure 2 visualizes the proportion of true claims, the count of false claims, and the dollar cost per dataset, which together support the claim that costs scale with the number of atomic claims and backend model pricing.
- Web demo and usability: The UI screenshots (Figures 4–7) show practical workflows for configuring a checker, uploading LLM outputs for evaluation, and contributing to a leaderboard. This improves accessibility for both researchers and practitioners.

Specific figure- and table-grounded strengths:
- Figure 1 provides a coherent architecture overview that clarifies data flow between LLMEVAL and CHECKEREVAL and how “best checker” selection feeds back into automated evaluations; this aids reader understanding of system scope and interactions.
- Table 4 and Table 5 together make a compelling engineering point: systems using stronger LLM judges and more expensive search APIs (e.g., Factcheck‑GPT with GPT‑4 + SerpAPI) yield higher F1 on false claims but at sharply increased latency and cost, which justifies the inclusion of cost-aware leaderboards.

## Summary Of Weaknesses
1) Limited novelty, primarily a unification/engineering contribution
- The core pipeline mirrors widely used abstractions in recent fact-checking frameworks (claim extraction, retrieval, verification). The paper’s distinctive value is integration and packaging rather than new algorithms, theory, or metrics. Section 3.1 emphasizes configuration and plug-ins but does not introduce new verification models, retrieval strategies, or extraction algorithms. This is fine for a system/demo, but thin for ACL main track.

2) Circularity and measurement validity concerns in LLMEVAL
- The LLMEVAL component often judges free-form answers using automatic checkers (Section 3.2, “no gold standard answers”). This risks compounding biases of the chosen checker and retrieval stack. Although CHECKEREVAL later evaluates checkers on human-labeled data (Section 3.3), the LLM evaluation results for open-domain long-form tasks still depend on one pipeline (FacTool by default, Figure 2), which may under- or over-penalize certain models. A human study to validate LLMEVAL’s judgments, even on a subset, would strengthen the scientific value.

3) Dataset construction details and labeling reliability are under-specified for key pieces
- FactQA’s domain/topic annotations are produced by GPT‑4 (Page 5, footnote 1) using GPT‑4’s own responses as references. This introduces measurement bias that is not quantified. There is no inter-annotator agreement or manual spot check reported to ensure GPT‑4’s domain/topic labeling is reliable, nor a sensitivity analysis showing that any downstream insights are robust to labeling noise.

4) Ambiguity about reproducibility and availability
- The abstract claims public release, but the URL is “withheld.” Without a reproducible package or, minimally, comprehensive configuration files and prompts, reproducing the exact LLMEVAL and CHECKEREVAL numbers is difficult. This is particularly acute since results depend on external APIs (Serper/SerpAPI) and model versions (gpt‑3.5‑turbo‑0125 vs gpt‑4‑turbo‑2024‑04‑09; Table 8). Clearer versioning and frozen prompts are needed to achieve consistent replication.

5) Incomplete analysis of error sources and component-level attribution
- Section 3.3 notes that the current evaluation treats each system as a black box; intermediate steps are “future work.” Given that Table 4 shows very low F1 for Label=False across several setups, a granular error analysis (e.g., retrieval failure vs. verification failure) is necessary to guide improvements. Without this, the paper’s recommendation that “implementation choices primarily drive performance” (Page 8) is too general.

6) Limited statistical rigor in model comparisons
- Results such as Table 3 and the three charts in Figure 2 do not include confidence intervals or statistical tests. Given the modest sizes of several datasets (e.g., FacTool‑QA: 50 prompts; Factcheck‑Bench: 94 prompts), apparent differences could be within noise, especially when broken down into many claims.

7) Potential mismatch between claimed takeaways and evidence
- The paper concludes that “more than 90% of the claims generated by LLMs in response to open-domain questions are factually correct” (Page 8), but this conclusion depends critically on FacTool’s decomposition and verification (Figure 2, left panel). Since Table 4 shows how hard it is for systems to detect false claims, the 90% figure may reflect verification/recall limitations rather than true LLM accuracy. This caveat should be front-and-center.

8) Missing or light comparisons to several closely related frameworks and leaderboards
- The related work is mostly descriptive (Section 2.1–2.3) and omits several directly comparable frameworks/benchmarks introduced recently, including multi-source factuality evaluators and long-form evaluators with stronger human-alignment studies (see “Potentially Missing Related Work”).

9) Small clarity and presentation issues
- Inconsistent spelling: “CHECKERÉVAL” with an accent appears in several places (Pages 2 and 3) whereas elsewhere it is “CHECKEREVAL.” Minor typos appear (“promot” in Appendix A). Figures 1–3 are referenced appropriately, but some figures (Figure 2 panels) would benefit from larger fonts and explicit y-axis units in captions.

Figure- and table-specific critical points:
- Figure 2: The right-most panel makes a central cost claim (“~$30 for 100 responses using GPT‑3.5‑Turbo” in text on Page 7). However, the plotted bars appear dataset-dependent and model-dependent; the caption should explicitly state what is held constant and how costs were normalized. Also, it would help to show error bars to reflect variance from different numbers of atomic claims across models (Figure 8 shows these claim count differences).
- Table 4: While the split reporting by true/false is valuable, the F1 for Label=False is low across most systems (e.g., 0.46 for FacTool GPT‑3.5 on Factcheck‑Bench and 0.39–0.49 on FELM‑WK), which undermines LLMEVAL’s reliance on these systems to adjudicate long-form answers. This tension deserves a more explicit discussion.
- Table 5: The cost differential between FacTool and Factcheck‑GPT is informative, but the table mixes two datasets (FacTool‑QA + FELM‑WK) without a per-dataset breakdown. A per-dataset view would make the scalability story clearer.

## Potentially Missing Related Work
1) Huang et al., “Evaluating the Factuality of Large Language Models Using Multiple Plug-and-Play Fact Sources,” 2026 — Presents a configurable framework with pluggable evidence sources (human references, web, parametric knowledge), very close in spirit to CUSTCHECKER/LLMEVAL. Should be compared in Section 2 and in Section 4.2, with discussion of multi-source adjudication vs. single-checker reliance.

2) Cheng et al., “The FACTS Leaderboard: A Comprehensive Benchmark for Large Language Model Factuality,” 2025 — A broad leaderboard assessing multiple factuality dimensions. Add to Section 2.3 and discuss alignment/differences with FactQA/FactBench in Section 3.2–3.3; consider as an external point of comparison in Section 4.1.

3) Scire et al., “Truth or Mirage? Towards End-To-End Factuality Evaluation with LLM-OASIS,” 2026 — An end-to-end benchmark focusing on localized falsifications in long text, directly relevant to LLMEVAL’s goal of handling free-form answers. Discuss in Section 2.3 and consider evaluating LLMEVAL on this benchmark in Section 4.

4) Liu et al., “VeriFact: Enhancing Long-Form Factuality Evaluation with Refined Fact Extraction and Reference Facts,” 2025 — Proposes improved fact extraction and recall-oriented metrics for long-form answers; highly relevant to both CUSTCHECKER’s claim extraction and LLMEVAL’s evaluation. Cite in Section 3.1 and compare metrics in Section 4.2.

5) Wan et al., “FaStfact: Faster, Stronger Long-Form Factuality Evaluations in LLMs,” 2025 — Targets efficiency and human-aligned judgments via chunk-level claim extraction and confidence-based pre-verification. Add to Section 4.2 as a baseline emphasizing speed–accuracy–cost trade-offs, and to the leaderboard discussion.

6) Rahman et al., “Hallucination to Truth: A Review of Fact-Checking and Factuality Evaluation in Large Language Models,” 2026 — A survey contextualizing pipelines, metrics, and datasets; helpful to strengthen Section 2 and position OpenFactCheck among alternatives.

7) Cheng et al., “Long-form factuality in large language models,” 2024 — Introduces LongFact and SAFE, a canonical long-form factuality pipeline using web search and atomic facts. While long-form work is briefly alluded to (e.g., Wei et al., 2024), this specific methodology and benchmark deserve explicit discussion in Section 2.3 and comparison in Section 4.2.

## Comments Suggestions And Typos
Actionable suggestions:
- Validate LLMEVAL with human judgments on a representative subset of the four long-form datasets to quantify agreement with the automatic checker. Report Cohen’s kappa or Krippendorff’s alpha and analyze disagreements by cause (retrieval failure vs. verification misclassification).
- Add component-level diagnostics in CHECKEREVAL. For a few systems, log whether each false negative arises from retrieval (no supporting/contradicting evidence found) vs. verification (evidence present but misjudged). Even a partial analysis would make Table 4 more actionable.
- Provide frozen prompts, API versions, and configuration files in the appendix or supplementary material. Given Table 8’s cost differences and evolving API behavior, precise reproducibility requires concrete versioning and seeds.
- Revisit claims such as “>90% of claims are true” by either (a) cross-checking with a second, stronger checker (e.g., Factcheck‑GPT) on a stratified subsample or (b) reporting human adjudication on responses where FacTool says “true.” This will guard against optimistic bias from a single checker’s recall limitations on false claims.
- Expand Section 2 to cover recent leaderboards/frameworks (listed above) and articulate how OpenFactCheck differs in scope, measurement philosophy, or extensibility.

Typos and nits:
- “CHECKERÉVAL” vs. “CHECKEREVAL” inconsistency (Pages 2–3).
- Appendix A: “promot” → “prompt”.
- Page 2 caption “CHECKERÉVAL” uses an accent; standardize naming throughout.
- Figures 2 (all three panels): clarify y-axis units in captions, and specify normalization for cost bars.
- Page 5: “We use the strict evaluation criterion which considers...” — minor grammatical cleanup suggested.

Criteria that could raise my score:
- Release of code, configurations, and prompts; a short human validation study for LLMEVAL; component-level error attribution in CHECKEREVAL; and direct comparison to at least one recent long-form factuality framework/leaderboard. If these are addressed convincingly, I could move to Findings (3.0) or even Borderline Conference (3.5) depending on the strength of added analyses.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and figures/tables but, due to reliance on anonymized resources and external APIs, some reproducibility aspects cannot be fully checked.

## Soundness
3: Acceptable — The framework is coherent and the experiments are informative, but reliance on an automatic checker for LLMEVAL without human validation, and limited component-level analysis in CHECKEREVAL, temper the strength of the claims.

## Excitement
2.5: Between potentially interesting and interesting — Useful consolidation and tooling for practitioners, but limited algorithmic novelty and several measurement caveats.

## Overall Assessment
2.5 Borderline Findings — The paper offers a practical, user-friendly integration of fact-checking pipelines and a useful consolidation of factuality datasets, along with an informative cost/latency analysis. However, for ACL main track, the contribution is primarily integrative rather than methodological, and key evaluation aspects lack human validation and component-level diagnostics. With code/config releases, stronger baselines, and human agreement studies, this could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a limitations section noting dataset coverage, latency/costs, and dependence on external sources. I encourage expanding societal impact to discuss:
- Risks of over-reliance on automated judges for downstream moderation or misinformation detection, particularly given Table 4’s low F1 on false claims; false negatives can enable misinformation to persist.
- Language/domain skew in FactQA (Table 6 shows concentration in top-20 domains), which could bias leaderboards toward anglophone or high-resource topics.
- Potential privacy or licensing concerns when web evidence is fetched and stored; clarify retention/anonymization policies for the web client and any logs.

## Ethical concerns
None beyond the above suggestions; the paper acknowledges general concerns. Clarifying data handling and annotator consent for the human-labeled datasets reused would strengthen the ethics narrative.

## Needs Ethics Review
No

## Reproducibility
3: Reproducible with difficulty — The architecture and metrics are described, and pseudo-code is given, but exact prompts, API versions, and code are not available in the anonymized paper. External dependencies and pricing models change, which can affect replication.

## Datasets
3: Potentially useful — FactQA is a consolidation; if released with clear splits/metadata and documentation, it can be useful. Strength would increase if human labels or adjudications accompany the long-form subsets.

## Software
3: Potentially useful — The framework appears practical and the UI is helpful. The score assumes the eventual release of code/configs post-review; otherwise it would be 2.