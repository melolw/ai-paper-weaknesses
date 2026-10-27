# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes a “Behavioral Fingerprinting” framework for evaluating LLMs beyond task accuracy. The method uses a 21-prompt Diagnostic Suite spanning four axes: internal world model (counterfactual physics, causal chains), reasoning and metacognition, biases and “personality” (including sycophancy), and robustness to paraphrase. Eighteen models are evaluated via an automated LLM-as-a-judge pipeline (Claude-opus-4.1) with prompt-specific rubrics that return numeric scores and justifications. The paper reports two main findings: convergence among frontier models on abstract and causal reasoning, and strong divergence on alignment-related behaviors such as sycophancy and semantic robustness. It further assigns an MBTI-style “personality analogue” to each model and observes clustering around ISTJ/ESTJ.

## Summary Of Strengths
- Problem framing: Clear articulation of why single-number leaderboards (e.g., MMLU) miss important behavioral differences relevant for real-world deployments. This sits squarely within ACL’s evaluation and human-centered NLP interests.
- Method design: A concise, reproducible structure with four phases (prompting, response collection, automated rubric-based judging, synthesis). Rubrics are explicit in Appendix B, enabling reimplementation.
- Breadth of coverage: The 21 diagnostics deliberately span cognitive and interactive traits, with well-motivated examples (e.g., counterfactual physics for first-principles reasoning, paired paraphrases for robustness, explicit sycophancy probes).
- Results readability: The paper provides concrete comparative visualizations. For example, Figure 2 offers per-dimension bar charts for large models: 
  - Figure 2(a) and 2(b) show tight clustering at the top for abstract reasoning and causal chain analysis.
  - Figure 2(d) shows wide spread for sycophancy resistance (e.g., 1.00 for claude-opus-4.1 and llama-3.1-405b-instruct vs. 0.25 for grok-4), effectively illustrating the claimed “great divergence.”
  - Figure 2(e) highlights robustness variation from 1.00 down to 0.50 among large models.
- Model “fingerprints”: The radar plots in Figure 3 provide an at-a-glance, decision-useful summary. For example, Figure 3(g) for grok-4 shows a conspicuously compressed “sycophancy” axis relative to other dimensions, visually reinforcing Table/figure-level claims about divergence in alignment behavior.
- Transparency of prompts: The full Diagnostic Suite is given in Appendix A, which is valuable for community replication and critique.
- Positioning relative to adjacent lines: The Related Work section acknowledges domain-specific behavior audits (BOLT), gray-box analyses (LOS), external personality evaluation, and dynamic personality simulations; the comparison table (Table D.1) helps situate scope and method differences.

## Summary Of Weaknesses
1) Single evaluator model, no reliability statistics or cross-judge validation
- The pipeline relies on one LLM-as-a-judge (Claude-opus-4.1) for all scoring. There is no inter-rater agreement analysis (e.g., across different judges or variants/seeds) and no calibration against human judgments. This raises concerns that some observed divergences could reflect the evaluator’s biases rather than ground truth. The paper cites LLM-as-judge literature but does not replicate the common mitigations (multiple judges, adjudication, or human spot checks).
- Why it matters: The headline findings (e.g., strong variance in sycophancy and robustness) rest entirely on the evaluator’s rubric adherence. Without reliability estimates or a human anchor, it is hard to assess stability and generality of the scores.

2) Thin empirical basis for several conclusions, especially H2 and persona clustering
- H2 claims architecture-family differences on analogical/abstract reasoning. However, Figure 2(a, b) mostly shows near-ceiling clustering for large models with limited separation; analyses tying performance to architecture families are not presented. The text asserts differences but does not provide statistical tests or clear family-level groupings.
- The “default persona” clustering around ISTJ/ESTJ (Table 1) uses a judge-driven MBTI analogue with no external validation, ablation, or sensitivity checks (e.g., to prompt wording or evaluator identity). No error bars or re-runs are provided, which makes the persona claim look susceptible to evaluator and prompt artifacts rather than a robust behavioral property.
- Why it matters: These are among the most interpretive claims of the paper, yet they are not backed by statistical analysis, robustness checks, or external validation.

