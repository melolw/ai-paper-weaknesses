# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper introduces Execution-Signature Recycling (ESR), a training-free, two-round test-time scaling method for LLM code generation. ESR clusters initial candidate programs by their execution signatures, defined as the set of failing unit tests paired with error types (Equation 1), and builds a deduplicated “failure bank” that conditions subsequent generations. Experiments on HumanEval+ using Qwen2.5-Coder-7B-Instruct with a fixed 16-generation budget compare ESR to Best-of-16 and a Self-Debug baseline. ESR attains the highest mean Pass@1 (87.60%) but does not significantly outperform Self-Debug (86.99%), with a 95% paired bootstrap CI for the difference that includes zero. The authors frame this as a negative result, suggesting simple per-sample self-debugging may be sufficient for strong code models on HumanEval+.

## Summary Of Strengths
- Clear, focused problem framing and method description. The notion of an execution signature as a deterministic, unit-test-grounded descriptor (Equation 1) is simple and intuitive.
- The two-round pipeline is well communicated. Figure 1 usefully illustrates the exploration, signature clustering, failure bank construction, and exploitation steps, making the procedure easy to follow.
- The evaluation protocol is stated cleanly, with fixed compute budgets, multiple seeds, and paired bootstrap confidence intervals. Reporting that ESR does not significantly beat Self-Debug is transparent and valuable as a negative result.
- Tables are informative. Table 1 summarizes per-seed and mean performance with deltas and significance; Table 2 provides diagnostic statistics about when ESR can act, which grounds the interpretation of limited benefits.
- The paper is tidy and readable, with a conventional structure and connections to relevant areas like self-debugging, test-time scaling, and experience recycling.

## Summary Of Weaknesses
1) External validity and breadth of evaluation are limited.
- Single model and single benchmark. Results are reported only for Qwen2.5-Coder-7B-Instruct on HumanEval+. Without additional code benchmarks (e.g., MBPP, LiveCodeBench already cited in the text but not used) or model families/sizes, it is hard to generalize the conclusion that cross-sample aggregation “does not provide reliable additional benefits.”
- The negative result may be specific to this setting. A stronger or weaker model, harder tests, or different programming languages might change the result. As written, the broader claim is under-supported.

2) Baseline coverage is narrow for the stated research question.
- Only Best-of-16 and a single-step Self-Debug are included. The paper mentions related iterative or memory-based methods (e.g., Reflexion, Self-Refine), but there is no empirical comparison. Likewise, no comparison to more global test-time compute allocation or coordination strategies that are conceptually adjacent to ESR’s cross-sample aggregation.

3) The self-debug baseline configuration and budget fairness are under-specified.
- It is not clear whether token budgets for feedback context are strictly matched across methods. ESR uses a 900-token cap for the failure bank; Self-Debug uses per-sample traces for up to 3 failing tests. The paper should quantify average feedback tokens in Round 2 for both methods, since additional feedback tokens can act as extra compute. This goes to the heart of whether the comparison is fair and whether ESR’s instability is related to prompt-length variability.

4) The design space is only partially explored.
- ESR fixes N=16, split 8/8, with M=3 clusters and K=2 examples each, but there is no ablation on these choices or on the maximum token budget. The lack of analysis on how M, K, or the round split affect performance makes it difficult to judge whether the core idea is limited, or the particular hyperparameterization is simply not effective under the tested conditions.
- Similarly, the signature definition is strict equality over (test_id, error_type), which ignores useful structure such as value-diff summaries in assertion messages, stack-frame localization, or parametric bucketing of exceptions. An ablation on richer signatures could clarify whether the negative result stems from an overly coarse representation.

5) The statistics in Table 2 raise questions about the setting and practical utility.
- Table 2 indicates about 68% of tasks have all 8 Round 1 candidates passing all base tests, creating empty failure banks. That leaves ESR inert on a large majority of problems, and it also implies that base-test selection is fairly easy for the chosen model. This observation should be reconciled with Table 1 gains by seed and with a discussion of base versus augmented tests. It would help to show how often the Round 1 “all-pass” candidates fail augmented tests, since ESR’s promise is mostly relevant when base tests under-specify correctness.

