# Preliminary Observations:
Topic/scope mismatch: the submission is a cosmology/astrophysics paper about tensor-train compression and graph embeddings for estimating Ωm and σ8 from dark matter halo merger trees. It does not study language, text, speech, or NLP systems, and it does not connect its methods to computational processing of language. Structurally complete and written in English. No hidden prompts detected.

# Expected Review Outcome:

## Paper Summary
The paper proposes a pipeline to estimate cosmological parameters (Ωm and σ8) from dark matter halo merger trees. The method: (i) identifies “significant” merger-tree substructures; (ii) extracts 10 physical features per substructure; (iii) computes a 64-d GraphSAGE autoencoder embedding per substructure; (iv) concatenates these into 74-d vectors for up to 60 substructures per tree, forming a (60, 74) tensor; and (v) applies a Quantum-Inspired Tensor Train (QITT) decomposition to compress 4440 features to 202 dimensions. Linear regression, Random Forest, and XGBoost are trained on these QITT features to predict Ωm and σ8. Reported test performance shows QITT_LinearRegression achieves R² ≈ 0.923 for Ωm and 0.621 for σ8, while a simpler baseline using global aggregate features attains even higher R² for Ωm (≈0.970). Figures visualize example substructures, embedding structure, TT core magnitudes, model comparisons, feature importances, and predicted-vs-true plots.

## Summary Of Strengths
- Clear pipeline description that integrates multi-scale graph-derived substructures, learned graph embeddings, and tensor-train compression into a compact feature space. The end-to-end story is coherent and easy to follow.
- Sensible experimental protocol for avoiding simulation leakage via splitting at the simulation level (Section 2.1.2), which is important in this setting.
- The figures support the narrative:
  - Figure 2 (t-SNE of 64-d embeddings) shows clustering by substructure size, suggesting the GraphSAGE embeddings capture meaningful structural variation consistent with the intended design.
  - Figures 4 and 5 (RMSE and R² comparisons) demonstrate that QITT features consistently improve over naive flattening of high-dimensional substructure features, especially for σ8, which helps justify the compression step.
  - Figures 10 and 11 (predicted vs. true) provide an intuitive view of performance differences between Ωm and σ8 and align with the reported metrics.
- The paper is transparent about a strong baseline: global aggregate features outperform QITT features for Ωm. Acknowledging this strengthens the credibility of the empirical section.
- QITT rank selection is spelled out in Section 3.2, and the derivation of the 202-d feature size from the TT-cores is explicit.

## Summary Of Weaknesses
1) Topic mismatch with ACL main track
   - The work is about cosmological parameter inference from astrophysical merger-tree graphs. There is no substantive connection to language, text, speech, or NLP tasks, datasets, or theory. This is a critical scope mismatch for ACL.

2) Inconsistency in tensorization description
   - Section 2.5.1 describes reshaping the 4440-d vector into a 6-mode tensor (2, 2, 2, 3, 5, 37). Later, Section 3.2 states the 74-d per-substructure block is reshaped to (2, 37), producing a 3rd-order tensor (60, 2, 37). Only the latter is used to derive the 202-d feature count. The paper does not reconcile these two different tensorizations. This matters because TT performance can depend strongly on mode order and ranks; readers cannot tell what was actually used across experiments, which undermines reproducibility and interpretation.

3) Ambiguity in the “10 physical features” count
   - Section 2.3.1 lists 1 mass ratio, 1 merger scale factor, 2 property differences, and 8 branch-level stats (means and stds for four properties), which totals 12, not 10. Elsewhere the paper repeatedly calls it a 10-d physical vector. This dimension mismatch is nontrivial because it propagates to the (60, 74) tensor shape, padding strategy, and rank selection for QITT.

4) Substructure definition and truncation may bias results
   - The “significance” threshold is described qualitatively in Section 2.2.1, then changed to the 20th percentile in Section 3.1 without a clear, principled justification. The truncation to at most 60 substructures per tree (Section 2.4.2) is fixed “based on preliminary analysis,” yet Figure 1 and the stats in Section 3.1 show highly variable substructure counts, even up to 563. Truncating or heavy padding risks discarding signal from complex trees and introducing variable proportions of synthetic “null” data, which can bias the learned representation.

5) Padding strategy may leak meta-information
   - The “null” substructure is not pure zeros; its 64-d topological embedding is produced by the GraphSAGE encoder applied to a canonical single-node graph (Section 2.4.2). This likely makes the fraction of padding detectable to downstream models, effectively injecting a proxy for “how many real substructures this tree had,” which could be a confound rather than desired physics/topology. If the padding fraction correlates with target parameters through dataset construction, models may exploit this shortcut.

6) GraphSAGE autoencoder training details and leakage risks
   - Section 2.3.2 mentions pretraining on “a large corpus of generated graphs, including a subset of the merger trees,” and Section 3.1 says it was trained on 33,759 substructures. It is unclear whether any pretraining data overlaps in simulation identity with the held-out test simulations, and whether the embedding model saw subgraphs derived from the same simulations that later appear in evaluation. Since the split is at simulation level, clarity on GNN pretraining splits is essential to avoid representation leakage.

