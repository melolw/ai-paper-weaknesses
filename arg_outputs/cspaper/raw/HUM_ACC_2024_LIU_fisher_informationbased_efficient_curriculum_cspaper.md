# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes FibecFed, a federated fine‑tuning framework for LLMs that combines two ideas driven by Fisher Information: (1) a curriculum at each client that prioritizes “easy” batches early, where difficulty is measured by the trace of a diagonal Fisher approximation computed from per‑sample gradients; and (2) an efficient sparse update scheme that selects a subset of layers for global aggregation (GAL) based on layer sensitivity to input perturbations, and further selects a subset of neurons per non‑GAL layer for local updates based on Fisher scores with momentum. The method is implemented with LoRA adapters. Experiments on 10 NLP datasets with RoBERTaLARGE and on 3 tasks with LLaMA report improved accuracy and large speedups over 17 baselines. The paper includes ablations isolating the two selection components and the curriculum schedule.

## Summary Of Strengths
- Combination of client‑side curriculum and Fisher‑guided sparsity in a federated LoRA setting is a sensible and timely direction for efficient FL with LLMs.
- Clear high-level system design: Figure 1 clearly depicts the initialization and tuning phases, the GAL selection, and the per‑round data flow between server and clients; this helps readers grasp what is synchronized and what remains local.
- Solid empirical sweep on RoBERTaLARGE: Table 1 shows consistent gains across 10 datasets and 17 baselines; the accuracy improvements are often nontrivial. Figures 2–5 visualize convergence trends and corroborate faster attainment of target accuracies.
- Efficiency evidence: Table 7 reports “time to target accuracy,” where FibecFed is typically the fastest by a wide margin on many datasets; this is aligned with the goal of reducing client computation and communication.
- Ablations: The paper investigates the impact of curriculum vs. no curriculum and alternative curricula; it also compares layer‑selection orders and shows that the proposed sensitivity metric helps. Figures 6–7 and the ablation discussion in Section 5.6 are informative.
- Federated‑specific concerns are acknowledged: robustness to client heterogeneity and varying client counts is evaluated (Section 5.5; Figure 6b–c), even if only briefly.

## Summary Of Weaknesses
1) Theoretical correctness and variable misuse in key derivations.
- In Section 4.3.1, the sensitivity of a layer is evaluated by adding noise ε to the input s_i (Eq. 10), but the Taylor expansion in Eq. 11 incorrectly uses the gradient with respect to parameters P_k, not the input. If s_i is perturbed, the correct first‑order term should involve ∇_s L_k(s_i), not ∇_{P_k} L_k(s_i). Consequently, Eq. 12, which resembles a dual‑norm solution used in adversarial perturbation derivations, appears to optimize in the wrong space. This makes the layer sensitivity score in Eq. 13 conceptually questionable. Since this sensitivity score drives GAL selection, the methodological validity is materially affected.

2) “Lossless” claims for GAL and local‑neuron selection lack justification and are computationally dubious.
- Section 4.3.1 proposes computing Hessians H_k, their eigenspectra, and a Lipschitz constant L_k to find r_k such that λ_{r_k+1} − λ_{r_k} > 4L_k, then sets the number of GAL accordingly. There is no proof that this procedure yields “lossless” aggregation, nor that the heuristic threshold ensures no performance drop. Moreover, computing and sorting Hessian eigenvalues and estimating L_k per client for LLMs on devices is practically unrealistic. The paper provides neither complexity analysis nor an approximation strategy for these quantities.
- The same issue recurs in Section 4.3.2 for selecting a fraction ρ_{k,l} of neurons per non‑GAL layer.

3) Fisher‑based difficulty definition and notation are internally inconsistent.
- Equations 3–7 define the Fisher measure in terms of ∇ log p_k(s_i) and then move to a diagonal approximation. The text on Page 5 writes “sum of the trace of F̃_i,” which is redundant (Tr of a diagonal matrix is already the sum of its diagonal elements). Right after, it states that “∫_i can be computed using the square of the elements in the diagonal of the first‑order derivative matrix,” which deviates from the outer‑product form used to define the Fisher approximation. These inconsistencies cast doubt on exactly what is computed and compared across batches.
- The difficulty score symbol “∫_i” suggests an integral, which is confusing. A clearer symbol would avoid misinterpretation.

