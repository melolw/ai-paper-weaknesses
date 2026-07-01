# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper studies robustness of multimodal LLM-as-a-judge systems for evaluating language outputs from visual prompts, which falls under Multimodality and Language Grounding, Evaluation/Resources, and Machine Learning for NLP.

## Minimum Quality
Pass ✅. The submission includes Abstract, Introduction, Related Work, Method, Experiments (setup, main results, per-category and variant analyses), Failure Analysis, Conclusion, and References. The study is empirical and self-contained, though there are notable weaknesses discussed below.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I see no hidden prompts, steganographic instructions, or attempts to influence the review process within the provided content.

# Expected Review Outcome:

## Paper Summary
This paper examines prompt-injection vulnerabilities in multimodal LLM judges and proposes an “isolated solve-then-judge” architecture. The judge first produces a self-answer using only trusted inputs (image and query), then in a second pass compares candidate responses against this uncontaminated reference. Using Qwen2.5-VL-7B-Instruct on VL-RewardBench (N=1,247), the approach reduces conditional attack success rate (ASR_cond) from 91.3% to 29.3% compared to a single-pass baseline, at the cost of a 10.8 percentage-point drop in clean accuracy. Analyses indicate stronger gains in hallucination detection than in reasoning tasks, and authority impersonation attacks remain effective.

## Summary Of Strengths
- Clear problem focus on a concrete failure mode of LLM-as-a-judge when adversarial instructions are embedded in candidate responses.
- Simple, interpretable two-pass design that isolates trusted inputs in Pass 1; the mechanism is easy to replicate in practice and integrates with common VLM judges.
- Solid ablation-style control: Condition C retains two-pass prompting but removes isolation, showing isolation yields an additional 4pp ASR_cond reduction beyond prompt engineering alone (Table 1).
- Careful metric design, using ASR_cond to quantify flips from originally correct judgments under attack, which is the most decision-relevant failure rate.
- Useful diagnostic analyses:
  - Per-category breakdown (Table 2) that clarifies where isolation helps most (hallucination) versus where it struggles (reasoning).
  - Attack-variant analysis (Figure 2, Table 3) showing authority impersonation remains a major vulnerability.
  - Failure analysis attributing many failures to weak self-answer anchors and possible position bias.
- Visual clarity: Figure 1 communicates the three experimental conditions and explicitly highlights where isolation happens; it improves understanding of how the defense is intended to work.

## Summary Of Weaknesses
1) Limited scope of empirical evidence and external validity
- Only one VLM judge (Qwen2.5-VL-7B-Instruct) and one dataset (VL-RewardBench) are used. This makes it hard to generalize conclusions to other MLLMs or evaluation settings. The paper’s claims about a “simple defense” would be more convincing with at least one additional open-source judge and another multimodal judging benchmark.
- No text-only judge comparison despite citing text-only injection work. The claimed generality to LLM-as-a-judge is not demonstrated across modalities.

2) Significant clean-accuracy degradation without deeper diagnosis
- CleanAcc drops by 10.8pp (Table 1). The paper attributes this to two-pass prompting/prompt design, but does not explore mitigations (e.g., strengthening Pass-1 prompts, ensembling self-answers, or constraining how S is used).
- Table 2 shows the decline is especially severe for Reasoning (from 85.2 to 61.8). The discussion notes terse numeric self-answers but offers no targeted intervention or ablation to improve anchors (e.g., requiring chain-of-thought for S, minimum length constraints, or rationales).

3) Authority attacks remain largely unsolved
- Figure 2 and Table 3 show ASR_cond remains 63.6% for authority impersonation. This undermines the defense’s practical utility because it leaves a common and simple attack vector highly effective.
- The paper posits these attacks “exploit perceived authority,” but there is no concrete mechanism or tested countermeasure beyond speculation. For example, adding source attribution checks or explicit skepticism instructions for authority claims could be evaluated.

4) Underdeveloped statistical rigor
- No confidence intervals, variance estimates, or significance testing. Attack success differences of a few percentage points (e.g., B vs C) may or may not be robust. Given N per category varies (e.g., 180 general vs 750 hallucination), uncertainty quantification is needed.
- No reporting on trial-level randomness, retries, or determinism, despite using greedy decoding. Even with temperature=0, non-determinism can arise from system-level differences.

5) Missing implementation specifics that affect reproducibility
- Pass-1 and Pass-2 prompts are summarized but not provided verbatim. Exact delimiter schemas, “explicit warning” wording, and verdict format constraints matter substantially for judge behavior and corruption detection.
- The exact injected strings for each attack variant are only sketched; full prompts are required for replication.
- The procedure to compute ASR_cond, filtering rules for originally correct cases, and how ties or invalid verdicts are handled are not fully specified.

