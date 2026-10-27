# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies self-detection for black-box API LLMs, focusing on mitigating the tendency to over-trust incorrect model outputs. It argues that prior paradigms, confidence calibration and self-evaluation, mostly score only the model’s own generated answer, which biases detection toward over-confidence. The authors propose a “comprehensive answer evaluation” paradigm that reflects over multiple candidate answers and aggregates these reflections to reassess the target answer’s trustability. Concretely, the two-step T^3 framework (Think Twice before Trusting) (1) prompts the LLM to reflect and produce a justification for each candidate answer, then (2) uses a Top‑K verbalized confidence prompt that conditions on those justifications to produce probabilities for the candidate answers, with the target answer’s probability serving as the detection score. Experiments on six multiple-choice datasets (SA, NLI, Commonsense QA) and three LLMs show consistent AUROC/PRAUC gains vs. baselines, ablations, robustness checks, and analyses indicating reduced over-trust.

## Summary Of Strengths
- Clear problem framing: the paper identifies the over-trust bias when self-detecting only the generated answer and formalizes a broader “comprehensive answer evaluation” paradigm that compares across the answer space.
- Method simplicity and black-box practicality: T^3 relies only on prompting and can be layered on top of existing confidence elicitation like Top‑K verbalization. This is attractive for API-only settings.
- Broad and careful empirical coverage:
  - Six datasets across three tasks and three LLMs; key results in Table 2 and cross‑LLM in Table 5.
  - Ablations in Table 3 test core design choices (reflection vs. CoT reasoning, joint vs. separate explanations, with/without shuffling).
  - Bias-mitigation visualizations in Figure 4 compellingly show reduced overlap between detection scores for correct vs. incorrect cases relative to Self‑cons and Top‑K Verb.
  - Selective prediction utility in Figure 5 demonstrates how T^3’s scores can drive abstention policies, with sizable accuracy gains as abstention increases.
  - Parameter sensitivity (Figure 6) provides guidance on the number of justifications and guesses.
- The initial counterfactual-based probe (Figure 3) is a neat diagnostic to motivate that considering “other plausible answers” can down‑weight over-trusted wrong answers.
- Clarity: the paper is generally well-structured and readable. Key prompts are summarized in Table 1, and the pipeline is depicted clearly in Figure 2 and Figure 1.

## Summary Of Weaknesses
1) Assumption of a provided answer space limits scope. All experiments are on multiple-choice datasets with a known finite answer set (Table 6), and Section 2 concedes that “for other settings, the answer space can be obtained via answer retrieval or additional model prediction,” but no demonstration is provided. T^3’s core mechanism depends on having concrete alternatives to reflect upon; extending to open‑ended generation is nontrivial and remains untested. This narrows significance for many LLM use cases.

2) Notation and method specification inconsistencies that obscure the core mechanism:
   - Equation 9 defines c = Aggr(a, {a1, …, ai}) with ai = LLM(p^v(q, e1, …, eN)) sampled D times, while Step 2 claims to use Top‑K verbalization with K = N in a single shot and then take the probability of the target answer. This creates confusion among D, K, and N and between “sampling multiple answers” vs. “reading out K guesses in one response.” Please reconcile Eq. 9 with the description on Page 5 (Step 2) and Table 1, and specify unambiguously how c is computed in all experiments.

3) Calibration claims are mixed. Although the paper emphasizes improved calibration, Table 2 shows that on SNLI the ECE of T^3 is quite large (0.157) and notably worse than CAPE (0.030) and Hybrid (0.029). On HANS, T^3 is not the best in AUROC/PRAUC and its ECE is good (0.022) but still close to CAPE (0.028). The paper should temper general calibration claims and analyze why T^3 sometimes hurts calibration (e.g., SNLI), perhaps by inspecting how conditioning on justifications shifts verbalized probabilities.

4) Sensitivity and prompt brittleness:
   - Table 3 “w/o shuffle” loses substantial performance across datasets, implying nontrivial order effects for explanations in p^v. The remedy is to shuffle and average, which increases cost and variance.
   - Appendix D notes Gemini often fails to follow reflection instructions, degrading T^3 (Table 9). The approach is thus instruction‑following sensitive, not merely model‑agnostic.

5) Lack of statistical significance or uncertainty reporting. Results in Table 2, Table 5, and ablations lack confidence intervals or statistical tests. Given API stochasticity and observed variances (e.g., ablations in Table 3, Gemini variability in Table 9), some improvements could be within noise. Please add runs with multiple random seeds or bootstrap CIs.

6) Limited discussion of efficiency/cost in the main paper. The method introduces an extra reflection step for each candidate answer, and later shuffling/averaging. The authors mention API call counts in the appendix, but a concise cost–benefit summary should be in the main text to contextualize gains vs. extra calls.

