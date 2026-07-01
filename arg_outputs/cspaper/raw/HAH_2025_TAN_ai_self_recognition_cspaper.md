# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper evaluates whether current LLMs can recognize their own outputs. The authors test 10 API-accessible models in two tasks: (1) exact model prediction among 10 candidates and (2) binary self-identification (yes/no). Two corpora of 1,000 samples each are generated at roughly 100 and 500 words, with cross-evaluation so that each model both generates and evaluates. The main findings are: models rarely predict themselves as the generator, model-prediction accuracy is near random (≈10%), and predictions are heavily biased toward GPT and Claude families. The paper argues these results have implications for bias auditing and AI safety.

## Summary Of Strengths
- Topic relevance and timeliness: Self-recognition in LLMs connects to interpretability, evaluation, and fairness, which are core ACL themes.
- Clear experimental framing: Two complementary tasks (multi-class vs. binary) and two lengths provide a straightforward framework readers can reuse.
- Cross-evaluation matrix: Treating each model as both generator and evaluator offers a systematic view of inter-model confusion patterns.
- Visualizations that make the bias pattern legible: Figure 1’s network diagrams for 100-word and 500-word corpora compellingly show the concentration of predictions on GPT and Claude families, communicating the “clustering” effect at a glance.
- Useful prompts disclosure: Tables 1 and 2 provide verbatim task prompts for multi-class and binary tasks, which is a step toward reproducibility and allows others to probe prompt sensitivity.
- Practical observations: Figures 2–3 and 5 surface conservative behaviors (mostly answering “No” on the binary task) and near-random performance on exact prediction, both of which are informative for those building evaluators or meta-evaluation pipelines.

## Summary Of Weaknesses
1) Core metric choice and baseline interpretation in the binary task are flawed and undercut central claims.
- The paper evaluates binary self-identification primarily with accuracy against a 90% “threshold” (Section 4, Page 4–5). If each evaluator receives a balanced mixture of texts from 10 generators, then the positive class rate for “self” is roughly 10%. A trivial majority “No” classifier will achieve 90% accuracy by construction. Thus, testing “accuracy < 90%” against a binomial null is not evidence of poor self-recognition; if anything, achieving ≈90% accuracy could be a degenerate baseline. This undermines the interpretation in Figure 2 and related text that accuracy “below 90%” signals failure. The paper should instead foreground metrics robust to class imbalance (per-class precision/recall, balanced accuracy, ROC-AUC, PR-AUC) and report the actual fraction of positives per evaluator so readers can verify the base rate.
- While Figure 4 reports F1, the paper does not provide class distributions, confusion matrices, or per-class PR that would let us interpret whether the low F1 is due to tiny positive prevalence or model behavior. Without these, the conclusions about “systematic failure” in self-recognition remain insufficiently supported.

2) Statistical claims are inconsistent and sometimes self-defeating.
- Appendix B states the exact-prediction accuracy is statistically indistinguishable from random (p = 0.75 and 0.34 for the two corpora), which is fine, but then the paper repeatedly uses language like “fundamental limitations” and “architectural rather than methodological” (e.g., Page 2, Page 6–8). The non-significant deviations from random accuracy should temper claims.
- More seriously, Appendix B reports binomial tests for “self-prediction willingness” of 4–5 models out of 10 vs a “conservative 50% expectation,” yielding p = 0.62 and 0.38. These p-values indicate no significant deviation from that expectation, yet the main text (Figure 6 and Page 6) frames this as a “fundamental failure of self-consideration.” The statistical test provided does not support the strength of that claim.

3) Ambiguity about label prevalence and sampling design details that are essential to interpreting results.
- The paper does not explicitly state, per evaluator, the proportion of samples that are truly self-generated in the binary task. If each evaluator saw exactly 10% positives, say so clearly in Section 3 (Task setup) and reiterate near Figure 2. If the proportion varies, provide distributions. This matters for the baseline and the interpretation of Figures 2–4.
- It is also unclear whether evaluators saw the same total number of self vs non-self samples for 100-word and 500-word corpora. Without these counts, readers cannot reconcile accuracy, F1, and yes-rates (Figure 3).

