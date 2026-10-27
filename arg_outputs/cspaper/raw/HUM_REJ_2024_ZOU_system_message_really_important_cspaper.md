# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies how the system message (short, long, or none) affects jailbreak success on several LLMs (GPT‑3.5‑turbo‑0613, Llama‑2 variants, and Vicuna). Using GPTFuzzer to generate jailbreak prompts from 77 templates and 100 harmful questions, the authors build three prompt sets: PS (generated under short system message), PL (long), and PN (none). They then test cross‑transfer of these prompts across models configured with different system messages and measure Attack Success Rate (ASR) with a RoBERTa‑based classifier adopted from GPTFuzzer. They find that system messages substantially change ASR, that “long” safety‑explicit messages generally reduce ASR, and that small paraphrases of system messages can shift ASR notably. To automate search for more robust system messages, they propose SMEA, an evolutionary framework that uses LLM‑based rephrasing and “crossover” between system messages. SMEA reportedly identifies populations of more “robust” system messages with only minor length changes.

## Summary Of Strengths
- Topical and relevant problem: studying the impact of system messages on jailbreaks is squarely within dialogue systems and safety evaluation, relevant to ACL audiences focused on alignment, evaluation, and model analysis.
- Clear empirical takeaway for practitioners: Tables 1–3 show that system‑message choice can change ASR substantially. For instance, in Table 1, LLAMA2‑7b‑chat with the long system message (ML1) yields only 7.0% ASR against PN, versus 31.0% with MS1 and 100% with MN1 in some cross‑tests; at minimum, the data convey that “long, explicit” policies often help.
- Concrete attempt at defense: SMEA turns the problem into a search over system messages under black‑box constraints, which is a useful framing for practitioners who can only edit prompts, not model weights.
- Figures and qualitative illustrations help ground the claims:
  - Figure 1 contrasts a failed jailbreak with a short system message (Fig. 1a) and a successful one with the same short message (Fig. 1b), then shows failure under the long message (Fig. 1c). This vignette supports the paper’s central hypothesis that system messages matter.
  - Figure 2 provides a readable schematic of SMEA’s pipeline, clarifying the generate–evaluate–select loop given the scarce algorithmic details in text.
  - Figure 3 shows boxplots of ASR distributions for final SMEA populations across models and generation operators, visually supporting the observation that “Rephrase” is stabler but often weaker than “Crossover/Mixed.”
- Actionable observation about sensitivity: Table 3 indicates that even near‑synonymous rewrites of the system message can alter ASR noticeably for many models, which is operationally important and motivates automated search.

## Summary Of Weaknesses
1) Evaluation methodology is under‑specified and raises validity concerns.
- The paper adopts the RoBERTa‑based classifier from GPTFuzzer but does not state thresholds, calibration, or error characteristics in this setting. There is no human evaluation to sanity‑check false positives/negatives, which is risky for safety claims. Since ASR is the core metric, the absence of human corroboration undermines the trustworthiness of the reported differences.
- In Section 3.2 the paper argues LLM‑based evaluators are expensive, but provides no reliability analysis of RoBERTa on these specific prompts and models. A small human audit would greatly strengthen conclusions.

2) Ambiguity and inconsistency in the experimental design.
- The construction of PS/PL/PN and the cross‑application protocol are hard to follow. Section 3.1 says “we employ GPTFuzzer to generate 300 jailbreak prompts on [each model] under three conditions,” yet Section 4 describes applying PS/PL/PN across MS1/ML1/MN1. It is unclear if PS/PL/PN are generated once per model, pooled per condition, or generated only on a specific source model and then transferred. This matters for claims about transferability and for interpreting Tables 1–2.
- In Section 6, the algorithm uses 200 PL prompts for evaluation and 100 PL for test, motivated by the claim that robustness to PL generalizes to PS and PN. This assumption is not empirically justified beyond qualitative references to Tables 1–2 and is contradicted in places (e.g., LLAMA2‑13b‑chat with MS1 shows 97% ASR on PN in Table 1, while MN1 shows 67.7% on PN, suggesting different behaviors across prompt families).

