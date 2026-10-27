# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies LLM-as-a-judge in pairwise preference evaluation and focuses on the “self-reference” setting where a judge first solves the question and then uses its own answer as a reference while judging two candidate responses. The authors identify an error-propagation failure mode when the self-answer is wrong. They propose Selective Self-Reference (SSR-Judge): generate k self-solves, compute agreement (Equation 1), and enable self-reference only if agreement exceeds a threshold (Equation 2); otherwise judge without a reference. On a constructed MMLU-Pro setup with Qwen2.5-72B as judge, k=5, and a 4/5 threshold, SSR-Judge reports 58.93% accuracy, slightly above always-self-reference (58.21%) and higher than no-reference (52.07%). Analyses visualize slice behavior and the calibration of agreement as a correctness proxy.

## Summary Of Strengths
- Clear and focused problem framing around error propagation from incorrect self-answers in self-referenced judging.
- Simple, transparent method: agreement-based gating using Equations (1) and (2), which most readers can implement.
- Empirical evidence tying higher agreement to higher correctness, shown explicitly in Figure 3, provides an intuitive and useful calibration story for practitioners.
- The slice analysis in Figure 2 and Table 2 concretely demonstrates where selective self-reference helps versus hurts, showing that SSR-Judge tracks the stronger baseline per slice.
- Figure 1 effectively communicates the two-path pipeline, including the 4/5 decision gate and how samples are reused; this aids reproducibility and re-implementation.
- Quantitative comparisons in Table 1 show consistent improvements over the no-reference baseline and a modest improvement over always-self-reference, indicating that guarding against uncertainty can pay off.

## Summary Of Weaknesses
1) Construction of the pairwise evaluation task is artificial and may bias results. In Section 4.1, for each question the authors form two candidate responses by forcing one to end with the correct option and the other with a randomly sampled incorrect option. This setup likely simplifies the judge’s task relative to real model comparisons where both candidates can contain partially correct reasoning, stylistic differences, or subtle errors. It also conflates “preference” with “final-option correctness,” which can exaggerate the benefit of a reference that points directly to an option letter. This matters because the claimed improvements might not translate to realistic judge settings like MT-Bench-style responses or system outputs with similar quality.

2) Missing critical baseline families and ablations. The paper does not compare to alternative confidence-aware or selective judging methods (e.g., using verbalized confidence, log-prob thresholds, entropy over self-solves, or selective test-time adaptation). Without such comparisons, it is hard to attribute gains specifically to agreement gating versus any reasonable confidence heuristic. Additionally, the method lacks ablations over k, temperature, prompt formats, and domain-specific thresholds beyond narrative remarks in Section 4.5. These omissions limit the generality of conclusions.

3) Weakness in statistical rigor and reporting. Table 1’s headline improvements are small (58.93% vs. 58.21%), but the paper provides no statistical significance testing or confidence intervals for overall accuracy. Figure 3 includes 95% confidence intervals for correctness vs. agreement, but not for the primary outcomes in Table 1 nor for the slice accuracies in Table 2. Given the narrow margin over the strongest baseline, statistical uncertainty must be addressed.

4) Reproducibility gaps in experimental setup. Section 4.1 states a “separate generator model” is used to create the two candidates, but the model name, sampling parameters, and prompt templates are not specified in the main paper. The rules for extracting the final answer from judge self-solves (the answer(r_i) operator in Equation 1) are also unspecified, which can materially affect agreement rates. Since the paper’s main claim relies on self-consistency statistics, these missing details hinder faithful reproduction.

5) Potential leakage and bias from using the same model for self-solving and judging. The judge generates the reference and also makes the final decision. This design conflates solving ability with evaluation ability and may amplify self-preference or anchoring biases. While the paper mentions position bias control, it does not examine self-preference bias beyond the selective gate, nor does it try heterogeneous-judge configurations where a different model supplies the self-solves or reference.

6) Limited external validity beyond MMLU-Pro multiple-choice. The study is restricted to a single benchmark and a single judge model. Many LLM-as-a-judge use cases are open-ended generation (summarization, dialogue, reasoning chains). It is unclear whether agreement over answer options would translate to agreement over rationales, score distributions, or rubric-based assessments. The conclusion acknowledges this but the empirical scope remains narrow.

