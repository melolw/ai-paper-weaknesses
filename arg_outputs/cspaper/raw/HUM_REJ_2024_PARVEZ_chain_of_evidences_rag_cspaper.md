# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper proposes prompting methods for large language models and evaluates them on multiple NLP tasks (QA, MRC, RAG, dialogue), which fits ACL topics including Question Answering, Generation, Information Retrieval for NLP, and Interpretability/Analysis.

## Minimum Quality
Pass ✅. The submission contains Abstract, Introduction, Related Work, Method (Sections 3.1–3.4), Experimental Setup (Section 4), Results (Section 5), Analysis (Sections 6–8), Conclusion (Section 9), Limitations/Ethics (Section 10/“Ethics”), and References. However, there are notable clarity, rigor, and reproducibility gaps detailed in the review below.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I did not find hidden prompts or manipulative instructions targeting automated reviewers in the main text.

# Expected Review Outcome:

## Paper Summary
This paper introduces two zero-shot prompting strategies aimed at improving context-grounded reasoning with LLMs, especially in retrieval-augmented generation (RAG) and long-context settings. Chain of Evidences (CoE) instructs the model to “generate the answer with evidence and explanation,” encouraging explicit extraction of context-grounded rationales. Evidence to Generate (E2G) is a two-step variant: Step E produces a temporary answer plus “evidence and explanation” from the original context; Step G answers again conditioned only on the extracted evidence (or evidence plus original context for multi-answer/joint queries). Evaluations across eight tasks (LogiQA, DROP, HotpotQA distractor split, NQ, TQA, FEVER, WoW, ELI5) with ChatGPT, GPT-4, and PaLM‑2 report gains over 0-shot CoT and several CoT variants.

## Summary Of Strengths
- Problem framing: Clear focus on a practical failure mode of CoT-style prompting in RAG and long contexts, namely ungrounded intermediate steps and distraction from irrelevant content.
- Method simplicity and generality: The prompts are simple and model-agnostic. CoE/E2G can be layered on top of existing APIs without fine-tuning, which is attractive for practitioners.
- Breadth of evaluation: Eight heterogeneous, context-intensive benchmarks, including distractor-based multi-hop (HotpotQA), arithmetic/logical MRC (DROP/LogiQA), ODQA (NQ/TQA), fact checking (FEVER), and generation (WoW/ELI5).
- Reported quantitative improvements: 
  - Table 3 (LogiQA) shows GPT‑4 CoE-LONG at 53.76% vs ToT 43.02% and CR 45.25% with far fewer steps; 
  - Table 4 (DROP) shows PaLM‑2 + CoE‑LONG F1 83.3, exceeding the Gemini Ultra few‑shot number they cite.
  - Table 5 (HotpotQA/FEVER) shows E2G improving over CoT and some iterative baselines.
- Qualitative insights tied to figures: 
  - Figure 2 clearly outlines the E2G pipeline and contrasts it with CoT and iterative variants, making the mechanics easy to understand. 
  - Figure 3 provides a compelling example where CoE remains grounded in the context and avoids CoT’s numerical distraction. 
  - Figure 6 explores how different choices for G‑step context affect performance, showing a thoughtful ablation mindset.
- Self-reflection and error analysis: Sections 6–8 analyze why CoE might help, identify limitations (over‑grounding), and discuss the impact of retrieval recall (Figure 9).

## Summary Of Weaknesses
1) Reproducibility and experimental transparency are insufficient.
- The paper states “we use sampling and dev splits for evaluation” (Page 4–5) without specifying exact sample selection, random seeds, or whether results are averaged across multiple runs. Given API-based variance, this is important for fair comparison.
- Prompts are central to the contribution, but the exact prompts used per dataset/setting are only partially shown. The system prompts are described generically in Section 3.1; Section 3.2 provides short/long variants but not a full, dataset-specific prompt inventory. For E2G, precise formatting, constraints, and stop conditions are critical and should be fully enumerated.
- The paper promises future release of prompts/outputs but does not state that code or evaluation scripts are available now. This materially reduces verifiability.

2) Fairness and completeness of baselines need strengthening.
- Many comparisons are restricted to 0-shot CoT and a subset of variants. Several recent faithfulness/grounding‑oriented prompting and verification methods are not compared or even discussed. For example, verification-first or NLI‑style verification (see missing related work) might directly challenge the claim that evidence‑first prompting is uniquely effective.
- For closed models (GPT‑4, ChatGPT), the paper aggregates prior results from different sources for some baselines (e.g., Table 5 citations) but does not fully align settings (prompt wording, temperature, trials), which may bias comparisons.