7) Evaluation protocol clarity. Section A.2 says “we randomly sample 300 training data for each dataset.” With API LLMs there is no training; presumably this means 300 evaluation examples. Please clarify splits, ensure test-only evaluation for standard datasets, and avoid using “training” terminology that suggests model fitting.

8) Baseline coverage and positioning: while many strong baselines are included, the paper misses several closely related black‑box uncertainty estimators and abstention‑oriented selective generation methods that can contextualize this contribution (see “Potentially Missing Related Work”). Also, Self‑detect is included but there are other semantic‑entropy style measures worth comparison.

9) Over-reliance on Top‑K verbalization as the aggregator. The paper shows T^3 + Top‑K Verb and T^3 + PE, but the aggregator choice may interact strongly with the justifications. Additional aggregators, or a cleaner formulation that maps multiple reflections to a calibrated probability without Top‑K verbalization, would strengthen the methodological contribution.

10) Figure and table interpretations could be tighter in places:
   - Figure 4 convincingly shows reduced overlap, but the narrative could explicitly tie each panel back to AUROC/PRAUC improvements in Table 2 to quantify the visual effect.
   - In Table 2b (NLI), T^3’s SNLI ECE is much worse than most baselines; this contradiction with calibration goals should be discussed centrally, not only in passing.

Detailed figure/table references:
- Figure 1 nicely illustrates the two-step T^3 process; in the running example, the Top‑K Verb score for the incorrect answer drops once multiple justifications are considered. This visually supports the “mitigate over-trust via cross‑answer reflection” claim.
- Figure 2 clearly contrasts prior pipelines with the proposed comprehensive evaluation, which conditions confidence calibration on the set of per‑answer reflections e1..eN.
- Figure 3 (preliminary CAD study) shows boxplots where “w/ cf” shrinks the overlap between correct and incorrect instances and improves AUROC relative to Self‑cons and Top‑K Verb, motivating the main idea.
- Figure 4 demonstrates, across all six datasets, that T^3 pushes the incorrect-group distributions downward relative to Self‑cons and Top‑K Verb; this aligns with higher AUROC/PRAUC in Table 2 for most datasets.
- Figure 5 shows monotonic accuracy gains under abstention using T^3’s score, up to +49.2% on IMDB at 50% abstention, underscoring downstream utility.
- Figure 6 shows AUROC increasing with more justifications and guesses on SNLI, while CommonsenseQA is less sensitive to #guesses; this supports the claim that NLI benefits from sufficient coverage of alternatives.
- Table 2 is the core evidence; T^3 is best or second‑best AUROC/PRAUC on 4/6 datasets, but has a notable SNLI ECE regression.
- Table 3 confirms that replacing per‑answer justifications with CoT from p(q) sharply hurts AUROC/PRAUC, supporting the paper’s reflection design choice; also confirms ordering sensitivity.
- Table 5 (GLM‑4) shows that T^3 combined with PE or Top‑K Verb is competitive across LLMs, though best results vary by dataset.

## Potentially Missing Related Work
1) Lee et al., “Selective Generation for Controllable Language Models,” 2024 — proposes abstention mechanisms using entailment and conformal prediction. Highly relevant for Section 5.2 “Selective Prediction” and for positioning T^3’s detection scores as decision policies. Should be discussed in Related Work (Section 4) and cited where Figure 5 is presented.

2) Beigi et al., “InternalInspector I^2: Robust Confidence Estimation in LLMs through Internal States,” 2024 — white‑box confidence estimation contrasting with black‑box T^3. Useful as a complementary baseline/discussion in Section 4; mention after “white‑box vs black‑box” paragraphs.

3) Nikitin et al., “Kernel Language Entropy: Fine‑grained Uncertainty Quantification for LLMs from Semantic Similarities,” 2024 — extensions of semantic entropy for black‑box confidence. Should be added to Related Work and, if feasible, compared experimentally as an additional black‑box baseline alongside Self‑detect and CAPE.

4) Wen et al., “Know Your Limits: A Survey of Abstention in Large Language Models,” 2025 — survey on abstention that contextualizes Section 5.2 and the use of detection scores for accept/abstain. Cite in Related Work and discuss around Figure 5.

5) Liu et al., “Revisiting Epistemic Markers in Confidence Estimation,” 2025 — analyzes verbal confidence markers, directly relevant to Top‑K verbalization and verbalized probability elicitation. Discuss in Related Work and possibly consider as an alternative elicitation scheme in Section 5.2 or Appendix A.3.

6) Chen et al., “Know More, Know Clearer: A Meta‑Cognitive Framework for Knowledge Augmentation in LLMs,” 2026 — meta‑cognitive calibration that aligns internal confidence and correctness. Relevant conceptual contrast to T^3’s reflection‑based self‑detection; add to Related Work.

