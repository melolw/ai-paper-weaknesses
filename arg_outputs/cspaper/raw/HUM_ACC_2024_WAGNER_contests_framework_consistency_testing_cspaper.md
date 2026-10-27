# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces ConTestS, a framework to test whether language models produce consistent joint probabilities for short spans when the joint is computed via two mathematically equivalent factorizations. For two adjacent tokens, the paper compares P(xi)·P(xi+1|xi) with P(xi+1)·P(xi|xi+1), defining a log-discrepancy d as the difference of the two log-joints. It uses nonparametric Wilcoxon signed-rank tests to assess whether discrepancies are symmetrically centered at zero and regression analyses to probe factors explaining variance, across both MLMs and autoregressive models. Experiments cover Wikitext-2, a post-cutoff News dataset, and synthetic data. Main findings: all models show statistically significant inconsistency except a couple of cases on News; MLMs generally have smaller median discrepancy and become more consistent as size grows, whereas autoregressive models show larger and often size-increasing discrepancies; entropy statistics correlate with the better decoding order and can be used to prefer an order likely to assign higher likelihood to the gold span.

## Summary Of Strengths
- Conceptual clarity and relevance: The question of whether token/span scores behave like coherent probabilities across equivalent factorizations is central to treating LMs as density estimators. The setup relating Equations 1–2 to PMI (Equation 3) is crisp and accessible.
- Methodological simplicity with statistical discipline: The discrepancy definition d (Equation 4) and the use of a paired two-sided Wilcoxon signed-rank test with Benjamini–Yekutieli correction is reasonable for a nonparametric setting with heavy tails and many samples (§5.2).
- Careful model coverage: Both MLMs (RoBERTa, XLM-R, ELECTRA generator) and several autoregressive families (Flan-T5 small→xxl, LLaMA-2 base and chat, various sizes) are examined, permitting meaningful cross-family comparisons (Sections 6–8).
- Post-cutoff data: Using fresh News articles (§5.3) helps eliminate training exposure confounds and makes the claims more credible than solely using Wikitext.
- Figures and analyses that directly support claims:
  - Figure 2: Clear boxplots show discrepancy distributions per model, separating MLMs (purples) and AR models (greens). Medians nearer zero for MLMs and offset medians for many AR models align with the narrative that AR models are less consistent.
  - Figure 3: Rank distributions of gold tokens for Rank 1 and Rank 2 highlight task comprehension differences between MLMs and AR models; LLaMA-2-Chat’s poor ranks are visible.
  - Figure 4: Violin plots of correlations between four entropy terms and d show consistent sign patterns, supporting the claim that entropy cues can guide decoding order.
  - Table 1: Regression of discrepancy variance against size, data size, and type shows size-dependence and captures variance reasonably (R^2 ≈ 0.78–0.79).
- Practical takeaways: The entropy-ordering finding in §9 provides an actionable heuristic for choosing a decoding order that is more likely to give higher gold-span likelihood, with concrete qualitative examples in Appendix F.

## Summary Of Weaknesses
1) Cross-model comparability compromised by tokenization and per-model sample differences.
- Section 6.2 states that “the exact set of word pairs evaluated in each dataset differed between models as different model types have different tokenizers,” and for large AR models the sample is further reduced due to compute. This undermines any strict cross-model or cross-size comparison of discrepancy distributions and especially the regression in Table 1, which treats models as observations of a single response derived from different underlying sample sets. Since the set of pairs, vocabulary units, and even span boundaries differ, part of the between-model variance could be sampling artifacts rather than model behavior.
- Why it matters: Conclusions like “variance increases with size for AR, decreases for MLM” are sensitive to which pairs are included. Without a shared sample across models (e.g., byte-level alignment or a fixed wordpiece sequence map), regression coefficients conflate model property with dataset selection.

2) Statistical testing focuses on symmetry about zero, not equality of the two factorizations or effect size.
- The Wilcoxon signed-rank test of symmetry around zero (Equations 5–6) is appropriate for detecting location shifts, but it is not a direct test of equality of the two factorizations. Moreover, no effect-size metrics (median d, median |d|, or robust Cohen’s d analogs) and no confidence intervals for medians are reported. With huge N, even tiny, practically negligible shifts will be “significant.”
- Why it matters: The practical impact of inconsistency is not quantified. Readers need effect sizes and CIs to gauge relevance in downstream uses like reranking or calibration.

