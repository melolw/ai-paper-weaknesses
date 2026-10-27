# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper targets false-memory formation in LLM agent memory systems. The core claim is that many systems verify extracted candidate memories against the full dialogue, allowing assistant-originated statements to “self-verify.” The proposed Speaker-Attested Grounding (SAG) keeps extraction on the full dialogue but restricts verification evidence to user turns only. On a 5-user subset of HaluMem-Medium, SAG increases False Memory Resistance (FMR) by 11.94pp over a dialogue-wide filtering baseline, with a 7.20pp recall drop. A per-source analysis attributes the FMR gains to assistant-only interference memories. An ablation suggests roughly half of the benefit is due to speaker restriction and half to shorter evidence.

## Summary Of Strengths
- Clear and targeted hypothesis: restricting verification evidence to user turns should prevent assistant self-verification. Equation (1) concisely formalizes the intervention, and the pipeline in Figure 1 makes the single-variable change easy to understand.
- Clean experimental control: prompts and components are fixed while only the evidence corpus changes, improving attribution of effects to the proposed mechanism.
- Focused analysis: Figure 2 breaks down FMR by interference source and shows that improvements concentrate on assistant-only interference, which matches the intended mechanism.
- Useful ablation: Table 2 introduces a token-length-matched dialogue-wide baseline to separate speaker restriction effects from reduced evidence length.
- Practicality: SAG is a drop-in change that many agent systems can implement quickly and is likely to matter in production where false memories are particularly harmful.

## Summary Of Weaknesses
1) Limited evaluation scope and representativeness
- The main results rely on a 5-user subset (343 sessions) of HaluMem-Medium (Section 4.1). There is no evidence the effect generalizes to the full benchmark or to other datasets or workloads. This is a significant external validity gap given the paper’s broad framing.
- Table 1 reports performance only on this subset; no cross-domain or multilingual tests or longer-horizon sessions are considered.

2) Baseline coverage is narrow
- Baselines are Extract-Only and Dialogue-Wide filtering. Missing comparisons to stronger filtering or verification strategies, e.g., learned verifiers, entailment checkers, or multi-document fact-checkers commonly used in grounding (beyond citing MiniCheck). Without such baselines, the claim that speaker restriction is the right design choice is under-supported.

3) Over-interpretation of source analysis
- Figure 2 shows +4.6pp for assistant-only and 0pp for user-repeated. The text then states “100% of SAG’s overall FMR improvement comes from the assistant-only subgroup.” This conclusion implicitly depends on the subgroup mixture and weighting. Since overall FMR is a micro-average over all interference instances, it would help to show the exact aggregation and confidence intervals; otherwise, “100%” reads stronger than warranted.

4) Statistical rigor and uncertainty
- No confidence intervals, variance estimates, or statistical tests are reported in Tables 1–2 or Figure 2. Given reliance on LLM judgments and a single temperature setting, reporting variance across seeds or re-judging would strengthen the claims.

5) Judge model and potential bias
- The evaluation uses GPT-4o as judge and GPT-4o-mini for the system. A single-provider judge risks correlated biases. It is important to include either an alternative judge model, human spot checks, or an adjudication protocol. Otherwise, FMR and recall changes could partially reflect judge alignment with the proposed mechanism.

6) Threats to validity in ablation
- Table 2’s Token-Matched baseline truncates dialogue-wide evidence to match SAG length. However, length matching via truncation may interact with turn order and information asymmetry, unfairly harming recall. Consider length-normalized sampling stratified by speaker or turn recency to isolate length from content distribution. As presented, the 52.5% attribution to length may be confounded.

7) Metric definitions and tradeoffs need more nuance
- The paper reports Recall, FMR, and F1 (Table 1) but F1 is the harmonic mean of Recall and FMR, an unusual pairing for memory systems where false-write risks may dominate. The work would benefit from an explicit problem-driven metric discussion and possibly a utility-weighted score or cost-sensitive analysis.

8) Lack of downstream impact evaluation
- The paper does not evaluate how SAG affects agent behavior when memories are retrieved and used, e.g., correctness in task execution or user satisfaction. Preventing writes is valuable, but the practical impact depends on downstream outcomes.

9) Error analysis is shallow relative to claims
- Section 4.5 mentions semantic overlap as an “irreducible” floor and provides one illustrative pattern. More systematic categorization with counts and representative examples would guide mitigation strategies. In particular, how often are misses due to extractor inaccuracies versus verifier misses?

10) Reproducibility details still thin
- While prompts are said to be fixed across methods, the paper does not include or summarize the exact prompts or verifier criteria beyond “strict” vs “relaxed.” Readers need prompt text, verifier rubrics, and filtering outputs for a subset to ensure faithful replication.

Explicit references to figures/tables:
- Figure 1: The pipeline diagram is helpful, but the right panel claims “99.9% passes” for a baseline verifier; this looks illustrative rather than measured. If so, label it clearly as schematic to avoid confusion with empirical rates.
- Figure 2: Shows assistant-only bar rising from 86.7% to 91.2% and user-repeated remaining at 80.5%. This supports the targeted mechanism, but please add error bars and state how micro/macro averaging is performed.
- Table 1: SAG (relaxed) improves FMR to 70.70% with Recall dropping to 45.94%. The Dialogue-Wide baseline’s FMR (58.76%) is close to Extract-Only (56.90%), bolstering the self-verification hypothesis. Still, statistical significance and variability are missing.
- Table 2: Token-Matched achieves 66.98% FMR and 33.99% Recall, versus SAG (strict) 74.42% FMR and 43.81% Recall. The stronger recall under SAG is compelling, but the truncation protocol may bias Token-Matched negatively.

