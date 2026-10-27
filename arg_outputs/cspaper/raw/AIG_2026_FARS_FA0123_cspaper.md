# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper investigates whether previously reported gains from repeating a small, curated dataset for long chain-of-thought (CoT) supervised fine-tuning are simply a byproduct of higher training compute when comparisons are matched on optimizer steps. The authors propose token-budget matching, which early-stops the repetition setting once its cumulative response tokens equal the baseline’s token budget, and verify compute parity with a ΣL^2 FLOPs proxy. Using Qwen2.5-1.5B-Instruct trained on NuminaMath-CoT, they compare three settings: data scaling (51.2k unique samples), step-matched repetition (1.6k × 32 epochs), and token-matched repetition (1.6k, early-stopped to match tokens). Results on AIME’24/’25 and GPQA Diamond show token-matched repetition yields the best Acc@k and Pass@k and, notably, dramatically higher termination rates. An accuracy decomposition suggests the effect is driven by termination behavior rather than conditional accuracy.

## Summary Of Strengths
- Clear and targeted methodological contribution: token-budget matching to control compute in long-CoT SFT comparisons. The compute-control idea is simple, actionable, and directly addresses a plausible confound in prior step-matched comparisons.
- Good attention to compute verification: the paper tracks token deviation and a FLOPs proxy based on ΣL^2; Table 3 reports tight matching (0.50% tokens, 0.56% FLOPs), which strengthens the main claim that gains are not from extra compute.
- Strong, consistent empirical improvements under the token-matched setting across three benchmarks and multiple metrics. Table 1 shows Condition C outperforming both A and B on all reported metrics, including large gains on GPQA.
- Mechanism analysis is thoughtful and falsifiable: Table 4 decomposes accuracy into termination versus conditional accuracy and finds the improvements driven by termination. Figure 2 visually supports this interpretation, showing an 87–91% termination rate under token-matched repetition versus 29–55% otherwise.
- The decision-rule framing is explicit and pre-registered in spirit: Section 3.4 defines a quantitative threshold for “compute-confound refuted,” and Table 2 applies it.
- Figures are informative: Figure 1 clearly lays out the three training regimes and the early-stopping criterion; Figures 3a/3b provide training dynamics consistent with the narrative that repetition rapidly memorizes the small set, while the large, diverse dataset remains far from saturation.

## Summary Of Weaknesses
1) Compute matching excludes prompt tokens; termination changes effective lengths
- Section 3.2/3.3 state token matching is on response tokens only, and Table 3 reports response-token and ΣL^2 proxies. However, in standard SFT, both prompts and responses contribute to compute. Matching only responses can still leave a compute mismatch if prompt lengths differ across conditions (e.g., different input distributions per epoch or positional effects across repeated passes). This matters because termination rates and output-length distributions can shift teacher-forcing lengths, altering the ΣL^2 distribution in ways not captured if prompts are omitted. Please justify excluding prompt tokens and quantify prompt-token and total-sequence L and ΣL^2 parity.

2) The decision rule threshold and aggregation are ad hoc
- Section 3.4 sets 0.8 as the cutoff for “confound refuted” without principled derivation or sensitivity analysis. Table 2 then uses an “aggregate Pass@k” metric that is not defined precisely in the main text (how are benchmarks weighted? by instances or averaged per dataset?). The main headline ratio 6.33 depends on this aggregation. Provide a principled justification for the 0.8 threshold, define aggregation precisely, and run sensitivity analyses (e.g., per-dataset ratios, median-based aggregates, and confidence intervals over seeds).

3) Limited scope: single base model, single training corpus, three test sets
- The entire study uses Qwen2.5-1.5B-Instruct and NuminaMath-CoT with a specific curated 1,600-sample subset. The conclusion that “data curation and repetition outperform data scaling” may not generalize to larger models (where length-compute effects are more severe), different domains, or non-math reasoning. This limitation is acknowledged in Section 5 but it is central. At least one additional base model and one non-math dataset would substantially strengthen external validity.

