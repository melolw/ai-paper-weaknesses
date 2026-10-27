# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes MisLC, a task and dataset for detecting misinformation with legal consequences. The authors frame labels using legal tests and defenses across 4 broad topics and 11 legal issues, and curate data in two stages: crowd-sourced “checkworthiness” filtering on Russia–Ukraine tweets, followed by expert legal annotation that assigns one of three labels (MisLC, Non-MisLC, Unclear) and any applicable legal issues, optionally with evidence. They benchmark a range of LLMs, with and without retrieval-augmented generation (two RAG methods, IC‑RALM and FLARE), using a curated legal document database and web search. Results show the task is difficult; even the best systems underperform human experts, while retrieval sometimes helps. The paper argues for legally grounded misinformation detection and offers analysis and ablations.

## Summary Of Strengths
- Problem formulation and interdisciplinary framing:
  - The task focuses on legally consequential misinformation rather than only veracity, explicitly grounding decisions in legal tests and defenses (Sections 3.1 and E). This is an original angle that connects NLP with law and societal impact.
- Resource contribution and pipeline:
  - Two-stage curation (crowd checkworthiness plus expert legal labeling) is well motivated for this domain; Figure 1 (Page 1) clearly communicates the pipeline and the role of retrieval and expert judgment.
  - The dataset includes issue-level metadata (11 legal issues) and evidence links when available, which can support future modeling beyond binary detection.
- Empirical breadth:
  - Broad benchmarking across closed- and open-source LLMs, with two retrieval strategies (IC‑RALM and FLARE), legal-document retrieval, and web-search augmentation (Sections 4–5). This provides an initial, useful baseline landscape.
  - The paper includes ablations where models are given random legal documents or oracle issue definitions/evidence (Table 4, Page 8), providing insight into what information helps.
- Analysis and transparency:
  - Dataset statistics and label distributions are reported (Table 1, Page 5; Figure 2, Page 5).
  - The authors explicitly compute a human-expert “upper bound” reference (Table 3, Page 7).
  - Retrieval behavior is visualized via prediction distributions (Figure 3, Page 8) and extended analyses appear in the appendix (Figures 6–13).

## Summary Of Weaknesses
1) Ambiguities and inconsistencies in the formal task definition
- Equation (1), Page 3, defines y_i = 2 (MisLC) when |E_i| > 0 and |L_i| > 0, and y_i = −1 otherwise if |E_i| > 0 and |L_i| = 0 or t_i is not a claim. There is no explicit condition for the Unclear class (y_i = 1) in the equation. Later (Page 5), Unclear is described as cases where context prevents fact-checking and implies |E_i| = 0, but Table 1 reports “Evidence available” for only 51.0% of samples while Unclear is 11.0%. That would leave many samples with |E_i| = 0 that are not Unclear, contradicting the earlier implication. Please precisely formalize y_i = 1 and reconcile these counts with Equation (1).
- The text says “A necessary condition … is that it makes a claim,” while Table 1 has a “noClaim” attribute for 42.8%. How exactly are such samples used in evaluation if MisLC requires a claim?

2) Dataset size, class balance, and legal coverage
- The final dataset (Table 1) has 711 samples, with only 93 MisLC positives (13.1%). This is very small for training or robust benchmarking and highly imbalanced. The limited coverage complicates generalization claims across 11 issues, particularly when Figure 2 shows concentration in a few issues (Freedom of Expression and Defamation dominate), leaving others sparsely represented.
- The single topical source (Russia–Ukraine tweets) may bias the legal issues observed, reducing the dataset’s representativeness for other legally consequential misinformation contexts.

3) Inter-annotator agreement and expert protocol
- Legal-label Krippendorff’s α is 0.441 (Page 4), far below the commonly cited 0.667 threshold for reliability. The paper acknowledges legal subjectivity, but downstream experiments rely on these labels as ground truth without a deeper reliability analysis by issue type, by annotator cohort, or adjudication. For a legally grounded benchmark, more rigorous quality control or expert adjudication is warranted.
- Experts are first- and second-year graduate law students working for course credit (Page 4). Additional detail on calibration, training, and supervision is needed to support label validity for fine-grained legal issues.

4) Adversarial filtering design and its consequences
- The adversarial filtering process (Algorithm 1 and Equation 2, Pages 4–5) uses KL divergence on the crowd checkworthiness distributions and repeatedly removes “easy” items until a target size, but the target is k = 1000 while the final retained set reported is 711 after three runs. It is not entirely clear how the three runs interact to produce the final 711 or how much label distribution drift occurs across iterations. More clarity is needed.
- By construction the filtering “biases the label distribution to Checkworthy samples” (Page 4). Since gold MisLC is determined by legal experts and not equivalent to crowd checkworthiness, this filtering may inadvertently discard hard but valuable negatives or nuanced cases that are important to legal reasoning.

