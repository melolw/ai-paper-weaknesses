# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This is a survey on jailbreak attacks and defenses for large language models (LLMs) and multimodal large language models (MLLMs). It synthesizes datasets/benchmarks, attack taxonomies (non-parametric vs. parametric; competing objectives vs. mismatched generalization), and defense strategies (extrinsic vs. intrinsic), and contrasts the relatively mature unimodal landscape with the underexplored multimodal setting. The paper emphasizes limitations and forward-looking directions for multimodal jailbreak research, and includes an evaluation framework in the appendix. Figure 1 provides a high-level map from LLMs to MLLMs across evaluation benchmarks, attacks, defenses, and stated limitations/future directions.

## Summary Of Strengths
- Scope and organization: The survey gathers a wide range of work across unimodal and multimodal settings, structuring them coherently by attack/defense axes and by semantic vs. parametric access assumptions (Sections 4–5). This is accessible and useful for readers who need a quick entry into both literatures.
- Focused lens on multimodality: Compared to many general LLM safety surveys, the paper repeatedly returns to MLLMs, articulating gaps and specific research suggestions. Sections 3.3, 4.3, and 5.4 compile concrete multimodal limitations and clearly stated future directions that practitioners can operationalize (e.g., implicit toxicity, image-domain transfers, multimodal training interference, and robust image-based detection).
- Evaluation considerations: Appendix A discusses success definitions, metric choices (ratio vs. score-based), and judgment methods (human, rule-based, model-based), flagging important tradeoffs that regularly cause confusion in safety evaluation.
- Visual roadmap: Figure 1 (Page 2) is a helpful one-page map that aligns LLM vs. MLLM coverage across datasets, attacks, defenses, and limitations/future directions. It makes the paper’s thesis legible and could serve as a reference figure in talks or tutorials.

## Summary Of Weaknesses
1) Survey positioning relative to existing surveys is not fully established. The paper claims to provide a comprehensive overview, yet omits several closely related surveys on LVLM/MLLM safety and attack landscapes. Without discussing how this paper differs from or improves upon those, the unique contribution feels underspecified. This affects the significance and originality claims for a venue like ACL.

2) Limited synthesis beyond taxonomy recounting. While Sections 4 and 5 list many works, the analysis is often descriptive. The paper could better articulate cross-cutting insights such as: which defenses generalize across attack families, which evaluation setups correlate most with human judgments, or what failure modes dominate across model families. For example, in Section 5.4 “Limitations and Future Directions,” the points are reasonable but remain largely high-level, lacking prioritization, empirical evidence, or guidance for practitioners to triage effort.

3) No quantitative or systematic evidence to substantiate claims about gaps or trends. The paper would benefit from a small meta-analysis, e.g., a table of representative datasets with coverage by harm types, languages, modalities, or attack vectors; or a table of defenses with their main failure cases and computational costs. Currently, there are no tables synthesizing coverage, scope, or empirical comparisons. This reduces reproducibility and the utility of the survey for decision-making.

4) Lack of principled multimodal evaluation protocols. Appendix A provides general evaluation guidance, but it does not take a firm position for MLLMs on key open questions such as image perturbation–robust scoring, typography-induced text recovery, or defense evaluation under visually obfuscated semantics. For instance, the “Jailbreaking Judgment Methods” section does not discuss multimodal-specific pitfalls (e.g., OCR variance, font/handwriting artifacts, or image-only triggers) and how to normalize them across studies.

5) Some conceptual gaps in multimodal attack taxonomy. Section 4.1.2 focuses on typography, perturbations, and very brief mentions of domain shift, but only lightly touches complex multimodal chains (e.g., multi-image narratives, video, or tool-mediated visual reasoning) despite later recommending them as future directions. The gap between the rich future directions and the current taxonomy/coverage weakens the authority of the recommendations.

6) Figure-specific critique: While Figure 1 (Page 2) is a valuable overview, the “Future Direction” boxes on the right are presented as lists without clear linkage to concrete evidence or demonstrated failures in specific subsections. For instance, the “Unexplored Complex Multimodal Tasks” and “Neglected Image Domain Shift” items are asserted in Sections 4.3 and 5.4 but would be more convincing if the figure or nearby text connected these to representative negative results or case studies in the cited literature. As it stands, Figure 1 effectively organizes claims but underspecifies their empirical grounding.

7) Inconsistent depth across subsections and minor wording issues affect clarity. Some subsections provide concrete examples and citations, while others remain generic. For instance, Section 5.3 briefly notes transforming images to text to leverage unimodal defenses, then moves on without a deeper analysis of when modality reduction fails (e.g., for adversarial perturbations that do not survive captioning/OCR). There are scattered typos and grammatical errors that distract from the technical content (examples listed below).

Note: There are no results tables in the submission; consequently, I could not evaluate claims against tabulated benchmarks or ablations. The absence itself is a limitation for a survey that aims to guide practice.

## Potentially Missing Related Work
1) Liu et al., “A Survey of Attacks on Large Vision-Language Models: Resources, Advances, and Future Trends,” 2024 — Directly surveys attacks on LVLMs/MLLMs, including jailbreak, adversarial prompting, and poisoning; should be discussed early in Section 1 and Section 2 to position this paper’s jailbreak-centric angle and, in Section 4–5, to reconcile taxonomies and clarify what this survey adds for MLLMs.

2) Liu et al., “Safety of Multimodal Large Language Models on Images and Text,” 2024 — A systematic survey of MLLM safety with datasets, attack/defense coverage, and evaluation concerns. It should be cited in Section 1 and compared in Section 3 and Section 5 to show complementarities and differences, especially on evaluation protocols and defense recommendations.

