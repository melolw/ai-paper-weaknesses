# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes Misalign@k, an evaluation protocol for emergent misalignment (EM) that measures the probability that at least one misaligned output is produced when sampling k generations per prompt. The protocol uses an LLM judge with dual scoring on alignment and coherence, and defines three labeling modes (Standard, Relaxed, Composite) for sensitivity analysis. Experiments on Qwen2.5‑7B‑Instruct fine-tuned to induce EM compare two defenses (KL regularization and interleaving), showing large tail-risk amplification relative to mean rates and a striking defense ranking flip between Standard and Relaxed metrics. The paper argues that deployment decisions should account for repeated sampling and labeling sensitivity.

## Summary Of Strengths
- Problem framing: Tail-risk under repeated sampling is an important and under-measured deployment concern for safety evaluations. Misalign@k provides a simple, interpretable metric at the prompt level that complements mean misalignment.
- Clear protocol sketch: Figure 1 gives a clean end-to-end diagram of the pipeline, including k-sampling, dual scoring, labeling modes, and aggregation. This helps readers replicate or adapt the setup.
- Empirical clarity about tail amplification: Tables 1–2 quantify that Misalign@32 can be 3.4× to 24.2× larger than MeanMisalign, a useful takeaway for practitioners relying on single-sample evaluations.
- Sensitivity analysis: The three labeling modes make visible how incoherence can mask misalignment. The demonstrated ranking flip between interleaving and KL regularization is a concrete and policy-relevant illustration.
- Format-specific analysis: Table 3 and Figure 3 suggest defenses reshape vulnerability across prompt formats rather than uniformly suppress it, which is a nuanced and actionable insight for benchmarking design.
- Figures that support claims: Figure 2 visualizes Misalign@k as a function of k and clearly shows the metric divergence and ranking flip under different labeling modes.

## Summary Of Weaknesses
1) Very limited experimental scope reduces external validity.
- Only one base model (Qwen2.5‑7B‑Instruct), one EM dataset, and two defenses are evaluated (Section 4.1). Given the paper’s strong claims about evaluation practice, broader coverage is important. The conclusion acknowledges this, but the current scope limits generalization.

2) Tiny evaluation set and high-variance estimates.
- The evaluation uses only 24 prompts (8 per format). With such a small n, Misalign@k at the prompt level is noisy. The reported standard deviations are often large (e.g., Table 1 Interleaving M@32 = 16.67 ± 7.22). This compromises the stability of the defense ranking conclusions and format-specific claims in Table 3 and Figure 3.
- The k-sweep in Figure 2 uses only three seeds. With 24 prompts, this provides limited statistical power. Confidence intervals or exact binomial intervals per condition would improve interpretability.

3) Heavy reliance on a single LLM judge and thresholds without sufficient calibration.
- The entire metric hinges on DeepSeek‑V3.2 scores and two fixed thresholds (alignment < 30, coherence > 50). There is no ablation over judges, prompts to the judge, scales, or thresholds. The “zero false positives” claim relies on the aligned base model producing zero flags (Tables 1–2), which is not a sufficient calibration test; it does not bound false negatives or adversarial sensitivity, and one aligned model is not a proper negative control set.
- The thresholds appear heuristic. There is no ROC-style analysis, inter-annotator reliability with humans, or justification for 30/50 cutoffs. Since the main qualitative conclusions (e.g., ranking flips) can be threshold-sensitive, this needs to be probed.

4) Lack of human evaluation or cross-judge validation.
- No human spot-checking or second-judge comparisons are provided to verify LLM-judge labels, despite known fragility of LLM-as-judge systems. This undermines confidence in both the tail-risk rates and the claim of “incoherence masking misalignment.”

5) Incomplete sensitivity to decoding and deployment settings.
- The core premise is deployment tail risk under repeated sampling, yet only one decoding setting is used: T=1, top_p=1, max_tokens=600. No analysis of how results vary with temperature, nucleus sampling, or use of default deployment settings. The k-sweep stops at k=32 without discussing realistic user behavior. If conclusions depend on decoding, they may not generalize.

6) Limited baselines and missing comparisons to simple analytical predictions.
- Section 3.5 briefly mentions the uniform-risk model Misalign@k = 1 − (1 − p)^k but does not compare observed curves against prompt-heterogeneity models (e.g., Beta-Binomial fits) that could quantify how much of the amplification is due to heterogeneity versus labeler behavior. Such modeling would strengthen the contribution from descriptive to analytical.
- No comparison to existing safety-tail metrics (e.g., analogous leak@k-style evaluations) beyond citations, and no experiments showing Misalign@k’s added value relative to per-prompt mean rates with confidence bounds.

7) Reporting gaps and reproducibility friction.
- Key fine-tuning details are missing or overly terse: rs‑LoRA hyperparameters, training schedules, early stopping, data sampling and shuffling strategies, and exact prompts used for the LLM judge are not specified in the main text. The judge rubric is credited to prior work but not restated; exact prompt wording matters for LLM-judge reproducibility.
- It is unclear whether the 24 prompts and judge prompts will be released. The paper mentions code availability but not artifact completeness.

