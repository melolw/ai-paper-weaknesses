# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies why repeating a small long chain-of-thought (CoT) SFT dataset for many epochs can outperform using a much larger dataset for a single epoch under a fixed update budget. The authors hypothesize that the “repetition advantage” mainly reflects better termination/formatting rather than better reasoning. They propose a diagnostic decomposition of Acc@n into ParseRate and Acc|Parse and perform a simple mediation analysis. Using OLMo-3-7B fine-tuned on DOLCI-think and evaluated on AIME’24/’25 and GPQA, they report that repetition greatly increases ParseRate while Acc|Parse is comparable or worse than single-epoch data scaling; on AIME the conditional gap reverses sign. They also propose Termination-Aware SFT (TA-SFT) that upweights structure and EOS tokens, which modestly improves ParseRate and Acc@n but recovers only a small part of the repetition gains.

## Summary Of Strengths
- Clear and focused question: The paper directly targets a widely discussed but poorly understood phenomenon in long-CoT SFT under fixed-update budgets.
- Simple and useful diagnostic: Decomposing Acc@n into ParseRate and Acc|Parse provides immediate clarity about termination versus reasoning effects. Equation “Acc@n ≈ ParseRate × Acc|Parse” and the mediation fraction M are straightforward and easy to replicate.
- Empirical evidence that format/termination is a big driver: Table 1 shows a large ParseRate gap (40.6pp) between repetition and data scaling, with Acc|Parse actually lower under repetition. Table 2 further quantifies “over-explanation” (M > 1) on AIME benchmarks.
- Actionable baseline intervention: TA-SFT is simple to implement. Table 3 ablations suggest both <think> and EOS tokens matter, and that moderate reweighting with a cap works better than aggressive settings.
- Effective visual communication: Figure 1 nicely summarizes the experimental setup and the central diagnostic insight, highlighting the R^2 correlation between ParseRate and Acc@n. Figure 2 makes the unconditional-versus-conditional gap reversal on AIME easy to see.

## Summary Of Weaknesses
1) Limited scope of evidence and external validity
- Only one base model (OLMo-3-7B) and one training corpus (DOLCI-think). No exploration across model sizes, families, or alternative long-CoT datasets. This makes it hard to conclude that the “repetition advantage is a termination effect” beyond the specific setup. See Section 4.1.  
- Benchmarks are small (AIME has 30 items per year, GPQA has 198) and the paper reports no confidence intervals, no standard errors, and no multiple-seed reruns. The differences in Acc|Parse and ParseRate could be sensitive to sample variance. This is particularly important because the main claim rests on differences of just a few percentage points in Acc|Parse (Table 1).

2) Mediation analysis is informal and under-specified
- Section 3.4 defines M = 1 − Δcond/Δuncond and treats M > 1 as “over-explaining.” There is no uncertainty analysis, no regression-based mediation, and no sensitivity analysis to check robustness when Δuncond is small or when ParseRate varies nonlinearly with decoding hyperparameters. Figure 2 visualizes the gaps, but mediation as a causal statement is not established.  
- The decomposition in Section 3.3 is an approximation (≈) and assumes stationarity of ParseRate and Acc|Parse across samples; the paper does not quantify the approximation error or provide a sanity check (e.g., per-instance aggregation verifying the product identity holds closely).

3) Decoding and evaluation confounds are not controlled
- ParseRate is influenced by decoding settings (temperature, top-p, max tokens) and the stop sequences used for extraction. Section 4.1 fixes T=0.6 and top-p=0.95, but there is no sensitivity analysis across decoding settings or max generation length. Since the paper’s central claim hinges on termination, decoding-time early stopping, constrained decoding, or adjusted max_new_tokens could change ParseRate substantially without training changes.  
- Acc@n depends on n (16 for AIME, 4 for GPQA). The paper does not report how ParseRate responds to n, nor whether the repetition advantage persists under different n. For instance, majority voting with more samples could mitigate termination variance.

4) Missing competitive baselines focused on termination and long-CoT control
- The comparisons are only: single-epoch data scaling (A), many-epoch repetition (B), and TA-SFT (C). There is no evaluation against alternative termination-aware or length-control baselines such as early-stopping tokens, on-policy SFT that trades off brevity and correctness, or mixtures of long/short CoT supervision. This limits the practical takeaway.  
- Even simple inference-time interventions (e.g., stronger stop sequences, answer-first or dual-head decoding, constrained extraction) are not compared, though they can raise ParseRate without changing training.

