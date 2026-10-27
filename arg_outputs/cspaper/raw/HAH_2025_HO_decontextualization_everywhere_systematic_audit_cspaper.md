# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper audits decontextualization strategies for long-document scientific QA on the PeerQA dataset. It systematically varies chunk granularity (sentence versus paragraph) and decontextualization templates (minimal, title, heading, title+heading, aggressive title), and evaluates several retrieval families (BM25, TF-IDF, dense sentence transformer, ColBERT) plus a cross-encoder reranker. A key result is that oracle-style per-paper indexing yields vastly inflated retrieval metrics versus full-corpus search, while downstream answerability F1 is only weakly coupled to retrieval quality and can even be comparable or higher under full-corpus settings. The paper provides practical recommendations favoring paragraph-level chunks with measured decontextualization and prioritizing paper identification before fine-grained evidence search.

## Summary Of Strengths
- Clear, targeted audit question with practical relevance: when and how decontextualization helps retrieval for scientific QA, and how that propagates downstream.
- Systematic sweep across templates and granularities for multiple retrieval families; the design helps isolate the effect of structure augmentation and chunk size.
- Useful and concrete empirical observation: oracle evaluations can massively overstate retrieval effectiveness compared to full-corpus retrieval. The contrast is quantified in Tables 3–5 and should inform better evaluation practices.
- Strong, explicit, and actionable takeaways for practitioners: prefer paragraph-level chunks with measured decontextualization, and prioritize paper identification before evidence search.
- The inclusion of both retrieval metrics (Recall@k, MRR) and downstream answerability F1 is valuable; the weak correlation (Table 8) highlights a non-obvious decoupling that many practitioners might miss.
- The paper is generally well organized, with results tables that make the core claims easy to verify. For instance, Table 4 clearly demonstrates the difficulty of full-corpus retrieval and supports the claim that late-interaction models with more context perform better under realistic conditions.

Figure- and table-grounded strengths:
- Table 3 (oracle setting) and Table 4 (full corpus) together provide a compelling quantitative story: BM25 reaches Recall@10=1.000 with paragraph/minimal in oracle (Table 3), but only 0.011 in full corpus (Table 4). This directly supports the claim that paper identification is the primary bottleneck in realistic scenarios.
- Table 6 shows the “retrieval–downstream decoupling” concretely: the best full-corpus configuration (Dense, para/title_heading) achieves F1=0.718, slightly exceeding the best oracle BM25 configuration at 0.713, despite having far worse Recall@10. This is a core insight of the paper, well supported by the numbers.

## Summary Of Weaknesses
1) Limited scope and generality
- The dataset is small (579 Q&A pairs from 90 papers). While this is stated in Limitations, conclusions about decontextualization and evaluation regimes would be stronger if corroborated on an additional, diverse long-document corpus (e.g., scientific or legal). As is, external validity is uncertain.

2) Narrow downstream evaluation
- Downstream analysis focuses on answerability classification only. Since many scientific QA deployments require grounded answer generation, it is unclear whether the weak retrieval–downstream coupling found here would hold for generation, where faithfulness depends critically on retrieved evidence. The paper gestures at this, but does not provide empirical support.

3) Insufficient detail for key components
- The cross-encoder reranker is described abstractly without naming the exact checkpoint, input formatting, top-k candidates reranked, or reranking depth. Similarly, the dense retriever is loosely specified as “all-MiniLM-L6-v2” but lacks index parameters, training/tuning considerations, or normalization details that can materially affect results. These omissions hinder reproducibility and may bias outcomes in favor of sparse methods under certain templates.
- For ColBERT, the specific variant, maxlen/tokenization, query/document encoders, and ANN settings are not fully enumerated, yet its full-corpus result (Table 4) is the best. More detail is needed to attribute gains to late interaction rather than confounds.

4) Oracle results include potentially confusing comparisons
- Table 1 mixes “representative models” (BM25, ColBERTv2, SPLADEv3) with “Ours” and presents disparate numbers. The provenance of the non-“Ours” rows is unclear, and it is not obvious whether these were re-run under the exact same experimental protocol. This weakens the credibility of the comparison and the message about decontextualization effects across model families.

