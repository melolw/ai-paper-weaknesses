# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies the tradeoff between general-purpose multimodal LLMs and fine-tuned, task-specific systems for multimodal multi-hop question answering on the WebQA benchmark. The authors:
- Propose MH-VoLTA, a VoLTA-based classifier with a Fusion-in-Decoder-style multi-hop fusion that accepts a variable number of image sources (by padding single-image inputs).
- Compare three settings for Retrieval+QA: (i) fully fine-tuned retriever and QA (UniVL-DR + MH-VoLTA), (ii) in-context RALM (external retriever + GPT-4o for QA), and (iii) in-context “RLM” (GPT-4o performs both retrieval from provided candidates and QA).
- Report that GPT-4o achieves strong results and show a dependency of GPT-4o’s QA on retrieving correct sources (Figures 3a–b). They analyze how question complexity interacts with retrieval and QA performance (Figures 4–5).
- Claim GPT-4o achieves state-of-the-art accuracy on WebQA test via leaderboard submission and that fine-tuned models are preferable in closed-domain or higher-complexity settings.

## Summary Of Strengths
- Clear motivation and useful comparative framing: the paper asks when to prefer zero-shot multimodal LLM prompting versus fine-tuned specialized architectures for multimodal multi-hop QA.
- Methodological contribution: MH-VoLTA extends VoLTA with a FiD-inspired multi-hop fusion while handling single- and two-image cases consistently. Figure 2 gives a reasonably clear architectural overview of per-source individual fusion followed by concatenation and classification.
- Comprehensive end-to-end comparisons on WebQA’s image subsets: Table 2 contrasts multiple combinations of retrieval and QA, including oracle retrieval, and demonstrates how retrieval quality affects QA.
- Empirical findings are interesting for practitioners: 
  - GPT-4o can act as an in-context retriever; Figure 3(a) shows QA accuracy is high when recall is high, and low otherwise, suggesting limited reliance on parametric memory in this setting.
  - Complexity analysis (Figures 4–5) surfaces a nontrivial pattern: increased question complexity improves in-context retrieval but can degrade GPT-4o QA; fine-tuned systems are more robust to complexity.
- Explicit figure- and table-supported insights:
  - Table 1 robustly motivates the model choices for subsequent experiments by showing MH-VoLTA outperforming several baselines and GPT-4o outperforming other general LLM/VLM baselines on validation image questions.
  - Table 2 makes the retrieval–QA interaction concrete: gold retrieval raises GPT-4o QA accuracy from 0.53 to 0.56 on Val, and the fully fine-tuned pipeline (FT, FT) leads the Val image subset with Acc=0.69.
  - Figure 3(b) quantifies the QA drop as the number of distractors increases, reinforcing the paper’s central message about retrieval sensitivity.

## Summary Of Weaknesses
1) Limited novelty and positioning of MH-VoLTA.  
- While the FiD-style concatenation for multi-hop fusion is sensible, the design seems a direct adaptation of known FiD ideas (Section 4.2, Eq. 3) with VoLTA encoders and padding for single-image cases. The claim of “first application of FiD that works with a variable number of inputs” (Page 2) is not convincingly justified given prior FiD variants that work with variable passages in text QA and existing multi-image FiD-style VQA (Figure 1, Tanaka et al.). The novelty rests on rather incremental engineering without a deeper analysis or ablations that isolate what MH-VoLTA contributes over standard FiD-style designs.

2) Scope of evaluation is constrained and mixed.  
- The fine-tuned classifier only targets image-based categories with constrained vocabularies (Section 3), ignoring the text and mixed-modality parts of WebQA that are central to “multimodal, open-domain” claims. This makes the “closed-domain vs open-domain” comparison asymmetrical, weakening generalization of conclusions to the whole benchmark.  
- The results emphasize the image subsets and drop “choose” questions, further narrowing scope. This is acceptable if positioned as a focused VQA study, but the framing repeatedly generalizes to “multimodal retrieval and QA on WebQA.”

3) Ambiguity and inconsistencies in experimental reporting.  
- Table 2 has unclear entries: the “Test | GPT-4o | GPT” and “Test | FT | GPT” rows are ambiguous about whether “GPT” is GPT-4o and whether retrieval is GPT-4o or FT. Several labels across the paper interchange “GPT-4” and “GPT-4o.”  
- The definition of retrieval “F1” is insufficiently specified: is this F1 over positive source IDs with a fixed candidate set size? How many candidates are shown to GPT-4o for ICR? How are distractors sampled and randomized across runs (Section 4.3 and A.1)?  
- For GPT-4o prompting, crucial details are missing: temperature, decoding settings, prompt variants and sensitivity, image input formatting (raw pixels vs URLs, resolution constraints), number of shots (zero-shot vs few-shot), and handling of multiple images. The “in one word” instruction in A.1 conflicts with multi-word class labels like “red orange” in color_set (Appendix A.4). How was exact matching done then?

