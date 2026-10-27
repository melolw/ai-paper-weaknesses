# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes a practical pipeline for adapting open-source Large Vision-Language Models (LVLMs) to non-English languages, focusing on Italian and Spanish. The pipeline comprises data translation (human-verified templates and automatic translation of large corpora), instruction formatting, optional language adaptation of the underlying LLM, and multimodal adaptation using the LLaVA 1.5 framework with an MLP projector. The authors evaluate on translated MultiInstruct test tasks and on Crossmodal-3600 in three languages, analyze open-ended versus close-ended evaluations, and study the effect of language adaptation via perplexity. Code, trained models, and datasets are announced as released.

## Summary Of Strengths
- Clear, end-to-end recipe for multilingual LVLM adaptation. Figure 2 provides a helpful, concrete overview of each step in the pipeline, including where human and machine translation are used, and how pretrain and instruction-tuning interact with the LLaVA components. This is useful for practitioners and reproducibility.
- Empirical exploration across multiple dimensions:
  - Cross-language training/evaluation on English, Italian, and Spanish, with multiple encoder/LLM/dataset language combinations.
  - Open-ended versus close-ended evaluation, with evidence that close-ended tasks understate cross-lingual difficulty, while open-ended tasks are more discriminative.
- Results are reported on multiple tasks and datasets. Table 1 covers 11 MultiInstruct test tasks with both Accuracy and ROUGE-L; Tables 2–3 present Crossmodal-3600 image captioning and image-text selection; Table 4 reports perplexity to probe language adaptation effects.
- The work surfaces and discusses catastrophic forgetting in the Spanish-adapted LLM based on perplexity trends in Table 4, and contrasts it with an Italian model that used LoRA, offering a plausible narrative connecting adaptation choices to forgetting.
- Equations 1–3, while simple, correctly formalize how visual tokens condition generation and how language-adapted parameters θ_L conceptually shift the conditional distribution.

## Summary Of Weaknesses
1) Limited novelty, largely a systems integration of known components  
- The core pipeline is a straightforward composition of machine translation, instruction formatting, optional language adaptation, and LLaVA-style multimodal adaptation. Methodological contribution beyond prior LLaVA-style recipes appears modest. Equations 1–3 restate standard conditional LM formulations without adding a new modeling insight. This limits originality for the ACL main track.

2) Evaluation design leaves several key questions unanswered  
- Missing multilingual LVLM baselines. The paper does not compare against multilingual or non-English-capable VLMs (e.g., models that report multilingual VQA or captioning performance). Without such baselines, it is hard to gauge whether the proposed recipe advances the state of practice for non-English LVLMs. This is a primary missing comparison given the paper’s stated goal.
- The reliance on translated MultiInstruct for both training and evaluation raises concerns about evaluation strictness and potential artefacts. Although test tasks are disjoint from train tasks, they originate from the same collection and share formatting conventions. No independent multilingual VQA/VLQA benchmark beyond Crossmodal-3600 is used, and there is no human evaluation of open-ended generations.
- The choice of metrics for open-ended tasks is narrow. ROUGE-L alone can be brittle across languages with diacritics and morphology, and greedy decoding can handicap models unevenly. Metrics such as BLEU, METEOR, chrF, or CIDEr, plus qualitative or human judgments, would strengthen claims. This is especially salient for Table 1’s open-ended rows (e.g., Text VQA, Visual Dialog, Visual Text Extraction).

3) Inconclusive evidence for the benefits of language adaptation  
- The paper claims potential benefits from language adaptation, but Table 1 shows mixed signals. For the Italian test set (Table 1b), an English LLaMA + English CLIP trained on ES-DS is best on 4/11 tasks, and EN-LLaMA + EN-CLIP + IT-DS leads on some tasks as well, diluting the case that target-language adaptation clearly improves end-task performance. The text acknowledges that close-ended tasks are weak indicators, but even open-ended improvements are not consistently demonstrated.
- Table 4’s perplexity analysis is a step in the right direction, but the extremely large values (e.g., 1999.88 on English for ES-LLAMA+ES-CLIP+ES-DS) suggest either a very different tokenization or a computation detail that needs clearer explanation. Since all models share tokenizer and architecture, such magnitude differences need careful sanity checks and error analysis. Also, perplexity is reported only for Crossmodal-3600 captions, which are short and may not fully reflect broader language proficiency.

4) Crossmodal-3600 close-ended setup is too easy and under-informative  
- Table 3 shows high accuracies across all language/test combinations and sometimes best performance in mismatch languages. The negative sampling for image-text selection uses only three distractors, which is a weak test and supports the authors’ own conclusion that close-ended tasks are not diagnostic. Given that, this table adds little to the main argument.

