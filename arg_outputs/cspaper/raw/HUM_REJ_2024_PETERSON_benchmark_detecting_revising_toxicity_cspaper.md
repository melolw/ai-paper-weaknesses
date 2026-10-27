# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces a benchmark focused on toxicity in scientific paper reviews. The authors (1) collect reviews from OpenReview, (2) define a sentence-level taxonomy of toxic behaviors tailored to peer review (accusatory tone, lack of constructive feedback, excessive negativity, personal attacks, sweeping generalization), and (3) build two tasks: binary toxicity classification and sentence-level detoxification (rewriting). They combine human annotation with GPT-4-assisted identification and human verification. For detection, they compare a DeBERTa-v3-feature-based random forest to fine-tuned LLMs (Zephyr 3B and Mistral 7B), reporting best macro-F1 of 0.87. For rewriting, they create 1,402 verified toxic-to-detox pairs and evaluate models via human judgments on 100 samples and several GPT-4–based preference protocols.

## Summary Of Strengths
- Topicality and relevance: Addressing toxicity in peer review is timely and important for the NLP community. The framing is clearly within Human-Centered NLP and Ethics, with potential impact on review culture and tooling.
- Resource contribution: The paper proposes a benchmark with clear task definitions (classification and rewriting) and an explicit, review-specific toxicity guideline (Section 3.2). This domain shift beyond social media toxicity is valuable and underexplored.
- Empirical grounding: The detection task includes a range of baselines, from a traditional random forest with DeBERTa-derived features to fine-tuned LLMs. The best detector (fine-tuned Mistral 7B) reaches macro-F1 0.87 (Table 2), which is a reasonable bar for an initial benchmark.
- Concrete technical findings: The random forest + DeBERTa features is competitive against zero-shot LLMs and gives diagnostic value; fine-tuning smaller LLMs substantially improves detection performance over zero-shot (Table 2).
- Visualization for annotation sanity check: Figure 1 (PCA-2 projection) offers a useful qualitative check that human labels are not entirely random with respect to semantically motivated features; it shows partial separability consistent with a challenging but learnable task.

Specific figure/table–based strengths:
- Figure 1: The PCA-2 plot shows distinct, though overlapping, regions for toxic vs. non-toxic sentences when projected on components associated with “blunt criticism/negative judgment” versus “encouraging/constructive.” This supports the paper’s claim that the taxonomy aligns with linguistically meaningful axes.
- Table 2: Provides a clear macro-level comparison across zero-shot LLMs, fine-tuned LLMs, and the DeBERTa+RF approach, substantiating the claim that fine-tuning yields consistent gains and that the task is solvable to a strong degree.
- Table 1: Offers a transparent breakdown of training/test composition from human and GPT-assisted pipelines, clarifying the class balance and scale for each split.

## Summary Of Weaknesses
1) Missing inter-annotator reliability and detailed annotation protocol.  
- The paper describes a two-stage annotate-then-verify setup with five annotators and a “consult” tag (Page 3), but does not report any inter-annotator agreement (e.g., Cohen’s kappa, Krippendorff’s alpha) or resolution protocol specifics. Given the subjectivity of toxicity, this omission is serious; without reliability statistics across the five categories or even for the binary mapping, the dataset’s label quality is unclear.

2) Limited and potentially biased sampling strategy.  
- The collection intentionally oversamples reviews with scores ≤5 “to ensure a greater representation of toxicity” (Page 3). This likely skews the distribution of both toxicity and linguistic style by review score. There is no analysis of how this affects generalization to the broader review population nor any stratified evaluation by score. It also increases the risk that the detector learns proxies for “negativity/low score” rather than toxicity as defined.

3) Task definition vs. taxonomy misalignment without analysis.  
- The paper defines five toxicity sub-categories (Section 3.2) but collapses them into a binary label for classification (Page 3). No per-category label counts or difficulty analysis are reported, and there is no multi-label or multi-class modeling. Table 6 and Table 7 report per-label (toxic vs. non-toxic) metrics only, leaving the taxonomy underutilized. Readers cannot tell which toxic modes are hardest or whether the model disproportionately flags some categories.

