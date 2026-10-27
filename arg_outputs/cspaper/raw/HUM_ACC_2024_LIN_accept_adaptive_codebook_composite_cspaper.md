# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes ACCEPT, a parameter-efficient prompt tuning method that factorizes soft prompts using shared, learnable codebooks defined over K subspaces of the embedding (product-quantization inspired). Each sub-prompt is a linear combination of r codewords in its subspace with adaptive weights, and two instantiations are combined: SCPP (prepended prompts) and SCAP (added prompts). The learnable codebooks are shared across all prompts so the number of codebook parameters is independent of prompt length. The method is trained end-to-end and tuned only on prompts, keeping the pretrained LM frozen. Experiments on 17 tasks (GLUE, SuperGLUE, MRQA) and several model sizes (T5-small/base/large/3B, Flan-T5-11B) show consistent gains over strong PEFT baselines with about 0.3% tunable parameters. Ablations analyze subdivision granularity, contributions of SCPP vs SCAP, and initialization strategies.

## Summary Of Strengths
- Methodological idea: Using shared, learnable subspace-specific codebooks with soft linear combination provides a compact, composite prompt parameterization. The parameter accounting in Equation 7 clarifies how codebook cost decouples from prompt length.
- Clear architecture presentation: Figure 1 shows SCPP and SCAP factorization and their combination into the full ACCEPT pipeline, making the mechanism easy to follow.
- Strong empirical coverage:
  - Large-scale comparisons on 13 GLUE and SuperGLUE tasks plus 4 MRQA datasets with T5-base in Table 1 and Table 2, typically outperforming PEFT methods and sometimes exceeding full fine-tuning with far fewer parameters.
  - Few-shot results in Table 3 illustrate consistent improvements, especially on BoolQ.
  - Scaling to larger backbones (Figure 3, Tables 7–8) shows benefits persist up to T5-3B and Flan-T5-11B.
- Thorough ablations:
  - Table 4 isolates the effects of learnable codebooks and subdivision.
  - Table 5 and Table 11 explore subdivision granularity t and codebook size r, with clear parameter budgets.
  - Table 6 and Table 14 quantify the contribution of SCPP and SCAP individually and combined across benchmarks.
  - Table 9 and Tables 13/15 probe initialization strategies.
  - Figure 4 explores the trade-off between prompt length and training time, and finds a sweet spot around m = 60.
- Clarity and reproducibility: The method is mathematically specified (Equations 1–7), training objectives are standard, and implementation details plus hyperparameter search spaces are spelled out in Appendix A. Dataset statistics and metrics are tabulated in Table 10.

## Summary Of Weaknesses
1) Soft combination vs. simple linear bases: The subspace-wise linear combination of r codewords (Equation 3) effectively defines a shared linear basis per subspace. Without sparsity or diversity constraints, the representational benefit over a low-rank linear mapping is unclear. There is no analysis of codeword utilization, redundancy, or collapse (e.g., entropy of w_i^k, rank of assembled sub-prompts), which is central to validating the PQ motivation. This matters because the core claim is parameter-efficient compositionality; quantifying how many distinct codewords are effectively used would strengthen that claim.

2) Equation and notation issue: In Equation 3, the second term uses c_2^1 instead of c_2^k, which is likely a typo but creates confusion about whether subspace indices are shared or independent. Given Equation 3 is the core construction, this should be corrected and explained.

3) Fairness of configuration selection and initialization:
   - Section 4.1 states that SCPP/SCAP are pretrained under three strategies (random/intermediate/target), and “on each dataset, we select the best strategy as the final results.” This per-dataset selection risks inflating headline results relative to baselines that do not enjoy per-dataset initialization sweeps. Please clarify whether comparable sweeps are allowed for baselines and how selection is done without peeking at test.
   - Hyperparameter selection: K and r are tuned on RTE (Section 4.4), then applied to all datasets. That is fine, but other sensitive hyperparameters (learning rates are unusually high, e.g., 0.3–0.5 for SCPP and up to 10 for SCAP as per Appendix A) may bias comparisons if not consistently tuned across methods. A transparent protocol for HPO budgets across baselines is needed.

4) Efficiency claims lack runtime evidence: The paper emphasizes parameter efficiency and claims inference/training efficiency gains (e.g., Section 3.3 citing reduced input length via SCAP+SCPP and Section 5). However, runtime or memory metrics are not reported beyond Figure 4’s training-time trend for varying m on two datasets. There is no wall-clock comparison against DePT, LoRA, or PT for both training and inference, nor FLOPs or activation memory analyses. Since efficiency is a central selling point, reporting speedups and memory footprints would be important.