5) Evaluation design and metric choices
- Error handling conflates instruction-following with task performance: predictions that violate output-format constraints are converted to Non‑MisLC (Page 6). This choice, combined with heavy class imbalance, can unduly penalize some models and entangle calibration/obedience with detection performance. Please report metrics with and without this conversion, or treat “error” as a separate class and report macro-F1 including it.
- Hyperparameters for FLARE (e.g., θ via Figure 5, Page 15) are tuned on 100 samples from the same dataset used for evaluation. Given the small dataset, this can lead to optimistic estimates. A clean split or cross-validation would be preferable.

6) Retrieval and evidence pipeline limitations
- The legal database contains 27 long documents that were chunked (Page 6 and Appendix B.2), but Table 4 ablations show that an Oracle injection of legal-issue definitions can hurt performance relative to retrieved context. This suggests the current retrieval may be surfacing long, context-heavy text that helps models answer heuristically rather than enforcing precise legal tests, or that prompts are not optimized for concise definitions. The paper should analyze which retrieved spans correlate with correct decisions.
- Web search incorporates only the first result’s snippet per query (Page 6), leading to high miss rates and sparse evidence. This is acknowledged, but it limits the conclusion that “retrieval helps” in a general sense.

7) Limited external validity and jurisdictional scope
- Legal tests and defenses appear primarily Canadian and European (Page 3). The dataset is English tweets about a global conflict. The paper does not examine portability across jurisdictions or how the same claim might be labeled under different legal frameworks. Without cross-jurisdiction analysis, claims of “legal consequence” are narrow and should be framed accordingly.

8) Missing or confusing legal descriptions
- In Table 11 (Pages 18–19), the “Food and Drugs Act” and “Data Privacy” rows appear swapped: the description under “Food and Drugs Act” actually discusses privacy and consent, while the “Data Privacy” row cites the Food and Drugs Act. This is a substantive clarity error for a legally grounded dataset and needs correction.
- Several issues in Table 11 have “N/A” defenses where in practice multiple defenses usually exist. This risks oversimplifying the legal landscape and can mislead model design.

9) Limited qualitative error analysis
- The work would benefit from case studies showing model decisions versus expert reasoning and retrieved content, especially false positives/negatives across Defamation vs. Freedom of Expression, where contextual defenses matter.

10) Figures and tables reveal important but under-explained patterns
- Figure 3 (Page 8) shows Llama2‑13b predicting MisLC for a large majority under IC‑RALM, while Llama3‑70b collapses to Unsure with IC‑RALM. These are striking failure modes of retrieval frequency and prompt sensitivity. The paper mentions this briefly; deeper analysis or parameter sweeps for retrieval stride and query windows would strengthen the conclusions.
- Table 2 (Page 7) shows some retrieval settings degrade performance for smaller models, and most models remain close to random in 3‑way macro‑F1. This undermines the general claim that “retrieval helps,” which should be qualified to the strongest settings and models.

Overall, while the dataset and framing are promising, the current version has definitional gaps, small and imbalanced data, limited reliability, and evaluation choices that blur instruction-following with detection.

## Potentially Missing Related Work
- Kennedy et al., “Repeat Spreaders and Election Delegitimization: A Comprehensive Dataset of Misinformation Tweets from the 2020 U.S. Election,” 2022 — directly relevant to the “Election Laws” framing; should be discussed in Related Work and considered as an external evaluation set for claims tied to election misinformation. Add in Section 2 and consider a transfer test in Section 5.
- Nguyen et al., “RMDM: A Multilabel Fakenews Dataset for Vietnamese Evidence Verification,” 2023 — aligns with legal/evidence-oriented verification in a non-English setting; useful for cross-lingual transfer discussion. Cite in Section 2; compare paradigms in Section 3.2 and discuss cross-lingual portability in Section 6.
- Socol de la Osa et al., “Artificial intelligence at the bench: Legal and ethical challenges of informing—or misinforming—judicial decision-making through generative AI,” 2024 — complements the paper’s legal angle by analyzing downstream legal risks of LLM outputs; include in Ethics/Limitations discussion and Related Work to contextualize legal-consequence framing.

(Other listed items are later than the time window strongly implied by this paper’s references. If the authors include a broader, forward-looking related work section, the remaining entries could be briefly acknowledged as neighboring directions: dynamic multilingual misinformation benchmarks, search-grounded multimodal misinformation detection, and LLM legal-risk mitigation with knowledge graphs.)

## Comments Suggestions And Typos
Actionable suggestions:
1) Clarify and fix the formal labeling conditions.
- Provide a complete, non-contradictory definition for y_i = 1 (Unclear) in Equation (1) or a companion equation. Reconcile Table 1’s “Evidence available” with the Unclear rate and with the “noClaim” attribute.
- Explicitly describe how samples with noClaim are handled in evaluation and whether they appear in the final test set.

