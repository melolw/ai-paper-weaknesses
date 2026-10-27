# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies how to obtain streaming-compatible text embeddings that can be updated incrementally using a KV cache while retaining much of the quality typically obtained by bidirectional attention. The authors train a bidirectional “teacher” with Gradient-Guided Soft Masking (GG-SM) to transition from causal to bidirectional attention, then distill into a causal “student” using a combination of InfoNCE contrastive loss and an MSE embedding-matching loss. The student preserves causal masking, enabling O(Δ) updates with KV reuse. Experiments with a 0.5B-parameter base model on a six-dataset MTEB slice and LoCoV1 indicate that the student closes 68.1% of the performance gap to the teacher, exceeds an Echo-embeddings baseline by 2 points, achieves 4.1× average streaming speedup, and performs best on long-context retrieval.

## Summary Of Strengths
- Clear and relevant problem framing: many production embedding systems need streaming updates without recomputing the entire sequence, and bidirectional attention breaks KV-cache compatibility.
- Methodological idea is reasonable and well scoped: a teacher–student setup where a bidirectional teacher’s representations supervise a causal student via MSE alongside a standard InfoNCE objective.
- Concrete and easy-to-implement objective: Equations (3)–(5) clearly specify the losses and how they are combined; mean pooling in Equation (6) is compatible with streaming updates.
- Figures and tables help convey key claims.
  - Figure 1 provides a useful overview of how the bidirectional teacher is frozen and how the causal student is trained and deployed with KV-cache for streaming, aligning well with Section 3.
  - Figure 2 illustrates the latency benefit of KV-cache reuse: the flat blue curve for causal updates contrasts with the increasing orange curve for bidirectional recomputation, visually supporting Section 4.3’s speedup claim.
- Empirical signals of value:
  - Table 1: On the six-dataset MTEB slice, the student improves mean from 0.576 (causal) to 0.623, and surpasses Echo (0.603) without doubling tokens.
  - Table 2: On LoCoV1 long-context retrieval, the student (0.284) beats all baselines, which is interesting and suggests the approach may transfer generalizable representation quality rather than only mimicking bidirectional attention.
- Task-type analysis (Figure 3) is informative, suggesting where embedding-level distillation is most effective (classification, clustering) and where it lags (pair classification).

## Summary Of Weaknesses
1) Limited and idiosyncratic evaluation scope
- Only a six-dataset MTEB slice is reported, rather than the full MTEB suite. This makes generalization uncertain. For instance, retrieval coverage is narrow (ArguAna, SciFact) and lacks BEIR-style breadth.
- The training setup uses all-nli entailment pairs with sequence length 512 and only two seeds. No variance/error bars appear in Tables 1 and 2 or Figure 3, making it hard to assess robustness. This is especially important where student slightly exceeds the teacher (e.g., ArguAna and AmazonCF in Table 1).
- There are no comparisons to strong public causal and bidirectional LLM-based embedder baselines beyond Echo applied to the authors’ own causal model. Missing are, e.g., SGPT, Causal2Vec-type methods, and high-performing instruction-tuned embedders. As a result it is unclear where the proposed student stands against competitive open-source or production baselines.

2) Unclear or incomplete details for GG-SM teacher training (Section 3.2)
- Equation (1) defines a mask that depends on gradient norms for future tokens. It is not explained how these gradients are computed efficiently during training, at what frequency, or with what stability safeguards. Are gradient norms estimated from the same forward-backward pass or accumulated across steps? Do they add nontrivial overhead? Without these details, reproducibility and plausibility suffer.
- The transition schedule in Equation (2) refers to σ(||∇h_j L_warm||), but how exactly the warmup gradients are stored, normalized, and used is unspecified. Are the gradient scales layer-wise normalized? Are token- or position-dependent statistics smoothed over time?

3) Fairness and clarity of the Echo baseline
- Echo embeddings are instantiated only as “A+Echo” by duplicating the input for the authors’ model. The paper does not clarify whether other implementation nuances or recommended settings from the Echo paper are followed, including pooling choices, normalization, or optional instruction prompts. This makes it difficult to assess whether the 2-point advantage over Echo in Table 1 is a fair comparison.

4) Missing ablations and sensitivity analyses
- No ablations on λ in Equation (5). The choice λ=0.5 may not be optimal across tasks or lengths. Given Figure 3 shows task-type variability, a λ-sweep could change conclusions.
- No ablations on pooling strategies, contrastive temperature τ in Equation (3), or the effect of L2-normalization before MSE in Equation (4).
- No ablations on teacher quality: how does student performance depend on the teacher’s strength or on the GG-SM schedule? What if the teacher is trained bidirectionally without GG-SM?

