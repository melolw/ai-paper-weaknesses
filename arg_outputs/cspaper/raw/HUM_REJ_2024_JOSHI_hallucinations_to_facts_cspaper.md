# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper targets hallucination mitigation in language models using knowledge graphs, squarely within NLP topics such as Generation, Resources and Evaluation, and Dialogue and Interactive Systems.

## Minimum Quality
Pass ✅. The submission contains Abstract, Introduction, Related Work, Methodology, Experimental Setup, Results, Conclusion, Ethics/Limitations, and References. However, there are substantial issues in soundness and evaluation rigor that should be addressed during review rather than desk rejection.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I found no hidden prompts or manipulative instructions in the provided content.

# Expected Review Outcome:

## Paper Summary
The paper proposes mitigating language model hallucinations by integrating curated knowledge graph (KG) triples into in-context prompts (an in-context RAG approach). The KG focuses on environmental sustainability, sourced from Wikipedia; topics and subtopics are filtered using BERT-based similarity, then triples are created with a hand-curated set of 46 relations and a bias toward numeric/statistical tails. At inference, relevant triples are retrieved via embedding similarity (Equation 1), converted to sentences (Equation 3), and appended to the model’s response (Equation 4). Experiments compare several LMs (GPT-2, GODEL, Llama2, ChatGPT) using a suite of general NLG metrics and limited human evaluation; a FacTool score is also reported.

## Summary Of Strengths
- Problem focus: Attempts to directly tackle factual hallucination with explicit grounding, a highly relevant topic for ACL.
- Resource construction effort: Describes a pipeline to extract sustainability topics from Wikipedia, filter with embeddings, and build a KG using a custom relation schema. Figure 2 communicates a high-level flow of the KG creation, which helps readers follow the data path from text to extracted triples.
- Emphasis on numerical/statistical tails: Prioritizing triples with numeric facts is a reasonable heuristic to reduce vague-generation hallucinations; the tail-entity examples in Section 3.3 clarify the intended flavor of factual grounding.
- Simple, interpretable pipeline: The retrieval and triple-to-sentence conversion are straightforward and could be adopted by practitioners. Equations (1)–(4) correctly formalize the very high-level matching and insertion operations.
- Qualitative demonstrations: Table 1 and Table 4 provide concrete, human-readable cases where claimed incorrect outputs are contrasted against grounded responses, which helps illustrate the intended behavior.

## Summary Of Weaknesses
1) Core evaluation design does not test the proposed method
- Table 2 reports BLEU-1/METEOR/ROUGE-L/CIDEr/SPICE/STCS/EACS/VECS/GMS across GPT-2/GODEL/Llama2/ChatGPT, but it is unclear whether these numbers reflect baseline models, models augmented with the proposed KG, or both. There is no controlled comparison “w/ KG vs w/o KG” on the same prompts and outputs. As written (Pages 6–7), Table 2 reads like a generic model leaderboard that does not isolate the contribution of the proposed grounding method.
- The automatic metrics in Table 2 are general text-similarity measures and are not appropriate proxies for factuality/hallucination. There is no demonstration that improvements in, say, ROUGE-L or CIDEr correspond to reduced hallucination.

2) Weak hallucination-specific evaluation
- Hallucination is the central claim, yet only a single FacTool number is reported (Page 7), with minimal detail: no dataset size, no prompt distribution, no confidence intervals, and no per-model or per-method breakdown. The reported improvement (0.87 vs 0.81) is small and lacks statistical testing; we do not know variance or robustness.
- Human evaluation (Table 3) conflates dimensions and methods. FC1, FC-RAG, FC-IC, FC-CoT are scored, but the task setup is underspecified. For example, how were prompts constructed? Were the human judges blinded to the method? Were the same prompts used across models? What constitutes a factual error and what evidence was required? Page 7 says “100 scenarios” but there is no protocol sufficient to reproduce. The reported inter-annotator agreement in Appendix B stops short of category-specific agreement for factuality.

