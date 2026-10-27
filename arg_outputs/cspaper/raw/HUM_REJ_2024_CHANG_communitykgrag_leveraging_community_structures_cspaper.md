# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes CommunityKG-RAG, a zero-shot RAG framework that builds a knowledge graph from fact-checking articles, detects communities using Louvain, represents each community by averaging BERT node embeddings, ranks communities for a given claim using a dot product with a Sentence-BERT embedding of the claim, and then returns top-ranked sentences associated with the selected communities as context to an LLM for claim verification. Experiments on the MOCHEG dataset compare CommunityKG-RAG with no retrieval, semantic retrieval, and KAPING, reporting sizable accuracy gains (e.g., 56.24% vs 43.84%). Ablations vary δ (top percent of communities) and λ (percent of sentences per community) and explore two LLM backbones (LLaMa2-7B and LLaMa3-8B).

## Summary Of Strengths
- Clear motivation to exploit KG structure, especially multi-hop and community signals, to improve retrieval for fact-checking.
- Method simplicity and zero-shot nature are attractive: no additional model training; the graph is constructed once and reused.
- Figures and tables improve readability and give a coherent narrative.
  - Figure 2 provides a useful overview of the full pipeline from coreference resolution to relation extraction, community detection, and community-to-sentence selection. It helps readers follow the retrieval logic and locate potential bottlenecks.
  - Figure 1 offers an intuitive qualitative example contrasting no retrieval, vanilla semantic retrieval, and the proposed CommunityKG-RAG; it illustrates how multi-hop community context can change a prediction from NEI to True.
- Reported main results are competitive on MOCHEG:
  - Table 1 shows CommunityKG-RAG_100^25 at 56.24% accuracy, improving substantially over semantic retrieval (43.84%) and KAPING (39.41%).
- Ablations provide some insight into δ/λ sensitivity and backbone effects:
  - Table 3 and Table 4 probe the trade-off between breadth (more communities) and depth (more sentences), and suggest that including all sentences in top communities can yield the best LLaMa2-7B performance.
  - Table 2 demonstrates the approach transfers to LLaMa3-8B with improvements over no retrieval.
- The paper explicitly discusses limitations (Section 8), including computational demands and reliance on entity recognition quality.

## Summary Of Weaknesses
1) Insufficient baseline coverage and fairness of comparisons
- The evaluation omits standard, strong non-graph RAG retrieval baselines. For fact verification, a fair comparison should include BM25/Anserini, dense retrievers like DPR/Contriever, hybrid retrieval (BM25 + dense), late-interaction models like ColBERTv2, and recent RAG tricks (e.g., HyDE). Without these, it is hard to attribute gains to community structure rather than to a weak baseline choice.
- Only a single KG-based baseline is considered (KAPING), and the implementation is described at a high level. There are well-known graph-centric or hybrid KG+RAG systems that should be included as baselines or discussed more directly (see Missing Related Work).

2) Risk of data leakage and unclear split protocol (Appendix A; Section 5.1)
- Appendix A states: “The dataset was partitioned into training and testing… the training set employed for constructing the knowledge graph and verifying claim accuracy.” The phrase “verifying claim accuracy” with the training set is ambiguous and suggests use of training claims during evaluation or possible contamination. Clarify explicitly:
  - Is the KG built only from training articles while test claims are verified against sentences originating strictly from training articles?
  - If so, do many test claims require evidence not contained in the training articles, leading to NEI inflation for baselines that rely on broader corpora?
  - If the KG (or the sentence pool) also includes test articles, that would be leakage since the LLM is evaluated on those test claims. This point critically affects the validity of Table 1, Table 3, and Table 4.
- The paper needs a precise description of construction/evaluation splits for KG nodes, edges, and candidate sentences, and a check ruling out test leakage.

