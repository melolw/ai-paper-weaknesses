# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies whether gradient-based data selection can mitigate capability degradation during continual pre-training on low-quality social media content. It proposes Orthogonal Junk, which: (i) computes an “anchor” gradient from a small mixture of GSM8K, MMLU, and Alpaca examples; (ii) scores candidate junk tweets by the absolute cosine similarity to the anchor and prefers near-orthogonal gradients; and (iii) samples from the top half of the pool with temperature to trade off selection quality and data diversity. Experiments on Llama‑3.2‑1B‑Instruct with ~1.22M tokens report modest RULER gains over random selection but worse ARC‑Challenge performance; a simple perplexity filter outperforms on RULER. Analysis ties a large part of the reasoning drop to data repetition in small selected pools, questioning the value of head-layer gradient orthogonality as a proxy for capability preservation.

## Summary Of Strengths
- Conceptual clarity and self-contained hypothesis. Section 2 motivates the orthogonality criterion via the first-order inner-product analysis in Equation 3 and turns it into a practical selection score in Equation 5.
- Concrete pipeline with a reasonably clear diagram. Figure 1 helps readers understand the anchor construction, per-sample gradient scoring, and pool-weighted sampling stages.
- Honest and useful negative findings. Table 1 shows that a perplexity filter exceeds the proposed method on RULER, and the paper traces much of the ARC drop to data repetition rather than selection quality. The optimization trace in Figure 2 and Table 3 is a refreshingly candid analysis of a confound that many selection papers gloss over.
- Subtask-level breakdown. Table 2 makes it clear where orthogonality helps a bit (Variable Tracking) and where it hurts, giving practitioners a sense of where any benefits might lie.
- Relevance to the community. The brain-rot continual pretraining setting and data selection for stability are both timely and aligned with ACL interests in data-centric and robust training of LLMs.

## Summary Of Weaknesses
1) Anchor design appears severely under-justified and too small. Section 2.3 uses only 400 items across GSM8K, MMLU, and Alpaca to estimate a single anchor gradient, and computes it over only the embedding and LM head (21.25% of parameters). There is no sensitivity study to anchor size, composition, or layer choice. Since the main conclusion is that head-level orthogonality may not capture preservation dynamics, ablations are essential to rule out that the failure is an artifact of a small, noisy anchor or of ignoring middle and attention layers.

2) Limited scale and single-model scope. All results are on a 1B model and ~1.22M tokens. The original “brain rot” paper cited uses 8B. Without at least a second model size or a second token budget, it is hard to assess whether the reported effects are robust or scale-specific. Claims like “long-context understanding is more vulnerable than reasoning” (Section 3.2) may not generalize.

3) Missing comparisons to closely related gradient‑based selection approaches. The Related Work cites classical CL and some selection methods, but the experiments do not compare to gradient-aware selection baselines that are methodologically adjacent, such as gradient-influence or other normalization-aware strategies. This weakens the central claim that “gradient orthogonality” is a poor proxy; perhaps a better gradient statistic would work.

4) Statistical rigor and variance reporting are missing. The paper appears to report single runs. ARC‑Challenge CoT decoding uses sampling (temperature 0.6, top‑p 0.9) which can introduce run-to-run variance. There are no confidence intervals or seed sweeps. The observed deltas in Table 1 are not accompanied by uncertainty, which is particularly important because several differences are in the low single digits.

5) Evaluation scope for “capability preservation” is narrow. Only ARC‑Challenge and RULER are used, and the instruction-tuned setting relies solely on Alpaca 5K. Since the method’s goal is broadly “capability-preserving selection,” the benchmark coverage is thin. It would help to include at least a couple of reasoning/math datasets beyond ARC, and a knowledge benchmark that is not already used in the anchor.

6) Confound handling is incomplete beyond repetition. The paper thoughtfully diagnoses repetition as a culprit, but other confounds remain unexamined: length distribution shifts due to selecting short tweets, packing strategies, and per-token gradient scaling. The influence of sequence length and packing is known to bias gradient-based criteria; not accounting for this undermines conclusions about the orthogonality heuristic itself.

7) Optimization and cost accounting are unclear. The method requires per-sample gradients on the candidate corpus. There is no concrete measurement of compute overhead relative to perplexity filtering, no wall-clock cost, and no discussion of batching, microbatch size, or caching for gradient computation. Absent cost-benefit analysis, it is difficult to justify the additional complexity, particularly since the perplexity baseline performs better on RULER.

