# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper studies syntactic repetition in LLM-generated text using “syntactic templates,” defined as frequent n-grams over POS tags (and briefly, constituency templates). It proposes simple corpus-level metrics based on POS sequences, including a POS compression ratio (CR-POS), the proportion of texts containing at least one template of length n, and a length-normalized templates-per-token statistic. Using open-source OLMo-7B with access to its pre-training corpus (Dolma) and several closed-source instruction-tuned models, the paper reports: (i) model outputs exhibit substantially higher rates of POS templates than human references across multiple summarization datasets; (ii) most templates observed in model generations are present and frequent in the pre-training data and emerge early during pre-training; and (iii) a relaxed “style memorization” criterion based on POS sequences detects more memorization than exact string matching. The paper suggests that syntactic templates are informative diagnostics for model behavior across models, tasks, and domains.

## Summary Of Strengths
- Clear problem framing around structural repetition beyond token n-grams, with a concrete, implementable abstraction (POS templates) and straightforward metrics.
- Strong empirical sweep:
  - Multiple models, including open-source (OLMo-7B, Mistral-7B, Llama-2/3 variants, Alpaca) and GPT-4o.
  - Multiple datasets and tasks: open-ended generation, synthetic data generation (Cosmopedia-like instructions), and several summarization corpora (Rotten Tomatoes, CNN/DM, Cochrane, BooookScore).
  - Training-data analysis is enabled via OLMo, tying generated templates back to pre-training statistics.
- Useful diagnostic visualizations:
  - Figure 2 compellingly shows that perplexity of identified templates drops quickly in early checkpoints, indicating early acquisition of frequent syntactic patterns.
  - Figures 3–4 tie generated templates to pre-training coverage and high frequency ranks, empirically supporting the central memorization-style connection.
  - Figure 5 demonstrates higher rates of templates in model outputs versus human references across template lengths, reinforcing consistency of the finding.
- Tables provide systematic and interpretable evidence:
  - Table 1 and Table 11 show that, for OLMo-7B, varying temperature and top-p affects open-ended generation more than summarization; summarization remains highly templatic.
  - Table 3 and Table 10 summarize cross-model cross-dataset template incidence and CR-POS, including length-normalized templates-per-token, showing robustness across tasks and models.
  - Table 4 and Table 12 show high template rates for long-document summarization strategies.
- The “style memorization” analysis (Section 8) is a simple, convincing extension of exact-match that captures synonym and number substitutions, supported by Figure 6 and qualitative examples in Figure 7.
- Writing is generally clear and the contribution is easy to reproduce from the described pipeline.

## Summary Of Weaknesses
1) Definition and selection of templates can be ad hoc and under-specified across datasets.
- Section 3.1–3.2 defines a template as a POS n-gram that repeats at least τ times, but τ is not consistently specified. For Rotten Tomatoes, the paper “retains the top 100 most common template[s]” where the least frequent template appears 4 times. It is unclear how τ or “top 100” generalizes across datasets with vastly different sizes, distributions, and domains, which can bias cross-dataset comparisons.
- Actionable: Provide a principled, dataset-size-aware thresholding scheme (e.g., frequency per million tokens, or top-k relative to corpus size) and analyze sensitivity to k and n across datasets.

2) The diversity metric CR-POS (Equation 1) needs stronger justification and comparison to alternatives.
- Using gZip compression on POS sequences is plausible, but it conflates several phenomena and depends on concatenation order and segment boundaries. There is no comparison to simpler, more interpretable metrics such as POS n-gram entropy, type-token ratio on POS, Yule’s K, or distinct-n over POS. Without these, it is hard to interpret absolute CR-POS values or how they relate to more standard diversity measures.
- Actionable: Add baselines like POS 6-gram entropy and distinct-n@POS and report correlations and differences; discuss stability to concatenation order.

3) Limited ablations on the tagging layer and parsing choices; potential sensitivity to POS tagger errors.
- Section 3.2 relies on NLTK POS with Penn Treebank tags. The paper acknowledges tagger errors and language-mixing issues in Limitations but does not quantify their impact on template detection or CR-POS. There is only a brief appendix look at constituency templates; no quantitative comparison to dependency patterns or alternative taggers.
- Actionable: Compare results using at least one modern tagger (e.g., Stanza, spaCy), and report agreement on template incidence and ranks. Provide an error-sensitivity analysis on a POS-noised corpus.

4) Coverage analysis in pre-training data is restricted to the “top 50K” POS 6-grams; frequency matching is partial.
- Section 6.2 limits the search to top-50K POS 6-grams in Dolma. This may inflate “coverage” because generated templates are also biased to be frequent by construction. Figure 4 compares rank distributions, but the sampling protocol for non-templates is not fully detailed, and the effect of restricting to 50K is not ablated.
- Actionable: Expand to multiple cutoffs (e.g., 50K, 200K, 1M), report how coverage and rank-gaps change, and clarify the sampling of non-templates to ensure apples-to-apples controls.

