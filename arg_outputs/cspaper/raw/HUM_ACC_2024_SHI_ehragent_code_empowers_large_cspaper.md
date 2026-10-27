# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper presents EHRAgent, an LLM-based agent for few-shot complex tabular reasoning over electronic health records (EHRs). The agent generates, executes, and iteratively debugs code to answer natural-language clinical queries that may require multi-table joins and computations. Four components are emphasized: (1) medical information integration that distills query-specific knowledge from EHR metadata to assist schema linking; (2) long-term memory to retrieve successful past examples as few-shot demonstrations; (3) interactive coding with a Python-based executor and tool APIs; and (4) a “rubber duck” error tracing module that analyzes execution errors to guide debugging. Experiments on MIMIC-III, eICU, and TREQS show substantial gains in success rate over a range of planning and coding baselines, with ablations indicating each module’s contribution. Figures and case studies illustrate multi-turn debugging and planning behavior.

## Summary Of Strengths
- Methodological framing: Clear articulation of planning-as-code with an executor loop, enriched with domain-specific scaffolding (metadata-informed knowledge and long-term memory). The system diagram in Figure 3 is helpful to understand inputs, tool definitions, and the iterative planner–executor loop.
- Strong empirical results: Table 1 shows sizable improvements in success rate across three EHR datasets and multiple complexity tiers, with especially large margins on MIMIC-III and TREQS. Table 2 ablations on MIMIC-III carefully dissect the contributions of medical information, long-term memory, interactive coding, and error tracing.
- Robustness across LLMs: Table 6 indicates the approach still leads using a weaker backbone (GPT-3.5), suggesting some model-agnosticity.
- Insightful quantitative analysis: Figure 4 and Figure 5 examine performance vs. question complexity and number of demonstrations, revealing stable behavior of EHRAgent even as complexity rises or as demonstrations increase.
- Concrete case studies: Figures 7, 12–14 walk through real multi-turn error-driven refinements, illustrating how error tracing adds rationale rather than blind retries.
- Clarity and positioning: The paper is readable, connects to relevant agent, coding-interface, and medical QA literature, and provides implementation details and prompts in the appendix. Dataset statistics in Table 3 help contextualize the scale differences with general-domain text-to-SQL tasks.
- Figure-specific strength: Figure 2 effectively contrasts medical multi-tab reasoning vs. general-domain datasets by showing orders-of-magnitude increases in rows per table and more tables per question. This visual makes a compelling case for why generic text-to-SQL approaches may underperform and motivates the agentic coding interface.

## Summary Of Weaknesses
1) Baseline comparability and scope
   - Table 1 mixes natural-language planning baselines with code-generation baselines that use different programming languages (Table 5: Python vs. SQL). While the paper justifies Python as the primary interface (Appendix D) and includes an SQLInterpreter tool, it remains ambiguous how the SQL baselines were adapted to the same tools, error surfaces, and execution environment. For instance, DIN-SQL is designed for direct SQL generation; how much of its original self-correction was preserved when running against the provided schema? Please clarify prompt templates, schema exposure, and error feedback parity so that gains cannot be attributed to interface mismatch rather than planning quality. A controlled ablation where EHRAgent is forced to output SQL-only plans, or a fully parity-matched Python version of LLM2SQL/DIN-SQL, would strengthen the claim.
   - Reporting statistical significance or confidence intervals for success rates is missing. Given the number of queries, it would be useful to quantify whether deltas in Table 1 across strong baselines like Self-Debugging and AutoGen are statistically reliable.

2) Medical information integration lacks rigorous evaluation
   - The medical knowledge component B(q) is central: removing it drops success markedly (Table 2, e.g., “w/o medical information” lowers All from 58.97 to 33.66 on MIMIC-III). However, how often is B(q) correct vs. hallucinated? There is no quality analysis of B(q), nor safeguards when it is wrong. A small-scale annotation of schema-linking correctness, or a perturbation study with intentionally noisy B(q), would make the contribution more convincing.
   - The mechanism for limiting context length and selecting which parts of metadata and column descriptions get surfaced into B(q) is described at a high level; more concrete examples beyond Figure 8 would help quantify coverage and precision. 