## Potentially Missing Related Work
1) Xu et al., “Contextual Agentic Memory is a Memo, Not True Memory,” 2026 — Conceptual analysis of agent memory reliability and consolidation. Discuss in Section 2.1 and the Conclusion to frame SAG’s scope as preventing self-verification during writes rather than solving consolidation.
2) Wang et al., “SAGE: A Self-Evolving Agentic Graph-Memory Engine for Structure-Aware Associative Memory,” 2026 — Provides a structured, graph-based memory with diagnostics on hallucinations, including HaluMem. Compare in Section 2.1 and add as a stronger baseline or discussion point in Section 4.
3) Yang et al., “TRUSTMEM: Learning Trustworthy Memory Consolidation for LLM Agents with Long-Term Memory,” 2026 — Introduces learned consolidation verifiers and RL to reduce hallucinations and corruption. Discuss in Section 2.2 and consider as a baseline or ablation in Section 4.
4) Omri et al., “Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads,” 2026 — Systems-level taxonomy contextualizing memory write/read costs and tradeoffs. Cite in Related Work and expand Section 4.1 to position SAG’s cost-performance profile.
5) Xiang et al., “MemSyco-Bench: Benchmarking Sycophancy in Agent Memory,” 2026 — Relevant stress test for downstream misuse of stored content. Mention in Section 4 as a complementary evaluation for whether SAG reduces sycophancy-amplifying memories.
6) Wang et al., “EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective,” 2026 — Benchmark to assess memory evolution across episodes. Include in Section 4 as a future evaluation site to test long-term dynamics of SAG.
7) Shen et al., “Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented Autonomous Agents,” 2026 — Evaluates executable use of memories for tool arguments. Add to Section 4 as a downstream task benchmark to test whether SAG’s higher FMR helps task success.

## Comments Suggestions And Typos
Actionable suggestions:
- Expand evaluation beyond a 5-user subset. Report full HaluMem results and, if possible, at least one additional benchmark focusing on downstream use (e.g., task-oriented memory utilization).
- Strengthen baselines. Include: (a) a learned verifier (NLI-style or claim-evidence scoring), (b) a retrieval-augmented verifier with explicit quote matching, and (c) a multi-judge aggregation (e.g., different providers) to reduce judge-model bias.
- Report uncertainty. Add bootstrap confidence intervals or multiple seeds for extraction and verification; include error bars in Figure 2. Consider re-judging with another LLM and limited human adjudication on a random subset.
- Clarify aggregation. Precisely define how FMR is computed across subgroups and the weighting that leads to overall FMR. If claiming “100% of the gain,” add a decomposition table with counts and contributions.
- Improve ablation design. Replace naive truncation with stratified token-matching that preserves speaker distribution or randomized masking to separate length from content. Consider a user-probative subset of assistant turns to test whether specific assistant content types drive failures.
- Release prompts and verifier rubrics. Include all prompts in the appendix and link to an artifact tarball with candidate memories, decisions, and judgments for at least a sizable sample.
- Consider a cost analysis. Since SAG reduces evidence length, quantify average verification token savings and latency, and relate them to FMR/Recall shifts.
- Downstream assessment. Run a small study on whether higher FMR under SAG improves end-task accuracy or reduces harmful behaviors when memories are retrieved.

Typos/formatting:
- References list contains many formatting issues and probable typos (e.g., “Made laine Boyd,” “Jeff Belgium,” inconsistent capitalization and accents). Please clean and shorten large author lists per ACL style.
- Figure 1 includes “99.9% passes” in the baseline bubble; clarify that this is illustrative, not measured.
- Table captions: clarify that F1 is harmonic mean of Recall and FMR. Consider renaming to avoid confusion with classification F1.
- Minor spacing issues in author list and keywords; “Made laine” likely “Madelaine” or “Madeleine.”

Criteria to raise my score:
- Add comprehensive, statistically rigorous results on the full HaluMem dataset with uncertainty estimates and an additional independent judge or human verification.
- Include stronger baselines (learned verifier, fact-checker-style pipeline, or recent memory-consolidation methods) and show SAG remains competitive or complementary.
- Provide prompts, verifier instructions, and a reproducibility package with intermediate artifacts.
- Demonstrate downstream impact on at least one benchmark where memories affect actions or tool use.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details. Justification: good single-variable setup and clear effect on a subset; needs broader evaluation and stronger baselines.

## Excitement
2.5 Between potentially interesting and interesting. The idea is simple and practical, but the evaluation is narrow and heavy reliance on one benchmark and a small subset tempers enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The intervention is neat and well-motivated, and the attribution analyses are on the right track, but the evaluation scope, baseline coverage, statistical rigor, and reproducibility details need strengthening for the main conference. With broader experiments and stronger baselines, this could move to a solid Findings or borderline main-track contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper focuses on reducing false writes, which is a positive step for safety and privacy, but may omit legitimate memories if users only imply facts. The paper acknowledges a recall tradeoff and a semantic-overlap failure mode. Recommended additions: discuss potential disparate impacts if certain user populations more often imply than state facts; consider privacy implications of stricter verification leading to fewer sensitive details being stored; and analyze dual-use risks if attackers craft user turns to evade user-only filters.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The approach is simple and code is indicated as available. However, exact prompts, rubrics, and intermediate artifacts should be provided to ensure faithful replication and to address judge-model sensitivity.

## Datasets
1 No usable datasets submitted. The work evaluates on an existing benchmark subset; no new dataset contribution.

## Software
4 Useful.: I would recommend the new software to other researchers or developers for their ongoing work. Assuming the linked implementation is complete and documented, it should be a practical drop-in for many pipelines.