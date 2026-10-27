# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes IC-Former, a lightweight, LLM-agnostic context compressor that replaces quadratic-cost self-attention over long inputs with cross-attention from a small set of learnable “digest tokens” to frozen word embeddings. The digest vectors then substitute for the original context as a short soft prompt to a target LLM. Training proceeds in two stages: autoencoding-style pretraining to reconstruct the original text from digest vectors, followed by instruction fine-tuning so the digests support question answering over the compressed context. The method targets linear time and space growth in the compression range, reporting 68–112× faster compression and 1/32 FLOPs of a strong baseline (ICAE) while retaining ≥90% of its downstream ROUGE performance on the PwC dataset with Llama2‑7b‑chat.

## Summary Of Strengths
- Clear and simple architecture: Figure 2 concisely shows causal cross-attention from digest tokens to context embeddings, with an attention mask that permits digest-to-all-context and autoregressive digest-to-digest access. This mask choice, together with Equations (1)–(3), yields the stated O(kn + k^2) ≈ O(kn) complexity when k ≪ n.
- Strong efficiency results with careful accounting: Table 2’s FLOP derivation and the supporting Appendix C equations are explicit. Table 1 shows large wall‑clock wins for compression time across multiple batch and sequence lengths, and memory benefits when running the compressor independently from the LLM backbone.
- Sensible training recipe and diagnostics: Figure 3 clarifies the AE pretraining and instruction‑tuning setups. Ablations in Table 4 and the qualitative cases in Table 12 demonstrate that pretraining materially reduces hallucination and improves faithfulness.
- Useful analysis/interpretability: Figure 6 and the full attention maps in Figures 8–11 visualize digest‑to‑context attention. The observed local, diagonal “backslash” pattern supports the authors’ narrative that tokens aggregate neighborhood information, and Table 6’s layer‑wise token categories suggest progressive semantic diversification.
- Reproducibility details: Hyperparameters for model, pretraining, and fine‑tuning are listed (Tables 7–9), and FLOP formulas are made explicit (Tables 10–11), which should ease reimplementation.

## Summary Of Weaknesses
1) Limited empirical scope and baselines
- Only one compressor baseline (ICAE) is benchmarked. Important competitors focused on prompt/context compression are absent as baselines, for example LongLLMLingua and other soft‑prompt or hybrid methods. This makes it difficult to assess IC‑Former’s efficiency–quality trade‑off beyond one comparator.
- Only one LLM (Llama2‑7b‑chat) and essentially one downstream dataset (PwC) are used. The Limitations acknowledge this, but the current scope restricts confidence in generality.

2) Faithfulness and utility metrics are narrow
- Downstream evaluation relies primarily on ROUGE for PwC (Table 4) and BLEU for reconstruction (Table 3). These overlap heavily with surface overlap and length effects and may not reveal whether compressed digests systematically omit salient facts or overfit to prompt templates. More targeted faithfulness metrics (e.g., factual consistency measures) or human evaluation for Q/A correctness would strengthen claims.

3) Pretraining objective and target leakage concerns
- The AE pretraining (Figure 3, Eq. 10) feeds digest vectors plus “[AE]” into the same frozen LLM decoder with teacher forcing on the original context, which is reasonable. However, the paper does not clarify how exposure bias and label leakage are mitigated in reconstruction, nor how this objective balances memorization versus abstraction. Table 5 suggests sensitivity to randomness, but a deeper analysis of failure cases and whether reconstruction encourages trivial copying via positional cues is missing.

4) Fairness and completeness of efficiency measurements
- Table 1 reports compressor‑only vs end‑to‑end times, but does not state whether dataloader, tokenization, and host‑to‑device transfer are included. ICAE requires the target LLM during compression whereas IC‑Former does not; the paper notes this, but it also means the comparison mixes different runtime stacks. A controlled protocol that isolates compute kernels and reports time‑to‑first‑token and end‑to‑end latency with and without KV cache reuse would be more conclusive.

