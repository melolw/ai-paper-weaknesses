# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper tackles cross-task generalization for LLMs by composing previously trained LoRA modules rather than fine-tuning on novel tasks. Building on LoraHub, it proposes two changes: (1) task selection via semantic similarity between target samples and the training data of candidate LoRA modules, and (2) instance-level composition, where each test instance is matched to a tailored set of LoRAs and weights are optimized using a gradient-free method. Experiments use Flan-T5-Large and a library of LoRAs trained on subsets of FLANv2, evaluating on 27 BBH tasks. The method improves over LoraHub in 16/27 tasks and slightly improves average accuracy compared to task-level composition.

## Summary Of Strengths
- Problem relevance: Cross-task generalization without per-task fine-tuning is an important and timely direction for efficient NLP.
- Clear intuition and pipeline: Figure 1 effectively contrasts task-level versus instance-level composition, making the core idea easy to grasp. The overall retrieval–selection–composition flow aligns well with recent modular LoRA literature.
- Empirical coverage: Evaluation across 27 BBH tasks is nontrivial for this setting. The paper includes per-task breakdowns (Table 4), A/B win–loss statistics against several baselines (Table 2), and retrieval ablations (Table 3).
- Practicality: Using a compact sentence encoder for similarity and a black-box optimizer to set weights reduces engineering friction relative to full fine-tuning or heavy backprop updates for every new task.
- Instance-level benefit: The ablation shows a consistent albeit modest gain from instance-level composition over task-level BatchComp (Table 1; +0.9 points on average), and salient cases like “disambiguation qa” demonstrate sizable improvements, suggesting the approach can capitalize on instance-specific cues.

## Summary Of Weaknesses
1) Underspecified optimization and composition details limit reproducibility and interpretability.
- Section 3.3 and Equation (2) present ng(·) as a black-box gradient-free optimizer (citing Sun et al., 2022) but do not state the objective being optimized, the search space, constraints, or the scale of parameters. Are weights nonnegative, sum-to-one, or unconstrained? Are weights global per LoRA or layer-wise? How are multi-layer adapters handled during merging? Without these, independent reproduction is difficult and it is unclear why 40 global steps suffice (Section 4).
- It is also unclear whether weight optimization uses only the 5 sampled instances per task, a held-out subset, or any BBH dev splits. Using test data for weight tuning would inflate results, yet the paper says “we sampled 5 instances per task… followed by EM-based evaluation on the remaining data” without clarifying whether those 5 are exclusively for selecting/optimizing and the rest are purely held out.

2) Evaluation framing and metrics contain ambiguities and potential cherry-picking.
- Table 1 reports “average-3” that excludes the three lowest-performing tasks (<10% accuracy). This nonstandard post-hoc reporting inflates perception of gains and should be de-emphasized or justified with a principled rationale. BBH tasks are notoriously heterogeneous; excluding “hard” tasks may bias conclusions.
- “EM-based evaluation” (Section 4) is not defined. Most BBH tasks use accuracy; a few require task-specific scoring. The paper should state for each task whether accuracy or exact match is used, and how free-form generations are normalized.
- No statistical significance tests, confidence intervals, or variance across seeds are reported for the proposed method, while LoraHub is averaged over three runs. Given the paper’s critique of LoraHub’s instability under random selection, not reporting variance for the proposed method weakens claims of improved stability.

3) Modest average gains and mixed per-task results raise questions about practical impact.
- In Table 1, the average improvement over LoraHubavg is +1.6 points (35.6 vs. 34.0), while the improvement over BatchComp is +0.9. These are small in the context of BBH variation. Table 4 shows that the method loses to LoraHub or BatchComp on several tasks, including some where retrieval-based alignment should help (e.g., “penguins in a table”: 40.4 for BatchComp vs. 36.9 for Ours; “reasoning about colored objects”: 42.0 for BatchComp vs. 38.0 for Ours).
- Full fine-tuning still dominates for many structured tasks (Section 5.1), which is acknowledged but underscores limited headroom of the proposed approach.

4) Retrieval setup and embeddings are inconsistently described.
- Section 4 states using all_datasets_v4_MiniLM-L6 as Ms, then Section 2 and Table 3 discuss DPR and DPR metrics (L2 vs. cosine). It is unclear whether the main results in Table 1 use MiniLM, DPR, or both. Section 3.2 also references DPR-style retrieval and cosine similarity, but equations and implementation details do not specify the encoder used in the main experiments.
- The paper averages x+y to produce task embeddings (Section 3.2). Concatenation vs. addition vs. special separators can matter for sentence encoders; using “x+y” without token-level detail is ambiguous. It is also unclear how many examples per upstream task are used when computing emb_Ti beyond “the training set.”

