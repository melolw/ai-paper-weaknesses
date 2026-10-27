# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes GSIL, a generalized self-imitation learning framework for aligning LLMs using only offline human demonstrations. The key idea is to optimize a reverse-KL imitation objective by estimating a log density ratio between the demonstration distribution and the current policy via binary classification, then reparameterizing the discriminator in terms of the policy to obtain simple, fully offline training losses. The framework unifies a family of density-ratio estimation–based losses (e.g., Logistic, Hinge, Brier, KLIEP, LSIF) under a single objective that contrasts real demonstrations with model-generated samples. Experiments on UltraFeedback and Anthropic-HH show consistent gains over SFT and SPIN, and the paper reports stronger results than DPO on several benchmarks.

## Summary Of Strengths
- Conceptual unification and clarity: The paper connects imitation learning for LLM alignment with density-ratio estimation and shows how many proper scoring rules translate into practical offline losses. The general GSIL loss in Equation (17) is a clean umbrella that subsumes several well-known objectives.
- Practicality: The approach avoids adversarial training and RL loops. The proposed training pipeline uses simple binary classification losses and self-generated samples, aiming to keep finetuning costs closer to SFT.
- Strong empirical results on difficult tasks:
  - In Table 2, multiple GSIL variants outperform SFT and SPIN across ARC, TruthfulQA, Winogrande, GSM8K, HumanEval, MT-Bench, and AlpacaEval 2. Especially notable are the HumanEval gains (e.g., Logistic: 36.58 vs. 31.70 for SPIN and 26.82 for SFT) and GSM8K gains (31.84 vs. 28.63 for SPIN).
  - The iterative self-play in Table 3 shows continued improvements, especially for HumanEval (up to 42.15), suggesting the method compounds gains with additional rounds.
- Insightful analysis of training dynamics:
  - Figure 2 is compelling: while both SPIN and GSIL widen the margin between real and self-generated responses, SPIN’s “Rewards(Real)” decreases below zero, whereas GSIL keeps it positive and increasing. This directly supports the claim that GSIL avoids decreasing likelihood of real demonstrations, which matters for correctness-sensitive domains.
  - Figure 6 (heatmaps of β and γ) and the additional heatmaps (Figures 8–9 in Appendix) elucidate the role of scale and shift, informing practical tuning.
- Breadth of the framework:
  - Table 1 and Figure 7 demonstrate how different proper scoring rules instantiate different GSIL variants. The paper does not insist on a single loss, but rather shows a design space with trade-offs, which is valuable to practitioners.
- Safety alignment evidence:
  - On Anthropic-HH, Figure 4 shows higher GPT-4 win rates for GSIL across temperatures compared to SFT and SPIN. This, combined with qualitative examples (Tables 5–6 in Appendix), strengthens the case that GSIL improves both helpfulness and harmlessness when trained only on chosen demonstrations.

## Summary Of Weaknesses
1) Derivation clarity and correctness around density ratio and normalization:
   - Equation (9) introduces α (class-prior weight) and a power-scale 1/β. This goes beyond the standard link s*(x,y)=log p(c=1|x,y)/p(c=0|x,y) for logistic DRE. The paper motivates β as a bias-variance knob and α as prior reweighting, but it is not made explicit whether the resulting r(x,y) still corresponds to a log density ratio consistent with the closed-form optimal policy in Equation (10).
   - The claim right after Equation (10) that Z(x)=1 relies on r(x,y)=log πdata/πθt exactly. However, when r is parameterized via s* with α and β (Equations (11)–(13)), the self-normalization property no longer obviously holds. Please clarify whether Equations (12)–(13) still inherit Z(x)=1, or whether the α,β,γ reparameterization approximates the ideal r and breaks self-normalization. If the latter, state the conditions or bias induced.
   - Actionable request: add a short derivation that clearly shows when Equations (11)–(13) are equivalent to optimizing reverse KL in Equation (6) and when they are only approximations; make explicit how α and β affect normalization and fixed points.