3) Jeong et al., “Playing the Fool: Jailbreaking LLMs and Multimodal LLMs with Out-of-Distribution Strategy,” 2025 — Proposes JOOD, an OOD-based multimodal jailbreak framework; directly relevant to Sections 4.1.2 and 4.3 on domain transfer/mismatched generalization and should be included as an example of principled OOD-driven attack design.

4) Wang et al., “PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs,” 2025 — Organizes multimodal jailbreaks into atomic primitives, optimized via multi-agent RL; relevant to Sections 4.1.2 and 4.3, with explicit comparison on cross-modal asymmetries and black-box attack practicality.

5) Mao et al., “From LLMs to MLLMs to Agents: A Survey of Emerging Paradigms in Jailbreak Attacks and Defenses within LLM Ecosystem,” 2025 — Extends survey scope to agentic settings; useful to cite in Section 1 and in Section 4.3/5.4 to motivate agent-tool-vision pipelines as a frontier for multimodal jailbreaks and defenses.

6) Xu et al., “Utilizing Jailbreak Probability to Attack and Safeguard Multimodal LLMs,” 2025 — Introduces a probabilistic notion of jailbreak risk and a prediction network (JPPN); should be discussed in Section 5 and Appendix A to enrich the evaluation and defense toolset with risk estimation, and to suggest probability-guided defense strategies.

7) Chandna et al., “ExtremeAIGC: Benchmarking LMM Vulnerability to AI-Generated Extremist Content,” 2025 — A specialized benchmark illuminating domain-specific multimodal risks; relevant to Section 3.2 and 3.3 to broaden the benchmark discussion and motivate culturally and topically nuanced datasets.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide a comparative positioning table or paragraph in Section 1–2 explicitly contrasting this survey with other LVLM/MLLM safety and jailbreak surveys. Clarify unique contributions, e.g., the LLM-to-MLLM comparative lens, the attack/defense structuring, and the curated multimodal directions with concrete examples.
- Add at least one synthesis table that maps datasets (LLM and MLLM) to harm types, languages, image/text sources, task formats (single-turn, multi-turn, tool use), and evaluation protocols. Similarly, a defense table indicating assumptions (white/black-box, modality reduction, reliance on OCR), expected failure cases, and computational overhead would significantly improve utility for practitioners.
- Strengthen Section 4.1.2 and 4.3 by incorporating more detailed coverage of multi-image and video-based attacks, tool-augmented pipelines, and task reformulations that exploit cross-modal reasoning. Where possible, connect future directions to at least two concrete, cited failures or case studies to ground recommendations.
- Expand Appendix A with multimodal-specific evaluation issues, including OCR variance, font and typography normalization, image perturbation robustness, and protocol suggestions for consistent cross-paper comparisons.
- Revise Figure 1 caption and surrounding discussion to anchor each “Future Direction” to specific empirical gaps or recurring failures identified in Sections 3–5. This would convert the figure from a high-level map into an evidence-linked roadmap.

What could change my evaluation:
- Clear positioning vs. closely related surveys, with concrete differentiation.
- Inclusion of compact synthesis tables that enable readers to act on the literature (datasets and defenses), and a strengthened multimodal evaluation protocol section.
- Substantially enriched multimodal taxonomy coverage tied to representative negative results and explicit methodological guidance.

Typos and style issues (non-exhaustive):
- Page 1, Abstract: “multimodal domain remains underexplored” → “the multimodal domain remains underexplored.”
- Page 1, end of Introduction: “*multimodal* perspec-” → line break hyphenation; consider reflow.
- Page 2, Section 2.1: “or using training and decoding strategy” → “or using training and decoding strategies.”
- Page 3, “This issue indicates a misalignment in model's safety protocols” → “in the model’s safety protocols.”
- Page 4, bullets under future directions: “scuh as brightness” → “such as brightness.”
- Page 6, “moultimodal” → “multimodal.”
- Page 8, Conclusion: “of of MLLM” → “of MLLM.”
- References: Multiple capitalization and formatting inconsistencies (e.g., venue names, arXiv formatting). Please standardize to ACL Anthology style.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5: Between Acceptable and Strong — Solid survey curation and organization, but limited synthesis, missing comparative positioning vs. closely related surveys, and lack of tabulated coverage reduce the strength.

## Excitement
3.0: Interesting — The LLM-to-MLLM comparative framing and concrete MLLM directions are useful, but the lack of deeper synthesis and evaluation guidance tempers enthusiasm.

## Overall Assessment
3.5: Borderline Conference — Solid and timely survey with a helpful multimodal focus and a clear visual roadmap, but currently underpowered in comparative positioning and systematic synthesis. With stronger differentiation from existing surveys, concrete synthesis tables, and firmer multimodal evaluation guidance, it could be a clear conference accept.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations and Ethics Statement sections are present and appropriate for a survey. The paper could further discuss risks of dual use when curating jailbreak examples and benchmarks for MLLMs, especially around culturally specific harm definitions and regional legal norms. Suggest adding a subsection that:
- Distinguishes evaluation-only vs. training-time exposure to harmful multimodal content.
- Discusses governance for dataset updates as norms shift (noted in Section 3.3), including procedures to retire or annotate outdated or culturally sensitive content.
- Addresses accessibility concerns for low-resource languages and scripts in multimodal contexts where OCR and typography defenses may fail disproportionately.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — As a survey, it is mostly about literature curation. Adding synthesis tables and a public bib taxonomy would push this closer to 5.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.