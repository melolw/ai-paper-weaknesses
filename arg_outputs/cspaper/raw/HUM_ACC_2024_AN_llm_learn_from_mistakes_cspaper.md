# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper studies training methods for large language models to improve chain-of-thought reasoning on NLP benchmarks such as GSM8K, MATH, and CSQA, which squarely fits Machine Learning for NLP, Language Modeling, Reasoning, and Resources and Evaluation.

## Minimum Quality
Pass ✅. The submission contains Abstract, Introduction, Methodology (Sections 2.1–2.3 with Equations 1–3), Experimental Setup, Results and Analysis (Section 4 with multiple figures and ablations), Related Work, Conclusion, Limitations, and an Ethics Statement. The empirical setup is substantial across multiple models and tasks. I note a notable methodological weakness: Section 3.3 states that for QLoRA fine-tuning they evaluate all saved checkpoints on the test sets and report the best checkpoint, which risks test-set overfitting. I treat this as a significant weakness to be addressed in rebuttal and camera-ready, but I do not desk reject.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I did not detect any prompt-injection or manipulative instructions embedded in the paper content.

# Expected Review Outcome:

## Paper Summary
The paper investigates whether large language models can improve reasoning by learning from their own and other models’ mistakes. The authors construct mistake-correction datasets by: (i) sampling inaccurate CoT solutions from several LLMs, then (ii) prompting GPT-4 to identify erroneous steps, explain why they are wrong, and provide corrected reasoning. They fine-tune open models with either straightforward CoT training or with CoT plus mistake-correction supervision (LEMA). Across GSM8K, MATH, and CSQA, and multiple models and training regimes, LEMA improves accuracy, with ablations indicating that the textual explanations of mistakes contribute meaningfully. They further propose a correction-centric evolution strategy to scale data, showing additional gains, and analyze scaling behaviors under QLoRA vs full fine-tuning.

## Summary Of Strengths
- Clear problem framing with a concrete pipeline for constructing mistake-correction pairs. Figure 2 succinctly diagrams the collection of inaccurate chains, GPT-4 corrections, and the evolution loop; this helps readers follow the data flow and roles of the different models.
- Strong empirical coverage: results span five families of open models under both QLoRA and full fine-tuning, three core tasks, plus OOD evaluations (SVAMP, ASDiv in Appendix D.3). Table 1 is comprehensive and consistently shows LEMA outperforming CoT-only training across models and tasks; Table 2 further demonstrates additive gains when starting from specialized math LLMs.
- Insightful ablations on what matters in the correction signal. Figure 4 isolates the effect of including explanations and reasons for the mistakes, with consistent improvements across GSM8K, MATH, and CSQA. Figure 5 controls for data size and still shows LEMA’s advantage, strengthening the claim that the extra supervision is not merely more data.
- Useful methodological details: explicit prompts for correction generation (Figure 3), input-output fine-tuning formats (Figure 8), and quantitative analysis of correction success rates by difficulty (Figure 12). The ΔPPL metric in Equation 5 and Figure 13 is a nice proxy suggesting LEMA shifts likelihood away from mistaken chains relative to correct ones.
- The proposed correction-centric evolution is motivated and empirically supported: Figure 6 shows it outperforming general evolution on MATH, and Figure 7 reveals better scaling under full fine-tuning than under QLoRA.
- The paper is generally well written and organized; limitations and ethics are discussed candidly.

## Summary Of Weaknesses
1) Model selection on test data. Section 3.3 states that during QLoRA fine-tuning they “save checkpoints every 100 training steps” and “report the accuracy of the best checkpoint.” This implies selecting the best checkpoint on the test sets for each model, which biases reported numbers upward and undermines comparability. At minimum, a held-out validation split or cross-validation should be used for early stopping and selection. Although Appendix D.1 and D.2 provide variance and curves, this does not fully correct the leakage. Please re-run with a proper dev set and report single final checkpoints chosen without peeking at test.

2) Limited human evaluation of correction quality. The manual assessment in Section 2.1 covers only 50 corrections with 35 excellent, 11 good, and 4 poor. Given that training depends on tens of thousands of GPT-4-generated corrections, stronger sampling and inter-annotator agreement would increase confidence, and a study of error types would help link correction quality with downstream gains.

3) Heavy reliance on GPT-4 for both CoT augmentation and correction. Although common, the paper uses GPT-4 to (a) generate additional correct CoTs and (b) act as the corrector and evolution engine. This raises potential confounds: improvements may partially reflect implicit exposure to benchmark distributions. While the authors filter for correctness and discuss limitations, more controls would help, for example, repeating a subset with another corrector or using public verifiers to gate acceptance.

