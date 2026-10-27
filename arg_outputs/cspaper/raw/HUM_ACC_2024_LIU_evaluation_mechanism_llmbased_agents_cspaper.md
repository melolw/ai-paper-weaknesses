# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes an evaluation mechanism for LLM-based agents that manipulate API-based tools. The authors decompose “tool use” into seven decision behaviors, design eight evaluation tasks aligned to this schema, and provide a toolset sourced largely from a real API hub (RapidAPI) together with five types of user instructions intended to reflect realistic requests. They then evaluate several generic agents (GPT-3.5/4 and Qwen 7B/14B/72B) across these tasks, reporting per-capability results and observations about error modes, API documentation quality, and planning challenges.

## Summary Of Strengths
- Clear problem focus and scope: evaluating API-manipulating agents, separated from UI-based environments, with emphasis on realistic API designs and documentation.
- Thoughtful capability decomposition: the seven decision behaviors in Figure 2 offer a structured diagnostic view beyond end-to-end success. The explicit inclusion of “responding with intrinsic knowledge” is a good sanity check against over-fitting to tools.
- Realism in toolset construction: 66 APIs across 27 tools, mostly wrapped from RapidAPI, with explicit accommodation of inter-API dependencies and multi-API tools. The dependency example in Appendix A is concrete and helpful.
- The instruction taxonomy (Types I–V) is simple yet covers common user situations, including missing-parameter scenarios and higher-level planning tasks; Table 1 maps instruction types to evaluation tasks clearly.
- Useful empirical takeaways: Figure 4 and Table 5 highlight capability gaps among strong models, especially in dependency-aware planning (Task 7), tool selection (Task 2), and clarification requests (Task 3). Figure 5’s precision/recall/F1 breakdown for Task 1 surfaces distinct tendencies (e.g., GPT‑3.5’s conservativeness vs Qwen-7B’s over-triggering).
- Resource value: Tables 2 and 3 provide dataset size and per-task counts; the toolset organization in Table 4 shows coverage across daily life, travel, and image processing, which supports combinatorial tasks.

## Summary Of Weaknesses
1) Evaluation protocol relies heavily on LLM-as-a-judge without sufficient specification or validation.
   - Several tasks are judged by “mixing rules and GPT‑4 usage,” but the exact prompts, calibration, and inter-annotator checks are not described. In Task 5 (“relatedness” and “answer quality”) and Task 6 (“passing rate” and “precise interpretation”), criteria are underspecified. This can bias results and obscure reproducibility or fairness, especially since GPT‑4 is both a system under test and a grader.
   - Consequence: conclusions about relative model performance may be sensitive to the judge model and prompts. A small human evaluation sample or cross-judge agreement analysis would strengthen credibility.

2) Coverage and scale of complex tasks are limited; single-run evaluation with no variance.
   - Type‑V (high-level) instructions are only 50 instances (Table 2), which constrains conclusions about planning for realistic, multi-step tasks. Task‑7 (dependency planning) has 141 instances, but the “rate of progress” metric is not precisely defined, making it hard to interpret the <60% success even for GPT‑4.
   - The paper states experiments were run once and metrics averaged (Appendix C), without multiple seeds or significance tests. This weakens claims in Sections 4.2 and the “On scaling law” discussion.

3) Tool retrieval is central in the pipeline but out of scope for evaluation, creating a mismatch between stated process and measured capabilities.
   - Figure 2 places “Retrieval of tools” as a key orange block in the decision flow, yet retrieval is assumed to be solved by a third-party retriever (Limitations) and is excluded from tasks. This creates a gap between the end-to-end agent story and the reported numbers, and makes it harder to translate these diagnostics to real deployments where retrieval is a dominant failure mode.

4) Reproducibility and affordability claims are at odds with reliance on third-party services.
   - 83% of tools are remote RapidAPI services. Although caching and pre-request checks are mentioned, there is no accounting of cost variability, rate limits, API version drift, or service unavailability. Without a fully local fallback or frozen snapshots/mocks, exact reproduction of the reported results may be difficult, especially for Tasks 6–8 where tool outputs shape agent responses.
   - The paper indicates free alternatives exist for “some” tools, but it is unclear which tasks are covered by those, whether the semantics are identical to the originals, and how often the local alternatives were used in the reported experiments.

