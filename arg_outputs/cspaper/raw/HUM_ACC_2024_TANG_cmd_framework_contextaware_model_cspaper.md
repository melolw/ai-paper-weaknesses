# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes CMD, a context-aware self-detoxification framework for large language models. The key idea is to treat detoxification as a two-stage process: first, detect and rewrite toxic spans in the prompt to obtain a safe, semantically aligned context; second, guide generation to follow the detoxified context. CMD contains a Dataset Synthesis phase that builds training traces for three steps (toxic span detection, span detoxification via mask filling, and context-following generation) and an integration step using chain-of-thought templates; and a Model Training phase that fine-tunes LLMs with LoRA using cross-entropy plus a “toxic contrastive” loss that pushes model representations away from toxic candidates. Experiments on RealToxicityPrompts and parallel detox corpora show reductions in toxicity alongside reasonable perplexity. Results on multiple backbones (Flan-T5, Mistral-7B-Instruct, LLaMA2-7B/13B) and comparisons to DExperts, GeDi, SGEAT, and ToxicReversal indicate CMD improves the toxicity–quality trade-off.

## Summary Of Strengths
- Clear problem framing: the paper argues persuasively that ignoring context constraints leads to the common detoxification trade-off. The two-step “detoxify-then-follow” decomposition is sensible and well motivated.
- Methodological package: CMD integrates span-level detection (Segment-CNN), span rewriting with selective masking and iterative generation, multi-candidate context-following generation, CoT-style integration of steps, and a contrastive objective over safe vs. toxic candidates.
- Strong empirical results across backbones:
  - Table 2 shows CMD substantially lowers Expected Max Toxicity and Toxicity Probability compared to DExperts/GeDi/ToxicReversal/SGEAT while keeping PPL lower than output-intervention baselines.
  - Table 3 shows consistent gains across four LLM families and two LLaMA2 sizes.
  - Figure 5 isolates the contribution of the toxic contrastive loss, reducing toxicity probability across all models with modest PPL changes.
- Insightful preliminary analysis:
  - Figures 2a and 2b visualize how detoxifying the context reduces generation toxicity and weakens the context–toxicity coupling, supporting the central claim that safe context matters.
- Human evaluation on text quality (Figure 4) indicates improved coherence and consistency versus baselines.
- The framework maintains efficiency: LoRA fine-tuning with a few million parameters (e.g., 2.5M in Table 2) compared to very large auxiliary experts used in decoding-time methods.

In-figure engagement:
- Figure 3 effectively communicates the full pipeline including detection, detoxification, context-following generation, and how positive/negative candidates feed the contrastive loss. The depiction of candidate toxicity scores clarifies how Equation (1) is operationalized during training.

## Summary Of Weaknesses
1) Over-reliance on a single toxicity oracle (PerspectiveAPI) across the pipeline:
   - PerspectiveAPI is used to create labels for Segment-CNN (Section 3.1, Toxic Segment Detection), to steer iterative detoxification and candidate selection (Context-Following Generation), and to evaluate toxicity (Section 4.1). This creates a risk of circularity and reward hacking: the model may overfit to the API’s decision boundary rather than to a robust notion of toxicity. It also limits claims about general safety. Please quantify robustness to alternative toxicity assessors (e.g., Detoxify, HateXplain classifiers, or an in-house classifier trained on different data), and include human safety judgments, not only fluency/coherence.
   - Table 1 even lists PerspectiveAPI as a “model” with 100% detection recall and the lowest toxicity, which underscores that the system is anchored to this one signal. This should be framed as a dependency and potential bias rather than a fair “upper bound” baseline.

2) Representation details for the contrastive loss are underspecified:
   - Equation (1) introduces z_h, z_o’+, and z_o’i as vector representations, but the paper does not specify how they are computed from the LLM (which layer, token pooling strategy, whether encoder/decoder states or final logits are used). This is crucial for reproducing and trusting the loss. Please add exact extraction details and ablations for representation choices.

3) Inference path is not fully clear:
   - The Dataset Synthesis phase uses Segment-CNN, GENIUS, and CoT templates. At test time, the paper claims LLMs can “self-detoxify without the requirement of any external modules” (Figure 3 caption), but Section 3.2 and Section 4 do not concretely specify the prompting or decoding recipe the fine-tuned model uses to detect spans and rewrite before generating. Is a single pass prompted with the integrated CoT template always used? Is iterative generation still applied at inference? This should be explicitly described and evaluated for latency/cost.

