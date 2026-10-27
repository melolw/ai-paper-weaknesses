# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes LLM-TOPLA, a supervised ensemble framework for combining outputs from multiple LLMs across three task types: multiple-choice (MCQ), open-ended numeric/short-answer (OEQ), and sequence generation (GQ). The contributions are: (i) a focal diversity metric that estimates error co-occurrence within a candidate ensemble and a derived “focal diversity” score for the team; (ii) a genetic-algorithm-based pruning procedure to pick small, diverse sub-ensembles; and (iii) two learn-to-ensemble fusion models: TOPLA-Weighted (an MLP over per-choice or CoT-derived answer distributions) and TOPLA-Summary (a seq2seq model with sliding-window and selective global attention that generates a new output). Experiments on MMLU, GSM8K, SearchQA, and XSum report improvements over individual models, majority voting, LLM-Blender, and agent-style ensembling, with ablations on pruning and attention patterns.

## Summary Of Strengths
- Broad scope across task types: The paper formulates three solution spaces and provides two fusion mechanisms, one light-weight for MCQ/OEQ and one seq2seq generator for GQ (Sections 3.1–3.2, Figure 1).
- Clear framework story: Figure 2 gives a comprehensible end-to-end pipeline, from LLM pooling through pruning to learn-to-fuse inference. This helps readers see how components interlock.
- Concrete algorithmic elements: 
  - An explicit diversity score (Equation 10) tied to co-failure rates, and a GA-based pruning strategy that is simple to implement on top of validation logs.
  - A practical TOPLA-Weighted learner using concatenated probability vectors (Equation 3–4), and a TOPLA-Summary generator with sparse/global attention to control context cost (Equation 6–9).
- Useful empirical signals:
  - Correlation plots between focal diversity and accuracy/ROUGE in Figure 3 are informative; they support the premise that choosing small, diverse sub-ensembles can be as good as or better than using all models.
  - Ablations in Figure 4 show pruning often helps and that sliding-window plus selective global attention is beneficial for TOPLA-Summary across datasets.
- Quantitative results:
  - Table 2 shows consistent gains over strong single models for MCQ/OEQ (e.g., +2.2 over Mixtral on MMLU with TOPLA-Weighted; +7.85 absolute over Mixtral on GSM8K with K=10).
  - Table 3 shows very large gains on SearchQA and XSum with the generative fusion.
  - Table 4 benchmarks against Majority Voting, LLM-Blender, and MoreAgents; Table 5 includes XSum comparisons against strong summarization baselines.
- Reproducibility intent: The paper provides an anonymous code link and a dataset of LLM outputs, which, if high quality, can catalyze follow-on work.

## Summary Of Weaknesses
1) Validity and novelty of the focal diversity metric are under-supported.
- Equation 10 defines ρfocal by the ratio P(2)/P(1), with pj as the probability that j models fail together. This is close in spirit to established ensemble diversity/error-correlation measures such as double-fault, Q-statistic, disagreement, or generalized diversity; yet the paper does not situate ρfocal against these well-known metrics or empirically compare pruning guided by ρfocal versus these baselines. Without such comparisons, the case for the new metric’s superiority or even distinctiveness is incomplete. Figure 3 shows correlation with performance, but any error-based diversity proxy would likely correlate with accuracy by construction. Please add comparisons and discussion of trade-offs with classic diversity metrics.

2) Definition of “error” for generative tasks is simplistic and may bias pruning.
- For GQ, errors are defined as “missed 1-grams” (Page 6, lines 469–476), which can be length-sensitive and sensitive to frequent uninformative tokens. This could reward verbose or high-overlap models rather than genuinely complementary ones. It also departs from standard practice (ROUGE-L, BERTScore). The pruning objective and the ρfocal calculation for GQ should be recomputed with more faithful sequence-level metrics, and sensitivity analyses should be reported.

3) Potential issues with evaluation protocol and fairness of comparisons.
- MMLU: The paper states that, because no official train split is available, the test set was randomly split 70/30 and reused multiple times (Appendix D). Training an ensemble on a portion of the test distribution and then comparing against published single-model test numbers or HF leaderboard probabilities risks misalignment with standard evaluation practice. This makes cross-paper comparability weak. Please clarify precisely which numbers in Table 2 come from the re-split setting vs. standard test sets, and avoid mixing them in single comparisons.
- SearchQA: The original dataset is open-book; here, contexts are removed and a closed-book variant is used (Appendix D). Yet Table 5 compares XSum results against fully supervised summarization systems that follow the canonical setup. The setup differences across tasks and systems should be called out and aligned more rigorously, or results should be restricted to settings that are apple-to-apple.

4) Cost-quality trade-offs are not deeply analyzed.
- Although Figure 2 and Table 2 report per-sample latency, TOPLA often requires multiple LLM calls plus a seq2seq pass. The “efficiency” claim is mostly based on pruning fewer models rather than a holistic cost-benefit view. There is no analysis of monetary cost, energy, or throughput trade-offs for S vs. N and K in real deployments. Include plots of performance vs. total tokens or API cost, and analyze how pruning affects end-to-end latency and cost relative to baseline ensembles.