7) Gate metrics and interpretation could be clearer. In Table 1, Gate-On Rate and Gate Precision are reported for baselines that do not use a gate. While the intent is to characterize the underlying self-consistency process, readers may misread these numbers as method behavior. Moreover, the choice of τ=4/5 is motivated post hoc by Figure 3; a proper threshold sweep with ROC-like analysis would strengthen the claim that 4/5 is a principled choice for this setting.

8) Limited discussion of failure slices and mitigation. Table 2 shows the sizable “Unanimous + Wrong” slice (17.6%) where all methods that use self-reference suffer. This is the regime where error propagation is most damaging, yet the paper does not explore remedies, such as reference revision via step-level self-refinement, disagreement-aware re-sampling, or cross-checking with an auxiliary judge.

9) Incomplete related work positioning. The Related Work section omits several recent judge-centric methods that exploit self-consistency, uncertainty, or selective learning at evaluation time. This weakens claims about the uniqueness or necessity of the proposed gate and leaves open whether SSR-Judge is competitive against more sophisticated alternatives.

10) Figures and tables sometimes under-support global claims. While Figure 2 nicely illustrates per-slice behavior, the paper’s main takeaway hinges on small margins at the overall level (Table 1). Without significance analysis or sensitivity checks, the conclusion that SSR-Judge “outperforms” always-self-reference may not be robust. Also, Section 4.5 asserts per-category improvements, but no per-category table or figure is provided.

Explicit references to figures/tables/equations:
- Figure 1: The two-path diagram is clear and supports the method description in Section 3.4, but it would be helpful to annotate how answer(r_i) is parsed and how ties are broken when computing Agreement in Equation (1).
- Figure 2 and Table 2: These support the selective behavior claim by showing SSR-Judge matches the better of No-Reference and Always Self-Reference per slice. However, the Non-unanimous + Correct bar shows a large gap where SSR-Judge equals No-Reference (50.0%) while Always Self-Ref is 72.5%, which implies the 4/5 gate may be overly conservative in that slice; a sweep over τ should be provided.
- Figure 3: Shows monotonic calibration with only three agreement points (3/5, 4/5, 5/5). While suggestive, more granularity (e.g., with larger k) or cross-domain curves would give stronger evidence for general calibration. Confidence bands are shown here but not in the main accuracy tables.
- Equation (1) and Equation (2): The definitions are straightforward and central to the method, but there is no analysis of tie handling when multiple answers share the same frequency, nor of the sensitivity of Agreement to extraction errors.

## Potentially Missing Related Work
1) Zhou et al., “Self-Consistency of the Internal Reward Models Improves Self-Rewarding Language Models,” 2025 — Addresses consistency among judge-like reward models; directly relevant to using self-consistency as a confidence signal. Discuss in Section 2 and compare conceptually with Equations (1)–(2). Consider referencing near the calibration discussion in Section 4.4.

2) Jwa et al., “Becoming Experienced Judges: Selective Test-Time Learning for Evaluators,” 2025 — Proposes selective adaptation based on uncertainty during judging. Add to Section 2 and, if possible, include as a baseline or at least a discussion point in Section 4.2/4.3.

3) Calderon et al., “The Alternative Annotator Test for LLM-as-a-Judge,” 2025 — Formal framework for deciding when LLMs can replace humans. Cite in Section 2 and use its reliability framing to contextualize Table 1 claims; mention in Conclusion when discussing applicability.

4) Anonymous, “Beyond Single-Point Judgment: Distribution Alignment for LLM-as-a-Judge,” 2025 — Advocates aligning judge score distributions, relevant to gating by agreement. Discuss in Section 2 and relate to Figure 3’s calibration.

5) Xu et al., “J4R: Learning to Judge with Equivalent Initial State Group Relative Preference Optimization,” 2025 — Reasoning-focused judge training and robustness; should be compared in Section 2, and acknowledged as an alternative to test-time heuristics like SSR-Judge.

6) Arabzadeh et al., “A Human-AI Comparative Analysis of Prompt Sensitivity in LLM-Based Relevance Judgment,” 2025 — Highlights prompt brittleness; add to Section 2, and consider a prompt-sensitivity check for SSR-Judge in experiments.

7) Vasselli et al., “Measuring the Robustness of Reference-Free Dialogue Evaluation Systems,” 2025 — Probes robustness of LLM evaluators; discuss in Section 2 and consider as a lens for evaluating SSR-Judge’s robustness beyond MMLU-Pro.

