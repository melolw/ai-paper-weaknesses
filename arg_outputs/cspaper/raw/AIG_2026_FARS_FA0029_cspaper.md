# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies the objective used for global budget allocation in ROCKET, a training-free LLM compression method that profiles candidate layer-wise factorizations and solves a multi-choice knapsack problem (MCKP). While ROCKET derives per-layer factorizations from an output reconstruction objective in a whitened activation space (Equation 1), it allocates budgets using weight-space Frobenius error (Equation 3). The authors propose ROCKET-ActCost, which replaces the MCKP cost with an output-space error measured in the same whitened space used during factorization (Equation 4). On Qwen3-8B at 50% compression, this change improves average zero-shot accuracy by 0.8 percentage points across eight tasks but worsens WikiText-2 perplexity by 16%; on Llama-3.2-1B at 20% compression, both accuracy and perplexity improve. They attribute the modest effect to very high per-layer correlation (>0.99) between weight-space and output-space errors, which limits allocation divergence. Figure 1 illustrates the pipeline modification; Tables 1–3 report results and per-benchmark breakdowns.

## Summary Of Strengths
- Clear, focused question with a minimal change to a known pipeline: should the MCKP allocation cost align with the per-layer output reconstruction objective? The change is well-motivated in Section 2 by Equation 1 and formalized in Equation 4.
- The implementation is simple, appears to add no runtime overhead, and is easy to adopt wherever ROCKET-style profiling already computes whitened weights. Figure 1 succinctly shows that the only change is the error term used for MCKP, while all other stages remain intact.
- The empirical analysis explicitly surfaces an accuracy–perplexity tradeoff at aggressive compression, which is valuable for practitioners who often optimize for one metric while monitoring the other. Table 1 and Table 2 make this concrete: +0.8 pp AvgAcc on eight tasks, but 16% worse PPL; per-task accuracy improvements concentrate on ARC-C, MMLU, and LAMBADA.
- The high correlation analysis in Section 3.3 gives an informative negative result. Reporting that output-space and weight-space errors correlate >0.99 and that only 70 of 252 layers’ allocations change provides an explanation for the modest gains and properly calibrates expectations.
- Secondary setting on Llama-3.2-1B at 20% compression (Table 3) strengthens external validity by showing a regime where both accuracy and perplexity improve.

Specific figure/table-based strengths:
- Figure 1 is effective in clarifying the proposed change: the red-crossed “Weight-Space Error” versus the green-highlighted “Output-Space Error” boxes make it immediately clear that the factorization, candidate generation, and solver are shared; only the error fed to MCKP changes. This supports the claim of zero added runtime and minimal code changes.
- Table 2 provides a per-benchmark lens that supports the claim that accuracy gains are more pronounced on reasoning-centric tasks (ARC-C +1.5 pp, MMLU +1.5 pp, LAMBADA +1.2 pp), which is an insight beyond a single averaged score.

## Summary Of Weaknesses
1) Limited scope of evaluation and missing context on where this tradeoff matters most:
- Only two models are evaluated, with the main result on a single aggressive ratio (Qwen3-8B at 50%) and a single milder ratio on a smaller model (Llama-3.2-1B at 20%) in Section 3.4. The study would be more convincing if it explored more compression ratios per model to map out when the allocation objective matters.
- Seeds are minimal (two seeds for Qwen3-8B, one for Llama-3.2-1B), which is a slender basis for strong claims about consistent allocation benefits.

2) Lack of baselines targeting allocation objectives:
- The paper does not compare against alternative allocation criteria beyond the two at hand. For instance, error normalized by downstream sensitivity proxies (e.g., Hessian approximations, logit-layer sensitivity), or layer-wise calibration loss-based scores. Without such comparisons, it is unclear whether output-space error is the best next objective or just one reasonable option.

3) Incomplete exploration of the observed tradeoff:
- The accuracy–perplexity tradeoff is central, but the paper stops at reporting the phenomenon without deeper analysis. For example:
  - Which layers typically flip allocation and how do they correlate with attention vs. MLP blocks, or early vs. late layers?
  - Do changed allocations bias rank toward layers with higher activation variance under calibration? The text notes high error correlation and only 70/252 flips, but does not characterize those flips, which could yield actionable rules of thumb.
  - No analysis of calibration-distribution shift is provided: WikiText-2 for PPL differs from RefinedWeb calibration, which may partly explain the PPL drop. This deserves a controlled experiment.

