# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper evaluates GPT-4, Llama-2–70B-chat, and Gemini Pro on cross-lingual Natural Language Inference (NLI) using XNLI test sets for English, Hindi, Urdu, and a machine-translated Bangla XNLI. The authors study zero-shot prompting with five prompt settings, where some settings translate a base prompt across the four languages. They report aggregate and class-wise results, analyze invalid-label outputs across models, and conclude that English prompts yield higher performance than low-resource languages and that GPT-4 is strongest overall. They also claim that prompt translation quality has limited impact on performance.

## Summary Of Strengths
- Timely focus on multilingual and low-resource evaluation, with attention to large South Asian languages (Bangla, Hindi, Urdu) that are underrepresented in many LLM papers.
- Clear, practical framing of the question: how do off-the-shelf LLMs behave across English and several low-resource languages on a standard NLI benchmark under zero-shot prompting.
- Useful quantitative breakdowns:
  - Table 3 provides accuracy and macro-F1 across models, languages, and prompt settings, making cross-comparison straightforward.
  - Table 4 explicitly counts invalid labels per condition, which is rarely reported and gives a more realistic view of LLM output messiness.
  - Table 5 and Table 7 offer class-wise F1 and precision/recall, surfacing class imbalance effects and tendencies, for example Llama 2’s propensity to predict Neutral (cf. Table 5).
- Safety setting disclosure for Gemini (Appendix Table 6) acknowledges practical frictions with commercial APIs on content moderation, a real constraint for multilingual evals.
- The result that GPT-4 dominates across settings and languages (Table 3, blue-highlighted best scores) is consistent and actionable for practitioners deciding between available models.

## Summary Of Weaknesses
1) Severe prompt quality and validity issues in non-English conditions
- Table 2 contains multiple malformed prompts, with mixed scripts and fragments that are clearly not valid Hindi or Urdu, and even cross-contamination with Bangla script:
  - P1-HI line mixes Bangla text with Hindi and is ungrammatical.
  - P1-UR and P2/P3-UR contain repeated “میں سے کسی” fragments and code-switched Bangla words and English quotes; these are malformed.
  - P4 entries exhibit logical/connective errors in English (“Classify 'premise', or 'hypothesis'... 'entailment' and 'contradiction' or 'neutral'”), and the BN/HI are similarly garbled.
These prompt defects are central, because the paper’s main claim relates to cross-lingual behavior “under translated prompts.” If the non-English prompts are corrupted, then the observed English advantage and the assertion that translation quality has “minimal impact” are confounded. The validity of comparisons in Sections 4.1 and 4.3 is undermined.

2) Uncontrolled label-language confound
- The paper states: “Class labels are in English for all languages” (Section 3.2.2). This privileges outputting English tokens and likely induces more invalid labels or mismatches for non-English prompts, especially when models try to answer in the input language. Table 4 shows large invalid-label counts for non-English under Llama 2 and Gemini. This design choice biases against non-English settings and confounds the headline claim that “English prompts outperform others.” A fair design would translate the label strings into the target language and robustly map them back, or allow canonical bilingual labels.

3) Post-processing and invalid-label handling is outcome-distorting
- Section 3.2.3 and Table 4: the authors remove “unknown characters” and regex-filter class labels, assigning “None” or inverse class to invalid labels. This step can heavily sway scores, yet the paper does not:
  - Specify deterministic parsing rules and priorities when extra text plus a valid label appears.
  - Provide per-condition rates of “None” mapped versus successfully recovered.
  - Run sensitivity analyses showing result robustness to alternative post-processing strategies.
Given the very different invalid-label rates (Table 4), the evaluation may be disproportionately penalizing some languages/models.

4) Overstated claim that translation quality has minimal impact
- Section 4.3 asserts translation has limited effect, but results show sizable swings across settings and languages:
  - For GPT-4 English, P1/P3 F1_macro 86.79/87.08 versus P4 81.99 (Table 3). A drop >5 F1 is not “minimal.”
  - Gemini English drops from 73.36/73.09 (P1/P3) to 60.73 (P4), a large degradation (Table 3).
  - The authors highlight P5 EN>BN translation outperforming original EN for GPT-4 (87.08 vs 86.79), but this cherry-picks the smallest deltas while ignoring large negative shifts elsewhere. 
Without human-validated prompt quality or controlled paraphrase experiments, the conclusion about translation insensitivity is not supported.

5) XNLI use is fine, but Bangla XNLI is machine-translated and not standard
- Section 3.2.1: The Bangla XNLI is generated via Hasan et al. (2020b) English-to-Bangla MT. Unlike the official XNLI protocol with human translations for dev/test of some languages, this may introduce translation artifacts and label noise. This should be clearly analyzed. No human validation or error analysis is provided to ensure parity with Hindi and Urdu, which use official XNLI test sets.

6) Narrow scope and missing baselines limit significance
- Only one task (NLI), only zero-shot prompting, and only three models. There is no comparison to strong encoder baselines (e.g., XLM-R, InfoXLM) on XNLI for the same languages, which would contextualize whether LLMs are actually competitive in these low-resource settings.
- No few-shot or CoT variants are explored, though the paper claims to study prompt “settings.” The five “settings” are nearly all minor surface paraphrases/translations, not qualitatively different prompting strategies.

