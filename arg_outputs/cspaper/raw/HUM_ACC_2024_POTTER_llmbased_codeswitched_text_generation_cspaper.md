# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies grammatical error correction (GEC) for code-switched (CSW) learner text. It first filters a genuine CSW subset from Lang-8 and manually validates it. To address data scarcity, it proposes three CSW text generation methods (translation-based, parallel-corpus-based via alignment, and LLM prompting), evaluates their CSW characteristics using established CSW metrics, and finds that LLM prompting best matches genuine CSW patterns. It then injects errors into the generated CSW text using an extended PIE-style rule set and a backtranslation-like Rev-GECToR approach, forming two synthetic CSW GEC datasets. Finally, it trains a GECToR-based tagger with an added CSW token class under a three-stage schedule and shows improved ERRANT F0.5 on a held-out genuine CSW test set compared with strong monolingual baselines, while remaining competitive on BEA-2019.

## Summary Of Strengths
- Topic relevance and motivation: The focus on CSW GEC for ESL learners is timely and important for inclusive, real-world language technology. The introduction clearly frames why current monolingual GEC pipelines struggle on CSW and why this matters pedagogically.
- Resource creation and methodology: The paper constructs a substantial synthetic CSW GEC corpus via a two-step pipeline (CSW text generation then error injection). It thoughtfully compares three CSW generation strategies and quantitatively argues (Table 1) that LLM prompting yields CSW statistics closest to genuine ESL CSW text.
- Model and training protocol: The GECToR-based architecture with a CSW token class, plus a staged training schedule mixing monolingual and CSW data, is sensible for the low-resource CSW setting.
- Empirical gains on CSW: Table 2 shows consistent improvements on genuine CSW test data over a strong RoBERTa-base GECToR and a seq2seq T5 baseline. The inference-tuning phase further boosts recall on CSW without catastrophic precision loss.
- Error-type focus: The targeted error injection (noun, pronoun, word order, punctuation, determiners) aligns with observed weaknesses of monolingual systems on CSW (Table 3 in Appendix B) and is partially validated by improved per-category outcomes for the proposed model (Table 6 in Appendix E).
- Figures and tables: Figure 2 provides a concrete prompt used for LLM-based CSW generation, helping readers reproduce the style of generation; Table 1 and Table 2 clearly support the central claims about the relative quality of synthetic CSW text and the improved CSW GEC performance, respectively.

## Summary Of Weaknesses
1) Evaluation scope and representativeness of CSW test data:
- The genuine CSW set is small (5,875 total pairs across 6 language pairs with 81.9% English–Japanese), and only 10% is used as test. The evaluation therefore hinges on a few hundred instances dominated by English–Japanese. There are no per-language or per-type breakdowns on the test set. This matters because the central claim is about handling CSW broadly, yet Table 2 aggregates across a highly skewed language mix, making generalization beyond English–Japanese uncertain. At minimum, per-language results or stratified analyses would make the conclusions more credible.

2) Lack of human evaluation for synthetic CSW quality:
- The similarity judgment relies solely on automatic CSW metrics (CMI, M-Index, I-Index, Burstiness, CF1–3) in Table 1. These are known to be coarse and do not guarantee fluency, pragmatic plausibility, or sociolinguistic appropriateness of switching. The paper itself acknowledges limits of these metrics in Section 6. Without any human study (even a small annotator check for naturalness and well-formedness), the claim that the LLM-prompted CSW text is “high-quality” remains under-supported, especially since subsequent error injection may interact with unnatural switch points in ways that bias training.

3) Missing ablations on generation choices and training mix:
- The paper reports that LLM-generated CSW is most similar to genuine CSW by Table 1, but the final model’s gains are not dissected for the contribution of each generation approach. For example, there is no ablation showing model performance when trained with translation-based CSW or parallel-corpus-based CSW versus LLM-prompted CSW. Similarly, the two error injection strategies (PIE vs. Rev-GECToR) are combined in training, yet Table 2 does not separate their marginal contributions. Given that the methodological novelty centers on synthetic data, the absence of these ablations weakens causal attribution of the improvements.

