# Preliminary Observations:
- Topic fit is weak for ACL: the contribution centers on multi-agent reinforcement learning and emergent communication in a toy gridworld with discrete symbols; there is no natural-language data, modeling, or evaluation. The closest tie to ACL is “Human-Centered NLP” and “Dialogue/Interactive Systems,” but the work does not engage natural language or NLP benchmarks.
- There are internal inconsistencies between reported metrics across sections (e.g., Success Rate ≈ 85.5% in Table 2 vs. 3–16% SR values reported for ablation variants in Table 6 and Figure 2), raising basic reporting reliability concerns.

# Expected Review Outcome:

## Paper Summary
The paper proposes Bidirectional Cognitive Alignment (BiCA), a framework in which both the human and the AI co-adapt their policies, communication protocol, and internal representations under KL “budget” constraints. The method comprises: an AI policy with recurrent state, a human-surrogate policy with a learnable protocol table, a Gumbel-Softmax protocol generator, a representation mapper aligning human and AI latent spaces via OT and CCA, and an instructor that chooses interventions. The composite objective (Equation 7) adds KL-budget penalties, an information bottleneck on communication, a representation-alignment loss, and a teaching penalty, optimized with PPO for both agents and dual-variable updates. Experiments are conducted in an 8×8 partially observable gridworld (MapTalk) and a separate VAE latent-space “Navigator” task. The paper introduces new metrics for “co-alignment,” and reports sizable gains of BiCA over a single-directional baseline.

## Summary Of Strengths
- Ambitious reframing: The paper argues for bidirectional cognitive adaptation, contrasting to unidirectional RLHF. The objective in Equation 7 is clearly specified and integrates multiple constraints (KL budgets, IB, representation alignment) in a coherent way.
- Algorithmic clarity: Sections 3.2–3.3 and Appendix A provide the core components and a training loop (Algorithm 1). Dual-variable updates for KL budgets are a sensible, principled control knob.
- Well-motivated components: The protocol generator with Gumbel-Softmax (Equation 3) and the information bottleneck regularizer are appropriate choices for learning discrete communication with capacity control. The representation mapper objective tying Wasserstein distance with CCA is interesting and connects to representation-alignment literature.
- Some reproducibility steps: Compute envelope and random seeds are listed in Appendix A.2–A.3. Hyperparameter levers for ablations are cataloged (Appendix B.1).
- Figures help orient the reader: 
  - Figure 1a concretely illustrates the asymmetric information structure in MapTalk, making the communication need intuitive.
  - Figure 2 provides an at-a-glance ablation overview across variants and metrics, which is useful for diagnosing which levers matter most.
- Quantitative deltas in the main table are sizable: Table 2 reports BiCA outperforming the baseline across Success Rate (+21.6%), Avg Steps (-9.9%), BAS, and CCM with p < 0.001 and large effect sizes.

## Summary Of Weaknesses
1) ACL topical fit is weak. The work does not involve natural language or NLP tasks, datasets, or models. Communication is symbolic and domain-specific; there is no mapping to language, pragmatics, or grounded language evaluation that ACL audiences expect. Positioning as “Human-AI collaboration” without any language content limits relevance to ACL.

2) Baseline coverage is too narrow. The “single-directional RLHF” baseline disables multiple BiCA components, but there are many established communication and co-adaptation baselines from multi-agent RL that should be included for a fair test: e.g., CommNet (Sukhbaatar et al., 2016), RIAL/DIAL (Foerster et al., 2016), differentiable communication via channel regularization, LOLA [32], and CIRL [22]. Without these, it is unclear whether the reported gains are due to bidirectionality per se or simply the presence of any learned protocol and alignment regularization.

3) Internal inconsistencies in reported numbers. 
- Main results (Table 2) show Success Rate ≈ 85.5% vs. 70.3% for the baseline. However, Table 6 (ablation) reports SR values mostly between 0.03 and 0.16, and Figure 2 annotates success rates in a similarly low range. It is not explained whether these are different tasks, different success definitions, or different scaling/normalization. This undermines trust in the empirical narrative. Please clarify if Table 6/ Figure 2 are reporting per-variant deltas, tiny-sample debug runs, or a different metric scale.
- BAS/CCM are reported in Table 2 around 69% and 82%, while Table 6 lists BAS ≈ 0.30–0.50 and CCM ≈ 0.52–0.55. The paper should explicitly state units, normalization, and how to reconcile these mismatches.

4) Statistical reporting is opaque. The paper repeatedly states p < 0.001 and large Cohen’s d for all comparisons (Table 2 and Table 3) but does not specify: 
- the number of episodes and seeds used for the main comparisons (Section 5.1.1 does not state N; Appendix B.2 gives S=5 seeds, N=100 per variant for ablations, but not for the main results),
- which statistical test was used (two-sample t-test on per-seed means? nonparametric?),
- whether assumptions (normality, equal variances, independence) hold.
Given the complexity and non-normal performance distributions in RL, this needs careful justification.