5) Ablations on design choices are thin
- The method’s core claims rely on three choices: causal digest‑to‑digest masking, digest‑to‑all‑context access, and RoPE placement. While Section 3.2 describes these components and Eq. (7)–(9) justify relative position handling, there is no ablation on removing digest‑to‑digest causality, allowing bi‑directional digest interactions, or alternative position schemes. Figure 5 varies k but more architectural ablations are needed to validate the necessity of each element.

6) Divide‑and‑conquer strategy needs deeper evaluation
- The chunked “64+64” approach in Table 4 shows only a small performance drop, but there is no systematic study across chunk sizes, overlaps, or hierarchical aggregation schemes. Since the paper argues scalability to longer contexts in practice, a more thorough analysis of how chunking affects faithfulness and error accumulation is important.

7) Missing comparisons on higher compression ratios and long‑context tasks
- Most results target 4× compression (512→128). It would be informative to include results at 8× and 16×, and on long‑context tasks beyond PwC (e.g., long QA or multi‑passage reasoning). Without this, it is unclear how robust the linear‑time advantage is under aggressive compression or extreme context lengths.

8) Some clarity issues in presentation
- Table 1’s memory column reports two numbers for IC‑Former (“15.96 / 2.38”), later explained as end‑to‑end vs compressor‑only. It would help to present these as two separate columns or annotate them more clearly to avoid misinterpretation.
- Section 4.1 says “we replicate ICAE” without enough training‑setup parity details for strict fairness, beyond using the same target LLM. Key hyperparameters and training budget for ICAE should be specified.

Figure‑ and table‑specific critique
- Figure 2: The attention mask visually supports the O(kn) claim, but the text briefly notes O(kn + k^2). Please quantify the k^2 contribution in practice for your k=128 and discuss whether multi‑layer stacking amplifies this term.
- Figure 6: The local diagonal bands are compelling, yet they cover only a narrow index range on axes. A full‑range plot plus head‑wise variance and entropy statistics would better substantiate the “neighborhood aggregation” claim.
- Table 4: The “performance ratio” row, computed vs ICAE, is helpful. However, report confidence intervals or bootstrap variability to confirm that the ~92–93% ratios are stable, and add absolute differences to reveal practical significance.

## Potentially Missing Related Work
1) Jiang et al., “LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression,” 2024 — Provides strong prompt compression baselines and latency analyses highly relevant to your goal of efficient long‑context processing. Should be discussed in Section 2 and compared empirically in Section 4.2 (Table 4).
2) Wang et al., “Adapting LLMs for Efficient Context Processing through Soft Prompt Compression,” 2024 — A hybrid summarization + soft‑prompt method that targets long contexts; relevant alternative to independent compressors. Discuss in Related Work and, if feasible, include as a baseline in Section 4.
3) Li et al., “Prompt Compression for Large Language Models: A Survey,” 2024 — Offers taxonomy situating independent compressors, soft prompts, and retrieval‑time compression. Cite in Section 2 to clarify positioning and design choices like digest‑to‑all‑context attention.
4) Dai et al., “Pretraining Context Compressor for Large Language Models with Embedding‑Based Memory,” 2025 — Architecturally comparable decoupled compressor with reconstruction‑style pretraining; discuss near Sections 3.3 and 4.2; comparison would strengthen claims about training objectives and linear‑time behavior.
5) Berton et al., “CompLLM: Compression for Long Context Q&A,” 2025 — Segments long contexts and compresses each independently, advertising linear‑time properties; directly relevant to your divide‑and‑conquer strategy in Section 3.3 and Table 4’s “64+64” setup.
6) Li et al., “End‑to‑End Context Compression at Scale,” 2026 — Latent context models trained end‑to‑end; helpful for framing scalability limits and potential future directions. Add to Related Work and Limitations to contextualize how IC‑Former might scale.

