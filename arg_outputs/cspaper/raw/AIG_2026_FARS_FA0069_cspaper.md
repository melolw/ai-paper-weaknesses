# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies how to handle truncated rollouts in reinforcement learning with verifiable rewards (RLVR) for long chain-of-thought (CoT) mathematical reasoning. It compares three strategies when a response hits a token cap: (A) treating truncation as failure, (B) DAPO’s overlong shaping (a soft length penalty), and (C) the proposed timeout bootstrapping that replaces a terminal failure reward with the critic’s value estimate at the truncation state. Experiments with DeepSeek-R1-Distill-Qwen-1.5B on MATH-500, following a pre-registered plan, show mixed results: timeout bootstrapping does not win on average but improves over baselines on one stable seed. Analysis attributes the failure to critic value collapse and miscalibration, evidenced by negative correlation between critic estimates and eventual correctness.

## Summary Of Strengths
- Clear problem framing: truncation in long-horizon RLVR is a real practical issue; the paper cleanly formulates three strategies and ties the proposed idea to classical RL time-limit bootstrapping (Pardo et al., 2017).
- Methodology is explicitly specified with equations and implementation choices. Equation 4 concisely defines the proposed bootstrapping rule with clipping and stop-gradient, and Equation 5 provides the theoretical intuition for why bootstrapping at timeouts reduces bias.
- Empirical setup is mostly transparent: model, data split (MATH-500 and a long subset), PPO/GAE hyperparameters, and seeds are reported.
- The analysis is the main contribution. Figure 2c directly shows critic value collapse to approximately -1 within ~15–20 steps, which convincingly explains why Condition C largely degenerates to truncate-as-failure. Table 2 further demonstrates negative correlation and AUROC < 0.5 for the critic across prefixes, providing evidence of miscalibration rather than mere noise.
- Honest, pre-registered evaluation and a balanced discussion of failure modes and limitations. The paper avoids over-claiming and offers concrete next steps (e.g., critic pretraining, curriculum warmup, inclusion of truncated rollouts in the critic loss).

## Summary Of Weaknesses
1) Limited experimental depth and statistical power
- Only two seeds per condition and 100 rollout steps. This is explicitly acknowledged, but it undermines the reliability of conclusions and the pre-registered “collapse” criterion, which by design could not trigger within 100 steps (Section 5, Limitations). The instability of Condition C across seeds is therefore hard to interpret.
- The main significance claim for “promise” rests on a single stable seed; the average across seeds fails the pre-registered success criteria (Section 4.2).

2) Confounding implementation choices for Condition C
- Timeout bootstrapping uses several add-ons: delayed activation for 10 steps, truncated rollouts in critic loss at 10% weight, clipping to [-1, 1], and a nontrivial entropy bonus. These could each materially influence stability and value learning, yet ablations are missing. Without isolating these factors, it is unclear whether the core idea or the scaffolding drives the observed dynamics.
- The decision to mostly exclude truncated rollouts from critic training, then later include them at 10% weight (Section 3.4), may directly induce the “starvation” that leads to miscalibration at truncation states. A systematic sweep of this weight is essential.

3) Entropy tuning and stability
- Figure 2a shows that A/B collapse in entropy (< 0.2 nats), while Condition C seed 42 is stabilized at 0.75 nats and seed 137 explodes to 8.4 nats, diverging after ~60 steps. This suggests the 0.001 entropy coefficient is highly sensitive. There is no reported grid or adaptive control (e.g., EntroPIC-style) to determine whether moderate, robust settings exist. As a result, the comparison across A/B/C is entangled with very different entropy regimes.

4) Narrow evaluation scope
- All experiments are on one small model (1.5B) and one math dataset variant. Claims about “long-horizon reasoning” are plausible, but cross-domain generality remains untested. Even within math, the evaluation reports Pass@1 with 4 samples per problem; sensitivity to sampling settings or verifier extraction details is not analyzed.

5) Pre-registration criteria vs. experimental design
- The pre-registered success criteria require CI exclusions and collapse incidence checks, but the run length and seed count make these thresholds unlikely to be meaningfully assessed. This mismatch weakens the evidential weight of the conclusions.

