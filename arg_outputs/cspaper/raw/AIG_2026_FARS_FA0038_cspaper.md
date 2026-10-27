# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The work is squarely in RAG for QA, addressing permutation robustness and inference-time aggregation, which fits ACL topics such as Generation, Question Answering, Information Retrieval for NLP, and Analysis/Robustness of NLP models.

## Minimum Quality
Pass ✅. The paper contains Abstract, Introduction, Related Work, Method (with equations), Experiments and Results (with figures and tables), a Conclusion that includes limitations, and references. The claims are clearly stated, though empirical coverage is narrow.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. No hidden or manipulative prompts or instructions are present in the provided text.

# Expected Review Outcome:

## Paper Summary
The paper studies permutation sensitivity in RAG, attributing inconsistencies partly to position bias. It proposes Citation-Consistent Voting (CCV), a training-free aggregation method that runs the generator on K random permutations, asks for structured outputs with an answer, a cited document index, and a quote, filters for evidence-valid responses, maps citation indices to permutation-invariant document IDs, and selects the answer that shows the strongest agreement on document IDs. On NaturalQuestions with Contriever top-5 retrieval and Qwen3-8B, CCV slightly outperforms majority-vote self-consistency at K = 20 permutations, and the authors report that citation agreement correlates with correctness.

## Summary Of Strengths
- Conceptual clarity and simplicity: The idea to aggregate by cited document agreement rather than string-frequency is intuitive and easy to implement. Equations (1) and (2) formalize the voting rule crisply.
- Training-free and model-agnostic: The method requires only a prompt format that elicits citations and a deterministic aggregation pass, making it potentially useful across many RAG systems.
- Figure-grounding of the pipeline: Figure 1 gives a clear, stepwise depiction of the 3-stage pipeline, from permutation sampling to evidence filtering to docID-consistent aggregation. The visualization clarifies where validity checks happen and how grouping by answer precedes docID voting.
- Evidence that gains scale with K: Figure 2 and Table 2 show a monotonic increase of CCV’s advantage over majority vote as permutations increase, which is exactly the behavior one would hope to see if citation agreement is a stable signal.
- Diagnostic analysis: The reported Mann–Whitney test shows a statistically significant correlation between agreement scores and correctness, lending credence to the underlying hypothesis that consistent citations are informative.
- Practical ablation: Table 3 investigates relaxing the verbatim quote constraint, with concrete changes in coverage, average valid runs, and SubEM, which is helpful for practitioners who must decide how strictly to validate evidence.

## Summary Of Weaknesses
1) Narrow empirical scope limits generalizability  
- Only one dataset (NaturalQuestions) and one model (Qwen3-8B) are tested, with a single retriever (Contriever). This makes it hard to conclude that CCV is robust outside this setting. Testing at least one more open-domain QA dataset and a second generator would make the evidence more compelling.

2) Very small absolute gains and unclear practical significance  
- Table 1 reports +0.19 SubEM and +0.17 F1 at K = 20 compared to majority voting. Given the cost of 20 forward passes per query, the practical value of these small deltas is questionable. The paper acknowledges modest gains but does not analyze when CCV yields substantial improvements versus when it is neutral. Reporting confidence intervals or significance tests for Table 1 would help.

3) Mixed story with the prompting format confounds interpretation  
- Table 1 shows “Vanilla RAG (Standard)” achieving 48.98 SubEM, which is higher than any multi-permutation method that uses the JSON-citation prompt, even though F1 is lower. The paper attributes this to formatting differences but does not control for it in the main comparison. Since CCV requires the JSON citation format, the fairest comparison is among methods using that format, but the headline numbers conflate formats and may mislead readers about practical effectiveness.

4) Limited baselines and missing comparisons to closely related aggregation ideas  
- There is no comparison to simple yet strong alternatives such as: majority vote restricted to evidence-valid responses only; voting by answer frequency weighted by per-run retriever scores; or learned source-reliability weighting. Given CCV’s conceptual proximity to reliability-weighted aggregation, the absence of these baselines weakens the claim that document-ID agreement is the key signal.

5) Evidence filtering design needs sharper specification and robustness checks  
- Section 3.2 describes evidence validity by exact substring checks of the quote within the cited document and the answer within the quote, but Section 3.4 later relaxes this to only require a “valid document index,” which risks accepting runs where the citation is correct but the quote and answer grounding are not. Table 3 shows gains from relaxing, but there is no measurement of false-positive validity. A precision estimate for the validity filter would clarify trade-offs.

6) Lack of detail on prompting and parsing stability  
- The paper does not provide the exact prompt template or error-handling strategy when the model returns malformed JSON, multiple citations, or missing fields. Since CCV hinges on reliable structured outputs, the reproducibility and robustness of the parsing pipeline are important. How often are runs discarded due to malformed citations, and how sensitive are results to the prompt wording?

