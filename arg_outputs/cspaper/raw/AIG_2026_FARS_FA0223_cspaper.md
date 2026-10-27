# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes Delta SVD-EQ, a post-hoc method to mitigate catastrophic forgetting when sequentially fine-tuning LoRA adapters. At each task boundary, it computes the task-specific LoRA delta, performs an SVD, and replaces all singular values with their root-mean-square while preserving the Frobenius norm (Equation 3). The method is training-free, memory-free at training time, and applicable to existing checkpoints. On the FOREVER “Standard CL” benchmark with Qwen3-0.6B across four text classification tasks, the method reports a mean BWT improvement of +2.3 percentage points with essentially unchanged overall performance, and a large reduction in variance across seeds. Ablations suggest both magnitude effects and spectral redistribution contribute to gains, although a correlation analysis in Figure 3 finds no link between initial spectral concentration (Equation 2) and improvement.

## Summary Of Strengths
- Conceptual simplicity and clear post-hoc positioning: equalizing singular values to preserve Frobenius norm is easy to implement and can be layered on top of any trained LoRA checkpoint. The method is unintrusive and training-free, which is attractive for real deployments.
- The paper is generally well structured and readable, with a crisp problem setup, clear definition of OP and BWT (Equation 1), and a succinct method statement (Sections 3.2–3.3).
- Useful ablations and negative result: the comparison with “Mean-Smoothing” and “Random-Spectrum” in Table 1 helps tease apart norm shrinkage versus spectral redistribution. The lack of correlation in Figure 3 is forthright and informative, suggesting the mechanism is not just fixing over-concentration.
- Variance reduction is a practical benefit: Table 2 and Figure 2 show a 3–10× drop in within-order standard deviation, which could make sequential LoRA more predictable in practice.
- Figures aid comprehension: Figure 1 gives a compact end-to-end depiction of how the delta is extracted, equalized, and reinserted, and makes the “post-hoc, norm-preserving, training-free” aspects explicit.

## Summary Of Weaknesses
1) Limited empirical scope and marginal gains
- Only one base model (Qwen3-0.6B), one LoRA configuration (r=8, α=32, dropout 0.05), and one small benchmark protocol (FOREVER, four classification tasks with 1000 training instances per task, 10 epochs) are used. This is too narrow for ACL main; it is unclear whether results transfer to larger LLMs, instruction tuning, generation tasks, or more realistic continual-learning settings.
- The main effect size is small and order-dependent: +2.3pp average BWT with p=0.059, and SVD-EQ hurts one of three orders (Table 2; Figure 2). This weakens the central claim that equalization consistently reduces forgetting.

2) Missing comparisons to strong and directly relevant baselines
- The paper omits comparisons to well-known continual-learning baselines that are compatible with LoRA or otherwise standard for CL with LMs (e.g., O-LoRA, EWC, SI, SSR). Even if the method is post-hoc, side-by-side numbers would calibrate the practical value of a +2.3pp BWT change.
- More critically, several closely related spectral or post-hoc LoRA methods are neither cited nor compared (see “Potentially Missing Related Work”). Without these, the contribution is not positioned adequately.

3) Ambiguity around the “Random-Spectrum” ablation and what it tests
- As written, “Random-Spectrum randomly permutes the singular values, preserving the norm but disrupting the spectral ordering” (Section 4.4). However, in an SVD UΣV^T, permuting diagonal entries must be paired with corresponding column permutations in U and V to remain a valid SVD of the same matrix. If, instead, the diagonal is permuted while U, V are held fixed, it defines a different matrix but not a legitimate re-ordered SVD. It is unclear which operation was done and what hypothesis is being tested. Please clarify implementation and the intended scientific interpretation.

4) Definition and handling of task-specific delta
- Section 3.3 defines ΔW_t = B_tA_t − B_{t−1}A_{t−1} and then reconstructs ΔW_t^eq and “updates cumulative LoRA parameters accordingly.” It is unclear whether equalization is applied additively to the previously accumulated LoRA, or whether the whole module is rewritten. If the prior update is subtracted and a modified version re-added, please clarify numerical stability and whether this introduces drift across boundaries, especially given the order-dependent degradation seen for Order 6 (Table 2).
- The claim “memory-free” could be better qualified. While there is no data replay, one needs access to both current and immediate-previous LoRA to compute ΔW_t at the boundary. The paper should describe the exact buffering needed and whether this can be done without extra checkpoint storage at scale.

5) Weak mechanistic analysis
- The core hypothesis in Section 3.2 is that spectral concentration amplifies interference. Yet Figure 3 explicitly shows no predictive power of ρ for improvement. The discussion does not reconcile this with the design choice of uniformization. If norm shrinkage is implicated, why is norm-preserving SVD-EQ better than norm-reducing Mean-Smoothing only marginally (+0.1pp in Table 1)? A deeper layer-wise or module-wise analysis, or sensitivity to rank r, is needed to substantiate the mechanism.
- Equation 2 and the global ρ ignore which layers dominate interference. Aggregating into a single ρ per boundary may hide structure. A per-layer scatter of ρ against per-layer contribution to forgetting would be more diagnostic.

