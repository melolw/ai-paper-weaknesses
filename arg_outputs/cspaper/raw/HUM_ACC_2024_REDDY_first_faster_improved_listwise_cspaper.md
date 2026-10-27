# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes FIRST, a listwise LLM reranking method that avoids generating the full sequence of passage identifiers. Instead, at inference it ranks candidates by sorting the vocabulary logits of the first generated identifier token. For training, FIRST augments the usual language modeling loss with a learning-to-rank objective applied to those first-step logits, specifically a weighted RankNet that emphasizes high ranks. Experiments on BEIR show improved nDCG@10 over strong LLM listwise rerankers and competitive cross-encoders while reducing latency by about 50%. The paper further shows that listwise rerankers can serve as effective sources of pseudo-relevance feedback for retrievers, improving R@100 when the retriever is optimized with a ranking loss that uses the reranker’s output ordering.

## Summary Of Strengths
- Clear insight and practical design: The central observation, illustrated in Figure 2, that first-token logits correlate well with the full generated ranking motivates the single-token decoding strategy. This is a simple yet effective reframing that reduces decoding cost without architectural changes.
- Empirical gains with a principled objective: The joint objective in Equation 3 combines LM (Eq. 1) and a weighted RankNet loss (Eq. 2) focused on first-token logits. Table 2 shows consistent average improvements from adding the ranking component and its inverse-mean-rank weighting.
- Latency–quality trade-offs are carefully quantified: Figure 4 shows per-window latency scaling favoring FIRST as the window size m increases. Figure 3 demonstrates that, at matched latency budgets, FIRST can rerank more candidates and thus attains higher nDCG@10 across diverse BEIR datasets.
- Strong end-task utility: Using listwise reranker outputs for inference-time relevance feedback is well-motivated and yields higher R@100 than cross-encoder–based feedback (Table 4), with additional gains when combined (CE+LLM).
- Clarity and positioning: The paper is generally well written and easy to follow, with a concise description of data, model, training settings, and sliding-window evaluation.
- Practicality: The method requires no special model components, only a training loss and a different readout at inference, making it easy to adopt.

## Summary Of Weaknesses
1) Fairness and completeness of latency analysis
- Figure 4 compares single-window inference latency for FIRST vs. sequence generation as m varies, but it does not break down time into compute vs. I/O vs. KV-cache reuse. In Figure 3, the latency–quality curves match budgets by varying k, yet details like generation parameters (sampling/temperature), caching strategy, and maximum sequence lengths are not specified. Without this, it is difficult to assess how much of the 50% speedup is contingent on particular decoding or system settings.
- The main system-level baselines that reduce reranking calls, such as ranked list truncation or top-down partitioning discussed in Section 2.3, are not combined with or compared against FIRST in a matched budget to quantify additive effects.

2) Limited backbone and data scope
- All primary results are on a single 7B Zephyrβ backbone and GPT-4–labeled training data from 5k MS MARCO queries (40k instances). It is unclear if the single-token ranking readout generalizes to other backbones or instruction-tuning styles, and whether the gains hold at larger model scales. The conclusion that “substantial efficiency gains are achievable without compromising accuracy” would be stronger with 2–3 backbones or at least one larger model.

3) Identifier-token design and bias
- Section 3.2 uses alphabetic identifiers to ensure single-token coverage. This raises two concerns:
  - Vocabulary prior: Letter tokens may carry priors that interact with prompts and content distribution. It would help to test random permutations or different identifier token sets to demonstrate robustness.
  - Ceiling on m: While the paper notes the window is typically ≤20, many practical ranking scenarios exceed that; the paper does not evaluate how FIRST scales with larger identifier alphabets or alternative single-token surrogates.

4) Training objective design and ablation depth
- Table 2 shows the joint loss outperforms LM alone, and that the weighting helps. However, the paper does not present a sensitivity study over λ in Equation 3, nor analyze how much of the gain arises purely from changing the inference readout vs. the loss. Reporting curves over λ, and an “LM-only but FIRST-style inference” vs. “Joint-loss but full generation inference” matrix would disentangle effects.
- Table 3 compares RankNet, LambdaRank, and ListNet on a subset, but the rationale for the subset is not described, and run-to-run variance or statistical confidence intervals are missing. On Scifact, LambdaRank appears better than RankNet; it would be useful to discuss stability or data characteristics behind these flips.

