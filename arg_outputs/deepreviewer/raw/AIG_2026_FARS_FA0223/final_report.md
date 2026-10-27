## Summary
This paper proposes Delta SVD-EQ, a post-hoc spectral intervention for reducing catastrophic forgetting in sequential LoRA continual learning. The method equalizes the singular values of task-specific LoRA deltas at each task boundary while preserving the Frobenius norm, redistributing spectral energy uniformly across rank components. Evaluated on the FOREVER benchmark with Qwen3-0.6B, SVD-EQ achieves a +2.3pp improvement in backward transfer (15% relative reduction in forgetting) with marginal statistical significance (p=0.059). The most consistent finding is a 3–10× reduction in within-order variance, suggesting that SVD-EQ acts as a regularizer that stabilizes continual learning outcomes across random seeds. Ablation studies indicate that both norm shrinkage and spectral redistribution contribute to the observed effect, though the dominant mechanism remains partially understood. The paper is well-structured and presents a clean, reproducible method, but the novelty positioning is weakened by related post-hoc spectral methods, the evaluation scope is narrow (single benchmark, single model, limited runs), and key claims about uniqueness require qualification.

## Strengths
1. **Clean, reproducible method design:** Delta SVD-EQ is a simple, well-defined post-hoc intervention that can be applied to existing LoRA checkpoints without retraining. The method is transparent, norm-preserving, and computationally lightweight, making it practical for real-world deployment.

2. **Variance reduction finding:** The 3–10× reduction in within-order standard deviation is a compelling and practically significant result. Stabilizing continual learning outcomes across random seeds is a valuable contribution that is underemphasized in much of the CL literature.

3. **Honest limitation acknowledgment:** The authors explicitly state that improvement is order-dependent, statistical significance is marginal, and the mechanism is partially understood. This transparency improves the paper's credibility.

4. **Ablation study design:** The inclusion of mean-smoothing and random-spectrum ablations is thoughtful and provides meaningful insight into the mechanisms at play, even though the findings complicate the narrative.

5. **Self-contained evaluation:** The FOREVER benchmark with Qwen3-0.6B provides a clear, reproducible experimental setup. The reporting of OP, BWT, per-order breakdown, and statistical tests is comprehensive for the scope.

## Weaknesses
**W1 (Major) — Unsupported uniqueness claim.** The abstract and conclusion state that "SVD-EQ is the only continual learning method that is simultaneously training-free, memory-free, and post-hoc applicable." This is contradicted by retrieved literature: Spectral Surgery (Tian et al., 2026) performs training-free SVD-based singular value reweighting of LoRA adapters; PARA (Kumaravelu et al., 2026) applies data-free post-hoc SVD-based rank pruning; DESIRE (Guo et al., 2024) is a rehearsal-free LoRA CL method with post-processing modules. These methods also satisfy the "training-free" and "post-hoc" properties. The claim requires qualification.

**W2 (Major) — Missing critical related work.** The paper omits Spectral Surgery (Tian et al., 2026, arXiv:2603.03995), which is methodologically very close to SVD-EQ: it decomposes LoRA updates via SVD and reweights singular values post-hoc without retraining. This omission weakens the novelty claim and leaves a significant gap in the related work section.

**W3 (Major) — Narrow evaluation scope.** The evaluation uses only one benchmark (FOREVER with 4 text classification tasks), one model (Qwen3-0.6B), and only 9 total runs (3 orders × 3 seeds). No comparison with related post-hoc methods (EBLoRA, Spectral Surgery, DESIRE, P\&M) is included. This limits the generalizability of the findings and makes the marginal statistical significance (p=0.059) more concerning.

**W4 (Major) — Mechanism ambiguity undermines core motivation.** The paper is motivated by the hypothesis that spectral concentration amplifies cross-task interference. However, Section 4.5 finds no significant correlation (r=−0.027, p=0.893) between pre-equalization spectral concentration (ρ) and BWT improvement. Furthermore, the ablation study shows that mean-smoothing (which reduces the Frobenius norm by 13.3%) performs nearly identically to SVD-EQ (+2.2pp vs +2.3pp), suggesting that norm shrinkage, not spectral equalization, may be the primary mechanism. This directly contradicts the stated motivation and raises questions about what SVD-EQ actually does.

