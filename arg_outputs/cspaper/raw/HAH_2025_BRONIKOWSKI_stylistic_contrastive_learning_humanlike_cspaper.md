# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes Stylistic Contrastive Learning (SCL), a framework to make LLM outputs “sound more human.” A lightweight Transformer encoder is trained with a supervised contrastive loss (Equation 1) to separate human and AI texts while also supervising auxiliary style dimensions (lexical diversity, syntax, idioms, discourse markers, emotion). At inference, the base generator (GPT-5, kept frozen) is steered via a natural-language style prefix derived from the encoder’s human-style centroid (average or domain-specific). Experiments across argumentative essays, news leads, and chat report improved lexical diversity, higher idiom and discourse-marker rates, reduced stylometric detectability, and slightly better human “sounds-human” ratings, with minimal loss in semantic fidelity. The paper also discusses risks of reduced detectability and advocates provenance mechanisms.

## Summary Of Strengths
- Problem relevance and framing: The paper targets a well-observed gap between LLM and human writing along interpretable stylistic dimensions (idioms, discourse markers, syntactic templates). The motivation is clear and well aligned with ACL communities in generation, discourse, and detection.
- Conceptual simplicity: The approach uses a standard supervised contrastive objective (Equation 1) to learn a human-style manifold and applies generator-agnostic prefix steering. The idea is easy to grasp and potentially practical with closed-weight models.
- Multi-metric evaluation intent: The authors attempt to triangulate effects using detectability, lexical diversity (distinct-n), idiom/connective counts, and human ratings. Table 2 reports sizeable detectability reductions and diversity gains on essays; Tables 3 and 4 indicate generalization to chat and news.
- Ethics and risk awareness: The paper acknowledges that SCL can hinder stylometric detection and recommends provenance measures and domain-appropriate steering.
- Equation clarity: Equation 1 correctly instantiates supervised contrastive learning, and the text links it to auxiliary style heads that are meaningful to the stated goals.

Specific results references:
- Table 2 shows detectability drops from 72.4% to 53.6–54.1% TPR at 10% FPR on ArgEssay, along with increases in Dist-2, idioms, and discourse markers, which supports the core claim that SCL reduces stylometric detectability and increases stylistic variety.
- Table 4 shows higher distinct-3 and compression-diversity for SCL-Domain on NewsNYT, consistent with an uptick in discourse markers, aligning with the hypothesized drivers of perceived humanness.

## Summary Of Weaknesses
1) Underspecified steering mechanism (critical). The core operational step, converting a learned style vector into a natural-language prefix s(z*), is not concretely described. Section 3 states that s(z*) is “derived” from the average-human or domain centroid and “selected on validation,” but the paper does not specify:
   - How text is generated from z* (template? retrieval? learned verbalizer? decoding over a style lexicon?).
   - How long the prefix is, whether it changes by prompt, and how sensitive results are to its wording.
   - Whether s(z*) is optimized per instance or globally fixed; how selection avoids overfitting to detectors or raters.
   This gap makes the method hard to reproduce and weakens the causal interpretation that SCL, rather than clever prompting, drives gains.

2) Dataset construction and statistics are missing. Section 4 references three domains, but there are no dataset sizes, token counts, topic distributions, or representative examples. We cannot assess:
   - Balance/coverage across prompts and lengths;
   - Whether human/AI topics overlap or leak across splits;
   - How idioms/connectives vary by domain.
   Without basic dataset tables, replication and external assessment are not feasible.

3) Baseline under-specification. “Open-LLM-FT (human)” is not identified by model name, size, tokenizer, or training data. Hyperparameters for LoRA are only given in the appendix for a separate baseline, but not tied to the exact model used in Tables 2–4. This hampers fair comparison and reproducibility, particularly since the strongest claims hinge on outperforming this baseline.

