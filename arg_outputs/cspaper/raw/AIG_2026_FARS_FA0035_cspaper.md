# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces LASCon, a training-free scaffold for LLM-based terminal agents that targets two issues in long-horizon CLI tasks: loss of critical details during context compression and repetitive, unproductive loops. LASCon includes (1) a Deterministic CLI Condenser (DCC) that replaces LLM summarization with rule-based extraction of command, exit code, working directory, selected error lines, and head/tail output, while offloading full logs to disk, and (2) a Progress-Conditioned Loop Controller (PLC) that detects repeated action-error patterns without state change and temporarily blocks those specific actions. On Terminal-Bench 2.0 with Qwen3-32B, the authors report a 68.8% completion rate and zero timeouts for the full system, with ablations indicating DCC alone achieves 70.0% completion and PLC alone 75.0% (under a larger context window). The paper argues that structured, deterministic condensation is the main driver, and PLC acts as a conservative safety net.

## Summary Of Strengths
- Practical, training-free design: The DCC and PLC are drop-in modules that can be integrated into standard agent stacks (e.g., OpenHands) without finetuning or extra data. This lowers barriers to adoption and facilitates quick testing.
- Strong, clear articulation of the CLI-specific risks of free-form summarization: The paper is persuasive that exact tokens (paths, flags, error strings) are crucial in terminals, and that deterministic extraction can help preserve these.
- Useful ablations and safety stats: The split of OpenHands baseline, prompt-only baseline, DCC-only, PLC-only, and full LASCon provides a basic picture of component roles. PLC’s safety characteristics are quantified in Table 2.
- Clear architecture presentation: Figure 1 concisely shows the LASCon scaffold and the control/data flow between DCC, PLC, and the scratchpad. It makes it easy to see exactly what information is preserved and how loop blocking is triggered.
- Concrete gains on a realistic benchmark: Table 1 shows a large reduction of timeouts and a sizable completion-rate increase over the default OpenHands baseline, which is of practical interest to the agent community.

## Summary Of Weaknesses
1) Confounded experimental comparisons due to different context windows across conditions (major). In Section 4.1 (Page 4–5), the authors state the full LASCon condition used a 40K token limit, while ablations (including PLC-Only and DCC-Only) used 131K. This 3× disparity undermines attribution of improvements and makes it impossible to fairly interpret component efficacy. For example, Table 1 shows PLC-Only at 75.0% completion, outperforming the full system at 68.8%, but the larger window could explain much of this difference. Similarly, DCC-Only achieving 70.0% under 131K vs LASCon at 68.8% under 40K does not allow a clean conclusion about synergy. A uniform context budget is necessary to support the central claims.

2) Over-interpretation of PLC’s role versus prompting and context budget (moderate–major). Section 4.4 (Page 5) and Table 2 (Page 6) show PLC blocked only 1 action out of 806 in the full system, and the loop-aware prompt already eliminates detected loop-induced failures. This suggests that, in the tested regime, PLC adds minimal value beyond prompting and window size. Yet the paper highlights PLC conceptually; the empirical results instead imply its effect is negligible under the chosen settings. A more rigorous study varying PLC thresholds, pattern lengths, and expiry would help quantify when PLC matters.

3) Missing or insufficiently competitive baselines for deterministic or structured context management (moderate). The Related Work cites Lindenbauer et al. (2025) on simple observation masking, LongLLMLingua, and several agent memory/pruning works, but experiments do not include direct baselines that implement rule-based or structured extraction beyond the authors’ DCC and the OpenHands LLM condenser. Given the paper’s central claim that deterministic condensation outperforms LLM summarization for CLI, it is important to include: (a) a strong rule-based masking baseline, (b) a token-budget-matched LongLLMLingua setup, and ideally (c) a learned compression method like ACON or SWE-Pruner with the same context budget.

