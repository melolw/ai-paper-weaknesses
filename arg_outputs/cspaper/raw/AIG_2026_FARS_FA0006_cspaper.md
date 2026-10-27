# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes a training-free framework for robustly judging web-agent trajectories in the presence of adversarial chain-of-thought (CoT) rewrites. The method runs a base LLM judge on two counterfactual input views of the same trajectory: View1 includes the agent’s CoT and View2 excludes it. If the two judgments disagree, the case escalates to a strict, evidence-anchored rubric that ignores CoT and requires explicit evidence citation. On AgentRewardBench, the method reports lower attack sensitivity (Δ-FPR), competitive F1, and the highest recall relative to simple baselines. The authors also show that View1–View2 disagreement is enriched under CoT attacks, supporting their mechanism hypothesis.

## Summary Of Strengths
- Clear problem framing around CoT manipulation of trajectory judges and a simple, intuitive selective-escalation design. The counterfactual-view idea is easy to implement and model-agnostic.
- Empirical results on AgentRewardBench are presented with clear metrics (precision/recall/F1, FPR under unmodified vs attacked failures, and Δ-FPR). In Table 1, the proposed method attains the best recall (77.63%) and substantially reduces Δ-FPR to 4.31% compared to 11.71% for the standard CoT-using judge.
- The mechanistic story is explicitly tested: Figure 2 shows disagreement enrichment on attacked failures (16.4%) vs unmodified failures (7.6%), supporting the claim that CoT-only attacks differentially perturb the CoT-dependent view.
- The ablation in Table 2 is helpful: matched-rate random escalation does not reduce Δ-FPR, and a matched-cost control degrades F1, suggesting the specific disagreement trigger, not just extra calls or escalation per se, drives the improvement.
- Figure 1 is a strong architectural diagram. It clearly explains input composition for the two views, Stage 1 dual judging, the branching condition y1 ≠ y2, and the Stage 2 strict rubric. This helps readers reimplement the pipeline.

## Summary Of Weaknesses
1) Incomplete baseline coverage and limited stress testing
- Only simple baselines are considered (View1-only, View2-only, Strict-always, Random Escalation). The paper cites stronger related ideas (e.g., RULERS; Trust-or-Escalate), yet does not compare to them, which weakens the empirical positioning. Without comparisons to competitive robustness-oriented judge methods or ensembles, it is difficult to assess relative merit.
- The attack space is narrow. All conclusions are drawn from a single “Progress Fabrication” CoT attack on failures. Broader manipulations that do not rely on CoT content (e.g., framing/context attacks) or different CoT perturbations could undermine the method’s central assumption that View2 remains stable while View1 shifts. This limits external validity.

2) Ambiguity in mechanistic evidence
- Figure 2 shows that unmodified successes have an even higher disagreement rate (18.0%) than attacked failures (16.4%). This undermines the narrative that disagreement is a targeted signal of attack-induced unreliability. The paper should reconcile this with the mechanistic claim, for example by conditioning on class or analyzing disagreement’s predictive value for false positives specifically.
- No statistical significance or uncertainty is reported for the disagreement enrichment or for Table 1 metrics. Confidence intervals or random-seed variance would clarify robustness of the reported effects.

3) Evaluation design choices that may bias conclusions
- Δ-FPR focuses solely on failures under attack, which is appropriate for failure-targeted attacks, but the method’s cost or degradation on success cases under various conditions is not shown beyond aggregate precision/recall. An “attack-on-success” setting or at least additional breakdowns would strengthen claims that the method preserves utility where CoT is helpful.
- Table 1 is silent on calibration or abstention behavior. Since the system selectively escalates, metrics like escalation rate per class, conditional precision/recall on escalated vs non-escalated subsets, and a cost–performance frontier would improve interpretability of the trade-offs.

4) Reproducibility gaps and missing details
- The strict rubric P_strict is not presented in enough detail to reproduce results. The paper describes properties (evidence citation, checklist) but does not include the exact rubric/prompt or examples of “machine-parseable judgment with evidence justification.” Without this, reproducing Δ-FPR and recall improvements is difficult.
- The base prompt P_base is only described as following “AgentRewardBench simplified-judge format”; the exact wording is absent. While code availability is noted, the main paper needs enough detail to stand on its own for ARR assessment.