5) New metrics lack validation. The Bidirectional Alignment Score (BAS) is an average of several normalized components, some of which depend on surrogate models and normalization schemes (Equations 10–14). Similarly, CCM mixes HSIC-based diversity with a weighted synergy term (Equation 15). There is no sensitivity analysis showing that conclusions are robust to normalization choices or component weighting, nor comparison to established interaction/communication metrics. This is important because much of the claimed contribution hinges on BAS/CCM improvements.

6) Claims not backed by tables/figures. The abstract and conclusion assert “emergent protocols outperformed handcrafted ones by 84%” and “+23% OOD robustness,” but there is no dedicated table or figure presenting those specific comparisons, task settings, or definitions of “handcrafted” and of OOD shift. If Figure 2 or Table 6 are meant to support OOD claims, they should report OOD metrics consistently and explicitly link to the 23% number.

7) Ambiguity in the “human” component. The method trains a “human surrogate” (Equation 2) with protocol table updates and noise processes. While that enables controlled experimentation, it does not demonstrate co-adaptation with real humans or even with realistic human-like behavior distribution shifts. It is fine as a first step, but the paper generalizes to “humans and AI” quite strongly throughout. The limitations section recognizes this, but several strong takeaways in Sections 1 and 6 still read as overgeneralizations.

8) Limited environment scope. All results are in an 8×8 gridworld with short horizons and discrete messages, plus a VAE “Navigator” toy setup. Without tests on richer grounded language tasks (e.g., Vision-and-Dialog Navigation, as referenced [67–69], or even controlled natural-language channel variants), it is hard to assert the broader significance of “co-alignment” for real-world language-based collaboration.

9) Objective coupling not fully ablated. While there is a 15-variant ablation grid, several critical components are not disentangled. For instance:
- What is the performance if the protocol generator is present but the representation mapper is removed, and vice versa, under equal KL budgets?
- What is the effect of the CCA term alone vs. Wasserstein alone in L_rep?
- How sensitive are results to the specific KL budget thresholds τ_A and τ_H?
Currently, Figure 2 provides a high-level heatmap but does not expose these causal attributions clearly.

10) Figure- and table-specific concerns.
- Figure 1a: The asymmetric observations are well-illustrated; however, to support the co-alignment claim, it would be helpful to annotate an example episode where the learned protocol changes over time, so readers see how messages evolve in context.
- Figure 2: While it is a helpful overview, the color normalization and the raw values produce confusion vis-à-vis Tables 2–3 (see inconsistency in point 3). Please unify scales or explicitly explain the scaling used for this figure.
- Table 3: “Mutual Adaptation Rate,” “Protocol Convergence,” and “Representation Alignment” are central to the claim. Their operational definitions and measurement protocols should be clearly specified (e.g., for Protocol Convergence, what is the distance metric over code distributions? over message bigram frequencies? how is convergence time determined?).

11) Reproducibility gap. The paper does not state that code will be released, nor does it document environment seeds for the main experiments directly in Section 5. Key hyperparameters for BiCA components (e.g., τ_end, γ in Equation 3, concrete τ_A, τ_H) are not fully enumerated in the main text. Given the bespoke metrics and surrogates, code availability is important.

12) Safety and ethics claims are premature. The abstract and conclusion suggest that “bidirectional adaptation unexpectedly improved safety (+23% OOD robustness).” Safety is broader than OOD success or fewer collisions; calibration and harm analysis would require richer scenarios, and the definition of “safety” in Equation 13 is reductionist. The discussion should tone down the safety framing or provide much stronger evidence.

## Potentially Missing Related Work
- Sukhbaatar et al., “Learning multiagent communication with backpropagation,” NeurIPS 2016 — foundational differentiable communication (CommNet) that should be compared as a baseline and discussed in Section 2 and in the MapTalk experiments.
- Jaques et al., “Social Influence as Intrinsic Motivation for Multi-Agent Deep RL,” ICML 2019 — promotes coordinated communication/adaptation via influence; relevant as an alternative driver of mutual adaptation to be cited in Related Work and potentially added as a baseline.
- Eccles et al., “Biases for Emergent Communication in Multi-Agent Reinforcement Learning,” NeurIPS 2019 — examines pressures shaping protocol emergence; relevant to Section 3.2 Protocol Generator and the information bottleneck choice.
- Strouse et al., “Cooperative Communication with Deep Reinforcement Learning,” NeurIPS 2018 — examines communication learning in cooperative settings; relevant as a baseline family and to discuss in Section 4 with MapTalk results.