5) Potential data leakage via access to LoRA training data is not addressed.
- The method explicitly requires access to the training data of each LoRA to compute task centroids (Limitations mentions this). While BBH is unseen, it remains important to discuss whether any overlap exists between FLANv2 subsets used by the LoRA library and BBH, and whether overlapping instructions/templates could bias similarity retrieval. A principled check or at least a clear statement about overlap and controls would strengthen validity.

6) Composition mechanics and constraints are not experimentally explored.
- There is no ablation on the number of selected LoRAs N beyond the fixed N=20 used. How does performance vary with N? Is there diminishing return or instability for large N?
- No analysis of per-layer vs. global weights, or the effect of constraining weights (e.g., simplex constraints). Without such ablations, the paper’s core mechanism remains a design choice rather than an evidenced best practice.

7) Fairness of comparisons and compute budget parity need clarification.
- LoraHubavg is tuned for 40 steps and averaged over three runs; the proposed method’s variability and compute footprint are not equivalently reported. Section 7 concedes higher compute for instance-level optimization, but the main text does not quantify the overhead relative to LoraHub. Given the small average gains, a cost–benefit analysis is necessary.

8) Writing and notation issues hinder clarity.
- Several typos and unclear expressions appear in Sections 3.2–3.3 (e.g., “donated as Ii” for “denoted,” mixing e and ej, and x vs. xj), and multiple grammatical issues across the paper. Equation references are minimal; for example, Equation (1) is central but not linked back to reported retrieval settings in Table 3.

9) Figure-level detail is conceptual but omits important operational specifics.
- Figure 1 clearly illustrates the conceptual difference between task-level and instance-level composition, yet it does not depict how weights are learned or applied across layers, nor how retrieval interacts with per-instance LoRA selection quantitatively. A second figure that diagrams the optimization flow or weight application at the module and layer levels would improve technical transparency.

10) Missing positioning relative to several directly relevant recent works on dynamic and instance-wise LoRA composition and merging.
- The Related Work section omits closely related methods on dynamic adapter selection/merging, continual merging, and geometric analyses of LoRA spaces (see “Potentially Missing Related Work”).

Why these weaknesses matter: Together they make it hard to (a) verify the claimed stability and efficiency advantages, (b) reproduce the central optimization procedure, and (c) assess how broadly the approach transfers. The small average gains over strong baselines, combined with overhead and unclear evaluation protocol, reduce confidence in the practical significance for the main conference track.

## Potentially Missing Related Work
1) Lee et al., “LoRA on the Go: Instance-level Dynamic LoRA Selection and Merging,” 2026 — Proposes training-free, instance-level adapter selection and merging using activation signals. Directly relevant to Section 3.3’s instance-specific composition; should be discussed in Related Work and compared conceptually to the proposed similarity-based retrieval and gradient-free weighting.

2) Wu et al., “Convolutional LoRA Aggregation for Unseen Tasks Adaptation,” 2025 — Aggregates LoRAs via clustering and convolutional fusion for unseen tasks, targeting the same adaptation goal with a different fusion mechanism. Add to Section 2 and discuss trade-offs with instance-level selection; consider as a baseline if feasible.

3) He et al., “Compress then Merge: From Multiple LoRAs into One Low-Rank Adapter,” 2026 — Merges many LoRAs into one rank‑r adapter. Relevant to efficiency and storage considerations raised in Section 7; include in Related Work and discuss when single consolidated adapters might outperform per-instance routing.

4) Shenaj et al., “K-Merge: Online Continual Merging of Adapters for On-device Large Language Models,” 2026 — Focuses on online merging under storage constraints; relevant for long-term deployment scenarios alluded to in Section 7. Add to Related Work and contrast with the proposed per-instance on-the-fly optimization.

5) Liao et al., “Dynamic Adaptation of LoRA Fine-Tuning for Efficient and Task-Specific Optimization of Large Language Models,” 2025 — Adapts LoRA capacity across layers dynamically. Useful context for Section 3’s design choice of fixed-rank, fixed-placement LoRAs; compare adaptive placement vs. composition of multiple fixed LoRAs.

6) Xin et al., “Beyond Full Fine-tuning: Harnessing the Power of LoRA for Multi-Task Instruction Tuning,” 2024 — Systematic study of LoRA under multi-task regimes with insights into cross-task generalization. Should inform the positioning in Section 2 and motivate stronger multi-task baselines beyond LoraHub and ICL.

7) Lu et al., “On the Representation Geometry of LoRA Model Merging,” 2026 — Provides geometric perspective and training-free merging using SVD/CUR. Relevant for understanding and possibly improving the merging step in Section 3.3; cite near Equation (2) and discuss potential to replace or augment ng(·).

