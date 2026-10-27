# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies catastrophic forgetting of linguistic capabilities when turning a pretrained text-only LLM into a multimodal LLM following the LLaVA 1.5 recipe. The authors treat MLLM construction as a continual learning (CL) problem where task 1 is the pretrained LLM’s NLU/NLG ability and task 2+ are vision–language (VL) tasks. They benchmark nine base LLMs (mainly Pythia family, plus Phi-2 and LLaMA-2/Vicuna) and evaluate five mitigation strategies: naive fine-tuning, LoRA, soft targets, mSGM (a variant of SGM without classifier freezing), and rehearsal. The main finding is that soft targets reduce linguistic forgetting while largely maintaining VL performance in the two-task LLaVA setting, and that mSGM (+/- rehearsal) is the strongest in the sequential VL task setting. They report that forgetting is more severe for NLG (Lambada) than for NLU benchmarks and analyze scaling trends across model sizes. 

## Summary Of Strengths
- Clear framing of “LLM-to-MLLM” as a continual learning problem with concrete methods from the CL literature. The paper organizes the space into rehearsal vs. regularization and selects scalable variants appropriate for LLaVA-style training.
- Breadth of base models and settings: nine LLMs (Pythia 0.16B–2.8B, Phi-2 3B, LLaMA-2/Vicuna 7B), and two training regimes (single LLaVA mixture vs. sequential VL tasks). This gives the results reasonable ecological validity across small-to-mid scales where forgetting is most acute.
- Useful, reproducible details: optimizer and training schedules, FSDP use, LoRA target layers and rank/alpha sweeps (Table 6), alpha sweeps for soft targets (Table 7), and dataset preparation and “slim” evaluation protocol are all described in the appendix.
- Several figures and tables directly support claims:
  - Figure 2 (scatter) compactly shows the trade-off between VL performance and linguistic forgetting across nine MLLMs; five show positive forgetting, four show negative forgetting (backward transfer), supporting the claim that outcomes vary by base model and scale.
  - Figure 3a/3b demonstrates the central result: soft targets largely match naive FT on VL accuracy while strongly reducing forgetting across Pythia scales; the linguistic forgetting curve in Figure 3b is near zero/negative for soft targets at all sizes, unlike naive FT which forgets sharply for smaller models.
  - Figure 4a/4b (continual setting) shows mSGM + rehearsal maintains competitive VL performance while preventing the steady rise in forgetting that naive FT exhibits as tasks accumulate; the contrast is particularly notable at 1B scale where backward transfer is achieved.
  - Table 3 (Pythia-160M) provides a concrete, controlled comparison across methods, with soft targets delivering the highest VL average and the least forgetting among non-rehearsal approaches in the LLaVA recipe.
  - Figure 5 and Table 1 substantiate the claim that NLG forgetting (Lambada) is consistently worse than NLU, an insight likely to matter for future recipe design.
- The paper is clearly written overall, with a practical audience in mind, and provides concrete implementation choices that other groups can adopt immediately.

## Summary Of Weaknesses
1) Limited evaluation scope and metric choices may diminish the strength of the conclusions.
- Only one NLG dataset (Lambada) is used, and all metrics are accuracy. Lambada’s accuracy is a coarse signal for generation quality; other widely used NLG tasks (e.g., CNN/DM, XSum, GSM8K for reasoning, MMLU for knowledge) could change the picture. The paper itself emphasizes stronger forgetting on NLG, so focusing on a single NLG task risks overinterpreting a narrow proxy. This matters because the headline conclusion “NLG forgets more” rests on a single dataset.
- The VL evaluations rely on “slim” 1,024-example test subsets rather than full test sets. While explained for tractability, this may produce variance and distribution mismatch relative to standard reporting, especially for tasks like GQA and RefCOCO where fine-grained compositionality or grounding nuances may show up only at scale.

