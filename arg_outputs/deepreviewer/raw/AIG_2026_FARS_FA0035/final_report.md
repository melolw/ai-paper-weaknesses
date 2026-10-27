## Summary
This paper presents LASCon (Loop-Aware Scratchpad Condensation), a training-free scaffold for terminal agents that addresses context management challenges through two modules: a Deterministic CLI Condenser (DCC) for rule-based observation compression and a Progress-Conditioned Loop Controller (PLC) for preventing unproductive action repetition. On Terminal-Bench 2.0 with Qwen3-32B, LASCon achieves 68.8% completion rate (+21.2pp over the OpenHands default baseline of 47.5%), while eliminating all timeout failures.

The paper's core empirical finding is that structured deterministic condensation (DCC) alone achieves 70.0% completion, suggesting that preserving CLI-specific tokens (exit codes, error lines, canonicalized commands) provides higher information density than LLM-based summarization for terminal tasks. PLC serves as a conservative safety net with a 0.12% block rate and zero deadlock events, as loop-induced failures prove rare (2.5% in baseline) and addressable through prompting alone.

The strongest aspect of this work is its clear, deployable method design and honest empirical analysis—including the counterintuitive finding that DCC-Only outperforms the full LASCon system and the acknowledgment of the context window confound (40K vs 131K tokens) between experimental conditions. The primary limitation is that this context window confound severely limits the validity of component-level causal claims, as ablation variants use 3× more context budget than the full system. The paper also overlaps with prior work on observation masking (Lindenbauer et al., 2025), and the incremental novelty of deterministic extraction over simple masking should be more explicitly articulated.

## Strengths
1. **Clear, deployable method design:** LASCon is a training-free scaffold that can be deployed as a drop-in replacement for OpenHands components without fine-tuning. The DCC module's rule-based extraction (5 specific fields) and PLC module's conservative parameters are clearly specified and reproducible.

2. **Honest empirical analysis:** The paper courageously reports counterintuitive findings—that DCC-Only (70.0%) outperforms LASCon Full (68.8%) and that loop-induced failures are rare (2.5%). The authors explicitly acknowledge the context window confound (40K vs 131K) and its impact on interpretation, which demonstrates scientific integrity.

3. **Practical impact:** Eliminating all timeout failures (0 vs 36 in baseline) is a highly practical improvement for terminal agent deployment. The +21.2pp completion improvement over the OpenHands default is substantial and addresses a real pain point in long-horizon CLI tasks.

4. **Well-structured scratchpad mechanism:** The structured scratchpad (GOAL, CWD, RECENT COMMANDS, FILES EDITED, DO NOT REPEAT, TEST SUMMARY) provides a clean, high-density information format that is intuitively aligned with CLI agent needs.

5. **Plenty of negative evidence analysis:** The paper's analysis that PLC is primarily a safety net rather than a primary mechanism is valuable for the field. It helps calibrate community expectations about the importance of loop detection vs. context management.

## Weaknesses
1. **Context window confound limits component-level causal claims (Major/Fatal risk):** The most significant weakness is that the main LASCon Full condition uses a 40K token context limit, while ablation variants (DCC-Only, PLC-Only) use 131K tokens. This 3× difference confounds all component comparisons. The claim that "DCC alone achieves 70.0% completion, demonstrating that structured context management is the primary driver" is not supported when the component has 3× more context budget than the full system. DCC-Only could be superior simply because of the larger context window, not because deterministic condensation is inherently better.

2. **Overclaimed problem severity for loop detection (Major):** The method section (Section 3.3) opens with "A common failure mode in CLI agents is unproductive repetition," which is directly contradicted by the paper's own experimental findings: loop-induced failures are only 2.5% in the baseline, and the loop-aware prompt alone eliminates them. Presenting loop detection as a "common" problem undermines credibility when the data shows it is rare. The paper should have framed PLC as a safety net from the method section onward, not as a response to a common failure mode.

