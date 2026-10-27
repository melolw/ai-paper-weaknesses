# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper analyzes why some jailbreak prompts succeed by studying how prompts are embedded in the hidden representation space of safety-aligned LLMs. Using PCA on last-token hidden states, the authors show that harmless and harmful anchor prompts form separable clusters in several chat models, and that successful jailbreaks tend to move harmful prompts along a direction from a “refusal center” to an “acceptance center.” They formalize this by defining an acceptance direction in PCA space and propose a simple optimization objective that steers prompts along this direction. Integrated into GCG and AutoDAN, the approach increases attack success rate (ASR) in many settings, especially for GCG, and the paper further examines defenses (perplexity filtering and paraphrasing) and limited transferability.

## Summary Of Strengths
- Clear empirical analysis of internal representations:
  - Figure 1 (pages 4–5) compellingly visualizes separability between harmful and harmless anchors for Llama-2/3 models, and shows that successful jailbreak prompts tend to lie closer to the harmless region than failed ones. Table 1 quantifies this via projected distances to centers along the acceptance direction, strengthening the qualitative claim.
  - The authors provide additional evidence that the first two principal components capture harmfulness signals, including explained variance ratios and between/within-class variance estimates.
- Simple and interpretable formulation:
  - Definition 3.1 and Equation 1 define the “acceptance direction” and a steering objective that is easy to implement and plug into white-box attacks (GCG and AutoDAN).
  - The early-stopping protocol (Figure 2) balances speed and accuracy with a lightweight keyword screen and a learned LLM-based judge (Mazeika et al., 2024).
- Useful quantitative evaluation:
  - Table 2 shows sizeable ASR gains for GCG+Ours across several models, e.g., Llama-2-13b-chat: 26.15% to 62.31%; Llama-3-8B-Instruct: 57.12% to 73.85%.
  - Table 3 and Figure 3 corroborate the core hypothesis on Llama-2-7b: succeeded prompts move closer to the acceptance center than failed prompts under both GCG and AutoDAN variants.
  - The defense analysis (Table 5) reveals interesting interactions: perplexity filtering heavily affects GCG-style suffix attacks, while paraphrasing largely disrupts harmfulness while preserving much other semantics (Table 4).
- Clarity and organization:
  - The paper is well structured, with a clean narrative from analysis to method and experiments. Quantitative tables and figures are referenced appropriately.
- Reproducibility:
  - Hyperparameters are stated; code is promised; evaluation settings and datasets are standard in safety research.

## Summary Of Weaknesses
1) Dependence on PCA anchoring and anchor selection, with limited robustness study
- The acceptance direction is computed from PCA on two small anchor sets of 100 prompts each (Section 3, “Analysis Setups”). The paper does not examine robustness to:
  - alternative dimensionality reduction methods (e.g., CCA, UMAP, t-SNE used only for visualization, supervised LDA);
  - different layer choices or pooling strategies beyond using last-token hidden states;
  - anchor sampling variance or size.
- While some explained-variance statistics are reported for llama2-7b (page 3), systematic sensitivity analyses are missing. This matters because Equation 1 fully relies on this anchored geometry. If the direction is unstable across anchors, layers, or PCA runs, the method’s conclusions and benefits could be fragile.

2) Conceptual circularity and evaluator dependence
- The optimization and early stopping rely on moving representations toward a direction defined by the model itself, and then a learned LLM judge (Mazeika et al., 2024) is used to score success. There is a risk that the gains partially reflect alignment with the judge’s preferences rather than genuine task-level success. While the double-check in Figure 2 is sensible, the setup would be stronger with:
  - cross-judging using multiple, differently trained judges;
  - human spot checks on a stratified subset;
  - calibration against refusal-rate metrics independent of the specific classifier prompt.

3) Mixed results and method scope
- The proposed objective helps GCG consistently, but not AutoDAN; in Gemma-7b, AutoDAN+Ours drops sharply (59.81% to 46.15%, Table 2). The paper attributes this to volatility of genetic search, but this highlights that the objective is not robust across popular attack families.
- The approach requires white-box access (Section 5.1), which limits practical applicability; the black-box attack PAIR is only studied in the representation analysis but not enhanced by the proposed objective.

