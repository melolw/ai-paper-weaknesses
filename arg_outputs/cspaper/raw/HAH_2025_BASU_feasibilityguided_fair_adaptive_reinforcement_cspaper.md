# Preliminary Observations:
The submission’s core contribution is an offline reinforcement learning method for Medicaid care management. While there is a brief mention of NLP-extracted social determinants of health, the paper is not about computational approaches to human language, and its main technical content lies squarely in healthcare RL, safety, and fairness. This constitutes a significant topical mismatch with ACL’s scope.

# Expected Review Outcome:

## Paper Summary
The paper proposes FCAF-RL, an offline reinforcement learning framework intended to learn safe and fair care-management policies for Medicaid beneficiaries. It integrates three strands: feasibility-guided diffusion-based augmentation to constrain actions to a clinician-defined safe region, an RL objective with an equalized-odds fairness penalty, and constraint-adaptive policy switching to meet fairness targets at deployment. Using weekly trajectories from three states (Washington, Virginia, Ohio) and a leave-one-state-out evaluation, the authors report lower acute event rates and reduced fairness disparities compared to several baselines. Ablations suggest each component contributes to the final performance.

## Summary Of Strengths
- Addresses a societally important application, aiming to reduce acute events while improving equity in Medicaid care management.
- Clear, modular framing: feasibility constraints via generative augmentation, fairness-regularized Q-learning, and adaptive switching are presented as separable components.
- Cross-state generalization is evaluated, which is a reasonable stand-in for domain shift.
- The ablation in Table 2 is informative: removing fairness (“NOFAIR”) improves event reduction but increases disparity, while removing augmentation (“NOAUG”) worsens both metrics relative to the full model, supporting the claim that each element matters empirically.
- Figure 1 provides a compact visual comparison of event reduction and fairness disparity reduction together. The side-by-side bars with 95% CIs help readers see trade-offs at a glance; FCAF-RL’s blue and orange bars being highest is consistent with the claimed wins.
- Table 1 gives a broad head-to-head comparison on acute event rate, relative reduction, NNT, and fairness disparity, including confidence intervals.

## Summary Of Weaknesses
1) Topical mismatch with ACL. The work is a healthcare RL paper with limited connection to NLP beyond a one-line mention that some social determinants were extracted via NLP. It does not engage with NLP methodology, resources, or evaluation in a way that would interest the ACL community.

2) Internal inconsistency in the evaluation protocol. Section 3.4 states a leave-one-state-out scheme across three states with hyperparameter tuning on validation sets within training folds. Section 3.5 then says “All models were trained on the Washington cohort and evaluated on held-out Virginia and Ohio,” which contradicts LOSO and suggests single-source training. This inconsistency affects the interpretability of Table 1 and any claims about cross-state generalization.

3) Off-policy evaluation underspecified. The paper claims use of the weighted doubly robust estimator with additional FQE and ordinary IS checks (Section 4 and lines 186–191), but provides no critical details:
   - How was the behavior policy estimated? Was per-state behavior modeled to match domain shift?
   - How was coverage enforced or measured, and what clipping/truncation was used to control variance?
   - How were standard errors and p-values computed for WDR, especially given bootstrap CIs are reported elsewhere?
   Without these, the “p < 0.01” superiority claim is hard to evaluate.

4) Questionable fairness formulation inside the RL loss. Equation (3) adds a per-group equalized-odds penalty in the Q-learning objective. It is unclear:
   - What constitutes “positives” and “negatives” for TPR/FPR in this sequential setting. Are these defined over outcome events (which are not immediate classification labels) or over action recommendations?
   - How the TPR/FPR are computed during training at the transition level, and how gradients are taken through these non-differentiable counts.
   - Whether equalized odds is appropriate for action recommendation versus risk classification, since the base task is policy optimization, not binary prediction. This mismatch could lead to unstable or misaligned learning signals.

