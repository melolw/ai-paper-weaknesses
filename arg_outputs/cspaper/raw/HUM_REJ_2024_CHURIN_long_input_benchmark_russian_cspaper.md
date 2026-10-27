# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
The paper introduces LIBRA, a long-context benchmark for Russian that aggregates 21 tasks into four complexity groups and spans input lengths from 4k up to 128k tokens. It combines translated, adapted, and newly created datasets, many sourced or augmented from Librusec and ruSciBench, and proposes a standardized evaluation protocol with fixed prompts and largely EM-based metrics. Baseline evaluations on 12 long-context LLMs are reported across context lengths and tasks, with observations on how performance degrades as input grows and how SFT models generally outperform base ones. The benchmark, datasets, and leaderboard are claimed to be publicly available.

## Summary Of Strengths
- Clear gap addressed: There is no widely adopted long-context benchmark for Russian; LIBRA consolidates 21 tasks with explicit coverage of context scaling to 128k tokens, which should be valuable to the Russian NLP community.
- Breadth and organization: The benchmark is thoughtfully grouped by complexity (I–IV), and the taxonomy in Table 1 and the overview in Figure 1 give a coherent map of skills and task types across the benchmark.
- Attention to context length: The authors provide a tokenization-informed approach to constructing length-specific subsets (Table 3), explicitly enabling analysis of performance versus length across many models (Tables 4–7).
- Practical evaluation tooling: A unified prompting and greedy decoding protocol is described; datasets and a leaderboard are promised to be available, which can encourage replication and community participation.
- Baseline coverage: Evaluations include 12 models spanning various architectures and declared context limits, including a commercial model (GPT-4o) and numerous open models; cross-length summaries are provided (Table 4) alongside per-task aggregates (Tables 5–7).
- Constructed tasks for Russian: Several new datasets (e.g., MatreshkaNames, MatreshkaYesNo, LongContextMultiQ, LibrusecHistory/MHQA, ruSciAbstractRetrieval, ruSciPassageCount) are specifically tailored to Russian long-context reasoning rather than only relying on direct translations.

Figure- and table-grounded comment:
- Figure 1 succinctly visualizes the four complexity groups and lists the tasks per group. This figure is useful to readers for quickly mapping the landscape of the benchmark and recognizing that LIBRA tries to cover retrieval, multi-hop reasoning, and global-context comprehension.
- Table 4 is especially informative for length scaling: it shows a consistent downward trend in average performance as the length increases, with GPT-4o maintaining a noticeable lead. This supports the paper’s claim that increased length negatively affects most models.
- Table 2 (fertility) and Table 3 (length splits) concretely document the tokenization approximation and how dataset partitions are derived. This is an asset for reproducibility, though it also surfaces methodological issues (discussed below).

## Summary Of Weaknesses
1) Translation methodology and quality control for translated datasets are under-specified. Section 3.4 states Google Translate was used for multiple datasets. There is no discussion of post-editing, quality checks, or domain-specific corrections. For complex tasks like ruQasper or ruSciFi, translation artifacts can change difficulty and label validity. Without human verification, the scientific value of cross-model comparisons may be compromised.

2) Token length estimation via fixed “fertility” is fragile. Section 3.3 fixes a standard fertility of 3 based on a set of tokenizers (Table 2). This choice simplifies partitioning but risks misalignment with individual model tokenizers, especially those with Russian-specific vocabularies or byte-level differences. This has two critical consequences:
   - The nominal 4k/8k/… bins per model may correspond to very different true token counts, invalidating claims about “context length” comparability.
   - It can bias results if some models routinely receive effectively shorter or longer inputs than others.
   Suggestions: report actual token counts per model per sample, or evaluate models with their native tokenizer-based length control and aggregate over effective, not approximated, token lengths.

