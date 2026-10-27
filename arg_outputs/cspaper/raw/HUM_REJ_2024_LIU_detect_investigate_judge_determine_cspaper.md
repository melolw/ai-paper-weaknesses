# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes DAFND, a four-stage pipeline for few-shot fake news detection using large language models (LLMs): Detect, Investigate, Judge, and Determine. The Detection module prompts an LLM to extract N=5 keywords. The Investigation module gathers two types of evidence: (i) “inside” evidence by retrieving k=2 nearest positive and negative training samples via DeBERTa embeddings of the concatenated keywords, and (ii) “outside” evidence via Google search constrained to Wikipedia (top-1 result) using SerpAPI. The Judge module runs two parallel prompt-based classifiers over the inside and outside evidence, each producing a label and rationale. The Determination module then aggregates these two judgments, especially when they disagree, via an additional LLM prompt to produce the final label. Experiments on FakeNewsNet’s PolitiFact and Gossipcop, under K-shot settings (K in {8,32,100}), report accuracy and F1, with ablations (removing the Determination module) and qualitative case studies.

## Summary Of Strengths
- Clear, modular formulation. Figure 2 lays out the Detect–Investigate–Judge–Determine pipeline coherently, making it easy to understand where each component fits and how signals from training data and the web are combined.
- Practical dual-evidence design. The “inside” kNN retrieval over few-shot training data directly addresses the in-context example selection challenge, while the “outside” web retrieval helps mitigate staleness in LLM training data.
- Strong headline numbers across two benchmarks. In Table 2, DAFND consistently outperforms traditional, LLM-only, and hybrid baselines on PolitiFact and Gossipcop across K-shot configurations. The gains are large in accuracy (e.g., PolitiFact ACC 86.5–88.5 vs. best baseline 82.5) and in F1 (e.g., PolitiFact F1 81.4–84.4).
- Ablation suggests each component matters. Figure 3 shows the full system outperforming both Inside Judge and Outside Judge across all K and both datasets, which supports the claim that the Determination module is not redundant.
- Useful prompt details and system transparency. Equations (1)–(6) specify the data flow precisely, and Appendix A provides the core prompts, aiding reimplementation.
- Qualitative analysis is informative. Figure 4 illustrates success cases and disagreement resolution by the Determination module, helping readers understand the model’s behavior.

## Summary Of Weaknesses
1) Baselines and fairness of comparison need strengthening.
- LLM-only baselines use 6 randomly selected demonstrations due to token limits, while DAFND retrieves semantically nearest demonstrations (kNN over DeBERTa) tailored to each test instance. This retrieval advantage, central to the contribution, is not afforded to LLM baselines, potentially inflating the observed gaps. A fairer setup would compare to strong retrieval-augmented prompting baselines where in-context examples are also selected via kNN (e.g., as in prompt retrieval literature) or to RAG-style fact-checkers using the same LLM and search stack.
- The outside retrieval restricts to en.wikipedia.org and returns top-1 only. A competitive RAG baseline with multi-source, top-k retrieval, simple re-ranking, or verified fact-checking sources could alter the relative performance.

2) Limited reporting on variability and statistical significance.
- Results in Table 2 appear to be single-run numbers with a single random few-shot sample per K. Few-shot performance is notoriously variable. No standard deviations, confidence intervals, or statistical tests are reported. This is a major issue for claims of superiority in few-shot regimes.

3) Metric choice and class imbalance.
- Gossipcop test set is imbalanced (Table 1: 3,200 true vs. 1,060 fake). Reporting accuracy alongside positive-class F1 is not enough; macro-F1, precision/recall per class, and perhaps AUROC/PR-AUC would provide a more complete picture. For instance, Table 2 shows relatively low F1 (53.5–56.5) despite high accuracy (>82%), suggesting possible skewed decision thresholds or over-reliance on the majority class. The paper should explicitly analyze this.

4) Sensitivity and design ablations are missing.
- Several key design choices are fixed without justification or sensitivity analyses: N=5 keywords, top-1 outside evidence, k=2 neighbors per class, use of only keyword concatenations (Eq. 2) instead of full text for retrieval. Ablations like N ∈ {3,5,8}, k ∈ {1,2,4}, outside top-k ∈ {1,3,5}, and using full news text or title+text for M would clarify robustness and inform best practices.
- The DeBERTa-base encoder for retrieval is chosen without comparison to alternatives (e.g., Sentence-BERT, E5, Contriever, or domain-adapted encoders). This matters because the quality of nearest-neighbor demonstrations is central to Inside Judge performance.

5) Outside retrieval setup is narrow and under-specified for evidence quality.
- Constraining queries to Wikipedia and taking top-1 result risks brittle behavior for emerging or entertainment-domain claims common in Gossipcop. The method does not discuss handling non-Wikipedia evidence, multi-hop retrieval, or contradicting sources. Figure 4(b–c) shows disagreements; however, there is no systematic analysis of when Wikipedia-only evidence helps or hurts.
- It is unclear how long outside evidence snippets are, how they are preprocessed, and how non-English results or regional differences are handled.