5) Parameter accounting for SCAP: SCAP ties parameter count to sequence length l, which can be large (up to 348 for MultiRC). While you ensure rd + rmK ≤ md, the practical impact for long inputs is not examined. A sensitivity analysis vs. l or a breakdown of SCPP vs. SCAP parameter shares across tasks with different l would clarify when SCAP is advantageous.

6) Limited analysis on QA generation behavior: Section 4.4 mentions smaller gains on QA tasks and defers analysis of long-form generation to future work. Since MRQA is part of the main results, a qualitative or error analysis would be helpful to understand when compositional prompts help or fail in span extraction, especially given SCAP acts as embedding deltas.

7) Missing or under-discussed related work on codebook/discrete-prompt approaches:
   - The paper positions PQ mainly vs. VQ in general NLP or prompt clustering, but several recent codebook-based or VQ-style prompting methods are not compared or discussed. This weakens the positioning, especially since ACCEPT’s core mechanism is a learned codebook.
   - See the “Potentially Missing Related Work” section for specific items and suggested placement.

8) Robustness and stability: Very large learning rates are explored for SCAP (Appendix A, up to 10). The paper lacks a stability discussion or failure modes. Reporting training curves, gradient norms, or sensitivity plots would help establish robustness.

9) Statistical significance: The headline comparisons in Table 1 and Table 2 do not report variance or significance tests, although a few entries have small std in MRQA. Given the margins over strong baselines are sometimes modest, significance tests would improve credibility.

10) Clarity/minor inconsistencies:
   - Figure 2 plots “Avg. Acc. on GLUE/SuperGLUE vs #parameters,” but axes and exact budgets differ across methods. Add numeric labels or a table mapping each marker to its parameter count for easier verification.
   - Typos and formatting glitches (examples in “Comments Suggestions And Typos”) distract from clarity.

Detailed figure- and table-grounded comments:
- Figure 1: The architecture diagram succinctly conveys the subdivision and shared codebooks for both SCPP and SCAP, and how they integrate. However, it would help to annotate how many codewords r and subspaces K were used in the main T5-base runs for each branch so readers can visually map to Equation 7’s budget.
- Figure 2: This is a compelling visual for the efficiency claim. Still, without runtime axes, it supports parameter efficiency but not end-to-end speed. The claim “best performance with the fewest parameters” holds for T5-base per Table 1 averages, but showing per-dataset dots or confidence intervals would avoid overgeneralization from averages alone.
- Figure 3: Scaling curves show ACCEPT maintains or increases gains with larger models on BoolQ, MultiRC, and WiC. This strengthens the claim of good scaling behavior. Please add the exact tunable parameter counts per method per model size in a caption or appendix table for full transparency.
- Figure 4: The prompt length m versus training time is informative, and the accuracy peak at m=60 offers a practical guideline. However, this is only for MRPC and STS-B; showing a similar trend on at least one SuperGLUE task would generalize the finding.
- Table 1: ACCEPT shows strong average gains on GLUE (87.9) and SuperGLUE (78.3) with 74.9K parameters, beating DePT and TPT averages in this setup. Notably large improvements appear on MRPC (93.1) and RTE (86.3) vs the next-best PT variants. Please add standard deviations or paired tests across seeds to gauge stability.
- Table 2: MRQA gains are consistent but modest on average (73.6 vs 73.0 for DePT). Since MRQA tasks are extractive QA, qualitative examples or per-length breakdowns could illuminate where compositional prompts help.
- Table 4 and Table 6: These ablations are convincing that both learnable codebooks and subdivision matter, and that combining SCPP and SCAP yields the best average performance.
- Table 5 and Table 11: The RTE-driven search suggests fine-grained subdivision benefits SCPP (t=32, K=24) while SCAP prefers coarser t=384 (K=2). It would help to confirm that these choices also perform near-optimally on a second task to avoid overfitting to RTE idiosyncrasies.

## Potentially Missing Related Work
1) Menabue et al., “Semantic Residual Prompts for Continual Learning,” 2024 — uses a two-level prompt pool and a second-level codebook for adaptive prompt selection. Highly relevant due to its codebook concept for prompts. Should be discussed in Related Work (Section 2.1) and compared conceptually to ACCEPT’s shared, learnable subspace codebooks. If feasible, include as a baseline or at least a qualitative comparison.

2) Lu et al., “Prompt Tuning as User Inherent Profile Inference Machine,” 2024 — learns user-specific soft prompts and quantizes them via a learned codebook for deployment efficiency. Add to Section 2.2 to highlight codebook-based prompt discretization strategies and discuss differences from ACCEPT’s soft, dense combinations.

