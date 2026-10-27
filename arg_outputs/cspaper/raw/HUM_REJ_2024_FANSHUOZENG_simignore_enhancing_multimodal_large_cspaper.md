# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes Simignore, a training-free token selection scheme for multimodal LLMs that prunes image tokens deemed irrelevant to the current text prompt. The method computes pairwise cosine similarity between image-token embeddings and text-token embeddings after projecting them to a common space, then retains the top-K most similar image tokens and masks out the rest during decoding. The authors also visualize attention “information flow” and embedding distributions to motivate the approach. Experiments on ScienceQA(Image) with LLaVA-1.5 (7B/13B) and Mipha-3B report modest accuracy gains and some inference-time reduction.

## Summary Of Strengths
- Clear and simple idea, easy to plug in. The similarity-based selection requires no model changes or retraining, and the pseudo-code-level description in Section 3 is straightforward to implement.
- Useful qualitative analyses that attempt to connect attention concentration to token importance. The attention visualizations in Figure 4 and the schematic in Figure 3 are helpful for readers trying to reason about where image signal concentrates.
- Experimental signal on efficiency. Table 2 shows latency decreases as more tokens are ignored, which is valuable for practitioners concerned with inference cost.
- The ablations in Section 4.4 go beyond a single setting: varying number of ignored tokens (Table 2), pruning by importance tiers (Table 3), and alternative similarity metrics (Table 4) give some insight into the design space.
- Figure 2 communicates the overall pipeline well, from vision/text encoders to the similarity space and mask construction.

Specific positive note on figures/tables:
- Figure 2 clearly depicts the projection into a shared similarity space and the subsequent Top-K selection and mask construction, making the intended control flow explicit.
- Table 1’s comparison indicates Simignore provides consistent, if modest, gains for LLaVA-1.5-7B (+2.87 points) and -13B (+1.14), and small gains for Mipha-3B (+0.45), supporting generality across backbones.

## Summary Of Weaknesses
1) Insufficient baselines and positioning relative to closely related token-reduction work.
- The paper cites FastV (Chen et al., 2024) and LLaVA-PruMerge (Shang et al., 2024) but does not compare against them experimentally on ScienceQA(Image). Given that both are widely discussed token-reduction approaches, their omission makes it hard to judge Simignore’s relative merits.
- Beyond citing, the paper does not analyze trade-offs between attention-based vs similarity-based selection, nor discuss when one might fail. This limits the work’s significance.

2) Single-benchmark evaluation, modest gains, and absence of significance analysis.
- All core results are on one dataset, ScienceQA(Image), with only zero-shot evaluation. Broader validation on other complex multimodal reasoning tasks (e.g., chart/diagram reasoning, math with images) is important to substantiate generality.
- Improvements in Table 1 are modest for two of the three backbones (+0.45 on Mipha-3B, +1.14 on LLaVA-13B), and no confidence intervals or statistical tests are reported. It is unclear whether these gains are robust.
- Only greedy decoding is used, which may not reflect modern usage where sampling or temperature tuning affects reasoning quality.

3) Ambiguity and potential inconsistencies in the attention/”information flow” analysis.
- Section 3.1 defines token groups and attention masses, but then states the attention matrix shape is (B, H, Nimg, Nimg) and proceeds to reshape it to 14×14 patches. For a decoder-only LLM, attention is computed over all tokens, not just an Nimg×Nimg block. The text seems to conflate attention scores with masks and restricts to image-image attention, which does not match the earlier definition where image, system, and user tokens contribute jointly. The methodology for extracting the heatmaps should be clarified and corrected if necessary.
- Equation (2) already normalizes attention mass across S/I/U to sum to 1 for each query i, but the next sentence says “it is necessary to normalize the above summation results,” which is inconsistent with Eq. (2). Please specify exactly what is normalized at which step.

4) The masking semantics are unclear and potentially incorrect.
- Section 3.2 states “we set their corresponding attention mask to 0 to ignore them” (Eq. 15). In common implementations, a 0 mask typically means “no penalty,” while ignoring requires a large negative bias (e.g., -inf) before softmax. If you overload 0/1 as keep/drop, explain how this integrates into the actual attention computation and in which layers. If you use additive or multiplicative masking, please spell out the formula used in code and which logits are affected.

