# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies test-time “diverse inference” for ARC (Abstraction and Reasoning Corpus) puzzles. Instead of relying on a single model or pipeline, the authors aggregate outputs from 16 heterogeneous models and methods, counting a task as solved if any method produces a program that passes ARC’s training-pair verifier. Methods include best-of-N sampling, self-consistency, MCTS, plan search, mixture-of-agents, BARC, and MARC. Results on the 400 ARC public evaluation tasks indicate that simple aggregation boosts solve rate from 53% to 69.5% without reasoning LLMs and from 91.5% to 93.75% with them, exceeding average human performance and solving some puzzles previously missed by humans and by a strong reasoning model. The paper formalizes supervised/RL training views (Equations 1–9), describes an OR-aggregation scheme for verifiable problems, and presents case studies and ablations on puzzles where o3-high or humans fail.

## Summary Of Strengths
- Clear central idea with measurable gains under a verifiable setting. Because ARC solutions can be checked by execution on training pairs, aggregating independent pipelines is a principled way to expand coverage.
- Useful empirical contribution: Figure 2 and Table 3 systematically compare a variety of solvers on the 400-task public evaluation split. The reported “max” aggregation to 93.75% is competitive and informative for practitioners assembling ARC solvers.
- Concrete, interpretable qualitative demonstrations: Figures 3–6 (o3-high failure cases) and Figures 7–10 (human failure cases) show puzzles where other methods succeed, illustrating complementarity. In Figure 3 (task 52fd389e) and Figure 5 (aa4ec2a5), the visual grids make it evident that rule-centric pipelines like BARC/MARC can succeed where general reasoning fails.
- The paper frames “diverse inference” as a test-time resource alongside data/model scaling, and identifies a plausible empirical law relating performance to the number of distinct methods when verification is near-perfect (Section 2.3).
- Aggregation methodology is simple and replicable in principle, and the authors state that drivers and modular implementations will be released, which could be valuable to the community.

## Summary Of Weaknesses
1) Limited novelty in the core mechanism and insufficient methodological disambiguation
- The primary technique is a logical OR over correctness indicators (Section 2.3). While effective, this is conceptually straightforward and not clearly distinguished from standard ensembles, mixture-of-experts/agents, or prior ARC solver aggregations. The paper would benefit from a more formal analysis of complementarity and diversity (e.g., solver correlation matrices or marginal contribution curves) rather than mainly reporting the end-point “max”.
- The claim of a “third empirical scaling law” is not substantiated with a quantitative scaling study. There is no figure/table showing accuracy as a function of K diverse methods with confidence intervals or cost normalization. A simple curve plotting solve rate against the number of aggregated methods, randomized orderings, and confidence bands is needed to make this claim credible.

2) Evaluation protocol risks and lack of proper held-out development
- The 400 “public evaluation” tasks are commonly used for reporting, but with 16 methods, many prompts, hyperparameters, and post-hoc design choices, there is a non-trivial risk of implicit tuning on this same set. The paper does not demonstrate any safeguards such as a separate development split, cross-validated design selection, or pre-registered configurations. This undermines the strength of the 93.75% claim.
- Because the verifier checks only training pairs, some synthesized programs can overfit. The paper acknowledges this in Limitations but does not quantify false-positive rates. For example, what fraction of solutions that pass training pairs fail under slight perturbations or leave-one-out MARC-style checks? A falsification study would strengthen claims.

3) Mathematical correctness issue in the RL gradient for reasoning models
- Equation 9 appears incorrect. Starting from Equation 8 and policy-gradient logic, the REINFORCE gradient for joint sampling (z, y) should weight the sum of log-probability terms by the reward, i.e., proportional to r(x, z, y) [∇ log pθ(z|x) + ∇ log pθ(y|x, z)]. In Eq. 9, the second term becomes “+ log πθ(ŷ|x, ẑ)” inside the expectation without the gradient or reward multiplier. This looks like a typographical or derivational error and needs correction. As the RL exposition is used to motivate search and test-time simulations, accuracy here is important.

4) Ambiguity and missing details in methods and models
- Table 3 lists many cryptic abbreviations (e.g., “g1.5, g2.0, c3.5-ha, c3-ha, c-son, dev3/dev1, ol- variants, ollow/olmed/olhigh”), but the paper never exhaustively defines them in the main text. Readers cannot tell which base model each refers to, whether they are closed- or open-weight, what prompting or sampling was used, or how much compute each consumed. Figure 2 uses these same labels. This notably harms reproducibility and interpretability.
- Table 1 and Table 2 mark success/failure across methods for a handful of tasks, but they do not show confidence intervals or attempt-time/compute normalization. Average run times in Table 1 are reported in seconds for some methods, but compute hardware, concurrency, and sampling budgets are not specified in the main text, making cross-method comparisons opaque.