4) Baseline coverage and fairness of comparisons:
- Table 2 compares to RoBERTa-base GECToR and T5-small. Important baselines are missing: multilingual seq2seq models (e.g., mT5-small/base), stronger edit-based variants (e.g., DeBERTa- or ELECTRA-based GECToR of similar size), and LLM-inference baselines (instruction-tuned LLMs prompted for CSW-sensitive GEC). Since the task is inherently multilingual and CSW heavy, comparisons to multilingual GEC systems and prompting-based GEC are necessary to establish competitiveness beyond a single monolingual tagger baseline. This is especially relevant because seq2seq models can rewrite across languages more flexibly than taggers.

5) Reproducibility and labeling details:
- Figure 2 shows an example prompt, but the exact in-context examples are not shareable due to dataset privacy, and the LLM is proprietary (GPT-3.5). It is unclear how CSW token supervision for the added class is obtained and labeled consistently across datasets. Annotation reliability for Lang-8 corrections and for “missed errors” is handled by a single annotator with no inter-annotator agreement or guideline summary. The training schedule references Appendix C for exact splits, but many practical details remain underspecified: precise label set for GECToR edits, proportions of synthetic vs. genuine CSW per epoch, and any language-ID or tokenization strategy to robustly handle non-English scripts. These omissions increase variance for reimplementation and make it difficult to validate the central claims independently.

Explicit references to figures/tables supporting or undermining claims:
- Figure 2: The prompt example is useful, but since the 10 real CSW examples cannot be shared, replication of LLM generation style might diverge in content and diversity. Clarify the sampling strategy and error filtering applied to LLM outputs.
- Table 1: While the LLM CSW distribution is closer to genuine CSW than translation-based or parallel-corpus methods on several metrics, these metrics are not sensitive to pragmatic functions of switches or semantic drift. A human assessment would substantiate that the statistical proximity also reflects qualitatively acceptable CSW use.
- Table 2: The “Inference Tweaks” row shows the biggest CSW gain (F0.5 from 55.02 to 63.71) but with a BEA drop (from 68.92 to 66.59). This suggests that much of the CSW gain is driven post hoc by thresholding rather than modeling or data contributions alone. An ablation showing model performance without tweaks on CSW, and the delta per tweak, would clarify how much the training pipeline versus calibration drives the gains.
- Table 3 (Appendix B) and Table 6 (Appendix E): The baseline’s per-category collapse on CSW (e.g., PUNCT and WO) is compelling, and the proposed model’s per-category improvements are encouraging. Yet absolute F0.5 values in Table 6 for NOUN and PUNCT remain quite low, indicating substantial headroom. Reporting per-language per-category metrics would further illuminate where the method helps most.

## Potentially Missing Related Work
1) Tarunesh et al., “From Machine Translation to Code-Switching: Generating High-Quality Code-Switched Text,” 2021 — A neural MT-based CSW generation approach widely cited in CSW text generation. It should be discussed in Section 2.2.1 as a strong pre-LLM generation baseline and, if feasible, added as a data-generation baseline in the synthetic CSW creation pipeline.

2) Kuwanto et al., “Linguistics Theory Meets LLM: Code-Switched Text Generation via Equivalence Constrained Large Language Models,” 2024 — Proposes EZSwitch that integrates Equivalence Constraint Theory with LLMs for well-formed CSW generation. Relevant to Section 2.2.1 as a linguistically principled alternative to unconstrained LLM prompting; could be compared against the LLM prompting-based dataset both in Table 1 and via a downstream ablation.

3) Yu et al., “Code-Switching Text Generation and Injection in Mandarin-English ASR,” 2023 — Although in ASR, it develops CSW text generation and injection strategies that improve downstream performance. It is relevant to Section 2.2.2 on synthetic data creation and should inform design choices and error analysis.

4) Sheth et al., “Beyond Monolingual Assumptions: A Survey of Code-Switched NLP in the Era of Large Language Models across Modalities,” 2025 — A survey contextualizing LLM-era CSW methods. It would help position this work in Section 1 or Related Work and identify emerging evaluation practices beyond metric-only similarity.

5) Winata et al., “Can Large Language Models Understand, Reason About, and Generate Code-Switched Text?” 2026 — Provides systematic evaluation of LLMs on CSW comprehension and generation. Useful for discussion in Section 4 or the Limitations to connect the present GEC findings with broader CSW reasoning and generation capabilities.

6) “Generating Context-Aware Code-Switched Text Using Probabilistic Modeling and Generative Refinement,” 2025 — Presents a pipeline that constrains switch points probabilistically prior to LLM refinement. Could be compared in Section 2.2.1 as a complementary alternative to the paper’s three generation approaches.

