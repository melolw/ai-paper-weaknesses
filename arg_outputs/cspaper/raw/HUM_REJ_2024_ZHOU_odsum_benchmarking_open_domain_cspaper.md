# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
The paper introduces ODSUM, a pair of benchmarks for open-domain multi-document summarization (ODMDS) derived from SQuALITY (stories) and QMSum (meetings). The construction pipeline segments long sources into multiple documents, decontextualizes or clusters queries using LLMs, and forms a large document index from which systems must retrieve and then summarize. The authors evaluate retrieve-then-summarize pipelines with sparse, dense, and LLM-based retrievers and several summarizers, including BART, PRIMERA, GPT-3.5, GPT-4, and Llama-2. Results show that retrieval quality strongly governs downstream summarization, and that traditional metrics (ROUGE, BERTScore) poorly reflect retrieval-induced brittleness relative to G-EVAL. The paper also explores strategies like truncation, map-reduce, and refine to mitigate retrieval errors.

## Summary Of Strengths
- Clear motivation for ODMDS: the work articulates the gap between conventional MDS/QMDS and real-world scenarios where relevant documents must first be retrieved from a large corpus.
- Concrete benchmark construction: the paper details two variants, ODSUM-STORY and ODSUM-MEET, with dataset statistics (Table 2) and a human validation study (Table 3). The reported averages (e.g., 7176 tokens for meetings) indicate large-context difficulty aligned with ODMDS.
- Strong breadth of baselines: sparse (BM25), dense (Contriever), and LLM-embedding retrieval are considered, and summarization covers pre-trained seq2seq models and instruction-tuned LLMs. The retrieve-then-summarize pipeline is well instantiated.
- Insightful findings about evaluation: the consistent discrepancy between ROUGE/BERTScore and G-EVAL is repeatedly evidenced in Tables 5–6, which is valuable for the community when measuring ODMDS under retrieval noise.
- Useful ablation of robustness strategies: Table 7 compares truncation, map-reduce, and refine in both oracle and error settings, yielding concrete, nontrivial insights about how document inclusion and ordering interact with robustness.
- Figure grounding: Figure 1 provides a high-level depiction of the ODSUM construction and task framing that helps situate the benchmark in relation to MDS/QMDS/ODQA, clarifying the intended end-to-end flow from query to doc retrieval to summary.

Specific figure/table engagement:
- Figure 1: The pipeline schematic clarifies the transformation from source documents to a multi-document index and then to query-summary pairs, reinforcing that the benchmark requires both realistic retrieval and synthesis. It supports the authors’ claim that queries are designed to be standalone and require multi-document aggregation.
- Table 4: The retrieval comparison shows GPT-embedding outperforming BM25 and Contriever on ODSUM-STORY across NDCG/MAP and human Cov%/Rel.%/1st Pos., and achieving notably higher Ans% (86.7) for ODSUM-MEET. This concretely underpins the paper’s central premise that better retrieval correlates with better downstream outcomes.
- Tables 5–6: The oracle rows consistently top G-EVAL, while BM25 and Contriever trail, directly demonstrating retrieval-to-summarization error propagation and bolstering the claim that ROUGE/BERTScore understate those differences.
- Table 7: The method-level robustness analysis is a standout, quantifying how strategies degrade from oracle to “with error” and showing method-dependent sensitivity, which will be valuable for practitioners.

## Summary Of Weaknesses
1) Dataset construction clarity and rigor
- ODSUM-STORY segmentation (Section 3.2) relies on HTML delimiters (“<hr class="***"/>”) to define chapter boundaries. The paper does not quantify segmentation errors, cross-story bleed, or the rate of malformed splits. Given that retrieval performance depends on document integrity, lack of quality control or error analysis here weakens the benchmark’s reliability.
- ODSUM-MEET (Section 3.3) clusters queries using a similarity threshold with text-embedding-ada-002, then merges queries and summaries via LLMs. The threshold selection, clustering stability, and inter-annotator validation for merged query/summary quality are not reported. Without ablation on θ or robustness checks (e.g., variance in cluster formation), it is hard to assess the consistency and reproducibility of this step.
- The decontextualization of SQuALITY queries using GPT-4 (§3.2) is only loosely validated. While Table 8 suggests better BM25 P@K/R@K after including titles/answers, the paper ultimately selects queries “based on both the title and the answer,” which risks target leakage and reduces the open-domain nature of the retrieval query. The selection criterion and acceptance thresholds for rewritten queries are not made precise.