5) Genetic Algorithm (GA) pruning quality is not validated.
- Table 1 reports large runtime gains but does not measure the quality gap against brute-force in terms of the best achievable pruning score or downstream task performance. For small N where brute force is feasible, please report the performance of GA-selected teams vs. truly best teams to establish that speed does not sacrifice solution quality.

6) Notation and clarity issues harm precision.
- In Equation 10, P(1) uses “M” in the denominator while the rest of the paper uses S for ensemble size; this looks like a typo. There are also minor misspellings (“nominator” instead of numerator; “ROGUE” for ROUGE in multiple places). Some symbols in Equations 3–9 are introduced tersely, and the conditioning in Eq. 9 uses w_{<t-1} whereas w_{<t} is typical.
- Model IDs in Tables 2–4 such as “378†1 138†” are not self-explanatory. Please decode them in captions and state S explicitly for each ensemble.

7) Limited hyperparameter and training details for TOPLA-Summary.
- While Appendix D mentions Longformer-Encoder-Decoder initialised from BART, it lacks critical details: attention window size a, number and placement of global tokens, optimizer, learning rate, batch size, warmup, early stopping, epoch counts, and sampling strategy. Reproduction would be difficult without these.

8) Metric and variance reporting are inconsistent.
- Table 2 reports standard deviations for some MMLU columns but not for GSM8K K=1/K=10, SearchQA, or XSum metrics. Figure 4 lacks error bars. Given high variance in LLM prompting, statistical significance should be provided or multiple-seed runs reported where feasible.

9) Risk of tautological correlation in Figure 3 and Figure 6.
- Focal diversity and validation performance are both computed on the same validation set using label-dependent notions of failure. Correlations in Figure 3 and Appendix Figure 6 may be partly tautological. A stronger test is to measure correlation on a separate held-out split or under bootstraps to verify stability.

10) Choice of K and sensitivity for TOPLA-Weighted.
- Figure 4 (rightmost pane) shows K affects GSM8K performance; however, the paper does not examine the optimum K under limited compute or how K generalizes across datasets. A compute-normalized analysis would clarify practical settings.

Explicit figure/table engagement:
- Figure 2 effectively summarizes the pipeline and makes clear that pruning occurs before training fusion models; however, it does not indicate where validation labels are consumed and how much data is needed at each stage, which would aid reproducibility and reveal potential sources of leakage.
- Figure 3’s scatter plots show a positive trend between focal diversity and accuracy/ROUGE, but the visual density near top-right for GSM8K suggests many near-redundant teams; showing Pareto fronts or labeling S values would help understand the diversity-size-performance interplay.
- Figure 4’s first two subfigures show pruning helps for MMLU and GSM8K, but the y-axis lacks confidence intervals; the third subplot supports the claim that sliding+global attention improves performance on all four datasets relative to removing these components.
- Table 2 is central: it shows TOPLA-Weighted outperforming Mixtral on MMLU (72.77 vs. 70.53 HuggingFace LB) and boosts GSM8K substantially at K=10. However, the meaning of “Together-AI” vs. “HuggingFace LB” columns, and the hybrid evaluation protocol, should be clarified.
- Table 3 demonstrates large TOPLA-Summary gains on SearchQA/XSum, but adding per-dataset sample counts used for training and a note on closed-book vs. open-book would contextualize these jumps.
- Table 4 compares against MoreAgents and LLM-Blender, which is valuable; however, including additional routing-based or reward-guided ensemble baselines would strengthen the case.
- Table 5’s XSum improvements are striking; however, explicitly stating training data size for TOPLA vs. baselines and confirming that the same train/test splits and preprocessing are used is needed for fair comparison.

## Potentially Missing Related Work
1) Lu et al., “Routing to the Expert: Efficient Reward-guided Ensemble of Large Language Models,” 2023 — proposes reward-guided routing to select the best model per query, achieving ensemble-level gains at lower cost. It is directly relevant as an alternative to diversity-based pruning and should be discussed in Section 4 when motivating pruning, and considered as a baseline or at least a conceptual comparator in Section 6.1/Table 4.

2) Classic ensemble diversity metrics and analyses:
   - Kuncheva & Whitaker, “Measures of Diversity in Classifier Ensembles,” Machine Learning, 2003.
   - Giacinto & Roli, “Design of Effective Multiple Classifier Systems by Clustering of Classifiers,” ICPR, 2001.
   - Skurichina & Duin, “Bagging, Boosting and the Random Subspace Method for Linear Classifiers,” Pattern Analysis & Applications, 2002.
These works are directly related to the definition and evaluation of error correlation/diversity, and should be compared to the focal diversity metric in Section 4 and in ablations.

3) Reward/routing and mixture-of-experts selection for LLMs:
   - Madaan et al., “Self-Refine,” 2023; 
   - Shankar et al., “WhittleSearch: Efficient LLM selection,” 2023; 
   - Related routing/mixture selection that dynamically chooses LLMs per input. These connect to pruning and could be referenced in Section 1/Related Work as complementary strategies.

