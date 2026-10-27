# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces SUPER, a benchmark to evaluate language-model agents on the realistic task of setting up and executing experiments from research code repositories. The authors curate 42 research repositories and have experts produce full, deterministic, end-to-end solutions on CPU-limited, low-compute settings; from these, they extract 152 “masked” scenarios that target specific obstacles such as dependency resolution, dataset configuration, hyper-parameter changes, CPU-only adaption, and bug fixing. Evaluation includes strict outcome accuracy (matching gold outputs within 1e-2) and a softer landmark-based metric that credits partial progress. Baseline agents (ReAct, SWE-Agent, an improved ReAct-SUPER, and a Reflexion retry variant) are evaluated with GPT-4o, GPT-4-turbo, and Mixtral-8x22B, showing that even the best setup solves only around one third of scenarios and very few end-to-end tasks. The paper argues that SUPER fills a gap between code-generation or simple ML-agent benchmarks and the harder challenge of running real research repositories.

## Summary Of Strengths
- Clear and much-needed task framing. The problem of “set up and run research repositories” is important for the NLP/ML community, and the benchmark explicitly targets pain points that practitioners regularly face.
- Thoughtful dataset construction with expert gold solutions. The paper describes a careful process to collect deterministic, reproducible solutions on CPU-only constraints, with recorded dependencies and commit hashes. The masking strategy yields a spectrum of realistic subproblems.
- Evaluation design is well-motivated and practical. Outcome-based accuracy avoids over-reliance on code similarity, while the landmark metric provides a more graded signal for long-horizon tasks.
- Strong, transparent baselines and analyses. The results in Table 3 and Table 4 are informative, and the error analysis is candid. Table 6 ablates key agent features, and Table 5 demonstrates that naive retry with Reflexion has limited value here.
- Figures effectively communicate the benchmark design. Figure 2 and Figure 3 make the scenario extraction pipeline concrete, and Figure 1 nicely illustrates the nature of real obstacles (e.g., environment setup, multi-file edits, dependency pinning).
- Useful characterization of scenario categories (Table 2). Breaking down categories and average LOC clarifies what the benchmark actually stresses and helps future research target bottlenecks.

## Summary Of Weaknesses
1) External validity and selection bias. The benchmark focuses on “low-profile” repositories (median 11 stars; Table 1 and Appendix A) and constrains tasks to CPU and ≤10 minutes. While the authors argue this does not make the tasks easier, this still biases the challenge toward certain repository types and small models. It remains unclear how well results generalize to medium- to high-profile repos with maintained tooling, GPU-only codepaths, or longer training/eval loops. A stronger discussion on generalization, with at least a small-sample probe on more popular repos, would help.

2) Manual scenario extraction may bake in annotator priors. The masked-block selection (Section 3.3; Figure 3) is manual. Although the procedure is described, there is no check on inter-annotator consistency or potential bias in what kinds of steps were masked as “goals.” This matters because agent performance will depend heavily on which steps are pre-executed versus masked. An audit or agreement measure, or dual-annotator spot checks, would strengthen confidence.

3) Landmark metric robustness and potential gaming. Landmarks are surface string patterns from outputs (Section 3.4), which could, in principle, be accidentally or adversarially triggered by printing matching strings without truly completing the step. The paper claims this is “unlikely by design,” but does not show guardrails. A small experiment that tests for false positives, or a provenance-aware landmarking (e.g., regex tied to stdout context of a verified process, or hash checks on generated artifacts) would improve validity.

4) Limited coverage of baselines and open-source models. Only Mixtral-8x22B is tried for open-source and entirely fails (Table 3). Given the importance of open baselines for the community, including more recent strong open models and agent frameworks would be valuable. Moreover, the SWE-Agent implementation is adapted; a discussion of parity with the original toolkit’s editing affordances and UI assumptions would clarify whether the weaker performance is due to mismatch with the environment rather than agent design.

