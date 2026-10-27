# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes REL-A.I., an interaction-centered methodology to measure when humans choose to rely on LMs’ utterances that convey degrees of (un)certainty (epistemic markers). The approach has three parts: a self-incentivized trivia game where participants decide whether to rely on an agent’s answer given only its uncertainty preface, a library of epistemic markers elicited from deployed LMs, and post-task perception questions about warmth, competence, and humanlikeness. Using this setup, the authors run three studies that systematically vary: (1) prior interactions via distributions of confidence markers (RQ1), (2) anthropomorphic “warmth” cues such as greetings and names (RQ2), and (3) domain of questions (RQ3). Results show that reliance rates for identical markers vary with interactional context, with differences up to about 20% depending on prior marker distributions, perceived warmth, and subject domain.

## Summary Of Strengths
- Timely, well-motivated problem: The paper shifts attention from internal/numeric calibration towards human behavior during real interactions. This is increasingly important as LMs are deployed in interactive settings.
- Clear, concise framework: Figure 2 lays out the three components of REL-A.I. in a way that makes the evaluation pipeline easy to understand, and Table 1 concisely enumerates experimental conditions and marker distributions.
- Empirical insights with practical relevance:
  - RQ1: Table 2 and Figure 3 show that medium-certainty markers (e.g., “I’m pretty sure…”) are relied upon less when they come from an otherwise “confident” agent than from one that is usually less confident. The dotted line in Figure 3 helps visualize the systematic upward shift in reliance for the “unconfident” system, and the negative correlation underscores that low-reliance templates are most sensitive to context.
  - RQ2: Table 3 and Table 4 indicate that a simple greeting (“I’m happy to help!”) significantly boosts perceived warmth and is accompanied by increased reliance, with the “happy” subset S2C_happy the most relied upon. Figure 4 compellingly shows the monotonic relationship between perceived warmth (x-axis) and overall reliance (y-axis).
  - RQ3: Table 5 shows higher reliance on markers in computational domains (math, abstract algebra) versus non-computational ones (philosophy, religion, law), suggesting domain-level priors shape human reliance.
- Integration with literature: The work is placed against calibration in ML and linguistic calibration and links to HCI findings on overreliance, explanations, and anthropomorphism.
- Safety implications: The finding that small warmth cues can inflate reliance (even without added evidence) is an actionable insight for designers of agents and safety evaluators.

## Summary Of Weaknesses
1) Underspecified ground-truth and scoring logistics for the self-incentivized task (Section 3.2).
- The task description states that points depend on whether the agent’s answer is correct, but participants do not see the answer and payment is unaffected. The paper does not specify how correctness is determined for each trial, how accuracy is balanced across systems, or whether accuracy varies by domain or expression class. If correctness is not controlled and balanced, the stated “score” may be incidental, weakening the “self-incentivized” rationale and leaving open the possibility that observed reliance rates partly reflect participants’ assumptions about base accuracies rather than a controlled accuracy environment. Clarifying per-condition accuracy and whether reliance is analyzed independent of correctness is essential for interpreting Tables 2–5.

2) Statistical analysis choices and reporting lack detail (Sections 4–6).
- The design appears within-subject (the same participants interact with multiple systems), but Table 2 reports a “two-sample t-test” with bootstrap resampling; a paired test would be more appropriate when relying on within-subject differences. Similarly, in Tables 3–5 many comparisons are reported as significant with asterisks, but the paper does not describe multiple-comparison corrections, effect sizes, or confidence intervals beyond Figure 3’s correlation. Given the number of markers and conditions, without correction and effect sizes it is hard to assess robustness.
- Figure 4 reports Pearson’s ρ = 0.97 between perceived warmth and reliance, but it is unclear at what aggregation level this correlation is computed (per participant, per system, per marker), how many independent points comprise the regression, and whether the same participants contribute multiple dependent points. This raises concerns about inflated correlation due to aggregation or non-independence.