6) Lack of runtime and cost analysis.
- ESR adds a failure-bank construction and prompt-augmentation stage. While not obviously heavy, it is still extra overhead. The paper does not report wall-clock, execution counts, or token usage per method. In test-time scaling papers, compute accounting is important for fair comparison and for understanding the stability issues the authors observe.

7) Claims overgeneralize beyond the provided evidence.
- The conclusion suggests that per-sample self-debugging is sufficient for strong models and that cross-sample aggregation does not reliably help. Given the limited diversity of models and datasets, this statement should be narrowed or conditioned. As-is, it may mislead readers into dismissing cross-sample aggregation too broadly.

8) Missing or lightly treated baselines that are very close conceptually.
- Methods that coordinate multiple reasoning or verification trajectories at test time, or that allocate compute adaptively across attempts, are plausible alternatives to ESR. Not including these as baselines weakens the positioning of ESR as a general inference-time aggregation paradigm.

9) Figure- and table-linked concerns that touch core claims.
- Figure 1: While it effectively communicates the pipeline, it also reveals a strong assumption baked into ESR, namely that top-M frequent signatures are the most useful. The paper does not test whether selecting rare but informative failures in the bank might be better, nor does it show per-task bank contents to verify that frequent signatures are not dominated by trivial or already-addressed issues.
- Table 1: The inter-seed variability for ESR (std=1.27) is almost double Best-of-16 and notably higher than Self-Debug. This undermines reliability, which is central for a test-time scaling method that purports to organize feedback more intelligently. The paper acknowledges this but does not probe causes.
- Table 2: The heavy skew toward empty banks implies ESR’s cross-sample machinery is simply not engaged most of the time. The method’s benefit window is therefore small under the tested conditions, which directly weakens the practical significance of the approach.

10) Reproducibility details are still sparse in the main text.
- While a code link is provided, the paper does not include prompts, the exact serialization format of the failure bank, timeout thresholds, or treatment of flaky tests in the main body. For ARR main track standards, more detail in the paper itself would strengthen reproducibility without relying on external material.

## Potentially Missing Related Work
1) Hu et al., “PaCoRe: Learning to Scale Test-Time Compute with Parallel Coordinated Reasoning,” 2026 — Addresses coordinated parallel reasoning and allocation of inference-time compute, closely related to ESR’s goal of aggregating information across candidates. Should be discussed in Related Work as an alternative test-time scaling paradigm and, if feasible, compared in Experiments.

2) Lifshitz et al., “Multi-Agent Verification: Scaling Test-Time Compute with Multiple Verifiers,” 2025 — Scales computation through multiple coordinated verifiers. Relevant to ESR’s use of execution-derived signals for selection and improvement. Add to Related Work and discuss differences in how feedback is aggregated.

3) Montgomery et al., “Budget-aware Test-time Scaling via Discriminative Verification,” 2025 — Studies compute allocation under strict budgets via discriminative verifiers. This is pertinent to ESR’s fixed-budget setting and the need to balance feedback tokens versus samples. Cite in Related Work and briefly position ESR’s design choices relative to budget-aware alternatives.

4) Wan et al., “Inference-Time Scaling of Verification: Self-Evolving Deep Research Agents via Test-Time Rubric-Guided Verification,” 2026 — Iterative verification and refinement with rubric-guided feedback. Conceptually akin to ESR’s feedback reuse across attempts; should be cited in Related Work and possibly discussed alongside Reflexion/Self-Refine.

5) Cui et al., “Adaptive Test-Time Reasoning via Reward-Guided Dual-Phase Search,” 2025 — Proposes a two-phase search with adaptive budget allocation; directly analogous to ESR’s two-round procedure. Discuss in Related Work and consider as an alternative baseline or ablation framing.

6) Wang et al., “MCTS-Judge: Test-Time Scaling in LLM-as-a-Judge for Code Correctness Evaluation,” 2025 — Exploits unit-test-level rewards via search in code evaluation. A suitable comparator for structuring test-time exploration with execution signals. Add to Related Work and consider as a complementary baseline or discussion point.

