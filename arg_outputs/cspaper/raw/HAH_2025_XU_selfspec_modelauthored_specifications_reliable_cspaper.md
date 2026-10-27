# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes Self-Spec, a prompt-based orchestration for LLM code generation in which the model first invents its own compact specification schema, instantiates a task-specific spec from a problem’s docstring and signature, resolves ambiguities via a brief Q&A loop, and then generates code strictly from the confirmed spec under deterministic decoding (T=0). The motivation is that a model-authored spec better matches the model’s internal representational biases than either raw NL or rigid human-designed formal IRs. On HumanEval (pass@1, single sample), the method shows gains for GPT-4o (87%→92%) and Claude 3.7 (92%→94%), with a slight dip for Claude 3.5 (90%→89%) attributed to over-defensive guards. The paper includes an orchestration diagram, prompts, and qualitative error analysis.

## Summary Of Strengths
- Clear and concrete proposal: The paper articulates a simple, deterministic pipeline that is easy to implement and reason about. The roles, prompts, and gating logic are described with enough detail to be replicated.
- Useful middle ground between free-form reasoning and rigid IRs: The framing that a model-authored spec can align with a model’s distributional preferences is sensible and practically attractive for single-sample reliability.
- Deterministic evaluation reduces variance: Using T=0 and pass@1 avoids confounds from sampling variance, making observed deltas in Table 1 attributable to orchestration rather than decoding.
- Empirical uplift for strong models: Table 1 shows non-trivial improvements on HumanEval for GPT-4o (+5 points) and Claude 3.7 (+2 points), suggesting the approach can matter in practice.
- Insightful qualitative error analysis: Tables 2 and 3 surface recurring failure categories and model-specific tendencies that are actionable targets for future spec-level checks.
- Figure-ground clarity: Figure 1 gives a clean overview of the loop, especially the FMInterviewer–SpecApplier cycle and the explicit CONFIRM gate, which supports the claim about “confirmable” structure before code.
- Reproducibility posture: The paper states that prompts, scripts, model IDs, and harness configuration are released, aiding independent verification.

## Summary Of Weaknesses
1) Evaluation scope is too narrow for ACL main-track standards. Results are only on HumanEval, a small and highly saturated benchmark. No complementary datasets (e.g., MBPP, APPS subsets, SWE-bench lite) or robustness tests are provided. This limits claims about general utility in broader NL→code settings.

2) Limited and potentially confounded comparisons. The paper contrasts only with a Native baseline and cites a Dafny pipeline from another venue. It does not compare against other lightweight intermediates (e.g., PAL/PoT execution scaffolds, self-debug loops, structured CoT checklists) under the same decoding regime. Without these, it is hard to isolate what Self-Spec uniquely provides beyond “any” structured intermediate.

3) Attribution of gains to “model-authored” spec is untested. The central hypothesis is distributional alignment from model-invented schemas, but no ablation tests simple alternatives:
   - fixed human-authored schema vs model-authored schema,
   - free-form CoT checklist vs constrained spec,
   - differing amounts of Q&A, or removing the CONFIRM gate.
   This gap undermines the causal narrative that “self-designed schema” is the key driver.

4) Use of a second LLM as a simulated user introduces a hidden advantage. The FMInterviewer’s questions are answered by another LLM, not a human, which may lead to cleaner, more internally consistent specs than typical users would produce. There is no reporting of the number of questions asked, failure-to-confirm rates, or sensitivity to inconsistent answers. This weakens the external validity of the results for “vibe programming” use cases.

5) Cost and latency are not quantified. The paper argues the loop is “lightweight,” but does not report token counts, number of FMInterviewer turns, or wall-clock overhead. Without cost/latency data, practitioners cannot judge trade-offs versus single-shot or other two-stage methods.

6) Statistical uncertainty and sensitivity. With T=0, single-sample pass@1 is clean but does not report confidence intervals or sensitivity to minor prompt changes. Given deltas are small for Claude 3.7 (+2) and negative for Claude 3.5 (−1), a robustness check across slight prompt variants would increase confidence.

7) Weaknesses in the error-analysis methodology. Table 3 notes “potential regressions; baseline not provided,” making it hard to know whether those failures are introduced by Self-Spec or already present in Native. The qualitative taxonomy is useful but partially speculative without paired baseline logs for the same tasks.

8) Overclaims on novelty relative to emerging spec/DSL lines. The paper positions itself as the “first systematic study that lets an LLM design its own spec language,” but it does not engage with several close, recent works on DSLs or requirement alignment that would temper this claim and clarify where Self-Spec truly differs.

9) Limited discussion of failure on smaller models. The Claude 3.5 regression is attributed to “over-defensive guards,” and a heuristic removing guards is suggested post hoc. However, there is no quantitative re-run with the proposed guard stripping to substantiate the “returns to baseline” statement, and no preventive spec-level mitigation evaluated in the main results.

10) Figure- and table-specific concerns:
   - Figure 1: While the pipeline is clear, the figure leaves unspecified the average number of Q&A cycles to reach CONFIRM, the criteria for “fewest decisive questions,” and how often the loop backtracks. These omissions make it hard to evaluate claims of determinism plus practicality at scale.
   - Table 1: The absolute gains are modest and concentrated in stronger models, and there is no comparison to alternative structured prompts under identical conditions.
   - Tables 2–3: Helpful categorization, but the lack of cross-referencing to Native failure logs undercuts conclusions about new or mitigated error modes.

Why these matter: Together, these issues limit both the strength of the causal claims and the generality of the findings. Without broader evaluation, ablations, and comparative baselines, it is difficult to argue that “model-authored specs” are the primary mechanism behind the observed improvements, or that the approach scales favorably in realistic, noisy human-in-the-loop settings.

