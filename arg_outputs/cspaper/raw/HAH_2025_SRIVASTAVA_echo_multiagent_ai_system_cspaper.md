# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper presents Echo, a multi‑agent LLM pipeline for pharmacovigilance that mines Reddit posts to surface potential drug–symptom associations. Four agents are used: Explorer extracts drug/ADR mentions; Analyzer assigns three scores (temporal proximity, patient confidence, community engagement) and highlights confounders; Verifier compares associations to FDA/FAERS signals to flag potentially novel ones; Proposer synthesizes plausible mechanistic hypotheses from the biomedical literature. Using 187 Reddit posts, the system reports 640 associations, several with zero FAERS counts, and provides qualitative case studies that suggest Echo could have surfaced immune‑checkpoint‑inhibitor pneumonitis prior to widespread regulatory emphasis. A lightweight web interface is also provided.

## Summary Of Strengths
- Ambitious, end‑to‑end framing. Treating social media narratives as hypothesis‑generating pharmacovigilance signals is timely and relevant to NLP applications in health. The multi‑agent decomposition is sensible and maps cleanly to subtasks.
- Clear problem motivation. The gap between spontaneous reporting systems and patient‑reported experiences is well articulated and clinically meaningful.
- Usability component. The interface in Figure 2 gives a practical entry point for exploring extracted associations, links to Analyzer and Proposer reports, and supports ranking by a novelty proxy, which can benefit practitioners and researchers.
- Case studies are concrete. The retrospective pneumonitis example anchors the vision and illustrates the intended value of early patient‑voice signals.
- Figures communicate the intended workflow. Figure 1 effectively shows the Explorer–Analyzer–Verifier–Proposer pipeline with an imatinib–parosmia storyline, making the system architecture and information flow easy to grasp at a glance.

## Summary Of Weaknesses
1) Evaluation design and metrics are insufficient for ACL standards.
- Table 1 reports only recall on a restricted set of 20 drugs and omits precision and F1. Without precision, the practical value of 640 extracted associations cannot be assessed. High false‑positive rates would invalidate downstream novelty flags and hypothesis generation.
- The recall computation is unconventional: matching to the “top‑5 highest frequency adverse effects per drug in FAERS” is a coarse and biased ground truth. This penalizes quality‑of‑life ADRs that are less represented in FAERS and privileges severe outcomes like “death,” confounding the interpretation of the reported 0.08–0.27 recall.
- No human‑labeled evaluation set is provided. There is no inter‑annotator agreement, error taxonomy, or qualitative error analysis of extraction failures.

2) Terminology normalization and mapping to controlled vocabularies are not described.
- The paper does not specify normalization of Reddit colloquialisms to MedDRA or SNOMED terms. Consequently, both Table 1’s evaluation and Table 2’s “novel” associations may be artifacts of vocabulary mismatch (e.g., “daytime sleepiness” vs. “somnolence,” “bloating” vs. “abdominal distension”). This undermines the Verifier’s zero‑count findings.
- Equation‑level clarity is missing: the Verifier score is defined as ln(FAERS_count + 1), but mapping rules that connect Reddit expressions to FAERS PTs are unspecified, so the score is not interpretable across pairs.

3) The Analyzer’s scoring is underspecified and partly circular.
- Temporal, confidence, and community scores are described qualitatively on Page 2, but specific extraction rules, prompts, thresholds, or calibration procedures are not given. There is no validation that these scores correlate with ground‑truth temporality or reporter certainty.
- Community support uses upvotes and replies, but the paper does not report how these raw counts were normalized across subreddits or time, nor does it show that “engagement” correlates with signal quality. Confounding popularity with validity is a risk not addressed empirically.

4) Confounder discovery lacks methodological grounding or validation.
- Table 3 lists confounders (e.g., “male,” “recent surgery,” “multiple myeloma”), yet the paper does not detail how the Analyzer extracts, aggregates, and ranks confounders from text, nor how it distinguishes confounders from mediators or colliders. No manual audit is presented to evaluate correctness. Without causal framing or validation, these outputs risk misleading interpretations.

5) Novelty claims are overstated relative to evidence provided.
- Table 2 flags five associations with zero FAERS counts as “potentially novel,” but the pipeline does not include synonym expansion, multi‑level aggregation (e.g., HLT/HLGT in MedDRA), or check for label wording variants. Several listed ADRs plausibly exist under related PTs. Without a robust normalization layer and literature triangulation protocol, “novelty” is not substantiated.

6) Sample size and coverage are too limited for the strength of the conclusions.
- Only 187 Reddit posts are analyzed, yet 640 associations are reported. This ratio suggests extensive many‑to‑many extraction per post, raising concerns about over‑fragmentation or hallucinated pairings. The paper does not quantify evidence instances per association or provide per‑pair support distributions.
- No temporal hold‑out or prospective simulation beyond anecdotal case studies. The pre‑2017 restriction in Section 4 is informative but remains qualitative and selective rather than a systematic early‑warning backtest.