4) Missing or weak baselines that also exploit mistake data. Section 5 cites reflection and preference-optimization work, but the main comparisons use CoT-only SFT. The DPO baselines in Appendix D.4 are preliminary and limited to one backbone. Additional comparisons are needed, such as: (i) process supervision with verifiers trained on step-level correctness; (ii) error-detection-then-editing pipelines; (iii) reflection-based SFT that uses self-critique text as supervision. Otherwise, it is hard to attribute the advantage solely to explanation-level mistake supervision.

5) Statistical significance and uncertainty. Table 1 and Table 2 gains are mostly in the 0.4–3.4 point range, often within the variance that can occur across decoding or training runs. While Appendix D.1 reports three-best-checkpoint averages, this still uses test data for selection and lacks formal significance testing. Confidence intervals or bootstrap tests would improve scientific rigor.

6) CSQA setup is under-specified and potentially fragile. Section 3.1 and Appendix C.3 state that only 4 annotated CoT exemplars were created, then GPT-4 generated rationales over the entire training set. There is limited analysis of rationale quality, no ablation on prompt sensitivity, and no qualitative analysis of when corrections help commonsense versus math. Additionally, reporting dev-only results without a canonical test split leaves some uncertainty about generalization.

7) Evolution method lacks stronger baselines and cost analysis. While Figure 6 shows the correction-centric evolution beats general evolution on MATH, more detailed analysis is warranted: number of usable evolved items after filtering, cost per successful example, and how gains scale with quality vs quantity. A cost-performance frontier would be valuable, especially given the limitations section on expense.

8) Weak causal evidence for why explanations help. Figure 4 and Figure 5 suggest reasons-to-mistakes matter, but the paper would be stronger with controlled counterfactuals on explanation style, length, and specificity. For example, training on corrected chains with templated minimal corrections vs rich pedagogical commentary. Equation 4’s DPO variant in Appendix D.4 is informative, but more process-supervision baselines would sharpen the conclusion.

9) Limited failure-case analysis. Aside from Figure 12’s success rates by MATH difficulty, there is no thorough taxonomy of error types pre- and post-LEMA, nor breakdowns by operation types in GSM8K or by reasoning categories in CSQA. This would clarify which mistake patterns benefit most and where the method still fails.

10) Reproducibility and release readiness. The paper gives many training details and uses vLLM for inference, but it is unclear whether the full correction datasets and training code will be released with sufficient metadata. Given the centrality of the dataset, commitments here affect impact and reproducibility ratings.

Figure- and table-specific critiques:
- Figure 4 is central to the claim that explanations and reasons matter. However, the figure aggregates across models and tasks with no error bars, and the absolute margins are often small. Please include variability across seeds and report exact deltas on each bar.
- Figure 5 controls dataset sizes to 32K and 45K on GSM8K and shows LEMA outperforming CoT-only in matched-size settings. This is compelling, but note that Section D.5 indicates token counts still differ slightly. It would help to ensure length normalization or to show token-matched results on the same figure.
- Figure 6 compares general vs correction-centric evolution and shows consistent but modest gains. It would help to add a third baseline that evolves from randomly sampled questions matched by estimated difficulty, substantiating that “moderately difficult” selection is the operative factor.
- Table 1 is the main quantitative anchor. Improvements are consistent but modest on MATH; several models remain in low two-digit accuracy. A discussion on whether LEMA reduces reliance on self-consistency sampling or improves sample efficiency at inference would contextualize practical impact.
- Equation 4 introduces a modified DPO loss but the text does not report sensitivity to β and γ; additionally, these DPO results in Table 6 are for Mistral-7B only, not for the larger backbones used in Table 1.  
- Equation 5 and Figure 13 on ΔPPL are neat; still, correlating ΔPPL shifts with accuracy gains across checkpoints would strengthen the argument that the model truly prefers correct reasoning over similar but mistaken chains.

## Potentially Missing Related Work
1) Jiang et al., LLMs can Find Mathematical Reasoning Mistakes by Pedagogical Chain-of-Thought, 2024 — focuses on prompting that elicits error detection in solutions. Highly relevant to your correction-generation and filtering pipeline. Discuss in Section 2.1 as an alternative or complementary approach to using GPT-4 as a corrector, and in Section 5 to contrast correction quality and cost.

2) Yao et al., Learning From Correctness Without Prompting Makes LLM Efficient Reasoner, 2024 — proposes LECO, emphasizing accumulation of verified-correct steps rather than explicit error learning. Compare conceptual differences in Section 4.2 when interpreting Figure 4 and Figure 5, and consider adding as a baseline or discussion point.

3) Alazraki et al., LLMs can implicitly learn from mistakes in-context, 2025 — demonstrates in-context improvement from observing incorrect vs correct examples without explicit rationale. Add to Related Work to contrast in-context vs fine-tuning supervision and to motivate an evaluation that separates benefits from explicit explanations vs exposure to juxtaposed examples.

4) Pan et al., LEMMA: Learning from Errors for MatheMatical Advancement in LLMs, 2025 — introduces a framework very close in spirit to LEMA with explicit error-correction trajectories and taxonomy. It should be discussed in Related Work and possibly in Section 2.1 to position data construction choices and error categorization.

