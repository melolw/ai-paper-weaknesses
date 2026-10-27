# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes a two-step framework for financial numerical reasoning on FinQA and ConvFinQA. Step 1 is an ensemble retrieval pipeline: two instruction-tuned retrievers (FLAN-T5-Large with LoRA and Mistral-7B-Instruct with LoRA) extract relevant facts from long financial tables and text; a BART-large “ensemble” model fuses their outputs, followed by a sentence-level matching step against the original context using Sentence-BERT. Step 2 performs answer computation by prompting GPT-4 with Program-of-Thought (POT) exemplars and executing the produced Python via SymPy. In-context exemplars are selected dynamically using a retrained PromptPG policy, seeded with cluster-based diverse candidates. The method reports new SOTA execution accuracy on FinQA (75.67) and ConvFinQA (82.15), with analyses and ablations on retrievers, question types, exemplar selection, and k-shot sensitivity.

## Summary Of Strengths
- Clear overall architecture and motivation. Figure 1 concisely depicts the pipeline end-to-end, including the dual retrievers, the BART ensemble, PromptPG policy for example selection, POT prompting, and SymPy execution. The diagram helps readers understand how retrieval improvements are intended to reduce grounding errors typical in PoT prompting.
- Strong empirical results. Table 1 shows consistent gains over strong baselines, including APOLLO (current SOTA in long-form financial reasoning). The margins are substantial: +6.47 points on FinQA and +4.30 on ConvFinQA execution accuracy.
- Careful retriever analysis. Table 2 provides quantitative comparisons of “cosine similarity” to gold facts, “numerical coverage,” and “average words,” highlighting how Mistral is more inclusive but noisier, FLAN-T5 is closer to gold but sometimes incomplete, and the ensemble balances both. This directly supports the claimed motivation for ensembling.
- Ablations that isolate contributions. Table 3 shows that each retriever plugged into the same generator leads to different end accuracies, with the ensemble best. Table 5 demonstrates that dynamic in-context example selection and ordering matter, improving over static, random, and hybrid approaches.
- Useful qualitative error taxonomy with concrete examples. The appendix (Figures 5–13) provides instructive cases of wrong ground truth, logical/grounding errors, and retrieval misses, helping readers reason about remaining failure modes and devise follow-ups.
- The k-shot sensitivity analysis (Figure 3) is informative; both datasets benefit from 4-shot settings selected by the learned policy, consistent with the method’s design.

## Summary Of Weaknesses
1) Clarity and completeness around training data usage/splits for PromptPG and ensemble training
- Section 3.3.1 describes training PromptPG with rewards computed against ground truth answers but does not explicitly state that only training data were used to learn the policy nor how dev/test are guarded during policy learning. Given that GPT-4 is used “in the loop,” even inadvertent tuning on dev/test would inflate numbers. Please specify the exact split used at each stage for both FinQA and ConvFinQA, including whether any retrieval or policy hyperparameters were selected on test.
- Section 3.2.2 trains the BART ensemble to produce GTFact; please clarify precisely what constitutes GTFact in each dataset and how it is derived. FinQA annotations differ in granularity across works; do you use the original evidence sentences, the “supporting facts” provided by the dataset, or program-step surfaces? The cosine-similarity metric relies on this choice.

2) Evaluation scope limited to execution accuracy and self-defined retriever metrics
- While execution accuracy is standard, additional evidence-level evaluation would make the retrieval claims more convincing. For instance, evidence F1/precision/recall against annotated supporting facts (when available) or human assessment of factual sufficiency for a sampled subset. Table 2’s “cosine similarity” and “numerical coverage” are helpful but somewhat proxy measures. This matters because the principal contribution is a better retriever/ensemble.
- No program accuracy or step accuracy is reported. Since errors in Figures 8–12 are predominantly program/grounding issues, program-level diagnostics could better illuminate where the method helps or hurts.

