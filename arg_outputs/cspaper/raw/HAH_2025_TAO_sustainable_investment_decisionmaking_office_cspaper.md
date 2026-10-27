# Preliminary Observations:
Clear topical mismatch with ACL. The paper focuses on reinforcement learning for sustainable building investment, with LLMs used only for parameter extraction and stakeholder explanations. It does not present substantive NLP research, methodology, benchmarks, or insights of primary interest to the ACL community. All core sections are present; writing is in English; no prompt injection detected.

# Expected Review Outcome:

## Paper Summary
The paper proposes a reinforcement learning framework for life‑cycle investment decisions in office buildings that monetizes ESG factors and aligns RL discounting with economic NPV analysis. A DQN agent chooses among discrete actions at design, construction, and operation stages over a 20‑year horizon. Two theoretical statements are provided: equivalence between maximizing discounted RL return and minimizing NPV with ESG adders when γ = e^{-rΔt}, and the standard supported‑Pareto property for linear scalarization in a two‑objective (cost, carbon) setting. LLMs are used outside the training loop to (i) extract numeric parameters from unstructured guidance and (ii) generate stakeholder‑facing explanations, which are auto‑evaluated. Case studies for US and UK offices report sizable energy, carbon, and NPV improvements compared with conventional practice, with sensitivity and robustness analyses. The paper supplies a replication‑style appendix with scripts and commands.

## Summary Of Strengths
- End‑to‑end pipeline: The paper is well‑structured and documents an auditable workflow from data to RL training to sensitivity/robustness, with clear reproduction commands and file descriptions in the appendix.
- Practical framing: Casting sequential design‑construction‑operations decisions as an MDP is reasonable for life‑cycle reasoning, and the use of public data sources improves transparency (Table 1).
- Results clarity: Comparative outcomes are reported for two regional contexts with error bars and scenario analyses (Tables 2–5). Figure 5’s tornado chart usefully surfaces which drivers most influence LCC NPV.
- Figures support narrative: 
  - Figure 1 visualizes a cost–carbon frontier; it helps stakeholders understand trade‑offs along supported points.
  - Figure 2 shows how the “RL advantage” in societal NPV varies with γ, connecting discounting assumptions to outcomes.
  - Figure 3 provides a readable process diagram of the end‑to‑end pipeline.
- Reproducibility: The “Data and replication” section is unusually explicit (scripts, data workbook, run.sh), which is commendable for an applied systems paper.

## Summary Of Weaknesses
1) Out‑of‑scope for ACL. The central contribution is an RL decision‑support system for buildings, not NLP. LLMs are used only as a convenience tool for parameter extraction and drafting explanations, without new NLP methods, datasets, evaluations, or insights likely to interest ACL’s readership.

2) Limited novelty of theoretical results. 
   - Proposition 1 mainly restates a standard discounted‑cash‑flow equivalence under γ = e^{-rΔt} with undiscounted flows in rewards. This is a known accounting alignment rather than a substantive theoretical advance.
   - Proposition 2 is the classical result that linear scalarization recovers supported Pareto‑optimal points; it does not address unsupported points or propose an RL mechanism beyond standard scalarization.

3) Reward architecture and double‑counting clarity. Section 2.2 states r_t = −c_t + Σ_i α_i f_i(s_t) with discounting applied via γ^t and NPV “recovered externally.” It remains ambiguous how life‑cycle cost NPV in Tables 2–3 is computed relative to in‑RL rewards. For example, productivity benefits appear both as state‑dependent terms and as separate NPV figures, risking confusion over whether monetized co‑benefits are accounted for once or twice across reporting layers. A worked numeric example would help.

4) Baselines are weak for the RL claim. The comparisons are against “financial‑only” and “lowest first‑cost” heuristics, plus small MCDA/MILP heuristics on “simple subproblems” (Section 2.4), but there is no comparison to dynamic programming/planning over the small discrete action space, nor to a systematic LCCA/MCDA policy optimized under the same stochastic assumptions. This makes it hard to credit the RL component specifically for the gains.

5) Fragility of social multipliers and externalities. The largest headline benefits hinge on “productivity NPV” and SCC assumptions (Tables 2–4). Figure 5 shows α weights and productivity assumptions dominate NPV swings. While sensitivity analysis is reported, the paper would be stronger with uncertainty‑aware end‑to‑end propagation (e.g., joint distributions) rather than one‑at‑a‑time swings. Otherwise, conclusions about “robust” societal NPV could be overstated.

