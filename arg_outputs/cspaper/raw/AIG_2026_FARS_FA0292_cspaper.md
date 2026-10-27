# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper evaluates whether using a smaller learning rate when training proxy models for supervised fine-tuning (SFT) improves how well dataset rankings transfer from a small proxy LLM to a larger target LLM. Using Qwen2.5-1.5B as proxy and Qwen2.5-7B as target across 12 math-oriented SFT datasets, the authors compare four setups: Standard-LR Proxy (5e-5), Tiny-LR Proxy (1e-5), a training-free NLL baseline, and a target “ground truth” that fully fine-tunes the 7B model. Ranking agreement is measured via Pairwise Direction Accuracy (PDA), Spearman correlation, and top-1 match. Results show Standard-LR proxies outperform Tiny-LR proxies overall, though Tiny-LR proxies align well on MATH-500 but fail on GSM8K. The authors conclude tiny learning rates do not improve proxy-to-target ranking transfer for SFT.

## Summary Of Strengths
- Clear and focused empirical question: whether tiny learning rates improve proxy-to-target dataset ranking for SFT, extending a hypothesis from pretraining to instruction tuning.
- Well-scoped experimental framework with explicit comparison conditions, succinctly depicted in Figure 1, which helps readers understand the evaluation pipeline and where PDA is computed.
- Use of multiple agreement metrics with uncertainty estimates: Table 1 reports PDA with 95% bootstrap CIs, Spearman ρ with p-values, and top-1 correctness, providing a multi-view assessment of ranking transfer.
- Useful negative result: Contrary to expectations from related pretraining literature, Tiny-LR Proxy underperforms, which is valuable for practitioners considering proxy-based data valuation.
- Benchmark-specific insight: Table 2 and Figure 3 reveal that Tiny-LR performs well on MATH-500 but poorly on GSM8K, suggesting sensitivity to evaluation regimes and surface-level features.
- The paper surfaces a practical takeaway for data curation workflows: Standard-LR proxy SFT appears more reliable than Tiny-LR for dataset ranking in this math SFT setting.
- Figure 2’s visualization effectively communicates the core result, with error bars and the random PDA baseline; it helps readers quickly assess the significance gap between Standard-LR and Tiny-LR proxies.

## Summary Of Weaknesses
1) Scope and novelty are limited. The study evaluates only two learning rates with a single proxy-target family (Qwen2.5) and a single domain (math). Given the broad claim that the tiny-LR hypothesis is “refuted” for SFT (Abstract and Section 6), the evidence is narrow. Intermediate LRs, alternative schedules, or additional families would be required to generalize confidently.

2) Potential confounds in training budgets. Standard-LR proxy uses 500 steps while Tiny-LR uses 1000 steps (Section 3.2 and Appendix B.3). Although the LR is smaller, the step-count mismatch complicates attribution of effects to learning rate alone. Equalizing either total tokens seen, optimizer updates, or effective parameter movement would strengthen causal claims. As written, conclusions about LR per se are not cleanly isolated.

3) Limited baselines for data selection. Beyond training-free NLL, there are no comparisons to contemporary and relevant data selection or proxy methods used for SFT dataset valuation. The study would be stronger by including influence-based, trajectory-based, diversity-based, and random/heursitic selectors commonly examined in SFT data selection work. This omission makes it hard to position the observed behaviors relative to strong alternatives.

4) Incomplete reporting of per-dataset performance values. Table 3 lists only ranks, not the underlying composite or per-benchmark scores, nor standard deviations across seeds. This hinders diagnosis of effect sizes and noise levels, and it prevents external checks (e.g., computing Kendall’s τ, or testing if top-1 differences are within error bars).

5) Statistical analysis needs more rigor and consistency. 
- For PDA, 95% CIs are bootstrapped “over dataset pairs” (Section 3.3), but the resampling unit and stratification across seeds are not fully specified, which matters given dependence between pairs induced by shared datasets. 
- Reported p-values for Tiny-LR on MATH-500 are inconsistent: the Abstract says “PDA = 0.818, p = 0.846,” while Table 2 and Figure 3(b) indicate ρ = 0.846 with p = 0.0005. This inconsistency calls for correction.
- Multiple comparisons across methods and scopes are not adjusted.

6) Overstated interpretation relative to evidence. The paper states it “refutes the hypothesis” that tiny LRs improve transfer. The current evidence shows one task family, two benchmarks, two LRs, and a single proxy-target pair. A more cautious phrasing like “does not support” would be appropriate, especially given the strong per-benchmark success on MATH-500.

7) Limited analysis of the claimed mechanism. Section 4.3 attributes GSM8K failures to surface-level features like response length and formatting, but this is not quantitatively substantiated. There is no correlation analysis between response length and rank, no controlled decoding experiments (e.g., constraining output length or applying formatting normalization), and no GSM8K re-scoring with math-aware normalization. Concrete evidence would be needed to support the mechanism.

8) External validity is unclear. 
- Only math datasets are tested. Claims about SFT in general require at least some coverage of other domains (code, general instruction following, safety/alignment datasets).
- Only LoRA with a fixed configuration is evaluated. Results could depend on adaptation method and its capacity.

