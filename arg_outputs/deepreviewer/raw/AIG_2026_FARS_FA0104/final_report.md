## Summary
This paper investigates rollout drift in LLM-based world models for web agents and identifies search-result simulation as the primary failure mode. Through systematic error analysis on WebShop, the authors find that 100% of first divergences occur at search-result observations, with a 99.8% per-step divergence rate. Based on this finding, they propose search-anchored hybrid rollouts, which intercept search actions and substitute world model predictions with real BM25-retrieved results, while keeping other observations simulated. The method improves Consistency Ratio from 0.594 to 0.819 (+37.9%) with grounding alone, and to 0.824 when combined with ReAct prompting. Ablation on first-search vs. all-search anchoring confirms that compounding search errors drive rollout drift.

**Strengths:** The diagnostic finding (99.8% search divergence) is empirically convincing and directly motivates a clean, minimal intervention. The method is well-designed: it leverages BM25 determinism for efficient caching and correctly decomposes observations into structured state updates vs. high-entropy retrieval. The stratified analysis by search count provides strong evidence for the compounding-error hypothesis.

**Weaknesses:** (a) The +38.7% CR improvement conflates observation grounding with ReAct prompting, leading to mixed-effect attribution. (b) Key operational details are missing: divergence measurement protocol, search result format, and cache initialization. (c) The paper does not discuss the theoretical anomaly of CR > 1.0 in stratified analysis. (d) Evaluation is limited to WebShop with a deterministic retrieval assumption, limiting generalizability claims. (e) Retrieval overlap with R-WoM (Mei et al., 2025) should be more explicitly discussed.

**Verdict:** This is a well-motivated, methodologically clean paper with a strong empirical contribution. The core diagnostic finding is novel and the method is practical. After addressing the attribution confounding, operational definition gaps, and generalization limitations, the paper can make a solid contribution to the web agent world model literature.

## Strengths
1. **Strong empirical diagnostic finding**: The 99.8% per-step divergence rate for search results and 100% of first divergences at search observations is a compelling, data-driven discovery. This is not just a performance improvement claim but a mechanistic insight into why LLM-based world models fail for web agents. The stratified analysis by search count further strengthens this finding by showing compounding errors.

2. **Clean, minimal intervention design**: The search-anchored hybrid rollout method is elegant in its simplicity. By leveraging BM25 determinism for caching, the approach is computationally efficient and does not require retraining the world model. The decomposition of observations into structured state updates vs. high-entropy retrieval provides a theoretically grounded justification for selective grounding.

3. **Well-structured experimental design**: The paper compares six conditions organized into agent-side and observation-side baselines, including first-search vs. all-search ablation, Best-of-N, and ReAct. The stratified analysis by search count and the error source analysis (Figure 2) provide multiple angles of validation.

4. **Clear narrative arc**: The paper follows a logical progression from problem (rollout drift) → diagnosis (search-result failure) → solution (search anchoring) → validation (CR improvement, stratified analysis). The motivation-to-method alignment is strong.

5. **Practical relevance**: The finding that search-result simulation is the primary failure mode has practical implications for web agent development. The method demonstrates that targeted observation grounding can be more effective than general world model improvements, suggesting a complementary research direction.

## Weaknesses
1. **Mixed-effect attribution in CR improvement claims (Major)**: The +38.7% relative improvement (0.594 → 0.824) is attributed to "grounding search observations," but this comparison is between Pure WM and All-search anchored + ReAct. This conflates observation grounding with ReAct prompting. The grounding-only improvement is +37.9% (0.594 → 0.819), with ReAct adding only +0.005 additional CR. This attribution error is propagated from Section 4.2 to the Conclusion.

2. **Missing operational definitions for key metrics (Major)**: The 99.8% per-step divergence rate is the central empirical finding, but the divergence measurement protocol is not specified. Is it token-level exact match? Semantic similarity? What is the denominator for the per-step rate? Without this, the statistic cannot be independently verified.

3. **Missing reproducibility details for the method (Minor)**: The search-anchored rollout mechanism lacks critical details: (a) the format of substituted search results (raw HTML? serialized text?), (b) the cache initialization protocol (pre-built? on-demand? size?), (c) the definition of "exogenous observation channel." These omissions reduce reproducibility.

