# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes Multi-expert Prompting, a prompting framework that elicits multiple expert roles for a single input, gathers their long-form answers, and aggregates them in one turn via a seven-subtask process inspired by Nominal Group Technique. The system then selects the best answer among the aggregated output and the individual experts’ answers. Experiments on TruthfulQA, FactualityPrompt, BOLD, HONEST, and open-ended ExpertQA report gains in truthfulness, factuality, and reductions in toxicity/hurtfulness, as well as improved informativeness/usefulness, evaluated with both automatic and limited human judgments. Ablations suggest the aggregation subtasks and using around three experts are most effective.

## Summary Of Strengths
- Clear motivation that single “expert” prompting can bias outputs; the proposed approach operationalizes multi-perspective synthesis in a single turn.
- Method is explicit and replicable at the prompt level. Section 3 details the two steps; the seven-subtask aggregation is concrete, well-scoped, and easy to implement.
- Strong headline results: in Table 1, Multi-expert Prompting improves TruthfulQA true-rate to 89.35 with ChatGPT and 87.15 with Mistral, beating all listed baselines; factuality error rates and HONEST scores also improve, and toxicity sometimes drops to near zero.
- Useful ablations and analyses:
  - Table 3 shows skipping any of S1–S4 or S7 harms performance; the designed subtasks matter.
  - Table 4 shows three experts perform best overall, giving practical guidance.
  - Table 6 suggests one-sentence role descriptions are as effective as long paragraphs, reducing engineering burden.
  - Figure 4 is a compelling qualitative case where the majority of experts are wrong and the aggregated response is correct because it preserves an isolated but crucial viewpoint.
- The framework is model-agnostic and needs no task-specific training, making it attractive for deployment and generalization.
- Figures are informative: Figure 2 offers a clear process diagram of the two-step workflow; Figure 3 summarizes win/draw/lose rates for informativeness/usefulness on ExpertQA.

## Summary Of Weaknesses
1) Heavy reliance on LLM-as-a-judge and potential circularity
- A large portion of evaluation depends on ChatGPT-based judges and classifiers. For TruthfulQA, “True percentage” is computed by a fine-tuned ChatGPT judge (Page 4, “Setups”), but the paper does not provide enough detail on that judge’s training data, calibration, inter-rater reliability, or whether it favors certain response styles typical of the proposed method. On ExpertQA, informativeness/usefulness are measured via ChatGPT comparisons (Figure 3). This raises circularity and bias concerns, particularly when the same family of model both generates and evaluates.
- Consequence: Claims of superiority may reflect evaluator bias rather than model-intrinsic improvements. The paper would be more convincing with stronger human annotation or independent, open-source evaluation pipelines for truthfulness and factuality.

2) Metric choices and reported zeros require scrutiny
- In Table 1, several toxicity scores are exactly 0.000 across different settings. With long-form generations across hundreds of prompts, exact zeros suggest either an overly coarse threshold (the 0.5 cutoff noted on Page 22), overly conservative generation settings, or evaluator brittleness. The paper should report confidence intervals, per-category breakdowns, or more robust toxicity measurements to support such strong claims, and clarify whether decoding and safety filters are identical across all systems.

3) Limited discussion of stronger multi-sample selection and multi-agent aggregation baselines
- While the paper compares to USC and Multi-agent Debate, there is a fast-growing body of best-of-n selection/aggregation methods and preference-guided multi-sample strategies that are directly comparable in spirit to the proposed “generate many, then choose/aggregate” approach. These omissions weaken the positioning and may inflate novelty.
- See “Potentially Missing Related Work” for concrete items that should be cited and, where feasible, compared.

4) Evaluation design choices can advantage the method
- The method explicitly optimizes for “facts agreed by more than half,” “conflicts and their resolution,” and “isolated viewpoints,” then asks to choose the “most factual and useful” answer. This mirrors the criteria used by the ChatGPT judge for ExpertQA comparisons (Appendix D). There is a risk of target leakage in evaluation: the decision rubric resembles the generation rubric, which could bias automatic evaluations.
- Recommend adding out-of-distribution evaluation criteria or human judgments that do not use the seven-subtask vocabulary.

