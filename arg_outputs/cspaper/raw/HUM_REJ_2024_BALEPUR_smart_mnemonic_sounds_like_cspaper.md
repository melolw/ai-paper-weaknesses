# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper presents SMART, an LLM-based system for generating keyword mnemonics for GRE vocabulary. The pipeline: (1) fine-tunes LLaMA-2-70B on a curated subset of user-written mnemonics (selected via a Bayesian quality estimator using crowd up/downvotes; Equations 1–2); (2) deploys the model in a flashcard app to collect three types of preferences for pairs of generated mnemonics: pairwise choices, Likert ratings, and an observed signal based on the number of turns needed for a learner to recall a term when studying with a mnemonic; (3) fits a hierarchical Bayesian model (Equations 4–15) to synthesize a latent “mnemonic effectiveness” score from all three signals; and (4) aligns the generator with DPO (Equation 16) using the Bayesian winner. The paper reports preference disagreement between expressed and observed signals (Table 1; Figure 5), ablations showing fine-tuning and DPO improvements (Table 2), data-augmentation benefits from multi-preference labels (Table 3), and a qualitative expert evaluation indicating SMART’s outputs are competitive with GPT-4 on explanations and slightly better keyword simplicity than Transphoner (Figure 6; Tables 9–10).

## Summary Of Strengths
- Original framing and dataset: The paper targets keyword mnemonic generation, a niche yet meaningful NLP-for-education problem. It contributes both a cleaned fine-tuning set (Section 2.1–2.3; Table 4) and a multi-signal preference dataset collected in-situ from 45 learners over 2684 judgments (Section 3.3; Table 5). The app instrumentation cleverly captures expressed and observed preferences with minimal extra burden (Figures 2–4).
- Empirical insight about preferences: Clear evidence that expressed preferences (pairwise vs ratings) only moderately agree, and both diverge more strongly from the observed learning proxy (Table 1; Figure 5). This is a substantive and relevant finding for alignment in educational NLP.
- Bayesian integration of heterogeneous signals: The hierarchical model connecting latent effectiveness to pairwise choices (Bradley–Terry with ties; Equations 5–9), Likert counts (Equations 10–12), and geometric time-to-recall (Equations 13–15) is a thoughtful design. The paper provides convergence diagnostics and train/val likelihoods (Appendix B.4; Figures 9–10).
- Alignment improvements and data augmentation: DPO trained on the Bayesian-integrated labels does not hurt pairwise judged quality relative to training only on pairwise labels, and can improve it by resolving pairwise ties and leveraging examples without pairwise labels (Table 3). This is a practical recipe for better data efficiency when collecting costly human preferences.
- Expert qualitative analysis: The split evaluation on keyword vs explanation quality is well-designed. Figure 6 and Tables 9–10 give a nuanced picture: SMART trades a small drop in phonetic similarity for higher simplicity relative to GPT-4, and its explanations match GPT-4 in aggregate while a human expert still leads, which is an honest and useful benchmark.
- Figures that aid understanding: Figure 1 is an effective end-to-end schematic of the pipeline and the data flow from collection to Bayesian modeling to DPO; it directly supports the methodological narrative in Sections 2–5.

## Summary Of Weaknesses
1) Evaluation relies heavily on GPT-4-as-judge for pairwise quality
- Main quantitative results in Sections 6.1–6.2 (Tables 2–3) are adjudicated by a GPT-4 classifier (Appendix B.3). While the authors report 80% agreement with held-out human pairwise labels and attempt to mitigate bias (bidirectional comparison, DSPy prompt optimization), the core takeaways about DPO and multi-preference augmentation hinge on an automatic judge. This is particularly sensitive here because SMART explicitly optimizes for a blended objective, not just “pairwise quality,” and the link between the GPT-4 judgments and short-term recall isn’t validated.
- Why it matters: The claim that MPLs “do not harm and can improve pairwise quality” (Table 3) would be stronger with a modest-scale human study on the same test set, or at least a correlation analysis between GPT-4 judgments and observed learning outcomes.

