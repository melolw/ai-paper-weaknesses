# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes QQQ, a W4A8 (4-bit weights, 8-bit activations) post-training quantization pipeline for LLMs designed to improve both accuracy and throughput. The algorithm has two parts: (1) adaptive channel-wise smoothing of activations to mitigate outliers, followed by (2) Hessian-based weight compensation (GPTQ-style) after moving quantization difficulty from activations to weights. On the systems side, the authors implement specialized W4A8 GEMM kernels for both per-channel and per-group weight quantization, including a FastFP16→INT8 conversion routine and fused dequant-quant steps to reduce overhead. Empirically, QQQ is benchmarked on LLaMA-1/2/3 models for perplexity on WikiText2 and for zero-shot accuracies on five classification datasets, and integrated into vLLM for end-to-end throughput evaluation. Results indicate competitive perplexity and accuracy versus W8A8 and W4A16 methods, with substantial throughput gains, especially at larger batch sizes.

## Summary Of Strengths
- Practical problem framing: W4A8 can accelerate both prefill and decode, but is fragile; targeting this operating point is timely and useful to the community.
- Algorithmic combination that is reasonable and empirically effective: adaptive channel selection for smoothing, then GPTQ-style Hessian compensation for weights. The two-stage design is clear in Figure 1 and mathematically grounded in Equations (3)–(4).
- System co-design: careful kernel work for both per-channel and per-group W4A8 GEMM, including FastINT4→INT8 and FastFP16→INT8 (Figure 5), as well as fused dequant-quant (Figure 4), which directly addresses real deployment bottlenecks.
- End-to-end integration and throughput: integration into vLLM with continuous batching and paged attention, plus comparisons against commonly used baselines. In Figure 6, QQQ outperforms FP16, W8A8 SmoothQuant, AWQ, and Marlin W4A16 in most batch settings, and the effect is larger on LLaMA‑2‑13B than 7B, consistent with the claimed compute/bandwidth balance.
- Kernel microbenchmarks: Figure 7 shows up to 3.67× speedup over PyTorch FP16 GEMM, and the ablation in Figure 8 isolates the contribution of the FastFP16→INT8 routine, which improves per-group W4A8 GEMM by up to 2.02×. These figures substantiate the systems claims with concrete evidence.
- Ablations on algorithmic components: Table 3 separates baseline W4A8, +Adaptive Smoothing, and +GPTQ, revealing consistent perplexity improvements and showing that the combination is the best configuration.

## Summary Of Weaknesses
1) Inconsistency in the adaptive smoothing rule and its description
- Section 3.1 states that channels “with significant outliers” are smoothed, yet Equation (1) defines the selected set T as channels satisfying max(|X:,t|) < σ, i.e., not outliers. This appears reversed. If T indexes channels to be smoothed, then the inequality should be > σ. This is central because it determines which channels are altered, and a sign error here would undermine the method. Please clarify whether channels in T are smoothed, and correct Equation (1) or the description accordingly; also clarify whether σ is per-layer, per-tensor, or global.

2) Limited evaluation breadth and missing strong baselines
- The accuracy evaluation uses WikiText2 perplexity (Table 1) and five zero-shot classification tasks (Table 2). Modern LLM quantization works typically include broader suites (e.g., MMLU, BBH, GSM8K, HumanEval, multi-domain PPL). Restricting to only five multiple-choice tasks underrepresents reasoning and knowledge-heavy workloads where W4A8 can be brittle.
- System-level baselines: QServe (W4A8KV4), an explicit W4A8+system co-design, is cited but not compared in the end-to-end setting. Given QQQ’s positioning as a practical W4A8 solution, omitting a direct comparison weakens the systems claim.

3) Per-channel QQQ underperforms the best W4A8 competitor in perplexity
- Table 1 shows that per-channel QQQ lags QoQ on most models, with notable gaps (e.g., LLaMA‑3‑8B: 7.41 vs 6.89 PPL). The text attributes this to symmetric vs asymmetric weights, but then claims parity “with existing state-of-the-art.” This is too strong unless qualified: for per-channel W4A8, the SOTA accuracy appears to remain asymmetric. It would help to include symmetric-vs-asymmetric ablations for QQQ to disentangle the source of the gap.

4) Calibration protocol details are underspecified
- Only “128 sequences from PILE” are used for calibration (Section 4.1), but there are no details on selection, tokenization, prompt formatting, or sensitivity analyses. Since adaptive smoothing uses a grid search over σ and the GPTQ stage relies on representative activations, the small calibration size could bias results. Please report sensitivity to calibration size/content, and whether performance improves materially with larger calibration sets.