5) Human evaluation is limited in scope
- Table 2 shows small-scale human ratings (100 samples each from three datasets per model) with coarse 1–3 scales. While agreement is decent (alpha ~0.7–0.8), this is not enough to ground the numerous automatic findings, particularly for truthfulness and factuality. The paper would benefit from more detailed human protocols, larger samples, and blind pairwise comparisons across methods.

6) Statistical reporting is thin and sometimes unclear
- Table 1 uses t-tests for significance on TruthfulQA. It is unclear how many samples were used for each test, whether assumptions of independence hold across prompts and stochastic generations, and whether multiple comparisons corrections are applied. For other metrics and ablations (Tables 3–4), significance is not reported.

7) Cost/latency and practicality are underexplored
- The framework adds several prompts per input. Table 11 reports token costs for two datasets, but there is little discussion of latency, throughput, or real-time constraints, which matter for deployment. A compute–quality trade-off study would make the engineering costs transparent.

8) Some exposition and consistency issues
- In Section 3.2, Subtask 5 is described as “Collecting S1, S3, S4 viewpoints,” but Page 4 says “S1, S2, and S4,” which seems inconsistent. Please fix.
- Minor typos: “ExertPrompting” instead of “ExpertPrompting” in Table 6; “longiness” on Page 8 likely means “lengthiness” or “length.”

Detailed comments referencing figures/tables:
- Figure 2: The two-panel workflow figure is effective, but it would help to visualize the exact prompts or a schematic of token budget per subtask to anticipate runtime cost.
- Figure 3: The stacked win/draw/lose bars show strong wins for the proposed method in both informativeness and usefulness. However, since the judge is ChatGPT, please add a sensitivity study with an independent, open-source judge or humans.
- Figure 4: Strong qualitative evidence that the aggregation preserves unique minority evidence that flips an answer from popular-but-wrong to correct. This directly supports the claim that S4 is important, aligning with the quantitative drop when skipping S4 in Table 3.
- Table 1: The main result table is central. Please include confidence intervals or bootstrap CIs for key columns, and clarify test set size per dataset after sampling. Also explain why BOLD toxicity is often exactly 0.000 for several methods with ChatGPT; this is surprising.
- Table 3: The ablation clearly shows why S1–S4 matter, but the absence of significance tests makes it hard to judge which differences are robust.
- Table 4: The “three experts” sweet spot is useful, but please add variance bars or multiple random seeds to show stability of the optimum at n=3.

## Potentially Missing Related Work
1) Gui et al., “BoNBoN Alignment for Large Language Models and the Sweetness of Best-of-n Sampling,” 2024 — Provides theory and practice for best-of-n sampling and selection, directly relevant to your Step 7 selection and the overall “generate-many-then-choose” paradigm. Should be discussed in Related Work (Section 7) and compared where selection is used, e.g., alongside USC in Table 1.

2) Jinnai et al., “Regularized Best-of-N Sampling with Minimum Bayes Risk Objective for Language Model Alignment,” 2025 — Introduces MBR-BoN, a decoding baseline aligned with preference signals. Add to Section 7 and, where possible, as a baseline or at least a discussion point regarding principled selection under alignment objectives.

3) Ye et al., “Preference-Guided Reflective Sampling for Aligning Language Models,” 2024 — A tree-based reflective multi-sample method that explicitly optimizes a preference model; compare to your seven-subtask aggregation in Sections 3.2 and 6.2, and cite near USC/MAD references.

4) Zhou et al., “Adaptive heterogeneous multi-agent debate for enhanced educational and factual reasoning in large language models,” 2025 — A heterogeneous role-based debate with a learned consensus module. Add to Section 7 to differentiate your single-turn aggregation from multi-round learned consensus.

5) Jeong et al., “Tool-MAD: A Multi-Agent Debate Framework for Fact Verification with Diverse Tool Augmentation and Adaptive Retrieval,” 2026 — Tool-augmented multi-agent aggregation for factual reliability. Add to Section 7; helps position your single-turn, tool-free approach versus multi-turn, tool-based systems.