2) Observed learning proxy is under-specified and potentially confounded
- The observed signal is average turns to first correct recall with KARL scheduling (Section 3.2.2, Figure 2). However, details that affect validity are missing: randomization of which mnemonic (A/B) a learner gets upon error; control for learner-level ability and prior exposure; handling of repeated exposures and cross-item interference; distributional skew of turns (Appendix suggests geometric likelihood, but raw counts per pair often look small).
- Why it matters: Without tighter experimental control, the time-to-recall proxy can be confounded by user heterogeneity and app dynamics, which weakens both the Section 4 conclusions (preference disagreement) and the trustworthiness of the Bayesian integration (Section 5.1).

3) Bayesian model design choices need clearer justification, especially for ratings
- The Likert observation model defines R_A,i as cumulative counts “less than or equal to rating j” (Page 6), yet Equations 10–12 then use a Multinomial over a 5-length probability vector. Cumulative counts should not be modeled with a standard Multinomial without a transformation or a cumulative-link (ordinal) model; otherwise the likelihood is mismatched. The paper should clarify if R represents simple category counts or truly cumulative ones. If cumulative, a cumulative logit/probit ordinal model would be more appropriate.
- The priors (e.g., Beta(1,1) for θ; Normal(0,1) scalars; a single τ for all pairs) are reasonable defaults but their sensitivity is not explored. There is also no annotator-level structure, though annotator noise/heterogeneity is a primary motivation for Bayesian aggregation.
- Why it matters: A mismatch between data definitions and likelihood harms interpretability and potentially the correctness of y_bayes used for DPO.

4) Limited participant pool and per-item coverage
- Only 45 students provided 2684 preferences over 472 pairs, with average 3.57 labels per pair (Table 5). For observed learning, the per-mnemonic turn counts can be very small (Table 6 shows categories but not item-wise counts after filtering). Without participant/item-level random effects, pooling such small signals risks overfitting idiosyncrasies.
- Why it matters: Generalization of the “observed vs expressed” divergence (Table 1, Figure 5) and the stability of the Bayesian labels are limited by sample size and design.

5) Heavy backbone and practicality claims
- The system fine-tunes LLaMA-2-70B and uses it for DPO (Sections 2.3, 5.2), which is computationally and operationally expensive for education settings. Claims of “much lower deployment costs” than GPT-4 (Abstract) are not substantiated with real latency/cost measurements, model quantization choices at inference, or user-scale throughput analysis.
- Why it matters: A strong value proposition in education is cost-effectiveness. Provide concrete numbers.

6) Incomplete evaluation across objectives
- The paper acknowledges focusing on pairwise metrics due to cost (Section 6). However, since the key conceptual contribution is integrating expressed and observed signals, an evaluation that probes trade-offs on all three objectives, even for a smaller subset of items with humans, would better support the central thesis.
- Why it matters: Without validating gains on the observed learning metric itself post-DPO, it’s unclear whether the alignment helped the target educational outcome or just the proxy judged by GPT-4.

7) Best-of-n pair selection may bias preference distributions
- Pair construction (Section 3.1) uses best-of-5 with a reward that favors high model likelihood and low ROUGE-1 overlap. This may reduce diversity and inflate the apparent benefits of subsequent preference learning, since the pairs already contain relatively “good and distinct” candidates, potentially limiting the headroom or altering the label distribution.
- Why it matters: Report additional analyses on how this selection affects the difficulty of the pairwise task and label balance.

8) Decoding and prompting constraints are brittle
- Generation uses a fixed pattern “Term: v … v sounds like …” (Appendix B.2). This likely improves adherence to the two-step mnemonic format, but may constrain creativity or better forms students might prefer. An ablation on decoding temperature and prompt framing, including imageability-focused instructions, would be informative, particularly given expert feedback that imageability lags.
- Why it matters: The qualitative results (Figure 6) suggest clarity/strength are competitive but imageability is weaker; a prompt or training adjustment may address this.

9) Limited analysis of harmful or culturally specific mnemonics during training and DPO
- While filtering was applied pre-finetuning (Appendix A.1) and one problematic example is discussed (Appendix D.1), there is no systematic measurement of harmful content rates across models or after DPO. “Expressed preferences will filter it out” is not sufficient, especially if observed signals inadvertently reward shocking content (as the authors note).
- Why it matters: For educational deployment, safety metrics should be reported and integrated into the Bayesian model or DPO sampling policy.