3) Inconsistent and sometimes unclear reporting across tables and text.
- Table 2 has confusing column headers and entries (e.g., “7.41KCG/1.5KP,” missing metrics for some tasks). Please standardize dataset sizes, contexts lengths, and metrics.
- Table 3: “Steps” shows non-integers for ToT and CR but 1 for CoE; it is unclear how “steps” are counted across methods and whether API retries or self-consistency samples are included.
- Table 4: Mixed reporting across backbones and shot settings; “FEW-SHOT SOTA” appears while this work is zero-shot. The claim that PaLM‑2 + CoE‑LONG outperforms “Gemini Ultra few-shot” requires perfectly matched evaluation scripts and dev/test splits, which are not shown.
- Table 6: Marking “Red refer to an inferior performance” in the caption is unusual. Some cells have dots or extra punctuation (e.g., “36.6.”).

4) Dataset usage and evaluation protocol need clearer articulation.
- For HotpotQA distractor split and FEVER, it is unclear how retrieved contexts are constructed for each method and whether all methods receive identical retrieved passages. Section 4 says top‑5 DPR retrieved docs are used “by default,” but Hotpot distractor already has curated contexts; mixing two pipelines can confound results.
- The paper sometimes mixes “RAG” and “given context” settings across tasks without always clarifying the pipeline, e.g., whether retrieval is external or the dataset’s provided context is used.

5) Statistical robustness and significance.
- No statistical significance testing is reported. Given API stochasticity and small sampled evaluation sets (e.g., NQ 500, DROP 500, ELI5 300), improvements of 1–2 F1 may not be reliable.

6) Overclaiming and scope creep.
- The abstract and conclusion make strong claims like “new state‑of‑the‑art” across tasks without consistently qualifying that these are zero‑shot prompting results on sampled subsets using closed APIs. Claims vs. supervised SOTAs are sometimes juxtaposed (e.g., Table 6) but should be carefully caveated.
- The stated worst-case runtime “approximately double that of CoT” (Page 4) lacks time/latency measurements per dataset and model, and does not account for variable evidence length.

7) Limited depth of analysis regarding failure modes and trade-offs.
- While Figures 8–9 and Sections 7–8 discuss over‑grounding and recall sensitivity, there is limited quantitative analysis of when E‑only, E+OC, or adaptive contexts help and why. Figure 6 provides a bar chart, but a per-question-type breakdown and ablations on evidence length, evidence quality, and error categories would be more convincing.

8) Ambiguities in method definition and output control.
- The paper states that outputs are returned in JSON with answer and “evidence and explanation,” but the examples (Pages 5–13) show heterogeneous formats and sometimes missing tags. It is unclear whether output formatting is enforced programmatically and how parsing errors are handled.

9) Some figures and examples, while helpful, also raise questions about cherry-picking.
- Figure 4 and multiple example blocks (Pages 5–13) show CoT hallucinations corrected by E2G. A systematic study quantifying hallucination reduction rates per dataset, independent of task accuracy, would strengthen the claims.

10) Writing quality and typos detract from clarity.
- Many typos and formatting issues (e.g., “E2Gis,” “ungroundeded,” “morbidity” where “verbosity” or “variability” seems intended, inconsistent use of quotes and punctuation, repeated reference list fragments on Pages 9–11). These should be cleaned up.

Figure- and Table-specific comments
- Figure 2: Strong, central figure. It clearly depicts both CoT and the E2G pipeline, including where evidence is extracted and reused. This supports the paper’s main narrative and clarifies how the second pass benefits from a shorter, focused context. However, it should explicitly show the decision about using Evidence vs Evidence+Original Context in G‑step, which later ablations (Figure 6) discuss.
- Figure 3: The DROP example illustrates how CoT can be misled by focusing only on arithmetic while CoE checks textual validity. This is a persuasive qualitative case supporting the grounding claim.
- Figure 6: The bar chart comparing different G‑step contexts (Evidence, Evidence+Original Context, Adaptive) is useful but lacks error bars and exact sample counts. The absolute EM differences are small; it would be helpful to report per‑category gains to clarify when each variant helps.
- Table 3 (LogiQA): The performance vs steps comparison highlights efficiency. However, better define how steps are counted for each baseline and whether sampling/beam search contributes to step counts.
- Table 5 (HotpotQA/FEVER): The baselines span different papers and settings. Please standardize temperatures, trial counts, and prompts where possible, and add self-consistency CoT ablations for the same backbone for a fairer picture.
- Table 6 (NQ/TQA/WoW/ELI5): The reported gains are modest or mixed. Given the importance of these tasks, more detailed ablations (question type, answer length, retrieval recall bins) would help interpret where E2G is helpful.

