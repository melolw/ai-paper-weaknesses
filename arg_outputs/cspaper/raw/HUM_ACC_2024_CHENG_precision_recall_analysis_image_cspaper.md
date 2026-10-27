# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies how caption precision and recall affect training of text-to-image (T2I) diffusion models. Using a dense-caption dataset with human-written main captions and subcaptions, the authors construct training sets that vary two axes: precision (the proportion of “positive” sentences judged correct vs. “negative” altered sentences) and recall (number of subcaptions per image as a proxy for coverage). They fine-tune PixArt-α with LoRA and evaluate compositional alignment on T2I-CompBench. The main finding is that both axes help, but precision contributes more than recall, especially when precision is already high. They then generate synthetic captions with three LVLMs (LLaVA, BLIP2, uform), estimate their precision/recall using a modified FaithScore, train SD2.1 and SDXL on MS-COCO with these captions, and observe trends consistent with the human-captioned setting. Figure 1 and Tables 2–4 summarize these results.

## Summary Of Strengths
- Clear, focused question: isolates two intuitive factors in caption quality, precision and recall, and examines their effect on compositional alignment.
- Methodological simplicity with practical implications: the construction varying the percentage of positive sentences and the number of subcaptions offers a direct way to probe data quality trade-offs.
- Consistency across human and synthetic caption regimes: the same qualitative conclusion, that precision matters more than recall, appears in both settings.
- Quantitative evidence and concrete benchmarks: the study uses T2I-CompBench with breakdowns by color, shape, texture, spatial, and non-spatial relations. Table 2 makes the precision-vs-recall interaction visible; Table 3 shows that synthetic caption trends align.
- Helpful visualization: Figure 1’s surface plot visually supports the claim that moving toward higher precision raises performance more than purely increasing subcaption count. This figure makes the advocated position digestible at a glance.

## Summary Of Weaknesses
1) Ambiguous operationalization of “precision” and “recall” in human-caption experiments
- Precision is defined as the percentage of “positive” sentences, but negative sentences are created by LLaMA2-70B via edits and word shuffling. The paper states “a negative sentence does not necessarily indicate complete irrelevance,” suggesting partial correctness remains. Without a rigorous annotation protocol quantifying actual factual correctness per token/entity, the precision axis is noisy. This undermines the central causal narrative. Please clarify exactly how many incorrect propositions per negative sentence are typical and how that was verified beyond heuristic generation.
- Recall is proxied by the number of subcaptions (0–3), but the study does not show that adding subcaptions monotonically increases factual coverage of unique entities or attributes in the whole image. Table 1 lists average nouns and tokens per condition, but not unique grounded facts. More content length is not necessarily higher recall.

2) Confounds with caption length and density
- Table 1 shows substantial growth in average tokens with more submasks (e.g., 54.8 → 157.8) and more nouns. This simultaneously changes length, density, and topical breadth, so the recall axis is entangled with several factors. No controls exist for fixed-length variants, which makes it hard to attribute gains to recall rather than length or language modeling benefits.

3) Limited dataset scale and generalization
- The human-annotated analysis uses 8,012 images. Fine-tuning PixArt-α with LoRA for 10 epochs on such a small corpus might produce idiosyncratic effects. The paper claims broad implications for T2I training, but does not test on larger or more diverse human-captioned datasets, nor provide variance across seeds. This weakens generality.

4) Evaluation dependence and potential biases
- The compositional evaluation pipeline relies heavily on BLIP2, CLIP, and object detectors as task-specific judges, which may share biases with training encoders. There is no human evaluation to confirm that the reported differences reflect actual image–text faithfulness rather than judge-specific artifacts.

5) FaithScore-based synthetic caption assessment has circularity and sample-size issues
- Section 4 uses a modified FaithScore with GPT-3.5 for decomposition and LLaVA1.5-13B as the final judge. Since LLaVA is also one of the caption generators, the evaluation likely favors it, as the authors note in Limitations. However, this bias is not quantified, and the probe uses only 1,000 samples from 118k. Table 4’s differences could be within noise if not statistically tested.
- The revised decomposition (ENTITY, SHAPE, COLOR, TEXTURE, SPATIAL, NON-SPATIAL) is reasonable, but the paper does not release prompts, system templates, or adjudication rubrics, leaving reproducibility uncertain.

6) Cross-dataset mismatch across the two parts
- Human-caption analysis fine-tunes PixArt-α on Dense Caption Dataset-derived captions, then evaluates on T2I-CompBench. The synthetic-caption study trains on MS-COCO and again evaluates on T2I-CompBench. The different training corpora and different T2I backbones (PixArt-α vs SD2.1/SDXL) introduce confounds. While the qualitative trend is similar, it is difficult to separate effects of model family, dataset domain, and caption regime.

