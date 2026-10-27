# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes execution-trace guided remasking for masked diffusion language models in code generation. After an initial diffusion sampling pass, failing candidates are executed on a held-out “feedback” subset of tests. The method parses exception tracebacks or collects line-level traces to localize failure-relevant source lines, maps these lines to token indices, and remasks only those tokens for a short conditional diffusion repair. On MBPP+, the approach reports pass@1 of 31.22%, outperforming No-Repair and a perturbation-based remasking baseline (CORE). Analyses indicate most failures can be localized by exception or assertion tracing, and that trace-guided repair induces larger, more meaningful edits than global low-confidence remasking.

## Summary Of Strengths
- Clear, well-motivated idea that leverages the distinctive remasking capability of diffusion LMs for targeted repair, using execution diagnostics that developers naturally rely on.
- The pipeline is simple and well-specified: three stages (initial generation, execution-driven localization, targeted conditional repair). Figure 1 provides a coherent end-to-end diagram of the system that makes interfaces and control flow easy to follow.
- Empirical gains on MBPP+ over reasonable baselines. In Table 1, trace-guided repair achieves 31.22% pass@1, improving over No-Repair (19.84%) and CORE (26.98%). The paired McNemar test is reported.
- Useful ablations. Table 2 suggests the location signal dominates token-level selection within that region, and that widening the localization window helps. This offers insight into what matters for diffusion-time repair.
- Diagnostics that substantiate the mechanism: Figure 2 shows most failing programs admit exception- or assertion-based localization rather than resorting to a fallback; Figure 3 shows trace-guided edits are substantially larger (mean token edit distance ≈10) than global low-confidence edits (≈0.95), supporting the claim that semantic localization is essential.

## Summary Of Weaknesses
1) Baseline coverage and fairness
- Missing diffusion-specific inference baselines that are closely related to remasking policy or guided sampling. The paper compares to global low-confidence and CORE, but omits recent masked diffusion decoding and revision methods that also change token selection order/regions (see Missing Related Work). Without these, it is hard to isolate whether benefits come from execution-guided localization versus any stronger remasking policy.
- Compute mismatch. Table 1 shows NFE for the proposed method (294) is more than 2x CORE (136). The text claims “matched or lower compute budgets,” but NFE contradicts this. The gains could partly reflect more repair steps or more repair rounds. A compute-normalized curve (pass@1 vs NFE) is needed.

2) Limited scope of evaluation and weak absolute performance
- Only one diffusion backbone (LLaDA-8B-Base) is evaluated. Given the central claim is about inference-time guidance that should generalize, testing at least one additional diffusion code LM would strengthen conclusions.
- HumanEval+ results remain very low (Table 1: 2.64% pass@1). While the authors attribute this to “low base performance,” the paper does not analyze why the method cannot help more on this benchmark. Understanding failure modes across task difficulty is important for generality claims.

3) Experimental design choices need more justification
- Feedback/evaluation split: 20% of tests are exposed for decision making. The paper does not examine sensitivity to the size of T_fb, nor whether the approach can overfit T_fb yet fail generalization to T_eval. An analysis of pass rates on T_fb vs T_eval per round would help.
- Iteration budget and step counts: The method allows up to R_max = 3 rounds with S = 64 repair steps. Table 2 ablates S only on one seed and one dataset; there is no ablation of the number of rounds or K (max tokens remasked). Results could depend strongly on these limits.

4) Statistics and variability
- While a McNemar test is reported for MBPP+, Table 2 is single-seed and several other findings (e.g., edit distances in Figure 3) are not accompanied by uncertainty estimates or variance across seeds. Given the stochastic nature of diffusion sampling, error bars would be valuable.

5) Incomplete comparison to execution-guided AR methods and code-repair literature
- The paper cites CodeRL, Reflexion, and Self-Debug but does not adapt or compare to a competitive AR execution-guided repair baseline under the same test-time compute. Since the claim is about the importance of semantic localization, AR models with execution-guided edits are a relevant yardstick.
- Several very closely related diffusion code-repair or constraint-guided diffusion works are missing and not discussed (see next section).

6) Methodological details that may affect generality
- Line-to-token mapping is briefly described but could be error-prone in the presence of comments, string literals spanning lines, or different tokenization granularities. Section 3.4 would benefit from a more careful treatment of corner cases; otherwise remasking might miss the true error span.
- The approach depends on Python runtime instrumentation (tracebacks and sys.settrace). It is unclear how well this extends to other languages, or even to Python tasks with heavy I/O, imports, or C-extensions where traces may be incomplete. Section 4.5 mentions coverage but does not evaluate portability.

