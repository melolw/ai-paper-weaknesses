# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes MASS, a language-native multi-agent social simulation framework where LLMs act as “intersubjective” agents. Agents decide in natural language within a rule-based, round-based environment, output numeric actions (starting wage, target FTE employment, price) and one-sentence intention rationales. The authors articulate protocol elements (time granularity, exogenous rules, agent autonomy, controlled contrasts, replications) and separate causal identification from simulation by applying DID at the analysis layer. As a validity and reliability test, they simulate the 1992 New Jersey minimum-wage increase against Pennsylvania over 46 weeks, claiming MASS reproduces the Card–Krueger qualitative pattern: wages rise by roughly $0.65/h, employment effects are near zero, and price movements are small. Figure 1 shows DID effects with CIs across runs (A/B/C/D), and Table 2 reports point estimates.

## Summary Of Strengths
- Clear methodological positioning: The paper makes a concrete methodological claim that LLM agents, anchored in public-language intersubjectivity and operating under external rules, can support repeatable, language-native social simulations. The “single-equation anchoring” through the language modeling objective provides a unifying lens that ties behavior to corpus-learned distributions (Section 2.1, Eq. (1)).
- Transparent separation of layers: The design principle “rules outside, identification outside” is sound and clean. Identification via DID is applied post-hoc to Agent×Round panels rather than entangled with agent behavior rules, improving auditability.
- Emphasis on auditability: The protocol logs numeric actions plus intention texts, seeds, and rule changes, and states that intention texts are excluded from state updates to avoid leakage. This is a thoughtful step toward mechanism audits.
- Compact, interpretable validation case: The NJ–PA minimum-wage case is an appropriate testbed with a well-known qualitative pattern. Figure 1 is used to assess directions and uncertainty across independent runs, and Table 2 summarizes run-wise DID point estimates. These provide a first-order validity check.
- Replications and contrasts: The inclusion of independent replications (runs A/B/D) and a counterfactual (C, no NJ floor hike) addresses concerns about stochasticity and spurious correlations. Figure 1 shows that wage DID in C does not lift, while A/B/D do, consistent with the stated claim.

Specific figure/table-based strengths:
- Figure 1: The wage DID bars for A/B/D are consistently positive (about 0.6–0.7 USD/h) with non-overlapping CIs relative to zero, while C hovers near zero or slightly negative. This visually supports the validity claim for wage effects.
- Table 2: The wage DID magnitudes (A: 0.669, B: 0.654, D: 0.637) are tightly grouped and align with the target effect size described in the text. The presence of the counterfactual C (−0.034) strengthens the causal story within the simulation.

## Summary Of Weaknesses
1) Insufficient articulation of agent interaction and environment dynamics
- The core promise is “language-native” multi-agent interaction, yet the paper does not specify whether agents meaningfully converse with one another or only emit independent action–intention pairs each round. Section 2.6 and the Method Box detail returns (w, FTE, p + intention) and constraints, but do not describe message passing, negotiation protocols, memory, or coordination beyond shared rules. Without explicit interaction mechanics, it is unclear how this differs from parallel single-agent decision stubs with shared exogenous shocks. This undermines the “social” part of social simulation and limits interpretability of emergent dynamics.

2) Limited methodological detail on prompts, decoding, and model variation
- Critical implementation details are missing from the main text. The paper does not specify the prompting schema, role instructions, decoding parameters (temperature, nucleus sampling), or how randomness is controlled beyond “fixed seeds.” Since the results hinge on LLM behavior and its stochasticity, these details are necessary for ACL-level reproducibility and for interpreting sensitivity. The “Reproducibility Statement” promises an anonymized artifact, but the main paper should still document key hyperparameters and decision rules.

3) DID design lacks essential diagnostics and robustness checks
- The DID analysis claims agent-clustered SEs and time fixed effects, but the paper does not report:
  - Pre-trend checks or an event-study plot to assess parallel trends, which is central to DID validity.
  - Placebo or staggered-window checks to ensure the effect is not driven by early shocks or drift.
  - Sensitivity to alternative specifications (e.g., random effects, block bootstrap, aggregating to group-level panels).
- Figure 1 shows post-policy DID bars with CIs, but without pre-period dynamics it is difficult to assess whether the near-zero employment effects are a reliable consequence or an artifact of design.

4) Small and skewed group composition and unclear statistical power
- The design uses 20 agents per group with NJ:PA = 16:4 (Method Box). This is an unusual and highly imbalanced “treatment-control” composition that risks unstable DID estimates, especially for employment where variance is large. The authors should justify this ratio, report power analyses or at least precision metrics, and clarify whether results are robust to alternative NJ:PA mixes. Table 2’s employment DID shows very large swings (e.g., C: −28.9 FTE) that suggest instability.