5) Streaming latency methodology under-specified
- Figure 2 shows strong speedups, but the hardware, batch size, precision, KV-cache implementation, and framework are not specified. Without these, the absolute numbers and even relative speedups are hard to reproduce or compare. For example, attention kernel implementations, fused ops, and cache layout significantly affect latency.
- It is not clarified whether the student recomputes position encodings or reuses position-dependent caches in a specific way that might affect extrapolation to longer contexts.

6) Long-context claims lack supporting protocol detail
- Table 2’s LoCoV1 results are intriguing, but there is no description of the evaluation protocol beyond “NDCG@10.” What is the tokenizer/truncation policy, max length, and retrieval index configuration? Are documents chunked? How are queries encoded versus documents? These choices can swing long-context retrieval substantially.
- The explanation attributing teacher underperformance to “position bias artifacts from training on short sequences” is speculative, with no diagnostic evidence (e.g., position-sensitivity tests or length-controlled probes).

7) Limited external validity across scales and data
- All experiments use a single 0.5B model and a single training corpus (all-nli). It is unclear if the distillation approach holds for larger models, different objectives (e.g., multi-task instruction tuning), multilingual data, or domain-shifted settings.

8) Reproducibility gaps despite simple formulas
- Many critical training details are absent: optimizer, learning rate schedule, steps/epochs, negative sampling strategy specifics for InfoNCE, temperature τ value, LoRA target layers beyond “q, k, v, o” and whether biases are adapted, sequence packing, gradient clipping, and regularization terms. The statement that “teacher embeddings are precomputed and cached” does not include caching format, batching, or memory footprint.

9) Statistical reporting and significance
- No confidence intervals or standard deviations are reported in Tables 1 and 2, and Figure 3 lacks error bars. Given the small deltas in some datasets, it is unclear which improvements are statistically reliable.

10) Positioning within broader streaming/distillation literature is narrow
- The related work focuses mainly on text embeddings. There exists a growing literature on distilling from full/bidirectional teachers into causal or windowed students for streaming across modalities, KV-cache distillation, and windowed attention. These are immediately relevant and would strengthen the conceptual framing and baseline design choices.

Figure- and Table-specific comments
- Figure 1 clearly delineates frozen vs trainable modules and the streaming path. However, it would help to explicitly annotate where the gradient-guided mask from Section 3.2 is applied during teacher training and to indicate whether teacher pooling matches student pooling.
- Figure 2’s panels support the streaming claim convincingly at a qualitative level. Still, the missing hardware and implementation details limit how much weight to place on exact numbers; adding these would substantially improve credibility.
- Figure 3 provides a clean visualization of gap-closure ratios by dataset/task type, but lacks uncertainty estimates. It is especially important for pair classification, where the ratio is very low (0.30); error bars could reveal whether this is robust or a data point artifact.
- Table 1 is the central efficacy evidence and is readable; but adding standard deviations and including one or two widely used external baselines would help situate performance.
- Table 2 is striking in favor of the student; without evaluation protocol detail and comparisons to common long-context retrieval baselines, the practical significance is difficult to judge.