3) Long-term memory retrieval and evaluation protocol
   - Equation (1) uses negative Levenshtein distance to select examples. This is a very simple lexical proxy. Stronger embedding-based retrieval (e.g., domain-tuned encoders) might perform better and would be a reasonable baseline, especially given medical terminology variance. Figure 9 is a helpful qualitative; a quantitative comparison of retrieval strategies is missing.
   - The role of memory content on test distribution should be carefully controlled. Table 8 explores “LTM w/ Completion,” but there is still a risk of reinforcing suboptimal behaviors or leaking highly similar queries that inflate performance. Please clarify how you prevented near-duplicates or templatic overlaps between stored successes and test questions, especially for TREQS with templates.

4) Debugging via error tracing: design clarity and overhead
   - Section 3.4 indicates error parsing and a separate “rubber duck” LLM that hypothesizes root causes. The paper would benefit from a clearer breakdown of: which model is used for the rubber duck, how error traces are normalized, and how you prevent spurious hypotheses from sending the agent on long detours. Table 2 shows sizable drops without this component, but latencies and additional cost per turn are not reported beyond the brief cost averages in F.3. A latency–accuracy and cost–accuracy Pareto (or at least macro averages of iterations per query per dataset) would make the contribution more actionable for clinical deployments.
   - In Figure 12 and Figure 14, the explanations often boil down to case sensitivity or column misnaming. These are realistic but relatively shallow categories; a taxonomy of error depth versus fix complexity would be informative. Figure 6 starts this, but deeper analysis per error category and its fix success would help.

5) Realism and safety of the evaluation setting
   - The executor and tools are curated (Appendix B), and data preprocessing filtered out unexecutable or empty-result SQL (Appendix E.2). Please report how many items were filtered from each dataset and whether filtering biases the distribution of tasks toward ones favorable to the tool API set.
   - The completion rate (CR) metric counts “executable plans,” which is useful for agentic completeness. However, as you note, higher CR does not imply clinical safety. In Table 1 and Figure 4–5, please be careful not to conflate CR with “goodness,” and consider adding a stricter “safe failure” rate that rewards refusing to answer when code is likely wrong or when the plan contradicts constraints.
   - The Python-first choice is well-argued (Appendix D), yet scalability remains an issue on very large tables. The discussion acknowledges this, but a quantitative latency comparison with an SQL-first variant over a subset of heavy queries would ground the claim.

Figure- and Table-specific critique and interpretation:
- Figure 3: The pipeline makes clear how metadata, tool specs, few-shot examples, and B(q) feed into code generation. It would help to overlay where the rubber-duck LLM sits relative to the main agent to make orchestration explicit.
- Figure 4: Success and completion both degrade with complexity across all methods, but EHRAgent’s curves are consistently above baselines, particularly when the number of solution columns increases. This figure is central evidence that the approach scales better with compositional difficulty; consider adding the number of queries per bin to judge variance.
- Figure 5: The downward trend of AutoGen with more shots is interesting. A companion plot with prompt token lengths and step counts would support the context-length explanation.
- Table 1: The improvements are large and consistent; adding standard deviations over multiple runs with different few-shot seeds would be reassuring, despite temperature=0.
- Table 2: The jump when adding interactive coding is especially large (All: 24.55 to 58.97 SR). Since “w/o interactive coding” also changes the planning language from code to natural language, this ablation conflates two factors. A purer ablation where code planning remains but the executor loop is disabled would isolate the loop’s effect.

