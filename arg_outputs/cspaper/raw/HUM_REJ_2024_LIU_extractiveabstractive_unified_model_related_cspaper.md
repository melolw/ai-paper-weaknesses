# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes EAU, a unified extractive–abstractive framework for related work generation. An extractive module, the Multi-Granularity Sentence Classification (MSC) model, selects sentences from full-reference inputs without truncation; the selected sentences are concatenated and fed to an abstractive seq2seq model to generate the related work section. To enable joint training, the authors introduce a cross-attention–based optimization that aligns sentence-level selection probabilities from the extractor with decoder cross-attention scores of the abstracter (Equations 9–12). They also construct Delve-aug, a small (5k) LLM-augmented training subset intended to reduce training time while improving performance, plus Delve-cls and Delve-prob to pretrain the extractor and evaluate on the Delve test set. Experiments on Delve(-prob) indicate small ROUGE gains and much faster epoch times when training on Delve-aug. Figures 1–5 depict the architecture and analyses; Table 1 summarizes datasets; Table 2 reports baseline comparisons; Table 3 presents case studies of sentences added/removed by the extractor.

## Summary Of Strengths
- Problem relevance and scope: Addressing long-context, multi-document related work generation is squarely within ACL’s summarization and generation tracks, with practical importance.
- Unified pipeline: The idea of fusing extractive selection with abstractive generation in a single training objective is sensible. Figure 1 clearly communicates the workflow of MSC feeding the abstractive model, and Figure 3 outlines the intended loss coupling via cross-attention.
- Attempt at extractor–generator alignment: The use of decoder cross-attention to guide the extractor (Equations 9–12) is an intuitive way to couple content selection with generation focus. The qualitative plots in Figure 5 suggest the extractor’s distribution stabilizes during training.
- Dataset acceleration angle: Constructing a compact LLM-augmented subset (Delve-aug) to speed training and iterate faster is a useful engineering contribution. Table 1 gives clear statistics, and Table 2 reports substantially reduced epoch time when using Delve-aug (e.g., rows 14 vs. 17).
- Concrete ablations and hyperparameter sweep: The ablation that disables the extractor optimization (Table 2, row 17 vs. 18) provides some evidence that the alignment loss is helpful; Figure 4 explores the impact of λ on ROUGE.

## Summary Of Weaknesses
1) Fragile and under-specified alignment between token-level attention and sentence-level extraction.  
- The extractor outputs sentence-level probabilities p ∈ R^{k×2} (Equation 5), while decoder cross-attention operates at the token level over concatenated inputs of length K. Equation 9 sums M_crs over decoded positions to produce p_crs ∈ R^{1×K}, then Equation 10 compares p_crs to Linear(p) via MSE.  
- The paper does not explain how token-level cross-attention scores are aggregated to sentence-level evidence before supervision, beyond a generic linear projection. Without explicit pooling by sentence boundaries, the signal the extractor receives may be poorly aligned with sentence granularity. This is a central design choice and needs careful justification or a principled mapping. Figure 3 labels d_M and d_K but does not clarify the sentence-token alignment or normalization.
- Additionally, attention weights are not probabilities of utility; they are known to be noisy and head-dependent. No head averaging/normalization strategy is specified. This undermines the validity of Equation 10 as an extractor learning signal.

2) Limited and partially incomparable evaluation; small, inconsistent gains.  
- The strongest claim, that EAU “performs better than state-of-the-art,” is not supported convincingly. In Table 2 (Delve-aug block), EAU vs. BERT-Gen differs by only +0.10 ROUGE-1 and +0.18 ROUGE-L, with equal ROUGE-2 to NG-Abs/CaM; no statistical significance is reported.  
- There is no head-to-head comparison of EAU on the standard Delve test set under the same input convention as prior work. The top block of Table 2 reports Delve results for baselines (rows 1–15), but EAU is not reported there. Instead, EAU is evaluated only on Delve-aug training with Delve-prob test, which differs from standard setups, weakening comparability.
- The paper omits common long-context baselines like LED, PRIMERA, PEGASUS/BigBird-Pegasus, LongT5, or recent specialized related-work generators. Including only Longformer among long-context models is insufficient to establish competitiveness.

3) Potential evaluation artifacts introduced by dataset pipeline.  
- Delve-aug is produced by prompting an LLM to select sentences and rewrite errors, and Delve-prob augments the standard test set with MSC-predicted probabilities (Section 3.5). Using an MSC model trained on Delve-cls (derived from Delve-aug) to annotate the test set could couple the evaluation regime to the proposed architecture. While ROUGE is computed on generated text, the custom test-time inputs and pre-annotations risk hidden biases, especially since EAU’s extractor is pre-trained/optimized with similar signals. A clear statement that ground-truth references and target texts remain unchanged helps, but the paper should better justify that Delve-prob does not inadvertently advantage EAU.