5) Lack of statistical reporting and sensitivity analysis
- No error bars or variance estimates are provided, although retrieval metrics and F1 can vary substantially with random seeds, ANN hyperparameters, and reranking depth. The correlation analysis in Table 8 also lacks confidence intervals and details on the correlation method (Pearson/Spearman), which limits interpretability of the “weak correlation” claim.

6) Ambiguities in template definitions and “aggressive_title”
- Templates like “aggressive_title” are referenced in results (Tables 3–6) but not fully specified in Section 3.2. Without explicit formatting or examples, it is hard to reproduce why “aggressive_title” helps ColBERT in Table 4 or BM25 in Table 3.

7) Missing or incomplete retrieval protocol details
- Query construction is not discussed. In scientific QA, question reformulation and normalization can significantly impact sparse and dense retrieval. If questions were preprocessed or truncated, it should be stated.
- Indexing specifics like analyzer/tokenization for BM25/TF-IDF, stemming/stopword removal, and normalization are not detailed. These can alter the magnitude of oracle gains and the severity of full-corpus degradation.

8) Claims risk over-generalization
- The paper’s guidance is helpful, but some statements read more general than the evidence allows. For example, “retrieval may be optional for some tasks” (Section 4.7.2) is plausible for binary answerability, but this should be qualified more carefully so it is not misapplied to tasks where grounding is essential.

9) Figure–text mismatch
- Figure 1 outlines an AI-agent pipeline for paper generation, with references to GPT-5 and Claude Opus. This is not relevant to the research methodology of the audit and distracts from the scientific content. It raises avoidable questions about scope and coherence.

10) Limited analysis on why decontextualization hurts in oracle and helps in full corpus
- The paper reports the pattern (Tables 3 and 7) but stops short of a deeper lexical versus semantic matching analysis. For instance, sparse retrievers might be penalized by title drift in tight oracle settings and aided by disambiguation in large collections. A token-level or term-weight analysis would better support the narrative.

Figure- and table-grounded weaknesses:
- Figure 1 is orthogonal to the core technical content. Including a figure about “paper generation” instead of an architecture diagram or qualitative retrieval examples reduces clarity and could confuse readers about the contribution.
- Table 5’s “91× harder” label is rhetorically strong but methodologically vague. The calculation of “Relative Difficulty” is unclear and should be formalized or reframed as a simple ratio of search space and metric drops, with caveats.

## Potentially Missing Related Work
1) Newman et al., “A Question Answering Framework for Decontextualizing User-facing Snippets from Scientific Documents” (2023) — Directly studies decontextualization of scientific snippets. Should be discussed in Section 2 (Decontextualization and Structural Cues) and compared experimentally or conceptually with your templates in Section 4, especially regarding when added structure helps or hurts retrieval.

2) Chen et al., “DISRetrieval: Harnessing Discourse Structure for Long Document Retrieval” (2025) — Discourse-aware retrieval over long documents provides an alternative to ad hoc decontextualization. Add to Related Work (Section 2) and discuss as a complementary structural signal. If possible, include as a baseline or a point of contrast in Section 4.4.

3) Chen et al., “Retrieving on a Topic Graph for Long Document Question Answering” (2025) — Topic-graph retrieval (TGRAG) is a structured approach to long-document QA. Cite in Section 2 and discuss in Section 4.7 as an alternative to flat chunking plus decontextualization.

4) Wang et al., “Zero-Shot Complex Question-Answering on Long Scientific Documents” (2025) — Targets long scientific papers with zero-shot pipelines and emphasizes complex questions. Include in Section 2 to contextualize your PeerQA findings within broader scientific QA pipelines; optionally compare design choices in Section 4.1 and 4.6.

