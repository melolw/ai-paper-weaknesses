# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper targets multimodal question answering for educational videos and presents EDUVIDQA, a dataset curated from LearningQ with filtering to obtain video-linked questions that include timestamps. The final “challenging subset” contains 3,158 videos and 18,474 QA pairs in math and science, with each question anchored to a video timestamp. The paper evaluates common NLG metrics for answer quality, reporting low-to-moderate correlation with human judgments except for a GPT-4–based evaluator that correlates best. Benchmarks with several LLMs and VLMs show that GPT-4V performs best, transcripts help consistently, and finetuning smaller models (Vicuna/LLaMA-3/LLaVA) on EDUVIDQA can degrade performance, which the authors attribute to diverse answer styles. The paper concludes with open questions on building better metrics and training for smaller models.

## Summary Of Strengths
- Problem focus and resource value:
  - Addresses an impactful education-centric setting where student questions are grounded in lecture videos, focusing on timestamped questions to encourage temporal grounding.
  - Curates a sizeable dataset (18,474 QA pairs over 3,158 videos) that is more challenging than generic educational QA since each question is tied to a video time point; the release on a public hub is valuable for the community.
- Systematic evaluation of metrics:
  - The study explicitly tests a suite of automatic metrics (BLEU/ROUGE/BERTScore/BARTScore/BLEURT) against human judgments on 70 items and finds that a GPT-4–based evaluator has higher correlation (Table 1). The prompts for evaluation dimensions are described in Appendix A.3, which aids reuse.
- Empirical observations with clear takeaways:
  - Transcripts consistently improve performance across models; GPT-4V tends to outperform GPT-4 when both receive transcripts (Table 2), aligning with intuition for visually grounded questions.
  - Finetuning smaller LMs/VLMs on this data hurts performance substantially (Table 3), which is a noteworthy and sobering empirical result for practitioners planning supervised fine-tuning over heterogeneous, many-valid-answers datasets.
- Clarity and qualitative analysis:
  - The paper includes interpretable case studies (Appendix C) and an error analysis showing temporal reasoning failure modes even for GPT-4V (Figure 2), which is useful for setting a research agenda.
- Figure engagement:
  - Figure 1 gives a quick overview of question cognitive levels (via BloomBERT), indicating nontrivial proportions beyond “remember/understand,” which supports the claim that the dataset is not limited to trivial recall.

## Summary Of Weaknesses
1) Dataset construction and filtering clarity, quality control, and potential bias:
- The two-step GPT-based filtering pipeline (Page 2, Section 3) relies on GPT-3.5 for an initial cut (score ≥6), then GPT-4 for a stricter cut (score ≥9), with manual inspection used only to estimate irrelevance rates. There is no clear inter-annotator agreement study or a principled sample-based validation to quantify precision/recall of the filtering and to verify that crucial, visually grounded questions were not disproportionately removed. Given that this filtering defines the dataset, the lack of human validation at scale is a critical gap. It is unclear how many items were discarded at each step and what error patterns the GPT filters exhibit.
- The choice to keep only math and science and only timestamped questions (Pages 2–3, Section 3) is a strong heuristic. While reasonable, the paper does not quantify how much this heuristic actually increases multimodal and temporal dependency versus alternative filters. Appendix B states the rationale, but there is no measurable evidence (e.g., human verification that X% truly needs visual or temporal context).

2) Dataset documentation and reproducibility details:
- The paper gives basic statistics (question/answer length, number of videos, split sizes) but omits several key aspects:
  - Are all videos accessible and stable on YouTube? If not, what is the expected coverage/decay rate and how is this handled? This significantly affects reproducibility for video-grounded tasks.
  - How are transcripts obtained and standardized across videos? Is ASR quality discussed or normalized? The method uses ±1.5 minutes around timestamps, but no ablation explores different windows, overlap, or transcript noise.
  - The dataset contains only 500 test questions (Page 4, Table 2), which is small for robust model comparison and can produce wide confidence intervals. No confidence intervals or statistical significance tests are reported.

