# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper empirically evaluates whether large language models can understand DL-Lite ontologies. The authors define an evaluation framework spanning six tasks: syntax checking, subsumption of concepts or roles, instance checking, property characteristics probing (inverse and functional roles), query answering, and ontology satisfiability checking. They use several public ontologies to build inputs, reasoners to compute gold implications, and three prompting regimes (NI, WI, WIE). The main findings are that LLMs do reasonably well on syntax and on certain semantic tasks for small TBoxes or ABoxes, but they struggle with TBox NI transitivity rules and with large ABoxes. Figures 2–5 and Tables 1–7 summarize the pipelines, datasets, and results.

## Summary Of Strengths
- Clear problem framing and focus on DL-Lite, a formally grounded DL family that enables efficient reasoning, which makes the evaluation scope precise and relevant to structured semantic understanding.
- Broad coverage of DL services, from local syntax to model-theoretic semantics at both the component level (concepts, roles) and global level (satisfiability and QA). The task design maps reasonably onto standard DL services defined in Section 3.
- Use of real ontologies (GO, FMA, OBI, MarineTLO, Music; VICODI, STOCKEXCHANGE, UNIVERSITY, ADOLENA, SEMINTEC; UOBM, LUBM) increases ecological validity.
- Figures and tables are informative:
  - Figure 2 concisely visualizes the evaluation pipeline for syntax, subsumption, and instance checking. It helps readers understand how prompts, ontologies, and gold implications interact in the experiments.
  - Figure 3 shows a sharp performance drop on instance checking for UOBM1 and UOBM2, supporting the claim that ABox size is a limiting factor.
  - Figure 4 isolates performance on hand-crafted cases tied to specific transitivity rule categories, making the weakness on NI transitivity concrete.
  - Figure 5 shows that inverse and (inverse) functional role probing is largely successful.
  - Table 1 reports precision/recall/F1 for syntax checking across five ontologies and three prompt types, indicating robust syntax understanding, especially for GPT-4o-WIE.
  - Tables 2 and 3 provide transparent dataset statistics for subsumption and instance checking.
  - Table 5 reports satisfiability checking precision/recall/F1 over two inconsistent-ontology sources.
- The paper is generally well organized, with preliminaries that clearly define DL-Lite syntax and semantics. The transitivity rules listed in Appendix A help ground the evaluation in formal reasoning patterns.

## Summary Of Weaknesses
1) Evaluation metrics for semantic tasks undercount errors and inflate conclusions.  
   - For subsumption and instance checking (Section 4.2.1), the metric is the ratio of gold logical implications that an LLM returns, which amounts to recall. There is no measurement of false positives. Given that LLMs are prone to hallucinations, omitting precision risks overestimating capability. In Figure 3, high bars may mask significant incorrect inferences. A complete evaluation should report precision, recall, and F1, as done for syntax in Table 1 and satisfiability in Table 5. Without this, statements like “LLMs perform well in these two tasks when the input ontology is relatively small” are only partially supported.

2) Inadequate control of prompting and generation variability.  
   - The paper does not report decoding parameters, temperatures, number of trials, or seed control. Since the experiments rely on free-form reasoning and chain-of-thought-like explanations at times (e.g., case study in Section 4.2.1), variance can be large. There is also no majority-vote or self-consistency scheme. Results may not be stable or reproducible across runs.

3) Mixing instruction content with test objectives risks leakage of target knowledge.  
   - Prompts WI and WIE explicitly teach the rules that are being evaluated, including NI and PI transitivity and ABox rules (Appendix C). This tests following instructions more than prior understanding of DL-Lite. While the authors also test NI, the differences between NI, WI, and WIE are not statistically analyzed, and for key negative results on NI transitivity, it is unclear whether failures are due to misunderstanding the rules, brittle adherence, or prompt misinterpretation. A better design would include unseen rule compositions and adversarial paraphrases, and a fully held-out split of rule templates.

4) The case study on transitivity is insightful but under-analyzed.  
   - Figure 4 demonstrates weaker performance on cases dominated by NI transitivity. However, there is no breakdown by specific rule instances from Appendix A, nor error taxonomy. For example, in Case 1 of Table 4 (Page 6), several implications of the form ∃R1^- ⊑ ¬C are missed. It would help to report per-rule accuracy and whether mistakes stem from directionality, inverse handling, or negation scope.