5) Perplexity analysis lacks methodological detail and baseline clarity.
- Section 6.1 and Figure 2 plot average perplexity of templates and “randomly sampled 6-grams.” It is not fully specified whether the non-template 6-grams are matched for frequency and length of contexts, or whether perplexity is computed token-by-token within template spans versus entire sentences containing those spans. Reported numbers (e.g., “drop to around 500 for non-template tokens, compared to 200 for templates”) need standard deviations or confidence intervals.
- Actionable: Specify exact perplexity computation (span-based vs sentence-level), include statistical tests, and control for frequency of POS 6-grams.

6) Inference settings can confound cross-model comparisons.
- Most summarization results use greedy decoding for all models (Table 3, Table 10), but some models differ in default system instructions and output styles. For closed models in particular, default pre-prompts can induce more formulaic structure. The paper partly explores sampling hyperparameters for OLMo-7B (Table 1, 11), but not for other models.
- Actionable: For a subset of models, include temperature/top-p variations aligned to normalize effective randomness, and test whether template rates remain higher than human references.

7) Prompt sensitivity is shown but not fully disentangled from template prevalence claims.
- Appendix D (Table 9) shows prompt choice affects template incidence. However, the main narrative sometimes generalizes that “most models produce more templates than human authors,” which might vary with more task-specific prompts or constraints. Cochrane is also an edge case where human references are highly templatic due to genre conventions.
- Actionable: For each dataset, report per-prompt averages or a prompt-robust metric (e.g., median over prompts) and clarify in the main text how prompt choice mediates findings.

8) Style memorization methodology needs stronger controls and reporting.
- Section 8 uses top-50k common 100-grams in Dolma, truncates to 50 tokens, and then prompts with that prefix. This setting is favorable to extraction. While this parallels Carlini et al. (2022), the added POS criterion could overcount if tagger noise or near-trivial structural sequences inflate “style” matches.
- Actionable: Add a baseline where POS tags are permuted or coarse-grained to test false-positive rates; report confidence intervals per frequency bucket in Figure 6 and conduct significance tests between exact vs POS memorization across buckets.

9) Interpretation of domain differences could be deeper.
- Table 3 and Figure 5 show large gaps between model-generated and human references on Rotten Tomatoes and CNN/DM, but Cochrane behaves differently. The paper briefly points out genre conventions, but a more thorough analysis of which POS templates drive the domain differences and why would strengthen the explanatory value.
- Actionable: Provide top-k POS templates per domain, with examples of matched spans for model vs human, and analyze overlaps to reveal domain-specific drivers.

10) Minor clarity issues in figures and tables.
- Figure 5 and Figure 8 use dashed lines for human references; in the text, explicitly map line styles to legends and mention the reference rates at each n for quick reading. In Table 3 and Table 10, bolding is said to flag models exceeding human TPT, yet the table body does not visibly bold any entries; ensure consistency and a clear legend.
- Actionable: Improve figure captions to state exact takeaways numerically, and ensure visual encodings match the narrative.

A figure- and table-specific comment supporting or undermining claims:
- Figure 2: The green line (template tokens) consistently shows lower perplexity than the red line (other tokens) after early checkpoints, supporting the paper’s claim that templates are learned early. However, the main axis scale and the inset scale differ; adding error bars would quantify variability. The method section should clarify how template spans are scored to ensure comparability with non-templates.
- Table 3: On Rotten Tomatoes, nearly all models exceed 90% of summaries containing at least one 6-gram POS template (e.g., Mistral-7B at 99.6%), while human references are 46.4%. This directly supports the central claim that model outputs are more templatic than human texts, even when normalized by templates-per-token. The exception patterns and domain differences in Cochrane, however, suggest that genre conventions can partially close or invert gaps, and should be explicitly discussed in the main text, not only footnoted.

## Potentially Missing Related Work
- Zhan et al., “Discourse Diversity in Multi-Turn Empathic Dialogue,” 2026 — studies templatic behavior at the discourse move level in dialogues and proposes methods to increase diversity. Relevant to Section 2 and Discussion to situate POS templates within a hierarchy of repetition phenomena; consider adding to Related Work and discussing in Section 7 as a higher-level analogue.
- Gueorguieva et al., “AI generates well-liked but templatic empathic responses,” 2026 — shows LLMs follow stereotyped pragmatic templates in empathy tasks. Should be cited in Section 2 to connect syntactic repetition to pragmatic-level templates and in Section 5 to motivate domain-specific analyses.
- Namuduri et al., “QUDsim: Quantifying Discourse Similarities in LLM-Generated Text,” 2025 — introduces discourse-level similarity metrics grounded in Questions Under Discussion, directly related to structural repetition beyond syntax. Add to Section 2 and compare in Section 3.3 as an alternative structural diversity measure.
- Jiang et al., “Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond),” 2025 — large-scale study of diversity/homogeneity in open-ended generations. Mention in Section 2 and discuss in Section 5 as complementary corpus-level homogeneity evidence; consider correlating their homogeneity metrics with CR-POS and template rates.
- Williamson et al., “Syntactic Blind Spots: How Misalignment Leads to LLMs’ Mathematical Errors,” 2025 — manipulates syntactic templates in math word problems to repair reasoning. Relevant to Section 9 and Limitations as an instance where template manipulation impacts downstream behavior; cite in Related Work and Discussion.
- “The Syntactic Productivity of Large Language Models,” 2025 — tests syntactic productivity via determiner–noun pairing diversity. Compare in Section 3.3 and Discussion as an alternative corpus-level syntactic generalization measure, potentially explaining gaps between template frequency and productive syntactic variation.