6) Determination module procedure needs clearer, reproducible parsing.
- In Section 4.4 and Eq. (6), the LLM consumes Pi, Ri, Po, Ro and returns Pf. The paper should specify exact output formats, tie-breaking logic, and how non-conforming generations are parsed. For LLM baselines, the authors count any non-categorizable output as wrong; we need to know if the same strict parsing is applied to DAFND’s three LLM calls, and what fraction of cases needed fallback or regeneration.

7) Limited scope of ablation (Figure 3).
- The only ablations remove the Determination module, effectively comparing Inside vs Outside vs Full. This does not isolate the effect of the Detection module’s keywording, nor the impact of kNN vs random demonstration selection, nor the impact of restricting retrieval to Wikipedia vs broader web. Without these, it is hard to attribute gains to specific components.

8) Missing or thin baselines closely aligned with the proposed design.
- There is no direct comparison with: (i) prompt-retrieval methods that learn/select in-context examples (e.g., retrieve in-context exemplars via semantic similarity); (ii) generic RAG fact-checkers using the same LLM and web search to predict veracity; (iii) simple voting/ensemble between an “inside-only” LLM and an “outside-only” LLM without the extra Determination prompt, to test whether the final improvement is due to ensembling or to the specific aggregation prompt.

9) Claims of generality vs. experiment scope.
- The method is evaluated on two English text-only datasets. Given the entertainment domain difficulty (as also noted by the authors), an extension to broader topics, cross-domain transfer, or languages would better support the “dual-perspective” generality claim. Even within FakeNewsNet, an analysis of temporal splits to stress the Information Scarcity claim would be valuable.

10) Presentation and small inconsistencies.
- The figures are helpful but some labels and references could be tighter: Figure 2 uses “PLM-M” without defining M in the caption; please ensure consistent symbol definitions. Some example strings in Figure 4 include typos or awkward names (e.g., “Hailas Steinfeld,” “Met Gela”), making it hard to tell if these are OCR or dataset artifacts. Clarifying this would improve readability and trust in the examples.

Explicit references to paper elements:
- Figure 2: Effective high-level architecture, but details like how the DeBERTa embedding H (Eq. 2) from only keywords compares to using full text are not explored; this figure would be even stronger with a note on evidence lengths and parsing.
- Figure 3: The ablation clearly shows full DAFND > variants across both datasets and all K. However, the lack of error bars makes it hard to assess reliability, and the variants do not isolate the role of the Detection module or retrieval scope.
- Figure 4: The case studies (a–c) are illustrative for agreement and disagreement scenarios. They support the paper’s claim that the Determination module can resolve conflicts, yet they also reveal dependency on specific sources and fragile reasoning in entertainment news (b–c). Adding one clear failure case in the main text, beyond Appendix B, would make the limitations more balanced.
- Table 1: Dataset statistics help contextualize class imbalance, but the main text should comment explicitly on how this affects metric interpretation, especially for Gossipcop.
- Table 2: Main results are comprehensive, but lack of variance/significance and the absence of retrieval-augmented prompting or RAG-style baselines make it hard to judge whether the gains are due to the dual-perspective design or to better in-context example selection alone.

## Potentially Missing Related Work
1) Bai et al., “A Large Language Model-based Fake News Detection Framework with RAG Fact-Checking,” 2024 — Directly relevant RAG-style fact-checking approach that combines LLM claim processing with external retrieval. Should be discussed in Section 2 and compared experimentally or at least in design discussion near Section 4.2 (Outside Investigation) and Section 5.2 (Table 2).
2) Yi et al., “Challenges and Innovations in LLM-Powered Fake News Detection: A Synthesis of Approaches and Future Directions,” 2025 — A survey synthesizing recent LLM-powered detectors, including retrieval, multi-agent reasoning, and graph-enhanced approaches. Citing this in Related Work (Section 2) would position DAFND more clearly in the evolving landscape.
3) Aspromonte et al., “Beyond Fact-Checking: A Scalable, Domain-Agnostic, and Explainable System for Automated Fake News Detection,” 2025 — Uses LLMs with dynamic web search for veracity decisions and explanations. It is a close conceptual neighbor; include in Section 2 and discuss differences in Section 4.2–4.4 (evidence acquisition and aggregation).
4) Chen et al., “Enhancing text-centric fake news detection via external knowledge distillation from LLMs,” 2025 — Presents an alternative to online LLM prompting by distilling LLM-generated knowledge into smaller detectors. Adding to Related Work and Discussion would clarify trade-offs vs. DAFND’s online tool-use.
5) Wu et al., “ZoFia: Zero-Shot Fake News Detection with Entity-Guided Retrieval and Multi-LLM Interaction,” 2026 — Although zero-shot and later, it is a directly related multi-perspective LLM system with retrieval. Mentioning it in Related Work and contrasting the few-shot vs zero-shot setups would help readers situate DAFND.
6) Harris et al., “Multimodal misinformation detection across diverse languages using RAG and LLMs,” 2026 — Extends the retrieval+LLM idea to multilingual/multimodal settings. Briefly referencing in Related Work could motivate future multimodal, multilingual extensions.
7) Jiang et al., “Cross-Modal Augmentation for Few-Shot Multimodal Fake News Detection,” 2025 — Few-shot, but multimodal augmentation. Add to Section 2 to acknowledge related few-shot directions beyond text-only pipelines.

