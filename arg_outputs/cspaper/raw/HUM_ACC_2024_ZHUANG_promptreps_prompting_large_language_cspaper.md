# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper proposes PromptReps, a zero-shot document retrieval approach that prompts a generative LLM to produce both dense and sparse representations from a single forward pass. The dense vector is the last-layer hidden state of the last input token under a one-word (EOL) prompt, and the sparse vector comes from the next-token logits, pruned and transformed using a SPLADE-style pipeline over document vocabulary terms. The method builds hybrid indices that combine ANN-based dense retrieval and inverted-index sparse retrieval, with linear score interpolation at query time. Experiments on MS MARCO, TREC Deep Learning 2019/2020, and BEIR show that hybrid PromptReps can match or surpass strong unsupervised embedding baselines (e.g., E5-PT_large) without any contrastive training, especially with larger LLMs (Llama3-70B). The paper also studies prompt sensitivity and alternative representation variants (first-word, multi-token, multi-representation with ColBERT-style scoring).

## Summary Of Strengths
- Conceptual simplicity with a clear mechanism: use a single EOL-style prompt to make the LLM select a “representative word,” then (i) take the last hidden state as a dense embedding and (ii) use next-token logits, restricted to document tokens and sparsified via SPLADE-like transforms, as a sparse representation. The hybrid yields strong performance without any training.
- Effective and well-motivated hybridization: The method acknowledges known robustness of sparse signals and complements less stable dense signals from decoder-only LLMs in zero-shot settings. The hybrid improvements are consistent across datasets and model scales.
- Thorough evaluation across benchmarks and ablations:
  - Table 1 (BEIR): shows that PromptReps hybrid with Llama3-70B-Instruct exceeds E5-PT_large average nDCG@10 (45.88 vs. 44.61) and further improves with +BM25 (50.60).
  - Table 3 and Table 4: prompt sensitivity and multiple LLMs are carefully tested; the importance of “The word is: ” and “in a retrieval task” is convincingly demonstrated.
  - Figures 3–5: alternative representation strategies are examined, with clear conclusions about trade-offs and efficacy.
- Insightful scaling observation: Figure 2 shows consistent hybrid gains with larger LLMs, and instruction-tuned variants outperform non-instruction-tuned ones for 8B models. This is practically useful for practitioners deciding which base LLMs to deploy.
- Practical indexing recipe and IR engineering details: SPLADE-like ReLU/log-saturation, top-128 truncation, and quantization stabilize and sparsify logits; exact-term alignment via restricting logits to tokens appearing in text is a smart and efficient step that fits standard inverted indices.
- Clear linkage between figures/tables and claims:
  - Figure 1 provides a concise architecture diagram mapping hidden states to ANN and logits to inverted index, clarifying the hybrid pipeline.
  - Figure 5 directly supports the conclusion that first-token single-representation is an adequate, efficient default, as multi-representation schemes do not consistently help on BEIR.

## Summary Of Weaknesses
1) Missing or limited baselines that are central to the paper’s positioning:
   - Table 1 compares to BM25, E5-PT_large, and LLM2Vec, but omits other closely related unsupervised/LLM-based retrievers mentioned in Related Work (e.g., HyDE; Contriever; Gecko distilled embeddings; E5-Mistral-Inst). Since PromptReps claims first-stage zero-shot retrieval without training, contrasting against HyDE (query-side generation) and Contriever (unsupervised contrastive) is important to calibrate novelty and robustness across BEIR tasks. Without these, the comparative story is narrower than it needs to be.
   - On MS MARCO/TREC DL, Table 4 also lacks HyDE and Contriever; including at least HyDE would better ground the claim that prompting alone can be competitive.
   Why it matters: The main claim is “no training yet full-corpus retrieval with competitive quality.” Readers need to see comparisons against the strongest non-trained or weakly-supervised LLM-aided retrievers to trust the outcome’s generality.

2) Fairness of comparisons and interpolation choices:
   - Table 1 includes a “+BM25” row only for Llama3-70B-Instruct PromptReps. If interpolation with BM25 is allowed, it should be offered to all methods that can be combined with BM25 (e.g., E5-PT_large + BM25) for a fair apples-to-apples comparison, or be clearly framed as an orthogonal fusion analysis. Otherwise it risks overstating advantages.
   - The hybrid fusion of dense+sparse within PromptReps uses equal weights after min-max normalization, but competing methods are not given the same two-channel fusion pathway. A standardized fusion protocol across systems would strengthen claims.