5) Adaptive smoothing hyperparameters and search cost are unclear
- Section 3.1 sets σ via grid search over [0, max |X|], but lacks discretization granularity, stopping criteria, or per-layer treatment. Table 3 shows that adaptive smoothing contributes nontrivially to PPL gains, but the runtime and memory overheads of this grid search and the subsequent re-scaling are not reported. A wall-clock quantization-time table and sensitivity plot for σ would make the method actionable.

6) Missing methodological details for reproducibility
- Equation (2) optimizes s but leaves the quantizer Q and its calibration parameters unspecified (e.g., per-token activation scaling estimator, rounding mode, clipping). Section 4.1 states QQQ “exclusively uses symmetric quantization,” but the exact quantization ranges and how they are estimated per layer/token are not detailed. Implementation details are crucial, since Table 3’s deltas are modest and sensitive to design choices. Without code or a thorough spec, reproducibility is uncertain.

7) Throughput comparisons could be confounded by configuration differences
- Figure 6 compares “SmoothQuant (W8A8), AWQ (W4A16), Marlin (W4A16), QoQ (W4A8), QQQ (W4A8).” However, activation and KV-cache precisions and attention kernels can significantly affect throughput. It is unclear whether all methods share identical KV precisions, attention implementations, and quantized op coverage across all layers. Since W4A8 helps prefill and decode differently from W4A16 and W8A8, a prefill-vs-decode breakdown and a latency decomposition would strengthen the claim that speedups come from the proposed kernels rather than configuration mismatches.

8) Lack of longer-context and decoding-heavy scenarios
- The benchmarks (input 1024, output 128) favor prefill-heavy cases. Since one main motivation is to speed up both phases, please include longer outputs (e.g., 1024+) and longer contexts (e.g., 8k–32k) to test stability of speedups and accuracy at larger sequence lengths. This would also probe accumulation/overflow risks in INT8 GEMM and dequant.

9) Limited discussion of failure modes and accuracy–speed trade-offs
- Figure 7 shows that per-channel W4A8 GEMM slows as tokens increase, likely due to conversion overheads. But the paper does not discuss when to choose per-group vs per-channel in practice, how group size affects both accuracy and throughput, or how these trade-offs vary with model size and batch regime. More guidance would make QQQ easier to adopt.

10) Minor clarity issues and typos
- Page 1: “gies: weight-activation and weight-only quantization.” seems like a broken line break; please fix.
- Section 3.3: minor spelling “setp” → “step.”
- Section 4.1: “we have develop” → “we have developed.”

Specific references to figures/tables/equations supporting the critique:
- Figure 2 and Figure 3: Helpful diagrams of the per-channel vs per-group pipelines; however, the text should clarify how scaling factors are stored and fused to avoid runtime divides and whether these are precomputed per-tile to reduce memory bandwidth.
- Figure 5: The FastFP16→INT8 scheme is central to the per-group kernel’s advantage, and Figure 8 validates its impact. It would help to report numerical error introduced by this mapping vs the standard conversion, and any accuracy effect.
- Table 1: Perplexity gaps of per-channel QQQ vs QoQ contradict blanket parity claims with SOTA for the symmetric case; please rephrase or add experiments to reconcile.
- Table 3: Shows that +AS and +GPTQ both matter; please include a row with only +GPTQ to isolate its standalone effect, and report the σ selected to show convergence of the grid search.

## Potentially Missing Related Work
1) Elhoushi et al., “any4: Learned 4-bit Numeric Representation for LLMs,” 2025 — introduces learned 4-bit numeric formats and custom LUT-based GEMMs; directly relevant to W4A8 design space and could be compared in Section 2 and discussed alongside Figures 2–5 regarding numeric formats and kernel implications.

2) Zeng et al., “ABQ-LLM: Arbitrary-Bit Quantized Inference Acceleration for Large Language Models,” 2025 — proposes arbitrary-bit PTQ with GPU kernels reconstructing mixed-precision GEMM; should be included in Related Work (Section 2.2) and, if possible, as an additional systems baseline or at least discussed in Section 4.3.

3) Gong et al., “A Survey of Low-bit Large Language Models: Basics, Systems, and Algorithms,” 2024 — a comprehensive survey situating W4A8 within broader PTQ/QAT and system kernels; cite in Related Work to frame the contribution and evaluation scope.

4) Ouyang et al., “Low-Bit Quantization Favors Undertrained LLMs: Scaling Laws for Quantized LLMs,” 2024/2025 — scaling-law analysis of quantization effects; discuss in Section 4 to contextualize where W4A8 is expected to be robust or fragile, possibly guiding task/model choices.

5) Zhao et al., “Benchmarking Post-Training Quantization in LLMs,” 2025 — unified taxonomy and benchmarks for PTQ; useful to align evaluation protocol and include more standardized tasks in Section 4.