5) Ambiguities and inconsistencies in TA-SFT details
- Section 3.5 states structure tokens include “the substring (end of reasoning block)” which looks garbled; presumably this means the closing think-tag and possibly answer delimiters (e.g., \boxed{}). Exact tokenization and how positions are detected are not fully specified.  
- The warmup schedule and “loss cap of 50” are introduced, but Table 3’s “C-no-cap | alpha = 37.3 | 24.2 Acc@n” is confusing: “no-cap” should not show a numeric alpha as if it were a measured value; also Section 4.5 text calls this “formula-computed values (37–50),” which is not defined earlier. These inconsistencies make the intervention hard to reproduce precisely.

6) Lack of deeper analysis of why repetition teaches termination
- The paper concludes that repetition effects go beyond loss reweighting but stops short of offering concrete evidence or hypotheses beyond the intuition that repetition helps memorize format. For instance, are repeated examples more homogeneous in length, tags, or boxed-answer patterns that reduce variance? Is the training loss on structure tokens demonstrably lower under repetition? Token-level loss curves, head activations on structure markers, or error typology would strengthen the mechanistic story.

7) Limited error analysis and qualitative evidence
- No breakdown of unparseable outputs by failure types (truncation, malformed boxes, missing EOS, mid-trace halts) or by problem difficulty. No qualitative examples of near-miss parses or examples where Acc|Parse differs sharply across conditions.

8) Claims extend beyond demonstrated benchmarks
- The abstract states “Our findings suggest that apparent reasoning improvements from data repetition may largely reflect format learning rather than enhanced reasoning capabilities.” Given the narrow experimental scope and missing significance estimates, this reads too strongly. The GPQA row in Table 2 already shows a different pattern (mediation fraction < 1).

9) Figure- and table-specific concerns
- Figure 1 claims “ParseRate strongly predicts Acc@n (R^2 = 0.93).” The paper does not provide the regression details: across what points (benchmarks × conditions × seeds)? No plot or numeric table showing the paired values used for the correlation.  
- Figure 2 effectively communicates the gap reversal on AIME, but the graphic would benefit from error bars or per-seed bands to substantiate the strength of the claim.  
- Table 1 and Table 2 are central to the argument; however, there are no statistical tests (e.g., bootstrap CIs) despite the small test sizes.

10) Missing directly related work and ablations motivated by it
- The Related Work section omits several recent papers that study long-CoT generalization, harmful continuation, on-policy SFT, and early stopping signals that directly intersect with the termination lens of this paper. Incorporating them could both strengthen positioning and inspire stronger baselines.

## Potentially Missing Related Work
1) Li et al., On the Role of Reasoning Patterns in the Generalization Discrepancy of Long Chain-of-Thought Supervised Fine-Tuning, 2026 — Analyzes token-level effects of long-CoT supervision and generalization discrepancies. Should be discussed in Section 2 and compared with the ParseRate/Acc|Parse decomposition in Section 3.3; may suggest additional diagnostics or ablations around token-level losses and structure tokens.

2) He et al., Diagnosing Harmful Continuation in Answer-Correct Long-CoT Training Traces, 2026 — Shows that post-answer continuation can be harmful and provides mitigation strategies. Add to Section 2 and discuss in Section 4.4 as an alternative or complementary termination intervention; could be an additional baseline against TA-SFT.

3) Zhao et al., On-Policy Supervised Fine-Tuning for Efficient Reasoning, 2026 — Proposes an on-policy SFT scheme that trades off correctness and brevity without complex RL. Compare in Section 4 with TA-SFT as a termination- and length-control strategy under fixed-update budgets.

4) Wang et al., ESTAR: Early-Stopping Token-Aware Reasoning For Efficient Inference, 2026 — Introduces stop-token training that enables earlier termination. Should be discussed in Section 2 and used as a baseline in Section 4; directly relevant to improving ParseRate via explicit stop signals.

5) An et al., Long Chain-of-Thought Fine-tuning via Understanding-to-Reasoning Transition, 2025 — Curriculum-style long-CoT SFT that changes how supervision is presented, potentially affecting termination. Include in Section 2 and consider as a training baseline to test if curriculum reduces termination failures without repetition.

6) Yu et al., Long-Short Chain-of-Thought Mixture Supervised Fine-Tuning, 2025 — LS-Mixture of long/short CoT to reduce overthinking and improve efficiency. Compare in Section 4 as an alternative to repetition and as a possible way to increase ParseRate.

7) Li et al., Small Models Struggle to Learn from Strong Reasoners, 2025 — Shows scale-dependent learnability issues for long-CoT distillation. Discuss in Section 2 and consider scaling experiments beyond a single 7B model to test whether termination-vs-reasoning tradeoffs vary with size.

