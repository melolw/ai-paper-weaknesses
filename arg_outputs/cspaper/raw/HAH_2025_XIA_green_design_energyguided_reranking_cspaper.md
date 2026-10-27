# Preliminary Observations:
Primary scope mismatch: the work focuses on energy-guided reranking of LLM-generated source code for general programming tasks, not on natural language processing or language-centric evaluation. Apart from using a code LLM, there is no clear NLP task, dataset, or analysis. This is outside ACL’s core remit.

# Expected Review Outcome:

## Paper Summary
This paper proposes an energy-guided reranking pipeline for code generation. An LLM generates multiple Python program candidates per task; unit tests filter for correctness; then CodeCarbon is used to estimate per-candidate energy consumption, and the lowest-energy correct candidate is selected, with runtime as a tie-breaker. The study evaluates 10 algorithmic and data-processing tasks at three input scales on a single Apple M2 Ultra system. Results indicate average energy reductions of 44.69% versus the unguided Top-1 selection and 1.86% versus a Best-Time baseline, with negligible runtime penalties. Figure 1 outlines the pipeline; Figure 2 shows distributions of runtime penalties and energy savings; Table 1 provides experimental setup; Table 2 reports aggregate savings.

## Summary Of Strengths
- Clear problem framing and pipeline: The paper cleanly separates correctness checking from efficiency measurement and articulates a practical reranking procedure that developers could implement. Figure 1 is effective in conveying the end-to-end flow from candidate generation to reranking and baselines.
- Reproducibility-minded protocol: The environment is specified (Table 1), single-threaded configurations are enforced, and logs with source hashes are maintained. The authors state that all generated programs and scripts will be released.
- Empirical signals that speed != energy: The comparison with a Best-Time baseline is a useful test of whether minimizing runtime also minimizes energy. Table 2’s “Energy Savings vs Best-Time (%)” and Figure 2’s bottom panel together show that there is a nontrivial tail where energy-guided choices outperform the fastest implementations.
- Statistical reporting: The paper goes beyond point estimates and reports Wilcoxon signed-rank test results to claim significance over Top-1 and Best-Time.
- Actionable insight for tooling: The procedure is simple enough to integrate into code-assistant workflows, suggesting immediate practical impact for sustainable software efforts.

## Summary Of Weaknesses
1) Scope and venue fit: The contribution is squarely about general-purpose code generation and software energy profiling, with no NLP task, dataset, or language-focused analysis. Using a code LLM alone is not sufficient to make this an NLP paper.

2) Limited experimental breadth and external validity:
   - Only one model family and setting: The main experiments rely on Code Llama-Instruct (70B) candidates but provide no ablation across model sizes, families, or decoding strategies. Given the claim of generality, this is a narrow slice.
   - Single machine, single OS, one language: All measurements are from Python on one Apple Silicon system. Energy behavior can vary substantially across x86 vs ARM, Linux vs macOS, and Python vs other languages.
   - Only 10 tasks: The benchmark is modest and skews toward algorithmic kernels; it is unclear whether findings hold for larger, realistic applications or diverse libraries where I/O and cache behavior dominate.

3) Measurement fidelity and interpretation:
   - Reliance on CodeCarbon for millisecond-scale programs: With a 0.1 s sampling interval (Section 4.2) and many candidates likely finishing near that scale, quantization and attribution error can be substantial. The paper acknowledges model-based estimates but does not quantify minimal detectable effects or provide confidence intervals. This is especially problematic when Table 2’s median saving vs Best-Time is 0.00%.
   - No hardware validation: There is no RAPL, powermetrics, or external meter cross-check, even on a small subset. Without this, it is hard to know when reported differences reflect tool artifacts vs real effects.

4) Weakness in baselines and alternative explanations:
   - The “Best-Time” baseline is defined over the same set of generated candidates. There is no comparison to a carefully optimized human baseline or to standard library idioms known to be efficient. Energy savings may simply reflect discovering NumPy/vectorized paths occasionally, not a systematic advantage of the proposed reranker.
   - No accounting for amortization: The pipeline executes many candidates multiple times. The paper does not analyze whether the total energy cost of searching/reranking is outweighed by downstream savings, nor under what reuse horizon reranking becomes net-positive.

5) Missing key experimental details that affect replication and conclusions:
   - Decoding settings are not specified (exact temperature, top-p, number of samples per task). Candidate count N and its impact on improvement are not reported. There is no sensitivity analysis to N or sampling strategy.
   - Correctness tests only on small inputs: Some implementations might pass unit tests but fail or degrade at scale due to numerical issues or pathological cases. The paper notes unit + small randomized tests but does not quantify coverage or show post-measurement revalidation.