Note: Items 4–6 are forward-looking but directly relevant; at minimum, discussion would clarify where this work sits within the rapidly evolving CSW–LLM generation landscape.

## Comments Suggestions And Typos
Actionable suggestions:
- Report per-language performance and per-language error-type breakdowns on the genuine CSW test split, given the heavy English–Japanese skew. If sample size per language is small, at least provide confidence intervals or bootstrap estimates.
- Add an ablation study isolating the contributions of each CSW generation method and each error-injection method to downstream CSW F0.5. For instance: train with only LLM CSW vs. only translation-based CSW vs. only parallel-corpus CSW, and train with only PIE vs. only Rev-GECToR vs. both.
- Include a small-scale human evaluation of CSW naturalness and switching appropriateness on a stratified sample from each generation method. Even a 2–3 question protocol on fluency, appropriateness of switches, and semantic fidelity would complement Table 1.
- Strengthen baselines: add mT5-small/base or another multilingual seq2seq GEC model of comparable size; include a simple LLM-inference baseline (carefully prompted) for CSW-aware GEC; and, if feasible, a larger edit-based variant with similar parameter count to verify whether the gains are from CSW data rather than architectural choices.
- Clarify supervision for the CSW token class: how are CSW tokens labeled across genuine and synthetic data, what heuristics or LID tools are used, and how are ambiguous cases handled? Provide inter-annotator agreement or at least a consistency check on the manual validation of Lang-8 corrections and “missed errors.”
- Expand ERRANT evaluation details: how does ERRANT treat non-English tokens and CSW contexts? If there are known limitations, consider reporting complementary metrics or a manual spot-check on edit correctness specifically in CSW spans.

Criteria that could raise my score:
- New ablations demonstrating the marginal impact of each synthetic data source and error type on CSW F0.5.
- Per-language results with uncertainty estimates and a brief human evaluation validating synthetic CSW quality.
- Inclusion of stronger multilingual and LLM-based baselines that confirm the method’s advantage is not an artifact of baseline choice.
- Clearer, reproducible details for CSW label supervision and data release with documentation sufficient for re-creation of the generation steps.

Typos and minor issues:
- Section 2.2.2: The text lists targeted error types as “noun, pronoun, punctuation and word errors,” while earlier also mentioning “determiner” and “word order.” Please harmonize.
- Table labeling: Ensure consistent notation for F0.5 across main and appendix tables (subscript formatting varies).
- Some references repeat BEA-2019 citation entries (Bryant et al., 2019a/2019b) with identical titles; verify deduplication and correct mapping to shared task vs. test set usage.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5: Between Acceptable and Strong — The overall pipeline is coherent and empirical improvements on CSW are supported by Table 2, but missing ablations, limited test diversity, and lack of human validation on synthetic CSW reduce the strength of the claims.

## Excitement
3.5: Between interesting and exciting — The work fills an important gap and the resource angle is valuable. With stronger evaluation and broader baselines, it could be even more compelling.

## Overall Assessment
4: Conference — accept to ACL main. The paper presents a timely, well-motivated contribution with a substantial CSW GEC dataset and a practical training recipe that improves over strong baselines on genuine CSW inputs. The main reservations concern evaluation breadth, lack of human validation for synthetic CSW, and missing ablations/baselines; these appear addressable before camera-ready and do not undermine the central contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section candidly notes the English–Japanese skew and the constraints of a sequence-tagging approach. I would add:
- Potential bias transfer: Synthetic CSW that reflects specific switching norms might encode sociolinguistic biases that disadvantage learners from other communities. Human validation across demographic and language-pair strata would mitigate this.
- Educational setting risks: Overzealous correction in mixed-language contexts might implicitly discourage culturally appropriate CSW. Consider UX and feedback design that explicitly distinguishes “English grammar correction” from “language choice” to avoid penalizing CSW itself.
- Data governance: Clarify privacy considerations in handling and filtering Lang-8 data, and ensure the released datasets are fully de-identified and compliant with platform policies.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible — The approach and training schedule are described, and figures/tables support replication. However, reliance on proprietary LLMs, lack of shareable in-context examples, and limited details on CSW token labeling reduce reproducibility.

## Datasets
4: Useful — The synthetic CSW GEC datasets would be valuable to the community, especially if accompanied by documentation, per-language splits, and generation scripts.

## Software
3: Potentially useful — If released with data generation and training code, it will aid replication; otherwise, impact is limited to methodological description.