3) Reproducibility risks due to GPT-4 dependence and underspecified prompts
- The main gains hinge on GPT-4 POT prompting with dynamic exemplars. The exact prompt templates are only partially visible in Figure 2, and crucial generation details are missing: temperature, top-p, stop sequences, max tokens, retry or self-consistency settings, and SymPy sandbox controls. Without these, reproducing the numbers will be difficult and the stability of results unknown.
- API-based randomness can lead to variance; no multiple-run variance or significance testing is reported for Table 1 or Table 3. At a minimum, include one or two repeated runs to gauge robustness.

4) Long-context handling and preprocessing are under-specified
- Section 3.2 describes passing “text and tables” to FLAN-T5 and Mistral. What are the maximum input lengths used for each model? What chunking/windowing heuristics or table linearization method is used (beyond “TabText”), and how are large 10-K contexts pruned? The sentence-matching step at the end of Section 3.2.2 implies post-hoc repairs, but the details of earlier truncations are not reported. Since retrieval is the paper’s core contribution, the context construction procedures should be explicit.

5) Fairness of baseline comparisons and absence of significance testing
- Table 1 compiles results from multiple sources and model families. For Program-of-Thought, you do not report GPT-4 + POT on FinQA/ConvFinQA (Appendix A.3 cites difficulty reproducing others’ numbers). Since your generator is GPT-4 with POT, the most relevant comparison is fixed-POT with GPT-4 using the same final prompt format but static exemplars and without ensemble retrieval. The ablations in Table 5 partially address the exemplar piece, but not the retrieval-vs-full-context effect with GPT-4.
- APOLLO “with our strategy” in Table 3 is an important hybrid baseline, but details are sparse. How were APOLLO’s retrieved passages converted to your final prompt and SymPy code path? Were any retuning steps performed? Reproducible scripts would strengthen this point.

6) Metric interpretation and claims
- Section 7 argues that lower numerical coverage can still yield higher accuracy due to reduced confusion. This is plausible, but it also suggests the coverage metric may not be a meaningful proxy. Consider reporting a “precision of numbers actually used by the final program” or an overlap against program arguments to assess relevance, not just presence.
- Table 4 reports perfect accuracy on boolean FinQA questions (20 items). Given small sample size, adding confidence intervals or exact counts for each category would avoid overinterpretation.

7) Limited generalization claims
- The method is evaluated on two datasets within one domain. The Limitations section acknowledges no tests on GSM8K, AQuA, TaTQA, or other hybrid/table-text datasets. Since the key idea is ensemble retrieval plus adaptive few-shot PoT prompting, readers will reasonably ask whether this transfers beyond finance reports. Even a small-scale sanity check on one non-financial dataset would help support generality.

8) Compute and cost considerations
- Section 6 lists hardware and some LoRA settings, which is good. However, there is no reporting of GPT-4 query counts, average context lengths, or overall monetary cost. Given the heavy dependency on GPT-4, transparency here matters for reproducibility and practical adoption.

9) Minor notation and formulation clarity
- Equation (1) notation says e_i^k ~ pi_theta(e_i | p_i) and “e_i^k are independent,” but the policy outputs a K-sized set; are samples drawn without replacement? Is there masking to prevent duplicates? Also, is the policy conditioned on retrieved facts or only on the question text? Clarify the policy’s input state used by PromptPG.

