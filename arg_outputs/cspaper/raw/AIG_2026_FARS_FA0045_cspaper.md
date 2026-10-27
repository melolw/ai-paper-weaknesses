# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies example selection for repetition-heavy supervised fine-tuning of long chain-of-thought (CoT) reasoning. It scores pool examples by per-token negative log-likelihood (NLL) under a base model, builds length-matched subsets from the lowest-NLL and highest-NLL extremes, and repeats each subset for many epochs. Using OLMo3-7B and 800-example subsets trained for 32 epochs, it reports that high-NLL (hard-to-fit) examples outperform low-NLL (easy-to-fit) examples on AIME 2024, AIME 2025, and GPQA Diamond. The authors attribute the gap partly to termination behavior and to a confound in low-NLL examples that have higher textual repetition. Figure 1 diagrams the pipeline, Table 1 shows main results, Figure 2 shows termination rates, and Table 2 reports optimization attempts that failed to rescue low-NLL performance.

## Summary Of Strengths
- Clear, focused empirical question tightly scoped to a concrete training regime: for small datasets with many epochs, which examples should be repeated.
- The methodology for length-matched selection is sensible and visually communicated well in Figure 1. Partitioning by length deciles before ranking by NLL is a reasonable first-order control for length-NLL correlation.
- The results are coherent across multiple metrics and tasks. In Table 1, high-NLL subsets outperform low-NLL on AIME 2024, AIME 2025, and GPQA Diamond, with consistent advantages on Avg@k, Pass@k, and termination rate.
- The termination-focused analysis is informative. Figure 2 makes a concrete, interpretable point: high-NLL-trained models terminate more reliably, which plausibly mediates the accuracy gains.
- The paper is written clearly and is easy to follow. Equation (1) precisely defines the NLL scoring used for selection, making the selection criterion unambiguous.
- Practical takeaway is crisp: under repetition-heavy long-CoT SFT, prefer hard examples over easy ones.

## Summary Of Weaknesses
1) Limited scope and generality. Only one base model (OLMo3-7B) and one training dataset (Dolci-Think) are used. The claims are framed as general guidance, but Section 5 acknowledges this limitation without mitigation. The conclusion would be more convincing with at least a second base model or an additional CoT corpus.

2) Selection design restricted to extremes. The study compares only the two extremes of NLL plus random. There is no analysis of middle quantiles, mixtures, or continuous sampling policies. This matters because conclusions about “hard examples beat easy ones” could in practice favor a blend or a particular high-NLL band rather than the absolute top tail. Given the design in Section 3.3, at least a mid-NLL decile or a monotone trend analysis would help establish whether the effect is monotonic or thresholded.

3) Potential confounds beyond length and trigram repetition. While length decile matching controls length, and Section 4.3 addresses trigram repetition partially, other properties likely correlate with NLL, for example:
   - Answer-format regularity and lexical formulaicity beyond trigrams.
   - Domain composition shifts across deciles.
   - Presence and placement of <think> tags or other scaffolding tokens.
   The paper does not quantify or balance these additional factors, so attributing the effect solely to hardness plus repetition is premature.

4) Termination measurement and decoding details under-specified. Termination rate is central to the causal narrative. However, Section 3.4 and 4.2 do not specify decoding parameters such as max tokens, temperature, nucleus or top-k sampling, or enforced stop sequences for <think> and final answers. If decoding truncation length or temperature differs by seed or is not tuned equally, termination rates in Figure 2 and Table 1 could reflect decoding configuration rather than learned behavior. Precise decoding configs are needed to interpret termination causally.

5) Validation and model selection procedure unclear. Section 3.4 states that the “best checkpoint is selected by validation loss,” but it does not define the validation set composition or whether it is disjoint from the training pool and test benchmarks. If the validation set overlaps with the selected low- or high-NLL subsets or is drawn from the same decile distributions in a biased way, early stopping may differentially favor certain selection strategies.

6) Statistical rigor is limited. Table 1 uses 3 seeds for Low-NLL and High-NLL and 6 for Random, with large standard deviations for Low-NLL. A single bootstrap interval is cited in Section 4.1, but the bootstrap procedure is not described, and test sizes are small (AIME has 30 problems). Reported variance suggests instability, and uneven seed counts across conditions make comparisons less clean. More seeds, matched across all conditions, and reporting confidence intervals in the tables would strengthen claims.