4) Mechanism claims could conflate termination with answer-format induction
- Table 4 shows Acc|Term either comparable to or worse than the data-scaling baseline in two of three datasets, while termination skyrockets in Condition C. This supports the claim that repetition teaches “complete, decisive reasoning chains,” but may alternatively reflect stronger induction of a specific answer-format/template and termination token behavior. Without qualitative or length-distribution analysis of reasoning and final-answer formatting, the conclusion risks overstating “decisive reasoning” rather than “better termination control.” Add analyses: distribution of generated lengths, proportion of over-threshold truncations, and qualitative examples of where C succeeds/fails versus A/B; include error modes where termination is correct but content is wrong.

5) Missing ablations on repetition degree and data selection bias
- Figure 3 and Table 1 suggest heavy memorization of the 1.6k subset. Yet we do not see how performance varies with repetition epochs (e.g., 8×, 16×, 24×) under the same token-matched protocol or with alternative curated subsets of different average lengths/qualities. Because the 1.6k set is reported to have longer solutions, it likely alters the training distribution of target lengths. Ablating:
  - different repetition factors under token matching,
  - a short-CoT subset matched in topic but with shorter solutions,
  - mixtures of short/long traces at the same token budget,
would clarify whether “repetition per se” is the driver or whether the key is the length/template bias of the chosen subset.

Detailed figure- and table-based comments
- Figure 1: The diagram is effective in clarifying that Condition C stops at the data-scaling token budget, yet it implicitly assumes equal prompt compute across conditions. Please extend the schematic or caption to clarify whether prompt tokens are tracked, and if not, why not.
- Figure 2: Termination bars dominate the story, but the y-axis scale and absolute differences underscore a potential metric collapse: a model can win by merely terminating reliably with templated final answers, even if content accuracy per terminated sample does not improve. Pair Figure 2 with a panel showing median/quantile output lengths by condition to demonstrate a true behavioral shift rather than only termination token control.
- Figures 3a/3b: The loss and token-accuracy curves show near-complete memorization for B/C and much lower for A. This visual supports that repetition memorizes the small set. However, it also raises the question of overfitting and content diversity: please relate these curves to generalization by reporting in-distribution vs. out-of-domain behavior or at least length-normalized accuracy.
- Table 1: Results are consistently better for Condition C, with particularly large gaps in GPQA Pass@4 and termination rate. Please report statistical tests over seeds for key comparisons and ensure the same decoding parameters and max generation lengths are used across conditions, since termination is sensitive to these settings.
- Table 3 and Equation in Section 3.3 (ΣL^2): Good proxy, but please also report ΣL and optionally a more complete FLOPs model including attention and MLP terms to show robustness of matching conclusions.
- Table 4: The decomposition is the strongest piece of evidence about mechanism. It also reveals the potentially uncomfortable fact that Acc|Term is sometimes lower for C. Please discuss practical implications: for users who can afford reranking or majority vote among terminated samples, how should they weigh C’s trade-off?

## Potentially Missing Related Work
1) Wang et al., “M1: Towards Scalable Test-Time Compute with Mamba Reasoning Models,” 2025 — studies efficient long reasoning under compute constraints with alternative sequence models; discuss in Section 2 and compare in Section 4 as a complementary path to efficient long-CoT behavior under token budgets.

2) Balaji et al., “Evaluating the Safety and Skill Reasoning of Large Reasoning Models Under Compute Constraints,” 2025 — analyzes reasoning-length constraints and their impact on skill and safety; cite in Section 2 and discuss alongside your termination findings (Sections 4.1/4.4), especially regarding safety trade-offs when models are encouraged to terminate decisively.

3) Shi et al., “Rethinking Supervised Fine-Tuning: Emphasizing Key Answer Tokens for Improved LLM Accuracy,” 2025 — introduces SFTKey to reweight answer tokens post-CoT SFT; relevant to your termination-centric behavior. Compare in Section 4.4 and consider as an ablation/baseline emphasizing termination and key tokens versus repetition.