5) Single judge model and decoding setup
- All results use only Llama-3.3-70B-Instruct at temperature 0. The approach’s stability across model families, sizes, and decoding strategies is untested. Since the key signal is inter-view disagreement, findings could shift across judges with different CoT sensitivities.
- Relatedly, the “matched-cost control” ablation using two View2 calls at different temperatures conflates variability from sampling with the core counterfactual-view rationale. More principled controls, such as two independently-initialized models or two prompts that are both CoT-agnostic but evidence-anchored, would better isolate the mechanism.

6) Cost and practical utility analysis is shallow
- The paper states an average of 2.1× calls per trajectory but does not translate this into wall-clock or dollar cost nor show how to adjust the escalation threshold to trade off cost with Δ-FPR and F1. For deployment, practitioners need a cost–benefit curve and guidance on selecting operating points.

7) Claims occasionally overreach relative to evidence
- The conclusion emphasizes a 63% relative reduction in attack sensitivity “while maintaining competitive accuracy,” yet F1 decreases (72.13 vs 72.93 for View1-only). This trade-off is small but should be presented cautiously and accompanied by statistical tests.

8) Results communication details that reduce clarity
- Table 1 has a “Best/Second-best” styling note; however, “best recall” corresponds to the proposed method, and “best precision” and “best F1” are with View1-only. Discussing practical implications of different operating points would improve clarity.
- Equation (1) captures the decision rule but does not define y_strict explicitly in-symbol beyond prose. A short formal definition would improve precision.

9) Figure-specific critique
- Figure 1 is helpful, but the “Legend” colors overlap visually with the stage colors, which makes it slightly difficult to read the two branches in grayscale printing. Minor, but important for accessibility.
- Figure 2 would benefit from error bars and per-class conditional breakdowns (e.g., disagreement -> FP on attacked failures) to strengthen the mechanistic link.

10) Table-specific critique
- Table 2’s “Matched-Cost Control” is underspecified: “two View2 calls at different temperatures” does not clarify sampling details or whether the final decision is by agreement, majority, or escalation. The validation comments (“×” marks) are qualitative. Please quantify why it fails the goal, e.g., by showing which metric materially underperforms on which subset.

## Potentially Missing Related Work
1) Zhao et al., One Token to Fool LLM-as-a-Judge, 2025 — Studies targeted “master key” tokens that manipulate judges. Highly relevant as an alternative, non-CoT attack vector. Should be discussed in Section 2 and added as a stress test in Section 4 to probe whether view disagreement remains a useful trigger against token-level attacks.

2) Gupta et al., Context Over Content: Exposing Evaluation Faking in Automated Judges, 2026 — Shows that contextual framing can bias judges even with identical content. Discuss in Section 2 and consider as an additional attack in Section 4, contrasting with CoT-specific attacks and evaluating whether disagreement rises when only framing changes.

3) Wang et al., Time to REFLECT: Can We Trust LLM Judges for Evidence-based Research Agents?, 2026 — Offers a benchmark and taxonomy of judge failures for multi-step agents. Discuss in Related Work and consider cross-benchmarking or at least mapping your strict rubric to their failure modes in Section 4.

4) Jiang et al., Misaligning Reasoning with Answers — MATCHA, 2025 — Systematically misaligns reasoning and outputs to test CoT robustness. Directly relevant to your CoT-perturbation hypothesis; cite in Section 2 and compare your manipulation and detection mechanisms in Section 3.2–3.3.

5) Flynt et al., GroundEval: A Deterministic Replacement for LLM-as-Judge in Stateful Agent Evaluation, 2026 — Presents a non-LLM deterministic alternative targeted at evidence-grounding. Include in Section 2 and as a conceptual baseline in Section 4 (even if not fully comparable) to situate the strict rubric choice.

6) Gu et al., A Survey on LLM-as-a-Judge, 2024 — Broad survey to situate your approach among reliability/robustness strategies; add to Section 2.

7) Dietz et al., Principles and Guidelines for the Use of LLM Judges, 2025 — Offers practical guardrails and risk analysis; could strengthen Section 1 motivation and Section 5 limitations by aligning your escalation policy with recommended principles.

8) Yamauchi et al., An Empirical Study of LLM-as-a-Judge: How Design Choices Impact Evaluation Reliability, 2026 — Directly analyzes how CoT and prompting affect reliability; include in Section 2 and reference when motivating your two-view setup in Section 3.2.

9) Piergentili et al., An LLM-as-a-judge Approach for Scalable Gender-Neutral Translation Evaluation, 2025 — Demonstrates benefits and pitfalls of intermediate analytical steps; discuss in Section 2 as an example of domain-specific evidence-anchoring where your strict rubric might transfer.