7) Analysis gaps
- Figure 2 gives coverage for localization types, but there is no breakdown of accuracy conditional on each localization mode. For instance, what is the pass@1 when only exception-based localization is available vs only assertion-based?
- Table 3 reports success rates by error type, but the counts indicate syntax errors dominate. A deeper look at which syntax categories are fixed (e.g., indentation, missing colons, unmatched parentheses) would clarify whether the method mostly fixes surface errors or also addresses deeper semantic issues.

8) Reproducibility and artifacts
- The implementation details are helpful, but the paper does not specify whether the exact feedback/evaluation splits, localization/tracing code, and seeds are released in a way that reproduces Tables 1–3. Given small absolute margins and stochasticity, precise artifacts matter.

9) Interpretation of ablation (Table 2) raises new questions
- “Random selection within the localized region == confidence-based selection” implies token-level heuristics add little once localization is right. This suggests K and window size may be the dominant knobs. A stronger ablation sweeping window sizes, K, and S jointly, preferably with compute-normalized reporting, would make the conclusion more convincing.

Figure- and Table-specific comments:
- Figure 1: The three-stage diagram effectively clarifies how exception-based and assertion-based localization feed into token index selection, then controlled denoising. It supports the claim in Sections 3.3 and 3.4 that the method is modular and iterative. Including NFE contributors per stage in the figure legend would help with compute accounting.
- Table 1: The proposed method’s NFE = 294 is far larger than CORE = 136, while the gain on MBPP+ is +4.24 points. Without a pass@1 vs NFE curve, it is unclear if CORE with similar NFE would close the gap. Please report controlled NFE sweeps or per-round contributions to NFE and accuracy.
- Table 2: The “Wide Window (±5)” configuration outperforms “Full Method,” indicating window size is critical. Yet this is single-seed and conflicts with the default choice of ±1 elsewhere. Please justify the default or change it based on this observed benefit.
- Figure 2: The distribution corroborates that exceptions and assertion traces cover most cases. However, the y-axis aggregates across problems, not failures only. Clarifying whether percentages are over all prompts or only failing ones per round would avoid ambiguity.
- Figure 3: The stark difference in edit distances underpins a central claim, but there are no variance bars or per-problem scatter. Some zero-edit cases under trace-guided imply the remasking failed to trigger actual changes; analyzing why would be instructive.

## Potentially Missing Related Work
1) Qi et al., “Cluster-Level Attention-Guided Parallel Decoding for Masked Diffusion Language Models,” 2026 — Presents a decoding strategy for masked diffusion that improves efficiency and quality on reasoning/code tasks. Should be discussed as an alternative inference-time policy in Section 2 and compared in Section 4 as another way to alter remasking/unmasking behavior.

2) Peng et al., “Path Planning for Masked Diffusion Model Sampling,” 2025 — Optimizes token unmasking order and shows gains on language/code generation. Add to Related Work (Section 2) and consider as a baseline or discussion point in Section 4 for policy-level improvements vs execution-guided localization.

3) Meshchaninov et al., “Guided Star-Shaped Masked Diffusion,” 2026 — Proposes a learnable remasking module to selectively revise likely erroneous tokens, including code. Directly relevant to token selection; should be cited in Section 2 and, if feasible, included as a baseline or discussed alongside CORE in Section 4.

4) Lavon et al., “Execution Guided Line-by-Line Code Generation,” 2025 — Uses execution signals with classifier-free guidance in AR models. Though AR, it addresses closely related execution-guided repair; discuss in Section 2 and contrast to your runtime-guided diffusion in Section 3.3.

5) Shao et al., “Constrained Code Generation with Discrete Diffusion,” 2026 — Explores semantic/syntactic constraints in diffusion decoding. Compare in Section 2/4 as an alternative to dynamic execution guidance.

6) Singh et al., “Diffusion is a code repair operator and generator,” 2025 — Explicitly studies diffusion as a repair operator for programs. Highly relevant; discuss in Section 2 and consider replicating a subset of their repair baselines to contextualize your targeted remasking.

7) Fan et al., “Stable-DiffCoder: Pushing the Frontier of Code Diffusion Large Language Model,” 2026 — A strong diffusion backbone for code. Evaluate your inference method on a second backbone or discuss transferability in Section 4.1/5.