6) Inconsistencies and possible errors in Tables:
   - Table 2 “Productivity NPV ($ million)” shows 0 versus 10.11, yet “Difference” column lists “1” rather than approximately “+10.11.” 
   - Table 3 “Productivity NPV (£ million)” shows 0 versus 5.42, yet “Difference” shows “0.6.” These likely transcription/units errors undermine trust in other deltas.
   - Check also that “Societal cost NPV decreases by $12.00M” in text (Page 6, Sec. 3.1) is consistent with the −$3.50M difference reported in Table 2, which seems not to match.

7) Figure‑level issues:
   - Figure 1’s points suggest a non‑convex shape with gaps; it is unclear how the frontier was constructed and whether each point comes from distinct scalarization weights or post‑hoc selection. Clarify sampling, seeds, and whether dominated points are shown.
   - Figure 2 varies γ across a wide range, but the Methods fix γ = e^{−0.03} ≈ 0.97. The figure suggests conclusions depend heavily on γ, yet the paper does not justify alternative discount rates beyond public‑sector norm. Link Figure 2 to decision‑maker‑specific r and report how policy changes qualitatively.
   - Figure 4 aggregates multiple metrics into a single bar chart with different units and scales. This makes interpretation difficult. Consider separate panels or normalized indices with clear legends and units.

8) Experimental design leaves open simpler explanations. The discrete, small action space and short horizon for pre‑operation steps suggest that tabular or exact dynamic programming could deliver the same policy without approximation error, training instability, or replay buffer choices. The paper does not justify DQN over exact methods, nor quantify sensitivity to architectural choices beyond small ablations.

9) LLM component is not a research contribution. Parameter extraction via prompting and automated explanation scoring with QA‑style checks (Table 6) are implementation details. There is no human evaluation, no model comparison, and no novel NLP approach. The “92–94%” auto‑scores are not calibrated to real stakeholder understanding or factuality under distribution shift.

10) Compute/runtime reporting inconsistency. Table 7 reports training with “120 episodes,” yet Section 2.4 describes training with 5000 episodes. Reconcile which regime is used for the headline Tables 2–5.

11) Claims and numbers occasionally do not align. Section 3.1 states “Societal cost NPV decreases by $12.00M” in the US case, but Table 2 shows −$3.50M. Similar discrepancies appear for the UK text vs. Table 3. These gaps should be resolved.

12) Limited external validation. Results are simulation‑based and rely on secondary estimates for social valuation; there is no validation on real procurement data or blinded expert review of LLM explanations, as the paper itself notes.

Explicit references to figures/tables:
- Figure 1: The plotted frontier does not make clear whether points are all supported by linear scalarization weights or include dominated solutions; the method for constructing the curve should be documented to support Proposition 2’s practical relevance.
- Figure 2: Shows that the RL societal NPV advantage shrinks as γ increases toward 1.0. This undercuts strong claims of robustness unless decision‑maker‑specific r values are justified and reported with policy differences.
- Figure 5: Indicates α_weight and retrofit_productivity dominate LCC NPV variance, reinforcing that co‑benefit monetization drives outcomes more than core energy/carbon effects; this should temper the headline narrative.
- Table 2 and Table 3: These central result tables include clear arithmetic/units inconsistencies in the “Difference” columns for productivity NPV. Given their importance, these errors require correction and an audit of all deltas and summary claims derived from them.
- Table 5: Under +2°C, the conventional strategy’s societal NPV becomes positive while RL becomes more negative (−$3.75M vs +$0.50M advantage). The interpretation “RL’s relative advantage grows” is plausible, but the sign conventions and what “negative” denotes should be re‑explained to avoid confusion.

## Potentially Missing Related Work
1) Reinforcement learning‑based optimization framework for carbon emission reduction and circularity enhancement in buildings (2026) — Very close in life‑cycle framing, carbon objectives, and RL methodology. Should be discussed in Section 2 and contrasted in Related Work; consider as a conceptual baseline for extending beyond carbon to broader ESG monetization.

2) Ma et al., 2026, Adaptive smart energy management in buildings: A deep reinforcement learning and IoT framework for energy efficiency and thermal comfort — Field deployment with multi‑objective control; compare in Section 3.1 and add to the discussion of robustness and real‑world variability.

3) Guo et al., 2025, Deep RL control for co‑optimizing energy consumption, thermal comfort, and indoor air quality in an office building — Strong DDPG baseline with comparisons to MPC; relevant to the operational phase and multi‑objective reward design; cite in Section 2.2 and discuss as a baseline in the Results.

4) Xia et al., 2024, Multitask DRL recommender for energy, comfort, and air quality with humans‑in‑the‑loop — Relevant to stakeholder‑centric decision support and occupant behavior modeling; cite in Section 2.2 and discussion on explainability/LLMs.

5) Lee et al., 2022, Assessment of on‑policy DRL for building control efficiency and stability — Useful for stress‑testing DRL stability and safety; discuss in Section 2.4 and robustness (Section 3.3).