6) Limited metrics and reporting
- The study only reports OP and BWT (Equation 1). Other standard CL metrics like forgetting (F), forward transfer (FWT), and per-task final accuracy tables are absent. Confidence intervals beyond seed stds, and calibration of whether OP changes are significant, are also missing.
- The paper states “no harm criterion” is satisfied because OP rises 63.7→64.5 (Table 1). However, no statistical test is reported for OP. Given small sample size (9 runs), this claim should be qualified.

7) Reproducibility gaps
- Appendix A says “Code will be released upon publication,” while the main text footnote provides a URL. The discrepancy makes it unclear whether the exact scripts used for the paper are available now. Beyond code, important details are missing: tokenization and prompt formatting, optimizer and LR for each task, LoRA placement beyond “query and value,” batch sizes, early stopping or validation protocols, and dataset preprocessing. Without these, exact reproduction is nontrivial.
- No runtime measurements are provided to support “negligible overhead.” Even a micro-benchmark showing QR+SVD time per layer and total wall-clock overhead relative to training or inference would help.

8) Scope of ablations
- Only two ablations are explored. Other natural variants are not tested: partial equalization (e.g., top-k singulars preserved, tail equalized), adaptive scaling of Σ to match per-layer sensitivity, per-rank stochastic equalization, or layer selection via validation.
- Rank sensitivity is not explored. Since Σ equalization depends on r, varying r and observing whether the effect scales would strengthen the claim.

9) Positioning relative to merging and CL literature
- Section 2.3 cites some merging works, but there is no empirical comparison to simple, cheap post-hoc strategies like task arithmetic over LoRA deltas, or to orthogonalization constraints that are widely used in LoRA-based CL. Without empirical baselines of this kind, the contribution remains under-contextualized.

10) Figure/Table-specific concerns and interpretations
- Figure 1 clearly illustrates the pipeline and helps justify the claim that the method is post-hoc and norm-preserving. However, the box “Output: B′, A′ (new LoRA factors)” implies refactorization after equalization. Please detail whether you re-factor ΔW_t^eq into B′A′ with the same r and how you ensure numerical stability across layers.
- Figure 2 supports the claimed variance reduction with visibly smaller error bars for Orders 4 and 5. Still, the slight degradation for Order 6 suggests the method can backfire depending on task interactions; a qualitative analysis of that order would be valuable.
- Table 1 is central: the +2.3pp BWT is modest and roughly matched by “Mean-Smoothing” (+2.2pp) which is not norm-preserving. This undermines the narrative that equalization itself is the driver, and it motivates deeper analysis.
- Table 2’s 3–10× reduction in standard deviation is compelling for stability, but this is based on only three seeds per order. Please increase seed count or provide bootstrap intervals to bolster this finding.

## Potentially Missing Related Work
1) Ling et al., “LoRA-Based Continual Learning with Constraints on Critical Parameter Changes,” 2025 — Directly addresses catastrophic forgetting in LoRA-based CL via constrained training. Should be discussed in Section 2.1 and compared empirically in Section 4 to calibrate SVD-EQ’s gains relative to constrained-update approaches.

2) Xiao et al., “Meta-UCF: Unified Task-Conditioned LoRA Generation for Continual Learning in Large Language Models,” 2026 — Proposes task-conditioned adapter generation. Add to Section 2.1 and discuss how post-hoc spectral editing contrasts with meta-learned adapter generation; optionally include as a baseline if code is available.

3) Tian et al., “Spectral Surgery: Training-Free Refinement of LoRA via Gradient-Guided Singular Value Reweighting,” 2026 — Very close to SVD-EQ in spirit; training-free SVD manipulation but gradient-informed rather than uniform. Must be cited in Section 2.2/2.3 and used as a baseline in Table 1.

4) Zhang et al., “SDC-LoRA: Singular-Subspace Drift Controlled LoRA to Mitigate Knowledge Forgetting,” 2026 — Trains with spectral calibration to control drift. Add to Section 2.2 and compare in Section 4 to distinguish training-time spectral control from post-hoc equalization.

5) Yang et al., “SLoRA: Balancing Plasticity and Forgetting in Large Language Models for Continual Learning,” 2026 — Post-hoc subspace-denoising/pruning for LoRA with strong rehearsal-free CL results. Highly relevant; cite in Section 2.3 and add as a baseline in Table 1.

6) Patil et al., “Stacked LoRA: Isolated Low-Rank Adaptation for Lifelong Knowledge Management,” 2025 — Uses stacked, frozen task adapters to limit forgetting. Discuss in Section 2.1 and consider a comparison that highlights tradeoffs between stacking vs. post-hoc editing of a single adapter.

7) Tian et al., “ReCoLoRA: Spectrum-Aware Recursive Consolidation for Continual LLM Fine-Tuning,” 2026 — Spectrum-aware consolidation across tasks is conceptually close. Cite in Section 2.3 and, if feasible, compare quantitatively.