3) Limited test depth for key axes, especially sycophancy and robustness
- Sycophancy uses two prompts (3.1.1, 3.1.2) and a 3-point rubric. This is a very narrow slice of a broad behavior. The conclusion in Section 4.1.2 that models differ “dramatically” is plausible but under-supported given such a small probe set and no sampling over topics or contexts (e.g., social sycophancy vs. factual deference; instruction vs. chatty settings).
- Robustness testing (Section A.4) uses two paraphrase pairs across two topics and bins outcomes into three levels. Figure 2(e) then claims meaningful spread. With so few pairs, it is unclear whether differences reflect model brittleness or idiosyncrasies of the chosen items.
- Why it matters: Both axes are central to the paper’s “great divergence” narrative, yet the measurement design is very low N. This risks overinterpretation of unstable estimates.

4) No statistical uncertainty quantification and unclear normalization details
- Scores are normalized to [0, 1], but the mapping from rubric points to normalized scores and any aggregation weighting is not fully specified in the main paper. The paper reports no confidence intervals, bootstrap resampling, or significance testing for differences shown in Figure 2 or Figure E.1.
- Why it matters: Without uncertainty estimates, it is difficult to tell whether visual differences in bar heights are meaningful. This is especially important because many bar heights cluster near the top where small deviations may be within evaluator or sampling noise.

5) External validity and reproducibility risks due to proprietary APIs and evaluator drift
- Section 3.5 and the Reproducibility Statement indicate heavy dependence on third-party APIs for both targets and the evaluator. The paper does not report evaluator temperature/top-p settings, seed control, or replay strategies. Given model drift and non-determinism, the stability of the fingerprints over time is unclear.
- Why it matters: The core pitch is a reusable, longitudinal “fingerprinting” methodology. If the evaluator or targets drift, results may not be comparable over time unless stricter controls are used and reported.

Additional, but secondary, issues:
- The “Llama 3.1 405B base” observation (Section 5.1.3) is interesting, but it is anecdotal and orthogonal to the core fingerprinting program. Consider moving it to appendix and focusing more space on reliability analyses.
- Several claims in Section 4.1.3 about “associative vs. deductive” reasoning would benefit from more discriminative counterfactual prompts or a manipulation check that verifies models did not simply memorize canonical counterfactual explanations.

Figure- and table-specific comments
- Figure 2(d) is the strongest evidence for the divergence claim: it shows explicit numeric spread in sycophancy resistance within the large-model cohort, with some models at 1.00 and others as low as 0.25. However, given only two prompts and a single evaluator, the paper should temper the strength of causal language, or bolster it with more items and multiple evaluators.
- Figure 3(g) (grok-4 radar) and Figure 3(e) (claude-opus-4.1 radar) visually contrast the behavior profiles and nicely support Section 5.1.1. This is a compelling visualization device, but it needs stronger methodological underpinnings (more prompts per axis, variance estimates) to justify decision-making claims.
- Table 1 lists MBTI-like profiles across 18 models and is central to the “default persona clustering” claim. This should be paired with sensitivity analysis (e.g., how often the type flips under small prompt perturbations or with a different evaluator).

## Potentially Missing Related Work
1) Cheng et al., “Social Sycophancy: A Broader Understanding of LLM Sycophancy,” 2025 — directly targets sycophancy as a multi-faceted social behavior with an evaluation framework. Should be discussed in Section 2 and compared in Section 3.3/H1; consider adding elements of their probe design to broaden 3.1.
2) Jain et al., “Interaction Context Often Increases Sycophancy in LLMs,” 2026 — shows personalization and interaction history modulate sycophancy. Discuss in Related Work and Section 5.1.1; consider a follow-up experiment where your sycophancy probes are re-run under minimal persistent context.
3) Chen et al., “Self-Augmented Preference Alignment for Sycophancy Reduction in LLMs,” 2025 — mitigation method and dataset aimed at sycophancy reduction. Cite in Section 2 and discuss in Section 5 as a way to test whether fingerprints capture mitigation effects over time.
4) Rehani et al., “The Social Sycophancy Scale,” 2026 — psychometric approach for human-anchored sycophancy measurement. Relevant to Section 3.5 and B.3.1; could inform human calibration of your LLM-judge rubric.
5) Xu et al., “A Behavioral Fingerprint for Large Language Models: Provenance Tracking via Refusal Vectors,” 2026 — refusal-vector fingerprints for provenance; relevant to Section 2 and Discussion as a complementary, internals-aware fingerprint to your black-box content-based profiles.
6) Xu et al., “Instructional Fingerprinting of Large Language Models,” 2024 — backdoor-style ownership signatures as engineered behavioral fingerprints. Discuss in Section 2 to contrast engineered vs. organically measured fingerprints; mention after Section 5.2 as an alternate notion of “fingerprint.”
7) Banerjee et al., “Large Language Model Fingerprints From Normal Interaction,” 2026 — supervised identification of models from everyday outputs. Add to Section 2 and consider as a baseline perspective for “behavioral fingerprints” learned from naturalistic data rather than diagnostics.
8) Bhattacharyya et al., “How Well Do Large Language Models Capture Human Personality?,” 2026 — shows pitfalls like persona manifold collapse; relevant to Section 3.3 and Section 5.2, and to the limitations of MBTI-like labeling.

