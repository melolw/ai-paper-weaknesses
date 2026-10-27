## Summary
This paper proposes Selective DeLex-JSON, a training-free defense against control-plane jailbreaks in structured-output LLM APIs. The core idea is to intercept JSON schemas before constrained decoding, identify suspicious forced enum/const literals using a conjunction-based heuristic (length > 20 characters, contains whitespace, matches instruction-like patterns), and replace flagged literals with opaque placeholders. The defense achieves 0% HarmBench Attack Success Rate on both Llama-3.1-8B and Qwen2.5-7B, Pareto-dominating the Reject-Only baseline by reducing benign schema modification from 4.4% to 1.1%. The paper honestly acknowledges a key limitation: chunked-payload attacks that distribute harmful content across short literals evade the heuristic.

**Research value:** The paper addresses a genuinely emerging attack surface (control-plane jailbreaks via schema manipulation) with a lightweight, production-viable defense. The schema sanitization paradigm is novel within this specific setting, and the conjunction-based heuristic design is pragmatically effective.

**Core concerns:** (1) The suspicion function's hyperparameters (20-character threshold, imperative verb list) lack derivation justification. (2) Reproducibility details are incomplete (seed count, variance reporting, HarmBench classifier configuration). (3) The "first defense" novelty claim requires tighter scoping. (4) The Pareto-dominance claim is over-generalized relative to Input Guard. (5) No latency/overhead measurement supports the deployment-readiness claim.

## Strengths
1. **Novel Attack Surface Focus:** The paper correctly identifies and targets an under-explored control-plane jailbreak vector (embedding harmful payloads in forced enum/const literals) that bypasses traditional prompt-level defenses. This is a timely and practically relevant contribution.
2. **Elegant and Lightweight Design:** The conjunction-based suspicion heuristic (requiring 2 out of 3 criteria: length, whitespace, imperative patterns) is simple, interpretable, and computationally negligible. The placeholder replacement strategy preserves schema structural validity, which is critical for constrained decoding engines.
3. **Honest Limitation Reporting:** The authors proactively analyze and report the chunked-payload attack vulnerability (Section 4.6), honestly demonstrating that syntactic-level defenses have clear boundaries. This transparency significantly enhances scientific credibility.
4. **Clean Empirical Validation:** The ablation study effectively isolates the attack vector (Strip-Only achieves identical 22% ASR to No Defense) and validates the heuristic's selectivity (Delex-All incurs 35.5% modification vs. 1.1% for the full method). The utility preservation metrics on JSON-SchemaBench (8,825 schemas) provide strong evidence that the defense is production-viable.
5. **Clear Narrative Structure:** The paper follows a logical progression from problem definition to method intuition to empirical validation. The introduction clearly answers what is missing in prior work, what is solved, and why the approach is suitable.

## Weaknesses
1. **Unjustified Heuristic Hyperparameters (Major):** The conjunction-based suspicion function is the core novelty, yet the specific design choices lack empirical justification. The 20-character length threshold is presented without derivation (e.g., is it the 99th percentile of benign enum lengths?). The "imperative verbs" pattern matching is vaguely defined (predefined list? regex? POS tagging?). Without these details, the heuristic risks being viewed as handcrafted magic numbers, reducing reproducibility and generalizability confidence.
2. **Incomplete Reproducibility Reporting (Major):** The experimental setup does not report the number of random seeds, variance/standard deviation, or HarmBench classifier configuration (single judge vs. ensemble). The 0% ASR claim on HarmBench and the 2.6% residual on StrongREJECT cannot be statistically validated without multi-seed variance reporting. This is a critical gap for an empirical security paper.
3. **Over-Scoped Novelty Claims (Major):** The related work section claims "Our work presents the first defense specifically targeting control-plane jailbreaks." This strong first-claim is at risk because the manuscript does not survey alternative defense paradigms (e.g., schema validation LLMs, policy-aware decoders) that might address similar risks. The claim requires tighter scoping ("first heuristic-based schema sanitization defense" or "to our knowledge, first training-free defense via delexicalization").
4. **Over-Generalized Pareto-Dominance (Minor):** The manuscript states DeLex-JSON "Pareto-dominates existing defenses" (plural). However, Input Guard achieves 0% benign cost, meaning it is not Pareto-dominated by DeLex-JSON (which has 1.1% benign cost). DeLex-JSON only Pareto-dominates the Reject-Only baseline. This overstatement should be corrected to maintain scientific precision.
5. **Missing Operational Overhead Metrics (Minor):** The abstract and introduction claim the defense is "immediately deployable" with "no additional inference overhead." However, no latency, throughput, or memory overhead measurements are reported. While schema parsing is likely negligible, asserting zero overhead without empirical validation is scientifically imprecise.
6. **Missing Per-Criterion Ablation (Minor):** The ablation study compares Strip-Only, Delex-All, and the full method, but does not isolate the individual contribution of each suspicion criterion (length, whitespace, imperative verbs). A per-criterion breakdown would clarify which signals are most important for false-positive reduction vs. attack recall, strengthening the heuristic design narrative.