3) KG construction and quality are under-specified
- Section 3 lacks critical details: which embedding model(s) are used for topic filtering and for triple retrieval (Section 4.1)? What values of k in Equation (2)? What is the total KG size, coverage, and statistics per relation? Beyond Figure 2’s schematic, there is no rigorous audit of triple correctness, noise rates, or inter-annotator validation.
- Relation set design: The list in Section 3.2 and Table 5 contains duplicates and inconsistencies. “HasImpact” appears twice (Page 4 and Page 14), “HasPercentile-Value” (Table 4) is inconsistent with “HasPercentileValue” (Section 3.2), and “Volume10” in Table 4 appears to be a typo for “VolumeOf.” Such inconsistencies cast doubt on the reliability of the relation schema and its implementation.
- Provenance and verifiability: Many sample triples and numeric tails are given without sources. Since the KG is sourced from Wikipedia, one would expect page anchors or revision IDs. The pipeline admits LLM-generated triples (Page 5), which risks fabricating facts unless rigorously verified.

4) Triple generation via LLMs without verification
- Section 3.5 states that triples were “experimented” using Llama2 and ChatGPT prompts to create triples. Without a fact-checking and de-duplication pipeline, this risks introducing hallucinations into the KG itself. No audit or error analysis of LLM-created triples is provided.

5) Methodological clarity issues in the proposed algorithm
- Equation (4) uses a simple concatenation RLM(C) + {Si}. There is no decoding or re-ranking that ensures the model adheres to the facts rather than ignoring or contradicting them. There is no mechanism preventing conflicts between RLM(C) and the appended sentences.
- The retrieval units are “triples,” but embedding how a triple is represented is not described. Is the triple embedded as “subject [SEP] relation [SEP] object”? Is the embedding model shared with context embedding? Without details, retrieval reproducibility and quality are questionable.

6) Figures and tables contain factual or internal contradictions
- Figure 1 shows a conversation where the agent claims “up to 20 gallons of water per day” savings from shorter showers and asserts the “actual value is 8 gallons... on average.” No source is provided. This undermines the example’s evidentiary value for hallucination, because both numbers could be context-dependent.
- Table 4 has multiple problematic entries:
  - For the bioenergy dialogue, the KG triple is listed as [Bioenergy, HasPercentileValue, 15.1% to 20/0’], which seems malformed (“20/0”). The agent later says 13.1% by 2030 without citation. The connection between the malformed triple and agent response is unclear.
  - For the low-carbon electricity dialogue, the KG triple asserts 40% of global electricity in 2020, which stands at odds with the narrative immediately before and risks being factually wrong. The paper does not provide references or a verification log.
- Table 1 mixes edits that read more like stylistic strengthening than factual grounding. For instance, the metering case converts a general statement into a prescriptive one with a repeated percentage, but it is not clear that the triple itself is sourced, nor how conflicts are handled if multiple triples apply.

7) Missing strong baselines and comparisons
- No comparison is made to alternative KG-grounding mechanisms (e.g., decoding-time constraints, KG embedding fusion) or to strong retrieval-grounded text systems. There is no ablation showing the impact of each component (retrieval, triple-to-sentence conversion, number of triples k, or relation subsets).
- There is no assessment of sensitivity to retrieval quality, embedded model choice, or noisy triples. No analysis on failure modes (e.g., retrieving partially relevant but misleading statistics).

8) Literature coverage is incomplete
- The Related Work section focuses primarily on general LLM hallucination commentary and RAG/CoT/ICL. Directly related recent KG-based hallucination works and evaluation frameworks are not cited or compared. See “Potentially Missing Related Work.”

9) Reproducibility concerns
- The KG, code, prompts, and data splits are not released; Appendix C gives general prompts but not enough to reconstruct the KG or experiments. The Ethics section (Page 9) implies on-demand access only, which is insufficient for ARR/ACL reproducibility norms.
- Experimental details are sparse for how Table 2 and Table 3 were computed. Appendix A provides hardware and some training details for fine-tuning GPT2/GODEL/Llama2 but does not connect them to the main results in a way that would allow reproduction of the reported numbers.

10) Claim overreach
- The paper concludes that the approach reduces hallucinations (Page 8), but the primary quantitative evidence is general NLG metrics (Table 2) and a single FacTool delta without confidence or dataset grounding. The qualitative examples contain typos and inconsistent facts, weakening the central claim.