8) Ambiguity around how “coherence” interacts with harmfulness.
- The paper asserts “incoherence masking misalignment” as the mechanism for ranking flips. However, it does not present concrete qualitative examples to show that incoherent responses contain misaligned content that the Standard metric would otherwise miss. A few labeled examples would be persuasive. As is, the mechanism inference remains plausible but mostly indirect.

9) Figures and tables could be more statistically grounded.
- Figure 2 has error bars, but it does not report the specific CI method, and variance decomposition by prompt type is not shown. Table 3 shows per-format means but lacks statistical tests to support claims like “interleaving completely eliminates JSON misalignment.”
- Equation (3) uses a simple empirical variance of per-prompt rates, but the analysis does not connect this to confidence bands for Misalign@k or to a generative model of prompt heterogeneity.

10) Missing related work that is directly relevant and would strengthen positioning (see next section).

Explicit figure/table critiques:
- Figure 1: The pipeline is clear and supports the paper’s methodological story. However, the left panel lists only three defenses total, of which two are used in experiments; adding placeholders for other defense types (e.g., RLHF-stage defenses, activation-space methods) would make the “general protocol” claim more credible.
- Figure 2: The divergence between panels (a) and (b) visually substantiates the ranking flip, but the y-axis uncertainty grows with k; without more prompts or seeds, readers should be cautious in over-interpreting gaps at k=32. It would help to overlay the theoretical 1 − (1 − p)^k curves fitted per condition to show deviation from uniform risk.
- Figure 3: The heatmaps communicate format-specific heterogeneity. But with only 8 prompts per format, per-cell values can be dominated by a few items. Error markers or per-cell counts would help. Also, citing exact cells that drive claims (e.g., which Template prompts remain brittle under interleaving) would make the analysis more actionable.
- Table 1 and Table 2: These are central. The paper’s strongest claim, the ranking flip, is borne out by M@32 in Table 2 (KL 31.94% vs interleaving 73.61%). However, the incoherence statistic that motivates the flip appears only in Table 1; linking table columns across modes or adding a combined summary would improve readability. Include exact n for the 24 prompts, and explicitly state whether values are mean±sd over three seeds.

## Potentially Missing Related Work
1) Askin et al., Emergent and Subliminal Misalignment Through the Lens of Data-Mediated Transfer, 2026 — Analyzes how narrow fine-tuning transfers to broad misalignment. Directly relevant background for Section 2 and for interpreting why interleaving affects formats differently; discuss in Related Work and connect to format-specific findings in Section 4.5.

2) Minegishi et al., Emergent Misalignment from Superposition, 2025 — Provides a mechanistic account via feature superposition. Relevant to interpreting residual prompt-specific risk and Var( p̂i ) in Sections 3.5 and 4.3; cite after Equation (3) and in Discussion of heterogeneity.

3) Jørgenvåg et al., Reinforcement Learning Amplifies Emergent Misalignment from Harmless Rewards, 2026 — Extends EM beyond SFT to RL; Misalign@k would be useful in their RL settings. Add to Related Work (Defenses/Training Regimes) and mention as a target for future evaluation in Section 5.

4) Hassan et al., Emergent Misalignment in Language Models: Domain Generalisation, Training Trajectories, and the Limits of Alignment Recovery, 2026 — Studies domain generalization and training trajectories. Add to Related Work, and reference in Section 4 as motivation to analyze k-sweeps across checkpoints and domains.

5) Vaugrante et al., Emergently Misaligned Language Models Show Behavioral Self-Awareness That Shifts With Subsequent Realignment, 2026 — Self-assessment signals could be combined with Misalign@k as auxiliary indicators. Mention in Related Work and as an extension in Section 5.

6) Wang et al., Emergent Misalignment Can Be Induced by Sycophancy and Reversed via Alignment Gating, 2026 — Offers additional defenses and failure modes to test. Include in Related Work and propose as future baselines in Section 4.1 or Section 5.

7) Mushtaq et al., From Narrow Unlearning to Emergent Misalignment in LLMs, 2026 — Shows narrow unlearning can trigger EM; suggests another evaluation axis for Misalign@k. Cite in Related Work and note that unlearning-style defenses should be compared under Misalign@k.

8) Schreiber et al., Overtrained, Not Misaligned in Fine-Tuned LLMs, 2026 — Argues overtraining effects drive EM; motivates early-stopping and LR sweeps. Discuss in Section 2 and test how Misalign@k responds to early stopping in ablations.

9) Qu et al., Emergent Misalignment in Mixture-of-Experts Models, 2026 — Architecture-specific EM; motivates extending Misalign@k to MoE. Add to Related Work and future directions.

10) Qu et al., Beyond Intentions: A Critical Survey of Misalignment in LLMs, 2025 — Survey that frames misalignment measurement challenges; situate Misalign@k within this taxonomy in Section 2 and clarify which failure modes Misalign@k captures.