10) Statistical reporting and uncertainty
- Many tables (e.g., Table 3, top) lack confidence intervals; only some comparisons include p-values. Given modest sample sizes and GPT-4 judging, effect sizes and CIs would help assess robustness.

Figure- and table-specific comments:
- Figure 1 is strong: it clarifies how the three feedback channels feed into a single effectiveness signal and then into DPO. It supports the claim that MPLs can be combined to guide alignment.
- Figure 5 is central evidence for the “expressed vs observed” divergence; however, the cloud is dominated by low-iteration outcomes (1–2 turns). Reporting per-user partial correlations controlling for ability and item difficulty would strengthen the inference.
- Figure 6 shows that SMART’s explanation quality matches GPT-4 on clarity/strength but lags in imageability; this directly grounds the discussion in Section 6.3 and motivates targeted feedback features in future iterations.
- Table 1 quantifies disagreement across preference pairs; useful, but confidence intervals should be added.
- Table 2 ablations show that both fine-tuning and DPO help. It would be valuable to show absolute win rates with CIs and the number of non-tie cases to interpret effect sizes.
- Table 3 is important: it supports the data-augmentation angle for MPLs. Again, include CIs and a human-judged subset if possible.

## Potentially Missing Related Work
1) Lee et al., “Exploring Automated Keyword Mnemonics Generation with Large Language Models via Overgenerate-and-Rank,” 2024 — directly addresses LLM-based keyword mnemonic generation with an overgenerate-and-rank pipeline. It is methodologically comparable to Section 3.1’s best-of-n pairing and to prompt-only baselines. Should be discussed in Related Work (Section 7) and considered as a prompting-based baseline in Section 6.1.
2) Lee et al., “Personalizing Kanji Memorization: Designing Adaptive Mnemonics Based on Learner Preferences Using Large Language Models,” 2026 — studies preference-aware mnemonic generation in a different language/script. Useful to contextualize SMART’s preference modeling and to discuss personalization avenues in Section 6.3 and Limitations (Section 9).
3) Woodrow et al., “Improving Generative AI Student Feedback: Direct Preference Optimization with Teachers in the Loop,” 2025 — applies DPO to align educational feedback with instructor preferences in real courses. Relevant to Section 5.2; compare alignment data collection protocols and report differences in outcome metrics.
4) Elabd et al., “Designing Personalized Multimodal Mnemonics With AI: A Medical Student’s Implementation Tutorial,” 2025 — though tutorial-style, provides practical prompting and quality-control for textual+visual mnemonics. Useful for discussing multimodal extensions and safety controls in Section 10.
5) Zhang et al., “Students’ Perceptions and Preferences of Generative Artificial Intelligence Feedback for Programming,” 2024 — analyzes student perceptions vs effectiveness of LLM feedback. Supports the paper’s thesis about expressed vs observed divergence; cite in Sections 4 and 7 to broaden the educational HCI context.
6) Worden et al., “FoundationalASSIST: An Educational Dataset for Foundational Knowledge Tracing and Pedagogical Grounding of LLMs,” 2026 — not mnemonic-specific but relevant for modeling student learning trajectories. Cite in Section 9 as a path to extend observed signals beyond short-term recall to richer educational outcomes.

## Comments Suggestions And Typos
Actionable suggestions:
- Validate the observed learning signal more rigorously.
  - Randomize A/B mnemonic assignment upon an error, and log user-level covariates to fit mixed-effects models or include annotator/learner random effects in the Bayesian model. Report partial correlations controlling for user ability and item difficulty. If feasible, run a small preregistered human study comparing mnemonics selected by y_pair vs y_bayes on actual time-to-recall.
- Fix the Likert modeling mismatch.
  - Clarify whether R_A,i are category counts or cumulative counts. If cumulative, adopt an ordinal cumulative-link (e.g., cumulative logit) instead of a simple Multinomial. Report sensitivity analyses to prior choices and alternative likelihoods (e.g., negative binomial for overdispersed turns).