8) Orthogonality score details and design choices lack ablations. Equation 5 uses absolute cosine similarity, effectively collapsing positive and negative alignment. This choice may discard useful information about helpful transfer (positive inner products) versus harmful interference (negative). No comparison is shown between signed vs absolute cosine, top‑k cutoffs vs temperature, temperature T values, or pool size (top‑x%). Table 3 varies only the pool and weighting at a coarse level.

9) The anchor and target-task entanglement is not probed. The anchor mixes GSM8K, MMLU, and Alpaca, but the evaluation is mostly ARC and RULER, which only partially overlap with these distributions. It would be important to test anchors matched to RULER-like tasks or to ARC-like tasks separately to see whether task-aligned anchors fare better, and to test whether multiple anchors or layer‑wise anchors help.

10) Limited interpretability into why Variable Tracking improved. Table 2 shows a +9.2pp Variable Tracking gain over Junk‑Random, an interesting outlier. The paper attributes this loosely to preserving sequential reasoning, but does not analyze anchor gradients or token‑level patterns. Without analysis, it is hard to draw insight from the one bright spot.

Figure- and table-specific comments:
- Figure 1 supports the exposition well, but it also reveals a potential blind spot: all gradient arrows g_i are drawn at the head space, which tacitly encodes the main limitation the paper later suspects. This should prompt an ablation with deeper layers.
- Table 1 is central to the conclusions. It demonstrates that Orth Junk improves RULER by +2.89pp over Junk-Random but drops ARC by −5.12pp, while Perplexity achieves +10.94pp on RULER. These numbers do not justify the added complexity of gradient scoring as presented.
- Table 2 shows Orth Junk trailing Perplexity on most NIAH subtasks, especially MK3 (3.6% vs 23.4%). This contradicts the notion that gradient orthogonality preserves non-interfering skills in retrieval-heavy settings. The only relative win is Variable Tracking (44.8%).
- Table 3 and Figure 2 make a compelling case that repetition hurts ARC more than it affects RULER. However, because RULER slightly decreases as repetition drops (60.72 → 54.66), this suggests more nuanced trade-offs; the paper does not investigate why diversity fails to help long-context tasks.

## Potentially Missing Related Work
1) Liu et al., “Learn More, Forget Less: A Gradient-Aware Data Selection Approach for LLM,” 2025 — Presents GrADS, a gradient-aware selection method to choose informative subsets while mitigating forgetting. It is methodologically close and should be discussed in Section 4 and compared as a baseline in Section 3, ideally added alongside Perplexity in Table 1.

2) Wang et al., “Dynamic data selection with normalized gradient-based influence approximation for targeted fine-tuning of LLMs,” 2025 — Analyzes length bias in gradient selection and proposes normalized influence. Highly relevant to the short‑tweet regime here and to the repetition/length confounds. Discuss in Section 3.4 and add to Section 4 with commentary on Equation 5’s sensitivity to magnitude and length; consider an ablation replacing Equation 5 with a normalized criterion.

3) Wang et al., “ClusterUCB: Efficient Gradient-Based Data Selection for Targeted Fine-Tuning of LLMs,” 2025 — Offers scalable gradient-based selection via clustering and bandits. Compare computational cost and selection quality in Section 3.1/3.2 and cite in Section 4.

4) Chen et al., “Influence-Preserving Proxies for Gradient-Based Data Selection in LLM Fine-tuning,” 2026 — Proposes low-rank proxy models to approximate gradient influence. Relevant for scaling beyond 1B and reducing cost of Stage 2. Cite in Section 4 and discuss as a practical extension after Equation 4.

5) Wang et al., “Two-Stage Optimizer-Aware Online Data Selection for Large Language Models,” 2026 — Models how optimizers shape update geometry and adapts selection online. Discuss in Section 2.2 as an alternative to static filtering and in Section 4 as related perspective on shaping g_new in Equation 3.

6) Zhao et al., “Beyond Similarity: A Gradient-based Graph Method for Instruction Tuning Data Selection,” 2025 — Encodes gradient geometry in graphs, going beyond cosine. Discuss after Equation 5 as a richer representation than absolute cosine; consider as an alternative scoring baseline.

7) Moroni et al., “What we Learned from Continually Training Minerva: a Case Study on Italian,” 2025 — Provides a well-controlled continual pretraining study. Use in Section 3.1 to justify or contrast evaluation setup and in Section 4 for broader context of CPT design choices.