**W5 (Minor) — Contribution framing overemphasizes marginal gains.** Contribution C2 presents the +2.3pp BWT improvement as a definitive result, but this gain has marginal statistical significance and only benefits 2 of 3 task orders. The more compelling and consistent finding is the variance reduction, which should be elevated in the contribution statement.

**W6 (Minor) — Method reproducibility detail missing.** The description of how the equalized delta integrates into cumulative LoRA parameters ("updated accordingly") lacks an explicit formula, making full reproducibility uncertain.

## Key Issues
**KI1 — Novelty claim requires repositioning against Spectral Surgery and EBLoRA.**
The closest prior work is Spectral Surgery (Tian et al., 2026), which also performs post-hoc SVD decomposition and singular value reweighting of LoRA adapters without retraining. EBLoRA (Gu et al., 2026) addresses spectral imbalance in LoRA continual learning through training-time regularization. The paper must explicitly contrast SVD-EQ with these methods on at least three dimensions: (a) norm preservation vs. gradient-guided reweighting, (b) sequential CL application vs. single-task refinement, and (c) uniform equalization vs. constrained Stiefel optimization. Without this, the uniqueness claim is unsustainable.

**KI2 — Variance reduction should be the primary contribution, not mean BWT gain.**
The +2.3pp mean BWT improvement is marginally significant (p=0.059) and order-dependent (Order 6 degrades). The 3–10× variance reduction is more statistically reliable and practically significant. The contribution narrative and abstract should be restructured to lead with variance stabilization, treating the mean BWT gain as secondary.

**KI3 — Mechanism interpretation needs correction.**
The ablation shows mean-smoothing (+2.2pp) performs nearly identically to SVD-EQ (+2.3pp) despite reducing the norm by 13.3%. Combined with the null correlation between ρ and BWT improvement (r=−0.027), this suggests that norm shrinkage and implicit regularization during SVD reconstruction are the dominant mechanisms, not spectral equalization per se. The paper should reframe its mechanism discussion accordingly rather than claiming that both mechanisms contribute equally.

**KI4 — Evaluation scope is too narrow to support general claims.**
With only one benchmark, one model, and 9 runs, the paper cannot claim that SVD-EQ is broadly applicable. Adding at least one additional benchmark (e.g., task arithmetic-based CL), one larger model (e.g., Llama-3-8B), and a direct comparison with EBLoRA or Spectral Surgery is needed to establish credibility.

## Actionable Suggestions
**A1 [Must] — Qualify the uniqueness claim and add Spectral Surgery comparison.**
- Remove the absolute claim "SVD-EQ is the only continual learning method that is simultaneously training-free, memory-free, and post-hoc applicable" from both the abstract and conclusion.
- Add a paragraph in Section 2.3 discussing Spectral Surgery (Tian et al., 2026), explicitly contrasting its gradient-guided reweighting with SVD-EQ's norm-preserving uniform equalization, and noting that Spectral Surgery targets single-task refinement while SVD-EQ targets sequential CL.
- Reposition the contribution as: "SVD-EQ offers a norm-preserving, sequential spectral equalization approach that complements gradient-guided post-hoc reweighting and training-time spectral regularization methods."

**A2 [Must] — Restructure contributions to lead with variance reduction.**
- Move the variance reduction finding (3–10× within-order variance reduction) to C2 and present it as the primary empirical result.
- Move the mean BWT gain to a secondary position and explicitly note its marginal statistical significance and order-dependence.