## Potentially Missing Related Work
1) Guan et al., “Mitigating Large Language Model Hallucinations via Autonomous Knowledge Graph-Based Retrofitting,” AAAI 2024 — Directly targets hallucinations using external KGs post-generation. Should be discussed in Section 2 and considered as a post-processing baseline; compare effectiveness with your in-context triple insertion.

2) Shi et al., “Hallucination Mitigation in Natural Language Generation from Large-Scale Open-Domain Knowledge Graphs,” 2023 — Presents graph-to-text with hallucination control. Discuss in Related Work (Section 2) and clarify how your triple selection and grounding differ; consider evaluation alignment.

3) Sansford et al., “GraphEval: A Knowledge-Graph Based LLM Hallucination Evaluation Framework,” 2024 — Converts outputs to KG triples and checks with NLI. Add to Section 5.2 as a complementary evaluation to FacTool and consider reporting triple-level hallucination localization.

4) Hron et al., “Training Language Models on the Knowledge Graph: Insights on Hallucinations and Their Detectability,” 2024 — Studies hallucinations when training directly on KG triplets. Discuss in Section 2 to position your inference-time approach versus KG-based training.

5) Chekalina et al., “Addressing Hallucinations in Language Models with Knowledge Graph Embeddings as an Additional Modality,” 2024 — Adds KG embeddings via adapters to improve factuality. Compare architectures in Section 4 and consider as a baseline or ablation (embedding-level fusion vs text-level triple insertion).

6) Luo et al., “Graph-constrained Reasoning: Faithful Reasoning on Knowledge Graphs with Large Language Models,” 2024 — Constrains decoding with KG structure. Discuss as an alternative to in-context KG prompting in Section 4; contrast expected fidelity and coverage.

7) Semnani et al., “WikiChat: Stopping the Hallucination of Large Language Model Chatbots by Few-Shot Grounding on Wikipedia,” 2023 — A strong grounding pipeline using Wikipedia evidence (not explicit KG) with high factuality. Include in Related Work and consider as a retrieval-text baseline, especially since your KG is derived from Wikipedia.

8) Lavrinovics et al., “Knowledge Graphs, Large Language Models, and Hallucinations: An NLP Perspective,” 2025 — A survey framing KG-based hallucination mitigation. Cite in Section 2 to situate your contribution within the broader taxonomy of KG integration strategies.

9) Amayuelas et al., “Grounding LLM Reasoning with Knowledge Graphs,” 2025 — Grounds CoT/TOT/GoT steps in KGs. Discuss in Section 2 and contrast to your use of chain-of-thought in Table 3; consider integrating KG-grounded reasoning as an ablation.

## Comments Suggestions And Typos
Actionable suggestions:
- Evaluation redesign
  - Provide a hallucination-focused benchmark with transparent prompts, references, and labeling guidelines. For each model, report factuality before/after KG grounding with confidence intervals and per-category breakdown (numeric claims, entity-attribute, temporal facts). If using FacTool, report variance over multiple runs and present per-claim analysis.
  - Replace or complement Table 2 with metrics that measure factuality (e.g., FactScore, triple-level correctness via a GraphEval-style pipeline, or human factuality with explicit evidence rating). If you keep Table 2, add paired comparisons to show the effect of KG grounding on the same prompts.
  - In Table 3, separate methods rows (w/o KG, w/ KG-in-context, w/ RAG text retrieval, w/ CoT) and keep the model fixed to isolate method effects. Clarify blinding, randomization, and detailed rubric with examples. Report inter-annotator agreement specifically for factuality.

- Resource and method clarity
  - Specify the exact embedding models for topic filtering and for retrieval (Section 4.1), triple representation for embeddings, the value of k in Equation (2), and tie-breaking for near neighbors.
  - Provide KG statistics: number of entities, relations, triples; per-relation counts; % numeric tails; % sourced vs LLM-generated; error rates from manual auditing.
  - Implement and document a triple verification step with citations to Wikipedia page URLs and revision IDs; flag numeric ranges and uncertainty properly.

- Baselines and ablations
  - Add baselines: (a) Wikipedia text-only RAG, (b) KG-embedding fusion (adapter-based), (c) decoding constraints over KG, (d) post-generation KG retrofitting. Add ablations on number of triples, confidence thresholds, and triple sentence placement.
  - Report cases where retrieved triples are wrong or partially relevant and analyze impact.

