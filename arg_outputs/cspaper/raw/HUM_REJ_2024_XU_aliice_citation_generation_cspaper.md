# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper squarely targets NLP evaluation for long‑form QA with citations, proposing metrics and an evaluation framework; this fits “Resources and Evaluation,” “Generation,” and “Question Answering.”

## Minimum Quality
Pass ✅. The paper contains Abstract, Introduction, Background & Task Definition, Method (incl. equations and Algorithm 1), Datasets and Implementation, Experiments and Results (Tables 1–4; Figures 1–4), Error Analysis, Related Work, Conclusion, and a Limitations/Ethics Statement. The contribution is clear and empirically supported on two datasets.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. No manipulation or hidden prompts targeting reviewers are present in the paper text.

# Expected Review Outcome:

## Paper Summary
This paper introduces ALiiCE, an automatic evaluation framework for positional fine‑grained citation generation in long‑form QA. The core idea is to parse each sentence into atomic claims using dependency trees and an LCA‑based pruning procedure, align each inline citation group to the nearest head token, and evaluate support with an NLI model at the atomic‑claim level. Three metrics are proposed: positional fine‑grained citation recall, positional fine‑grained citation precision, and CPCV (coefficient of variation of citation positions) to quantify dispersion of citations. Experiments on ASQA and ELI5 compare GPT‑3.5, GPT‑4, and LLaMA‑3‑8B, and show ALiiCE tends to yield lower recall but higher precision than sentence‑level ALCE, with case studies illustrating failure modes of sentence‑level evaluation.

## Summary Of Strengths
- Timely problem formulation. The paper targets a clear gap: sentence‑level citation scoring conflates multiple claims within a sentence and can over/under‑credit citations. The task definition in Section 2.2 with Equation (1) formalizes word vs. citation groups clearly.
- Methodological clarity and implementability. The dependency‑based parsing plus LCA operations are well specified (Algorithm 1, Section 3.3). The worked example in Figure 2 is concrete and explains how claims are extracted and scored.
- Metrics that push beyond sentence level. The per‑claim recall/precision (Sections 3.4.1–3.4.2 with Equation (2)) and CPCV (Equation (5)) are simple enough to implement, making ALiiCE feasible for wider adoption.
- Empirical observations are informative. Tables 1–4 show consistent patterns across datasets: compared to ALCE, ALiiCE typically lowers recall and raises precision (also visualized in Figure 3). The paper discusses practical implications and when the stricter decision threshold might be preferable (e.g., professional domains).
- Useful qualitative analyses. Figure 4’s two cases demonstrate concrete sentence‑level pitfalls: long-context NLI failures and precision inflation due to overlapping evidence across atomic claims. These examples are persuasive and tied to the claims in Sections 5.1–5.2.
- Error analysis and sanity checks. Table 5 examines parsing errors and their downstream effect on NLI decisions; the <1% inconsistency after claim refinement suggests robustness to some parser noise.

Specific figure/table comments supporting strengths:
- Figure 2 effectively demonstrates end‑to‑end parsing and scoring: it shows the original dependency tree, identifies the LCA node, presents the pruned subtrees for each claim, and then separately evaluates recall and precision per claim. This figure anchors the methodology and clarifies the difference between claim‑level and sentence‑level scoring.
- Table 2 and Table 4 isolate outputs that actually contain fine‑grained citations, where the recall drop and precision gain under ALiiCE become more pronounced than in Table 1 and Table 3, substantiating the paper’s central assertion about stricter, more conservative decisions.

## Summary Of Weaknesses
1) Heuristic parsing without guarantees or comparative alternatives.  
- The LCA‑based pruning has many case rules (Algorithm 1 and Appendix A) and a heuristic citation‑to‑node matching rule (“closest token, prefer left”). There is no formal guarantee that the extracted subtree corresponds to the intended atomic claim, particularly in non‑canonical word orders, appositives, or multi‑clausal constructs. A controlled evaluation against gold claim spans or a stronger parser variant is missing; Appendix B figures (Figures 5–13) are illustrative but anecdotal.

2) Sensitivity to parser and NLI choice not quantified.  
- Section 4.2 fixes SpaCy and TRUE (T5‑11B) for NLI, but there is no sensitivity analysis with alternative parsers (e.g., Stanza, trankit) or NLI models. Because ALiiCE’s judgments are the product of both components, we need to know how stable the metrics are to these choices. Results could materially change with a different NLI or even different max‑length truncation. Equation (2) is binary; no calibration or thresholding variants are explored.

3) Binary entailment is too coarse for partial support and compositional claims.  
- The framework collapses support to 0/1, which fails to capture partially‑supported or under‑specified claims and can penalize otherwise useful citations. This limitation becomes salient in complex answers and is not contrasted against graded support metrics. The qualitative cases (Figure 4) show benefit in disambiguation, but do not address partial support or attribution granularity.