3) Underspecified mapping from communities to sentences (Section 4.5; Figure 2)
- The core operation is “community-to-sentence selection,” yet the mapping is not operationally defined. How are sentences linked back to nodes/edges? What if a sentence contains multiple entities spanning different communities? Is there deduplication? Are relation extractions used to index sentences, or are sentences attached to every entity they mention? Ambiguity here makes it hard to reproduce the pipeline and to reason about the noise profile when λ increases.
- Figure 2 labels the step but does not detail the algorithmic mapping. A pseudo-code or explicit indexing schema is needed.

4) Embedding and scoring choices are ad hoc and may bias results (Section 4.3)
- Community embeddings average BERT token embeddings of entity strings, but claims are encoded by Sentence-BERT. Dot-product similarity mixes encoders and is sensitive to vector norms; cosine similarity is more standard for SBERT. No evidence is provided that dot product outperforms cosine here.
- Averaging static BERT word embeddings for entities is a weak representation of subgraph semantics. At least test:
  - sentence-level embeddings for nodes (e.g., encode canonical descriptions),
  - graph-aware pooling (degree-weighted; centrality-aware),
  - relation-type features or edge-aware pooling.
- No ablation isolates the contribution of “community detection” versus “simply retrieving more topically similar sentences.” For example, compare against retrieving the top-N sentences by SBERT similarity without graph use, controlled for total token budget.

5) Limited dataset scope and metrics (Sections 5–6)
- Only MOCHEG is used. Standard textual fact-checking datasets such as FEVER, FEVER-Symmetric, LIAR, and SciFact would considerably strengthen claims of generality.
- The sole metric is accuracy. Given the 3-way label space, report macro-F1 and per-class F1 to account for imbalance and reveal whether gains come from a single class (e.g., NEI).
- No statistical significance testing is provided for Table 1–4 improvements.

6) Token budget, latency, and failure modes not quantified (Sections 6, 8)
- The approach can return many sentences when λ is large. Table 3 suggests the best LLaMa2-7B performance at λ=100%, which likely increases token counts and latency. There is no profiling of:
  - avg tokens passed to the LLM per claim,
  - runtime/latency vs baselines,
  - retrieval precision/recall of evidence. 
- Without cost-quality curves, it is unclear whether the headline gains stem from feeding far more context, not from the community structure per se.

7) Interpretation of ablations is incomplete or inconsistent (Section 6.2; Table 3; Table 4)
- Table 3 shows performance drops at λ=50% then rises at λ=75% and λ=100%. The explanation that “top 25% is most crucial; 50% adds noise; 100% adds helpful context” is plausible but not substantiated with evidence-level analyses (what types of sentences at 50% hurt performance?). A breakdown of error types and qualitative examples would help.
- Table 4 concludes that “targeted selection of highly relevant communities + comprehensive sentences” works best, yet CommunityKG-RAG_100^100 underperforms CommunityKG-RAG_100^25 in Table 1. The conditions and sample sizes differ across tables, so the narrative should be more carefully tied to identical settings or control for token budget.

8) Claims about “multi-hop” use remain largely indirect (Sections 1, 4.2; Appendix E; Figure 2)
- Table 5 reports shortest path and diameter statistics of the selected subgraphs, which is indirect evidence. The paper does not show that the system actually retrieves multi-hop evidence that matters for decisions, e.g., by tracing paths that connect claim entities to evidence sentences.
- A targeted study measuring performance on claims that require k-hop reasoning vs. 1-hop would substantiate the multi-hop hypothesis.

9) Missing or thin connections to closely related recent work and strong GraphRAG baselines
- The paper cites Edge et al., 2024 (GraphRAG), but does not position against broader GraphRAG design spaces and community-based subgraph retrieval that are now well-discussed. See the next section for specific, missing works to integrate and potentially add as baselines.

10) Reproducibility gaps
- Crucial details are missing for others to reimplement: REBEL configuration and post-processing; entity normalization and deduplication; how sentences are chunked; exact handling of coreference spans; how many sentences per claim are finally passed into the LLM; any truncation rules; community indexing data structures; thresholds for score ties; prompt templates per setting and any task-specific heuristics.

