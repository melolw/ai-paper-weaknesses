# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes STAR, a sociotechnical framework for human red teaming of language models that aims to improve both steerability and signal quality. Steerability is addressed via procedurally generated, parameterized instructions (rule, adversariality level, use case, topic, and targeted demographic group), designed to distribute human attacks more evenly across a specified risk space. Signal quality is addressed through demographic and expertise matching for annotation and a two-step annotator-to-arbitrator pipeline that elicits and leverages rater reasoning rather than collapsing disagreement to majority vote. Using 8,360 multi-turn dialogues collected from 227 red teamers and annotated by 308 annotators/arbitrators, the paper compares coverage patterns with prior red-teaming datasets (via UMAP and clustering), analyzes the impact of in-group vs out-group annotators, and shows that demographic intersections (race×gender) provide additional explanatory power in detecting failures at no extra cost.

## Summary Of Strengths
- Clear, well-scoped objectives with a methodologically coherent framework. The combination of parameterized instructions, demographic/expert matching, and an arbitration step is well articulated and addresses known pain points in human red teaming.
- Evidence of steerability: The UMAP-based comparison in Figure 2 and the cluster distribution in Table 1 demonstrate that STAR concentrates on the intended social-harm regions (e.g., cluster 2 and 16) while maintaining broad thematic coverage. Figure 3 further shows relatively even distribution of attack targets across demographic groups, including intersectional labels, which aligns with the stated coverage goal.
- Signal quality and annotator sensitivity: Figures 4 and 5, along with Table 2, provide quantitative evidence that in-group annotators are more likely to flag hate speech and, to a lesser extent, stereotype rule violations than out-group annotators, supporting the argument for demographic matching on harms targeted at specific groups. The qualitative excerpts (Section I) illustrate thoughtful, nuanced arbitrator deliberations that productively leverage disagreement.
- Useful resource framing and analysis scale: 8,360 dialogues with 16.4±11.3 turns on average indicate a nontrivial scale for a human red-teaming study. The structured pipeline and detailed instructions (Appendix C) are potentially replicable, at least conceptually, by other groups.
- Intersectional findings: The nested-model comparison (Section 6.2.3) showing added explanatory power from race×gender interactions, without added data collection cost, is a concrete and practically relevant benefit of the parameterized approach.

## Summary Of Weaknesses
1) Evidence for steerability is largely visual and descriptive. While Figure 2 and Table 1 indicate thematic focus and spread, claims of “comprehensive and even coverage” remain only partially substantiated. There is no formal coverage metric or diversity score (e.g., entropy across parameter buckets, quality-diversity metrics) that would quantify the extent to which STAR reduces redundancy relative to baselines. Figure 3 shows distribution across targets, but this is mostly driven by instruction assignment and recruiting, not necessarily by exploration diversity within those strata.

2) Limited causal attribution for arbitration benefits. The paper argues that arbitration improves label reliability, but quantitative evidence isolating the arbitration step is limited. For example, a side-by-side comparison of outcomes under majority vote vs. arbitration-mediated outcomes, measuring calibration, stability, or downstream agreement, is absent. We see inter-rater alpha reported (Section 6.2.2), but it is moderate (α≈0.47–0.50) and not compared to a non-arbitrated condition that would allow attributing any net reliability gain to the proposed pipeline.

3) Statistical methodology is under-specified in places. Section 5.2 references odds ratios, ANOVA, and t-tests, but details are sparse: model formulas, covariates, multiple-comparison handling, and exact sample sizes per subgroup are not provided. The nested-model test for interaction effects (Section 6.2.3) is promising, but the modeling family, link function, and control variables are not explicitly stated. Without this, interpretability and reproducibility of the inferential claims are constrained.

4) Proprietary dependencies and limited reproducibility. The attack target rules are tied to a proprietary policy, and the evaluated model is proprietary. The UMAP embedding uses a proprietary embedding model (Gecko). Together, these choices constrain exact replication and external validation. While the general pipeline is replicable, reproducing the exact quantitative results, especially Figures 2–5 and Tables 1–2, 8–9, would be difficult without mirrored assets.

5) Evaluation scope vs. real-world external validity. Section 9 candidly acknowledges English-only testing and a limited interaction modality. The Real-world flagged dialogue set in Figure 2 does not substantially overlap with any red-teaming approach, including STAR, suggesting a residual gap between red-teaming coverage and in-the-wild failure modes. The paper advocates STAR as a path to reproducibility and comparability, yet the empirical link to real-world harms is not tightened beyond the UMAP juxtaposition.

6) Ambiguity in instruction interpretation persists. The qualitative analyses (Appendix I) reveal persistent gray areas, such as whether a fictional story “promotes” stereotypes or whether disclaimers mitigate violations. While arbitration surfaces these disagreements, Section 6.2.2 does not translate the insights into concrete policy clarifications or annotation guidelines that would reduce variance in future rounds.