- Figures and tables
  - Figure 1: provide a citation for the “8 gallons” claim or replace with an example drawn from your KG with a linkable source.
  - Table 4: fix malformed triples (“15.1% to 20/0,” “Volume10”) and ensure all numbers link to verifiable sources. If numbers differ across sources/years, reflect uncertainty rather than assert corrections.
  - Table 2: explicitly state whether numbers are for baseline or grounded outputs. If for generic NLG quality only, move to appendix and lead with hallucination metrics in the main paper.

- Release and reproducibility
  - Release code, KG, prompts, and evaluation scripts under anonymization where needed. On-demand access is not sufficient for ARR. A public artifact will substantially improve the paper’s impact and credibility.

Typos and inconsistencies (non-exhaustive):
- Section 3.2: “HasImpact” listed twice; consolidate.
- Section 3.3: “such as up to, approximately, on average, can save” — consider formalizing as pattern list; current phrasing is informal.
- Section 3.5: “We experimented with the triples creation process using 2 LLMs” — clarify whether those triples were actually included in the final KG and how verified.
- Table 4: “HasPercentile-Value” vs “HasPercentileValue”; “Volume10” vs “VolumeOf”; “15.1% to 20/0” is invalid; “Dialogue on Environmental Sustainability Topics showcasing ... generated by us” — standardize tense and grammar.
- Page 5: “BERTScore (Zhang et al., 2019)” is cited for relation extraction by similarity matching; BERTScore is a text similarity metric for generation evaluation, not a standard relation extractor. Clarify the exact role and model.

Criteria to shift my score upward during rebuttal:
- Provide a rigorous, hallucination-focused evaluation with transparent datasets, clear protocols, and statistically sound comparisons “with vs without KG grounding” on the same LM and prompts.
- Release the KG and code with detailed documentation, or provide a strong commitment and anonymized link during rebuttal.
- Fix all Table 4 issues, add sources to all numeric claims, and run an audit demonstrating KG accuracy.
- Add strong baselines (text RAG, KG-embedding fusion, decoding constraints, retrofitting) and demonstrate competitive or superior factuality under fair conditions.

## Confidence
3: Reasonably confident but not fully verified. I carefully examined the paper and figures/tables, but the missing implementation details and dataset opacity limit full verification.

## Soundness
2.5: Between Poor and Acceptable. The core idea is plausible, but the evaluation is misaligned with the main claim, key details are missing, and several tables/figures contain inconsistencies that undermine the conclusions.

## Excitement
2.5: Between potentially interesting and interesting. The topic is important and the general idea has practitioner appeal, but the current execution and evidence are not strong enough to be exciting.

## Overall Assessment
2: Resubmit next cycle. The paper needs substantial revisions that can be completed by the next ARR cycle. Key reasons: evaluation does not isolate the method’s effect on hallucination, important baselines and ablations are missing, and several factual inconsistencies/typos exist in the presented examples and relation schema.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper’s Limitations section acknowledges constrained coverage and potential biases from curated KGs, which is appreciated. Missing, however, are: explicit discussion of what happens when the KG is incorrect or out-of-date, policies for updating facts, and the risk of presenting KG-derived numbers without uncertainty bounds. Given the focus on environmental policy-relevant statistics, incorrect grounding could misinform users. I recommend: (a) explicit provenance and timestamps per triple, (b) uncertainty-aware phrasing in generation, (c) a fallback policy when retrieved triples conflict, and (d) assessment of domain bias due to Wikipedia sourcing.

## Ethical concerns
None beyond the need for transparent sourcing and careful handling of factual claims. The “on-demand” resource sharing is not sufficient for reproducibility and accountability; public anonymized release is preferred.

## Needs Ethics Review
No.

## Reproducibility
2.5: Reproducible with difficulty. Important details (embedding models, retrieval configs, datasets, prompts, KG artifacts) are missing or not publicly available.

## Datasets
2: Documentary. The KG could be useful, but without release and verification, its value is limited.

## Software
2: Documentary. If released with retrieval and evaluation scripts, it could become more useful; currently unclear.