5) Query answering setup is insufficient to support conclusions about LLM capacity for QA over ontologies.  
   - Section 4.2.3 splits the ABox into ten parts and sends them sequentially to GPT-4o. Without a memory mechanism, a retrieval plan, or a scratchpad that persists across calls, failure is expected and says little about QA potential. Established OBDA or DL-Lite rewriting baselines are not compared. At minimum, include an ablation with external memory, retrieval-augmented prompting, or proof-state carryover, and report precision/recall.

6) Satisfiability checking lacks explanation diagnostics.  
   - Table 5 gives precision/recall/F1, but there is no analysis of failure modes by constructor, inconsistency pattern, or MIS size. Since Maa-edas-iasted is “more complex” (Page 8) the paper should quantify which constructs hamper performance and whether errors correlate with specific NI rules listed in Appendix A. Presenting representative incorrect predictions with the purported reasoning would make the findings more actionable.

7) Limited comparisons to adjacent DL reasoning with LLMs and neurosymbolic hybrids.  
   - The Related Work (Section 2) focuses on general logical reasoning and concept structure, but omits several directly relevant works that probe DL reasoning or integrate LLMs with DL reasoners. This weakens positioning and misses opportunities for stronger baselines or methodological alternatives.

8) Minor inconsistencies and clarity issues.  
   - Table numbering mismatch on Page 4: the text says “In Table 2, we present precision, recall and F1,” but the syntax results are actually in Table 1 under Figure 2.  
   - Some equations and examples contain typos in Appendix E/Table 6 (the symbol “∓” appears where “∃” or “∧” is expected; also “R6⊆R5” typed as “R5⊆R5” in Case 4).  
   - In Appendix A, the first ABox rule repeats C1 ⊑ C2, β = C1(a) → βnew = C1(a), which looks like a no-op rather than C2(a). This might be a transcription error and could confuse readers.

9) Limited statistical rigor.  
   - No confidence intervals or significance testing across multiple samples of randomly selected implications (Table 3 sampling) are reported. Given the stochastic nature of LLM outputs, intervals or bootstrap variances would be helpful.

10) Reproducibility gaps.  
   - Although prompts are included (Appendix C) and data sources are named, it is unclear whether the exact split of axioms, the randomly corrupted axioms for syntax, and the sampled logical implications for instance checking will be released. Also, the precise mapping from OWL axioms to DL-Lite fragments used for each dataset needs more detail for exact replication.

11) Overgeneralization of claims.  
   - Several conclusions state that “LLMs can understand formal syntax and model-theoretic semantics of concepts and roles” but the evidence is limited to accuracy on small handcrafted cases or recall-only metrics. Given the absence of precision in Figure 3 and limited ablations, these conclusions should be qualified more narrowly.

## Potentially Missing Related Work
1) Poulis et al., “Transformer-based Language Models for Reasoning in the Description Logic ALCQ,” 2024 — directly evaluates LLMs and fine-tuned transformers on entailment tasks derived from DL contexts. The methodology and failure modes are highly relevant for Section 4.2; should be discussed in Related Work and contrasted in Section 4, especially regarding dataset construction and rule depth.

2) Poulis et al., “Transformers in the Service of Description Logic-based Contexts,” 2023 — earlier DELTA_D framework; informs how reasoning depth and linguistic paraphrase affect model performance. Add to Section 2.2 and compare reasoning scaffolds after Eq. definitions in Section 3.

3) Barua et al., “Description Logic Concept Learning using Large Language Models,” 2025 — presents a neurosymbolic loop where LLMs propose class expressions and a DL reasoner checks them. This is relevant to your property probing and satisfiability tasks; cite in Section 2.2 and discuss as a hybrid alternative in Section 5.

4) Ciatto et al., “Large language models as oracles for instantiating ontologies with domain-specific knowledge,” 2025 — complements your ABox-heavy evaluation; discuss in Section 4.2.3 as a strategy for scalable ABox population with reasoner feedback.

5) Garbacz et al., “Large Language Models and Foundational Ontologies,” 2024 — assesses aligning LLM outputs with formal ontological theories. Include in Section 2 as a complementary perspective on formal semantics beyond taxonomies, and contrast with your DL-Lite focus.