5) Interpretation of employment effects is not well supported by the reported uncertainty
- The paper repeatedly claims employment effects are “≈0” or “statistically indistinguishable from zero,” yet the right panel of Figure 1 shows wide CIs around employment DID estimates for A/B/C/D. Without numeric CIs or p-values, it is hard to substantiate the “≈0” framing. Table 2’s employment DIDs vary in sign and magnitude across runs, further suggesting high variance that needs deeper analysis (e.g., distributional summaries across all weeks and agents, not only a single DID point).

6) Mechanism inference from intention texts remains superficial
- Section 3.2 presents a few representative intentions, but does not analyze them systematically. If intention texts are a key differentiator of MASS, the paper should code them with a transparent scheme, report inter-annotator agreement, and link intention distributions to numeric outcomes. As written, the mechanism story is anecdotal and concentrated in the single run where intentions were required (D), which introduces reporting bias relative to A/B/C.

7) External validity and scope claims outpace evidence
- The paper positions MASS as a “low-risk platform for ex-ante policy probing and extreme counterfactuals.” Given the limited interaction modeling, lack of pre-trend diagnostics, high employment variance, and small sample size, the validation is not strong enough to generalize the framework’s reliability for policy-relevant ex-ante evaluation. Stronger evidence is needed across diverse policy domains and model variants.

8) Missing baselines and ablations
- There are no comparisons to standard ABM baselines or to alternative LLM-agent frameworks under the same scenario. Nor are there ablations showing the effect of key design choices: with vs. without intention texts, with different decoding temperatures, with/without legal price bands, or with different time granularities. These are essential to isolate what in MASS is responsible for the observed effects.

9) Over-reliance on a single, proprietary LLM without model diversity
- The “AI Agent Setup” cites GPT-5 series, with no cross-model checks. Given that behavioral outputs can vary substantially across foundation models, at least one alternative model replication is warranted. Otherwise, generality is not demonstrated.

10) Figure and table reporting gaps
- Figure 1 does not include numeric CIs, making it hard to verify the “≈0” employment conclusion. Table 2 reports only point estimates for four runs, and omits standard errors or CIs. The paper also lacks an event-study figure to demonstrate pre-trends, and does not provide a distributional figure for intention categories, which would directly serve the mechanism-audit claim.

How these weaknesses affect the contribution:
- Without clear interaction mechanisms and diagnostics, the central claim that language-native multi-agent simulation yields credible social-process evidence is undercut. The DID claims for employment, the most contentious outcome, are not sufficiently supported by the uncertainty quantification shown in Figure 1 and the volatility seen in Table 2. Missing baselines/ablations and single-model dependency limit the methodological insight and broader reproducibility. Overall, the idea is promising but the empirical and methodological validation needs to be strengthened to meet main-track standards.

Explicit references:
- Figure 1: Wage DID bars support the wage-lift claim; employment DID CIs appear wide, raising doubts about the “≈0” effect characterization without numeric intervals.
- Table 2: Wage DID magnitudes are consistent across A/B/D, but employment DID shows large magnitudes and sign variation, suggesting instability and the need for pre-trend checks and precision reporting.
- Equation (1): The anchoring argument is plausible, but it does not substitute for missing details on interaction protocols and agent communication needed to justify “social” emergence.

## Potentially Missing Related Work
1) Li et al., “Generalized Multi-agent Social Simulation Framework,” 2025 — Proposes a reusable, modular LLM-based social simulation framework. Directly relevant as an alternative architectural approach. Should be discussed in Section 2.3 to position MASS’s protocol choices and cited near Table 1 to refine the comparison against existing frameworks.

2) Mangla et al., “NegotiationGym: Self-Optimizing Agents in a Multi-Agent Social Simulation Environment,” 2025 — Focuses on negotiation/cooperation with learning agents over repeated interactions. Relevant for interaction mechanics and optimization. Compare in Section 2.1/2.3 and add as a baseline or discussion point in Section 3 to highlight how MASS handles interaction versus adaptive optimization.

3) Yang et al., “Think-Before-Speak: From Internal Evaluation to Public Expression in Multi-Agent Social Simulation,” 2026 — Separates private internal states from public utterances. Pertinent to the intention-text concept and mechanism audits. Discuss in Section 3.2 to contrast MASS’s one-sentence intentions with deeper internal-state modeling.

4) Yang et al., “ScioMind: Cognitively Grounded Multi-Agent Social Simulation with Anchoring-Based Belief Dynamics and Dynamic Profiles,” 2026 — Integrates psychologically motivated belief updates with LLM reasoning. Discuss in Section 2.1/2.3 as a contrasting mechanism-rich design and in Section 3.3 for external validity considerations.

5) Xu et al., “Topology-Aware LLM-Driven Social Simulation: A Unified Framework for Efficient and Realistic Agent Dynamics,” 2026 — Emphasizes network structure and efficiency. Add to Section 2.3 and Section 3.3 to address scalability and networked interaction absent in MASS’s current description.