2) Limited scale and diversity
- Table 2 shows only 635 queries for stories and 436 for meetings, with 250–262 training and 131–260 test instances. For a “benchmark,” this is modest and may not surface generalization issues or encourage robust data-driven learning. There is minimal discussion on domain coverage diversity, temporal robustness, or adversarial retrieval cases.

3) Retrieval evaluation design and reporting gaps
- Section 4.3: nDCG/MAP usage requires clear positive labels. It appears positives are oracle documents from the source datasets, but for STORIES, positives are at the story level, not necessarily chapter-level relevance. The paper should clarify how graded relevance is defined for multi-chapter relevance and how many true positive chapters exist per query. This matters because Table 4 shows discrepancies between automated and human metrics, and ambiguity on ground-truth construction limits interpretability.
- The human retrieval evaluation (Cov%, Rel.%, 1st Pos.; Ans% for meetings) is limited to 40 samples per subset (§3.4) and does not report inter-annotator agreement or confidence intervals. Given the centrality of retrieval to the findings, the qualitative validation is underpowered.

4) Evaluation methodology concerns for summarization
- G-EVAL is implemented with GPT-3.5 and used in a reference-based manner (§E.2.2, §E.2.3), diverging from source-grounded evaluation. This can reward paraphrase overlap and penalize factual additions not mirrored in the reference, especially in open-domain settings where multiple valid summaries exist. The paper argues G-EVAL correlates better with retrieval quality but does not present correlation analyses to human judgments on this dataset to substantiate that claim.
- Using a proprietary LLM to evaluate outputs from related proprietary LLMs raises risks of evaluator bias or style preference. While GPT-3.5 is used as an evaluator and GPT-4 as a generator in some settings, this still warrants a stronger triangulation with human evaluation on summarization, not only dataset quality.
- ROUGE reporting is limited: Tables 5–6 emphasize ROUGE-2 and BERTScore. Given the long-form nature, ROUGE-1 and ROUGE-L are relevant; ROUGE-L appears only in Table 7. This partial reporting also obscures the magnitude of retrieval-induced changes beyond bigram overlap.

5) Fairness of “oracle” vs retrieval settings
- It is unclear how many documents are provided in the oracle, how they are ordered, and whether inputs are normalized across retrievers in concatenation and truncation policies. The truncation strategies (§6.1) and model token limits (§E.1) imply that even oracle inputs are truncated; the degree and impact of oracle truncation should be reported. Otherwise, the comparison may confound retrieval quality with truncation artifacts.

6) Insufficient ablation on construction choices
- ODSUM-MEET query clustering: No experiments varying θ, min/max cluster sizes, or embedding models for similarity. Without this, the benchmark’s composition might be brittle to these arbitrary hyperparameters.
- ODSUM-STORY decontextualization: No user-study or crowd validation that the rewritten queries are truly standalone and realistic beyond the 80-sample dataset quality check, which focuses more on summary coherence and high-level properties (Table 3) rather than query naturalness.

7) Missing or minimal comparisons to directly related ODMDS advances
- The paper primarily contrasts BM25/Contriever vs LLM embeddings for retrieval, and standard LLMs for summarization. There is little engagement with ODMDS-specific retrieval reranking, graph augmentation, or clustering-aware methods that directly target multi-source synthesis. This weakens the claim that ODMDS remains challenging, since stronger ODMDS-specific pipelines are not included.

8) Ethical and licensing considerations are underdeveloped
- The paper does not include a dedicated Ethics section. For SQuALITY stories and QMSum meeting transcripts, licensing, copyright status, and any restrictions on redistribution need to be explicitly discussed. The use of GPT-4 to rewrite queries also raises data provenance questions. Human evaluation is reported but with no mention of consent, compensation norms, or IRB review, which is important when creating a lasting benchmark.

9) Figure and corpus transparency
- While Figure 1 is helpful, the paper does not quantify corpus size beyond counts in Table 2, nor specify retrieval index construction details such as tokenization, passage segmentation, or chunk sizes. For ODMDS, corpus granularity and indexing strategy significantly affect both retrieval and summarization; these details are necessary for reproducibility.