3) Regression modeling (Table 1) likely suffers from small-N per group, heteroskedasticity, and omitted-variable bias.
- Section 5.4 and Table 1 model variance of d as a linear function of size, data size, and type, with an interaction for size×type. However, the number of model instances per family is small, and variance estimates are themselves noisy and sensitive to per-model sample differences. No checks for heteroskedasticity, robust standard errors, or model diagnostics are described.
- Why it matters: P-values can be misleading with small and unbalanced samples and nonconstant variance; conclusions about “size effects” should be tempered or supported by alternative analyses (e.g., nonparametric trend tests within families on comparable subsets).

4) Potential confounds for autoregressive models: instruction following, EOS handling, and quantization.
- Section 6.1 notes 4-bit quantization for all AR models. Quantization can distort logprobabilities in nontrivial, model-size-dependent ways. The paper also shows that T5 is biased to complete spans “by order” and that reversing order decreased likelihood generally. Moreover, EOS modeling varies across families. While §8 attempts to assess task comprehension (Figures 3, 6, 7), the confounds are not fully controlled.
- Why it matters: Some of the larger discrepancy medians for AR could be due to prompt sensitivity or quantization artifacts rather than fundamental inconsistency. At least one run with non-quantized models or per-family ablations could help.

5) Adjacent-token only and aggressive preprocessing may bias the test set.
- Section 6.2 removes punctuation, stop-words, and non-whole-word tokens, and restricts to adjacent tokens. This deletes many syntactic signals and changes the token distribution substantially. Dependence structures over punctuation and stop-words can affect the conditionalization and PMI-like behavior.
- Why it matters: The inconsistency pattern could shift for more general spans and natural contexts, including multi-token entities, punctuation, and function words. The synthetic template in Appendix D is also quite constrained.

6) Incomplete alignment across MLM and AR probability definitions.
- Section 2 mentions that in AR, “the probability of the token followed by EOS should match the MLM probability.” That requires same granularity, tokenizer, and a true single-token completion. In practice, AR can place significant probability on multi-token alternatives or copy behavior, while MLM predicts a softmax over a masked position. The paper partly addresses this by EOS analysis (Appendix E) but does not reconcile the remaining mismatch rigorously when computing joint spans across different vocabularies.
- Why it matters: The theoretical equality that underpins the comparison may not strictly apply between model classes, which weakens cross-class conclusions.

7) Limited ablations on prompts and decoding order definitions for AR.
- Section 6.1 says “We tested various prompts but did not notice notable differences,” yet no quantitative results or prompt variants are reported beyond pointing to Appendix B. Since the main claim includes that AR has larger inconsistency, providing a prompt-robustness ablation table would strengthen the conclusion.

8) Synthetic data design under-specified and arguably too template-like.
- Appendix D: The template “MASK1 MASK2 is a thing” filled with 2-word noun phrases from fiction is very stylized. The paper acknowledges that sentences are “not meaningful but mostly grammatical.” The claim that “the model is expected to produce consistent probabilities” in such contrived contexts is not justified, especially for AR models whose priors may penalize such frames.
- Why it matters: The strong pattern differences on synthetic data (Figure 5) might reflect domain misspecification rather than model inconsistency, and this limits how much we can generalize from synthetic to real.

9) Interpretation of Table 1 coefficients needs normalization and unit clarity.
- In Table 1, the “Size” coefficient on News is 72.2883 with an interaction near −3.0734, which is hard to interpret without standardizing predictors and clarifying the unit of variance (variance of what distribution, per-token log-d differences?). A standardization or reporting standardized betas would help.

10) Reproducibility gaps.
- Although Appendix B includes prompts, more details are needed: exact tokenizers and versions; treatment of multi-token words in AR; how probabilities were aggregated for pairwise joints in AR (teacher forcing vs. revealing gold token between steps); batch size and FP precision; entropy computation details, especially vocabulary truncation if any; random seeds; compute budget. Code is promised but not provided.

11) Claims partly conflate inconsistency with over/under-confidence without calibrating for frequency or PMI magnitude.
- Figure 4’s entropy correlations are suggestive, but there is no control for token pair frequency or PMI magnitude. Since d relates to PMI differences, stratifying by empirical co-occurrence strength or frequency bins would clarify if the entropy-order heuristic is robust across frequency regimes.