5) Relevance-feedback fairness
- In Section 4.4 and Table 4, CE feedback uses 100 gradient updates at lr=0.005 while LLM feedback uses only 20 updates at lr=0.001. Since the loss families differ, this may be reasonable, but the paper should show sensitivity curves for both methods with matched computational budgets so the conclusion that LLM feedback “significantly improves recall compared to the cross-encoder reranker” is not confounded by suboptimal CE hyperparameters.
- The conversion from ranked sequence to RankNet targets for distillation is not fully specified, for example whether ties or unlabeled items in k are handled, and what happens when the reranker reorders candidates across overlapping windows.

6) Missing statistical testing and variance
- None of the tables (1–4) report standard deviations, confidence intervals, or significance tests. BEIR metrics can vary non-trivially across runs or with re-ranking windows; without uncertainty estimates, some deltas may be within noise.

7) Limited discussion of potential failure modes
- Figure 2 shows rank agreement between first-token logits and generated ranks decays quickly beyond top ranks even for the finetuned model. The paper argues this is sufficient, but does not quantify how often FIRST misplaces a single highly relevant passage in difficult settings, or whether long-tail errors become more likely for shallow-recall retrievers.
- The method presumes the model computes a consistent list-level judgment before producing the first token. Failure cases where the model relies on chain-of-thought–like internal steps could make first-token logits unstable.

8) Scope of evaluation
- Only BEIR is used, always with Contriever top-100. It would strengthen claims to also test a different first-stage retriever, long-document datasets, or RAG-style pipelines, particularly since Figure 3 argues about latency–quality trade-offs that matter in those settings.

9) Reproducibility gaps
- Training details are reasonably specified, but exact prompts, identifier mapping, and tokenization hygiene for different alphabets are not fully detailed. For latency, batch size, framework versions, and CUDA/transformers configs matter; these are only partially described.

10) Minor clarity issues
- Table 1 and Table 2 headers contain hyphenation artifacts (“DBP-edia”, “NFC- orpus”, “Sci- docs”) that make reading harder. Standardizing MS MARCO capitalization and consistent naming of datasets and models would help.

Figure- and table-specific comments
- Figure 1 is a helpful schematic contrasting explicit sequence generation with FIRST’s single-token logits. It would be even clearer to annotate where the ranking loss is applied (first-token softmax slice) and show how logits over identifier tokens are extracted among the full vocabulary.
- Figure 2 supports the core premise that first-token logits carry global ranking info. However, the curves bottom out around ranks 5–7 and rise later. Please discuss this U-shape and provide numerical agreement per rank to complement the plot.
- Figure 3 is strong evidence for latency–quality benefits under fixed budgets. Still, the y-axis ranges differ across subplots, which can visually amplify small absolute gains on low-scoring datasets like SCIDOCS; consider uniform axes or add absolute deltas per k.
- Table 1 is the central benchmark. FIRST edges RankZephyr in average nDCG@10 while using less training data. Please report the number of tokens decoded per query on average for both methods to make the efficiency story concrete next to accuracy.
- Table 2 cleanly shows the effect of the joint loss and the weighting. Adding a column for “FIRST with LM-only” would isolate how much improvement comes from changing the inference readout alone.
- Table 3 gives a reasonable comparison of ranking losses. Please clarify whether LambdaRank weights were computed w.r.t. nDCG@10 and how the per-pair λ was normalized.
- Table 4 shows compelling recall gains from LLM feedback. Please add sensitivity to the number of updates and learning rate, and CPU/GPU time per query for feedback to quantify cost–benefit.

## Potentially Missing Related Work
- Chen et al., “An Early FIRST Reproduction and Improvements to Single-Token Decoding for Fast Listwise Reranking,” 2024 — reproduces and extends single-token listwise reranking; compare methodology and robustness analyses in Section 2.3 and discuss in Section 4.2 as an external validation of design choices.
- Na et al., “Multi-view-guided Passage Reranking with Large Language Models,” 2025 — proposes a single-step non-generative scoring strategy with multi-view embeddings; relevant as an alternative efficiency path to first-token logits. Add to Section 2.1 and consider as a baseline or discussion point in Table 2/Section 4.2.
- Liu et al., “CoRanking: Collaborative Ranking with Small and Large Ranking Agents,” 2025 — addresses efficiency via a two-stage system-level design; discuss in Section 2.3 as a complementary approach and consider a combined strategy analysis with FIRST as future work.
- Zhou et al., “Shifting from Ranking to Set Selection for Retrieval Augmented Generation,” 2025 — reframes reranking as set selection; include in Section 2.3 to position FIRST’s strict ranking vs. set-based objectives and potential downstream trade-offs.
- Déjean et al., “Efficient Listwise Reranking with Compressed Document Representations,” 2026 — compresses documents to reduce input length and latency; discuss in Section 2.3 as an architectural alternative to FIRST’s decoding reduction.
- Lu et al., “CompRank: Efficient LLM Reranking via Token-Level Compression and Decoding-Free Scoring,” 2026 — pursues efficiency with decoding-free scoring; add to Section 2.3 and contrast with FIRST in terms of latency accounting and integrability into existing rerankers.
- Du et al., “ONE-PASS: Single Forward Pass Decoding for Listwise Reranking,” 2026 — aligns conceptually with minimal decoding; cite in Section 2.3 and compare efficiency–effectiveness as it relates to Figure 4’s single-pass latency story.
- Clinchant et al., “Very Efficient Listwise Multimodal Reranking for Long Documents,” 2026 — explores single-logit scoring with token pruning for long/multimodal documents; include in Section 2.3 to broaden the discussion of methods addressing long-context reranking.