5) Environment dependence and portability. The environment is a custom Jupyter-in-Modal sandbox with special edit tooling and truncation heuristics (Section 4.1 and Appendix C/D). It is not fully clear to what extent results would transfer to other execution harnesses or real Colab/VSCode flows. For a benchmark intended to measure broadly useful capabilities, more details on portability, and whether the exact harness will be released with a reference runner, are essential.

6) Limited statistical analysis for scenario-level variability. While Table 2 reports category distributions, there is no analysis connecting scenario length/LOC, number of files touched, or extent of multi-file edits to success likelihood. Such analysis would help isolate which structural properties most impede agents.

7) Ambiguity in “accuracy” for multi-value answers. Section 3.4 notes multi-valued answers are compared value-wise, but it is not entirely clear how missing or extra values are handled, and whether minor formatting differences beyond the 1e-2 numerical tolerance are penalized. A precise specification, ideally with examples, would avoid evaluation ambiguity.

8) Minimal cross-benchmark positioning beyond Table 1. Table 1 is appreciated, but some directly relevant, recent efforts on research reproducibility agents and codebase deployment are not discussed, which weakens the positioning and may understate prior art.

9) Results interpretation needs tighter linkage to figures/tables. The core claim that agents are better at well-specified failures than repository comprehension is compelling; however, it would be stronger to ground this more concretely in per-category numbers embedded in the main paper (e.g., providing a short per-category results table, not just text in Section 4.3).

10) Small but nontrivial reproducibility gaps. The paper mentions determinism up to 1e-2 and uses fixed commits and dependency lists, but it is not entirely clear whether intermediate artifacts (e.g., cached downloads, data preprocessing scripts or mirrors) are archived to ensure longevity. For a benchmark likely to be run over time, stronger guarantees would help.

Figure- and table-specific comments:
- Figure 2 convincingly clarifies the three-step pipeline (task writing, expert solutions, scenario extraction). It supports the central claim that SUPER evaluates both end-to-end and masked sub-tasks derived from real solutions. Still, the figure could profit from including quantitative labels on how many scenarios per step to give the reader a sense of yield.
- Figure 3 concretely illustrates the masking scheme. However, this figure also makes clear that goal selection is somewhat subjective. A small study where different annotators produce alternative masks for the same solution would quantify potential variance.
- Table 3 is central to the paper. It shows that ReAct-SUPER with GPT-4o attains 34.9% accuracy and 64.7% landmark rate, while SWE-Agent is notably lower. The very large gap between landmark and accuracy suggests many near-miss behaviors; I recommend adding a small failure taxonomy tied to this table, e.g., percent of runs that reached “training started” but missed “training completed.”
- Table 4 (E2E) reinforces the difficulty of full tasks, with accuracies dropping to single digits. This supports the authors’ argument that scenario-level evaluation is a more usable hill-climbing signal.
- Table 5 shows that Reflexion increases submission rate and yields a modest accuracy lift to 38.3%. This is a useful negative result tempering enthusiasm for “just retry.” A breakdown by category here would be helpful to see whether reflection helps more on dependency/config issues than on repo comprehension.
- Table 6 ablates the edit tool and progress-line filtering and shows meaningful improvements on landmarks. This figures into the agent design claim that affordances matter. It would be helpful to include average token usage per scenario with and without these features to further support the truncation argument.

## Potentially Missing Related Work
1) Siegel et al., “CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark,” 2024 — Directly tackles agent-based computational reproducibility from real scientific papers. It should be compared in Section 2 and discussed alongside Table 1, clarifying differences in repository scope, evaluation harness, and success criteria.

2) Chen et al., “ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery,” 2024 — Evaluates agents on executing scientific data-analysis tasks from real papers. Relevant to Section 2; should be contrasted with SUPER’s repository-setup focus versus program synthesis/data-analysis emphasis.

3) Jain et al., “R2E: Turning any GitHub Repository into a Programming Agent Environment,” 2024 — Presents a method to convert arbitrary repositories into agent-test environments. It is relevant to Section 3 for possible automation of scenario generation and to Section 5 as a path toward scaling SUPER.