## Key Issues
| Issue | Risk Level | Root Cause | Impact on Validity/Value | Confidence |
|---|---|---|---|---|
| Heuristic hyperparameters (20-char threshold, verb list) unjustified | Major | Design choices presented without empirical derivation or implementation specification | Reduces reproducibility; heuristic may be viewed as arbitrary | High |
| No multi-seed variance reporting for ASR results | Major | Experimental setup omits seed count and statistical reporting | 0% ASR claim cannot be statistically validated; reviewer confidence undermined | High |
| "First defense" claim lacks scoping | Major | Related work does not survey all potential control-plane defense paradigms | Novelty claim at risk of being challenged if other schema-sanitization methods exist | Medium |
| Pareto-dominance over-generalized | Minor | Claim applies to "existing defenses" (plural) but only dominates Reject-Only | Scientific imprecision; Input Guard is not Pareto-dominated | High |
| No latency/overhead measurement | Minor | Deployment claim without operational metrics | Production-readiness assertion is unverifiable | Medium |
| Missing per-criterion ablation for suspicion function | Minor | Ablation isolates Strip-Only vs. Delex-All but not individual criteria | Limits interpretability of heuristic design choices | High |

**Ranked Top-3 by Severity × Research-Value Impact:**
1. Heuristic hyperparameters unjustified → directly affects core method's reproducibility and defensibility
2. Missing multi-seed variance → directly affects statistical validity of 0% ASR claim
3. Over-scoped novelty claim → directly affects contribution positioning and review decision confidence

## Actionable Suggestions
1. **Justify Heuristic Hyperparameters (Must):** In Section 3.3, explicitly state how the 20-character length threshold was derived (e.g., "derived from the 99th percentile of benign enum lengths in JSON-SchemaBench"). Briefly specify how "instruction-like patterns" are implemented (e.g., "using a predefined list of 50 common imperative verbs provided in Appendix A"). This single addition transforms the heuristic from magic numbers to a reproducible, defensible design.
2. **Add Multi-Seed Variance Reporting (Must):** In Section 4.1 and all result tables, report the number of random seeds used (e.g., 3) and include mean ± standard deviation for ASR and utility metrics. This is essential for validating the statistical reliability of the 0% HarmBench ASR claim.
3. **Scope the Novelty Claim (Must):** In Section 2.3 and the abstract, change "Our work presents the first defense specifically targeting control-plane jailbreaks" to "To our knowledge, our work presents the first training-free, heuristic-based defense specifically targeting control-plane jailbreaks in structured output APIs through schema-level sanitization." This bounds the claim to what is directly evidenced.
4. **Correct the Pareto-Dominance Statement (Must):** Change "Pareto-dominates existing defenses" to "Pareto-dominates the Reject-Only baseline." Input Guard has 0% benign cost and thus is not dominated by DeLex-JSON. Clarify the distinct trade-off point relative to Input Guard in the main text.
5. **Add Per-Criterion Ablation (Nice-to-have):** If space permits, add a small table or paragraph showing the false positive rate and attack recall when each suspicion criterion (length, whitespace, imperative verbs) is applied individually. This strengthens the narrative of why the conjunction design is superior.
6. **Measure and Report Latency Overhead (Nice-to-have):** Add a brief measurement of the schema parsing and sanitization overhead (e.g., "schema processing adds an average of 0.5ms per request, measured on JSON-SchemaBench"). This empirically validates the "immediately deployable" claim.