7) Insufficient experimental controls and reproducibility details
- No decoding parameters, temperature, or sampling details are given; no timestamps for API versions or model release variants; no retry policy; no rate limiting or batching details; no cost constraints beyond a general remark in Limitations. Given the variability of LLM outputs, this affects replicability.
- No confidence intervals, variance estimates, or bootstrap tests. All conclusions are based on single runs, although Table 4 shows very different invalid-label rates per condition that could induce volatility.

8) Safety setting choices and ethical risk handling are under-discussed
- Appendix Table 6 shows Gemini’s harmful-content filters were set to BLOCK_NONE to force responses, but the main text acknowledges many prompts still got blocked. This raises concerns about reproducing the exact behavior and about the ethics of evaluating models with disabled safeguards on potentially sensitive content. The Ethics/Impact discussion does not grapple with dual-use or exposure risks adequately.

9) Ambiguities and contradictions in prose
- Section 4.2 says Gemini “lacked support for the Urdu language,” but the paper reports multiple Urdu results for Gemini in Tables 3, 5, and 7. If “lack of support” means higher invalid labels or degraded quality, this should be stated precisely.
- The paper calls NLI “Natural Language Interface” in multiple places (e.g., Section 3.2.1), but the evaluated task is Natural Language Inference. This repeated mislabeling signals editorial inattention.

10) Central tables suggest alternative interpretations
- Table 5 shows that for Llama 2 English, Contradiction F1 is high while Neutral is extremely low in several settings, reflecting skewed decision behavior that warrants error analysis beyond aggregate F1. Without this, conclusions about overall “poor multilingual ability” may miss class-prior effects or parsing artifacts induced by the English-only label constraint.
- Table 7 further shows large swings in precision/recall across classes and languages that could align more with prompt well-formedness and label language choices than intrinsic language ability.

11) Missing key related work that is directly relevant
- The paper’s Related Work does not engage with recent cross-lingual LLM evaluation studies focused on prompt language choice, factuality, domain-specific multilingual QA, or multilingual classification under zero-/few-shot prompting; see “Potentially Missing Related Work.”

12) Presentation quality and typographical issues
- Multiple garbled prompts in Table 2 reduce confidence in the study’s execution and inferences.
- Several grammatical issues and typos throughout; the writing is serviceable but not polished.

Collectively, these issues substantially weaken the empirical validity of the main claims and limit the paper’s contribution beyond confirming an already well-acknowledged English advantage in LLMs.

## Potentially Missing Related Work
1) Rohera et al., “Better To Ask in English? Evaluating Factual Accuracy of Multilingual LLMs in English and Low-Resource Languages,” 2025 — Directly evaluates English vs low-resource Indic languages on factual QA and hallucinations. Should be discussed in Section 2 and contrasted in Section 4.1 as a complementary finding on English-centric accuracy; consider adding a factual QA comparison or at least a qualitative error analysis aligned with their methodology.

2) Jin et al., “Better to Ask in English: Cross-Lingual Evaluation of Large Language Models for Healthcare Queries,” 2024 — Introduces XLingEval/XLingHealth for domain-specific multilingual QA. Relevant for the broader claim about prompt language effects; cite in Related Work and discuss in Section 4.3 as a domain-focused counterpoint to NLI findings.

3) Hasan et al., “Do Large Language Models Speak All Languages Equally? A Comparative Study in Low-Resource Settings,” 2024 — A companion-style study by overlapping authors with broader task coverage. It should be integrated in Related Work and compared explicitly in Section 4 for alignment or discrepancies across tasks and design choices.

4) Ghorbanpour et al., “Can Prompting LLMs Unlock Hate Speech Detection across Languages? A Zero-shot and Few-shot Study,” 2025 — Evaluates prompting strategies for multilingual classification. Should be cited in Related Work and discussed in Section 3.1 and 4.2/4.3 to contextualize zero- vs few-shot and to motivate adding few-shot baselines.

5) Schmidtová et al., “How Important is ‘Perfect’ English for Machine Translation Prompts?,” 2026 — Studies robustness to imperfect English. Highly relevant to claims about translation quality insensitivity; add to Section 2 and discuss after Table 3 in Section 4.3.

6) Laba et al., “From Sparse to Sense-Grounded: Wikipedia Training for Ukrainian,” 2026 — Presents a low-resource evaluation and resource-building strategy; cite in Related Work and discuss in Conclusion/Future Work as an alternative to purely prompt-based evaluation.

7) Teklehaymanot et al., “LLM Probe: Evaluating LLMs for Low-Resource Languages,” 2026 — Proposes linguistically fine-grained probing; add to Section 2.2 and consider as a diagnostic framework in Section 4.2/Conclusion to go beyond task-level metrics.

8) Nasution et al., “Benchmarking Open-Source Large Language Models for Sentiment and Emotion Classification in Indonesian Tweets,” 2025 — Multilingual classification benchmarking with open and closed LLMs; discuss in Section 2.2 and consider adding sentiment as a second task or referencing their efficiency/accuracy trade-offs.