2) Missing or underdeveloped baselines for CL in MLLMs and regularization-based forgetting mitigation.
- The method suite omits several strong, directly relevant CL baselines for MLLMs that do not require storing past data, such as gradient orthogonalization and distillation-style regularization beyond label smoothing. For instance, no explicit comparison to EWC/SI/KD-style regularizers is presented, even though they are lightweight and standard in CL. This weakens claims that soft targets/mSGM are the most appropriate scalable regularizers.
- The paper cites VILA but does not reproduce a variant that includes text–image interleaved corpora as a control for the “train data composition can mitigate forgetting” hypothesis. Given that VILA is the one prior that claims to reduce forgetting via MMC4-style data, this is a conspicuous gap.

3) Incomplete positioning vs. rapidly growing literature on continual MLLM training.
- Several closely related works proposing continual instruction tuning or modality/task-shifting settings for LLaVA-style models are not discussed or contrasted experimentally (see “Potentially Missing Related Work”). This affects how the contribution is situated, especially for the sequential-VL setting in Section 4.3.

4) Ambiguities in reporting and a few editorial errors reduce clarity.
- Table 2 references “Table ??” in the text on Page 5 and the table formatting is inconsistent; the row/column headings are confusing, and the “Instr.” column and symbol usage (✕) are unclear. This table underpins the instruction-tuning analysis; it needs fixing.
- The claim “reduces linguistic performance degradation by up to 15%” (Abstract) is not tied to a specific figure/table, metric, or base point in the main text. If this is relative reduction in Δ or absolute accuracy recovery, please specify precisely where it occurs.
- In Table 4 (continual setting), Task 2 “Instruct” shows VL A ~0 for most methods, but the paper notes that Task 2 contains no overlapping “academic” VL datasets; indicate explicitly in the caption or text that Task 2 VL scores are expected to be near zero and should not be compared head-to-head to later tasks.

5) Design choices limit generality of the conclusions.
- Only one alignment/training protocol (LLaVA 1.5) and one frozen visual encoder are considered. The conclusion that soft targets dominate over other scalable methods may depend on this recipe. Alternative fusion layers or cross-attention integration strategies might interact differently with forgetting.
- Training for one epoch in both alignment and fine-tuning stages is consistent with LLaVA 1.5, but this can undertrain models on several VL datasets, which the authors also acknowledge. Since forgetting depends on the stability–plasticity trade-off, short schedules could bias outcomes toward or against specific methods.

6) The rehearsal setup is not fully representative.
- Rehearsal stores 1% or 10% of prior VL data but, by design, excludes Task 1 (text pretraining), which is precisely the content most needed to directly mitigate linguistic forgetting. While the authors argue that Task 1 data is unavailable, an approximate rehearsal using publicly available text corpora that reflect the base LLM’s domain would be an informative control.

7) Statistical uncertainty and significance.
- The main tables and figures do not report standard deviations or confidence intervals for accuracy or Δ, nor do they discuss randomness across seeds. Especially with “slim” 1k-example test splits, variance could be nontrivial and should be quantified.

8) Limited analysis of failure modes and ablations beyond alpha and LoRA rank/targets.
- For soft targets, only α is tuned (Table 7). For mSGM, the omission of the original SGM’s initialization/freezing is reasonable here, but the effect of each component in the final mSGM recipe is not ablated. Figure 4 suggests strong results with mSGM + rehearsal, but it would help to disentangle which part contributes most to stability at different task transitions.

9) Societal implications and data governance are underdiscussed.
- The work relies on ShareGPT, COCO-based datasets, and instruction data that can encode demographic bias and PII risks. There is little discussion about data licensing or privacy considerations, nor about who might be negatively impacted if language skills degrade differentially across language varieties, dialects, or domains.