4) Robust sequence-level evaluation beyond 1-gram misses:
   - Zhang et al., “BERTScore: Evaluating Text Generation with BERT,” ICLR 2020.
This should be considered in defining GQ error for focal diversity in Section 4.

If the authors already cover some of these in the appendix, they should be elevated into the main text with empirical comparisons.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide side-by-side pruning with alternative diversity metrics (e.g., double-fault, Q-statistic, disagreement) and with “accuracy-only” pruning. Report both pruning score and downstream performance. This will clarify whether focal diversity is necessary and beneficial.
- For GQ, recompute focal diversity using ROUGE-L or BERTScore-based error definitions and redo Figure 3 and the pruning selection. Provide a sensitivity analysis showing whether the chosen metric changes the top-k ensembles and their performance.
- Strengthen evaluation protocols:
  - For MMLU, avoid mixing leaderboard/test numbers with re-splits. Use a clearly defined, held-out validation split for pruning and another disjoint test split for final reporting. Do not report any value that was tuned on the same split it is evaluated on.
  - For SearchQA, clearly label your setup as closed-book and avoid comparisons to open-book systems or to models trained under a different protocol unless you also reproduce them in your setting.
- Add cost-quality plots: accuracy/ROUGE vs. total tokens or API dollars; analyze K and S under compute budgets. This would make the “efficient ensemble” claim concrete.
- Expand training details for TOPLA-Summary: attention window a, number of global tokens and their placement, optimizer and schedule, batch size, gradient accumulation, epochs, early stopping, random seeds, and decoding parameters. Include multiple seeds and standard deviations in Tables 2–5 where feasible.
- Validate GA quality: for small N, report the best team found by GA vs. brute-force in both pruning score and test performance.
- Clarify Table IDs: explain “Model ID” encoding (e.g., “378†1 138†”), the ensemble size S per task, and confirm parallelism settings in latency measurements.
- Figures: add confidence intervals or error bars in Figure 4; in Figure 3, annotate point colors by S and add Pareto contours to make the diversity-size-performance trade-off explicit.

Minor typos and clarity:
- Equation 10: denominator “M” should likely be “S”. Please check.
- Multiple instances of “ROGUE” should be “ROUGE”, and “nominator” should be “numerator.”
- Eq. 9 conditioning term should read p(w_t | w_{<t}, x, Z; φ).
- Page 7/Table 2 caption: “LLMTopla” → “LLM-TOPLA.” Ensure consistent capitalization for “TOPLA-Summary/Weighted.”
- In Appendix D, “BLUE-1” should be “BLEU-1.”

Criteria for changing my recommendation:
- If the authors (a) add rigorous comparisons against classic diversity metrics in pruning and show focal diversity provides clear consistent wins, (b) fix evaluation protocols and report clean held-out test results with error bars, and (c) include compute/cost analyses demonstrating efficiency under budget constraints, my overall score could increase.

## Confidence
4: Quite sure after careful checking. I read the paper carefully, verified equations and tables, and cross-checked the methodology and experiments. Some details could still be in the appendix or code, but the main points are clear.

## Soundness
3.5: Between Acceptable and Strong. The system design is sensible and results are promising, but concerns remain about evaluation protocol alignment, the definition and validation of the focal diversity metric, and incomplete cost analyses.

## Excitement
3.0: Interesting. The framework is practically useful, covers multiple task types, and the large SearchQA/XSum gains are attention-grabbing, but some methodological gaps temper enthusiasm.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. The framework is coherent and empirically promising, especially the general learn-to-ensemble treatment of different task types and the pragmatic pruning approach. However, the focal diversity metric is not sufficiently compared against established diversity measures; the evaluation protocols mix nonstandard splits and task settings; and the efficiency claim would benefit from explicit compute/cost analyses. With strengthened methodological validation and clearer, fairer comparisons, this could be a solid main-track paper; as it stands, it fits well as a strong Findings candidate.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper’s Limitations section acknowledges computational overhead and reliance on labeled Dtrain. Additional points to discuss:
  - Environmental and monetary cost of querying multiple LLMs and training/fine-tuning a fusion model.
  - Potential bias amplification: ensembles of similar pretraining distributions can reinforce shared biases; pruning by error overlap may not explicitly control for fairness or harmful content.
  - Dual-use: improved question-answering and summarization can be misused for disinformation or spam generation. Authors should outline guardrails or risk mitigations.
  - Data licensing and API terms: using third-party APIs may have terms that limit redistribution of outputs; clarify that released datasets respect licenses.

## Ethical concerns
None beyond standard concerns about LLM usage, cost, and potential bias amplification. The paper does not appear to use sensitive personal data.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible. Code and datasets are promised, method is reasonably specified, but TOPLA-Summary training details and some evaluation protocol ambiguities reduce the rating.

## Datasets
4: Useful. If released as stated, the pooled outputs from 8 LLMs across four benchmarks will be valuable for ensemble research.

## Software
4: Useful. An end-to-end pipeline with pruning and both fusion models would be a practical asset for the community.