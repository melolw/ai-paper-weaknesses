# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper analyzes long-context behavior of large language models using probing on transformer representations, directly fitting ACL topics such as Interpretability/Analysis of Models, Language Modeling, Question Answering, and Resources and Evaluation.

## Minimum Quality
Pass ✅. The submission includes Abstract, Introduction, Related Work, Experimental Setup (methodology and data), Results (Sections 4.1–4.3 with figures), Conclusion, Limitations, and Ethical Considerations. While there are gaps in experimental rigor and clarity, the content is coherent and within ACL scope.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I found no attempts to manipulate the review process or hidden instructions.

# Expected Review Outcome:

## Paper Summary
This paper probes long‑context failures in LLMs by training linear classifiers on last‑token hidden states across layers to predict the position of the gold item in a long prompt. Using two tasks from prior work (key‑value retrieval with UUID pairs and multi‑document QA with one gold document among distractors), the authors compare (i) peak per‑layer probing accuracy at locating the gold position and (ii) the LLM’s final answer accuracy. They consistently find that probes can accurately identify the gold position even when the model’s output is wrong, calling this “know but don’t tell.” Layer‑wise analyses show that middle‑position items require more layers to be encoded, and later peak localization correlates with worse final accuracy.

## Summary Of Strengths
- Clear, focused diagnostic question: whether location information about the gold item is present in intermediate representations even when the model fails to answer.
- Simple, interpretable methodology: layer‑wise linear probes on last‑token embeddings with a standard cross‑entropy objective (Equation in Section 3), trained multiple times to report mean and variance.
- Consistent empirical signal across tasks and models:
  - Figure 2 shows probing peak accuracy outstripping generation accuracy for both 100‑KV and 30‑Doc settings, supporting the central “know but don’t tell” claim.
  - Figure 3 (both panels) demonstrates that mid‑context items require more layers to be “located,” aligning with “lost in the middle” observations while offering a mechanistic, layer‑wise view.
  - Figure 4 quantifies a negative correlation between the layer of peak localization and generation accuracy, adding a useful predictive lens.
  - Appendix figures (Figures 5–8) replicate the broad pattern on Mistral‑7B‑Instruct and Gemma‑7B‑IT, suggesting some model‑family robustness.
- The paper is clearly written and positions probing as a tool to separate “encoding” from “utilization,” which is a useful conceptual distinction for the community.

## Summary Of Weaknesses
1) Train/test leakage and evaluation protocol are under‑specified, risking overestimation of probe accuracy.
   - Section B states that for each layer, 110,000 embeddings are collected and “train a classifier for ten times,” but there is no explicit train/validation/test split, no cross‑validation description, and no held‑out set details. Without a held‑out evaluation, high probe accuracy could reflect memorization of position‑format correlations rather than faithful recoverability of the gold position. This is central to the paper’s claims and must be clarified and fixed.

2) Probing target conflates “position detection” with “content grounding,” limiting the interpretation of “know.”
   - The classifier predicts the ID of the gold pair/document, which is entangled with explicit index tokens and formatting (e.g., “Document [k]”; see Appendix A prompt). The probe may primarily learn cues about indices encoded in the final representation of the last token, not necessarily evidence that the model has retrieved the content. This matters because the headline claim is about “knowing” vs “telling.” If “knowing” is only “which index looks salient,” it is a weaker notion than encoding enough content to answer.
   - Suggested fix: add probes that must recover the value string embedding direction, a document semantic signature, or attention‑weighted features that require actual content access rather than just position.

3) Last‑token‑only probing is a strong but narrow design choice.
   - The method uses only the last token’s hidden state for every layer. This can underestimate or mischaracterize where information is represented, since retrieval signals might be stored in other positions or attention patterns and only intermittently aggregated into the final token. Probing other positions, pooled residual streams, or attention head outputs would yield a more complete picture and could test whether “early‑layer retrieval heads” vs “late‑layer composition” drive the effects.

4) Limited control over key confounders in MDQA.
   - For MDQA, the generation metric is not specified precisely (exact match vs relaxed string match), which affects the magnitude of the “gap” in Figure 2 (right) and Figure 4. There is also no control for distractor difficulty, question type, or document length. Because probe targets are index IDs, increased distractor salience could lower generation accuracy without affecting position locatability, inflating the gap. A controlled ablation varying distractor hardness and context length would strengthen the argument.