5) Diffusion augmentation and feasibility specification lack critical detail. Section 3.2 describes a “four-layer conditional U-Net with a linear noise schedule” trained for 50k steps, but:
   - There is no quantitative analysis of whether generated samples remain in-distribution other than the feasibility filter, and no concrete safety metrics are reported to show augmentation does not inject artifacts.
   - The clinical feasibility region is loosely described (lines 122–129) without exact rule cardinality, coverage statistics, or an audit showing how many candidate samples were rejected/accepted and how this varied across states or actions.
   These omissions undercut the safety claims.

6) Theory claims are tenuous. Section 3.3 says the method “inherits” safety and fairness benefits from FISOR/OGSRL/FairDICE, but no concrete assumptions or composite guarantees are articulated. This is fine if framed purely as an empirical contribution, but the text implies a stronger connection than is justified.

7) Figure 1’s unified scaling may mislead. It shows “relative improvement” on both outcomes and fairness on the same axis. Since event reduction and disparity reduction are not commensurate, plotting them on a unified normalized percentage scale could exaggerate visual differences. Moreover, the caption mentions normalization but does not specify how percentage reductions were computed or normalized across metrics.

8) Runtime and resource reporting are inconsistent. Section 5 cites approximately 6 hours on a single A100 GPU with 12 GB memory; Section 398–404 says “approximately 4 hours” and “24 CPU cores.” The A100 commonly has 40/80 GB; 12 GB is atypical. These discrepancies should be reconciled for reproducibility.

9) NNT reporting is nonstandard. Table 1 lists NNT with wide, seemingly symmetric CIs (e.g., 8.0 (4.6–44.0)). NNT is the reciprocal of absolute risk reduction and typically yields highly skewed CIs, sometimes unbounded; the text acknowledges instability but the computation method and transformation from ARD CIs are not described.

10) Missing evaluation dimension for “safety.” The paper stresses safety but reports only event rate, relative reduction, NNT, and fairness disparity. There is no explicit safety-violation rate, feasibility-constraint violation rate, or OOD action rate in any result table. An ablation claim that “removing diffusion reduces safety” is made, but no direct safety metric is presented.

11) Loss design relative to CQL is unclear. Equation (2) resembles the conservative Q-regularization by pushing down Q on out-of-behavior actions relative to behavior. However, the paper neither connects to known CQL variants nor justifies the exact signs/scales; a brief derivation or reference to an equivalent form would help avoid confusion.

12) Ambiguity in how protected groups and metrics are aggregated. The text indicates fairness across sex and race (lines 111–113), but:
    - Does the penalty act on marginal axes, intersectional subgroups, or both?
    - How are group sizes accounted for to avoid instability in small subgroups?
    - How are these fairness metrics computed per-step vs per-episode?

13) Table 1 says “runtime” is reported (Section 3.5), but the table itself contains no runtime column. This is an explicit mismatch between description and content.

14) Adaptive switching design may induce non-stationarity and variance. The sliding window of 20 patients triggers policy switches when disparity exceeds a threshold. This mechanism is plausible but raises questions about:
    - Stability of OPE under a non-stationary evaluation policy.
    - How group prevalence affects false triggers; Table 3 shows small sensitivity to window size, but neither threshold selection nor false-alarm/latency trade-offs are explored.

15) Minor duplications and editorial issues. The Discussion’s limitations paragraph is partially duplicated (lines 215–231 and again 222–231/225–231 style repetitions), suggesting editing artifacts and making it harder to parse distinct limitations.

Reference to figures/tables:
- Table 1: The claimed best-in-class acute event rate and fairness disparity for FCAF-RL are clearly shown, but the missing runtime column contradicts Section 3.5’s statement that runtime is reported. The NNT CIs also look unconventional and need methodological clarification.
- Table 2: The NOFAIR variant achieves the lowest acute event rate but with much higher disparity, which evidences the intended fairness-performance trade-off and supports the fairness regularizer’s role. However, “NOAUG reduces safety” is asserted without a corresponding safety metric in the table.
- Table 3: Sensitivity to window size in the switching rule appears minimal, which is reassuring but only explores one axis (window length) and not the fairness threshold itself.
- Figure 1: The normalized, unified scale may conflate comparability across fundamentally different quantities. It visually supports the claim that FCAF-RL leads in both objectives, but clarity on normalization and metric comparability is needed.