4) Limited breadth of representation analysis
- The paper focuses on the last input token’s final-layer representation. Without ablations over:
  - intermediate layers or averaged token states;
  - instruction-tuned vs. base models beyond the chosen set;
  - multilingual or multi-turn settings;
it is hard to claim that the acceptance direction generalizes. The negative or ambiguous findings for gemma-7b (Table 1 and Figure 1d/h/l) underscore the need for broader analysis.

5) Defenses and transfer experiments are informative but underspecified statistically
- Table 5 and Table 6 provide useful evidence, but the paper does not report confidence intervals or significance testing for ASR improvements or drops, despite sometimes small absolute differences. Given the variability in genetic algorithms and sampling, this is important to support strong claims.

Figure- and table-specific comments
- Figure 1: The trend that successful jailbreaks cluster closer to harmless anchors is visually most obvious for Llama-2-7b and Llama-2-13b with GCG and AutoDAN; for Gemma-7b the pattern is weaker, which the paper acknowledges. This difference is central to the paper’s story and could be analyzed more deeply, e.g., by explaining why non-explicit alignment training leads to reduced harmfulness separability.
- Table 1: The projected distances clearly decrease toward the harmless center for success vs. failure in Llama-2/3, but less consistently for Gemma-7b. It would help to add variance across runs or bootstrapped CIs on these projected distances.
- Table 2: The headline gains for GCG+Ours are strong, but AutoDAN+Ours is mixed. A per-iteration plot of Equation 1 for AutoDAN could reveal whether the optimizer ever meaningfully optimizes the steering objective.
- Table 4: Nicely supports the claim that paraphrasing disrupts harmfulness specifically by primarily moving points along the first two PCs. Given this is a core interpretability claim, replicating the finding on another model beyond Llama-2-7b would strengthen it.
- Table 5: Perplexity filtering almost wipes out GCG(+Ours) but not AutoDAN(+Ours), showing these defenses detect different attack families. It would be useful to include AUC-style curves over multiple thresholds, not just a single threshold at 120.
- Table 6: Transferability remains poor; although unsurprising, this raises the question of whether the acceptance direction is model-idiosyncratic. A cross-model alignment experiment that computes directions on one model and evaluates geometric separability on another would be insightful.

## Potentially Missing Related Work
1) Lee et al., xJailbreak: Representation Space Guided Reinforcement Learning for Interpretable LLM Jailbreaking, 2025 — Optimizes jailbreak prompts in representation space using RL. Highly relevant baseline for attack performance and for discussing objective design similar to Equation 1. Should be cited and compared in Related Work (Section 2) and discussed after Equation 1, and ideally considered in experiments or as a conceptual baseline.

2) Zhang et al., JBShield: Defending Large Language Models from Jailbreak Attacks through Activated Concept Analysis and Manipulation, 2025 — A defense via concept activations in hidden states. Directly related to this paper’s representation-space framing; should be discussed in Section 2 and referenced in Section 5.3 as a complementary defense to perplexity/paraphrasing.

3) Bullwinkel et al., A Representation Engineering Perspective on the Effectiveness of Multi-Turn Jailbreaks, 2025 — Studies conversation trajectories and benign-region steering in activation space. Useful to contextualize single-shot acceptance-direction results and suggest extensions to multi-turn, to be discussed in Section 6 and Related Work.

4) Chen et al., Cross-model Transferability among Large Language Models on the Platonic Representations of Concepts, 2025 — Investigates cross-model alignment of concept directions. Directly relevant to Section 5.4 on poor transferability; should be discussed and could inform additional analyses on cross-model direction alignment.

5) Sheng et al., AlphaSteer: Learning Refusal Steering with Principled Null-Space Constraint, 2026 — Learns refusal directions with null-space constraints. Relevant to the construction of acceptance/refusal directions and potential defenses; cite in Related Work and discuss in Section 6.

6) Derya et al., Revisiting JBShield: Breaking and Rebuilding Representation-Level Jailbreak Defenses, 2026 — Analyzes robustness of representation-level defenses against adaptive attacks. Good counterpoint to claims about direction-based methods; discuss in Related Work and Section 5.3 as a cautionary note.

7) Wei et al., Understanding and Defending VLM Jailbreaks via Jailbreak-Related Representation Shift, 2026 — Extends representation-shift analysis to multimodal models. Relevant for positioning this work as the text-only counterpart; cite in Related Work and mention as future extension in Section 6.