**A3 [Must] — Reframe mechanism discussion to acknowledge norm shrinkage dominance.**
- In Section 4.4, explicitly state that the near-identical performance of mean-smoothing and SVD-EQ suggests norm shrinkage may be the dominant mechanism.
- In Section 4.5, acknowledge that the null correlation between ρ and BWT improvement weakens the spectral concentration hypothesis.
- Propose a revised mechanism narrative: "SVD-EQ may act as an implicit regularizer through SVD reconstruction, with norm shrinkage contributing to forgetting reduction regardless of initial spectral concentration."

**A4 [Must] — Add explicit update rule for cumulative LoRA parameters.**
- In Section 3.3, add one sentence with the exact formula: "The equalized delta replaces the original task-specific delta, and the cumulative LoRA parameters are updated as $B_t A_t = B_{t-1} A_{t-1} + \Delta W_t^{eq}$."

**A5 [P1] — Expand evaluation scope.**
- Add at least one additional model size (e.g., Qwen3-1.5B or Llama-3-8B) to demonstrate scalability.
- Include EBLoRA (Gu et al., 2026) as a comparison baseline in Table 1, with a note on whether it requires training-time access (which SVD-EQ does not).

**A6 [Nice-to-have] — Strengthen limitations section.**
- Expand each limitation with one sentence of concrete detail, as provided in the PDF annotation on Page 6.
- Discuss whether p=0.059 reflects genuinely weak effect size or low statistical power from N=9 runs.

## Storyline Options + Writing Outlines
### Current Storyline Diagnosis
The current narrative follows: Problem (CL + LoRA forgetting) → Gap (existing methods need training modifications) → Solution (SVD-EQ post-hoc equalization) → Evidence (BWT +2.3pp, variance reduction) → Contributions. The core weakness is that the gap statement overreaches (claims no prior post-hoc method exists), the motivation hypothesis is later falsified by the paper's own data, and the contribution ordering overemphasizes a marginal mean gain over a more compelling variance reduction finding.

### Abstract Outline (complete)
- **S1 (Problem):** "Sequential LoRA fine-tuning for large language models suffers from catastrophic forgetting, degrading performance on earlier tasks as new ones are learned."
- **S2 (Challenge/Gap):** "Existing continual learning methods require training-time modifications, replay buffers, or architectural changes, limiting their applicability to pre-trained LoRA checkpoints. While post-hoc spectral refinement methods exist for single-task LoRA adapters, their role in sequential continual learning remains unexplored."
- **S3 (Method):** "We propose Delta SVD-EQ, a post-hoc spectral intervention that equalizes the singular values of task-specific LoRA deltas at each task boundary while preserving the Frobenius norm, redistributing spectral energy uniformly across rank components."
- **S4 (Key Result):** "On the FOREVER benchmark with Qwen3-0.6B, SVD-EQ reduces within-order variance by 3–10×, stabilizing continual learning outcomes across random seeds. Mean backward transfer improves by +2.3pp (15% relative reduction) with marginal statistical significance."
- **S5 (Implication):** "Ablation studies suggest that both norm shrinkage and spectral redistribution contribute to the effect. SVD-EQ offers a lightweight, complementary direction to existing post-hoc continual learning techniques."

### Introduction Outline (complete)
- **P1 (Big Picture + Problem):** Establish CL for LLMs as a practical deployment challenge. Quantify the forgetting problem in sequential LoRA fine-tuning. State why this matters for real-world continual deployment.
- **P2 (Gap in prior work):** Survey existing CL methods (regularization, replay, architecture-based). Acknowledge that post-hoc model merging methods exist but typically assume simultaneous access to all task models. Identify the gap: sequential post-hoc intervention without training modifications.
- **P3 (Motivation + Method):** Motivate spectral equalization based on the observation that LoRA updates develop concentrated spectra. Present SVD-EQ as a post-hoc intervention. Acknowledge that the exact mechanism remains partially understood.
- **P4 (Evidence Preview):** Preview the two key findings: (a) variance reduction as the most consistent benefit, and (b) mean BWT improvement with marginal significance.
- **P5 (Contributions):** Restate contributions with variance reduction elevated to primary position, mean BWT gain as secondary, and mechanism exploration as a third point.