10) Figure/Table-specific critique and interpretation:
- Figure 2’s scatter is effective, but it would benefit from labeling each point directly with the model name/size to reduce back-and-forth with the legend; as is, the message is still clear: small Pythia models lie at high forgetting and lower VL accuracy, while Vicuna/LLaMA2 sit near zero or negative forgetting with higher VL accuracy.
- Figure 3b is the strongest empirical support for the paper’s advocacy of soft targets over naive FT: the forgetting line for soft targets hugs zero or below across scales, contrasting sharply with naive FT’s spike at small model sizes. This directly backs the claim in Section 4.2.
- Table 3 shows soft targets outperform naive FT for Pythia-160M on average VL accuracy (10.57% vs 5.29%) while slashing linguistic Δ (2.83 vs 7.83). This is a central piece of evidence; however, results are on slim sets and should be paired with variance estimates.
- Figure 4b clearly demonstrates escalating forgetting under naive FT over tasks 2–5, while mSGM+rehearsal remains near zero; paired with Figure 4a, it shows that stability does not come at a large cost to VL accuracy. This figure is persuasive for the sequential VL setting.
- Figure 5 breaks down NLU vs NLG forgetting and substantiates the “NLG is worse” claim visually; the Lambada bars dominate the forgetting signal, which motivates additional NLG datasets.

## Potentially Missing Related Work
1) Pian et al., “Modality-Inconsistent Continual Learning of Multimodal Large Language Models,” 2024 — proposes continual learning scenarios where both modality and task type vary over time; introduces methods using pseudo-targets and distillation. This is directly related to Section 4.3 and should be discussed in Background/Related and contrasted experimentally if feasible.

2) Qiao et al., “LLaCA: Multimodal Large Language Continual Assistant,” 2024 — continual instruction tuning method for LLaVA-1.5 that balances stability/plasticity via EMA and gradient-informed weighting. Highly comparable to your sequential VL setup. Please discuss in Section 2.2 and compare as a baseline if possible.

3) Liu et al., “Octopus: History-Free Gradient Orthogonalization for Continual Learning in Multimodal Large Language Models,” 2026 — a rehearsal-free technique that orthogonalizes gradients online. This belongs in Section 2.2 and should be acknowledged as a rehearsal-free alternative to consider in future comparisons.

4) Zhao et al., “MLLM-CL: Continual Learning for Multimodal Large Language Models,” 2025 — introduces a benchmark and parameter-routing methods for domain/ability continual regimes. Relevant to Section 4.3; please add to Related Work and discuss alignment/differences to your task grouping in Table 5.

5) Huai et al., “CL-MoE: Enhancing MLLM with Dual Momentum Mixture-of-Experts for Continual VQA,” 2025 — architectural alternative (MoE) for continual VQA. Add to Related Work and discuss whether such parameter-isolation designs could complement your soft targets/mSGM approach.

6) Ge et al., “Dynamic Mixture of Curriculum LoRA Experts for Continual Multimodal Instruction Tuning,” 2025 — proposes dynamic LoRA expert allocation under parameter budgets; directly relevant to your LoRA baselines in Sections 3.2 and 4.2. Discuss and, if possible, add as a baseline.

7) Guo et al., “MLLM-CTBench: A Benchmark for Continual Instruction Tuning with Reasoning Process Diagnosis,” 2025 — provides process-level diagnostics for continual instruction tuning. Consider for future evaluation beyond accuracy, especially for NLG forgetting analysis.