6) Weak baselining on value learning
- The core failure mode is attributed to critic miscalibration. The paper does not test standard remedies such as critic pretraining on completed rollouts, auxiliary per-step supervision (e.g., predicting local correctness or solution-state features), or contrastive prefix-level objectives. Without at least one such baseline, it is difficult to assess how much of the observed failure is due to Condition C vs. an underpowered critic.

7) Missing ablations that matter
- No sweeps for: entropy coefficient, delayed bootstrapping length, the 10% truncation weight for critic, the clipping range for V, or activation thresholding based on critic calibration. Given Figure 2c and Table 2, these ablations would be decisive for interpreting the negative results.

8) Limited statistical reporting
- Table 1 gives point estimates, but only one explicit CI appears in text (Section 4.2). There are no CIs for per-condition deltas, no tests for the seed-by-condition interaction, and no reporting of variance of truncation rates in Figure 2b beyond final bars. A fuller uncertainty analysis would strengthen the empirical case.

9) Positioning gaps in related work
- The Related Work section is focused on DAPO/LAPO/APRIL/UloRL and time limits in RL, but omits several highly relevant RLVR analyses that study critic and reward pathologies and long-horizon training in adjacent domains (see “Potentially Missing Related Work”).

10) Reproducibility details
- While many hyperparameters are listed and the code is reportedly available, some key items remain underspecified in the paper body: verifier implementation details and answer-extraction heuristics, hardware and throughput, and exact stopping/divergence handling procedures during the divergent run. These matter for reproducing entropy dynamics and truncation rates reported in Figure 2.

Figure- and Table-specific comments:
- Figure 1 is a clear schematic of the three conditions. The right-hand PPO blocks and GAE equations contextualize where reward assignment differs across A/B/C. This supports the methodological clarity claim.
- Figure 2c is central: it shows V(s_T) quickly trending from near 0 to ≈ −1 within 15–20 steps for both seeds under Condition C, effectively making Equation 4 revert to Equation 2 behavior. This directly undercuts the intended advantage of timeout bootstrapping.
- Table 1: timeout bootstrapping (C) achieves 54.60% on the long subset for seed 42 versus 52.40% (A) and 50.60% (B), but averages to 52.50% across seeds due to the divergent seed 137. This supports the authors’ “promise but unstable” narrative, yet also underscores instability as a first-order concern.
- Table 2: the critic’s Pearson r becomes more negative with longer prefixes (−0.211 at 90%), and AUROC falls to 0.314. Coupled with mean V differences flipping the expected sign at longer prefixes (−0.377 for correct vs −0.083 for incorrect at 90%), this is strong evidence that the critic is learning inverted signals.

## Potentially Missing Related Work
1) Wen et al., Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs, 2025 — Analyzes how RLVR shapes CoT and credit assignment, directly relevant to the paper’s claims about value learning and miscalibration. Should be discussed in Section 2 and contrasted with the failure analysis in Sections 4.4–5.

2) Wu et al., RLVR-World: Training World Models with Reinforcement Learning, 2025 — Extends RLVR to long-horizon generative settings with GRPO-style training. Compare stabilization choices in Section 2 and consider as a reference for alternative critic designs in Section 5.

3) Shao et al., Spurious Rewards: Rethinking Training Signals in RLVR, 2025 — Shows RLVR can benefit even under misaligned/random rewards, shedding light on why critic/value failures may not doom performance. Discuss in Section 5 to contextualize the observed negative correlation in Table 2.

4) Su et al., Crossing the Reward Bridge: Expanding RLVR Across Diverse Domains, 2026 — Proposes probabilistic, soft verifiers as rewards. Add to Section 2 and discuss as an alternative to sparse binary rewards that could reduce the need for fragile bootstrapping (Section 5).

5) Jiang et al., From Verifiable Dot to Reward Chain: Verifiable Reference-based Rewards for RL of Open-ended Generation, 2026 — Decomposes rewards over generation to improve credit assignment. Cite in Section 2 and discuss as a complementary strategy to timeout bootstrapping in Section 5.

6) Liu et al., HarmRLVR: Weaponizing Verifiable Rewards for Harmful LLM Alignment, 2025 — Highlights stability and safety risks from mis-specified RLVR signals. Add to Section 2 and briefly reflect on safety implications of modifying truncation rules (Section 6/Limitations).

