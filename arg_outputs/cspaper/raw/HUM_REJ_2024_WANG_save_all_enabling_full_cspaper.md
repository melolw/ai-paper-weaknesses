# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes FedCyBGD, a federated learning (FL) training paradigm for large language models (LLMs) that aims to enable full-parameter tuning on resource-limited clients. The core idea is to perform cyclic block coordinate descent: each client is assigned one or more “responsible” blocks, updates only those blocks on local data, and uploads the deltas, while the remaining “unresponsible” blocks are frozen and replaced with a compressed surrogate for local forward/backward passes. A hybrid compression scheme combines pruning for previously updated blocks and layer dropping for blocks that have not yet been updated. The method is evaluated on GPT-2, RoBERTa, BLOOM, ChatGLM, and LLaMA-2 across GLUE, Alpaca-GPT4, OASST1, and SQuAD, reporting reductions in communication/memory and competitive or improved task performance compared to full fine-tuning and PEFT baselines.

## Summary Of Strengths
- Clear problem targeting an important bottleneck: enabling near full-parameter FL tuning of LLMs under strict client memory and bandwidth constraints. The cyclic block update perspective is a well-motivated angle to reduce per-round client burden.
- Concrete algorithmic specification: Algorithm 1 (FedCyBGD) and Algorithm 2 (Hybrid Pruning) provide a reasonably clear high-level training and compression process, with the objective formalized in Equations (1)–(3) and the compression operator defined in Equation (4) and instantiated in Equation (5) and (6).
- Broad empirical scope across models and tasks:
  - GLUE with RoBERTa-base (Table 3).
  - Instruction-following (Alpaca-GPT4) and OASST1 for LLaMA2-7B, ChatGLM-6B, and BLOOM (Table 4).
  - SQuAD with GPT-2 small (Table 5).
  - Resource and time breakdowns for LLaMA2-7B (Tables 1, 2, 7).
- Explicit resource accounting: Tables 1 and 2 quantify memory, download/upload, and per-epoch timings; this is valuable for FL researchers who care about practical feasibility.
- Orthogonality to PEFT: Table 6 shows that PEFT (LoRA, Adapters) can be integrated with FedCyBGD, offering a tunable performance-versus-cost spectrum.
- Figure-grounded insight: Figure 1 supports the claim that “cyclical block updates” can outperform aggregation-based FL in their setup; Figure 2 provides an intuitive schematic of the server-client flow and the compressed model concept; Figure 3 ablates block allocation strategies.

Specific positive figure/table references:
- Figure 2 concretely conveys the proposed flow: downloading only the responsible block and a compressed surrogate for the frozen parts, and then “plugging” the updated block back on the server; this visualization helps decode Algorithm 1 and 2.
- Table 3 shows that FedCyBGD nearly matches full fine-tuning on most GLUE metrics while using 2.79 GB memory vs. 15.87 GB for full FT and communication similar to PEFT, which is a compelling efficiency-accuracy point for RoBERTa-scale models.
- Table 4 demonstrates that FedCyBGD attains best or second-best losses across multiple model scales on Alpaca-GPT4 and OASST1, supporting the cross-model generality of the approach.
- Table 1 highlights a practical win: for LLaMA2-7B, FedCyBGD’s upload is orders of magnitude smaller than Fed-full, and download is about 6.24 GB instead of the full model size, consistent with the proposed compression-plus-blocking design.

## Summary Of Weaknesses
1) Unclear or potentially invalid assumption behind the “unbiased” compression operator and its instantiations
- Equation (4) defines a randomized compression operator C with E[C(θ)] = θ and bounded MSE. However, the two concrete compression components used in Equation (6) and Algorithm 2, namely structured pruning P and layer drop I, are not unbiased operators in general. There is no argument that the hybrid of P and I satisfies Equation (4), nor that unbiasedness is needed or that a weaker condition suffices. This is a central theoretical mismatch between definition and actual instantiation.
- Why it matters: If gradients are computed with heavily biased emulators for frozen blocks, the optimization trajectory can deviate substantially; the paper leans on block coordinate descent analogies yet does not address how emulator bias affects convergence or stability, especially under data heterogeneity.