## Potentially Missing Related Work
1) Al Mazrouei et al., “Anka: A Domain-Specific Language for Reliable LLM Code Generation,” 2025 — Introduces a purpose-built DSL to constrain code generation for reliability. Directly relevant to the claim that model-authored specs are a preferable middle path. Should be discussed in Section 2 (contrast with fixed human-designed DSLs) and cited in Section 7 when arguing model-agnostic generality.

2) Tian et al., “Aligning Requirement for Large Language Model’s Code Generation,” 2025 — Proposes Specine for requirement alignment to improve pass@1. This is squarely related to the “spec-first” idea and should be compared in Section 2 and potentially added as a conceptual baseline in Section 5 discussion.

3) Sevenhuijsen et al., “Generating Safety-Critical Automotive C-programs using LLMs with Formal Verification,” 2025 — Presents a pipeline with formal verification/static analysis. Add to Section 2 as a rigorous alternative where reliability is enforced post-generation and verification serves as the contract.

4) Huang et al., “Towards LLM-Powered Verilog RTL Assistant: Self-Verification and Self-Correction,” 2024 — VeriAssist adopts generate→self-verify→self-correct loops. Relevant to Section 2 and 7 as an alternative orchestration emphasizing post-hoc verification rather than pre-specification.

5) Wang et al., “ChronoLLM: customizing language models for physics-based simulation code generation,” 2026 — Domain-constrained code generation in a specialized simulation setting. Useful in Section 7 to discuss generalization claims beyond HumanEval and how Self-Spec might adapt to structured domain APIs.

6) Song et al., “ProgCo: Program Helps Self-Correction of Large Language Models,” 2025 — Uses program-driven self-correction. Should be contrasted in Section 2 as an alternative intermediate (verification pseudo-programs) and in Section 6 when interpreting error classes that might be caught by programmatic checks.

## Comments Suggestions And Typos
Actionable suggestions:
- Expand evaluation beyond HumanEval. Include at least one of MBPP, APPS (a curated difficulty slice), or SWE-bench lite. Even partial coverage with T=0 would make the case stronger for generality.
- Add ablations isolating the “self-authored” effect: compare against (i) a fixed human-authored schema, (ii) a checklist-style structured CoT without schema fields, (iii) Self-Spec without the CONFIRM gate, and (iv) varying numbers of FMInterviewer questions. Report deltas analogous to Table 1.
- Include apples-to-apples baselines under identical conditions: PAL/PoT-style intermediate execution prompts, a recent self-debug loop (single-iteration), and a DSL prompt inspired by a human-authored template. This will contextualize Table 1’s gains.
- Quantify overhead: average number of FMInterviewer questions, tokens per stage, and wall-clock latency. Report a cost-benefit plot that shows pass@1 uplift vs token/latency overhead for each model.
- Strengthen error analysis: for a representative subset, align Tables 2–3 with matched Native logs and show how Self-Spec mitigates or introduces errors. This makes the qualitative taxonomy more persuasive.
- Substantiate the Claude 3.5 claim: re-run with the proposed “guard-stripping” or a spec-level “no extra validation unless stated” switch and report the revised Table 1 result. If the dip disappears, include it in the main results.
- Figure and table clarity: augment Figure 1 with average Q&A loop counts and termination criteria. Annotate Table 1 with exact task counts solved/failed to disambiguate “one or two tasks” swings. For Tables 2–3, add a column indicating whether the error also appeared in the Native baseline for those tasks.
- Related work: integrate the six missing works above to sharpen the positioning around DSLs, requirement alignment, and self-verification approaches.
- Minor typos/edits:
  - §1: “To our knowledge, this is the first systematic study…” — consider softening after adding DSL/requirement-alignment citations.
  - §6 last sentence: ends with “***” which looks like a stray editor mark; remove.
  - §8 “Futurework” → “Future work.”
  - §4 “Mac M4” — specify CPU/GPU, RAM, and API latencies if possible.

What could change my score:
- A revised version that includes ablations isolating “model-authored schema” as the causal factor, broader benchmarks with consistent gains, and cost/latency reporting would substantially strengthen soundness and significance. If these are addressed convincingly, I could raise to 4.0 (Conference).

## Confidence
4: Quite sure after careful checking — I checked the core methodology, figures, and tables closely. Some details (e.g., exact prompts and logs) are referenced in the appendix, but my evaluation does not rely on external materials.

## Soundness
3.5: Between Acceptable and Strong — The method is coherent and reasonably supported by Table 1 and the qualitative analysis, but broader evaluation, ablations, and comparative baselines are missing.

## Excitement
3.5: Between interesting and exciting — The idea of model-authored specs is appealing and the pipeline is clean. With stronger evidence, the excitement could be higher.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. The approach is well-articulated, practically useful, and shows promising gains for strong models. However, the evaluation is narrow, comparative baselines are thin, and the central “model-authored” hypothesis is not isolated via ablations. This package would comfortably land in Findings; a stronger empirical section could justify main-track acceptance.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper discusses limitations around model/version drift and scope. Additional impacts to consider: user-spec quality if humans, not LLMs, answer FMInterviewer questions; risk that self-authored specs can entrench model biases or omit critical safety checks under “no extra validation unless stated;” and increased token cost that may disadvantage some users. Positive impact: more reliable, auditable NL→code workflows for non-experts.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Prompts and code are stated to be released; deterministic decoding helps. Closed-source model drift remains a caveat.

## Datasets
1: No usable datasets submitted. The work does not release a dataset; it uses HumanEval.

## Software
4: Useful — The released prompts and orchestration scripts should be directly useful to practitioners and researchers.