# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes RC-MemStop, a post-hoc calibration method for early stopping in long-context “memory agents.” The stopping rule terminates when k consecutive normalized draft answers match (Equation 1). Using conformal risk control with the Waudby-Smith–Ramdas betting bound, the method selects the smallest k that satisfies a user-specified broken-success risk budget ε (Equations 2–3). Experiments with MemAgent on long HotpotQA-style settings at 448K and 896K tokens show that the formal risk target is met on held-out test data, but speedups are minimal (1.02×–1.14×) because draft answers stabilize only near the end of processing, requiring k between 60 and 120. The paper concludes that calibration-only stopping based on answer stability is insufficient for meaningful compute savings and suggests learned stopping policies.

## Summary Of Strengths
- Clear and focused problem formulation: the paper explicitly defines the deployment risk of interest as “broken-success risk” (Equation 2) and calibrates a single interpretable parameter k with a user-chosen ε.
- Faithful application of conformal risk control to a memory-agent setting, with the selection rule in Equation 3 well-motivated and tied to finite-sample guarantees.
- Negative result that is informative: the main empirical finding that answer stability requires very large k is valuable for practitioners weighing calibration-only early stopping.
- Transparent reporting with concrete quantitative outcomes. Table 1 gives a compact summary of k, risk, accuracy, chunks, and speedup; Table 2 surfaces the case where the UCB bound does not certify ε at 896K/ε=0.05.
- Figures help diagnose the limitation. Figure 2 makes the monotonic—but very slow—decay of calibration risk Rcal(k) visually explicit, clarifying why speedups are negligible in practice.

## Summary Of Weaknesses
1) Narrow scope of method and evaluation
- Only one stopping signal is investigated, i.e., exact-match answer stability (Section 3.2). Alternative, often stronger signals (e.g., confidence margins from the model’s probabilities or logits, representational stability, entropy thresholds, auxiliary critics, or agreement under prompt variations) are not explored or even ablated. This severely limits the generality of the conclusion that “calibration-only early stopping is insufficient.”
- Only one agent (MemAgent-7B) and one task family (HotpotQA-style long-context QA with synthetic distractors) are used (Section 4.1). It is unclear whether the weak signal is specific to this configuration or universal across memory agents, backbones, or tasks (e.g., summarization, retrieval-style QA, code QA).

2) Small calibration/test sample sizes and limited statistical analysis
- The calibration pool of full-read successes is small (e.g., n_succ = 47 for the 896K setting; Section 4.3), which directly affects UCB tightness and the selected k. The paper acknowledges the UCB>ε case but does not analyze sensitivity to calibration-set size. A simple power analysis or curves of selected k versus calibration-set size would clarify whether more data could make CRC practical here.
- Only one random split/seed (Section 4.1) is used. No variability analysis is reported. Confidence intervals or bootstrap variability around speedup and risk would strengthen claims.

3) Incomplete risk-control discussion relative to non-monotonicity
- The selection rule in Equation 3 assumes approximate monotonicity of R(k). Figure 2 shows “mild violations” for small k, but the theoretical implications are not covered. There exists work on CRC under non-monotone losses over discrete grids; those tools could strengthen guarantees without relying on monotonicity. The paper does not discuss or compare such alternatives.

4) Limited baselines and ablations
- There is no comparison to other training-free stopping rules, such as: k-of-m matching, EMA-based stabilization, confidence/entropy thresholds, agreement under paraphrases or stochastic decoding, or oracle-peak draft answer. Even if the paper’s goal is to study answer stability, ablation with a soft-normalization or token-level matching could show whether the limitation is due to the string-normalization strictness or the underlying agent dynamics.
- No analysis of decoding choice is provided. The method uses “deterministic decoding” (Section 3.1), but how beam size, temperature, or nucleus parameters influence stabilization is not evaluated. This is pertinent because Figure 2’s slow decay might partially reflect deterministic decoding that suppresses informative variance.

5) Measurements of compute and cost are under-specified
- “Speedup” is reported in terms of average chunks processed (Table 1), which is a reasonable proxy, but token-level or wall-clock measures are not reported. Since chunk lengths may differ slightly and per-step memory updates can vary in cost, end-to-end GPU-time or token-throughput speedup would be more convincing.