5) Scope of datasets and positions is narrow.
   - The main text uses 100‑KV and 30‑Doc prompts with 11 probed positions (Appendix B picks {1, 0.1n, …, 1.0n}). The conclusions about positional bias would be more convincing with denser positional sweeps, more lengths (e.g., 10/50/100/300 docs), and additional long‑context tasks beyond two synthetic/curated settings.

6) Statistical analysis is thin.
   - Section 4.3 mentions a “two‑sided t‑test” with p < 5e‑5 for the negative correlation in Figure 4, but there is no description of the test construction, effect size, or corrections across multiple groupings. The regression line is shown but no slope, confidence interval, or R^2 is reported. This weakens the quantitative weight of the claim.

7) Risk of over‑interpreting “near‑perfect” peak accuracy.
   - Figure 2 (left) appears close to ceiling for probe peak accuracy in KV‑pairs, but Appendix Figure 7 (Gemma, KV) shows slower localization and delayed saturation, and Figure 8 (Gemma, MDQA) shows non‑monotone layer curves with dips. The main text generalizes strongly from LLaMA‑3; cross‑model heterogeneity deserves more attention in the core narrative, not just the appendix.

8) Missing ablations on prompt formatting and indexing scheme.
   - The current prompt explicitly marks documents as [k]. If you remove bracket indices, randomize numbering schemes, or verbalize positions, does the “know but don’t tell” gap persist? This is important to rule out format‑specific shortcuts that probes can latch onto.

9) Limited connection to mechanism and interventions.
   - The paper hints that “early localization helps” (Figure 4) but stops short of testing concrete interventions, e.g., inference‑time attention calibration, retrieval‑guided decoding, or architectural changes. Even a small pilot (e.g., attention reweighting toward the identified position) could bridge diagnosis to remedy and validate the interpretation.

10) Reproducibility details are incomplete.
   - Hyperparameters, optimizer, regularization, and exact training/evaluation splits for probes are not provided. It is unclear whether code or data will be released. Without these, reproducing Figures 2–4 and Appendix figures will be difficult.

Figure‑ and equation‑specific comments
- Figure 2: The persistent gap between the red (peak probe) and blue (generation) curves is the core evidence for the claim. However, without a held‑out probe evaluation and a precise generation metric for MDQA, the magnitude of this gap is hard to trust quantitatively.
- Figure 3: The per‑layer curves nicely show that mid‑position items require more layers to localize; the left panel (KV) peaks around layer ~13, which supports the early‑layer‑retrieval interpretation. The right panel’s “peak then decay” for middle positions suggests late‑layer overwriting or competition, but this would be much stronger with supporting attention‑head or residual‑stream analysis.
- Figure 4: The negative slope indicates that later localization predicts lower answer accuracy. Reporting regression coefficients, CIs, and R^2 would let readers assess practical significance.
- Equation in Section 3: The cross‑entropy objective is standard, but the variable naming is slightly confusing: θi appears as per‑class parameters although indexed by i (data point) in the numerator. Please fix notation to avoid ambiguity (e.g., use θj or Wj for class j).

## Potentially Missing Related Work
1) Ye et al., “DySCO: Dynamic Attention‑Scaling Decoding for Long‑Context Language Models,” 2026 — proposes decoding‑time up‑weighting of task‑relevant tokens via retrieval heads, directly targeting the disconnect between encoded evidence and generation. Should be discussed in Section 2 and referenced in Section 4.3 when interpreting Figure 4; also relevant for proposing interventions.
2) Gao et al., “The First Drop of Ink: Nonlinear Impact of Misleading Information in Long‑Context Reasoning,” 2026 — shows how small amounts of hard distractors disproportionately degrade accuracy. Add to Related Work on positional bias and discuss in Section 4.1–4.2 as an alternative explanation for large probe–generation gaps under distractor interference.
3) Zhang et al., “Positional Failures in Long‑Context LLMs: A Blind Spot in Reasoning Benchmarks,” 2026 — introduces a positional‑aware diagnostic framework. Cite in Section 2 and compare to your positional sweeps; consider adopting their controls for filler content and length in Section 3.
4) Huber et al., “Short Data, Long Context: Distilling Positional Knowledge in Transformers,” 2026 — shows distillation of long‑context positional knowledge; relevant to your finding that earlier localization helps. Discuss in Section 5 as a potential mitigation and in Section 4.2 for interpreting layer dynamics.
5) Schuhmacher et al., “Information Representation Fairness in Long‑Document Embeddings,” 2026 — permutation‑based evaluation for positional and language bias in long‑document embeddings. Add to Section 2 and consider its attention‑calibration ideas alongside your probing in Section 4.2.
6) Bianchi et al., “Hidden in the Haystack: Smaller Needles are More Difficult for LLMs to Find,” 2025 — shows interaction between answer span size and positional sensitivity. Discuss in Section 3–4 to motivate varying gold span lengths in KV/MDQA and to interpret Figure 3’s mid‑position difficulty.
7) Chen et al., “LongBench Pro: A More Realistic and Comprehensive Bilingual Long‑Context Evaluation Benchmark,” 2026 — a richer, controlled benchmark to test whether your probe‑generation gap replicates on naturalistic samples. Suggest as an additional evaluation venue in Section 3/5.
8) Martin et al., “Classifier Context Rot: Monitor Performance Degrades with Context Length,” 2026 — extends long‑context failures to safety monitoring. Include in Section 2 to broaden application relevance and motivate measuring “know vs tell” in decision‑making settings.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
1) Probing protocol and splits
   - Specify and enforce a clean train/validation/test split for probes. Report held‑out accuracy with standard deviations. If already used, clarify explicitly in Section 3 and Appendix B and report the split ratios.
   - Provide probe implementation details: optimizer, learning rate, batch size, regularization, early stopping, number of epochs, and selection criteria.