7) Proposer agent risks unsupported claims.
- Table 4 contains rich mechanistic narratives with citations, but there is no verification step to check citation correctness, recency, or direct relevance. In the absence of human curation or automated reference validation, there is material risk of plausible‑sounding but imprecise or off‑target mechanistic stories.

8) Missing comparisons and baselines from closely related lines of work.
- The paper cites foundational social‑media pharmacovigilance work but omits several recent, directly comparable systems that mine web forums or Reddit and connect to FAERS, knowledge graphs, and GUIs. This weakens positioning and denies readers an empirical and design‑level context.

9) Reproducibility gaps remain despite a code URL.
- Prompts for each agent, post‑processing rules, entity dictionaries, normalization resources, and Reddit sampling procedures are not specified in enough operational detail to ensure replication. Compute budgets and inference settings are not reported per agent. Given closed models, these details are necessary.

10) Figure and table‑specific concerns.
- Figure 1: The pipeline diagram communicates flow well, but it elides crucial normalization, de‑duplication, and aggregation steps between Explorer and Verifier. The right‑hand claim “Parosmia still not formally associated with imatinib (2022)” is presented without systematic evidence or cross‑terminology search, which weakens the case study’s generality.
- Figure 2: The UI mockups are helpful, but the Analyzer Report panel does not indicate term mappings, evidence counts per association, or confidence intervals for scores. Without provenance links to specific Reddit posts and their time stamps, auditability is limited.
- Table 1: Reporting only “Total Drugs,” “Total Associations,” and “Recall” on a restricted set is insufficient for an IE task. A precision/recall/F1 breakdown, error categories, and per‑drug variability are needed.
- Table 2: The five “top” novel associations are ranked by high Analyzer scores, but those scores are themselves unvalidated. Zero FAERS counts, when produced without synonym/ontology alignment, are not strong novelty evidence.
- Table 3: The notion of “saliency” for confounders is defined as the number of unique symptoms they touch. This ignores prevalence, effect size, and causal plausibility; a frequency‑only criterion risks over‑calling generic descriptors.
- Table 4: The Proposer’s outputs read like well‑formed literature‑based narratives. Absent a verification step or expert adjudication, they should be framed as speculative; the paper occasionally implies higher confidence than warranted.

Why this matters: The central claim is that Echo can surface clinically valuable, potentially novel signals from patient narratives. Without careful normalization, robust extraction evaluation, causal framing for confounders, and a conservative novelty protocol, the system risks producing attractive but unreliable leads. For a health application, evaluation quality must be commensurate with the stakes.

## Potentially Missing Related Work
1) Karapetiantz et al., “Monitoring Adverse Drug Events in Web Forums: Evaluation of a Pipeline and Use Case Study,” 2024 — End‑to‑end pipeline for mining patient posts from health forums with normalization and signal detection; directly comparable to Echo’s Explorer/Analyzer/Verifier and GUI. Should be discussed in Related Work and compared in Section 3, with extraction and validation baselines added alongside Table 1.

2) Dong et al., “Pharmacovigilance in the digital age: gaining insight from social media data,” 2025 — A comprehensive review of social‑media‑based pharmacovigilance across platforms and methods. Should anchor the positioning in Section 6 and inform the evaluation design and risk discussion.

3) Roche et al., “A holistic AI‑based approach for pharmacovigilance optimization from patients behavior on social media,” 2023 — Presents an AI framework using temporal social‑media behavior for safety signal optimization. Compare architectures in Section 2 and discuss design trade‑offs relative to Echo’s multi‑agent approach.

4) Dreyfus et al., “Application of NLP techniques to identify off‑label drug usage from various online health communities,” 2021 — A multi‑stage NLP pipeline over online health communities; relevant as a baseline for extraction and reasoning over unstructured patient narratives. Should be cited in Section 3.1 and methods contrasted.

5) Allen et al., “Pharmacovigilance in the Age of Legalized Cannabis: Using Social Media to Monitor Drug‑Drug Interactions Between Immunosuppressants and Cannabis‑Derived Products,” 2025 — Illustrates linking social‑media‑derived signals to regulatory data for validation. Add to Section 3.2 and the Verifier discussion.

6) Yu et al., “Knowledge‑augmented Agentic AI for Mental Health Medication Information Seeking,” 2026 — A multi‑agent, knowledge‑graph‑grounded system integrating Reddit, WebMD, and FDA records with provenance. Should be discussed in Section 2 and Section 6 as a closely related agentic architecture.

7) Hu et al., “Crowdsourcing‑Based Knowledge Graph Construction for Drug Side Effects Using LLMs with an Application on Semaglutide,” 2025 — Extracts Reddit‑based side effects and validates against FAERS, directly aligned with Echo’s goal. Should be compared empirically in Section 3.1 and as a validation strategy in Section 3.2.