## Comments Suggestions And Typos
Actionable questions and suggestions (responses could raise my score):
1) Specify the optimization objective and constraints for ng(·).
- What is the loss minimized when learning weights for an instance? Is it cross-entropy on the 5 sampled instances, likelihood on a validation split, or task-specific metrics? Are there regularizers or sparsity constraints?
- Are LoRA weights per-module scalar coefficients broadcast to all layers in that adapter, or per-layer coefficients? Are weights constrained to [0,1] and/or sum to 1? Please include pseudocode, and add a diagram showing how weights are applied across layers and modules.
- Report sensitivity to the number of optimization steps and initializations; include variance over multiple seeds.

2) Clarify retrieval and embeddings.
- For the main results (Table 1 and Table 4), which encoder is used to compute emb_ej and emb_Ti? MiniLM or DPR? If MiniLM is used, why is Table 3 titled “DPR” cosine/L2? If DPR is used, how is it trained? Please unify terminology, report encoder hyperparameters, and detail input formatting for “x+y” (e.g., special separator tokens).
- Quantify how many examples per upstream task are used for computing emb_Ti (all training data or a sample?). Does using only instructions vs. full (x,y) change results?

3) Ensure evaluation protocol is unambiguous and fair.
- Define “EM-based evaluation” exactly for each BBH subtask. Provide normalization (lowercasing, punctuation stripping) if you use EM on free text.
- Confirm that the 5 instances per task are used solely for selecting/optimizing weights and not for evaluation. Report multiple random splits and average results with standard deviations for your method, as done for LoraHubavg.
- Remove or justify “average-3.” If kept, treat it as auxiliary, not the main headline.

4) Expand ablations and efficiency analysis.
- Vary N (e.g., 5, 10, 20, 40) to show composition sensitivity. Report runtime and memory overhead vs. LoraHub and ICL. Show win–loss–tie vs. baselines under matched compute.
- Explore weight constraints (simplex, nonnegativity), sparsity-inducing penalties, and per-layer vs. global weights. Include an ablation showing the effect of these choices on stability and accuracy.

5) Strengthen figure- and table-level exposition.
- Figure 1 is helpful conceptually; add a second figure detailing the end-to-end instance-level pipeline with weight learning, including where retrieval is used and how the selected adapters are merged into the base model at inference.
- In Table 4, mark significant wins/losses, and add per-task metrics used. For Tables 1–3, add standard deviations over seeds for your method.

Typos and clarity issues (non-exhaustive):
- Section 3.3: “donated as Ii” should be “denoted as Ii”; “Having aggregated the adjusted weights for all e” → for all ej.
- In Section 3.2, “Following the approach of Mussmann and Ermon, 2016 and Karpukhin et al., 2020b” — ensure consistent citation formatting.
- Use consistent notation for inputs x, instances ej=(xej, yej), and queries Q; currently x, xj, and Q are mixed.

Criteria to increase my score:
- Provide full optimization details for Equation (2) with constraints and pseudocode; show multiple-seed averages and significance tests for your method; clarify retrieval encoders and input formatting; add ablations on N and weight constraints; replace “average-3” with standard reporting; and include a compute/overhead comparison.

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and checked figures/tables, but missing implementation details and possible ambiguities in the evaluation reduce certainty about exact replication.

## Soundness
3: Acceptable — Main claims are supported at a high level, but the optimization and evaluation details are underspecified, and analysis of stability/compute is incomplete.

## Excitement
2.5: Between potentially interesting and interesting — The instance-level idea is appealing and Figure 1 is compelling conceptually, but modest average gains and gaps in clarity temper enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The instance-level composition idea is relevant and reasonably validated across BBH with informative tables (e.g., Table 1, Table 4). However, underspecified optimization details, ambiguous retrieval setup, lack of statistical rigor and compute analysis, and reliance on “average-3” detract from the strength and clarity of the empirical story. With fuller methodology disclosure, cleaner evaluation, stronger ablations, and clearer positioning against closely related adapter-merging/selection work, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section is appreciated and candid about computational overhead and reliance on LoRA training data. Additional points to discuss: 
- Potential data overlap risks between upstream datasets used for LoRA training and downstream test instances, and mitigation strategies.
- Risks of biased retrieval if embeddings reflect societal biases in training corpora, which could route instances to suboptimal or biased adapters. A brief bias analysis or mention of auditing steps would be helpful.
- Practical deployment considerations where storing training data for all LoRAs is not feasible; discuss privacy or governance constraints.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — High-level steps are present and tables are comprehensive, but critical details of ng(·), constraints, validation splits, and encoder formatting are missing. Public code would help.

## Datasets
1: No usable datasets submitted. No new dataset contribution.

## Software
3: Potentially useful. If the promised code is complete and documents the optimizer, retrieval, and merging pipeline, it could be a helpful reference; otherwise impact is limited.