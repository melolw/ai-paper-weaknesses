# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper studies multimodal chain-of-thought prompting for structured reasoning tasks and proposes visual Chain-of-Thought (v-CoT). v-CoT decomposes inference into three steps: first extract task-oriented propositions from the image, then reason over these propositions with the task text, and finally produce the answer. The authors evaluate prompting-only and instruction-tuned variants across four benchmarks: MathVista (math with visual context), ChartQA (chart understanding), ARC (abstraction and reasoning over grids), and Spider (NL-to-SQL with tables rendered as images). Results suggest consistent improvements of v-CoT over vanilla prompting and over multimodal CoT (m-CoT), with analyses of successes and failures.

## Summary Of Strengths
- Clear idea: structuring the first step of multimodal reasoning as proposition extraction that is task-conditioned, then using these propositions as axioms in subsequent reasoning. The definitions in Section 3 (Definitions 3.1–3.5) help precisely communicate the intended abstractions.
- Breadth of evaluation across four distinct structured-reasoning settings, spanning numeric reasoning, vision–data analysis, program synthesis (SQL), and pattern extrapolation. Table 1 and Figure 4 clarify task scope and outputs.
- The prompting formulation is explicit and easy to follow; Figure 3 nicely juxtaposes v-CoT against m-CoT and makes the added proposition step tangible. This is helpful for practitioners who want a lightweight method without retraining a model.
- Quantitative improvements are reasonably consistent across models and settings. Table 3 shows v-CoT beats both CoT and m-CoT on most datasets for both inference-only and fine-tuned models (e.g., GPT-4V inference: ChartQA 79.2 vs. 75.6 m-CoT; Spider 86.2 vs. 84.3; MathVista 49.1 vs. 47.5).
- The analysis on reasoning quality, especially Figure 5, is useful: separating correctness of reasoning vs. correctness of final answer provides insight into where v-CoT helps and where it fails.
- Ablation study (Table 4) is informative: proposition extraction pretraining and program-analysis propositions contribute substantially, which supports the paper’s central claim that structured propositions are the key lever.

Specific comment referencing figures/tables:
- Figure 2 usefully contrasts m-CoT and v-CoT on the same math-graph task, and the color-coded rationale highlights where m-CoT drifts. This figure concretely supports the claim that proposition-first steps reduce early hallucinations and guide the model toward correct local deductions.
- Table 3 is the core evidence for the main claim. Improvements are largest where perception errors are frequent (e.g., ChartQA), suggesting that the proposition step mitigates perception-to-reasoning entanglement.

## Summary Of Weaknesses
1) Data leakage risk in training data generation (Section 3.2). For both proposition generation and reasoning-path generation, the target answer A is explicitly provided to the model to construct propositions and rationales. This makes the resulting 5-tuples potentially answer-conditioned. Even after “proposition refinement,” there is a risk of encoding spurious cues correlated with the answer into the propositions or reasoning text. As a result, the instruction-tuned models may implicitly learn to reverse-engineer answers from such cues. This undermines the causal interpretation of the reported gains and complicates claims about “reasoning” rather than exploiting supervision artifacts. An ablation where the data generation forbids access to A would be critical.

2) Incomplete and sometimes inconsistent reporting of experimental details limits reproducibility and interpretation.
   - Training details for instruction tuning are missing: model variant(s) used, exact architecture settings, hyperparameters, optimizer, batch size, number of steps/epochs, learning rates, data mixture ratios for the multiple corpora in Table 2, and compute budget are not reported.
   - It is unclear what exact metric defines “task success rate” for Spider (exact string match? execution accuracy? component F1?). For ARC, how are outputs compared (exact pixel equality)? The paper should precisely define evaluation criteria per dataset.
   - No statistical significance tests or confidence intervals are provided for Table 3 or Table 5, although many reported deltas are small (e.g., +1.1 to +2.0 points). This is especially important given that for each dataset only 20% of tasks were used (Section 8).
   - There is an internal inconsistency: for ARC, GPT-4V+v-CoT shows 51.2 in Table 3 (inference), yet in Table 5 the corresponding value is 40.5. Please reconcile these or explain the different conditions.

3) Use of proprietary models as core components. A large part of the results rely on GPT-4V and gpt-4-turbo, and the proposition/chain generation also leans on InstructBLIP plus GPT-4. Without releasing the generated 5-tuples, prompts, and exact inference parameters (e.g., temperature, sampling top-p, number of samples per question), the work will be difficult to reproduce and compare against.

