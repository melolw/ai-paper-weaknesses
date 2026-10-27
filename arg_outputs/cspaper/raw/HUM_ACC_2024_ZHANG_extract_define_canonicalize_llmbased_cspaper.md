# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes Extract-Define-Canonicalize (EDC), a three-phase LLM-based framework for knowledge graph construction (KGC) from text. Phase 1 performs open information extraction to generate subject–relation–object triplets without requiring a schema. Phase 2 uses LLMs to generate natural-language definitions for induced schema components (primarily relations). Phase 3 canonicalizes triplets either by aligning them to a provided target schema or by self-canonicalizing to a growing schema when no target is available; vector similarity over relation definitions proposes candidates and the LLM verifies transformations. An optional refinement step (EDC+R) adds a trained Schema Retriever to surface schema elements likely to appear in the text, improving extraction in an RAG-like loop. Experiments on WebNLG, REBEL, and Wiki-NRE show EDC/EDC+R is competitive or superior to state-of-the-art baselines in target-alignment settings and yields more concise, less redundant schemas than clustering-based canonicalization for self-canonicalization.

## Summary Of Strengths
- Clear and useful problem decomposition. Splitting KGC into open extraction, schema definition, and canonicalization is well-motivated and addresses the context-window limits of including large schemas in prompts.
- Flexible design. The framework supports both target alignment against large schemas and self-canonicalization when no schema exists, which is pragmatic for real-world deployments.
- Empirical gains and careful analyses. 
  - In the target-alignment setting, Figure 2 shows consistent improvements from EDC over baselines and further gains from refinement (EDC+R) across all three datasets; the pattern is stable across multiple LLMs for OIE.
  - Table 1 clearly demonstrates that removing the Schema Retriever reduces F1 on all datasets and criteria, supporting the claim that retrieval adds value beyond vanilla prompting.
  - Table 2 shows that, in self-canonicalization, EDC substantially reduces the number of relation types and the redundancy score versus Open KG and CESI while largely preserving precision (minor drop from Open KG but much improved schema quality).
- Sensible use of LLMs for definition and verification. Using LLM-generated relation definitions to drive candidate retrieval and LLM verification steps is a reasonable approach to mitigate overgeneralization typical of clustering-based canonicalization.
- Strong appendix with full results (Tables 3–10), ablations, and iteration studies. The authors also analyze why distant-supervision datasets penalize valid extractions and provide a small synthetic test to address leakage concerns.
- Figure 1 crisply communicates the pipeline, making it easy to grasp where each component contributes; the example concretely illustrates how definitions inform canonicalization decisions.

## Summary Of Weaknesses
1) Evaluation design for self-canonicalization relies on limited manual assessment and unconventional schema metrics.
- Table 2 reports human-evaluated precision and two schema metrics (number of relations and “redundancy” as average cosine similarity between relations and nearest neighbors). There is insufficient detail on how the redundancy score is computed: which embedding model is used, how relation strings/definitions are embedded, and sensitivity to the choice of encoder. Without such details, it is hard to compare to prior canonicalization metrics or to reproduce exactly.
- The human evaluation protocol is only briefly summarized: two annotators, inter-annotator agreement 0.94, but no details on sample sizes per dataset, annotation interface choices, per-annotator workload, or adjudication rules beyond the screenshot in Figure 3. This limits interpretability and reproducibility of Table 2.

2) Possible domain leakage in retriever training and impact on fairness of comparisons.
- The Schema Retriever is fine-tuned on TEKGEN (Appendix A.3), which was created by aligning Wikidata to Wikipedia. REBEL and Wiki-NRE are also Wikipedia-derived; WebNLG references DBpedia/Wikidata-like schemas. The paper does not quantify overlap between training pairs and test schemas/text, nor does it perform a “no-Wikipedia” retriever variant. This risks overstating the benefit of EDC+R if the retriever has indirectly seen similar text–relation distributions.

3) Scope of canonicalization is limited to relations; entity canonicalization is deferred.
- Section 6 acknowledges missing entity de-duplication and coreference. In practice, lack of entity canonicalization can inflate edge multiplicity and obscure improvements attributed to relation standardization. The paper would be stronger with at least a basic entity canonicalization module or a quantitative estimate of error attributable to entity variants.

4) Clarity and replicability of prompts and hyperparameters.
- Prompts are described, but some key details are missing for end-to-end replication: the exact few-shot examples (6-shot, but which items?), random seed control, temperature and decoding settings for each LLM by phase, and how errors in earlier phases propagate or are filtered. While Appendix A.2 lists retrieval cutoffs (top-5, top-10), the overall reproducibility still depends on prompt and decoding specifics.

