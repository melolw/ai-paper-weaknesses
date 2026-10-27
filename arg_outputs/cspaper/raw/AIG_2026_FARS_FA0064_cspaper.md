# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies how to select which Transformer layers should keep full attention during prefill when adapting pretrained LLMs to sliding-window attention (SWA) for long-context inference. It proposes a training-free calibration procedure that, for each layer, measures the degradation in negative log-likelihood (NLL) on answer tokens when that layer is switched from full attention (FA) to SWA while all other layers are in SWA. The top-k layers with the largest NLL degradation are then assigned FA during prefill; all layers use FA during decode. Experiments on Qwen3-4B-Thinking-2507 with LongMemEval show that using 1/4 FA layers selected by this criterion attains 64.6% accuracy, close to a 1/2-FA periodic baseline at 65.0% and substantially above periodic 1/4-FA and an attention-mass heuristic (LightTransfer). The paper includes a de-confounding analysis contrasting long- versus short-prompt calibration to argue that the signal specifically reflects long-range attention needs.

## Summary Of Strengths
- Clear, focused problem framing: the paper targets a specific and practical question in hybrid attention deployment, namely which layers should retain FA during prefill under a budget.
- Method simplicity and practicality: the proposed Δ-NLL score (Equation 1, Page 3) is easy to compute via teacher-forced forward passes, requires no training, and is compatible with any pretrained model following SWA adaptation. The one-time calibration cost is reported as ~15 minutes for a 36-layer model.
- Strong headline result under a tight FA budget: Table 1 (Page 5) shows that NLL-guided 1/4-FA reaches 64.6% on LongMemEval, nearly matching the 1/2-FA periodic baseline (65.0%), while outperforming the best periodic 1/4-FA (54.2%) and LightTransfer (38.2%).
- Evidence that the score targets long-range needs: Figure 2 (Page 6) compares rankings from long versus short prompts and reports low correlation (ρ = 0.306) and small overlap, supporting the claim that Δ-NLL is not just measuring generic layer sensitivity.
- Informative qualitative analysis: Figure 3 (Page 6) visualizes per-layer Δ-NLL, showing a non-periodic pattern and giving intuition that the selected layers span early, middle, and late depths.
- The paper’s organization is clear, with concise equations and an overview diagram (Figure 1, Page 3) that makes the pipeline easy to follow.

## Summary Of Weaknesses
1) Limited evaluation scope and generality
- Only one model family and size: all results are on a single 36-layer Qwen3-4B variant (Section 4.1, Page 4). The claimed generality to “any pretrained Transformer” is not substantiated. Different families can have different depth-wise roles and inter-layer dynamics, which could change selection patterns and gains.
- Single benchmark: LongMemEval is the only task suite. Although relevant, the method is motivated as generic long-context inference. Additional evaluations on other long-context QA or RAG-style datasets (e.g., NarrativeQA long-context settings, Needle-in-a-Haystack-style probes, or code-long-context tasks) would better establish robustness.

2) Comparisons and baselines are too narrow
- Table 1 (Page 5) compares to periodic patterns, a single attention-mass heuristic, and an all-SWA variant, but omits several closely related methods that also optimize where to spend dense attention. This limits claims about advancing the efficiency–accuracy Pareto frontier.
- No ablation against simple but strong search procedures under the same budget, such as greedy forward selection using task accuracy on a small held-out set, or stochastic search over FA masks constrained to 1/4 of layers. Even a limited sweep on the 36-layer space would help rule out that Δ-NLL is just a proxy for a cheap mask search.

3) Heavy reliance on an LLM judge without transparency on variance
- Evaluation uses a “GPT-5-mini” judge (Section 4.1, Page 4). There is no measurement of judge variance, double-annotation, or agreement. Without agreement metrics or at least repeated judging with uncertainty intervals, it is difficult to assess whether the reported 0.4-point gap to 1/2-FA is statistically meaningful. At minimum, confidence intervals or bootstrap estimates for Table 1 and Table 2 are needed.

4) Potential confounds in the calibration–evaluation linkage
- Calibration uses LongAlign-10k and fusang-v1-filtered (Appendix A.1, Page 8), while evaluation is on LongMemEval. The paper asserts calibration is general, but provides no analysis of data distribution shift. A sensitivity study varying calibration sources, answer length distributions, or content domains would strengthen the claim that Δ-NLL generalizes.
- The de-confounding analysis (Section 4.4, Page 5; Figure 2, Page 6) shows low rank correlation between long- and short-prompt calibrations, but does not exclude other confounds like answer-length dependence, formatting artifacts, or prompt structure. Reporting Δ-NLL as a function of answer length and positional distance to the supporting evidence would make the claim tighter.