3) Zhang et al., “Conceptual Codebook Learning for Vision-Language Models (CoCoLe),” 2024 — learns conceptual codebooks of prompts for CLIP adaptation, relevant for codebook-driven prompting. Add a brief discussion in Section 2.2 noting modality differences but conceptual overlaps in codebook prompts.

4) Jiao et al., “Vector Quantization Prompting for Continual Learning,” 2024 — integrates VQ into a discrete prompt pool trained end-to-end. Directly relevant to the codebook/discrete prompt theme. Discuss in Section 2.2 and, if possible, include a comparison highlighting ACCEPT’s soft subspace combinations vs discrete pools.

5) Luo et al., “Vector-Quantized Prompt Learning for Paraphrase Generation,” 2023 — learns a codebook of discrete prompts for textual generation. Include in Section 2.2 to clarify how ACCEPT differs from discrete VQ approaches in text-only settings.

6) Zhang et al., “Multi-modal prompt codebook learning: Achieving adaptive and generalizable prompting for CLIP-based visual recognition,” 2026 — while multimodal and later, it reinforces the generality of prompt codebooks and selection mechanisms. A short mention in Section 2.2 would contextualize ACCEPT within a broader movement toward codebook-based prompting.

## Comments Suggestions And Typos
Actionable suggestions and questions:
- Please fix Equation 3’s index typo (c_2^1 should be c_2^k). Given its centrality, re-check all indices throughout Section 3.3 for consistency.
- Provide runtime and memory metrics. At minimum, report training and inference wall-clock time and peak memory for ACCEPT vs PT, DePT, and LoRA on representative tasks, controlling for batch size and hardware. This would substantiate the “efficient” in the title beyond parameter counts.
- Codebook utilization analysis: Report statistics such as average entropy of weight vectors w_i^k, per-codeword selection frequency, or an effective number of active codewords. A visualization over training steps would show whether the model truly leverages compositional sharing rather than collapsing to a few bases.
- Initialization fairness: Clarify whether baselines also benefit from per-dataset initialization strategies or HPO budgets comparable to ACCEPT’s. If not, consider standardizing selection protocols or adding a row with a fixed initialization policy to isolate method gains from initialization gains.
- SCAP sensitivity to input length: Provide a breakdown showing how parameter count and performance vary with l across datasets and whether SCAP remains advantageous at longer sequence lengths.

Typos and minor issues:
- Section 3.3: “c_2^1” in Equation 3 likely should be “c_2^k”.
- Section 1: “To ease the learning process and make it dif-” line breaks appear mid-word.
- Section 4.4: “SueprGLUE” → “SuperGLUE”.
- Section 3.3: “Combing SCPP and SCAP then forms our final ACCEPT” → “Combining”.
- Table captions: Some abbreviations are not defined locally (e.g., “HP” in Table 2 stands for HotpotQA; clarify).
- Figure 2 caption could note exact parameter counts per marker to avoid ambiguity.
- Throughout: A few punctuation/spacing inconsistencies in math (e.g., use consistent spacing in subscripts/superscripts).

Criteria for raising my score:
- Add runtime and memory comparisons and demonstrate clear wall-clock or FLOPs benefits.
- Provide codebook utilization analyses showing non-trivial compositional sharing.
- Clarify the fairness of per-dataset initialization and HPO selection compared with baselines.
- Fix Equation 3 and the noted typos, and add significance testing for Table 1 and Table 2.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
4 Strong: This study provides sufficient support for all of its claims. Some extra experiments could be nice, but not essential. Justification: Broad benchmarks and ablations are solid; missing runtime evidence and codebook-use analysis prevent a higher score.

## Excitement
3.5 Between interesting and exciting. The compositional codebook framing is appealing and results are strong across many tasks, but the conceptual gap vs. low-rank bases and lack of efficiency measurements temper enthusiasm.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The core idea is clear, empirically validated across many tasks and scales, and the ablations are thoughtful. To solidify the efficiency narrative and distinctiveness of the PQ-inspired design, I encourage adding runtime/memory analyses and codeword utilization studies, and tightening fairness in initialization/HPO protocols.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The Limitations section acknowledges hyperparameter overhead (t, K, and separate learning rates) and limited large-model experiments due to compute. I agree and would add:
  - The approach may encourage per-task hyperparameter and initialization sweeps that are costly and complicate fair comparisons.
  - As with other PEFT methods, task-specific prompts may inadvertently encode dataset artifacts or biases. Although datasets are standard, there is no explicit bias or fairness analysis; a brief reflection on potential prompt-induced biases and mitigations would be beneficial.
  - Dual-use risks are typical of adaptation methods; guidance on responsible use is not discussed but could be mentioned.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in protocol. Many details and search spaces are provided; code availability is not stated.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.