8) Fars et al., “Token-Balanced Continual Pretraining Eliminates Brain Rot Degradation,” 2026 — Investigates token-level gradient imbalance and sequence packing as main drivers of degradation, offering a mitigation complementary to this work’s selection idea. Discuss in Section 3.4 as an alternative explanation and in Section 4; consider adding a token-balanced packing control to Table 1.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Anchor ablations. Please add experiments varying: (a) anchor size (e.g., 400 → 4k), (b) anchor composition (GSM8K-only, MMLU-only, Alpaca-only, and task‑aligned anchors for RULER vs ARC), and (c) layer scopes (head‑only vs middle vs all layers). This directly tests whether the core conclusion is an artifact of a weak anchor or of restricting gradients to the head.
- Scoring ablations. Compare signed vs absolute cosine in Equation 5, test different pool sizes (e.g., top‑20/35/50/80%), and sweep temperature T. Include a “no filter, score-weighted sampling” control at matched diversity to decouple orthogonality from repetition more cleanly.
- Normalization and length effects. Incorporate a gradient normalization or influence-approximation baseline to mitigate per-token length bias and report how this changes Table 1 and 2. Also report average length distributions of selected pools.
- Statistical rigor. Run at least 3 seeds for ARC CoT, fix the decoding stochasticity, and report mean ± std. For RULER, report bootstrap confidence intervals. If compute is tight, concentrate on the two most informative configurations and justify choices.
- Cost-benefit analysis. Report wall-clock time and GPU-hours for computing g_ref and per-sample gradients, and compare to perplexity filtering. Without this, readers cannot judge whether +2.89pp on RULER justifies the overhead.
- Packing and repetition controls. Since repetition is central in Figure 2 and Table 3, add a token-balanced packing baseline and a “matched repetition” control for Perplexity and Orth Junk to equalize repetition across methods.

Typos and minor issues:
- Page 1: “Experiments on Llama-3.2-1B-Instruct reveal mixed results” — later you write “Llama‑3.2‑1B.” Keep naming consistent.
- Table 1 caption: clarify that “Δ” is relative to Junk‑Random SFT, not Base.
- Section 3.1 “All conditions use matched token budgets of approximately 1.22M tokens.” Table 3 shows varying unique sample counts; explicitly state whether total tokens and packing policies are indeed matched across variants.
- Section 3.2, last paragraph: “Both filtered methods underperform the unfiltered Junk-Random baseline on ARC” — Table 1 shows Orth Junk (23.21) < Junk‑Random (28.33), Perplexity (21.76) < Junk‑Random. This is correct but add a short rationale about potential overspecialization from subset filtering.
- Figures: Add font sizes or labels for axes in Figure 2 for clarity in the camera-ready.

Criteria that could increase my score:
- A thorough set of anchor and scoring ablations showing that the negative result is robust to reasonable design choices, plus at least one comparison to a modern gradient-aware selection baseline (e.g., a normalized influence method). 
- Multi-seed statistics and a second model size or larger token budget to reduce the risk of scale-specific conclusions.
- A compute/efficiency analysis that contextualizes the gains relative to cost and shows a practical regime where Orth Junk is preferable to perplexity filtering or to a token-balanced packing control.

## Confidence
4: Quite sure after careful checking — I checked the important points and figures/tables carefully; unlikely that I missed something that would reverse my assessment.

## Soundness
2.5: Between Poor and Acceptable — The idea is clear and analysis of repetition is insightful, but the experimental validation is thin (no multi-seed, no strong baselines beyond perplexity, limited ablations), and conclusions about orthogonality are not yet well-isolated from implementation choices.

## Excitement
2.0: Potentially Interesting — The negative result and the repetition analysis are useful to practitioners, but the current method underperforms a simple baseline and lacks breadth to be exciting.

## Overall Assessment
2.5 Borderline Findings: The paper offers a clear formulation and a candid, useful negative result with concrete evidence in Tables 1–3 and Figures 1–2, but lacks essential ablations, broader baselines, variance analysis, and cost accounting. In its current form it is better suited for Findings than the main track. With stronger ablations, normalized gradient baselines, multi-seed reporting, and a second scale, it could move toward a main-track contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges that it operates on engagement-optimized social media content. Additional limitations worth stating explicitly:
- The method may inadvertently encode biases from the anchor datasets, which are English-centric and contain their own biases, thereby shaping selection in potentially skewed ways.
- RULER and ARC may not reflect safety-relevant capabilities; preserving scores on these does not guarantee harmlessness.
- Gradient computation over user-generated content could surface sensitive text in logs or caches; discuss data handling and privacy if releasing code and pipelines.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible — The setup is described, and code is said to be available; however, missing multi-seed protocols, partial details on packing, and lack of compute accounting and exact decoding templates for ARC reduce reproducibility.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If the selection and scoring code is available as claimed, it can help others reproduce the negative result and build stronger baselines.