3) Evaluation methodology and correlation study limitations:
- The correlation study for automatic metrics uses 70 human-annotated samples (Page 3, Table 1). This is a small sample without stratification analysis across question types, difficulty, or modalities; confidence intervals are not reported. The paper concludes that neural metrics are “moderate” and GPT-4 eval is best, but these conclusions are fragile with such a small annotation pool and without a second annotator-based validation round.
- The GPT-4 evaluator is used in both correlation analysis and as the main scoreboard for model comparison. Even though the authors present prompts in Appendix A.3, there is no assessment of evaluator bias, inconsistency across runs, or susceptibility to prompt changes. There is also no sanity check such as adversarial swaps or controlled perturbations.
- The inter-human agreement is reported as 0.909 (Table 1), but the exact measure, setup, and annotation protocol are not fully specified. For example, per-aspect agreements, rubric calibration steps, and rater training are not documented in the main text.

4) Insufficient baselines and ablations for video grounding:
- The video input to VLMs is represented by a single frame at the timestamp (Page 3, Section 5.1). The authors state that “multiple frames” did not help but provide no details on sampling rate, number of frames, or training/inference cost tradeoffs. Many video-QA works rely on multi-frame or clip features; without reporting those explorations, the VLM comparisons may underrepresent the benefit of video signals.
- No retrieval or temporal selection baselines beyond the ±1.5-minute transcript chunk are considered. For timestamped questions, a simple intra-video retrieval baseline over transcript windows, or alignment using temporal segments, would be natural and likely stronger than a coarse fixed window.

5) Interpretation of finetuning failures (Table 3) is underdeveloped:
- The paper attributes the severe performance drop after fine-tuning to diverse answer styles, but does not test mitigation strategies such as response format normalization, instruction tuning with answer style constraints, preference optimization, or training with multiple valid references. Without these, the conclusion risks overgeneralizing; it might be dataset-specific, prompt-specific, or avoidable with training-objective changes.
- The catastrophic drop for Vicuna (Q+TR: 2.85 → 1.31) and LLaVA (Q+V+TR: 2.67 → 1.62) in Table 3 is a key finding, yet there is minimal error diagnosis beyond high-level speculation. For example, were the fine-tuned models overfitting to idiosyncratic phrasings, or failing on generalization across topics?

6) Limited test set and absence of uncertainty reporting:
- Table 2 and Table 3 report point estimates with no variance or significance testing. With 500 test items and an evaluator that may have non-negligible variance, the observed differences may not all be reliable. This is especially relevant when arguing for small but consistent transcript gains, and for interpreting fine-tuning degradation magnitudes.

7) Missing comparisons to closely related educational multimodal QA datasets and settings:
- The Related Work section focuses on classic VQA and a few education datasets (TutorialVQA, SlideVQA, ScienceQA, LearningQ) but omits recent educational video QA and STEM multimodal QA resources that are highly pertinent. This weakens positioning and complicates claims about EDUVIDQA’s distinctiveness, temporal grounding, and open-endedness.

8) Figure- and table-specific concerns:
- Figure 1 shows that “Remember” and “Understand” dominate, with small slices for Apply/Analyze/Evaluate/Create. While the authors acknowledge this in Section 3, it somewhat conflicts with later claims that a significant portion is complex. The paper would benefit from stratified results by Bloom levels, to show where models actually gain from visual grounding.
- Figure 2 and Table 7 illustrate the temporal/geometry failure case. This is useful, but a single example is anecdotal. A systematic temporal-grounding evaluation slice, or explicit temporal reasoning probes, would make the argument much stronger.

9) Ethical and societal considerations are minimal:
- Section 8 is brief and focuses on general generative-model caveats. There is no discussion of educational equity, accessibility, potential harm from incorrect answers in learning settings, or bias amplification in STEM contexts. As this is an education-facing dataset, failure modes can have real pedagogical impact that deserves deeper treatment.

10) Clarity and scope:
- Several details are deferred to appendices that feel central (e.g., full prompts, score scales, examples), and some experimental choices lack justification in the main paper, making it harder to reproduce results without reading appendices and code.

## Potentially Missing Related Work
1) Gupta et al., “A dataset for medical instructional video classification and question answering,” 2023 — MedVidQA provides QA over instructional videos with temporal grounding in a specialized educational domain. It is directly relevant as a domain-specific counterpart; should be discussed in Section 2 and compared in Section 3 when motivating timestamp conditioning and domain choices.

2) Liang et al., “SceMQA: A Scientific College Entrance Level Multimodal Question Answering Benchmark,” 2024 — STEM-focused multimodal QA benchmark with both free-response and MCQ. It complements EDUVIDQA’s educational focus and should be discussed in Section 2, with positioning around complexity and modality, and potentially referenced when interpreting Table 2 results.