7) Hu et al., “Test-Time Learning for Large Language Models,” 2025 — Presents on-the-fly adaptation during inference as an alternative to training-free scaling. Cite in Related Work to clarify where ESR sits relative to methods that update model parameters at test time and to inspire possible hybrids.

## Comments Suggestions And Typos
Actionable suggestions and questions:
- Add breadth: Evaluate on at least one additional benchmark beyond HumanEval+, ideally LiveCodeBench or MBPP, and include at least one other model family/size. This would ground the negative result and limit overgeneralization.
- Strengthen baselines: Include or discuss stronger test-time coordination baselines (e.g., Reflexion, Self-Refine) and, if feasible, a representative coordinated reasoning method. Even a light-weight instantiation would help contextualize ESR’s contribution.
- Budget fairness and compute accounting: Report token usage per method and round, average failure-bank length, number of executed tests, and wall-clock cost. Clarify whether Self-Debug’s context length is comparable to ESR’s 900-token cap and how often caps are hit.
- Ablations: Vary M, K, and the exploration–exploitation split; experiment with alternative signature definitions that incorporate value diffs or partial unification of tracebacks. Also test including low-frequency but diverse failures in the bank to check the “top-M by frequency” heuristic.
- Engage with Tables and Figure explicitly: For Table 2’s high All-Pass rate, report how often these Round 1 all-pass candidates fail the augmented tests to justify whether ESR’s feedback would help if Round 1 were more challenging. For Figure 1’s bank construction, add a qualitative table or appendix excerpt of typical bank entries to validate that frequent signatures capture meaningful failure modes.
- Narrow the claims: Reframe conclusions to be conditional on the tested setting. Emphasize that the negative result may be due to the limited activation window (Table 2) and the strict signature design rather than an inherent limitation of cross-sample aggregation.
- Reproducibility: Include in-paper details of prompts, serialization formats, timeout and error handling, and deterministic seeds. A short hyperparameter table would help.

Typos and minor issues:
- Page 1: The CI is given in the Abstract as “[-0.81, 2.24]” but later as “[−0.81, 2.24]” with different dash glyphs. Standardize punctuation.
- Page 1: Footnote marker formatting “¹https://...” is a bit cramped; consider moving the URL into a formal Code Availability statement.
- Page 2: “inspired by recent work on experience recycling for test-time scaling (Wang et al., 2026)” would benefit from briefly clarifying the domain difference if that work is on math rather than code.
- Ensure consistent capitalization of “Self-Debug” across the paper.
- Table captions: add units where possible (Pass@1 in percent).

Criteria that could increase my score:
- A broader evaluation suite plus at least one additional model.
- Clear compute accounting with matched token budgets and added baselines.
- Ablations on M/K/splits and on alternative signature definitions, plus analysis connecting Table 2 to augmented-test failures.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: The methodology is simple and appears correctly implemented, results are clearly reported with CIs, but the evaluation breadth and design-space exploration are limited.

## Excitement
2.0 Potentially Interesting: Negative results on test-time scaling are useful, but scope and baseline coverage are limited.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The work is clearly written and methodologically clean, and the negative result is reported transparently with appropriate statistics. However, the evaluation is too narrow, the design space is underexplored, and baselines are limited for the paper’s claim about cross-sample aggregation. With broader experiments, ablations, stronger baselines, and compute accounting, this could be elevated to a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper appropriately positions itself as a negative result on a standard code-generation benchmark. Societal risks are minimal, although any method that improves automated coding can have dual-use implications, such as accelerating generation of buggy or insecure code if verification is weak. The paper could add a brief note on failure modes, including the risk that banked feedback might bias the model toward overfitting to base tests rather than general correctness. There is also an equity consideration in evaluating only Python tasks; broader language coverage would increase inclusivity.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The protocol and hyperparameters are mostly stated, and code is reportedly available. Including prompts and exact serialization details in the paper would further improve this.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: Someone might find the new software useful for their work.