7) Unclear handling of ties and edge cases  
- Section 3.3 states ties are broken by raw answer frequency. However, there are no details on tie scenarios where different answers have the same docID-consistency and frequency, or when R(a) is empty after filtering. These choices can influence the small margins reported in Table 1 and Table 2.

8) No analysis of sensitivity to retrieval quality and k  
- All experiments use Contriever top-5. The effect of changing the retriever or top-k is not studied. Since CCV aggregates over citations, which depend on retrieval sets, showing the behavior at top-10 or with a stronger retriever would strengthen claims.

9) Diagnostics do not fully explain where CCV helps most  
- The instability analysis in Section 4.5 is a start, but we still do not see qualitative or quantitative breakdowns by question type, answer length, or presence of multiple supporting passages. Case studies contrasting CCV decisions against majority vote on failure examples would aid interpretability.

10) Figure 2 presentation is supportive but underspecified  
- Figure 2 shows monotonic gains, which is encouraging, but confidence bands or per-query variance would make the trend more statistically persuasive. Without uncertainty visualization, it is difficult to judge whether the gains at K = 10 and K = 15 are robust.

11) Statistical testing is limited and not applied to main outcomes  
- The Mann–Whitney p-value is used to validate the hypothesis about agreement scores, but there is no significance testing for the central performance comparisons in Table 1 or Table 2. Given the small margins, this is important.

12) Missing, closely related prior work  
- The Related Work section is brief and omits several directly related lines of study on positional bias, robustness, and reliability-weighted aggregation in RAG. This weakens positioning and leaves open whether CCV addresses recognized failure modes beyond the few cited sources.

Specific references to figures and tables  
- Figure 1: The three-stage diagram is helpful, but it implicitly assumes a one-to-one answer-to-document mapping per run. The method does not discuss multi-document support, which is common in NQ, and how to aggregate if the model cites multiple passages.  
- Table 1: The largest improvements happen at K = 20 with small margins. Without confidence intervals, it is uncertain whether this holds across random seeds or different retrieval samples.  
- Table 2: The monotonic improvement is a nice property, but Δ is essentially zero at K = 5 and small at K = 10 and K = 15, suggesting limited benefit unless one can afford many permutations.  
- Table 3: The ablation shows that removing the strict quote check increases coverage and boosts SubEM by +0.64 at K = 5, but the lack of a grounding precision measure leaves open how often the relaxed filter accepts spurious evidence.

## Potentially Missing Related Work
1) Cuconasu et al., “Do RAG Systems Really Suffer From Positional Bias?”, 2025 — Directly analyzes order sensitivity in RAG and quantifies positional effects. Should be discussed in Section 2.1 and used to contextualize the motivation for permutation-robust aggregation in Section 1.  
2) Iratni et al., “Dynamic Context Selection for Retrieval-Augmented Generation: Mitigating Distractors and Positional Bias”, 2025 — Proposes pre-selection strategies to counter position bias. Compare in Section 2.4 and mention as a complementary non-ensemble baseline in Section 4.  
3) Yao et al., “Who is in the Spotlight: The Hidden Bias Undermining Multimodal RAG”, 2025 — Introduces diagnostic tools for position sensitivity. Cite in Section 2.1 and adopt their sensitivity metrics to deepen Section 4.5 diagnostics.  
4) Hwang et al., “Retrieval-Augmented Generation with Estimation of Source Reliability”, 2025 — RA-RAG weights sources by reliability, akin to citation-weighted voting. Compare in Section 2.3 and add a reliability-weighted baseline in Section 4.2.  
5) Faisal et al., “Improving Consistency in Retrieval-Augmented Systems with Group Similarity Rewards”, 2025 — Trains for answer consistency across paraphrases. Discuss in Section 2.4 as a training-based alternative to CCV and note in Section 5 as a candidate for hybridization with CCV.  
6) Kim et al., “Towards Fair RAG: On the Impact of Fair Ranking in Retrieval-Augmented Generation”, 2024 — Studies ranking-sensitive behavior of RAG, relevant to permutation effects. Add to Section 2.2 and leverage their methodology to analyze ranking-quality versus generation-quality trade-offs in Section 4.5.  
7) Bagwe et al., “Your RAG is Unfair: Exposing Fairness Vulnerabilities in RAG via Backdoor Attacks”, 2025 — Shows retrieval-level vulnerabilities. Discuss in Section 5 as potential adversarial risks for CCV that relies on document IDs.  
8) Wang et al., “Adaptive Retrieval-Augmented Generation for Conversational Systems”, 2025 — Introduces gating strategies using confidence signals. Cite in Section 2.2 and discuss in Section 5 how CCV’s agreement scores could serve as a gating signal.  
9) Stankovic, “Cross-Document Topic-Aligned Chunking for RAG”, 2025 — Improves chunk structure which may impact CCV’s citation signal. Mention in Section 2.2 and discuss combined use in Section 5.  
10) Cao et al., “Out of Style: RAG’s Fragility to Linguistic Variation”, 2026 — Studies RAG robustness to perturbations. Add to Section 2.4 and consider extending Section 4 with style-robustness tests to evaluate whether CCV also improves stability under query paraphrases.