6) Potential confounds in the position/recency bias analysis
- The failure analysis claims 98.7% of failures had the attacked response in position 2. This could reflect dataset ordering, consistent attack-side placement, or the Pass-2 prompt structure emphasizing the second candidate. Without counterbalancing or randomized ordering, it is hard to isolate true model bias from experimental setup.

7) Isolation vs. prompt engineering not exhaustively disentangled
- Condition C is a good step, but further controls would help: equal token budgets, swapping the order of Pass 1 and Pass 2 prompts, or having a Pass 1 that produces a non-semantic placeholder to control for “two-pass + extra context” but not content.
- Also missing: a condition where S is withheld at judgment time to see how much of Pass-2 improvements come from any prior thinking vs the concrete reference.

8) Limited analysis of failure modes within categories
- Table 2 shows isolation helps hallucination substantially, but the paper does not drill down into which hallucination subtypes benefit (e.g., object presence vs attribute vs count).
- For reasoning, the claim that seeing candidate responses can “help the model understand problem structure” is plausible, but there is no task-structure analysis, no per-subtask breakdown within reasoning, and no ablations on richer S.

9) Over-reliance on a single figure-of-merit
- ASR_cond is appropriate, but practitioners will also care about calibration, agreement with humans under adversarial conditions, and stability across paraphrased attacks. None of these are assessed.

10) Clarity issues around Equations and definitions
- Equations (1)–(4) are useful formal scaffolding, but the threat model lacks detail: can both candidates be malicious, are system prompts considered trusted, how are multimodal injections (e.g., OCR’d text in images) handled? These distinctions matter for generalizing the defense.

Concrete figure/table/equation references:
- Figure 1 is central to the paper’s contribution, clearly distinguishing isolation in Condition B. However, it would benefit from explicit notes on whether Pass-2 uses cross-attention to S and how S is referenced in the rubric; these design choices might strongly influence the CleanAcc drop.
- Table 1 shows the headline improvements but also reveals the concerning CleanAcc reduction. The near-identical CleanAcc values of B and C suggest the loss is due to two-pass prompting rather than isolation per se, yet the paper does not explore architecture/prompt variants to recover accuracy.
- Table 2 undermines the generality claim: for Reasoning, the control (C) beats the isolated defense (B) on ASR_cond. The paper acknowledges this, but the takeaway should be more cautious about recommending isolation broadly.
- Figure 2 and Table 3 demonstrate that authority attacks remain the Achilles’ heel; this should temper conclusions and drive a targeted defense section.
- Equations (1)–(4) formalize the setup, but the adversary model in Eq. (2) assumes injection in R2 only; the empirical section often attacks the human-dispreferred response, yet tie-breaking and bidirectional or dual-injection cases are not discussed.

## Potentially Missing Related Work
1) Wang et al., “On the Adversarial Robustness of Multimodal LLM Judges,” 2026 — directly studies robustness of multimodal LLM judges with broader attack models and evaluation protocols. Should be discussed in Related Work and considered as an additional comparison point or evaluation protocol extension in Section 4.

2) Park et al., “Mitigating Perceptual Judgment Bias in Multimodal LLM-as-a-Judge via Perceptual Perturbation and Reward Modeling,” 2026 — offers an orthogonal pipeline modification to improve judge reliability; relevant for discussing accuracy–robustness trade-offs and could be cited after Section 4.3 when interpreting category-wise effects.

3) Wu et al., “Multi-Task Reinforcement Learning for Enhanced Multimodal LLM-as-a-Judge,” 2026 — presents training-side improvements for judges; compare in Section 2.1/2.2 and mention as a potential way to recover CleanAcc while integrating isolation.

4) Slyman et al., “Calibrating MLLM-as-a-judge via Multimodal Bayesian Prompt Ensembles,” 2025 — addresses calibration and overconfidence via prompt ensembles. Discuss in Section 2.2/2.3 and consider as a complementary defense or baseline; could also be added to Table 1 as a control if available.

5) Yasunaga et al., “Multimodal RewardBench: Holistic Evaluation of Reward Models for Vision Language Models,” 2025 — relevant benchmark with broader coverage of reasoning/safety failure modes. Add to Section 4.1 as an additional dataset or at least as a discussion item; could strengthen claims about generality.

