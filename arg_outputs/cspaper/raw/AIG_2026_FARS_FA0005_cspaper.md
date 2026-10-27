# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper targets control-plane jailbreaks in structured-output LLM APIs that use JSON Schema–constrained decoding. The core observation is that attackers can place harmful natural-language payloads in forced literals (enum/const), which decoding must emit verbatim. The proposed defense, Selective DeLex-JSON, is a training-free preprocessing step: it scans schemas, flags “suspicious” literals using a conjunction of simple heuristics (length > 20, contains whitespace, instruction-like patterns), and replaces them with opaque placeholders (OPTION_i). Experiments on HarmBench (safety), StrongREJECT, and JSONSchemaBench (utility) report 0% attack success rate (ASR) for DeLex-JSON against the EnumAttack on two models while changing only 1.1% of benign schemas. Ablations suggest forced literals, not metadata, are the primary attack vector; a delex-all variant attains similar safety but with much higher benign modification cost. Figure 3 highlights a limitation: chunked payloads made of many short literals evade the heuristic.

## Summary Of Strengths
- Simple, deployment-friendly idea: schema-time sanitization that does not require retraining or modifying decoding engines. The method is clear and easy to implement.
- Empirical signal that the immediate attack vector is in forced enum/const literals; the Strip-Only baseline in Table 3 showing identical ASR to No Defense is a useful negative control isolating where risk resides.
- Table 1 shows strong headline safety results against the evaluated EnumAttack, including across two instruction-tuned models, suggesting model-agnosticism because the defense operates before inference.
- Utility evaluation on JSONSchemaBench in Table 2 indicates a low benign modification rate (1.1%) and small deltas in validity/compliance, supporting claims that structural guidance is mostly preserved.
- Figure 2 (safety–utility frontier) is helpful for visually situating the approach relative to baselines, clarifying the claimed Pareto advantage over Reject-Only.
- Clear documentation of a key failure mode: Figure 3’s chunked-payload analysis explicitly demonstrates that the heuristic can be bypassed when payloads are split into short segments, which is an honest and informative limitation.
- The paper’s pipeline description (Figure 1) is straightforward and practically relevant for teams already using JSON Schema with constrained decoding.

## Summary Of Weaknesses
1) Scope of the safety claims and evaluation coverage
- The 0% ASR result is limited to the specific EnumAttack instantiation; the paper does not test broader control-plane attacks (e.g., schema-level tricks beyond forced literals, grammar-driven payloads, multi-stage attacks that interleave literals with generative fields). Table 1 reports ASR only for HarmBench and StrongREJECT under EnumAttack; there is no exploration of whether attackers adapt to the defense by altering schema structure rather than literals.
- Figure 3 shows that chunked payloads achieve 8–14% ASR with or without the defense, directly contradicting the “complete neutralization” narrative in the abstract and Section 4.2. This substantially narrows the claimed threat coverage.

2) Baseline completeness and fairness
- Input Guard is shown only partially and with dashes for Qwen in Table 1. Similarly, Escape-Hatch and Reject-Only are not consistently reported across both models. The absence of full cross-model reporting weakens comparative conclusions.
- There is no comparison to defenses that sanitize schemas using learned or semantic filters, or to grammar-level defenses in closely related domains (e.g., code grammars or function-calling masks). Given that the proposed heuristic is intentionally simple, the baselines are narrow and leave open whether stronger semantic filters would outperform with comparable benign cost.

3) Incomplete methodological details on detection patterns
- Section 3.3 defines “instruction-like patterns” in broad terms (imperatives, “Sure,” “Step 1”), but no concrete, reproducible pattern inventory or regex is provided. Reproduction and robustness analysis require exact rules, language coverage, case-folding decisions, and tokenization assumptions.
- No sensitivity analysis for the threshold of 20 characters or for conjunction logic (“at least two criteria”). Without ROC-like curves or utility–safety tradeoff sweeps, it is hard to assess generality or tune the defense for other deployments.

4) Measurement choices and reporting gaps
- The paper states that forced literals are excluded from harm scoring for “safety evaluation” (Section 3.4). This is a non-trivial evaluation choice: if an attack’s goal is to force a harmful literal into the output stream, removing that content from scoring can understate risk to downstream consumers that will see those literals. The paper should justify this decision and report alternative metrics that include the effect on the serialized output stream before any postprocessing.
- Table 2 has “–” entries for several subsets’ validity/compliance deltas, leaving the utility picture incomplete. If measurements were not computed, explain why; if they were computed but omitted, include them. Confidence intervals or statistical tests are absent across Tables 1–3.
- Runtime and throughput costs are not discussed. Even training-free defenses can impact latency through schema traversal and string operations. Especially for high-QPS production systems, a performance profile is needed to substantiate “immediately deployable” claims.