4) Response parsing and prompt-format sensitivity may artifactually depress performance in the multi-class task.
- Section D.3 parses model names via exact string matching (normalizing only case and whitespace). Table 1’s instruction is strict, but LLMs often produce minor format variants (e.g., “OpenAI GPT-4.1”) or add punctuation. Any non-exact but clearly correct answer would be scored wrong. This design choice could push accuracy artificially toward the 10% baseline. At minimum, report the rate of near-miss strings and perform a robustness check with a more permissive canonicalization (e.g., regex or alias mapping).
- Relatedly, the evaluation temperature is 0.6, which invites some variability. A deterministic decoding pass would be a useful ablation to isolate formatting errors vs recognition ability.

5) Overreach in causal interpretation about “architectural limitations.”
- The paper repeatedly attributes failures to deep architectural constraints (Page 2, Page 6–8), but only tests closed, instruction-tuned APIs under one fairly narrow task formulation. The hint ablation is helpful, but it does not rule out many alternatives: prompt framing, allowed output schema, calibration methods, in-context exemplars, or simple alias-acceptance in parsing. Stronger language about “architectural” causes is not warranted given the presented evidence.

6) Inadequate reporting of variance and uncertainty in main figures.
- Apart from a few CIs in text, figures lack error bars. For example, Figure 5 (model prediction accuracy) and Figures 2–4 (binary results) would benefit from per-model CIs or bootstrapped intervals across prompts or samples. As-is, readers cannot judge robustness across prompt sets or seeds.

7) Limited coverage of stylometry and authorship-attribution literature as a baseline.
- The paper cites one stylometry reference [25] and several detector works [11, 19, 26], but does not compare to modern authorship attribution or LLM-stylometry methods adapted to model family id. Even a simple external baseline (e.g., a classifier on function words, perplexity profiles, or rank-features) would contextualize how hard the 10-way model attribution task is under the same data.

8) Insufficient analysis of the content space and prompt coverage.
- Section 3 notes 20 prompts across domains, but there is no breakdown of performance by prompt type, topic, or genre. If the claimed “prestige bias” toward GPT/Claude (Figure 1) is consistent, it should appear across prompt categories. A per-domain analysis could reveal important structure or confounds.

9) Claims about societal impact outrun the evidence presented.
- The paper links self-recognition failure to fairness in hiring and resource allocation (Page 1 and Discussion) but never demonstrates downstream decision-making pipelines where self-recognition is the bottleneck. These applications motivate the work, but the paper should be more cautious and specific about what, exactly, breaks in realistic systems.

10) Reproducibility gaps.
- The paper states code and data “can be made accessible,” but no link is provided. Given heavy reliance on API behavior and response parsing, exact scripts and logs are important to reproduce Figures 1–6 and Appendix figures reliably.

Figure-specific comments:
- Figure 1: The network diagrams effectively convey concentration of predictions on GPT/Claude, supporting the bias claim. However, the figure filters links below 3%; readers cannot assess whether omitted edges would alter the qualitative takeaways. Please also provide the unfiltered confusion matrices as a table or heatmap so the magnitude of the bias is numerically verifiable.
- Figure 2 and Figure 3: When accuracy is judged against an implicit ≈90% majority baseline, the bar plots are potentially misleading. Figure 3’s “Yes Prediction Rate” reveals the conservative pattern, but the paper should juxtapose these with per-class metrics and a trivial-baseline line.
- Figure 5: The near-10% accuracy is clearly shown, but again there are no error bars or per-evaluator confusion matrices to determine whether specific pairs are systematically confusable.

Table-specific comments:
- Table 1 and Table 2: The prompts are helpful. Yet, the requirement “Please respond with exactly one model name” plus strict parsing (Section D.3) likely penalizes otherwise correct answers that include vendor prefixes, hyphen variants, or minimal extra tokens. A results table quantifying how many responses were discarded as format errors would clarify how much of Figure 5’s ≈10% arises from parsing rather than recognition.

## Potentially Missing Related Work
N/A