4. **CR > 1.0 anomaly unexplained (Minor)**: Table 2 shows CR = 1.034 for 1-search episodes with all-search anchoring, exceeding the theoretical maximum of 1.0 for perfect fidelity. While CR > 1.0 is theoretically possible when the world model filters trajectories, this is not discussed in the text, which can confuse readers.

5. **Limited generalizability discussion (Minor)**: The evaluation is limited to WebShop with a deterministic BM25 retrieval assumption. The paper does not discuss whether the approach generalizes to environments with personalized/dynamic search results (e.g., real Amazon, WebArena). The limitations paragraph should explicitly address this boundary condition.

6. **Retrieval overlap with R-WoM not fully addressed (Minor)**: R-WoM (Mei et al., 2025) also uses retrieval augmentation to ground world model simulations. The paper states "Our work differs by identifying search-result simulation as the specific failure mode," but does not explicitly compare with R-WoM's grounding mechanism, which also targets hallucination mitigation through retrieval. The differentiation should be more precise.

## Key Issues
### 1. Mixed-effect attribution in CR improvement (Severity: Major)

**Problem**: The +38.7% CR improvement (0.594 → 0.824) is attributed to "grounding search observations," but the comparison is between Pure WM and All-search anchored + ReAct, which conflates two interventions: observation grounding AND ReAct prompting.

**Evidence**: Page 5 - Section 4.2, line 3: "First, all-search anchoring improves CR from 0.594 (pure WM) to 0.824, a +38.7% relative improvement." The 0.824 value corresponds to "All-search anchored + ReAct" in Table 1, not "All-search anchored (basic)" which is 0.819.

**Impact**: Overstates the grounding-only gain and misleads readers about where the value lies. The grounding-only improvement is +37.9% (0.594 → 0.819), with ReAct adding only +0.005 additional CR.

**Repair path**: Decompose the +38.7% into grounding-only and ReAct components: "All-search anchoring alone improves CR from 0.594 to 0.819 (+37.9%), with ReAct adding a small but variance-reducing complement (+0.005 to reach 0.824)."

### 2. Missing divergence measurement protocol (Severity: Major)

**Problem**: The 99.8% per-step divergence rate is the central empirical claim, but the measurement protocol is not specified.

**Evidence**: Page 1 - Abstract and Page 6 - Section 4.3 both state "99.8% per-step divergence rate" without defining the divergence metric.

**Impact**: Without operational definition, the statistic cannot be independently verified. Reviewers may question whether the metric is overly strict (e.g., token-level exact match) or whether the evaluation protocol is fair.

**Repair path**: Add one sentence specifying the divergence measurement: "We measure divergence as token-level mismatch between world model predictions and real environment observations at each step. The 99.8% rate is computed over all search-result steps across 200 test episodes."

### 3. Missing reproducibility details (Severity: Minor)

**Problem**: Critical implementation details are missing: search result format, cache protocol, and exogenous channel definition.

**Evidence**: Page 3 - Section 3.3 describes the method but does not specify how search results are formatted for substitution or how the cache is initialized.

**Impact**: Reduces reproducibility and makes the theoretical framing partially ambiguous.

**Repair path**: Add one paragraph specifying: (a) search results match the original WebShop observation format, (b) cache is pre-built before evaluation, (c) define exogenous channel as observations determined by external retrieval rather than learned state transitions.

## Actionable Suggestions
1. **Decompose CR improvement claims (P0 - Must)**: In Section 4.2 and the Conclusion, separate the grounding-only improvement from the combined grounding + ReAct improvement. Replace "all-search anchoring improves CR from 0.594 to 0.824 (+38.7%)" with "all-search anchoring alone improves CR from 0.594 to 0.819 (+37.9%), with ReAct adding a small but variance-reducing complement (+0.005 to reach 0.824)." This makes the value attribution transparent and defensible.

2. **Add divergence measurement protocol (P0 - Must)**: In Section 3.2 and Section 4.3, add one sentence specifying how divergence is measured. For example: "We measure divergence as token-level mismatch between world model predictions and real environment observations at each step. The 99.8% per-step rate is computed over all search-result steps across 200 test episodes with 3 random seeds." This makes the central empirical claim verifiable.

3. **Add reproducibility details to Method section (P0 - Must)**: In Section 3.3, add one paragraph specifying: (a) search results are substituted in the same observation format as the original WebShop environment, (b) the cache is pre-built before evaluation to avoid runtime latency, (c) define "exogenous observation channel" as observations whose content is determined by external retrieval rather than learned state transitions. This ensures the method can be reproduced from the text alone.

