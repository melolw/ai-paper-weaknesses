# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies how to train language model based heuristics to accelerate A* search. The core idea is to subsample training data from solved problems in a way that is better aligned with what both A* and the LM need. Through an oracle-noise study and empirical LM training, the authors argue that prediction accuracy near the goal is most important for reducing A* search length, and that LMs also generalize better when trained more on those “end” nodes. They formalize a per-node contribution score C(n) that increases toward the goal, then propose sampling nodes along optimal paths with a softmax over C(n) at temperature τ. On maze and sokoban domains, under two losses (L2 and LM), their sampling outperforms uniform subsampling on ILR, sometimes matching or surpassing a full-data baseline with substantially fewer training nodes. They also report wall-clock speedups in harder settings.

## Summary Of Strengths
- Clear disentangling of planner-side vs. model-side requirements. The oracle perturbation experiment in Table 1 is a clean way to show that A*’s iteration count (ILR) is most sensitive to heuristic errors near the goal; the effect persists as noise σ increases.
- Consistent empirical support that LMs benefit from a heavier focus on end nodes. Figure 1 (heatmaps) shows that each split generalizes best to itself; focusing on the “end” split reduces validation MAE on end nodes and, as seen in Table 2, also leads to better ILR than “initial” or “middle,” though still behind using “all,” which motivates the weighted mix.
- Simple, planner-aware sampling distribution. Equation 6 defines a monotonically increasing contribution C(n) and Equation 7 uses a temperature-controlled softmax to allocate more training samples near the goal while still including earlier nodes. This directly operationalizes the earlier observations.
- Practical efficiency gains with limited data. In Table 3, sampling from D(n, τ) generally improves ILR over uniform with the same training-set size and sometimes rivals a full-data baseline trained on substantially more nodes. Table 7 suggests the trend carries to larger LMs as well.
- Measurement of wall-clock impact. Table 4 reports ITR; on harder sokoban OOD, ITR > 1 indicates real speedups, which matters for the practical cost-benefit of adding an LM to A*.

Originality: The planner-aware data selection view for LM-based heuristic training is a useful angle.  
Quality: The experiments are generally sound, use multiple metrics (ILR, SWC, Optimal %, ITR), and ablations across data splits, two losses, and different model sizes.  
Clarity: The paper is mostly clear, with concrete definitions (Equations 1–7) and domain details.  
Significance: While the domains are classical and constrained, the findings are likely relevant for LLM-planning setups that integrate search.

## Summary Of Weaknesses
1) Limited baselines for data selection and curriculum. The main comparison is to uniform subsampling and a full-data baseline. Given the framing as data-centric selection, one would expect comparisons to at least a few standard coreset or curriculum variants (e.g., distance-to-go buckets with hand-tuned schedules, hardness-proportional sampling, or known data-pruning heuristics). Without these, it is hard to attribute gains specifically to the proposed log-shaped C(n) vs. simply “more end nodes.” Actionable: add baselines like linear w.r.t. distance-to-go, inverse distance, fixed-frontier-only sampling, or curriculum over initial→middle→end and end→middle→initial.

2) Heuristic contribution model lacks justification. Equation 6 uses a log form, C(n) = log(|π*| / (|π*| − g(n))). The paper claims it captures “diminishing returns,” but there is no derivation or sensitivity analysis. Why log and not linear, quadratic, or piecewise schedules? A small ablation contrasting shapes and reporting ILR/SWC would strengthen the claim that the particular form matters. Actionable: add an ablation comparing log vs. linear vs. polynomial vs. learned weighting.

3) Narrow domains and path-only supervision. Training only on optimal-path nodes is conventional but excludes off-path states that A* will expand. In sokoban especially, off-path states can be critical for effective pruning. The oracle experiment in Table 1 considers all nodes but is limited to maze and uses synthetic noise. Actionable: evaluate a variant that sparsely samples near-optimal or off-path nodes, or quantify the frequency at which end-of-path training transfers to non-path nodes encountered during search.

4) Missing comparisons to planner-aware learning baselines. Related lines include differentiable-planner training and RL-over-search (cited in Section 2.1) that optimize search behavior more directly, though at higher cost. Even a scaled-down comparison would help contextualize cost-performance trade-offs. Actionable: include at least one such method or a simpler policy-guided baseline to illustrate relative efficiency.

