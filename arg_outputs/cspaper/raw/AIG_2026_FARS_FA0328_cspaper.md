# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper studies whether correcting position bias in long-context LLMs is sufficient to make single-pass attention-based document sorting perform as well as iterative Attention Sorting. The proposed Debiased One-Pass Attention Sorting estimates a per-prompt position-bias curve from distractor documents, then subtracts or divides it out from raw attention masses (computed from the first generated token’s attention over all layers and heads; Equation 1) before reordering documents. Experiments on SynthWiki@28K with two models show: (a) on LLaMA‑2‑7B‑32K‑Instruct, debiasing changes nothing relative to uncalibrated k=1 sorting (both 94.83%); (b) on YaRN‑Llama‑2‑7b‑64k, debiasing improves k=1 by +8.67pp but still trails k=5 by 14.84pp. The authors conclude that explicit position-bias correction alone cannot replace iterative sorting and hypothesize additional gains come from attention-context refinement across passes.

## Summary Of Strengths
- Clear, testable hypothesis with a simple, transparent intervention. The per-prompt bias curve is well specified procedurally in Section 3.3, and Equation (1) precisely defines the attention mass used.
- Negative-result character is valuable: the paper challenges a plausible assumption that position-bias correction might close the gap to iterative sorting.
- Results are communicated concisely with reproducible ingredients: models, dataset construction protocol, and seeds are documented.
- Figures and tables are informative:
  - Figure 1 clearly contrasts pipelines and highlights the added calibration component, making the computational tradeoff explicit (2 prefills vs 6).
  - Figure 2 shows how accuracy and mean gold-document position progress with k, supporting the claim that improvements persist even after the gold doc is near the end.
  - Table 1 and Table 2 give per-seed and mean±std results, enabling readers to assess stability and the size of the remaining gap.
- The paper’s main takeaway is crisp: on a well-tuned model, position-bias debiasing had no effect; on a highly recency-biased model, it helped but was far from sufficient. This provides practical guidance on when such calibration is likely to matter.

## Summary Of Weaknesses
1) Overgeneralized conclusion from a narrow setup
- The core claim that position-bias correction is “insufficient” is drawn from only two models and a single synthetic benchmark (SynthWiki@28K). The conclusion risks overreach beyond this setting. For instance, no real-world RAG datasets or multi-evidence tasks are evaluated, nor are other long-context suites like LongBench, Needle-in-a-Haystack, or multi-hop QA benchmarks.
- Figure 2 is only for LLaMA‑2‑7B‑32K‑Instruct. A similar progression plot for YaRN would help verify whether the same “beyond bias” effects hold there and whether the convergence behavior differs.

2) Missing or weak baselines
- Although Section 2.3 cites related ranking ideas (ICR, permutation self-consistency, RankFusion), there is no empirical comparison. Even one strong reference baseline beyond Attention Sorting would contextualize the effectiveness of the proposed debiasing strategy.
- Closely related position-bias mitigation techniques at inference-time are not compared (see “Potentially Missing Related Work”), leaving readers unsure how this calibration stacks up against alternatives that do not require iterative sorting.

3) Limited analysis of the bias-curve estimator
- The estimator trims the top α=0.05 attention documents, bins positions (B=20), uses medians, and interpolates, but there is no sensitivity analysis for α, B, choice of additive vs divisive debiasing, or interpolation scheme. The paper asserts defaults but does not justify them or report ablations.
- The “most docs are distractors” assumption is central, yet the method’s robustness when a query accidentally causes widespread spurious attention spikes is untested. A stress test with adversarially noisy contexts would be informative.

4) Attention-mass design choices are under-explored
- Equation (1) aggregates only the first generated token’s attention. This can be fragile, particularly with attention sinks and early-layer artifacts. There is no ablation over using multiple generated tokens, per-layer weighting, head selection, or normalization by token counts or attention entropy. These could change conclusions.
- Summing across all layers/heads without normalization implicitly assumes comparability, which is not guaranteed. For example, layers with different sparsity or scaling may dominate a_i. No justification or control is provided.

5) Statistical support is thin
- Table 1 and Table 2 report mean±std over three seeds of 200 examples each, but no significance tests are presented. On LLaMA, the 0.67pp gap between k=1 and k=5 might be within noise; conversely, on YaRN, confidence intervals or tests would better support the “closes only 37% of gap” narrative.