8) Anonymous, “SSR: Socratic Self-Refine for Large Language Model Reasoning,” 2025 — Uses self-consistency for step-level refinement; relevant to mitigating the “Unanimous + Wrong” slice in Table 2. Mention in Section 4.3 as a possible extension.

9) Yuan et al., “Self-Rewarding Language Models,” 2024 — Closes the loop between generation and self-judgment; useful context for error propagation risks. Cite in Section 2 and discuss implications in Conclusion.

10) Zhou, “More Convincing, Not More Correct: Self-Play Reward Hacking of Reference-Free LLM Judges,” 2026 — Shows structural failure modes of judge-based supervision; relate to the motivation in Section 1 and discuss whether agreement gating would resist such reward hacking.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Please report significance testing or confidence intervals for overall accuracies in Table 1 and for slice results in Table 2. Given the small margin over Always Self-Reference, statistical support is essential.
- Provide full experimental details in the main paper: the generator model name and version used to create R1/R2, prompts for generation and judging, the exact parsing rules for answer(r_i), seed handling, and swap-aggregation policy. Also clarify tie-breaking for majority in Equation (1) when multiple answers are tied.
- Add an ablation over k (e.g., k=3,5,7) and temperature T to show stability of Figure 3’s calibration and the main result. A threshold sweep over τ with a precision-coverage curve will make the gate choice more principled.
- Evaluate on at least one open-ended evaluation setting (e.g., summarization or dialogue scoring) where the “final option letter” is not available. Show how to generalize agreement to rationales or scalar scores, and whether benefits persist.
- Include heterogeneous-judge experiments where the self-solves are produced by a different model than the judge. This will probe self-preference bias and test whether SSR-Judge’s gains hold when reference and judge are decoupled. Also consider ensemble or cross-check variants to reduce the “Unanimous + Wrong” risk highlighted in Table 2.
- Provide the per-category breakdown referenced in Section 4.5 as a table or figure, and discuss domain-specific thresholding with quantitative evidence rather than narrative claims alone.

Typos and minor issues:
- Table 2 header uses “Non-unan.”; spell out “Non-unanimous” for clarity.
- Section 4.1: “Model. We use Qwen2.5-72B-Instruct … as the judge model M_J” — notation capitalization varies (M_j vs. M_J) across Sections 3.1 and 4.1; standardize.
- Section 4.1 Hyperparameters: ensure consistent spacing for τ=4/5 and k=5 (some instances include extraneous spaces).
- Figure 1: consider annotating how answer extraction works and how ties are handled when computing Agreement from Equation (1).
- Reference formatting: a few entries lack consistent capitalization and diacritics; tidy for camera-ready.

Criteria that could raise my score:
- Add statistical tests with CIs showing the improvement over Always Self-Reference is reliable.
- Provide complete methodological details and ablations (k, T, τ sweep), plus at least one open-ended task evaluation.
- Include a strong alternative confidence baseline (e.g., entropy of self-solves, verbalized confidence, or selective test-time learning) and a heterogeneous-judge setup.

## Confidence
4: Quite sure after careful checking — I checked methods, figures, and tables closely; conclusions hinge on small improvements and limited scope.

## Soundness
2.5: Between Poor and Acceptable — The core idea is sensible and analyses are helpful, but the experimental design is narrow and key baselines, significance testing, and ablations are missing.

## Excitement
2.5: Between potentially interesting and interesting — Practical, easy-to-implement heuristic; modest gains and restricted scope temper enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The selective self-reference idea is simple and practically useful, and Figures 1–3 with Table 2 provide helpful intuition about when to apply self-reference. However, the main empirical margin over always-self-reference is small and unsupported by significance testing; the evaluation setup is artificial and narrow; and important baselines and ablations are absent. With a strengthened experimental section and broader validation, this could reach Findings or beyond.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly notes compute overhead and potential need for domain-specific thresholds, but it does not substantively discuss broader impacts of LLM-as-a-judge systems. Missing are considerations of bias amplification when the judge supplies and trusts its own references, domain shifts where agreement may be miscalibrated, and risks of deploying selective self-reference in high-stakes settings. A short section analyzing fairness across subject domains (beyond the brief narrative in Section 4.5) and discussing mitigation strategies for systematic judge errors would improve the work.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Core method is simple and Figures/Tables are clear, but missing generator model and prompt details, answer parsing rules, and threshold sweeps impede faithful reproduction.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — The method is simple to implement; the paper claims code availability, but core implementation details should be clearer in the text for full reproducibility.