3) Alawwad et al., “Evaluating Multimodal Large Language Models on Educational Textbook Question Answering,” 2025 — Studies MLLM performance on educational materials with an evaluation framework. Add to Section 2 and the evaluation discussion in Section 4 to broaden comparison points for metrics and multimodal RAG-style setups.

4) Alawwad et al., “Beyond Retrieval: Joint Supervision and Multimodal Document Ranking for Textbook Question Answering,” 2025 — Proposes a joint ranking retriever–generator for multimodal QA; relevant as a stronger retrieval baseline. Cite in Section 5 when discussing transcript windows and note in future work as an alternative to fixed-window context.

5) Zhu et al., “MuRAR: A Simple and Effective Multimodal Retrieval and Answer Refinement Framework for Multimodal Question Answering,” 2024 — Retrieval-plus-refinement architecture that could be adapted to timestamped transcript/video snippets. Discuss in Section 5 as a baseline direction beyond zero-shot prompting and single-frame input.

6) Lee et al., “Realizing Visual Question Answering for Education: GPT-4V as a Multimodal AI,” 2024 — Examines GPT-4V for educational image QA; relevant to the GPT-4V analysis in Table 2 and qualitative examples. Add to Section 2 and briefly connect in Section 5.2 (GPT-4 vs GPT-4V observations).

7) Ray et al., “EduVidQA: Generating and Evaluating Long-form Answers to Student Questions based on Lecture Videos,” 2025 — Very close in topic. Should be discussed in Section 2 and in Sections 3–5 to clarify overlap/differences in dataset design, evaluation protocol (long-form vs concise answers), and modeling insights.

8) Shafiq et al., “Intra-Video Temporal-Aware RAG: A Self-Contained Framework for Video-Based Question Answering,” 2026 — Proposes temporally aware retrieval within videos. It is directly relevant to timestamp-aware transcript selection; add to Section 2 and cite in Section 5 as a stronger temporal grounding baseline than a fixed ±1.5-minute window.

9) Dutulescu et al., “EduMUSE: A Multimodal Educational Dataset with Automatically Extracted Instructional Context,” 2026 — While text-centric, it organizes multimodal instructional content; useful context in Section 2 when motivating broad educational QA resources and multimodal structure.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Dataset validation and documentation:
  - Provide a human-audited validation of the GPT-based filtering, reporting precision/recall and error typology on a stratified sample. Include inter-annotator agreement for relevance and “requires video/temporal grounding” labels.
  - Document video availability over time and propose a stable subset, or provide mirrored visual features or frame hashes. Clarify transcript sourcing and quality; report any ASR normalization.
  - Offer per-domain and per-Bloom-level breakdowns of test results. The Figure 1 distribution suggests a dominance of lower-order skills; stratified evaluation will make the case for multimodality stronger.

- Evaluation robustness:
  - For Table 1, enlarge the human annotation pool and report confidence intervals for correlations, plus per-aspect correlations. Consider a second-round adjudication protocol to support the 0.909 inter-human claim with details on metric and setup.
  - For GPT-4 evaluator, add robustness checks: multiple seeds/temperatures, prompt ablations, calibrated pairwise comparisons, and simple adversarial tests (e.g., swapped answers). Report evaluator agreement with humans across skill strata and modalities.

- Modeling baselines and ablations:
  - Go beyond single-frame input. Report results for clips or frame sequences with a principled sampling strategy that aligns with the timestamp. Even a small ablation (e.g., 1 vs 4 vs 16 frames) would strengthen the video grounding claim.
  - Replace fixed ±1.5-minute transcript windows with intra-video retrieval of segments around the timestamp and compare. Cite and, if feasible, adapt a temporal-aware retrieval baseline.
  - Investigate why fine-tuning fails: try enforcing concise answer formats, training with multiple references per question, consistency regularization, or preference optimization. Report whether these interventions mitigate the collapse in Table 3.

- Reporting:
  - Add statistical significance for Table 2 and Table 3 differences. Small gains from transcripts and large fine-tuning drops both need uncertainty estimates.
  - Clarify details for “Inter-human 0.909” in Table 1: metric type, rater count, and per-dimension agreements.

- Ethics and societal impact:
  - Expand Section 8 to discuss risks of incorrect explanations for learners, mitigation via uncertainty estimates or “show-your-work” evidence grounding, language inclusivity, accessibility, and bias in STEM examples. Consider model card guidance for deployment as a tutor.

