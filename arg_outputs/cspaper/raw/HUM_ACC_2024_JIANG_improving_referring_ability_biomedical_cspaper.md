# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper investigates whether reordering the same biomedical pre-training corpus using citation links can improve the “referring ability” of decoder-only LMs under continual pre-training. The authors construct LinkLM sequences by following citation edges in PubMed abstracts, sampling multiple cited references per step via a retriever, prioritizing the one with highest in-degree to extend the chain, then reversing the chain so later documents are supported by earlier ones. They continually pre-train TinyLlama-1.1B on 8B tokens and evaluate zero-shot and few-shot multiple-choice QA in the biomedical domain. Results show gains in intra-sample referring (PubMedQA) and improvements in few-shot settings, especially with one-shot retrieved demonstrations, while knowledge-recall benchmarks sometimes degrade slightly versus standard random-packing continual pre-training.

## Summary Of Strengths
- Clear, focused question: can citation-aware sequence construction improve decoder-only continual pre-training in a tightly focused domain where documents are already thematically close.
- Method is simple, annotation-free, and leverages easily accessible citation metadata; Algorithm 1 is straightforward to implement.
- Empirical evidence that sequence composition matters in continual pre-training, not only when training from scratch. This fills a gap relative to prior general-domain sequence design work.
- Intra-sample referring ability: Figure 3 shows consistent and eventually sizable zero-shot PubMedQA gains for LinkLM over Standard after ~3B tokens.
- Inter-sample referring ability: Figure 4a (3-shot, random) and Figure 4b (1-shot with KNN retrieval) show LinkLM often outperforms Standard during training. Table 3 confirms that with retrieved demonstrations, LinkLM attains the best micro-average (37.30%) among the three setups.
- Useful negative/neutral findings: Table 4 shows similar perplexities between Standard and LinkLM despite downstream differences, reinforcing that pre-training loss may not predict downstream in-context behavior.
- The preliminary analysis around selecting multiple references acknowledges practical retriever limitations and motivates the multi-reference sampling design.

## Summary Of Weaknesses
1) Scale and generality are limited
- All results are on a 1.1B-parameter model with 8B continual tokens. This is small for biomedical LLMs, which may induce behavior that does not transfer to larger models; the claims are sometimes phrased more broadly than the evidence supports (e.g., conclusions in Section 6). The paper’s own Limitations section (Page 9–10) notes this, but the main narrative sometimes implies wider applicability.

2) Methodological choices insufficiently ablated
- No ablation on critical LinkLM design knobs: the Poisson mean for K (Algorithm 1, line 7), the reference-selection retriever, tie-breaking by in-degree (line 9), reversing vs. not reversing sequences, and the sequence-wise shuffling step. Many of these could drive the effect size.
- Without these ablations, it is hard to identify which component produces the observed gains, and whether the approach is robust under different hyperparameters.

3) Use of Meditron-7B perplexity as a “ground-truth” ranking signal in Table 1 is questionable
- In Section 3, Equation (1) defines information via conditional perplexity and then Meditron-7B is used to rank references as “ground truth.” This presumes Meditron’s conditional perplexity is an oracle for relative informativeness, which is not validated. It amounts to asserting that one LM’s PP-based ranking is the correct target for evaluating another model or retriever. This could bias conclusions about retriever performance, especially since Meditron is a much larger, domain-adapted model while Contriever is a dual-encoder trained on different supervision.
- The biomedical-IR community typically assesses retrievers against relevance judgments or downstream utility, not PP of another LM. A small human study or using PubMedQA’s provided abstracts to compute utility-based metrics would strengthen the claim.

4) Retriever choice and evaluation are narrow
- The preliminary experiment (Table 1) uses facebook/contriever-msmarco. This domain mismatch likely underestimates dense retrieval of biomedical abstracts. Strong medical/biomedical bi-encoders exist. Without comparisons to biomedical-tuned retrievers, the conclusion that retrievers are “not as reliable as we expect” is under-substantiated for this domain.

5) Limited benchmarking breadth and protocol
- Only MCQA tasks are used; other tasks that more directly stress “referring” like long-context reading, citation-based QA, or open-book QA with explicit retrieval could better isolate the proposed benefit. The paper cites open-book QA in Introduction but does not include it.
- Few-shot evaluation largely uses raw accuracy with minimal prompting; no calibration or uncertainty adjustments. For 3-shot (random) results, the observed degradation versus zero-shot (Table 3) is largely hypothesized to be due to poor demonstration quality but not rigorously tested beyond the 1-shot KNN variant.
- No significance testing is reported for the main zero-shot and 1-shot KNN results. Figure 3 and Figure 4b present smoothed curves with shaded areas, but final checkpoint comparisons in Table 3 lack statistical tests to support the claimed improvements on several datasets.

