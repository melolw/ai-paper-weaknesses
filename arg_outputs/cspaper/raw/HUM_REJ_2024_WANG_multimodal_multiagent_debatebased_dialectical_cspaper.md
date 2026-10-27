# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces M2D-DKTL, a framework that first conducts multi-modal, multi-agent debates (M2D) with roles of debaters, a judge, and a summarizer to refine answers and reduce hallucinations, then condenses the debate trace into chain-of-debate (CoD) rationales, and finally distills this dialectical knowledge into smaller MLLMs via supervised fine-tuning. Algorithm 1 formalizes the debate loop and Equation (1) specifies stance updates across rounds. CoD examples are created with GPT‑4V and filtered using heuristic rules; the distilled student is trained with the likelihood objective in Equation (2). Experiments on MMMU, MathVista, and CMMMU report gains both for the debate-time teacher (GPT‑4V with M2D vs baselines) and for students (LLaVA‑1.5 7B/13B, LoRA/full) fine-tuned on CoD. The paper also analyzes the number of agents, debate rounds, and token costs.

## Summary Of Strengths
- Clear, three-stage pipeline that is easy to follow. Figure 2 usefully summarizes roles, message flow, and the transition from raw debate to CoD and then to knowledge transfer.
- The idea of condensing multi-agent debate into a distilled format for small MLLMs is interesting and practically relevant, especially for multimodal reasoning where hallucinations are prevalent.
- Quantitative improvements are reported for both debate-time inference and knowledge transfer:
  - Table 2 shows M2D (with GPT‑4V) improves over strong prompting baselines on MMMU and MathVista, with category-level breakdowns.
  - Table 3 shows consistent student improvements across LLaVA‑1.5 7B/13B and LoRA/full settings; CoD beats “Standard” and CoT data in most cases.
  - Figure 4 and Figure 8 show generalization to MathVista and CMMMU, respectively, indicating some cross-dataset and multilingual benefits.
- Useful analyses:
  - Figure 3 examines how the avg. number of rounds saturates, informing a practical max-round choice.
  - Table 4 explores performance vs. number of agents across datasets and discusses when more agents help or hurt.
  - Table 10 reports token costs vs. alternatives; Tables 11–12 break down gains by question difficulty, showing larger benefits on hard items.
- The paper includes explicit prompts and some hyperparameters for reproducibility (Appendix B, G; Table 6, Table 8).

## Summary Of Weaknesses
1) Reliance on LLM-as-judge for accuracy without a strong grounding in official metrics or human evaluation.
- Section 4.1.1 states that GPT‑4 is used to judge correctness given the reference answer. While this can be pragmatic, MMMU and MathVista have established evaluation protocols. It is unclear whether the LLM judge exactly replicates these, or how often it disagrees with strict matching. This casts uncertainty on all accuracy numbers in Table 2 and Table 3. A small-scale human or official-script validation would greatly strengthen claims.

2) Potential leakage and evaluation fairness are insufficiently discussed.
- In Section 4.2.3, 3,000 items are sampled from the MMMU test set “without including the truth answers” to produce training CoD. The students are evaluated on the MMMU validation split (Table 3), and debate-time numbers (Table 2) use MMMU validation. While this avoids direct train-eval overlap, using test questions to create supervision is unconventional for a benchmark and may violate intended usage (even without access to labels). The paper should justify this decision and clarify dataset usage policies.
- For Table 2, M2D (GPT‑4V) entails multiple calls and longer outputs than single-pass prompting. Although Table 10 gives token costs, no cost-normalized comparison is presented. The paper should compare under matched compute/call budgets or report cost-effectiveness metrics.

3) The “dialectical knowledge reduces factual errors” claim is weakly evidenced.
- The central claim is qualitative and not directly measured. Table 5 uses GPT‑4V to score “logic, depth, and detail,” which introduces circularity and possible bias in favor of debate-shaped outputs. There is no independent factuality metric or human assessment of error rates. Additional evidence (e.g., hallucination audits, contradiction detection, fact-check probes) would substantiate the core premise.

4) CoD construction and filtering are under-specified and heuristic-heavy.
- Section 3.3.1 filters by “No Answer,” “Wrong Answer,” and “Closest Answer,” but “Closest Answer” (especially for non-option outputs) is ill-defined and may inadvertently remove difficult-but-correct examples or keep plausible-but-wrong ones. The impact of each filtering rule on the final dataset quality is not ablated.
- The CoD format is primarily described through prompts (Appendix B.2, Prompt B.1) and a conceptual contrast with CoT (Section 3.3.2) rather than a formal schema. Without a clear specification, reproducing the exact debate-to-CoD conversion is difficult.