4) Incomplete training and model details hinder reproducibility.  
- Important details are missing: tokenizer/vocab, training steps/epochs, batch sizes, early stopping, validation selection, decoding parameters, sentence selection thresholds, and exact mapping from extractor output to abstracter input (e.g., max number of selected sentences, tie-breaking).  
- The abstractive model has 12 layers and heads (Section 4.1), but learning rate is set to 0.01, which is unusual for Transformer fine-tuning; no warmup, scheduler, or gradient clipping is specified. These omissions make replication hard.

5) Questionable assumption about attention as supervision and lack of controls.  
- The core assumption “sentences with higher positive probability should receive more attention” is not validated. There is no analysis showing a correlation between attention mass and human-judged content utility.  
- No variant is tested that uses simpler and arguably more faithful supervision signals (e.g., KL divergence after per-sentence attention pooling, or binary cross-entropy against oracle-selected sentences when oracle labels are available). This makes it difficult to attribute small gains to the proposed MSE-based alignment rather than, say, stabilizing regularization.

6) Weak ablation and analysis depth.  
- The ablation (Table 2 row 17 vs. 18) removes the optimization and equates the model to BERT-Gen, which is not rigorously justified. BERT-Gen is an encoder–decoder architecture, while the ablation here is “abstractive-only within EAU,” likely with different inputs defined by a frozen extractor; these are not identical.  
- Figure 5 shows “smoothed” extractor probabilities across epochs, but it plots logits with very small ranges (~0.02–0.06), which are hard to interpret, and does not connect distributional changes to ROUGE changes. Table 3’s cases are anecdotal and do not quantify selection precision/recall relative to oracle.

7) Claims about speed are mostly due to using fewer training instances, not architectural efficiency.  
- The order-of-magnitude speedups reported when training on Delve-aug (Table 2, rows 14–17) conflate dataset size with model efficiency. There is no per-step or per-token-time comparison. For a fair efficiency claim, compare equal-sized datasets and report tokens/sec or wall-clock per epoch at fixed sample counts.

8) Dataset construction is under-documented and may not be reusable.  
- The prompt for ChatGLM3 is given, but not the exact sampling process, failure handling, or deduplication. Table 1 indicates vocabulary and output length differences across datasets, but the paper does not release data or code nor provide a clear protocol to regenerate Delve-aug/Delve-cls/Delve-prob. This reduces the value of the dataset contribution.

9) Missing or inconsistent details and typos reduce clarity.  
- “RRG” in Table 2 conflicts with “RGG” in text. “Table 4.5” is referenced instead of Table 3 in Section 4.6. Duplicated citation entries (Xing et al., 2020a and 2020b with same title). Some notational points are unclear: in Equations 6–8, s' = ĥs[:, 0] suggests taking the first token of each sentence; this should be stated explicitly and justified (e.g., [CLS] token usage).

10) Figure/table-specific concerns.  
- Figure 3 is central to the claim: it visualizes summing the decoder cross-attention matrix along d_M to match extractor distributions. However, the figure and Section 3.4 do not specify how multiple heads/layers are combined, whether attention is normalized per step, or how padding is handled. This undermines the core methodological claim.  
- Table 2 results are very close across systems; without significance tests or human evaluation, the claim that EAU “performs better than the state-of-the-art” is not substantiated.

## Potentially Missing Related Work
1) Shi et al., “Towards a Unified Framework for Reference Retrieval and Related Work Generation,” 2023 — Proposes a unified framework connecting retrieval/selection and generation, closely related to EAU’s extractive–abstractive unification. Should be discussed in Section 2 and compared experimentally if possible; at least position EAU’s alignment loss versus their joint training strategies.

2) Docekal et al., “OARelatedWork: A Large-Scale Dataset of Related Work Sections with Full-texts from Open Access Sources,” 2024 — Provides a large-scale full-text dataset and benchmarks for related work generation with long contexts. Discuss in Sections 2 and 4.1 as an alternative to Delve for long-context evaluation; consider reporting results or explaining constraints.

3) Wang et al., “What can rhetoric bring us? Incorporating rhetorical structure into neural related work generation,” 2024 — Introduces discourse- and rhetoric-aware modeling to improve coherence. Discuss in Section 2 and relate to EAU’s content selection; potentially add a baseline or ablation using rhetorical signals alongside attention-based alignment.

4) Long-context summarization baselines:  
   - Beltagy et al., 2020: Longformer is included, but more recent strong models should be acknowledged:  
   - LED (Longformer Encoder-Decoder), PEGASUS/BigBird-Pegasus (Zaheer et al., 2020; Manakul et al.), PRIMERA (Xiao et al., 2022), LongT5 (Guo et al., 2022). These should be discussed in Section 2 with rationale for inclusion/exclusion and, where feasible, compared in Table 2.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify alignment granularity. Precisely describe how token-level cross-attention is converted into sentence-level supervision. A simple and more faithful approach is to sum token attentions within each sentence boundary and L1/L2-normalize per sentence before computing a divergence with the extractor’s sentence probabilities. Please specify head/layer aggregation and normalization choices, and provide a control experiment that uses sentence-pooled attention versus the current Linear(p) projection approach.
