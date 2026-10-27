# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies rollout drift in text-based world models for web agents, using WebShop as the testbed. The authors identify search-result prediction as the dominant source of divergence between simulated and real trajectories, claiming that 100% of first divergences occur on search observations and that search steps have a 99.8% per-step divergence rate. They propose search-anchored hybrid rollouts: during simulated rollouts, intercept search[query] actions and replace the world model’s predicted search results with real WebShop results from a BM25 index via a cache; all other observations remain simulated. On 200 WebShop tasks across 3 seeds, they report Consistency Ratio (CR) improvements from 0.594 to 0.824 when anchoring all searches, with negligible gains when anchoring only the first search. The paper argues that compounding search errors drive rollout drift and that targeted observation grounding can be more effective than agent-side prompting or sampling tricks.

## Summary Of Strengths
- Clear and focused problem framing: the paper isolates a concrete failure mode of text-based world models in web navigation, namely search-result simulation.
- Minimal, easily implementable intervention: search anchoring is simple and low overhead, with a practical cache to avoid repeated external calls.
- Empirical gains on WebShop: Table 1 shows improvements in Consistency Ratio, especially for all-search anchoring (0.819–0.824) relative to the pure world-model baseline (0.594).
- Useful stratified analysis: Figure 3 and Table 2 break down CR by the number of search actions, linking performance benefits to multi-search episodes and supporting the “compounding errors” explanation.
- Results variance discussion: the combination of anchoring and ReAct reduces variance (Table 1, std 0.018 vs 0.062), which is useful for practitioners concerned with stability.
- Figure 1 provides a clear diagram of the rollout architecture and data flow among agent, world model, and the anchored search pathway; this helps readers understand exactly what is replaced and when.

## Summary Of Weaknesses
1) Limited novelty relative to the idea’s simplicity. The method is an oracle-style intervention that replaces the hardest-to-simulate channel with ground-truth retrieval. While pragmatic, it is conceptually straightforward and akin to “bypassing” the learned dynamics at the most difficult step, which raises questions about generality and scientific insight beyond WebShop.

2) Insufficient details about divergence measurement. Section 4.3 reports 99.8% per-step divergence for search results and that 100% of first divergences occur at search, “always at step 0.” However:
   - The exact divergence criterion is not defined. Is divergence measured by exact match of ranked lists, partial overlap, or some structured comparison? For product details and navigation, what constitutes a match?
   - Alignment protocol is unclear: given a stochastic agent (temperature 1.0), how are step-by-step comparisons synchronized between WM and real environment to localize “first divergence”? Please add a precise protocol describing how actions and observations are paired.
   - The “always step 0” statement needs context. If the first action is almost always search, this result could be tautological. Please report the empirical distribution of first actions and clarify whether there are tasks where the first step is not a search.

3) Scope limited to WebShop with deterministic BM25. The approach depends on deterministic retrieval and a stable index. Section 5 briefly notes generalization concerns, but the paper’s main claims lean heavily on determinism and a fixed corpus. In real-world web settings (non-deterministic results, personalization, time drift), the method’s effectiveness and reproducibility are unclear. A small-scale ablation on a non-deterministic or noisy retrieval variant would strengthen claims.

4) Baseline coverage and comparisons could be stronger.
   - The related R-augmented world-model line (e.g., retrieval-augmented world models) is cited but not compared. Even a light-weight variant that supplies retrieved snippets to the WM at search steps (without hard-replacing results) would make the case that hard anchoring is uniquely effective.
   - No comparison to alternative hybrid choices, such as anchoring product-detail pages or navigation states, or selectively anchoring only subsequent searches (e.g., anchor k-th search only for k≥2). This would help rule out that any form of partial grounding yields similar gains.

5) Statistical testing is missing. Table 1 reports means and standard deviations, but there are no significance tests or paired analyses across seeds/tasks for the main CR gains (e.g., pure WM vs all-search anchoring). Given modest absolute CR increases in some conditions and overlapping variances, significance tests would improve rigor.

6) Interpretation of Table 1 could be clearer. For example, in the ReAct row, W2R (24.6%) slightly exceeds WM (24.0%). While possible because the real environment differs from the simulated one, the paper should briefly explain how W2R can exceed WM and whether this occurs systematically across conditions or is an anomaly.

7) External validity of the “compounding errors” claim. While Figure 3 and Table 2 show scaling benefits with more searches on WebShop, the causal story would be stronger with per-episode analyses tying actual divergence loci to downstream failure categories, or with controlled experiments where later searches are selectively perturbed or anchored to quantify marginal contributions across time steps.

8) Implementation and reproducibility details are thin in places. Section 3.4 names models and temperatures, but omits fine-tuning data size and procedure for the world model, tokenization and prompt formats for each action type, and the precise structure of serialized search results inserted into the rollout history. These matter for re-implementers aiming to replicate the exact CR values.

9) Positioning within broader world-model evaluation metrics. The paper exclusively uses Consistency Ratio (Eq. 1) as the central metric. Recent work has noted that text similarity or state consistency may not capture behavior alignment; alternative or complementary metrics (e.g., behavior consistency rewards or functional success preservation) could nuance the conclusions. A short discussion or auxiliary metric would bolster the evaluation.

10) Claims in Figure 2 need accompanying counts and stratification. The bar plot gives percentages, but absolute counts per action type and the number of steps considered would help readers judge whether categories like “Unknown” or rarer action states are sufficiently represented.