2) Positioning to closely related imitation-style LLM post-training:
   - The paper’s narrative around reverse-KL and density-ratio classification is timely, but discussion is thin on adjacent imitation or IRL-based finetuning for LLMs and reverse-KL preference optimization variants. See “Potentially Missing Related Work.”
   - Actionable request: add a subsection contrasting GSIL’s objective to recent IRL-style or reverse-KL imitation/post-training formulations for LLMs, clarifying theoretical and practical distinctions.

3) DPO comparison is limited and difficult to assess:
   - Figure 5 compares GSIL to DPO on three benchmarks but omits the settings, number of training steps, sampling strategy for positives/negatives, and base models. In the main setup you restrict yourself to chosen-only data, but DPO requires preferences and therefore uses more information. It is important to disclose how DPO was trained and tuned here.
   - Actionable request: report a complete DPO baseline table matching Table 2 (same base model, same training budget, tuned across β and other hyperparameters), or clearly state the purpose and scope of Figure 5 to avoid overclaiming.

4) Reproducibility and missing procedural details:
   - Section A.3 provides batch size, optimizer, LR schedule, and search ranges for β and γ. However, critical aspects for reproduction are missing:
     - Number of self-generated samples per prompt, and whether negative sampling is refresh-once or resampled each epoch.
     - Sampling temperature(s) during self-generation for UltraFeedback training and Anthropic-HH training (Figure 4 explores evaluation temperatures, not training).
     - Mixing ratio between demonstrations and self-generated samples within a batch.
     - Sequence lengths, stop criteria, filtering of degenerate generations, de-duplication, and tokenization normalization.
     - Epochs/steps per dataset and per GSIL iteration, and early stopping criteria.
   - Actionable request: add a one-page methods box or algorithm pseudocode detailing the self-generation protocol and data mixing; include exact training budgets and sequence lengths.

5) Limited exploration of failure modes and stability across losses:
   - Table 1 presents six losses, but the stability characteristics differ substantially (e.g., KLIEP/LSIF can be unstable due to heavy-tailed weights). Figure 10 suggests all GSIL variants keep real rewards positive, yet KLIEP shows very large reward scales (Appendix Figure 10 and the main Figure 2 vs. Figure 10 panels).
   - Actionable request: report simple stability diagnostics (e.g., gradient norm statistics, training loss curves) and one stress test with noisy demonstrations to show which losses are robust under imperfect data.

6) Fairness of SPIN comparisons:
   - SPIN hyperparameters are said to be “thoroughly tuned,” but only β∈{0.01,0.1,1} seems explored. Given SPIN’s sensitivity to reference scaling and temperature, this may be narrow. Also clarify if SPIN uses the same self-generated pool and exact generation settings so that comparisons isolate the loss only.
   - Actionable request: document matched generation and data-mixing protocols and report sensitivity to generation temperature and number of negatives for both SPIN and GSIL.

7) Overgeneralized “mode-seeking vs mass-covering” claim:
   - Figure 1 and the discussion around reverse KL are sound as high-level intuition, but the empirical link would be stronger if you included a controlled diagnostic that shows how reverse-KL sharpening, rather than just relative-likelihood contrast, drives the observed improvements on GSM8K/HumanEval. For instance, report log-likelihood changes on the demonstration set and on a held-out set of correct solutions for GSM8K to empirically confirm the “non-decreasing likelihood of correct responses.”
   - Actionable request: add a quantitative plot mirroring Figure 2 but tracking per-token NLL on the demonstration data and a curated “gold” subset.

8) Scope of evaluation:
   - The main table (Table 2) is solid, yet broader reasoning datasets (e.g., BBH, MATH, GSM8K-cot variants), or code datasets beyond HumanEval (e.g., MBPP) would further confirm robustness.
   - Actionable request: at minimum add MBPP or MBPP+ for code, and one additional math benchmark, or provide a rationale for the current selection.