2) Strengthen “know” beyond index prediction
   - Add content‑aware probes (e.g., whether a probe can linearly predict the gold value embedding or a document semantic fingerprint) and show that probes using only index tokens are insufficient. This will align “know” with semantic retrieval, not just positional salience.

3) Prompt formatting ablations
   - Remove or randomize explicit document indices; verbalize positions; shuffle numbering schemes. Re‑run Figure 2 and 3. If the gap persists, the central claim becomes much stronger and less format‑dependent.

4) Analysis depth
   - Report regression details for Figure 4 (slope, CI, R^2) and provide robustness checks (e.g., bootstrapping over prompts).
   - Add attention‑head or residual‑stream diagnostics to support the “late overwriting” hypothesis suggested by Figure 3 (right).

5) Evaluation and data diversity
   - Define MDQA answer matching precisely (EM, token‑level F1, case normalization). Include qualitative examples of “know but don’t tell” failures.
   - Vary number of documents/pairs (e.g., 10/50/100/300), sweep positions more densely, and control distractor difficulty. Summarize these in an additional figure.

6) Release artifacts
   - Commit to releasing code, probe checkpoints, and the prompt generators for full reproducibility.

Notation and minor issues:
- Section 3 objective: change e^{θ_i^T x_i} to e^{θ_j^T x_i} in the numerator to match class j; or clarify parameter indexing.
- Typos: “are in shown §C” → “are shown in §C”; “dont tell” → “don’t tell”; “ther’re” → “there are”; “it middle context” → “its middle context”.

Criteria for score increase:
- Clear held‑out evaluation for probes with full hyperparameter details.
- Prompt formatting ablations showing the gap persists without explicit indices.
- At least one semantic probe demonstrating content retrieval, not just index prediction.
- Stronger statistical reporting for Figure 4 and added robustness checks.
- Partial intervention experiment (even small‑scale) showing that earlier localization or probe‑identified positions can be exploited to improve generation.

## Confidence
4: Quite sure after careful checking — I checked figures, math, and setup carefully; conclusions depend on clarifying splits and ablations.

## Soundness
2.5: Between Poor and Acceptable — Core idea is interesting and figures are suggestive, but missing held‑out probe evaluation, limited controls, and narrow probing design undermine the strength of the claims.

## Excitement
2.5: Between potentially interesting and interesting — Useful diagnostic framing, but current scope and methodology limit immediate impact.

## Overall Assessment
2.5: Borderline Findings — The paper raises a timely and valuable diagnostic (“know but don’t tell”) with supportive visual evidence (Figures 2–4), yet the evaluation protocol for probes is under‑specified, the notion of “knowing” is conflated with position indexing, and key ablations/controls are missing. With a strengthened probe evaluation (clean splits), content‑aware probes, and prompt‑formatting ablations, this would rise to clear Findings acceptance and possibly main‑track relevance.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges that locating a gold document is distinct from generating a correct answer, but could elaborate on failure modes where late‑layer overwriting leads to hallucination or reliance on recent distractors. Potential societal impacts are indirect: miscalibrated confidence in long‑context LLMs for domains like healthcare or legal assistance. A brief discussion on how to responsibly deploy models given the “know but don’t tell” gap, and on language or domain biases in long contexts, would improve the section.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Core idea is simple, but missing split details, hyperparameters, and artifact release impede straightforward reproduction.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.