5) Positioning and metric definitions could be sharpened; minor internal inconsistencies.
   - Related work coverage mentions T‑Eval and AgentBoard but does not sufficiently contrast the proposed schema and resources with other tool-use benchmarks. The paper would benefit from a clearer differentiation in methodology, scale, and realism, as well as acknowledging complementary focuses.
   - Metric definitions are often high-level. For example, Task‑5 “Relatedness” is vague; Task‑6 “Passing rate” and “precise interpretation” need formal criteria; Task‑7’s “rate of progress” is undefined in the main text. These ambiguities make cross-paper comparison and reuse harder.
   - Figure 2 includes “Respond according to tool return” and “Respond with intrinsic knowledge,” which are indeed evaluated, but the pipeline box also highlights “Retrieval of tools” while Section 6 admits retrieval is not covered, creating a small mismatch between the figure narrative and evaluation scope.

Additional, more minor points:
- Potential bias: GPT‑4 generated instructions and also graded outputs for several tasks; this may advantage GPT‑4. Some mitigation or ablation would help.
- Ethical and licensing aspects of reusing third-party API docs and executing live services are only briefly touched upon (Disclaimer), with no detailed discussion of ToS compliance or PII surfaced by certain APIs (e.g., IP lookup, user info).
- Table 5’s Task‑2 accuracy for GPT‑3.5 is substantially affected by “no call” choices. Reporting both top‑1 selection accuracy conditional on attempting a call and overall accuracy would be more interpretable.

Figure- and table-specific comments:
- Figure 2 effectively communicates the seven decision behaviors and where they occur in the interaction loop, which supports the paper’s decomposition argument. However, the inclusion of “Retrieval of tools” in orange suggests centrality that the subsequent tasks do not evaluate; acknowledging this visually in the caption or with a dashed outline could avoid confusion.
- Figure 4’s radar plot nicely surfaces relative weaknesses, especially Task‑7 for all models; it strengthens the claim that “talking is easier than doing.” Still, without confidence intervals or multiple runs, readers cannot judge robustness.
- Figure 5’s precision/recall/F1 bars for Task‑1 substantiate the qualitative observations about GPT‑3.5’s conservativeness and Qwen‑7B’s overuse of tools; this figure usefully complements the aggregate F1 in Table 5.
- Table 1 cleanly maps instruction types to tasks and helps readers reason about coverage.
- Tables 2 and 3 quantify dataset and per-task size; it is evident that high-level planning has limited instances (Type‑V = 50; Task‑8 = 50).
- Table 5 provides the core quantitative results; it would benefit from reporting standard deviations over repeated runs or bootstrap CIs.

## Potentially Missing Related Work
1) He et al., “TRAJECT-Bench: A Trajectory-Aware Benchmark for Evaluating Agentic Tool Use,” 2025 — Evaluates tool use at the trajectory level, including selection, parameterization, and ordering. Highly relevant to the paper’s decomposition and Task‑7/8 planning. Should be cited in Related Work and compared in Section 2.2 and Section 4 to clarify complementary metrics and how this work’s API design realism aligns with trajectory-focused evaluation.

2) He et al., “VitaBench: Benchmarking LLM Agents with Versatile Interactive Tasks in Real-world Applications,” 2026 — Focuses on complex, multi-turn, tool-intensive life-serving scenarios. Add to Related Work and discuss in Section 3.3/4 whether the proposed instruction taxonomy and toolset support comparable multi-turn realism, and how evaluation scales to more intertwined tasks.

3) Liu et al., “MCPAgentBench: A Real-world Task Benchmark for Evaluating LLM Agent MCP Tool Use,” 2026 — Uses Model Context Protocol tools with distractors and measures both success and efficiency. Include in Related Work; compare in Section 3.1/3.4 how the paper’s schema would transfer to protocol-structured tool environments and whether Tasks 1–8 capture MCP-specific dynamics like schema standardization.

4) Yehudai et al., “Survey on Evaluation of LLM-based Agents,” 2025 — A broad survey of evaluation methodologies; helps position the seven-aspect schema within a larger taxonomy. Cite in Related Work and use to discuss missing axes (e.g., safety, robustness, cost, and efficiency) in Section 6 Limitations.

5) Mohammadi et al., “Evaluation and Benchmarking of LLM Agents: A Survey,” 2025 — Emphasizes practical deployment considerations, behavior reliability, safety, and tooling. Add to Related Work and incorporate into the discussion about extending metrics beyond accuracy to cover stability, cost, and safety.

