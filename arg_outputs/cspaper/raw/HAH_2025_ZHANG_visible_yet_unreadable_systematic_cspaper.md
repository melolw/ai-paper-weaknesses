# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper probes whether modern vision–language models (VLMs) can read text that remains legible to humans but violates typical glyph boundaries. Two small, psychophysics-inspired benchmarks are introduced: (a) Chinese four-character idioms whose characters are split (horizontally, vertically, diagonally) and recombined across positions, and (b) English eight-letter words whose two halves are overlaid in different colors. Human participants achieve near-perfect recognition, while multiple VLMs perform poorly. The authors argue this reveals a structural blind spot: models rely on generic visual invariances rather than symbol-centric segmentation and composition.

## Summary Of Strengths
- Clear problem framing: testing human–AI asymmetry in reading under controlled visual perturbations is a meaningful question for multimodal NLP.
- Cross-script evaluation: examining both Chinese logographs and English alphabetic words increases the generality of the observation.
- Simple, replicable generation procedures: Figures 2 and 3 clearly illustrate the perturbation pipeline, making the stimuli creation straightforward to reproduce.
- Head-to-head results across many popular VLMs: Table 3 and Figure 4 show a consistent drop under perturbation across closed- and open-source systems, with differences by prompting strategy.
- The “visible-but-unreadable” setup is an interesting diagnostic distinct from typical OCR/VQA settings, potentially useful as a robustness stress test for future models.

Specific figure/table remarks supporting strengths:
- Figure 1 concisely diagrams the end-to-end evaluation flow, from stimuli creation to parallel human/model testing; this helps readers quickly grasp the evaluation design.
- Figure 2 and Figure 3 make the manipulation concrete, reducing ambiguity about how the composites are produced and why humans can still resolve them.
- Table 3 provides a broad sweep over models and prompts for the idiom task; despite different prompts, strict match remains extremely low, reinforcing the claimed brittleness.
- Figure 4 shows the same trend for English, with detailed prompts providing only a modest lift; the visual contrast across models underlines that this is not an isolated failure of one system.

## Summary Of Weaknesses
1) Limited dataset scale and diversity; over-strong generalization of claims
- Both benchmarks are small (100 Chinese idioms, 100 English words) and rendered in what appears to be a single font and resolution (Section 3.2). The paper sometimes generalizes to “universal failure mode” and “cross-script blind spot” (Abstract, Section 5) that the presented evidence does not fully justify. More languages, fonts, sizes, background clutter, and parameterized overlap/offsets are needed to substantiate universality.

2) Under-specified human study and statistics
- Section 3.4 mentions 10 participants and “report aggregate accuracy with confidence intervals,” but tables and figures present only point values “100%.” There are no CIs or per-item confusion matrices shown. If accuracy is truly 100%, it should be shown transparently, and any borderline items should be discussed. Without basic details (participant demographics, display conditions, timing, screening), the human–model gap is hard to calibrate.

3) Incomplete evaluation design for VLM inference stochasticity
- API inference temperature, sampling parameters, and retry policies are not specified. Several results depend on prompts (Tables 1–2), but the number of generations per item per prompt is unclear; Section 7 of the checklist mentions “averaged over 2 runs,” which is weak given high variance in API responses. Stronger aggregation (n≥5–10 samples per item) or deterministic decoding would yield more defensible estimates.

4) Missing comparisons to OCR and segmentation baselines
- The benchmark targets reading robustness. However, there are no comparisons to OCR-specific systems (e.g., Tesseract, TrOCR, CRNN/CTC variants) or to simple classical segmentation pipelines (color-thresholding and layer separation in the English overlap; connected-component analysis or radical-level segmentation for Chinese). Such baselines would help determine whether the deficit is specific to current VLM architectures or a broader vision issue. As it stands, the conclusion that “architectural blind spot” is the main cause is plausible but not isolated from simpler explanations.

5) Limited parametric analysis; no accuracy–perturbation curves
- The psychophysics framing (Section 2.3) suggests controlled variation. Yet the paper uses a single fusion strength per stimulus. There are no curves showing recognition as a function of overlap amount, color contrast, stroke collision density, or cut axis/offset. This prevents understanding where models fail and what design choices matter, and it weakens the claim that the effect is systematic rather than stimulus-specific.

6) Evaluation metrics for Chinese are ad hoc
- For idioms, a difflib-based “Average Similarity” is reported (Section 3.4, Table 3). This string similarity can be misleading for Chinese, where a single wrong character often changes meaning entirely. Edit distance or character-level accuracy distributions would be more interpretable. Also, the preprocessing “removing all non-Chinese characters using regex” could inadvertently bias results if models output near-miss characters or include punctuation; details on normalization and mapping variants are missing.