4) Baseline coverage and fairness questions:
   - The paper cites Niu et al. (2024) but does not include a contrastive-decoding detox baseline in Tables 2–3. More broadly, comparison to stronger recent decoding or training baselines that prioritize the toxicity–quality balance would strengthen claims.
   - Trainable parameter lines in Table 2 list billions for decoding-time baselines, which conflates inference backbones with “trainable” parameters and may be misleading. DExperts/GeDi are decoding-time controls and typically do not train billions of parameters for the detox controller. Please clarify the accounting and ensure like-for-like settings per original papers.

5) Evaluation scope and statistical rigor:
   - The automatic safety evaluation is single-metric dominant. The human study in Figure 4 measures coherence and consistency, not safety. Please add a human safety evaluation (offensiveness, targetedness, false positives) and report inter-rater agreement for safety as well.
   - No significance testing is reported for Table 2 and Table 3 despite multiple runs and stochastic sampling. Add tests or confidence intervals beyond ± for toxicity statistics.

6) Segment-CNN design and validation:
   - Section 3.1 describes a bespoke Segment-CNN with a global threshold λ equal to the dataset’s average toxicity. This thresholding choice seems ad hoc. There is no comparison to contemporary toxic span detectors on a public span benchmark. Table 5 reports only recall; precision/over-detection costs are not shown, yet the method’s premise hinges on fine-grained edits that preserve semantics. Please report precision/F1 and compare to strong span baselines.

7) Potential distribution shift and leakage concerns:
   - The RTP dataset is used to synthesize training traces (9 parts) and to test on the held-out part (1 part). Because PerspectiveAPI determines toxic spans and selection during data synthesis and again during evaluation, the train–test boundary depends on the same scoring function. Consider an out-of-domain toxicity set to evaluate generalization.

8) Quality metrics and comparability:
   - PPL is reported in Tables 2–3 across heterogeneous architectures (encoder–decoder vs. decoder-only) without clarifying tokenization and calculation details. PPL is not directly comparable across vocabularies and model families. The additional Fluency metric (Table 10) helps, but please standardize or supplement with reference-free, model-agnostic readability or grammaticality measures and report consistent generation lengths.

9) Missing ablations or design justifications:
   - The iterative generation hyperparameter K, the number of candidates in context-following generation, segment length L, and λ are not ablated in the main paper. Figure/Table references in the appendix help, but the core paper should make the sensitivity story more transparent.

10) Ethical and societal impacts are underdeveloped:
   - Optimizing to PerspectiveAPI can suppress reclaimed slurs or dialectal expressions (as discussed by Xu et al., 2021, which you cite). A deeper analysis of disparate impact and failure modes is warranted, ideally with group-specific evaluations and qualitative audits.

Figure- and table-specific critiques:
- Figure 2a and Figure 2b are central to the premise that detoxifying context reduces toxicity while maintaining quality. They are informative, yet it would help to overlay confidence bands or report sample sizes per bin to assess stability.
- Table 2 is compelling, especially the toxicity probability drop to 5.5% overall and 17% on toxic prompts, with PPL 30.38. However, it mixes GPT2-XL backbones with decoding-time baselines that may rely on their own classifiers; clarify settings and decoding hyperparameters for fairness.
- Table 3 shows CMD’s scalability. The claim that foundation models are “easier to detoxify” than instruction-tuned models is interesting; consider a more careful analysis to separate instruction-tuning effects from architectural differences.

## Potentially Missing Related Work
1) Ko et al., “Large Language Models can be Strong Self-Detoxifiers,” 2024 — proposes self-disciplined autoregressive sampling to steer decoding away from toxic subspaces without retraining. Directly related to your self-detoxification goal; discuss in Section 6.1 and compare to CMD in Section 4.2 as a decoding-time alternative.

2) Niu et al., “Parameter-efficient detoxification with contrastive decoding,” 2024 — uses contrastive decoding ideas for detox. Should be added as a baseline or at least discussed in Section 4.1 and Related Work (6.1), since CMD also leverages contrastive signals during training.

3) Klein et al., “Contrastive Perplexity for Controlled Generation: An Application in Detoxifying Large Language Models,” 2025 — introduces a training-time contrastive signal targeting fluency and safety. Relevant to Eq. (1); cite after Equation (1) and compare conceptually in Section 6.1.

4) Lu et al., “Adaptive Detoxification: Safeguarding General Capabilities of LLMs through Toxicity-Aware Knowledge Editing,” 2025 — mechanism-centric detox that routes FFN computations. Useful contrast in Section 6.1 to situate CMD’s data-driven, context-level strategy versus parameter-space editing.

5) Duan et al., “Projecting Out the Malice: A Global Subspace Approach to LLM Detoxification,” 2026 — global toxic subspace suppression, complementary to CMD’s context-first approach. Discuss in Section 6.1.

