# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes Hierarchical Delegated Oversight (HDO), a framework for scalable oversight in multi-agent systems. HDO organizes verification as a tree of delegated debates in which a root overseer decomposes contentious alignment judgments into sub-claims routed to specialized verifiers (factual, logical, policy, planning) under a cost budget. Theoretical analysis provides a pathwise error compounding lemma and a PAC-Bayesian bound (Equation 1) suggesting that misalignment risk decreases with delegation depth. Experiments on WebArena and AgentBench report improved task success, reduced “collective hallucination,” and better cost–accuracy trade-offs relative to baselines such as flat debate and CoT+Verifier, with additional claims about robustness to collusion. The paper also discusses a cost-aware routing policy and presents an ablation/error taxonomy.

## Summary Of Strengths
- Problem framing and scope: The paper tackles an important and timely question in NLP-adjacent agentic settings, namely how to scale oversight beyond human bottlenecks when multiple LLM agents collaborate.
- Conceptual synthesis: Clear articulation of a hierarchical “verification game” with cost-aware delegation and verifier diversity as a defense against collusion. Figure 1 is a helpful schematic linking routing, budget constraints, and leaf verifiers, making the architecture understandable at a glance.
- Theoretical scaffolding: The pathwise-miss analysis (Lemma 1) and PAC-Bayesian style risk bound (Equation 1) provide a starting point for formalizing how added depth could reduce error, with some consideration for unbalanced trees and correlations (Sections 5 and Appendix A–C).
- Practical angles: The cost-aware routing policy (Section 4.2) balances uncertainty reduction per token, aligning with practical constraints in LLM oversight. The pseudo-code in Appendix B improves clarity and could guide implementation.
- Initial empirical signals: On WebArena and AgentBench, the paper reports better success and lower hallucination than automated baselines, while using notably fewer tokens than a “human-oversight” proxy. Table 1 and Table 2 summarize these claimed gains succinctly. Table 4’s error taxonomy is a valuable diagnostic lens.

## Summary Of Weaknesses
1) Strength of theoretical guarantees and assumptions
- The core bound (Equation 1) rests on Assumption 1 and an independence-like premise across nodes. The paper acknowledges potential correlation and proposes diversity/redundancy as mitigation, but stops short of quantifying or validating these effects. As a result, the exponential e^(-αd) improvement can be optimistic in realistic settings where leaf verifiers share blind spots (Section 5, Appendix A). The necessity and practical verifiability of ε (leaf false-negative rate) and η (type assignment correctness) are not established or empirically calibrated.

2) Limited connection between theory and practice
- The routing policy and monotonicity proposition (Section 4.2) are not linked to measurable properties of real verifiers. There is no empirical audit of calibrated uncertainty u(q), nor a sensitivity analysis showing how miscalibration affects delegation depth, budget consumption, and final risk.

3) Experimental design under-specified
- Despite reporting aggregated results, many critical details are missing for reproducibility. For WebArena, Section 6 reports “50 tasks,” but does not specify task selection, seed control, or whether agents have browsing/tool access parity across conditions. For AgentBench, only two tracks are discussed and “5 seeds” are mentioned (Appendix E), but the main text omits confidence intervals, variance, or statistical significance tests. The paper itself notes “significance tests deferred to supplement” (Agents4Science checklist), which prevents assessing robustness.

4) Baseline parity and fairness
- The “Human oversight” proxy baseline is a “strong evaluator model” that reviews all steps (Section 6). It is not clear whether the tool usage and access affordances at evaluation time are controlled to be comparable with HDO’s leaf verifiers. This weakens claims that HDO matches human oversight accuracy “at ~half the tokens” (Section 6.1). Similarly, “CoT+Verifier” is defined as per-step verification without hierarchy, but the exact verifier stack and triggers differ from HDO; comparisons may reflect different tool budgets rather than oversight strategy.

5) Metrics and definitions need more rigor
- “Collective hallucination” and “oversight accuracy” are central to the paper’s claims, but their operational definitions are only sketched. For hallucination, it is unclear how disagreements are adjudicated, what counts as “reinforcing a false claim,” and how these were annotated. For oversight accuracy, agreement with human labels is cited, but sampling, labeling protocol, and inter-annotator reliability are not provided.

6) Missing or thin ablations tying decisions to outcomes
- The paper claims randomized routing, redundancy at probability p_red = 0.25, and multiple verifier types. However, there is no ablation isolating the contribution of each defense to the final performance or the risk–cost frontier. Table 3 lists hyperparameters, but there is no analysis of their impact on Table 1/Table 2 outcomes or Figure 2’s claimed Pareto dominance.