5) How K is chosen is under-specified and appears tuned on the test set.
- The core method depends on “select the K image tokens with the highest similarity.” However, there is no principled rule or validation protocol for choosing K. Section 4.4.1 sweeps many “ignored numbers” and then reports the best result. Because there is no held-out validation set and all results are on the ScienceQA(Image) test split, this risks de facto test-set tuning. Please report a clear selection protocol that avoids leakage, or provide results across a fixed K chosen without peeking at test outcomes.

6) Limited description of where embeddings come from and when selection is applied.
- Section 3.2 describes projecting ImgEmb and TextEmb to a shared space via F⊃, but it is not stated which intermediate tensors are used in LLaVA-1.5 and Mipha-3B, and at which stage the pruning is enforced (prefill only? All decoding layers? Cross-attention only?). This bears directly on both correctness and efficiency.
- Figure 2 implies a single projection, but realistic MLLMs have multiple bridge/adapter layers; exact placement affects results. Without details, reproducibility is hindered, and the causal story about “information flow” remains speculative.

7) Methodology around Figure 5 is incomplete.
- Figure 5 plots “distribution of image token and prompt token in cosine metric space” and highlights a blue rectangle where they co-locate. It is unclear which dimensionality reduction (PCA/UMAP/t-SNE) is used, on which layer’s embeddings, and with what hyperparameters. Without this, claims about token co-localization are hard to interpret.

8) The cluster analysis and “spy tokens” narrative (Section 4.5) are weakly evidenced.
- Figure 7 and Table 5 intend to show cluster-dependent effects, but Table 5 appears malformed: the rows repeat “✕” across clusters and report alternating T/F results with no clear mapping to which clusters are actually ignored. The logic for the “critical value: 86” and statements such as “these 86 tokens are all located in cluster0” are anecdotal and not derived from a systematic protocol. As written, this section reads like a single-case exploratory vignette and should not be used to generalize about “spy tokens.”
- Figures 8–9 (appendix) show patterns post-clustering, but again lack quantitative backing and ablations to tie them causally to performance changes.

9) Reproducibility details are missing.
- No code link or release statement. The paper does not provide prompts used for ScienceQA(Image), exact LLaVA instruction templates, tokenization and preprocessing, GPU batch sizes, maximum generation lengths, or how masks are applied across layers/heads. Table 2 reports “Running time(/s)” without specifying the number of examples, batch size, sequence lengths, or whether I/O and model loading are included. This makes it difficult to reproduce either accuracy or timing numbers.

10) Scope of claims vs. evidence.
- The paper claims improved “complex reasoning ability,” but at present the evidence is one benchmark with relatively modest gains. The attention and embedding visualizations are interesting but do not establish causality. A stronger causal link would require controlled perturbations that isolate specific token groups and measure consistent, statistically significant effects across multiple datasets and backbones.

Explicit references to figures/tables supporting these points:
- Figure 2 supports the pipeline clarity but also highlights missing details about where in the real model the projectors live.
- Figure 3 and Figure 4 support the qualitative attention-concentration claim, but the described attention tensor shapes in Section 3.1 conflict with standard decoder attention over all tokens.
- Table 1 demonstrates modest top-line gains, but without significance testing and broader datasets, the strength of the claim is limited.
- Table 2 supports inference-time reduction as more tokens are ignored, but absent full runtime protocol details, it is hard to compare across systems.
- Table 3 validates that pruning “important” tokens hurts accuracy, which is consistent with the intended mechanism, yet depends on an under-specified definition of importance and K.

## Potentially Missing Related Work
1) Liu et al., Multi-Stage Vision Token Dropping: Towards Efficient Multimodal Large Language Model, 2024 — Introduces MustDrop, a multi-stage framework to estimate visual token importance across stages. It is directly related to your similarity-based token pruning. Please discuss in Section 2.3 and compare methodologically in Section 3. A quantitative comparison on ScienceQA(Image) or a second benchmark would strengthen Section 4.
2) PuMer: Pruning and Merging Tokens for Efficient Vision Language Models, 2023 — A text-informed pruning and modality-aware merging approach; it uses cross-modal relevance cues closely related to your similarity idea. Add to Related Work (Section 2) and discuss differences after Eq. (11) in Section 3.2. If feasible, include as a baseline.
3) Yang et al., Enhancing Instruction-Following Capability of Visual-Language Models by Reducing Image Redundancy, 2024 — Focuses on reducing redundant visual tokens using relevance to improve instruction-following and reasoning. Cite in Section 2.3; compare conceptual overlap with your mask-based inhibition (Eq. 15–16) and discuss potential integration.

