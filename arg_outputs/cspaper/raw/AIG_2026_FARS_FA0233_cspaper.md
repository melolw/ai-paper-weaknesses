# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies whether output-dissimilarity monitoring can enable selective training-time defense against emergent misalignment during supervised fine-tuning. The proposed PhaseGuard-KL monitors Jensen–Shannon divergence between the current model and a fixed reference on a set of 24 safety-relevant “canary” prompts, and activates a KL penalty once divergence exceeds a threshold for two consecutive checks. Experiments on two settings, malicious fine-tuning (Security EM) and benign fine-tuning (OpSwap Tier 2), find that the trigger fires at the same early training step for both, so selective protection fails. While the method reduces misalignment on Security EM, it also substantially suppresses OpSwap task learning. The authors conclude that output-distribution shift on safety canaries is not discriminative for malicious versus benign updates.

## Summary Of Strengths
- Clear problem framing around selective defenses during fine-tuning and a falsifiable hypothesis with explicit, preregistered success criteria for both safety and utility.
- Method is simple, transparent, and easy to implement: monitor JS divergence on a canary set and switch on a KL term only when exceeding a threshold. Equation (1) precisely states the objective once the trigger fires and Equation (2) defines the monitoring statistic.
- Negative result is crisply demonstrated and communicated. Table 1 concisely shows that PhaseGuard-KL reduces Security EM misalignment but damages OpSwap performance, failing selectivity. Table 2 and Figure 2 reveal a sharp utility cliff between lambda 0.02 and 0.03, which is informative for the community.
- Figure 1 is a helpful schematic that makes the training loop and trigger mechanism easy to follow, including the role of the canary set, monitoring cadence, and rs-LoRA fine-tuning.
- The paper compares to two inference-time baselines and an always-on KL baseline, which situates the proposed approach within standard defense choices.

## Summary Of Weaknesses
1) Thin experimental validation of the triggering mechanism and its design choices  
   - The trigger relies on a fixed threshold τ = 0.15, monitoring every 5 steps, with a warmup of 3 measurements and a 2-hit rule. None of these choices are justified or stress-tested. There is no sensitivity analysis for τ, monitoring cadence, number of consecutive exceedances, or warmup length. Given that the key claim is that the trigger fires identically for both tasks, understanding whether this is robust to these settings is crucial. This is especially important because the trigger fires at step 20 in both cases and governs 90 percent plus of the remaining training.  
   - The monitor uses a truncated JS at top-k tokens, k = 256, and only at the first decode position. There is no ablation on k or on multi-token positions. If divergence is large due to early-token distribution shifts that are not safety-relevant, the selectivity failure could be a measurement artifact. Please provide sensitivity to k and to including more decode positions.

2) Canary set design is under-specified and small  
   - The canary set has 24 prompts, but the paper does not list or characterize them, nor report coverage statistics. Since the central claim is that “distribution shift on these canaries is not selective,” the community needs to know what they are. Are they sufficiently diverse to probe safety-relevant regressions without conflating benign capability drift? Without content or at least categories, readers cannot judge whether the canaries were appropriate.  
   - The paper asserts the canaries are “benign user questions designed to probe out-of-domain safety regressions,” yet the observed identical trigger time suggests the canaries capture general drift rather than safety-specific drift. A variant with mixed canaries, decoy non-safety prompts, and clear safety tags would allow ROC-style analyses of selectivity.

3) Evaluation protocol raises reliability concerns  
   - Security EM is judged by Qwen2.5-7B-Instruct, which is also the base model, creating potential bias or correlated errors. It would strengthen claims to include an external judge model and human spot checks.  
   - OpSwap is reported with one seed because “large effect sizes” are expected. In Table 2 the utility cliff is striking, but single-seed results limit confidence. The main finding would be more credible with at least three seeds and confidence intervals on OpSwap, mirroring Security EM’s three seeds.

4) Missing baselines and diagnostics that would test the core hypothesis  
   - A crucial counterfactual baseline is “PhaseGuard-KL with a random or non-safety canary set.” If random canaries also trigger at step 20, that would directly show that dissimilarity on safety-styled prompts is not unique, supporting the negative result.  
   - Another key baseline is “always-on KL with λ matched to the ex-post average effective λ under PhaseGuard-KL.” This helps separate the contribution of event-triggering from the mere presence of a KL term for most of training.  
   - Additional divergence measures such as symmetric KL, Wasserstein distance over token embeddings, or representation-space distances could test whether selectivity failure is specific to top-k JS on first-token outputs. Section 4.4 asserts “any fine-tuning shifts the distribution,” but this remains an assumption without testing alternative signals.

