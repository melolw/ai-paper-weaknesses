# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes KL-Time Replay, a replay-scheduling mechanism for continual learning in LLMs that measures function-space drift instead of parameter-space drift. Concretely, at the start of each task it snapshots the model as θ_ref and builds a fixed anchor set from previously learned tasks’ memory. During training, it computes a label-space forward KL divergence between q_θt(·|x) and q_θref(·|x) over the anchors (Equation 2) and accumulates drift. Replay is triggered whenever cumulative drift passes thresholds derived from an Ebbinghaus-style schedule, scaled to match a target compute budget. On a 5-task text classification sequence, KL-Time attains Overall Performance (OP) comparable to the FOREVER parameter-norm–based scheduler while showing different trigger patterns, particularly around task boundaries. An ablation suggests that monitoring drift on current-task examples may reduce replay frequency with similar or slightly better accuracy.

## Summary Of Strengths
- Clear conceptual motivation: the paper argues that catastrophic forgetting is fundamentally behavioral, so monitoring changes in output distributions is a direct signal for scheduling replay. The transition from parameter norms (τ) to function-space drift (KL) is well-articulated in Sections 3.2–3.5.
- Simple, implementable method: Equation (2) defines a compact metric using task label distributions rather than full-vocabulary KL, making the approach practical for classification tasks.
- Useful diagnostic analysis: Figure 2 shows high within-task correlation (>0.97) between KL drift and parameter update norms, but only moderate correlation over full trajectories. This supports the core claim that signals diverge at task boundaries, explaining why schedules differ.
- Competitive empirical results: In Table 1, KL-Time reaches OP 0.704 vs 0.708 for FOREVER with similar BWT and replay compute, suggesting function-space drift is a viable alternative scheduler.
- Insightful ablation: Table 2 indicates current-task anchors reduce replay events by 37% and slightly improve OP (0.713), a nontrivial and actionable observation for practitioners.
- Figure-ground clarity: Figure 1 concisely diagrams the pipeline from continual training to function-space monitoring and Ebbinghaus-triggered replay, aiding reproducibility.

## Summary Of Weaknesses
1) Limited scope and scale of evaluation
- Only a single 5-task, small-sample (1k/train per task, 2% memory) classification benchmark is considered (Section 4.1), all with similar short-form text. This is a narrow slice of LLM continual learning. No experiments on generative tasks, instruction-following, or multilingual settings, which are central to LLM CL today.
- Using a 0.6B model with PEFT is reasonable for cost, but the paper does not examine whether conclusions hold for larger models or different base families.

2) Drift definition and calibration details are under-specified or potentially brittle
- Equation (1) turns labels into verbalized strings and computes q_θ via log p_θ(verbalize(y) | prompt(x)). The paper does not specify:
  - How multi-token labels are scored (sum of token log-probs? prefix handling? special tokens?).
  - How ties, ambiguity, or sensitive tokenization effects are addressed.
  - Whether calibration or temperature scaling is used to stabilize KL estimates across tasks.
- Section 3.5 sets D_day at S=24 steps and applies human-day multipliers. The choice of S and its sensitivity are not justified. If replay timing critically depends on D_day, lack of sensitivity analysis leaves robustness unclear.

3) Asymmetry and task-dependence of the KL choice
- The method uses forward KL KL(q_θt || q_θref) (Equation 2). This can behave very differently from reverse KL when support shifts or when θ_ref assigns near-zero probabilities. The paper does not justify forward vs reverse KL, Jensen-Shannon, or other distances, nor analyze stability when q_θref(y|x) is small. This matters for robustness and may bias trigger frequencies.

4) Compute and overhead are not sufficiently quantified
- Section 4.2 states compute parity is maintained within ±10% by scaling ρ, but the paper does not report the cost of drift computation per step, the cadence of D_t evaluation, or its share of total runtime. With an anchor size up to 256 and per-step divergence computation, overhead can matter in larger settings. Without explicit profiling, the claim of “compute parity” is incomplete.

5) The “compute-matched by construction” comparison undermines the main claim
- Section 3.5 scales thresholds by a factor ρ “to match total replay compute within ±10%.” This makes scheduling policies partially tuned to produce similar budgets rather than independently driven by their signals. The ablation in Table 2 shows policies can vary in replay count substantially under comparable performance; forcing parity between FOREVER and KL-Time makes it harder to assess the intrinsic efficiency gains or losses of the drift signal.