5) Threat model and safety boundary clarity
- Section 3.1 grants attacker control of the entire schema, including enums and consts. The paper does not consider defenders who may rely on schema provenance, signing, or allowlists for tool contracts. This is fine as a strong threat model, but then the defense’s post-hoc “restore original value” mapping in Section 3.4 could reintroduce the very payload; more discussion is needed on safe restoration practices and how downstream systems should handle placeholders.
- Non-English or obfuscated payloads: the patterns seem tuned to English imperatives and affirmative prefixes. There is no evaluation on multilingual or obfuscated strings that avoid whitespace or common verbs, which weakens generality.

6) Limited connection to rapidly growing, directly related literature
- The Related Work section misses several closely aligned studies on schema or grammar–level jailbreak vectors and structured-output evaluation benchmarks. This omission weakens positioning and may hide stronger comparison points. See the “Potentially Missing Related Work” section below.

7) Figure- and table-specific concerns
- Figure 2 is persuasive, but it relies on a benign-cost axis that conflates modification and rejection rates across methods with very different operational semantics. A clearer normalization or separate panels for “modification” vs “rejection” would avoid aggregating distinct costs.
- Table 1’s note on guard rejection rates is helpful, but the interplay between guard decisions and constrained decoding is not fully unpacked. For instance, does guarding first change the schema distribution shown to decoding? What fraction of attacks are filtered at guard vs leaked? More granular breakdowns would clarify why 3.8% residual ASR persists.
- Table 3’s Delex-All shows 35.5% benign modification with worse utility metrics; however, the differences in Validity/Compliance are modest (≤1 pp), which challenges the claim that Delex-All is “unacceptable.” The paper should better justify practical unacceptability with downstream task metrics or user-facing degradation evidence.

8) Reproducibility and transparency gaps
- Although a code URL is provided in a footnote, the paper does not enumerate versions, commit hashes, or exact pattern lists. The evaluation protocol for excluding literals in harm scoring should be fully specified to avoid metric ambiguity.

9) Overstatements in the narrative
- The abstract and contributions claim “complete attack neutralization,” yet Section 4.6 and Figure 3 clearly refute this for chunked payloads. The main text should calibrate claims to match the limitations section.

## Potentially Missing Related Work
1) Rafiei Oskooei et al., “BreakFun: Jailbreaking LLMs via Schema Exploitation,” 2025 — Directly addresses schema-level jailbreaks that force harmful outputs, closely aligned with the control-plane attack vector here. Should be discussed in Section 2.3 and compared empirically as an additional baseline in Table 1.

2) Zhang et al., “Grammar-Constrained Decoding Can Jailbreak LLMs into Generating Malicious Code,” 2026 — Shows constraint-level vulnerabilities akin to JSON schema abuse; their mitigation strategies are relevant comparators. Cite in Section 2.3 and discuss differences after Section 4.2; consider adapting their defenses as baselines.

3) Li et al., “Constraint Tax in Open-Weight LLMs: An Empirical Study of Tool Calling Suppression Under Structured Output Constraints,” 2026 — Analyzes how constraints interact with tool use; relevant for understanding DeLex-JSON’s downstream impact when placeholders replace literals. Add to Section 2.2 and discuss operational implications in Section 4.3.

4) Singh et al., “The Structured Output Benchmark,” 2026 — A comprehensive structured-output benchmark; could be used to quantify benign utility under non-adversarial and adversarial conditions. Reference in Section 4.1 and consider additional evaluation.

5) Attouche et al., “Elimination of annotation dependencies in validation for Modern JSON Schema,” 2025 — Clarifies JSON Schema semantics that matter for safe delexicalization, e.g., annotation vs validation keywords. Useful for formalizing which literals can be changed without altering instance space. Discuss in Section 3.4.

6) Agarwal et al., “Think Inside the JSON: Reinforcement Strategy for Strict LLM Schema Adherence,” 2025 — Presents a training-based route to robust schema adherence; a contrasting approach to your training-free method. Add to Section 2.2 and consider as a complementary baseline or discussion point.

7) Yang et al., “StructEval: Benchmarking LLMs' Capabilities to Generate Structural Outputs,” 2025 — Could strengthen utility analysis and provide standardized metrics; cite in Section 4.1–4.3.

8) Feng et al., “SO-Bench: A Structural Output Evaluation of Multimodal LLMs,” 2025 — Expands to multimodal settings where control-plane issues may persist; include in Section 5 for future directions and positioning.