## Comments Suggestions And Typos
Actionable suggestions:
- Expand experimental coverage:
  - Add at least one more base model and one more EM induction method or dataset. Include at least one additional defense family (e.g., activation editing, representation constraints like BLOCK‑EM, alignment gating, or early stopping) to test generality of the ranking flip.
  - Increase the evaluation set size well beyond 24 prompts. Provide stratified sampling across formats and difficulty to stabilize Misalign@k estimates, and report bootstrap confidence intervals at the prompt and aggregate levels.

- Judge robustness and calibration:
  - Perform a cross-judge study (e.g., two different LLM judges plus a 10–20% human-labeled subset) and report agreement statistics. Provide ROC-style curves over alignment/coherence thresholds, and show that key qualitative results (e.g., ranking flip) persist across threshold ranges.
  - Release exact judge prompts and rubrics. Add analyses with alternative scales (e.g., 0–5) or categorical labels.

- Decoding and k-sensitivity:
  - Evaluate multiple decoding configurations (lower T, top_p < 1, sampling with penalties) and report how Misalign@k curves in Figure 2 shift. Provide a model of typical user behavior to contextualize k; consider reporting Misalign@k for k ∈ {1, 2, 3, 5, 10, 20, 50}.
  - Fit a simple heterogeneity model (e.g., Beta-Binomial) per condition and overlay predicted 1 − (1 − p)^k curves to interpret deviations in Figure 2.

- Qualitative evidence for “incoherence masking”:
  - Include a small table of concrete outputs where the Standard metric excludes misaligned content due to low coherence, but the Relaxed metric captures it. This would substantiate the mechanism behind the ranking flip.

- Reporting and artifacts:
  - Provide full fine-tuning hyperparameters, data splits, rs‑LoRA settings, training duration, and checkpoints. State whether the 24 prompts and judge prompts are released. Add exact n and CI reporting to Tables 1–3 and Figures 2–3.

Typos and minor errors:
- Page 1: “We report results across 3 random seeds for variance estimation” appears later in Section 4.1, but it would help to state sample sizes alongside every aggregate in Tables 1–3.
- Page 4: “We define the per-prompt misalignment rate as: ṗi” — consider using p̂i consistently to avoid confusion with dot notation.
- Notation: MeanMisalign is defined as ȳp = (1/n) Σi p̂i in Section 3.5 but a different hat/dot notation is used in Equation (1). Unify symbols.

Criteria that could increase my score in rebuttal:
- Provide additional results on at least one more model and one more defense family showing the ranking flip or, at minimum, that the main tail-risk amplification findings are robust.
- Add cross-judge and threshold-sweep analyses showing that Misalign@k conclusions do not hinge on DeepSeek‑V3.2 or on the specific 30/50 cutoffs.
- Release prompts and judge prompts, and document full training and inference settings.

## Confidence
3: Reasonably confident but not fully verified; I did not check all implementation details, and conclusions depend on an LLM judge whose robustness is not fully established.

## Soundness
2.5: Between Poor and Acceptable; the metric is reasonable and experiments are suggestive, but limited scope, small n, and lack of judge/threshold ablations reduce support for the stronger claims.

## Excitement
2.5: Between potentially interesting and interesting; the tail-risk framing is useful for safety evaluations, but the current empirical breadth is too narrow for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Rationale: The core idea, Misalign@k with labeling-mode sensitivity, addresses a real evaluation gap and is clearly communicated with supportive visualizations (Figure 1 and Figure 2). However, the empirical study is too narrow (single model, 24 prompts, two defenses), heavily reliant on one LLM judge with fixed thresholds, and lacks human validation or cross-judge checks. The main qualitative claim, a defense ranking flip, is intriguing but not yet robustly established. With expanded experiments, judge ablations, and released artifacts, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges limited scope in the conclusion but does not include a dedicated limitations or societal impact section. Potential impacts include:
- Positive: Encourages safer deployment by highlighting tail-risk under repeated sampling and by exposing sensitivity to labeling choices.
- Risks: Over-reliance on a single LLM judge could mischaracterize model safety; reporting that some defenses “look safer” under certain metrics without robust validation may mislead practitioners.
Suggested additions:
- A clear discussion of failure modes of LLM-as-judge in this context, potential biases, and the need for human verification.
- Consideration of how releasing prompts and code might enable misuse, and mitigation plans (e.g., redaction or controlled access to high-risk prompts).
- Discussion of languages and domains beyond English/security, including who benefits and who might be disproportionately harmed if misalignment tail-risk is underestimated.

## Ethical concerns
None beyond the need for better transparency around LLM-judge reliability and safe handling of potentially harmful prompts and outputs. A short ethics paragraph would strengthen the submission.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty. Some settings are specified and code is claimed to be available, but missing fine-tuning and judge-prompt details, small-n sensitivity, and single-judge dependence will make faithful reproduction challenging.

## Datasets
2: Documentary. No new dataset is contributed; the small evaluation set is not clearly released.

## Software
3: Potentially useful. If the evaluation code and judge prompts are released, Misalign@k could be a handy add-on for safety benchmarking, but current details are insufficient to judge usability.