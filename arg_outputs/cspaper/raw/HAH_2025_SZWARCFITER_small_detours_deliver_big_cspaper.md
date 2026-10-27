# Preliminary Observations:
The submission is squarely about public transit operations and transportation simulation, not computational approaches to human language. It does not address NLP, language modeling, linguistics, or any ACL topic area. Hence it falls outside ACL’s scope.

# Expected Review Outcome:

## Paper Summary
The paper studies whether fixed-route buses on partially overlapping corridors can make brief, bounded off-corridor detours to serve nearby side stops without degrading headway regularity. It formalizes two online accept/reject policies evaluated in a discrete-event simulator: (i) Myopic-Feasible, which accepts requests that pass capacity and feasibility checks, and (ii) Slack-Aware, which accepts only when a simple headway-risk score is below a threshold. A 2⁴ factorial design varies excursion budgets, return-to-corridor windows, side-stop geometry, and reliability. Key findings are that Myopic-Feasible reduces average waiting time and abandonments with negligible impact on headway CV and minimal excursion kilometers, while the default Slack-Aware threshold is overly conservative, increasing waits and abandonments, suggesting the need for calibration.

## Summary Of Strengths
- Clear problem framing within a well-motivated operational gap between fixed-route and fully flexible DRT, with safeguards (budgets, windows, risk gating) that are implementable.
- Methodological transparency: scenario factors and parameters are explicitly defined, including stochastic generators, dwell models, and replication strategy; code, data, and logs are promised as open resources.
- Quantitative evidence is presented with confidence intervals and multiple KPIs that align with policy questions. 
- The paper leverages a simple, auditable risk score that could be operationally deployed and tested.
- Concrete, visual presentation of scenario-level heterogeneity and trade-offs:
  - Figure 1 (all panels) shows how Myopic-Feasible improves average wait and abandonment relative to Baseline across most scenarios with near-constant headway CV; Panel (d) confirms excursion kilometers are tiny.
  - Table 2 aggregates across all scenarios and reinforces that headway CV remains nearly unchanged across policies while Myopic-Feasible substantially reduces waits and abandonments.
  - Figure 2 makes the compliance/access trade-off explicit: Slack-Aware reduces missed return-window violations relative to Myopic-Feasible but at the cost of far fewer accepted excursions.

## Summary Of Weaknesses
1) Out of scope for ACL. The topic is transportation operations and simulation, not NLP or computational linguistics. There is no connection to language technologies, data, or analysis. This is the primary reason it is unsuitable for ACL.

2) Limited external benchmarking. While the paper positions itself among flex-route and DRT literature, it does not compare the proposed bounded-excursion policies against other semi-flexible or hybrid designs within a shared simulation framework. For example, no comparison to alternative semi-flexible baselines such as loop deviation or station-based feeders that could be configured in the same environment. This limits the generality of conclusions.

3) Slack-Aware risk model is simplistic and under-justified. The “risk” definition (Section 2.5, risk = 0.5·load ratio + 0.5·headway_clock/h_planned, threshold 0.6) is chosen ad hoc. The paper shows that this default threshold is too conservative, but it does not provide a systematic calibration protocol, ablation on weights, or sensitivity curves over thresholds. This weakens guidance on how an agency should set these parameters.

4) Reliability conclusions hinge on a narrow metric. Headway CV at control points remains nearly constant across policies (Table 2 and Figure 1c), but there is no analysis of spatial-temporal headway profiles, tail metrics, or probability of bunching. Minor changes to CV can obscure localized reliability degradation that matters in practice.

5) Return-window violations and their implications are under-explored. Figure 2 shows a high missed return-window rate for Myopic-Feasible (~43%) and non-trivial rates for Slack-Aware (~27%). The text downplays the operational consequences of these violations, which, if enforced in the real world, could trigger denials, penalties, or safety issues. A scenario breakdown of violations, causes, and mitigations is missing.

