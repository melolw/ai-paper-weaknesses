# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies continual learning with LoRA adapters and proposes MidPC, an SVD-based initialization that selects an intermediate “slice” of singular components from a pretrained weight matrix, rather than the top (PiSSA) or bottom (MiLoRA) components. The LoRA update is initialized to be function-preserving using Equation (2), with the base weight set as a residual (Equation (1)). Experiments on the FOREVER Standard CL benchmark with Qwen3-0.6B report that MidPC improves overall performance (OP) and reduces backward transfer (BWT) relative to PiSSA and MiLoRA. The authors analyze spectral alignment and spectral imbalance (Figure 2) and run a learning-rate matching study (Table 2) to argue that the gains are not due to conditioning alone.

## Summary Of Strengths
- Conceptual clarity and unification: The paper cleanly frames PiSSA and MiLoRA as endpoint choices in the singular spectrum and positions MidPC as the intermediate slice in the same framework. Figure 1 helps communicate this “spectrum” view and how initialization affects continual learning stability and plasticity.
- Simple, reproducible mechanism: MidPC requires no architectural change and provides a single, interpretable knob (the slice start index s). The function-preserving initialization in Equation (2) is straightforward.
- Empirical gains under one setup: On the FOREVER Standard CL benchmark with Qwen3-0.6B, MidPC improves OP and BWT versus PiSSA and MiLoRA (Table 1). The results are consistent across two task orders (Table 3).
- Diagnostic analysis: The spectral diagnostics in Figure 2 are informative. In panel (a), MidPC maintains high subspace alignment across tasks, avoiding the degradation seen with PiSSA; in panel (b), MidPC exhibits moderate spectral imbalance between PiSSA’s low and MiLoRA’s high concentration, aligning with the claimed stability–plasticity trade-off.
- Attempt to control confounds: Table 2’s learning-rate matching analysis is a reasonable step to test whether improvements stem from spectral choice rather than effective step size.

## Summary Of Weaknesses
1) Narrow empirical scope limits generality and impact.  
- Only one base model (Qwen3-0.6B), one adapter rank (r=8), one set of LoRA targets (Q and V), and one benchmark are used. There is no evaluation on generative or instruction-following tasks, multilingual tasks, or other standard CL benchmarks for LLMs. This makes it hard to conclude the method’s robustness beyond a single classification setting.

2) Missing key baselines and related work weaken positioning.  
- The paper compares only to PiSSA and MiLoRA for SVD-initialization and to several methods from a different setup via † entries in Table 1. It omits several directly relevant recent methods for LoRA continual learning or SVD-informed initialization (see “Potentially Missing Related Work”). Without these, the “state-of-the-art among SVD-based methods” claim is not well supported.

3) Limited ablations on design choices central to the claim.  
- The middle slice is set to s=508 for 1024-d layers, but there is no scan over s, no sensitivity to rank r, and no exploration of which layers benefit most from MidPC. A sweep over s around the middle and a rank study would be essential to verify the “middle is best” hypothesis and to inform practitioners. Right now, the choice looks ad hoc.

4) Learning-rate matching methodology under-specified (Section 4.4, Table 2).  
- It is unclear exactly how “early-step update norms” are measured and matched across methods (per-layer or global matching? measured with respect to which layers or parameters? how many steps?). Without these details, the 91.9% retained-gap claim vs. MiLoRA cannot be independently validated.

5) Spectral diagnostics require more precise definitions and reporting.  
- Figure 2(a): “Mean alignment score” lacks full specification. What k is used for top-k singular vectors, across which layers, and how are layers aggregated?  
- Figure 2(b): “Top-1 concentration” is not formally defined in the main text. Do you compute this per layer and average, or on concatenated updates? Are changes statistically significant? Including exact definitions and variance estimates would improve rigor.

6) Potential confounds remain.  
- All methods use the same global learning rate, but SVD slices differ in magnitudes across many layers. Even after LR matching, only BWT gaps are analyzed; OP gaps could also be reported post-matching. Additionally, weight decay, dropout, and LoRA scaling (alpha) might interact differently with SVD slices. A more comprehensive control analysis is warranted.

7) Comparisons in Table 1 mix setups, obscuring conclusions.  
- Several baselines (Fine-tuning, EWC, MoELoRA, O-LoRA, FOREVER) are marked † and come from a different setup. While the authors note this, the table headline still lists them together. This risks misleading readers about direct comparability. A separate table or clearer partitioning would help.

