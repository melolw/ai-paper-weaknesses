# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies a failure mode of LLM safety judges under “benign-padding” attacks, where innocuous text is prepended and/or appended to unsafe content. The authors show that holistic judging can collapse under such padding (e.g., WildGuard’s FNR goes from 0.0455 to 1.0). They propose WindowScan-Judge (WSJ), a post-hoc wrapper that slides overlapping windows across the response at multiple scales and aggregates per-window decisions using a length-aware false-positive-rate control (LA-FPR). On JailbreakBench’s judge-comparison split (110 unsafe, 190 safe), WSJ greatly reduces FNR for padded cases while keeping FPR within a specified budget for most settings and generalizes to multiple base judges. The paper includes ablations on window size and aggregation.

## Summary Of Strengths
- Clear problem formulation and a simple, deployment-friendly defense. The paper isolates a realistic and practically important vulnerability of safety judges: dilution of the harmful signal by length and benign content.
- Strong headline effects for the target threat model. In Table 1, WSJ-WildGuard reduces FNR from 1.0 to 0.009 on the prepend+append attack, and improves F1 on both padded and original inputs.
- Black-box, post-hoc applicability. WSJ only requires query access to the base judge and no retraining, which is attractive for practitioners who want robustness with minimal integration cost.
- Explicit, interpretable mechanism and ablations. Figure 2 makes a compelling case that small windows (W=128/256) are decisive for recovering recall, and Table 2 compares aggregation strategies showing why conditional LA-FPR can be too conservative while marginal calibration with k=1 suffices here.
- Useful cross-model evidence. Improvements transfer to Llama Guard 3 (Table 1), suggesting the technique is not tailored to a single judge.
- The architecture-level overview in Figure 1 is easy to follow, showing where LA-FPR sits relative to window scoring and how decisions are composed across scales.

## Summary Of Weaknesses
1) Narrow evaluation scope and small testbed
- The study uses one dataset (JailbreakBench judge-comparison, 300 items), with a small calibration set (95 safe) and 110 unsafe for testing (Section 4.1). No additional datasets or multilingual scenarios are evaluated, despite claims of broad applicability. This raises concerns about overfitting to a single benchmark distribution and attack style. Confidence intervals or significance tests are missing, which is problematic given small sample sizes.
- The paper acknowledges this limitation in the Conclusion, but the main claims are framed strongly throughout without uncertainty quantification.

2) Threat model breadth and adaptive adversaries
- The attack space is limited to four padding patterns (Original, Append Long, Prepend+Append, Interleaved). Details on how benign padding was generated are insufficient for replication and for anticipating stronger adversaries. For instance, an adaptive attacker could split unsafe content into sub-window fragments shorter than the smallest W, paraphrase across window boundaries to evade local detectors, or pad with safety-looking content whose semantics dominate local windows. There is no experiment where the attacker targets the windowing defense explicitly.

3) Calibration methodology and FPR budgeting lack statistical grounding
- Equation (1) defines k via P(Cm ≥ k | safe) ≤ δ, but the paper relies on “marginal calibration” over all lengths from 95 safe examples and then reports that k=1 suffices globally (Section 3.3). There is no description of the estimator, its variance, or how it adapts when the number of windows m grows with much longer inputs than seen in calibration, which is exactly what padding encourages. A standard multiple comparisons control (e.g., Bonferroni/Šidák approximations or m-aware modeling) would be a natural baseline. Table 2 shows conditional LA-FPR becomes too conservative, but the paper does not present a principled alternative that balances per-m control with power.
- The FPR budget is defined ad hoc as δ = FPRholistic + 0.05 (Section 4.1), which can permit substantial FPR inflation when holistic FPR is already nontrivial. There is no exploration of other budgets or sensitivity analysis.

4) Incomplete reporting on computational overhead and deployment feasibility
- The paper states that the cost scales linearly with response length and is parallelizable (Section 3.4), but provides no latency or throughput numbers, judge-call counts per example, or a cost–accuracy trade-off. In practice, moderation systems are latency sensitive; without empirical cost curves, it is hard to assess deployability.

5) Missing baselines and alternatives to length-aware OR-aggregation
- The baselines in Table 2 are all variants around OR and thresholding. There is no comparison to simpler heuristics like “judge only the top-k TF-IDF-suspicious windows,” attention-based segment selection, or uncertainty-calibrated voting (e.g., score averaging with calibrated probabilities or p-values rather than hard labels). The authors could also compare to a single-pass length-debiased judge (e.g., normalizing scores by length) to isolate how much of the win comes from segmentation versus mere length compensation.

6) Limited analysis of failure cases and qualitative insights
- There is no qualitative error analysis of the unsafe cases still missed by WSJ (e.g., the few examples where FNR > 0), nor of the safe cases that become false positives under windowing (which increase noticeably in several cells in Table 1). Understanding the content types that flip under windowing would help practitioners decide when to adopt the method and which W to prefer.