4) Overreliance on a proprietary model and limited reproducibility.  
- The core positive results rely on GPT-4o. Without released code, prompts, and detailed prompting protocols, reproduction is unlikely. The fine-tuned system details are incomplete as well: LoRA is described (Eq. 2), but hyperparameters beyond r, α and “only attention weights” lack clarity, and training protocols are split between main text and Appendix A.3. No variance, seeds, or significance tests are reported. Reproducibility is therefore limited.

5) SoTA claims are under-substantiated and sometimes contradictory.  
- The paper states GPT-4o achieves SoTA on WebQA, and also that In-Context RLM outperforms In-Context RALM by 4.5% on the test set (Section 6.2). Yet, in validation experiments, the fully fine-tuned pipeline (FT, FT) has 0.69 Acc vs 0.56 for GPT-4o with gold retrieval (Table 2). The narrative oscillates between “GPT-4o is SoTA” and “specialized models win in closed domains,” but the paper does not reconcile dataset splits, coverage (image-only vs full WebQA), or differences in category distributions between Val and Test. A more transparent, like-for-like test-set comparison across the same subsets is needed to back a SoTA claim.

6) Limited ablations and diagnostic analysis for MH-VoLTA.  
- The classifier’s architecture choices are not well-justified quantitatively. There is no ablation on: number of FiD-fused layers, the padding strategy with blank images, influence of captions versus images, or swapping VoLTA with other encoders. Figure 6 in Appendix A.3 shows per-category accuracies for single vs multiple images, but there is no analysis on why certain categories gain from two images or how the classifier leverages cross-image attention.

7) Missing or incomplete baseline coverage.  
- Baselines are mostly classic (VLP, GIT, BLIP-2). There is no comparison against more recent multimodal RAG pipelines, multi-turn retrieval, or agentic tool-use methods on WebQA. This gap is especially problematic given the paper’s central question about general LLM prompting versus specialized RAG systems.

8) Methodological clarity around candidate pools and distractors.  
- For ICR, WebQA provides a fixed set of distractors per question, but the paper does not clearly state the candidate pool size and whether it is controlled identically across different systems. Figure 3(b) shows QA accuracy vs number of retrieved distractors, but it is unclear how this “number of distractors retrieved” is operationalized and whether the pool size varies across questions or models.

9) Statistical rigor and uncertainty reporting are lacking.  
- No confidence intervals or significance tests accompany Table 1 or Table 2. Given the small margins in some rows (e.g., 0.69 vs 0.71), the absence of statistical analysis weakens the strength of claims.

10) Presentation issues and typos that cause confusion.  
- “In-Content RLM” vs “In-Context RLM” is inconsistent (Page 2).  
- “MH-VoLTA fairs better” should be “fares better” (Page 7).  
- Equation (3) formatting is awkward; the intended concatenation could be clearer.  
- Some figure references in Appendix A.3 (“The results presented in 6(b) demonstrate …”) clash with the main text numbering style and create reading friction.

How these weaknesses affect the paper’s value: together, they undermine the strength and generality of the conclusions, limit reproducibility, and leave the community without a fully convincing, apples-to-apples SoTA comparison. The central message is interesting and relevant, but the experimental design and reporting need to be tightened, the baseline landscape broadened, and the methodology documented to ACL standards.

## Potentially Missing Related Work
1) Yang et al., Progressive Evidence Refinement for Open-domain Multimodal Retrieval Question Answering, 2023 — directly targets multi-hop multimodal retrieval on WebQA with iterative retrieval and evidence refinement; should be discussed in Section 2 and compared experimentally in Section 6, ideally as a retrieval+QA baseline in Table 2.

2) Rajabzadeh et al., Multimodal Multi-Hop Question Answering Through a Conversation Between Tools and Efficiently Finetuned Large Language Models, 2023 — LLM orchestrating tools for multimodal multi-hop QA; relevant to the paper’s general-versus-specialized theme. Cite in Section 2 and discuss as an alternative to in-context-only GPT-4o; consider as a baseline if feasible.

3) Bai et al., RAMQA: A Unified Framework for Retrieval-Augmented Multi-Modal Question Answering, 2025 — unified multimodal RAG with learned ranker and LLM reranker; should be positioned in Section 2 as a current SoTA-style pipeline and, if possible, contrasted in Table 2 or the test-set leaderboard discussion.

4) Carragher et al., Quantifying Memorization and Retriever Performance in Retrieval-Augmented Vision-Language Models, 2025 — analyzes memorization vs retrieval in multimodal RAG; highly relevant to claims in Figures 3(a)–(b). Add to Section 2 and connect to the dependency analysis in Section 6.3.

5) Liao et al., Global Question-Aware Multimodal Retrieval-Augmented Generation for Multimedia Multi-Hop QA, 2025 — strong global question-aware retriever; include in Section 2 and, if possible, compare or discuss in Section 6 to better support SoTA claims.