4) Metrics reported without uncertainty or full calibration details in the main paper. While Section 4.1 promises bootstrapped 95% CIs and ROC-AUC, Table 1 (semantic fidelity) and Table 2 (main results) present point estimates without CIs. For borderline human-rating shifts (e.g., 3.7 → 4.2), interval estimates and effect sizes are essential to rule out noise. Similarly, detector ROC-AUCs and reliability curves are deferred to the appendix; operating points at 10% FPR are reasonable, but the full curves and calibration matter given the paper’s central detectability claims.

5) Ambiguity in auxiliary style heads and loss weighting. Section 3 lists auxiliary heads for lexical diversity, syntax, idioms, emotion, and discourse markers but does not provide:
   - The exact targets and feature computation per instance during training;
   - The joint loss, weighting coefficients relative to Equation 1, or optimization schedule;
   - How noisy proxy labels (e.g., idiom/marker counts) are stabilized and whether the heads are multi-tasked on shared batches or curriculum-trained.
   The absence of a precise loss formulation undermines implementability.

6) Limited human evaluation reporting. The protocol is described, but essential specifics are missing in the main text:
   - Number of prompts rated per domain and per condition;
   - Exact inter-rater agreement (α values promised but not shown);
   - Rater calibration or attention check outcomes beyond thresholds.
   Given the subjective nature of “sounds human?”, transparency here is crucial.

7) Potential mismatch between goals and ethics. The paper is explicit that SCL reduces detectability (Table 2, Table 3), but the evaluation does not stress-test responsible-use scenarios, e.g., educational integrity or impersonation. While the discussion mentions watermarking and provenance, there is no empirical assessment of compatibility with known watermarks or with detector-shift scenarios. Given the stated risks, stronger empirical treatment would be appropriate.

8) Missing or placeholder citations and editorial issues that affect credibility. Appendix A.1 includes “(author?)” placeholders for two tools ([8], [17]); multiple references are future-dated without publication details; and several claims rely on resources “in supplementary materials,” which are not necessary for core understanding but currently indispensable to replicate metrics.

9) Limited novelty positioning. The contrastive-learning angle applied to style is sensible, but the paper does not engage with closely related contrastive or steering approaches in generation and detection, nor with dedicated AI→human style transfer. This makes it difficult to judge genuine conceptual contribution versus recombination of known techniques.

10) Dependence on a closed generator and lack of release details. The main method is evaluated by steering a closed API model, with no commitment to release code, prefixes, or the trained encoder at review time. Section 5 cites “will release” language, which does not satisfy ARR/ACL expectations for reproducibility.

Explicit references:
- Equation 1 correctly formulates SupCon, but the paper never specifies the full training objective combining SupCon with auxiliary style heads, leaving the optimization under-defined and preventing independent verification.
- Table 1 shows tiny absolute changes in BERTScore and QAFactEval (e.g., 0.874 → 0.886 and 0.612 → 0.631). Without CIs and per-domain breakdowns, it is unclear if such differences are statistically and practically meaningful.
- Table 2’s detectability reductions are large, but the absence of ROC-AUC and CI reporting in the main body, coupled with an opaque s(z*) derivation, makes it hard to attribute causality to SCL rather than hand-crafted prompting or domain mismatch. 
- Tables 3 and 4 provide out-of-domain and news metrics, but again lack uncertainty and detailed setup, and “Open-LLM baseline” remains underspecified.

## Potentially Missing Related Work
1) Paneru et al., “Please Make it Sound like Human: Encoder-Decoder vs. Decoder-Only Transformers for AI-to-Human Text Style Transfer,” 2026 — Directly tackles transforming AI text into human-like prose on parallel AI–human corpora. Should be discussed in Related Work (Section 2) and compared as a post-hoc transformation baseline in Section 4 and Table 2.

2) Gu et al., “MASH: Evading Black-Box AI-Generated Text Detectors via Style Humanization,” 2026 — Multi-stage style humanization to evade detectors. It is conceptually close to this paper’s goal and should be contrasted in Section 2 and evaluated against as an adversarial baseline in the detectability experiments (Tables 2–3).