3) Limited baseline space and lack of statistical analysis.
- The paper does not compare SMEA to straightforward alternatives like: (i) random paraphrasing without selection, (ii) greedy scoring of multiple rephrasings without EA, (iii) using different decoding parameters or safety prefixes. Without baselines, it is unclear whether EA provides unique value over simple sampling plus best-of selection.
- No confidence intervals or hypothesis tests are provided for ASR differences across conditions. Given ASR noise and the automatic evaluator, the paper should quantify uncertainty, especially in Table 3 where “small changes” are claimed to cause “significant” shifts.

4) System messages are defined narrowly and somewhat artificially.
- The “short” message is a single sentence (“You are a helpful, respectful and honest assistant.”). The “long” message hard‑codes explicit safety instructions. The “none” condition is unrealistic for most production systems. Many real deployments include medium‑length safety messages, tool instructions, and policy references. The conclusions might not generalize beyond these specific choices.
- There is no analysis of interaction with chat templates, role tokens, or punctuation/formatting, which are known to affect instruction hierarchy following.

5) Potential confounders are uncontrolled or not reported.
- Decoding parameters for evaluation are not stated for each target model (temperature, top‑p, max tokens, repetition penalties), only that the text generation LLM inside SMEA uses temperature 1. Safety filters and chat templates for the open‑source models are not discussed. These can change ASR significantly and confound “system message” effects.
- Vicuna results are extreme in Tables 1–2 (ASR above 90% almost everywhere), which suggests either known Vicuna fragility or evaluator bias; the paper does not analyze the discrepancy, beyond noting that SMEA struggles on Vicuna.

6) Over‑claiming without deeper analysis.
- The conclusion that “long system messages consistently exhibit the lowest ASR” is only partially supported. Counter‑examples exist within Tables 1–2, and the text acknowledges anomalies (e.g., LLAMA2‑13b‑chat with MS1 vs. MN1 on PN). The paper does not attempt a causal analysis of why certain models invert the trend. Without error analysis or stratification by attack template, the generalization is fragile.
- Table 3’s “synonymous sentences” sometimes appear more like re‑written, expanded policies than truly “minor length and semantics” changes (Appendix Table 12). The claim of “little change” needs an operational definition (edit distance, token count delta, entailment scores).

7) SMEA details are thin and several descriptions conflict.
- Section 6 states “population size 20, 30 iterations,” but Limitations (Page 9) says “SMEA defaults to only 20 iterations.” Selection pressure, tie‑breaking, and mutation probabilities are unspecified. No ablations on population size/iterations are provided.
- Overfitting risk is non‑trivial: SMEA is trained against 200 PL prompts from the same distribution as the held‑out PLt/PS/PN. While Appendix Figure 3 suggests some generalization, the main paper does not present quantitative generalization metrics on unrelated prompt families or models.

8) Missing or outdated related work.
- The related‑work discussion ends around 2023 vintage, despite a rapidly moving area with directly relevant 2024–2026 studies on system‑prompt robustness, instruction hierarchy, and optimization‑based jailbreaks. See the “Potentially Missing Related Work” section below for specific pointers.

9) Clarity and writing quality issues.
- There are numerous grammatical errors and repeated phrases, e.g., “Whether the longer system system message is better” (Page 2), and small inconsistencies (e.g., “30 iterations” vs. “20 iterations”). A careful language pass is needed.

10) Figure‑ and table‑specific observations that temper conclusions.
- Figure 1 is helpful qualitatively, but it is a single example; the paper relies heavily on automatic ASR without human inspection to connect anecdotes to aggregate claims.
- Figure 3’s boxplots suggest substantial overlap across SMEA operators for some models, and relatively high medians for Vicuna, indicating limited effectiveness where jailbreakability is high; this nuance is not discussed in the main text.
- Tables 1 and 2 drive the core claims. For example, Table 1 shows LLAMA2‑13b‑chat with ML1 has 32.7% ASR against PN, lower than MS1’s 91.7% under the same PN row, supporting the “long helps” claim; however, the same table also shows GPT‑3.5‑turbo‑0613 with ML1 only slightly reduces ASR vs. PN compared to MS1 (13.6% vs. 16.7%), a small absolute gap that is not analyzed statistically. The paper tends to generalize from mixed patterns.