7) Statistical testing assumes independence of test examples
   - Section 3.3.5 reports paired t-tests run over per-tree errors from the 150 test trees. But test trees are clustered within only 6 simulations (Section 2.1.2). Treating 150 trees as i.i.d. when there are only 6 independent simulation settings can inflate effective sample size and lead to overly optimistic p-values. A correction accounting for cluster structure (e.g., within-simulation aggregation or mixed-effects models) is warranted.

8) Limited comparison against standard dimensionality reduction
   - The strongest QITT claims are about “creating compact, informative representations.” However, there is no comparison to simpler reducers such as PCA on 4440-d flattened features, PCA on 600-d physical features, or ridge/lasso on the high-dimensional space. Since QITT_LinearRegression is very strong, a PCA+Linear baseline is a natural, necessary control to isolate whether TT structure, rather than general shrinkage/rotation, provides the gains.

9) Over-interpretation of TT core magnitudes
   - Section 3.2 and Figure 3 discuss magnitude ranges of cores (Core 2 reaching ~300), interpreting this as “larger leverage.” TT cores are not unique due to gauge freedom; differences in scale across cores can arise from factorization choices, not necessarily physical import. Without fixing a gauge or providing invariants, magnitude comparisons may mislead readers about which core matters most.

10) Presentation gaps and lack of tables
   - The paper relies exclusively on figures for results (no numeric tables for key metrics, ablations, or hyperparameters). This makes exact reproduction and careful comparison difficult. For example, Figures 4–5 do not list confidence intervals or standard deviations. A tabular ablation that includes: with/without topology embedding, with/without truncation, varying padding strategies, PCA vs. QITT, and rank sweeps would clarify where the gains originate.

11) Discrete target structure and potential shortcut learning
   - Figures 10 and 11 show clear vertical clusters along discrete true-parameter values, which likely reflect that only 40 simulations exist with fixed parameter settings (25 trees each). This makes the task closer to within-simulation regression or between-simulation classification. The paper should discuss to what extent models are inferring simulation identity (possibly via features like padding fraction, tree size, or other artifacts) rather than learning smooth dependence on cosmological parameters.

12) Minor internal inconsistencies
   - Section 2.3.2 says the GraphSAGE encoder uses three layers; Section 3.1 says two SAGEConv layers were used. Such inconsistencies complicate replication and hamper clarity about what was actually trained and evaluated.

Specific engagement with figures:
- Figure 2: supports the claim that learned embeddings encode substructure size; however, no quantitative link is given between these clusters and downstream parameter sensitivity.
- Figure 3: used to argue Core 2 “has larger leverage,” but as noted, core magnitudes are not gauge-invariant, so this interpretation is shaky.
- Figures 4–5: show QITT consistently beating flattened features for σ8 and often for Ωm, but also that B1_Aggregate_LinearRegression dominates Ωm. This weakens the claimed advantage of fine-grained substructures for Ωm.
- Figures 10–11: predicted-vs-true plots reveal discrete target levels and broader spread for σ8, reinforcing that the evaluation design should carefully control for simulation clustering.

## Potentially Missing Related Work
1) Denario-0 et al., “Hierarchical Contrastive Graph Representation Learning for Cosmological Merger Trees and Parameter Inference,” 2025 — directly learns 64-d merger-tree embeddings for Ωm/σ8 without TT compression. Should be compared in Section 2 (related methods) and added as a baseline alongside B4 in Section 3.3 to decouple the benefits of QITT from purely neural embeddings.

2) Denario-0 et al., “Contrastive Learning of Merger Tree Embeddings for Likelihood-Free Cosmological Inference,” 2025 — uses learned summaries within SNPE for Ωm/σ8. Discuss in Section 2 and compare conceptually to the regression setting; cite when positioning QITT vs. likelihood-free pipelines.

3) Denario-0 et al., “Parameterized Manifold Learning and Sparse Tensor Train Regression for Cosmological Parameter Inference from Merger Trees,” 2025 — combines parameter-conditioned manifolds with sparse TT regression; highly relevant to the design choices in Sections 2.5–3.2. Add discussion and, if feasible, a sparse-TT ablation.

4) Denario-0 et al., “Cosmological Parameter Inference from Merger Trees Using Hierarchical Quantum Tensor Networks,” 2025 — tree tensor networks vs. flat TT; compare in Section 4 as an alternative quantum-inspired representation with differing inductive bias.

5) Denario-0 et al., “Cosmological Parameter Inference from Filtered Merger Tree Motifs via Quantum Tensor Train Decomposition,” 2025 — motif-focused TT features. Discuss in Section 2.7 as another substructure-centric, TT-based approach.

6) Denario-0 et al., “QTT-Based Compression of Merger Tree Trajectories for Assembly Bias Studies: A Proof-of-Concept,” 2025 — Q(T)T compression of trajectories; compare in Section 3.2 to clarify tensorization alternatives and implementation specifics.