3) Truncation policy is likely unfair and can distort conclusions. Section 4.2 truncates inputs from the right when they exceed the maximum context. For tasks where the answer is often at the end or distributed (e.g., LibrusecMHQA, ruSciPassageCount), truncation can underrepresent some models more than others. Table 6 shows large drops on tasks like LongContextMultiQ and ruSciAbstractRetrieval for many models; without clarifying how often answers were truncated away, it is hard to separate model limitations from evaluation artifacts. A fairer policy would check answer position statistics, use sliding windows, or at least quantify truncation-induced answer loss.

4) Prompt and decoding choices are too rigid and under-analyzed. The evaluation uses a single prompt per task and greedy decoding (temperature=1.0 with do_sample=False). Long-context tasks are notoriously prompt-sensitive, and the paper acknowledges prompts were empirically chosen (Section 4.2) but provides no sensitivity analysis or prompt variants. For few-shot tasks (ruTREC, ruGSM100), the precise ordering and content of demonstrations can dominate results. Without reporting robustness to prompt templates, the observed differences risk being prompt artifacts.

5) Metric design is uneven and often too narrow. Most tasks use EM, but several tasks would benefit from span-aware or soft matching metrics, or hierarchical scoring where partial retrieval is meaningful. In Table 10 (GPT-4o), ruSciAbstractRetrieval drops sharply with length (from 99.0 at 4k to 19.8 at 128k), but pure EM masks whether models retrieve near-miss spans or produce approximately correct rationales. Similarly, ruQasper (F1) is the exception, but the paper does not describe F1 computation details for Russian (tokenization, normalization).

6) Incomplete reporting for GPT-4o and cross-model comparability. GPT-4o is evaluated on only 10% of data (Section 4.1 note), yet it dominates many comparisons in Tables 4–7 and anchors several conclusions. The mismatch in sample sizes and possible selection bias make the leaderboards and model ranking hard to interpret. At minimum, provide confidence intervals, bootstrapped variance, or sensitivity to subsampling so readers can assess comparability.

7) Insufficient dataset quality controls for newly created tasks. Appendix A describes crowdsourcing and editorial roles but lacks:
   - Inter-annotator agreement (IAA) or adjudication procedures for LibrusecHistory and ruSciAbstractRetrieval.
   - Clear validation of multi-hop structure in LibrusecMHQA (beyond expert editors), such as explicit supporting-fact annotations or answer provenance checks.
   - Error audits for the “synthetic length extension” methodology acknowledged as a limitation in Section “Limitations,” which can produce contradictions when concatenating neighboring paragraphs.
   The absence of these controls weakens confidence in ground-truth integrity, particularly for longer contexts.

8) Data leakage not empirically audited. While Data leakage is acknowledged in “Limitations,” there is no analysis to estimate its extent. Since Librusec and Wikipedia-like sources are common pretraining data, without probing memorization (e.g., unseen-book splits, publication date filters, or membership inference style checks), performance could reflect memorization rather than long-context reasoning, especially on PasskeyWithLibrusec and ruBABILong where background texts come from books.

9) Missing or thin comparisons to closely related long-context benchmarks and design rationales. The Related Work focuses on LongBench, L-Eval, and ZeroSCROLLS, but omits several recent long-context benchmarks that push sequence lengths well beyond 100k and target realistic global reasoning. This omission reduces the paper’s positioning and limits insights into why LIBRA’s task mix and scaling choices are appropriate for Russian.

10) Limited analysis depth. The Results section mainly reports scores and a few qualitative takeaways. Missing elements include:
   - Statistical significance tests across models and lengths.
   - Error analyses by error type or answer distance from query, which are critical for long-context tasks.
   - Breakdown by answer position relative to truncation point.
   - Prompt robustness experiments or alternative decoding settings.

11) Ethical and legal aspects of data sources need more detail. Although “Ethical Considerations” and “Limitations” mention open data and permissions, Librusec’s licensing and the legality of using book texts for redistribution and model evaluation are not clearly documented. If redistribution is restricted for some texts, this affects dataset release claims and reproducibility.