## Comments Suggestions And Typos
Actionable questions and suggestions that could change the assessment:
- Stronger baselines and controls:
  - Add a retrieval-augmented LLM baseline that selects in-context examples via the same DeBERTa kNN mechanism used in DAFND’s Inside Investigation, and a RAG-style fact-checker using the same LLM and search engine. This would isolate the value of dual-perspective aggregation and the Determination module beyond retrieval quality alone.
  - Include a simple ensemble of Inside Judge and Outside Judge (e.g., majority vote or confidence-weighted) to test whether the Determination prompt offers additional benefit beyond ensembling.
- Variance and significance:
  - Report means and standard deviations over multiple random seeds for few-shot sampling and, if feasible, multiple random demonstration draws for baseline LLMs. Include paired significance testing where appropriate for Table 2 and Figure 3.
- Sensitivity ablations:
  - Vary N (keywords), k (neighbors), and top-k outside retrieval; compare keyword-only vs full text representations in Eq. (2). Evaluate alternative retrieval encoders (e.g., Sentence-BERT, E5, Contriever). This will strengthen claims about design choices.
- Metrics and imbalance:
  - Add macro-F1, per-class precision/recall, and PR-AUC for Gossipcop to complement Table 2. Analyze thresholding and calibration, especially given the low F1 but high accuracy.
- Outside retrieval generality:
  - Evaluate with broader web domains beyond Wikipedia, include top-k evidence with brief re-ranking, and provide an error analysis on when external retrieval contradicts ground truth.
- Clarify parsing and failure handling:
  - Specify exact output formats and parsing rules for Pi, Po, and Pf, and report the rate of non-conforming generations and how you handled them consistently across methods.

Minor issues and typos:
- Several named entities in Figure 4 examples appear misspelled (“Hailas Steinfeld,” “Met Gela”). Please verify whether these are dataset artifacts or transcription errors.
- In Section 5.1, clarify whether “⑤ ∼ ⑥” should read “⑤ ∼ ⑧” when referring to LLM-based baselines; there seems to be a mismatch.
- Consistency: ensure notation like M in Figure 2 and Eq. (2) is defined once and used consistently. Also check capitalization (“google” vs “Google”).

Criteria that could raise my score:
- Adding the stronger retrieval-augmented baselines and reporting multi-seed significance while retaining substantial gains; plus sensitivity analyses that justify the fixed design choices.
- Improved metric reporting addressing imbalance, with clear evidence that gains hold across metrics and seeds.
- A more comprehensive related work discussion covering RAG-style fact-checking and prompt-retrieval methods.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5 Between Poor and Acceptable: Some central claims are promising, but the empirical evidence is weakened by limited baselines, lack of variance, and missing sensitivity/significance analyses.

## Excitement
2.5 Between potentially interesting and interesting: The dual-perspective framing is appealing and the pipeline is neat, but the current evaluation does not yet justify main-track acceptance.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The modular DAFND pipeline is clear and practical, and the reported gains are sizeable. However, the evaluation lacks stronger retrieval-augmented baselines and multi-seed significance; sensitivity studies for key hyperparameters are absent; metric reporting is incomplete for imbalanced data; and some implementation details about parsing and retrieval scope are under-specified. These issues are fixable, and the work could be suitable for Findings after strengthening the experimental section and positioning with additional related work.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section noting computational overhead and reliance on inference-only prompting. Additional considerations worth discussing:
- Bias and coverage in outside retrieval: restricting to Wikipedia top-1 may privilege certain perspectives and under-represent marginalized viewpoints, potentially skewing veracity judgments.
- Risk of overtrusting externally retrieved snippets: without multi-source corroboration or quality control, the system may be misled by outdated or context-mismatched pages, especially for time-sensitive or entertainment rumors.
- Transparency: while rationales are produced, they are LLM-generated and may appear convincing without being faithful. Consider transparency measures or human-in-the-loop review when deployed.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Prompts are given, model and retrieval APIs are specified, and key hyperparameters are listed. Multi-seed details, parsing rules, and sensitivity studies would further improve reproducibility.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: Code, if released as stated, would be useful for others to build on or baseline against, particularly the multi-judge prompting and determination pipeline.