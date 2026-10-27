# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes Evolutionary-Boids, a preliminary framework for coordinating LLM-based agents that create, share, and reuse software tools. The approach adapts Boids-style local interaction rules—separation, alignment, and cohesion—to the cognitive/action space of tool building, and couples them with a simple evolutionary selection mechanism based on a Tool Complexity Index (TCI). Agents follow an observe–reflect–build loop, with tests and a shared registry, and selection periodically replaces the least “complex” contributors. Results across three task families (text analysis, data science, simulation/modeling) indicate higher throughput and more balanced contributions under Boids+evolution compared to a global baseline, with comparable pass rates but marked decreases in compositional complexity. The work is positioned as an early step toward understanding how simple local rules and selection pressures shape evolving agent ecosystems.

## Summary Of Strengths
- Conceptual clarity and framing:
  - The paper offers a clear synthesis that frames decentralized multi-agent tool creation as local-rule coordination plus evolutionary selection. The mapping of separation/alignment/cohesion to prompt-level guidance is clearly explained in Section 3.2, with explicit mathematical notations in Equations (1)–(6) that make the intended signals interpretable to readers.
- Method design and measurability:
  - The TCI metric in Section 4.1 is explicitly defined with subcomponents for code, interface, and composition, including concrete ranges and capping functions. This improves transparency and supports ablation-style discussions about what aspects of complexity are being optimized.
- Preliminary empirical signal:
  - Table 1 shows consistent increases in “Tools created” under Boids+Evolution across all three domains (e.g., 13 vs 9 for text analysis; 18 vs 10 for data science; 16 vs 14 for simulation/modeling), while maintaining comparable pass rates. This suggests the local-rule nudges increase exploratory throughput without severe reliability degradation.
- Honest self-assessment:
  - The Limitations section (Pages 7–8) is unusually thorough for a preliminary study. It candidly discusses construct/internal/external validity threats, the bias toward self-contained tools, and confounds such as per-round build enforcement.
- Clarity and readability:
  - The exposition is accessible, with a clean articulation of the agent loop, registry, and assurance mechanisms (Section 3.1) and how these integrate with Boids rules (Section 3.2) and selection (Section 3.3). The writing is direct and avoids hype.

## Summary Of Weaknesses
1) Insufficient empirical depth and rigor for ACL main-track standards
- The experimental section is extremely lean for an empirical systems paper. Table 1 is the sole quantitative results table. There are no error bars, confidence intervals, or seed-controlled replications reported in the main paper, despite the complexity and stochasticity of LLM-based systems. The Agents4Science checklist statement that “replicated runs across randomized initializations/topologies” were reported is not reflected with concrete statistics in the main text; the Results section does not present variability measures. This makes it difficult to assess the robustness of the throughput and pass-rate differences.
- The study scope is small: three task families with similar trends but without deeper breakdowns (e.g., per-agent output distributions, time-series of test pass rates, composition depth trajectories per round). The claims about balanced contributions and “lower top share” in Section 4.2 are not substantiated with explicit numeric evidence in the main text.

2) Evaluation metric misalignment and selection pressure that ignores correctness
- The evolutionary selection is driven by average TCI (Section 3.3), which explicitly does not weight correctness or collaboration metrics (“selection is TCI-based without directly weighting correctness or collaboration metrics,” Page 5). This can reward tool bloat or superficial interface breadth rather than utility or reliability. Although a parsing quality gate penalizes syntax errors (Section 4.1), the evolutionary objective does not directly consider pass rates or real downstream task value. This weakens the causal link between selection pressure and the desirable emergent properties the paper aims to study.
- As corroborated in Table 1, the “Compositional complexity” column under Boids is near zero across domains (0.03/0.04/0.01), which suggests the TCI’s composition component is not being effectively selected for in practice, undercutting the intended “evolution toward reusable parts.”