## Comments Suggestions And Typos
Actionable suggestions:
1) Rebuild the binary self-identification analysis with class-imbalance-aware metrics and transparent base rates.
- Report, per evaluator and corpus, the exact count and proportion of true “self” items.
- Replace the “90% threshold” framing with: majority-baseline accuracy, balanced accuracy, per-class precision/recall/F1, ROC-AUC, PR-AUC. Include confusion matrices.
- Revisit all p-values and claims after correcting the baseline logic. If the main conclusion holds, it will be on firmer ground.

2) Make parsing robust and quantify formatting errors.
- Extend response canonicalization beyond case/whitespace to a small alias map for each model (e.g., “gpt4.1”, “OpenAI GPT-4.1”, “Claude Sonnet 4”). Recompute Figure 5 under strict vs. lenient parsers and report the delta. Also run greedy/deterministic decoding to minimize extraneous text.

3) Add ablations to justify the “architectural limitation” claim.
- Vary prompt framing beyond Tables 1–2: e.g., include compact model IDs inline, provide 1–2 few-shot labeled examples, require JSON field “model”: “…”. Report whether Figures 5–6 move meaningfully.
- Provide a per-domain breakdown across the 20 prompts and show that the clustering in Figure 1 persists across domains.

4) Provide baselines and sanity checks.
- Train a simple external classifier for 10-way model attribution (function-word features, log-rank distributions, or perplexity signatures) on the same corpora. If even a simple baseline exceeds 10%, it reframes the difficulty as specific to LLM self-identification rather than inherent impossibility.
- Evaluate chance and trivial heuristics (always predict GPT-4.1) to quantify how much of the observed pattern in Figure 1 could be explained by a prestige prior alone.

5) Tighten claims and the statistical narrative.
- Align the strength of claims with statistical support. If Appendix B continues to show non-significance for key tests (e.g., self-prediction willingness vs 50%), soften the language in Sections 4–6 accordingly.
- Add error bars or CIs to Figures 2, 4, and 5, and give per-model intervals in the captions.

Typos/clarifications:
- Page 4: “We used a generation temperature of 0.7… evaluation temperature 0.6.” Consider justifying these choices and adding a sensitivity check.
- Page 6: “Only 4–5 models ever predicted themselves…” Pair this with the exact counts per corpus and a table listing which models self-predicted.
- Page 10: “detailed code and results available in the supplementary materials.” No link is provided in the main text; please add one upon camera-ready.
- References formatting on Page 10 is compressed; consider consistent punctuation and spacing.

Criteria that would raise my score:
- Corrected binary-task analysis with proper baselines and full confusion matrices that still support the main conclusions.
- Robust parsing and prompt ablations showing near-random multi-class accuracy is not an artifact.
- Release of code, evaluation logs, and generated corpora, plus at least one external baseline for 10-way attribution.
- Calibrated language around “architectural” causes or, ideally, evidence ruling out simpler alternatives.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5 Between Poor and Acceptable

## Excitement
2.5 Between potentially interesting and interesting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The question is timely, the setup is appealing, and the visualizations are informative, but key analyses rest on a mis-specified baseline in the binary task and inconsistent statistical claims. The strong “architectural” narrative is not yet substantiated. With corrected metrics, stronger ablations, and released artifacts, this could reach solid Findings.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper usefully discusses limitations (Appendix C), including model access constraints and scope. The societal impact section rightly cautions about fairness and bias, but it currently overgeneralizes from text-identification tasks to decision-making systems without an explicit causal pathway. I recommend adding concrete examples of where self-identification is functionally required in a pipeline, how failures would propagate, and what mitigations are realistic. Also note that bias toward “prestige” models could differentially affect regions or institutions relying on alternative providers, raising equity concerns across languages and markets.

## Ethical concerns
None.

## Needs Ethics Review
No

## Reproducibility
3 Reproducible with difficulty: They could reproduce the results with some difficulty. The settings of parameters are underspecified or subjectively determined, and/or the training/evaluation data are not widely available.

## Datasets
2 Documentary: The new datasets will be useful to study or replicate the reported research, although for other purposes they may have limited interest or limited usability.

## Software
2 Documentary.: The new software will be useful to study or replicate the reported research, although for other purposes it may have limited interest or limited usability.