## Comments Suggestions And Typos
Actionable suggestions likely to change my assessment if addressed:
- Provide principled, size-normalized template selection and a sensitivity analysis. Report results for multiple k values and explicit τ-defined thresholds across datasets, not just “top 100” (Section 3.1–3.2).
- Add alternative syntactic diversity baselines and ablations: POS entropy, distinct-n over POS, and at least one modern POS tagger. Quantify robustness of key findings to the tagger choice (Section 3.3).
- Expand Section 6.2 coverage analysis beyond top-50K POS 6-grams and clarify non-template sampling. Include multiple cutoffs and show how coverage/rank gaps evolve.
- Clarify perplexity computation in Section 6.1 and Figure 2, add uncertainty estimates, and ensure non-templates are frequency-matched controls. This would solidify the “learned early” claim.
- For at least a subset of closed/open models, report template rates under matched sampling settings (temperature, top-p) to reduce decoding-confound arguments in Table 3 and Table 10; include prompt-robust aggregates in the main text.
- Expand the domain analysis: list top-k POS templates per dataset for model vs human, with qualitative spans; this will make Tables 3–4 and Figures 5, 8 more interpretable.
- Style memorization: add a negative-control analysis by permuting tags or coarse-graining tagsets to estimate false positives. Add confidence intervals and significance tests to Figure 6.
- Make figure/table presentation fully consistent: bolding rules in Table 3/10, explicit dashed-line legend for human references in Figure 5 and Figure 8, and include exact numbers in captions where feasible.

Minor editorial notes:
- Page 4, Table 1 caption: “average text length” is not in the displayed Table 1 on Page 4, but appears later in Table 11; align captions with content.
- Section 3.3: In Equation (2), T is overloaded as both corpus length and a set of texts; consider renaming variables to avoid confusion, for example N for number of texts and L for length.
- Figure 1 caption: “following by the frequency” → “followed by the frequency.”
- Page 5, “We find that templates are learned quickly … trained on 4B tokens” — specify exact checkpoint indices for reproducibility.

Criteria for raising my overall score:
- Add the robustness ablations and methodological clarifications above, especially around template selection thresholds, tagger choice, and perplexity computation; and provide stronger controls in style memorization.
- A brief comparison to alternative structural metrics (POS entropy, distinct-n@POS) showing consistent conclusions.

## Confidence
4: Quite sure after careful checking — I checked figures, tables, and equations; some implementation details are not fully specified, so there is residual uncertainty.

## Soundness
3.5: Between Acceptable and Strong — The empirical story is consistent and well supported across datasets and models, but several methodological choices need firmer justification and ablation (template selection thresholds, CR-POS alternatives, tagger sensitivity, coverage cutoff).

## Excitement
3.5: Between interesting and exciting — The paper offers a useful, simple lens on structural repetition and connects it to pre-training and memorization. It is not primarily a new model, but as an analysis paper it can influence evaluation and diagnostics.

## Overall Assessment
4: Conference — solid analysis paper with broad, consistent empirical evidence and actionable insights. Some methodological details are ad hoc and should be tightened, but they are addressable before camera-ready.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
- Limitations are acknowledged: reliance on third-party taggers, English-only scope, need for large corpora. I would add:
  - Potential misuse for AI-text detection is discussed as out of scope, but given frequent templates in human-written domain-constrained texts (e.g., Cochrane), any naive use risks false positives and unfair treatment of specific genres or non-native writers.
  - Memorization analysis via POS may surface sensitive training snippets even if not exact-matched; discuss privacy risk when large-scale prompting with training prefixes is performed.
- Societal impact: This framework can help auditing stylistic homogeneity and implicit data influence, potentially improving transparency. Risks stemming from overinterpreting templates as “AI fingerprints” should be clearly caveated.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — The pipeline, datasets, and models are standard; some key thresholds and controls need clearer specification. Releasing code and exact template lists per dataset would push this to 5.

## Datasets
2: Documentary — No new dataset is introduced; the analyses over existing corpora are useful to replicate findings.

## Software
3: Potentially useful — If the authors release scripts for template extraction, CR-POS computation, and coverage analysis, this will be practically helpful. Currently they rely on external libraries; custom code availability would increase the rating.