## Comments Suggestions And Typos
Actionable suggestions that could change my evaluation:
- Add strong baselines and broaden evaluation. Include FastV and LLaVA-PruMerge as quantitative baselines on ScienceQA(Image), and add at least one more complex multimodal reasoning benchmark. Report statistical significance where applicable.
- Clarify and correct attention/heatmap methodology. Precisely specify the attention tensor shapes, which heads/layers are aggregated, and how image-only vs full-token attention is visualized in Figures 3–4. If you used cross-attention or decoder self-attention over all tokens, explicate how the matrices were sliced to produce the 14×14 maps.
- Specify where embeddings are taken from, and how the mask is applied. For LLaVA-1.5 and Mipha-3B, name the exact layers/nodes that provide ImgEmb and TextEmb, the projector F⊃ architecture, and whether masking is additive (−inf) or multiplicative, and at which layers/heads it is enforced. Provide pseudo-code for the mask application.
- Define a principled K-selection protocol. Either fix K a priori based on a small validation set, or provide a simple, training-free heuristic that does not peek at test accuracy. Then report all results with that fixed rule. This addresses potential test-set tuning and strengthens claims.
- Tighten the cluster/“spy token” analysis. Replace anecdotal single examples with aggregated statistics over many samples: proportion of tokens dropped per cluster, average accuracy change per cluster dropped, and permutation tests to rule out chance. Clarify Table 5 and ensure each row corresponds to a unique, interpretable cluster-drop configuration.
- Report runtime methodology. For Table 2, state dataset size, number of examples processed, batch size, average sequence length (image+text), hardware details, and whether timings exclude model loading and disk I/O. Consider reporting tokens/sec or wall-clock normalized by total generated tokens.

Typos and clarity issues (non-exhaustive):
- Page 3, Eq. (2) and the sentence immediately after: “To ensure that the sum of attention scores for each token is 1, it is necessary to normalize …” contradicts Eq. (2) which already sums to 1. Rephrase to explain what is normalized in practice.
- Throughout: “markup” seems to intend “prompt” or “tokens.” Please standardize terminology: system tokens, image tokens, user tokens.
- Section 3.1: “perform unsequenced to change the attention matrix” is unclear. Perhaps “reshape” or “permute dimensions”?
- Section 4.1: “single 4090D GPU” is unusual nomenclature; confirm exact GPU model.
- Table 5 appears malformed: many rows are duplicates with identical ✕ entries but alternating results. Please fix.
- Figure 5: state projection method (e.g., PCA with top-2 components), random seed, and sample selection.

Criteria for raising my score:
- Add the missing baselines and a second dataset, and clarify the masking/embedding pipeline and K-selection with a leak-free protocol. If Simignore consistently outperforms FastV/LLaVA-PruMerge or yields competitive accuracy–efficiency trade-offs with clear, reproducible methodology, I would consider a main conference recommendation.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure about the evaluation; however, several implementation ambiguities prevent full verification.

## Soundness
2.5 Between Poor and Acceptable: The idea is plausible and there are promising results, but important methodological details are unclear, baselines are missing, and some analyses are internally inconsistent.

## Excitement
2.5 Between potentially interesting and interesting.: The training-free, similarity-based pruning is convenient, but current evidence is limited and gains are modest on one dataset.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Rationale: Clear, simple technique with some positive results and analyses, but the lack of key baselines, single-benchmark scope, unclear masking/attention methodology, and potential test-set tuning for K collectively limit the strength of the contribution at this time.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly mentions limitations and future work around adaptively selecting the number of tokens. The societal impact discussion is minimal. Potential impacts include efficiency improvements that lower compute cost and energy use, which are positive, but also the risk that pruning alters attention to sensitive visual content and could degrade performance disproportionately on certain image types or domains. Consider analyzing failure cases where pruning harms safety-critical comprehension, and whether pruning amplifies biases by consistently discarding visually subtle but semantically relevant cues.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Core idea is simple, but insufficient details on where embeddings are extracted, exact masking implementation, prompts, and runtime setup impede faithful reproduction.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.