4) Algorithmic clarity issues and potential bugs.
- Algorithm 1 (Appendix A) line 4 appears to miss a gradient descent minus sign and uses a nonstandard in‑place update expression, which is likely a typographical error but critical for reproducibility.
- Equation 19 states ∇_{P_k^t} f = P_A^t P_B^t − P_A^{t−1} P_B^{t−1}, which is not a valid gradient expression for LoRA; this looks like a finite‑difference of reconstructed low‑rank products, not a gradient.
- The hyperparameter table (Table 8) fixes “number of layers in GAL = 18” across all datasets, which conflicts with the text’s promise of dynamic, Fisher‑guided GAL sizing via the lossless rule.

5) Reporting and consistency gaps.
- LLaMA results are inconsistently described: Section 5.4 claims LLaMA is evaluated on MRPC, MR, and SST‑2, but Table 2 reports COLA, MRPC, and RTE. This needs correction.
- Results mix development‑set (GLUE) and test‑set evaluations across tasks (Table 1 caption), yet a single “Avg” is reported. This conflates protocols and may bias the average. Provide separate averages or a uniform evaluation policy.
- No variance or confidence intervals are reported across random seeds for Tables 1–2–7 or the curves in Figures 2–5. Given the number of baselines and tasks, lack of variance makes it hard to gauge robustness of improvements.

6) Communication efficiency is not quantified directly.
- The main selling point includes reduced communication by synchronizing only GAL. However, the paper reports only wall‑clock time, not actual communication volume (bytes per round, total bytes to reach target accuracy). Without this, it is hard to attribute speedups to communication vs. just smaller local compute due to selective updates or implementation specifics.

7) Computational overhead of Fisher and sensitivity scoring is not measured.
- The paper claims the Fisher and sorting overhead is negligible (<2.98%), but I cannot find a dedicated measurement or breakdown. With per‑sample gradient computation to score batches and momentum‑averaged Fisher per layer/neuron, the overhead could be significant on devices.

8) Heterogeneity setting may be mild; generalization to strong non‑IID is unclear.
- The partition uses Dirichlet α=5 (G.1) which is relatively close to IID. Claims about robustness to non‑IID (differences <1.83%, Section 5.5) may not hold under more extreme heterogeneity (smaller α). This limits the strength of the FL‑specific conclusions.

9) Ambiguities in the sensitivity metric.
- Equation 13 uses relative Frobenius norm changes of hidden states as sensitivity. Across layers, hidden dimensions and activation scales vary; without normalization or whitening per layer, larger‑magnitude layers could be unfairly favored. Figure 7(b) suggests performance depends on the number of transferred layers, but the mapping from sensitivity to a stable GAL set is unclear.

10) Limited consideration of privacy/security.
- The method leverages Fisher information and transmits gradients/adapter updates but does not analyze privacy leakage or defenses. Section H.3 explicitly defers security to future work. For a federated LLM paper, at least a brief risk analysis or compatibility with DP/secure aggregation would strengthen the impact.

11) Writing/typo issues that hinder precision.
- Section titles and text contain noticeable mistakes, for example “Related Word & Preliminaries” should be “Related Work,” “boradcasted,” “Talyor,” “fist part of LoRA,” “Select decision,” etc. Several equations and symbols are inconsistently defined, which complicates verification.