7) Over-interpretation without qualitative failure analysis
- The paper asserts that models produce “unrelated or incoherent outputs” (Abstract, Section 4.1) but provides no systematic error taxonomy or examples. Qualitative panels contrasting human-readable composites with typical model outputs would substantiate this claim and guide future mitigation.

8) Ambiguity around figures that rank “hardest/easiest” items
- Figure 5 and Figure 6 list hardest/easiest cases, but the methodology for ranking, number of trials per item, and model aggregation are unclear. In Figure 5, several “easiest” words still top out below 60% accuracy, which suggests limited signal and small-N effects rather than clean separability. The text states humans show “no meaningful difference” across these items, but no human-item-level stats are shown.

9) Reproducibility is not yet ensured
- Code and stimuli are promised upon acceptance. Given small datasets and simple generation, release at submission should be feasible. Absent code, details such as font family, rendering engine, color space, anti-aliasing, exact idiom/word lists, and random seeds are essential for replication; most are not specified.

10) Related work coverage around OCR robustness and VLM text-reading deficits is thin
- Section 2 cites general VLM and psychophysics literature, and one recent Chinese sub-character paper [27]. It omits several directly relevant recent robustness and OCR/VLM reading works (see “Potentially Missing Related Work”).

Figure/table-linked critiques:
- Figure 4: The bar chart shows modest differences among closed-source models and near-zero performance for open-source models, but lacks error bars or per-model variance across runs. Given stochastic decoding, the absence of uncertainty quantification weakens the conclusion strength.
- Table 3: Average Similarity differs widely across prompts and models, but strict match is near zero everywhere; this could also reflect the difficulty of exact four-character recovery under any ambiguity rather than a uniquely VLM failure. A breakdown by character position and per-character confusion would clarify whether models partially recover structure.

Why these weaknesses matter:
Collectively, these issues reduce confidence that the observed failures are (a) robust across reasonable rendering conditions, (b) specifically attributable to the hypothesized architectural blind spots rather than evaluation choices, and (c) generalizable beyond these two small datasets. Strengthening statistical rigor, baselines, and parametric analyses would convert an intriguing observation into a persuasive, citable benchmark study.

## Potentially Missing Related Work
1) Cheng et al., “How Robust is OCR-Reasoning? Evaluating OCR-Reasoning Robustness of Vision-Language Models under Visual Perturbations,” 2026 — Directly examines robustness of VLMs and OCR pipelines under controlled corruptions. Should be discussed in Related Work and compared in Section 4; adopt their perturbation taxonomy to structure the psychophysics-inspired analyses.

2) Kargaran et al., “GlotOCR Bench: OCR Models Still Struggle Beyond a Handful of Unicode Scripts,” 2026 — Introduces a large multilingual OCR benchmark; relevant to generalizing the cross-script claim beyond English/Chinese. Cite in Section 2.2 and discuss potential extension plans in Section 5.

3) Tangtartharakul et al., “Visual language models show widespread visual deficits on neuropsychological tests,” 2026 — Provides convergent evidence of specific low-/mid-level visual deficits in VLMs. Discuss in Sections 2.1/2.3 to connect psychophysics framing with broader visual competency gaps.

4) Fang et al., “Unveiling the Fragility of Vision-Language Models: Multi-Modal Adversarial Synergy via Texture-Constrained Perturbations and Cross-Modal Optimization,” 2026 — Security-oriented multimodal adversarial work; relate in Section 2.3 and the Discussion as an alternative but complementary route to stress models beyond natural renderings.

5) Lee et al., “Do VLMs read or rewrite?,” 2026 — Empirically studies whether models transcribe or rewrite degraded text. Highly relevant to interpreting “incoherent/unrelated outputs”; cite in Section 4.1 and analyze outputs accordingly.

6) Ren et al., “Seeing the Threat: Vulnerabilities in Vision-Language Models to Adversarial Attack,” 2026 — Offers a taxonomy for evaluating multimodal vulnerabilities; situate the proposed stimuli within that framework in Section 5.

7) Zhang et al., “Do Images Speak Louder than Words? Investigating the Effect of Textual Misinformation in VLMs,” 2026 — Shows susceptibility to misleading text; relevant to understanding how models arbitrage conflicting signals. Discuss in Section 5 as a neighboring failure mode involving text dominance vs. visual evidence.