Collectively, these issues substantially weaken confidence in the empirical conclusions and their reproducibility, even setting aside the topical mismatch.

## Potentially Missing Related Work
1) Fatemi et al., “Semi-Markov Offline Reinforcement Learning for Healthcare,” 2022 — directly relevant for irregular clinical decision intervals and SMDP formulations; discuss in Related Work and consider as an alternative backbone in Section 3 or as a baseline in Table 1.
2) Tang et al., “Leveraging Factored Action Spaces for Efficient Offline Reinforcement Learning in Healthcare,” 2023 — action-factorization is pertinent to multi-component care-management interventions; cite in Related Work and discuss applicability to your nine-intervention space.
3) Zhang et al., “Continuous-Time Decision Transformer for Healthcare Applications,” 2023 — sequence-modeling and continuous-time RL are natural comparators for weekly trajectories; add to Related Work and discuss in Section 3.1/3.5 as an alternative approach.
4) Emerson et al., “Offline reinforcement learning for safer blood glucose control in people with type 1 diabetes,” 2023 — presents practical safety-focused offline RL evaluation patterns; discuss in Related Work and consider their safety metrics when reporting results.
5) Killian et al., “Risk Sensitive Dead-end Identification in Safety-Critical Offline Reinforcement Learning,” 2023 — risk-aware avoidance of dead-ends complements feasibility constraints; cite and compare in Section 2 and discuss integration with your feasibility region in Section 3.2.
6) Delphic et al., “Delphic Offline Reinforcement Learning under Nonidentifiable Hidden Confounding,” 2024 — directly relevant to confounding in observational healthcare RL; add to Related Work and discuss in Section 3.4/4 how your OPE and learning pipeline address or do not address hidden confounding.
7) Li et al., “Federated Offline Reinforcement Learning,” 2024 — applicable to multi-state Medicaid where data sharing is constrained; include in Related Work and note as a path for scaling beyond central training.
8) Zhang et al., “CFRL: A Python library for counterfactually fair offline reinforcement learning via sequential data preprocessing,” 2025 — a causal-fairness comparator to equalized-odds regularization; cite in Related Work and consider a discussion/baseline contrasting statistical vs counterfactual fairness.
9) Basu et al., “Offline reinforcement learning for care management: addressing sparse rewards, temporal dependencies, and fairness in Medicaid populations,” 2026 — closely aligned empirically and methodologically; compare evaluation protocol, fairness metrics, and OPE practices in Related Work and Discussion.
10) Basu et al., “Mechanistic interpretability of reinforcement learning in Medicaid care coordination,” 2026 — relevant for governance, interpretability, and fairness guardrails; add to Related Work/Discussion and position FCAF-RL within a broader governance stack.

## Comments Suggestions And Typos
Actionable questions/suggestions:
- Clarify evaluation protocol consistency. Resolve the LOSO vs “train on Washington only” inconsistency (Sections 3.4 vs 3.5) and, if LOSO is used, present per-fold results or confirm averaging protocol. If single-source training is intended, adjust claims about cross-state generalization accordingly.
- Specify OPE details. Precisely describe:
  - Behavior policy estimation procedure per state and per action, any state-action density ratio modeling, clipping, and handling of support mismatch.
  - How WDR standard errors and p-values are computed. If bootstrap is used, detail the resampling scheme for policies vs trajectories.
  - FQE hyperparameters, rollout lengths, target networks, and stabilization tricks to support reproducibility.