4) CPCV construct validity is unclear.  
- Section 3.4.3 posits CPCV as a proxy for “capability to place fine‑grained citations.” Yet dispersion can be increased by adding arbitrary citation marks or by inserting multiple citations adjacent to each other mid‑sentence. There is no user study or correlation analysis with human‑judged usefulness. Further, CPCV is undefined for sentences with a single citation mark and excludes sentences without citations, potentially biasing comparisons across models that differ in when they choose to cite.

5) Precision conflation when recall = 0 and groupwise scoring design.  
- By definition, if claim‑level recall is 0, ALiiCE assigns precision 0 as well (Section 3.4.2). This couples two dimensions and may obscure interesting behaviors such as “wrong but non‑redundant” citations. Also, precision is averaged over citations within a group; a single redundant citation depresses the entire group’s precision, which could be harsh when models over‑cite defensively. An ablation varying group granularity or performing per‑citation rather than per‑group precision would clarify this.

6) Limited scope of evaluation and weak diversity.  
- Only two datasets are used (ASQA dev and 1k ELI5 val), both open‑domain. The claim that the method benefits professional domains is not substantiated with domain‑specific datasets (e.g., biomedical, legal, scientific). Multi‑hop or structured answers, where intra‑sentence claim interleaving is common, would stress‑test the parser and the decision rules.

7) Missing human validation of atomic claims and metric correlations.  
- While Table 5 shows low NLI flips after GPT‑3.5 claim rewrites, there is no human check that the parsed claim text truly matches the intended scope of the inline citation. Moreover, there is no study correlating ALiiCE scores with human judgments across systems, which weakens the external validity of adopting ALiiCE as a replacement or complement to ALCE.

8) Incomplete ablations and significance reporting.  
- The results in Tables 1–4 provide means and standard deviations, but there is no statistical significance testing across model settings. There are no ablations on the matching heuristic (nearest token vs. head selection), LCA tie‑breakers, or text cleaning choices. Given the complexity of Algorithm 1 and Appendix A rules, this is important.

9) Relation to concurrent fine‑grained citation literature is thin.  
- The Related Work section does not compare against several directly relevant fine‑grained citation generation and evaluation works that emphasize span‑level or per‑claim alignment and could be used as alternative evaluators or baselines (see “Potentially Missing Related Work” below).

10) Figure 3 interpretation needs nuance.  
- Figure 3 shows the typical recall drop and precision rise under ALiiCE versus ALCE for three models. However, it would help to annotate exact deltas and discuss whether the lower recall stems more from stricter claim boundaries or from NLI truncation due to multiple concatenated passages per claim. Without this, the “conservative” interpretation in Section 5.2 remains partly speculative.

Specific references to figures/tables that undermine or complicate claims:
- Table 1 (ASQA) and Table 3 (ELI5) include “Fluency” and “Correctness” that vary widely across models and settings. The paper briefly interprets CPCV yet does not analyze whether higher CPCV correlates with better Fluency or Correctness. For example, LLaMA‑3‑8B has much higher CPCV (0.44/0.45 in Table 1; 0.53/0.61 in Table 3) but often worse citation recall and sometimes better fluency. This contradicts a simplistic “dispersion equals capability” story and needs deeper analysis.
- Figure 4’s Case 1 attributes failures partly to long‑context NLI on concatenated passages, but ALiiCE still uses concatenation per claim; the reduction is relative, not absolute, and the paper does not quantify how often claim‑level concatenations still exceed NLI limits.