3) Conflation of factors and incomplete ablations
- The paper itself acknowledges potential confounds (Page 7: “per-round build enforcement and ‘novelty-seeking’ cues” may drive the observed gains), but no ablations are presented to separate the effects of (i) Boids prompts versus (ii) deterministic build enforcement versus (iii) evolutionary selection. For instance, a “build-enforcement only” condition, or an “evolution only” condition with correctness-weighted selection, would be valuable. Section 3.3 says the authors study “boids-only, evolution-only, and combined conditions,” yet the reported results only contrast “Baseline (Global) vs Boids+Evolution” in Table 1; there is no table or figure showing boids-only or evolution-only outcomes.

4) Narrowness of evidence for emergence and collaboration
- The core claim is about emergent coordination and ecosystem dynamics. However, the only quantitative evidence is overall throughput and pass rates. There are no quantitative measurements of collaboration events, adoption graphs, or specialization indices, despite these being identified as observables in Section 3.1. Qualitative examples of cross-agent reuse, or dependency graphs illustrating how cohesion/alignment influenced tool chaining, are absent.
- The cohesion rule (Equation 6) is intended to favor using neighbors’ tools, but Table 1 shows reduced compositional complexity under Boids+Evolution. This contradiction should be explicitly analyzed: why does the cohesion prompt fail to raise composition scores in practice? Is it outweighed by separation, by the deterministic “build” step, by dependency policy limits, or by the TCI incentives?

5) Overreliance on a static-complexity proxy (TCI) and under-instrumented composition
- TCI is a static, non-semantic proxy (Section 5.2). Particularly, Ccomp weights breadth over depth and counts top-level imports and tool references. This can be gamed by superficial wrapper code and does not reflect actual runtime reuse or utility. Given that a central claim is about composition and emergent pipelines, the lack of dynamic call-graph or runtime composition metrics is a significant gap. The paper acknowledges this but still bases selection entirely on TCI.
- The discrepancy between the narrative and Table 1’s “Compos. complexity” highlights potential construct-validity issues: the system is said to “encourage composition,” yet the measured indicator shows composition falling near zero.

6) Missing or unclear baseline definitions and fairness
- The “Baseline (Global)” is not fully specified in the main text beyond high-level descriptions. Key elements are missing: Are prompts identical except for Boids fragments? Is the per-round deterministic build enforcement used in baseline? How are examples/exemplars surfaced to baseline agents? Without a rigorously controlled baseline, improvements in “Tools created” could reflect differences in prompting template complexity and variety rather than inherent benefits of local-rule conditioning.
- Table 1’s “Pass rate (%)” is ambiguous: are these pass rates per-submission, per-tool, or per-final-promoted tool? Are multiple retries allowed? The Discussion mentions “lightweight, failure-aware retries” as a possible extension, but it is unclear what retry protocol, if any, was in place during reported runs.

7) Limited connection to NLP-specific benchmarks and relevance
- While tool creation with LLM agents is relevant to ACL, the current tasks and metrics are not strongly tied to standard NLP evaluation practices. The paper would be much stronger if it connected to recognized NLP agent/tool benchmarks, or at least to text-heavy evaluation suites where composition depth can be objectively correlated with downstream performance (e.g., complex IE or multi-hop QA with tool calls).
- The text-analysis domain is mentioned, but the empirical analysis remains framework-centric. There is no direct comparison to multi-agent orchestration baselines common in NLP (e.g., CAMEL/AutoGen-style pipelines executing text-processing workflows with tool reuse).

8) Lack of figures and diagnostic visualizations
- There are no figures visualizing tool ecosystems, adoption graphs, specialization divergence, or composition depth over time. This is a missed opportunity to demonstrate the paper’s central thesis about emergent organization. Even a single figure showing evolving dependency graphs per round would materially strengthen the narrative.

9) Claims partially unsupported by presented results
- Section 4.2 asserts “the gain is ecosystem-wide rather than star-driven: the most productive agent accounts for a smaller share of total output,” but no data are provided to back this. A simple Lorenz curve or top-k share table would suffice.
- The Conclusions state “30–50% more valid artifacts than global baselines,” which is roughly consistent with Table 1 tool counts, but “valid” implies test-passing artifacts; the paper should directly report “number of passing tools” per regime to substantiate this term.