- Make the fairness penalty operationally clear. Define TPR/FPR in the sequential decision context. If based on action recommendation vs subsequent observed outcomes, state that explicitly and justify why equalized odds suits your use case. Explain how gradients are propagated through these statistics.
- Report safety metrics explicitly. Add columns to Table 1 (or a new table) for feasibility-constraint violation rates, OOD action rates, and any guardian/feasibility filter statistics, including acceptance/rejection counts for augmented samples and policy outputs.
- Reconcile resource/runtime reporting and include runtime in tables. Fix the A100 memory/time discrepancies and either add runtime to Table 1 (as promised in Section 3.5) or revise the text.
- Figure 1 normalization. Explain the normalization procedure for combining different metrics on one axis, or split into two axes to avoid conflation.
- NNT methodology. Describe how NNT CIs were computed, including transformations from ARD CIs, and consider presenting absolute risk reduction with appropriate uncertainty to avoid NNT instability.
- Connect Eq. (2) to known CQL forms. Either provide a short derivation or cite an equivalent conservative objective to ground your choice of signs and scalings.
- Fairness scope and stability. Clarify whether you penalize marginal or intersectional groups and provide safeguards for small-n subgroups. If only sex and race are used, discuss the decision and potential extensions.
- Adaptive switching threshold analysis. In addition to window size (Table 3), report sensitivity to the disparity threshold and analyze false-trigger vs responsiveness trade-offs.

Typos/clarifications:
- Section 3.2: “cliniciandefined” → “clinician-defined”; “threelayer” → “three-layer”; “equalisedodds” → “equalized-odds.”
- Section 3.5: You state runtime is reported but Table 1 lacks that column; fix mismatch.
- Section 5 (Limitations): Paragraph is partially duplicated; remove repetition (lines ~215–231 vs ~222–231).
- Hardware: “A100 GPU with 12 GB memory” is unusual; verify and correct.
- References: Ensure all healthcare-RL fairness and safety references that are closely related are covered (see Missing Related Work).

Criteria for raising my score:
- Resolve the LOSO vs single-state training inconsistency and provide per-fold or averaged results with matching OPE details.
- Add explicit safety (violation) metrics and comprehensive OPE methodology, making the pipeline reproducible.
- Clarify and justify the fairness penalty design for sequential decision making, with a clear, differentiable training formulation.
- Correct runtime/resource inconsistencies and add runtime where promised.
- Expand Related Work to include strong, directly related baselines and considerations listed above.

## Confidence
4: Quite sure after careful checking — I carefully checked the key methodological claims, equations, and tables. While not my core subfield within ACL, I am comfortable with offline RL and fairness in clinical decision support.

## Soundness
2: Poor — Several methodological and reporting inconsistencies (evaluation protocol mismatch, insufficient OPE details, unclear fairness operationalization in an RL objective, missing direct safety metrics) undermine confidence in the results.

## Excitement
2.0: Potentially Interesting — The unification of feasibility constraints, fairness regularization, and adaptive switching is practically relevant for healthcare RL, but the topical mismatch with ACL and methodological issues temper enthusiasm.

## Overall Assessment
1: Do not resubmit — This paper is outside ACL’s primary scope and exhibits key methodological and reporting weaknesses that must be addressed. While the societal motivation is strong and the framing is promising for a healthcare/ML venue, the current version is not suitable for ACL.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper lists several limitations: offline evaluation, potential unmeasured confounding, focus on equalized odds, computational cost, limited action granularity, and modest number of states. These are appropriate and appreciated. Missing is a deeper discussion of:
- How fairness penalties interact with subgroup prevalence and potential harm if a fairness push inadvertently reduces care quality for small or high-risk groups.
- Risks from non-stationary adaptive switching in clinical workflows, including accountability and auditability when policies dynamically change.
- The implications of learning from biased historical allocation patterns; consider counterfactual fairness or deconfounding strategies.

## Ethical concerns
None beyond what the authors outlined. The work uses de-identified retrospective data. Ensure that any deployment includes human oversight, detailed audit logs for policy switching events, and subgroup monitoring to prevent harm.

## Needs Ethics Review
No.

## Reproducibility
2: Extremely difficult to reproduce — Critical OPE and training details are missing or inconsistent, runtime reports conflict, the fairness penalty is not operationalized clearly for a sequential RL setting, and promised runtime reporting is absent from Table 1.

## Datasets
2: Documentary — No real data release for understandable reasons, and synthetic data are provided. Useful for studying the algorithmic pipeline but limited for validating the reported real-world results.

## Software
2: Documentary — The paper promises code, which would be useful for study and replication in principle, but given the current reporting gaps, the software would need to clearly implement WDR/FQE/IS, augmentation, and switching as described to be truly useful.