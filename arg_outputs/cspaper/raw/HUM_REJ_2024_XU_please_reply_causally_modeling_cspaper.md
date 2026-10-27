# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies email reply behavior on public mailing lists (GMANE). It introduces SIZZLER, a set of 1,811 expert-labeled emails with communicative intents and reply expectations. Using RoBERTa and zero-shot Llama-3, the authors predict intents/expectations for 11.03M emails from 2009 and combine these predictions with additional linguistic (e.g., politeness, formality, argumentation quality) and network features (e.g., PageRank, HITS, reciprocity). The core analysis uses propensity score matching followed by logistic regression to estimate which factors are associated with receiving a reply, separately for initial vs. response emails. The paper reports that social status and affective argumentation correlate more strongly with replies than social connection.

## Summary Of Strengths
- Ambitious, relevant problem at the intersection of discourse/pragmatics, computational social science, and email applications, clearly within ACL scope.
- New human-annotated resource (SIZZLER) focusing on intents and reply expectation in email, with a careful annotation schema and discussion of agreement; useful for downstream modeling.
- Large-scale analysis over 11M messages, with a clear split of initial vs. response emails that maps to different conversational dynamics.
- Empirical findings are interpretable and connected to prior theory on argumentation, status, and social ties.
- The figures communicate the main messages well. For example, Figure 5a–5b distill the regression coefficients after matching, visibly contrasting initial vs. response emails; the negative association of PageRank for initial emails and positive association for response emails is easy to parse from the plotted CIs.
- The benchmarking of intent/expectation classifiers is helpful. Figure 4 and Table 3 jointly show the clear advantage of the fine-tuned RoBERTa model over zero-shot Llama-3 and n-gram logistic regression, supporting the claim that context beyond n-grams is needed.
- Useful transparency about limitations and annotator disagreements.

## Summary Of Weaknesses
1) Central causal design is mis-specified (Section 4.2). The paper claims to use propensity score matching (PSM) “to estimate whether the likelihood of a response is associated with linguistic and network factors,” but the implementation appears to generate “propensity scores” by training a Random Forest to predict the outcome (whether the email received a reply) and then sampling treated and control units (replied vs. not replied) per score bin. This is not propensity score matching for a treatment; it is matching on a prognostic score for the outcome. Proper PSM requires modeling the probability of receiving the treatment given covariates, then estimating the average treatment effect on the outcome. Here, there is no single treatment variable; instead, 14 continuous factors are jointly analyzed. Matching on outcome-prediction scores can introduce severe bias and post-treatment conditioning problems. As a result, causal language throughout Section 4 is not supported.

2) Conditioning on post-treatment variables (Page 6). The set of matching covariates includes “discussion tree features,” such as number of nodes, leaves, and branches. For an initial email, these quantities are only realized after replies are made; conditioning on them can induce collider bias and wash out or create spurious associations. This is especially problematic when the outcome is reply occurrence and the covariates capture downstream thread growth.

3) Multiple simultaneous “treatments” without a coherent causal estimand. The analysis treats 14 linguistic/network features as independent causes and runs a single logistic regression after matching. Even with “double robustness,” this design does not yield identifiable causal effects for each feature. A principled causal approach would define explicit treatments (e.g., high vs. low PageRank, or an incremental change in PageRank) and estimate their effects separately (e.g., with IPTW, TMLE, CEM, or causal forests), or adopt a structural model with strong, stated assumptions.

4) Lack of matching/balance diagnostics. Beyond Figure 16 (propensity score distributions), the paper does not report standard balance checks (standardized mean differences before/after matching) for the covariates. Without balance diagnostics, the success of the matching step is unverifiable. This undermines the validity of the regression stage and the conclusions in Figure 5a–5b.

5) Measurement validity and specification of linguistic features is under-documented. Table 5 cites sources, but many features are described as “judged by annotators” while later text implies automated scoring at population scale. It is unclear which off-the-shelf models were used, their calibration, domains, thresholds, or any adaptation to GMANE. For example, argumentation measures (Cogency, Effectiveness, Quality, Clarity) are imported from different datasets; construct validity and domain transfer are not validated. Figure 9–10 provide distributions, but no reliability checks or error analyses are shown.