4. **Discuss CR > 1.0 anomaly (P1 - Nice-to-have)**: In Section 4.4, add one sentence interpreting the CR = 1.034 result for 1-search episodes: "CR values above 1.0 suggest the world model may filter out trajectories that would fail in the real environment, though this observation is based on a small sample (n=37)." Also note the sample size limitation for the 1-search conclusion.

5. **Clarify WebShop search-at-step-0 property (P1 - Nice-to-have)**: In Section 4.3, clarify that "100% of first divergences at step 0" is partly because WebShop tasks universally begin with a search action. Reframe as: "100% of first divergences occur at the first search action, which corresponds to step 0 in WebShop since all tasks begin with search." This avoids overgeneralizing to other environments.

6. **Add deterministic-retrieval limitation (P1 - Nice-to-have)**: In the Limitations paragraph, add one sentence: "Additionally, our method relies on the deterministic retrieval assumption (BM25), which may not hold in environments with personalized or dynamic search results, such as real-world e-commerce platforms."

7. **Fix CR rendering error (P0 - Must)**: In Section 4.2, line 2, the CR value appears as `$(\mathbf{CR} = 0.82\bar{4} \doteq 0.018)$`. The `\doteq` should be `\pm`. Fix the LaTeX source to produce `CR = 0.824 ± 0.018`.

8. **Enhance R-WoM comparison in Related Work (P1 - Nice-to-have)**: In Section 2, add one sentence explicitly comparing with R-WoM (Mei et al., 2025): "Unlike R-WoM, which grounds world model simulations with retrieved tutorials for procedural knowledge, our method targets the specific high-entropy search-result channel with ground-truth BM25 retrieval, addressing a different failure mode in the observation generation pipeline."

## Storyline Options + Writing Outlines
### Abstract Outline (complete)
- **S1 (Problem/Domain):** LLM-based world models enable scalable training and evaluation of web agents through simulated trajectories, but suffer from rollout drift where simulated behavior diverges from real environments.
- **S2 (Significance/Challenge):** Rollout drift limits the utility of world models for planning, verification, and synthetic data generation, as hallucinated observations cause cascading errors in agent trajectories.
- **S3 (Gap/Discovery):** We identify the root cause of this drift in text-based world models: 100% of first divergences occur at search-result observations, with a 99.8% per-step divergence rate measured as token-level mismatch.
- **S4 (Method):** We propose search-anchored hybrid rollouts, which ground search observations with real BM25-retrieved data while keeping other observations simulated, leveraging deterministic retrieval for efficient caching.
- **S5 (Result/Implication):** Using a Qwen2.5-7B world model and Gemini-2.5-Flash agent on WebShop, our method improves Consistency Ratio from 0.594 to 0.819 (+37.9% from grounding alone), with benefits scaling for multi-search episodes that comprise 90% of tasks.

### Introduction Outline (complete)
- **P1 (Big Picture + Problem):** Establish world models for web agents (Word2World, WebDreamer, DynaWeb) and define rollout drift with clear stakes: simulated trajectories diverge after few steps, making synthetic trajectories unreliable for planning and data synthesis.
- **P2 (Core Diagnostic Finding):** Present the 99.8% search divergence rate with operational definition (token-level mismatch over 200 episodes). Explain the mechanism: world models hallucinate ASINs and descriptions, causing cascading errors. Clarify that search is the universal initial failure point.
- **P3 (Method Proposal):** Introduce search-anchored hybrid rollouts: intercept search actions, substitute with real BM25 results, cache for efficiency. Justify feasibility through BM25 determinism and the decomposition of observations into structured state updates vs. high-entropy retrieval.
- **P4 (Evidence Preview + Contributions):** Preview key results: CR improves from 0.594 to 0.819 with grounding alone; first-search anchoring provides negligible benefit confirming compounding errors; observation grounding outperforms agent-side baselines. List contributions: (C1) diagnostic finding, (C2) method proposal, (C3) empirical validation with stratified analysis.