4) Inconsistent and confusing table references and numbering.  
- On Page 6: “A few examples of these issues are present in Table 7,” but Table 7 (Page 10) is “Non-Toxic label performance.” The qualitative examples are instead in Table 5 (Page 8). These inconsistencies hinder readability and call for careful editing.

5) Detoxification evaluation is fragile and relies heavily on GPT-4, with contradictory human findings.  
- Table 3 reports that GPT-3.5 zero-shot achieved 77 human approvals out of 100, Mistral zero-shot 74, Zephyr zero-shot 61, and notably the fine-tuned Mistral only 52. Yet the abstract and conclusion state “Human judgment showed a 76% preference for the revised sentences over the original toxic ones,” which seems to reflect GPT-3.5 zero-shot performance rather than the proposed fine-tuned models. This creates confusion about the main claim for the detoxification component.  
- Table 4 and the “preference test” mainly compare base vs. fine-tuned outputs using GPT-4 as judge. This is methodologically circular given GPT-4 also assisted in dataset creation/verification; it risks evaluator bias and does not adequately measure content fidelity or hallucination rates. The authors do mention hallucination issues for the fine-tuned Mistral (Page 6–7), which further undermines the validity of a GPT-only assessment.

6) Weak fidelity and hallucination analysis for rewriting.  
- The paper correctly flags that revised sentences can change content or numbers (Page 6–7), but there is no systematic fidelity metric, no editing distance constraints, and no human rubric with multiple raters. The human test set is only 100 sentences, with insufficient details on who judged, whether blind to model identity, and inter-rater reliability. Without rigorous fidelity checks, “friendlier but wrong” revisions remain a serious failure mode.

7) Lack of strong, domain-appropriate baselines and external toxicity metrics.  
- The detection experiments do not include widely used toxicity classifiers (e.g., Perspective API / Detoxify variants adapted to this domain), nor do they try off-the-shelf social-media toxicity models re-tuned on the new dataset to control for domain shift. For the rewriting task, external toxicity scorers, politeness classifiers, or style-transfer metrics could triangulate beyond GPT-4 judgments. The absence of such baselines weakens claims about the benchmark’s difficulty and the relative merits of the proposed methods.

8) Reproducibility gaps in modeling details.  
- PEFT/LoRA settings and training hyperparameters are not specified beyond “LoRA and 4-bit” and “four RTX 3070s” (Page 4). Prompt templates are partially shown, but key implementation details for the random forest features are vague: how DeBERTa-v3 outputs were mapped to “keyword/phrase” features, feature dimensionality pre-/post-PCA, RF hyperparameters, and validation strategy are not described. Without these, reproducing the reported 0.87 macro-F1 or the RF baseline is difficult.

9) Evaluation metric reporting confusion.  
- Table 2 is labeled “Macro Result” while also listing overall Precision/Recall/F1/Accuracy; it is unclear whether the precision/recall are macro-averaged or micro/overall. Table 6/7 present toxic/non-toxic label performance separately, but it is unclear how these relate to the macro F1 in Table 2. Provide unambiguous definitions for all metrics per table.

10) Ethical considerations are underdeveloped for a resource paper.  
- The dataset is drawn from OpenReview content; there is no discussion of licensing, consent, privacy protection for identifiable information, or potential harms of releasing toxic sentences. The paper should clearly state steps to anonymize sensitive information, venue policies permitting text reuse, and precautions against doxxing or targeting specific reviewers/authors. Given the topic, a Responsible NLP ethics section is essential but missing.

11) Limited error analysis for detection.  
- Beyond Figure 1, there is little qualitative or quantitative error analysis for the detector. For example, false positives that are harsh but constructive, or false negatives that are short but overtly toxic. Such analysis would help validate the taxonomy and model behavior.

12) Minor but noticeable writing and formatting issues.  
- There are several typos and grammatical issues, e.g., “there is a urgent need,” “The De-Identification Quality metric… you method,” inconsistent capitalization (“The paper”), and inconsistent table back-references as noted above. The writing is generally clear but could use careful editing.