7) Overclaiming dominance on efficiency frontiers
- Figure 2 is described as showing that HDO dominates flat debate for budgets > 4k tokens, but the figure itself is not included in the PDF as an actual plot; the text describes the frontier without presenting numerical curves, error bars, or exact budget points. The absence of the actual figure hinders verification of the frontier claim and inspection of potential crossover regions or variance.

8) Weaknesses in collusion evaluation
- The collusion stress tests (Section 6.3) are synthetic and not tied to a standardized benchmark. The detection rate comparison (8/10 vs. 3/10) is based on 10 injected attempts, which is too small for reliable inference, and the construction protocol is not described in enough detail to be reproducible.

9) Reproducibility and release plans
- The paper states “Full prompts/seeds deferred to supplement; will release upon acceptance,” and “code to be released post-review.” This prevents independent verification of the empirical findings during review. Given the centrality of empirical claims in Sections 6–6.3, this is a significant limitation.

10) Ambiguous scope relative to ACL
- The work focuses on multi-agent oversight with LLMs; while relevant to Dialogue and Interactive Systems, Human-Centered NLP, and Interpretability/Analysis, several components (e.g., policy rule-checkers, planning verifiers) are domain-general AI. The NLP relevance is present but not as central as desired for the main track; this would be fine if the empirical validation strongly leveraged core NLP tasks or datasets in depth, which is currently limited.

Detailed comments referencing figures, equations, and tables:
- Figure 1: The diagram communicates the intended architecture well, but it hides crucial design choices. For example, the “Fact verifier (retrieval+NLI)” box does not specify how NLI confidence is calibrated to feed u(q) in Equation for routing. Also, the “Budget B” and “argmax Δu/c” box suggests myopic selection; there is no discussion of submodularity or global budget allocation. This undercuts the claim in Section 4.2 that the policy is alignment-monotone under practical conditions.
- Equation (1) and Lemma 1: The multiplicative miss assumption is strong. Section 7 admits “risk bounds degrade under correlated failures,” but the main claims in Section 5 rely on the exponential decay; there should be a quantified bound under correlation (e.g., via dependency graphs or variance-inflation factors) to assess realistic gains at moderate depth.
- Table 1: The improvements on WebArena (Success 88 vs. 84–80; Hallucination 10 vs. 12–14; Tokens 7.5k vs. 6k or 16k) look promising. However, there are no standard deviations, confidence intervals, or per-domain breakdowns. “Oversight Acc. 95” is unclear without methodology for human labels. It is also unclear whether “Avg. Tokens” includes tool calls identically across methods.
- Table 2: AgentBench highlights show large relative gains (e.g., Lie detection 80% for HDO vs. 50% flat debate). Again, the sample size, seeding, and label protocol for “lies” require detail, especially since “fair deals” depends on a task-specific fairness definition. Without these, it is hard to judge the robustness of the reported 12–15 point deltas.
- Table 3 and Table 4: Table 3 lists hyperparameters but lacks sensitivity analysis; the reader cannot infer how much each hyperparameter contributes to Table 1/Table 2. Table 4’s error taxonomy is helpful qualitatively, yet the process for labeling errors (who labeled, how disagreements were resolved) is not given, limiting its scientific value.

## Potentially Missing Related Work
1) Liang et al., “Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate,” 2024 — Studies debate protocols that promote divergent reasoning to avoid premature consensus. This is directly relevant to HDO’s goal of mitigating sycophancy; should be added to Related Work and discussed in Section 4.1 to contrast delegated entailment games with divergence-promoting debate strategies.

2) Li et al., “Improving Multi-Agent Debate with Sparse Communication Topology,” 2024 — An efficiency-focused debate design that reduces token costs while preserving accuracy. Compare to HDO’s cost-aware routing in Section 4.2 and include as a baseline or at least discuss potential hybridization in Section 6.

3) Chan et al., “ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate,” 2024 — Builds heterogeneous evaluator teams via debate; directly relevant as a possible leaf-verifier ensemble. Cite in Sections 2 and 4 and consider as an alternative verifier design in experiments.

4) Smit et al., “Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs,” 2024 — Systematic benchmarking of debate strategies and failure cases; should inform HDO’s debate-tree design, especially thresholds and redundancy. Discuss in Related Work and in Section 6.3 ablations.

5) Chern et al., “Combating Adversarial Attacks with Multi-Agent Debate,” 2024 — Uses debate as inference-time defense; relevant to HDO’s collusion-resilience claims. Add to Section 6.3 and consider as an evaluation setting.