6) Inconsistency in guarantees vs. observed risk
- Table 2 flags that the UCB bound at 896K/ε=0.05 is 0.0816>ε (no formal guarantee), while Table 1 still marks ✓ for “no risk violation” on test; Section 4.2 then states “zero risk violations across all 8 configurations.” This is factually fine but could be confusing: it would help to disambiguate clearly between “certified by bound” vs. “empirically observed on one sample.” Right now the presentation can be read as stronger than warranted.

7) Missing experimental details impede exact reproducibility
- The paper does not fully specify: the exact checkpoint hash, prompt templates, normalization details aligned with HotpotQA evaluation, and the precise RULER synthesis parameters. The footnote provides a code URL, but the main text should include enough to reproduce results without browsing a repository.

8) Limited discussion of task quality and dataset construction
- The 448K–896K contexts are constructed by embedding gold evidence into large distractor documents “following RULER” (Section 4.1). More detail is needed: How diverse are distractors? Is there leakage between calibration and test contexts through template artifacts? Are there failure analyses showing whether errors are due to missing later evidence versus instability in earlier drafts?

9) Overreach in conclusions
- The core experimental finding is that exact-match answer stability fails to produce meaningful speedups in this particular setup. However, the conclusion suggests that “training-based stopping policies are necessary” (Abstract, Conclusion). That is stronger than justified without testing stronger training-free signals or broader agent/task coverage. The data shows this signal is too weak here; it does not yet rule out other calibration-first designs.

10) Limited engagement with closely related CRC-for-agents literature
- The related work section does not cover recent CRC work for sequential or agentic settings. This weakens the positioning, particularly around how CRC could be adapted when monotonicity is violated or when decisions are made over trajectories rather than a single parameter k.

Figure- and Table-specific critique
- Figure 1: The architecture diagram is clear and helpful for readers unfamiliar with CRC. It also mentions Learn-then-Test (LTT), but LTT is not instantiated in experiments. If LTT is shown in the pipeline, a brief empirical comparison or a reason for excluding it would avoid confusion.
- Figure 2: This figure is central to the main claim. The curves show Rcal(k) staying around 0.75 up to k≈10 and crossing ε=0.10 only near k≈60 for 448K and k≈100–120 for 896K. This strongly supports the argument that answer stability is too weak to allow early stopping. I encourage adding vertical lines at chosen k_UCB and k_naive to directly connect the diagnostic to the selections reported in Table 1.
- Table 1: The presentation is clean. However, reporting standard errors or CIs for “Avg Chunks” and “ES Acc” would help judge whether 1.04× vs 1.08× is meaningful. Also, including the number of calibration successes used per condition would contextualize R_test volatility.
- Table 2: Good that the “no guarantee” case is explicitly marked. Please add the corresponding n_succ values in the table so readers understand bound looseness.

## Potentially Missing Related Work
1) Opoku et al., “ToolChain-CRC: Conformal Risk Control for Agentic AI Under Retrieval and Tool-Use Drift,” 2026 — directly addresses CRC for sequential agent trajectories under distribution shift. It should be discussed in Section 2 to position RC-MemStop among CRC-for-agents approaches and cited after Equation 3 to contrast selection under trajectory-level risks.
2) Feng et al., “CORA: Conformal Risk-Controlled Agents for Safeguarded Mobile GUI Automation,” 2026 — applies CRC to calibrate execute/abstain decisions in GUI agents. Discuss in Section 2 as a closely analogous design pattern for CRC thresholds and compare with answer-stability stopping in Section 4.5.
3) Aldirawi et al., “Non-monotonicity in Conformal Risk Control,” 2026 — analyzes CRC when losses are non-monotone over policy grids. This is technically relevant to the mild non-monotonicity of R(k) seen in Figure 2. Cite in Section 3.3 and discuss how their results could yield guarantees without relying on approximate monotonicity.
4) Gonzales et al., “Safe Probabilistic Planning for Human-Robot Interaction using Conformal Risk Control,” 2026 — integrates CRC with sequential decision-making and safety constraints. Useful background to broaden Section 2 and suggest future extensions where stopping interacts with other risk-aware controls in agents.