5) Incomplete positioning with respect to directly related ARC ensemble and multi-agent literature
- The paper cites BARC, MARC, self-consistency, MoA, and plan search, but several closely related ARC-focused ensemble/multi-agent works and object-based/1D-ARC analyses are not discussed. These missing references matter because they study the same question of combining heterogeneous solvers or emphasize representational choices that could drive complementarity. See “Potentially Missing Related Work”.

6) Over-claiming “beyond humans” without deeper qualitative error/process analysis
- While Figure 1 and Figure 2 present overall solve rates and claims such as “80% of puzzles that 948 humans collectively fail,” there is little analysis of why these puzzles are solved by the aggregated system and what types of abstractions are captured. For example, are these predominantly geometric filling, symmetry, or object-relational rules? A taxonomy or process-centric analysis (e.g., solution DSL primitives or plan categories) would make the “generalization” story more meaningful.
- The work does not measure robustness under perturbations or tiny specification changes, which is important for claims of “generalizable reasoning”.

7) Cost/benefit and ablations on sources of gain are underdeveloped
- Figure 2 highlights individual methods and “max,” but there is no systematic Shapley-style or leave-one-solver-out ablation to quantify each solver’s marginal contribution to the final 93.75%. For instance, what is the delta if MARC is removed, or if MoA is replaced by BoN with equal compute?
- Similarly, there is no analysis normalizing for test-time compute. If a single strong reasoning model sampled longer could close part of the gap, the practical value of the 16-way aggregation would look different.

8) ARC-specific concerns
- The paper evaluates only on the fixed 400 public evaluation tasks, not on private sets or procedurally generated ARC-style tasks. The “diversity scaling law” and complementary-coverage claims might be particular to this split. The absence of robustness studies on variants like 1D-ARC or ARC-style generators weakens generalization claims.

9) Figure- and table-specific issues and interpretations
- Figure 1: The four annotated claims (①–④) are visually clear, but the y-axis is unlabeled in the cropped rendering; in the manuscript text it is described as success rate. To firmly support claim ③, please show the exact five tasks humans failed and which specific methods solved each, perhaps as an inset bar chart.
- Figure 2: Good comparative visualization, but the legend and categories (“Gamma,” “Claude,” “Deepseek,” etc.) do not map 1:1 to the abbreviations used on the x-axis. Add a table legend mapping each bar to a concrete model/method and version.
- Tables 1–2: These ablations are helpful examples. However, Table 1 reports average times but Table 2 does not. Also, methods are inconsistent across the two tables; a unified set with clear definitions would improve clarity.
- Table 3: Central to the paper’s headline number. It needs explicit definitions of all abbreviations, sampling budgets, and prompts. Without this, the table is not actionable.

10) Agentic automation and computation graph claims are underspecified
- The abstract mentions automating MARC in an agentic framework using a computation graph. The body, however, does not provide a diagram, pseudo-code, or concrete description of this graph. A figure akin to an architecture diagram would clarify the agent composition, the control flow, and where verification gates are placed.

## Potentially Missing Related Work
1) Tan et al., “LLM as a System of Multiple Expert Agents: An Approach to solve the ARC Challenge,” 2023 — Directly tackles ARC with multiple expert agents and environment feedback, closely aligned with the paper’s ensemble-of-diverse-solvers idea. Should be discussed in Section 1.1 and compared empirically where possible; at minimum, cite near Figure 2 and Table 3 as an ensemble baseline.

2) Xu et al., “LLMs and the Abstraction and Reasoning Corpus: Successes, Failures, and the Importance of Object-based Representations,” 2023 — Demonstrates representational gains via object-based/1D-ARC; provides diagnostics for LLMs on ARC. Add to Related Work (Section 1.1) and use its error taxonomy to analyze what categories benefit most from diversity.

3) Lei et al., “From Reasoning to Generalization: Knowledge-Augmented LLMs for ARC Benchmark,” 2025 — Proposes KAAR with hierarchical priors and planning-aided code generation, reports strong results on ARC public evaluation. Should be compared in Section 3; if direct numbers are not comparable due to protocol differences, discuss design contrasts and potential complementarities in the aggregation.