Overall, the work highlights an important and under‑explored factor, but the experimental design and reporting fall short of ACL main‑track standards.

## Potentially Missing Related Work
1) Xu et al., “Bag of Tricks: Benchmarking of Jailbreak Attacks on LLMs,” 2024 — Presents a systematic benchmark varying attack and defense details. It should be discussed in Section 2 and used to contextualize the evaluation in Sections 3–4, especially for design choices and reporting standards; consider aligning ASR reporting and adding a comparison paragraph after Tables 1–2.

2) Zheng et al., “Improved Few‑Shot Jailbreaking Can Circumvent Aligned Language Models and Their Defenses,” 2024 — Studies system tokens/prompts and reports strong ASR. It directly relates to RQ1–RQ3; add to Section 2.2 and compare transferability findings after Table 1.

3) Wu et al., “Evolutionary Computation in the Era of Large Language Model: Survey and Roadmap,” 2024 — Provides EA context for LLMs; cite in Section 2.3 and position SMEA among EA variants, clarifying selection and variation operators.

4) Lin et al., “PathSeeker: Exploring LLM Security Vulnerabilities with a Reinforcement Learning‑Based Jailbreak Approach,” 2024 — A black‑box adaptive jailbreak method complementary to SMEA; discuss in Section 2.2 and consider as a stronger attack set when evaluating SMEA‑optimized system messages.

5) “Mission Impossible: A Statistical Perspective on Jailbreaking LLMs,” 2024 — Offers a quantitative framework for jailbreak probability and robustness; adopt in Section 3.2 to motivate confidence intervals and statistical tests for ASR in Tables 1–3.

6) Zhang et al., “MEEA: Mere Exposure Effect‑Driven Confrontational Optimization for LLM Jailbreaking,” 2025 — Optimization‑based attack relevant to SMEA’s search framing; discuss in Section 2.2 and as a stress test for SMEA‑found messages.

7) Schwartz et al., “Graph of Attacks with Pruning (GAP): Optimizing Stealthy Jailbreak Prompt Generation,” 2025 — Another optimization‑driven attack; include in Section 2.2 and propose cross‑evaluation under SMEA‑optimized system messages.

8) Wu et al., “EvoJail: Evolutionary Diverse Jailbreak Prompt Generation for Large Language Models,” 2026 — An EA for attacks; compare methodologically in Section 5.3 and, if possible, evaluate SMEA‑generated messages against EvoJail prompts.

9) Zhang et al., “IHEval: Evaluating Language Models on Following the Instruction Hierarchy,” 2025 — Directly relevant to the role of system messages; discuss in Section 2.1/2.2 and consider adding an instruction‑hierarchy adherence metric alongside ASR.

10) “A Closer Look at System Prompt Robustness,” 2025 — Focused on system prompts robustness using realistic production prompts; cite in the Introduction and Section 4 and compare evaluation methodology.