## Potentially Missing Related Work
1) Zhang et al., “LongCite: Enabling LLMs to Generate Fine‑grained Citations in Long‑Context QA,” 2025 — Proposes fine‑grained citation generation and GPT‑4o–based citation F1/precision metrics. Should be discussed in Section 6 (Citation Evaluation) and compared experimentally as an alternative evaluator to ALiiCE in Section 5 (e.g., add as another column or a post‑hoc analysis).
2) Zhang et al., “Towards Fine‑Grained Citation Evaluation in Generated Text: A Comparative Analysis of Faithfulness Metrics,” 2024 — Benchmarks multiple faithfulness metrics for fine‑grained support levels. Situate in Section 3.4 as related alternatives to binary entailment; discuss partial‑support handling and potential integration with ALiiCE.
3) Choi et al., “CiteGuard: Faithful Citation Attribution for LLMs via Retrieval‑Augmented Validation,” 2025 — Introduces a retrieval‑aware citation validator approaching human judgment. Compare in Section 5 as a complementary evaluation tool and acknowledge limitations of static NLI‑only scoring.
4) Yeginbergen et al., “Explicit Evidence Grounding via Structured Inline Citation Generation,” 2026 — Generates structured inline citations with span‑level grounding and evaluates document‑ and span‑level correctness. Discuss in Section 2.2/6 as an alternative to dependency parsing for defining atomic claims; consider span‑level evaluation as a baseline or ablation.
5) Peng et al., “FineRef: Fine‑Grained Error Reflection and Correction for Long‑Form Generation with Citations,” 2026 — Two‑stage reflection and correction for per‑citation mismatch. Reference in Section 5 to highlight systems designed to improve fine‑grained citations and consider evaluating them with ALiiCE metrics.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide a sensitivity study: swap SpaCy with at least one other dependency parser and swap TRUE with at least one strong NLI variant (e.g., DeBERTa‑MNLI‑xxl or a recent instruction‑tuned NLI model) to quantify robustness. Report effect sizes on Tables 1–4.
- Validate CPCV: include a small human study correlating CPCV with perceived citation usefulness or add a simulation showing how CPCV behaves under adversarial but unhelpful dispersion (e.g., many short citations clumped together). Alternatively, normalize CPCV by number of citations per sentence and report both.
- Uncouple precision from recall: report per‑citation precision even when recall = 0, or add an auxiliary “redundancy rate” that is recall‑agnostic. Provide variance across claims and sentences, not only means.
- Present significance testing and ablations: include paired tests across system variants in Tables 1–4. Ablate the node‑matching heuristic (nearest vs. head of governed phrase) and key case rules in Appendix A.
- Add a small human audit of parsed claims: sample a few hundred claims, ask annotators to judge whether the extracted text correctly captures the intended scope of the inline citation. Report agreement and error types.
- Clarify Equation (3): explicitly define |s_i| as tokenized length after text cleaning or before; ensure consistency with the indexing j in Equation (1).
- Expand Figure 3: add numeric deltas atop bars, and provide a breakdown of how often claim‑level concatenations still hit NLI length limits.
- Consider partial support: report an auxiliary graded entailment variant (e.g., 3‑way support/partial/contradict/neutral), at least as an analysis.

Typos and minor issues:
- Page 3, “possess ing” should be “possessing.”
- Page 4, Algorithm 1, line 12: the condition formatting “node_lca = node_i ∨ (node_lca ≠ node_j ∧ T_i < T_j)” is hard to parse; define “<” clearly as left‑to‑right order earlier.
- Page 5, Table 2 caption: “The best performances are highlighted in bold.” but bolding is not visible in the provided markdown; ensure consistency in camera‑ready.
- Page 6, Table 3: model labels mix “psg‑sum” vs “psg‑summ”; standardize.
- Page 14, Figure 9: the claim text shows a stray “$25^{\prime \prime}$”; likely a latex artifact for quotation marks.

Criteria to change my score upward in rebuttal:
- Provide at least one robustness study (parser and/or NLI swap) with stable results.
- A small human validation of claim spans that shows high accuracy (>90%) of ALiiCE parsing.
- Clearer justification and validation for CPCV, or replace it with a better‑founded dispersion/usefulness proxy.
- Add comparisons or discussion against the missing fine‑grained citation literature listed above.

## Confidence
4: Quite sure after careful checking — I checked the equations, algorithm, and results carefully; some details (e.g., parser/NLI robustness) remain untested but the main critique stands.

## Soundness
3.5: Between Acceptable and Strong — The framework is coherent and executed, but lacks robustness studies, significance testing, and validated construct metrics (CPCV).

## Excitement
3.0: Interesting — The problem is relevant and the approach is practical; the evaluation gaps and metric questions temper enthusiasm.

## Overall Assessment
3.5 Borderline Conference — A solid and timely step toward atomic claim‑level citation evaluation with clear methodology and informative results, but it needs robustness checks, stronger validation of CPCV and claim parsing, and broader related‑work integration to reach a confident main‑track accept.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges language and parser transfer limitations and domain scope. Additional points worth noting: binary entailment could misrepresent nuanced evidence, and errors in claim extraction might mislabel faithful citations as unfaithful, potentially discouraging useful citations. The work nonetheless aims to increase transparency and verifiability, which has positive societal value if metrics are reliable.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Equations, Algorithm 1, datasets, models, and prompts are described; code and parser/NLI versions are specified. Some heuristic details in Appendix A may still require careful reimplementation.

## Datasets
2: Documentary — No new datasets are released; the setup on ASQA/ELI5 is useful but not a new resource.

## Software
3: Potentially useful — If released, the parsing and metric code would likely be useful; otherwise, reimplementation is feasible from the paper.