4) Perplexity vs. accuracy interpretation is underdeveloped:
- Section 3.2 infers that output-space cost may favor task-relevant information over language modeling quality. This is plausible but remains speculative. A more direct check would inspect changes in distribution of next-token errors by part-of-speech or frequency, or calibration loss on sampled dev text aligned with the tasks.

5) Modest gains and limited practical guidance:
- On the flagship setting (Table 1), gains are +0.8 pp AvgAcc with a 16% PPL increase. Many users will not accept worse PPL, so the guidance should be: when to use which objective. There is an initial attempt in Section 3.4, but the paper stops short of a practical decision guide across ratios and model families.

6) Missing ablations and sensitivity to calibration data:
- The method relies on the calibration distribution via Equation 4, yet there is no study of sensitivity to calibration set composition or size. Since the paper’s motivation is activation-aware allocation, this is an important omission. At minimum, small vs. larger calibration sets or alternative data subsets would help. Equation 4’s normalization by ||W_L||F can also be sensitive to the whitening quality.

7) Statistical reporting and uncertainty:
- Table 1 and Table 2 report means across two seeds but no confidence intervals or standard deviations. With small deltas (+0.8 pp), uncertainty is needed to assess significance. Similarly, Table 3 uses one seed only, which further limits interpretability.

8) Claims about zero runtime overhead need measurement details:
- Section 3.5 states a 7.7% faster runtime on average due to different allocations, but provides no protocol, variance, or per-stage timings. A microbenchmark table would make this credible, especially since solver time vs. profiling time may shift with allocations.

9) Presentation/positioning gaps in Related Work:
- The paper positions itself primarily against ROCKET and activation-aware low-rank works (ASVD), but omits several directly relevant studies on calibration data’s role in compression choices and task–perplexity discrepancies. See “Potentially Missing Related Work.”

10) Minor but notable: the paper emphasizes that it was generated by an automated system. This is fine, but the writing sometimes reads like a concise engineering note rather than a full-blown empirical study. For ACL main, more breadth in analysis and validation would be expected.

Specific figure/table-based weaknesses:
- Table 1 shows the core tradeoff, but the paper does not provide statistical measures to contextualize the +0.8 pp gain, which could be within noise given only two seeds.
- Figure 1 clearly explains the pipeline but also highlights the limited algorithmic delta. The contribution is almost entirely the choice of cost fed into the existing MCKP, with no exploration of alternative objectives or multi-objective formulations (e.g., combining output- and weight-space errors), which would be a natural extension.
- Table 2 and Table 3 lack error bars or per-task variance, making it hard to conclude robustness of the observed effects.

## Potentially Missing Related Work
1) Williams et al., “On the Impact of Calibration Data in Post-training Quantization and Pruning,” 2024 — directly investigates how calibration data choice affects compression outcomes. It should be discussed in Section 4 and connected to Section 3.1’s calibration setup; ideally, add a sensitivity study or acknowledge expected sensitivity with citation.

2) Ji et al., “Beware of Calibration Data for Pruning Large Language Models,” 2025 — analyzes calibration data properties versus sparsity levels and proposes self-generated calibration. Relevant to Section 3.1; discuss and consider in the analysis of why output-space costs might hurt perplexity under mismatch with PPL corpus.

3) He et al., “Preserving LLM Capabilities through Calibration Data Curation: From Analysis to Optimization,” 2025 — introduces curation to preserve capabilities post-compression. Integrate into Section 4 and discuss in Section 3.3–3.4 how curated calibration could change the high error correlation or tradeoffs.

4) Monaco et al., “Frequency Matters: Fast Model-Agnostic Data Curation for Pruning and Quantization,” 2026 — proposes ZipCal for sample selection. Discuss in Section 4 and consider in future work as a way to reduce the observed PPL hit through better calibration sampling.

5) Cunegatti et al., “From Layers to Submodules: Rethinking Granularity in Replacement-Based LLM Compression,” 2026 — alternative calibration-guided structural compression at submodule granularity. Compare in Section 4; could inform whether allocation at different granularities changes the observed correlation and effect size.

6) Xuke et al., “EPTS: Elastic Post-Training Sparsity for Efficient Large Language Model Compression,” 2026 — framework spanning multiple sparsity levels; relevant to the paper’s setting-dependent findings. Add to Section 4; the method’s robustness across compression ratios is a useful foil to the paper’s narrow ratios.