Figure- and table-specific comments:
- Figure 1: The qualitative example is helpful, but please provide the exact evidence snippets used in each panel (semantic retrieval vs CommunityKG-RAG) and why semantic retrieval missed them. This would support the claim that community structure enables multi-hop retrieval that pure semantic similarity missed.
- Figure 2: The “Community-to-Sentence Selection” block is central to the paper, yet its algorithm is not specified. How the dotted arrows correspond to concrete indexing steps should be spelled out and referenced in Section 4.5 with explicit equations or pseudo-code.
- Table 1: The margins over semantic retrieval are large. To strengthen the claim, add stronger retrieval baselines (BM25, Contriever, ColBERTv2) and normalize token budgets across methods.
- Table 3 and Table 4: Please add the average number of sentences and total token counts passed to the LLM per configuration. Without controlling for input length, conclusions about the superiority of particular δ/λ settings are hard to generalize.
- Table 5: The community statistics are good diagnostics for graph structure, but they do not yet demonstrate that the model exploits multi-hop information causally. Consider adding an analysis of retrieved paths supporting decisions.

## Potentially Missing Related Work
1) Peng et al., “Graph Retrieval-Augmented Generation: A Survey,” 2024 — Provides a taxonomy of GraphRAG, including community/subgraph retrieval and graph-enhanced prompting. It should be discussed in Related Work to position CommunityKG-RAG among existing indexing and retrieval strategies and to guide stronger baselines.

2) Khaliq et al., “RAGAR, Your Falsehood Radar: RAG-Augmented Reasoning for Political Fact-Checking using Multimodal Large Language Models,” 2024 — A fact-checking pipeline with RAG-based reasoning strategies (Chain-of-RAG, Tree-of-RAG). Add to Related Work and, if possible, compare empirically or discuss differences in retrieval and reasoning modules.

3) Kolli et al., “Hybrid Fact-Checking that Integrates Knowledge Graphs, Large Language Models, and Search-Based Retrieval Agents Improves Interpretable Claim Verification,” 2025 — A modular system combining KG retrieval over DBpedia with web RAG fallback. Discuss as an alternative KG+RAG integration path; cite in Section 2 and compare conceptually in Section 6.

4) Zeng et al., “DA-RAG: Dynamic Attributed Community Search for Retrieval-Augmented Generation,” 2026 — Formulates community retrieval as query-aware attributed community search. Highly relevant to your community selection step; cite in Section 2 and discuss differences versus your dot-product ranking and fixed Louvain communities.

5) Liu et al., “TruthfulRAG: Resolving Factual-level Conflicts in Retrieval-Augmented Generation with Knowledge Graphs,” 2026 — Proposes KG-based retrieval and conflict resolution. Add to Section 2 and discuss how your approach handles contradictory evidence compared to their explicit conflict modeling.

6) Chaudhary et al., “EZ-check: Explainable zero-shot knowledge extraction and fact checking using knowledge graphs,” 2026 — Zero-shot KG-centric fact-checking over ConceptNet with explainability. Include in Related Work to contrast retrieval units and explainability.

7) Hang et al., “TrumorGPT: Graph-Based Retrieval-Augmented Large Language Model for Fact-Checking,” 2025 — Domain-specific GraphRAG for health misinformation; discuss in Related Work and possibly in a broader-scope comparison.

8) Liu et al., “From vectors to knowledge graphs: A comprehensive analysis of modern retrieval-augmented generation architectures,” 2026 — Survey unifying vector, hybrid, and KG-based RAG. Useful for contextualizing your architectural choices in Section 2 and for identifying baseline families to include.

## Comments Suggestions And Typos
Actionable questions and suggestions that could change my assessment:
1) Splits and leakage
- Precisely describe the train/test split for KG construction and sentence pools. If the KG or candidate sentences include test articles, rebuild strictly from training articles and re-run Table 1–4. If the intent is to simulate a production scenario with a fixed corpus, then ensure claims used for evaluation are strictly unseen and that no label information or test meta-data leaks into index construction.