5) Missing details for exact reproducibility
- Equation 1 defines Δℓ as a mean over “answer tokens,” but practical details matter: Are BOS/EOS or assistant role tokens included? Are answer spans detected via template markers or assistant role boundaries? Are padding and truncation ever involved at 24k? How are special tokens treated under SWA during calibration? These choices can shift Δℓ and alter selected layers.
- SWAA hyperparameters are listed (Appendix A.3), but calibration implementation details are thin: batching strategy for L+1 passes per example, numeric precision, and whether KV caches are reused across per-layer toggles. Such choices affect both timing claims (~15 minutes) and numerical stability.

6) Lack of statistical rigor around the headline comparisons
- Table 1 gaps are presented as point estimates without error bars. Given the 500-sample size, a 0.4-point difference to the 1/2-FA periodic baseline may not be significant. Likewise, the large gains over LightTransfer warrant sanity checks to ensure the LightTransfer implementation and hyperparameters match the original, or at least are tuned comparably.

7) Narrow mechanistic insight
- Figure 3 (Page 6) is helpful, but the paper stops at describing where Δ-NLL is large. There is no investigation into attention maps, head specialization, or cross-layer information flow that could explain why layers 9, 13, 15, and 21 dominate. Without deeper analysis, it is hard to anticipate when the method might fail or how to adapt it to different architectures.

8) Fairness of compute budgets and decode settings
- All methods use FA during decode (Section 3.1), which is sensible but yields a specific operating point. The paper argues prefill is the bottleneck yet gives no wall-clock or FLOP breakdowns per configuration. Reporting actual latency and memory under the same hardware would make the “Pareto” claim concrete and verify the “half the FA budget” narrative translates to user-perceived speedups.

9) Figure- and table-specific issues that affect interpretation
- Figure 1 (Page 3) is clear and aligns well with the text, but it does not depict how answer segments are demarcated in mixed-role chat formats, which is critical for replicating Δℓ computation.
- Figure 2 (Page 6) supports the long-range-specific signal claim; however, using only rank correlation discards magnitude information. Showing the raw Δ-NLL scales for both settings would make the “85.6× larger” statement more verifiable (right now it is text-only).
- In Table 2 (Page 5), per-task improvements versus LightTransfer are large, but there is no per-task sample size or variance, and it is unclear whether the task-type distribution matches the overall 500-sample evaluation. Without that, the largest deltas (e.g., +37.1pp for single-session-user) could reflect small-N slices.

10) Literature coverage is incomplete
- The related work misses several recent methods that also perform training-free or lightly-trained allocation of attention resources across layers/heads/windows. This weakens positioning and raises the risk that stronger baselines exist.

## Potentially Missing Related Work
1) Qiao et al., “Rethinking the Role of Efficient Attention in Hybrid Architectures,” 2026 — Provides mechanistic and scaling analysis for when full-attention layers are actually needed in hybrids. Should be discussed in Section 2.3 to contextualize why Δ-NLL might align with genuine long-range dependencies rather than generic sensitivity.

2) Lan et al., “Morphing into Hybrid Attention Models,” 2026 — Learns layerwise FA vs. linear attention gates under a budget. Directly comparable to the proposed selection approach, though theirs requires training. Add to Section 2.4 and compare conceptually in Section 4.2; consider a small-scale baseline if possible.

3) Wang et al., “How Much Dense Attention is Necessary? Oracle-Guided Sparse Prefill for Full/GQA Layers in Hybrid Long-Context Models,” 2026 — Also optimizes the placement of dense attention during prefill using an oracle-style signal. Discuss in Section 2.3 and relate to Δ-NLL’s task-grounded calibration.

4) Du et al., “Native Hybrid Attention for Efficient Sequence Modeling,” 2026 — Provides an architectural hybrid that unifies linear and full attention. Add to Section 2.3 as an architectural baseline and discuss trade-offs vs. post-hoc SWA adaptation.

5) Ge et al., “A LITTLE GOES A LONG WAY: EFFICIENT LONG CONTEXT TRAINING AND INFERENCE WITH PARTIAL CONTEXTS,” 2025 — Empirically studies how much dense attention/context is needed. Cite in Section 2.1/2.3; its findings could guide budget choices and interpretation of Table 1.

6) Fu et al., “Mixture of Attention Spans: Optimizing LLM Inference Efficiency with Heterogeneous Sliding-Window Lengths,” 2024 — A calibration-style approach assigning heterogeneous spans to heads. Discuss in Section 2.1/2.3 and, if feasible, adapt as a head-level baseline complementary to your layer-level selection.

7) Long et al., “Focus-dLLM: Accelerating Long-Context Diffusion LLM Inference via Confidence-Guided Context Focusing,” 2026 — Uses confidence-guided sparsification; conceptually connected to using output-quality signals for allocation. Briefly mention in Section 2.1 as related calibration-style sparsification.