4) Scope of baselines and recent related methods. The paper compares to m-CoT and text-only CoT/PoT with captioning, but there are other visual-CoT style or staged/verified reasoning pipelines that should be discussed and, when feasible, compared.
   - For example, Visual CoT prompting with see–think–confirm pipelines; reinforcement fine-tuning methods that explicitly target visual reasoning steps; and interleaved visual–textual rationales could change the competitive landscape. The Related Work section is brief and does not fully position v-CoT relative to these contemporaneous approaches.

5) Limited ablation breadth and missing controls weaken causal claims.
   - Table 4 examines removing pretraining objectives and proposition sources on Llava, but there is no “no-proposition” control under the same instruction-tuning setup that keeps training size constant while removing Step (1). The current comparison to m-CoT confounds the effect of proposition extraction with different prompt formats and possibly different output lengths.
   - For the prompting-only setting, a control that forces m-CoT to output bullet-pointed “observations” before free-form rationale, but without the structured e/p/v schema, would help verify whether it is the structure of propositions or just an intermediate “perception” step that matters.

6) Evaluation design choices increase the chance of dataset-specific overfitting or optimistic measurement.
   - Only 20% of each benchmark is used (Section 8), purportedly uniformly sampled; but sample statistics and seed details are not given. As Figure 6 and Figure 7 show, many examples hinge on precise numeric extraction; sample composition could sway overall rates. It would be more convincing to evaluate on the official full test splits or at least report variance across multiple random subsamples.
   - For Spider, the setup restricts to single-table tasks and renders up to 50 rows as images. This changes the task distribution and may conflate visual token-efficiency with differences in content exposure. As Figure 9b shows, constant strings remain hard to read from images, which raises questions about real-world applicability versus a carefully chosen simplified subset.

7) The proposition formalism, while elegant in Definitions 3.2–3.5, is not operationalized rigorously.
   - There is no precision/recall measure for proposition extraction quality, nor an analysis of how errors in P_T affect downstream accuracy. A sensitivity study where noise is injected into P_T would strengthen the argument that structured propositions causally improve reasoning robustness.
   - The boundary between “captioning” and “task-oriented proposition extraction” is asserted but not quantified; for example, in Table 2, Len(P′) is given in characters, yet there is no breakdown by proposition types or conformity rates to the {e,p,v} schema.

8) Clarity issues and minor inconsistencies.
   - Missing cross references: Section 3.4 says “Figure ??” for the prompt structure; this should be Figure 3.
   - Section 5.3 references “Table ??” for ablations; should be Table 4.
   - Some phrasing suggests generalization beyond the demonstrated scope, especially for ARC where Table 3 shows very large relative gains but Figure 8 and Section B.3 still show fundamental perception errors; temper claims accordingly.

Figure- and table-specific critiques:
- Figure 3 is central but the exact tokenized templates and allowed formats for propositions are not specified beyond the conceptual description. Practitioners would benefit from seeing 2–3 concrete proposition examples per dataset inline with the figure.
- Figure 5 shows reasoning-vs-answer correctness bars but does not provide counts or CI; it is hard to gauge reliability. Given manual annotation of 100 samples per dataset, please add error bars and inter-annotator agreement if multiple annotators were involved.
- Table 2 lists character lengths but not per-dataset variance; more granular stats (e.g., average number of propositions per task, proportion adhering to the triplet schema) would make the “structured” claim more concrete.
- Table 3 is the main result; please reconcile with Table 5 for ARC and specify exact success metrics and evaluation scripts used per dataset.

## Potentially Missing Related Work
1) Chen et al., “Visual Chain-of-Thought Prompting for Knowledge-Based Visual Reasoning,” 2024 — Presents a staged see–think–confirm visual CoT pipeline highly aligned with the paper’s v-CoT design. It should be discussed in Section 2 (Related Work) and compared methodologically to v-CoT’s proposition-first step; if possible, include as a conceptual baseline or at least a detailed comparison after Figure 3.

2) Mu et al., “EmbodiedGPT: Vision-Language Pre-Training via Embodied Chain of Thought,” 2023 — Demonstrates that CoT over visual inputs improves structured, long-horizon tasks in embodied settings. While the domain differs, it supports the central claim and should be discussed in Section 2 to better situate the contribution.

3) Dong et al., “Insight-V: Exploring Long-Chain Visual Reasoning with Multimodal Large Language Models,” 2025 — Proposes a multi-agent framework and data pipeline for long-chain visual reasoning. Add to Section 2 and discuss how v-CoT compares to longer-horizon visual reasoning mechanisms; consider reporting on overlapping benchmarks if feasible.

4) Tan et al., “Reason-RFT: Reinforcement Fine-Tuning for Visual Reasoning,” 2025 — Uses GRPO-based RL to improve visual reasoning after supervised CoT. Cite in Section 2 and contrast in Section 5, highlighting the trade-offs of prompt-only v-CoT vs. heavier RL-based tuning.