3) Warmth manipulation may conflate multiple cues (Section 5).
- The manipulation combines a name change (Agent37821 → Gordon → Marvin) and a greeting (“I’m happy to help!”). Table 3 suggests names alone do little, while the greeting drives the warmth effect. However, the greeting also adds discourse structure and positivity, not just “warmth” in isolation; it may act as a politeness or engagement prime that changes perceived helpfulness or competence. A cleaner manipulation (e.g., orthogonally varying greeting frequency and content-neutral fillers or counter-greetings) would better isolate warmth. Moreover, Table 4 shows a non-monotonic pattern for weakeners (S2B > S2C > S2A), suggesting heterogeneity that deserves analysis by individual templates rather than collapsing all weakeners.

4) Domain effects risk confounds (Section 6).
- Table 5 shows domain-driven reliance differences, but the paper does not state whether question difficulty was equated across domains after converting MMLU items to free response, nor whether participants’ own prior knowledge or perceived base-accuracy of LMs by domain was controlled or measured. Since the design explicitly withholds the actual answer, the observed differences may reflect participants’ beliefs about where “machines excel” rather than an effect of domain per se. That may be the intended construct, but then claims should more clearly state that measured reliance differences capture domain priors rather than properties of model outputs. A short manipulation check (e.g., eliciting perceived LM competence by domain) would align better with the interpretations in Table 5.

5) Reproducibility and procedural specifics are thin (Sections 3–6).
- The paper does not provide enough operational detail to enable replication: how templates were mapped to questions; randomization constraints; per-condition counts at the template level; whether order was fully counterbalanced or merely randomized; the precise text shown beyond the epistemic marker (Figure 7 shows “It’s not entirely clear, maybe it’s…” but not the rest of the “beginning of an answer”); and accuracy assignment if scoring truly depends on correctness. Code/materials availability is not stated. Without these, recreating Tables 2–5 is difficult.

Minor but worth addressing:
- Power and sensitivity analysis are not reported. With N=50 per setting and many conditions/templates, some comparisons could be underpowered.
- The rationale for choosing geography for RQ1/RQ2 is reasonable, but discussing whether any observed effects replicate across multiple non-overlapping trivia domains would strengthen the generality claims.
- It would be useful to include CIs alongside means in Tables 2–5.

Figure- and table-specific comments:
- Figure 2 is effective in communicating the framework and helps anchor the rest of the paper. It supports the claim that REL-A.I. is a modular, system-level approach.
- Figure 3 adds a substantive point: the biggest deltas occur for the least-relied-upon markers in the confident system. This is a strong illustration of context-sensitivity beyond average rates.
- Figure 4 visually supports the claim that warmth correlates with reliance, but, as noted, the unit of analysis and independence of points should be clarified.
- Table 1 is helpful to understand the marker distributions across systems, but it would benefit from adding per-system item counts per template to assess statistical stability.
- Tables 2–5 are central to the paper’s claims. However, effect sizes and CIs, and clear statements about corrections for multiple testing, are needed to interpret the asterisks.

## Potentially Missing Related Work
1) Steyvers et al., “What Large Language Models Know and What People Think They Know,” 2025 — analyzes gaps between model confidence, human confidence, and correctness, proposing calibration metrics for human–LLM trust. Highly relevant to positioning the interaction-level reliance findings, especially in Sections 2 and 7; should be discussed and contrasted with REL-A.I. after the calibration discussion.
2) Xu et al., “Confronting verbalized uncertainty: Understanding how LLM’s verbalized uncertainty influences users in AI-assisted decision-making,” 2025 — controlled study of verbalized uncertainty levels and their effects on user trust and performance. Directly related to RQ1/RQ2; should be cited in Background and compared in Section 5.
3) Liu et al., “Revisiting Epistemic Markers in Confidence Estimation: Can Markers Accurately Reflect Large Language Models' Uncertainty?” 2025 — probes whether linguistic markers map to model uncertainty. Relevant to the epistemic-marker foundation of REL-A.I.; add to Section 3.2 and the discussion in Section 7.
4) Krishnan et al., “Enhancing Trust in Large Language Models with Uncertainty-Aware Fine-Tuning,” 2024 — proposes uncertainty-aware training that affects user-facing reliability. Useful in Section 2 and concluding discussion on deploying calibrated interactions.
5) Sui et al., “Diagnostic Uncertainty: Teaching Language Models to Describe Open-Ended Uncertainty,” 2025 — explores richer uncertainty communication beyond scalar hedges; discuss in Sections 2 and 7 as an avenue to test via REL-A.I.
6) Tao et al., “Can Large Language Models Express Uncertainty Like Human?” 2025 — builds a dataset of hedging expressions with human-annotated confidence; relevant to Section 3.2 and could be used to refine marker selection.
7) Liu et al., “Behavioral Indicators of Overreliance During Interaction with Conversational Language Models,” 2026 — identifies interaction patterns indicating overreliance; discuss in Section 7 as complementary signals that REL-A.I. could incorporate.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Clarify and, if needed, rebalance correctness:
  - State explicitly how correctness was determined in each experiment and whether accuracy was matched across conditions. If the primary analysis only uses reliance rates irrespective of correctness, say so plainly and justify why the “self-incentivized” framing remains valid. If correctness varied, provide per-condition accuracy, and re-analyze reliance conditional on later-revealed correctness to rule out confounds.