3. **Novelty overlap with observation masking (Lindenbauer et al., 2025) is not sufficiently differentiated (Major):** The DCC module's core idea—deterministic extraction of structured information from CLI outputs—overlaps significantly with the finding that "simple observation masking is as efficient as LLM summarization" (Lindenbauer et al., 2025). The incremental novelty (preserving exact CLI tokens vs. simple masking) is stated but not demonstrated. Without a direct comparison to observation masking as a baseline, it is unclear how much of DCC's improvement comes from token preservation vs. simply avoiding the cost of LLM summarization.

4. **Docker unavailability limits evaluation validity (Major):** The paper states that "Docker unavailability prevented Pass@1 evaluation with automated test verification," meaning completion rate serves as a proxy metric without automated correctness verification. This is a significant limitation for a paper evaluating terminal agents, as completion rate may not correlate with task correctness.

5. **Truncation policy (first/last 10 lines) lacks justification (Minor):** The DCC truncation heuristic of preserving the first and last 10 lines is not motivated. For very long outputs (e.g., large file listings, deep stack traces), the discarded middle section may contain critical diagnostic information. No sensitivity analysis is provided for this parameter choice.

## Key Issues
| Issue | Risk Level | Root Cause | Impact | Priority |
|-------|------------|------------|--------|----------|
| Context window confound (40K vs 131K) | Critical | Different context budgets for main condition vs ablation variants | Invalidates component-level causal claims; DCC-Only > Full comparison is uninterpretable | P0 |
| Loop detection overclaim in Method | Major | "Common failure mode" contradicted by own data (2.5%) | Undermines credibility; readers lose trust when method section contradicts results | P0 |
| Docker unavailability limits evaluation | Major | No Pass@1 with automated test verification | Completion rate may not correlate with correctness; evaluation validity is reduced | P1 |
| Novelty overlap with observation masking (Lindenbauer 2025) | Major | DCC's core idea (deterministic extraction) overlaps with masking | Without masking baseline, incremental novelty is unclear | P1 |
| Truncation policy lacks justification | Minor | First/last 10 lines chosen heuristically without analysis | Reproducibility risk; parameter choice appears arbitrary | P2 |

**Ranking rationale:** The context window confound is the single most impactful issue because it directly affects whether component-level conclusions are valid. The loop overclaim is also high-risk because it creates a credibility gap between the method motivation and experimental findings. Docker unavailability is a validity concern but does not necessarily invalidate the relative comparisons. Novelty overlap requires addressing in revision but does not change the empirical contribution.

## Actionable Suggestions
1. **Add a controlled comparison with matched context windows (P0-Must):** Re-run DCC-Only with 40K context (matching LASCon Full) to provide a fair component comparison. If re-running is not feasible, explicitly bound all component synergy claims to "under the current experimental settings" and add a sensitivity analysis paragraph.

2. **Rewrite PLC method section opening (P0-Must):** Replace "A common failure mode in CLI agents is unproductive repetition" with "While loop-induced failures are rare in practice (2.5% in our baseline), when they do occur they can stall execution indefinitely." This aligns the method section with the paper's own findings.

3. **Add observation masking as a baseline comparison (P1-Must):** Include a simple observation masking baseline (à la Lindenbauer et al., 2025) to isolate how much of DCC's improvement comes from structured token preservation vs. simply avoiding LLM summarization cost. This directly addresses the novelty overlap concern.

4. **Add state versioning overhead estimate to Appendix (P1-Nice-to-have):** Report measured overhead of SHA-256 state versioning per step (e.g., "State versioning adds <50 ms per step on our evaluation tasks"). This strengthens deployment feasibility claims.

5. **Add truncation sensitivity or rationale (P2-Nice-to-have):** Either add a short ablation on truncation length (e.g., 5, 10, 20 lines) in the appendix, or add one sentence in the main text explaining the heuristic rationale for choosing 10 lines.

6. **Move context window confound to Experimental Setup section (P1-Must):** Currently the confound is mentioned in Section 4.3 (Ablation Study). Move this acknowledgment to Section 4.1 (Experimental Setup) so it is front-loaded and readers can properly interpret all results.

7. **Strengthen abstract with counterintuitive finding (P1-Must):** Reposition the abstract to lead with the DCC-Only 70.0% result as the primary finding, then present LASCon Full as a conservative integration that includes safety guarantees. Acknowledge the context window confound in one sentence.

