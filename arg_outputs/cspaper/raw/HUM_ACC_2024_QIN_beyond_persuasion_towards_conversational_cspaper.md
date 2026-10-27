# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper studies credibility in persuasive explanations for conversational recommender systems (CRSs). It proposes PC-CRS, a two-stage, training-free approach that (i) selects from a set of credibility-aware persuasive strategies to generate an explanation candidate, and (ii) iteratively critiques and refines the candidate to remove misinformation using a self-reflective loop. Experiments with a simulator-based evaluation on Redial and OpendialKG show gains in both persuasiveness and credibility, and analyses suggest that many LLM-based CRSs tend to “cater” to user utterances rather than adhere to factual item information. Additional results indicate credible explanations may also improve recommendation accuracy.

## Summary Of Strengths
- Clear problem framing and motivation: The paper identifies a concrete, underexplored failure mode in LLM-based CRSs, namely persuasive but unfaithful explanations that erode trust.
- Simple and practical method: The two-stage pipeline makes intuitive sense, is training-free, and relies on prompts that are easy to adopt. Figure 2 helps readers understand the flow from strategy selection to self-refinement.
- Empirical gains on two datasets: Table 1 shows consistent improvements over strong LLM baselines in both Persuasiveness and Credibility, plus large boosts in “Convincing Acceptance.” Table 2 shows PC-CRS also improves recall and success rate, which is nontrivial given identical retrieval backbones across LLM-based methods.
- Insightful analysis: The “why LLMs lie” analysis is thought-provoking. Figure 3 quantifies a relevance gap, showing that low-credibility explanations align more with user utterances and less with item facts. Table 3 complements this by showing PC-CRS raises alignment to both sources.
- Useful observations about trade-offs: Figure 4 shows a clean trend where iterative refinement increases credibility but can dampen persuasiveness, highlighting a real design tension that future work should address.
- Ablations are aligned with claims: Figure 5 indicates both Strategy-guided Explanation Generation (SEG) and Iterative Explanation Refinement (IER) contribute meaningfully, which supports the design choice.

## Summary Of Weaknesses
1) Heavy reliance on LLM-as-a-judge without sufficient grounding or variance analysis.
- The primary metrics, including Credibility and Persuasiveness, rely on GPT-4-based evaluation. While Section 4.4 mentions human validation, the main text does not provide confidence intervals, inter-run variance, or significance testing for the automatic evaluation. Without such analysis, improvements in Table 1 and Table 2 could be sensitive to prompt or sampling variance. Also, the evaluator itself can hallucinate or misinterpret subtle factual claims, which can bias the Credibility score.

2) Ambiguity in how “ground truth” item information is constructed and verified.
- Section 3.1.2 and 3.2 assume access to reliable item information I, but the main paper does not specify the source(s), coverage, and curation quality for Redial and OpendialKG. If the retrieved I is incomplete or noisy, the critic and the GPT-4 evaluator may penalize factually correct but out-of-knowledge claims. This is central because the method’s value depends on the factual substrate. Please detail provenance, filtering, coverage rates, and failure handling in the main paper.

3) Persuasiveness metric definition may bias scores upward.
- Equation (5) clamps the metric by only computing Persuasiveness when i_post ≤ i_true (Appendix E.1 hints at this restriction), which excludes cases where the explanation over-raises intention or where intention legitimately declines with more information. This censoring risks overstating persuasiveness and can bias comparisons in Table 1. A more symmetric formulation or reporting both clamped and unclamped variants with distributions would be fairer.

4) Lack of comparison to general-purpose faithfulness or hallucination-mitigation baselines.
- The method is conceptually similar to Self-Refine or RARR-style critique-and-rewrite. However, no direct comparison is provided against standard, strategy-agnostic verification or retrieval-augmented generation specifically tuned to reduce hallucination. This makes it hard to isolate the incremental value of the proposed credibility-aware persuasive strategies beyond generic self-critique loops.

5) Simulator-based evaluation risks overfitting to the evaluator/simulator pairing.
- The user simulator and the evaluator are both LLM-driven. Although a human study is included (Section 4.4), it is confined to a relatively small sample and one dataset. A stronger study would triangulate across multiple evaluators, report cross-evaluator agreement, and present results from at least a second simulator design or human-in-the-loop pilots.

6) Missing details that affect reproducibility and external validity.
- The paper says all LLM-based methods share the same dual-tower retriever, yet the main text omits training data, negative sampling, hyperparameters, and retrieval corpus size. This limits reproducibility and independent verification of Table 2. Similarly, costs and latency of SEG+IER compared to baselines are not reported, even though iterative refinement can be expensive.

