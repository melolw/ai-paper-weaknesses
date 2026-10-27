# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper defines a new task, multi-target cross-lingual summarization (MTXLS), where the goal is to generate summaries in multiple target languages that are semantically coherent with one another. It proposes a re-ranking framework that is language-neutral: for each target language, generate k candidate summaries with an M2M summarizer, then select one candidate per language to maximize a set-level semantic similarity score, computed via cross-lingual sentence encoders (SONAR) and aggregated over pairs. The authors formalize connections to summarize-and-translate, present a pivot-based and a pivot-free variant, and relate the pivot-free model to rejection sampling. Evaluation on a clustered reconstruction of CrossSum covers seven languages, using ROUGE-2 and BLASER 2.0 for reference-based quality, and COMETKiwi and BLASER 2.0 for cross-language coherence. Results show improved cross-language coherence over standard decoding, with minor impact on ROUGE-2, and better balance than summarize-and-translate.

## Summary Of Strengths
- Clear problem framing: MTXLS is well motivated as a practical need for multi-language users and regulatory contexts. The task definition in Section 3 is clean, and the graphical models in Figure 1 succinctly distinguish summarize-and-translate versus the proposed language-neutral view.
- Methodological clarity and simplicity: The re-ranking formulation in Equations (5)–(6) is intuitive and model-agnostic, and Algorithm 1 provides a practical O(Nk^2) heuristic to approximate the set-level maximization. The link to rejection sampling (Section 4.3, Equation 7–8) provides a useful probabilistic lens even if used primarily for motivation.
- Language-neutrality: The pivot-free design in Section 4.2 is appealing, as it avoids biases of a fixed pivot and treats all languages symmetrically.
- Evaluation protocol extends standard CLS evaluation: The paper explicitly measures cross-language coherence using QE models (CometKiwi and BLASER 2.0) by translating generated summaries across target languages. This more directly probes the stated objective than per-language ROUGE alone.
- Empirical evidence is consistent and well-structured: Table 2 shows that NeutralRR improves coherence metrics (CometKiwi, BLASER 2.0 (C)) compared to M2MS, while preserving ROUGE-2 better than summarize-and-translate. Figure 2 further shows coherence gains grow with more candidates k, and the runtime trade-off is quantified.
- Actionable dataset engineering: Appendix A’s simple graph-based clustering of CrossSum into multilingual “story” cliques is a pragmatic way to approximate MTXLS-style references, with descriptive statistics (Table 3, Figure 3) and intra-cluster coherence diagnostics (Figure 4).

## Summary Of Weaknesses
1) Reliance on automatic clustering introduces uncontrolled noise that directly affects both training context and evaluation:
- The dataset restructuring uses maximal cliques on automatically paired CrossSum examples (Appendix A), but no manual verification or noise quantification beyond QE matrices is provided. Since the main claim is about semantic coherence across languages, noisy or partially overlapping “story clusters” can either inflate or mask coherence. The authors acknowledge mispairings (Section 5.1), yet there is no sensitivity analysis to cluster noise beyond Figure 4’s average QE levels. This matters because the task hinges on cross-language alignment quality.

2) Evaluation on coherence is fully automatic, lacks human validation, and may be partially circular:
- The selection function φ uses SONAR cosine (Equation 10) and evaluation uses BLASER 2.0 and COMETKiwi. Although SONAR is not the same model as COMETKiwi/BLASER, all are cross-lingual embedding/estimation models trained to align translations. The paper should show that coherence gains hold under human judgment. Absent human evaluation, it remains unclear whether the selected sets are truly more semantically aligned or just more “QE-aligned.” A small human study on factual and content overlap across languages would substantively strengthen claims.

3) Limited baselines and incomplete exploration of alternatives that also target agreement:
- The paper compares to M2MS, summarize-and-translate (S&T), and a single zero-shot LLM (Mistral 7B). Missing are broader re-ranking or agreement strategies that could serve as stronger baselines, for example: (i) consensus-based re-ranking across languages without SONAR (e.g., agreement via MT round-trips or round-robin back-translation similarity), (ii) decoding with mutual-information or bi-directional agreement constraints, (iii) content-plan or pivot-free agreement models at decoding time beyond re-ranking. This omission weakens the evidence that the proposed heuristic is the preferred approach.

4) Theoretical link to rejection sampling is suggestive but not operational:
- Section 4.3 posits sampling from p(S|x,T) using rejection sampling with proposal ∏ q(y_t|x,t) and acceptance by φ. However, Z′ is unknown, and the method used in practice is a deterministic, mode-seeking heuristic (Section 4.4), which optimizes a proxy objective hat{φ} based on a random permutation (Equation 9). The paper would benefit from a clearer statement that the rejection-sampling narrative is mainly conceptual and that no guarantee is provided on the correlation between hat{φ} and φ or on near-optimality.