6) Mixed results and trade-offs on knowledge recall
- Table 3 shows that in zero-shot settings LinkLM underperforms Standard on MedMCQA and USMLE-QA while winning on PubMedQA. The paper acknowledges a memorization trade-off, but does not further diagnose it, e.g., with controlled experiments on knowledge retention or evaluations on broader medical knowledge suites.

7) Baselines and related methods in-domain are thin
- Prior biomedical continual pre-training efforts that structure sequences around citations or document relations for decoder-only LMs are not discussed or compared. This weakens positioning. See “Potentially Missing Related Work.”
- No comparison to a simple and strong baseline discussed in prior sequence-design works: packing documents by same-source or same-venue or same-Mesh terms as in Zhao et al. (2024)-style composition but using biomedical metadata. This would help disentangle whether “any tighter topical clustering” suffices, vs. explicit citation chains.

8) Limited analysis of failure modes and interpretability
- Figure 2 gives an illustrative chain and the narrative suggests benefits from multi-hop references. However, the paper does not dissect erroneous or regressed cases. For instance, do longer chains help or hurt more often? Is there an optimal hop length? Are gains consistent across subfields?

9) Reporting clarity in figures and tables could be improved
- Figure 3 and Figure 4 use smoothing and shaded areas. It would help to mark specific checkpoints used in Table 3 and to provide exact numeric deltas with confidence intervals at those checkpoints. As is, reviewers must infer consistency between the curves and the tabulated final numbers.

10) Reproducibility gaps
- While Algorithm 1 and hyperparameters are described, it is unclear whether code, exact data processing scripts, and the constructed LinkLM sequences will be released. Given the sensitivity to construction details, lack of artifacts will impede replication.

Specific figure/table/equation comments:
- Figure 2: The architecture and data-flow diagram is helpful; it concretely shows how the chain is built from an anchor (D1^1) to multi-hop references and then reversed to create the pre-training input order. This supports the claim that the model can attend to both one-hop and multi-hop citations. However, the figure also underscores a potential bias: consistently prioritizing high in-degree nodes (Algorithm 1, line 9) may drift chains toward influential papers rather than the most semantically supportive ones. An ablation with random among top-K would test this.
- Figure 3: The PubMedQA zero-shot curve shows LinkLM’s smoothed accuracy trending above Standard after ~3B tokens, supporting the claim on intra-sample referring. It would help to annotate the end-of-training points and provide exact end-of-training confidence intervals.
- Figure 4a and 4b: These demonstrate that LinkLM improves few-shot averages, especially with random 3-shot (4a) where the orange curve dominates blue for most of training, and shows competitive results in 1-shot KNN (4b). Nevertheless, peak-to-peak volatility appears large, suggesting potential sensitivity to training step or sampling variance; more seeds or checkpoint averaging would give stronger support.
- Table 1: The use of Meditron-7B perplexity to define “top-5 references” is the core methodological concern. This is a non-standard proxy for ground truth, and stronger validation is needed.
- Table 3: Central to the paper’s claims. LinkLM beats Standard on PubMedQA in zero-shot (66.00 vs 62.80) and on average in 3-shot random (31.37 vs 30.59) and 1-shot KNN (37.30 vs 36.75). However, LinkLM lags Standard on MedMCQA and USMLE-QA in zero-shot, aligning with the paper’s own memorization trade-off narrative.
- Equation (1): The information measure framing is reasonable for intuition, but adopting a different LM’s conditional perplexity as oracle for ranking remains problematic without further justification or triangulation with human or task-based labels.

## Potentially Missing Related Work
1) Asada et al., “Citation-Aware Continual Pre-Training for Biomedical Language Models,” 2026 — Directly studies citation-structured continual pre-training for decoder-only biomedical LMs. Should be discussed in Section 2 and compared experimentally where possible; at minimum, clarify differences in sequence construction (pairwise vs multi-hop chains) and evaluation protocols.

2) Yano et al., “Effect of Multilingual and Domain-adapted Continual Pre-training on Few-shot Promptability,” 2025 — Analyzes few-shot promptability after biomedical continual pre-training. Relevant to Sections 5.4 and 6 to contextualize observed trade-offs between knowledge retention and in-context gains.

3) Xie et al., “Medical foundation large language models for comprehensive text analysis and beyond” (Me-LLaMA), 2025 — Large-scale medical continual pre-training and broad evaluation. Should be cited in Section 2.1 to position against strong medical LLM baselines and to clarify scalability expectations beyond 1.1B.