## Storyline Options + Writing Outlines
### Current Storyline Assessment
The current narrative follows a clean arc: Big Picture (structured-output APIs) → Gap (control-plane jailbreaks) → Solution (DeLex-JSON) → Evidence (0% ASR, 1.1% cost) → Contribution. The main issue is claim overstatement rather than structural breakdown.

### Abstract Outline (complete)
- **S1 (Problem/Domain):** Structured-output APIs enable reliable LLM integration through constrained decoding, but recent work reveals that JSON schema specifications create a new attack surface for control-plane jailbreaks. *(Keep as is; strong opening.)*
- **S2 (Significance/Challenge):** Attackers can embed harmful instructions in forced enum or const values, bypassing safety alignment by forcing models to output malicious content verbatim. *(Keep as is; clear mechanism.)*
- **S3 (Gap):** Existing prompt-level defenses cannot detect harmful intent embedded in schema structures, and output-level escape mechanisms fail under constrained decoding. *(Suggest adding this explicit gap statement, which is currently implicit.)*
- **S4 (Method):** We propose Selective DeLex-JSON, a training-free defense that sanitizes JSON schemas before constrained decoding using a conjunction-based suspicion heuristic and opaque placeholder replacement. *(Keep as is; clear method summary.)*
- **S5 (Result/Implication):** On HarmBench, DeLex-JSON achieves 0% attack success rate on both Llama-3.1-8B and Qwen2.5-7B while incurring only 1.1% benign schema modification rate, Pareto-dominating the Reject-Only baseline. *(Modify: change "Pareto-dominating the Reject-Only baseline" to "while reducing benign cost by 3.3 percentage points compared to Reject-Only.")* Remove the final "immediately deployable" sentence and replace with: "As a schema-level preprocessing step, the defense introduces minimal computational overhead."

### Introduction Outline (complete)
- **P1 (Big Picture):** Structured-output APIs as production infrastructure. *Revision: Add one sentence foreshadowing the security dual-use nature of constrained decoding.*
- **P2 (Gap):** Control-plane jailbreaks exploit the schema specification; prompt-level defenses are insufficient. *Revision: Add one sentence explaining how constrained decoding masks refusal tokens, clarifying the escape-mechanism failure.*
- **P3 (Solution):** DeLex-JSON overview. *Revision: Add one sentence on the design intuition (why heuristic filtering is sufficient for this attack class). Soften "no additional inference overhead."*
- **P4 (Contributions):** Four bullet points. *Revision: Reposition C1 to foreground the heuristic design. Separate empirical validation from conceptual contributions.*

### Recommended Title Revision
Current: "SELECTIVE DELEXICALIZATION TO DEFEND STRUCTURED-OUTPUT LLM APIS FROM CONTROL-PLANE JAILBREAKS"
Suggested: "Defending Structured-Output LLM APIs from Control-Plane Jailbreaks via Selective Schema Delexicalization" *(Problem-first framing; method identity; clearer payoff.)*

## Priority Revision Plan
### P0 — Critical (Must address before resubmission)
1. **Justify suspicion function hyperparameters (Section 3.3):** Add derivation for the 20-character threshold and specify the implementation of the imperative verb pattern matcher. Estimated effort: 1 day of writing + appendix addition.
2. **Add multi-seed variance reporting (Section 4.1, Tables 1-3):** Report mean ± std over ≥3 random seeds for all ASR and utility metrics. Estimated effort: 2-3 days of re-running experiments + table updates.
3. **Scope the novelty claim (Abstract, Section 2.3):** Change "first defense" to "to our knowledge, first training-free, heuristic-based defense via schema sanitization." Estimated effort: 1 day of text revision.

### P1 — Important (Strongly recommended)
4. **Correct Pareto-dominance wording (Abstract, Section 4.2, Conclusion):** Scope to "Pareto-dominates the Reject-Only baseline" and clarify the distinct trade-off relative to Input Guard. Estimated effort: 1 day of text revision.
5. **Add attacker knowledge assumption (Section 3.1):** Explicitly state whether the threat model assumes a black-box or white-box attacker w.r.t. the heuristic parameters. Estimated effort: 1 day of text revision.
6. **Add per-criterion ablation (Section 4.4):** Report individual criterion performance if data is available, or add a supplementary analysis. Estimated effort: 2-3 days of analysis.