6) Shao et al., “Detoxification for LLM: From Dataset Itself,” 2026 — corpus-level detoxification pipeline at pretraining time; compare to CMD’s fine-tuning-time strategy in Section 6.1.

7) Zhang et al., “Cleansing the Artificial Mind: A Self-Reflective Detoxification Framework for Large Language Models,” 2026 — self-reflective detox with self-generated contrastive data, conceptually close to CMD’s data synthesis; cite in Section 3 and 6.1 and clarify differences in data construction and training signals.

## Comments Suggestions And Typos
Actionable suggestions likely to change my assessment:
- Provide exact representation details for z_h and z_o’ used in Equation (1): layer index, token pooling, normalization, and whether gradients backprop through these projections. Include an ablation showing sensitivity to these choices.
- Reduce single-metric dependency:
  - Re-evaluate Tables 2–3 with at least one alternate toxicity assessor and report correlation to PerspectiveAPI. Add a small-scale human safety study alongside the existing quality study in Figure 4.
  - Consider group-aware analyses (e.g., identity terms) to check for marginalization or over-suppression.
- Clarify inference procedure:
  - Describe precisely how the fine-tuned model is prompted/decoded at test time to detect toxic spans, rewrite, and generate. If CoT templates are required at inference, include latency/cost. If not, show that the behavior emerges without explicit templates.
- Baseline corrections:
  - Add a decoding-time self-detox baseline such as contrastive decoding detox and, if feasible, a self-representation steering baseline. Clarify the “trainable parameters” accounting for DExperts/GeDi in Table 2.
- Statistical rigor:
  - Add significance tests for toxicity and PPL improvements in Tables 2–3. In Figure 5 and Table 4/5, report confidence intervals or paired tests to support claims.
- Segment-CNN validation:
  - Report precision/F1 for span detection. Compare against recent span detectors on a public benchmark or provide a carefully constructed internal one. Explain the choice of λ and provide sensitivity analysis.

Minor issues and typos:
- Table 1 header: “PerpectiveAPI” -> “PerspectiveAPI.”
- Section 2.3: “we manually detect the toxic segments … with PerspectiveAPI” — clarify “manually” vs. API-driven.
- Footnotes 6–7 refer to appendices for key procedures; consider moving minimal details to the main text for self-containment.
- Consistently format BLEU/Fluency/SIM capitalization across the paper.
- In Figure 12/13 examples, red/green boxes are referenced in text; ensure colorblind-friendly cues in camera-ready.

Criteria for score increase:
- Add the missing inference details and representation definitions, include at least one strong additional baseline, and demonstrate robustness to a different toxicity assessor and to a human safety evaluation. With these, I could raise to 4.0 (Conference).

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong — Solid empirical gains with sensible design, but important details (contrastive representations, inference procedure) are under-specified and evaluation leans too heavily on one toxicity oracle.

## Excitement
3.5 Between interesting and exciting — The context-first formulation and step-integrated self-detox pipeline are compelling and empirically effective.

## Overall Assessment
3.5 Borderline Conference: The contribution is promising and practically useful, with broad empirical support and clear framing. However, reliance on a single toxicity oracle, some under-specified training/inference details, and limited baseline coverage temper confidence in generality. Strengthening robustness and clarity as suggested could justify full acceptance.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges open issues with semantic similarity metrics under toxic contexts, but the societal impact discussion is brief. Given the heavy dependence on PerspectiveAPI, there is a real risk of over-sanitization, dialect suppression, and demographic bias amplification. The authors should:
- Evaluate disparate impacts across identity terms and protected attributes.
- Discuss failure cases where reclaimed language or counterspeech is incorrectly suppressed.
- Consider red-teaming or targeted robustness checks beyond PerspectiveAPI’s taxonomy.
- Clarify dual-use concerns, e.g., the possibility of producing superficially “safe” yet subtly harmful content, and propose mitigation strategies.

## Ethical concerns
Potential concerns include bias transfer from PerspectiveAPI into the trained models, suppression of minority dialects, and the creation of “safety theater” that passes a particular API while not being broadly safe. Data usage appears compliant and warned for offensive content. None of these concerns are blockers if addressed with expanded evaluation and transparency.

## Needs Ethics Review
No

## Reproducibility
3.5 Mostly reproducible to reproducible with some difficulty — Many implementation choices are documented, and appendices include prompts and templates. However, missing details about representation extraction for the contrastive loss and the exact inference routine reduce reproducibility.

## Datasets
3 Potentially useful — The synthesized CMD dataset and Segment-CNN resources could be useful if released with clear licensing and construction details, though their value depends on how much they encode PerspectiveAPI biases.

## Software
3 Potentially useful — If released, the pipeline and training code would assist practitioners; clarity on inference flow will increase utility.