4) Limited model scope and absence of statistical rigor (moderate). All results are with Qwen3-32B at temperature 0. No results are shown for other models or decoding settings. There are no variance estimates, confidence intervals, or significance tests. Given the magnitude of claimed improvements, even simple nonparametric tests over task-level completions and per-task deltas would add credibility. Cross-model results would test generality.

5) Central claim attribution vs. token usage and tool-call increases (moderate). Table 1 shows higher token usage and more tool calls in the improved conditions. While the paper argues these indicate “productive computation,” the increased budget could itself account for some gains. Without enforcing the same global token budget or per-step cap, it is hard to isolate the contribution of DCC’s information preservation from the effect of simply processing more content and taking more actions.

6) Evaluation limitations and proxy metric (moderate). The paper notes Docker unavailability prevented Pass@1 with automated test verification, using completion status instead. That proxy may not align perfectly with correctness, especially if agents reach “explicit failure” states that are not comparable to verified success. A per-task analysis of where completion labels diverge from test-based verification, or a subset run with full verification, would increase confidence.

7) Ambiguity in DCC extraction details and robustness (minor–moderate). Section 3.2 (Page 3–4) lists regex families and “first/last 10 lines,” but provides no sensitivity analysis. CLI outputs vary widely across tasks and OS environments. It is important to show robustness to: (a) error strings that do not match the chosen regex patterns; (b) long error traces where the crucial line is not in the first/last 10; (c) noisy outputs where canonicalization of commands could remove meaningful whitespace or quoting. An ablation across different extraction hyperparameters would be informative.

8) Lack of retrieval evaluation for offloaded logs (minor–moderate). DCC offloads full logs with pointers, but the paper does not analyze whether the agent actually follows pointers to retrieve needed details, or how often retrieval is necessary. If retrieval is rare, the benefit might be mostly from concise scratchpad structure; if frequent, then the method should quantify latency and success of pointer-following.

9) Scratchpad contributions are not isolated (minor–moderate). The structured scratchpad encodes GOAL, CWD, RECENT_COMMANDS, FILES_EDITED, DO_NOT_REPEAT, TEST_SUMMARY. There is no ablation to identify which fields matter most, or whether a lighter-weight scratchpad plus basic masking would suffice. Since the scratchpad is always visible to the LLM, its token footprint and precise impact on decision quality are worth isolating.

10) Claims about loop rarity may be benchmark-specific (minor). Section 4.4 concludes loop failures are rare and mostly solvable by prompting. That might be a property of Terminal-Bench 2.0 and Qwen3-32B rather than a general statement. Broader evidence across other agent tasks or models would support the generality of this claim.

Figure- and Table-specific critiques and interpretations:
- Figure 1 (Page 3) clarifies that the scratchpad is injected into every LLM context alongside the compact DCC record, and that PLC interposes only when the action signature and error signature repeat without state-version changes. This diagram supports the claim that LASCon is a scaffold around an existing agent. However, the figure also makes visible that PLC relies on a workspace fingerprint; the paper does not report failure cases where meaningful state changes do not alter file metadata (e.g., environment variables, network state), potentially weakening PLC detection. A discussion of such blind spots would be helpful.
- Table 1 (Page 5) is central to the paper’s claims. It shows zero timeouts for DCC-Only and the full system, which supports the argument that structured condensation helps prevent stalls. However, the higher completion for PLC-Only (75.0%) under a 131K context, compared to 68.8% for the full system under 40K, undercuts the takeaway that “DCC alone is the primary driver” unless all conditions are run under identical budgets. The token and tool-call columns further confound interpretation since they are not controlled.
- Table 2 (Page 6) shows a 0.12% block rate for PLC. This supports the claim that PLC is conservative and not over-blocking, but it also indicates negligible direct impact in the tested configuration. It would be useful to include a parallel table for PLC-Only, where PLC’s effect should be more pronounced, to contrast behavior across setups.