6) Ding et al., 2023, Holistic DRL for multi‑subsystem smart building control — Offers a broader MDP structure and holistic control; compare with your staged MDP in Section 2.2.

7) Jang et al., 2022, Demand response with DRL and guardrails — Discuss in Section 2.4/3.3 as it connects decarbonization, financial outcomes, and deployment constraints, resonating with your “governance” theme.

8) Herzog et al., 2023, Deep RL at Scale for building waste sorting — While task‑different, it informs real‑world deployment, data efficiency, and robustness. Mention in the Discussion on scaling your framework to live assets.

## Comments Suggestions And Typos
Actionable suggestions:
- Clarify and fix numeric inconsistencies. Audit Tables 2–3 “Difference” columns for Productivity NPV and reconcile the narrative in Section 3.1 with table values (e.g., “$12.00M” vs “$3.50M”). Provide a signed‑convention note for Tables 4–5.
- Provide a worked example. Include a one‑page numeric walk‑through that shows exactly how r_t is formed from costs and monetized co‑benefits, how γ is applied, and how LCC/“Societal cost NPV” are derived for reporting. This will eliminate ambiguity about double counting.
- Strengthen baselines. Add: (i) exact dynamic programming or value iteration over the discrete space; (ii) an LCCA/MCDA optimizer that uses the same stochastic assumptions; and (iii) a planning baseline that optimizes the same scalarized reward. Report in a new results table.
- Tighten the role of LLMs. If kept as a contribution, add a small human study comparing LLM explanations against expert write‑ups on faithfulness, usefulness, and numerical accuracy; or compare multiple LLMs with ablation on prompt constraints. Otherwise, present LLM use as an engineering aid, not a research result.
- Expand uncertainty treatment. Replace one‑at‑a‑time sensitivities with joint uncertainty propagation (e.g., Monte Carlo over SCC, prices, productivity, carbon intensity) and show distributions for LCC and societal NPV.
- Figures: 
  - For Figure 1, explain how points are generated (weights, seeds), whether dominated points are filtered, and include uncertainty bars if applicable.
  - For Figure 4, avoid mixing heterogeneous units in a single panel; split or normalize.
  - For Figure 2, discuss decision‑maker‑specific r and show policy or action‑frequency shifts across γ, not just aggregate NPV advantage.

Minor typos and nits:
- Page 6, Sec. 3.1: “Societal cost NPV decreases by $12.00M” appears inconsistent with Table 2 (−$3.50M). 
- Table 2/3: Fix “Difference” for Productivity NPV rows (currently “1” and “0.6”).
- Section 2.2: “Intermediate rewards equal the negative of the immediate cost plus any instantaneous social value,” but “NPV is recovered externally,” which is potentially confusing; tighten wording.
- Table captions: add unit notes for all monetary entries (NPV in 2023 USD/GBP) and clarify whether negatives are “reductions” vs “losses.”

Criteria that could increase my score:
- Demonstrate substantive NLP contribution (new method, dataset, or evaluation) or reposition the work squarely as an NLP paper; or
- Add rigorous algorithmic baselines and resolve all numeric inconsistencies, with improved uncertainty analysis and a human evaluation for the LLM explanations.

## Confidence
4: Quite sure after careful checking — I carefully checked the core claims, equations, and tables, and verified consistency across sections.

## Soundness
2: Poor — Several methodological and reporting inconsistencies (tables, accounting clarity), weak RL baselines, and limited evidence for the LLM component’s research contribution.

## Excitement
2: Potentially Interesting — The application area is valuable, but the NLP relevance is limited and the technical novelty is modest.

## Overall Assessment
1: Do not resubmit — The paper is out of scope for ACL and lacks substantive NLP contribution. In addition, numerical/reporting inconsistencies and insufficient baselines weaken the technical case.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges important limitations: reliance on secondary multipliers for social value, stylized transition dynamics, and auto‑evaluation of LLM explanations. Potential negative impacts include over‑reliance on monetized health/productivity proxies and miscalibration of SCC or α weights that could bias procurement. I encourage adding a more explicit discussion of who bears risks if estimates are wrong, and how governance mitigations (audit trails, expert panels, sensitivity envelopes) would be enforced in practice and procurement.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The appendix and scripts are detailed, but numeric inconsistencies, unclear reward/NPV accounting, and a dependence on proprietary LLM tooling without full prompt/eval release make exact replication nontrivial.

## Datasets
2: Documentary — No new dataset; collated public data/workbooks are useful for replication but have limited standalone value.

## Software
3: Potentially useful — The RL environment, scripts, and evaluation tooling appear usable; value would increase with corrected results, stronger baselines, and clearer documentation of the LLM components.