8) Computational overhead and practicality not discussed.  
- Full SVD per target weight for every layer can be costly in large LLMs. The paper does not quantify the added initialization time or describe any truncated SVD or approximation strategy. This is important for adoption.

9) Limited statistical reporting and small number of seeds.  
- The main results are averaged over two task orders and three seeds. More seeds would help, especially since BWT is noisy in continual learning. Reporting per-task accuracies over time would also clarify where gains come from.

10) Claims sometimes overreach evidence.  
- Statements like “state-of-the-art among SVD-based methods” are made without comparing to several recent, closely related baselines. With the narrow experimentation and missing ablations, the claims should be toned down.

Figure- and table-specific comments:
- Figure 1: The schematic clearly situates MidPC between PiSSA and MiLoRA and ties the SVD slice to qualitative stability–plasticity effects in the pipeline. However, the figure implies a clean causal link from slice choice to BWT/OP outcomes. Given potential confounds (e.g., per-layer conditioning), the caption could be more circumspect or refer readers to the controls in Table 2.
- Figure 2(a): The red PiSSA curve descends notably from about 0.94 to roughly 0.845 by task 5, supporting the claim that top-slice adaptation disrupts pretrained subspaces. Yet, the y-axis starts high, which visually compresses differences between MidPC and MiLoRA. Please add numeric deltas and exact k, layer scope, and averaging protocol.
- Figure 2(b): MiLoRA’s spectral imbalance being around 0.72 while MidPC sits near 0.32 is a compelling diagnostic that aligns with the central thesis. That said, a complementary metric, such as entropy of singular-value-normalized energy, might provide a fuller picture.
- Table 1: This is the central quantitative evidence. As noted, mixing incomparable setups with † baselines can mislead; better to segregate them or add a row block header. For the comparable rows, report per-task final accuracies or intermediate accuracies to show retention dynamics, not just OP and BWT.
- Table 2: The LR-matching protocol needs fuller specification, and it would help to also report OP and variance post-matching. Right now, interpretation hinges on BWT gap alone.
- Table 3: The per-order stability of MidPC’s BWT is promising. Please add per-task breakdowns and significance tests to strengthen the robustness claim.

## Potentially Missing Related Work
1) Quercia et al., “Least but not Last: Fine-tuning Intermediate Principal Components for Better Performance-Forgetting Trade-Offs,” 2026 — Directly studies intermediate principal components for balancing performance and forgetting, closely paralleling the MidPC hypothesis. Should be cited in Section 2 and compared empirically in Section 4 (ideally as a baseline if code is available).  
2) Pasquali et al., “Low-Rank Adapters Initialization via Gradient Surgery for Continual Learning,” 2026 — Proposes SLICE, a gradient-surgery SVD initialization tailored to CL. Highly relevant as a strong baseline and conceptual contrast. Discuss in Section 2 and compare in Table 1 or a new table focused on SVD-initialization methods.  
3) Luo et al., “KeepLoRA: Continual Learning with Residual Gradient Adaptation,” 2026 — Constrains LoRA updates to residual subspaces to protect knowledge. Should be discussed with orthogonal/subspace-projection approaches in Section 2 and compared where feasible.  
4) Wang et al., “PLAN: Proactive Low-Rank Allocation for Continual Learning,” 2025 — Allocates task-specific low-rank subspaces to mitigate interference. Relevant for stability–plasticity and should be discussed in Section 2 and, if possible, included as a baseline.  
5) Das et al., “ConsNoTrainLoRA: Data-driven Weight Initialization of Low-rank Adapters using Constraints,” 2025 — Provides a closed-form, data-driven LoRA initialization. Include in Section 2 and consider as an additional initialization baseline to contextualize MidPC’s purely spectral approach.  
6) Zhu et al., “SILoR: SVD-Based Initialization for Low-Rank Adaptation in Vision Transformers,” 2025 — Though in vision, the SVD-initialization angle and subspace alignment focus are technically pertinent. A brief discussion in Section 2 could help situate MidPC among SVD-initialization strategies.  
7) Hou et al., “FS-LoRA: Fast and Slow Low-Rank Adaptation for Class Incremental Learning,” ICASSP 2026 — A CL-with-LoRA variant designed for class-incremental settings. Mention in Section 2 and, if feasible, include as a baseline.  
8) Chen et al., “Replay-Free Continual Low-Rank Adaptation with Dynamic Memory,” 2026 — Offers a replay-free continual low-rank approach. Useful as a complementary baseline to compare MidPC’s initialization benefits versus memory-based methods.