## Priority Revision Plan
| Priority | Action | Target Section | Effort | Expected Impact |
|----------|--------|----------------|--------|-----------------|
| P0 (Must) | Remove absolute uniqueness claim; reposition with bounded comparison to Spectral Surgery, EBLoRA, DESIRE | Abstract, Conclusion, Sec 2.3 | Low | Resolves credibility risk; prevents reviewer rejection on overclaim |
| P0 (Must) | Add Spectral Surgery (Tian et al., 2026) to Related Work with explicit differentiation | Sec 2.3 | Low | Closes critical related-work gap; strengthens novelty defense |
| P0 (Must) | Reframe contributions: lead with variance reduction, demote mean BWT gain | Abstract, Intro, Conclusion | Low | Aligns narrative with strongest empirical finding |
| P1 (Must) | Rewrite mechanism discussion: acknowledge norm shrinkage as likely dominant pathway | Sec 4.4, 4.5 | Medium | Resolves contradiction between motivation and results |
| P1 (Must) | Add explicit update rule for cumulative LoRA parameters | Sec 3.3 | Low | Improves reproducibility |
| P1 (Nice) | Expand limitations section with concrete detail on order-dependence, statistical power, mechanism | Sec 5 | Low | Improves scientific rigor and transparency |
| P2 (Nice) | Add one additional model/benchmark and EBLoRA comparison | Sec 4.1, 4.2 | High | Strengthens generalizability; not strictly required for publication |

### Execution Path
1. **Day 1–2:** Complete all P0 text revisions (claims, related work, contributions).
2. **Day 3–4:** Complete P1 revisions (mechanism rewrite, update rule, limitations).
3. **Day 5–7 (optional):** Run additional experiments for P2 if resources allow.

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|--------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | SVD-EQ improves backward transfer in sequential LoRA CL | FOREVER 4 tasks, Qwen3-0.6B, LoRA r=8, 3 orders × 3 seeds=9 runs | OP, BWT, p-value | BWT +2.3pp, OP +0.8pp, p=0.059 | Partially (marginal significance) | Low statistical power (N=9) |
| E2 | SVD-EQ effects are order-dependent | Same setup, per-order breakdown | BWT per order, std | Orders 4,5 improve; Order 6 degrades | Yes | No analysis of why Order 6 fails |
| E3 | SVD-EQ reduces within-order variance | Same setup, std comparison | Within-order std | 3–10× variance reduction | Yes, strong | Not validated across benchmarks |
| E4 | Ablation: norm shrinkage vs. spectral redistribution | Mean-smoothing, Random-spectrum baselines | BWT, norm change | Mean-smoothing +2.2pp (norm −13.3%); Random-spectrum +1.6pp | Partially (mechanism unclear) | Dominant mechanism not identified |
| E5 | Correlation: pre-equalization ρ vs. BWT improvement | 27 task boundaries (3 orders × 3 seeds × 3 boundaries) | Pearson r, p-value | r=−0.027, p=0.893 (no correlation) | Hypothesis falsified | Alternative mechanism not tested |

### Research-Theme Gap Diagnosis
- **New knowledge:** The variance reduction finding provides new insight, but the mechanism is not well-understood due to the ablation results.
- **Reproducibility:** Method is well-specified except for the cumulative update rule.
- **Impact on practice:** The practical value of variance stabilization is clear, but the narrow evaluation limits confidence in real-world applicability.

### Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Est. Cost | Expected Gain |
|--------------|-----------|----------------|-------------------|---------|-------------------|-----------|---------------|
| Generalizability beyond FOREVER | SVD-EQ stabilizes CL outcomes across different benchmark settings | Evaluate on one additional CL benchmark (e.g., task arithmetic CL or a 6-task sequence) with same model | Sequential LoRA baseline | OP, BWT, std | Variance reduction ≥3× in at least one additional benchmark | 1–2 GPU days | Establishes generalizability |
| Dominant mechanism identification | Norm shrinkage is the primary driver of forgetting reduction | Add ablation: norm-shrinking-only variant (scale delta by 0.867× without SVD) | Sequential LoRA, Mean-Smoothing | BWT, std | Norm-shrinking-only matches SVD-EQ performance | Minimal | Resolves mechanism ambiguity |
| Comparison with EBLoRA | Post-hoc equalization is complementary to training-time spectral regularization | Run EBLoRA on same setup; compare BWT and std | Sequential LoRA, SVD-EQ | BWT, std, training time | Identify complementary vs. overlapping benefit | 2–3 GPU days | Strengthens positioning |
| Scaling to larger models | Variance reduction persists with larger model sizes | Evaluate on Qwen3-1.5B or Llama-3-8B with same protocol | Sequential LoRA | OP, BWT, std | Variance reduction ≥2× | 3–5 GPU days | Demonstrates practical value |

## Novelty Verification & Related-Work Matrix
### 9A — Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|---------------------|-----|------------|----------------------|
| C1 | Post-hoc norm-preserving spectral equalization for LoRA CL, simultaneously training-free, memory-free, post-hoc | [1], [2], [3] | partially_overlapping | Spectral Surgery [1] and EBLoRA [2] address similar spectral properties; SVD-EQ differs in sequential CL application and norm preservation, but overlap in mechanism is significant | High | Reposition as complementary direction rather than unique first |
| C2 | +2.3pp BWT improvement (15% relative reduction) on FOREVER | — | unclear | Marginal significance (p=0.059), order-dependent (2/3 orders), no comparison with EBLoRA [2] | Medium | Downgrade to secondary finding; emphasize variance reduction instead |
| C3 | 3–10× within-order variance reduction, stabilizing CL outcomes | — | supported | Novel empirical finding with clear practical value; not reported in prior CL spectral work | High | Elevate to primary contribution |

### 9B — Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|--------------------------|-------------------|-------------------------|-------------------|
| Root: Spectral Interventions for CL | Branch: Training-time spectral regularization | Leaf: Stiefel-constrained optimization [2] | Requires gradient access during training | SVD-EQ is post-hoc; EBLoRA uses projected first-order method | Medium |
| Root: Spectral Interventions for CL | Branch: Post-hoc spectral refinement | Leaf: Gradient-guided SVD reweighting [1] | Requires small calibration set with gradients | SVD-EQ is fully data-free; Spectral Surgery uses gradient sensitivity | High |
| Root: Spectral Interventions for CL | Branch: Post-hoc spectral pruning | Leaf: SVD-based rank allocation [3] | Data-free compression | SVD-EQ equalizes rather than prunes; targets CL not compression | Low |
| Root: Model Merging for CL | Branch: Post-hoc adapter merging | Leaf: Dynamic consolidation [4], Perturb-and-Merge [5] | Assumes task model availability | SVD-EQ operates sequentially online at each boundary | Low |

### 9C — Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---------|----------------|-------------|------------------------|-----------------|-------------------------|
| [1] | Single-task LoRA refinement | Gradient-guided SVD reweighting | Post-hoc SVD intervention on LoRA adapters | Spectral Surgery uses gradient sensitivity; SVD-EQ uses uniform equalization | High: narrows novelty space |
| [2] | Sequential LoRA CL | Stiefel-manifold spectral regularization | Identifies spectral imbalance as CL forgetting cause | EBLoRA is training-time; SVD-EQ is post-hoc | High: directly comparable problem |
| [3] | LoRA compression | SVD-based adaptive rank pruning | Post-hoc SVD manipulation | PARA targets compression; SVD-EQ targets CL forgetting | Low: different objective |
| [4] | Rehearsal-free LoRA CL | Post-hoc merging with representation consolidation | Post-hoc LoRA CL without training mods | DESIRE uses merging; SVD-EQ uses spectral equalization | Medium: alternative post-hoc approach |
| [5] | Sequential CL | Hessian-guided perturbation then merging | Post-training CL intervention | P&M uses convex combination; SVD-EQ uses SVD equalization | Medium: different mechanism |