9) Khan et al., “Low-Resource Dialect Adaptation of Large Language Models: A French Dialect Case-Study,” 2025 — Demonstrates adaptation via PEFT under data scarcity; include in Related Work and discuss in Conclusion as a path to improving low-resource performance instead of solely evaluating off-the-shelf models.

## Comments Suggestions And Typos
Actionable suggestions:
- Fix and validate all non-English prompts. Engage native speakers to author and proof each prompt. The corrupted Table 2 entries make current results inconclusive. Provide a public repository with the exact prompts used. My overall assessment could increase if you re-run experiments with human-validated prompts and show stable trends.
- Translate labels into the target language for non-English prompts and map them back deterministically. Alternatively, instruct the model to answer in the same language as the prompt and standardize label parsing across languages. Re-run with this fairer setup. If English still dominates, the claim is stronger.
- Report full decoding and API details: temperature, top-p, system vs user roles for each API, model version strings and dates, retry strategy, and any forced JSON or schema constraints if used. Include multiple runs or confidence intervals to assess variance.
- Add at least one non-NLI task (e.g., cross-lingual sentiment classification or QA) and include few-shot prompting. Also, add strong encoder baselines (e.g., XLM-R-large) on the same test sets to contextualize LLM performance.
- Provide ablations on post-processing: compare strict label-only parsing, permissive parsing, bilingual label acceptance, and show how Table 3 metrics change. This will clarify whether Table 4’s invalid-label burden is driving the main conclusions.
- Clarify the Gemini “Urdu support” statement in Section 4.2, since Tables 3, 5, and 7 contain Gemini–Urdu results. If “support” refers to frequent moderation blocks or character-handling issues, state that precisely and quantify it.
- Ethics: Instead of blanket BLOCK_NONE, consider a controlled protocol for safety overrides, document the categories of content encountered in XNLI that trigger blocks, and justify why disabling protections is necessary and safe in this research context.

Typos / terminology:
- Replace “Natural Language Interface (NLI)” with “Natural Language Inference (NLI)” throughout (e.g., Section 3.2.1).
- Table 2: multiple entries are malformed or mixed-script; these must be corrected and re-checked by native speakers before results are trusted.
- Punctuation/formatting issues in prompts (e.g., mismatched quotes) appear in Table 1 and Table 2; clean these to avoid tokenization oddities.

Criteria that could raise my score:
- Provide corrected, human-validated prompts and label-language parity, re-run experiments with decoding details and variance estimates, and demonstrate that the English advantage and GPT-4 dominance persist.
- Add at least one more task and a few-shot baseline; include a strong encoder model baseline on XNLI for context.
- Extend analysis to show robustness to post-processing choices, and add qualitative error analysis for high-invalid-label conditions.

## Confidence
4: Quite sure after careful checking — I examined the tables and methodology in detail. Some replication aspects depend on missing API/decoding details, but the core concerns are clear.

## Soundness
2.5: Between Poor and Acceptable — The study asks a relevant question, but prompt corruption, label-language confounds, limited scope, and insufficient controls weaken the validity of the conclusions.

## Excitement
2.5: Between potentially interesting and interesting — The topic is important, yet the current execution undercuts the potential impact.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
- The idea is relevant to ACL and the community cares about multilingual evaluation in low-resource settings. However, corrupted prompts (Table 2), English-only labels for all languages, and insufficient experimental controls lead to confounded conclusions. With corrected prompts, parity in label language, stronger baselines, and clearer methodology, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges the narrow task scope and zero-shot only setup. However, the societal impact and ethics discussion is thin given that harmful-content filters were disabled for Gemini (Appendix Table 6). The paper should discuss:
- Risks of disabling protections, even for evaluation.
- Potential harms from misclassification in sensitive languages or domains.
- Equity implications of recommending “ask in English” when many users cannot or prefer not to use English.
- The responsibilities of researchers when handling multilingual toxicity in benchmarks and systems with varying moderation behavior.

## Ethical concerns
- Disabling Gemini’s safety filters (BLOCK_NONE across categories) without a thorough justification or a mitigation plan is an ethical red flag. The paper should explain why this is necessary, how harmful content was handled, and what safety protocols were followed.
- The study implies that English prompts are “better,” which, if taken at face value, can reinforce linguistic inequities. The paper should carefully contextualize this claim and avoid normative recommendations that marginalize non-English speakers.
- None of these issues are unresolvable, but they require a more careful ethics section and, ideally, safer evaluation procedures.

## Needs Ethics Review
Yes — due to disabling safety filters and insufficient discussion of implications for multilingual users and potential misuse.

## Reproducibility
3: Reproducible with difficulty — The prompts are given in principle, but many are malformed; decoding/API details are missing; and commercial model variability is not controlled. A public repo with corrected prompts and scripts would help.

## Datasets
1: No usable datasets submitted. The paper uses XNLI and a machine-translated Bangla XNLI; nothing new is released.

## Software
1: No usable software released. The work would benefit from sharing exact prompts, parsing scripts, and evaluation code.