3) Efficiency and resource reporting are underdeveloped:
   - Section 8 qualitatively discusses latency but there is no quantitative runtime/latency or memory footprint analysis. The approach requires computing logits and a dense vector per query, plus running both ANN and inverted index. Measured query latency, throughput, GPU RAM, and index size overhead relative to BM25 and strong dense baselines would help substantiate the practicality claim.
   - Index-time costs for processing millions of documents with an LLM are not quantified; this matters for real deployments, even if it is one-time.

4) Sensitivity to tokenization and vocabulary biases:
   - The sparse vector is derived by restricting logits to tokens for words present in the lowercased document (Section 3, steps 1–2). The paper notes subword issues and explores multi-token representations later, but does not quantify how often key terms split into multiple subwords and how that affects retrieval quality. Figure 5 and Table 5 suggest first-word pooling can hurt, but a deeper analysis of tokenization effects on sparse term coverage, OOV handling, and multi-token matching would provide more confidence.
   - The lowercasing constraint is operationally important. Table 3 shows prompts with “Make sure your word is in lowercase” perform better (#6). It would help to establish whether this benefit comes primarily from the sparsification pipeline or from better term matching distributions, with a controlled ablation on the logits side (e.g., same prompt but no lowercasing of documents; or lowercase prompt but mixed-case indexing).

5) Limited analysis of the dense component’s instability:
   - The dense-only variant underperforms on some models (e.g., Mistral-7B-Instruct in Table 4 and Figure 2). The paper stops at observation. A deeper diagnosis, e.g., probing similarity structure, layer selection sensitivity, or head/MLP contribution, would clarify when hidden-state embeddings from decoder LLMs are reliable.

6) Prompt design scope is narrow relative to the space:
   - Table 2 explores six closely related prompts, and Table 3/4 show effects. Given the centrality of prompting for both dense and sparse signals, exploring few-shot variants, format changes (system vs. user priming), or different task phrasings could reveal further gains. The Conclusion hints at this but the main text could include at least one demonstration beyond EOL to ground the claim.

7) Scoring protocol details and choices could be more transparent:
   - Dense and sparse scores are min-max normalized and linearly interpolated “with equal weights.” Are weights tuned on MS MARCO/TREC DL and then held fixed on BEIR? If so, please state explicitly. If not tuned, justify 50–50. Also, clarify per-query vs. global normalization, and whether normalization pools only retrieved candidates per channel or the entire corpus score distribution.
   - For ANN, FAISS configuration is under-specified (index type, training samples, PQ or HNSW parameters). Since small ANN choices can alter recall vs. latency, basic parameters should be included.

8) Missing reporting on robustness and failure cases:
   - The method relies on representative tokens; how does it behave for very short or noisy queries, non-English content in BEIR, or domains with high OOV rates? A small qualitative section analyzing failure modes would make the claims more actionable.

9) Figure-specific critique:
   - Figure 2 clearly shows the hybrid impact across models on MS MARCO MRR@10, and strongly supports the scaling argument. However, a dashed BM25 reference line is visible but not explicitly labeled in the caption, and the y-axis scale is tight; adding numeric labels would ease interpretability.
   - Figure 5 aggregates BEIR hybrid nDCG@10 across representation variants. It convincingly supports the claim that first-token single-representation is a strong default. Still, the figure would benefit from including average bars with error bars, or marking statistically significant wins.

10) Table-specific critique:
   - Table 1 is central and compelling, but the heading “Unsup Contrastive training” column grouping is unclear. Columns for E5-PT_large and LLM2Vec sit under it, while PromptReps has dense/sparse/hybrid. Clarify headers so readers do not misinterpret model classes. Also, consider adding HyDE/Contriever/Gecko where possible to strengthen completeness.

Collectively, these issues are addressable, but several (fairness, baselines, and efficiency reporting) are non-trivial and would strengthen the paper’s case for the main track.