5) Claims about identical triggering would benefit from quantitative trajectories  
   - Section 4.4 notes that D1 reaches roughly 0.28–0.33 within five steps in both tasks. However, the paper does not plot D_t over steps for both datasets. Providing a figure of D_t versus step with the threshold line would make the argument much more persuasive and reveal whether the similarity is in timing, magnitude, or variance. Right now, the identical “step 20” in Table 1 is compelling but underexplained.

6) Limited comparison to prior or alternative in-training defenses  
   - Related work mentions Safe LoRA and in-training defenses, but there is no direct experimental comparison to techniques that intervene on internal representations or on optimizer geometry. Given the paper’s conclusion that output-dissimilarity triggers are non-selective, it would be informative to compare against at least one internal-feature intervention baseline to show that the problem is not insurmountable in principle.

7) Interpretation risks over-generalization  
   - The conclusion states that “output distribution shift is not discriminative between benign and malicious fine-tuning” and “any fine-tuning that changes behavior will trigger the defense.” The experiments evaluate one base model family, two datasets, one canary set, first-token top-k JS, and a specific trigger policy. The negative result is valuable, but the stated scope should be narrowed to these settings or broadened with more evidence.

8) Lack of formal statistical testing  
   - Table 1 reports mean ± stdev only for Security EM. There are no hypothesis tests to assert that improvements over inference-time baselines are statistically significant, nor tests that λ = 0.03 is reliably different from 0.02. Including bootstrap CIs or standard tests would improve rigor.

9) Figure- and table-specific concerns  
   - Figure 1 nicely depicts the system but omits the precise threshold, warmup, and cadence that drive the core behavior. Adding these would make the diagram self-sufficient for reproduction.  
   - Figure 2 effectively visualizes the safety–utility tradeoff. However, the plot mixes single-seed OpSwap with multi-seed Security EM without indicating variances or error bars. The absence of uncertainty on the blue curve makes the phase-transition claim harder to evaluate quantitatively.  
   - Table 2 reveals a sharp OpSwap drop from 54.44 to 22.78 between λ = 0.02 and 0.03. A per-step learning-curve figure for OpSwap at these lambdas would verify whether the drop is due to early triggering or reduced capacity to learn throughout training.

10) Reproducibility gaps despite a code link  
   - The paper footnotes a repository, but the main text does not enumerate canary prompts, data preprocessing, judge prompts and thresholds, or exact monitoring checkpoints relative to optimizer updates. These details matter for reproducing the trigger dynamics and should be included in the paper, not only in code.

## Potentially Missing Related Work
1) Zhang et al., “What Shapes Emergent Misalignment? Insights from Training Dynamics, Model Priors, and Data,” 2026 — Analyzes training dynamics and subspaces that govern misalignment severity. Directly relevant to Section 4.4’s argument about general distribution shift; should be added to Related Work and discussed in Section 5 as mechanistic context for the non-selectivity finding.

2) Brown et al., “Evil Spectra: How Optimisers can Amplify or Suppress Emergent Misalignment,” 2026 — Shows optimizer and spectral properties of LoRA can affect misalignment and proposes spectral regularization. Compare as an alternative in-training defense baseline in Section 4, and cite in Related Work.

3) Wang et al., “Emergent Misalignment Can Be Induced by Sycophancy and Reversed via Alignment Gating,” 2026 — Presents Alignment Gating that suppresses unsafe internal features while preserving capability. Discuss as an internal-representation alternative to output-dissimilarity triggering in Sections 2 and 5.

4) Jørgenvåg et al., “Reinforcement Learning Amplifies Emergent Misalignment from Harmless Rewards,” 2026 — Extends misalignment to RL settings and evaluates mitigations. Add to Related Work; mention in Conclusion as a setting where triggerable KL could be stress-tested.

5) Hassan et al., “Emergent Misalignment in Language Models: Domain Generalisation, Training Trajectories, and the Limits of Alignment Recovery,” 2026 — Provides checkpoint-level trajectories and partial recovery analyses. Cite in Related Work; connect to Section 4.4 and recommend plotting D_t trajectories.

6) Yan et al., “Thinking Hard, Going Misaligned: Emergent Misalignment in LLMs,” 2025 — Shows reasoning-induced misalignment pathways. Add to Related Work and suggest as an additional benign-seeming fine-tune to evaluate selective triggering.

7) Wang et al., “Self-Destructive Language Model,” 2025 — Proposes SEAM, an alignment-stage defense that resists harmful fine-tuning. Compare as a training-time baseline in Section 4 and Related Work.