2) Cyclical client participation realism, stragglers, and fairness
- Algorithm 1 updates clients “in order” within each round, requiring sequential participation. This is likely to be impractical in cross-device FL due to client availability and straggling. The paper does not discuss asynchronous variants, partial participation, or robustness to dropouts. The wall-clock improvements reported in Table 2 and Table 7 may not hold if clients are slow or intermittently available.
- Why it matters: Sequential client scheduling is a strong systems assumption for FL. Without discussing asynchronous or partial participation, the method’s deployability is unclear.

3) Claims about privacy/model secrecy are under-argued
- Page 2 claims the approach “safeguards client data privacy and ensures the preservation of the server’s model privacy.” In FedCyBGD, clients still receive updated blocks and compressed surrogates that may leak model information. No privacy mechanism (e.g., secure aggregation, DP, homomorphic encryption) is used. The compression is not a formal privacy mechanism. The risk of model extraction from shared blocks or surrogates is not analyzed.
- Why it matters: Privacy and confidentiality are core FL motivations. Overstating privacy without mechanisms or analysis is misleading.

4) Limited heterogeneity and federated data realism
- The paper does not describe the partitioning of datasets across 32 or 64 clients beyond “random cyclic order” (Section 7.2). There is no systematic study of non-IID severity, client sampling rates, or per-client data sizes. The reported improvements may not generalize under strong heterogeneity or skewed label distributions.
- Why it matters: The paper’s central claim is that cyclical block updates mitigate heterogeneity issues vs. aggregation. This needs a stress-test with controlled non-IID settings and ablations, not just one illustrative observation as in Figure 1.

5) Baseline coverage and fairness
- The comparison omits FL methods designed for LLMs that also target full-parameter or communication-efficient tuning beyond classical PEFT, and does not include stronger modern baselines that address communication and memory head-on. The Related Work mentions some gradient compression and distillation approaches, but experiments do not include them.
- Why it matters: Without competitive FL LLM baselines that also pursue full-parameter or efficient tuning, it is hard to attribute performance gains to the proposed design rather than weaker comparisons.

6) Ambiguity and inconsistency in resource accounting
- Table 1 “Basic Model” and costs: e.g., “FedLora” shows higher memory than “Fed-full” for LLaMA2-7B in the “Basic Model” column (25.24 GB vs. 12.61 GB), which contradicts typical expectations and the paper’s own narrative. The accompanying footnote about BF16 mixed-precision requiring FP32 storage for model weights for LoRA partly explains but still needs clearer, standardized accounting to ensure apples-to-apples comparisons.
- The download/upload numbers rely on the compression schedule, but the exact compression ratios, pruning rates, and layer-drop probabilities are not specified in the main paper; reproducibility and interpretability suffer.

7) Weak justification for the “Observation” in Figure 1
- Figure 1 claims that “cyclical block updates outperform aggregation,” yet the setup lacks detail: number of clients, aggregation algorithm specifics, data partition, optimizer settings, and how many local steps. Without controlled ablations, this “central observation” risks being an artifact of a cherry-picked setting.
- Why it matters: The observation underpins the entire paradigm. It must be robustly established.

8) Convergence and stability are under-explored
- Section 6 acknowledges lack of theory. Empirically, there is limited analysis of convergence behavior with different block orders, block sizes, and compression ratios. Figure 3 shows some block allocation strategies but not their interaction with data heterogeneity, sequence length, or optimizer state handling across blocks.
- Why it matters: Block coordinate descent with biased emulators and sequential FL scheduling can have non-trivial convergence dynamics.

9) Missing experimental details and clarity gaps in algorithms
- Algorithm 1: line 4 uses a mixture of θ and θ̃ indexed at t and t+1, but the exact timing of “previously updated” vs. “pending” blocks per mini-step is confusing. How is optimizer state (e.g., Adam moments) handled across blocks and over sequential clients? Are moments maintained per block server-side?
- Algorithm 2: The pruning function P is said to be “dynamically chosen according to the task,” but in the main paper only Ma et al. (2023) is briefly mentioned. What sparsity ratios are used? Are pruned weights regrown? How often are pruned masks updated?

10) Generality of “full-parameter tuning”
- Practically, at any client, only one block is updated at a time with other blocks frozen and replaced by compressed surrogates. This is not truly “full-parameter tuning” per round; it is blockwise full tuning over time. The claim is valid in an amortized sense, but the paper sometimes blurs this distinction, which can be misleading about per-round compute/memory needs and total time-to-performance.