6) Lee et al., “Exploring the Trade-Offs: Quantization Methods, Task Difficulty, and Model Size in LLMs,” 2025 — broad empirical trade-off study; reference in Related Work to support the selection of diverse evaluation tasks and model sizes.

7) Lee et al., “LittleBit: Ultra Low-Bit Quantization via Latent Factorization,” 2025 — while more extreme than W4A8, its techniques inform accuracy–speed–bitwidth trade-offs; briefly discuss in Related Work.

8) Gong et al., “Training Dynamics Impact Post-Training Quantization Robustness,” 2025 — relevant to robustness of PTQ and could be cited to motivate calibration choices and sensitivity analyses.

9) Lee et al., “LUQ: Layerwise Ultra-Low Bit Quantization for Multimodal LLMs,” 2025 — extends low-bit methods to multimodal models; add as forward-looking related work.

## Comments Suggestions And Typos
Actionable requests for rebuttal/camera-ready:
- Clarify and correct Section 3.1: Resolve the inequality/sign inconsistency in Equation (1) versus the narrative, define whether σ is per-layer or per-tensor, and report the grid-search discretization and selected σ values. Provide the runtime overhead of adaptive smoothing, and add an ablation of σ sensitivity.
- Reproducibility details: Precisely specify the quantizer Q for activations and weights, including range estimation, clipping, rounding mode, per-token scaling estimator, and calibration pass. Report calibration data selection and add a sensitivity study w.r.t. calibration size (e.g., 128/512/2048 sequences).
- Strengthen evaluation breadth: Add at least one reasoning suite (e.g., MMLU, BBH or GSM8K) and a code generation task (e.g., HumanEval or MBPP), and include longer outputs and longer contexts to test both prefill and decode. Consider instruction-tuned checkpoints, where users often care about W4A8.
- Systems baselines and breakdowns: Where feasible, compare against another W4A8 system-level implementation (e.g., a QServe-style pipeline), and provide a prefill-vs-decode latency breakdown and component-wise kernel profiling to attribute gains to Figure 5’s conversion and Figure 4’s fusion versus other differences.
- Per-channel vs per-group guidance: Extend Figure 7 with accuracy overlays or add a separate table/plot quantifying accuracy vs throughput trade-offs for different group sizes, and practical recommendations by batch/token regimes.

Typos and minor edits:
- Page 1: “gies: weight-activation and weight-only quantization.” → fix broken word wrap.
- Section 3.3: “de-quantization setp” → “dequantization step.”
- Section 4.1: “we have develop” → “we have developed.”
- Consistency: unify notation for Hadamard product/division (you use “⊘”, “⊙”, and in text “∅/odot”; ensure symbols render correctly).

What could raise my score:
- Correct the Eq. (1) issue with a detailed clarification and provide the σ-sensitivity/overhead study.
- Add broader task evaluations and a prefill/decode breakdown with matched configurations, plus a direct W4A8 system baseline.
- Release code for kernels and quantization pipeline, or provide a detailed reproducibility appendix with full quantization specs and configs.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully, including equations, figures, and tables. It’s unlikely, though conceivable, that I missed something that would change my assessment.

## Soundness
3.5: Between Acceptable and Strong — Methods are sensible and supported by results and ablations, but there are clarity gaps (Eq. 1 inconsistency, limited eval breadth) that reduce the strength of claims.

## Excitement
3.5: Between interesting and exciting — The W4A8 operating point with strong kernels and reasonable accuracy is practically impactful; broader eval and comparisons would make it more compelling.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. The systems engineering and end-to-end integration are solid and useful, and the figures/tables substantiate key claims (Figures 6–8; Tables 1–3). However, there is a core clarity issue in Equation (1) vs Section 3.1, limited evaluation scope, and missing direct W4A8 system comparisons. With these addressed and more comprehensive evaluation, this would be a clear accept.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper lists two engineering limitations (quantization time and GEMM support only for 4-bit weights). I encourage a broader discussion:
- Potential degradation on safety-sensitive tasks due to quantization errors, especially for low-bit activations; testing on instruction-tuned models and safety benchmarks would be informative.
- Bias and robustness: low-bit quantization can disproportionately harm minority or long-tail linguistic phenomena; discussing mitigation (e.g., calibration data diversity, per-domain smoothing) would strengthen the section.
- Dual-use: faster, smaller-footprint LLMs can lower barriers for misuse; consider referencing responsible deployment practices.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Clear architecture and measured results; however, important quantizer details and calibration protocol specifics are missing. Public code or a more detailed specification would raise this to 5.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — Integration into vLLM is claimed; if the kernels and quantization pipeline are released and documented, this could be a 4.