## Comments Suggestions And Typos
Actionable suggestions likely to change my recommendation:
- Provide an evaluation audit. For a stratified sample of outputs across models and conditions in Tables 1–3, include human annotations (e.g., 2–3 raters, 200–300 outputs) and report inter‑annotator agreement. Quantify false positive/negative rates of the RoBERTa evaluator on this sample and adjust ASR or add confidence bands.
- Clarify the construction of PS/PL/PN and the cross‑transfer protocol. State precisely: which source model generated each set, whether multiple model‑specific sets were pooled, and the per‑condition sizes for Tables 1–2. Add a schematic similar to Figure 2 but for data flow.
- Report decoding and safety settings for each target model, including system/assistant/user role formatting. If open‑source models used chat templates, specify them. If any filters were disabled, say so.
- Add baselines: (i) simple best‑of‑k paraphrase sampling without EA; (ii) random paraphrase without selection; (iii) “medium‑length” safety message templates commonly used in open‑source chat models. Compare ASR and compute relative reduction with 95% CIs.
- Quantify “small change” in system message: report token length deltas, BLEU/chrF edit distance, and an NLI entailment score between original and synonym. Correlate these measures with ASR shift to support RQ3 rigorously.
- Move at least one key SMEA result from Appendix to the main text. For example, summarize Figure 3 (final populations) in Section 6 and provide numeric medians/IQRs.
- Include an error analysis. For a subset of failures and successes under MS1/ML1/MN1, qualitatively categorize why attacks succeeded or failed. This would help explain anomalies in Tables 1–2 (e.g., LLAMA2‑13b‑chat MS1 vs. MN1 on PN).
- Tighten language and fix inconsistencies: “longer system system message” (Page 2), “VI‑CUNA” label in Figure 4 captions, and the mismatch between “30 iterations” in Section 6 and “defaults to only 20 iterations” in Limitations.
- Release code, the evaluated system messages, and the exact prompt lists for PS/PL/PN, or at least a deterministic recipe to regenerate them with seeds. This will raise the reproducibility rating.

Typos and minor issues (non‑exhaustive):
- Page 2: “Whether the longer system system message” → “whether a longer system message”
- Page 3: “aim to answer RQ2: … Whether the longer system system message” duplicated “system”
- Page 6: “The details of SMEA is shown” → “are shown”
- Tables/Figures: Ensure consistent capitalization of model names (LLAMA2 vs. Llama‑2) and Vicuna spelling; some appendix figures use “VI‑CUNA.”
- Table 1/2 headers: clarify that entries are “#successes (ASR%) over N prompts,” and state N in captions.

Criteria for improved score:
- If the authors add a human evaluation audit, fix the experimental ambiguities, report decoding/safety settings, introduce the proposed baselines with uncertainty estimates, and clarify/strengthen SMEA details with ablations, I would move toward Findings (3.0–3.5) or even main conference (3.5–4.0) depending on the resulting evidence.

## Confidence
3: Reasonably confident but not fully verified; I reviewed the methods and results carefully, but the lack of experimental detail and reliance on an automatic evaluator leave room for misinterpretation.

## Soundness
2.5: Between Poor and Acceptable — Interesting observations, but issues in evaluation design, reporting clarity, lack of statistical analysis, and missing baselines weaken the support for strong claims.

## Excitement
2.5: Between potentially interesting and interesting — The question is timely and practically useful, but execution leaves me cautious.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The topic is important and the high‑level empirical message is valuable, but experimental clarity, evaluator validity, and baseline/statistical rigor need work.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section that acknowledges resource constraints and local optima risks. However, societal impact is not substantively discussed. Recommended additions:
- Dual‑use: publishing a method for optimizing system messages may also inform attackers about brittleness; outline responsible disclosure steps.
- Fairness and over‑blocking: strong system messages may increase refusal rates for benign content. Assess false refusals to avoid harm to legitimate users and topics (e.g., health, marginalized groups).
- Language coverage: all prompts appear to be in English; discuss applicability to other languages where policies and phrasing differ.
- Deployment guidance: emphasize that prompt‑only defenses are brittle and should be combined with model‑level safety training and monitoring.

## Ethical concerns
None beyond the need for clearer discussion on dual‑use and potential over‑blocking harms; datasets appear to be established benchmarks of harmful questions, and no PII collection is described.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many ingredients are known (GPTFuzzer, model names, some system messages in Appendix), but missing decoding settings, evaluator thresholds, and code/data release will cause variance.

## Datasets
2: Documentary — No new dataset is offered; the prompt sets are derived from existing templates/questions. If the authors release the exact generated PS/PL/PN splits, this could rise to 3.

## Software
2: Documentary — No code is provided. If SMEA and evaluation pipelines are released, this could rise to 3–4.