8. **Add practical value sentence to Introduction opening (P2-Nice-to-have):** After the first sentence about CLI agents, add one sentence explaining the practical importance (e.g., automating repetitive sysadmin work, debugging assistance) to establish stakes.

## Storyline Options + Writing Outlines
### Recommended Storyline: "CLI-Specific Token Preservation as the Key to Context Management"

The current introduction follows a standard Problem -> Gap -> Solution structure but presents two problems (context overflow + loop repetition) with roughly equal weight, even though the experiments show loop repetition is rare. A stronger narrative would foreground the DCC finding and frame PLC as a complementary safety net.

**Storyline Option A (Recommended): "Structured tokens beat summaries"**
Big Picture: Terminal agents face context overflow in long-horizon tasks.
Gap: LLM-based summarization discards exact CLI tokens (error messages, exit codes) critical for task completion; simple masking also fails to preserve structured metadata.
Solution: DCC extracts and preserves these exact tokens in a compact, deterministic format. PLC provides a lightweight safety net for rare edge cases.
Evidence: +21.2pp completion improvement; DCC-Only achieves 70.0% (highest among variants); all timeouts eliminated.
Contribution: Training-free CLI-aware condensation that outperforms both LLM summarization and simple masking on Terminal-Bench 2.0.

### Abstract Outline (complete)

- **S1 (Problem & Domain):** Long-horizon terminal agents accumulate growing observation histories that fill context windows, leading to timeout failures and degraded task completion.
- **S2 (Significance/Challenge):** CLI environments require exact tokens (error messages, exit codes, file paths) for task completion, making lossy summarization suboptimal.
- **S3 (Prior Gap):** Existing approaches rely on LLM-based summarization (risking token loss) or simple observation masking (discarding structured metadata), neither of which preserves the full operational context needed for terminal tasks.
- **S4 (Method):** We present LASCon, combining a Deterministic CLI Condenser (DCC) that extracts structured command-state records with a Progress-Conditioned Loop Controller (PLC) as a safety net for repetitive failures.
- **S5 (Key Result & Bounded Implication):** DCC alone achieves 70.0% completion on Terminal-Bench 2.0 (+22.5pp over baseline), demonstrating that structured token preservation is the primary driver of improvement; the full LASCon system eliminates all timeout failures while maintaining a conservative 0.12% action block rate.

### Introduction Outline (complete)

- **P1 (Big Picture & Stakes):** Introduce LLM agents for CLI tasks (software engineering, sysadmin). Add one sentence on practical value: automating repetitive technical workflows, reducing human workload, improving consistency. State the challenge: long-horizon interactions fill context windows, causing timeouts.
- **P2 (Concrete Gap):** Review prior context management (LLM summarization, observation masking). Explain why both fail for CLI: summarization loses exact tokens; masking discards structured metadata. Acknowledge Lindenbauer et al. (2025) showing masking ≈ summarization, but clarify that CLI needs more than masking. Frame loop detection as a rare but serious edge case.
- **P3 (Solution Intuition):** Present LASCon's two modules. DCC: deterministic extraction of 5 key fields (command, exit code, CWD, errors, truncated output) into a structured scratchpad. PLC: converts loop detection into action-space shaping (blocking + forcing exploration) rather than termination.
- **P4 (Evidence Preview):** Report key results: +21.2pp completion improvement, 0 timeouts, DCC-Only 70.0% as primary driver. Acknowledge context window confound (40K vs 131K) briefly.
- **P5 (Contribution Summary):** Three explicit contributions: (1) LASCon scaffold, (2) Empirical finding on DCC's primary role, (3) Analysis showing PLC as safety net.

## Priority Revision Plan
This plan is organized by priority (P0 = publication-critical, P1 = significant improvement, P2 = nice-to-have) and estimated effort.

### P0 — Must Fix Before Submission