6) Compute and latency not measured
- The pitch is about cutting prefill passes. However, the paper reports only pass counts, not wall-clock latency, throughput, or memory footprints. Model-level throughput differences, KV cache reuse strategies, and attention extraction overheads could shift the practical tradeoff.

7) Evaluation design matches the method’s assumptions
- The paper assumes exactly one gold document. SynthWiki conforms to this, so the method benefits from its own assumption. How would calibration behave with multiple relevant documents, or when relevant evidence is diffuse? Without such stress tests, the behavioral claims remain limited.

8) Incomplete clarity on implementation details that affect reproducibility
- While a code link is given, the paper itself lacks precise details about: tokenization boundaries for S_i, how answers are extracted or scored as “exact match” in edge cases, attention extraction mechanics for the two different models, and any handling of special tokens that might skew attention (e.g., BOS, system prompts).
- Greedy decoding is assumed throughout; no analysis of whether temperature or nucleus sampling changes the attention signals or the downstream accuracy.

9) Missing directly relevant related work
- Several recent methods offering inference-time or training-time position-bias mitigation are not cited or discussed, and some are close to this paper’s goals. This weakens the positioning of the contribution and complicates assessing novelty.

10) Limited discussion of failure modes
- The conclusion mentions limitations briefly, but the paper does not characterize canonical failure patterns when debiasing helps but still loses to k=5. For instance, are errors clustered when relevant docs start in the middle vs early? Do adjacency effects dominate after k=2, as suggested? Qualitative examples would help.

Figure- and table-specific comments
- Figure 1: This schematic is effective at communicating the pipeline difference and computational budget. It supports the cost-oriented motivation, but because the paper does not provide latency numbers, the figure’s practical impact argument remains conceptual.
- Figure 2: The blue curve (accuracy) and orange curve (gold position) show that even after the gold doc is placed near the end by k=1, additional iterations can nudge accuracy upward. This visualization underpins the “beyond debiasing” hypothesis. However, the y-axes are compact and there is no confidence band; given the small numerical changes, statistical context is needed.
- Table 1 and Table 2: These tables drive the main claims. Table 1’s exact equality between uncalibrated and debiased k=1 on LLaMA is compelling for the “no effect” conclusion in that setting. Table 2’s +8.67pp for YaRN is substantial, yet the residual 14.84pp to k=5 indicates meaningful missing ingredients. The paper could strengthen both by adding significance tests and by reporting how often the gold doc is actually moved to the last position by each method.

## Potentially Missing Related Work
1) Wang et al., Eliminating Position Bias of Language Models: A Mechanistic Approach, 2024 — Proposes PINE, a training-free inference-time intervention targeting position invariance via attention-mask modifications and reordering. Directly relevant as an alternative to attention-score calibration; should be discussed in Section 2.1/2.3 and considered as a baseline in Section 4.

2) Zehle et al., Can Calibration of Positional Encodings Enhance Long Context Utilization?, 2026 — Introduces CALIOPE, calibrating RoPE to reduce lost-in-the-middle and recency bias. Operates at the positional-encoding level and is a natural point of comparison; cite in Related Work and, if feasible, evaluate alongside Debiased k=1 in Section 4.

3) Yu et al., Mitigate Position Bias in LLMs via Scaling a Single Hidden States Channel, 2025 — Shows a simple inference-time, channel-scaling method that mitigates positional bias. Highly pertinent to the same problem scope; should be discussed in Section 2 and considered as a lightweight baseline.

4) Wang et al., Position Bias Mitigates Position Bias: Mitigate Position Bias Through Inter-Position Knowledge Distillation, 2025 — Pos2Distill is a training-based approach that transfers performance from advantaged to disadvantaged positions. Even if training-based, it is an important comparator for framing the limits of inference-only techniques; discuss in Section 2 and reference when interpreting the insufficiency of one-pass calibration.

5) Tian et al., Distance between Relevant Information Pieces Causes Bias in Long-Context LLMs, 2024 — LongPiBench reveals biases driven by relative spacing of multiple relevant chunks. Useful to extend evaluation beyond single-gold-doc settings; add to Related Work and consider as an additional benchmark in Section 4.

6) Schuhmacher et al., Information Representation Fairness in Long-Document Embeddings: The Peculiar Interaction of Positional and Language Bias, 2026 — Proposes attention calibration for pooled embeddings to balance positional contributions. While focused on embeddings, the calibration framing is conceptually close and can inspire alternative debiasing scores; discuss in related work.

