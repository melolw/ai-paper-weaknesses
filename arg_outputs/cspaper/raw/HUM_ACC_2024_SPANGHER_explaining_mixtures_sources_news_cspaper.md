# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies planning for long-form news writing through the lens of source selection. It proposes that a journalist’s plan can be approximated by choosing a schema that partitions sources in an article into categories, such as stance, affiliation, discourse role, etc. The authors operationalize eight schemas (five adapted from prior work and three designed with journalists), train supervised classifiers to assign schema labels to sources, and then compare schemas per document using two latent-structure-inspired metrics: conditional perplexity p(x|z) with a GPT‑2 LM conditioned on schema labels, and posterior predictive p(z|z−,x) via a held-out source-type prediction task. Across 90k news articles, they report that stance and affiliation often best “explain” documents under conditional perplexity, although stance is less predictable under posterior predictive. They also show that the lowest-perplexity schema for an article can be predicted from just the headline with ROC-AUC 0.67. The paper releases NewsSources, a large silver-standard corpus of extracted sources with schema labels.

## Summary Of Strengths
- Framing: The paper offers a concrete, human-centered framing of plan extraction from naturally occurring text, focusing on the practically important case of journalistic source selection.
- Methodological idea: The conditional perplexity and posterior predictive comparisons are a creative adaptation of latent-variable model evaluation to a supervised-schema setting. Figure 1 clearly illustrates the intuition that better plans should lower conditional perplexity and yield more internally consistent posterior predictions.
- Resource: A large-scale pipeline to extract sources and assign schema labels, and plans to release models/code, can be valuable to computational journalism and discourse researchers.
- Empirical breadth: Evaluates eight schemas with diverse provenance, including three developed with professional journalists, and explores topic-dependent preferences (Table 4, Table 5).
- Engagement with figures and analyses:
  - Figure 2 concisely lays out all label sets, which helps readers understand the scope and differences among schemas.
  - Figure 6 provides useful sanity checks about conditional perplexity behavior against random and k-means baselines and the effect of label set size.
  - Figure 3 and Figure 7 analyze cross-schema relationships; it is informative that schemas are largely uncorrelated at the categorical level but perplexities correlate in clusters.
- Human validation: A small but relevant validation with two expert journalists reports F1=0.74 agreement with the inferred “best” schema.

## Summary Of Weaknesses
1) Conceptual validity of conditional perplexity implementation and confounds
- The metric in Equation 3 is implemented by prompting GPT‑2 with schema labels and attributed source text (Figure 2 and the red/green prompt in Figure 2/“img‑2”), then computing perplexity over article text segments. This departs significantly from a clean p(x|z) setting because z is represented via textual tokens and the prompt contains structural markers that carry information beyond the latent structure itself. While the authors try to mitigate via “negative prompting” (Section 4.1; footnote 11), the method may still capture spurious cues:
  - Number of sources and their ordering, token patterns, and label name lexical priors can leak predictive signal unrelated to schema quality.
  - No ablation isolates the contribution of label semantics versus structural tokenization versus source-sequence length; Figure 6 addresses k relative to perplexity for baselines, but not the semantic leakage of label strings themselves.
  - The assumption “green preserves the meaning of x” is strong; the green text is a concatenation of attributed sentences, which may differ stylistically and distributionally from the full article, especially for non-attributed content.

2) Comparability across schemas with different classifier accuracies and classes
- Table 2 shows substantial variance in macro-F1 across schemas (53–68). To “equalize,” the authors introduce noise by random label-swapping for better classifiers (end of Section 3.3) before using their outputs in Section 4. However, this ad-hoc calibration is under-specified and can distort real structural information in ways that vary by label imbalance (Table 8) and class cardinality. There is no quantitative sensitivity analysis of how much noise was introduced per schema, nor a report of results without noise. This undermines the comparability claims in Table 3.

3) Posterior predictive task design and evaluation
- The posterior predictive p(z|z−,x) is operationalized as predicting a held-out source label from headline + remaining labels using a BERT classifier, evaluated by micro F1 (Table 3). Concerns:
  - Using the headline as x for predicting a fine-grained source type seems weakly justified, especially for functional schemas (e.g., Argumentation, Discourse). Unlike Figure 1’s conceptual depiction, the model receives minimal textual context.
  - Micro F1 on highly imbalanced label sets (Table 8) can be misleading. Macro F1 or per-class breakdowns would be more informative, yet Table 3 mixes micro F1 with ratio-to-baselines; the text alternately calls it “micro F1” and simply “F1,” which is confusing.
  - The “4 most-salient sources per article” heuristic may bias toward certain roles or affiliations, affecting comparability across schemas that encode different phenomena.

