# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies soft prompt tuning for FLAN-T5 in few-shot classification and reports two empirical observations: (i) during training, prompt token embeddings become more similar to label token embeddings; (ii) cross-attention from the predicted token to prompt tokens increases after tuning. Based on these, the authors propose Prompt Tuning Refactoring (PTR) with three components: initialize prompt tokens with label embeddings, add “bridge” tokens computed from label-related keywords to facilitate information flow, and apply a sharp-to-smooth cross-attention schedule by annealing a temperature in softmax. Experiments on AGNews, SST-2, TREC, and Amazon-5 with 128-shot training show that PTR improves over standard prompt-tuning initializations and is competitive with LoRA and prefix-tuning under similar or fewer trainable parameters.

## Summary Of Strengths
- Empirical analysis with explicit measurements: Equation (1) and Figure 1 quantify the increase of dot-product similarity between prompt tokens and label tokens over training, providing a concrete, easy-to-replicate diagnostic. Figure 2 complements this by comparing pre-/post-tuning cross-attention to prompt vs text tokens via Equations (2)–(3).
- Clear, simple methodological ideas: The label-based initialization and temperature-annealed attention in Equation (4) are straightforward to implement for encoder–decoder models. The bridge-token construction is mathematically specified in Equations (7)–(9).
- Parameter efficiency and competitive accuracy: Table 1 shows PTR uses only 0.02M tunable parameters yet matches or exceeds more parameter-heavy PEFT baselines on average. In particular, TREC and Amazon-5 see large gains over default prompt-tuning initialization.
- Convergence behavior: Figure 4 shows faster early-epoch validation accuracy gains for PTR than other prompt-initialization variants, consistent with the stated goal of sample-efficient tuning.
- Architecture illustration: Figure 3 helps ground the proposed components and makes the intended data flow explicit for practitioners.

## Summary Of Weaknesses
1) Limited and potentially fragile empirical scope
- Only four English classification datasets are used, all relatively standard; no multilingual, generative, or structured prediction tasks. The method’s generality is mostly argued, not demonstrated. Section 4.1 confines evaluation to 128 examples per task without a study of different data regimes or variance across seeds.

2) Insufficient comparison to closely related prompt-tuning improvements
- Beyond LoRA and prefix-tuning, strong prompt-tuning baselines that specifically address initialization stability or reparameterization are missing. For instance, Residual Prompt Tuning and other recent prompt-initialization strategies are not compared. This omission makes it hard to judge whether label-based initialization is consistently superior, especially in few-shot settings.

3) Ambiguity in evaluation protocol and splits
- Section 4.1 says 128 samples from each training set and full validation for evaluation. It is unclear whether a separate test set is used or if the validation set serves as test. Early stopping and model selection criteria are not described. Without a clean held-out test set or consistent selection procedure, reported numbers may be optimistic.

4) Lack of statistical rigor and reporting
- No confidence intervals, standard deviations, or significance tests are provided. Given the high variance of few-shot tuning, single-run results in Table 1 and Table 2 are hard to interpret. Figure 4 shows single curves with no error bands.

5) Incomplete ablation and component analysis
- Table 2 reports 5-epoch accuracies for “Label,” “Bridge,” and “Sharp” in isolation, but does not include their combination, even though the full PTR method uses all three. It is therefore unclear whether the combined method’s improvement is additive or dominated by one component. The role of the number of bridge tokens and prompt length is also not studied.

6) Sharp-to-smooth attention lacks critical implementation details
- Section 3.3 and Eq. (4) specify the temperature schedule qualitatively, but do not provide initial/final temperatures, schedule length, whether it is per-layer or per-head, or how it interacts with T5’s normalization. Appendix C.2 illustrates distributions conceptually, but the core hyperparameters and schedule used in experiments are missing, hurting reproducibility and interpretability.

7) Bridge token construction may introduce leakage-like biases and extra compute
- Section C.3 uses the same backbone LLM to compute logits for inputs appended with “means in one word:” and aggregates over label-specific sets from the training data to derive important tokens. This implicitly learns from the training set distribution via an auxiliary probe, yet the computational overhead and its sensitivity to k, template phrasing, and domain are not quantified. There is also no analysis of whether this step overfits in very small data regimes or how it generalizes across datasets.