7) Wang et al., More Thinking, More Bias: Length-Driven Position Bias in Reasoning Models, 2026 — Introduces Position Bias Score (PBS) and diagnostics showing bias increases with longer reasoning chains. Relevant to the interpretation that iterative procedures may change the available evidence; include in Related Work and consider PBS-style metrics when analyzing long-context behavior.

## Comments Suggestions And Typos
Actionable suggestions that could change my evaluation:
- Add stronger baselines and ablations:
  - Compare against at least one inference-time positional mitigation baseline (e.g., PINE, CALIOPE, channel-scaling). This will contextualize how much of the k=5 gap remains with other single-pass remedies.
  - Provide ablations on α, B, interpolation method, additive vs divisive debiasing, and on using multiple generated tokens rather than only the first. Also test per-layer or per-head weighting and normalization to mitigate domination by specific layers or attention sinks.
- Strengthen empirical scope and statistical support:
  - Evaluate on at least one real RAG or multi-hop QA dataset and one standard long-context suite. Include a multi-relevant-evidence setting that violates the single-gold assumption.
  - Report statistical significance for Table 1 and Table 2. Confidence intervals or bootstrap tests would help; for Figure 2 add confidence bands or error bars.
  - Provide wall-clock latency and throughput (tokens/sec), including attention-extraction overheads. Prefill counts are informative but not sufficient for practical claims.
- Deepen analysis:
  - Include a YaRN version of Figure 2 to visualize iteration dynamics under severe recency bias.
  - Offer qualitative examples where debiasing fails but extra iterations succeed, and probe adjacency/context-refinement hypotheses. For instance, analyze attention maps before and after reordering.
  - Report distributional shifts in gold-document positions, not just means. How often do methods actually move the gold doc to last place?
- Clarify implementation details that affect reproducibility:
  - Precisely define token spans S_i segmentation, how BOS/system tokens are handled in Equation (1), attention extraction interfaces used for each model, and exact EM matching protocol.
  - Discuss decoding choice: show whether temperature/sampling alters attention masses and final outcomes.
- Position the contribution more carefully:
  - Reframe conclusions to avoid generalization beyond the tested setting. Emphasize “on SynthWiki@28K with these two models” and identify hypotheses to test next.

Typos and minor issues:
- Page 1, footnote marker “¹” should be consistently spaced before the URL; consider formatting as a proper footnote reference.
- Page 2, “10× fewer tokens” is ambiguous; consider “uses one-tenth the number of tokens.”
- Page 6, references sometimes omit conference/venue formatting; standardize citation styles.

Criteria to raise score:
- Add at least one strong positional-mitigation baseline plus ablations of α/B/additive-vs-divisive and multi-token attention. Include a real-data RAG benchmark and significance testing. Provide latency measurements. If these are addressed convincingly and the core takeaway still holds, I would consider raising to Findings (3.0) or Borderline Conference (3.5) depending on results strength.

## Confidence
4: Quite sure after careful checking — I checked the important points, equations, figures, and tables; conclusions are limited by scope but the critique is unlikely to hinge on a missed detail.

## Soundness
3: Acceptable — Main claims are supported for the tested setup, but empirical scope is narrow, baselines are missing, and key ablations are absent.

## Excitement
2.5: Between potentially interesting and interesting — The negative result is useful, and the method is simple, but the evaluation breadth and comparative context are limited.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The study is cleanly executed, and the negative result is informative, but the scope is narrow, baselines are missing, and the analysis of the debiasing mechanism is shallow. With broader evaluation, stronger comparisons, and richer ablations, this could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper mentions limitations around the number of models and the single benchmark. Additional societal impact discussion is minimal. While the work does not introduce new datasets or sensitive data, position-bias interventions in deployed RAG systems may change which sources are surfaced or trusted; a brief discussion of potential failure modes, such as over-confidence when reordering fails or inadvertent de-prioritization of relevant but stylistically atypical documents, would be helpful. Consider also whether calibration might differentially affect content from certain domains or writing styles that receive systematically lower attention.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The paper provides essential setup details and a code link; however, several implementation specifics are not fully documented in the text, and more ablations would help.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: The described code appears likely to be useful for reproducing the experiments and as a baseline for future work, but the paper would benefit from more implementation detail and ablations to maximize utility.