| Action | Effort | Expected Impact |
|--------|--------|-----------------|
| **1. Re-run DCC-Only with 40K context** to provide fair comparison with LASCon Full. If not feasible, bound all component claims and add explicit interpretation limitations. | High (re-run experiments) / Medium (rewrite only) | Resolves the critical validity issue; makes component conclusions defensible. |
| **2. Rewrite PLC method section opening** to frame loop detection as a rare but serious edge case, not a "common failure mode." Align method motivation with experimental findings. | Low (text revision) | Restores credibility gap between method and results. |
| **3. Move context window confound to Experimental Setup (Section 4.1)** so it is front-loaded, not buried in the ablation discussion. | Low (text relocation) | Improves transparency and allows readers to interpret all results correctly from the start. |

### P1 — Should Fix for Stronger Submission

| Action | Effort | Expected Impact |
|--------|--------|-----------------|
| **4. Add observation masking baseline** (Lindenbauer et al., 2025) to isolate structured token preservation vs. simple masking. This directly addresses the novelty overlap concern. | Medium (1-2 days of experiment) | Clarifies incremental novelty of DCC over prior deterministic baselines. |
| **5. Reposition abstract** to lead with DCC-Only 70.0% as the primary finding, acknowledge context window confound, and present LASCon Full as a conservative integration with safety guarantees. | Low (text revision) | Improves abstract accuracy and sets correct reader expectations. |
| **6. Add state versioning overhead estimate** to Appendix A (e.g., "<50 ms per step"). | Low (measure + 1 sentence) | Strengthens deployment feasibility claims. |

### P2 — Nice-to-Have Improvements

| Action | Effort | Expected Impact |
|--------|--------|-----------------|
| **7. Add truncation sensitivity or rationale** (ablation on 5/10/20 lines, or one sentence explaining the heuristic). | Low-Medium | Addresses reproducibility concern for DCC parameters. |
| **8. Add practical value sentence to Introduction opening** to establish stakes for CLI agents. | Low (1 sentence) | Improves reader engagement and narrative flow. |
| **9. Add one model generalization check** (e.g., run LASCon on one additional model like Llama-3-70B) to support the "deployable with any LLM backend" claim. | Medium (1 day) | Strengthens generalization claims. |

### Execution Sequence

```text
Stage 1 (today): Rewrite PLC method opening + move confound to setup + reposition abstract
Stage 2 (this week): Re-run DCC-Only with 40K context OR bound component claims if re-run not feasible
Stage 3 (next week): Add observation masking baseline if resources allow
Stage 4 (before submission): Add overhead estimate + truncation rationale + introduction polish
```

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|-------|---------|--------------|-----------------|-------------------|
| E1: Main Results | LASCon improves completion rate over OpenHands default | Terminal-Bench 2.0 (80 tasks), Qwen3-32B, 40K context | Completion%, Timeout, Fail, Loop%, Tokens, Tool Calls | 68.8% vs 47.5% (+21.2pp); 0 timeouts vs 36 | Core claim supported | Docker unavailability; no Pass@1; 40K context |
| E2: Loop Prompt | Loop-aware prompt eliminates loop failures | Same as E1, + loop prompt, 40K context | Completion%, Timeout, Loop% | 51.2% (+3.7pp); 0% loop failures | Prompt alone handles loops | Small improvement; still 32 timeouts |
| E3: DCC-Only Ablation | DCC is primary driver of improvement | DCC condenser, no PLC, 131K context | Completion%, Timeout | 70.0% (+18.8pp over prompt); 0 timeouts | DCC provides gains | **131K context confounds vs Full** |
| E4: PLC-Only Ablation | PLC effectiveness isolated | PLC blocking, no DCC, 131K context | Completion%, Timeout | 75.0% (+23.8pp over prompt); 19 timeouts | PLC effective with large context | **131K context confounds vs Full** |
| E5: PLC Safety | PLC does not over-block | Condition C (Full), 806 actions | Block rate, Deadlocks | 0.12% block rate; 0 deadlocks | PLC is conservative safety net | Only tested on one model |

### (b) Research-Theme Gap Diagnosis