Figure- and table-specific comments:
- Figure 1: The diagram is helpful to understand where the observational substitution happens. However, it would be useful to indicate in the figure (or caption) the exact serialization format of grounded search results and how they integrate into the dialog history consumed by the agent and WM. This affects downstream tokenization and may influence CR.
- Figure 2: The red callout “100% of first divergences occur at search results” is a central claim; please add the raw counts and the definition of “divergence” in the caption or main text near this figure to avoid ambiguity in interpretation. Also, the “Unknown” category at 75.5% is unexplained and should be defined.
- Figure 3 and Table 2: These are the strongest pieces of evidence for the compounding error hypothesis. That said, the first-search-anchored condition is missing for the “1 search” stratum (Table 2 shows N/A). If first-search anchoring induces behavior that changes search counts, report how the distribution shifts. Otherwise, include the corresponding CR for single-search episodes to complete the picture.
- Table 1: Present paired statistical tests for CR, and include confidence intervals if feasible. Clarify whether Real, WM, and W2R are per-seed aggregated or per-episode averaged, and how CR is computed relative to those aggregates to avoid denominator issues (e.g., averaging ratios vs ratio of averages).

## Potentially Missing Related Work
1) Xiao et al., “WebWorld: A Large-Scale World Model for Web Agent Training,” 2026 — Builds a large-scale learned simulator for web agents and introduces WebWorld-Bench. It directly addresses simulation fidelity for web agents and should be discussed in Section 2 and compared conceptually in Section 4 as an alternative to hybrid rollouts focusing on reducing drift.

2) Huang et al., “Beyond State Consistency: Behavior Consistency in Text-Based World Models,” 2026 — Proposes behavior-oriented evaluation (BehR) on WebShop/TextWorld. It is directly relevant to the reliance on CR (Eq. 1). Discuss in Section 2 and consider adding an auxiliary behavior-consistency metric in Section 4.

3) Xu et al., “How Mobile World Model Guides GUI Agents?,” 2026 — Studies multimodal GUI world models and when rollouts can safely replace real interactions, which is analogous to hybrid rollouts. Cite in Section 2 and contrast their guidance analyses with the present anchoring strategy.

4) Murty et al., “NNetscape Navigator: Complex Demonstrations for Web Agents Without a Demonstrator,” 2024 — Generates synthetic web trajectories without explicit world models. Compare in Section 2 and briefly discuss in Section 4 how hybrid rollouts relate to high-quality synthetic data generation pipelines.

5) Li et al., “Bridging the Agent-World Gap: Text World Models for LLM-based Agents,” 2026 — A survey that frames text world models across domains. Cite in Section 2 to properly position search-anchored hybrid rollouts in the broader landscape.

6) Qwen Team et al., “Qwen-AgentWorld: Language World Models for General Agents,” 2026 — Introduces large-scale language world models and a multi-domain benchmark. Discuss in Section 2 and mention in Section 5 as a broader context for scaling hybrid or grounded rollouts beyond WebShop.

## Comments Suggestions And Typos
Actionable questions and suggestions:
1) Specify the divergence protocol. Provide a formal definition of “divergence” for each observation type, the synchronization procedure between WM and real environment rollouts under a stochastic agent, and the rule for identifying the first divergence. Add per-action-type counts next to percentages in Figure 2.

2) Add significance tests for Table 1 and Table 2. Given three seeds over 200 tasks, paired bootstrap or stratified permutation tests would bolster the claim that all-search anchoring outperforms both the pure WM baseline and agent-side baselines.

3) Strengthen ablations. Include:
   - Selective late-search anchoring (e.g., anchor only k≥2 searches).
   - Product-detail anchoring and navigation anchoring to confirm specificity to search.
   - A “soft” retrieval-augmented WM baseline where the WM receives retrieved evidence but still predicts results, isolating the effect of hard substitution vs retrieval conditioning.

4) Clarify generalization to non-deterministic retrieval. Run a small experiment introducing controlled noise or alternative rankers to assess robustness. Discuss the cost/benefit when APIs are rate-limited or when results drift over time.

5) Expand implementation details. Report WM fine-tuning data size, training hyperparameters, prompting formats, and the exact serialization of grounded search results (e.g., fields kept per product, maximum list length). Provide the query cache format and a reproducible seed protocol.

Typos and minor edits:
- Page 3, “always at step 0” — consider rephrasing or justifying with the distribution of first actions; otherwise it reads as tautological.
- Table 1 caption: define CR once more for readability and specify whether bolding reflects mean only.
- Figure 2: Define “Unknown” action type in caption.
- Page 5, “3.4× lower variance” — consider providing numeric variance values alongside standard deviations for clarity.
- References: verify years (e.g., DynaWeb 2026 is marked without venue; ensure consistent formatting).

Criteria that could raise my score:
- Clear definition and protocol for divergence measurement with added counts in Figure 2.
- Statistical significance tests showing robust gains in Table 1 and Table 2.
- Ablations demonstrating that benefits are specific to search-result anchoring rather than any generic grounding.
- A robustness check for non-deterministic retrieval or time-varying indices.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
2.5 Between potentially interesting and interesting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The work isolates a specific, practically important failure mode in text-based web world models and shows that anchoring search observations delivers sizable CR gains on WebShop. However, the method is a straightforward oracle-style intervention tied to a deterministic BM25 environment; divergence measurement lacks a precise, reproducible protocol; statistical testing is absent; and comparisons to closely related hybrid or retrieval-augmented world-model baselines are missing. With stronger methodology details, additional ablations, and significance testing, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The limitations section acknowledges confinement to WebShop and reliance on a deterministic search engine. I encourage expanding on:
- Potential brittleness to non-deterministic or personalized search results, which are common on the real web.
- Any risks of leakage if the cache contains sensitive product metadata, and how to sanitize or version such caches for reproducibility.
- Broader applicability beyond e-commerce search, including other high-entropy channels (e.g., APIs) that might expose private or dynamic content; discuss safe caching and access controls.

## Ethical concerns
None.

## Needs Ethics Review
No

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful.: Someone might find the new software useful for their work.