6) Heavy reliance on noisy labels for confounding control. The matching includes predicted probabilities from RoBERTa for intents/expectations trained on small, imbalanced, and partly low-agreement labels (Table 1). Table 3 shows several categories with F1 close to zero, indicating near-random predictions for rare classes. Using such predictions as covariates in matching may not adequately control for confounding and could inject noise. A sensitivity analysis to misclassification would help.

7) Temporal leakage risks remain. Although network features use the previous month’s network to avoid contemporaneous leakage, other covariates (e.g., thread structure) are realized after the focal email. Additionally, features like out-degree might be cumulative in ways that still correlate with future replies within the same month; the temporal granularity and windowing for all covariates should be clarified.

8) Limited year coverage and generalization. The analysis is restricted to 2009 due to a volume drop (Appendix Figure 7). This choice is reasonable for stability, but nullifies multi-year robustness checks. Key findings could be contingent on that year’s network structure and community norms. A brief replication for an earlier stable year (e.g., 2008) would strengthen claims.

9) Missing or incomplete details impede reproducibility. Important implementation details are missing: exact toxicity/politeness/formality/argumentation model names, versions, and thresholds; PageRank/HITS parameters and normalization choices; the exact log-scaling used for edge weights; handling of aliasing or identity resolution across lists; whether content preprocessing filtered signatures/quotes consistently for all features. The Appendix gives some classifier hyperparameters, but not enough for end-to-end reproduction.

10) Annotator pool and potential bias. All annotators are authors from the same institution, which can bias schema design and labels. Only single annotations were used for the majority of data; while the authors justify this using “noisy labels can be helpful,” the risk to construct validity is inadequately mitigated.

11) Overinterpretation of associations as causal mechanisms. The narrative in Section 4.3 repeatedly interprets coefficients as support for hypotheses H1–H4. Given (1) the misapplied “propensity score” step, (2) post-treatment conditioning, and (3) unmeasured confounding, these should be framed as observational associations, not causal effects. Several explanations offered (e.g., moderators replying to toxicity) are plausible but remain speculative without targeted tests.

12) Figures are informative but need tighter alignment to claims. In Figure 5a–5b, the axes are standardized log-odds, but the paper does not report effect sizes on the probability scale or discuss practical significance. Confidence intervals are Bonferroni-adjusted, but the multiple-testing correction details and the number of simultaneous tests per panel are not clearly specified.

Detailed comments on figures and tables:
- Figure 3: The stratification by intent and expectation is compelling and supports the modeling decision to include expectations as confounders. However, several strata have very small n (e.g., Pleasantries, Yes), which leads to wide CIs. It would help to report exact counts in the caption and consider collapsing rare strata for stability.
- Figure 4 + Table 3: These jointly substantiate the choice of RoBERTa. Yet Table 3 shows F1=0 for Promising and Spam with RoBERTa, revealing near-complete failure on rare labels. Since these predictions are later used in matching, please justify the robustness of the causal analysis to these errors. Calibrating probabilities and aggregating extremely low-frequency classes might help.
- Figure 5a–5b: The visual separation into Connection/Status/Argumentation is effective. Still, given the methodological issues, the coefficients should be re-estimated under a correct design, and standardized differences for matched covariates should be included as a supplement to this figure. A probability-scale effect plot would improve interpretability.

## Potentially Missing Related Work
1) Wang et al., “PROMINET: Prototype-based Multi-View Network for Interpretable Email Response Prediction,” 2023 — Directly addresses interpretable reply prediction combining semantic and structural signals. Should be discussed in Section 5 (Email Response, Social Factors in Engagement) and compared as a modeling baseline for reply likelihood in Section 3 or 4.

2) Shay et al., “EnronSR: A Benchmark for Evaluating AI-Generated Email Replies,” 2024 — Relevant to reply evaluation and properties of effective replies. Discuss in Related Work (Section 5) and consider as a complementary evaluation perspective on when and how replies are appropriate.

3) He et al., “Corrective or Backfire: Characterizing and Predicting User Response to Social Correction,” 2024 — While focused on social media, it analyzes response types using textual and user-level features. Include in Section 5 to situate the paper among recent causal/predictive analyses of reply behaviors and consider adaptation of their characterization strategies.