## Comments Suggestions And Typos
Actionable suggestions:
- Add comprehensive ablations:  
  - Vary s around the midpoint (e.g., ±64, ±128), evaluate several ranks (e.g., r=4, 16, 32), and test additional LoRA target modules (e.g., MLP projections, K/O in attention). This is essential to validate the “intermediate is best” claim.  
  - Include per-task accuracy trajectories and forgetting curves, not just final OP/BWT.
- Strengthen LR-matching and diagnostics:  
  - Fully specify the LR-matching protocol, including layer-wise vs. global matching, number of steps used to estimate norms, and whether norms are measured on identical mini-batches. Also report OP after LR matching and provide variance/confidence intervals.  
  - Precisely define all spectral metrics in the main text (alignment k, layer aggregation, top-1 concentration formula) and add sensitivity analyses (e.g., different k).
- Expand baselines and discussion:  
  - Incorporate several of the missing related methods above, at least in discussion and ideally in experiments. If implementation is impractical, explain why and provide conceptual comparisons with expected trade-offs.  
  - Clearly separate incomparable † baselines in Table 1 or move them to an appendix table to avoid confusion.
- Report computational overhead:  
  - Quantify SVD wall-clock overhead and memory footprint relative to random-initialized LoRA and to PiSSA/MiLoRA. Consider truncated or randomized SVD and discuss accuracy–overhead trade-offs.
- Clarify scope and claims:  
  - Temper “state-of-the-art” claims to those methods actually compared in the same setting. Reframe as “best among the tested SVD-slice initializations under our setup” unless further baselines are added.

Minor issues and typos:
- Abstract/Intro: “FOREVER Standard CL benchmark” is introduced without a concise description; a one-sentence summary would help.  
- Section 3.3: Spell out r_max once when first used, even though it is implicitly defined.  
- Section 4.1: Specify exactly which layers received LoRA in Qwen3-0.6B and whether all transformer blocks were included.  
- Tables: Include per-task accuracies in an appendix table.  
- Figure captions: Add definitions or pointers to exact metric definitions for Figure 2.

Criteria for score increase in rebuttal:
- Provide additional ablations on s and r, with per-task metrics and sensitivity plots.  
- Clarify and strengthen LR-matching methodology and report both BWT and OP after matching.  
- Include or thoroughly discuss at least two of the closely related baselines (e.g., SLICE, PLAN, KeepLoRA), or justify why they cannot be included, along with a careful conceptual comparison.  
- Quantify SVD overhead and discuss approximation options.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something, especially around the LR-matching details and the FOREVER benchmark specifics.

## Soundness
2.5 Between Poor and Acceptable: The core idea is plausible and supported by some diagnostics, but the evaluation is narrow, several critical methodological details are missing or under-specified, and key ablations/baselines are absent.

## Excitement
2.5 Between potentially interesting and interesting: The framing is intuitive and the results are promising for one setup, but the limited scope and missing comparisons reduce broader excitement.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is neat and practically attractive, and the diagnostics are a plus, but the empirical scope is too narrow, several related methods are missing, and important ablations and methodological clarifications are needed. With the suggested additions and clearer methodology, this could rise to a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper focuses on training dynamics rather than new data collection. Limitations include: narrow evaluation scope (single model/benchmark), unclear generality to generative or multilingual settings, and unquantified SVD overhead. Societal risks are indirect, tied to broader issues of continual adaptation in deployed LLMs, such as potential drift or degradation if slicing choices are poor. The paper would benefit from a short discussion on deployment considerations and safeguards when applying MidPC in production continual learning.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: The method is simple and several training details are provided, and the paper claims public code. However, key details for LR matching and spectral diagnostics are underspecified, and per-task curves/metrics are missing.

## Datasets
1 No usable datasets submitted.

## Software
4 Useful.: If the promised code is complete and includes MidPC initialization, LR matching scripts, and diagnostics, it will be useful to others experimenting with continual LoRA.