6) “Debating to verify: A robust and explainable multi-agent LLM system for fact-checking,” 2026 — A training-free, debate-style consensus method focused on factuality and hallucination reduction. Should be discussed in Section 7, clarifying differences to your NGT-style aggregation.

7) Gupta et al., “CSMAD: Hallucination detection via multi-agent debate with NLI-verified contradictory statements,” 2026 — Hallucination reduction via agents that generate contradictory statements and NLI checks. Relevant to your conflict identification/resolution subtasks (S2–S3); cite and contrast in Section 3.2 and Section 7.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide stronger non-LLM-judge evaluations. For TruthfulQA, report exact-match true/false against gold with minimal LLM involvement, or add substantial human verification of truth labels for a representative subset. For ExpertQA, supplement ChatGPT judgments with blinded human pairwise comparisons.
- Report confidence intervals and significance across all major metrics and ablations. Clarify the number of prompts per experiment after sampling and whether multiple runs/seeds were used.
- Add at least one best-of-n alignment baseline (e.g., BoN/MBR-BoN or preference-guided reflective sampling) to Table 1 or discuss why this was infeasible. At minimum, include an analysis showing whether “n expert roles + your aggregation” outperforms “n vanilla samples + a principled selection rule.”
- Expand cost/latency analysis beyond token counts: wall-clock latency per query, number of LLM calls, and throughput under realistic settings. Provide a compute–quality curve showing how performance varies with n and with partial omission of subtasks.
- Clarify the ChatGPT judge details: training sources, partitioning from evaluation data, safeguards against overfitting, and inter-rater reliability vis-à-vis human annotators.

Typos and clarity:
- Section 3.2, Subtask 5: Page 4 says “collects viewpoints from S1, S2, and S4,” but earlier text says S1, S3, S4. Please correct.
- Table 6 header “ExertPrompting” should be “ExpertPrompting.”
- Page 8: “Are Informativeness and Usefulness the Results of Output Longiness?” → “length” or “lengthiness.”
- A few subject–verb agreement issues and duplicated words in captions; a careful proofreading pass would help.

Criteria that could change my evaluation:
- If you add a best-of-n alignment baseline and independent human evaluation that still shows clear improvements in truthfulness/factuality and informativeness/usefulness, I would raise my score.
- If you provide robust cost–performance analysis showing favorable trade-offs against strong multi-sample baselines, I would also raise my score.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: The methodology is clear and mostly sound. Main concerns lie in evaluation design and reliance on LLM judges, not in the core prompting framework.

## Excitement
3.5 Between interesting and exciting: The single-turn multi-expert aggregation via NGT-inspired subtasks is practical and broadly appealing, though somewhat close to best-of-n/ensemble ideas.

## Overall Assessment
3.5 Borderline Conference: Close to acceptable for the main conference but has notable weaknesses. The framework is well-articulated and empirically promising, with strong main-table gains and useful ablations. However, the reliance on LLM-based judges and missing comparisons to strong best-of-n style baselines limit the conclusiveness of the claims. With stronger human evaluations, independent metrics, and comparisons to more recent multi-sample selection methods, this could be a clear accept.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper acknowledges that equal weighting of experts may not match real-world expertise hierarchies; exploring weighted aggregation would be valuable.
- Societal impact is generally positive if truthfulness and safety improve, but the framework may also synthesize persuasive long-form content that is misinformative if the expert set is poorly generated. Discuss potential misuse cases and mitigation, such as constraining expert generation in sensitive domains.
- The toxicity evaluation should be stress-tested across more sensitive subcategories beyond two BOLD categories, and report uncertainty. Overreliance on one toxicity classifier risks under-detection.

## Ethical concerns
None, beyond the need for careful measurement of harmful outputs and transparent human evaluation. The human annotation protocol and compensation are described; this is good. The work uses public datasets with known ethical considerations.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: Prompts are provided, datasets are public, and model versions are named. Some dependence on proprietary APIs and opaque judging reduces full reproducibility. Clearer release of code and evaluation scripts would help.

## Datasets
1 No usable datasets submitted.

## Software
2 Documentary.: The prompts and procedures are helpful to replicate the study, but it is unclear if full code and evaluation scripts will be released; if released, this could rise to 3–4.