5) Kyoung et al., “Reasoning Beyond Length Limits: Improving Accuracy in Long-Context Question Answering With Small-Scale Language Models” (2025) — Combines instruction-tuned embedding-based retrieval and question rephrasing for long-context QA. Discuss in Related Work and as a potential avenue for addressing the “paper identification bottleneck” highlighted in Table 5.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Please provide full implementation specifics for all retrievers and the cross-encoder reranker: exact checkpoints, tokenization, max lengths, ANN index types and parameters, reranking depth, query/document formatting, and any normalization. A minimal config table would help reproducibility and interpretability.
- Clarify the “aggressive_title” template. Give explicit examples for all templates in Section 3.2, including punctuation and ordering, and whether titles/headings were normalized, stemmed, or length-truncated.
- Add statistical reporting: error bars from multiple runs for retrieval and F1, and confidence intervals for the correlations in Table 8. If compute is tight, even bootstrapped CIs on metrics would strengthen claims.
- Replace Figure 1 with a figure that is directly relevant to this paper’s contribution, such as: (a) a schematic of the retrieval pipeline under oracle versus full-corpus regimes, (b) a visualization of template construction, or (c) qualitative retrieval examples showing how decontextualization changes matches.
- Deepen the analysis of why decontextualization helps or hurts per retriever family. For example, add a term overlap/drift analysis for BM25 under oracle vs. full-corpus, and a token-level MaxSim inspection for ColBERT with and without titles.
- Consider a simple two-stage retrieval variant to illustrate your recommendation on “paper identification first,” e.g., a paper-level retriever (BM25 on titles/abstracts) followed by intra-paper evidence retrieval. Even a lightweight ablation would materially strengthen the guidance.
- If feasible, add at least one end-to-end answer generation metric (e.g., exact match, ROUGE, or faithfulness via QA-based evaluators) to test whether the retrieval–downstream decoupling holds beyond binary answerability.

Criteria to improve my score:
- Provide the missing implementation details and template definitions; add statistical significance or CIs; clean up Table 1’s provenance and ensure apples-to-apples comparisons. Replace Figure 1 with a relevant figure. A small two-stage retrieval experiment and one generation evaluation would likely move my rating toward main conference.

Typos and minor issues:
- Section 2: trailing duplicated phrase “tive guidance on decontextualization best practices...” appears to be a copy-editing artifact.
- Table 1 caption and entries: clarify whether “ColBERTv2” and “SPLADEv3” are re-implemented in your setup or quoted from prior work; if quoted, ensure consistent conditions or clearly mark them as non-comparable.
- Section 4.5/Table 5: define “Relative Difficulty” precisely and avoid overstating exact “× harder” without a formal measure.
- Ensure consistent naming of templates across sections and tables (e.g., “title_heading” vs. “Full Context” vs. “aggressive_title”).

## Confidence
3: Reasonably confident but not fully verified — I carefully read the paper and checked tables/claims, but some implementation details are missing, and I did not independently verify the reported numbers.

## Soundness
3: Acceptable — The study supports its central claims with controlled experiments and clear tables, but missing implementation details, lack of statistical reporting, and a narrow downstream task scope reduce the overall rigor.

## Excitement
3.0: Interesting — The findings on oracle vs. full-corpus evaluation and the retrieval–downstream decoupling are useful and discussion-worthy, especially for practitioners in scientific QA.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The work presents a careful empirical audit with practically important observations about oracle versus full-corpus retrieval and decontextualization choices. However, the scope is limited to answerability F1 on a modest dataset; several essential implementation details are missing; statistical reporting is absent; and Figure 1 is off-scope. With clarifications, stronger methodology documentation, and minor experimental extensions, this would make a solid Findings contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper includes a Limitations section that candidly notes dataset scope, task coverage, tuning, and indexing scale. The Broader Impacts and Code of Ethics sections acknowledge risks from overreliance on answerability detectors and recommend provenance display and abstention mechanisms. One additional suggestion: emphasize that conclusions about retrieval–downstream decoupling are specific to binary answerability; for decision support that requires factual grounding, retrieval quality remains critical. Also note potential bias amplification if paper-identification is weak, and suggest monitoring venue/topic distributions explicitly.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty — The experimental matrix is clear, but missing implementation specifics and statistical details limit faithful reproduction. The paper states that code is provided as a zip, but the text should still specify enough to re-run the key configurations.

## Datasets
1: No usable datasets submitted.

## Software
3: Potentially useful — If released, the configurable framework that sweeps templates and retrievers would be useful. Value depends on providing complete configuration defaults and scripts for both oracle and full-corpus settings.