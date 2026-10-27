# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes an interpretable, multi-objective reward modeling framework for RLHF. The approach has two stages: (i) train an Absolute-rating Multi-Objective Reward Model (ArmoRM) via multi-objective regression on absolute ratings from various datasets, and (ii) learn a prompt-conditioned Mixture-of-Experts (MoE) gating module that aggregates the predicted objective scores into a scalar reward using Bradley–Terry loss on pairwise data. To mitigate verbosity bias, each objective is adjusted to be decorrelated from the verbosity objective using a data-driven penalty. The resulting model, built on a Llama-3 8B backbone with a shallow MLP gate, achieves strong results on RewardBench, reported to approach a 340B reward model and outperform GPT-4 judges.

## Summary Of Strengths
- Clear problem motivation focused on interpretability and debuggability of reward models for RLHF, grounded in known issues like verbosity bias.
- Method is conceptually simple and modular: linear regression head for multi-objective absolute ratings (Equation 1), explicit verbosity-bias correction (Equations 2–3), and a lightweight MoE gating trained with BT loss (Equation 5). This pipeline is easy to understand and plausibly robust.
- Effective use of absolute rating datasets and a principled argument that binarization discards useful signal; the regression formulation sensibly leverages all dimensions.
- Concrete treatment of verbosity bias through correlation-based adjustment is valuable and aligns with known failure modes; the use of Spearman correlation is reasonable.
- Architecture is compact and efficient: gating is trained with the backbone frozen, which is attractive for practical deployment.
- Strong empirical result on RewardBench (Table 1): with an 8B backbone, ArmoRM+MoE attains an overall 89.0, outperforming LLM-as-a-judge with GPT-4/4-Turbo and exceeding the provided Llama-3 8B Bradley–Terry and Preference Model baselines. Particularly notable are gains in Reasoning and Safety.
- Figure 1 communicates the full pipeline cleanly: LLM backbone produces features, regression layer outputs interpretable objective scores, and the gating layer combines them into a scalar. The annotated example coefficients in Figure 1 reinforce the claim of interpretability by showing how objectives are weighted, including down-weighting the verbosity dimension.

## Summary Of Weaknesses
1) Limited experimental depth and analysis beyond a single benchmark.
- Table 1 is the sole quantitative evaluation. There is no ablation isolating the contribution of: (a) multi-objective regression without MoE (ArmoRM only), (b) MoE without verbosity debiasing, (c) the effect of different correlation metrics in Equations 2–3, or (d) freezing vs. fine-tuning the backbone or regression head during gating training. Without these, it is hard to attribute where the gains come from or how robust they are across settings.
- The paper would benefit from controlled ablations showing, for example, ArmoRM vs. ArmoRM+MoE across RewardBench categories, and the specific delta from the verbosity correction. Given the strong swing on Reasoning (97.3) compared to baselines in Table 1, dissecting which component drives this is important.

2) Incomplete details for the verbosity-bias correction step.
- Equations 2–3 define the correction r’i = ri − λi rverbose with Corr(r’i, rverbose) = 0. However, there is no procedural detail on estimating λi: choice of estimator, regularization, stability, per-objective variance, or whether λi is re-estimated per dataset split or globally. The selection of the reference distribution D (UltraFeedback) is mentioned in Section 4, but a sensitivity study to D is missing. If D shifts from RewardBench’s distribution, the decorrelation may be suboptimal.
- It is also not clear whether the penalty introduces unintended degradation on objectives that are legitimately correlated with verbosity (e.g., explanation detail). Some diagnostics (pre/post-correlation plots, impact on per-objective calibration) are needed.

3) Interpretability claims are under-demonstrated empirically.
- The core claim is interpretability and debuggability, yet the paper does not include qualitative analyses, case studies, or aggregated statistics of the learned gating coefficients across prompt types. Figure 1 is a schematic, not a result. For an “interpretable” RM, examples of per-objective scores and gate weights on representative prompts (safety-critical, math, casual chat) would be very informative. Even simple analyses like distributions of gate weights per RewardBench category or heatmaps would substantiate the claims.
- Without evidence that practitioners can effectively diagnose or fix failure modes using the objective-wise outputs and the gate, the interpretability advantage remains argued but not validated.

4) Possible data leakage and benchmark overlap are not addressed.
- Section 4 uses many datasets for training both stages, several of which are included in or overlap with RewardBench categories or their prior sets. The paper does not analyze contamination or quantify overlap. Given RewardBench’s construction, this is nontrivial. A careful de-duplication or at least an overlap audit is needed to ensure the reported Table 1 gains are not partly due to data leakage.