5) Mixed story on optimality and solution quality. While ILR improves, SWC and Optimal % are sometimes flat or slightly worse, especially in Table 3 for maze under L2/LM. The paper states “near-optimal solutions,” but this trade-off is not fully analyzed. Actionable: quantify admissibility violations, analyze where suboptimality occurs, and whether temperature τ shifts an optimality–speed trade-off.

6) Incomplete exploration of τ and data–parameter scale. Table 3 and the text note different τ preferences for L2 vs LM objectives, but there is no systematic sensitivity curve. Similarly, Table 7 shows non-monotonic behavior across model sizes. Actionable: add plots of ILR/SWC vs. τ and vs. training set size for fixed model size, plus a short discussion about stability across random seeds.

7) Wall-clock reporting is hard to interpret for maze. Table 4’s ITR for maze is ~5e-3, which suggests the LM heuristic is far slower, but the text attributes this to domain simplicity and low node expansions. A breakdown of total time into A* expansions, LM forward passes, and cache hits would clarify where the time goes. Actionable: add a runtime decomposition and report average number of LM calls per puzzle.

8) Figures and prompts need tighter integration. Figure 4 shows the prompt, but there is little analysis of how decoding choices (top-k, self-consistency) influence ILR/ITR. Since Table 4 shows LM-head models are significantly slower, the choice of decoding and head could matter. Actionable: ablate decoding settings and the L2 head vs LM head trade-offs on wall-clock.

9) Evaluation breadth and statistical rigor. Results are averages, but there is no report of variance or confidence intervals. Given small OOD splits in sokoban (notably the 15-puzzle subset), this matters. Actionable: include error bars and multiple random seeds for training and data sampling.

10) Limited connection to broader LLM planning and agent systems. The paper positions itself within LM-heuristic learning but could better connect to current LLM-agent planners and adaptive lookahead designs that also tackle efficiency. This would help readers understand when this approach is likely to be preferable.

Specific references to figures and tables:
- Figure 1: The validation MAE heatmaps clearly show split-specific generalization and that the “end” split exhibits lowest error on its own validation split. This is directly used to motivate Equation 7, but the figure also reveals that training on “all” gives the best cross-split generalization, which the proposed softmax mixture is meant to approximate. A discussion of how the selected τ reproduces the “all” trend while emphasizing end nodes would strengthen the link.
- Table 1: The oracle study is compelling evidence that correcting the heuristic at the “end” of the path yields the largest ILR gains, and that increasing σ reduces optimality. However, it appears to be maze-only; repeating a smaller-scale version for sokoban would increase confidence.
- Table 2: Confirms the advantage of “end” over “initial” or “middle” when training real LMs; also shows that excluding “end” (~end) hurts. This supports the main design but also reveals that “all” still wins, underscoring the need for a balanced but end-heavy sampling rather than end-only.
- Table 3: The proposed D(n, τ) subsampling improves ILR over uniform in most settings and can rival full-data. The mixed SWC/Optimal % results suggest a speed–quality trade-off that warrants further analysis or constraints.
- Table 4: ITR indicates the LM amortizes compute on hard sokoban OOD but not on maze. A per-component time breakdown would make this more actionable.
- Table 7: The scaling experiment suggests the trend persists, but larger models do not always help ILR. This points to a data–parameter mismatch that should be discussed.

## Potentially Missing Related Work
1) Opedal et al., “Learning to Reason Efficiently with A* Post-Training,” 2026 — directly uses A* to inform LLM post-training signals for both accuracy and efficiency. It should be discussed in Section 2.2 and contrasted with this paper’s data-selection approach; also mention in Section 6 when discussing computational cost and efficiency signals.

2) Liu et al., “Imagine-then-Plan: Agent Learning from Adaptive Lookahead with World Models,” 2026 — proposes adaptive multi-step lookahead with learned world models. Relevant as an alternative to static training distributions for efficiency. Add to Section 2.2 and compare conceptually after Equation 7 regarding dynamic vs. static planning guidance.

3) Webb et al., “A brain-inspired agentic architecture to improve planning with LLMs,” 2025 — introduces a modular planner architecture with internal search. It connects strongly to improving LLM planning efficiency; include in Section 2.2 and briefly contrast in the Conclusion.

4) Zheng et al., “Monte Carlo Tree Search for Comprehensive Exploration in LLM-Based Automatic Heuristic Design,” 2025 — explores the heuristic space via MCTS. This is directly relevant for “how to obtain better heuristics,” offering an alternative to supervised residual learning. Cite in Section 2.2 and discuss as a potential complementary baseline in Section 6.