5) Gu et al., “ThinkMorph: Emergent Properties in Multimodal Interleaved Chain-of-Thought Reasoning,” 2026 — Interleaves visual and textual thoughts, an alternative to v-CoT’s perception-then-reason pipeline. Include in Section 2 and discuss implications for tasks like ARC that may benefit from interleaved perception.

6) Li et al., “VisReason: A Large-Scale Dataset for Visual Chain-of-Thought Reasoning,” 2026 — A dataset with explicit visual-CoT annotations; could be a useful benchmark to further validate v-CoT. Mention in Section 2 and the Conclusion as future evaluation.

7) Wu et al., “Better Eyes, Better Thoughts: Why Vision Chain-of-Thought Fails in Medicine,” 2026 — An analysis paper on failure modes of visual CoT. Cite in Section 6/Limitations to contextualize failure patterns observed in Figures 6–8.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide a data-leakage-free variant of the v-CoT training pipeline where neither propositions nor reasoning paths are generated with access to the gold answer. Report the delta to isolate how much of the gain comes from supervision artifacts.
- Precisely define the evaluation metrics and scripts per dataset. For Spider, specify whether exact-match, execution accuracy, or component-level scores are used. For ARC, define the grid-comparison protocol. Add statistical significance (e.g., bootstrap CIs) to Tables 3 and 5.
- Expand training details: model architecture(s) for instruction-tuned variants, hyperparameters, schedule, dataset mixture, and compute. Include prompts, decoding parameters, and the exact proposition schema with several fully worked examples per dataset.
- Reconcile the ARC discrepancies between Table 3 and Table 5, and explain the sampling protocol and seeds for the 20% subsets. If feasible, include full-test results or multiple random subsamples with mean±std.
- Strengthen ablations: add a “no propositions, same training size” control; a “bullet observations without triplet structure” prompt control; and a noise-sensitivity study on P_T. Also report proposition precision/recall against program-derived ground truth for ChartQA and SQL subsets.
- Release the generated 5-tuples, prompts, and code. If releasing the proprietary outputs is impossible, provide a fully open alternative pipeline with open models and report corresponding numbers.
- Tone down generalization claims on ARC; supplement Figure 8 with quantitative error-type distributions and a discussion on how v-CoT could be adapted, e.g., interleaving perception and reasoning steps.

Typos and clarity:
- Section 3.4: “Figure ??” should be “Figure 3.”
- Section 5.3: “Table ??” should be “Table 4.”
- Page 3: “Now that we have defined key high-level components, we proceed to define v-COT” — consistent casing: v-CoT.
- Minor grammar (e.g., Page 2 “vanillamodels” -> “vanilla models”; Page 2 “not able find” -> “not able to find”).

What could change my assessment:
- A leakage-free training pipeline with consistent gains, plus clarified metrics, full experimental details, and reconciled tables would significantly raise Soundness and Reproducibility. If these are addressed, I could raise to 3.5–4.0 depending on results.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
3.0 Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there’s time.

## Overall Assessment
3 Findings: This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The central idea is clear and practically useful, and results are promising across multiple datasets. However, answer-conditioned data generation, missing experimental specifics, and limited ablations lower confidence that the reported gains strictly reflect better “reasoning” rather than supervision artifacts. With stronger controls, clearer metrics, and improved reproducibility, this could move toward main conference quality.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section acknowledges partial sampling, potential ground-truth noise, and English-only scope. Additional points to discuss:
- Reliance on proprietary models and answer-conditioned data generation raises transparency concerns and may inadvertently promote “reasoning-like” artifacts. Clarify risks of over-claiming reasoning capabilities and how proposition hallucinations can mislead users, especially in high-stakes domains.
- Visual datasets like charts can encode demographic or policy-relevant statistics; misinterpretations could lead to improper conclusions. Consider guidelines or uncertainty reporting for numerical extractions.
- For code generation (SQL), erroneous queries against sensitive databases could have downstream harms if automated. Emphasize human-in-the-loop validation.

## Ethical concerns
None.

## Needs Ethics Review
No

## Reproducibility
2.5 Reproducible with difficulty: They could reproduce the results with some difficulty. The settings of parameters are underspecified or subjectively determined, and/or the training/evaluation data are not widely available.

## Datasets
2 Documentary: The new datasets will be useful to study or replicate the reported research, although for other purposes they may have limited interest or limited usability.

## Software
2 Documentary.: The new software will be useful to study or replicate the reported research, although for other purposes it may have limited interest or limited usability.