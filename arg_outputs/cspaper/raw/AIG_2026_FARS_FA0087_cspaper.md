# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes RazorSFT, an on-policy supervised fine-tuning procedure for continual learning with LLMs. For each prompt, the current policy samples k candidate responses, a task-specific verifier filters correct ones, and the method selects as the training target the accepted response with the highest log-probability under the current model (Equation 1). The authors argue this “KL-minimal” target selection keeps updates close to the current policy and mitigates catastrophic forgetting without RL machinery. Experiments on a 3-stage curriculum (IFEval → MMLU → Countdown) with Qwen2.5-7B-Instruct compare RazorSFT to Offline SFT, GRPO, Zero-shot, and Best-of-8, reporting large reductions in forgetting and competitive or better average accuracy. An ablation claims most forgetting mitigation comes from using on-policy data, with a smaller additional gain from KL-minimal selection. Figures visualize the pipeline (Figure 1), per-task trajectories (Figure 2), and replacement rates (Figure 3). Tables 1–2 provide the main results and ablations.

## Summary Of Strengths
- Simple, clear formulation that operationalizes on-policy SFT with verifier filtering and a principled selection rule. Equation (1) concisely specifies the target-construction mechanism and fallback policy, which helps reproducibility.
- The framework diagram in Figure 1 effectively contrasts Offline SFT versus RazorSFT step-by-step, making the contribution easy to grasp for practitioners.
- The focus on on-policy data as the main driver of forgetting mitigation is timely and relevant to current LLM post-training practice.
- The per-task accuracy trajectories in Figure 2 are informative: they show how Offline SFT collapses on prior tasks while RazorSFT retains performance more stably across stages, aligning with the stated motivation.
- The replacement-rate analysis in Figure 3 is a useful diagnostic; consistently high replacement suggests the method indeed trains mostly on self-generated data, which supports the claimed mechanism.
- Table 1 reports both average accuracy and a forgetting metric (FM), providing a more holistic view than single-metric reporting. Table 2 attempts to isolate contributions from on-policy training and target selection.

## Summary Of Weaknesses
1) Limited and potentially unbalanced experimental scope
- Single model and one curriculum: All results use only Qwen2.5-7B-Instruct and a single 3-stage sequence (IFEval → MMLU → Countdown). This makes generalization uncertain. There is no evidence the method transfers across base models, task orders, or additional task families (e.g., program synthesis, multi-hop reasoning, generation-heavy tasks).
- Missing established continual-learning baselines: While EWC and LwF are cited in Related Work, they are not evaluated in LLM form. Replay-based approaches (e.g., experience replay variants) are not compared, despite being standard for continual learning. In the LLM-CL literature, PEFT-for-CL baselines (e.g., LoRA-based adapters per task) or rehearsal buffers are also common; none are included. The lack of these baselines weakens the claim that RazorSFT is competitive beyond the specific GRPO comparison.

2) Evaluation choices and fairness
- GRPO setup is under-specified. The Countdown performance for GRPO reported in Table 1 (0.261) is low compared with RazorSFT and even Best-of-8. Without clear details about reward shaping, group size, sampling budget, verifier tolerance, and hyperparameters, it is hard to judge if GRPO is a strong baseline here or a strawman.
- Compute parity is unclear. RazorSFT samples k = 8 or 16 candidates per example per epoch. GRPO typically also samples multiple candidates but the paper does not report comparable wall-clock, GPU-hours, or token budgets. A fair comparison requires normalizing training-time sampling and verifier calls across methods.
- Best-of-8 is an inference-time upper bound, not a training baseline. While informative, presenting it as “best” in Table 1 can be misleading when judging training methods. It would be more appropriate to bracket training-time results relative to a standardized compute budget and possibly include a “train with same sampling budget but no verifier filtering” control.

3) Metrics and statistical analysis
- Forgetting Measure (FM) is reasonable, but its use in Table 2 to claim “76% of the improvement is due to on-policy data” is not statistically supported. No confidence intervals or formal tests are provided to verify that the deltas (e.g., -0.642 to -0.179) are robust across seeds and task orders.
- Table 2 shows the KL-minimal variant improves FM only slightly over First-Accepted (-0.032 vs. -0.042) and AvgAcc by 0.021. With no error bars, it is unclear if these gains exceed noise. This undermines the central “KL-minimal” narrative.

4) Verifier design, data splits, and leakage risks are under-specified
- The paper does not describe the exact verification prompts, acceptance criteria, or any calibration of verifier precision/recall. For MMLU, “exact match” is mentioned, but it is unclear whether responses are constrained to single letters, how formatting errors are handled, or whether choices are re-prompted.
- It is not clear what splits are used for training vs. evaluation, especially for MMLU where improper use of test questions during training is a critical flaw. The paper needs explicit guarantees against leakage and must detail whether official dev/test partitions were respected.
- For IFEval and Countdown, the construction of training sets, the sizes per stage, and whether evaluation prompts overlap with training prompts are not documented.