4) Bober-Irizar et al., “Neural networks for abstraction and reasoning,” 2024 — Introduces PeARL and discusses ensembles of heterogeneous ARC solvers. Add to Related Work and discuss its ensemble findings vis-à-vis Figure 2’s diversity gains.

5) Mesnage et al., “Evaluating … with the One-Dimensional ARC,” 2025 — Uses 1D-ARC with program-execution verification. Add as related methodology supporting verifiable evaluation and consider adding 1D-ARC as a robustness check for the “diversity scaling” claim.

6) Lee et al., “Reasoning Abilities of LLMs: In-Depth Analysis on ARC,” 2025 — Process-centric evaluation using a Language of Thought framework. Incorporate into Section 3 as a lens for analyzing the kinds of reasoning improved by aggregation, beyond headline accuracy.

## Comments Suggestions And Typos
Actionable suggestions:
- Correct Equation 9 and provide a brief derivation to avoid confusion: the reward should multiply the gradient of both rationale and answer log-likelihoods.
- Define every abbreviation used in Figures 2 and Tables 1–3 in the main text, including model families, parameter sizes, API variants, prompts, sampling budgets, and verification settings. A single mapping table would help.
- Provide a real scaling analysis for the “diversity law”: plot solve rate as a function of the number of aggregated methods K, averaged over many random solver orderings; include error bands and cost-normalized variants (e.g., fixed total test-time tokens).
- Add leave-one-solver-out ablations to quantify marginal contributions to the 93.75%. Report the top-5 contributors and the overlap matrix across solvers (pairwise Jaccard of solved-task sets). A small barplot next to Figure 2 would be ideal.
- Quantify verifier imperfections: show how often solutions that pass training pairs fail under leave-one-out or simple augmentations; include a small suite of adversarial or perturbed checks to estimate false-positive rates.
- Clarify evaluation protocol to mitigate tuning-on-test: either show that all design choices were locked before running on the 400 eval set or add a held-out dev split (e.g., from public training tasks or generated tasks) for method selection.
- Include compute details in the main text: hardware, parallelism, wall-clock per method, and token budgets. Normalize some comparisons by compute.
- Expand the “agentic computation graph” claim with a concrete diagram and algorithmic description. If available, include a minimal open-source release that replicates the aggregation and runs at least a subset of methods.
- Add a qualitative error/process analysis of the five human-failed tasks solved by the system (Figure 7–9). Describe the kind of abstraction each solving method used, not only that it succeeded.
- Minor typos/clarity:
  - Page 1, Abstract: “increase the success rate … from 91.5% to 93.75% with them which exceeds …” → add comma after “with them,” or rephrase.
  - Page 5, Table 2 header lists “Task ID 8719d442,” while Figure 7 shows 8719f442; verify consistency.
  - Figures 8–10 captions: a8610ef7 vs a0610cf7 in Table 2; check IDs.
  - Page 7–8: ensure consistent naming “o3-high” vs “o3 high compute”.

What could change my score:
- A corrected Eq. 9; a thorough mapping/definition of all methods and compute; a genuine diversity-scaling curve with cost normalization and leave-one-out ablations; quantification of verifier false positives; and a clearer, reproducible aggregation toolkit. If these are addressed convincingly, I would raise to Borderline Conference (3.5) or Conference (4.0) depending on the strength of the analysis.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
3.0 Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there’s time.

## Overall Assessment
3 Findings: This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility.
Justification: The empirical message that OR-aggregating diverse ARC solvers improves solve rates under verification is useful and practically relevant. However, novelty is limited, Eq. 9 likely contains an error, method definitions are underspecified, the “diversity scaling law” is unsubstantiated by proper analysis, and evaluation protocol and compute normalization need tightening. With the recommended revisions, this could rise to the main conference.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section noting compute costs, closed-model reliance, and potential verifier overfitting. I recommend expanding societal impact to cover:
- Risks of overstating “human-level” claims on a fixed benchmark without robustness testing.
- Dual-use considerations for automated program synthesis and search, including generation of exploit scripts, and proposed mitigations like rate-limiting or sandboxing.
- Inclusivity considerations: ARC is language-free; discuss to what extent findings generalize to multilingual or low-resource NLP tasks when using verification.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.
Rationale: The aggregation idea is simple and ARC is public, but method abbreviations, prompts, and compute details are not fully specified in the main text; reliance on closed APIs further complicates exact replication.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: Someone might find the new software useful for their work.