**Contribution-level Novelty Conclusion:** C1 is `partially_overlapping` due to significant methodological overlap with Spectral Surgery [1] and EBLoRA [2] in the post-hoc spectral intervention space. C2 is `unclear` due to marginal statistical evidence and lack of direct comparison. C3 is `supported` as a novel empirical finding with practical value. The paper should be repositioned to emphasize variance stabilization as the primary contribution and acknowledge the incremental nature of the spectral equalization mechanism.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Continual Learning for LoRA (Root)
├── Branch 1: Training-Time Spectral Methods
│   ├── Leaf 1.1: Stiefel-manifold regularization [2]
│   └── Leaf 1.2: Spectral clipping/regularization [6]
├── Branch 2: Post-Hoc Spectral Interventions
│   ├── Leaf 2.1: Gradient-guided SVD reweighting [1]
│   ├── Leaf 2.2: SVD-based rank pruning [3]
│   └── Leaf 2.3: Norm-preserving equalization (This Paper)
├── Branch 3: Post-Hoc Model Merging for CL
│   ├── Leaf 3.1: Dynamic consolidation [4]
│   └── Leaf 3.2: Perturb-and-Merge [5]
└── Branch 4: Architecture-Based CL
    ├── Leaf 4.1: Orthogonal subspace [7]
    └── Leaf 4.2: Shared attention [8]