3) Fang et al., “Your Language Model Can Secretly Write Like Humans: Contrastive Paraphrase Attacks on LLM-Generated Text Detectors,” 2025 — Contrastive paraphrase attacks subtracting machine-style from human-style distributions. Highly relevant to the contrastive framing in Section 3. Add to Related Work and discuss methodological differences after Equation 1.

4) Anonymous, “Interpretable Stylistic Variation in Human and LLM Writing Across Genres, Models, and Decoding Strategies,” 2026 — Provides interpretable stylistic features and genre effects that match the evaluation axes here. Cite in Section 2 and consider adopting their feature sets in Section 4 metrics.

5) Durandard et al., “LLMs stick to the point, humans to style,” 2025 — Shows humans accommodate style more than LLMs, directly motivating SCL’s objective. Add to Section 2 and discuss in Section 5’s interpretation.

6) Toney et al., “Comparing the Humanness of Machine-Generated and Human-Authored Text,” 2026 — A survey defining humanness metrics and protocols beyond Turing-style tests. Cite in Section 4 to justify evaluation choices and in Section 5 for broader context.

7) Ta et al., “FAID: Fine-grained AI-generated Text Detection using Multi-task Auxiliary and Multi-level Contrastive Learning,” 2026 — Strong detector using multi-level contrastive objectives. Include as a detector baseline in Section 4 and discuss alongside GLTR/RoBERTa in Table 2 and Table 3.

8) Guo et al., “DeTeCtive: Detecting AI-generated Text via Multi-Level Contrastive Learning,” 2024 — Contrastive detection model; relevant as a baseline and for understanding what features SCL must overcome. Add to Section 2 and incorporate as an additional detector in evaluation.

9) Su et al., “A Contrastive Framework for Neural Text Generation (SimCTG),” 2022 — Foundational contrastive training/decoding for generation and diversity. Should be cited in Section 2 and compared as an alternative to SCL in the diversity results (Table 4).

10) Zhang et al., “Personalized Text Generation with Contrastive Activation Steering (StyleVector),” 2025 — Activation-space style vectors for steering without finetuning. Highly relevant to “frozen generator” steering; discuss in Section 3 and compare conceptually in Section 5.

## Comments Suggestions And Typos
Actionable questions and suggestions:
1) Precisely define s(z*). Provide the algorithm that maps a centroid in style space to a natural-language prefix, with examples, length, and vocabulary constraints. Report ablations:
   - no prefix vs learned prefix vs hand-written prefix;
   - global fixed prefix vs per-domain vs per-instance;
   - sensitivity to prefix length and temperature.
   This is the single most important addition for reproducibility and to attribute gains to SCL rather than ad-hoc prompting.

2) Specify datasets. Add a table with, per domain: number of prompts, mean length, vocabulary size, topic categories, human/AI split sizes, and overlap controls. Include illustrative examples and clarify how AI outputs were generated for training the encoder vs for test-time evaluation to avoid leakage.

3) Complete the training objective. After Equation 1, write the full loss with auxiliary heads and weights, e.g., L = L_SupCon + Σ_k λ_k L_k. Describe targets, normalization, and batch sampling. Report λ_k and any curriculum or multi-task scheduling.

4) Expand evaluation reporting in the main text:
   - Add 95% CIs and effect sizes to Tables 1–4;
   - Include ROC-AUC for detectors and, if space is tight, at least summarize AUCs in the main body;
   - Provide the number of prompts rated per domain, Krippendorff’s α with CIs, and rater demographics breakdown; share rater calibration outcomes.

5) Strengthen baselines. Identify the exact “Open-LLM” model and LoRA setup. Add baselines from SimCTG (Su et al., 2022) for diversity, an activation-steering approach (e.g., StyleVector), and a dedicated AI→human style transfer model (e.g., Paneru et al., 2026). Evaluate against a stronger detector such as FAID or DeTeCtive.