5) Di et al., Not All Negative Samples Are Equal: LLMs Learn Better from Plausible Reasoning, 2026 — analyzes how the quality of negative chains affects learning. Tie into Section 2.1 and 4.2; consider reporting statistics on the plausibility of mistaken chains used in your correction data and whether filtering by plausibility improves LEMA.

6) Ren et al., Learning from Failures: Correction-Oriented Policy Optimization with Verifiable Rewards, 2026 — a reinforcement-learning approach that reuses failed trajectories for correction-oriented learning. Add to Section 5 to contrast RL-based correction learning with your supervised LEMA pipeline.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Please fix the evaluation protocol so that checkpoint selection does not peek at the test set. Provide a clean dev split or cross-validation and re-report Table 1, Table 2, and Figure 6–7 results. This point will materially affect my overall score.
- Expand human evaluation to at least a few hundred randomly sampled corrections, report inter-annotator agreement, and present an error taxonomy linking correction quality to downstream impact.
- Provide stronger baselines that also exploit errors as supervision, including: (i) process supervision using a trained verifier to score steps, (ii) reflection-style SFT where the model’s self-critique is distilled as training targets, (iii) more DPO variants, and (iv) chain-edit models trained to patch identified steps. Even if all cannot be implemented, include discussion and partial experiments to triangulate the source of gains.
- Add cost and efficiency analysis: average GPT-4 tokens and cost for generating one usable correction or evolved item; success rate per source model; wall-clock cost per point of improvement on GSM8K and MATH. This will help practitioners adopt LEMA.
- For CSQA, analyze representative qualitative examples and conduct an ablation on the number and type of seed rationales. The current setting relies on 4 hand-annotated exemplars; sensitivity to exemplars would be informative.

Typos and minor issues:
- Page 1: “chain-of-though” should be “chain-of-thought.”
- Page 2: “arrive at the following conclusions” could be “arrive at three conclusions.”
- Page 3: Footnote marker “1” after “pre-steps” is dangling; ensure the footnote is present or remove the marker.
- Page 5 Table 1 header: spacing around columns is slightly misaligned; consider reformatting for readability.
- Page 6: “leaning from mistakes” appears once; should be “learning.”
- Page 9 Limitations: “can not” should be “cannot” in formal writing.
- A few references have inconsistent capitalization and formatting; please standardize.

Criteria for score increase in rebuttal:
- Provide results with a corrected evaluation protocol that uses a validation set for checkpoint selection and show that gains persist.
- Add at least one stronger error-exploiting baseline beyond the current DPO ablation, or strengthen DPO comparisons across at least one large backbone used in Table 1.
- Expand human evaluation and add error-type analysis linking to measured gains.
- Clarify code and dataset release plans, including documentation and licenses.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
4 Strong: This study provides sufficient support for all of its claims. Some extra experiments could be nice, but not essential.  
Justification: Despite the test-set checkpoint-selection flaw that must be corrected, the breadth of results, multiple ablations, and figure-table evidence give the central claims credible support.

## Excitement
3.5 Between interesting and exciting.  
Justification: The idea is timely and the empirical signals are consistent; the detailed ablations on explanations and the evolution strategy are useful to the community.

## Overall Assessment
4 Conference: This paper could be accepted to an ACL conference. It demonstrates sufficient novelty, soundness, and impact.  
Justification: The work is a solid empirical contribution showing that fine-tuning on mistake-correction pairs improves reasoning across backbones and tasks. The analysis around explanations and evolution adds useful insights. The largest concern is the improper checkpoint selection on test data; if addressed in rebuttal, the paper would present a clean and convincing case. Without this fix, I would lean to Findings.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges key limitations: reliance on GPT-4 for correction generation, modest data scale due to cost and low success rates on hard problems, and QLoRA’s limited ability to absorb large correction datasets. Potential societal risks are mild here, primarily tied to data usage of proprietary APIs and general LLM biases. An added point: if correction data inherit biases or flawed pedagogical patterns from GPT-4, LEMA could ossify these across open models; consider lightweight bias audits or sanity checks on correction style and content.

## Ethical concerns
None. The study uses public benchmarks and generated texts; privacy risks are minimal. The Responsible NLP Checklist should confirm no sensitive data usage.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.  
Rationale: Many training and inference details are specified. Releasing the correction datasets and scripts would raise this to 4.5–5.

## Datasets
3 Potentially useful: Someone might find the new datasets useful for their work.  
Rationale: If the mistake-correction pairs and evolution data are released with metadata and quality indicators, they could be quite valuable.

## Software
3 Potentially useful.: Someone might find the new software useful for their work.  
Rationale: If code for the pipeline and training is released and documented, it would be helpful; otherwise the contribution remains largely conceptual and empirical.