Manuscript Positioning: Branch 2, Leaf 2.3
Value Solved: Variance stabilization in sequential CL via norm-preserving SVD equalization
Novelty Risk: High overlap with Leaf 2.1 (Spectral Surgery) on post-hoc SVD mechanism
```

## References
[1] Spectral Surgery: Training-Free Refinement of LoRA via Gradient-Guided Singular Value Reweighting 2603.03995

[2] Spectral Imbalance Causes Forgetting in Low-Rank Continual Adaptation 2602.00722

[3] Post-Optimization Adaptive Rank Allocation for LoRA 2604.27796

[4] DESIRE: Dynamic Knowledge Consolidation for Rehearsal-Free Continual Learning 2411.19154

[5] Train with Perturbation, Infer after Merging: A Two-Stage Framework for Continual Learning 2505.22389

[6] Enhancing LLM Training via Spectral Clipping 2603.14315

[7] Orthogonal Subspace Learning for Language Model Continual Learning 2310.14152

[8] Merge before Forget: A Single LoRA Continual Learning via Continual Merging 2512.23017

[9] Resolving Conflicts in Lifelong Learning via Aligning Updates in Subspaces 2512.08960

[10] Scalable Strategies for Continual Learning with Replay 2505.12512

[11] Learning Continually by Spectral Regularization 2406.06811

[12] LoRA vs Full Fine-tuning: An Illusion of Equivalence 2410.21228

[13] Energy-Structured Low-Rank Adaptation for Continual Learning 2605.27482

[14] Revisiting Weight Regularization for Low-Rank Continual Learning 2602.17559

[15] Spectral Adapter: Fine-Tuning in Spectral Space 2405.13952

[16] On Catastrophic Forgetting in Low-Rank Decomposition-Based Parameter-Efficient Fine-Tuning 2603.09684

[17] A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA 2312.03732

[18] CLoRA: Parameter-Efficient Continual Learning with Low-Rank Adaptation 2507.19887

[19] Online-LoRA: Task-free Online Continual Learning via Low Rank Adaptation 2411.05663

[20] Chain of LoRA: Efficient Fine-tuning of Language Models via Residual Learning 2401.04151

[21] LoRA-GA: Low-Rank Adaptation with Gradient Approximation 2407.05000

[22] Collaboratively adding new knowledge to an LLM 2410.14753

[23] Closed-form merging of parameter-efficient modules for Federated Continual Learning 2410.17961

[24] Continual Learning in Vision-Language Models via Aligned Model Merging 2506.03189

[25] HAM: Hierarchical Adapter Merging for Scalable Continual Learning 2509.13211

[26] DOLFIN: Balancing Stability and Plasticity in Federated Continual Learning 2510.13567

[27] Hybrid-LoRA: Bridging Full Fine-Tuning and Low-Rank Adaptation for Post-Training 2605.18822

[28] How Efficient Are Today's Continual Learning Algorithms? 2303.18171

[29] Towards Symmetric Low-Rank Adapters 2504.03719

[30] Energy-Based Models for Continual Learning 2011.12216

[31] TAIL: Task-specific Adapters for Imitation Learning with Large Pretrained Models 2310.05905

[32] Avalanche: A PyTorch Library for Deep Continual Learning 2302.01766

[33] Parameter Efficient Instruction Tuning: An Empirical Study 2411.16775

[34] RegCL: Continual Adaptation of Segment Anything Model via Model Merging 2507.12297

[35] LoRA-Loop: Closing the Synthetic Replay Cycle for Continual VLM Learning 2507.13568

[36] Simple Recipe Works: Vision-Language-Action Models are Natural Continual Learners with Reinforcement Learning 2603.11653

[37] Deep Generative Continual Learning using Functional LoRA: FunLoRA 2510.02631

[38] Signs Beat Floats: Low-Rank Double-Binary Adaptation for On-Device Fine-Tuning 2605.24058

[39] Recent Advances of Continual Learning in Computer Vision: An Overview 2109.11369

[40] Out-Of-Distribution Detection In Unsupervised Continual Learning 2204.05462

[41] PIVOT: Prompting for Video Continual Learning 2212.04842

[42] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[43] Selective Replay Enhances Learning in Online Continual Analogical Reasoning 2103.03987

[44] Few-Shot Continual Learning for 3D Brain MRI with Frozen Foundation Models 2602.23533

[45] Towards continual learning in medical imaging 1811.02496

[46] LOHA: Direct Graph Spectral Contrastive Learning Between Low-pass and High-pass Views 2501.02969

[47] Spectral Surgery: Class-Targeted Post-Hoc Rebalancing via Hessian Spike Perturbation 2605.07790

[48] Dynamic VAEs with Generative Replay for Continual Zero-shot Learning 2104.12468

[49] Continual Learning in 3D Point Clouds: Employing Spectral Techniques for Exemplar Selection 2409.08388

[50] Cut out and Replay: A Simple yet Versatile Strategy for Multi-Label Online Continual Learning 2505.19680

[51] Online Continual Learning via Multiple Deep Metric Learning and Uncertainty-guided Episodic Memory Replay 2111.02757

[52] Long-distance axial spectral encoding using space-time wave packets 2505.00895

[53] Ring Artifact Correction in Photon-Counting Spectral CT Using a Convolutional Neural Network With Spectral Loss 2302.00921

[54] Implementing spectral methods for hidden Markov models with real-valued emissions 1404.7472

[55] A survey on computational spectral reconstruction methods from RGB to hyperspectral imaging 2106.15944

[56] Spectral Dynamics of Learning Restricted Boltzmann Machines 1708.02917

[57] The spectral weight of the Hubbard model through cluster perturbation theory cond-mat/9908045

[58] Trace formulae and inverse spectral theory for Schrödinger operators math/9310229

[59] On applying the subspace perturbation theory to few-body Hamiltonians 1311.6604

[60] Seeing bulk perturbations in Lifshitz holography 1703.10676

[61] Spectral Analysis For the Matrix Sturm-Liouville Operator on a Finite Interval 1008.4339

[62] Spectral conditions for a graph to be Hamilton-connected 1207.6447

[63] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[64] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[65] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[66] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[67] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[68] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[69] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[70] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[71] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

[72] Balanced Data, Imbalanced Spectra: Unveiling Class Disparities with Spectral Imbalance 2402.11742

---

### ASCII Diagram — Paper Structure & Evidence Map

```text
[Abstract/Intro: Post-hoc SVD equalization for LoRA CL]
    ├── [Claim C1: Training-free, memory-free, post-hoc uniqueness]
    │   └── [Evidence gap: Spectral Surgery [1] and EBLoRA [2] overlap]
    │       └── [Risk: Uniqueness claim rejected as overreach]
    ├── [Claim C2: +2.3pp BWT improvement]
    │   └── [Evidence: p=0.059, order-dependent]
    │       └── [Risk: Marginal significance, low power (N=9)]
    └── [Claim C3: 3-10× variance reduction]
        └── [Evidence: Consistent across orders]
            └── [Strength: Most reliable finding]