12) Minor: Figures and notation could be sharpened.
- Figure 2 y-axis “d” is in log space, but the base and unit are not restated in the caption. Figure 3 axes are “log rank” without explicit base; boxplot whisker definitions vary across figures. Equation (1) and (2) define Pi,i+1 with bold x−xi,−xi+1, but the conditioning notation could be made more explicit in text about revealing the correct token between steps for each order.

Explicit engagement with figures/tables:
- Figure 1: The schematic clarifies the two computation orders for joint probabilities in MLM, but it would help to denote explicitly that after predicting MASK1, the gold token is revealed before predicting MASK2, and vice versa. As drawn, this matches the verbal description and supports the setup.
- Figure 2a,b: The boxplots are central evidence. For example, on News (Figure 2b), LLaMA-2 70B shows a negative-shifted median with relatively tight IQR compared to MLMs, which substantiates the claim that AR models have more systematic offsets. Conversely, RoBERTa-large shows a median near zero but high variance. These visual patterns support the main inconsistency claims, though they inherit the tokenization comparability caveat above.
- Figure 3: The Rank 1 and Rank 2 distributions show LLaMA-2-Chat with much worse rank distributions, which the text attributes to poor task comprehension. The figure supports this qualitative point.
- Figure 4: The violin plots make clear the sign flip between two-mask vs one-mask entropy correlations with d, and that MLMs (green) show stronger absolute correlations. This figure is the main support for the entropy-order heuristic; however, reporting correlation magnitudes and CIs per model would strengthen it.
- Table 1: Shows significant size effect and decent R^2. As noted, per-model sample differences and possible heteroskedasticity limit how definitive these inferences are.
- Table 2: Fine-grained model-type regression only finds a significant size effect for Flan-T5, likely due to larger within-family sample size; this aligns with the authors’ own caution about small-N.

## Potentially Missing Related Work
1) Baldelli et al., “Probabilistic Calibration Is a Trainable Capability in Language Models,” 2026 — Demonstrates targeted fine-tuning can improve LM probability calibration. Directly relevant to Section 10; discuss as potential remedies to reduce span-inconsistency and cite near §3 (Calibration) and §9–§10; consider as a follow-up experiment or discussion point.
2) Band et al., “Linguistic Calibration of Language Models,” 2024 — Aligns verbalized confidence with correctness in long-form generations. While your work focuses on internal probabilities, this connects externalized confidence to internal scores; add to §3 and discuss in §10 as complementary.
3) Tao et al., “Revisiting Uncertainty Estimation and Calibration of Large Language Models,” 2025 — Large-scale study comparing uncertainty estimation methods. Add to §3 and relate to Figure 4’s entropy correlations; could inform which entropy/probability summaries to trust.
4) Tao et al., “Can Large Language Models Express Uncertainty Like Human?” 2025 — Bridges internal uncertainty and linguistic hedging. Add to §3 and §10 to connect your entropy-guided decoding recommendation to linguistic uncertainty expression.
5) Wagner et al., “Express Your Doubts — Probabilistic World Modeling Should not be Based on Token logprobs,” 2025 — Theoretical critique of token logprobs as world-event probabilities. Discuss in §3 and §10 to contextualize your negative results and motivate alternative probabilistic targets.
6) Qiao et al., “Lowest Span Confidence: A Zero-Shot Metric for Efficient and Black-Box Hallucination Detection in LLMs,” 2026 — Uses span-level confidence for hallucination detection. Add to §1 and §3, and compare in §9 as an application where your span-consistency diagnostics and entropy heuristics could plug in.
7) Narasinh et al., “Stability Evaluation of Confidence Features Across Model and Data Variants in Large Language Models,” 2026 — Studies stability of token-probability and entropy features. Add to §3 and §9 to frame your entropy-order heuristic with known stability considerations.
8) Yeh et al., “Retrieval-Augmented Linguistic Calibration,” 2026 — Post-hoc pipeline that calibrates linguistic confidence using uncertainty signals. Add to §3 and §10; your span-inconsistency signals could be upstream features for such post-hoc calibration.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Provide a shared, controlled evaluation subset across all models:
  - Construct a byte-level or character-level alignment to define the same two-token spans across tokenizers, or evaluate on a curated set where spans are single tokens in every tokenizer. Alternatively, compute both at the byte level to eliminate tokenizer confounds. Report Figure 2 style plots on this common subset.