5) Baselines for distillation are limited; the student training objective is simplistic.
- Section 3.4 trains with a standard next-token likelihood over (reasoning, answer) tuples (Equation 2). Strong multimodal distillation methods use teacher distributions, feature-level alignment, or uncertainty weighting. Table 3 compares only to “Standard” and “CoT” SFT data generated by GPT‑4V. The absence of competitive MLLM distillation baselines leaves open whether the reported gains are specific to dialectical knowledge or largely due to any better-curated rationales.

6) Limited student diversity and scope.
- Only LLaVA‑1.5 7B/13B are used as students. Given the framing of generalizable knowledge transfer, including another open-source MLLM (e.g., Qwen‑VL as student) would strengthen generality claims.

7) Statistical rigor and variance reporting.
- No confidence intervals, statistical tests, or multiple-run variance are reported for main tables (Table 2, Table 3). Many improvements are modest (e.g., +2–3% absolute), which may be within noise without variance reporting.

8) Risks of evaluation bias toward debate-shaped outputs.
- Both correctness (Section 4.1.1) and reasoning-quality scoring (Section 4.2.5, Table 5) rely on GPT‑4/V. This may favor verbose, structured reasoning and penalize concise answers, especially for smaller models (see Table 13). A human or rule-based check would mitigate this bias.

9) Missing or incomplete ablations on key design choices.
- The paper analyzes max rounds and agent number (Figure 3, Table 4) but omits ablations on judge vs. no-judge, summarizer impact, different debate termination criteria, or alternative CoD condensation strategies (e.g., summarizing last round only vs. aggregating all rounds).

10) Equation and training clarity.
- Equation (2) optimizes over concatenated reasoning and answer; the paper does not analyze whether this encourages verbosity at inference or whether separate losses for rationale vs. answer would be better. Given Table 13’s concern about “extremely short responses” with small models, a targeted loss could be important.

11) Figures/tables interpretation that raises questions:
- Figure 2 clearly illustrates the pipeline, but the “Condensing Dialectical Knowledge” box indicates CoD is produced by feeding the entire debate history to GPT‑4V. There is no verification that the condensation itself is faithful or error-reducing. A qualitative audit comparing debate traces to CoD outputs would be helpful.
- Table 2 shows large category-level swings (e.g., TE from 0.410/0.381 to 0.505 for M2D), but no analysis of failure cases or where debate backfires. Similarly, Table 4 shows more agents hurt MathVista, yet CoD is created from 2 agents; exploring agent specialization or expert roles might be warranted.

12) Reproducibility and release.
- The work depends on GPT‑4V (Azure 2023‑12‑01). While prompts and some hyperparameters are provided, the CoD dataset and code are not available at review time, which will make faithful reproduction difficult.

## Potentially Missing Related Work
1) Xu et al., “LLAVADI: What Matters For Multimodal Large Language Models Distillation,” 2024 — analyzes distillation choices for MLLMs with strong baselines. Should be discussed in Section 2.3 and used to contextualize Equation (2) vs. more advanced objectives.

2) Lu et al., “MIKO: Multimodal Intention Knowledge Distillation from Large Language Models for Social-Media Commonsense Discovery,” 2024 — relevant multimodal knowledge distillation from large models into smaller ones; cite in Section 2.3 and compare conceptually with CoD in Section 3.3.

3) Progressive Knowledge-Guided Distillation for Multimodal Reasoning Models, 2025 — proposes structured, knowledge-guided distillation; compare in Section 2.3 and discuss in relation to dialectical knowledge in Section 3.3.

4) Lee et al., “Multi-aspect Knowledge Distillation with Large Language Model,” 2025 — distills multi-aspect supervision; relate to CoD as a form of multi-aspect debate supervision in Section 2.3 and near Equation (2).

5) Liang et al., “Multi-Agent Undercover Gaming: Hallucination Removal Through Counterfactual Test for Multimodal Reasoning,” 2026 — reinterprets multi-agent methods for hallucination mitigation; compare in Section 2.2 and discuss how CoD differs from counterfactual testing.

6) Li et al., “M3MAD-Bench: Are Multi-Agent Debates Really Effective Across Domains and Modalities?,” 2026 — systematic evaluation of multi-agent debates; discuss in Section 2.2 and use to qualify claims about when debate helps or hurts (connect to Table 4).

7) Sun et al., “Uncertainty-Aware Knowledge Distillation for Multimodal Large Language Models,” 2026 — Bayesian, uncertainty-aware KD; compare in Section 2.3 as a principled way to mitigate teacher noise, which is highly relevant when debates still contain residual errors.