6) Wasserman et al., DocReRank: Single-Page Hard Negative Query Generation for Training Multi-Modal RAG Rerankers, 2025 — hard-negative reranking for multimodal RAG; relevant to the distractor sensitivity in Figure 3(b). Discuss in Section 2 and consider implications in Section 7 for mitigating distractor effects.

7) Yang et al., Evidence-chain-driven Multimodal Retrieval Question Answering, 2026 — explicit modeling of direct/indirect evidence chains on WebQA; add to Section 2 and relate to the paper’s multi-hop reasoning framing, possibly as a retrieval baseline or diagnostic comparator.

8) You et al., AgenticRAGTracer: A Hop-Aware Benchmark for Diagnosing Multi-Step Retrieval Reasoning in Agentic RAG, 2026 — diagnostic benchmark for multi-step retrieval; discuss in Section 7 as relevant for deeper failure analysis beyond Figures 3–5.

## Comments Suggestions And Typos
Actionable suggestions that could change my evaluation:
1) Clarify evaluation protocols and fix inconsistencies.  
- Precisely define retrieval F1, candidate pool sizes, and the number and selection of distractors per question across systems. For ICR, state how many candidates GPT-4o sees, in what order, with what randomization, and whether multiple trials are averaged.  
- Disambiguate Table 2 labels (e.g., “Test | GPT-4o | GPT”): spell out the exact retriever and QA model variants. Ensure consistent use of GPT-4o terminology.

2) Strengthen baseline coverage and SoTA claims.  
- Add or at least discuss recent multimodal RAG systems and multi-turn retrieval/tool-use methods on WebQA (see “Potentially Missing Related Work”). If running them is infeasible, provide a careful, category-matched comparison and a transparent leaderboard-based analysis that aligns subsets and avoids scope mismatches.

3) Improve reproducibility.  
- Release prompts, decoding parameters, and exact GPT-4o API settings; document image input formatting and preprocessing. Provide code to run MH-VoLTA with training scripts and configs, report seeds, multiple runs, and confidence intervals.  
- Include ablations for MH-VoLTA: effect of blank-image padding, number of fused layers, captions vs images, and replacing encoders.

4) Present a tighter, apples-to-apples test-set evaluation.  
- If claiming SoTA, ensure the reported number covers the same slice of WebQA used by baselines. Provide per-category and per-modality breakdowns on test, not just validation, and include statistical tests.

5) Expand qualitative analysis and diagnostics.  
- Add example cases where GPT-4o retrieval fails versus UniVL-DR, and where MH-VoLTA succeeds or fails per category. Show retrieved distractors and model rationales to substantiate Figures 3–5.

Typos and minor issues:
- “In-Content RLM” should be “In-Context RLM” throughout (Page 2).  
- “MH-VoLTA fairs better” → “fares better” (Page 7).  
- Equation (3) formatting could be simplified to a linear concatenation expression to avoid line breaks.  
- Appendix A.3: references to “6(a), 6(b)” are ambiguous without consistent cross-referencing style.

Criteria for raising the score:
- Provide the clarified, rigorous experimental protocol with corrected tables and figure references; add missing baselines or carefully justified comparisons; release prompts/code; and include ablations and uncertainty estimates. If the SoTA claim becomes unambiguous and the methodology is fully reproducible, I would consider raising to Findings (3.0) or higher.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Some central claims are interesting, but evaluation clarity, baseline coverage, and reproducibility are not yet at the main-track standard.

## Excitement
3.0 Interesting: The comparative framing and the GPT-4o in-context retrieval observation are useful and will interest practitioners, even if the study is not fully polished.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.  
Justification: The idea and analysis are timely and practically relevant, and figures/tables support some compelling observations (Table 1, Table 2, Figure 3). However, gaps in experimental clarity, weak baseline coverage, incomplete reproducibility, and a constrained scope relative to the broader WebQA task prevent a higher recommendation at this time.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section acknowledges the constrained scope (image-only categories, reliance on WebQA’s distractor construction) and the need to generalize ICR beyond this setting. Ethical considerations note potential misuse risks if LLMs are used to retrieve unsafe content. These are reasonable starting points, but the discussion could be expanded:
- Address dataset licensing and privacy issues around images/captions on WebQA.  
- Discuss bias amplification in category-restricted settings and the implications of training classifiers on limited vocabularies.  
- Consider the societal implications of relying on proprietary APIs for research reproducibility and access equity.

## Ethical concerns
None beyond the need for expanded discussion above.

## Needs Ethics Review
No

## Reproducibility
2.5 Reproducible with difficulty: Key prompting details and implementation specifics are missing; reliance on GPT-4o without released prompts and code makes replication hard.

## Datasets
1 No usable datasets submitted.

## Software
2 Documentary.: If code/prompts are released, they would help study and replicate, but no evidence is provided at submission time.