- Validate the core assumption. Add an analysis correlating sentence-pooled attention mass with gold or oracle sentence utility (e.g., based on ROUGE to target sentences, or human labels). If attention is not a reliable proxy, consider alternative signals (e.g., gradient-based attribution, input salience from attention rollout, or supervision from oracle content selection).
- Strengthen evaluation on standard Delve. Report EAU trained and evaluated on the canonical Delve setup with consistent input trimming used by prior work, alongside your long-input setting. Add statistical significance testing. Where possible, include stronger long-context baselines (LED, PRIMERA, BigBird-Pegasus, LongT5) or justify their exclusion.
- Separate efficiency from dataset size. Provide per-step throughput and wall-clock comparisons on the same number of training examples/tokens for EAU versus strong abstractive baselines. If the main acceleration is from dataset curation (Delve-aug), state this explicitly and reframe the claim accordingly.
- Reproducibility. Provide full training details: tokenizer/vocab, batch sizes, gradient accumulation, warmup/scheduler, number of epochs, early stopping/selection criteria, decoding settings, the sentence selection threshold and max selected sentences, and exact pretraining procedure on Delve-cls.
- Human evaluation or expert study. Given the small deltas in Table 2, a small-scale human evaluation on coherence, coverage, factuality, and citation appropriateness would increase confidence in the claimed quality gains. Alternatively, include BERTScore or QAEval as additional automatic measures.
- Delve-aug pipeline documentation. Detail the sampling, error handling, and quality control for ChatGLM3 outputs; report inter-run variance; and, if possible, release scripts/prompts and a small anonymized sample to facilitate reuse. Explicitly confirm that Delve-prob only augments inputs with predicted probabilities and does not alter ground-truth targets.

Typos/inconsistencies:
- Section 4.6: “Table 4.5 shows…” should be “Table 3 shows…”.  
- Table 2: “RRG” should be “RGG” for consistency with text.  
- Duplicate citations for Xing et al. (2020a, 2020b) with the same title; verify which is correct.  
- Section 3.3: clarify that s' = ĥs[:, 0] refers to the first token embedding per sentence (e.g., [CLS]); justify this choice.  
- Several capitalization/style inconsistencies (e.g., “longformer” in Table 2 row 10 vs. “Longformer” in text).  
- Minor grammar issues throughout; a careful proofreading pass will help.

Conditions under which my score could increase:
- Provide a rigorous sentence-level alignment method and analysis showing that the proposed loss meaningfully improves selection quality, plus stronger baselines and standardized Delve results with significance testing.
- Add either human evaluation or stronger automatic metrics demonstrating clear, consistent quality gains beyond small ROUGE differences.
- Release code and data or provide sufficient details to reproduce results, including all training and decoding hyperparameters.

## Confidence
4: Quite sure after careful checking — I checked the key equations, figures, and experimental tables; it is unlikely I missed something that changes my assessment.

## Soundness
2.5: Between Poor and Acceptable — The core idea is plausible, but the alignment mechanism is under-specified and the evaluation is not sufficiently controlled or competitive to fully support the claims.

## Excitement
2.0: Potentially Interesting — The unified extractive–abstractive angle is interesting, but the current evidence is not compelling.

## Overall Assessment
2.5 Borderline Findings: The paper has an interesting direction and a sensible high-level design, but key methodological details around attention–selection alignment are missing, and the evaluation lacks rigorous, comparable baselines on the standard setup. With stronger analysis, clearer alignment mechanics, and more competitive experiments, it could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper briefly notes scalability and LLM-dependence in Section “Limitations.” Additional points to discuss:  
  - Potential copyright/licensing issues when using LLMs to transform or extract from copyrighted scholarly texts.  
  - Bias amplification or topical skew introduced by LLM-based extraction, which might preferentially select certain phrasing or fields.  
  - Risk of hallucination in the abstractive stage; mechanisms to avoid generating incorrect attributions or misrepresentations should be discussed.  
  - Language/domain coverage: Delve is primarily English and CS-heavy; results may not generalize to other disciplines or languages.  
- Suggest adding a clearer statement of responsible release plans (data/code), privacy/copyright considerations, and limitations on use in academic authoring workflows.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Several critical hyperparameters and pipeline details are missing; code/data are not promised.

## Datasets
1: No usable datasets submitted — The paper introduces Delve-aug/Delve-cls/Delve-prob but does not state that they will be released in anonymized form, nor provide sufficient protocol to fully reproduce them.

## Software
1: No usable software released — No code or detailed implementation package is provided or promised.