## Comments Suggestions And Typos
Actionable suggestions:
- Redesign the causal analysis:
  - Define explicit treatments for each factor (e.g., binary high vs. low PageRank via quantile thresholding) and estimate effects separately using correct treatment propensity scores p(T=1|X), with overlap checks and standardized mean difference diagnostics before/after matching. Alternatively, use doubly robust estimators (AIPW/TMLE) or causal forests with honesty and cross-fitting.
  - Remove post-treatment covariates from matching, notably thread-level properties that are realized after the email is sent (nodes/leaves/branches). If you need to control for thread context, restrict to features determinable at send time (e.g., depth if available at send time for response emails).
  - Add sensitivity analyses: Rosenbaum bounds for unobserved confounding; robustness to alternative binning/thresholds; re-estimation without noisy intent covariates; placebo/negative control outcomes where applicable.
  - Report full balance diagnostics (means, standardized differences, variance ratios) for all covariates, not only score histograms (Figure 16). Include overlap plots per treatment.
- Strengthen measurement validity:
  - Specify exact models, datasets, and versions used to compute politeness, formality, toxicity, intimacy, and argumentation features; report domain adaptation or calibration on a GMANE subset. Provide inter-model correlations and an error analysis showing that these signals behave sensibly on emails.
  - Given Table 3’s very low F1 for rare labels, consider merging categories or using class-balanced training, focal loss, or calibrated probabilities. Report reliability of predicted probabilities (ECE/Brier) since you use them as covariates.
- Temporal design:
  - Clarify time indexing for all features and ensure they are computed strictly from information available at send time. Consider month-by-month rolling analyses or within-thread fixed-effects models to mitigate unobserved heterogeneity.
  - Replicate key findings on 2008 or early 2010 data to test stability.
- Reporting:
  - Provide probability-scale effect sizes for Figure 5 to aid interpretation. Explicitly state the number of tests per panel used for Bonferroni.
  - Include ablations demonstrating how much each cluster of features (Connection/Status/Argumentation) contributes when modeled correctly.
- Resource release:
  - Release code for feature computation, network construction, and the full pipeline. Clearly document preprocessing (e.g., signature/quote stripping, language filtering).
  
Typos/clarifications:
- Page 2, “We prepossess and analyze data…” → “We preprocess and analyze data…”
- Table 5: “Clarify” → likely “Clarity.”
- Figure captions: add sample sizes where small strata lead to wide CIs (Figure 3).
- Section 3.2: “All models outperform the random baseline, except the logistic regression F1-macro score…” Consider rephrasing for clarity and note that several per-class F1 are zero in Table 3.

What could change my evaluation:
- A corrected causal design with proper treatment definitions, removal of post-treatment confounders, thorough balance checks, and sensitivity analyses that preserve the main qualitative findings in Figure 5.
- Clearer, reproducible documentation of all linguistic feature models and validation of their construct validity on email data.
- Replication on an additional year or a robustness check across several months strengthening generalization.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable — Major issues with the causal identification strategy, post-treatment conditioning, and lack of balance diagnostics. The resource and classifier benchmarking aspects are acceptable.

## Excitement
2.5 Between potentially interesting and interesting — The question and scale are appealing, but the current methodology undercuts the strength of the conclusions.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The dataset and large-scale framing are valuable, and the descriptive analyses and classifier benchmarking are informative. However, the central causal analysis is mis-specified (matching on an outcome-prediction score, not treatment propensity), includes post-treatment covariates, and lacks balance/sensitivity diagnostics. The main claims in Section 4.3 should be reframed as associations unless the analysis is redone with a correct design.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section acknowledging language restriction, domain specificity, and labeling challenges. Ethical considerations note toxicity and anonymity. Missing are risks around deanonymization through network features, potential misuse of “status” predictions in organizational or community settings, and bias amplification from off-the-shelf toxicity/politeness models not validated on mailing lists. Discuss who benefits or is harmed by tools that encourage “affective” writing for replies, and whether this may incentivize manipulation or toxicity.

## Ethical concerns
None beyond those mentioned; however, the authors should expand on potential harms of modeling social status and persuasive tactics, and document safeguards when releasing features that could enable targeting or harassment.

## Needs Ethics Review
No

## Reproducibility
3 Reproducible with difficulty — Many implementation details are missing for the feature pipeline and network construction; code/data release would likely address this.

## Datasets
3 Potentially useful — The annotated SIZZLER set is small but focused on intents and expectations; useful if released with guidelines.

## Software
3 Potentially useful — If released, the preprocessing, feature extraction, and modeling code would be valuable; currently insufficient details are provided.