Figure- and Table-specific comments
- Figure 1: The architecture diagram is a strength; it explicitly shows that the ensemble prompt fuses “FLAN-T5 Retrieved” and “Mistral Retrieved,” and then uses Sentence-BERT matching before passing to GPT-4 via the “Final Prompt.” This visually supports the paper’s claim that ensembling reduces grounding errors by curating a more focused context. It would help to annotate approximate token budgets for each block to clarify how long contexts are managed.
- Figure 2: The exemplars show POT style for both single-turn (FinQA) and conversational (ConvFinQA) cases. However, the figure also reveals partial/incomplete “probable relevant facts” in the first example, mirroring the issues you discuss for FLAN-T5 vs. Mistral. It would be useful to show one example before and after the BART ensemble to concretely illustrate the factual consolidation.
- Figure 3: The k-shot analysis indicates a clear peak at 4-shot for both datasets. This supports the design choice to learn an exemplar policy. Please add error bars or exact counts to indicate variance across runs.
- Table 1: The main results table is central to the paper’s claim. Since many baselines are reported from prior work, present your own re-runs for at least GPT-4 with fixed few-shot POT under your prompt format to isolate the gains of ensemble retrieval and dynamic exemplars.
- Table 2: This table is critical to the ensemble motivation. The ensemble’s highest cosine similarity with gold facts and the shortest average output length align with the “less but relevant” narrative. Adding a precision-oriented metric (e.g., fraction of retrieved numbers actually used by the executed program) would concretely validate the “less confusion” claim.
- Table 3: The ablation supports that each retriever materially affects final accuracy, with ensemble best. Please add statistical testing or report multiple seeds to demonstrate stability.
- Table 4 and Table 5: These are helpful breakdowns. For Table 5, the “reverse ordering” result strengthens the importance of positioning the strongest exemplar last; consider discussing whether the policy explicitly optimizes for order, or if ordering is a heuristic post-processing step.

## Potentially Missing Related Work
1) Tang et al., “FinMMR: Make Financial Numerical Reasoning More Multimodal, Comprehensive, and Challenging,” 2025 — Introduces a broader, multimodal benchmark for financial numerical reasoning with multi-step computation. It is directly relevant for evaluating whether ensemble retrieval plus adaptive PoT generalizes beyond FinQA/ConvFinQA; discuss in Related Work and consider as a future evaluation target in Section 9–11.
2) Tang et al., “FinMMDocR: Benchmarking Financial Multimodal Reasoning with Scenario Awareness, Document Understanding, and Multi-Step Computation,” 2025 — Focuses on realistic long financial documents and multi-step computations, highly aligned with your retrieval-plus-generation pipeline. Cite in Section 2 and discuss how your retriever would scale to scenario-aware, long-context settings.
3) Du et al., “Enhancing Financial Reasoning via Program-of-Thought Learning,” 2026 — Presents a PoT training framework tailored to financial numerical reasoning (e.g., SFT + RL with executable programs). It is a natural baseline/contrast to your prompting-only approach; add to Section 5 and discuss whether combining with your retrieval would be synergistic.
4) Wang et al., “Document-Level Numerical Reasoning across Single and Multiple Tables in Financial Reports,” 2026 — Proposes FinLongDocQA and a long-context agent with multi-round RAG for financial QA. This is directly comparable to your ensemble retriever; include in Section 2 and discuss in Section 7 as an alternative long-context strategy.
5) Zhang et al., “Integrating Domain Knowledge for Financial QA: A Multi-Retriever RAG Approach with LLMs,” 2025 — Multi-retriever RAG on FinQA targeting similar error modes. It should be discussed as a close baseline in Section 5 and referenced around Table 3 as an alternative ensembling paradigm.
6) FinanceReasoning: “Make Financial Numerical Reasoning More Credible, Comprehensive, and Challenging,” 2025 — Aggregates and hardens financial numerical reasoning benchmarks with Python solutions. Comparing on this benchmark could verify robustness; mention in Section 4 or 7 as a broader evaluation bed.
7) Abdallah et al., “MoCA-Agent: A Market-of-Claims Code Agent for Financial and Numerical Reasoning,” 2026 — A code-synthesis and verification approach that addresses reliability of numerical programs, relevant to your SymPy-based execution stage. Discuss in Section 2 and compare conceptually with your example-selection policy.
8) Bikov et al., “Financial Data Analysis with Fine-tuned Large Language Models,” 2025 — Examines fine-tuning paradigms for financial QA, contrasting with your prompt-based approach. Cite in Related Work to position your choice of instruction-tuned retrievers plus GPT-4 generator.
9) FLaME: Finance Language Model Evaluation, 2025 — A comprehensive evaluation suite including FinQA/ConvFinQA; referencing it would contextualize your gains under unified protocols.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Please detail data splits and protocols for each training stage: FLAN-T5/Mistral LoRA fine-tuning, BART ensemble training, and PromptPG policy learning. Explicitly confirm that no dev/test leakage occurred for policy learning or prompt refinement.
- Provide the exact GPT-4 prompting parameters and templates, including sampling settings, token limits, stop criteria, and any self-consistency or retry logic. Share prompts in the repo if possible. Report average and variance over at least two independent runs for Table 1 and Table 3.
- Expand long-context preprocessing details: maximum input lengths, chunking and selection strategy, and table linearization format (“TabText”). Include statistics on average context size before and after the Sentence-BERT matching step.
- Add evidence-level metrics or a small-scale human evaluation to substantiate retrieval quality claims beyond cosine similarity and numeric coverage. Also consider a precision-of-used-numbers metric tied to the executed program.
- For Table 5, clarify whether the learned policy also decides ordering, or whether you sort by score post hoc. If the latter, consider adding a policy that outputs a permutation.
- Consider including a fixed GPT-4 POT baseline under your exact prompting scheme but without ensemble retrieval or without dynamic examples, to isolate the contribution of each component cleanly within the same generator.
- Report GPT-4 cost and call counts to help the community assess practicality.
- Minor typos:
  - Page 3, “We refer FLAN-T5-Large and Mistral-7B Instruct v0.2 as FLAN-T5 and Mistral” → “We refer to … as …”
  - Figure 2 captions contain minor formatting issues (e.g., stray line breaks, missing punctuation).
  - Page 5 “consisting 14,115” → “consisting of 14,115”.