9) Evaluation design could better align with “transfer” questions. The “ground truth” target uses 2,000 steps at 5e-5. It would be informative to include target runs at different LRs or step counts to test whether the proxy alignment depends on target hyperparameters as well, or to test a second target model size to see if findings scale.

10) Figures and tables are informative but leave out crucial diagnostics. 
- Figure 2’s error bars are helpful but do not show seed-level variance or per-benchmark breakdown beyond Tiny-LR. A parallel bar plot for Standard-LR across GSM8K vs MATH-500 would clarify whether the asymmetry is unique to Tiny-LR.
- Table 1 mixes PDA CIs with p-values for Spearman, but no p-values for PDA or a consistent inferential framework across metrics is provided.

11) Missing important related work that directly bears on proxy alignment and SFT data selection (see next section). This hurts positioning and leaves out competitive baselines that could materially shift conclusions.

Overall, while the core negative result for this particular setup is useful, the above issues, particularly the confound between LR and steps, limited baselines, inconsistent statistics, and narrow scope, prevent strong conclusions and reduce confidence in generality.

Explicit figure/table comments:
- Figure 1 clearly lays out the four conditions and where PDA is measured. However, it masks the compute mismatch between Standard-LR (500 steps) and Tiny-LR (1000 steps). Since the figure is used to communicate experimental parity, it should footnote or color-code the unequal budgets to avoid misleading readers about fairness.
- Figure 2 supports the main claim: Standard-LR’s PDA bar is above the dashed random baseline with non-overlapping CIs relative to 0.5, whereas Tiny-LR hovers near chance. This is convincing at the aggregate level, but it would be strengthened by adding per-benchmark bars for Standard-LR for symmetry with Tiny-LR’s breakdown in Figure 3.
- Figure 3(a,b) are central to the paper’s narrative that Tiny-LR behaves differently across MATH-500 vs GSM8K. The large ρ on MATH-500 in Fig. 3(b) contrasts sharply with the near-zero ρ on GSM8K. This visualization backs the benchmark-specific thesis, but without analogous breakdowns for Standard-LR or any analysis tying this to response length quantitatively, the mechanistic interpretation remains speculative.
- Table 1 is a good high-level summary and correctly emphasizes that Standard-LR achieves the best PDA and top-1 match. However, the absence of PDA p-values and details of the bootstrapping procedure make it hard to evaluate significance claims uniformly.
- Table 2 shows strong Tiny-LR alignment on MATH-500. The table would benefit from also listing Standard-LR’s per-benchmark numbers side by side to support the statement that Tiny-LR “nearly matches Standard-LR” on MATH-500.
- Table 3 provides full ranks, which is helpful for qualitative inspection, but raw accuracies and variances are needed to evaluate if rank differences are statistically meaningful.

## Potentially Missing Related Work
1) Chen et al., “Influence-Preserving Proxies for Gradient-Based Data Selection in LLM Fine-tuning,” 2026 — Directly targets proxy-to-target alignment with influence-preserving small models, highly relevant to this paper’s central question. Should be discussed in Section 2.2 and compared empirically or at least conceptually in Section 4 to clarify how learning-rate-based proxy choices differ from influence-preserving construction.

2) Yang et al., “SmallToLarge (S2L): Scalable Data Selection for Fine-tuning Large Language Models by Summarizing Training Trajectories of Small Models,” 2024 — Provides a trajectory-based proxy signal for dataset selection. Should be added to Related Work (Section 2.2) and, if possible, added as a baseline or discussed in Section 5 to contextualize tiny-LR signals versus loss-trajectory clustering.

3) Xia et al., “Rethinking Data Selection at Scale: Random Selection is Almost All You Need,” 2024 — Argues that simple random selection often competes with complex selectors. Should be cited in Section 2.1/2.2 and used to motivate additional baselines in Section 4, particularly a random-permutation ranking or random-subset baseline to calibrate the utility of proxy-based ranking.

4) Wang et al., “Diversity Measurement and Subset Selection for Instruction Tuning Datasets,” 2024 — Proposes gradient-space diversity metrics and DPP-based selection. Should be discussed in Section 2.1 and considered in Section 4 as an alternative, diversity-aware ranking baseline.

5) Cheng et al., “Task-Aware Data Selection via Proxy-Label Enhanced Distribution Matching for LLM Finetuning,” 2026 — Task-conditioned data selection with proxy labels and distribution alignment. Add to Section 2.1/2.2 and discuss in Section 5 as a complementary approach that might behave differently across GSM8K vs MATH-500.

6) Schoch et al., “Data Selection for Fine-tuning Large Language Models Using Transferred Shapley Values,” 2023 — A canonical proxy-based valuation method using Shapley values. Should be included in Section 2.2 and, resources permitting, referenced as a comparison point in Section 4.

7) Liu et al., “Tuning Language Models by Proxy,” 2024 — Although focused on steering rather than dataset ranking, it shares the idea of leveraging small proxies to guide large LMs; include in Section 2.2 for conceptual context.