- Report effect sizes and confidence intervals:
  - Alongside Wilcoxon p-values, report median d, median |d|, and 95% CIs per model, and the fraction of pairs with |d| exceeding practical thresholds (e.g., 0.5, 1.0 nats). This addresses practical significance.
- Strengthen regression analyses:
  - Use standardized predictors and robust standard errors; check residuals and heteroskedasticity; complement with within-family nonparametric trend tests on a common subset to avoid sample-selection confounds. Clarify units by standardizing variances or reporting log-variance.
- Control confounds in AR experiments:
  - Include at least one non-quantized AR run to check sensitivity to 4-bit quantization; add a prompt-robustness table with quantitative differences; detail the exact procedure for joint probabilities in AR (teacher-forcing, revealing gold between steps, EOS handling).
- Broaden span settings:
  - Add experiments with non-adjacent tokens and 3-token spans to demonstrate that the observed inconsistency pattern is not an artifact of adjacency-only design. Consider including punctuation/function-word pairs to test generality.
- Stratify entropy–order correlations:
  - Condition correlations on frequency or empirical PMI bins to show robustness across easy vs rare pairs; include correlation magnitudes with CIs in Figure 4.
- Release artifacts:
  - Publish code, News URLs, and per-model sample indices; provide a script to reproduce the controlled common-subset evaluation suggested above.

Minor comments and typos:
- §6.1: “We note that a natural option to test decoding order is to use T5’s special tokens… Reversing the order lowered the likelihood for all word pairs” — quantify this; otherwise it reads anecdotal.
- §7.1: Figures 2 caption labels are swapped in text ordering (“on both Wikitext (2b) and News (2a)”) vs the figure labels (2a Wikitext, 2b News). Please ensure consistency.
- Table 1: Clarify whether “Size” is in billions and whether the response is raw variance of d. Consider standardized betas.
- Figures 3–4: State log base for rank plots; add y-axis unit “nats” if log base e is used for d.
- Notation, Equations (1)–(2): Make explicit that the gold token is revealed between steps for each order and that conditioning contexts differ slightly in the two orders, which is the crux.

Criteria for score change:
- If a controlled common-subset analysis across tokenizers is added and confirms the main conclusions, and effect sizes with CIs demonstrate practical impact, I would raise Soundness and Overall scores by 0.5.
- If non-quantized AR results and prompt-robustness ablations show the AR inconsistency is robust to these confounds, I would further increase the Overall score by another 0.5.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
4 Strong: This study provides sufficient support for all of its claims. Some extra experiments could be nice, but not essential. The main conclusions are supported by multiple figures and tests, but cross-model comparability and AR confounds should be tightened.

## Excitement
3.5 Between interesting and exciting. The framing is timely and the entropy-ordering heuristic is practically useful, though the paper is primarily diagnostic rather than offering fixes.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The contribution is a clear, well-argued analysis framework with actionable findings. The main limitations are cross-tokenizer comparability and AR confounds; these are addressable and do not nullify the central empirical takeaways.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges adjacency-only spans, small sample sizes for regression, and qualitative cross-type comparisons. I recommend adding:
- Discussion of tokenization bias and its implications for fairness across languages with different segmentation properties, since tokenizer choices could differentially affect “consistency” conclusions for morphologically rich languages.
- Clarify dual-use: exposing inconsistency patterns could be used to game likelihood-based detectors or calibration pipelines; propose disclosure that emphasizes safe diagnostic use.
- Note that News scraping should respect robots.txt and site licenses; providing only URLs and access dates is good, but also consider whether any paywalled content was included.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Prompts are given, datasets are standard or clearly described, and the methodology is simple. Releasing code and the exact sample indices would likely move this to 5.

## Datasets
2 Documentary: The News set is described and will not be redistributed; Wikitext-2 is public. If URLs and access dates are released, this remains documentary.

## Software
3 Potentially useful: If the authors release scripts for computing span discrepancies, entropy stats, and plots, this will be useful as a diagnostic tool.