5) Cost/latency and scalability considerations are underdeveloped.
- EDC runs several LLM passes per text: extraction, definition, canonicalization MCQs, and optional refinement with entity extraction plus retriever guidance. There is no discussion of throughput, cost per document, or scalability to large corpora, which is relevant for claims about handling large schemas. Reporting average tokens per step and wall-clock estimates would help practitioners.

6) Dataset curation and scoring concerns are acknowledged but not mitigated in the main results.
- Section 4.2.1 argues REBEL/Wiki-NRE annotations are incomplete; however, the paper still centers automatic metrics from the WebNLG scorer. A complementary human evaluation on a sample from these datasets would better support claims about extracting more correct triplets than the reference.

7) Limited variety of baselines for self-canonicalization.
- Only CESI is compared. There exist other open KG canonicalization or alignment approaches, including more recent LLM-infused or definition-based methods. A broader comparison, or at least discussion of why other models were not included, would improve credibility.

8) Ambiguity around “Target Alignment” choices and rejection handling.
- In Phase 3 (Target Alignment), when no semantic equivalent exists, the component and its triplets are “excluded.” This could disproportionately reduce recall without explicit reporting. The paper should quantify how often exclusions occur and their effect on metrics.

9) Some claims could be tempered or supported with more granular error analyses.
- For example, Figure 2 suggests that refinement helps consistently, but the text notes Mistral-7b benefits less. A breakdown of which error types refinement fixes (head–tail swaps, granularity corrections, literal handling) by dataset would make the case tighter.

10) Minor clarity issues around “vector similarity space.”
- Section 3.2 states the retriever’s similarity captures “relevance” and differs from “semantic equivalence” of sentence embeddings. Yet both stages use E5/Mistral embeddings. More precise descriptions of the query/candidate encodings, pooling strategy, and calibration would reduce confusion.

Figure- and table-specific comments:
- Figure 1 effectively communicates how EDC uses LLMs for definitions and then leverages candidates plus LLM verification for canonicalization. It supports the argument that LLMs can perform both semantic explanation and verification, not just extraction.
- Figure 2: The three bar charts help triangulate that EDC+R outperforms both EDC and baselines across datasets. However, the figure shows only Partial F1. Since Strict and Exact emphasize type correctness and triplet fidelity, including them (or referencing Tables 3–5 in the caption) would provide a more balanced view.
- Table 1 (ablation on Schema Retriever) convincingly supports the necessity of the retriever for refinement; the deltas are material on all datasets.
- Table 2 (self-canonicalization) is central to the “self” setting claim. The drop in precision vs. Open KG is small on WebNLG and Wiki-NRE, but notably larger on REBEL (0.903 to 0.867). A qualitative error analysis explaining this gap on REBEL would help, given the dataset’s noisier supervision.