6) Missing or weak baselines for scheduling
- Beyond fixed-step VBM and FOREVER, no comparisons to simple function-space or loss-based triggers (e.g., moving-average validation loss spikes, current-task loss variance), or to learned policies as in Klasson et al. (2022). Since the contribution is about scheduling, breadth of scheduling baselines is important for significance.

7) Inconsistencies and clarity gaps in the analysis
- Figure 2’s caption claims “across all four tasks,” but the benchmark is 5 tasks (Section 4.1). It is unclear why only four appear in panel (a) and what is omitted.
- Figure 3’s “Phase-0 gate” and “trigger divergence” require a precise definition. How is divergence computed, over which windows, and why focus on the first 2,500 steps? The 10% threshold is stated as “required,” but by what criterion? The statistical test or justification is not given.

8) Generality is constrained by classification-only KL
- The label-space KL avoids full-vocab costs, but it restricts the approach to tasks with closed label sets. The paper does not discuss how to extend KL-Time to generation, open-ended QA, or instruction tuning, which are central to LLM CL. This limits impact beyond small classification streams.

9) Reproducibility details are thin in the main text
- Several design choices are fixed but not fully justified: LoRA rank and placement, replay epochs, memory sampling policy, anchor selection determinism, and exact prompting/verbalization templates for each dataset. While Section 4.1 lists some hyperparameters, reproducing Equation (1) faithfully for all datasets would require more specific templates and tokenization handling.

10) Interpretation tension between main method and ablation
- The core story motivates monitoring past-task behavior, yet Table 2 shows current-task anchors yield fewer replays and slightly better performance. This result deserves deeper analysis, including trigger timelines and drift curves, and discussion about whether the primary actionable recommendation is actually to monitor current-task drift.

Figure- and table-specific comments:
- Figure 1: The diagram is helpful but omits details about how often D_t is computed, how cumulative drift is reset after a replay event, and whether θ_ref is ever updated mid-task.
- Figure 2(a,b): These support the “agreement within tasks, divergence across tasks” narrative. However, without specifying the segmentation of tasks and controlling for anchor composition, it is hard to know whether boundary effects stem from anchor distributional changes or the metric itself.
- Figure 3: Bars show “trigger divergence” across runs with a blue threshold at 10%, but the operational definition is missing. Without this, it is hard to judge whether 14.24% is practically meaningful in terms of downstream accuracy or forgetting.
- Table 1: Shows OP differences within 0.004 between KL-Time and FOREVER, within one standard deviation. It would help to include per-task accuracies to see whether drift-based scheduling helps some tasks more than others, and to report the variance of replay events for VBM for fairness.
- Table 2: The ablation is compelling but raises the concern that current-task anchors undermine the stated motivation of monitoring past-task behavior. An additional column with compute time and trigger counts over steps would clarify practical differences.