5) Theoretical framing is suggestive, not rigorous
- Section 3.3 asserts KL-minimality by selecting the highest-probability accepted sample and writes KL[δ_{π*} || πθ]. This mix of a delta distribution over a selected trajectory and distributional KL is more intuition than proof. A crisp statement of what is minimized, under which assumptions, and how that connects to parameter updates would strengthen the claim. Otherwise, the “KL-minimal” label risks overclaiming.
- The connection to prior analyses (e.g., on-policy effects vs. reward optimization) is cited but not concretely tied to this selection rule. A formalization of how the acceptance set and argmax by log-probability bounds the induced KL from the previous policy would help.

6) Missing ablations and stress tests
- No sensitivity analysis for k, sampling temperature, verifier strictness, or fallback rates beyond the descriptive Figure 3. For example, how does performance trade off with k or with stricter vs. looser verifiers?
- No permutations of task order. Catastrophic forgetting often depends on order; showing robustness across alternative curricula would be important evidence.
- No experiments with PEFT (e.g., LoRA) vs. full fine-tuning under RazorSFT to see if capacity control interacts with on-policy target selection.

7) Reporting gaps impede reproducibility
- Training data sizes per stage, exact prompt formats, tokenizer/version, batch sizes, optimizer details beyond LR, gradient clipping, and stopping criteria are not specified. The verifier implementation details and acceptance thresholds are missing.
- Results are “averaged over 3 seeds” but the specific seeds, seed variance per task, and CI bars in Figures/Tables are mostly absent. Table 1 shows some ± values, but not everywhere, and Table 2 has none.

8) Claims vs. evidence tension in figures and tables
- Table 1: The claimed superiority on average accuracy is clear (0.616 vs 0.515 for GRPO). However, MMLU after Stage 3 drops for RazorSFT relative to Best-of-8 and GRPO; the text emphasizes retention relative to Offline SFT, but does not analyze why GRPO remains higher (0.730) than RazorSFT (0.673) on MMLU despite similar FM. A per-stage breakdown would help.
- Figure 2: In the Countdown panel, RazorSFT improves sharply while GRPO lags near zero-shot. Without matching compute/sampling budgets, it is hard to conclude the algorithmic cause of this divergence.
- Figure 3: High replacement rates are consistent with on-policy dominance, but the figure does not relate replacement to performance changes across epochs. A scatter or temporal correlation analysis would strengthen the causal interpretation.

9) Positioning and related work coverage
- The paper cites RAFT/RFT and GRPO, but omits several closely related on-policy SFT and continual SFT works that would sharpen the positioning and motivate stronger baselines and ablations (see Missing Related Work).

Overall, while the idea is appealing and the preliminary results are promising, the evaluation is too narrow, the GRPO comparison may not be compute-matched, the “KL-minimal” benefit over simpler first-accepted is small and not statistically established, and important implementation and data-protocol details are missing.

## Potentially Missing Related Work
1) Zhao et al., “On-Policy Supervised Fine-Tuning for Efficient Reasoning,” 2026 — Very close in spirit to replacing RL with on-policy SFT under verifier guidance. Should be discussed in Section 2 and contrasted with Equation (1)’s selection rule; add as a conceptual baseline in Section 4 where feasible.

2) Chen et al., “On-Policy Replay for Continual Supervised Fine-Tuning,” 2026 — Directly targets continual forgetting with on-policy replay, highly relevant to the stated setting. Compare in Related Work (Section 2) and consider adding an on-policy replay baseline in Experiments (Table 1 or a new table).

3) Tajwar et al., “Preference Fine-Tuning of LLMs Should Leverage Suboptimal, On-Policy Data,” 2024 — Analyzes mode-seeking and on-policy effects in preference tuning. Discuss after Section 3.3 to relate “KL-minimal” selection to mode-seeking behavior and cite in Section 2.

4) Ramos et al., “Combining On-Policy Optimization and Distillation for Long-Context Reasoning in Large Language Models,” 2026 — Hybrid on-policy RL with distillation. Discuss in Section 2 as a neighboring design that balances on-policy optimization and auxiliary supervision; relevant when arguing simplicity vs. performance trade-offs.

5) Zhao et al., “Large Language Model Post-Training: A Unified View of Off-Policy and On-Policy Learning,” 2026 — Survey that frames on-policy SFT/RL variants in a unified lens; cite in Section 2 to position RazorSFT within this taxonomy.

6) Ye et al., “Online Experiential Learning for Language Models,” 2026 — On-policy consolidation from deployment data. Situate in Section 2 and discuss in Section 5 as a direction to move RazorSFT beyond controlled curricula.

7) Zhu et al., “On-Policy Self-Distillation for Efficient Diffusion Language Models with Early-Stage Calibration,” 2026 — Shows on-policy self-distillation in another LM family; cite in Section 2 to broaden the scope of related on-policy self-training strategies.

Additionally, evaluate standard continual-learning baselines adapted to LLMs: EWC/LwF with LLM-scale implementations; rehearsal/replay buffers; PEFT-based CL (e.g., task-wise adapters), many of which are covered in TRACE (Wang et al., 2023) and recent LLM-CL surveys.