## Potentially Missing Related Work
1) Qiao et al., “EHR-Complex: Benchmarking Medical Agents for Complex Clinical Reasoning,” 2026 — introduces an agentic benchmark over multi-table EHRs with executable evaluation. Directly relevant to your problem setting; should be discussed in Section 5 and considered in future comparisons.
2) Wu et al., “EHRFlow: A Large Language Model-Driven Iterative Multi-Agent Electronic Health Record Data Analysis Workflow,” 2024 — multi-agent pipeline with local code execution on EHR tables. Compare architectures in Section 5 and discuss in contrast to your single-agent planner–executor in Section 3.
3) Xu et al., “MedAssist: LLM-Empowered Medical Assistant for Assisting the Scrutinization and Comprehension of Electronic Health Records,” 2025 — integrates code execution and medical knowledge for EHR comprehension; useful as a downstream application context to be mentioned in Introduction/Conclusion.
4) Klang et al., “Large language models are poor clinical administrators: An evaluation of structured queries in real-world electronic health records,” 2026 — provides a cautionary empirical evaluation on structured EHR querying, including code generation. Cite in Section 1/5 to motivate the need for robust agentic planning and debugging.
5) Yang et al., “EHRMaster: Reliable EHR Task Execution,” 2026 — code-augmented planning with schema-aligned execution and pandas/SQL constraints. Compare in Section 5 and, if feasible, add to Table 1 as a reliability-focused baseline.
6) Tang et al., “MedAgentsBench: Benchmarking Thinking Models and Agent Frameworks for Complex Medical Reasoning,” 2025 — broader clinical multi-step reasoning benchmark; cite in Section 4.1 or Related Work as an alternative evaluation scope.
7) Li et al., “Exploring LLM Multi-Agents for ICD Coding,” 2024 — while task is different, it is an agentic decomposition over EHR-derived data. Mention in Section 5 to position your single-agent vs multi-agent choices.
8) Reinforcement Learning for Tool-Calling Agents in FHIR-based EHRs, 2026 — RL for tool selection over structured EHRs. Discuss as an alternative training paradigm in Section 6 or Limitations/Future Work.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Baseline parity: Provide more detail on prompts, schema exposure, and the exact error feedback seen by SQL-based baselines. Consider adding a parity-check experiment where EHRAgent is forced to output SQL-only or where DIN-SQL is allowed to use the same error-rich executor loop.
- B(q) validation: Add a small labeled study quantifying the correctness of schema linking and table/column suggestions in the distilled knowledge, and a robustness test with noisy knowledge to show the agent’s tolerance to hallucinations.
- Retrieval variants: Compare Levenshtein-based retrieval with embedding-based retrieval for long-term memory, and report effects on both SR and CR.
- Loop and cost metrics: Report average number of iterations, average token usage, and wall-clock latency per query by dataset and complexity level. A cost–accuracy plot would be helpful.
- Ablation refinement: Keep the code interface but disable executor feedback to isolate the value of the loop itself versus code vs. NL planning.
- Evaluation transparency: In Appendix E.2, quantify how many items were filtered, per dataset. Consider adding a “safe failure” metric or refusal rate to complement CR for clinical applicability.

Typos and minor issues:
- Page 15, “Number of Language” header could be “Primary language.” 
- Several code snippets in Figures 10–14 include minor formatting errors (e.g., mismatched variable names like in_time vs. INTIME; quoting artifacts). Consider sanitizing for readability.
- Occasionally “inexcusable” is used where “inexecutable” seems intended (e.g., Page 7 bottom for error categories).

Criteria that could increase my score:
- Add the parity-checked baseline or the SQL-only EHRAgent variant, plus statistical significance tests on Table 1.
- Provide B(q) quality analysis and an embedding-based retrieval comparison.
- Add latency/cost/iteration analyses and a clearer breakdown of the rubber-duck module design and overhead.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
4 Strong: This study provides sufficient support for all of its claims. Some extra experiments could be nice, but not essential.

## Excitement
3.5 Between interesting and exciting: I would mention this paper to others and/or make an effort to attend its presentation in a conference.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The agentic design for EHR tabular reasoning is well-motivated, with clear empirical gains, solid ablations, and informative figures, though baseline parity, knowledge validation, retrieval strength, and deployment metrics deserve further work.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper includes a limitations section acknowledging added execution calls, privacy, and clinical applicability. I appreciate the explicit note that CR is not necessarily better in clinical settings.
- Additional points to consider:
  - Safety and reliability: erroneous code execution may silently produce plausible wrong answers. A “safe failure” or abstention mechanism would be important before deployment.
  - Bias and coverage: metadata-driven B(q) could amplify biases if metadata are incomplete or skewed. An audit of which patient subgroups appear in successful vs. failed queries could reveal disparities.
  - Dual use: the agent could be repurposed to extract sensitive information or conduct fishing expeditions on EHRs; discuss stricter access controls, auditing, and differential privacy considerations.
  - Internationalization: the approach likely depends on English-language metadata and specific schema conventions; discuss multilingual or FHIR-based portability more concretely.

## Ethical concerns
None beyond what is already noted and the general risks of operating over sensitive EHR data. The privacy compliance statement is a good step. For completeness, consider including an explicit discussion of audit logging, role-based access, and oversight mechanisms for clinical settings.

## Needs Ethics Review
No

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method. The use of a closed model is noted, but prompts, datasets, and tools are well described.

## Datasets
2 Documentary: The paper leverages established public datasets; no new dataset is introduced. The dataset overview is useful for replication.

## Software
4 Useful.: I would recommend the new software to other researchers or developers for their ongoing work. The described tool APIs and prompts appear reusable, and the agent is a solid baseline for structured EHR reasoning.