## Potentially Missing Related Work
1) Gandhi et al., “Endless Terminals: Scaling RL Environments for Terminal Agents,” 2026 — Directly targets CLI agents and long-horizon interactions. It provides a complementary environment suite for stress-testing designs like DCC/PLC. Suggested addition: Section 2 (Related Work) and Section 4 (Experiments), as a venue for broader evaluation beyond Terminal-Bench 2.0.

2) Shrivastava et al., “ECHO: Terminal Agents Learn World Models for Free,” 2026 — Uses dense supervision from terminal outputs to improve performance on Terminal-Bench 2.0. Highly relevant to leveraging terminal feedback; comparison could clarify whether deterministic condensation complements or competes with learned exploitation of outputs. Suggested addition: Section 2 for positioning, and Section 4 for discussion and, if feasible, a baseline.

3) Zhao et al., “AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications,” 2026 — Introduces a memory benchmark suite for long-horizon tasks. Relevant to analyzing construction vs. retrieval loss in structured condensation and could offer a more principled evaluation of scratchpad efficacy. Suggested addition: Section 2 and a brief discussion in Section 4 about memory evaluation protocols.

4) Hu et al., “Memory in the Age of AI Agents: A Survey,” 2025 — Provides a taxonomy of agent memory mechanisms. Useful for situating LASCon’s scratchpad within broader memory frameworks. Suggested addition: Section 2.

5) Luo et al., “From Storage to Experience: A Survey on the Evolution of LLM Agent Memory Mechanisms,” 2026 — Emphasizes evolution from storage to experience abstraction, directly relevant to analyzing when deterministic condensation helps. Suggested addition: Section 2.

6) Shi et al., “LongCodeZip: Compress Long Context for Code Language Models,” 2025 — Presents importance-aware compression that preserves task-critical tokens under budget constraints. While code-focused, its structured pruning and allocation principles are pertinent baselines/designs for deterministic condensation. Suggested addition: Section 2 and, if possible, an experimental baseline or discussion in Section 4.

7) “ShallowPPL: Investigating Early-Exit Logit Lens for Code Context Compression,” 2026 — Negative result on early-exit scoring for compression. Informative in motivating lightweight but reliable deterministic approaches. Suggested addition: Section 2.

8) “Last-Write-Wins Memory: Isolating Deterministic Overwrite Semantics for Long-Context Conflict Resolution,” 2026 — Speaks to deterministic conflict resolution in long-context memories, aligning with the scratchpad’s predictable structure. Suggested addition: Section 2, with potential mention when describing the scratchpad in Section 3.2–3.4.

9) “Context Bagging: Inference-Time Ensembling for Robust Long-Context QA Under Hard Distractors,” 2026 — Shows inference-time restructuring of context to improve robustness. Could inspire ensemble-style scratchpad or segmented condensation strategies. Suggested addition: Section 2 and a brief mention in Future Work.

10) “Memory Matters More: Event-Centric Memory as a Logic Map for Agent Searching and Reasoning,” 2026 — Event-graph perspective that could generalize DCC’s structured records to richer relational memories for CLI histories. Suggested addition: Section 2 and Future Work.

## Comments Suggestions And Typos
Actionable suggestions:
- Control the context budget across all conditions. Re-run Table 1 with identical context-window limits, fixed per-trajectory token budgets, and matched decoding settings to isolate DCC and PLC effects. This single change would substantially increase the soundness of the core claims.
- Add stronger baselines. Include at least: (a) a robust observation-masking baseline (as per Lindenbauer et al., 2025); (b) a token-matched LongLLMLingua run; and (c) a learned compression policy (e.g., ACON or SWE-Pruner) under the same budget. If possible, include one learned baseline fine-tuned or configured for CLI outputs.
- Expand PLC analysis. Present results where PLC parameters are more aggressive (vary W, L, R, T) and environments where state change is not captured by file metadata, highlighting failure modes and recovery. Consider adding a PLC-Only safety table analogous to Table 2.
- Isolate scratchpad contributions. Provide an ablation removing or swapping fields (e.g., remove FILES_EDITED, vary RECENT_COMMANDS history length) and track completion/timeouts/tokens. Also include a variant with a minimal scratchpad plus masking to test whether the structure itself is the main driver.
- Evaluate retrieval usage. Quantify how often offloaded log pointers are followed, whether retrieval changes decisions, and its latency. A micro-study on “errors missed by the regex + recovered via retrieval” would directly validate the design.
- Improve statistical reporting. Add per-task deltas, confidence intervals over completion rates (e.g., bootstrap over tasks), and simple significance tests against baselines.
- Generalize beyond Qwen3-32B. Test at least one other competitive model (e.g., Llama-family or Mistral-family) and a different temperature to probe robustness of the reported gains.