6) An et al., “IPIGuard: A Novel Tool Dependency Graph-Based Defense Against Indirect Prompt Injection in LLM Agents,” 2025 — while agent-focused, its structural isolation ideas are conceptually related; cite in Section 2.3 and compare to your isolation mechanism, possibly inspiring stronger pipeline-level defenses.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide full, verbatim Pass-1 and Pass-2 prompts, including all delimiters, explicit warnings, and formatting constraints. Also release the exact strings for each attack variant. State whether the code and prompts will be released and under what license.
- Add at least one more open-source VLM judge and one additional multimodal judging benchmark to validate generality. If compute is tight, prioritize evaluating authority attacks across models to assess whether the 63.6% ASR_cond is model-specific.
- Explore methods to improve the self-answer S: require rationales, enforce minimum length, or prompt for step-by-step visual grounding. Report how these affect both CleanAcc and ASR_cond, especially in Reasoning (Table 2).
- Target authority impersonation specifically: include an authority-skepticism instruction, require source verification, or add a classifier head to flag authority claims. Evaluate these in a new ablation table side by side with the current defense.
- Quantify uncertainty: add confidence intervals or bootstrap standard errors for all reported rates in Tables 1–3, and report whether improvements over C are statistically significant.
- Randomization and counterbalancing: re-run with randomized candidate order, report whether the 98.7% “position 2” failure persists, and include a controlled analysis to isolate recency vs format biases.
- Consider additional controls to isolate the benefits of “prior thinking” vs “reference anchoring,” e.g., Pass 1 that generates a thought but withholds S at judgement time, or Pass 1 that produces a neutral placeholder with the same token budget.

Typos/clarifications:
- Section 3.2 citation “(shi2025towards)” appears malformed; ensure the proper reference key and capitalization.
- Some references list 2025/2024 but cite CVPR 2025 with 2024 page numbers; check consistency for [6].
- Page 5, Table 1 caption: “Best values in bold, second-best underlined.” The table as rendered in text does not show formatting; ensure camera-ready typesetting reflects this.
- Page 6: “$63.6\%$ of attacks succeed” — consistent with Table 3 but consider adding CI here as well.

Criteria that could increase my score:
- Adding at least one more VLM judge and one more dataset, with full prompts released.
- Demonstrating a concrete, working mitigation for authority attacks that materially lowers ASR_cond.
- Recovering a non-trivial portion of the 10.8pp CleanAcc drop through improved S or prompt refinements, especially on Reasoning.
- Providing statistical uncertainty and randomized order controls.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and checked the main claims and tables, but lack full prompts/code and multiple models/datasets to be fully certain.

## Soundness
3: Acceptable — The core experimental design is sensible and the main claim is supported on one model/benchmark, but statistical rigor, ablations for authority attacks, and breadth are limited.

## Excitement
3.0: Interesting — The isolation idea is practically appealing and the figures/tables suggest real benefits, but the residual vulnerabilities and accuracy trade-offs temper enthusiasm.

## Overall Assessment
2.5 Borderline Findings — The paper offers a simple, practical isolation defense with clear benefits on VL-RewardBench and a thoughtful control condition, but it has multiple substantive weaknesses: single model/dataset scope, large clean-accuracy hit with limited mitigation, unresolved authority attacks, missing statistical uncertainty, and incomplete reproducibility details. With broader evaluation, stronger authority defenses, and prompt transparency, this could move toward main-track readiness; at present it fits better as Findings documenting a useful baseline defense pattern.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper discusses limitations qualitatively (category dependence, authority vulnerability) and provides a failure analysis. Additional societal considerations worth adding:
- Over-reliance on self-reference can amplify judge biases, especially if S is weak or biased; this is visible in the drop on Reasoning. Potential harm includes misjudgment in safety-critical moderation or model selection loops.
- The defense may encourage confidence in automated judging pipelines without addressing remaining attack surfaces (authority), which could be risky if adopted in high-stakes settings.
- Multilingual/multicultural settings are not evaluated; authority cues and deference norms can vary by language/culture, affecting robustness.
- Consider the implications for model training when judges are used for RLHF or reward modeling: changes in CleanAcc and bias profiles can propagate into trained models.

## Ethical concerns
None evident beyond standard concerns for evaluation with public benchmarks and responsible disclosure of vulnerabilities/defenses. No PII or sensitive data usage is indicated.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Many operational details are present (model, decoding, hardware), but missing verbatim prompts, exact attack strings, and full protocol for ASR_cond computation hinder exact replication.

## Datasets
1: No usable datasets submitted. The paper uses VL-RewardBench; no new data contribution.

## Software
3: Potentially useful — The text claims public code, but critical artifacts (prompts, exact attack strings) are not included in the paper; if fully released, the software could be useful to others.