## Potentially Missing Related Work
1) Li et al., “Pseudo-Relevance Feedback Can Improve Zero-Shot LLM-Based Dense Retrieval,” 2025 — Direct extension of zero-shot LLM retrievers using PRF to refine query embeddings. Discuss in Section 6 as a complementary enhancement to PromptReps’ prompting; consider as a baseline on at least one dataset, or position as future integration.
2) Li et al., “LLM-VPRF: Large Language Model Based Vector Pseudo Relevance Feedback,” 2025 — Vector-based PRF tailored to LLM-based dense retrievers. Discuss in Related Work Section 2.2 and 2.3, and mention in Conclusion as a natural augmentation to the proposed hybrid method.
3) Deng et al., “Following the Autoregressive Nature of LLM Embeddings via Compression and Alignment,” 2025 — Proposes alignment of embeddings with the generative next-token objective, highly relevant to PromptReps’ use of last hidden states and logits. Compare conceptually in Section 2.2 and discuss as an alternative to prompting-only solutions.
4) Schlatt et al., “TITE: Token-Independent Text Encoder for Information Retrieval,” 2025 — Presents an efficient single-vector IR encoder; useful foil to PromptReps’ dense component. Mention in Related Work and consider as an additional dense baseline or discussion point.
5) Xu et al., “ComLQ: Benchmarking Complex Logical Queries in Information Retrieval,” 2026 — A challenging IR benchmark for compositional queries. Add to future work in Section 7 to test PromptReps under harder logical constraints.
6) DiffRetriever: “Parallel Representative Tokens for Retrieval with Diffusion Language Models,” 2026 — Conceptually close via representative tokens but with a diffusion backbone. Discuss briefly in Section 6/7 as an alternative generative mechanism and a direction for comparison or fusion.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Baseline completeness and fairness:
  - Please add or discuss results for HyDE and Contriever on BEIR, and, if available, Gecko or E5-Mistral-Inst. If compute is prohibitive, a subset of BEIR would still be informative. Also include BM25 interpolation for E5-PT_large in Table 1 or, at minimum, clarify that “+BM25” is an orthogonal fusion analysis, not a head-to-head comparison.
- Efficiency reporting:
  - Provide quantitative latency (per-query) and throughput under a standard hardware setting for: BM25, PromptReps sparse-only, dense-only, and hybrid. Report ANN parameters and index sizes for both dense and sparse indexes. Similarly, quantify the offline indexing cost for large corpora.
- Scoring/normalization transparency:
  - Specify whether fusion weights and min-max normalization ranges are tuned on MS MARCO/TREC DL and then fixed for BEIR. Clarify per-query vs. corpus-level normalization and candidate set on which min-max is computed.
- Tokenization and OOV analysis:
  - Add a diagnostic showing the proportion of words split into multiple sub-tokens and how often the top representative token is a subword vs. whole word. Consider reporting retrieval deltas when retaining all sub-tokens vs. only the first token in the sparse map.
- Broaden prompt exploration minimally:
  - Include a small few-shot or meta-task prompt variant (even on a subset) to empirically validate the promise stated in the Conclusion.

Typos and minor issues:
- Figure 2: The caption could mention explicitly that the dashed line indicates BM25 MRR@10 for readability.
- Section 3: “which is often refers to as ‘logits’” → “which is often referred to as ‘logits’”.
- Table 1 header: “-BM25” is ambiguous; consider “BM25 (no interpolation)” or similar. Also rework the “Unsup Contrastive training” header to make grouping unambiguous.
- Section 5.2: “The results demonstrate that PromptReps can achieve a similar level of retrieval effectiveness as BM25 and surpass LLM2Vec with most of the prompts.” Consider qualifying with dataset/task where exceptions occur.

Criteria that could raise my score:
- Add at least one of HyDE/Contriever/Gecko results on BEIR or MS MARCO/TREC DL and clarify fusion fairness against E5-PT_large.
- Include end-to-end efficiency and index size measurements, with ANN configuration details.
- Add a tokenization/OOV diagnostic and one additional prompt variant beyond EOL.

## Confidence
4: Quite sure after careful checking — I checked the key results, figures, and methods carefully; some implementation details are not fully specified, but my evaluation is unlikely to change dramatically.

## Soundness
3.5: Between Acceptable and Strong — The empirical evidence supports the main claims; however, missing strong baselines and limited efficiency reporting prevent a higher score.

## Excitement
3.5: Between interesting and exciting — Simple, clever use of logits and hidden states with consistent hybrid gains, and practical implications if efficiency holds.

## Overall Assessment
4: Conference — Solid contribution suitable for ACL main. The paper offers a clear and well-executed idea that removes training while enabling first-stage retrieval, with convincing hybrid results and ablations. To further strengthen, add stronger baselines, clarify fusion fairness, and report efficiency.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper’s Limitations section candidly notes latency due to longer prompts and the cost of running both dense and sparse retrieval; this should be complemented by quantitative measurements.
- Ethical considerations appropriately recognize compute- and water-related impacts of LLM inference at scale, and the potential for biased representations. I recommend adding:
  - An explicit note on potential retrieval harms from biased sparse logits (e.g., topical overexposure), and a brief plan to audit top-terms distributions across demographic or sensitive topics.
  - Discussion of multilingual and non-English content in BEIR-like corpora, where case normalization and tokenization choices may disadvantage certain languages or scripts.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Code link is provided; the method description is generally clear. Add missing FAISS index details, scoring normalization scope, and exact sparsification thresholds to reach 5.

## Datasets
1: No usable datasets submitted.

## Software
4: Useful — The released code appears positioned to reproduce results and be adapted as a baseline. Adding scripts for index-time and query-time profiling would increase utility.