7) Li et al., “Knowledge Boundary of Large Language Models: A Survey,” 2025 — comprehensive survey on recognizing LLM knowledge boundaries. Cite to frame the broader motivation for over‑trust mitigation and abstention in the Introduction or Related Work.

8) “Rethinking Uncertainty Estimation in LLMs: A Principled Single‑Sequence Measure,” 2026 — single‑sequence uncertainty that avoids multi‑sampling. Relevant to discuss as a cost‑efficient alternative when arguing about API call budgets; add to Related Work and cost discussion.

## Comments Suggestions And Typos
- Please reconcile and clarify the scoring formulation:
  - Precisely define N (number of candidate answers), K (number of guesses returned by Top‑K verbalization), and D (number of samples/responses). Currently Eq. 9 and Step 2 conflict. If the main score c is simply the probability assigned to the target answer in one Top‑K verbalized response conditioned on e1..eN, please state this explicitly and fix Eq. 9 accordingly.
  - Specify how ties and missing target answers are handled when the LLM’s K guesses omit the target answer (you briefly say c=0 in Eq. 5’s discussion; confirm this also holds in T^3).
- Calibration analysis:
  - Add a dedicated discussion of why SNLI’s ECE degrades in Table 2 and how to mitigate it, e.g., temperature post‑scaling on the verbalized probabilities, or prompt adjustments for p^v.
  - Consider reporting Brier score or reliability diagrams to complement ECE.
- Efficiency:
  - Summarize main API call counts and latency in the main text, not only in the appendix. A table listing per‑method calls for a typical 5‑choice question would help practitioners.
  - Report throughput/cost trade‑offs when shuffling explanations (Table 3 shows it matters).
- Robustness and significance:
  - Add CIs over at least 3–5 runs for key rows in Table 2 and Table 5. For Top‑K Verb and T^3, randomize order of explanations, few-shot exemplars if any, and measure variability.
- Scope:
  - If possible, include a small open‑ended experiment that constructs a candidate set via retrieval or paraphrased candidates (beyond the model’s own outputs) to illustrate feasibility in generative settings, even if only as a proof‑of‑concept.
- Minor wording/typos:
  - Page 5, “Think Twice Before Assure Framework” header: elsewhere the method is “Think Twice before Trusting.” Standardize the name.
  - Section A.2: “we randomly sample 300 training data for each dataset.” There is no model training; rephrase as “300 evaluation examples.”
  - Table labels: ensure every subtable has a clear caption indicating task and model for ease of cross‑reference (Table 2 already does this well).
  - Page 7: “We can observe the followings.” → “We observe the following.”

Criteria for score change after rebuttal:
- A precise fix to the scoring formulation and notation (Eq. 9 and Step 2) and clear per‑dataset, per‑method API cost summary in the main paper.
- Added uncertainty intervals or statistical tests for Table 2 and Table 5; and a brief analysis for SNLI calibration degradation.
- Stronger baselines or discussion including at least one semantic‑entropy‑style black‑box method not already covered.

## Confidence
4: Quite sure after careful checking — I checked the pipeline, tables, and figures closely. Some details in the math may still need author clarification.

## Soundness
3.5: Between acceptable and strong — The approach is sensible and empirically supported across tasks and models, though calibration results are mixed and the setting is restricted to multiple choice.

## Excitement
3.5: Between interesting and exciting — The idea is simple and useful for black‑box LLMs, with appealing practical value, but scope is limited and some results are uneven.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. The central idea of cross‑answer reflection to reduce over‑trust is well-motivated and supported by solid experiments (Table 2, Figure 4), and the method is simple enough to serve as a strong black‑box baseline. However, the reliance on multiple-choice answer spaces, the notation/specification inconsistencies around Eq. 9 and Step 2, mixed calibration outcomes (notably SNLI in Table 2b), sensitivity to instruction-following and ordering (Table 3, Appendix D), and lack of statistical testing prevent a clear accept. With clarifications and modest additions, this would be a strong candidate.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The Limitations section acknowledges focus on black‑box API LLMs and lack of systematic prompt optimization; both are fair. I would add:
  - Applicability beyond multiple choice remains open; care is needed to avoid implying generality to open‑ended tasks without evidence.
  - Reflection prompts may inadvertently bias models toward majority or spurious rationales, potentially reinforcing stereotype‑laden “justifications” in sensitive domains; some guardrails or filtering strategies could be discussed.
  - Selective abstention policies could differentially impact user groups if accuracy varies by dialect or domain; worth noting as a risk when operationalizing Figure 5.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Prompts and datasets are described; however, some results depend on API variability, instruction adherence, and the exact ordering/shuffling of explanations.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful: If code and prompt templates are released as claimed for splits, it would be practically helpful; otherwise, at least the prompts and procedure are sufficiently described to implement.