### P2 — Nice-to-have (Quality improvement)
7. **Measure latency overhead (Section 4.1):** Add a brief measurement of schema processing time per request. Estimated effort: 1 day of profiling.
8. **Strengthen Related Work 2.1 (Section 2.1):** Add explicit citation of Zhang et al. (2026) to ground the control-plane threat motivation independently. Estimated effort: 1 day of writing.

### Execution Order
Start with P0 items (justification, variance, scoping), then proceed to P1 (wording, threat model, ablation), and finish with P2 (latency, related work polish). This sequence ensures that validity-critical issues are resolved first, followed by narrative improvements.

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1: Main Safety | DeLex-JSON neutralizes EnumAttack better than baselines | Llama-3.1-8B, Qwen2.5-7B; HarmBench (159 behaviors), StrongREJECT (313 prompts); Baselines: No Defense, Input Guard, Reject-Only, Escape-Hatch | ASR (binary) | DeLex-JSON achieves 0% HarmBench ASR, 2.6% StrongREJECT ASR | 0% ASR claim, Pareto dominance | No multi-seed variance reported |
| E2: Utility Preservation | DeLex-JSON preserves schema utility | JSON-SchemaBench (8,825 schemas, 7 subsets) | Mod. Rate, Validity Δ, Compliance Δ | 1.1% mod rate, -0.38pp validity, -0.70pp compliance | Low false positive claim | No per-criterion contribution analysis |
| E3: Ablation | Forced literals are the key attack vector; selective filtering is superior | Variants: Strip-Only, Delex-All, Full DeLex-JSON | ASR, Benign Mod, Validity, Compliance | Strip-Only=22% ASR, Delex-All=35.5% mod, Full=0% ASR + 1.1% mod | Core mechanism validation | Missing per-criterion ablation |
| E4: Pareto Analysis | DeLex-JSON optimizes safety-utility tradeoff | All defense methods plotted | HarmBench ASR vs Benign Cost | DeLex-JSON dominates Reject-Only on tradeoff frontier | Tradeoff claim | Over-generalized to "existing defenses" |
| E5: Chunked Attacks | Chunked payloads evade the heuristic | Chunked-payload variants (≤20 chars) | ASR vs chunk size | 0% detection, 8-14% ASR remains | Honest limitation reporting | No mitigation proposed |

## Novelty Verification & Related-Work Matrix
### Contribution Claims (C1-C3)
- **C1:** Identify forced enum/const literals as the key attack vector in control-plane jailbreaks, validated through ablation showing metadata removal provides no benefit.
- **C2:** Propose Selective DeLex-JSON, a training-free defense using a conjunction-based suspicion heuristic and opaque placeholder replacement, achieving 0% HarmBench ASR with 1.1% benign modification rate.
- **C3:** Demonstrate that DeLex-JSON Pareto-dominates the Reject-Only baseline and characterize the chunked-payload evasion limitation.

### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Forced enum/const literals are the key control-plane attack vector | [1] | supported | Zhang et al. [1] identify the attack vector but do not isolate enum/const vs. metadata; this manuscript's Strip-Only ablation provides unique validation | High | None needed |
| C2 | Schema sanitization via conjunction heuristic + placeholder replacement | [1][3][4] | supported | No prior work proposes schema-level delexicalization as a control-plane defense; SafeDecoding [3] operates at token probability level, Self-Refine [4] at output level | High | Scope "first defense" to "first heuristic-based schema sanitization defense" |
| C3 | Pareto-dominates Reject-Only; characterizes chunked-payload limitation | [5][6] | partially_overlapping | The heuristic-based defense-evasion dynamic aligns with Purple Problem [5] and Guardrail Bypass [6] findings on enforcement limits; the chunked attack analysis is novel but conceptually consistent with prior evasion literature | Medium | Clarify Pareto scope to Reject-Only only |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: LLM Jailbreak Defenses | Branch 1: Prompt-Level Defenses | Leaf 1.1: Input guards / Prompt filtering [2] | Attacker manipulates user prompt | This paper targets schema-level attack, orthogonal to prompt filtering | Low |
| | | Leaf 1.2: Output-aware decoding [3] | Defense modifies token probabilities during generation | SafeDecoding [3] operates at token level; this paper operates at schema preprocessing level | Low |
| | Branch 2: Model-Level Defenses | Leaf 2.1: Self-refinement / Post-processing [4] | Model revises its own output | Self-Refine [4] targets unconstrained output; this paper modifies schema before decoding | Low |
| | Branch 3: Enforcement Analysis | Leaf 3.1: Enforcement limits and evasion [5][6] | Defenses can be bypassed with adaptive attacks | Purple Problem [5] and Guardrail Bypass [6] validate the general difficulty of enforcement; this paper applies these insights to the control-plane setting | Medium |
| | | Leaf 3.2: Defense checkpoint frameworks [7] | Multi-layer defenses have varying strengths | Four-Checkpoint [7] provides a taxonomy; this paper occupies the input-literal checkpoint | Low |
| | Branch 4: Adversarial Baselines | Leaf 4.1: Adversarial attack defenses [8] | Discrete text optimization limits adaptive attacks | Baseline Defenses [8] evaluates perplexity/paraphrase defenses; this paper uses a deterministic heuristic | Low |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] Zhang et al. (2503.24191) | Control-plane jailbreaks via enum/const in JSON schemas | Chain Enum Attack (CDA) | Same attack surface, same EnumAttack evaluation | [1] is the attack paper; this paper is the defense | No novelty risk; [1] is the motivating work |
| [3] Xu et al. (2402.08983) | Jailbreak defense via token probability modification | SafeDecoding: amplify safety disclaimer tokens | Both are training-free defenses | SafeDecoding modifies logits during generation; this paper sanitizes schema before decoding | No overlap in mechanism |
| [4] Kim et al. (2402.15180) | Jailbreak defense via self-refinement | Iterative output revision | Both are training-free | Self-Refine targets unconstrained output; this paper modifies input schema | No overlap in mechanism |
| [5] Kim et al. (2403.14725) | Enforcement limits on simple definitions | Purple Problem: testing enforcement for trivial targets | Both demonstrate enforcement difficulty | Purple Problem uses a different threat model (output filtering); this paper uses schema preprocessing | Conceptual overlap on enforcement limits; validates limitation analysis |
| [6] Hackett et al. (2504.11168) | Guardrail bypass via AML evasion | Character injection + word importance transfer | Both study heuristic defense failure modes | [6] targets prompt injection guards; this paper targets schema heuristics | Low novelty risk; different domain |
| [7] Dhabhi & Thimmaraju (2602.09629) | Defense checkpoint analysis | Four-Checkpoint Framework | Both analyze defense layer strengths | [7] provides taxonomy; this paper implements one checkpoint | No novelty risk |

### Contribution-level Novelty Conclusion
C1 (attack vector identification) is **supported**: Zhang et al. [1] expose the control-plane threat but do not validate that enum/const literals (vs. metadata) are the primary vector. The Strip-Only ablation provides unique empirical support. C2 (schema sanitization via delexicalization) is **supported**: no prior work proposes preprocessing schema literals as a control-plane defense. The conjunction-based heuristic + placeholder replacement paradigm is genuinely novel. C3 (Pareto analysis + limitation characterization) is **partially_overlapping**: the heuristic defense-evasion dynamic is conceptually consistent with Purple Problem [5] and Guardrail Bypass [6], which establish that enforcement mechanisms are fragile under adaptive attacks. The specific application to schema sanitization remains novel, but the broader insight (heuristics can be bypassed) is not.

**Required Repositioning for C3:** Clarify that the Pareto dominance applies specifically to the Reject-Only baseline, and frame the chunked-payload limitation as a natural consequence of the syntactic-level enforcement boundary, consistent with broader findings on heuristic defense fragility [5][6].

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
LLM Jailbreak Defenses (Root)
├── Branch 1: Prompt-Level Defenses
│   ├── Leaf 1.1: Input Guards / Prompt Filtering [2]
│   └── Leaf 1.2: Output-Aware Decoding [3]
├── Branch 2: Model-Level Defenses
│   └── Leaf 2.1: Self-Refinement / Post-Processing [4]
├── Branch 3: Enforcement Analysis (Manuscript sits here)
│   ├── Leaf 3.1: Enforcement Limits & Evasion [5][6]
│   ├── Leaf 3.2: Defense Checkpoint Frameworks [7]
│   └── Leaf 3.3: Schema-Level Sanitization (This Paper)
└── Branch 4: Adversarial Baselines
    └── Leaf 4.1: Baseline Defense Evaluation [8]