9) Liu et al., “Are LLMs good at structured outputs? A benchmark for evaluating structured output capabilities in LLMs,” 2024 — Baseline structured-output evaluation results; useful for contextualizing the benign utility costs. Add to Section 2.2 and Section 4.3.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide full specification of the suspicion function: exact regexes, tokenization, case sensitivity, language assumptions, and the full list of imperative cues and affirmative prefixes. Include ablations sweeping length thresholds (e.g., 10–40) and conjunction logic (1-of-3 vs 2-of-3 vs 3-of-3) with ROC-like plots for safety vs utility. This would materially strengthen Section 4 and Table 2.
- Revisit the safety metric in Section 3.4 that excludes forced literals from harm scoring. Add a secondary metric that evaluates the literal-inclusive serialized output, possibly demarcating “model-chosen” vs “schema-forced” spans. Report both to avoid optimistic bias and to reflect user-visible risk.
- Expand baselines and coverage: include a semantic schema sanitizer (learned classifier or LLM-based judge over literals), grammar-level mitigations inspired by related code-grammar work, and full cross-model reporting for all baselines in Table 1. Consider adaptive adversaries responding to placeholders, including multi-lingual and obfuscated payloads.
- Add runtime/latency profiling for the sanitization step on large schemas, with per-stage breakdown (traversal, pattern matching, replacement). Production relevance claims would be more convincing with p50/p95 overheads.
- Clarify placeholder restoration policy. If restoration is used, specify safe gating mechanisms so harmful content is not re-injected downstream. Otherwise, state clearly that restoration is disabled in high-safety modes and quantify utility impact without restoration.

Typos and minor issues:
- Section 4.2: “completely neutralizing the EnumAttack” conflicts with Section 4.6’s residual ASR under chunking. Rephrase to “completely neutralizing the standard EnumAttack variant evaluated in Table 1.”
- Table 1: Use consistent reporting across both models for all baselines; avoid dashes where results are central to a conclusion.
- Table 2: Fill in missing validity/compliance deltas or explain why they are omitted. Consider adding confidence intervals.
- Section 3.3: “matches instruction-like patterns (imperative verbs, affirmative prefixes such as 'Sure,' or 'Step 1')” — list the exact set; consider multilingual analogues or note the scope explicitly.
- Figures: Add captions that define axes precisely and indicate whether benign cost combines modification and rejection or if separate measures are used.

Criteria to raise my score:
- Add the expanded baselines and complete cross-model results in Table 1, plus sensitivity analyses and exact rules for the suspicion function.
- Provide dual safety metrics with and without counting schema-forced literals; demonstrate consistent risk reduction under the stricter metric.
- Include runtime overhead measurements and demonstrate robustness to multilingual and obfuscated payloads. Evidence that chunked attacks are at least partially mitigated by augmented heuristics or simple aggregation would also help.

## Confidence
3: Reasonably confident but not fully verified — I have a good feel for this area and checked the paper closely, but details like exact regex inventories and evaluation protocols were not fully specified, leaving room for misunderstanding.

## Soundness
2.5: Between Poor and Acceptable — The core idea is plausible and some experiments support it, but incomplete baselines, metric choices that may undercount risk, and missing sensitivity analyses weaken the empirical case.

## Excitement
2.5: Between potentially interesting and interesting — Practical appeal and a neat, low-friction defense, but the simplicity of the heuristic and the clear bypass via chunking reduce excitement for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The approach is simple and practical with encouraging results against one attack variant, and the ablation helps isolate the key vector. However, baseline coverage, metric design, and robustness analyses are not yet at a main-venue standard, and the chunked-attack bypass undercuts the headline claim. With the suggested additions and calibrated claims, this could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges a key limitation: defense failure on chunked payloads (Figure 3). Additional limitations to discuss:
- Language scope: the suspicion function appears tailored to English and whitespace-sensitive payloads.
- Possible false sense of security if placeholders are restored downstream without safety checks.
- Dual use: while the work is defensive, publishing bypass analysis helps attackers; emphasize responsible disclosure and mitigations.
On societal impact, a training-free mitigation that reduces risk in production schema-constrained systems is positive. Risks include overreliance on heuristics and potential silent dropping or alteration of legitimate schema values that carry important semantics; operators should be warned and offered auditing tools.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The method is simple and code is claimed to be available, but evaluation specifics (pattern lists, thresholds, scoring that excludes literals) and missing baselines hinder exact reproduction.

## Datasets
1: No usable datasets submitted. The paper does not release new datasets; it relies on existing ones.

## Software
3: Potentially useful. If the code indeed implements the pipeline with configuration hooks for thresholds and pattern lists, it will be handy for practitioners, but more documentation and benchmarks are needed for broad adoption.