## Potentially Missing Related Work
1) Abbes et al., “Revisiting Replay and Gradient Alignment for Continual Pre-Training of Large Language Models,” 2025 — Large-scale study of replay for LLMs with gradient alignment; directly relevant as a strong baseline and for analyzing replay trade-offs. Discuss in Related Work (Section 2) and compare policies in Experiments (Section 4), ideally adding it as a baseline or at least contextualizing replay rates and stability.
2) Wang et al., “Learning Dynamics in Continual Pre-Training for Large Language Models,” 2025 — Provides scaling laws for replay ratio and learning dynamics. Relevant for calibrating ρ and interpreting compute/replay trade-offs. Cite in Section 3.5 when motivating threshold scaling and in Section 4.2 when analyzing compute parity.
3) Zheng et al., “Cross-Lingual Continual Pre-Training at Scale,” 2024 — Shows replay mixing ratios in multilingual scenarios. Include in Related Work (Section 2) and discuss as an evaluation target for future work; evaluate KL-Time under cross-lingual shifts where function-space drift may behave differently.
4) Borhanifard et al., “Combining replay and LoRA for continual learning in natural language understanding,” 2025 — ERI-LoRA combines replay with PEFT for NLU; highly relevant due to the same PEFT+replay design space. Add in Section 2 and consider as a baseline on similar text-classification sequences.
5) Lu et al., “MSSR: Memory-Aware Adaptive Replay for Continual LLM Fine-Tuning,” 2026 — Adaptive, Ebbinghaus-inspired scheduler driven by memory states rather than parameter norms or KL; very close in spirit to this work. Compare conceptually in Section 2 and, if possible, experimentally in Section 4.
6) Nitzan Hidekel et al., “Catastrophic Forgetting is Low-Rank: A Function-Space Theory for Continual Adaptation,” 2026 — Theoretical support for function-space monitoring, indicating forgetting concentrates in low-dimensional prediction subspaces. Cite in Section 2 and connect to Section 3.4 as motivation for function-space drift metrics.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Provide exact prompting and label verbalization templates for each dataset, including tokenization details and how multi-token labels are scored in Equation (1). Clarify whether temperatures or calibration are used when forming q_θ.
- Report the cadence and cost of computing D_t: per step, per N steps, or minibatch-sampled anchors? Include wall-clock overhead and GPU memory/time in Section 4.2, and specify whether D_t accumulation resets after replay.
- Justify S=24 for D_day and analyze sensitivity to S and anchor size (e.g., 64, 128, 512). Add an ablation that varies S and |A_k| and plots OP/BWT vs replay counts.
- Explain the choice of forward KL vs reverse KL or JS; include a small ablation swapping divergences and quantifying trigger stability and performance.
- Expand scheduling baselines: at minimum, add a simple loss-based trigger on a small validation buffer; if feasible, a learned scheduler (Klasson et al., 2022). This will clarify whether KL-Time brings advantages beyond parameter norms and naïve loss heuristics.
- Reconcile the main narrative with Table 2: include trigger timelines and per-task accuracies showing where current-task anchors improve efficiency; discuss when to prefer past-task vs current-task anchors in practice.
- Clarify Figure 2’s “four tasks” wording and define “Phase-0 gate” and “trigger divergence” in Figure 3, including the statistical justification for the 10% threshold.

Typos and minor issues:
- Page 4, Figure 1 caption: “When cumulative drift exceeds a threshold ρ” is ambiguous because thresholds are a set. Consider “exceeds the next threshold ρ·D_KL[j].”
- Page 5, Figure 2 caption: “across all four tasks” conflicts with a 5-task benchmark; specify which tasks were analyzed.
- Table formatting: ensure ± errors are consistently formatted as x±y and that replay event counts include standard deviations for all methods or state “N/A” where not applicable.

Criteria that could raise my score:
- Add at least one stronger, conceptually different scheduling baseline (e.g., validation loss trigger or learned policy) with careful compute accounting.
- Provide cost/overhead measurements for KL-Time vs FOREVER without compute-matching ρ; show raw efficiency.
- Include sensitivity analyses for S, anchor size, and divergence choice; clarify Equation (1) implementation details.
- Demonstrate at least one non-classification setting (e.g., short-form generation or QA) or a multilingual variant.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper, figures, and tables, but some implementation details are unspecified in the main text and I did not verify code.

## Soundness
2.5: Between Poor and Acceptable — The core idea is plausible and partially supported, but evaluation breadth is limited, compute comparisons are confounded by ρ matching, and methodological details around KL computation and thresholds need more rigor.

## Excitement
2.5: Between potentially interesting and interesting — Monitoring function-space drift for scheduling is an appealing direction, but the narrow evaluation and baseline set temper enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper has a sound core idea with suggestive evidence, but the empirical scope, missing baselines, and methodological under-specification prevent a confident acceptance. With additional baselines, cost analyses, sensitivity studies, and at least one broader setting, this could rise to Findings.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper focuses on scheduling for classification tasks, which limits applicability to broader LLM use cases like open-ended generation and multilingual adaptation. The reliance on label verbalization may introduce bias if certain verbalizations are culturally or linguistically skewed; this should be acknowledged. Failure modes include unstable triggers when q_θref assigns very low probabilities, which could lead to excessive or insufficient replay. No new data is collected, and all benchmarks are standard, reducing direct societal risk; however, replay over historical data can encode and reinforce earlier biases if not audited.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many hyperparameters are given, but key implementation details for Equation (1), drift cadence, and thresholding are missing from the main text; compute overhead is unreported.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If the promised code is provided, it would help reproduce and extend the study, though the paper itself lacks several necessary details.