7) Insufficient statistical reporting
- No confidence intervals, standard deviations, or significance tests are reported for Tables 2–3. Some deltas are small, especially at higher precision levels where recall adds marginal gains. Without error bars, it is hard to tell whether improvements are robust.

8) Under-specified training details and ablations
- LoRA rank, text encoder freeze policy, effective training tokens, and sampling details are missing for PixArt-α. For SD2.1 and SDXL, the paper states 100k iterations, batch size 8, LR 1e-4, but not validation protocols, prompt sampling, checkpoint selection strategy, or the total compute. No ablation checks if longer training equalizes differences between captioners.

9) Equation and notation clarity
- The diffusion loss is given, but the text encoder τθ(c) and image encoder ε(x) are only briefly mentioned and not described for the specific backbones used in each experiment. Since the analysis centers on text conditioning, more precision about which encoders are trained or frozen in each setting would help interpretability.

10) Figure- and table-level interpretation could be tighter
- Figure 1 suggests a larger gradient along the precision axis than along the submask axis, matching the narrative. However, the figure’s color scale and absolute ranges are not explicitly tied to the task-average scores in Table 2, which might confuse readers trying to map visual to numeric gains.
- Table 2 supports the claim that at 0% precision, increasing submasks from 0 to 3 yields a nontrivial average increase (0.2377 → 0.3000). At 100% precision, 0 to 3 submasks improves from 0.3196 → 0.3471, a smaller margin, consistent with diminishing returns from recall. Nevertheless, the paper does not quantify effect sizes or relative improvements per category; some cells show very small shifts that may be within expected variance.
- Table 3 indicates that LLaVA captions outperform others in average scores on both SD2.1 and SDXL. However, because Table 4 reveals heterogeneity in entity count and faithscore, it would help to correlate those metrics explicitly with Table 3 performance via regression or controlled subsampling to strengthen the causal reading of “precision dominates recall.”

Collectively, these issues do not negate the main empirical trend, but they limit the strength of the causal claim and reduce clarity about scope and reproducibility.

## Potentially Missing Related Work
1) Yu et al., “Is Your Text-to-Image Model Robust to Caption Noise?”, 2024 — Directly examines how hallucinations and caption noise affect T2I training and proposes mitigation via confidence-weighted learning. Should be discussed in Related Work and compared conceptually to the present precision-versus-recall framing, ideally in Section 2 and in the discussion following Table 2.

2) Ge et al., “Visual Fact Checker: Enabling High-Fidelity Detailed Caption Generation”, 2024 — Presents a pipeline to generate more faithful, detailed captions. Relevant to Section 4 as a candidate synthetic captioner designed for high precision. Should be cited and, if feasible, included as a captioning baseline.

3) Brack et al., “How to Train your Text-to-Image Model: Evaluating Design Choices for Synthetic Training Captions”, 2025 — Systematically varies synthetic caption properties (length, density, descriptiveness) and measures impacts on alignment/aesthetics. Highly relevant to both Sections 3 and 4; should be discussed and used to contextualize the precision–recall trade-offs.

4) Merchant et al., “Structured Captions Improve Prompt Adherence in Text-to-Image Models (Re-LAION-Caption 19M)”, 2025 — Shows benefits of structured, information-dense captions for controllability in PixArt-Σ and SD2. Compare in Section 4 and reference when discussing caption recall/coverage effects.

5) Gutflaish et al., “Generating an Image From 1,000 Words: Enhancing Text-to-Image With Structured Captions”, 2025 — Demonstrates advantages of very detailed, structured captions with new evaluation loops. Relevant to the recall axis and to long-context encoders; should be cited in Section 2 and discussed where token limits are mentioned.

6) Cheng et al., “CapArena: Benchmarking and Analyzing Detailed Image Captioning in the LLM Era”, 2025 — Provides a benchmark and automatic evaluation methodology for long, detailed captions, analyzing precision/recall and hallucination. Directly relevant to the FaithScore-based analysis in Section 4 and could strengthen evaluation.

7) Zhang et al., “Low-hallucination Synthetic Captions Via Visual CheckList Based Reinforcement Learning for Vision-Language Model Pre-training”, 2025 — Proposes RL-based captioning to lower hallucination, with large-scale recaptioned data. Should be compared in Section 4 as a precision-oriented synthetic caption approach.