## Comments Suggestions And Typos
Actionable suggestions that could materially change the evaluation:
- Fairness and compute accounting
  - Report wall-clock, GPU-hours, sampled tokens, and verifier calls per method to normalize comparisons with GRPO. If GRPO uses fewer samples per example than RazorSFT’s k = 8/16, increase GRPO’s sampling to parity or downscale RazorSFT to a matched budget.
  - Add a control that uses on-policy sampling with acceptance but picks the first correct sample with matched compute, and report CIs. In Table 2, add error bars across seeds; otherwise, the incremental benefit of “KL-minimal” is not credible.

- Evaluation breadth and baselines
  - Add at least one additional base model and vary the curriculum order (e.g., Countdown → IFEval → MMLU), demonstrating robustness to model choice and task order.
  - Include EWC, LwF, and a rehearsal-based baseline adapted to LLMs. Also include a PEFT-CL configuration (e.g., LoRA adapters per task with or without rehearsal) to show that RazorSFT’s gains are not just from full fine-tuning capacity.
  - Evaluate on an established CL benchmark like TRACE for additional credibility and comparability.

- Protocol clarity and leakage controls
  - Provide exact dataset sizes per stage, prompt templates, formatting of answers (especially for MMLU), and verifier definitions. State clearly which splits are used for training, validation, and test, and guarantee that no test items are used for training or hyperparameter selection.
  - Quantify verifier precision/recall on a labeled subset. Analyze how varying verifier strictness affects replacement rate, FM, and AvgAcc.

- Ablations and diagnostics
  - Sensitivity to k, temperature, and fallback policy. Report how replacement rate correlates with forgetting and current-task adaptation over epochs. Extend Figure 3 with temporal correlations to performance changes.
  - Study the impact of PEFT vs. full fine-tuning within RazorSFT. Are the benefits additive or redundant?
  - Provide per-stage and per-task confusion patterns, especially for MMLU formatting failures, to understand where RazorSFT loses ground against GRPO.

- Theory and framing
  - Tighten Section 3.3: formally define the objective you implicitly minimize with the “max log-prob among accepted” rule, specify assumptions, and connect it to parameter update magnitudes. Clarify the use of KL with a delta distribution over trajectories and avoid overclaiming without a bound.

Typos and minor issues:
- Table 1 caption: clarify that Best-of-8 is an inference-time oracle-like baseline, not a training method; avoid bolding it alongside training methods to prevent confusion.
- Section 4.3: “accounts for 76% of the total FM improvement” — add confidence intervals and exact formula used to compute the share.
- Figures 2–3: include error bars across seeds; current plots may overstate certainty.
- Reference formatting is inconsistent in places (missing spaces after periods; merged references in a single line on Page 7).
- Throughout: specify temperatures used per stage more precisely (“0.8–1.0” is too coarse without per-stage detail).

Criteria that could raise my score:
- Add the missing continual-learning baselines (EWC/LwF, replay, PEFT-CL) and a compute-matched GRPO comparison, all with thorough reporting and CIs.
- Demonstrate robustness across at least one additional base model and permuted task orders.
- Provide detailed protocols for verifiers, data splits, and leakage safeguards, plus sensitivity studies for k/temperature/verifier strictness.
- Strengthen the theoretical section with a clear statement and, ideally, a bound relating the selection rule to induced KL or update norms.

## Confidence
3: Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5: Between Poor and Acceptable — Some main claims (KL-minimal advantage) are not sufficiently supported statistically; compute parity and leakage controls are unclear; evaluation breadth is limited.

## Excitement
3.0: Interesting — Simple on-policy SFT with verifier filtering is a practical direction and the results are promising, but the current evidence is not yet compelling for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Rationale: The method is appealing and supported by intuitive diagnostics (Figures 1–3) and summarized performance (Table 1). However, compute-parity questions with GRPO, absent strong continual-learning baselines, limited scope (one model/one curriculum), and insufficient statistical backing for the central “KL-minimal” benefit collectively prevent a confident acceptance. With a broader and more rigorous evaluation and clearer protocols, this could rise to a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not include a limitations or societal impact section. It should discuss:
- Reliance on verifiers: bias or brittleness in rule-based or programmatic verifiers can skew training, potentially entrenching failures for underrepresented formats or domains.
- On-policy training risks: distributional narrowing around verifier-amenable solutions; potential degradation of generality or stylistic diversity.
- Resource intensity: repeated sampling and verification can increase compute and carbon cost; discuss ways to budget or amortize verifier calls.
- Application contexts: continual adaptation might inadvertently retain harmful behaviors if verifiers miss them; consider safety-oriented verifiers or red-team checks.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Code availability is stated, but many crucial experimental details (verifier specs, data splits, compute budgets, hyperparameters, exact prompts) are missing from the paper. More comprehensive reporting is needed to reach “mostly reproducible.”

## Datasets
1: No usable datasets submitted. There is no new dataset contribution; training/evaluation data are existing benchmarks.

## Software
3: Potentially useful. If the released code includes the verifier implementations and training scripts as used, it could be useful; otherwise, the paper alone is insufficient.