Specific figure/table–based weaknesses:
- Figure 1: While visually helpful, the heavy overlap between toxic and non-toxic clusters suggests that annotation consistency cannot be claimed solely from this projection. A quantitative measure (e.g., silhouette score per class, or clustering separability with a linear probe on the PCA components) would strengthen the argument.  
- Table 3 vs. Abstract/Conclusion: The abstract and conclusion emphasize a “76% preference” for revised sentences, but Table 3’s human approvals show only the GPT-3.5 zero-shot model at 77/100; fine-tuned Mistral drops to 52/100. This discrepancy needs reconciliation.  
- Table 5 (examples): Several “fine-tuned” outputs substantially rephrase the originals. For “Eq. (5) is wrong,” Zephyr’s fine-tuned version shifts the claim to “room for improvement,” which may reduce directness at the cost of accuracy. This illustrates the fidelity risk raised in the text but is not measured systematically.

## Potentially Missing Related Work
1) Ghosal et al., “Peer review analyze: A novel benchmark resource for computational analysis of peer reviews,” 2022 — Provides sentence-level annotations over OpenReview (ICLR) for review structure, aspects, and sentiment. Highly relevant as a source for multi-task signals and as a baseline corpus to contextualize your taxonomy. Should be discussed in Related Work (Section 2) and considered for comparison or as auxiliary training/evaluation in Section 5.

2) Luo et al., “Benchmark on Peer Review Toxic Detection: A Challenging Task with a New Dataset,” 2025 — Directly targets toxicity in peer reviews with a labeled dataset and LLM benchmarking. The taxonomy and prompting strategies appear closely aligned with this paper’s scope. It should be cited in Section 2 and compared empirically in Section 5 to position contributions and difficulty.

3) Purkayastha et al., “LazyReview: A Dataset for Uncovering Lazy Thinking in NLP Peer Reviews,” 2025 — Focuses on low-quality, unconstructive reviewing, which overlaps with your “lack of constructive feedback” category. Discuss in Section 2, and consider using it to probe whether models confuse toxicity with low-effort or vague criticism.

4) Ryu et al., “ReviewScore: Misinformed Peer Review Detection with Large Language Models,” 2025 — Defines and detects “misinformed review points,” which often co-occur with perceived toxicity. Include in Section 2 and consider analysis in Section 5 on whether misinformed content elevates toxicity scores or vice versa.

5) Zhang et al., “Re2: A Consistency-ensured Dataset for Full-stage Peer Review and Multi-turn Rebuttal Discussions,” 2025 — Large corpus of submissions, reviews, and rebuttals with consistency checks. Highly relevant as a source to extend your dataset and to study toxicity dynamics pre- and post-rebuttal. Add to Section 2 and mention in future work.

6) Yu et al., “Is Your Paper Being Reviewed by an LLM? Benchmarking AI Text Detection in Peer Review,” 2025 — Data and methods for distinguishing AI vs. human-written reviews. Useful for analyzing whether LLM-generated reviews differ in toxicity. Discuss in Section 2 and consider auxiliary experiments in Section 5.

## Comments Suggestions And Typos
Actionable suggestions:
- Report inter-annotator agreement for the five toxicity categories and for the binary mapping used for modeling. Describe the annotation interface, training, and adjudication in more detail. Provide confusion matrices across annotators if possible, and per-category counts.
- Clarify sampling and mitigate bias. Provide a realistic test set reflecting natural review-score distributions, or include additional stratified results by score bucket. Analyze whether models are leveraging score or sentiment as a proxy for toxicity.
- Strengthen rewriting evaluation:  
  - Increase human evaluation size, ensure blind, multi-rater judgments with reliability stats; separate judgments for tone improvement and content fidelity.  
  - Introduce automatic auxiliary metrics for toxicity/politeness (e.g., Perspective API, politeness classifiers) to triangulate with GPT-4 judgments.  
  - Add a simple fidelity metric (e.g., semantic similarity constraints, numeric preservation checks, or templated slots for entities/numbers).