## Comments Suggestions And Typos
Actionable suggestions:
1) Latency methodology and accounting
- Provide a detailed latency accounting: prompt length, average decoded tokens per query for generation, KV-cache settings, batch size, beam/sampling settings, hardware and software stack versions. Add per-component timing (encode vs. decode vs. I/O). Clarify whether you amortize over sliding windows with shared encodings or recompute each window.
- Report “tokens decoded per query” next to Table 1 to ground the efficiency claim numerically.

2) Robustness of identifier tokens
- Evaluate robustness to identifier vocabularies: random letter subsets, different alphabets, symbol tokens, or frequent subword tokens; include rank permutations of identifiers per query to remove priors. A small study would address concerns about token-specific biases.

3) Objective sensitivity and disentangling effects
- Add λ ablations for Equation 3 and a 2×2 comparison: {LM vs. Joint} × {Generation vs. FIRST inference}, ideally on a BEIR subset with means and confidence intervals. This would make clear how much each design choice contributes.

4) Relevance-feedback fairness and cost
- Include sensitivity curves for both CE and LLM feedback under matched compute budgets and show time-per-query for the feedback optimization. Consider reporting results where both use identical step counts and perform a mild hyperparameter search for CE.

5) Broader scope and stability
- Add at least one more backbone (e.g., LLaMA-family or a larger Zephyr/Mistral) to show the generality of single-token ranking. If compute is tight, provide a smaller-scale reproduction on a different 7B model.
- Report run-to-run variance or confidence intervals for Tables 1–4; consider significance testing across queries.

Typos and presentation:
- Table headers: fix hyphenation artifacts like “DBP-edia”, “NFC- orpus”, “Sci- docs”.
- “MS Marco” vs. “MS MARCO” capitalization is inconsistent; standardize.
- Minor spacing around math in Eq. (1)–(3) and consistent notation for identifiers [A…Z] vs. tokens ti.
- In Figure 3, consider harmonized y-axis ranges or add absolute deltas to avoid misinterpretation across datasets.

Criteria for score change during rebuttal:
- Provide thorough latency accounting and sensitivity analyses (λ, identifier vocab, generation settings).
- Add significance tests/variance and at least one more backbone or convincing evidence that the effect is backbone-agnostic.
- Strengthen fairness in relevance-feedback comparisons with matched budgets and hyperparameter sweeps.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
4 Strong: This study provides sufficient support for all of its claims. Some extra experiments could be nice, but not essential.

## Excitement
3.5 Between interesting and exciting.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The idea is simple, effective, and well validated, with clear latency–quality benefits and a useful relevance-feedback application. I would like to see stronger robustness and fairness analyses, but the current version is already solid.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges reliance on GPT-4–labeled data, English-only experiments, and the identifier-token constraint. Additional points to consider:
- Feedback loops: Using LLM rerankers for inference-time optimization of retrievers could amplify biases present in the reranker’s training data. A short discussion on monitoring for topic or demographic skew in recall would be valuable.
- Compute and environmental impact: While FIRST reduces decoding costs, fine-tuning and listwise inference on large windows remain expensive; a brief estimate of energy savings vs. full generation would contextualize the benefits.
- Domain overgeneralization: BEIR coverage is good, but results on long-document or multilingual retrieval should not be inferred; clarifying scope will prevent overuse in settings where identifier-token constraints or long-context behaviors differ.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.

## Datasets
2 Documentary: The new datasets will be useful to study or replicate the reported research, although for other purposes they may have limited interest or limited usability.

## Software
3 Potentially useful.: Someone might find the new software useful for their work.