5) Wei et al., “PlanGenLLMs: A Modern Survey of LLM Planning Capabilities,” 2025 — a comprehensive survey that can better situate this work’s contribution relative to broader planner–LLM integrations. Add to Section 2 and use it to sharpen the problem framing.

6) Du et al., “A Survey on the Optimization of Large Language Model-based Agents,” 2026 — reviews optimization strategies for LLM agents, including methods to improve long-horizon reasoning and efficiency. Include in Section 2.2 and position the proposed data selection within agent optimization techniques.

## Comments Suggestions And Typos
Actionable suggestions:
- Add stronger baselines for data selection and curricula: linear or polynomial weightings over distance-to-go; simple end-only; and schedule-based curricula. Report ILR, SWC, Optimal %, and ITR across these.
- Justify or ablate the form of Equation 6: compare log vs. linear vs. convex/concave forms; include a short theoretical or empirical rationale that this shape best matches the diminishing-returns behavior seen in Table 1.
- Analyze optimality trade-offs: report rates of inadmissible predictions, highlight the distribution of suboptimal gaps, and show how τ controls the ILR vs. Optimal % frontier. A Pareto frontier plot would be ideal.
- Provide runtime breakdowns: LM forward time (by head), number of LM calls per puzzle, cache hit rate, A* expansions. This will make Table 4’s results easier to interpret and guide practitioners.
- Explore limited off-path sampling: assess whether a small percentage of near-path or frontier nodes improves transfer when the search strays, especially in sokoban where deadlocks are common.
- Expand sensitivity analyses: ILR/SWC vs. τ curves, data size vs. ILR, and variance across seeds.
- Decoding and head ablations: compare top-k values, self-consistency counts, and the L2 regression head vs. LM head with respect to both ILR and ITR.

Typos and minor issues:
- Page 4, Section 3.4: “a another node m” → “another node m”
- Throughout: “upto” → “up to”
- Page 6, footnote marker: “^4 The high ILR of ~middle is therefore not representative” — consider clarifying what it is not representative of and why.
- Page 3, 3.2: “This becomes very expensive… therefore, we only consider nodes on the optimal path” — add a brief justification that this choice is conventional but discuss potential downsides for generalization to off-path expansions.
- Page 8, Table 4: report standard deviations or 95% CIs; also clarify hardware and batching for LM inference.

Criteria that could raise my score:
- Add the ablations on C(n) functional form and data-selection baselines; show consistent ILR gains without sacrificing Optimal %.
- Provide runtime decomposition and decoding/head ablations; demonstrate a favorable cost–benefit on at least one additional domain or a larger sokoban OOD set.
- Include limited off-path sampling results or a short study showing robustness to off-path expansions.

## Confidence
4: Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5: Between Acceptable and Strong — The empirical core is solid with multiple metrics and ablations, but the contribution function’s form is under-justified and comparisons to stronger data-selection baselines are missing.

## Excitement
3.0: Interesting — The planner-aware sampling idea is tidy and useful, but the scope is somewhat narrow and evaluation breadth is limited.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The work provides a careful, planner-aware training distribution with consistent ILR gains under constrained data budgets, supported by an oracle study and multiple metrics. However, the evaluation is limited to two classical domains, the contribution function is not sufficiently justified relative to alternatives, and comparisons to broader data-selection/curriculum baselines and planner-aware learners are missing. These gaps limit readiness for the main conference track but fit the Findings bar.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section noting the classical nature of the domains and inherited LM biases. Additional points to consider:
- Generalization beyond grid-based puzzles remains untested; performance on real-world language-heavy planning tasks is unclear.
- Efficiency benefits depend on domain hardness; as Table 4 shows, LM heuristics can be net slower on easy problems.
- Since training focuses on end-of-path nodes, there is a risk of degraded behavior on off-path or deadlocked states; this could bias search toward late-stage quality at the expense of mid-search pruning.

Overall, the societal risk profile is low for the studied domains, but if extended to real-world settings, care should be taken regarding data bias and the consequences of suboptimal planning.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Datasets are described, equations and metrics are explicit, prompts are shown, and hyperparameters are given. Adding code and random seeds would move this to 5.

## Datasets
2: Documentary — The datasets are adapted or procedurally generated for classical domains. They are useful to replicate the study but of limited broader utility.

## Software
1: No usable software released. If code will be released, please state this and include essential scripts for data generation, training, and evaluation.