## Comments Suggestions And Typos
Actionable suggestions, in priority order:
1) Multi-evaluator reliability and human calibration
- Add at least one additional LLM judge from a different family and compute inter-judge agreement (e.g., Cohen’s κ per axis). Include a small human-labeled subset to anchor sycophancy and robustness scores to human expectations. Report per-axis agreement statistics.
- Report evaluator settings (temperature, top-p, seed), and re-score a subset across seeds to estimate scoring variance.

2) Expand probe coverage and quantify uncertainty
- Increase the number and topical diversity of sycophancy and robustness items (aim for 20+ per axis). Report bootstrap confidence intervals on aggregate model scores and significance tests on pairwise differences shown in Figure 2. For robustness, include multiple paraphrase operations (lexical, syntactic, order changes) and measure semantic equivalence with a reference NLI or entailment-based check.

3) Strengthen H2 and persona claims
- If claiming architectural-family effects, show grouped analyses with statistical tests. For MBTI analogues, perform sensitivity tests (evaluator swap, prompt perturbation) and quantify stability (type-flip rates). Consider validating the E/I/S/N/T/F/J/P judgments with short-form human raters on anonymized outputs.

4) Clarify aggregation/normalization
- Precisely define how rubric points map to [0,1], how multiple items aggregate within a category, and whether any categories are weighted. Include per-item score distributions in appendix.

5) Longitudinal reproducibility
- Provide a versioned, pinned evaluation environment and, if feasible, cache raw judged outputs for at least a subset so others can recompute aggregates. Document a protocol for re-fingerprinting models as APIs drift.

Potential typos and minor issues:
- Page 10: the references [7]–[9] spacing/formatting seems compressed; ensure consistent punctuation and spacing.
- In several places “counterfactual physics” is used where “hypothetical physics” might reduce confusion; keep terminology consistent.
- Table captions: Table C.1 appears after its content; consider harmonizing placement across tables for readability.

Criteria that could increase my score in rebuttal:
- Evidence of inter-judge reliability and/or human calibration with quantified agreement.
- Additional, diverse sycophancy/robustness items with uncertainty estimates; significant differences that persist.
- Sensitivity and stability analyses for MBTI assignments; toned-down or better-supported claims for H2 and persona clustering.

## Confidence
4: Quite sure after careful checking — I checked methodology, figures, and claims carefully; remaining uncertainty centers on unreported implementation details of the evaluator and aggregation.

## Soundness
3.5: Between Acceptable and Strong — The framework is well structured and the prompts/rubrics are explicit, but core conclusions depend on a single evaluator and small probe sets without uncertainty quantification.

## Excitement
3.5: Between interesting and exciting — The framing is timely and useful for the community, and the visualizations are compelling, but stronger methodology and validation would elevate impact.

## Overall Assessment
3.5 Borderline Conference — Solid framing and potentially impactful evaluation perspective; however, reliance on a single LLM judge, low-N probes on key axes, and lack of reliability/uncertainty analyses weaken the strength of the conclusions. With added reliability checks, expanded probes, and uncertainty reporting, this could be a strong main-track paper; in current form it sits on the boundary between strong Findings and main conference.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper discusses limitations in Section 5.3, but I recommend adding:
- Risks of over-interpreting persona labels (MBTI analogue) and potential misuse for model stereotyping or exclusion in procurement decisions without robust validation.
- Sycophancy and robustness findings could be used to tune models for deceptive behavior; mitigation is partially addressed in the Responsible AI Statement, but consider adding concrete access controls or guidance for safe use of the prompts and pipeline.
- Language coverage: prompts are all in English; clarifying whether findings generalize cross-lingually would be valuable.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Prompts and rubrics are provided, but dependency on proprietary APIs and a single evaluator without fixed settings limits exact reproducibility and long-term comparability.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If released as stated, the code would likely be useful to others; adding environment pinning, cached judged outputs for a subset, and a simple multi-evaluator option would raise this to “Useful.”