## Comments Suggestions And Typos
Actionable suggestions
- Baselines and datasets: Add LongLLMLingua and at least one hybrid or extractive compression baseline. Include another long‑context benchmark (e.g., multi‑document QA or fact‑seeking QA with distractors). Evaluate on a different LLM family to test generality.
- Faithfulness and hallucination: Complement ROUGE/BLEU with factual consistency or answer accuracy metrics (e.g., exact match for specific questions, sentence‑level faithfulness like FACTScore). Include a small human study for answer correctness and attribution to source spans.
- Architectural ablations: Systematically ablate digest‑to‑digest causal masking, vary cross‑attention depth, and try alternate positional schemes. Quantify how each change affects speed and accuracy.
- Efficiency reporting: In Table 1, standardize measurement protocol: report time‑to‑first‑token, tokens/sec, include I/O, tokenization, and H2D transfer; clarify whether KV cache reuse and tensor parallelism are used. Separate the memory columns for clarity.
- High‑ratio and long‑context stress tests: Report 8×–16× compression and contexts beyond 4k tokens using your split‑compress‑concat pipeline; vary chunk overlap to test robustness.
- Pretraining analysis: Examine whether AE encourages copying or true abstraction. For example, evaluate reconstruction on paraphrased or shuffled contexts, and report attention entropy statistics layer‑wise.
- Release: Provide code and trained IC‑Former weights; include scripts to reproduce Table 1, Table 2 FLOP counts, and all evaluation tables.

Minor presentation/typos
- A.3 prompt template: “Response the Prompt based on the below text” → “Respond to the prompt based on the text below”.
- Section 3.2 “We restate Eq.1 & 2” → “Eqs. 1 and 2”.
- Use consistent notation for θbase (Table 7 says “theta base”).
- Section 4.1: “which includes contexts accompanied by corresponding questions” — consider specifying average context length and preprocessing steps.
- Table 1 header: clarify “Memory (GB)” by splitting into “End‑to‑End Peak GPU Mem (GB)” and “Compressor‑Only Mem (GB)”.
- Figure captions: include n and k values used in Figure 6 and specify the exact layer index.

What could change my overall recommendation
- Adding at least one strong prompt‑compression baseline and one additional dataset, plus head‑to‑head faithfulness metrics beyond ROUGE, would likely move my overall to 3.5 (borderline conference) or 4.0 (conference) if the efficiency–quality Pareto holds.
- Clear, controlled latency reporting, along with architectural ablations that confirm the necessity of the mask and RoPE choices, would increase Soundness.

## Confidence
4: Quite sure after careful checking — I checked the main derivations, figures, and tables; there may be details I missed, but my evaluation is unlikely to change drastically without new experiments.

## Soundness
3: Acceptable — Main claims are supported by complexity analysis and experiments, but the empirical scope and baseline coverage are limited, and more ablations and faithfulness evaluations are needed.

## Excitement
2.5: Between potentially interesting and interesting — The linear‑time compressor design is appealing and practical, but the current evaluation is too narrow to be exciting for the main track.

## Overall Assessment
2.5 Borderline Findings — The idea is practical and the efficiency gains are convincing, but the evaluation is too limited in baselines, datasets, and faithfulness metrics for the main conference. With stronger comparisons, broader tasks, and deeper ablations, this could rise to 3.5–4.0.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section that candidly notes the single‑model and single‑dataset scope and the performance gap to ICAE. Potential impacts include enabling real‑time compression for RAG or web data, which can be beneficial. Risks center on information loss and hallucination if compressed digests omit salient evidence; the paper partially addresses this with pretraining and shows qualitative failures in Table 12, but broader faithfulness evaluation and guidelines for safe deployment would help. No clear concerns regarding sensitive data or demographic harms are raised by the current experiments.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Equations, hyperparameters, and profiling setup are given. Lack of released code and incomplete ICAE training details may cause variance.

## Datasets
1: No usable datasets submitted — The work uses existing corpora; nothing new is released.

## Software
1: No usable software released — The paper does not state a code release.