## Comments Suggestions And Typos
Actionable suggestions
- Strengthen the scope: Add at least one training-free alternative stopping signal baseline. Candidates include confidence/entropy thresholds, representation-space stability, k-of-m agreement, or agreement under paraphrased prompts. Even if speedups remain small, this will clarify whether the limitation is specific to string-level answer stability or more general.
- Calibration size sensitivity: Provide a study varying calibration-set size and showing selected k, UCB bound, and speedup as functions of n_succ. This will reveal whether CRC is inherently impractical here or simply calibration-data starved.
- Multi-seed robustness: Repeat experiments with multiple seeds/splits and report variability for R_test, speedup, and ES Acc in Table 1. Include CIs or error bars.
- Guarantees vs. outcomes: In Section 4.2 and Table 2, explicitly separate “WSR-certified” vs. “observed on test” outcomes, and reflect this in Table 1 with a distinct mark for configurations whose bounds do not meet ε even at the largest k.
- Figure 2 linkage: Overlay vertical lines at k_UCB and k_naive on Figure 2, and annotate the fraction of the document processed at τ(k) for median examples to visually link risk decay to compute.
- Compute metrics: Report token-level or wall-clock speedups in addition to “Avg Chunks,” ideally with hardware specs and batch configurations.
- Reposition conclusions: Soften the claim that “training-based policies are necessary,” and instead conclude that “exact-match answer-stability, calibrated via CRC, is too weak in our setting.” If you add training-free baselines and they also fail, the stronger statement becomes better supported.
- Experimental details: Add exact checkpoint identifiers, prompt templates, decoding parameters, and normalization rules in the main text; include a short pseudo-code for the calibration loop, including the WSR computation. Clarify whether the UCB is uniform over k or applied per-k with multiplicity control.
- Explore partial-credit metrics: For multi-hop QA, consider F1 or span overlap for draft answers to define softer normalization in Equation 1. This may yield earlier stabilization with an interpretable ε on partial-credit risk variants.

Typos and minor edits
- Section 4.2: “Across all 8 configurations” is technically accurate for observed test risk, but could be misread as certified. Clarify.
- Table 2 caption: “UCB bound exceeds ε at 896K/ε=0.05” — add the n_succ used to contextualize the looseness.
- Figure 1 caption: LTT is mentioned but unused in experiments; add a brief note clarifying it is shown as a possible alternative but not evaluated.

Criteria that can change my score
- Inclusion of at least one strong training-free stopping baseline beyond answer stability, with full ablations and a sensitivity analysis on calibration size. If results remain similar, the negative conclusion is more compelling; if an alternative signal works, the contribution becomes more actionable. This could raise Soundness and Overall Assessment.
- Multi-seed variability analysis with CIs, and token-level or wall-clock speedups. Clearer and stronger empirical methodology could improve Soundness.
- Incorporation of CRC under non-monotone losses (or an LTT variant) to provide certified guarantees even when R(k) is not monotone. This would strengthen the theoretical footing and calibration procedure.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
2.5 Between potentially interesting and interesting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The paper is clear and tackles a practical question with a principled tool, and the negative result is informative. However, the scope is narrow (single agent, single signal, single task family), alternative training-free signals are not tested, statistical analyses are thin (single seed, limited calibration size study), and related CRC-for-agents literature is missing. With added baselines, sensitivity analyses, and tighter positioning, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper focuses on reducing compute for long-context agents with risk control. It does not introduce sensitive data or user studies. Potential positive impacts include safe efficiency gains, though the demonstrated gains are small. Potential negative impacts are minimal, but an overconfident interpretation of empirical “no violation” without certified bounds (as in 896K/ε=0.05) could mislead deployment if not clearly distinguished. The paper could add a brief discussion of energy use vs. negligible speedups to make the trade-off explicit.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.

## Datasets
1 No usable datasets submitted.

## Software
4 Useful.: I would recommend the new software to other researchers or developers for their ongoing work.