8) Anonymous, “Task Arithmetic with LoRA for Continual Learning,” 2023 — Linear combinations of LoRA deltas for CL. Add to Section 2.3 and use as a low-cost post-hoc baseline.

9) Anonymous, “S-LoRA: Scalable Low-Rank Adaptation for Class Incremental Learning,” 2025 — Decouples direction/magnitude across tasks for scalable CL. Discuss in Section 2.1 and clarify how SVD-EQ complements or differs.

10) Zhang et al., “Spectral Disentanglement: Rank-Aware Task Adaptation for Continual Learning in Large Language Models,” 2026 — Shapes singular structure to reduce interference, closely aligned with your hypothesis. Cite in Section 2.2 and, if available, include as a baseline.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify precisely how “Random-Spectrum” is implemented. If you permute Σ but not U and V, the product defines a different matrix and is not an SVD of the original delta; if you permute all jointly, the resulting matrix is identical to the original. What hypothesis is this ablation testing and how is it implemented to isolate spectral-order effects?
- Provide a precise algorithmic description of how ΔW_t is computed and reinserted. Do you subtract B_{t−1}A_{t−1} from the current LoRA and add back the equalized ΔW_t^eq? How do you re-factor ΔW_t^eq into new LoRA factors B′, A′ for each layer while keeping rank r? Include pseudocode and any numerical stabilization strategies.
- Expand evaluation: add at least one larger model and a generative task, increase seeds, and report FWT/forgetting metrics. Include comparisons against at least one training-time method (e.g., O-LoRA/EWC/SI) and at least one post-hoc spectral baseline (e.g., gradient-guided reweighting) to position the contribution.
- Deepen mechanism analysis: provide per-layer ρ trends, examine how equalization shifts the layer-wise contribution to forgetting, and test rank sensitivity (e.g., r ∈ {4, 8, 16}). A partial-equalization variant that preserves top-1 or top-2 singular values while equalizing the tail would clarify whether interference is mainly in the head or tail of the spectrum.
- Quantify overhead: report wall-clock time and memory for QR+SVD at task boundaries relative to fine-tuning and inference. This will make the “negligible” claim concrete.

Minor issues and typos:
- Section 4.3: “6 shows slight degradation (-1.0pp)” would read more clearly as “Order 6 shows slight degradation.”
- Table 1 caption: state explicitly that ± values are across 9 runs (3 orders × 3 seeds).
- Section 4.2: you report a paired t-test for BWT; please also report a test for OP change or qualify the “no harm” statement.
- Appendix A vs. footnote ¹: one says “Code will be released upon publication,” the other links a repository. Please reconcile and ensure the exact versioned scripts used for the paper are available.
- References: ensure consistent citation formatting and years; several entries appear with future years and missing venues.

Criteria that could raise my score:
- Add the missing related baselines, especially a training-free spectral reweighting method and at least one training-time CL baseline compatible with LoRA; show clear improvements on BWT and OP with significance testing.
- Demonstrate effectiveness on a larger LLM and at least one generation task; increase the number of seeds; include additional CL metrics.
- Clarify the ablation methodology and the ΔW_t implementation details with pseudocode and release fully reproducible code and configs.

## Confidence
4: Quite sure after careful checking — I checked the important points, including equations, figures, and tables. Some implementation details are ambiguous, but the overall assessment is unlikely to change with minor clarifications.

## Soundness
2.5: Between Poor and Acceptable — The method is clear and empirically evaluated, but the scope is narrow, the gains are small and order-dependent, key baselines are missing, and some ablations and implementation details are ambiguous.

## Excitement
2.5: Between potentially interesting and interesting — Post-hoc equalization is neat and practical, and the variance reduction is attractive, but the empirical evidence is limited and not yet compelling.

## Overall Assessment
2.5 Borderline Findings — The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is simple and appealing, and the figures and tables do support some benefit (e.g., Figure 2 variance shrinkage; Table 2 per-order gains). However, empirical scope is narrow, effects are modest and order-dependent with marginal significance, and several directly relevant baselines and citations are missing. Clarifying the ablations and ΔW_t handling, expanding evaluation, and adding stronger comparisons would elevate this to a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly acknowledges limitations around order dependence and marginal significance; these could be expanded. It would also help to discuss:
- Risks of post-hoc parameter manipulations inadvertently degrading safety-aligned behaviors in LLMs, especially for generative tasks; propose guardrails or validation checks.
- Potential differential impacts across languages or domains not covered by the four English classification tasks; caution against overgeneralization.
- Reproducibility considerations for practitioners applying SVD-EQ to proprietary models without access to intermediate task checkpoints.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many details are missing or ambiguous, and it is unclear whether the exact scripts are publicly available despite the URL. With effort, one could likely reproduce trends.

## Datasets
1: No usable datasets submitted.

## Software
2: Documentary — The method is simple and code is claimed, but availability/versioning is unclear; in its current form it is primarily useful to study or replicate the reported research once clarified.