7) Overreliance on a single windowing configuration
- Figure 2 highlights that W=128 is the winning configuration for the showcased attack. However, the paper fixes stride S=W/2 and does not explore smaller strides, dynamic W, or tokenization effects. No evidence is given that multi-scale fusion helps in distributions beyond what is tested, and Table 2 suggests no advantage over single-scale W=128 in the primary scenario.

8) Statistical reporting gaps
- Table 1 and Table 2 lack confidence intervals or statistical tests. With sample sizes as small as 95 safe and 110 unsafe, point estimates can be noisy. This is especially important when the paper emphasizes FNR improvements from 1.0 to 0.009, where even a few flips could meaningfully change conclusions.

9) Reproducibility details that should be explicit in the paper
- Although a link to code is included in a footnote, the paper itself does not describe benign-padding construction (sources and composition rules), tokenization libraries and settings, input length constraints, or prompt templates used to query each judge. Deterministic decoding is specified (temperature = 0), but other decoding or prompt-format details can materially affect judge behavior.

10) Discussion of societal/ethical trade-offs is thin
- Windowing increases FPR in many configurations (e.g., WildGuard Original FPR from .137 to .168 in Table 1, and other larger increases under padding scenarios). The paper should discuss the implications of increased overblocking for user groups, false positive harms in moderation contexts, and how to tune the method to different policy risk appetites. The Conclusion notes overhead, but not downstream harms.

Figure- and Table-specific comments:
- Figure 1: The pipeline clarifies how decisions are counted and thresholds applied across scales. However, the figure suggests length-aware calibration but the text later states k=1 suffices marginally for all scales; the figure would benefit from explicitly indicating that, in reported experiments, the decision effectively degenerates to a simple OR. This difference between the general design and the realized regime is important for reader expectations.
- Figure 2: The bar plot makes the central empirical point vivid: W=128 and 256 dramatically reduce FNR relative to holistic (1.0), while W≥512 fails. This supports the hypothesis that padding dilutes local signal and that fine-grained windows are necessary. It would help to annotate average harmful-span length and total-length distributions so readers can connect the threshold effect to concrete length ratios.
- Table 1: The main empirical claim rests here. WSJ-WildGuard restores F1 to ~0.924 in the hardest setting while substantially increasing FPR relative to the holistic padded baselines that were near-zero FPR because they labeled almost everything safe. A fairer comparison is against the holistic Original setting: WSJ raises FPR from .137 to .168 while reducing FNR from .045 to .018, showing a nontrivial precision–recall trade-off that should be discussed more explicitly.
- Table 2: The aggregation comparison is helpful, but the “Fixed-k Adaptive” and “LA-FPR Conditional” are not precisely defined in the text. For instance, how is “Fixed-k Adaptive” chosen and over what validation protocol? Clarifying this would make the ablation more informative.