9) Efficiency claims:
   - The paper claims GSIL is “lightweight and efficient,” but there is no report of training wall-clock time or token throughput relative to SFT and SPIN. Since GSIL requires self-generation, the cost could exceed SFT even without adversarial training.
   - Actionable request: report end-to-end training time and GPU-hours for SFT, SPIN, and at least GSIL-Logistic.

10) Minor clarity issues:
   - Notation swaps between πt, πθt, and πref can be confusing. In Equations (7), (10)–(13), clearly define whether θt is the fixed sampling policy per iteration and how often it updates. Provide a compact algorithm box with these dependencies.

Detailed figure- and table-specific comments:
- Figure 2: The side-by-side dynamics for SPIN vs. GSIL with Logistic are one of the most persuasive pieces of evidence in the paper. They directly support the claim that GSIL does not sacrifice the likelihood of real demonstrations. Consider adding a third panel for Brier (or include a reference to Appendix panels) to show that the positive trend is not unique to Logistic.
- Figure 3: The MT-Bench radar plot shows noticeable gains in Reasoning, Math, and Coding for GSIL variants, which aligns with Table 2’s GSM8K and HumanEval boosts. Please include the underlying per-category numeric scores in an appendix table.
- Figure 4: Win-rate vs. sampling temperature is informative. Indicate error bars or confidence intervals for all curves and state the number of sampled dialogues per temperature.
- Figure 5: The DPO comparison bar chart is helpful but incomplete without exact setups. See weakness (3).
- Figure 6: The β,γ grids are valuable. The GSM8K heatmap suggests small β and larger γ tend to help. It would be helpful to add one more grid for HumanEval to see if the same pattern holds.

## Potentially Missing Related Work
1) Wulfmeier et al., “Imitating Language via Scalable Inverse Reinforcement Learning,” 2024 — IRL-style post-training on supervised data for LLMs; directly relevant to the paper’s imitation perspective. Should be discussed in Section 2 (Background) and contrasted with Equations (6)–(7) to clarify differences between IRL reward-learning vs. GSIL’s density-ratio surrogate and reparameterization.
2) Yu et al., “Offline Imitation Learning with Suboptimal Demonstrations via Relaxed Distribution Matching,” 2023 — RelaxDICE uses f-divergence–based density-ratio regularization to handle imperfect offline data, thematically aligned with Section 4.3. Should be cited in Section 4.3 and discussed after Equation (17) as a robustness-oriented extension when demonstrations are noisy or suboptimal.
3) Lv et al., “Towards a Unified View of Large Language Model Post-Training,” 2025 — Presents a unified framework connecting SFT, RLHF, and offline/online variants; GSIL should be situated within this taxonomy in Section 1 or 2 to help readers place it among post-training methods.
4) Ruoss et al., “LMAct: A Benchmark for In-Context Imitation Learning with Long Multimodal Demonstrations,” 2025 — While focused on in-context imitation rather than parameter finetuning, it provides complementary evaluation regimes for imitation. Could be briefly mentioned in the evaluation discussion as a future direction to test GSIL’s advantages beyond parametric finetuning.
5) Ding et al., “Rethinking Expert Trajectory Utilization in LLM Post-training,” 2026 — Analyzes how to best use expert trajectories in SFT–then–RL pipelines for math reasoning. Add to Section 5 or Limitations to discuss when GSIL might be combined with RL phases and how it could interact with trajectory-quality considerations.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Provide a precise derivation around Equations (9)–(13) explaining the role of α, β, and γ, and explicitly state when Z(x)=1 still holds. If it does not, discuss what fixed point GSIL optimizes and whether it is still reverse-KL consistent.
- Expand the DPO comparison into a full table like Table 2 with matched compute, data, and hyperparameter sweeps. If the goal is only to demonstrate that GSIL can be competitive without preferences, state this clearly and avoid broader claims.
- Add an algorithm box that specifies: generation temperature(s), number of self-generated negatives per prompt, refresh frequency, mixing ratios with demonstrations, max lengths, stopping criteria, and de-duplication/quality filters. This will materially improve reproducibility.
- Efficiency: report GPU-hours and wall-clock time relative to SFT and SPIN (and DPO if included). If generation dominates cost, discuss mitigations (e.g., cached negatives, short-answer sampling for math/code).
- Robustness: show at least one experiment with noisy or partially incorrect demonstrations to verify which GSIL losses are stable (Table 1 losses can behave very differently under noise).
- Clarify exact scoring and aggregation for Anthropic-HH GPT-4 judging. State the number of sampled prompts per temperature, confidence intervals, and the prompt in Table 4 (already included) to ensure full transparency.