## Potentially Missing Related Work
1) Lei et al., “Chain of Natural Language Inference for Reducing Large Language Model Ungrounded Hallucinations,” 2023 — directly addresses grounding by verifying outputs via NLI chains; should be discussed in Section 2 and contrasted with CoE/E2G’s evidence-first prompting (verification vs. prompting) and, if possible, used as a comparison on FEVER or HotpotQA.
2) Xu et al., “Re-Reading Improves Reasoning in Large Language Models,” 2023 — proposes input-side re-reading that improves reasoning faithfulness; compare conceptual overlap with E2G’s two-step re‑contextualization in Section 3 and add to Related Work.
3) Islam et al., “Open-RAG: Enhanced Retrieval-Augmented Reasoning with Open-Source Large Language Models,” 2024 — retrieval-augmented reasoning pipeline emphasizing better use of retrieved evidence; discuss in Section 2 and, where feasible, compare on NQ/TQA style settings.
4) Wang et al., “FACT: Examining the Effectiveness of Iterative Context Rewriting for Multi-fact Retrieval,” 2025 — relevant to long-context multi-fact retrieval; connect to E2G’s handling of distractors in Section 5 and consider as an additional baseline or discussion point for HotpotQA.
5) Hagström et al., “A Reality Check on Context Utilisation for Retrieval-Augmented Generation,” 2025 — offers analyses on how LLMs actually use retrieved context under noise; should be cited in Section 8 to frame limitations and robustness claims.
6) Hung et al., “MSR2: A Benchmark for Multi-Source Retrieval and Reasoning in Visual Question Answering,” 2025 — while multimodal, it targets multi-source evidence reasoning and could be used in the discussion as future work for testing E2G beyond text-only QA.

## Comments Suggestions And Typos
Actionable suggestions
- Provide a complete, task-specific prompt appendix with all exact wordings for CoE-SHORT/LONG and E2G (E and G steps), including formatting constraints and output-parsing details. This would directly raise my reproducibility score.
- Standardize and clarify experimental protocols:
  - For each dataset: exact split, sample size, retrieval pipeline (dataset-provided context vs DPR), decoding parameters (temperature, max tokens), number of trials/self-consistency samples, and step counting conventions for all baselines.
  - Report statistical significance or confidence intervals, ideally over multiple randomized runs.
- Strengthen baselines on grounding: add or discuss verification-first approaches (e.g., chain-of-NLI, verify-and-edit) and input-side methods like re-reading. Even one additional controlled baseline on 1–2 datasets would materially improve the empirical case.
- Expand quantitative analysis of E2G’s components:
  - Break down results by question type (wh vs yes/no; single vs multi-entity) to substantiate the Evidence vs Evidence+OC vs Adaptive G-step choices (Figure 6).
  - Analyze evidence length, evidence token overlap with gold rationales (where available), and how evidence quality correlates with final accuracy.
- Tighten claims and reporting:
  - Reframe “state-of-the-art” to “best 0-shot prompting results under our settings,” unless you can fully align with prior pipelines.
  - Clean up Tables 2, 3, and 6 for consistent formatting and complete metric reporting. Add footnotes defining “Steps.”
- Consider adding a hallucination-rate metric independent of task accuracy (e.g., contradiction with context or QA consistency checks), since grounding is the core claim.

Typos and clarity issues (non-exhaustive)
- “ungroundeded” → “ungrounded” (Page 1, Figure 1 caption bottom).
- “E2Gis” → “E2G is” (Page 4).
- “Goal (Cost)” in Table 1 likely means “Goal (Cost-optimized)” or similar; consider rewording and fix symbols like “-1, -2” to “SHORT/LONG.”
- Table 2 has multiple formatting issues (dataset sizes, metrics, odd notations like “7.41KCG/1.5KP”); standardize.
- Multiple places refer to “morbidity” where “verbosity” or “variability” seems intended (e.g., Page 7, “Although the performance difference is marginal due to morbidity”). Please correct.
- Several reference list fragments are duplicated or malformed on Pages 9–11.

What would change my assessment
- A thorough reproducibility package (full prompts, scripts, seeds, decoding params) and standardized baselines, plus significance testing.
- A stronger, controlled comparison against at least one verification-first or re-reading baseline on 2–3 representative datasets.
- Clearer, consistent tables and expanded ablations tying Figure 6–style choices to question types and evidence properties.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but I did not have full prompts or code to verify detailed claims.

## Soundness
3 Acceptable: The idea is plausible and supported by multi-dataset results and examples, but the evaluation protocol and baseline coverage need tightening, and significance is not reported.

## Excitement
3.0 Interesting: Practical and simple prompting that many will try; not conceptually deep, but useful and timely for RAG practitioners.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. I find the core idea practical and the cross-task evidence suggestive, but reproducibility gaps, baseline coverage, and reporting inconsistencies prevent a higher recommendation for the main track at this time.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges limitations like over‑grounding that may suppress commonsense or world knowledge (Figure 8), and low performance on long-form generation tied to retrieval recall (Figure 9). Societal impact is relatively low‑risk in this form, but deploying evidence-focused prompting in user‑facing systems should consider the risk of over‑conservative outputs (“unknown”) and ensure transparency when evidence is partial or conflicting. A brief discussion on multilingual and domain transfer risks is included, but could be expanded with concrete mitigation strategies (e.g., calibration, uncertainty reporting).

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Key prompts and parameters are under‑specified and code is not available, but the method is simple enough that results could be approximated.

## Datasets
2 Documentary: No new datasets are released here; if the promised evidence outputs are actually released, they would be useful for instruction tuning and analysis.

## Software
2 Documentary.: No software appears to be released; scripts to run standardized E2G/CoE across datasets would be beneficial.