What could change my evaluation:
- A clarified, leakage-free protocol for PromptPG and ensemble training; full prompt details and reproducible scripts; and a fixed GPT-4 POT baseline under your exact setup that narrows attribution of gains to the proposed retrieval and dynamic exemplar selection. Evidence-level metrics or human assessment for retrieval quality would also strengthen the paper.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: The approach is technically solid with good analyses, but evaluation design could be more comprehensive (evidence metrics, variance, fixed GPT-4 POT baseline).

## Excitement
3.5 Between interesting and exciting: The combination of ensemble retrieval and adaptive few-shot PoT for financial reasoning is timely and practically useful, with strong reported gains.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact. The method is well-motivated and empirically effective, with clear diagrams and ablations. Some evaluation and reproducibility gaps remain, but they appear addressable in a camera-ready.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges the financial-domain focus and lack of tests on broader benchmarks. Additional considerations:
- Heavy reliance on a proprietary API (GPT-4) raises reproducibility and accessibility concerns.
- Numerical reasoning in finance can have downstream impacts if deployed without safeguards; errors like those in Figures 8–12 (unit handling, sign conventions) could mislead analysts. The paper’s use of SymPy helps, but incorporating unit-aware checks or post-verification would mitigate risks.
- Potential biases in financial disclosures and English-centric datasets may limit applicability across markets and languages; acknowledging linguistic and regional coverage would be useful.
Overall, a more explicit discussion of deployment safeguards and error handling in real financial workflows would strengthen the societal impact section.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: Code link is provided; LoRA training details for retrievers and ensemble are adequate. However, missing GPT-4 prompt/generation specifics and no variance reporting make exact reproduction challenging.

## Datasets
1 No usable datasets submitted. (No new datasets are introduced; existing FinQA/ConvFinQA are used.)

## Software
4 Useful.: I would recommend the new software to other researchers or developers for their ongoing work. (Assuming the anonymous repository includes training/inference scripts for retrievers and ensemble; adding full GPT-4 prompts and run scripts would move this closer to 5.)