## Comments Suggestions And Typos
Actionable suggestions:
- Define and validate precision/recall more rigorously in the human-caption setting. For precision, provide human spot-checks quantifying the number and type of incorrect propositions per negative sentence. For recall, report unique grounded entities/attributes covered by subcaptions using a VQA or grounding tool, rather than relying on token/noun counts.
- Control for caption length. Construct fixed-length conditions for different numbers of subcaptions, or normalize by trimming/rewriting to equal token budgets. Re-run ablations to isolate recall effects from length.
- Report variance. Add multiple training seeds and confidence intervals for Tables 2–3. Even two seeds with standard deviations would make the trends more trustworthy.
- Strengthen synthetic caption evaluation. Reduce circularity by employing an external judge not used as a captioner. Consider human audits on a stratified subset and report inter-annotator agreement. Provide the exact prompts and schemas used for FaithScore decomposition and entity correctness evaluation.
- Tighten cross-regime comparability. Where feasible, keep the T2I backbone fixed across human- and synthetic-caption experiments, or include an overlap experiment that uses the same backbone to better attribute effects to caption properties rather than model family.

Figure- and table-specific comments:
- Figure 1: The surface shows steeper gains along the “Positive Sentences (%)” axis than along “Num of Submasks,” visually corroborating the text’s claim. Annotate the color bar and z-axis with ranges that directly map to the “Average Result” column in Table 2, and cite the exact minimum/maximum to ease cross-referencing.
- Table 2: The average increases from (0% precision, 0 submasks) to (0% precision, 3 submasks) is roughly 0.2377 → 0.3000, while from (100% precision, 0) to (100% precision, 3) is 0.3196 → 0.3471. Consider adding relative improvements and confidence intervals per category. Also, highlight that spatial scores remain low across all conditions, indicating a different failure mode less sensitive to caption tweaks.
- Table 3: LLaVA captions yield the best averages on SD2.1 and SDXL. Provide per-task deltas and significance tests. A regression of model performance against the two caption metrics in Table 4 (#Entities as proxy for recall, FaithScore as proxy for precision) would strengthen the causal reading.
- Table 4: Expand the probe size or provide bootstrapped CIs. Also include per-category FaithScores (e.g., SHAPE, SPATIAL) to analyze whether certain dimensions of precision are more predictive of T2I alignment.

Typos and minor issues:
- Table 1 caption: “tokinzer” → “tokenizer.”
- Consistency: Use a single capitalization for LLaVA throughout.
- Section 3: “Data constructed analysis” → “Dataset analysis” or “Data construction analysis.”
- Clarify that you do not use subimages for training; this is important for understanding how subcaptions relate to whole-image recall.
- Provide LoRA rank, target modules, whether τ(c) is frozen or fine-tuned for each backbone, and sampling details.

Criteria for score movement during rebuttal:
- If you add variance/error bars and control for caption length to cleanly separate recall from length effects, the Soundness score could rise by 0.5–1.0.
- If you replace or complement LLaVA-based judging with an external or human evaluation and show consistent trends, the Overall Assessment could move up by 0.5.
- If you include at least one additional precision-oriented synthetic captioner (e.g., a visual fact-check pipeline) and it behaves in line with the claimed trend, that would also strengthen the case.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Central trend is plausible and supported by multiple tables, but causal interpretation is weakened by construct validity, confounds, and limited variance reporting.

## Excitement
2.5 Between potentially interesting and interesting: The question is timely and practically relevant, but the experimental rigor and scope limit enthusiasm for main-track acceptance.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The core message is useful for practitioners and supported by two regimes and several metrics, but construct validity of precision/recall, confounds with caption length, limited statistical rigor, and evaluation circularity prevent a higher recommendation.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a limitations section acknowledging potential bias from using LLaVA as both captioner and evaluator. Additional points to discuss:
- Dataset licensing and non-commercial restrictions (Dense Caption Dataset CC-BY-NC) may limit broad retraining reproducibility.
- Automated judges may encode social and cultural biases that influence which compositional relations are considered “correct.” Consider discussing fairness implications if these pipelines are used to curate large-scale training data.
- Synthetic captions can propagate hallucinations and stereotypes; the work’s emphasis on precision is positive, but mitigation strategies and audits should be highlighted for downstream deployment.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Many hyperparameters are given, but critical details on LoRA configuration, seed control, and FaithScore prompting are missing; evaluation depends on external APIs.

## Datasets
1 No usable datasets submitted.

## Software
2 Documentary.: The described setup could be instructive, but code, prompts, and scripts are not provided; value is primarily explanatory.