[Method: SVD equalization at task boundaries]
    ├── [Formula: σ_i → σ̄ = ||σ||₂/√r]
    │   └── [Verified: Norm preservation correct]
    └── [Missing: Explicit cumulative update rule]

[Experiments: FOREVER benchmark, Qwen3-0.6B]
    ├── [Main result: BWT +2.3pp, p=0.059]
    ├── [Variance: 3-10× reduction]
    ├── [Ablation: Mean-smoothing +2.2pp ≈ SVD-EQ +2.3pp]
    │   └── [Implication: Norm shrinkage may be dominant mechanism]
    └── [Correlation: ρ vs ΔBWT: r=-0.027, p=0.893]
        └── [Implication: Spectral concentration hypothesis falsified]
```

### ASCII Diagram — Revision Strategy Roadmap

```text
[P0: Remove uniqueness claim + add Spectral Surgery]
    ├── Fix: Rewrite Abstract/Conclusion uniqueness statement
    ├── Fix: Add Sec 2.3 paragraph on Spectral Surgery [1]
    └── Expected gain: Resolves credibility risk

[P0: Reframe contributions to lead with variance]
    ├── Fix: Reorder contribution bullets
    ├── Fix: Update Abstract S4-S5
    └── Expected gain: Aligns narrative with strongest finding

[P1: Correct mechanism discussion]
    ├── Fix: Acknowledge norm shrinkage as dominant in Sec 4.4
    ├── Fix: Note falsified hypothesis in Sec 4.5
    └── Expected gain: Resolves motivation-results contradiction

[P1: Add explicit update rule]
    ├── Fix: Add formula in Sec 3.3
    └── Expected gain: Improves reproducibility

[P2: Add EBLoRA comparison + larger model (optional)]
    ├── Experiment: Run EBLoRA on same setup
    ├── Experiment: Evaluate on Qwen3-1.5B
    └── Expected gain: Strengthens generalizability
```

### ASCII Diagram — Experiment Upgrade Plan

```text
Stage 1 (Day 1-2): Text revisions only
├── Remove uniqueness claims (Abstract, Conclusion)
├── Add Spectral Surgery to Related Work (Sec 2.3)
├── Reframe contribution order
└── Add update rule formula

Stage 2 (Day 3-4): Mechanism discussion rewrite
├── Rewrite Sec 4.4 ablation interpretation
├── Rewrite Sec 4.5 correlation discussion
└── Expand limitations section

Stage 3 (Day 5-7, optional): Additional experiments
├── Run EBLoRA baseline comparison
├── Evaluate on larger model (Qwen3-1.5B)
└── Add one additional benchmark
```

## Scores
**Final Score: 4.5/10**

The paper presents a clean, reproducible post-hoc spectral intervention for LoRA continual learning with a compelling variance reduction finding. However, the novelty is substantially weakened by related post-hoc spectral methods (Spectral Surgery, EBLoRA), the evaluation scope is too narrow to support general claims, the statistical significance is marginal, and the mechanism remains poorly understood. The variance stabilization finding is the strongest asset and should be elevated as the primary contribution. With the recommended revisions (claim repositioning, related work additions, mechanism reframing), the paper could reach a moderate score.

**Post-Revision Target: [6.0, 7.0]/10**

If the authors successfully (a) reposition the novelty claim against Spectral Surgery and EBLoRA, (b) reframe contributions to lead with variance reduction, (c) correct the mechanism discussion, and (d) add at least one additional benchmark or model size, the paper could achieve a solid mid-tier score reflecting its practical value as a lightweight CL stabilization tool.