4) Long et al., “Long-Short Chain-of-Thought Mixture SFT Eliciting Efficient Reasoning in LLMs,” 2025 — proposes mixing long and shortened CoT traces to reduce overthinking while preserving accuracy; directly related to your mechanism findings. Discuss in Section 2 and, if possible, add a comparison or ablation under the same token budget in Section 4.

## Comments Suggestions And Typos
Actionable questions and suggestions
- Report total-sequence compute matching: Include prompt tokens in both token and ΣL^2 accounting. Add a table mirroring Table 3 with total lengths and ΣL^2_total to preclude residual compute confounds.
- Clarify aggregation and statistics: Define “aggregate Pass@k” precisely, add per-benchmark confidence intervals or nonparametric tests across seeds, and provide sensitivity analyses for the decision-rule threshold and aggregation weighting.
- Add ablations: Vary repetition epochs under token matching; test at least one short-CoT curated subset; and include an LS-mix baseline (e.g., per Long et al.) to decouple “repetition” from “length bias.”
- Extend scope: Include a second model family or parameter scale, and one non-math long-reasoning dataset to establish external validity.
- Qualitative and length analyses: Provide length-distribution shifts, typical success/failure cases, and examples where termination is correct but reasoning is vacuous, to support the “decisive reasoning” interpretation.

Typos/clarifications
- Page 1, Abstract: “amplified 6.33× (Δ_tok/Δ_step ratio on aggregate Pass@k)” — define “aggregate Pass@k” where first introduced.
- Page 3, “with a tolerance of ±0.5%. This results in approximately 49,541 training steps (96.8% of Condition B's 51,200 steps), corresponding to roughly 31.96 epochs” — consider adding the exact steps at which warmup ends in C to make schedules comparable.
- Table 1 caption: specify that means and standard deviations are across three seeds.
- Section 3.5: State max generation length and stop conditions, and confirm identical decoding hyperparameters across conditions.
- Table 4 formula: you state Acc@k ≈ Termination% × Acc|Term; consider showing the small residual if any, due to finite-sample estimation.

Criteria that could increase my score
- Provide total-sequence compute matching and sensitivity analyses showing the headline conclusions are unchanged.
- Add at least one ablation on repetition degree or a long-short mixture baseline under identical token budgets.
- Include a second model or dataset to establish generality.
- Strengthen statistical reporting and clarify the aggregation method for the decision rule.

## Confidence
4: Quite sure after careful checking — I verified the main methodological and empirical points and cross-checked figures/tables, though generality beyond the presented setup remains uncertain.

## Soundness
3.5: Between Acceptable and Strong — The compute-control methodology and verification are solid, and tables/figures support the claims; however, excluding prompt tokens from matching and an ad hoc decision threshold reduce rigor, and scope is narrow.

## Excitement
3.5: Between interesting and exciting — The token-budget matching idea is useful and the termination-centric mechanism is insightful, though the study is limited to one model/dataset family.

## Overall Assessment
3.5 Borderline Conference: Solid methodological idea with compelling empirical patterns and careful compute verification, but scope and analysis gaps prevent a clear accept. With added ablations, broader validation, and total-sequence compute matching, this could be a strong conference paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly notes limitations (single model and benchmarks). A fuller discussion would help:
- Generalization risks: Encouraging decisive termination without improving conditional accuracy may amplify confidently wrong answers, which can mislead users in high-stakes settings.
- Safety: Faster termination and templated answer formats may bypass internal checks or safety scaffolding if not monitored, especially under sampling.
- Data provenance: Please confirm NuminaMath-CoT licensing and any filtering that avoids leakage with AIME-style test sets.
- Fairness/coverage: Long-CoT SFT on math may not translate to other domains or languages; clarify applicability to multilingual or resource-lean settings.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Training details, seeds, and datasets are specified; code is reported as available. Matching prompts and full-sequence FLOPs would further reduce ambiguity.

## Datasets
2: Documentary — No new dataset is introduced; existing datasets are used appropriately.

## Software
4: Useful — If released as claimed, the token-budget-matching and logging scripts would be valuable for future SFT comparisons.