7) Analysis choices could be confounded.
- Figure 3 uses BLEU-1, ROUGE-L, and BERTScore to measure alignment with “user historical utterances” versus “item information.” Overlap metrics can be affected by style and surface form. It would be stronger to verify alignment via factual slot checks or NLI-style entailment templates keyed to item attributes.

8) No per-strategy effectiveness analysis.
- The method hinges on “credibility-aware persuasive strategies,” but there is no ablation per strategy or per-turn effectiveness analysis. Which strategies contribute most to credibility versus persuasiveness? Figure 5 ablates the entire SEG stage but not the specific strategies.

9) Limited discussion of broader impacts and potential misuse.
- While the paper targets credibility, persuasion mechanics can still manipulate users even when “factually correct,” for example via framing or selective disclosure. The ethics section in the main text is limited, and risks like undue influence in sensitive domains are not discussed.

10) Statistical rigor and reporting.
- Tables 1–3 lack error bars, confidence intervals, or significance tests. With LLM evaluations and sampling noise, effect sizes need uncertainty quantification to support strong claims. The same holds for Figure 6 win rates.

Specific figure- and table-grounded comments:
- Figure 2: The pipeline is clear, but it would help to add how many critique-refine rounds were typical per example and to annotate which components call which model variants. A complexity or latency bar beneath the figure would strengthen the practicality claim.
- Figure 3: The “relevance gap” shows that low-credibility explanations are more aligned with user utterances and less with item info. This supports the paper’s central diagnosis, but the analysis could be made more robust by replacing overlap metrics with attribute-level factual entailment checks.
- Figure 4: Nicely shows the trade-off curve between credibility and persuasiveness across iterations. However, the axes mix different scales (left for persuasiveness, right for credibility); please report exact numeric deltas and CIs in the caption.
- Figure 5: The ablation shows that removing SEG or IER hurts both credibility and downstream accuracy. It would help to add Persuasiveness deltas after each removal and annotate whether the differences are statistically significant.
- Table 1: Strong improvements across datasets in Credibility and Convincing Acceptance. Please report standard deviations across multiple seeds/runs and clarify how Convincing Acceptance is computed exactly, including the “high credibility” threshold.
- Table 2: PC-CRS shows sizable Recall@1 and Success Rate gains, which is a compelling secondary benefit. However, since the retriever is the same, it is important to detail exactly how conversation histories are converted to retriever queries and whether they differ across methods.
- Table 3: Useful to corroborate the “relevance gap” narrative. Still, the same caveat about overlap metrics applies; consider factual slot accuracy per attribute.

## Potentially Missing Related Work
1) Feng et al., “A Large Language Model Enhanced Conversational Recommender System,” 2023 — An early LLM-enhanced CRS baseline that modularizes elicitation, recommendation, and explanation. It should be compared in Section 4 and discussed in Related Work to better position PC-CRS among LLM-forward architectures.

2) Yu et al., “Counterfactual Explainable Conversational Recommendation,” 2024 — Introduces counterfactual explanations for CRS. Discuss in Section 2 and contrast with PC-CRS’s credibility-focused strategies; a complementary baseline or analysis could be added around explanation faithfulness vs. counterfactual usefulness.

3) Lubos et al., “LLM-generated Explanations for Recommender Systems,” 2024 — Studies user perceptions of LLM-generated, post-hoc explanations. Add to Section 2 to connect with human-centered evaluation of explanation quality and perceived credibility.

4) Felfernig et al., “Less is More: Towards Sustainability-Aware Persuasive Explanations in Recommender Systems,” 2024 — Empirical study on Cialdini-style persuasive principles in explanations. Discuss in Section 2 to situate the proposed credibility-aware strategies within a broader persuasion literature.

5) Ricci et al., “Persuasive explanations for recommender systems: how explanations can influence users’ choices?” 2026 — Experimental study of how persuasive wording affects rational vs. irrational choices. Reference in Section 2 to motivate the need for credible persuasion and potential unintended effects.

6) Chen et al., “Tailoring explanations in conversational recommendations: The impact of decision contexts and user interfaces,” 2025 — Offers design and evaluation insights for conversational explanations across contexts. Discuss in Section 2 and consider in Section 4.3 when analyzing trade-offs in persuasiveness vs. credibility.