- Tighten the statistical analysis:
  - Use within-subject (paired) tests where appropriate, report effect sizes and confidence intervals, and control for multiple comparisons. For Figure 4, specify the unit of analysis and check the correlation with a mixed-effects model that accounts for repeated measures and random intercepts for participants and templates.
- Disentangle warmth manipulations:
  - Run a follow-up manipulation check isolating greetings from names, and consider a neutral-content greeting vs. an affectively warm greeting to ensure the effect is truly warmth rather than general positivity or engagement. Analyze per-template effects within the weakaner/weak-strengthener classes to explain the S2B anomaly in Table 4.
- Domain priors:
  - Add a brief post-task survey item on perceived LM competence by domain, and relate it to reliance (partial correlations or mixed models). This would strengthen the interpretation of Table 5.
- Reproducibility:
  - Provide a complete protocol: per-template counts per condition, randomization/counterbalancing scheme, question lists, marker–question assignment logic, and the exact text shown to participants after the epistemic marker. Release code/materials if possible.

Typos/clarity:
- p.2: “Machine learning as focused largely” → “has focused largely.”
- p.5: “statements of moderate certainty are relied on significantly less in a confident model (49% compared to 54%)” but Table 2 shows 52.4 vs 57.4. Please reconcile the numbers and ensure consistent rounding.
- p.6: Uniformly denote S2C_happy as S2C_happy (not S2Chappy sometimes).
- Tables: Add confidence intervals and effect sizes next to means; specify whether asterisks denote p < .05 after correction.

Criteria for score increase:
- Provide the missing methodological/statistical details and corrections above, plus a small follow-up or reanalysis that (1) controls explicitly for correctness and (2) isolates warmth from general politeness. If those confirm the main conclusions and improve reproducibility, I would raise to “Conference.”

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong — Well-motivated with informative results, but statistical choices, lack of accuracy control reporting, and incomplete procedural details limit rigor.

## Excitement
3.5 Between interesting and exciting — The framework and safety implications are timely and practically useful, with several striking findings, especially the warmth–reliance coupling.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses.
Rationale: The paper offers a clear, impactful framework and produces several compelling, figure- and table-backed insights (Figures 2–4; Tables 1–5). However, underspecified correctness/accuracy control in the “self-incentivized” task, statistical analysis choices without multiple-comparison handling, and incomplete procedural details make it hard to fully assess robustness and reproduce the findings. With clarifications and modest reanalysis, this could be a strong accept; as written, it sits on the borderline.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a limitations section acknowledging single-turn interactions, English-only US participants, and modality constraints, which is good. One key missing point is the role of answer correctness and base performance in shaping reliance; this has societal implications because overreliance may be exacerbated if users infer high base accuracy from warmth cues or domain priors. The ethical discussion appropriately flags dual-use risks of persuasive wording; the paper could further suggest mitigations, e.g., discouraging warmth cues in high-stakes interfaces unless calibrated by outcome-level constraints, or adding interface nudges that counteract overreliance when warmth is present.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: With additional details, others could reproduce, but current write-up leaves gaps (accuracy control, randomization, per-template counts, exact stimuli).

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.