6) Confounding of feasibility and gating. Since Slack-Aware both enforces feasibility and gates on risk, it becomes hard to isolate which component drives performance changes. A clearer ablation (feasibility-only vs. feasibility+gating with multiple thresholds) would strengthen causal interpretation.

7) Generality to bus network contexts is limited. The study focuses on two lines, off-peak, uniform arrivals, and small groups, with moderate capacity slack. Important dimensions such as peak demand, heterogeneous stop demand, interlining, or coordinated control (e.g., holding) are not covered, limiting applicability of the rules-of-thumb.

8) Cost and labor considerations are not modeled. The KPIs omit agency-facing costs (driver duty complexity, schedule robustness, safety margins) and community-facing impacts (e.g., curb management at side stops). This makes it difficult to evaluate whether benefits in waiting/abandonment outweigh operational overhead.

9) Insufficient analysis of equity across stops. The paper mentions equity concerns qualitatively, but does not disaggregate KPIs by stop type or geography. Policies that systematically under-serve side stops when thresholds are too conservative could have disparate impacts; empirical stratification is needed.

10) Limited statistical depth. While 95% CIs are reported, there are no formal statistical tests for factor effects or interactions in the 2⁴ design. A simple ANOVA or mixed-effects analysis could quantify main and interaction effects of budgets, windows, geometry, and reliability on KPIs to support the narrative seen in Figure 1.

11) Figure/Table-specific critique and interpretation:
   - Table 2: The headway CV values differ only in the fourth decimal place (e.g., 0.100124 vs. 0.100296). The paper concludes there is “no measurable impact,” but given very large sample sizes across replicates, even tiny differences could be meaningful. Reporting CIs or standard errors for CV in the aggregate table would help avoid over-interpretation.
   - Figure 1(c): Error bars show overlap, yet a few scenarios exhibit visibly larger variance for Myopic than Baseline. The text does not discuss whether certain factor settings amplify CV variance. Linking panel (c) patterns to factor levels in Table 1 would make the mechanism clearer.
   - Figure 2: A 42.57% missed return-window rate under Myopic is operationally alarming if violations are truly “hard” constraints. The discussion states that violations were “rare,” which contradicts the figure. This needs reconciliation and a drill-down on when/why violations occur.

## Potentially Missing Related Work
1) Yoon et al., “A simulation sandbox to compare fixed-route, semi-flexible-transit, and on-demand microtransit system designs,” 2021 — Provides a unified environment to compare fixed, semi-flexible, and on-demand services. The paper should discuss how its excursion policies relate to semi-flexible designs in Section 1 and consider replicating or contrasting results in Section 3/4.

2) Leffler et al., “Simulation of fixed versus on-demand station-based feeder operations,” 2021 — Station-based feeders are a direct comparator to bounded excursions. Add to Related Work and discuss as an alternative policy baseline; if feasible, include as an additional baseline in Section 3.

3) Guo et al., “Optimal fare and headway for a demand adaptive paired-line hybrid transit system,” 2024 — Paired-line hybrid analysis is closely aligned with overlapping corridors. Cite in Section 1–2 and contrast policy levers with excursion budgets and return windows; discuss implications for headway setting in Section 4.

4) Ng et al., “Semi-on-Demand Hybrid Transit Route Design with Shared Autonomous Mobility Services,” 2024 — Analytically tractable semi-on-demand hybrids provide a cost-coverage trade-off baseline. Add to Related Work and contrast in Discussion, especially regarding fleet size and headway interplay.

5) Olivos et al., “Modeling flex-route transit systems with a continuous approximation Markovian approach,” 2026 — Offers an analytical lens on deviations, slack, and reliability. Cite in Section 2.5 to connect the risk model and in Section 4 for calibration insights.

6) Shen et al., “Supplementing Fixed-Route Transit with Dynamic Shared Mobility Services: A Marginal Cost Comparison Approach,” 2022 — Provides cost/user-experience benchmarks for supplementing fixed-route services. Add to Related Work and propose cost comparisons in future work or an extended KPI set.