- **New knowledge gap:** The claim that "deterministic condensation outperforms LLM summarization for CLI contexts" is partially confounded by the context window difference and overlaps with the observation-masking finding (Lindenbauer et al., 2025). A controlled comparison with masking would clarify the incremental contribution.
- **Reproducibility/reusability gap:** Truncation parameters (10 lines) lack sensitivity analysis. State versioning overhead is not reported. Docker unavailability limits independent verification.
- **Impact on practice gap:** Only one model (Qwen3-32B) is tested. The "deployable with any LLM backend" claim needs multi-model validation.

### (c) Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost/Time | Expected Gain |
|--------------|-----------|---------------|-------------------|---------|------------------|----------------|---------------|
| Component synergy (E3/E4) | DCC provides gains independent of context window | Re-run DCC-Only with 40K context | LASCon Full (40K), Baseline A (40K) | Completion%, Timeout | DCC-Only 40K comparable to Full 40K | 1 day compute | Resolves critical confound |
| Novelty vs masking | DCC improves beyond simple masking | Add observation masking baseline (Lindenbauer 2025) | Masking (40K), DCC-Only (40K), Full (40K) | Completion% | DCC significantly > masking | 1 day compute | Isolates token preservation value |
| Model generalization | LASCon works across model families | Run Full on Llama-3-70B or Claude-3.5-sonnet | Same baselines on same model | Completion%, Timeout | +15pp improvement replicated | 1-2 days compute | Validates "any LLM" claim |
| Truncation sensitivity | Truncation length affects completion | Run DCC with 5/10/15/20 lines | 10-line baseline | Completion% | Identify optimal range | 0.5 day compute | Justifies parameter choice |
| Task-level failure analysis | Understand where DCC succeeds/fails | Categorize failures by task type (file ops, config, debug) | - | Completion by category | Identifies strength/weakness patterns | Analysis only | Improves limitation discussion |

### (d) Traceability

Every proposed experiment maps to at least one unresolved core claim: E3/E4 confound (component synergy), masking overlap (novelty), single-model testing (generalization), truncation arbitrariness (reproducibility).

### ASCII Diagram — Experiment Upgrade Plan