5) Gating training design choices are not justified.
- Equation 5 trains a gate with BT loss and a global scale β, while the regression head and backbone are frozen. The paper does not justify freezing, nor compare to fine-tuning the regression head jointly. The initialization of β = 100 is ad hoc, with no sensitivity analysis. Results may be brittle to β and the learning schedule without evidence to the contrary.

6) Limited generalization analysis.
- The method conditions gate weights on prompt features fθ(x), but the paper does not evaluate distribution shift, prompt length extremes, or unfamiliar topics. The static choice of a single reference D for verbosity decorrelation (UltraFeedback) could underperform when prompts differ significantly from that distribution.

7) Missing or brief training details impede full reproducibility.
- While Appendix B lists datasets and some training settings, several important details are under-specified: regression head regularization, handling objective imbalance, calibration of absolute targets, validation splits for MoE, and exact pre-processing for pairwise data (beyond referring to an external pre-processing). This is especially relevant given the sensitivity of preference models to preparation and scoring.

8) Comparative context around multi-objective alignment is thin.
- Related work acknowledges multi-objective RMs and naive linear combinations. However, there is limited discussion of alternatives that implement context-aware scalarization or routing at policy or reward level. Discussion should be expanded to include more recent multi-objective alignment and adaptive judging techniques, and to clarify how the proposed approach differs in assumptions, data needs, and failure modes.

9) Figure-level evidence is sparse.
- Figure 1 is useful architecturally, but the paper does not present any empirical figures showing learned gate behavior, objective distributions, or pre/post-adjustment correlations. This undermines the interpretability story and hinders diagnosing whether the MoE behaves as intended across prompt types.

10) Table 1 reporting would benefit from statistical context.
- No confidence intervals, standard errors, or significance testing are provided. Given RewardBench’s heterogeneity, reporting variation or bootstrap CIs per category would strengthen claims, especially for close margins like 89.3 vs 89.0 overall.

Explicit references to figures/equations/tables:
- Figure 1: The architecture figure clarifies the full pipeline and highlights interpretability via objective-level scores and gate weights. However, it is purely schematic; the paper lacks any figure that shows actual gate outputs on test prompts or distributions across categories, which weakens the interpretability and adaptability claims.
- Equation 1: Defines the multi-objective regression training. The choice of plain L2 without per-objective normalization or weighting could be problematic, given heterogeneous scales and rater reliability, although Section B states min-max normalization to [0,1]. A short analysis on objective weighting or robustness to noise would help.
- Equations 2–3: Introduce the verbosity debiasing mechanism. This is a central contribution but currently under-specified in terms of λi estimation and sensitivity to the reference D.
- Equation 5: The BT loss for gating with β scaling is reasonable, but β = 100 and freezing choices need justification. An ablation over β or a learned per-dataset β would address potential instability.
- Table 1: Provides the only quantitative comparison. The model’s Reasoning score (97.3) is notably high relative to other 8B baselines; a per-dataset breakdown within the category would help confirm robustness. The “Chat Hard” dip (76.8) versus the 70B HelpSteer2 RM (80.3) merits analysis, potentially reflecting gate mis-weighting on adversarial prompts.

## Potentially Missing Related Work
1) Lyu et al., MACPO: Weak-to-Strong Alignment via Multi-Agent Contrastive Preference Optimization, 2025 — A recent preference-optimization approach that could serve as a multi-agent alternative to reward modeling; discuss in Related Work as a contrasting route to leverage diverse signals without explicit interpretable scalarization. Consider referencing when motivating MoE vs. contrastive multi-agent strategies.

2) Kong et al., EMORL: Ensemble Multi-Objective Reinforcement Learning for Efficient and Flexible LLM Fine-Tuning, 2025 — Proposes policy-level ensembles for balancing competing goals. Add to Related Work and Discussion to contrast policy ensembles with interpretable reward scalarization; optionally mention as a future baseline.

3) Li et al., Multi-objective Large Language Model Alignment with Hierarchical Experts, 2026 — Hierarchical mixture-of-experts at the policy level to traverse Pareto trade-offs. Compare in Section 2 to clarify differences between routing on policy experts vs. interpretable objective mixing on rewards.

4) Agnihotri et al., Multi-Objective Preference Optimization: Improving Human Alignment of Generative Models, 2026 — A preference-optimization method with explicit secondary objective guarantees under KL constraints. Cite in Related Work and discuss trade-offs between training-time multi-objective PO vs. interpretable reward decomposition.

5) Miao et al., AdaJudge: Adaptive Multi-Perspective Judging for Reward Modeling, 2026 — Adaptive reward-model architecture with multi-view pooling and task-aware routing. Discuss alongside your MoE gate in Section 3.2 to position differences in representation and aggregation.

6) Chen et al., PAD: Personalized Alignment of LLMs at Decoding-Time, 2025 — Personalized reward shaping at decoding time. Discuss in Related Work as a complementary inference-time adaptation versus your training-time interpretable RM.