8) Defending LLMs against jailbreak attacks through representation offset detection, 2026 — Proposes Representation Offset Defense (ROD) that detects misalignment in hidden space. Highly relevant to defense-side comparisons; add to Section 2 and Section 5.3.

9) Yamaguchi et al., Adversarial Manipulation of Reasoning Models using Internal Representations, 2025 — Identifies “caution” directions in CoT models and manipulates them. Relevant to analyzing layer-wise or step-wise refusal/acceptance signals; cite in Related Work and discuss as an avenue to extend beyond last-token embeddings.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment if addressed:
- Robustness of the acceptance direction:
  - Add ablations over layers (early/middle/final), token pooling strategies (mean over prompt tokens vs. last token), and dimensionality reductions (PCA, supervised LDA/PLS, CCA). Report how Figure 1 and Table 1 patterns change. If the effect is stable, it strengthens the hypothesis substantially.
  - Study anchor sampling variance. For multiple randomly sampled anchor subsets of various sizes (e.g., 50/100/200), report stability of the direction and the downstream ASR gains with GCG+Ours (include confidence intervals).
- Evaluator diversity and human calibration:
  - Evaluate ASR with at least two additional automatic judges (e.g., different fine-tuned LLMs and a rule-based refusal detector) and include a small human audit for borderline cases. Report inter-judge agreement.
- Strengthen AutoDAN analysis:
  - Plot Equation 1 values and acceptance-direction projections across AutoDAN generations to test whether the genetic search ever benefits from the steering signal. If not, explore integrating steering as a fitness term with adaptive weighting or mutation constraints.
- Beyond last-token and single-turn:
  - Include at least one study with trajectory-level features (e.g., average over final hidden states of generated tokens or contrasts at the first response token), and a short multi-turn pilot to see whether the hypothesis holds across turns.
- Statistical reporting:
  - Add standard errors or bootstrap CIs for ASR in Table 2 and for distances in Tables 1 and 3, and perform statistical tests for the main comparisons.
- Minor issues and typos:
  - Page 4 caption: Label “(1) gemma-7b” should likely be “(l) gemma-7b.”
  - Ensure consistent capitalization of model names and datasets (e.g., llama2-7b vs. Llama-2-7b-chat).
  - Check dangling hyphenation in Section 5.3 around “Auto-DAN.”
  - Appendix F: stray sentence breaks and encoding artifacts around “It is not …”.

Criteria for score increase
- If the authors provide strong robustness ablations for the acceptance direction (layer, pooling, anchor sampling), diversify and calibrate evaluators, and add statistical significance reporting for the main results in Tables 1–3, I would be inclined to move to 4.0. Demonstrating improved integration with AutoDAN or black-box settings would further strengthen the case.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: The representation-analysis narrative is coherent and supported by multiple figures and tables. The main caveats are evaluator dependence, limited robustness ablations, and mixed results for AutoDAN.

## Excitement
3.5 Between interesting and exciting: The geometric view is clear and useful, and the plug-in objective is elegant. The limitations around robustness and scope temper the excitement.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses. The representation-space analysis and the acceptance-direction objective provide useful insight and deliver clear gains for GCG, supported by Figure 1 and Tables 1–3. However, reliance on PCA anchoring with limited robustness study, evaluator dependence, and mixed effectiveness for AutoDAN hold it back. With additional robustness ablations, diversified evaluation, and statistical reporting, I would lean to 4.0.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges white-box limitations and scope. Given the dual-use nature of jailbreak research, further discussion would help:
- Potential for misuse by improving attacks versus value to defenders for understanding and mitigation.
- Responsible release practices for code, including safeguards and intended-use statements.
- Risks of false positives/negatives in automated judges and who might be harmed by over- or under-blocking policies suggested by these findings.
- Over-refusal risks if defenses overfit to representation directions.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Key hyperparameters and setups are described, code is promised, datasets are standard. Some dependencies on specific judges and anchors suggest moderate variance, but overall it should be reproducible.

## Datasets
1 No usable datasets submitted.

## Software
4 Useful.: I would recommend the new software to other researchers or developers for their ongoing work.