7) Jannach et al., “Evaluating conversational recommender systems,” 2022 — Survey/framework on CRS evaluation. Cite in Section 4 to motivate a broader, multi-faceted evaluation that includes human trust, calibration, and long-term outcomes.

8) Daolio et al., “DaLimeLlama: A Persuasive XAI Framework For Learning-to-Rank Product Recommenders,” 2024 — An LLM-based persuasive explanation framework from model signals. Compare in Section 3.1 or 4 as an alternative mechanism for generating persuasive yet faithful narratives.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Evaluation rigor
  - Report confidence intervals, multiple seeds, and significance tests for Tables 1–3 and the main figures. Show inter-run variance for GPT-4 evaluations.
  - Provide complete details on item information I: sources, coverage, curation, and how conflicts are handled. Include examples where I is incomplete and how the critic/evaluator behaves.
  - Clarify Convincing Acceptance: define the exact “high credibility” threshold and acceptance criteria, and analyze sensitivity to the threshold.
  - Revisit Equation (5): report scores both with and without the i_post ≤ i_true restriction; include distributions or calibration curves to ensure the metric is not biased.
- Baselines and ablations
  - Add comparisons to generic hallucination-mitigation/fact-checking approaches (e.g., Self-Refine variants without strategies, RARR-like verification, retrieval-grounded verification prompts) to isolate the benefit of “credibility-aware persuasive strategies.”
  - Provide per-strategy ablations: frequency of selection, impact on credibility/persuasiveness, and interactions over turns. Even a retrospective tagging of produced explanations by strategy would be helpful.
- Robustness and cost
  - Quantify API call counts, latency, and cost per dialogue for SEG+IER compared to baselines. Add results with more than 2 refinement iterations to show convergence or diminishing returns.
  - Evaluate with an alternative simulator/evaluator or a second human study on OpendialKG to reduce coupling to a single LLM judge and dataset.
- Analysis improvements
  - Replace or complement overlap metrics in Figure 3/Table 3 with attribute-level factual checks or NLI templates keyed to genres, cast, awards, and plots. This would strengthen the causal link between credibility and improved recommendation accuracy.
  - Add qualitative error analyses where I is incomplete or where the critic yields false positives.
- Ethics and societal impact
  - Expand the ethics/impact discussion to cover domains beyond movies, risks of manipulation even with “credible” content, and safeguards (e.g., disclosure that language is persuasive, links to verifiable sources, user controls).

Minor notes and typos:
- Table 4 caption says “Credible information in these examples are bold,” but the table entries in the paper body are not typographically bolded; please fix or rephrase.
- In Table 1, label the “Improvement (%)” more explicitly as the relative gain over the best baseline and verify the percentage math for each column.
- “CRS aims to engage…” should be “CRSs aim to engage…” for subject-verb agreement (Page 1).
- Figure 6 caption: “Tabel 1” → “Table 1.”
- Several places use informal phrasing (“lies?” on Page 6); consider neutral academic phrasing, e.g., “produces unfaithful content.”

Criteria to raise my score:
- Add the missing baselines for hallucination mitigation; show that strategies + self-refinement outperform strong verification-only pipelines.
- Strengthen evaluation rigor with CIs, significance, multiple seeds, and transparent details on I.
- Provide per-strategy analysis and costs; demonstrate robustness across evaluators or additional human studies.
- Address the Equation (5) bias and report both clamped and unclamped versions.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong

## Excitement
3.0 Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there’s time.

## Overall Assessment
3.5 Borderline Conference: The paper is close to being acceptable for the main conference but has notable weaknesses.
Justification: The problem is well-motivated, the method is practical, and gains in Tables 1–2 are meaningful. Figures 2–5 and Table 3 support the main narrative. However, dependence on LLM-as-a-judge, incomplete specification of factual sources, the biased persuasiveness metric, and missing comparisons to faithfulness-focused baselines prevent a clear acceptance. With the suggested fixes, this could be a strong Findings paper or a main-track accept.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper acknowledges limited backbone diversity and strategy personalization. It should also discuss broader societal risks: even factually correct persuasion can manipulate choices through framing and selective emphasis. In sensitive domains (health, finance), “credible persuasion” still requires oversight, disclosure, and user control.
- Consider failure modes where the factual source I is incomplete or wrong; describe safeguards, fallbacks, or confidence-qualified explanations. Provide transparency by citing sources in the output.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.
Notes: Prompts are included, and setup is sketched, but details about item information sources, retriever training, and variance statistics are insufficient.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.