10) Reproducibility and dependency specifics
- The Acknowledgements specify Azure OpenAI endpoints and a single deployment “gpt-4.1-nano,” but there are no details on random seeds, rate limiting, retry/backoff policies, or cost/accounting. Given the stochasticity of LLM sampling, reproducibility requires more than endpoint details. The paper mentions logs/JSON emission but does not provide a concrete protocol in the main text for reconstructing Table 1 from these artifacts.

Explicit reference to equations and table:
- Equation (6) (cohesion) aims to increase Pcoh(a_use) when N_T > 0, yet Table 1 shows lower compositional complexity under Boids. This undermines the claim that cohesion fosters collaborative tool use in the current implementation and should be reconciled either by revising the implementation or by adjusting incentives.
- Equation (2) (separation tiers) and Equation (5) (alignment boost) are clear but are only instantiated as prompt text fragments. Because the orchestrator “deterministically proceeds to a build action each round” (Section 3.2), these preference functions are not part of a decision policy; they are narrative guidance. This discrepancy between formalism and implementation should be highlighted and empirically evaluated via ablations.

## Potentially Missing Related Work
1) Plaat et al., “Agentic Large Language Models, a survey,” 2025 — comprehensive survey of LLM agents, multi-agent coordination, and tool use. Directly relevant for situating the framework within the agentic-LLM landscape. Should be cited in Related Work (Section 2) and used to refine positioning against existing orchestration paradigms.

2) Abou Ali et al., “Agentic AI: A Comprehensive Survey of Architectures, Applications, and Future Directions,” 2025 — broad taxonomy of agentic AI architectures and governance. Relevant for comparing Evolutionary-Boids’ institutional rules with other coordination/governance mechanisms. Discuss in Section 2 and contrast after describing Boids rules in Section 3.2.

3) Qu et al., “CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery,” 2026 — multi-agent evolutionary framework for open-ended discovery using LLMs. Very close in spirit; should be discussed as a directly comparable evolution-driven approach in Section 2 and as a baseline or conceptual comparator in Section 4.

4) Feng et al., “EvolvingAgent: Curriculum Self-evolving Agent with Continual World Model for Long-Horizon Tasks,” 2026 — self-evolving agent with curriculum and long-horizon adaptation. Relevant to claims about open-endedness and long-term composition. Add to Section 2 and compare in Conclusions regarding future directions for curriculum and forgetting.

5) Kumar et al., “Evolving Interpretable Constitutions for Multi-Agent Coordination,” 2026 — evolves normative rule sets for societies of LLM agents. Directly touches on “evolving local rules” and societal stability. Discuss in Section 2 and relate to the paper’s concept of institutional primitives in Section 3.2–3.3.

6) Wang et al., “EVOLVING ROLLOUTS: Harnessing Historical Experience for Web Agent Evolution in Reinforcement Learning,” 2026 — leverages historical trajectories and in-context evolution, relevant for integrating experience repositories with selection pressure. Cite in Section 2 and discuss potential incorporation into the registry and alignment rules.

7) Nachkov et al., “LLM Agents Beyond Utility: An Open-Ended Perspective,” 2025 — conceptual work on open-ended agents, task generation, and evaluation. Add to Section 2 to strengthen the discussion of open-endedness and evaluation criteria beyond utility.

8) EvoAgent: “An Evolvable Agent Framework with Skill Learning and Multi-Agent Delegation,” 2026 — evolvable skills and delegation in real-world scenarios. Relevant to tool creation, reuse, and specialization. Discuss in Section 2 and compare the skill abstraction with this paper’s tool abstraction and TCI.

## Comments Suggestions And Typos
Actionable suggestions and questions:
1) Add ablations to disentangle factors:
- Report results for: (a) Baseline, (b) Boids only, (c) Evolution only with TCI selection, (d) Build-enforcement only, (e) Combined (current). This will clarify what drives the throughput gains and what suppresses composition.

2) Align selection with utility and collaboration:
- Add a correctness-weighted or utility-weighted selection signal (e.g., number of passing unit tests; calls by other agents; downstream task success). Consider a composite fitness: α·TCI + β·pass_rate + γ·adoption_count. Show in a new table how this affects “Compositional complexity” and pass rates.