4) Shi et al., “MedAdapter: Efficient Test-Time Adaptation of Large Language Models towards Medical Reasoning,” 2024 — Presents an alternative to continual pre-training via test-time adapters for medical reasoning. Useful to discuss in Section 2.1 or 2.2 as a complementary or competing strategy and to highlight when data-centric sequence design vs. adapter-based methods are preferable.

5) Cheng et al., “Instruction Pre-Training: Language Models are Supervised Multitask Learners,” 2024 — Offers another sequence-structuring route through instruction-style data for continual pre-training. Adding to Section 2.2 would situate LinkLM with respect to instruction-driven pre-training that also aims to improve in-context behavior.

6) Jeong et al., “Medical Adaptation of Large Language and Vision-Language Models: Are We Making Progress?,” 2024 — Survey with head-to-head evaluations. Adding a brief discussion in Section 2.1 could sharpen the paper’s evaluation design and claims, given reported inconsistencies in benefits from medical DAPT.

7) Anonymous, “Continual knowledge infusion into pre-trained biomedical language models,” 2022 — Addresses catastrophic forgetting and continual updates in biomedical PLMs. Citing in Section 2.1 can frame the memorization trade-off observed in Table 3 and suggest mitigation strategies.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide ablations:
  - Vary K’s Poisson mean, replace in-degree heuristic with random among top-K, and test without reversing sequences. Report how each affects Table 3 outcomes and Figure 3/4 trends.
  - Swap retrievers: include at least one biomedical-tuned dense retriever and a BM25 baseline, and repeat Table 1 and the end-to-end LinkLM training using those variants.
  - Analyze chain length: report performance vs. average hop count and sequence length; check whether gains saturate.
- Strengthen the preliminary study:
  - Replace the Meditron-7B PP-based “ground truth” with human judgments on a small sample, or use downstream utility (e.g., change in PubMedQA perplexity or accuracy when providing that reference alone).
  - If using PP anyway, triangulate across multiple LMs to test robustness.
- Expand evaluation:
  - Add an open-book QA setting where retrieval is explicit and controllable, to directly measure intra-sample and inter-document referring.
  - Report significance tests for Table 3 and highlight exact CIs in the figures at end-of-training checkpoints.
- Clarify reporting:
  - In Figures 3 and 4, mark the final checkpoints used in Table 3, and include numeric values with error bars at those points.
  - Describe whether titles are included with abstracts during pre-training; titles often carry critical cues for linking.
- Reproducibility:
  - Release code, data-preprocessing scripts, and a small sample of constructed LinkLM sequences. Provide the exact tokenizer, filtering decisions, and seed values. This would raise the reproducibility rating.

Typos and minor issues:
- Page 1, the caption under Figure 1 mixes narrative about intra- vs inter-sample referring. Consider tightening the distinction.
- Page 4: “We know the information that a reference provides can be measured by” — add a brief justification or citation for Equation (1), or rephrase as a heuristic.
- Table 3: Consider adding statistical significance markers for per-dataset improvements.
- Page 7–8: “there are 71.43% of checkpoints” → “71.43% of checkpoints”.

Questions for rebuttal that could change my assessment:
- Can you provide ablations on K, in-degree selection, reversal, and shuffling? If the gains are robust across these, it strengthens the central claim.
- Can you include a biomedical-tuned retriever baseline in Table 1 and redo the end-to-end with it? If conclusions hold, the preliminary justification becomes much stronger.
- Will you release code and at least a subset of constructed sequences?
- Can you report results for an explicit open-book QA setting and significance tests for Table 3?

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
3 Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.

## Excitement
2.5 Between potentially interesting and interesting.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.
Justification: The idea is relevant and the empirical results are suggestive, especially on PubMedQA and in few-shot settings. However, the scale is small, core design choices lack ablations, the preliminary “ground truth” for reference ranking is non-standard and weakly justified, and evaluations are narrow. With stronger ablations, more robust retriever baselines, significance testing, and artifact release, this could move to a stronger recommendation.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The Limitations section acknowledges small scale and dependence on citation networks. Additional points to discuss:
- Potential bias amplification: prioritizing high in-degree references could over-emphasize historically prominent viewpoints and under-represent newer or minority perspectives in biomedical literature.
- Domain coverage and equity: Focusing on PubMed abstracts biases toward English-language and certain regions; discuss potential impacts on underrepresented populations and specialties.
- Dual-use and clinical risk: While ethics notes hallucination risks, it would help to state guardrails if the model is used in retrieval-augmented clinical settings and emphasize that the method tunes sequence structure, not factual correctness.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5 Mostly reproducible: They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.

## Datasets
1 No usable datasets submitted.

## Software
1 No usable software released.