Engagement with figures and tables:
- Figure 1 effectively lays out the pipeline and the two‑phase procedure. However, the figure depicts a clean separation of GAL and local update layers, while Table 8 fixes GAL to 18 for all tasks, undercutting the “adaptive” claim from Figure 1. Clarifying how Figure 1’s adaptive selection actually produced the constant “18” in Table 8 would reduce confusion.
- Table 1 shows the proposed method winning the average by a clear margin (88.31 vs. 86.69 for the next best baseline sLoRA/Delta‑LoRA), with especially large gains on MRPC and RTE. Still, the lack of standard deviations and the dev/test mixing diminish the strength of the claim. Please add multi‑seed means with confidence intervals and unify evaluation splits.
- Table 2 (LLaMA) suggests consistent improvements in both accuracy and time. Yet the task list mismatch with Section 5.4 and the undefined time units deserve fixes.
- Table 7 convincingly demonstrates faster time to reach preset accuracy targets. These are the strongest quantitative indicators of efficiency, but again, communication bytes should be reported to back the communication‑efficiency narrative.

## Potentially Missing Related Work
1) Hu et al., FedQLoRA: Federated Quantization‑Aware LoRA for Large Language Models, 2024 — targets communication and compute efficiency in federated LoRA fine‑tuning via quantization‑aware training. Directly relevant to the efficiency focus here. Should be cited in Related Work and discussed alongside Section 4.3 as an orthogonal or complementary approach; consider adding a communication‑bytes comparison or combined baseline.

2) Lu et al., FDLoRA: Personalized Federated Learning of Large Language Models via Dual LoRA Tuning, 2024 — proposes dual adapters to separate global and personalized knowledge. This is an alternative to your Fisher‑guided GAL/local selection to handle non‑IID personalization; compare conceptually in Section 2 and empirically if possible.

3) Zhu et al., Promoting Data and Model Privacy in Federated Learning through Quantized LoRA, 2024 — combines LoRA with quantization for both privacy and communication reduction. Add to Related Work and discuss compatibility in Section 6/I.

4) Fang et al., Federated Sketching LoRA: A Flexible Framework for Heterogeneous Collaborative Fine‑Tuning of LLMs, 2025 — updates submatrices of shared adapters using sketching, which also aims at reducing communication under heterogeneous resources. Compare to your Fisher‑guided sparsity in Section 4.3; cite and discuss.

5) Li et al., FED‑FSTQ: Fisher‑Guided Token Quantization for Communication‑Efficient Federated Fine‑Tuning of LLMs on Edge Devices, 2026 — also leverages Fisher information, but for token‑level quantization. The methodological kinship warrants a discussion in Section 2 and after Eq. 6 to clarify similarities and differences.

6) Bian et al., FedALT: Federated Fine‑Tuning Through Adaptive Local Training with Rest‑of‑World LoRA, 2026 — personalized federated LoRA with adaptive mixing. While you compare against FedALT (Pillutla et al., 2022) for partial model personalization, this later LoRA‑specific variant should be acknowledged in Related Work and positioning of your GAL/local update strategy.

7) Liu et al., Rethinking LoRA for Privacy‑Preserving Federated Learning in Large Models, 2026 — analyzes LoRA under DP and proposes LA‑LoRA to mitigate DP noise amplification. Include in Related Work and ethical discussion to frame future extensions of FibecFed under DP constraints.

8) UniFLoW: Universal Multi‑Modal Federated LoRA Fine‑Tuning Framework with Analytical Aggregation, 2026 — proposes an analytical aggregation rule for LoRA in a unified framework. It is relevant to Section 4.1 aggregation; at least discuss as an alternative to FedAvg over adapters.