5) Translation fidelity and its impact are under-analyzed  
- The pipeline depends heavily on machine translation for both pretraining captions and instruction data, yet there is no targeted ablation on translation quality or error propagation. For sensitive tasks like VQA and especially Text VQA, translation artefacts can systematically bias results. The paper notes regex-based Q/A concatenation for joint translation, but does not quantify error rates or provide examples of failure modes.
- Relatedly, the OCR/Text VQA rows in Table 1 show large gaps (e.g., English model dominating across languages). This may reflect the unavoidable language dependence of OCR tokens and their overlap with pretraining corpora, but the paper stops short of analyzing the causes in detail.

6) Missing breadth in tasks and languages  
- Only two target languages are considered, both relatively well-resourced compared to truly low-resource languages. The authors acknowledge this limitation, but the generality of the pipeline for genuinely low-resource languages remains untested. The discussion states this explicitly but the conclusions sometimes generalize beyond demonstrated scope.

7) Lack of stronger ablations and principled controls  
- Beyond cross-language swapping of CLIP/LLM/dataset, there are no ablations on adapter choice (e.g., LoRA versus full fine-tuning during language adaptation for Spanish to test the catastrophic forgetting hypothesis) or on the effect of translating pretrain captions versus leaving them in English and adapting only at instruction-tuning. Given the central claim about language adaptation and forgetting, a controlled LoRA vs full-FT comparison for Spanish would be highly informative.

8) Statistical testing description versus practice  
- The paper performs McNemar’s test for accuracy-based tasks and reports aggregate counts in Appendix Tables 7–8. This is good practice, but for the main claims, the most contentious differences often lie in open-ended metrics where no significance testing or uncertainty is reported. Confidence intervals or bootstrap tests for ROUGE-L in Table 1 would increase rigor, particularly for small deltas.

9) Figure-level qualitative support is minimal  
- Figure 1 illustrates multilingual outputs on a single image. It is aligned with the paper’s goal, but it is too sparse to substantiate claims about language adaptation or reasoning improvements. A small qualitative analysis section with representative successes/failures per language and task would make the narrative more concrete.

10) Some conclusions reach beyond the evidence  
- The statement that “knowledge is language-independent, and specializing models for a given language limits their reasoning capabilities” is strong. The perplexity evidence in Table 4 suggests forgetting under a specific full-parameter adaptation regime on Wikipedia-only Spanish; it does not establish language-independent reasoning in general. This should be framed more cautiously.

Specific references to figures/tables:
- Figure 2 effectively communicates the engineering flow and helps readers reproduce the process. It supports the claimed contribution around open resources and a unified pipeline.  
- Table 1 is central, but it also reveals that target-language adaptation does not consistently win, particularly on the Italian and Spanish test sets’ open-ended tasks. This undermines the paper’s core hypothesis that language adaptation necessarily helps downstream performance.  
- Tables 2 and 3 together show that open-ended captioning is more sensitive to language match than close-ended selection, supporting the authors’ argument that close-ended tasks are not ideal for multilingual evaluation.  
- Table 4’s perplexity analysis is insightful but needs stronger methodological clarity and validation, especially to justify very large perplexity numbers and the inference about language-independent reasoning.

## Potentially Missing Related Work
1) Musacchio et al., “Extending Large Language Models to multimodality for non-English languages,” 2026 — Directly tackles non-English LVLM adaptation with a translation-based pipeline and multilingual evaluation. Should be discussed in Section 2 and used as a point of comparison in Section 4.4 for both methodology and evaluation scope.

2) Musacchio et al., “xVLM2Vec: Adapting LVLM-based embedding models to multilinguality using Self-Knowledge Distillation,” 2025 — Presents multilingual adaptation for LVLM embeddings via self-distillation. While focusing on embeddings, its adaptation recipe and multilingual evaluation are relevant; cite in Related Work and discuss contrasts in Section 3.

3) Geigle et al., “Centurio: On Drivers of Multilingual Ability of Large Vision-Language Model,” 2025 — Systematic study of multilingual ability drivers, including data composition and OCR effects. Relevant to design choices in Section 3 and interpretation of Table 1 and Table 4; should be cited in Related Work and discussed in Section 4.4.2.

4) Statkiewicz et al., “Annotation-Efficient Vision-Language Model Adaptation to the Polish Language Using the LLaVA Framework,” 2026 — Very close in spirit to translation-based LLaVA adaptation to a non-English language. Should be discussed in Related Work and, if possible, used as an external point of empirical comparison.

5) Lahmi et al., “Multilingual VLM Training: Adapting an English-Trained VLM to French,” 2025 — Compares translation-based pipelines and parameter-efficient finetuning, directly relevant to your LoRA versus full-parameter discussion in Section 4.4.2; cite in Related Work and discuss implications around forgetting.