5) The proxy objective and transitivity assumption need empirical justification:
- Equation (9) sparsifies the full pairwise graph to a chain per permutation and assumes transitivity of similarity. Although Figure 2 shows improvements as k increases, there is no ablation comparing chain-based maximization vs direct pairwise maximization on small N (where exhaustive search is cheap), except the limited setting of Figure 5 with 4 languages. It would help to systematically validate that the chain proxy tracks φ across source languages and cluster sizes, or at least bound the gap empirically.

6) Modest absolute improvements and metric trade-offs:
- In Table 2, NeutralRR generally trails M2MS on ROUGE-2 by a small margin, and much more strongly trails S&T on cross-language coherence. The main claim is to balance both sides, but the practical magnitude may be viewed as modest. For en as source, NeutralRR’s CometKiwi rises from 59.28 to 64.34 for en target and from 60.31 to 64.76 averaged over “rest,” while ROUGE-2 slightly dips from 17.88 to 17.59 (en) and 13.20 to 12.90 (rest). This is a reasonable trade for some users, but the paper could better articulate where this balance is most beneficial.

7) LLM baseline coverage is limited and partially unreliable:
- The Mistral 7B baseline is evaluated only from English and Chinese sources and often fails formatting or language adherence (Section 5.4 and Appendix D.1). Given current practice, broader LLM comparisons (e.g., stronger multilingual LLMs, instruction-tuning variants, or few-shot prompting) and a robustness check of prompt design would give a fairer picture of state-of-the-art behavior under MTXLS constraints.

8) Metric choice for summary quality is narrow:
- ROUGE-2 is the only n-gram metric reported, and on news-like data this can under-represent abstractive quality. Complementary measures like ROUGE-Lsum, BERTScore, or QAFactEval-style factuality metrics would make the quality side more convincing, especially since the argument in Section 5.5 asserts that cross-language agreement correlates with factuality.

9) Clarity and small issues in formulas and exposition:
- In Equation (4), “where y_π ∼ p(y_π|x_o, t)” appears to have a typo; conditioning should be (x_o, π), not t. This recurs in other places where π vs t is easy to mix up; careful proofreading is recommended.
- The assumption in Section 4.1 that Z is independent of y_t and ∑_{y_t} φ(y_t,·) < ∞ is plausible but unverified for the chosen φ; a brief justification would help.

10) Scope of languages and domains is narrow:
- The study focuses on up to seven languages and a single news domain via CrossSum reconstructions. The claim that this is a generally applicable language-neutral method would be stronger with at least one non-news domain or a language set with more typological variety and script diversity.

Figure- and table-specific comments:
- Figure 1: This is central to the paper’s narrative. The move from panel (a) to (b) clarifies that y_t is not conditionally independent of x_o given y_π, and panel (c) illustrates the language-neutral joint with pairwise similarity. The graphical contrast supports the methodological distinction clearly.
- Figure 2: The CometKiwi panel (bottom-left) shows a consistent monotonic increase in cross-language coherence as k grows, and NeutralRR’s advantage over PivotRR widens with larger k. The Time-per-summary panel confirms the runtime trade-off. These plots substantiate the claim that re-ranking headroom scales with candidate diversity.
- Table 2: This is the key results table. It convincingly demonstrates the intended trade-off: compared to M2MS, NeutralRR raises cross-language coherence (e.g., en source, “rest”: CometKiwi 60.31 → 64.76; BLASER 2.0 (C) 3.61 → 3.89) while keeping ROUGE-2 nearly intact. Compared to S&T, NeutralRR protects ROUGE-2 far better but gives up some coherence. This table underpins the paper’s “balanced” positioning.

## Potentially Missing Related Work
1) Ye et al., “GlobeSumm: A Challenging Benchmark Towards Unifying Multi-lingual, Cross-lingual and Multi-document News Summarization,” 2024 — Introduces a unified, many-to-many news summarization benchmark with clustering and event-centric design. It directly speaks to dataset construction for multilingual and cross-lingual settings and could be discussed alongside Section 5.1 and Appendix A, and potentially used as an additional evaluation setting.
2) Qiu et al., “Detecting and Mitigating Hallucinations in Multilingual Summarisation,” 2023 — Proposes mFACT and discusses multilingual factuality. Relevant to the claim in Section 5.5 that cross-language agreement may be a proxy for factuality. Should be discussed in Section 2.1 and cited in Section 5.5 when arguing about the relationship between agreement and quality.
3) Datta et al., “MILDSum: A Novel Benchmark Dataset for Multilingual Summarization of Indian Legal Case Judgments,” 2023 — Domain-specific multilingual and cross-lingual summarization with comparisons of summarize-then-translate vs direct methods; relevant for Section 5 (Experiments) as an alternative domain to validate MTXLS and in Related Work for applications in high-stakes domains mentioned in the Introduction.
4) Takeshita et al., “Cross-lingual extreme summarization of scholarly documents,” 2023 — Releases a CL-TLDR dataset and baselines for scientific papers. Relevant to Related Work (Section 2.1) and as a possible out-of-domain testbed to assess generality of the language-neutral approach.
5) Liang et al., “D^2TV: Dual Knowledge Distillation and Target-oriented Vision Modeling for Many-to-Many Multimodal Summarization,” 2023 — While multimodal, it addresses many-to-many summarization with cross-lingual dimensions. Worth citing as an extension avenue in Related Work and Conclusion for multimodal MTXLS.
6) Ryu et al., “Understanding LLM Behavior in Multi-Target Cross-Lingual Summarization,” 2026 — Presents a larger MTXLS benchmark with detailed analyses of LLM behavior, which directly speaks to the same task definition. It should be discussed in Section 2 and contrasted in Section 5 as an alternative evaluation framework and as context for broader LLM comparisons.