12) Figure and table integration could be stronger in the narrative. Figure 1 is a nice overview, but the text could more explicitly tie claims to specific empirical patterns visible in Tables 4–7. For instance, the text claims ruSciFi at 64k “is beyond the capabilities of most models,” which is borne out in Table 6, but referencing exact per-model numbers and discussing outliers would strengthen the argument.

## Potentially Missing Related Work
1) Zhang et al., “∞Bench: Extending Long Context Evaluation Beyond 100K Tokens,” 2024 — directly addresses ultra-long context evaluation with both synthetic and realistic tasks over 100k tokens. Should be discussed in Section 2.2 and compared in Section 5 to justify LIBRA’s length choices and task diversity; include as a point of contrast for 128k-scale evaluation.

2) Hsieh et al., “RULER: What’s the Real Context Size of Your Long-Context Language Models?,” 2024 — introduces configurable synthetic tasks to measure effective vs. advertised context. Discuss in Section 2.2 and consider an auxiliary RULER-style analysis in Section 5 to quantify effective context lengths for Russian tasks.

3) Ni et al., “XL^2Bench: A Benchmark for Extremely Long Context Understanding with Long-range Dependencies,” 2024 — focuses on 100k+ contexts across multiple domains. Add to Section 2.2 with a methodological comparison and cite when motivating LIBRA’s Group IV tasks in Section 3.2.

4) Karpinska et al., “One Thousand and One Pairs: A ‘novel’ challenge for long-context language models,” 2024 — NoCha tests global reasoning over entire novels with human-authored claims. Discuss in Section 2.2; could inspire a Russian analogue and strengthen the rationale for LibrusecMHQA and ruSciFi-style global tasks.

5) Li et al., “Long-context LLMs Struggle with Long In-context Learning,” 2024 — LongICLBench highlights failure modes in many-shot classification with long inputs. Discuss in Section 2.2; consider adding long-ICL Russian tasks to LIBRA or clarifying why such tasks were excluded.

6) Churin et al., “Long Context Benchmark for the Russian Language,” 2025 — a closely related effort in an ACL-affiliated venue defining Russian long-context datasets and levels. Must be discussed in Section 2.2 and contrasted in methodology, dataset composition, and evaluation protocol.

7) Xu et al., “From 128K to 4M: Efficient Training of Ultra-Long Context Large Language Models,” 2025 — provides training strategies and evaluations at ultra-long contexts. Cite in Section 2.1 and Section 5 to contextualize models’ performance at 128k and to suggest future LIBRA usage for 1M+ contexts.

8) Ji et al., “LongAttnComp: Cross-Family Context Compression for Long-Context Reasoning,” 2026 — attention compression scheme preserving accuracy on long-context tasks. Discuss in Section 2.1 or 2.2; relevant to fair and cost-effective evaluation on LIBRA and as a baseline direction.

## Comments Suggestions And Typos
Actionable questions and suggestions:
1) Fairness in length and truncation:
   - Please report, per task and length, the proportion of instances where the gold answer lies in the truncated region. Add a sensitivity analysis using sliding windows or chunked retrieval to show whether conclusions in Tables 4–7 hold when answers are guaranteed visible.
   - Replace the fixed fertility=3 approximation with per-model actual token counts. At minimum, add supplementary per-model effective-length histograms to confirm that LIBRA’s bins correspond to comparable true token lengths.

2) Translation and annotation quality:
   - For all translated datasets, describe post-editing and validation protocols. Provide spot-check accuracy rates for labels after translation and report any detected systematic translation issues.
   - For human-created tasks, report IAA where applicable, describe adjudication, and provide examples of typical errors. For LibrusecMHQA, add explicit supporting-fact annotations or rationale spans to verify that questions truly require multi-hop reasoning.