## Comments Suggestions And Typos
Actionable suggestions that could change my assessment:
- Add broader experiments and stronger baselines:  
  - Evaluate on at least one more QA dataset and one more generator.  
  - Include baselines such as majority vote restricted to evidence-valid runs, answer-frequency weighted by retrieval scores, and a learned reliability-weighted aggregator.  
  - Report statistical significance or confidence intervals for Tables 1–3.
- Provide implementation details to ensure reproducibility:  
  - Release the exact prompts and parsing instructions, handling of malformed JSON, multiple citations, and missing fields.  
  - Report the fraction of runs discarded per query due to invalid structure at each K and under each filtering setting.
- Expand diagnostic analysis:  
  - Break down gains by question type, answer length, number of supporting passages, and retrieval hit rate.  
  - Study sensitivity to top-k retrieval and alternative retrievers.  
  - Include qualitative case studies showing when CCV overturns majority vote and why, grounded in the cited passages.
- Clarify evidence filtering and edge cases:  
  - Quantify precision and recall of the evidence-validity filter for both “with quote” and “no quote” variants.  
  - Explain tie-breaking beyond the first tiebreaker and what happens if R(a) is empty.  
  - Discuss how CCV would extend to multi-document support if the generator produces multiple citations.
- Report efficiency and cost:  
  - Provide per-query latency and cost breakdowns for K = 5, 10, 15, 20, and discuss practical guidance on choosing K given the small deltas in Table 2.

Minor comments and typos:
- Section 3.3: clarify notation “docID(r) = πk(jk)”. State explicitly that πk maps positions in the permuted list to original document indices, and that the underlying document set is fixed across permutations.  
- Table 1: ensure consistent significant figures and provide standard deviations for all multi-permutation entries, not only K = 5.  
- Section 4.2, last paragraph: “We note that the standard Vanilla RAG prompt achieves higher SubEM but lower F1 … reflecting differences in output format rather than method quality.” Consider moving this to a dedicated analysis subsection that controls for format effects.  
- Figure 2: add error bars or shaded confidence regions.  
- Table captions: specify that SubEM is substring exact match and F1 is token-level, and confirm whether lowercasing or normalization is applied.

Criteria for raising my score:
- If the authors add at least one more dataset and model, include the suggested baselines, and provide significance tests or CIs demonstrating consistent improvements at practical K values, I would consider 3.5 (borderline conference).  
- If, in addition, they release prompts and code with robust handling and show non-trivial gains where majority voting fails, I would consider 4.0 (conference).

## Confidence
4: Quite sure after careful checking — I checked the method, equations, and experimental tables closely, but broader experiments would still help validate external generality.

## Soundness
2.5: Between Poor and Acceptable — The core method is sound and simple, but empirical support is limited to a single setup with small margins and missing stronger baselines and significance analysis.

## Excitement
2.5: Between potentially interesting and interesting — The idea is neat and practical, but the demonstrated gains are small and the study is narrow.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The approach is easy to adopt and well explained, and the pipeline in Figure 1 plus Equations (1)–(2) is clear. However, the evidence is thin: small absolute gains, only one dataset and model, limited baselines, and no significance testing on the main results. With broader evaluation, stronger baselines, and a clearer accounting of evidence filtering trade-offs, this could rise to Findings or even borderline conference.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper briefly acknowledges several limitations in Section 5: modest gains, single dataset-model evaluation, and computational cost from multiple forward passes. Additional impacts to discuss:  
- Reliance on citations and document IDs means that retrieval-level poisoning or biased sources could systematically sway aggregation, potentially entrenching unreliable or biased documents.  
- Because CCV rewards agreement on a single cited document, it may underweight multi-hop or multi-source answers, possibly reducing coverage for complex queries.  
- The approach inherits any biases present in retrieval; explicit fairness or bias checks would be beneficial, especially under adversarial retrieval scenarios.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The high-level algorithm and equations are clear, but exact prompts, parsing logic, and error handling are not specified. Releasing these would likely raise this to 4.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If the promised code is available and includes prompts and parsers, it will be useful for practitioners experimenting with permutation ensembling.