7) Fairness of optimization attempts in Table 2. Only the Low-NLL condition receives hyperparameter and filtering variants, and both variants reduce performance. While this is informative for the authors’ thesis, the comparison risks asymmetry. For example, would high-NLL also degrade under epochs=8 or benefit from alternative regularization. The narrative that Low-NLL is fundamentally limited would be stronger if symmetric sweeps were provided for all conditions or if tuning was done via a held-out grid search per condition with the same search space.

8) Insufficient detail to reproduce core setup. Training hyperparameters in Section 3.4 are partial: optimizer type, gradient clipping, dropout, EOS token handling with <think> tags, stop sequences, and data preprocessing are not fully documented. Exact targets for NLL scoring (e.g., whether intermediate tool- or math-specific tokens are masked) are unclear beyond “mask prompt tokens.” Without these, reproducing the exact behavior, particularly termination, is difficult.

9) Aggregation metric definition not fully specified. Table 1 reports an “Agg.” score. The definition of the aggregate accuracy metric is not described, including weighting across benchmarks that differ in size and difficulty. This impedes cross-condition interpretability.

10) Missing or weak baseline comparisons to selection literature. The method uses simple NLL extremes. Many recent instruction tuning selection methods directly target difficulty, diversity, or influence. Section 2 cites some related work, but there is no empirical comparison against at least one modern alternative appropriate for reasoning or long-CoT. This weakens the methodological significance.

11) Causal interpretation overreach. Section 5 attributes low-NLL failure largely to textual repetition and open-ended generation. Table 2’s trigram filtering partially addresses repetition but the intervention affects only the Low-NLL subset, and it simultaneously changes the selection pool’s hardness profile and content distribution. Without controlled interventions that hold hardness fixed while manipulating repetition and vice versa, claims about mechanisms remain speculative.

12) Minor exposition issues. References include several entries with compressed formatting and missing venue details. Some citations appear future-dated relative to widely available literature. This does not by itself invalidate the results but reduces clarity and scholarly polish.

Figure- and table-specific comments:
- Figure 1: The three-stage diagram is helpful. However, it shows “80 examples per decile” and “32 epochs” as fixed. Adding a small inset sensitivity plot or clarifying that these are design choices, not tuned optima, would prevent over-reading the defaults as recommended settings.
- Figure 2: The termination gap is striking and supports the paper’s main argument. Still, without decoding details and stop sequence handling, it is hard to determine whether the gap stems from training or inference configuration. Reporting the same plot with controlled max tokens and temperature, and a second plot varying max tokens, would clarify robustness.
- Table 1: Central to the paper’s claim. It would benefit from confidence intervals on Avg@k and Pass@k, matched seed counts across rows, and an explicit definition of “Term%.” Given the small test sizes for AIME, displaying per-problem bootstrap or stratified confidence intervals would increase trust.
- Table 2: Useful but asymmetric. The low-epoch variant confounds two changes at once (epochs and lr) plus weight decay. Independent ablations per factor would be more informative. Also, applying analogous ablations to High-NLL would show whether the condition is generally robust or merely benefits from the chosen default.

## Potentially Missing Related Work
1) Wang et al., A Survey on Data Selection for LLM Instruction Tuning, 2024 — Comprehensive taxonomy of selection methods that directly contextualizes difficulty-based and NLL-based strategies. Should be cited in Section 2.1 and used to position why an NLL-extremes approach is selected over influence-based or multi-criteria methods.

2) Liu et al., What Makes Good Data for Alignment? A Comprehensive Study of Automatic Data Selection in Instruction Tuning, 2024 — Empirical analysis of quality, complexity, and diversity signals. Relevant for Section 2.1 and Discussion to compare whether the reported benefits from high-NLL might instead be captured by diversity or complexity indicators and to motivate additional baselines.

3) Xia et al., LESS: Selecting Influential Data for Targeted Instruction Tuning, 2024 — Influence-function-based targeted selection, relevant to reasoning capabilities. Should be discussed in Section 2.1 and considered as a baseline or at least as a comparison point in Section 4.

4) Mekala et al., Smaller Language Models are capable of selecting Instruction-Tuning Training Data for Larger Language Models, 2024 — Demonstrates small-to-large data selection for hard examples. Add to Section 2.1 and consider its selection signals as an alternative to NLL in Section 4.

5) Song et al., IterSelectTune: An Iterative Training Framework for Efficient Instruction-Tuning Data Selection, 2024 — Iterative selection-finetuning loop. Discuss in Section 2.1 and contrast with this paper’s static selection; optionally include a simple iterative baseline.