4) Xiao et al., “CSR-Bench: Benchmarking LLM Agents in Deployment of Computer Science Research Repositories,” 2025 — Very close in goal to SUPER, emphasizing repository deployment and environment configuration. Should be included in Section 2 and contrasted in Table 1–style taxonomy, with a short empirical or conceptual comparison if feasible.

5) Zhang et al., “BuildBench: Benchmarking LLM Agents on Compiling Real-World Open-Source Software,” 2025 — Focuses on building/compiling complex software. Discuss in Section 2 to position SUPER’s ML/NLP repo execution against more general OSS build challenges.

6) Miao et al., “RECODE-H: A Benchmark for Research Code Development with Interactive Human Feedback,” 2025 — Complements SUPER by stressing feedback-driven research code development. Add to Section 2 and briefly discuss how interactive feedback loops might change outcomes on SUPER.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Strengthen landmark validity. Add safeguards so landmarks cannot be satisfied by printing strings. For example, tie patterns to subprocess provenance, check generated file hashes, or require hitting multiple corroborative events (e.g., log + artifact + exit code). A small “false positive” stress test would be convincing.
- Add more open-source baselines. Include at least two additional strong open models and an open-source agent framework tuned for repository-level tasks. Reporting token usage and failure modes for each will improve community usefulness.
- Quantify annotator effects in masking. For a subset of tasks, have two annotators independently define masked scenarios, report overlap (e.g., Jaccard over masked code blocks) and performance variance. This would address subjectivity in Figure 3’s process.
- Expand structural analyses. Provide a results table breaking down accuracy/landmarks by scenario properties: number of files edited, gold LOC edited, presence of multi-file edits, and output length. Link the observation to the claim in Section 4.3 that “repository comprehension” is the hardest piece.
- Portability and long-term reproducibility. Document a reference runner and release the environment scripts. Clarify how datasets, models, and dependencies are mirrored to avoid bit-rot. If possible, include a CI script that re-validates gold notebooks monthly.
- Minor presentation fixes:
  - Table 1: clarify “partially observed environment” with one sentence of what is hidden or restricted in SUPER’s setup.
  - Section 3.4: define precisely how multi-valued answers are matched, including handling of missing/extra values and formatting edge cases.
  - Figure 2: add counts for tasks → scenarios to quantify pipeline yield.

Typos/format:
- Section 4.1: “execute and command” should be “execute and edit command.”
- Table 3 caption: consider stating “Acc., Subm., Landm. are percentages” explicitly.
- Appendix C prompt examples: minor punctuation/quoting inconsistencies; ensure JSON examples are valid.

Criteria for a higher score in rebuttal:
- Provide evidence of landmark robustness (experiment or implementation detail).
- Add at least a small open-source baseline expansion and parity discussion for SWE-Agent in this environment.
- Include a brief dual-annotator or audit check on masking to quantify subjectivity.
- Release a reference runner and clarify long-term asset archiving.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
4 Strong: This study provides sufficient support for all of its claims. Some extra experiments could be nice, but not essential.

## Excitement
3.5 Between interesting and exciting.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The benchmark is well-motivated and carefully built; results are informative. I would like to see stronger landmark validation, more open-source baselines, and a short analysis of annotation subjectivity, but these feel addressable.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper discusses size limitations and single-language focus. Additional limitations worth noting:
- Potential overfitting to the particular execution harness or the prompt format used by the agents.
- Risk that users over-trust agents to reproduce research without human oversight, which could propagate errors.
- English-only and Python-only scope underrepresents other languages and ecosystems where reproducibility challenges also matter.
- Bias in selecting low-star repositories may over-emphasize poor documentation scenarios compared to mainstream research repos. Expanding scope could balance this.
Potential positive impact is high if this benchmark drives more robust research-execution agents and improves reproducibility practices.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.

## Datasets
4 Useful: I would recommend the new datasets to other researchers or developers for their ongoing work.

## Software
4 Useful: I would recommend the new software to other researchers or developers for their ongoing work.