6) Enhancing LLMs through Neuro-Symbolic Integration and Ontological Reasoning, 2025 — proposes coupling LLMs with OWL reasoners for inconsistency detection and correction. Discuss in Section 4.2.4 as a path to improve satisfiability checking and NI-transitivity weaknesses.

7) Yang et al., “Large Language Model for OWL Proofs,” 2026 — focuses on proof generation over OWL; discuss in Section 4.2.1 and 4.2.4 as a deeper reasoning target and to motivate adding proof-structure evaluation beyond label prediction.

## Comments Suggestions And Typos
Actionable suggestions:
- Report precision, recall, and F1 for subsumption and instance checking, not just recall. If outputs are multi-label, define exact matching criteria and handle partial correctness. Include confusion analyses for incorrect entailments.
- Control and report decoding details: temperature, top-p, max tokens, number of samples, and whether self-consistency or voting is used. Provide averaged results with standard deviations over multiple runs to quantify variance.
- Strengthen the NI-transitivity analysis. Break down Figure 4 by each rule in Appendix A, add per-rule accuracy, and include qualitative error categories (negation handling, inverse placement, role vs concept confusion). Connect these to concrete examples in Table 4.
- Improve query answering methodology. Evaluate with a retrieval or memory-augmented prompting scheme, or a neuro-symbolic loop that rewrites queries to SQL-like forms via DL-Lite rewritings, then compare with a standard OBDA baseline. As-is, sequentially feeding ten chunks is an unfair test.
- Clarify and correct typos and notational issues:  
  - Page 4: “In Table 2, we present precision, recall and F1” should refer to Table 1.  
  - Appendix A: ABox rule “α = C1 ⊑ C2, β = C1(a) → βnew = C1(a)” likely intends βnew = C2(a). Please verify all ABox rules.  
  - Appendix E/Table 6: Several “∓” symbols appear; if these should be “∃” or another operator, fix consistently. In Case 4, “R5⊆R5” seems odd; confirm intended axiom.  
  - Section 4.2.1: “LLaMA3-7b” appears once; the rest of the paper uses “LLaMA3-8B.” Standardize.
- Reposition claims to better match evidence. Qualify conclusions about “understanding semantics” by emphasizing the conditions: small inputs, recall-focused metric, with or without instructions and examples.
- Release all constructed datasets: the exact corrupted axioms for syntax, the sampled logical implications per dataset, and the handcrafted transitivity cases. Provide scripts that extract and normalize DL-Lite fragments from the source OWL ontologies.

Questions for rebuttal that could raise my score:
- Can you provide precision/F1 for subsumption and instance checking and show that false positives are limited?  
- Can you add per-rule NI-transitivity results and error analyses aligned with Appendix A?  
- Can you provide multi-run variance, decoding settings, and, if possible, a simple self-consistency baseline?  
- For QA, can you test a memory-augmented or retrieval-augmented setup and include a symbolic DL-Lite rewriting baseline?

## Confidence
3: Reasonably confident but not fully verified — I checked the core design and results carefully, but some dataset construction details and symbol typos make me cautious.

## Soundness
3.5: Between Acceptable and Strong — The study is broadly sound and the task coverage is good, but key evaluation choices for semantic tasks use recall-only metrics and lack variance controls.

## Excitement
2.5: Between potentially interesting and interesting — A useful and timely empirical study in a specific niche (DL-Lite), with some insightful negative results on NI transitivity and scalability, yet methodologically conservative.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The study is meaningful and well-scoped, but not ready for the main track due to evaluation gaps (precision/variance), limited NI-transitivity analysis, and underdeveloped QA methodology.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The Limitations section acknowledges dataset size/diversity and focus on DL-Lite. Additional points to discuss: reliance on proprietary APIs limits long-term reproducibility; potential bias if prompts inadvertently encode ontology-specific cues; and risk of overclaiming “understanding” from recall-only metrics. Societal risks are minimal here, but it is worth noting that misinterpreting ontologies in safety-critical domains (biomedical, legal) could propagate errors if LLMs are used without a symbolic verifier.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible with some effort — Prompts and sources are given, but randomness, decoding settings, and construction scripts are needed for full replication.

## Datasets
3: Potentially useful — If released, the corrupted-axiom sets, sampled implication sets, and handcrafted transitivity cases would be useful.

## Software
1.5: Documentary — No software is indicated; scripts to generate datasets and evaluate model outputs would substantially improve value.