8) Attention analysis may be confounded
- Figure 2 shows average cross-attention to prompts rising after tuning, but the comparison is across different sequence lengths and prompt embeddings. Because attention mass must sum to 1 per query, averaging over tokens may be misleading unless normalized for length and head/layer variations. The paper does not clarify whether scores are averaged per head/layer, nor does it report where the effect is strongest in the stack. Additional stratified analyses are needed.

9) Gains are not uniformly strong, and macro findings are modest
- In Table 1, LoRA and prefix-tuning are comparable or better on some tasks (e.g., LoRA is best on SST-2). The average improvement over prefix-tuning is marginal (83.01 vs. 82.98), which weakens the claim that PTR is broadly better, despite having fewer parameters. The strongest benefit is versus default/random prompt tuning, which is known to be fragile.

10) Missing training and prompt details
- Section 4 and Appendix D omit key details: random seed(s), decoding strategies, exact verbalizers/label words used per dataset, prompt length allocation between label-initialized and bridge tokens, and the vocab-initialization baseline’s specifics. Reproducing Table 1 faithfully would be difficult without these.

11) Figure- and table-specific concerns
- Figure 1: The y-axis “Similarity Score” magnitude is very large; it is unclear if embeddings are normalized. If not, changes in vector norms may drive the effect, not alignment. Please clarify whether dot products are computed on normalized vectors.
- Figure 3: The diagram shows “Bridge 1..4,” but Section 3.2 and Appendix C.3 do not specify how many bridge tokens are actually used per dataset, nor selection sensitivity.
- Figure 4: Convergence graphs over five epochs do not include LoRA “since it shows almost no effect,” which biases the comparison and hides a potentially slower but stronger method if trained longer. Better to include it and note the trade-off.
- Table 2: The combined PTR variant over five epochs is not presented, making it hard to attribute Figure 4’s convergence to specific components.

## Potentially Missing Related Work
1) Razdaibiedina et al., Residual Prompt Tuning: Improving Prompt Tuning with Residual Reparameterization, 2023 — Directly targets prompt-tuning stability and sensitivity to initialization in few-shot regimes. Should be cited in Related Work (Section B) and compared experimentally in Section 4 as a strong prompt-tuning baseline, especially when arguing about the importance of initialization.

2) Lu et al., Context Tuning for In-Context Optimization, 2026 — Initializes trainable prompts/prefixes from task-specific demonstrations rather than random tokens. This is an alternative principled initialization strategy that should be discussed in Section 3.1 and compared to label-based initialization in Section 4 to clarify trade-offs.

3) Pouramini et al., CrossPT: Exploring Cross-Task Transferability through Multi-Task Prompt Tuning, 2025 — Uses attention over modular prompts and studies initialization under varying data regimes. Relevant to Sections 2.2 and 3.2; should be discussed in Related Work and, if feasible, used as an additional baseline or a point of comparison for attention dynamics and initialization sensitivity.

4) Shernazarov et al., Parameter-Efficient Fine-Tuning for Medical Text Summarization: A Comparative Study of LoRA, Prompt Tuning, and Full Fine-Tuning, 2026 — Provides a careful FLAN-T5 comparison across PEFT methods, including prompt-token counts and budgets. Useful for Section 4 to calibrate parameter counts, training budgets, and to ensure fair comparisons, even though the domain differs.