8) Huo et al., “When Continue Learning Meets Multimodal Large Language Model: A Survey,” 2025 — a broad survey contextualizing benchmarks and methods. Citing it would help position your contributions within the latest taxonomy of MLLM-CL.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Clarify and fix Table 2: explicitly show base vs instruction-tuned variants, define the “Instr.” column, and remove the stray “Table ??” reference. State clearly how Δ is computed and which datasets contribute to “NL Avg. Acc.”
- Tie the “up to 15%” improvement claim to a specific Figure/Table and define the metric precisely (absolute vs relative reduction, averaged over which tasks).
- Report variance: add standard deviations or confidence intervals for Tables 1, 3, 4 and for Figures 3 and 4, or at least multiple seeds. With 1k-example “slim” sets, error bars are important to judge stability.
- Broaden NLG evaluation: add at least one more text-generation benchmark with accuracy-like scoring (e.g., HellaSwag/PIQA for commonsense multiple choice, or a constrained exact-match dataset such as SciQ). Alternatively, include perplexity-based NLG signals on a held-out corpus and discuss how that correlates with Lambada forgetting.
- Consider a distillation baseline: use the base LLM as a teacher during multimodal fine-tuning (e.g., KL divergence on next-token distributions) as a rehearsal-free regularizer. This is directly comparable to soft targets and would strengthen the argument for your chosen regularization strategy.
- Discuss data governance: add a paragraph in Limitations or an Ethics/Societal Impact section about dataset licenses, potential PII in ShareGPT, and bias considerations, including concrete mitigations (e.g., filtering steps, usage compliance).
- Continuous task order sensitivity: you briefly note task sensitivity; please provide at least one alternative ordering or explain why the chosen order is representative, especially for OCR vs RefCOCO transitions where forgetting patterns in Figure 4b diverge.
- Failure modes: When soft targets underperform (e.g., in Table 4, Task 3 VL accuracy is very low for soft targets at 410M), analyze why. Is the label-smoothing effect suppressing learning when supervision is sparse or when answer formats vary (e.g., OCR)?
- Figures: In Figure 2, consider annotating points with model names to reduce legend lookup. In Figure 4a/4b, include a note in the caption clarifying that VL performance is near zero at Task 2 by construction, to avoid misinterpretation.

Typos/formatting:
- Page 5: “As shown in Table ??” should reference the correct table index.
- Page 6, left column: “their 12B parameter model lost 87.3%.” Add “on NLG/NLU” for clarity.
- Table 3 header is slightly misaligned, and the column ordering “VL Avg.Acc, NL Δ, NL Acc” could be clarified with units and definitions; similarly for Table 4, define A↑ and Δ↓ near the table.
- Consistently hyphenate “fine-tuning.”
- Ensure all acronyms (e.g., RSLoRA) are defined at first usage.

Criteria that could raise my score:
- Add at least one strong, rehearsal-free CL baseline beyond soft targets/mSGM (e.g., gradient orthogonalization or distillation from the base LLM) with multi-seed reporting.
- Expand NLG beyond Lambada and provide variance; or, alternatively, add a perplexity-based NLG assessment on a held-out corpus to corroborate the “NLG forgets more” claim.
- Fix reporting inconsistencies (Table 2; tie the “15%” claim to a specific result) and strengthen the discussion of task ordering and failure modes in the continual setting.

## Confidence
4: Quite sure after careful checking — I checked the main experimental claims, figures, and tables closely; some details such as variance and broader baselines are missing but the core is clear.

## Soundness
3: Acceptable — The methodology is sound overall and experiments support the central claims, but the evaluation scope is limited (single NLG benchmark, slim VL sets) and some strong CL baselines are missing.

## Excitement
2.5: Between potentially interesting and interesting — The framing is useful and the empirical takeaways are actionable for practitioners, but novelty is moderate and the evaluation is narrower than I would expect for the main track.

## Overall Assessment
2.5 Borderline Findings — The work is solidly executed and practically useful, but its novelty is moderate and the evaluation has notable gaps (single NLG dataset, slim VL test sets, missing rehearsal-free CL baselines). I recommend it for Findings after addressing clarity issues and adding a bit more experimental depth if feasible.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper discusses limitations regarding model sizes, single-recipe focus (LLaVA 1.5), and compute-driven constraints. Additional societal impact considerations would improve the paper:
- Data governance: ShareGPT and other instruction data may contain PII, copyrighted, or user-generated content with unclear licenses; clarify compliance and filtering.
- Bias and representation: The datasets are predominantly in English, and the methods could preserve or amplify existing biases; discuss what edge cases were observed and potential mitigations.
- Dual use: Stronger retention of language ability is generally positive, but consider scenarios where preserving misinformation or biased patterns could persist; recommend auditing steps when deploying CL-based updates.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible — Training/eval details are well documented, and code/weights are promised. Reporting multiple seeds and providing the exact slim splits used strengthen reproducibility.

## Datasets
1 No usable datasets submitted.

## Software
3 Potentially useful — The planned code and recipe releases will likely be useful to practitioners reproducing LLaVA-style training with CL methods.