## Comments Suggestions And Typos
Actionable suggestions that can change my assessment:
- Expand the benchmarks and add parametric control:
  - For English overlays, vary color contrast, spatial offset, overlap degree, and font families; plot accuracy–perturbation curves as in psychophysics (Section 2.3 goal). For Chinese, vary cut axes, offsets, radical-boundary respect/violation, and font styles. Include at least 3–5 settings per factor.
- Strengthen human study reporting:
  - Provide participant demographics, display specs, item-level accuracies, CIs, response times, and attention-check outcomes. If accuracy truly is 100%, show per-item distributions and note any marginal cases.
- Add OCR and segmentation baselines:
  - Evaluate Tesseract and at least one modern neural OCR (e.g., TrOCR) plus classical color-channel separation for English and simple morphological segmentation for Chinese composites. This will localize whether the gap is VLM-specific or more general.
- Report decoding details and uncertainty:
  - State temperature, top-p, max tokens, and retry policy. For each item, collect multiple generations or enforce deterministic decoding; report per-model variance with error bars on Figure 4 and an uncertainty table for Table 3.
- Improve error analysis:
  - Provide qualitative panels with typical mistakes, a taxonomy of failure modes (e.g., hallucinated words vs. partial matches vs. language-switching), and character-position error breakdowns for Chinese. Replace or complement difflib similarity with per-character accuracy and edit distance.

Typos/clarifications:
- Table 3 “Average Matching Rate” is called “Average Similarity” in text; use a consistent term and define the exact normalization.
- Section 3.3 model names and versions should be fixed and consistently referenced across text and figures.
- Section 4.2: Figure 5 labels include truncated strings like “pyna,” “neuf,” “acou,” “sche,” “keyb.” Clarify whether these are model outputs, word fragments, or placeholders.
- Ensure all figures have legible axes and units; Figure 4 should include error bars if multiple runs are averaged.

Criteria for score improvement:
- Release code and exact stimuli at rebuttal, with rendering details (fonts, colors, anti-aliasing, resolution) and full word/idiom lists.
- Add at least one OCR baseline and one simple segmentation baseline with quantitative results.
- Provide uncertainty estimates and decoding settings; include parametric analyses on at least one perturbation factor and show curves.
- Expand human-study reporting with CIs and per-item stats; include a few qualitative failure examples and an error taxonomy.

## Confidence
3: Reasonably confident but not fully verified; I am familiar with VLM robustness and OCR evaluation, but several experimental details are under-specified and could change some conclusions after clarification.

## Soundness
2.5: Between Poor and Acceptable; interesting and plausible findings, but current empirical design lacks key baselines, parametric analyses, and statistical reporting to fully support the broader claims.

## Excitement
2.5: Between potentially interesting and interesting; the setup is appealing and could be impactful if strengthened, but current scope is narrow.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The idea and early evidence are compelling, the figures/tables make a strong prima facie case, and the topic is relevant to multimodal NLP. However, the benchmarks are small and not yet parameterized, human-study/statistical reporting is insufficient, decoding and variance are under-specified, and key OCR/segmentation baselines are missing. With the suggested additions and clearer uncertainty quantification, this could become a solid Findings paper and a useful robustness diagnostic.

## Best Paper Justification
N/A (score below award threshold).

## Limitations And Societal Impact
The paper notes limitations around the number of scripts and controlled perturbations. This is correct but incomplete. Additional limitations to discuss:
- Single-font, lab-like renderings may not reflect real-world documents.
- Closed-source API behavior can change over time; reproducibility may drift without pinned versions and decoding configs.
- The benchmark may be used adversarially to bypass VLM-based content filters; release should include guidance and potential mitigations.
Potential positive impacts include improved accessibility, cultural-heritage digitization, and safer deployment by revealing brittle failure cases. The authors should explicitly address dual-use concerns and how to responsibly release adversarial-like stimuli.

## Ethical concerns
None beyond standard concerns for releasing a robustness benchmark that could be used to evade automated systems. Human-subjects details appear minimal risk, but the protocol and consent process should be clarified when releasing the data/code.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty. Stimuli generation appears simple and prompts are listed, but code and exact rendering parameters are not yet provided; proprietary APIs and unspecified decoding settings limit repeatability.

## Datasets
3: Potentially useful. If released with full details and parametric variants, the benchmark could be a handy robustness testbed.

## Software
3: Potentially useful. The promised stimuli-generation and evaluation scripts would be helpful if made available with clear instructions.