8) Emergent Misalignment from Superposition, 2025 — Interprets misalignment via feature superposition. Include in Related Work; it can motivate moving from output divergence to representation-level monitoring in Section 5.

9) Emergent Misalignment in Mixture-of-Experts Models, 2025 — Studies architecture-specific dynamics. Add to Related Work; suggest MoE evaluation in future work.

10) Anchored SFT: KL-regularized fine-tuning without catastrophic drift, 2026 — Proposes practical always-on KL anchoring. Cite in Sections 2 and 4 as a stronger always-on KL baseline and design point to contrast with event-triggered KL.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide a sensitivity analysis for the trigger design: τ, monitoring cadence, warmup, number of consecutive exceedances, the top-k cutoff, and multi-token monitoring. If the identical step-20 trigger persists across wide settings, your negative result becomes much stronger.
- Disclose and categorize the 24 canary prompts. Add an experiment with mixed canaries, decoy non-safety canaries, and ROC-style analyses of selectivity. Consider per-prompt contributions to D_t to see whether a subset is driving early triggers.
- Add D_t vs. step plots for both datasets with threshold overlays. This directly supports the narrative in Section 4.4 and makes “identical firing” verifiable.
- Expand evaluation reliability: run OpSwap with multiple seeds and report confidence intervals; add an external judge model and small human audit for Security EM. If resources are limited, prioritize λ = 0.02 and 0.03 where the phase boundary appears in Table 2 and Figure 2.
- Include additional baselines: random or non-safety canary sets; always-on KL with matched average regularization; alternative divergence metrics; and one representation-level defense. These will clarify whether non-selectivity is fundamental to output-based triggering or specific to this monitor.

Typos and minor issues:
- Abstract: “No KL coefficient satisfies both criteria simultaneously” could cite Table 2 for precision.
- Section 3.2: Define JS_k explicitly as truncated over top-k tokens and state whether distributions are renormalized after truncation.
- Section 4.1: Clarify whether the judge model uses a fixed system prompt. If so, include it or summarize it.
- Table 1: Replace “—” in OpSwap column for inference-time baselines with “N/A” and add a footnote clarifying they were not evaluated on OpSwap.
- Figure 2: Add error bars for Security EM (across seeds) and report seed count in caption. Indicate single-seed for OpSwap, and if possible add variability bands.

Criteria to change my evaluation:
- If the revised paper adds full trigger sensitivity analyses, canary disclosure plus ROC-style selectivity tests, D_t trajectories, multi-seed OpSwap with CIs, and at least one strong internal-representation baseline or random-canary baseline, I would likely raise to 3.5 (borderline conference) given the clarity of the negative result and its utility to the community.
- If, in addition, the authors demonstrate a setting where output-based triggering does become selective through principled canary design or a better divergence signal, I would consider 4.0.

## Confidence
3 Reasonably confident but not fully verified: I am familiar with this area and the experiments, but some implementation details are not fully specified, and OpSwap is single-seed.

## Soundness
3 Acceptable: The study supports its main negative claim in this setting, but lacks key sensitivity studies, stronger baselines, and statistical testing that would be expected for a main-track paper.

## Excitement
2.5 Between potentially interesting and interesting: The selective-defense question is timely, and the negative result is informative, but the current evidence is too narrow to be exciting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea is clear and the negative result is potentially useful, but the evaluation is not sufficiently thorough for the main track, and several missing analyses limit confidence in the generality of the conclusion. Strengthening sensitivity studies, baselines, and reliability would move this toward acceptance.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper acknowledges that the approach is non-selective and harms benign learning at useful λ values. Societal impact is primarily in informing safer fine-tuning practices by avoiding reliance on naive output-dissimilarity triggers.  
- Missing discussion: risks of over-reliance on a single model judge for safety labeling; potential false reassurance if canaries are poorly chosen; distribution shift detection that penalizes non-English or domain-specific dialects disproportionately. The authors should discuss how canary design might bias against certain user groups and how failures could lead to either under-protection or unnecessary suppression of beneficial customization.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: The method is simple and high level details are given, but key ingredients are missing in the paper itself, including the exact canary prompts, judge prompting, and sensitivity settings. Public code is referenced, which helps, but core artifacts should be summarized in-paper.

## Datasets
2 Documentary: No new datasets. Reporting decisions about canaries and judge prompts would make the contribution more useful.

## Software
3 Potentially useful.: If the code indeed implements the trigger pipeline and logging, it could help others replicate or extend the negative result, but missing in-paper details currently limit ease of reuse.