7) Zhu et al., Video Models Can Reason with Verifiable Rewards, 2026 — Uses dense decomposed rewards and early-step focus for long visual trajectories, relevant for stabilizing long sequences. Discuss in Section 2 as cross-modal evidence that richer reward structure can help mitigate bootstrapping fragility.

8) Liu et al., Instructing LLMs to Negotiate using RLVR, 2026 — Demonstrates long interactive trajectories under RLVR; useful to discuss external validity of timeout-style bootstrapping beyond math (Section 5).

9) Jiao et al., Tandem Reinforcement Learning with Verifiable Rewards, 2026 — Introduces co-generation dynamics for long CoT. Compare in Section 2 and consider in Section 5 as an alternative route to reduce truncation by modifying rollout generation.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide ablations for the components that most plausibly affect stability and critic calibration:
  - Entropy coefficient grid or an adaptive controller (e.g., EntroPIC); report entropy trajectories and final KL for each.
  - Critic training on truncated rollouts: vary the 0%, 10%, 30%, 50% weights; report impact on Figure 2c and Table 2 statistics.
  - Delayed bootstrapping horizon (e.g., 0, 5, 10, 20 steps) and clipping ranges (e.g., [-1,1], [-0.5,0.5]).
- Add at least one remedy baseline specifically targeted at value collapse:
  - Critic pretraining on completed rollouts before RL starts.
  - Auxiliary prefix-level targets (e.g., step correctness or decomposition scores) to encourage value calibration at intermediate states.
  - Calibration-gated activation: enable bootstrapping only when AUROC on a held-out prefix set exceeds a threshold.
- Expand statistical reporting:
  - Confidence intervals for all entries in Table 1, deltas, and truncation-rate differences; include seed-by-condition interaction tests.
  - Report evaluation variance over multiple decoding seeds per checkpoint and sensitivity to temperature/top-p.
- Clarify reproducibility details in the paper body:
  - Verifier implementation, answer-extraction heuristics, and any failure cases excluded.
  - Hardware, tokens/sec, wall-clock per step, and the exact criteria/procedure that detected divergence for seed 137.
- Consider a small-scale cross-domain check (e.g., coding or proof-style tasks with verifiable rewards) to assess generality, even if only for a short training budget.

Typos/clarifications:
- Section 4.3: “Figure 2 reveals the primary failure mode…” Consider labeling subplots (a/b/c) explicitly in the caption earlier; you already do, but referencing them in-text as “Figure 2c” consistently would help.
- Table 1 caption: define the “long subset” again for self-containment.
- Section 3.4: clarify whether truncated rollouts contribute to the critic loss uniformly across steps or only at truncation states.

What could change my evaluation:
- Demonstrating robustness of Condition C across ≥3 seeds with entropy-stabilized training and meaningful ablations that isolate bootstrapping effects would raise Soundness and Overall Assessment.
- Showing a value-calibrated critic (e.g., AUROC > 0.6 at 75–90% prefixes) together with improved long-subset accuracy over both baselines, with CIs excluding zero, would move me toward main-conference acceptance.

## Confidence
4: Quite sure after careful checking — I examined the core claims, equations, and figures; unlikely I missed a critical point.

## Soundness
2.5: Between Poor and Acceptable — The analysis is insightful, but experimental support is thin (two seeds, short training), key ablations are missing, and instability confounds the comparison.

## Excitement
2.5: Between potentially interesting and interesting — The problem is timely and the negative results are instructive, but the current evidence is limited.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Rationale: The study targets an important, concrete issue in RLVR and provides thoughtful analyses (Figure 2c, Table 2) that are useful to the community. However, the empirical foundation is not strong enough for the main conference: results hinge on one stable seed, instability is not adequately ablated, and value-collapse remedies are not tested. With stronger ablations and stability controls, this could be a solid Findings candidate.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges several limitations: small model size, short training horizon, limited seeds, and possible lack of generality. Societal risks are modest here, but RLVR systems can exhibit reward hacking or unintended behavior amplification; discussing potential safety implications when modifying truncation/bootstrapping rules would be prudent, especially if these alter exploration and entropy dynamics. Consider commenting on compute costs and accessibility for researchers without large budgets.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Many details and hyperparameters are provided and code is said to be available, but some verifier and operational details are missing from the paper body.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — The code could help others replicate the comparison and analyze critic collapse, assuming the repository matches the described setup.