7) Missing baselines on automated or hybrid red teaming. Given that the paper positions STAR against a broad landscape, it would be informative to compare coverage and sensitivity with automated-diversification methods (e.g., prompt generators or quality-diversity search beyond Rainbow Teaming) under controlled costs. As it stands, comparisons are to prior human datasets with very different instructions, models, and time frames, which weakens claims that STAR achieves comparable spread “at no increased cost.”

8) Cost and efficiency not rigorously reported. There is no rigorous accounting of annotation/attack cost per useful finding or per discovered failure mode. Claims of “no additional cost” for intersectional analysis (Section 6.2.3) are true in labeling space but do not address overall human time, arbitration overhead, and recruiting complexity. A table quantifying time-on-task per step and the arbitration trigger rate would strengthen the efficiency argument.

9) Some inconsistency in hypothesis focus. Section 6.2.1 emphasizes coverage and thematic targeting; Section 6.2.2 highlights demographic matching in annotation; Section 6.2.3 focuses on intersectional analysis of failures. Each is valuable, but the paper would benefit from a unifying set of primary hypotheses and pre-registered analyses. As written, the result sections can feel somewhat parallel rather than tightly integrated into one evaluation narrative.

10) Figure and table attributions could be tighter to claims. For example, Figure 2 and Table 1 support broad coverage and intended focus, but the text occasionally overgeneralizes to “comprehensive and even coverage” without formal quantification. Similarly, Table 2’s p-values are convincing for hate speech but not for stereotypes; the main text should clearly delineate claim boundaries to avoid overextension.

Specific figure/table references:
- Figure 2 and Table 1: support claim that STAR concentrates on targeted harms while maintaining spread; however, they do not quantify diversity or redundancy reduction, so they only partially substantiate “comprehensive and even coverage.”
- Figure 3: shows even distribution across demographic targets as assigned; it demonstrates instruction steerability but not exploration diversity within each demographic cell.
- Figure 4 and Figure 5: convincingly show in-group annotators are more sensitive, especially on hate speech. This strongly supports demographic matching for annotation.
- Table 2 (and Tables 8–9 in Appendix): provide the clearest quantitative support for the annotation-sensitivity claims, though the statistical modeling details would benefit from fuller disclosure.

## Potentially Missing Related Work
1) Lee et al., “Learning Diverse Attacks on Large Language Models for Robust Red-Teaming and Safety Tuning,” 2024 — presents a GFlowNet-based automated attacker for diverse jailbreak prompts. It is directly relevant to the paper’s steerability and coverage claims. Compare as an automated baseline in Section 5 and discuss after Section 2.1; optionally include as a complementary baseline to Figure 2/Table 1 style analyses.

2) Inie et al., “Summon a demon and bind it: A grounded theory of LLM red teaming,” 2025 — a qualitative grounded-theory study of practitioner strategies. It is germane to the sociotechnical framing and could deepen the rationale for parameterization and disagreement handling. Discuss in Section 2 (Background) and relate to STAR’s instruction design and arbitration in Sections 3.1–3.2.

3) Verma et al., “Operationalizing a Threat Model for Red-Teaming Large Language Models (LLMs),” 2025 — provides a structured threat model and taxonomy. Useful for situating STAR’s focus on social-harm content relative to broader system and security threats. Add to Section 2 and clarify scope in Section 9.

4) Purpura et al., “Building Safe GenAI Applications: An End-to-End Overview of Red Teaming for Large Language Models,” 2025 — an end-to-end practical survey. Incorporate in Section 2 and relate STAR’s multi-stage human pipeline to application-focused workflows.

5) Jabbar et al., “Red teaming large language models: A comprehensive review and critical analysis,” 2025 — a systematic review that would help position STAR’s contribution among attack types, datasets, and metrics. Cite in Section 2 and in the discussion around evaluation breadth vs. depth.

6) Gillespie et al., “AI Red-Teaming is a Sociotechnical System. Now What?,” 2024 — aligns closely with STAR’s sociotechnical argument; should be referenced in Section 3.2 to strengthen the theoretical grounding for valuing disagreement, annotator identity, and labor practices.

7) Jung et al., “STAR-Teaming: A Strategy-Response Multiplex Network Approach to Automated LLM Red Teaming,” 2026 — despite being automated and later work, it offers a complementary network-based coverage perspective. Adding a brief discussion in Section 2 and Section 8 would situate STAR with respect to structured automated approaches and potential hybridization.

8) Alvarado Garcia et al., “Red Teaming LLMs as Socio-Technical Practice: From Exploration and Data Creation to Evaluation,” 2026 — ethnographic/CHI perspective on red teaming as data practice. Mention in Section 2 and Section 8 to broaden the sociotechnical lens and motivate future participatory extensions.