7) Denario-0 et al., “QTT-Informed Subgraph Feature Engineering for Merger Tree Regression: A Proof-of-Concept,” 2025 — localized QTT on k-hop neighborhoods; relate in Section 2.3/2.4 as a different granularity of TT-driven feature engineering.

8) Denario-0 et al., “Predicting Halo Assembly Bias from Merger Trees using Graph Neural Networks with Formation Time Regularization,” 2025 — strong GNN baselines on merger trees; cite in Section 2.3 as relevant architecture/training references for the embedding stage.

9) Leisher et al., “Linking Warm Dark Matter to Merger Tree Histories via Deep Learning Networks,” 2025 — demonstrates cosmology-from-merger-trees using GNNs; include in Section 1–2 for broader context and as a baseline type to benchmark against.

10) Chuang et al., “Leaving No Branches Behind: Predicting Baryonic Properties of Galaxies from Merger Trees,” 2024 — mature end-to-end GNNs on merger trees; cite in Section 2.3 to motivate more comprehensive GNN ablations and training protocols.

## Comments Suggestions And Typos
Actionable suggestions:
- Clarify tensorization once and for all. If the experiments used (60, 2, 37) with ranks (1, 2, 2, 1), remove or reconcile the 6-mode description in Section 2.5.1; detail implementation (library, truncation tolerances, initialization, gauge normalization if any).
- Fix the “10 physical features” discrepancy. Provide an explicit table enumerating the fields and their exact count. If 12 features are used, update all dimensions consistently and revise the (60, 74) statement accordingly.
- Rework the substructure thresholding and truncation design:
  - Justify the percentile choice with sensitivity analysis.
  - Replace hard truncation with either variable-length TT on ragged tensors or hierarchical pooling that avoids discarding substructures.
  - Use padding that is truly neutral (e.g., zeros only), and mask padded positions so downstream models cannot exploit padding fraction.
- Strengthen baselines and ablations:
  - Add PCA+Linear and PCA+XGBoost on both 4440-d and 600-d spaces.
  - Compare QITT to ridge/lasso on the 4440-d features to test whether linear shrinkage explains most gains.
  - Ablate the GraphSAGE step (physical-only vs. topology-only vs. both) under identical QITT ranks.
- Redo significance testing with simulation-level aggregation or mixed-effects to honor the clustered test design.
- Provide a table of numeric results with seeds, 95% CIs, and hyperparameters for all models, plus a table that lists the final TT ranks and resulting feature sizes.
- Explicitly confirm that GNN pretraining excludes graphs from test simulations. If not, retrain with strict split and report the delta.
- Discuss the discrete nature of target parameters and assess whether the models infer simulation identity; a control is to randomize non-physical identifiers and verify no performance change.

Minor typos/clarifications:
- Section 2.3.2: “three GraphSAGE layers” vs. Section 3.1: “Two SAGEConv layers.” Make consistent.
- Section 3.1: the average and median numbers for substructures and halos could be summarized in a small table for clarity.
- Figure captions for feature-importance plots (Figures 6–9) should note whether importances are gain-, split-, or permutation-based.
- In Section 3.2, explicitly state the TT algorithm variant (e.g., TT-SVD, ALS, TCI) and stopping criteria.

Criteria that could change my score:
- If the paper were redirected to a suitable venue (astro/ML or general ML) and the methodological issues above were addressed with stronger ablations and corrected statistics, I would likely raise to “Conference” at that venue. For ACL, even with fixes, scope remains the gating factor.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Interesting pipeline, but key methodological ambiguities (tensorization inconsistency, feature-count mismatch), potential leakage, and weak statistical treatment reduce confidence.

## Excitement
1.5 Slightly below potentially interesting.: Technically creative, but outside ACL scope; excitement here is limited for the ACL audience.

## Overall Assessment
1 Do not resubmit: This paper is so flawed that it has to be fully redone, or it is not relevant to the ACL community (e.g., it is in no way related to computational processing of language).
Justification: The work is clearly outside ACL’s topical scope. Methodologically, there are several substantive issues to resolve before evaluation in an appropriate venue (tensorization inconsistency, feature-count mismatch, padding/leakage risks, clustered significance testing, and missing PCA/regularization baselines). Despite interesting ideas and supportive figures, its current form and domain focus make it unsuitable for ACL.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper briefly notes that aggregate features outperform QITT for Ωm and that σ8 is harder to predict, but a dedicated limitations section is missing. Given this is purely simulation-based cosmology work with no human data, the direct societal impact is limited. However, clearer discussion of generalization beyond the 40 simulations, robustness to simulation systematics, and risks of shortcut learning (e.g., padding fraction, simulation identity) would improve transparency.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Some details are provided and code is implied, but internal inconsistencies (tensorization, feature counts, GNN architecture) and lack of numeric result tables hinder exact replication.

## Datasets
1 No usable datasets submitted. (The work relies on existing simulations; no new dataset contribution is claimed.)

## Software
3 Potentially useful.: If released and cleaned up, the QITT+GNN pipeline could be useful to the astro-ML community, but ambiguities need resolution before it is reliably reusable.