## Comments Suggestions And Typos
Actionable recommendations:
- Build a labeled evaluation set. Provide a manual annotation study over a representative Reddit sample with entity normalization to MedDRA PTs, including inter‑annotator agreement. Report precision/recall/F1 for the Explorer and end‑to‑end association extraction. Include qualitative error analysis.
- Strengthen normalization and mapping. Add a terminology normalization layer that maps Reddit expressions to MedDRA terms; document rules for synonym expansion, phrase clustering, and deduplication. Recompute Verifier scores after normalization and report sensitivity to mapping choices.
- Redesign the “novelty” protocol. Move beyond ln(FAERS+1). Aggregate at multiple MedDRA levels, check label variants, and triangulate with literature and drug‑class analogs. Report a blinded clinical adjudication for the top K purportedly novel pairs.
- Validate Analyzer scores. Provide prompt templates, extraction heuristics, and calibration. Correlate temporal and confidence scores with human judgments. Show robustness across subreddits and time periods. For community support, analyze whether engagement predicts correctness or is confounded by topic popularity.
- Confounder methodology. Specify extraction rules, distinguish confounders from mediators and colliders, and provide a small‑scale human audit. Consider simple causal diagrams and compare against text‑based causal discovery baselines.
- Proposer verification. Add a citation‑verification pass to guard against hallucinated or off‑target references. Include an expert review for a subset of hypotheses and report agreement and revision rates.
- Expand evaluation. Go beyond 187 posts. Include additional health forums with clearer permissions, or at least demonstrate robustness across Reddit communities. Provide per‑pair evidence counts and distributions.
- Baseline comparisons. Include pipelines from the missing related work for extraction and validation; alternatively, implement strong open baselines for NER/RE plus MedDRA normalization.
- Interface provenance. In Figure 2, add clickable provenance to original posts, timestamps, and normalization mappings; expose evidence counts and confidence intervals for scores.

Typos and minor issues:
- Page 2: “tasking Gleevec” likely “taking Gleevec.”
- Page 3, footnote 1: minor grammar issues; consider clarifying SerpAPI limits and search queries.
- Section 3.2: “primary goal is to identify novel associations” is stated; consider toning down to “hypothesis‑generating associations” given current validation.
- Ensure consistent capitalization of adverse events and drug names; a few instances appear inconsistent.
- Check references for consistent formatting of FDA labels and access dates.

Criteria that could raise my score:
- A thorough, normalized, human‑labeled evaluation with precision/recall/F1, clear prompts and rules, and ablations showing each agent’s contribution.
- A conservative, multi‑source novelty determination with expert adjudication and demonstrated precision of top‑ranked findings.
- Detailed confounder extraction methodology with validation, plus improved ethical and data‑use documentation.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully; unlikely I missed something that should affect ratings.

## Soundness
2.5: Between Poor and Acceptable — Main claims are promising, but extraction/normalization evaluation, novelty verification, and confounder methodology are under‑specified and weakly validated.

## Excitement
2.5: Between potentially interesting and interesting — The vision is appealing, but current empirical rigor is not yet at main‑track standard.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The problem and system framing are compelling, and the interface and case studies add practical value. However, the extraction evaluation lacks precision/recall, normalization to MedDRA is not described, novelty is inferred from a simplistic FAERS count without ontology‑aware mapping, and confounder/hypothesis components are unvalidated. With a stronger, normalized evaluation and conservative novelty protocol, this could rise to a solid Findings or even conference submission.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper’s Ethics and Limitations section acknowledges reporting bias, platform restrictions, and privacy concerns, which is appreciated. Additional points to address:
- Risk of surfacing sensitive or identifiable medical narratives; the UI should enforce strict provenance controls and aggregation to reduce re‑identification risk.
- Potential harm from premature or misinterpreted “novel” ADRs; recommend a gated release of candidate signals and mandatory expert adjudication before dissemination.
- Platform compliance: clarify adherence to Reddit’s ToS and data‑use policies, including rate limits, caching rules, and downstream sharing.
- Demographic bias: Reddit populations may not represent broader patient groups; discuss stratified analyses and how to avoid overgeneralization.

## Ethical concerns
None beyond those noted above, provided data use complies with platform policies and no attempt is made to clinically act on unverified signals. Strengthen provenance protection and expert review before surfacing “novel” claims.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — Code link is helpful, but missing prompt details, normalization resources, sampling procedures, and evaluation sets make exact reproduction and fair comparison difficult.

## Datasets
2: Documentary — If the curated Reddit subset and normalized association list are released with clear licensing, they will help replicate the study but may have limited broader reuse due to size and policy constraints.

## Software
3: Potentially useful — The multi‑agent pipeline and UI could be useful, contingent on released prompts, mappings, and documentation for end‑to‑end runs.