Typos and minor issues:
- Page 1, Abstract: “timeout failures” appears multiple times; acceptable but consider defining the exact stopping criterion earlier in Section 4.1 for clarity.
- Page 2: “loop-induced failures are rare (2.5% in baseline) and eliminated by prompting alone” — consider softening the generality, as this may be benchmark/model-specific.
- Page 4: “The fingerprinter computes SHA-256 hashes over the task workspace (/testbed)” — maybe specify whether symlinks, device files, or environment variables are considered; current text implies only file metadata.
- Page 5, Table 1 caption: “Best results in bold.” Only PLC-Only has best completion, but this is under a different context window; consider clarifying the confound directly in the caption.
- Ensure consistent naming: “execute_bash” vs “execute_bash tool calls” is fine; just keep capitalization uniform.

Criteria that could raise my score:
- A revised Table 1 with identical context budgets and token limits across all conditions, adding the baselines listed above, and reporting confidence intervals/significance.
- Additional model(s) and a short per-task analysis, including Pass@1 with Docker-based verification on at least a substantiated subset.
- An ablation on DCC hyperparameters and a PLC parameter sweep showing when PLC contributes beyond prompting.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and checked key claims but cannot fully validate the empirical design given the confounded comparisons and missing baselines.

## Soundness
3: Acceptable — The paper provides initial support for the main claims, but the context-window confound and missing competitive baselines weaken the empirical case. Additional controlled experiments would likely move this to 3.5–4.

## Excitement
3.0: Interesting — The scaffold is practical and the CLI-centric condensation perspective is useful, but the current evaluation does not fully establish the contribution.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. Justification: The idea is practical and relevant, the architecture is clear (Figure 1), results show promise (Table 1, Table 2), and code availability improves reproducibility. However, the core empirical evidence is weakened by major confounds, limited baselines, and single-model scope. In its current form, it fits Findings rather than the main conference; with uniform-budget experiments and stronger comparisons, it could be reconsidered for the main track.

## Best Paper Justification
N/A (not applicable; score is not in award range).

## Limitations And Societal Impact
The paper’s limitations section acknowledges the lack of Docker-based Pass@1 evaluation, single-model scope, and context-window confound, which are indeed central. Societal risks are limited since the method targets agent scaffolding; however, improved CLI agents can implicate dual-use risks (e.g., automating system changes). It would be beneficial to note:
- Potential misuse if agents are deployed with blocking policies that mask harmful repeated actions rather than terminate safely.
- The need for guardrails when agents write to system directories or handle permissions, since DCC preserves exact tokens that might include sensitive paths or credentials appearing in logs.
- Inclusion guidance for non-English or localized CLI environments where regex-based error extraction may fail; documenting language coverage and failure modes would be helpful.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — The method is deterministic and described at a reasonable level of detail, and the paper claims public code. Some parameter choices and environment details would still benefit from fuller documentation, and exact replication of benchmark runs will require the standardized setup.

## Datasets
1: No usable datasets submitted. The paper does not introduce a new dataset.

## Software
4: Useful — If released as claimed, the scaffold will likely be useful to others building CLI agents, particularly as a baseline for deterministic context management.