## Priority Revision Plan
| Priority | Issue | Action | Expected Impact |
|---|---|---|---|
| **P0** | Mixed-effect CR attribution (0.594→0.824 conflates grounding+ReAct) | Decompose in §4.2 and Conclusion: grounding-only +37.9% (→0.819), ReAct +0.005 (→0.824) | Fixes validity-critical attribution error |
| **P0** | Missing divergence measurement protocol | Add token-level mismatch definition in §3.2 and §4.3 | Makes central 99.8% claim verifiable |
| **P0** | Missing reproducibility details | Add search format, cache protocol, exogenous channel definition in §3.3 | Ensures method can be reproduced from text |
| **P0** | CR rendering error (`\doteq` → `\pm`) | Fix LaTeX source in §4.2 line 2 | Professionalism fix |
| **P1** | CR > 1.0 anomaly unexplained | Add interpretation sentence in §4.4 | Improves result interpretability |
| **P1** | WebShop step-0 property | Clarify "100% at step 0" is partly dataset artifact in §4.3 | Avoids overgeneralization |
| **P1** | Missing deterministic-retrieval limitation | Add sentence in Limitations paragraph | Strengthens generalization defensibility |
| **P1** | R-WoM comparison depth | Add explicit differentiation sentence in Related Work | Improves novelty positioning |

**Page Coverage Audit:**
| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|---|---|---|---|
| Page 1 (Abstract, Intro P1-P3) | 4 annotations | Covered | - |
| Page 2 (Related Work) | 0 annotations | Skipped | Non-substantive literature survey; no core claims |
| Page 3 (Method §3.1-§3.3) | 3 annotations | Covered | - |
| Page 4 (Exp Setup §4.1) | 1 annotation | Covered | - |
| Page 5 (Main Results §4.2) | 1 annotation | Covered | - |
| Page 6 (Error Analysis §4.3-4.4) | 2 annotations | Covered | - |
| Page 7 (Conclusion, References) | 1 annotation | Covered | - |

```text
ASCII Diagram — Revision Strategy Roadmap
[CR attribution error]
    -> [Decompose +38.7% into grounding +37.9% + ReAct +0.005]
    -> [Fix in §4.2 and Conclusion]
    -> [Expected impact: valid value attribution]

[Missing divergence protocol]
    -> [Add token-level mismatch definition + denominator]
    -> [Fix in §3.2 and §4.3]
    -> [Expected impact: verifiable central claim]

[Missing reproducibility details]
    -> [Add search format + cache protocol + exogenous definition]
    -> [Fix in §3.3]
    -> [Expected impact: full method reproducibility]

[CR > 1.0 + sample size]
    -> [Add interpretation sentence in §4.4]
    -> [Note n=37 limitation for 1-search]
    -> [Expected impact: complete result narrative]
```

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Main CR comparison: grounding vs. baselines | WebShop 200 test episodes × 3 seeds; 6 conditions | CR (mean±std) | All-search + ReAct: CR 0.824±0.018 | Grounding improves CR | Conflates grounding+ReAct effects |
| E2 | First-search vs. all-search ablation | Same setup, 2 anchoring conditions | CR | First-search: 0.598; All-search: 0.819 | Compounding errors hypothesis | Small sample for 1-search (n=37) |
| E3 | Agent-side baselines (Best-of-N, ReAct) | Same setup, 3 agent-side conditions | CR | Best-of-N: 0.748; ReAct: 0.812 | Observation grounding > agent-side | Best-of-N uses same flawed WM |
| E4 | Error source analysis (divergence by action type) | 200 episodes, token-level mismatch measurement | Per-step divergence rate | Search: 99.8%; Product: 50.9%; Nav: 68.4% | Search is primary failure mode | Divergence protocol not fully specified |
| E5 | Stratified CR by search count | 200 episodes, stratified by ≥1/≥2/≥3 searches | CR by stratum | Multi-search benefits more (+22% for ≥2) | Scaling confirms compounding errors | CR > 1.0 anomaly not discussed |

### Research-Theme Gap Diagnosis
- **New knowledge**: The search-as-primary-failure-mode finding is strong and well-supported. The compounding-error mechanism is validated through stratified analysis.
- **Reproducibility**: Missing operational definitions (divergence protocol, search format, cache protocol) reduce reproducibility confidence.
- **Impact on practice**: The method is practical and efficient, but limited to deterministic retrieval environments. Generalization to dynamic/personalized search is untested.

### Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Expected Paper-Quality Gain |
|---|---|---|---|---|---|---|---|
| C2 (Method effectiveness) | Grounding-only CR improvement is +37.9% (not +38.7%) | Re-run All-search anchored (basic) without ReAct | Pure WM baseline | CR mean±std | CR ≥ 0.815 | Low (existing code) | Fixes attribution error; strengthens validity |
| C1 (Search failure mode) | Divergence is measured at token level | Explicitly report divergence protocol + denominator | N/A | Per-step divergence rate with confidence intervals | Protocol clearly documented | Low (text edit + recheck) | Makes central claim fully verifiable |
| Generalizability | Method transfers to non-BM25 search | Evaluate on one environment with dynamic search (e.g., REAL benchmark) | Pure WM baseline | CR comparison | Directional improvement shown | Medium (1-2 days) | Strengthens generalization claims |
| Robustness | CR is stable across agent backbones | Swap agent from Gemini-2.5-Flash to another LLM | Same grounding protocol | CR variance across agents | Consistent CR improvement | Medium (1 day) | Demonstrates method robustness |

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | Search-result simulation is the primary failure mode (100% first divergences at search, 99.8% per-step divergence) | [1], [2] | supported | BehR [1] improves consistency but does not diagnose specific failure modes; AgentErrorBench [2] catalogs agent errors but does not analyze world model observation divergence at this granularity | High | None needed; claim is well-supported |
| C2 | Search-anchored hybrid rollouts: grounding only search observations while keeping others simulated | [3], [4] | partially_overlapping | R-WoM [3] grounds world models with retrieval; WAC [4] uses world model for action correction. But this paper's targeted search-only grounding with BM25 caching is a distinct mechanism | Medium | Clarify differentiation from R-WoM's tutorial-based grounding |
| C3 | +38.7% CR improvement on WebShop, scaling with multi-search episodes | [1] | partially_overlapping | BehR [1] also evaluates on WebShop with consistency metrics. The CR improvement claim is valid but the attribution conflation (grounding+ReAct) needs decomposition | Medium | Decompose grounding-only vs combined CR gains |

### (9B) Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root: World Model Evaluation | Leaf: Consistency metrics | [1] BehR | Frozen reference agent measures action consistency | BehR focuses on training signal; this paper uses CR for evaluation | Low risk; different objectives |
| Root: World Model Grounding | Leaf: Retrieval-augmented simulation | [3] R-WoM | Tutorial knowledge reduces hallucination | R-WoM uses procedural tutorials; this paper uses ground-truth BM25 search results | Medium risk; both use retrieval but for different channels |
| Root: World Model-Augmented Agents | Leaf: Action correction via simulation | [4] WAC | World model simulates outcomes for risk awareness | WAC corrects actions; this paper corrects observations | Low risk; different intervention targets |
| Root: Agent Failure Analysis | Leaf: Error taxonomy and debugging | [2] AgentErrorBench | Errors propagate through agent modules | AgentErrorBench analyzes agent-level failures; this paper analyzes world model observation failures | Low risk; different analysis levels |

### (9C) Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [1] BehR | WebShop world model consistency | Behavior Consistency Reward training | Evaluates world models on WebShop | BehR proposes training paradigm; this paper proposes inference-time grounding | Complementary; no direct overlap |
| [3] R-WoM | WebArena/OSWorld world model hallucination | Retrieval-augmented simulation with tutorials | Both ground world models with retrieval | R-WoM targets procedural knowledge; this paper targets search result hallucination | Partial overlap; residual novelty in targeted search grounding |
| [4] WAC | VisualWebArena/Mind2Web web agents | World model for action correction | Both use world models for web agents | WAC corrects actions through simulation; this paper corrects observations through grounding | Complementary; different intervention level |

### Contribution-level Novelty Conclusion

C1 (search-as-primary-failure-mode): **supported**. The 99.8% per-step divergence rate at search observations is a novel diagnostic finding not present in prior work. BehR [1] improves consistency but does not perform this granular failure mode analysis.

C2 (search-anchored hybrid rollouts): **partially_overlapping**. R-WoM [3] also grounds world models with retrieval, but the targeted search-only intervention with BM25 caching represents a distinct mechanism. Repositioning should explicitly differentiate from R-WoM's tutorial-based approach.