6) Statistical analysis under-specified:
   - The Wilcoxon tests are mentioned (p-values), but it is unclear what the paired samples are (per-task per-scale? per-candidate?), whether multiple-comparison corrections were applied, or what the effect sizes are. Given Table 2’s median 0.00% vs Best-Time, reporting effect size and confidence intervals is essential.

7) Figures and tables leave important questions unanswered:
   - Figure 2: The top panel’s clustering of runtime penalties at zero and the bottom panel’s long-tailed savings are informative, but the axes and bins are not discussed in the text, and there is no overlay of uncertainty. The figure supports the claim that many selections tie on runtime with occasional wins on energy, yet it also underscores how often gains are exactly zero, challenging the “consistently surfaces greener solutions” phrasing.
   - Table 2: Aggregate metrics are helpful, but averages can be dominated by a few tasks (e.g., 98% reduction in one matrix case). Per-task breakdowns, variance bars, and confidence intervals are needed to avoid overinterpreting the mean.

8) Overstated novelty/positioning relative to closely related contemporaneous work:
   - The paper claims a research gap where “no prior work directly integrates energy signals into the act of code generation itself.” Recent studies on energy-aware code generation, RL-based optimization for green code, and completion strategies with carbon accounting suggest otherwise. The Related Work section does not engage with these lines, making the novelty claim difficult to sustain.

9) Security and safety of executing untrusted code:
   - The paper states that candidates are executed in isolated processes, but there is no discussion of sandboxing, resource limits beyond timeouts, or filesystem/network isolation. This is a practical concern for real deployments and for reproducible artifacts.

10) Reusability and practical guidance:
   - The paper does not provide a guideline for when to prefer energy-guided reranking in practice, given the overhead cost and the frequent zero-gain cases relative to Best-Time. A cost-benefit model or heuristic would strengthen applicability.

Why these concerns matter: The measurement fidelity issues and limited scope undermine the strength of the generalized claims; the lack of sensitivity analyses and stronger baselines make it hard to tell whether the gains would persist across models, platforms, and realistic code; and the missing related work weakens the paper’s positioning and contribution statement. The venue mismatch compounds these issues for ACL specifically.

## Potentially Missing Related Work
1) Ilager et al., “GREEN-CODE: Optimizing Energy Efficiency in Large Language Models for Code Generation,” 2025 — Directly targets energy-efficient code generation using RL and analyzes energy–latency–accuracy trade-offs. Should be discussed in Section 2.2 and compared as an alternative to reranking; if feasible, include as a methodological baseline in Section 5.

2) Islam et al., “Evaluating the Energy-Efficiency of the Code Generated by LLMs,” 2025 — Large-scale measurement across many models and problems; offers per-model energy statistics. Discuss in Section 2.1/2.2 and use as external validation of claims about variability in LLM-generated code energy.

3) Ashraf et al., “Energy-Aware Code Generation with LLMs: Benchmarking Small vs. Large Language Models for Sustainable AI Programming,” 2025 — Compares small vs large models on correctness, runtime, memory, and energy. Add to Section 2.2 and consider a cross-model ablation in Section 5.

4) Rajput et al., “Beyond the Need for Speed: Energy-Aware Code Generation via Simulation-Guided Reinforcement Learning,” 2026 — Introduces simulation-in-the-loop optimization for energy-aware code generation. Compare methodological differences in Section 2.3 and discuss pros/cons vs CodeCarbon-based reranking in Section 6.

5) Nulle, “Reducing Carbon Emissions of Code Generation in Large Language Models with Line-level Completions,” 2025 — Studies completion granularity and carbon accounting on BigCodeBench. Discuss in Section 2.2 and consider as an additional baseline strategy (line-level vs function-level) in Section 5.

6) Masthan Ali et al., “Learn to Code Sustainably: An Empirical Study on LLM-based Green Code Generation,” 2024 — Presents metrics and empirical assessment of sustainable coding by LLMs. Incorporate in Section 2 for positioning and potentially adapt its metrics in Section 4.