2) Strengthen baselines and control for token budgets
- Add BM25, DPR/Contriever, ColBERTv2, and a hybrid BM25+dense baseline. For KAPING and semantic retrieval, ensure the same maximum number of tokens is passed to the LLM as in CommunityKG-RAG for fair comparisons. Report avg evidence tokens per method per claim.

3) Specify the community-to-sentence algorithm and provide ablations
- Formalize how sentences are mapped to communities, including handling of sentences with entities from multiple communities, deduplication, conflicts, and ranking function r(M*_c, p). Include pseudo-code and release scripts where possible.
- Add an ablation where the same number of sentences is selected purely by SBERT similarity without using the graph, matching the token budget of CommunityKG-RAG_100^25.

4) Evidence-level analysis and multi-hop substantiation
- Beyond Table 5, measure performance on subsets requiring 1-hop vs multi-hop reasoning; show retrieval paths for a sample of correct vs incorrect cases.
- Provide per-class F1 and confusion matrices; include statistical significance tests over multiple random seeds or subsets.

5) Efficiency reporting
- Add retrieval latency and end-to-end response time, and plot accuracy vs tokens/latency to show efficiency trade-offs. The current best setting λ=100% may be impractical in resource-constrained scenarios; quantify this.

6) Embedding/Similarity choices
- Justify dot product vs cosine and the mixing of BERT for nodes vs SBERT for claims; consider using the same sentence encoder for both and compare.
- Explore simple graph-aware pooling (e.g., degree-weighted averages) or relation-type embeddings to enrich ϕ(m).

7) Broaden datasets
- Evaluate on at least one additional textual fact-checking dataset (e.g., FEVER, LIAR, SciFact). If the pipeline depends on REBEL trained on Wikipedia, discuss domain adaptation strategies and report cross-domain results.

Typos/clarity nits:
- Section 5.1: “More details are included in the Appendix A.” Consider summarizing key stats (already partly done) and ensure consistent counts for claims and label distributions.
- Section 5.3: “LLaMa27B” in Table 2 header is missing a space; use “LLaMa2 7B.” Similarly “LLaMa38B” should be “LLaMa3 8B.”
- Section 3: Notation “P_c = p_i^k” is nonstandard; define explicitly P_c = {top-k sentences for claim c}.
- Minor grammar: Several instances of missing commas and inconsistent capitalization of “Language Model(s)” and “Knowledge Graph(s).”

Criteria for raising my score:
- Clear, leakage-free experimental protocol and re-run of main results with stronger baselines under matched token budgets.
- Concrete algorithmic specification of community-to-sentence mapping and release of code or detailed pseudo-code enabling reproduction.
- Additional datasets and evidence-level analyses demonstrating that performance gains derive from multi-hop community structure rather than longer contexts alone.
- Efficiency analysis and significance testing.

## Confidence
3: Reasonably confident but not fully verified. I checked the main claims and experiments carefully, but some implementation details are underspecified, which could alter conclusions after clarification.

## Soundness
2.5: Between Poor and Acceptable. The idea is plausible and results are promising, but experimental design has gaps (baselines, leakage risk, token budget control), and key algorithmic details are missing.

## Excitement
2.5: Between potentially interesting and interesting. The direction is timely and relevant for GraphRAG/fact-checking, but the current empirical evidence and analysis are not yet compelling for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The approach is on-topic and interesting, with encouraging results and a clear system narrative (Figure 2), but the evaluation lacks strong baselines and clear leakage-free protocol, and several algorithmic details are missing. With the suggested revisions and expanded experiments, this could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The Limitations section acknowledges computational overhead and dependency on entity recognition quality. This is appropriate, but the paper could further discuss:
  - Risks of propagating biases and errors from relation extraction into retrieval and final judgments.
  - Potential misuse in automated content moderation; false positives could suppress legitimate speech, while false negatives could amplify misinformation.
  - Under-representation of non-Wikipedia domains if REBEL and the entity linker are biased toward Wikipedia styles.
  - The need for human-in-the-loop guardrails when deploying automated fact-checking systems.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3: Reproducible with difficulty. Many components are described, but crucial implementation details, mapping logic, and strict dataset split handling are missing; no code link is provided.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.