## Comments Suggestions And Typos
Actionable suggestions:
- Clarify grading protocols. Provide judge prompts, rubric details, and agreement checks for LLM-judged tasks. Consider a small human evaluation sample and include cross-judge analysis (e.g., GPT‑4 vs another strong LLM) to quantify grading bias.
- Tighten metric definitions. Precisely define Task‑5 “relatedness/answer quality,” Task‑6 “passing rate” and “precision of interpretation,” and Task‑7 “rate of progress.” Add examples and edge cases, ideally with a public scoring script.
- Report variance. Rerun evaluations with multiple seeds or perturbations, and provide confidence intervals in Table 5 and Figures 4–5. For Task‑2, also report conditional accuracy given the model attempted a call, alongside overall accuracy.
- Expand complex-task coverage. Increase the number of Type‑V instructions and Task‑7 dependency chains, possibly by procedurally generating additional scenarios within the same toolset to improve statistical power for planning claims.
- Retrieval consistency. Since Figure 2 shows retrieval as central, add an auxiliary retrieval task or provide a retrieval plug-in and evaluate it. Alternatively, visually mark retrieval as “assumed provided” in Figure 2 to prevent over-interpretation.
- Reproducibility safeguards. Ship a fully local, mockable version of the toolset with frozen responses for a fixed subset of tasks, plus a cost/latency log. Document which results used remote vs local tools and quantify the effect of caching.
- Bias and leakage checks. Because GPT‑4 generated instructions and also graded outputs, add countermeasures: regenerate some instructions with a different LLM, re-grade with a different judge, and report deltas; this will bolster claims in Section 4.2.

Typos and minor style issues:
- Page 5, “Complementing tools.” Consider rephrasing “comprise dependencies” to “introduce dependencies.”
- Page 7, “On interpreting tool results.” “copy&paste capability” -> “copy-and-paste capability.”
- Page 8, “Though both settings require the planning capability of LLMs, they impose very different challenges.” The paragraph could be tightened; avoid sentence fragments around “talking is much easier than doing.”
- Page 6, footnote “Two of our authors participate in data annotation.” Consider anonymization-safe phrasing and clarifying annotation protocol.
- Ensure consistent capitalization of “API(s)” and “LLM(s).”
- There are a few places with minor subject-verb agreement and article usage errors; a thorough proofread will help.

Criteria that could change my score upward during rebuttal:
- Release of code, mockable toolset, precise scoring scripts, and judge prompts, plus evidence of grading robustness or a small human eval.
- Clearer, formal metric definitions for Tasks 5–7, and additional results with confidence intervals.
- Expanded complex-task coverage or an auxiliary retrieval evaluation consistent with Figure 2’s pipeline.

## Confidence
4: Quite sure after careful checking — I reviewed the methodology, figures, tables, and metrics claims closely; remaining uncertainty centers on grading details that are not fully specified.

## Soundness
3.5: Between Acceptable and Strong — The schema and resources are solid and well-motivated; however, reliance on LLM-as-a-judge without robust validation, small complex-task sets, and single-run reporting limit the strength of empirical claims.

## Excitement
3.0: Interesting — The capability decomposition and real-API emphasis are useful and timely. With stronger evaluation rigor and complex-task scaling, this could become a go-to reference.

## Overall Assessment
3.5 Borderline Conference: Solid framing and potentially impactful resource with clear diagnostics, but current evaluation rigor and reporting leave gaps (judge dependence, metric precision, variance, and complex-task scale). With clarifications and added robustness, it would be a strong main-track candidate; as-is, it sits on the conference border.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper acknowledges not evaluating multi-turn dialogues with iterative clarification and excluding retrieval. Both are common in real deployments; documenting these omissions is appropriate.
- Potential societal considerations include: inadvertent exposure or misuse of sensitive information via tools (e.g., IP lookup, user profile), over-reliance on third-party services with opaque policies, and cost barriers that can exclude researchers. The paper would benefit from a short discussion of ToS compliance for API docs and usage, PII handling in any returned data, and mitigation strategies for cost and access inequities.
- As failure modes, misinterpretation of API results or hallucinated parameters (noted in Task‑3/6 error analyses) could lead to harmful or misleading actions in deployment settings. Encouraging safe fallbacks and refusal behaviors would be prudent.

## Ethical concerns
None, beyond the need for clearer statements about third-party API ToS, potential PII in tool outputs, and judge-model biases which could skew conclusions.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible — The paper describes dataset/task design, provides counts and examples, and outlines a toolset. However, dependence on live third-party APIs and unspecified judge prompts reduce exact reproducibility. Providing a mockable subset and detailed grading scripts would raise this to 4–5.

## Datasets
4: Useful — The instruction taxonomy and per-task splits are practical. Scaling up complex-task instances and adding multi-turn examples would further increase value.

## Software
4: Useful — The toolset design emphasizing real APIs and dependencies is helpful. A fully local/mock mode and documented cost controls would make it even more broadly usable.