6) GroupDebate et al., “GroupDebate: Enhancing the Efficiency of Multi-Agent Debate Using Group Discussion,” 2024 — Proposes clustered debate for cost reduction. Discuss in Section 4.2 and consider relating Figure 2’s efficiency frontier to group-based protocols.

7) Asad et al., “RedDebate: Safer Responses through Multi-Agent Red Teaming Debates,” 2025 — Targets unsafe behavior via adversarial debate with memory modules; compare to HDO’s safety/violation metrics in Section 6, and consider as a baseline on safety-relevant tasks.

8) Gho et al., “From Competition to Coordination: Market Making as a Scalable Framework for Safe and Aligned Multi-Agent LLM Systems,” 2025 — Presents a market mechanism for truth-aligned coordination. Add to Section 2 as an alternative to hierarchical oversight and discuss empirical comparison possibilities.

9) Yin et al., “Towards Scalable Oversight via Partitioned Human Supervision,” 2026 — Provides formal guarantees for scalable supervision via partitioned human expertise; conceptually parallel to HDO’s theoretical framing. Include in Section 5 discussion to contrast guarantees and assumptions.

10) Nguyen et al., “On Controllability in Agentic AI: A Survey,” 2026 — A broader governance/controllability framing that situates hierarchical oversight; cite in Section 8/9 to strengthen the positioning within governance paradigms.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Quantify correlation: Extend Section 5 or Appendix A to include bounds under correlated leaf errors (e.g., via dependency graph assumptions or a correlation coefficient). Show in simulation how correlation affects the e^(-αd) term and practical depth caps.
- Calibrate u(q) and thresholds: Provide a calibration study for uncertainty u(q) and thresholds (τ_acc, τ_rej). An ablation showing performance vs. threshold choices, including miscalibration stress tests, would strengthen Section 4.2.
- Report variance and significance: For Table 1 and Table 2, add per-task or per-domain variance, confidence intervals, and statistical tests. If 50 tasks are used on WebArena, include bootstrapped CIs for success and hallucination; for AgentBench, report per-seed variance and exact sample sizes for lie detection.
- Baseline parity audit: Detail the “Human oversight” proxy and ensure capabilities and budgets are comparable. Consider additional baselines like group-debate and sparse-topology debate. Under matched token budgets, report full accuracy–cost curves with error bars and include the actual plot corresponding to Figure 2 in the paper body.
- Collusion evaluation: Increase the number of collusion trials, describe the steganography construction protocol, and report precision/recall, not just detection fraction. Include ablations that disable randomized routing and verifier diversity to isolate their contributions.

Criteria that could raise my score:
- Inclusion of full plots (currently only described) with CIs for efficiency frontiers, and statistically grounded comparisons on WebArena and AgentBench with clear labeling protocols.
- A correlation-aware theoretical bound or empirical calibration connecting ε, η to real verifier performance.
- Reproducible release: code, prompts, seeds, and evaluation scripts sufficient to replicate Tables 1–4 and Figure 2.

Typos/clarifications:
- Page 5, “Efficiency curves: Risk (y, lower is better) vs. tokens (x). HDO dominates flat debate...” — The figure is referenced as “Figure 2,” but the actual plot is not present; ensure inclusion and labeling.
- Page 3, Proposition 1: “non-expansive (R_q^post ≤ R_q^pre)” — define R_q formally earlier and specify conditions for learned aggregators to be isotone.
- Notation: Ensure consistent use of H, T, and d across Sections 4–5 and Appendix A–C to avoid ambiguity between tree depth and policy depth caps.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5 Between Poor and Acceptable: Some central claims are under-supported by current experiments and rely on strong assumptions; more rigorous evaluation and correlation-aware analysis are needed.

## Excitement
3.0 Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there’s time.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The idea and framing are valuable, and the theoretical scaffold is a good start. However, several core empirical claims rely on under-specified protocols, absent variance/significance, and unshared code/prompts. The exponential depth benefit assumes conditions that are not substantiated empirically. With stronger, reproducible experiments, clearer baseline parity, and correlation-aware bounds, this could move toward main-track suitability.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper’s Section 7–8 covers limitations and broader impacts thoughtfully, including overreach risks, centralization, privacy concerns with logging, and distributional harms if verifiers encode bias. Additional suggestions:
- Clarify data governance for audit logs in regulated domains (e.g., redaction, retention windows, DSARs).
- Discuss how appeals and human escalation are triggered when verifier diversity still fails due to shared bias.
- Consider fairness auditing of verifiers themselves, including cross-architecture checks and periodic third-party audits.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
2.5 Reproducible with difficulty: Important details (prompts, seeds, labeling protocols, exact tool stacks) are deferred; variance and significance are missing; figures referenced but not fully included.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.