10) Metric–human correlation claims not empirically substantiated on this benchmark
- The paper states G-EVAL is “more reliable” for ODSUM, but does not provide correlation coefficients with human judgments collected on this benchmark. The human study in Table 3 focuses on dataset quality, not system output quality, so the key assertion about evaluation reliability remains unproven on the target setting.

## Potentially Missing Related Work
1) Giorgi et al., “Open Domain Multi-document Summarization: A Comprehensive Study of Model Brittleness under Retrieval,” 2023 — Directly defines ODMDS and analyzes retrieval brittleness; should be discussed in Section 2 with deeper differentiation and compared in the experimental framing. Include as a baseline framing reference in §4.
2) Zhou et al., “ODSum: New Benchmarks for Open Domain Multi-Document Summarization,” 2023 — Introduces open-domain MDS benchmarks highly aligned with this paper’s aims; should be discussed in Section 2 and explicitly compared in Sections 3 and 5 to clarify novelty in dataset design (query sources, corpus sizes, labeling) and evaluation protocol; address overlaps and differences in Tables 1–2 and retrieval/summarization setups.
3) Enomoto et al., “LightPAL: Lightweight Passage Retrieval for Open Domain Multi-Document Summarization,” 2024 — Proposes retrieval tuned for ODMDS; should be cited in §4.1 and, if feasible, added as a retrieval baseline in Table 4 or discussed as future inclusion.
4) Shen et al., “Graph-Augmented Open-Domain Multi-Document Summarization,” 2025 — Uses graph/clustering-aware methods to improve ODMDS. Discuss in §2 and contrast in §6 as a complementary approach to mitigate retrieval noise via inter-document modeling; if not included as a baseline, acknowledge in limitations/future work.
5) Phanse et al., “MSRS: Evaluating Multi-Source Retrieval-Augmented Generation,” 2025 — Introduces multi-source RAG benchmarks (MSRS-STORY/MEET) overlapping task structure. Discuss in §2 and contrast evaluation methodology/metrics in §5, especially with respect to retrieval–generation interactions.

## Comments Suggestions And Typos
Actionable suggestions:
- Retrieval labeling and evaluation
  - Precisely define relevance labels for nDCG/MAP at the document/chapter level. Report the number of positives per query and how graded relevance is handled for STORY and MEET. Add inter-annotator agreement for human retrieval evaluation and provide confidence intervals.
  - Include stronger, ODMDS-specific retrieval baselines or reranking (e.g., lightweight graph or cluster-aware methods). If infeasible, discuss expected effects relative to your reported baselines.
- Summarization evaluation
  - Complement G-EVAL with a system-level human evaluation on a representative subset, and report correlation (e.g., Kendall/Spearman) between G-EVAL, ROUGE-1/2/L, BERTScore, and human preferences on this benchmark. This would substantiate the claim that G-EVAL better captures retrieval-induced differences.
  - Report more complete ROUGE metrics (R-1, R-2, R-L) in Tables 5–6 to give a fuller picture of content vs structure overlap under retrieval perturbations; you already use R-1/R-L in Table 7.
- Construction transparency and robustness
  - For ODSUM-MEET, report the similarity threshold θ, sensitivity to θ, and min/max cluster size effects. Provide examples where merged queries improved coverage vs cases where they introduced ambiguity.
  - For ODSUM-STORY, quantify segmentation errors when using HTML delimiters and include a small manual audit; if needed, refine splitting heuristics.
  - In §3.2, clarify the precise rule for selecting decontextualized queries and the safeguards against target leakage when using the reference answer or title during rewriting. Consider a version constructed without answer access and report the performance gap.
- Oracle vs retrieval normalization
  - Explicitly state oracle document counts and input truncation policies across models. In Tables 5–6, add a column indicating the average token budget utilized for each setting to ensure fair comparison and to isolate retrieval from truncation effects.
- Ethics, licensing, and release
  - Add a dedicated ethics and data licensing section. State the licensing status of source texts and meeting transcripts, redistribution terms, anonymization safeguards, and human evaluation protocols (consent, compensation, IRB). Clarify plans for dataset/code release and any restrictions.