```

```text
ASCII Diagram — Paper Structure & Evidence Map
[Problem: Control-plane jailbreaks via schema manipulation] [Page 1, Sec 1.2]
    -> [Evidence: Zhang et al. CDA, EnumAttack 22% ASR] [Page 2, Sec 2.3]
    -> [Gap: Prompt-level defenses insufficient] [Page 1, Sec 1.2]
    -> [Solution: Selective DeLex-JSON (heuristic + placeholder)] [Page 3-4, Sec 3.3-3.4]
    -> [Evidence: 0% ASR, 1.1% benign cost, ablation] [Page 5-6, Sec 4.2-4.4]
    -> [Limitation: Chunked-payload evasion] [Page 6, Sec 4.6]
    -> [Conclusion: Bounded claim with future work direction] [Page 7, Sec 5]
```

```text
ASCII Diagram — Revision Strategy Roadmap
[Problem: Heuristic hyperparameters unjustified]
    -> [Fix: Add 20-char threshold derivation + verb list specification]
    -> [Expected gain: Reproducibility + defensibility of core method]

[Problem: No multi-seed variance]
    -> [Fix: Re-run over 3 seeds, report mean ± std]
    -> [Expected gain: Statistical validity of 0% ASR claim]

[Problem: Over-scoped novelty + Pareto claims]
    -> [Fix: Scope to "first heuristic-based schema sanitization" + "Pareto-dominates Reject-Only"]
    -> [Expected gain: Claim-evidence alignment, reviewer confidence]

[Problem: Missing attacker knowledge assumption]
    -> [Fix: Add black-box vs white-box specification to threat model]
    -> [Expected gain: Clarified robustness boundary for 0% ASR]
```

## References
[1] Output Constraints as Attack Surface: Exploiting Structured Generation to Bypass LLM Safety Mechanisms 2503.24191

[2] Jailbreak Attacks and Defenses Against Large Language Models: A Survey 2407.04295

[3] SafeDecoding: Defending against Jailbreak Attacks via Safety-Aware Decoding 2402.08983

[4] Break the Breakout: Reinventing LM Defense Against Jailbreak Attacks with Self-Refinement 2402.15180

[5] Testing the Limits of Jailbreaking Defenses with the Purple Problem 2403.14725

[6] Bypassing LLM Guardrails: An Empirical Analysis of Evasion Attacks against Prompt Injection and Jailbreak Detection Systems 2504.11168

[7] Stop Testing Attacks, Start Diagnosing Defenses: The Four-Checkpoint Framework Reveals Where LLM Safety Breaks 2602.09629

[8] Baseline Defenses for Adversarial Attacks Against Aligned Language Models 2309.00614

## Scores
Final Score: 6.5/10. The paper tackles a highly relevant and timely problem (control-plane jailbreaks) with a novel, lightweight, and pragmatically effective defense. The schema sanitization paradigm is genuinely new. However, the score is reduced due to missing statistical variance reporting (undermining the 0% ASR claim), unjustified heuristic hyperparameters, and over-scoped novelty/Pareto claims.

Post-Revision Target: [8.0, 9.0]/10. The core issues are highly fixable: adding multi-seed variance, justifying the 20-character threshold, and scoping the novelty claim are all manageable tasks that do not require fundamentally new experiments. Once these validity and precision gaps are closed, the paper will be a strong and compelling contribution.

### Page Coverage Audit
| Page | Annotation Count | Coverage Status | Skip Reason |
|---|---|---|---|
| Page 1 | 4 | Covered | (Abstract + Intro P1-P3) |
| Page 2 | 3 | Covered | (Contributions + Related Work P1, P3) |
| Page 3 | 1 | Covered | (Threat Model) |
| Page 4 | 3 | Covered | (Suspicion Function + Placeholder Replacement + Experimental Setup) |
| Page 5 | 1 | Covered | (Main Results) |
| Page 6 | 2 | Covered | (Ablation Study + Limitations) |
| Page 7 | 1 | Covered | (Conclusion) |