## Potentially Missing Related Work
1) Zhou et al., “Toward Robust LLM-Based Judges: Taxonomic Bias Evaluation and Debiasing Optimization,” 2026 — Proposes a taxonomy and debiasing strategies for judge robustness. Directly relevant to length and position effects. Should be discussed in Section 2 and related to WSJ’s length-aware design; could also be used as an additional evaluation benchmark.
2) Almasoud et al., “Security in LLM-as-a-Judge: A Comprehensive SoK,” 2026 — Systematizes threats and defenses for LLM judges. This work would situate benign-padding within a broader taxonomy; cite in Section 2 and use to position WSJ’s contribution among other guardrail strategies.
3) Tan et al., “JudgeBench: A Benchmark for Evaluating LLM-based Judges,” 2025 — A judge-focused benchmark across tasks. Including this would broaden evaluation in Section 4 and help assess whether WSJ improves judgments beyond safety-only datasets.
4) Radharapu et al., “Calibrating LLM Judges: Linear Probes for Fast and Reliable Uncertainty Estimation,” 2025 — Uncertainty calibration for judges. Relevant to Section 3.3; discuss as an alternative to LA-FPR for controlling FPR/recall trade-offs and consider a baseline that aggregates calibrated probabilities rather than hard labels.
5) Feng et al., “Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges,” 2026 — Provides hypothesis-testing tools for noisy judges. Could inform more principled FPR control than the ad hoc δ and motivate statistical tests for Table 1/2; cite near Equation (1) and in Section 4.
6) Yang et al., “FairJudge: An Adaptive, Debiased, and Consistent LLM-as-a-Judge,” 2026 — Addresses non-semantic biases including length effects. Highly relevant to benign-padding dilution; compare in Section 2 and consider as a baseline or complementary technique.
7) Le et al., “Prompt Attack Detection with LLM-as-a-Judge and Mixture-of-Models,” 2026 — Deployment-oriented judge ensembles for attack detection under latency constraints. Useful for Section 4 to discuss how WSJ compares in cost–latency–accuracy trade-offs.
8) Hwang et al., “Can You Trick the Grader? Adversarial Persuasion of LLM Judges,” 2025 — Shows stylistic and rhetorical manipulation of judges. Complementary to benign-padding and could be tested with WSJ to see if local windowing reduces persuasion effects; discuss in Section 2 and consider in future work.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Expand evaluation beyond JailbreakBench. Include at least one more safety dataset (e.g., HarmBench’s evaluation split in a judge-setting, ShieldGemma evaluations, or other judge-specific suites) and, if possible, one multilingual dataset to validate generalization claims. Provide confidence intervals or bootstrap resampling for Table 1 and 2.
- Clarify calibration details. For Equation (1), report the estimator for P(Cm ≥ k | safe), how it accounts for varying m, and add a sensitivity analysis across δ values (e.g., δ ∈ {FPRholistic, FPRholistic+0.02, +0.05, +0.1}). Include a principled multiple-comparisons baseline (e.g., Bonferroni/Šidák) and compare empirically against marginal calibration.
- Describe benign padding generation precisely. Provide templates, sources for benign text, average length distributions, tokenization library, and how interleaving is constructed. Report the distribution of L and m across test conditions to connect with Figure 2’s threshold behavior.
- Report computational cost. Include average number of windows per example for each setting, end-to-end latency on a standard GPU/CPU, and throughput under parallelization. Compare W=128 vs multi-scale in both accuracy and cost to motivate a deployment recommendation.
- Add failure analysis. For unsafe examples still missed at W=128 and for safe examples flipped to unsafe, include qualitative cases and categorize errors (e.g., sarcasm, implicit harm, policy edge cases). This will ground the practical trade-offs.
- Strengthen aggregation baselines. Add a probability-calibrated voting baseline (e.g., judge likelihood of “unsafe” per window with a calibrated threshold), and a simple length-normalized holistic baseline to separate “segmentation” gains from “length-control” gains.
- Consider a simple adaptive attacker study. Allow an attacker to split the harmful content into fragments shorter than W or to spread harmful content across windows and measure the degradation; this will help bound WSJ’s robustness envelope.

Typos and minor issues:
- Section 4.3: “99.1% absolute FNR reduction” is phrased oddly. It is an absolute reduction of 0.991 or a 99.1 percentage-point reduction; consider clarifying the wording.
- Table 1 header repeats “Method” with a misaligned multi-column layout; consider improving readability (group columns by setting with clear multi-row headers).
- Section 4.5: “LA-FPR Conditional (per-window-count thresholds) is overly conservative” — briefly define how thresholds are chosen per m in the main text for completeness.

Criteria for updated score:
- If the authors add one more dataset, provide uncertainty quantification for Tables 1–2, include a principled m-aware FPR control comparison, and report cost–latency trade-offs, I would likely raise Soundness to 3.5–4 and Overall to 3.5 (borderline conference) or 4.0 (conference) depending on results.
- Demonstrating robustness against an adaptive padding attacker that targets W would further strengthen the case for main-track acceptance.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure about the assessment given the clarity of the method and reported numbers, but broader novelty and robustness could hinge on additional experiments and missing comparisons.

## Soundness
3 Acceptable: The approach is plausible and the empirical gains for the target attack are clear, but evaluation breadth, statistical reporting, and calibration methodology are not yet strong enough for a higher score.

## Excitement
3.0 Interesting: The problem is important and the fix is simple and practical, but the current evidence is narrow and missing stronger baselines and adaptive-attack testing.

## Overall Assessment
3 Findings: This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The contribution is practical and addresses a real failure mode with clear empirical wins in the showcased setting. However, the narrow evaluation, ad hoc calibration budget, lack of uncertainty reporting, and limited cost analysis prevent me from recommending main conference at this time.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly acknowledges limitations in scope and overhead. It should also explicitly discuss the societal trade-off of elevated FPR: overblocking may disproportionately affect certain user groups or legitimate content (e.g., sensitive health or legal discussions that contain locally “unsafe-looking” spans). Also consider the implications of deploying windowed scanning in multilingual or code-mixed contexts where tokenization and segmentation may amplify bias. Finally, discuss dual-use risks: publishing an effective countermeasure is good, but attackers can adapt by fragmenting harmful content to sub-window spans. Articulate mitigation strategies and monitoring plans.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The method is straightforward and the paper includes enough high-level detail, and code is claimed to be available. However, critical generation details for padding, tokenization specifics, and calibration implementation should be more explicit in the paper body.

## Datasets
1 No usable datasets submitted.

## Software
4 Useful.: The wrapper approach and code, if released as stated, would be practical for others to use and extend.