C3 (+38.7% CR improvement): **partially_overlapping**. The improvement claim is valid but conflates grounding with ReAct prompting. After decomposition (grounding-only +37.9%), the claim is defensible. BehR [1] provides a relevant comparison point for WebShop consistency evaluation.

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)
World Model Research (Root)
├── Branch 1: World Model Evaluation
│   ├── Leaf 1.1: Consistency Metrics
│   │   └── [1] BehR (action-level consistency training signal)
│   └── Leaf 1.2: Stability Metrics
│       └── [5] World Consistency Score (video generation)
├── Branch 2: World Model Grounding Strategies
│   ├── Leaf 2.1: Retrieval-Augmented Simulation
│   │   ├── [3] R-WoM (tutorial-based grounding for OSWorld)
│   │   └── THIS PAPER (BM25 search grounding for WebShop) ← partial overlap
│   └── Leaf 2.2: Observation Correction
│       └── [4] WAC (world model for action correction)
└── Branch 3: Agent Failure Analysis
    ├── Leaf 3.1: Error Taxonomy
    │   └── [2] AgentErrorBench (agent-level error categorization)
    └── Leaf 3.2: World Model Failure Modes
        └── THIS PAPER (search-result divergence diagnosis) ← novel contribution
```

## References
[1] Beyond State Consistency: Behavior Consistency in Text-Based World Models 2604.13824

[2] Where LLM Agents Fail and How They can Learn From Failures 2509.25370

[3] R-WoM: Retrieval-augmented World Model For Computer-use Agents 2510.11892

[4] World-Model-Augmented Web Agents with Action Correction 2602.15384

[5] World Consistency Score: A Unified Metric for Video Generation Quality 2508.00144

## Scores
**Final Score: 7/10**

This score emphasizes the paper's novelty and research value: the core diagnostic finding (search-as-primary-failure-mode) is novel and empirically well-supported, and the method is clean, practical, and theoretically grounded. The score is tempered by the mixed-effect CR attribution error, missing operational definitions that reduce reproducibility confidence, and limited generalizability discussion.

Scoring dimensions:
- Novelty (2.5/3): C1 (search-as-primary-failure-mode) is a genuinely novel diagnostic finding. C2 (search-anchored rollouts) partially overlaps with R-WoM but maintains residual novelty through targeted search-only grounding.
- Research Value (2.0/3): The method is practical and efficient, leveraging BM25 determinism for caching. The diagnostic finding has implications for web agent development beyond this specific benchmark.
- Validity (1.5/2): The attribution conflation between grounding and ReAct effects, plus missing divergence measurement protocol, reduce confidence in the strongest claims. These are fixable P0 issues.
- Reproducibility (1.0/2): Missing operational details (search format, cache protocol, exogenous channel definition) and the divergence measurement protocol reduce reproducibility from the text alone.

**Post-Revision Target: [8, 9]/10**

If all P0 items are fully addressed (decomposed CR attribution, divergence measurement protocol added, reproducibility details provided, rendering error fixed), the paper's validity and reproducibility scores would improve substantially. The novelty score would remain stable, and the research value is already strong. A score in the [8, 9]/10 range is achievable with a clean, well-attributed revision.

```text
ASCII Diagram — Paper Structure & Evidence Map
[Claim: search-result simulation is primary failure mode]
    -> [Evidence: 99.8% per-step divergence rate (token-level mismatch)]
    -> [Evidence: 100% first divergences at search (WebShop step-0)]
    -> [Status: Novel finding, well-supported by E4 error analysis]

[Claim: search-anchored rollouts improve CR]
    -> [Evidence: CR 0.594 → 0.819 (grounding alone), → 0.824 (+ReAct)]
    -> [Evidence: First-search CR=0.598 vs All-search CR=0.819]
    -> [Gap: +38.7% conflates grounding+ReAct; needs decomposition]
    -> [Fix: Report grounding-only +37.9% separately]

[Claim: compounding errors drive drift]
    -> [Evidence: Stratified CR by search count (≥2: +22%, ≥3: +0.247)]
    -> [Evidence: 90% of episodes are multi-search]
    -> [Status: Strong support from E5 stratified analysis]

[Claim: method generalizes to web environments]
    -> [Evidence: None beyond WebShop]
    -> [Gap: Single-benchmark evaluation, BM25 determinism assumption]
    -> [Risk: May not transfer to dynamic/personalized search environments]
    -> [Mitigation: Acknowledge as limitation; propose OOD evaluation]
```