## Potentially Missing Related Work
1) Sauka et al., “Building Hierarchy-Aware Knowledge Graphs: Ontology-Grounded Triple Extraction with LLMs,” 2024 — addresses LLM-driven triple extraction grounded in hierarchical ontologies and includes retriever-style components; relevant to Sections 3.1–3.2 and the refinement strategy. Should be discussed in Background/Related Work and compared in Section 4.
2) Meher et al., “LLM-Driven Knowledge Graph Construction for Human Smuggling Networks,” 2025 — modular pipeline with explicit hallucination and node-duplication control, closely related to the EDC pipeline’s practical constraints. Discuss as application-driven alternative in Section 2 and contrast failure controls in Section 6.
3) Khorashadizadeh et al., “Construction and Canonicalization of Economic Knowledge Graphs with LLMs,” 2025 — focuses on relation canonicalization and quantitative evaluation protocols; relevant to Section 4.1.1 and Table 2 metric choices. Cite in Related Work and discuss measurement alternatives after Eq./metric definitions in Section 4.1.1.
4) Zhang et al., “A large language model-based approach to building the knowledge graph for master plan,” 2025 — real-world policy document extraction; useful for discussing scalability and long-context issues (Section 4.1 and Section 6).
5) Polo-Bautista et al., “Harnessing large language models to build knowledge graphs from earthquake news,” 2025 — multi-step LLM pipeline with hallucination filtering; compare in Section 2 and discussion of failure modes in Section 6.
6) Yang et al., “Knowledge Graph and Large Language Model Co-learning via Structure-oriented RAG,” 2024 — surveys SRAG approaches that could frame the Schema Retriever more formally; cite in Section 3.2 and Related Work to contextualize the retriever+LLM loop.
7) Gangemi et al., “Text2AMR2FRED: converting text into RDF/OWL knowledge graphs via AMR,” 2026 — structured pipeline alternative to triplet extraction; discuss in Related Work and in Section 4 as a contrasting approach emphasizing logical consistency vs. open IE.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Please fully specify the redundancy metric in Table 2: the encoder used, what text is embedded (relation labels vs. definitions), normalization, nearest-neighbor protocol, and sensitivity to embedding choice. If possible, add a second redundancy metric or report variance across two encoders to show robustness.
- Quantify the rate of “exclusions” in Target Alignment (Phase 3) and their impact on Precision/Recall. A table or histogram of excluded vs. aligned transformations would clarify the trade-off.
- Provide more details for the human evaluation in Section 4.2.2: number of instances per dataset, sampling strategy, instructions, decision criteria, adjudication, and confidence intervals. Consider adding a small-scale human evaluation for REBEL and Wiki-NRE in the target-alignment setting to address annotation incompleteness.
- Address potential domain leakage: measure lexical/schema overlap between TEKGEN training pairs and the test sets’ schemas/text; if feasible, provide an additional retriever training variant excluding Wikipedia-derived sources, or at least a filtered training set, to check sensitivity.
- Report computational cost: average tokens per step, number of LLM calls per document, latency, and cost estimates for EDC vs. EDC+R. This would substantiate claims of scalability to large schemas.
- Add an error analysis by category for refinement (head–tail swaps, literal normalization, relation granularity, homonym disambiguation), connected to Table 1 and Figure 2.
- Minor: Clarify in Section 3.2 whether the retriever encodes text and relation definitions symmetrically, and whether any temperature-scaled similarity or margining is used.

Typos and small edits:
- Page 6, “reasonableness of triplet extractions” → “correctness/reasonableness of triplet extractions” (to match the later precision definition).
- Page 7, “Figure 2: ... (F1 scores with 'Partial' criteria).” Consider adding Strict/Exact curves or point to Tables 3–5 explicitly in the caption.
- Appendix A.3: missing closing quote for the instruction template string in one inline equation; ensure consistent LaTeX escaping of quotes and newlines.

Criteria for score change during rebuttal:
- Provide complete redundancy metric details and a small robustness check across two encoders.
- Add quantitative analysis of exclusions in Target Alignment and their effect on recall.
- Expand human evaluation protocol details and, ideally, include a small human eval for target-alignment on REBEL/Wiki-NRE.
- Provide leakage analysis for the retriever and a brief cost/latency breakdown.
If addressed convincingly, I would be inclined to raise Soundness and Overall Assessment by one notch.

## Confidence
4: Quite sure after careful checking — I checked the main claims, figures (Figure 1–2), and key tables (Tables 1–2, with references to 3–10). It is unlikely I missed something material.

## Soundness
3.5: Between Acceptable and Strong — Method and results are generally solid, but the self-canonicalization evaluation and leakage/scalability questions merit additional evidence.

## Excitement
3.5: Between interesting and exciting — The decomposition and refinement loop are practical and likely useful; not flamboyant, but clearly impactful.

## Overall Assessment
4: Conference — recommend acceptance to ACL main. The work presents a well-thought-out, flexible framework with convincing empirical support, clear ablations (Table 1), and informative visual summaries (Figure 2). Some evaluation and clarity gaps remain but are addressable before camera-ready.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges key limitations (lack of entity canonicalization; reliance on GPT-3.5 for most modules; retriever training data breadth). I suggest also discussing:
- Risks of propagating LLM hallucinations through definition and verification stages, especially in self-canonicalization where no ground-truth schema constrains outputs.
- Potential bias amplification: if the retriever and LLMs are trained on Wikipedia-like distributions, underrepresented entity types/relations may be systematically missed in both extraction and canonicalization.
- Privacy considerations when processing personal data at scale, with guidance for redaction and audit logs.
Overall, the societal impact can be positive for building structured knowledge from text, but failure modes (incorrect canonicalization, spurious relations) can misinform downstream applications if not audited.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — prompts, high-level algorithm, ablation settings, and datasets are provided; some missing specifics (prompt examples, decoder settings, cost) should be added to reach 5.

## Datasets
2: Documentary — no substantive new dataset beyond a small fictional set for leakage checks; still useful to replicate.

## Software
4: Useful — authors state code is available in supplementary materials; if fully released with prompts, it will be valuable for others to build upon.