8) Jiao et al., “DiffBench Meets DiffAgent: End-to-End LLM-Driven Diffusion Acceleration Code Generation,” 2026 — Focuses on diffusion-time efficiency. Include in Section 2 and consider NFE-normalized comparisons.

9) Ni et al., “NExT: Teaching Large Language Models to Reason about Code Execution,” 2024 — Execution-trace–centric training improves repair. Contrast your inference-only approach in Sections 2 and 5, and discuss potential synergy.

10) Zhu et al., “CodeDiffuSe: A masked diffusion framework for structure-aware code completion and repair,” 2025 — Combines AST-guided masking and error-aware remasking for repair. Very close to your problem; should be discussed and, if possible, included as a baseline or ablation in Section 4.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Compute normalization: Please provide pass@1 versus NFE curves for all methods, and a version of Table 1 at matched NFE (e.g., cap each method to 294 and to 136). Also break down NFE contributions per stage/round (generation, localization, each repair round).
- Robustness to T_fb size and overfitting: Report performance as T_fb varies (e.g., 10%, 20%, 40%), and show per-round pass rates on T_fb vs T_eval to check for overfitting to feedback tests.
- Broader baselines: Add at least one of the closely related diffusion decoding/repair methods listed above, and an execution-guided AR repair baseline under the same compute budget. If full implementations are not feasible, provide reasoned approximations or ablations (e.g., AR+trace replace-at-lines).
- Hyperparameter sweeps: Extend Table 2 to include K (max tokens), R_max (rounds), and window size across multiple seeds, ideally with confidence intervals. Given “Random Selection == Confidence-based,” probe whether K and window size alone explain gains.
- Failure analyses: Expand Table 3 with finer-grained categories for syntax and runtime errors, and give representative qualitative before/after code snippets per error type to demonstrate non-trivial semantic fixes.

Typos and minor issues:
- Page 5, “We compare against four baselines…” then lists four, but bullets are formatted inconsistently (one line starts with “- •”). Standardize bullet formatting.
- Section 4.2 “matched or lower compute budgets” conflicts with Table 1 NFE; please correct the claim or add clarifications.
- Section 4.3 “Best-of-2 performs worse than no repair,” but NFE differs; clarify that this comparison is not compute-normalized.
- Page 3, 3.3: “default M = 20.” Later in Appendix A the same M = 20 is used; consider cross-ref to avoid duplication.
- Ensure all symbols are defined at first use (e.g., L for sequence length appears in Appendix but also earlier; define once in Section 3.1).

Criteria to raise my score:
- Add compute-normalized comparisons and at least one additional strong diffusion inference baseline; show gains persist at equal NFE.
- Provide results on a second diffusion code model and strengthen seed variance reporting.
- Include analyses on T_fb sensitivity and per-round generalization to T_eval.
- Expand error-type and qualitative analyses to demonstrate semantic rather than mostly syntactic fixes.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
2.5 Between potentially interesting and interesting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The idea is clean and the analyses around Figures 1–3 and Tables 1–3 are informative. However, compute-normalized comparisons are missing, baseline coverage is narrow given recent diffusion-time decoding/repair works, and several experimental choices are underexplored (feedback split sensitivity, rounds/steps/K, seed variance). With these addressed, this could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not provide a dedicated limitations or impact section. Key points to discuss:
- Generality: The approach relies on Python exceptions and line tracing; portability to other languages or to sandboxed environments with restricted tracing is uncertain.
- Security and safety: Executing model-generated code is risky. Clarify sandboxing, resource limits, filesystem/network isolation, and mitigations against malicious or non-terminating programs.
- Bias and domain coverage: MBPP+/HumanEval+ focus on Python functions; results may not transfer to multi-file projects, other languages, or broader software engineering tasks.
- Environmental impact: Iterative execution and repair increase compute; discuss NFE-cost tradeoffs and techniques to reduce runtime (e.g., early stopping, selective test execution).
Including these considerations would strengthen the paper.

## Ethical concerns
Executing untrusted generated code poses risks. The paper should explicitly describe the sandboxing and isolation procedures beyond timeouts (e.g., process/container isolation, disabled network, limited syscalls). None of the other typical Responsible NLP risks appear acute here.

## Needs Ethics Review
No

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.

## Datasets
1 No usable datasets submitted.

## Software
4 Useful.: I would recommend the new software to other researchers or developers for their ongoing work.