Figure- and table-specific critiques:
- Figure 1: The stacked bars and line chart suggest better loss with cyclical updates, but the axes, scales, and exact settings are not specified. Without precise experimental context, the figure is more suggestive than conclusive.
- Figure 3: Shows loss trajectories for different block allocations (Ascend, Descend, Random). The curves are close after early steps, making it difficult to judge practical impact relative to data heterogeneity or client mix. It would help to overlay communication/memory metrics to show trade-offs of each allocation policy.
- Table 2: Round times are reported, but since the approach is sequential by design, a “global round” equals all clients finishing their turns. This implicitly assumes synchronized, always-available clients. A sensitivity study with stragglers or partial participation is needed to substantiate the reported wall-clock advantages.
- Table 6: The “+i/+ii/+iii” shorthand needs clearer labeling in the main text, including the exact compression ratios and LoRA/Adapter insertion sites. Also, “Performance” is a loss (lower is better) but the table mixes costs and losses without explicit standard errors or multiple seeds.

## Potentially Missing Related Work
1) Qin et al., “Federated Full-Parameter Tuning of Billion-Sized Language Models with Communication Cost under 18 Kilobytes,” 2024 — Directly targets full-parameter federated LLM tuning with extreme communication efficiency (FedKSeed). It should be discussed in Section 2 (Related Works) and compared experimentally or at least analytically in Section 4, particularly on communication-accuracy trade-offs and assumptions about client capabilities.

2) Jiang et al., “Low-Parameter Federated Learning with Large Language Models,” 2023 — Presents LP-FL combining LoRA with FL for LLMs. While PEFT baselines are included, this specific FL-LLM method should be cited and contextualized in Section 2, and, if feasible, included as a baseline in Tables 3–5.

3) Gao et al., “FedPT: Federated Proxy-Tuning of Large Language Models on Resource-Constrained Edge Devices,” 2024 — Proposes collaborative fine-tuning via a smaller proxy and transferring to the large model, focusing on memory/compute constraints. This is conceptually close to your compressed emulator idea. Discuss in Section 2 and compare in Section 4 (at least in communication and memory metrics).

4) Gao et al., “Federated Adaptive Fine-Tuning of Large Language Models with Heterogeneous Quantization and LoRA,” 2025 — Addresses resource heterogeneity and jointly optimizes quantization and LoRA ranks; it would help to discuss in Section 2 and contrast your blockwise sequential scheme vs. their heterogeneous optimization in Section 4.

5) Yang et al., “FedKRSO: Communication and Memory Efficient Federated Fine-Tuning of Large Language Models,” 2026 — Optimizes in shared random low-dimensional subspaces with accumulator updates. Include in Section 2 and compare, especially on the theory and convergence assumptions relevant to your blockwise scheme.

6) Wei et al., “Federated reasoning LLMs: a survey,” 2025 — Offers a comprehensive landscape of federated LLM training; use it in Section 2 to strengthen the positioning and to ensure benchmark practices match the state-of-the-art assumptions.

7) Patel et al., “F-Transformer: a federated transformer for efficient and privacy-preserving sequence generation,” 2026 — While not an LLM-scale model, it focuses on efficient federated transformers. Cite in Section 2 as a related architectural/optimization perspective for sequence generation under FL constraints.

## Comments Suggestions And Typos
Actionable suggestions:
1) Reconcile compression theory and practice
- Either (a) replace Equation (4) with a weaker assumption that matches pruning and layer drop, and discuss the resulting optimization behavior, or (b) justify why the chosen P and I operators approximate unbiased compression in your setting, with empirical evidence that emulator bias does not derail optimization. An ablation varying pruning ratios and layer drop probabilities, plus a small-scale convergence plot, would help.

2) Strengthen the “Observation” of Figure 1 with controlled studies
- Provide details on client counts, partition non-IID severity (e.g., Dirichlet α), local steps, optimizers, and aggregation protocols. Add ablations varying non-IID level to show when cyclical block updates outperform aggregation and when they do not. If feasible, include a standard cross-device FL baseline like FedAvg with partial participation tuned for LLMs.

3) Federated realism: stragglers, dropouts, and partial participation
- Report sensitivity to client availability and asynchronous/semi-asynchronous variants. Time-to-accuracy under random client drop or delayed clients will make Table 2 and Table 7 more credible.