8) Li et al., Language Models Can Easily Learn to Reason from Demonstrations, 2025 — Emphasizes that structural corruption is more harmful than content errors, reinforcing the importance of format. Cite in Section 2 and consider additional ablations in Section 4.5 that manipulate structural cleanliness versus content to see how ParseRate responds.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Statistical robustness: Please report confidence intervals or standard errors for Acc@n, ParseRate, and Acc|Parse, preferably via bootstrap over problems and across at least 3 seeds. Add error bars to Figure 2. This is crucial given the small sizes of AIME and GPQA and the paper’s reliance on gap comparisons.
- Decoding sensitivity: Provide a decoding sweep (temperature, top-p, max_new_tokens, stop sequences, and n) to assess how sensitive ParseRate and Acc|Parse are to these knobs. If the core claim holds across a reasonable range, it will be much more convincing.
- Expanded baselines: Add at least one training-time termination baseline (e.g., stop-token training/ESTAR-like design or on-policy SFT with brevity preference) and one inference-time baseline (e.g., stronger/constrained stop sequences or answer-first dual decoding) to isolate training versus decoding contributions to ParseRate.
- Mechanistic analysis: Include token-level loss curves for structure tokens, termination logits at the final step, or attention patterns to show how repetition versus TA-SFT changes termination behavior internally. This would substantiate the “more than just loss reweighting” conclusion.
- Clarify TA-SFT details:  
  - Precisely define “structure tokens,” including how <think> and its closing tags, boxed-answer delimiters, and EOS are tokenized and detected.  
  - Resolve inconsistencies around “loss cap 50,” “alpha warmup to 10,” and Table 3’s “no-cap alpha=37.3” phrasing. If “no-cap” used a different alpha schedule or a computed value, specify clearly.  
  - Explain how loss normalization across tokens is handled when reweighting, and whether padding tokens are excluded from the denominator.
- Product decomposition accuracy: Provide a check showing how closely Acc@n matches ParseRate × Acc|Parse empirically on your runs, and quantify any residual.

Minor comments and typos:
- Section 3.5: “where structure tokens include positions belonging to the substring (end of reasoning block)” appears corrupted; likely missing markup for the closing think tag or boxed answer delimiter.  
- Table 3 header “C-no-cap | α = 37.3” conflicts with the “no-cap” label and with α=10 in the main method; please clarify.  
- Consistent notation for Acc@n: sometimes spaced as “Acc@n,” sometimes “Acc @ n” in prose; unify.  
- Figure 1 claims R^2=0.93 without specifying the fit data; add a caption note or a sentence in Section 3 explaining the regression inputs.

Criteria for score improvement after rebuttal:
- Provide multi-seed results with uncertainty and a decoding sweep showing robustness of the mediation finding.  
- Add at least one strong termination-focused training baseline and one inference-time baseline; show that the main claim about repetition-as-termination holds.  
- Clarify TA-SFT implementation details and fix inconsistencies in Table 3.  
- Include limited-scale extension to a second base model or dataset to support generality.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure of the assessment, but missing details on statistics and decoding sensitivity could change the interpretation.

## Soundness
2.5: Between Poor and Acceptable — The diagnostic is clear and the results are suggestive, but lack of statistical rigor, single-model scope, and missing baselines reduce the strength of the claims.

## Excitement
2.5: Between potentially interesting and interesting — The question matters and the diagnostic is handy, but the empirical scope is narrow and the intervention modest.

## Overall Assessment
2.5 Borderline Findings — The paper raises an important point about termination vs. reasoning in long-CoT SFT and offers a clear diagnostic with compelling initial evidence (notably Figure 2 and Tables 1–2). However, the current scope, lack of statistical robustness, decoding-sensitivity analysis, and missing termination-focused baselines make the main claim feel premature for the main track. With multi-seed uncertainty, stronger baselines, clarified TA-SFT details, and minimal generalization checks, I could see this moving to solid Findings or beyond.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper does not deeply discuss broader societal impacts. For this topic, the main concerns would involve potential over-claiming of “reasoning” improvements in widely deployed systems when they may be termination artifacts, which can mislead users and policymakers. It would be helpful to add a short discussion noting that:  
- Misattributing termination improvements to reasoning could skew evaluation practices, leading to overconfidence in systems used in education or decision support.  
- Datasets like AIME are narrow; conclusions should not be generalized to broader language tasks without caution.  
- Longer CoT traces increase compute and cost; emphasizing termination and format may encourage more efficient and transparent evaluation.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Training hyperparameters, data sources, and evaluation settings are given, and the intervention is simple. However, inconsistencies around TA-SFT details and missing seeds/uncertainty prevent a 5.

## Datasets
1: No usable datasets submitted — The work relies on existing benchmarks; no new dataset contribution.

## Software
3: Potentially useful — If released as stated, code would likely be useful to reproduce the diagnostic and TA-SFT runs, but current ambiguities and missing baselines limit broader utility.