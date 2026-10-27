# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper examines whether large language models modulate determinism appropriately across question types, which the authors term “question awareness.” The central diagnostic is the steepness of the next-token distribution, quantified by average kurtosis across generated tokens. Empirically, the paper measures kurtosis on open-ended vs non-open-ended questions (TruthfulQA, GSM8K, RefGPT-Fact; plus three open-ended categories curated from ShareGPT) for LLaMA 2 and Falcon models. Observing mismatches (e.g., factual QA not being treated more deterministically), the authors propose Question Awareness Temperature Sampling (QuATS): a small “DetBlock” head predicts a determinacy score from question representations, which is mapped to a target kurtosis interval; during decoding, QuATS adaptively adjusts temperature per step to steer the running average kurtosis toward this target. Experiments report that QuATS increases kurtosis separation between open vs non-open-ended questions and improves benchmark scores (Table 1), while outperforming fixed-temperature decoding baselines (Figure 3).

## Summary Of Strengths
- Framing: The paper offers a simple, concrete operationalization of “question awareness” via token distribution steepness, and links it to hallucination risk on factual tasks. This framing is accessible and actionable.
- Practical method: QuATS is lightweight at inference time and compatible with common decoding strategies. It treats temperature as a controllable knob guided by a learned determinacy signal and on-the-fly feedback from current distributions.
- Clear, inspectable pipeline: The paper provides step-by-step algorithmic detail, including Equations (5)–(10) and Algorithm 1 for per-step temperature updates.
- Cross-model applicability: Results cover both LLaMA 2 and Falcon, and both small and large variants. Table 1 shows consistent gains, especially for smaller models and factual tasks.
- Figure- and table-grounded narrative:
  - Figure 2 clearly visualizes that, at T=1, kurtoses for RefGPT-Fact are not markedly higher than open-ended categories, supporting the core diagnosis.
  - Figure 3 shows that non-open-ended tasks (e.g., GSM8K) benefit from lower temperatures, while open-ended tasks benefit from higher temperatures, directly motivating adaptivity; QuATS consistently beats the dashed “baseline” reference.
  - Figure 5 demonstrates that with QuATS, the separation in average kurtosis between non-open-ended and open-ended tasks increases, aligning with the method’s goal.
  - Table 1 reports broad metric improvements with QuATS across datasets and model sizes, with especially notable accuracy gains on TruthfulQA and RefGPT-Fact for both LLaMA 2 and Falcon.

## Summary Of Weaknesses
1) Validity of kurtosis as the determinism proxy
- The choice of kurtosis over more standard measures such as entropy, top-1 probability, margin (p1−p2), Gini, or logit variance is not justified. Equation (2) normalizes by κ_one-hot to account for vocabulary size, but the statistical behavior of this “excess kurtosis” on a simplex-constrained discrete distribution is not analyzed. Without comparison to simpler, widely used alternatives, it is hard to assess whether kurtosis is the right signal. This matters because the core claims and QuATS training targets depend on kurtosis.
- Actionable: add ablations replacing kurtosis with entropy, top-1 probability, and margin; report correlations among these metrics and downstream performance changes.

2) Evaluation construct and ground truth for “question awareness”
- The paper assumes that non-open-ended tasks warrant high determinism and open-ended tasks low determinism, but does not validate this with human judgments on per-question determinacy beyond the small training set for DetBlock. Figure 2 shows cases where the separation is small, but there is no measurement of whether low separation is truly “lack of awareness” rather than inherent ambiguity in the tasks.
- Actionable: include human-rated determinacy on a held-out subset of the evaluation set (not just the 3.5k training items), and correlate it with measured kurtosis and with QuATS’s chosen temperatures.

3) DetBlock supervision is subjective and underspecified
- Section A states 3.5k questions labeled by two annotators with scores rescaled to (0,1). Missing details: inter-annotator agreement (Cohen’s κ or Krippendorff’s α), label distribution, examples per category, and how disagreements were resolved. The criteria in Table 2 are reasonable but broad; without agreement stats and distributional details, the reliability of the supervision is unclear.
- Actionable: report agreement metrics, distribution of labels, and several borderline examples to illustrate consistency.

4) Potential confounds in open-ended evaluation
- Open-ended metrics are judged by GPT-4-turbo (Section 4.1), which is known to be sensitive to output style and verbosity. No sensitivity analysis or judge-variance control is presented, and significance testing is absent. In Figure 3, some QuATS gains are small; it is unclear if they are statistically meaningful.
- Actionable: report bootstrap confidence intervals for Table 1 and Figure 3, and run at least two judge configurations (e.g., different prompts or sampling seeds) to test robustness.