6) Huang et al., Multi-view fusion for instruction mining of large language model, 2024 — Multi-criteria selection operationalizing difficulty and quality. Include in Section 2.1 and relate to the trigram-repetition confound in Section 5.

7) Yu et al., Cold-Start Data Selection for Better Few-shot Language Model Fine-tuning: A Prompt-based Uncertainty Propagation Approach, 2023 — Uncertainty-driven selection under strict budgets. Mention in Section 2.1 as a different hardness proxy that could be explored in repetition-heavy regimes.

8) Shang et al., THTB: A Cognitive-Difficulty-Aware Framework for Instruction Data Selection in Supervised Fine-Tuning of Large Language Models, 2026 — Cognitive-difficulty-aware selection, highly relevant to the hard-vs-easy framing. Discuss in Section 2.1 and compare to NLL hardness in Section 4.

9) Pikus et al., Hard Examples Are All You Need: Maximizing GRPO Post-Training Under Annotation Budgets, 2025 — Converging evidence that hard-example selection is advantageous for reasoning in a GRPO setting. Cite in Section 2.2 or 2.3 and relate findings in Section 5.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide full decoding details that were used for all evaluations: sampling strategy, temperatures, top-p or top-k, max tokens, stop sequences including <think> tags and final answer formats, and whether EOS was constrained. Since termination is central, controlled decoding is essential.
- Define the aggregate metric used in Table 1. Specify whether it is a macro-average across benchmarks or a weighted average by number of problems, and justify the choice.
- Expand the experimental section with:
  - A mid-NLL selection condition and at least one mixture (e.g., 50 percent high-NLL + 50 percent mid-NLL), or a monotone sweep across NLL quantiles.
  - A small sensitivity analysis for subset size n and epoch count E, to test whether the hard-example advantage persists across repetition budgets.
  - Symmetric hyperparameter sweeps for all selection strategies, or a shared tuning protocol with a held-out validation set clearly disjoint from training and test.
- Add at least one alternative selection baseline beyond random and NLL extremes, for example LESS (influence-based), a multi-criteria selector, or uncertainty-based selection. Even a lightweight approximation would strengthen positioning.
- Deepen the analysis of the repetition confound:
  - Report additional diversity measures (distinct-3, type-token ratio, entropy) and structured format features (e.g., markers for step lists, algebraic templates).
  - Conduct ablations that manipulate repetition while approximately holding NLL fixed, and vice versa, to support or refute the causal story.

Typos and formatting:
- Several references on Page 7 are concatenated without proper separators, and some lack venue details. Please correct citation formatting.
- In Section 3.2, clarify the text around Equation (1) to ensure consistent typography for subscripts and tokenization notes.
- In Section 4.1, “bootstrap 95% CI: [3.27, 20.36]” should include a brief description of the bootstrap unit and resampling procedure.

Criteria that could raise my score:
- Add a second base model and, if feasible, a second long-CoT dataset to test generality.
- Include mid-quantile and mixture selections and at least one modern selection method baseline.
- Provide full decoding and validation details and re-run with matched seeds across all conditions, reporting confidence intervals in Table 1.
- Strengthen the causal analysis with controlled interventions on repetition vs hardness.

## Confidence
3: Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5: Between Poor and Acceptable — The main empirical trend appears real in this setup, but limited scope, incomplete experimental controls, and missing details on decoding and validation reduce the strength of the evidence.

## Excitement
2.5: Between potentially interesting and interesting — The message is practical and timely for repetition-heavy long-CoT SFT, but the study is narrow and misses key baselines.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The central empirical insight, supported by Table 1 and Figure 2, is interesting and useful. However, the work is narrowly scoped to one model and dataset, lacks stronger baselines and mid-quantile analyses, and omits key decoding and validation details. With the suggested additions and clearer controls, this could reach a solid Findings contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper notes limited generalization across models and datasets. Additional points to discuss:
- Potential for overfitting to specific reasoning styles introduced by hand-curated or internet-scraped CoT traces, with downstream brittleness on out-of-domain tasks.
- If termination is improved by selecting hard examples, it might also amplify model confidence or verbosity. Discuss how this interacts with hallucination risk when applied to non-math domains.
- Language and domain coverage: if the Dolci-Think corpus is monolingual and skewed to certain scientific and mathematical styles, discuss implications for more diverse user populations.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Some core details are missing, especially decoding settings and validation protocol. The method is otherwise straightforward and the selection criterion is clear.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If the promised code is available and documents selection and training, it will help others probe repetition-heavy regimes, though missing details may still require guesswork.