- Add a safety component to the model or training.
  - Incorporate a basic toxicity/offensiveness detector or a human-in-the-loop veto into the Bayesian effectiveness (e.g., constrain or downweight items flagged as harmful). Report safety metrics pre/post-DPO.
- Broaden evaluation beyond GPT-4-as-judge.
  - For a subset of V_test, collect human pairwise judgments and a small-scale learning study to triangulate the effect of MPL-DPO on the observed metric itself. Include CIs and effect sizes in Tables 2–3 and, where possible, per-item calibration curves linking GPT-4 judgments to human outcomes.
- Cost/latency reporting.
  - Substantiate “lower cost than GPT-4” with inference throughput, latency, and $/1k mnemonics for SMART vs GPT-4 (quantization, batch size, GPU type). If applicable, consider lighter backbones (e.g., 13B) and show the trade-off.

Typos and minor clarity issues:
- Section 2.3: “\(D_{train}\)” appears but dataset is earlier denoted \(D_{ft}\); ensure consistent notation.
- Section 3.3: “All users, including the two users that failed the quality checks, are given 50.” The compensation unit is unclear ($, minutes?).
- Section 5.1: Please disambiguate “cumulative counts less than or equal to rating j” vs categorical counts for R_A,i.
- Appendix B.1: “use the accuracy of the reward model as the metric for the best model” — there is no explicit reward model in DPO; clarify selection criterion.
- Tables: add confidence intervals for win/tie/loss rates.

What could change my score:
- Evidence that MPL-aligned SMART improves the observed learning outcome (turns-to-recall) in a controlled A/B over a decent subset, and a corrected Likert likelihood model with sensitivity checks, would substantially strengthen soundness.
- A small-scale human replication of Table 3 outcomes and concrete cost/latency comparisons versus GPT-4 would also help.

## Confidence
4: Quite sure after careful checking — I verified equations, tables, and key figures, but some experimental and modeling details (especially observed-signal validity) are hard to fully confirm without additional data.

## Soundness
3.5: Between Acceptable and Strong — The pipeline is coherent and implemented, but evaluation leans on GPT-4 judgments and the Bayesian Likert modeling likely needs correction; observed learning proxy could be better controlled.

## Excitement
3.5: Between interesting and exciting — The expressed vs observed preference analysis and the Bayesian+DPO integration for educational alignment are timely and useful.

## Overall Assessment
4: Conference — accept to ACL main conference. The paper offers a well-argued, data-backed exploration of aligning mnemonic generation with diverse student feedback, a practical Bayesian synthesis of heterogeneous signals, and clear evidence that multi-preference labels can augment DPO training without harming pairwise quality. Weaknesses around the observed-signal validity, Likert modeling, and GPT-4-heavy evaluation should be addressed, but they are not fatal and can be reasonably improved for camera-ready.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper discusses risks of optimizing purely on observed signals that might reward bizarre or offensive mnemonics (Appendix D.1; Section 10). More systematic safety assessment would be beneficial: quantify harmful content rates pre/post-DPO; consider fairness across cultural backgrounds given Appendix A.1’s examples; and discuss potential biases introduced by GRE-centric English datasets. There is also a risk of overfitting to short-term recall at the expense of durable learning; acknowledging the need for delayed post-tests would be appropriate.

## Ethical concerns
None beyond those already acknowledged. The user study has IRB approval, participants were compensated, and PII is not collected; app screenshots (Figures 2–4) align with the described protocols. The paper is transparent about content filtering and ethical trade-offs.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Datasets and code are promised; training details and prompts are described, including DPO hyperparameters (Appendix B.1–B.3). Some ambiguity remains in the Bayesian observation model and the app randomization, which should be clarified.

## Datasets
4: Useful — A curated fine-tuning set and a multi-preference educational dataset are valuable, and their planned releases will likely support follow-on work.

## Software
3: Potentially useful — The pipeline uses standard tooling (TRL/QLoRA/DSPy) and a Bayesian model; releasing scripts and the GPT-4 judge prompt would make it more useful.