10) Badshah et al., Reference-Guided Verdict: LLMs-as-Judges in Automatic Evaluation of Free-Form QA, 2025 — Ensemble/reference-conditioned judges; discuss in Section 2 and consider as an alternative multi-judge baseline style in Section 4.

## Comments Suggestions And Typos
Actionable suggestions for rebuttal and camera-ready:
- Report full prompts. Include the exact P_base and P_strict prompts in the main paper or an appendix pointer, plus 2–3 worked examples showing the evidence-anchored checklist and machine-parseable outputs. Without these, the work is hard to reproduce.
- Add competitive baselines and stress tests. Implement at least one evidence-anchored robust judge (e.g., RULERS-style rubric), a Trust-or-Escalate variant, and an ensemble/reference-guided verdict baseline. Add additional attacks: token-level “master key,” framing/context manipulation, and at least one alternative CoT attack (e.g., hallucinated subgoals). Show whether disagreement remains enriched.
- Clarify Figure 2’s finding that unmodified successes have higher disagreement than attacked failures. Provide conditional analyses: among attacked failures, what fraction of disagreements correspond to false positives by View1? Report precision/recall conditioned on disagreement to prove it is a good escalation trigger for what you care about.
- Strengthen statistical reporting. Provide confidence intervals or bootstrap ranges for Table 1 metrics; include significance tests for Δ-FPR reductions and for the disagreement enrichment in Figure 2.
- Cost–performance frontier. Report wall-clock and monetary cost versus F1/recall/Δ-FPR as the escalation trigger is tuned (e.g., use soft signals like confidence margins, rubric scores) to help practitioners pick operating points. Break down escalation rates per class and per environment.
- Multi-judge robustness. Evaluate across at least one additional closed- or open-weight model, and a second decoding setting. Show whether disagreement rates and robustness improvements persist.

Minor issues and typos:
- “AgentReward-Bench” vs “AgentRewardBench” appears inconsistently (e.g., Abstract vs Section 4.1). Standardize.
- Reference formatting is inconsistent in years and capitalization; double-check venue info where available.
- In Equation (1), define y_strict explicitly as the prediction of P_strict; currently implied by prose.
- Figure 1 legend colors are close; consider pattern or shape coding for accessibility.
- Clarify “Matched-Cost Control” procedure in Table 2: how is the final decision formed from two View2 calls?

Criteria that could increase my score:
- Inclusion of missing baselines and broader attacks with statistically supported improvements.
- Full prompt details and ablations that demonstrate portability across models.
- A clear reconciliation of the high disagreement on unmodified successes with the mechanism narrative.

## Confidence
3.5 Quite sure after careful checking: I checked the main claims, figures, and tables in detail, though broader literature positioning and extra experiments would further solidify conclusions.

## Soundness
3.0 Acceptable: The two-view escalation idea is reasonable and the empirical results support reduced Δ-FPR with small F1 trade-offs, but baseline coverage, attack diversity, and statistical analysis are limited.

## Excitement
2.5 Between potentially interesting and interesting: Practical and neat idea with plausible utility, but the present scope and analysis are not yet compelling enough for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is simple and promising, with clear gains in Δ-FPR and recall on one benchmark and one attack, and the mechanism is illustrated well in Figure 1 and partially validated in Figure 2. However, the evaluation is too narrow, missing several directly relevant baselines and broader attack stress tests; Figure 2’s higher disagreement on unmodified successes complicates the mechanistic story; and reproducibility details for the strict rubric are insufficient. With fuller baselines, diverse attacks, statistical reporting, and prompts, this could reach solid Findings.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The method increases inference cost and could still be vulnerable to non-CoT manipulations (e.g., prompt framing, position/verbosity biases) that affect both views similarly. If used for reward modeling or training data curation, residual false positives could amplify reward hacking or label noise. The paper briefly notes cost but does not analyze resource implications or environmental impact. Authors should expand on dual-use risks, fairness impacts across websites and languages, and failure modes where escalation misfires (e.g., when evidence is ambiguous or incomplete). Discuss safeguards if this is deployed to judge human work products.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.0 Reproducible with difficulty: Core setup is described, but missing exact prompts and strict rubric details impede faithful reproduction. Reported code availability helps, but the paper itself should be sufficient.

## Datasets
1.0 No usable datasets submitted.

## Software
3.0 Potentially useful.: If the implementation is released as stated, others could try the approach; however, the lack of in-paper prompt/rubric specifics currently limits plug-and-play reuse.