8) Feng et al., “EM-KD: Distilling Efficient Multimodal Large Language Model with Unbalanced Vision Tokens,” 2026 — specialized MLLM distillation; cite in Section 2.3 and discuss potential complementarity to CoD.

9) Pan et al., “Beyond a Single Perspective: A Multi-Agent Debate Framework for Affective Computing,” 2026 — modality-specific agents in debates; discuss in Section 2.2 as another example of multi-agent debate for multimodal reasoning, and contrast design choices.

## Comments Suggestions And Typos
Actionable questions/suggestions for rebuttal:
- Provide an evaluation with the official MMMU/MathVista scripts and report the correlation with GPT‑4 judgments. If this is infeasible, include a manual audit on a representative sample to validate Table 2 and Table 3.
- Clarify dataset policies and potential leakage: justify using MMMU test prompts to build CoD for training (Section 4.2.3). If needed, re-run by sourcing CoD from other datasets or MMMU dev/val only.
- Add stronger distillation baselines and/or losses: e.g., KL to teacher logits, feature alignment across visual tokens, or uncertainty-aware weighting. Compare these to CoD to demonstrate a specific benefit of dialectical supervision over generic distillation.
- Ablate key components: no-judge vs. judge; no-summarizer vs. summarizer; different termination criteria; different CoD condensation methods. A minimal ablation plus cost breakdown would help attribute gains.
- Add an independent factuality/consistency metric or human-verified error counts to substantiate the “reducing factual errors” claim beyond GPT‑4V scoring in Table 5.

Smaller points and typos:
- Throughout: minor grammar issues (“Filter Nosiy Data” → “Filter Noisy Data”; “We propose using chain-of-debate to condense” → “We propose a chain-of-debate to condense”).
- Section 3.3.1 “Closest Answer” rule needs a precise definition. Consider adding concrete examples and an ablation on how many items each rule removes and their impact on accuracy.
- Equation (2): specify whether the objective masks image/question tokens and whether rationale tokens are weighted differently from answer tokens; consider reporting a length-controlled decoding strategy to avoid verbosity.
- Table 2 and Table 3: please add confidence intervals or report mean ± std over multiple runs.
- Figure 2: label where the judge terminates vs. continues more explicitly; show an example of a mistaken stance being corrected to strengthen the narrative link to dialectical error reduction.

Criteria that could raise my score:
- Verified accuracy with official evaluators or robust human audits; clarified dataset usage policy; inclusion of stronger distillation baselines and component ablations; and at least one non-LLaVA student model.

## Confidence
4: Quite sure after careful checking — I checked important points, equations, and tables. Some implementation specifics depend on unreleased data/code.

## Soundness
3.5: Between acceptable and strong — Method is plausible and experiments are suggestive, but evaluation via LLM-as-judge, heuristic filtering, and limited baselines/ablations weaken support for the strongest claims.

## Excitement
3.0: Interesting — The combination of multi-agent debate with distillation to smaller MLLMs is appealing and relevant, though evidence is not yet fully convincing.

## Overall Assessment
3: Findings — The paper could be accepted to Findings of ACL. It is sound enough, presents a clear method with solid motivation, and provides useful empirical signals, but the reliance on LLM-as-judge for correctness, limited baselines for distillation, and under-specified CoD pipeline constrain confidence for the main conference.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper’s Limitations section acknowledges data volume constraints and a narrow set of evaluation domains. Additional societal considerations to discuss:
- Using closed-source GPT‑4V to generate and judge content poses reproducibility and potential bias issues; debate-shaped outputs may receive higher scores from an LLM-as-judge, amplifying stylistic bias.
- Constructing CoD from benchmark test items may challenge dataset governance norms; clarify licensing and adherence to usage guidelines.
- Debate-generated rationales could encode spurious correlations or biases; consider a short bias/risk analysis, including failure cases where debate converges on confidently wrong conclusions and potential harms in downstream high-stakes contexts.

## Ethical concerns
Potential concerns include: reliance on proprietary models without clear reproducibility path; possible benchmark-policy issues from generating supervision on test items; and evaluation bias introduced by LLM-as-judge. These concerns should be explicitly discussed and, where possible, mitigated with alternative evaluators and data governance clarifications.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Prompts and many settings are given, but the core CoD dataset and code are not available at review time, and the approach depends on GPT‑4V.

## Datasets
2: Documentary — No new public dataset is released at submission time; if the CoD corpus is released, it would be useful as a resource.

## Software
2: Documentary — If code to run the full M2D and CoD pipeline is released, it will aid replication but current description is not sufficient alone.