6) Stress-test ethics claims. Empirically evaluate whether SCL preserves or disrupts known watermarking schemes, and include detector-shift experiments (train on A, test on B; switch models or domains). This will contextualize the stated risks and provide evidence-based guidance.

7) Report concrete examples. Include a small qualitative table of side-by-side outputs with idiom and discourse-marker highlights. Even 3–5 examples would help readers connect metrics to perceptual changes.

8) Clarify open- vs closed-weight applicability. Provide results on at least one open-weight LLM to show SCL’s portability. If GPT-5 access is versioned, note the specific API release used.

9) Editorial fixes and typos:
   - Appendix A.1: “(author?) [8]” and “(author?) [17]” placeholders must be corrected.
   - Table 2 caption: define Dist-2 (%) precisely and explain whether “%” refers to unique bigram ratio ×100 or another normalization.
   - Section 3: avoid duplicate “Training procedure” paragraph; currently appears to repeat content.
   - References [12]: The cited work title and venue do not match figurative-language evaluation as described; verify.
   - Ensure all future-dated citations include full venue information or arXiv identifiers.

Criteria that would change my score:
- Upward: A revised version that fully specifies s(z*), provides dataset statistics, adds uncertainty estimates to Tables 1–4, and includes at least one strong additional baseline and detector (e.g., SimCTG and FAID/DeTeCtive), plus an open-weight replication, would move me to consider Findings (3.0) or borderline conference (3.5) depending on results.
- Downward: If it turns out that s(z*) is largely hand-crafted or tuned post hoc per prompt, or if improved reporting shows non-significant human-rating gains and marginal detectability changes against stronger detectors, my score would drop to 2.0.

## Confidence
3 Reasonably confident but not fully verified: I understand the area and method, but key implementation details (s(z*)) are missing, and several baselines are under-specified, so I cannot fully verify claims.

## Soundness
2.5 Between Poor and Acceptable: The core idea is plausible and Equation 1 is fine, but incomplete method specification, under-reported uncertainty, and sparse baselines weaken support for the central claims.

## Excitement
2.5 Between potentially interesting and interesting: The goal and framing are timely, but the current execution is not yet compelling enough for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. Justification: The topic is relevant and the contrastive framing is promising, and Tables 2–4 suggest real movement on key metrics. However, the method’s pivotal component (textualization of the style vector) is insufficiently specified; datasets and baselines are under-detailed; and statistical reporting is incomplete in the main body. With a focused revision addressing these points, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s discussion acknowledges that reduced detectability can exacerbate plagiarism, impersonation, and misinformation risks, and argues for watermarking and provenance. I concur, but recommend empirical validation: test SCL’s interaction with watermarking, quantify detector-shift robustness, and analyze bias risks across writer populations, including non-native speakers. Also consider domain-appropriateness, since a generic “human” centroid may inject informality into formal registers.

## Ethical concerns
Two issues require attention:
- Intentional reduction of detectability is dual-use. The paper should include stronger empirical safeguards or deployment guidelines and test compatibility with provenance schemes.
- Authorship and disclosure sections at the end include “AI authorship” and tool-use specifics that would typically conflict with ACL authorship and anonymity policies. Ensure compliance with ARR/ACL policies for the camera-ready version and remove identity-revealing content.

Otherwise, datasets appear to avoid sensitive personal data, and human-rating protocols include fair compensation.

## Needs Ethics Review
No.

## Reproducibility
3 Reproducible with difficulty: Key parameters are given, but the crucial s(z*) derivation, dataset statistics, and some baselines are underspecified; closed-model dependence further complicates replication.

## Datasets
2 Documentary: No new datasets are clearly released, and dataset descriptions are insufficient; if released with full stats, they could support replication but have limited broader value.

## Software
2 Documentary.: No usable software at review time; a future release is promised. Clear code for the style encoder, s(z*) generation, and evaluation scripts would raise this rating.