8) Lan et al., “STILL: Selecting Tokens for Intra-Layer Hybrid Attention to Linearize LLMs,” 2026 — Token-level selection using self-saliency with sliding windows. Discuss in Section 2.3 as a complementary strategy; consider combining token- and layer-level selection in future work.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Statistical reporting and judge robustness:
  - Please add confidence intervals or standard errors for Table 1 and Table 2. Given the headline claim that NLL-guided 1/4-FA matches the 1/2-FA periodic baseline within 0.4pp, uncertainty is critical.
  - Report inter-annotator agreement or stability for the GPT-5-mini judge: e.g., dual-judging a 10–20% subset, repeated judging trials, or calibration against exact-match variants where possible.
- Reproducibility of Δ-NLL computation:
  - Precisely define how answer tokens are identified in the chat template and whether special tokens (system/assistant role markers, BOS/EOS) are included in NLL. Clarify handling of very long completions and truncation.
  - Specify whether KV caches are reused across the L+1 passes for each example during calibration, and the numerical precision used. This directly affects both the reported 15-minute runtime and the Δℓ estimates.
- Baselines and ablations:
  - Consider a simple mask-search baseline under the same 1/4-FA budget: e.g., a greedy selection that directly optimizes accuracy on a small held-out subset of LongMemEval, or random-restart hill climbing with 200–500 mask evaluations. This would test whether Δ-NLL provides a uniquely strong signal beyond task-level mask search.
  - Add, at least in discussion form, comparisons against head-level or span-level allocation methods (e.g., MoA) to position your contribution in the calibration landscape.
- Mechanistic probing:
  - Augment Figure 3 with analyses of attention-distances or cross-attention to supporting evidence for top-Δℓ layers. Alternatively, show that masking long-range tokens disproportionately hurts those layers. This would reinforce the “long-range” interpretation beyond rank correlation in Figure 2.
- Efficiency claims:
  - Provide wall-clock latency, prefill FLOPs, and memory for the configurations in Table 1 on the same hardware. The claim of halving FA layers is compelling, but concrete user-centered metrics will make the Pareto claim much stronger.

Typos and minor issues:
- Page 4, Section 4.1: “batch size 64, and temperature 0” — consider clarifying whether nucleus/top-k sampling is disabled; you later say deterministic decoding, but spell it out.
- Page 5, Table 1 caption: “Best in bold, second-best underlined.” In the table, the second-best is not visibly underlined in plaintext; ensure the camera-ready renders as intended.
- Page 5, Table 1 FA lists: layer indices are mixed zero/one-based across rows ([0,4,8,...] vs [1,3,9,...]). Please standardize indexing and state whether the model layers are 0- or 1-based throughout (also affects Figure 3 x-axis).
- Page 6, Figure 3 y-axis: The label “Δ-ELL (×10^4)” likely intends “Δ-NLL” or “Δ-ℒ.” Please correct the axis label and units.

Criteria that could raise my score:
- Add confidence intervals and judge robustness checks; show significance for the 0.4pp gap to 1/2-FA.
- Include at least one additional model family or size and one additional long-context benchmark, demonstrating consistent gains.
- Provide efficiency measurements (latency, memory, FLOPs) corresponding to Table 1.
- Add a simple mask-search baseline and demonstrate Δ-NLL’s advantage.
- Clarify Δ-NLL implementation details sufficient for plug-and-play reproduction.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
3.5 Between Acceptable and Strong: The method and experiments support the central claims, but the scope is narrow and key evaluation details and baselines are missing. Statistical rigor and broader validation would strengthen it.

## Excitement
3.0 Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there’s time. Practical and tidy idea with good potential, but limited breadth.

## Overall Assessment
3 Findings: This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The training-free Δ-NLL criterion is simple, practical, and appears effective on LongMemEval with Qwen3-4B, with clear visual support in Figure 2 and Figure 3 and strong gains in Table 1 over fixed/heuristic selections. However, the evaluation is narrow (single model/benchmark), significance and judge variance are unreported, and comparisons omit several directly relevant methods. With broader validation, statistical reporting, and at least one stronger calibration/search baseline, this could rise to main-track caliber.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges limited evaluation scope in the conclusion, which aligns with my concerns. Societal impact is relatively minimal here, since the contribution is an efficiency technique for long-context inference; the main risks are indirect, such as enabling wider deployment that inherits biases of underlying models. It would be helpful to briefly note:
- Any bias amplification if calibration examples are drawn from skewed sources, potentially privileging certain domains when selecting FA layers.
- Energy and cost benefits from reduced prefill computation, and how those trade off with potential accuracy regressions on safety-critical tasks.

## Ethical concerns
None.

## Needs Ethics Review
No

## Reproducibility
4 Mostly reproducible: The core idea and settings are described clearly; code is said to be available. Some missing implementation specifics around Δ-NLL calculation, answer-span demarcation, and caching/batching may cause variance.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: Code availability is noted; if released as described, it should help practitioners reproduce the calibration and layer selection.