4) Weaknesses in stance and NLI operationalization
- For NLI, each source sentence is treated as a hypothesis and the article headline as the premise (Section 3.2). Headlines are often rhetorical, elliptical, or lack explicit claims. This premise choice is likely misaligned with factual entailment; it may explain the low NLI F1 (Table 2) and complicate conclusions about NLI’s relative merits (e.g., in Table 6).
- For stance, the dataset is constructed by aggregating multiple datasets, then fine-tuning GPT‑3.5 and distilling to T5. This introduces domain shift and opaque label quality. No cross-dataset or calibration analysis is reported. The later finding that stance has good conditional perplexity but poor posterior predictive (Table 3) may partly be an artifact of this pipeline rather than an intrinsic property of stance planning.

5) Human validation is too thin to substantiate the central claim
- The paper’s key assertion is that conditional perplexity reliably picks the “right” planning schema for a document. The human validation is 120 articles labeled by two journalists with F1=0.74, but:
  - The task details are unclear: Did journalists choose among the same eight schemas? What was the instruction and adjudication process? Was there a tie option? How were disagreements handled?
  - The sample is small relative to 90k articles, with no breakdown by topic or schema, confidence intervals, or inter-annotator agreement reported for this specific task. Without stronger human evaluation, it is hard to accept p(x|z) as meaningfully reflecting planning choices.

6) Statistical analysis and significance reporting
- Table 3 reports t-tests on per-document perplexities, but perplexity distributions are heavy-tailed and non-normal (Figure 5 shows large outliers). Robust tests or bootstrap CIs would be more appropriate. The same concern applies to F1 bootstrapping: clarity on resampling units and class imbalance handling is missing.

7) Baseline design limitations
- The k-means baseline clusters all sources globally using sentence-BERT embeddings, ignoring document-specific structure and topic. This favors schemas whose labels correlate with global lexical clusters. Stronger baselines could include: per-document clustering, topic-conditioned clustering, or contrastive variants that use both source text and headline/topic.
- A meaningful “label-shuffled” control where only label-texts are shuffled but structural markers retained for conditional perplexity is only partly addressed by negative prompting; a direct ablation where labels are replaced by anonymized IDs across schemas would isolate semantic effects of label names.

8) Reproducibility and reliance on closed models
- Several core steps use GPT‑3.5‑turbo fine-tuning for source attribution and stance pseudo-labeling (Sections 3.2, A.1). The paper notes this in Limitations/Ethics, but it still substantially reduces reproducibility and interpretability of the learned signals. The released distilled models may not replicate the same behavior.

9) Claims that stretch beyond evidence
- The abstract and Section 7 state that stance and affiliation “best explain” sourcing overall and that headline-only prediction achieves “moderate accuracy.” Given the design caveats above and relatively modest discrimination (Table 5 shows only 42% affiliation and 18% stance coverage under best-schema assignment), these conclusions should be softened and more clearly scoped.

10) Missing details that impede replication
- Conditional perplexity prompt engineering and training details are brief: tokenization, training/validation splits for GPT‑2 fine-tuning, length truncation, prompt format edge cases, and γ in negative prompting are not fully specified. Appendix E has examples but not full hyperparameters. For posterior predictive, architecture and training details are also sparse.

Specific figure/table-based comments
- Figure 1: The diagram effectively communicates the two metrics, but it presumes label semantics are the only difference across schemas. In practice, label cardinality and leakage through prompt formatting may also drive perplexity differences. An explicit control in the figure or text would help ground readers’ interpretation of p(x|z).
- Figure 2: The schema taxonomy is helpful. However, several categories overlap semantically (e.g., Argumentation-Statistics vs Discourse-Background vs Identity-Document). The paper should discuss expected cross-schema interactions and potential confounds when used as conditioning signals.
- Figure 6: The comparison between k-means and random trials is a nice sanity check for the metric. Still, it underscores that structural clustering alone can move perplexity, suggesting that lowered perplexity is not necessarily evidence of “better” schema semantics.
- Table 2: Macro-F1s are modest and vary widely; given this, the fairness and stability of downstream schema comparison should be accompanied by an uncertainty analysis that propagates classification noise into Table 3.
- Table 3: The mixture of absolute PPL, Δ vs k-means/random, and F1 ratios is informative, but it makes it hard to compare across schemas. Consider unifying to effect sizes with CIs and report macro as well as micro F1 for posterior predictive.