- Figure/Table-specific feedback
  - Figure 1 helps, but augment with a small inset summarizing corpus granularity (e.g., “#docs per query,” “avg positives per query,” “avg chapters per story,” “index chunk length”) to better set expectations on retrieval difficulty.
  - Table 4: Consider adding top-k variations (e.g., k=5,10,20) and retrieval time/memory footprints to contextualize LLM-embedding gains relative to dense retrievers. Also, explain the notable gap where Contriever has low nDCG/MAP in ODSUM-MEET but relatively high Rel.% — is this due to evaluation label granularity or ranking depth?
  - Tables 5–6: Since you claim GPT-4 is more sensitive to retrieval noise, quantify the effect size per retriever with confidence intervals or bootstrap CIs over G-EVAL. This will make the brittleness claims more rigorous.

Potential typos/clarifications:
- Table 1: “Rewrittn” → “Rewritten”; “Avg. Sum. Len.” spacing inconsistent.
- §3.2: “light document” likely “individual document.”
- §4.1: Footnote marker “¹” appears before the URL in §4.3; ensure consistent placement and formatting.
- §6.2: “Map-reduce achieves the highest score among all the settings,” then notes it has the lowest ROUGE; specify “highest G-EVAL” to avoid confusion.
- Table 7: Label columns consistently (e.g., R-1/R-2/R-L) and indicate which model this table uses (appears to be GPT-3.5 per §6, but make explicit).

Criteria for improved score in rebuttal:
- Provide concrete details and ablations for query clustering thresholds and STORY segmentation quality; clarify oracle composition and truncation fairness across settings.
- Add at least a small-scale system-level human evaluation of summarization output to validate G-EVAL’s alignment on ODSUM, and provide correlation analyses.
- Expand the related work to include closely overlapping ODMDS benchmarks and methods; if possible, add one ODMDS-specific retriever/reranker baseline or a reasoned discussion with expected outcomes.

## Confidence
3: Reasonably confident but not fully verified — The area is familiar, and the paper is clear, but several construction and evaluation details are underspecified and would benefit from author clarification.

## Soundness
3: Acceptable — The study broadly supports its main claims, but important methodological and evaluation details are missing or underspecified (retrieval labeling, oracle/truncation control, metric–human correlation), and analysis of construction choices is limited.

## Excitement
3.0: Interesting — The benchmark direction is useful and the analysis of retrieval brittleness is relevant, but missing comparisons and evaluation gaps temper enthusiasm.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The contribution is sound and useful as a resource and analysis for ODMDS, but the benchmark construction needs more transparency and ablation, the evaluation requires stronger human validation and comparisons to closely related benchmarks/methods, and ethics/licensing should be explicitly addressed. With these addressed, it could be competitive for the main conference in a subsequent cycle.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper’s Limitations section acknowledges context-length advances and LLM-generated query bias, which is good. However, societal and ethical impacts are not sufficiently discussed for a dataset-heavy contribution:
  - Licensing and redistribution of stories and meeting transcripts should be clarified.
  - Risks of LLM rewriting introducing unintended biases or leakage need discussion.
  - Human evaluation protocols (consent, compensation, IRB) should be stated.
  - Potential downstream harms from summarizing multi-source meeting content, including privacy considerations and misattribution risks, should be analyzed with suggested mitigations.

Constructively, adding a dedicated ethics section covering data sources, processing, participant protections, potential misuse, and dataset release terms would materially strengthen the paper.

## Ethical concerns
The absence of a dedicated ethics section is a concern for a benchmark paper. Key missing items: licensing of source texts, privacy/anonymization for meeting transcripts, consent/IRB for human evaluation, and risks of LLM-rewritten queries. These should be explicitly addressed.

## Needs Ethics Review
Yes

## Reproducibility
3: Reproducible with difficulty — High-level pipeline is clear and prompts are shared, but several critical details are underspecified (retrieval labeling, clustering thresholds, oracle/truncation normalization, index chunking), and dependence on proprietary APIs complicates exact reproduction.

## Datasets
3: Potentially useful — The benchmark is promising and could be used by others, but current documentation and ethical/licensing clarity need improvement, and scale/diversity are moderate.

## Software
3: Potentially useful — If released, the retrieval/summarization pipelines and evaluation scripts would be useful. As written, availability and completeness are unclear.