5) Wei et al., Sample-efficient fine-tuning with textual prompts for time series forecasting, 2026 — Although out of domain, it motivates prompt-driven sample efficiency and warm starts. Citing in Introduction/Related Work would strengthen the broader positioning of sample-efficient prompt tuning.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify and standardize evaluation: Specify whether a separate test set is used. Provide details on model selection, early stopping, and the number of runs. Report mean ± std across at least 3–5 seeds for Tables 1 and 2 and add error bands in Figure 4.
- Reproducibility details: Release or precisely document prompt templates, label verbalizers (“World,” “Sports,” etc.), decoding settings (e.g., greedy vs. beam), prompt/bridge token counts, initial and final temperatures and schedule length for Eq. (4), per-layer/per-head application, and the exact “vocab init” procedure. Add seeds and compute budgets.
- Strengthen baselines: Include at least one strong prompt-tuning variant that addresses initialization such as Residual Prompt Tuning. Consider P-Tuning v2 or recent reparameterizations where relevant. Include LoRA curves in Figure 4 rather than omitting them.
- Deeper attention analysis: Break down Figure 2 by layer and head, normalize for sequence length, and report relative rather than absolute averages. A control experiment with normalized embeddings for Figure 1 would disambiguate norm vs. alignment effects.
- Bridge-token sensitivity: Provide k-sweep and token-count sweeps for Equations (7)–(9). Report time/compute overhead of the “means in one word:” probing step and its impact on very small data. Add a variant without this auxiliary step to quantify its marginal benefit.
- Five-epoch ablation: Add the combined PTR configuration to Table 2, and show whether effects are additive or whether one module dominates. Include an analysis linking Figure 4 to the corresponding ablation configurations.
- Claims calibration: In Section 4.4, soften claims of superiority over LoRA/prefix-tuning given the small average difference in Table 1 and LoRA’s strong SST-2 result.

Typos and minor issues:
- Page 3, Section 3.2: “so replacing low-similarity associations ... ensures effective information transfer” reads as a causal claim; consider rephrasing as a hypothesis.
- Page 4, 4.2: “We also provide a comparison of the number of trainable parameters ... to demonstrate the computational efficiency” — consider adding actual wall-clock and memory profiles to substantiate efficiency beyond parameter count.
- Page 4, 4.4: “As shown in 2,” should be “As shown in Table 2.”
- Figures 1 and 5: Label axes with units and clarify if embeddings are normalized before dot products.

What could change my evaluation:
- Add strong prompt-based baselines (e.g., Residual Prompt Tuning) and multi-seed reporting with significance tests; provide full implementation details and a proper test split. If PTR remains competitive or superior under these stricter conditions, I would raise to Borderline Conference or Conference.
- Provide comprehensive ablations including the combined PTR in Table 2, sensitivity to bridge-token parameters, and detailed attention-layer analyses that directly validate the mechanism; a positive outcome would increase Soundness and excitement.

## Confidence
4: Quite sure after careful checking — I checked the central claims, equations, figures, and tables; details are missing in experimental protocols, but the critique and interpretation are unlikely to hinge on minor misunderstandings.

## Soundness
3: Acceptable — The main claims are plausible and partially supported, but experimental rigor is limited by missing strong baselines, absent variance reporting, and ambiguous evaluation splits.

## Excitement
3.0: Interesting — The observations and the simple label-initialization + attention schedule are useful, but the empirical scope and comparisons limit broader excitement.

## Overall Assessment
3: Findings — The paper could be accepted to Findings of the ACL. It presents clear diagnostics and simple, implementable ideas that appear helpful for sample-efficient prompt tuning on FLAN-T5. However, missing strong baselines, incomplete experimental reporting, limited scope, and some confounds in the analyses make it not yet ready for the main conference.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges focusing on encoder–decoder models and not addressing decoder-only LMs or prompt placement variants. Additional points to discuss:
- The bridge-token construction leverages model-internal probing on training data, which may encode dataset biases into prompts more strongly. Consider the risk of amplifying spurious correlations and how to detect or mitigate them.
- The method relies on specific English label words; cross-lingual applicability and fairness across label naming conventions or culturally sensitive labels should be discussed.
- Potential dual-use is low, but if applied to sensitive classifications, attention-focusing and label-initialization could harden biased decision pathways; consider mitigation such as calibration, diverse label verbalizers, and fairness auditing.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Equations are clear, but key hyperparameters (e.g., temperature schedule), templates, verbalizers, seeds, and selection protocols are missing. Code or precise recipes would substantially help.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.