7) Farghly et al., “Mutual information–based line criticality analysis in public transport networks,” 2026 — Relevant for identifying where overlapping lines can tolerate excursions. Cite in Section 4.5 and suggest using criticality to localize excursion permissions.

8) Burke et al., “A Swarm Approach to Public Transit Using On-demand Routing in a Slime-Mold-Inspired Framework,” 2026 — Presents a contrasting decentralized routing approach. Briefly situate in Related Work as an alternative to rule-based excursions and discuss in Section 4 how centralized risk gates compare to distributed online decisions.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide a calibration protocol for Slack-Aware. Include sensitivity sweeps over thresholds and weights in the risk score and report ROC-like curves showing access vs. reliability trade-offs. A small grid search with held-out replicates would already strengthen claims.
- Disaggregate outcomes. Report KPIs by stop type (corridor vs. side), by geometry settings, and by reliability level to substantiate equity and heterogeneity claims. A simple two-way or three-way ANOVA across the 2⁴ factors would add statistical backing.
- Clarify the severity of return-window violations. Are these hard constraints? If so, 42.57% (Figure 2) is not “rare.” Provide per-scenario violation rates and root causes; propose enforceable mitigations (e.g., dynamic windows or micro-holds).
- Add at least one external semi-flexible baseline (e.g., station-based feeder or loop deviation policy) in the same simulator to contextualize benefits of bounded excursions. Even a simplified proxy would help.
- Enrich reliability metrics. Complement headway CV with tail quantiles of headway gaps, fraction of extreme headway deviations, and spatial-temporal heatmaps of headways along the overlap to ensure localized reliability problems are not masked.

Typos/clarifications:
- Page 7, “violations were rare on average” conflicts with Figure 2’s 42.57% for Myopic. Reconcile wording with data.
- Table 1 notes “Slack-Aware gating: Accept if headway risk score ≤ 0.6.” Consider citing how 0.6 was chosen or mark it explicitly as a placeholder to be calibrated.
- Ensure consistent capitalization of policy names (e.g., “Myopic-Feasible,” “Slack-Aware”) throughout.
- Units: In Table 1, “T_max min” should read “T_max minutes” for clarity.

What could change my score:
- If the authors convincingly connect their methods to an NLP-relevant framing (e.g., learning-based online decision policies trained from textual incident logs, natural-language driver dispatch interfaces evaluated with language models, or language-driven policy calibration) and add empirical evidence of such a component, the scope mismatch would be mitigated.
- Alternatively, absent an NLP connection, a transfer to an appropriate transportation venue is advisable.

## Confidence
4: Quite sure after careful checking — The scope mismatch is unambiguous; the technical reading is careful.

## Soundness
3.5: Between Acceptable and Strong — The simulation is transparent and thoughtfully designed, but the risk model calibration is ad hoc and some interpretations (return-window “rarity”) conflict with Figure 2.

## Excitement
1.5: Slightly below potentially interesting — For ACL audiences this is outside scope; within transportation it may interest practitioners.

## Overall Assessment
1: Do not resubmit — Not relevant to ACL; strong scope mismatch despite a reasonably sound and reproducible simulation study. The work would be better suited to transportation or operations research venues.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges key limitations: stylized off-peak setting, simplified demand/dwell models, and the need for local calibration. Additional points to consider:
- Potential labor and safety implications of frequent rejoining maneuvers and driver workload; coordination with labor rules and training.
- ADA and accessibility impacts at side stops selected for excursions.
- Equity impacts quantified by stop type and neighborhood demographics.
- Cost trade-offs for agencies, including schedule robustness and maintenance from more turns.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
5: Easily reproducible — Parameters are explicit, and datasets/code/run logs are stated to be openly available.

## Datasets
3: Potentially useful — The simulation datasets could be useful for follow-up studies and calibration.

## Software
4: Useful — The simulator and scripts appear suitable for adaptation and replication by agencies and researchers.