3) Strengthen measurement of composition and collaboration:
- Go beyond static Ccomp by instrumenting runtime call graphs. Report: average composition depth per round, proportion of tools that call at least one existing tool, adoption DAG visualizations, and per-agent reuse rates. A figure tracing dependency graphs over rounds would substantiate emergent cohesion.

4) Clarify baseline and evaluation protocol:
- Precisely define the Baseline prompts, per-round action policy, retry policy, and exemplar surfacing. Report “passing tools created” in addition to “tools created,” and define pass rate denominator (per-tool vs per-attempt). Include seed management and present error bars in Table 1 or an expanded results table.

5) Make cohesion effective or explain failure modes:
- Given Equation (6)’s intent, diagnose why Table 1 shows lower composition under Boids. Test stronger cohesion prompts, composition quotas, and a whitelist of dependencies as proposed on Page 7. Report the delta in composition scores and show a qualitative example where an agent correctly chains neighbor tools.

6) Clarify the role of Equations (1)–(6) in the actual decision policy:
- Currently these are “descriptive scaffolds” while the orchestrator deterministically builds each round. Either (a) convert them into an explicit probabilistic policy over actions or (b) clearly position them as prompt heuristics and present evidence that the textual signals, not just build enforcement, causally change behavior.

7) NLP grounding:
- Include at least one task where composition depth matters for a known NLP benchmark (e.g., multi-step IE, multi-hop QA with tool APIs). Show that composition-aware selection measurably improves end-task metrics, not just TCI.

Criteria for score increase during rebuttal:
- Provide ablation results separating Boids, evolution, and build-enforcement effects, with error bars.
- Add a corrected selection criterion that includes correctness and adoption and show improved compositional complexity and utility.
- Include at least one figure visualizing adoption/call graphs over time, and a table breaking down per-agent contribution shares to back the “balanced contribution” claim.
- Clarify baseline details and report seed-controlled replications.

Minor typos/edits:
- Page 2: “The paper is organised” → “organized” (US spelling, for consistency; or standardize throughout).
- Page 5, Table 1 caption: clarify what “Code/Comp. are last-round complexities” means operationally. Are these per-tool last-round means or last tools’ scores?
- Page 9, References [13]–[14]: citations are concatenated in one line; separate entries cleanly and standardize punctuation.
- Several spots use italics or quotes inconsistently around terms like “parts bin,” “novelty-seeking”; consider standardization.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure, but there’s a chance I missed something. The methodology is clear, but empirical details are sparse in the main text.

## Soundness
2.5: Between Poor and Acceptable — The framework is coherent and the metrics are specified, but the evaluation is too thin, selection is misaligned with correctness, and key ablations are missing.

## Excitement
2.5: Between potentially interesting and interesting — The idea of marrying Boids-style rules with evolution for tool-building agents is appealing, but the current empirical evidence is limited.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The conceptual framing and preliminary results are promising, and the paper is transparent about limitations. However, for ACL, the empirical evaluation is too shallow, ablations are missing, and the selection objective is misaligned with utility. Strengthening the experimental section with ablations, corrected selection metrics, and runtime composition evidence could move this toward acceptance in Findings.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section (Pages 7–8) is thorough and candid, covering construct/internal/external validity, prompt/policy confounds, and stochasticity. For societal impact, while the system focuses on autonomous tool generation, potential risks include propagation of insecure or harmful tools if the registry is not vetted, and biased specialization if alignment signals amplify artifacts from certain agents. It would help to discuss:
- Governance of the shared registry (approval, sandboxing, safety tests).
- Auditability and rollback mechanisms if harmful tools proliferate.
- Equity in credit and specialization to avoid mode-collapse on certain agent “identities.”

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The paper describes the system and gives some implementation details and TCI formulas, but lacks seeds, full baseline specs, and a concrete replication protocol for Table 1 in the main text.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If released, the codebase could be useful for researchers studying multi-agent tool creation; however, to be truly useful it needs clearer baselines, seeds, and a mock or open-source LLM backend option to avoid vendor lock-in.