2) Strengthen dataset reliability and coverage.
- Report IAA per legal issue, with confusion matrices among issues to show where disagreements arise. Consider expert adjudication for low-agreement items.
- Expand data sources beyond a single topical stream to diversify legal issues and reduce topic bias, or clearly position MisLC‑v1 as a pilot dataset and commit to a roadmap for broader coverage.

3) Improve evaluation protocol.
- Separate format errors from predictions, and report both constrained and unconstrained metrics without collapsing errors into Non‑MisLC. Include an “obedience/format” metric to decouple instruction adherence from classification.
- Use a held-out development split or cross-validation for hyperparameter tuning, especially for FLARE’s θ, to avoid optimistic estimates on a small dataset.

4) Deepen retrieval analysis.
- For Table 4’s Oracle vs. Retrieved gap, show example retrieved passages that helped/hurt. Compare using definitions plus a small set of directly relevant statutory snippets to test whether concise, precise legal text is more useful than long, general passages.
- Consider multi-hop evidence aggregation for web search and a more robust evidence selection policy than the first result’s snippet.

5) Legal taxonomy cleanup and documentation.
- Correct Table 11 (Food and Drugs Act vs. Data Privacy rows are swapped). Add missing defenses where applicable and provide specific citations inline for each issue.
- Provide short, concrete examples for each legal issue and defense to guide future modeling.

Typos/formatting:
- Table 7 (Appendix): “Llama1‑8b” likely “Llama3‑8b”; “Llama2‑12b” probably “Llama2‑13b.”
- Table 9: Several model names have inconsistent parameter counts (e.g., “Solar‑18b,” “Llama2‑78b”), which do not match earlier sections. Please standardize names across the paper.
- Page 6: “Mi-f1 ↑” sometimes appears as “Mu-f1 ↑” in appendices; ensure consistent notation.
- Page 8: In Table 4 caption, there is a stray “i” under the table.
- Check consistent capitalization of “Unsure” vs. “Unclear” throughout.

How my recommendation could change:
- If the authors fix the labeling definition inconsistencies, separate obedience errors from classification metrics, correct the legal taxonomy table, and add a small, held-out split for hyperparameter tuning with a clearer retrieval analysis tied to specific legal tests, my assessment could increase by one notch.
- A larger, more balanced dataset or a stronger reliability protocol and adjudication would further strengthen the case for main-track acceptance.

## Confidence
4: Quite sure after careful checking — I checked equations, figures, and tables carefully, and I am familiar with LLMs/RAG and dataset design in NLP. Some legal nuances may still admit alternative interpretations.

## Soundness
3: Acceptable — Core claims are supported, but the labeling definition is under-specified, reliability is modest, and parts of the evaluation conflate obedience with classification.

## Excitement
3.0: Interesting — The legal-consequence framing is timely and useful. Execution has notable caveats that limit immediate impact.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The dataset and framing are valuable and the empirical study is informative, but definitional ambiguities, small scale, modest IAA, and evaluation choices prevent a strong main-track case at this time.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper acknowledges censorship risks and contested roles of law in misinformation regulation (Limitations and Ethics). Additional points to address:
  - Jurisdictional narrowness: labels are tied primarily to Canadian and European law, which may not transfer. The dataset should include clear jurisdictional metadata and guidance against overgeneralization.
  - Annotator expertise: given that graduate students provided labels, potential misapplication of legal tests exists; more senior review or adjudication would mitigate this.
  - Dual use: tools trained on MisLC could be misused to suppress speech under the guise of “legal consequence.” The paper should propose governance, auditing, and transparency practices for downstream deployment.
  - Privacy: tweets are public, but ethical use still demands care; reiterate policies on redaction, user anonymity, and compliance with platform terms, especially given sensitive topics.

## Ethical concerns
None beyond those discussed; the paper is aware of and discusses core risks. Strengthening the jurisdictional and annotator-expertise disclosures, and adding deployment safeguards, would be beneficial.

## Needs Ethics Review
No

## Reproducibility
3: Reproducible with difficulty — Dataset construction and prompts are described, but reliance on closed APIs, a code/data placeholder, and small hyperparameter tuning on the same dataset reduce ease of reproduction. A public release with fixed seeds, retrieval indices, and evaluation scripts would raise this to 4.

## Datasets
3: Potentially useful — The dataset is small and imbalanced but could seed research on legally grounded misinformation detection. Clearer documentation and a growth plan would increase utility.

## Software
3: Potentially useful — Retrieval code and evaluation scripts could be useful if released and decoupled from closed APIs.