7) Masthan Ali et al., “Sustainable Code Generation Using Large Language Models: A Systematic Literature Review,” 2026 — A survey that would anchor the paper within the broader landscape. Cite in Section 2 and use to refine claims of novelty and scope.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide full decoding details and sensitivity: Report temperature, top-p, number of candidates per task, and any sampling seeds. Add a curve of energy improvement vs number of candidates sampled to quantify diminishing returns and cost-benefit.
- Hardware validation and uncertainty: For a subset of tasks, validate CodeCarbon readings against a hardware-based tool (e.g., powermetrics on macOS or RAPL on x86) and report confidence intervals. Define minimal detectable effect (MDE) given sampling resolution and variance; avoid decisions on differences below MDE.
- Stronger baselines and per-task analysis: Include optimized human baselines or standard-library idioms; provide per-task tables with effect sizes and CI, not only aggregate Table 2. An ablation where you disable NumPy would help separate algorithmic vs library-driven gains.
- Amortization analysis: Quantify the total energy spent on reranking (including 5 repeats per candidate at multiple scales) and estimate breakeven points for realistic reuse scenarios.
- Safety and sandboxing: Describe process isolation in detail (no-network, tmpfs-only, CPU/memory caps, file system sandbox) and add safeguards in the artifact.
- Clarify statistics: Specify the pairing scheme for Wilcoxon tests, sample sizes, multiple-comparison handling, and report effect sizes (e.g., rank-biserial correlation). Provide per-task p-values with correction or, better, report CIs and avoid dichotomous significance framing.
- Presentation and claims: Temper phrasing like “first conclusive evidence” and “consistently surfaces” in light of Table 2’s median 0.00% vs Best-Time and existing related work. Frame contributions as demonstrating feasibility and identifying conditions where energy-guided reranking is beneficial.

Figure- and table-specific comments:
- Figure 1: The pipeline diagram is helpful, but it abstracts away two critical levers: number of candidates N and measurement repetitions R. Consider annotating these, since they drive both energy overhead and gains.
- Figure 2: The top panel (runtime penalties) clustering at zero supports the “no runtime cost” claim; the bottom panel’s long right tail shows that some tasks benefit materially. Please add confidence intervals or bootstrap whiskers and mark the zero bin frequency to make the prevalence of ties explicit.
- Table 1: Good coverage of environment details; add exact CodeCarbon configuration (geography, carbon intensity source, process tracking mode flags).
- Table 2: Add the number of tasks contributing to each statistic, and accompany averages with standard deviation or robust dispersion (IQR). A per-task table in the main text, even if compact, would substantiate aggregate claims.

Typos and formatting:
- Page 10 references [11]–[26] are compacted into one paragraph with inconsistent punctuation and spacing; split into standard reference formatting.
- Minor: “anonymized GitHub repository referenced earlier” is followed by a concrete URL (Section 4.3). For double-blind review, ensure anonymity policies are followed.

Criteria that could raise my score:
- Add cross-hardware and cross-model experiments, with validated energy readings on at least one alternative measurement tool.
- Provide full decoding/sampling details, sensitivity analyses, and a rigorous amortization study.
- Include and discuss the missing related work listed above and recalibrate novelty claims accordingly.
- Release a hardened sandbox and document security constraints.

## Confidence
4: Quite sure after careful checking — I checked the main methodological and empirical claims and the figures/tables carefully; some external factors (e.g., unreported decoding details) limit complete verification.

## Soundness
3: Acceptable — The study supports its core claim that reranking by measured energy can sometimes beat Top-1 and even Best-Time, but limitations in measurement fidelity, baselines, scope, and statistical analysis require substantial strengthening.

## Excitement
2.5: Between potentially interesting and interesting — Practical, potentially useful for green software communities, but limited breadth and venue misfit dampen excitement for ACL.

## Overall Assessment
2.5 Borderline Findings — The paper may meet minimal standards but requires improvements before being accepted to Findings. The methodology is clear and potentially useful, with some positive empirical signals, but measurement fidelity, missing baselines/ablations, incomplete statistical reporting, and a significant venue scope mismatch make it unsuitable for the ACL main track in its current form. With broadened experiments, stronger validation, and revised positioning, it could be appropriate for a findings-style publication or a software engineering venue.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges several limitations: model-based energy estimates, single-machine study, Python-only tasks, and lightweight correctness checks. Additional points to discuss:
- Risk of over-optimizing for energy at the expense of readability and maintainability; consider including code complexity metrics or human ratings.
- Rebound effects: adopted in Discussion, but a quantitative framing would help.
- Safety of executing untrusted generated code: expand on sandboxing and mitigations.
- Carbon accounting of the search itself: incorporate in limitations and results to avoid overstating net gains.

## Ethical concerns
- None related to human subjects or sensitive data.
- Practical ethics: executing untrusted code warrants stronger sandboxing discussion. Also ensure authorship and credit policies of target venues are followed.
- Otherwise, none.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible — Environment details and logging are solid, and artifacts are promised, but missing decoding parameters and sensitivity analyses limit exact replication.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful — The pipeline and scripts, if released with proper sandboxing and instructions, would be useful to practitioners, but the lack of cross-hardware validation and missing sensitivity analyses limit immediate adoption.