5) Incomplete baselines and related work on adaptive temperature/calibration
- The paper positions QuATS mainly against fixed-temperature sampling and post-processing (top-k, top-p, typical, entmax), but omits directly comparable adaptive-temperature schemes and calibration heads. Relevant prior work includes adaptive temperature for code generation and calibration-oriented temperature scaling modules.
- Actionable: compare to an adaptive-temperature baseline that predicts temperature from question embeddings (without the kurtosis feedback loop), and discuss/benchmark against adaptive temperature or calibration heads (see “Potentially Missing Related Work”).

6) Algorithmic clarity and potential instability
- Equation (9) scales the temperature update by t, which can induce aggressive changes later in decoding. Although Equation (10) clamps T, there is no analysis or empirical sweep over η, T_min, T_max, or λ. Algorithm 1 also computes one distribution at T_{t−1} to estimate κ_t, then re-computes at T_t to sample, effectively doubling softmax operations per step, but runtime overhead is not reported.
- Actionable: provide sensitivity plots for η, λ, T_min, T_max and report per-token latency overhead; consider a one-pass estimator or show that added overhead is negligible.

7) Ambiguities/typos in the target-kurtosis interval
- On Page 6, Equation (6) is presented with upper and lower definitions, followed by a duplicate line “K_lower = K_avg − λ·K_std,” which looks like a typesetting error. It raises confusion about the intended interval definition and the role of λ.
- Actionable: fix Equation (6) and add a short derivation or intuition for the interval construction and its empirical range.

8) Hallucination claims not directly measured
- The paper claims QuATS alleviates hallucinations because non-open-ended tasks improve. However, TruthfulQA accuracy is not a calibrated hallucination rate, and RefGPT-Fact’s “factuality” is not analyzed in terms of citation support or answer verifiability. The link between higher kurtosis and fewer hallucinations remains correlational.
- Actionable: add a factuality/hallucination evaluation with automatic (e.g., FactScore, SelfCheckGPT) or human verification on a factual subset, and analyze whether QuATS actually reduces unsupported claims.

9) Scope limitations and generality
- QuATS requires access to logits and per-token softmax, making it inapplicable to many closed APIs. The paper notes this but does not discuss alternatives (e.g., learning a proxy from output text only). Also, the approach is evaluated only in English, raising questions about cross-lingual robustness where determinacy and tokenization differ.
- Actionable: discuss deployability in API settings and the potential of an output-only proxy; add at least a small-scale multilingual check or explicitly bound the claims to English.

10) Reproducibility gaps
- Missing critical details: sizes and composition of the evaluation subsets from ShareGPT for Creation/Discussion/Suggestion; prompts used for LLM-as-judge; hyperparameters for η, λ, T_min, T_max; whether nucleus/top-k was combined with QuATS; decoding length limits; random seeds; significance testing. Without code or config dumps, it will be hard to reproduce Figure 3 and Table 1 precisely.
- Actionable: provide a full experimental appendix or artifact, including scripts and prompts.

Figure-/Table-specific comments
- Figure 2: Supports the paper’s central claim by showing RefGPT-Fact has kurtosis close to open-ended categories for several models, suggesting insufficient determinism on factual QA. However, the absolute scale is compressed (near 0.9+), which could mask practically significant differences; a delta plot would help.
- Figure 3: Critical to the argument that temperature matters differently by task. GSM8K accuracy peaks at low T (~0.5), while Creation peaks near T>1, justifying QuATS. Please add error bars or confidence bands and clearly mark the QuATS point relative to each curve to quantify the margin.
- Figure 4: The DetBlock diagram clarifies that the head is built by copying the last decoder layer, but the cost implications are not discussed. Clarify whether DetBlock shares weights or is separate during inference.
- Figure 5: Shows improved separation in average kurtosis between categories under QuATS. It would be helpful to add a numeric delta per category and test whether the separation correlates with performance gains in Table 1.
- Table 1: Shows consistent gains with QuATS across most settings. However, some changes are small (e.g., LLaMA 2 70B GSM8K 62.7 → 61.5 is a drop), and significance is not reported. Please add per-task sample counts and CIs. Also state whether “Acc” is exact-match or normalized variants.