6) Yang et al., “Attention: What Prevents Young Adults from Speaking Up Against Cyberbullying in an LLM-Powered Social Media Simulation,” 2026 — An applied simulation in social psychology with policy implications. Cite in Section 2.4 to broaden application context and in Section 3.3 to temper claims about ex-ante policy relevance.

7) Liu et al., “MASS: Deep Research for Social Sciences with Memory-Augmented Social Simulation,” 2026 — Extends language-native simulations with memory for deeper research workflows. Discuss in Section 2.1/2.3 and Section 3.2 to contrast memory-augmented mechanism tracing with single-sentence intentions.

8) Wang et al., “AgentSocialBench: Evaluating Privacy Risks in Human-Centered Agentic Social Networks,” 2026 — A benchmark for safety/privacy in multi-agent setups. Include in Section 3.3 to motivate standardized stress-testing and safety evaluation for MASS-like frameworks.

## Comments Suggestions And Typos
Actionable suggestions:
1) Clarify interaction mechanics and agent communication
- Specify whether and how agents exchange messages, negotiate, or condition on others’ actions or texts over time. Provide a schematic (a new figure) showing the message flow per round, agent memory/state, and where numeric decisions are formed. If interaction is minimal in the current implementation, acknowledge this explicitly and scope claims accordingly.

2) Strengthen DID validity and reporting
- Add an event-study figure showing pre- and post-policy dynamics with CIs; report pre-trend tests. Provide numeric CIs or p-values for the DID estimates in Table 2. Consider alternative NJ:PA ratios and aggregated group-level analyses to test robustness. Include placebo tests and alternative windows.

3) Provide key implementation details in the main text
- Summarize the prompting schema, role descriptions, decoding parameters, and randomness controls. Include at least one ablation varying temperature and one varying time granularity. Show sensitivity to enforcing or omitting intention-text requirements across runs, and assess their influence on numeric outcomes.

4) Baselines and ablations
- Add a simple ABM baseline (hand-coded decision rules) and a second LLM-based framework or at least a second foundation model to demonstrate generality. Include ablations toggling legal price bands, varying agent counts, and using balanced NJ:PA sizes.

5) Systematic mechanism audit
- Develop a coding scheme for intention texts, report inter-annotator agreement, and link intention categories to observed actions over time. Provide a figure showing the distribution of intentions across rounds in runs A/B/D and the mandated-intention run D, to avoid cherry-picking.

6) Optional but impactful: show inter-run variance
- Include violin or box plots of agent-level outcomes by week to visualize dispersion and help reconcile “≈0” employment effects with wide CIs in Figure 1.

Typos and minor edits:
- Section 2.2: “?Searle, 1969” appears with a stray “?”; standardize citation formatting.
- Method Box itemization: ensure consistent punctuation and symbols (e.g., “$4.25→$5.05” spacing).
- Figure 1 caption: Consider including numeric 95% CI values in a supplementary table or directly on the plot for clarity.

Criteria that could increase my score:
- Addition of event-study and pre-trend diagnostics with numeric CIs supporting the employment “≈0” claim.
- Clear documentation of agent interaction, prompts, decoding, and message passing.
- At least one baseline or alternative model replication, plus core ablations demonstrating which design choices matter.
- A systematic, quantitative mechanism-audit of intention texts linked to behavior.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and checked figures/tables, but missing implementation details prevent full verification of claims.

## Soundness
2.5: Between Poor and Acceptable — The framing is promising and some evidence aligns with expectations, but the empirical foundation lacks critical diagnostics (pre-trends, ablations, baselines) and methodological specifics.

## Excitement
2.5: Between potentially interesting and interesting — The direction is timely and could be impactful with stronger validation, but current evidence is limited.

## Overall Assessment
2.5 Borderline Findings: The paper presents an appealing methodology and a sensible validation target, but lacks key technical details, diagnostics, and baselines needed for main-track acceptance. With added interaction clarity, stronger DID diagnostics (including pre-trends), thorough ablations, and at least one baseline or cross-model replication, this could rise to Findings or beyond.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges corpus and decoding biases and warns against equating simulation outputs with factual truth. Additional considerations:
- Proprietary model reliance may limit reproducibility and auditability; cross-model checks would mitigate this.
- Policy inference risk: Emphasize that simulation-based results should not be used for policy recommendation without triangulation against empirical data and established economic models.
- Bias auditing: Consider integrating checks for demographic or linguistic biases in agent decisions or intention texts, even in synthetic setups.

## Ethical concerns
None beyond standard concerns for LLM simulations. No human data is used; outputs are synthetic. The paper should, however, discuss the implications of using proprietary models for reproducibility and transparency.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The authors commit to artifacts and some logging, but the main text omits crucial details of prompting, decoding, and interaction, and relies on a single proprietary model.

## Datasets
1: No usable datasets submitted. (No new dataset contribution is central to the paper.)

## Software
3: Potentially useful. (If released as claimed, the simulation code and analysis scripts could help others, but usefulness depends on documenting prompts/decoding and clarifying interaction design.)