## Comments Suggestions And Typos
Actionable suggestions:
- Add a small-scale human evaluation of cross-language agreement and factual consistency. Even a 100–200 example subset rated for “same facts across languages” and “faithfulness to source” would greatly strengthen claims that QE-based gains reflect real semantic coherence.
- Expand baselines. Include at least one agreement-aware decoding or consensus-style re-ranking baseline not relying on SONAR, such as selecting candidates by round-robin machine-translation similarity between languages, or a mutual-information flavored decoding setup. Also broaden LLM baselines with more capable multilingual models and robust prompting.
- Validate the proxy objective. Provide a more systematic study comparing hat{φ} vs φ across more language counts and source languages, not only the small-N case in Figure 5. Report the correlation and frequency with which the chain-based solution matches or closely approximates the exhaustive optimum.
- Diversify quality metrics. Add ROUGE-Lsum and a semantic metric like BERTScore or QAFactEval to better capture abstractive quality and factuality, particularly since ROUGE-2 alone is known to be limited on news.
- Stress-test on an additional dataset/domain. If possible, evaluate on a second corpus with stronger cross-language alignment (e.g., WikiLingua or a subset of GlobeSumm), or a non-news domain (e.g., legal or scholarly) to test generalizability and support the claim that the approach is language-neutral and domain-agnostic.

Typos and minor issues:
- Equation (4): “where y_π ∼ p(y_π | x_o, t)” should be “p(y_π | x_o, π)”.
- Section 4.5: “we define the similarity function as … where s_a and s_b represent the L2-normalized SONAR embeddings” — earlier variables use boldface for vectors; ensure consistent notation.
- Table 2, last row entry: “1.02 | 1.348” has a dot in the number of parameters; likely “1,348”.
- Section 5.2: “beam search multinomial sampling using with 5 beams” — stray “using”.
- Clarify the independence assumptions around Z and boundedness of φ in Section 4.1–4.3; justify that φ ∈ [0,1] indeed holds for Equation (10) and that this bound propagates as stated.

Criteria that could increase my score:
- Inclusion of the human evaluation and stronger baselines, plus expanded metric coverage, would likely raise Soundness to 4. With an additional dataset/domain and a more thorough validation of the proxy objective, I could see this as a clear main-track accept.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3.5 Between Acceptable and Strong: Method and evaluation are generally sound, but the reliance on automatic QE for coherence without human validation and limited baselines limit the strength of the claims.

## Excitement
3.0 Interesting: The task framing and language-neutral re-ranking are interesting, and the evaluation protocol foregrounds an important dimension. The empirical gains are useful but not striking.

## Overall Assessment
3.5 Borderline Conference: Close to acceptable for the main conference but with notable weaknesses. The work identifies a meaningful gap, proposes a practical, language-neutral re-ranking method with clear probabilistic framing, and demonstrates improved cross-language coherence with minimal ROUGE cost. However, the evaluation relies entirely on automatic metrics closely related to the selection signal, the dataset clustering is noisy without human checks, and baselines are incomplete. With added human evaluation, stronger baselines, and a second dataset, this could cleanly clear the bar.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The Limitations section is candid about computational cost and dependence on candidate quality. Additional points worth discussing:
- Risks of misaligned multilingual outputs in sensitive domains: the method aims to reduce discrepancies, but when it fails, who is harmed and how? Consider domain-specific harms (legal, medical, policy) and the need for calibration or abstention mechanisms.
- Dataset provenance and alignment uncertainty: clustering CrossSum may incorporate copyrighted material and mismatches; discuss data licensing and the implications of evaluating on automatically paired content.
- Bias and coverage: the seven-language set skews toward better-studied languages; consider how the approach and QE metrics behave for low-resource or typologically distant languages.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The paper includes model checkpoints, decoding details, metric configurations, and algorithmic steps. Code/data release is promised; including clustering scripts and exact evaluation scripts would likely move this to 5.

## Datasets
2 Documentary: No new curated dataset is released; the clustering protocol over CrossSum is useful for replication but limited in standalone value.

## Software
3 Potentially useful.: The re-ranking code and scripts could be directly reusable by practitioners with multilingual summarizers, especially if the clustering and evaluation pipelines are included.