## Comments Suggestions And Typos
Actionable questions and suggestions:
1) Resolve metric inconsistencies. Reconcile Table 2 vs. Table 6 vs. Figure 2 for Success Rate, BAS, and CCM. Explicitly indicate units, normalization, and whether these are different experimental regimes. A single consolidated table that reports ID and OOD SR, BAS, CCM, Avg Steps for the main comparison, plus per-variant deltas in an appendix, would help substantially.
2) Expand baselines. Add at least one differentiable-communication baseline (CommNet or DIAL), one opponent-aware/bidirectional baseline (LOLA), and CIRL. If full reimplementation is heavy, at minimum include a protocol-learning MARL baseline with comparable capacity and messaging costs. Report them in a new results table alongside Table 2.
3) Clarify the statistics. State the number of seeds and episodes for main results, detail which tests are used (e.g., two-sample t-tests on per-seed means), and justify assumptions. Provide confidence intervals and discuss variance typical of RL. If normality is doubtful, consider nonparametric tests or bootstrap CIs.
4) Define co-alignment metrics operationally. For BAS/CCM, append precise definitions: how normalization constants are computed, how surrogates are trained/evaluated, and show robustness to component reweighting. Consider a sensitivity figure demonstrating conclusions are invariant to reasonable weight ranges.
5) Strengthen Figure 1/qualitative analysis. Add a panel showing a representative episode with message traces and how the protocol shifts across training phases. This will ground the “mutual adaptation” claim qualitatively.
6) Calibrate “safety” language. If “SS” is mostly OOD success minus collisions and miscalibration, say so explicitly and avoid broad “safety” claims. Consider reporting additional OOD stressors and failure analyses.
7) Human-subjects planning. Since the narrative is about human–AI co-adaptation, outline a feasible human study with hypotheses, measurable endpoints, and risk mitigations, even if deferred to future work. This would make the framing more credible.
8) Reproducibility. Commit to releasing code and configuration files, including environment generation, metrics computation, and the human-surrogate implementation. Document key hyperparameters not currently specified (e.g., τ_A, τ_H, τ_start/end, γ).

Minor typos and nits:
- Page 4, “We employ alternating optimization with adaptive dual variable updates to maintain constraint satisfaction throughout training (see Algorithm 1 in Appendix A for implementation details).” The pointer is correct, but list default τ_A, τ_H near Equation 7 in the main text.
- In Figure 2 caption, spell out which normalization is applied to each metric axis and whether higher is always better.
- Page 7, Section 5.2.1: “The 68.1% CCA correlation … 59.4% preference correlation …” specify sample size and protocol for computing these numbers (per-session means? pooled?).
- Use consistent notation for latents and mappings; Equations 5 and L_rep reference z^H, z^A, and T_ψ, but the Wasserstein term compares P(z^H) and P(T_ψ(z^H)) rather than P(z^H) and P(z^A). Explain the rationale clearly.

What could change my assessment:
- Adding strong, fair MARL communication baselines and resolving the metric inconsistencies would substantially raise Soundness.
- Clear, reproducible definitions and sensitivity analyses of BAS/CCM would improve confidence.
- A small-scale human-user pilot in MapTalk or Navigator (even N=12–20) showing measurable bidirectional adaptation would strengthen significance and ACL relevance, especially if done with natural-language variants.

## Confidence
3: Reasonably confident but not fully verified — Pretty sure of the technical concerns and positioning, but I did not have code to verify the metrics or reproduce the statistics.

## Soundness
2.5: Between Poor and Acceptable — The framework is well-specified, but experimental evidence is weakened by baseline gaps, statistical opacity, and inconsistent reporting.

## Excitement
2.5: Between potentially interesting and interesting — The bidirectional framing is thought-provoking, but the current empirical scope and ACL fit limit excitement.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is interesting and the method is clearly written, but the ACL fit is weak, baselines are insufficient, and result inconsistencies need to be resolved. With stronger baselines, clarified metrics/statistics, and better alignment to language-centric evaluation, this could rise to a stronger case.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper includes a limitations discussion acknowledging surrogate humans, simple environments, and ethical questions about shaping human behavior. This is appreciated. Missing, however, is a concrete harm analysis for cases where the instructor or protocol learning might nudge users toward suboptimal or unsafe behaviors, especially under asymmetric power or information. For societal impact, the authors should articulate governance mechanisms for KL-budget choices when real humans are involved, consent and transparency around adaptation, and safeguards against manipulative or coercive protocol emergence. If future work uses natural language, risks escalate and would require stronger mitigation plans.

## Ethical concerns
None beyond the concerns already identified. The paper uses synthetic/surrogate agents and toy environments, so immediate risk is low. However, the safety framing should be more cautious, and future human-subjects plans should consider informed consent, debriefing, and limits on AI-initiated cognitive steering.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Seeds and some details are given, but code is not promised and several hyperparameters/metric definitions are underspecified. The inconsistencies across tables also hinder reproduction.

## Datasets
1: No usable datasets submitted.

## Software
2: Documentary. The description could help replication, but lack of released code limits usability for others.