```text
P0: DCC-Only @ 40K context
   -> Resolves: Component synergy confound
   -> Maps to: E3, E4 validity

P1: Observation Masking Baseline @ 40K
   -> Resolves: Novelty vs Lindenbauer 2025
   -> Maps to: Incremental contribution claim

P1: Multi-model validation
   -> Resolves: "any LLM" generalization claim
   -> Maps to: Practical deployment claims

P2: Truncation sensitivity (5/10/15/20)
   -> Resolves: Parameter justification
   -> Maps to: Reproducibility

P2: Task-category failure analysis
   -> Resolves: Limitation specificity
   -> Maps to: Conclusion/Limitations section
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|---------------------|-----|------------|----------------------|
| C1 | LASCon: training-free scaffold combining DCC + PLC, deployable with any LLM without fine-tuning | [1], [3] | partially_overlapping | Scaffold integration is novel, but DCC's deterministic extraction overlaps with masking [1] and TACT [3] addresses agent drift in similar settings. PLC's action-space shaping is a modest extension of existing stuck detection. | Medium | Clarify that novelty is in the CLI-specific extraction design and the combined deployment, not in the general idea of deterministic context management. |
| C2 | DCC alone achieves 70.0% completion, demonstrating deterministic condensation outperforms LLM summarization for CLI | [1] | partially_overlapping | Lindenbauer et al. [1] already shows masking matches LLM summarization. DCC goes beyond masking by preserving structured tokens, but this incremental value is not demonstrated against a masking baseline. | Medium | Reposition as "DCC preserves structured CLI tokens beyond simple masking," pending controlled comparison. |
| C3 | Loop-induced failures are rare (2.5%) and addressable by prompting; PLC serves as conservative safety net | [3] | supported | This is an empirical analysis finding unique to the paper's evaluation. TACT [3] detects drift at the activation level but does not report loop prevalence analysis. | High | None needed; this is a valid empirical contribution. |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|----------------|-------------|----------------------|-------------------|------------------------|-------------------|
| Root: Agent Context Management | Branch 1: Compression Strategy | | | | |
| | Leaf 1.1: LLM-based summarization | [4] | Summarization preserves semantic content; LLM can be trusted to keep relevant info | DCC rejects LLM summarization for CLI due to token loss risk | Low (paper explicitly differentiates) |
| | Leaf 1.2: Deterministic masking | [1] | Simply omitting older observations is sufficient | DCC preserves structured tokens (exit codes, errors) that masking discards | **High** — overlap if masking baseline not compared |
| | Leaf 1.3: Learned adaptive pruning | [5], [6] | Learned policies can identify important context segments | DCC uses no training; rules are hand-crafted for CLI structure | Medium (different paradigm but same goal) |
| Root: Agent Drift Mitigation | Branch 2: Drift Detection | | | | |
| | Leaf 2.1: Stuck detection + termination | [4] | Detecting repetition → terminate execution | PLC blocks specific actions + forces exploration instead of termination | Medium |
| | Leaf 2.2: Activation steering | [3] | Drift manifests in model activations; can be corrected via steering | PLC operates at the action level, not the activation level | Low (different intervention point) |
| Root: Evaluation Benchmark | Branch 3: Terminal Agent Evaluation | | | | |
| | Leaf 3.1: Terminal-Bench evaluation | [2] | Hard, realistic CLI tasks with outcome verification | Paper evaluates on Terminal-Bench 2.0 with a specific model | Low (standard benchmark usage) |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|------------------|-------------------------|
| [1] | SWE-agent on SWE-bench; OpenHands scaffold | Simple observation masking (remove verbose outputs) | Both show deterministic approaches match/beating LLM summarization | DCC preserves structured CLI tokens (exit codes, errors) that masking discards | **Major**: Without masking baseline, DCC's incremental value is unclear |
| [2] | Terminal-Bench 2.0 benchmark creation | Benchmark design and task curation | Same evaluation benchmark | Paper uses Terminal-Bench for method evaluation | No impact (benchmark usage, not method overlap) |
| [3] | SWE-bench, Terminal-Bench 2.0, CLAW-Eval | Activation steering to correct overthinking/overacting | Both address agent drift on Terminal-Bench 2.0 | TACT operates on model activations; PLC operates on action signatures | Low (complementary approaches, different levels) |
| [5] | SWE-bench for coding agents | Self-adaptive pruning learned during execution | Both reduce context length for agents | Learned vs. deterministic; SWE-Pruner requires training | Medium (different paradigm but same goal) |
| [6] | General LLM agents | Selective trajectory retention via learned policy | Both aim to reduce context length | AgentDiet is general; DCC is CLI-specific with rules | Low (different scope) |

### Contribution-level Novelty Conclusion

C1 (LASCon scaffold) is `partially_overlapping`: the combined integration is novel, but the individual components (deterministic extraction + action blocking) build on established ideas. C2 (DCC superiority) is `partially_overlapping`: the core finding that deterministic approaches can outperform LLM summarization for CLI tasks overlaps significantly with Lindenbauer et al. [1], who show that simple masking matches LLM summarization. The residual novelty—structured token preservation beyond masking—requires a controlled masking baseline to be defensible. C3 (loop analysis) is `supported`: the empirical finding that loop-induced failures are rare and addressable by prompting is a unique contribution of this paper.

**Required repositioning for C2:** Reframe as "DCC preserves structured CLI tokens (exit codes, error lines, canonicalized commands) that simple observation masking would discard, providing higher information density per token for terminal tasks." This narrowing is defensible pending a masking baseline comparison.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Related Work Taxonomy (Root: Agent Context Management & Drift Mitigation)
├── Branch 1: Compression Strategy
│   ├── Leaf 1.1: LLM-based summarization [4]
│   ├── Leaf 1.2: Deterministic masking [1] <<< OVERLAP RISK with DCC
│   └── Leaf 1.3: Learned adaptive pruning [5][6]
├── Branch 2: Drift Detection & Mitigation
│   ├── Leaf 2.1: Stuck detection + termination [4]
│   ├── Leaf 2.2: Activation steering [3]
│   └── Leaf 2.3: Action-space shaping (this paper) <<< RESIDUAL NOVELTY
└── Branch 3: Terminal Agent Evaluation
    └── Leaf 3.1: Terminal-Bench benchmark [2]

LASCon Positioning:
  - Between Leaf 1.2 (masking) and Leaf 1.1 (summarization): preserves more than masking,
    but deterministic like masking
  - Between Leaf 2.1 (termination) and Leaf 2.2 (steering): blocks actions like 2.1,
    but at action level not activation level
  - Value solved: CLI-specific token preservation + conservative safety net for terminal agents
```