- Resolve contradictions around Table 3 and the 76% claim. If “76% preference” refers to GPT-3.5 zero-shot only, state that explicitly in Abstract, Results, and Conclusion to avoid over-generalization to your fine-tuned models.
- Expand baselines: Include adapted off-the-shelf toxicity classifiers and/or domain-adapted sentence-level politeness detectors. For rewriting, compare against a rewrite-by-instruction baseline that enforces constrained edits (e.g., via edit-distance penalties or span-level minimal edits).
- Reproducibility: Provide all hyperparameters (LoRA ranks, alpha, dropout, target modules, batch sizes, LR, epochs, warmup, max sequence length, tokenizer, truncation, early stopping), RF details (n_trees, max depth, feature dimensionality, class weights), and data splits. Release code and the benchmark with clear licenses.
- Ethics and data release: Add a Responsible NLP section. Detail data licensing from OpenReview, steps to anonymize identifiers, masking rules for names/emails/affiliations, and potential harms. Provide a use policy discouraging abusive use and examples of mitigations.
- Figure 1: Add quantitative separability diagnostics. Consider plotting per-toxic-subcategory overlays if available and analyze their relative separability.
- Tables:  
  - Fix table numbering and cross-references (e.g., the Page 6 pointer to “Table 7” should likely be “Table 5”).  
  - Standardize metric definitions; if Table 2 shows macro-averaged precision/recall/F1, say so unambiguously.  
  - Add standard deviations where feasible.

Typos and style:
- “there is a urgent need” → “there is an urgent need.”
- “which you use would obviously get the optimal 20% accuracy here as the we have no way … you method” → grammatical issues in example; consider neutralizing personal references and fixing grammar.
- “The paper and is mutually inconsistent” → “the paper and is mutually inconsistent” appears twice inconsistently capitalized; standardize.
- Use consistent capitalization for “the paper,” “Equation,” “Figure,” etc.

What could change my score:
- Provide robust inter-annotator agreement and a clearer, unbiased evaluation split.  
- Resolve the detoxification evaluation contradictions with larger, more rigorous human studies and fidelity metrics, reducing dependence on GPT-4-as-judge.  
- Add strong baselines (adapted toxicity and politeness models) and clearer, reproducible training details.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5: Between Poor and Acceptable — The detection results are promising, but core resource details (agreement, sampling bias) and the detoxification evaluation (heavy GPT reliance, contradictions with human approvals, limited fidelity guarantees) leave key claims insufficiently supported for the main track.

## Excitement
2.5: Between potentially interesting and interesting — The topic is important and useful, but current evaluation and resource details do not fully deliver on the promise.

## Overall Assessment
2.5 Borderline Findings — The paper may meet minimal standards but requires improvements before being accepted to Findings. The direction is valuable for the community, and initial results are promising. However, the dataset’s annotation reliability, evaluation rigor for rewriting, confusing/contradictory results, missing baselines, and limited ethics discussion prevent a main-track recommendation at this stage.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- Limitations are briefly acknowledged (sentence-level labeling without context), but further discussion is needed on domain coverage, annotator subjectivity, and sampling bias by review score.  
- Societal impact should be expanded to cover: risks of misclassifying frank yet constructive feedback as “toxic,” potential chilling effects on honest critique, and harms from releasing or misusing toxic snippets.  
- Ethics: Clarify licensing/consent for OpenReview content, anonymization/masking policies, and a usage agreement. Consider accessibility and inclusivity across languages and cultures in toxicity definitions.

## Ethical concerns
Significant concerns that should be addressed:  
- Lack of a Responsible NLP ethics section detailing data licensing, consent, and anonymization practices for OpenReview-derived text.  
- Release of potentially identifying or harmful content without clear safeguards.  
- Heavy reliance on GPT-4 for both data creation and evaluation in detoxification may introduce opaque or biased judgments, which should be acknowledged and mitigated.

## Needs Ethics Review
Yes

## Reproducibility
2.5: Reproducible with difficulty — Several missing training and feature-engineering details prevent straightforward reproduction; code and data release plans are not specified.

## Datasets
3: Potentially useful — The dataset could be valuable, but it requires stronger documentation, agreement statistics, ethics documentation, and clearer splits to be broadly useful.

## Software
1: No usable software released — No explicit software release is described.