Minor notes and typos:
- Page 3, Equation (9): The expression is split awkwardly across lines; rewrite for clarity. Consider explicitly showing P(c=1)/P(c=0)=α and how β enters the mapping.
- Page 5, “syntactic data” is used a few times; it should be “synthetic data.”
- Page 6, Table 1 caption: “please refer to Figure 7 in the Appendix for the loss visualization” — good cross-reference; also ensure the domains of fθ that cause unbounded penalties (e.g., LSIF) are discussed in text.
- Page 7, Table 2: add standard deviations or at least multiple-run averages for the stochastic datasets (HumanEval Pass@1 especially benefits from repeated sampling).
- Figure 3 (radar): include a legend font that is easier to read and consider plotting confidence ranges.
- Page 8, “syntactic” appears again; replace with “synthetic.”

Criteria for score change:
- If the authors provide the missing derivation/clarifications around Equations (9)–(13) and add a rigorous, matched DPO baseline table, along with the full training protocol (algorithm box) and compute costs, I would raise Soundness and Reproducibility, and my overall score could increase to 4.5 (borderline award) if the results remain as strong.

## Confidence
4: Quite sure after careful checking — I tried to check important points (derivation consistency, experiment tables/figures, and positioning). Some uncertainty remains around the exact normalization guarantees under α,β,γ.

## Soundness
4: Strong — The paper provides substantial support for its main claims via consistent improvements in Table 2, training-dynamics evidence in Figure 2, and safety gains in Figure 4. However, derivation clarity for the density-ratio reparameterization and normalization warrants tightening, and the DPO comparison needs a fuller account.

## Excitement
3.5: Between interesting and exciting — The framework is thoughtfully unified and the wins on code/math are meaningful. With clearer theory-experiment linkage and stronger baselines, this could be even more impactful.

## Overall Assessment
4: Conference — Recommend accept. The paper offers a principled and practical framework that unifies density-ratio–based offline imitation losses for LLM alignment and shows robust gains over strong demonstration-only baselines across multiple benchmarks. The method is simple to implement, avoids adversarial training, and is well analyzed with informative figures. The main gaps are clarity around the role of α,β,γ in the density-ratio mapping and the limited DPO comparison. These are addressable in camera-ready.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
- Limitations are acknowledged: the need to tune γ, and the fact that GSIL currently leverages only chosen responses rather than full preference data. I would add:
  - Efficiency trade-offs vs. SFT due to self-generation.
  - Potential for overfitting to demonstration style if γ is large (Figure 6 suggests strong prior weight helps; discuss risks).
  - Bias amplification: if demonstrations reflect demographic or stylistic biases, GSIL may “mode-seek” those modes more sharply than SFT.
- Societal impact: The Anthropic-HH results suggest GSIL improves harmlessness; however, GPT-4-as-judge may inherit its own biases. A brief discussion of evaluator bias and potential mitigations would strengthen this section.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — The paper includes many key details and a code link is stated. To reach 5, add the precise self-generation protocol, mixing ratios, and full compute accounting, and include seed control with run-to-run variance.

## Datasets
1: No usable datasets submitted.

## Software
4: Useful — If the promised code is released with the missing training-protocol details and scripts, it should be straightforward for others to apply GSIL and its variants.