### ASCII Diagram — Paper Structure & Evidence Map

```text
[Claim: DCC improves completion by preserving CLI tokens]
    -> [Evidence: DCC-Only 70.0% > Baseline 47.5%]
    -> [Gap: 131K context confounds vs Full 40K]
    -> [Gap: No masking baseline comparison]
    -> [Risk: Claim may be reduced to incremental over masking]

[Claim: PLC is a conservative safety net]
    -> [Evidence: 0.12% block rate, 0 deadlocks, 3 loop events]
    -> [Evidence: Prompt alone eliminates 2.5% loop failures]
    -> [Verdict: Supported by data]

[Claim: LASCon eliminates timeouts]
    -> [Evidence: 0 timeouts vs 36 in baseline]
    -> [Verdict: Supported, but Docker unavailability limits correctness verification]
```

### ASCII Diagram — Revision Strategy Roadmap

```text
[Problem: Context window confound (40K vs 131K)]
    -> [Fix: Re-run DCC-Only @ 40K OR bound claims]
    -> [Expected gain: Component conclusions become defensible]

[Problem: Novelty overlap with masking [1]]
    -> [Fix: Add masking baseline + reposition C2 claim]
    -> [Expected gain: Incremental value of token preservation is isolated]

[Problem: Loop overclaim in method section]
    -> [Fix: Rewrite "common failure mode" to "rare edge case"]
    -> [Expected gain: Method motivation aligns with experimental findings]

[Problem: Abstract leads with Full system result]
    -> [Fix: Lead with DCC-Only 70.0% as primary finding]
    -> [Expected gain: Abstract accurately reflects main contribution]
```

## References
[1] The Complexity Trap: Simple Observation Masking Is as Efficient as LLM Summarization for Agent Context Management 2508.21433

[2] Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces 2601.11868

[3] TACT: Mitigating Overthinking and Overacting in Coding Agents via Activation Steering 2605.05980

[4] The OpenHands Software Agent SDK: A Composable and Extensible Foundation for Production Agents 2511.03690

[5] SWE-Pruner: Self-adaptive context pruning for coding agents (no arxiv_id available)

[6] Improving the efficiency of LLM agent systems through trajectory reduction 2509.23586

## Scores
**Final Score: 5.5/10**

**Scoring Rationale:**
- **Research Value (High):** The paper addresses a real and practical problem—context overflow in long-horizon terminal agents. The +21.2pp completion improvement and elimination of all timeout failures represent meaningful practical gains for agent deployment.
- **Novelty (Medium):** The core DCC contribution (deterministic CLI token preservation) partially overlaps with Lindenbauer et al. (2025), who show that simple observation masking matches LLM summarization. The incremental value—structured token preservation beyond masking—is stated but not demonstrated. The PLC action-space shaping and loop analysis provide valid but modest contributions.
- **Validity (Medium-Low):** The context window confound (40K vs 131K tokens) is a critical issue that limits causal interpretation of component contributions. Docker unavailability further limits evaluation completeness. The method section's "common failure mode" overclaim contradicts the paper's own data.
- **Reproducibility (Medium):** The method is clearly specified and deployable as a training-free scaffold. However, truncation parameters lack sensitivity analysis, and state versioning overhead is not reported.

**Post-Revision Target: [7, 8.5]/10**

If the context window confound is resolved (DCC-Only re-run at 40K context for fair comparison), an observation masking baseline is added to isolate token preservation value, and the method section overclaims are corrected, the paper would be significantly stronger. The core DCC contribution would be clearly differentiated from prior masking work, and the empirical findings would be defensible under controlled conditions. The practical impact of eliminating timeout failures and achieving substantial completion improvements would remain well-supported.