## Potentially Missing Related Work
1) Yin et al., “From Slow Bidirectional to Fast Autoregressive Video Diffusion Models,” 2025 — distills a bidirectional teacher into a causal, streaming-capable student with KV caching. Conceptually parallel to this paper’s bidirectional-to-causal transfer; should be discussed in Section 2 and contrasted with the proposed embedding-level MSE + InfoNCE objective in Section 3.3.
2) Shin et al., “MotionStream: Real-Time Video Generation with Interactive Motion Controls,” 2026 — uses distillation to enable real-time streaming with rolling KV caches and sliding-window causal attention. Relevant to Section 3.4’s streaming design; add to Related Work and discuss in the context of infinite-horizon streaming.
3) Kuzina et al., “KaVa: Latent Reasoning via Compressed KV-Cache Distillation,” 2026 — introduces KV-cache–based supervision and latent transfer. Highly relevant to Section 3.3; discuss potential to augment embedding-level distillation with cache-alignment signals.
4) Lee et al., “WAND: Windowed Attention and Knowledge Distillation for Efficient Autoregressive Text-to-Speech Models,” 2026 — combines windowed attention with distillation from a full-attention teacher. Should be cited in Section 2 and compared as an alternative masking+distillation strategy.
5) Chen et al., “StreamingTOM: Streaming Token Compression for Efficient Video Understanding,” 2026 — training-free streaming with bounded KV growth; discuss in Section 3.4 as complementary techniques for long inputs and potential integration with the student to manage KV size.
6) Zheng et al., “Context Distillation as Latent Memory Management,” 2026 — cache-sharing distillation and latent context storage. Relevant to long-context Section 4.4; could inspire memory management that pairs well with the proposed student.
7) Ye et al., “On-Policy Context Distillation for Language Models,” 2026 — distills context-dependent behavior on student trajectories via reverse KL; consider in Section 3.3 as a principled alternative or complement to MSE at the embedding level.
8) Kim et al., “CDLM: Consistency Diffusion Language Models For Faster Sampling,” 2025 — block-wise causal masks restore KV compatibility; include in Section 2 as related ideas for converting non-streaming models to streaming-friendly ones.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify GG-SM computation: For Equation (1), describe exactly how ||∇h_j L|| is obtained and used during training. Is it per-layer or per-token? How are gradients normalized, smoothed, and cached for Equation (2)? What is the wall-clock overhead relative to standard training?
- Provide hardware and implementation details for Figure 2: GPU/CPU type, framework, precision, attention kernels, batch size, and cache layout. Report both absolute latency and tokens-per-second to improve comparability; include a sensitivity analysis to chunk size (Δ) and prefix length.
- Expand evaluation to the full MTEB and include common public baselines: SGPT variants, Causal2Vec-like methods, and competitive instruction-tuned embedders. Also, ensure the Echo baseline follows best-practice settings; report all choices.
- Add ablations: λ in Equation (5), τ in Equation (3), pooling strategies, with and without L2-normalization before MSE, teacher trained without GG-SM vs with GG-SM, and teacher strength vs student performance.
- Long-context protocol details for Table 2: tokenization, truncation, chunking, embedding of queries vs docs, index type, and reranking if used. Consider reporting Recall@k alongside NDCG@10 and include long-context baselines from the literature.
- Statistical reporting: include standard deviations or confidence intervals for Tables 1–2 and error bars in Figure 3. Report significance tests for key claims like “student > Echo” and “student > teacher on LoCoV1.”
- Streaming correctness: the “maximum cosine distance 1.19×10⁻⁶” is good. Please specify whether numerical identity holds across different chunk sizes, mixed-precision modes, and position-encoding schemes.
- Scaling and generality: test on a larger base model and at least one multilingual or domain-shifted dataset to probe generality of the approach.
- Minor presentation: In Section 4.1, explicitly list optimizer, learning rate schedule, total steps, gradient clipping, dropout, and LoRA configs (target modules per layer and whether biases/norms are adapted).

Typos and small nits:
- Page 2, “68.1% gap-closure ratio ... (0.623 vs 0.645)” — correct, but consider adding the explicit computation in the main text as in Section 4.2 for clarity.
- Page 5, caption of Figure 2: ensure consistent spacing for units, e.g., “22 ms,” “67 → 120 ms.”
- Page 6, “7.1 percentage points over the causal baseline” — Table 2 shows 0.284 vs 0.213 (7.1 points), OK. Consider also stating relative improvement.

Criteria that could raise my score:
- Full MTEB results with uncertainty, plus strong public baselines, together with complete implementation details for latency and long-context protocols.
- Ablations on λ, τ, pooling, and GG-SM design, including efficiency measurements for GG-SM.
- Evidence that the Echo baseline and other comparisons are instantiated fairly and per original recommendations.
- Verification at a larger model scale and, ideally, at least one multilingual or domain-shifted setting.

## Confidence
4: Quite sure after careful checking — I inspected the technical exposition, equations, figures, and tables; remaining uncertainty stems from missing experimental details and limited scope.

## Soundness
2.5: Between Poor and Acceptable — The core idea and loss formulation are reasonable, but the evaluation is narrow, several methodological details are missing (especially for GG-SM and latency protocols), and key comparisons/ablations are absent.

## Excitement
2.5: Between potentially interesting and interesting — Useful idea with promising signals, but current evidence and scope are not yet compelling for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is relevant and the preliminary results are promising, particularly the latency behavior in Figure 2 and the long-context win in Table 2. However, the evaluation breadth, missing implementation details, absent ablations, and narrow baselines make it premature for the main conference. With expanded experiments, robust reporting, and clearer methodological detail, this could be a solid Findings paper in a subsequent cycle.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly notes limitations around task-type transfer and model scale. Additional discussion is advised on:
- Bias and fairness: distilling from a teacher trained on specific domains could encode biases into a streaming system that continuously updates user or conversation state. Consider whether streaming updates amplify recency or confirmation biases, and how to mitigate that (e.g., debiasing constraints during distillation).
- Privacy and safety: streaming embeddings for user interactions may carry sensitive information over long horizons. Clarify retention policies, on-device vs server processing, and risks from embedding leakage or linkage attacks.
- Misuse risks: efficient streaming representations could be used for large-scale surveillance or targeted manipulation; include responsible-use guidance and safeguards.

## Ethical concerns
None.

## Needs Ethics Review
No

## Reproducibility
3: Reproducible with difficulty — Equations are specified, but many crucial training and evaluation details are missing (GG-SM computation, latency setup, long-context protocol, optimization schedule), which would likely cause replication variance.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — The paper states code is available; however, the paper itself lacks enough detail to ensure others can easily match results without relying on external material.