## Potentially Missing Related Work
1) Zhu et al., “Hot or Cold? Adaptive Temperature Sampling for Code Generation with Large Language Models,” 2023 — Proposes adaptive temperature (AdapT) based on token difficulty. It is directly relevant to QuATS’s adaptive temperature idea, though in a different domain. Should be discussed in Related Work and, if feasible, adapted as a baseline in Section 4 (compare in Figure 3/Table 1).
2) Xie et al., “Calibrating Language Models with Adaptive Temperature Scaling,” 2024 — Introduces calibration heads that predict token-wise temperatures to align model confidence and correctness. Conceptually similar to DetBlock. Should be cited in Section 3 and compared methodologically; consider a calibration-head baseline without kurtosis feedback.
3) Yin et al., “Uncertainty-Aware Semantic Decoding for LLM-Based Sequential Recommendation,” 2025 — Uses uncertainty and adaptive temperature tied to semantic structure. While in recommender systems, the decoding principle is relevant; discuss in Section 5 and contrast the uncertainty signal (entropy/semantic grouping) vs kurtosis.
4) Ji et al., “Towards Mitigating Hallucination in Large Language Models via Self-Reflection,” 2023 — Addresses hallucination reduction through self-reflection loops. Given the paper’s motivation around hallucinations, it should be related in Section 5 and possibly used as a complementary baseline on factual tasks.

## Comments Suggestions And Typos
Actionable suggestions most likely to change my assessment:
- Validate the metric: add ablations replacing kurtosis with entropy, top-1 probability, and margin; report correlations and redo key plots (Figure 2, Figure 5) and results (Table 1) under those alternatives.
- Strengthen evaluation: report CIs, significance tests, and judge robustness for all open-ended scores; include a direct hallucination metric on factual QA to substantiate the claim that QuATS reduces hallucinations.
- Baseline completeness: implement a question-embedding→temperature regressor baseline without per-step kurtosis feedback, and, if possible, an adaptive-temperature method from prior work (e.g., adaptive scaling/calibration heads).
- Sensitivity and overhead: provide sensitivity analyses for η, λ, T_min, T_max in Eq. (9–10), and report the runtime overhead of Algorithm 1 compared to fixed-temperature decoding on representative hardware.
- Clarify data and labels: provide inter-annotator agreement for the determinacy labels, label distribution, representative examples, and release the 3.5k labeled questions if possible.
- Fix and clarify notation:
  - Page 6, Equation (6): duplicate/typo for K_lower definition; please correct.
  - Algorithm 1: explain the rationale for multiplying the update by t in Eq. (9) and justify stability; consider alternative schedules.
  - Section 2.2: explicitly justify normalization by κ_one-hot and discuss its dependence on vocabulary size and distribution shape.

Other typos/edits:
- Page 2–3: “kurtosises” → “kurtoses” throughout.
- Figure 3 captions: consider adding the exact QuATS operating point markers; currently the dashed “Baseline” line may be misread as a fixed temperature reference rather than T=1.
- Section 3.1 “DetBlock Structure”: specify dimensionality and whether the “copied last decoder layer” shares or duplicates parameters.
- Section 4.1: specify the exact number of instances per subset for Creation/Discussion/Suggestion and any prompt templates used for GPT-4-judge.

Criteria for score increase in rebuttal:
- Provide ablations with alternative determinism metrics and robust statistical reporting; add at least one adaptive-temperature baseline from prior work; and supply agreement stats plus partial artifact release. If these are addressed convincingly, I could raise to 3.5 (Borderline Conference) or 4.0 (Conference), depending on the strength of added evidence.

## Confidence
4: Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3: Acceptable — The study provides sufficient support for its main claims, but the determinism metric and evaluation design need stronger justification and additional baselines.

## Excitement
2.5: Between potentially interesting and interesting — Practical idea with clear value, but the current empirical and methodological framing limits impact.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the framing and method are practical and the results promising, key methodological choices (kurtosis as determinism proxy), missing adaptive baselines, limited statistical analysis, and incomplete reproducibility details prevent a stronger recommendation.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges that QuATS depends on access to logits and externally adjusts behavior rather than improving intrinsic understanding. Additional considerations to discuss:
- Judge bias and style sensitivity when using LLM-as-a-judge for open-ended evaluation.
- Potential over-regularization toward “safe” determinism, which may suppress valid diversity, especially for underrepresented language varieties or creative tasks.
- English-centric experiments; determinacy behaviors can be language- and tokenization-dependent.
- Dual use: making models more “confident” on factual queries without evidence grounding may inadvertently increase user overtrust; tie QuATS with retrieval or verification for high-stakes domains.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many implementation details are missing, including hyperparameters for Eq. (9–10), evaluation subset composition, prompts, and statistical reporting. Code/data availability is not stated.

## Datasets
1: No usable datasets submitted. A 3.5k determinacy-labeled set is described but appears not to be released; details are insufficient.

## Software
1: No usable software released. The paper does not state code availability.