7) He et al., “LLMCodec: Adapting Video Codecs for Efficient Weight Compression of Large Language Models,” 2026 — explores different compression quality tradeoffs via configurable codecs. Add to Section 4 and discussion of perplexity–accuracy tradeoffs; provides a distinct path with comparable concerns.

8) Khanal et al., “Evaluating the Impact of Compression Techniques on Task-Specific Performance of Large Language Models,” 2024 — documents that preserving PPL does not guarantee strong task accuracy, aligning with Section 3.2. Cite in Section 3.2 to ground the tradeoff claims.

## Comments Suggestions And Typos
Actionable suggestions and questions:
- Please add uncertainty estimates. Report standard deviations or confidence intervals for AvgAcc in Tables 1 and 3, and per-task in Table 2. With small improvements (+0.8 pp), this is essential.
- Expand calibration sensitivity analysis. Vary calibration size and composition, and consider an alternative calibration corpus closer to WikiText-2 to test whether PPL degradation is due to distribution mismatch. Even a small-scale study would strengthen Section 3.2.
- Characterize allocation flips. In Section 3.3, analyze which layers change under ActCost: attention vs. MLP, early vs. late, and correlation with activation variance or norm. A figure or table listing flip density per block would turn a modest empirical tweak into more general guidance.
- Explore multi-objective or hybrid costs. For instance, a convex combination λ·eout + (1−λ)·eweight or a bi-criteria MCKP to balance perplexity and accuracy, with λ tuned on a held-out validation of the calibration set. This would speak directly to practitioners weighing both metrics.
- Add microbenchmarks. Provide a runtime breakdown (profiling, SVD/factorization, solver, and end-to-end) with means and standard deviations to substantiate the “no overhead” and “7.7% faster” claims in Section 3.5.

Typos and minor issues:
- Page 1, Abstract: “+0.8 percentage points higher average accuracy” is fine, but later “+0.8pp” is used; consider consistent style.
- Table captions: use consistent bold formatting and arrows for metrics (↑/↓) across all tables; Table 3 caption uses “Best in bold” whereas Table 1 uses “Best in bold.” Standardize punctuation.
- Section 2.1: notation alternates between ℓ and t when referring to layers (eℓ,i vs et,i). Make it consistent.
- Section 3.3: “Concretely, only 70 of 252 compressible layers receive different allocations” — consider adding which layers are excluded as non-compressible and why.

What could change my evaluation:
- Providing uncertainty and demonstrating that the reported +0.8 pp (Qwen3-8B) and +0.6 pp (Llama-3.2-1B) gains are statistically reliable.
- Adding calibration sensitivity experiments showing when ActCost avoids the PPL hit or when it is preferable, and characterizing allocation flips by layer type to yield practical guidance.
- Including one or two alternative allocation objectives or a hybrid that better navigates the tradeoff.

## Confidence
3: Reasonably confident but not fully verified — I checked the equations and setup and the claims follow from the presented data, but limited seeds and missing ablations leave room for uncertainty.

## Soundness
3: Acceptable — The study supports its main claims, but breadth is limited, statistics are thin, and several key analyses are missing.

## Excitement
2.5: Between potentially interesting and interesting — The question is clear and practical, the finding is useful, but the contribution is small and the evaluation is narrow.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The contribution is a small but tidy change that is easy to adopt, and the tradeoff insight is useful. However, the empirical scope is narrow, uncertainty reporting is missing, calibration sensitivity is untested, and the gains are modest with a countervailing PPL degradation in the primary setting. With added analysis, uncertainty, and a broader evaluation, this could reach a stronger Findings case.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
Limitations are only partially discussed in the text. Additional important points to include:
- Calibration dependence: The proposed cost is tightly bound to the calibration distribution. If calibration data are unrepresentative, allocation may overfit to certain activation directions, potentially harming generalization or PPL. This deserves explicit acknowledgment and empirical checks.
- Metric tradeoffs: The method can improve task accuracy while worsening perplexity, which could affect applications that rely on fluent generation or log-likelihood-based reranking. Guidance on choosing objectives for different deployment contexts would mitigate risks.
- Broader capability coverage: Zero-shot accuracy on eight English benchmarks is informative but does not speak to multilinguality, safety, or bias; compression may alter these characteristics in ways not captured here.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — The method change is simple, equations are clear, and the code link is provided. Some implementation and data-selection details, seeds, and metrics variance would further help.

## Datasets
1: No usable datasets submitted.

## Software
4: Useful — If the provided code runs as claimed, it should be straightforward for others to use as a drop-in change to ROCKET-style pipelines.