3) Prompt and decoding robustness:
   - Add a prompt sensitivity study (e.g., two to three prompt variants per task) and a decoding sensitivity study (greedy vs. temperature sampling with top-p). Report variability bars in Tables 4–7 or a new table.
   - For few-shot tasks (ruTREC, ruGSM100), randomize example order or provide multiple seeds to show stability.

4) Statistical reporting and analysis depth:
   - Provide confidence intervals or standard deviations across multiple runs or subsamples. Especially clarify GPT-4o’s “10% evaluation” by reporting sampling procedure, variance, and whether the subset is representative.
   - Include error analysis by failure type and by answer distance from query to substantiate long-range reasoning claims.

5) Ethics and licensing:
   - Clarify Librusec and other sources’ licenses and whether redistribution in benchmark form is permitted. If any components cannot be redistributed, provide clear instructions for users to reconstruct the datasets and a filtered leaderboard.

Typos and minor issues:
- Section 5: “Overlall” should be “Overall.”
- Section 3.2: “belongs to the tasks” should be “belongs to tasks” or “includes tasks.”
- Appendix B: Ensure all Russian originals of prompts are available upon de-anonymization as promised.

Criteria that could change my evaluation:
- Adding per-model actual token-length accounting, a truncation visibility audit, and prompt/decoding sensitivity analyses that do not alter the main conclusions would raise Soundness and could move this to a strong Findings or borderline main track.
- Demonstrating translation verification quality and IAA for the new datasets would substantially improve confidence.
- A leakage probe or split design that reduces memorization concerns would strengthen claims about long-context reasoning.

## Confidence
4: Quite sure after careful checking — I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
3: Acceptable — The core contribution is sound as a resource, but evaluation methodology has notable issues (fertility approximation, truncation policy, prompt sensitivity, limited quality controls) that should be addressed.

## Excitement
3.0: Interesting — Filling the Russian long-context gap is useful; the breadth is appealing. Methodological reservations temper enthusiasm.

## Overall Assessment
3: Findings — This paper could be accepted to the Findings of the ACL. The main criteria are soundness and reproducibility. The resource fills an evident gap for Russian long-context evaluation, offers broad task coverage, and provides initial baselines. However, methodological limitations around token-length estimation, truncation fairness, translation and annotation quality assurance, missing related work, and limited analysis depth make it fall short of the main track bar at this stage.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper has a dedicated Limitations section, which is appreciated. Still, several points could be strengthened:
- Translation bias and its impact on fairness across tasks should be explicitly discussed and empirically probed.
- Data leakage: provide an estimate via date-based splits, overlap checks, or memorization probes. State who benefits or is harmed if leakage causes overestimation of capabilities in certain domains.
- Representational bias: clearly note domain skew (Librusec books, ruSciBench abstracts), and potential undercoverage of dialectal or sociolectal Russian; consider adding tasks that better reflect diverse registers or sensitive topics, with appropriate safeguards.
- Legal/ethical release: confirm licensing for book excerpts and whether redistribution is permitted; where not, provide reconstruction scripts and document constraints.

## Ethical concerns
Potential licensing and redistribution issues around book texts; lack of explicit verification of permissions may affect dataset release claims. Risks of data leakage and representational bias are acknowledged but not empirically assessed. None rise to the level of requiring an ethics review if licensing is clarified and quality controls are strengthened, but this should be addressed before public leaderboard promotion.

## Needs Ethics Review
No

## Reproducibility
4: Mostly reproducible — Datasets and splits are described; prompts are provided; code/leaderboard are claimed to be available. Some ambiguity remains around translation QC, tokenizer-specific lengths, and truncation impacts, but results are largely reproducible.

## Datasets
4: Useful — The assembled datasets are likely valuable to Russian NLP researchers and practitioners, particularly for long-context modeling.

## Software
4: Useful — If released as stated, the evaluation code and leaderboard will be useful for ongoing work and benchmarking.