Typos and minor issues:
- Section A.2/A.3 prompts contain line breaks with stray spaces and “\n” artifacts; ensure clean formatting in released code.
- In Table 2 header, “Visual Ground-ing” has a hyphen; standardize labeling across text/tables.
- In Table 3 caption and text, ensure consistent notation for “Q, V, TR” and match these consistently to the entries.
- Clarify in Page 3: “We use LoRA finetuning with rank = 64 and alpha = 64” — specify target modules and whether vision encoders were frozen.

Criteria that could change my evaluation:
- A stronger, audited dataset validation with human checks and stability plan for video access.
- More robust evaluator analysis (larger human set, CIs, evaluator robustness) and at least one non–LLM judge or learned open-source metric tuned to this task.
- Solid video-centric baselines beyond single frames and a retrieval-based transcript selection, plus controlled ablations.
- Evidence that finetuning failures can be mitigated with reasonable training adjustments.

Explicit references to figures and tables:
- Figure 1: The pie chart shows “Understand” dominating, with “Remember” substantial and small slices for higher-order skills. This supports the authors’ claim of diversity but also suggests that many questions may be solvable without deep video reasoning. Stratified results by these categories would directly test this.
- Table 1: Shows weak-to-moderate correlation of standard metrics with human scores, with BLEURT at 0.488 and GPT-4 eval at 0.782. Given only 70 samples, this is suggestive but not definitive; CIs are needed.
- Table 2: Transcript inclusion boosts scores consistently for Vicuna, LLaMA-3, LLaVA, GPT-4, and GPT-4V, and GPT-4V with transcripts is best overall (Total = 4.554). The gains are small in absolute terms, so significance reporting is needed.
- Table 3: Finetuning causes large drops, e.g., LLaVA (Q+V+TR) from 2.67 to 1.62 and LLaMA-3 (Q+TR) from 4.11 to 3.10. This is an important empirical warning; however, without trials of mitigation strategies, the conclusion remains preliminary.
- Figure 2: The failure case highlights temporal grounding and geometric reasoning errors even with transcripts. This strongly motivates the need for temporally aware modeling and structured reasoning, but a quantitative analysis of such failures would be stronger evidence than a single example.

## Confidence
4: Quite sure after careful checking — I checked the important points, tables, and figures carefully; unlikely I missed something that would flip the verdict.

## Soundness
2.5: Between Poor and Acceptable — Good motivation and some careful analyses, but the dataset filtering lacks rigorous human validation, the evaluation relies heavily on a small human set and a single LLM judge, and the modeling baselines underuse video signals. Solid insights but not fully supported experimentally.

## Excitement
2.5: Between potentially interesting and interesting — The setting is timely and the negative result on fine-tuning is useful, yet the current evaluation and baselines feel underdeveloped for a main-track venue.

## Overall Assessment
2.5 Borderline Findings — The dataset and early analysis are potentially useful, but I recommend this for Findings rather than the main conference. Key reasons: limited and under-validated filtering pipeline, overreliance on a small human study and a single LLM judge, weak video signal usage (single frame), lack of retrieval/temporal baselines, and underexplored remedies for fine-tuning collapse. With stronger dataset validation, evaluator robustness checks, and better video/temporal baselines, this work could be significantly strengthened.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper mentions general risks of generative models but does not consider education-specific harms: misleading explanations, false confidence, or inequities amplified by biased content or availability. A deeper discussion is warranted given the target domain.
- The dataset is English-only and STEM-skewed; this limits inclusivity and global applicability. Future releases might include multilingual content and broader subjects.
- Video availability drift on hosting platforms could reduce reproducibility and access over time; mitigation (e.g., frame-level features or mirrored metadata) should be considered.

## Ethical concerns
- None beyond the need for a deeper, domain-specific discussion of harm/mitigation in educational contexts. The source dataset is openly available; the paper states adherence to intended-use policies.

## Needs Ethics Review
No

## Reproducibility
3.5: Mostly reproducible — Code and prompts are provided, and the dataset link is public. However, dependence on external video availability and limited dataset documentation reduce reproducibility.

## Datasets
4: Useful — The curated, timestamped educational QA dataset has clear value, but stronger validation and documentation would raise this further.

## Software
3: Potentially useful — The released code and prompts look helpful, but more ablations and scripts for multi-frame/video baselines and evaluator robustness would increase utility.