8) Yang et al., “Let the Target Select for Itself: Data Selection via Target-Aligned Paths,” 2026 — Defines a target-aligned path scoring rule directly addressing alignment issues that this paper studies. Add to Section 2.2 and discuss in Section 5 how path-aligned scoring compares to learning-rate-based proxies.

## Comments Suggestions And Typos
Actionable suggestions:
- Control for training budget confounds. Re-run Standard-LR and Tiny-LR with matched token budgets, identical step counts, or matched cumulative update magnitude (e.g., integrate squared update norms) so that learning rate is the only manipulated factor. Report both step-normalized and token-normalized settings.
- Expand baselines. Add at least one influence-based method (e.g., TracIn/LESS variant on your setup), a trajectory-based selector (S2L-style), a diversity-based selector, and a strong “random or heuristic” baseline to contextualize PDA and Spearman results. Even if full implementations are heavy, a subset of datasets or a compute-matched slice would strengthen claims.
- Report raw accuracies with uncertainty. For each method and dataset, include GSM8K and MATH-500 accuracies with mean ± standard deviation across seeds in the main text or an appendix table, and provide rank stability analyses (e.g., Kendall’s τ confidence intervals).
- Firm up statistics. 
  - Clarify the bootstrap scheme for PDA CIs, including whether resampling is over datasets, pairs, or seeds, and how dependence is handled. 
  - Correct the inconsistent p-value statements for Tiny-LR on MATH-500 between Abstract and Table 2/Figure 3(b). 
  - Consider reporting permutation-test p-values for PDA, and adjust for multiple comparisons where applicable.
- Substantiate the mechanism. Provide a quantitative analysis linking response length and formatting to GSM8K rank preferences. Examples: (i) plot correlation between average response length per dataset and its GSM8K rank under Tiny-LR; (ii) normalize GSM8K outputs via formatting rules or length caps and re-evaluate; (iii) ablate decoding strategies to equalize verbosity; (iv) run GSM8K with math-aware evaluation to test sensitivity.
- Widen scope or temper claims. Either extend to another domain/target family or soften the language from “refute” to “does not support in this setup,” reflecting the limited scope.
- Figure improvements. Add per-benchmark bars for Standard-LR in an analog of Figure 3 to show whether Tiny-LR’s asymmetry is unique. In Figure 1, annotate training steps per condition to make compute differences explicit.
- Clarify LoRA application. You state LoRA is applied to all attention and MLP projections (Appendix B.2). Report the total number of trainable parameters and verify that adaptation capacity is not a hidden confound across LRs.

Typos and minor issues:
- Abstract/Page 1: “p = 0.846” attached to Tiny-LR’s MATH-500 PDA appears inconsistent with Table 2/Figure 3(b), which show ρ = 0.846, p = 0.0005. Please fix.
- Section 4.2/Page 5: Ensure consistent notation for math-verify vs math_verify.
- Table captions: Consider adding “higher is better” and the number of datasets (K = 12) for clarity.

Criteria to raise my score:
- Provide compute-controlled comparisons demonstrating that LR itself, not step or token differences, drives the result.
- Add at least one strong contemporary baseline from influence-, trajectory-, or diversity-based selectors, and show Tiny-LR vs Standard-LR conclusions persist.
- Supply raw per-dataset accuracies with uncertainty and a more rigorous statistical treatment resolving the p-value inconsistency.
- Include quantitative evidence supporting the response-length/formatting mechanism on GSM8K, ideally with mitigation experiments that change the observed behavior.

## Confidence
4: Quite sure after careful checking — I checked the key claims, figures, and tables carefully; remaining uncertainty is mainly about unreported details and limited scope.

## Soundness
3: Acceptable — The study supports its main empirical claim for the tested setup, but confounds (LR vs steps), incomplete baselines, and statistical inconsistencies weaken rigor.

## Excitement
2.5: Between potentially interesting and interesting — Useful negative result, but narrow scope and analysis gaps limit broader excitement.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The negative result about Tiny-LR proxies not transferring for SFT is practically relevant, and the benchmark-specific behavior is interesting. However, compute confounds, missing strong baselines, inconsistent statistics, and lack of mechanism substantiation reduce confidence. With tighter controls, broader comparisons, and clearer statistical reporting, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a limitations section noting single-family focus, math-only scope, and only two LR settings. Additional points to consider:
- Environmental/compute impact: Multiple fine-tuning runs over 12 datasets and several seeds can be compute intensive; reporting total FLOPs or energy estimates would be responsible.
- Bias and representation: Math-focused findings may not transfer to data with sensitive attributes or to multilingual settings; discuss how proxy-based ranking could inadvertently prioritize superficial patterns that disadvantage certain genres or languages.
- Dual use: Dataset ranking methods could be used to over-optimize for specific leaderboard formats; note risks of overfitting to evaluation artifacts.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Models, datasets, and many hyperparameters are specified; the released code is referenced. Still, missing raw per-dataset scores, incomplete statistical details, and ambiguity in bootstrapping reduce reproducibility.

## Datasets
1: No usable datasets submitted. — No new dataset contribution.

## Software
3: Potentially useful. — If the referenced code is indeed available and runnable, it could be useful for reproducing the workflow, though broader utility is limited without stronger baselines and diagnostics.