## Potentially Missing Related Work
N/A

## Comments Suggestions And Typos
Actionable suggestions to strengthen the paper:
- Strengthen human validation:
  - Expand the expert study to a larger, stratified sample with per-topic breakdown and multiple journalists. Report inter-annotator agreement and confidence intervals. Ask journalists to rate multiple schemas per article, not just pick one, to capture mixed plans.
- Make conditional perplexity more principled and controlled:
  - Replace label strings with anonymized IDs shared across schemas to remove lexical priors; provide an ablation that varies only the mapping from labels to IDs.
  - Report γ in negative prompting (Section 4.1) and include ablations with γ∈{0, 0.25, 0.5, 0.75, 1}. Also report results without negative prompting.
  - Provide a control where the same labels are randomly permuted across sources within an article to quantify how much of the signal comes from order/position.
- Posterior predictive evaluation:
  - Use macro F1 and per-class metrics; stratify by class frequency (Table 8) and report calibration.
  - Provide text context beyond the headline (e.g., ledes or section headers) to make the prediction task closer to Equation 4’s spirit.
- Stance/NLI pipelines:
  - Justify the headline-as-premise choice with a small human study, or replace it with a claim sentence or lede extracted from the article. For stance, include a cross-dataset calibration and a quality check of GPT‑generated labels on a held-out gold subset.
- Baselines and robustness:
  - Add per-document clustering baselines and topic-conditioned clustering; test “label-ID only” conditioning for p(x|z).
  - Provide results without classifier-noising, plus a sensitivity analysis to the added noise rate.
- Clarify reporting:
  - Clearly distinguish micro vs macro F1 throughout. In Table 3, add uncertainty intervals and robust tests (e.g., bootstrap over documents) for perplexity comparisons due to heavy tails (see Figure 5).
  - In Table 5, add the number of articles per schema and topic; the small fractions for many schemas raise questions about coverage.
- Release plan:
  - Since GPT‑3.5‑based components limit reproducibility, ensure the distilled open models, prompts, and exact preprocessing scripts are released and can reproduce Table 2 and Table 3 within reported variance.

Minor issues and typos:
- Page 4, Table 2 caption: “In Section 2, when we compare schemas” should reference Section 4, where comparisons occur.
- Page 6, “it’s prompt” should be “its prompt.”
- Page 7, “it’s baselines” should be “its baselines.”
- Page 8, “we calculate the lowest-perplexity schema” is repeated; consider removing redundancy.
- Appendix labels: some figures are referenced in-text with numbers that are easy to confuse with main-body Figure numbers; consider consistent labeling (e.g., Fig. A.1).

Criteria for score change during rebuttal:
- Provide an ablation that replaces schema label strings with anonymized IDs and reports conditional perplexity and posterior predictive again, plus γ ablations. If this preserves the main findings with robust uncertainty estimates, I would revise Soundness upward.
- Expand and detail the journalist validation study with statistics and protocol; if it convincingly shows that conditional perplexity aligns with expert judgments across topics, I would consider main-conference acceptance.
- Clarify and improve the NLI and stance setup, especially the premise selection for NLI. Evidence that results are not artifacts of the chosen premise would materially improve confidence.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Some main claims rely on a metric with potential confounds, incomplete human validation, and limited robustness checks.

## Excitement
3.0 Interesting: The framing is interesting and potentially useful for computational journalism, but the current evidence is not yet compelling.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The framing is promising and the analyses are extensive, but core methodological choices for conditional perplexity and posterior predictive introduce confounds, and the human validation is too limited to substantiate the central claims. With stronger controls and a more rigorous validation study, this could mature into a solid contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a candid Limitations and Ethics section noting English-only data, reliance on closed APIs, and dual-use risks in automating journalistic planning. Additional points to discuss:
- Potential amplification of sourcing biases: schemas like Affiliation depend on extraction and labeling choices that may under-represent marginalized voices. Consider an analysis of demographic or institutional skew across sections (e.g., Table 9) and potential mitigations.
- Transparency for newsroom use: if used to suggest “best” schema, tools should expose uncertainty and encourage diverse sourcing rather than enforce homogeneity.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Key components rely on GPT‑3.5 fine-tuning and several prompt engineering choices; more detailed hyperparameters and ablations are needed.

## Datasets
3 Potentially useful: The large-scale silver-standard corpus could be useful, but label quality and closed-model dependencies temper its value.

## Software
3 Potentially useful: If the open-source classifiers and pipelines are released as stated, they will be useful; current reliance on closed models reduces immediate utility.