6) Li et al., “VaaWIT: Visual-Aware Adaptation of Large Language Models for Multilingual Web Image Translation,” 2026 — Although focused on OCR-style translation, it introduces visual-aware adapters and multilingual evaluation relevant to your OCR/Text VQA rows in Table 1; discuss in Related Work and contrast adapter design in Section 3.

## Comments Suggestions And Typos
Actionable suggestions:
- Expand baseline coverage. Include at least one multilingual LVLM baseline known to produce non-English outputs, or a closely related multilingual VQA/captioning model. If compute prevents full training, run zero-shot or lightweight finetuning where feasible. This is critical for situating the contribution.
- Strengthen open-ended evaluation. For Table 1’s open-ended rows and Table 2, add metrics beyond ROUGE-L (e.g., BLEU, METEOR, chrF, CIDEr) and report confidence intervals or bootstrapped significance. Consider top-k decoding or nucleus sampling for more fluent generation, and include a small-scale human evaluation to assess adequacy and fluency.
- Analyze translation artefacts. Provide an error analysis showing how MT issues affect at least two tasks (e.g., VQA and Text VQA). Include a mini-ablation with a small human-curated subset to quantify the upper bound. Align this analysis with unexpected patterns in Table 1 (e.g., Text VQA dominance by English configuration).
- Clarify perplexity computation (Table 4). Describe tokenization details, sequence lengths, and whether perplexity is computed per-token over the caption continuation only. Sanity check the very large values via a calibration study (e.g., reporting perplexity on an English-only captioning dataset with a known English model) and add CI/error bars across the 3,600 examples.
- Add ablations on adaptation regimes. For Spanish, contrast full-parameter language adaptation with LoRA using the same data to test the forgetting hypothesis more cleanly. Also test whether translating only instruction data (not pretrain captions) changes results, to assess where language adaptation yields most benefit.
- Report qualitative examples. Complement Figure 1 with a grid of qualitative outputs per model/test language for at least two tasks (e.g., VQA and captioning), including success and failure cases. Tie observed errors back to translation artefacts or visual grounding issues.
- Discuss generalizability. Frame conclusions more cautiously regarding “language-independent knowledge.” Consider an experiment where the Italian model is also fully adapted on monolingual Wikipedia to mirror Spanish, isolating LoRA vs full-FT effects.

Typos and minor issues:
- Page 12, Table 9: several Italian/Spanish strings contain hyphenation breaks (e.g., “con-ciso”, “im-age”). Clean these artefacts.
- Page 6: “We will justify these results in Section 4.4.2.” The justification is plausible but incomplete; consider softening language or adding analyses as suggested above.
- Ensure consistent capitalization of LLaMA and LLaVA throughout.
- Confirm whether “Visual Text Extraction” ROUGE-L is computed with case/diacritics normalization; state explicitly.

Criteria that could change my evaluation:
- Adding strong multilingual baselines and more rigorous open-ended evaluation with statistical testing and human judgments.
- Clear, validated perplexity methodology with ablations that isolate forgetting causes.
- Targeted translation error analysis and small human-curated subset experiment demonstrating measurable gains from your pipeline.

## Confidence
3: Reasonably confident but not fully verified — I am familiar with LVLM and multilingual adaptation, but the paper’s reliance on translated datasets and perplexity without full methodological details leaves room for uncertainty.

## Soundness
3: Acceptable — The study supports several claims, but evaluation breadth and baseline coverage are limited; some conclusions (e.g., language-independent knowledge) are stronger than the evidence presented.

## Excitement
2.5: Between potentially interesting and interesting — The topic is timely and practically useful, but methodological novelty is limited and the empirical evidence is mixed.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The pipeline is helpful and the release of code/models is valuable, but limited novelty, incomplete baselines, and gaps in evaluation prevent a main-track recommendation.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges that base LLaMA-2 13B models and datasets are not safety-filtered, and that machine translation may introduce artefacts. Additional discussion to consider:
- Translation bias amplification, especially for culturally specific images and captions; who is disadvantaged when translation fails.
- Licensing implications of translating datasets with usage restrictions, and whether translated derivatives can be shared.
- The potential for domain shift in OCR/Text VQA across scripts and typography; errors may disproportionately affect languages with diacritics or different orthographies.
- For lower-resourced languages without reliable MT systems, the pipeline’s applicability is limited; risks of building models that appear multilingual but underperform for those communities.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Code and hyperparameters are provided, datasets are publicly referenced, and the pipeline is clearly described. Some dataset access steps require acceptance of third-party terms, and perplexity computation needs additional clarity.

## Datasets
3: Potentially useful — Translated resources and formatting scripts are likely useful to others, though they are derivative and bound by original dataset licenses.

## Software
4: Useful — A packaged pipeline for multilingual LLaVA-style adaptation is practical and should help other researchers reproduce and extend these experiments.