9) Ema et al., “Red teaming for culturally grounded LLM evaluation: lessons learned from a Japanese team’s engagement with stereotype risks,” 2026 — highly relevant to extending beyond English/US norms. Discuss in Section 8 to motivate multilingual and locally grounded instruction parameterization.

Note: While some items are recent, they are directly pertinent and would strengthen positioning and claims about coverage, sociotechnical practice, and potential hybridization with automated approaches.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide formal diversity/coverage metrics. In addition to Figure 2 and Table 1, report quantitative measures such as entropy over instruction parameters, coverage ratios per cluster normalized by instruction intent, and redundancy measures (e.g., average pairwise distance in embedding space per parameter cell). This would substantiate the central steerability claim.
- Quantify arbitration’s net value. Add an ablation that compares label outcomes under (a) single annotator, (b) majority vote of two annotators, and (c) the annotator→arbitrator pipeline. Report changes in inter-rater reliability, calibration to gold (for a subset adjudicated by domain experts), and the distribution of final labels. This would ground the arbitration step beyond qualitative examples.
- Expand statistical details. Explicitly specify model families, link functions, fixed/random effects, data inclusion criteria, and multiple-testing handling for Table 2 and Section 6.2.3. Include N per cell in Figures 4–5. Report effect sizes with CIs in addition to p-values.
- Add efficiency accounting. Include a table of person-minutes per dialogue for attack, annotation, and arbitration, arbitration trigger rate, and any differences in throughput across parameter settings. This would validate “no additional cost” claims and guide practitioners on expected budgets.
- Clarify policy-interpretation ambiguities. Based on Appendix I analyses, propose concrete rule clarifications and next-iteration annotation guidelines for ambiguous cases (fictional narratives; disclaimers; attacker-forced violations). A short subsection in Section 6.2.2 or 7 would close the loop from observation to practice.

Typos and minor issues:
- Section 4, Annotation task checkboxes in Figure 7: the options appear mislabeled (“Quarterly/Monthly break the rule”); verify Likert labels for consistency with the 4-point scale elsewhere.
- Consistently spell “Krippendorff’s Alpha” (currently appears as “Krippendorf’s”).
- Section 6.2.3 contains a duplicated paragraph about the nested model; condense to one statement and ensure exact p-values are consistent.
- Figure captions: include brief notes on N per bar in Figures 4–5 and clarify whether error bars are 95% CIs of proportions or model-based CIs.

Criteria for raising my evaluation:
- Add the arbitration ablation and formal coverage metrics; and include fuller statistical specifications for the intersectional analysis. If these are addressed with clear positive results, I would likely move to 4.0 (Conference).

## Confidence
4: Quite sure after careful checking — I checked key figures (2–5), tables (1–2, 8–9), and methods; some proprietary constraints prevent full verification.

## Soundness
3.5: Between Acceptable and Strong — The framework and results are generally sound, but the steerability claim would benefit from formal coverage metrics, and arbitration impact is not quantitatively isolated.

## Excitement
3.5: Between interesting and exciting — The sociotechnical design and intersectional analysis are timely and useful; stronger quantitative validation would increase excitement.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses.
Justification: This is a thoughtfully designed, well-argued sociotechnical framework with promising empirical evidence and clear practical value. However, several central claims, especially around coverage/steerability and arbitration benefits, are supported primarily by qualitative or indirect evidence. Strengthening the quantitative evaluation and reporting would make this a solid accept.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper candidly acknowledges several limitations (English-only evaluation, limited parameter count due to human cognitive load, divergence from real-world flagged cases). Additional points to discuss:
- Risks of over-relying on in-group annotator judgments without explicit safeguards for internal group heterogeneity or minority views within groups.
- Potential labor and well-being considerations in arbitrated pipelines, including additional cognitive load from reading disagreements.
- Demographic matching can improve sensitivity, but may inadvertently exclude cross-group harms that are salient to those outside the group (e.g., allies, targets of intergroup conflict). Consider a secondary “cross-check” pass by out-group annotators on a subset.
- Dual use: parameterized instructions that maximize coverage could be repurposed for malicious exploration. Mitigation strategies and access controls for red-team protocols merit brief treatment.

## Ethical concerns
None beyond what the paper already anticipates; ethics approval, compensation standards, and well-being measures are described. A short note on safeguarding arbitrators from repeated exposure to contentious content during disagreement resolution would be helpful.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The pipeline is described in fair detail, but replication of specific quantitative results is hard due to proprietary models, policies, and embeddings; fuller statistical specs would help.

## Datasets
3: Potentially useful — If released in any form, the structured dialogues and annotations could be useful; current proprietary constraints limit broad utility.

## Software
3: Potentially useful — Even partial release of instruction generators and the annotation/arbitration toolchain would aid adoption; current description suggests feasibility but availability is unclear.