7) Zhang et al., AMULET: Realignment During Test Time for Personalized Preference Adaptation of LLMs, 2025 — Training-free test-time adaptation optimizing a utility function. Add in Related Work to contrast static interpretable RMs with dynamic test-time adaptation.

## Comments Suggestions And Typos
Actionable suggestions:
1) Add ablations and diagnostics.
- Report ArmoRM vs. ArmoRM+MoE; with and without verbosity correction (Equations 2–3); alternative Corr metrics (Pearson vs. Spearman); and freezing vs. unfreezing the regression layer during gating training. Include category-level results with confidence intervals. This will clarify where improvements originate and how robust they are.

2) Interpretability evidence.
- Provide case studies that show objective-wise scores and gate weights for several prompt archetypes (safety-triggering, math, general chat). Include summary plots: distribution of gate weights by RewardBench category, and pre/post-verbosity correlation matrices across objectives. This would concretely support the interpretability claim beyond Figure 1’s schematic.

3) Verbosity correction details.
- Describe how λi is estimated (closed-form slope from rank regression, numerical optimization, or another method). Add sensitivity to the choice of reference distribution D and to sample size. Report residual correlations post-adjustment on held-out data. Consider a small regularization on λi to prevent over-correction.

4) Address data leakage concerns.
- Audit overlap between training data (both stages) and RewardBench, especially its prior sets. If overlap exists, re-run with de-duplication or masked training and report the delta. At minimum, provide an overlap analysis and a discussion of impact.

5) Robustness and generalization.
- Evaluate the gate’s behavior under distribution shift: unseen domains, very short vs. very long prompts, or non-English prompts if available. Even a stress-test subset from existing data would be informative.

6) Reporting.
- Augment Table 1 with standard errors or bootstrap CIs. Provide per-dataset breakdowns within categories, especially for Chat Hard and Reasoning, to understand variability.

7) Training details and release.
- Expand Appendix B with exact preprocessing scripts, objective-wise normalization/weighting procedures, regression solver settings (including regularization), validation splits, β tuning rationale, and early-stopping criteria. If possible, release code and the trained checkpoint to strengthen reproducibility.

Typos and minor edits:
- Page 2, end of second paragraph: “making RM-aligned LLMs more reliable and robust, making RM-aligned LLMs more reliable and robust.” Duplicate clause; delete the repetition.
- Section 3.1 opening references “previous blog”; remove or replace with a formal citation.
- Appendix B: Some bullet points use “•” vs “-” inconsistently; unify formatting.
- Ensure consistent capitalization of datasets (e.g., “BeaverTails-30k” vs “Beaver-Tails”).
- Page 4, “The scaling variable β is initialized with a value of 100” — consider clarifying if tuned or fixed.

Criteria that could raise my score:
- Strong ablations isolating contributions of each component, with statistical confidence.
- Concrete interpretability evidence via gate/objective visualizations and case studies.
- Overlap analysis with RewardBench and, if necessary, contamination-mitigated results.
- Detailed description and sensitivity analysis for the λi estimation procedure.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully; unlikely I missed something material.

## Soundness
3.5: Between Acceptable and Strong — Solid idea and promising results, but ablations and methodological details (verbosity correction estimation, freezing choices, contamination audit) are missing.

## Excitement
3.5: Between interesting and exciting — A practical and interpretable approach to an important problem with strong headline results; additional analysis would further raise excitement.

## Overall Assessment
3.5 Borderline Conference: Close to being acceptable for the main conference but has notable weaknesses. The approach is well-motivated, methodologically clean, and shows strong RewardBench results (Table 1). However, limited ablations, under-specified verbosity-correction details (Equations 2–3), lack of interpretability demonstrations beyond a schematic, and no overlap audit temper the case for a clear accept. With the suggested additions, this could become a strong main-track paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section noting model size, benchmark scope, language coverage, and potential risks in deployment. This is appreciated. Additional suggestions:
- Bias and fairness: Evaluate whether the gating or objective corrections inadvertently disadvantage certain content types or dialects. Include a brief audit across demographics or topics if feasible.
- Dual use: Interpretable objective weights can help users diagnose behavior, but also enable adversaries to game the reward. Discuss safeguards beyond general recommendations, such as randomized audits or ensemble checks.
- Non-English coverage: Even a small-scale check on multilingual prompts, or a discussion on extending objectives to multilingual ratings, would inform broader impact.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Many details are present and the approach is straightforward, but full reproducibility would benefit from code/models and more precise training/preprocessing descriptions.

## Datasets
2: Documentary — No new dataset is released; training data are collated from existing sources. The curation details are useful for replication but do not constitute a new resource.

## Software
1: No usable software released — The paper does not state that code or checkpoints are available.