9) Dai et al., Federated Split Learning for Large Language Models with RSMA, 2026 — a contrasting systems approach to efficiency via split learning. While orthogonal, adding a short discussion will help position FibecFed among systems‑level efficiency designs.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Correct the gradient mismatch in Section 4.3.1: if the perturbation is on inputs, replace ∇_{P_k} with ∇_{s} consistently in Eqs. 10–12 and clarify how ε_i* is computed in practice for text inputs (token embeddings? continuous prompts?). If the intent was to perturb hidden states instead of raw inputs, state that explicitly and re‑derive the sensitivity measure accordingly.
- Revisit the “lossless” selection claims for GAL and neuron subsets. Provide either (a) a principled approximation that is computationally feasible at LLM scale, with complexity estimates and ablations, or (b) tone down the claim and present it as a heuristic. In either case, report actual compute/communication overhead of eigen‑gap/Lipschitz estimation. If you used a fixed number of layers (Table 8), explain how that aligns with Section 4.3.1 and Figure 1.
- Report communication volume and breakdown: bytes per round and total bytes to target accuracy for all methods in Table 7. This will substantiate the communication‑efficiency narrative beyond wall‑clock time.
- Strengthen the non‑IID evaluation: include more skewed Dirichlet α (e.g., 0.1/0.3/1.0) and report performance and stability. Current α=5 is close to IID and may understate cross‑client drift.
- Add multi‑seed runs and report mean ± std for Tables 1, 2, and 7. Also, unify evaluation splits or report separate averages for dev/test to avoid mixing protocols.
- Clarify LLaMA evaluation: fix the inconsistency between Section 5.4 and Table 2. Define time units in Table 2 (seconds?) and provide hardware details to contextualize the numbers.
- Provide an explicit measurement of Fisher/scoring overhead on clients. The claim “<2.98%” should be backed by a profiling study.
- Ethics/privacy: briefly discuss compatibility with secure aggregation and DP, and how Fisher/gradients might leak information. Even a short empirical check or a citation‑backed argument would help.

Typos and minor issues (partial list):
- Section title: “Related Word & Preliminaries” → “Related Work & Preliminaries”
- “boradcasted” → “broadcast”
- “Talyor” → “Taylor”
- “fist” → “first”
- “The sum of the trace” → “the trace”
- Algorithm 1, line 4: missing minus sign in gradient descent update and confusing notation; please fix.
- Equation 19: gradient expression appears incorrect; replace with the true gradient of the loss w.r.t. A and B in LoRA or remove.
- Use a different symbol for difficulty than “∫_i”, which suggests an integral.
- Table 8 says “non‑IID degree 5.5” for BoolQ but “5” elsewhere; explain or fix.
- Several figure captions could explicitly mention that accuracy is plotted against time in seconds.

Criteria that could change my recommendation upward:
- Fixing the gradient/input perturbation inconsistency and clarifying the actual implemented sensitivity computation.
- Either justifying or simplifying the Hessian/Lipschitz “lossless” selection with measurable overhead and ablations, plus reporting communication bytes.
- Adding stronger non‑IID experiments and multi‑seed statistics; correcting inconsistencies and typos.

## Confidence
4: Quite sure after careful checking — I checked equations, algorithmic steps, and tables carefully; some derivations appear inconsistent, but the empirical section is extensive.

## Soundness
3.5: Between Acceptable and Strong — The empirical evidence is broad and promising, but there are nontrivial methodological inconsistencies and unsubstantiated “lossless” claims that must be clarified.

## Excitement
3.5: Between interesting and exciting — The Fisher‑guided curriculum and sparsity combination for federated LoRA is timely and useful, but theoretical clarity and measurement of communication savings are needed.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. With corrections to the sensitivity derivation, clearer and feasible GAL/parameter selection justification, multi‑seed and stronger non‑IID experiments, and explicit communication‑bytes reporting, it could become a solid conference paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges reliance on a central server and the lack of integration with compression; this is appropriate. Additional limitations to discuss:
- Potential privacy leakage via gradients/Fisher scores; no DP/secure aggregation.
- Applicability to very resource‑constrained clients given Fisher computations.
- Dependence on LoRA and its known failure modes under DP or extreme heterogeneity.
Societal impact is likely positive in enabling on‑device collaborative fine‑tuning without raw data sharing, but risks around gradient leakage or client manipulation deserve mention. Section H.3 notes adversarial issues only superficially; a stronger mitigation plan is recommended.

## Ethical concerns
None beyond standard FL concerns already noted. However, adding a short discussion on privacy leakage risks from adapter updates and Fisher computations, as well as compatibility with secure aggregation/DP, would be advisable.

## Needs Ethics Review
No

## Reproducibility
4: Mostly reproducible — Many details and hyperparameters are provided, but code is not included and some equations/algorithms are inconsistent. Multi‑seed configs and communication metrics are missing.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If released, the code would likely be used by others; right now availability is only promised.