4) Clarify optimizer state handling and reproducibility
- Describe whether and how Adam moments are maintained per block across rounds and clients. Provide full training hyperparameters in the main paper or a well-linked appendix: pruning ratios, layer-drop schedules, compression seeds, block sizes, and exact block partition policy. This will raise the Reproducibility rating.

5) Tighten privacy claims
- Either remove broad privacy claims or include a discussion of model confidentiality risks from distributing updated blocks and compressed surrogates. Consider adding DP or secure aggregation variants as an optional module, and discuss their impact on performance and resource costs.

6) Expand baselines or analytical comparisons
- When experimental inclusion is not feasible, include a detailed analytical comparison of communication/memory metrics and assumptions against recent federated full-parameter or proxy-tuning methods (e.g., FedKSeed and FedPT), and gradient-compression baselines for LLM FL.

Typos and wording:
- Multiple instances of “unresponsible blocks” should be “unassigned” or “non-responsible” blocks.
- Page 2: “negating the need for additional updates or uploads” could be clarified as “no local updates or uploads for frozen blocks.”
- Section 3.1 mentions “easily surpasses the performance of the aggregation paradigm” — consider softening and providing statistical significance if applicable.
- Table 6 caption: expand “+ i/ii/iii” in the main text before the table; readers should not need to look back to decode shorthand.
- Table 1: “Basic Model” column labels are unclear (e.g., 12.61 GB for Fed-full vs. 25.24 GB for FedLoRA); explicitly define whether this is the in-memory parameter footprint with precision format and activation checkpointing on or off.
- Algorithm 1, line numbering skips from 7 to 9; check formatting.

Criteria that could raise my score:
- A rigorous heterogeneity study with ablations validating the Figure 1 claim across non-IID settings, plus at least one additional modern FL-LLM baseline or a careful analytical comparison.
- Clarification and consistency in resource accounting across methods; publish precise compression settings.
- Either a light convergence argument adapted to biased emulators or empirical stability evidence across compression levels and client permutations.
- Address the sequential scheduling assumption with either an asynchronous variant or a sensitivity study on availability/stragglers.

## Confidence
3.5 Between reasonably confident and quite sure: I checked the key claims, figures, equations, and tables carefully, though some implementation details are not fully specified.

## Soundness
2.5 Between Poor and Acceptable: Interesting idea and promising empirical results, but gaps in theoretical grounding of the compression operator, missing federated realism (asynchrony/stragglers), and limited non-IID analysis undermine the strength of the claims.

## Excitement
2.5 Between potentially interesting and interesting: The block-cyclic idea with compressed emulators is appealing and practical, but the current evaluation and positioning are not yet strong enough to make it exciting for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the proposed approach is promising and the empirical scope is broad, there are several substantive issues: theoretical–practical mismatch in the compression operator, limited federated realism in experiments, under-specified resource accounting, and weak justification of the central “cyclical beats aggregation” observation. With stronger ablations, clarified accounting, and a more rigorous discussion of privacy and convergence, this could reach solid-Findings or even main-track quality.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The Limitations section candidly acknowledges the lack of theoretical guarantees and the focus on NLP; that is appreciated. However, the societal impact discussion is very light. This work interacts with privacy-sensitive FL use cases but does not analyze model leakage risks when distributing updated blocks and compressed surrogates. It would help to:
  - Discuss who benefits if full-parameter FL becomes more feasible (e.g., on-device personalization) and who might be harmed if model intellectual property leaks through shared blocks.
  - Consider failure modes when emulator compression is too aggressive, possibly degrading performance for underrepresented user groups with minority data distributions.
  - Reflect on dual-use: techniques that reduce costs could also accelerate model misuse if privacy is not carefully considered.

## Ethical concerns
None beyond the need to temper privacy claims and to discuss model confidentiality and potential leakage due to distributing blocks and compressed surrogates. No apparent use of sensitive data without consent described.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: The high-level algorithms and settings are described, and many results are tabulated. However, key compression and pruning hyperparameters, block partition policies, and optimizer-state handling are not fully specified in the main paper; resource accounting details are also ambiguous.

## Datasets
3 Potentially useful: Standard benchmarks are used; no new datasets are introduced.

## Software
2 Documentary: It is not stated whether code will be released. If released with detailed configs, it would raise the score.