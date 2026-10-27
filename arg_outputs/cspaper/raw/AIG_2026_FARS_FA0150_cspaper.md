# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper evaluates whether early-exit scoring via a logit-lens projection can replace full-depth perplexity-based AMI scoring in LongCodeZip for repository-level code context compression. The proposed variant, ShallowPPL, truncates forward passes at layer L of a 28-layer code LLM and computes perplexity from the intermediate representation using the model’s unembedding matrix. The authors pre-register success criteria (≥1.5× speedup with ≤1.0 point quality drop) and test on Long Code Completion and RepoQA. Results show that ShallowPPL does not meet the bar: best speedup is 1.05× with quality drops larger than allowed. Ablations indicate that coarse function ranking is the key failure point and that the last layers contribute disproportionately to relevance scoring quality, limiting the viability of early-exit perplexity for code.

## Summary Of Strengths
- Clear, falsifiable hypothesis with pre-registered success criteria; the paper stays honest about a negative outcome and provides evidence-backed reasoning.
- Solid experimental framing: compares against Full AMI and an embedding-RAG baseline, across two complementary benchmarks (LCC and RepoQA), using a modern 7B code model.
- Diagnostic ablations are informative. Table 3 shows that keeping full-depth for coarse ranking and using shallow only for fine-grained scoring recovers most of the quality gap. Table 4 highlights a strong nonlinearity with depth, pinpointing the importance of the final layers.
- Useful insights about systems constraints: Section 4.4 explains why layer truncation barely improves latency due to fixed per-call overhead in the scoring pipeline.
- Figures and tables aid interpretation. Figure 1 clearly contrasts the full-depth AMI pipeline with the proposed early-exit variant, making explicit where computation is saved and how logits are produced. Figure 2 visualizes the quality-speed tradeoff, supporting the claim that the target region (≥1.5× speedup with ≤1.0 drop) is unattainable under their setup.
- The negative result is practically valuable: it cautions others against investing in logit-lens early-exit perplexity for code relevance scoring without addressing coarse ranking and system overhead.

## Summary Of Weaknesses
1) Narrow model scope and external validity
- All results are on a single model, Qwen2.5-Coder-7B-Instruct (Section 4.1). Claims about “final transformer layers encode critical information for code relevance that cannot be approximated” may not generalize to other decoder-only code models, larger scales, or architectures with different normalization/unembedding behaviors. This limits the strength of the main conclusion.

2) Limited baselines for acceleration
- The comparisons focus on RAG embeddings and Full AMI. Given that the thesis concerns efficiency, it is important to compare with other speed-focused compressors for code or general long-context methods adapted to code (e.g., learned token pruning, latent compression). Without these, the efficiency–quality frontier is underexplored, and it is hard to position the negative result relative to strong alternatives.

3) Underdeveloped systems analysis
- Section 4.4 attributes the limited speedup mainly to per-call overheads (embedding, attention setup, KV init). While plausible, the paper does not provide profiling breakdowns, batch-size sensitivity tests, or measurements with KV reuse/batching. Since this is central to the negative finding, a more systematic latency decomposition is needed to separate fundamental representational limits from engineering choices.

4) Pre-registered thresholds feel ad hoc
- The success criteria (≥1.5× speedup and ≤1.0 point drop) are reasonable but not justified by user studies or cost–benefit analysis. For example, Table 2 shows a 3.83 point gap on RepoQA in the best hybrid setting. Some users might accept that in exchange for a larger speedup if achievable with system changes. The paper treats the thresholds as universal, which may overstate the “hypothesis does not hold” conclusion.

5) Missing or sparse statistical treatment
- Results are averaged over 3 seeds for timing, but accuracy/ES metrics lack variance estimates, confidence intervals, or significance tests (Tables 1–4). Given relatively small absolute differences in Table 1 (e.g., 56.59 vs 54.76 ES), statistical reporting would help determine whether small gaps are robust.

6) Ambiguity about where perplexity is computed and its calibration
- Section 3.2 applies final LayerNorm before the unembedding projection to reduce “representational drift.” However, details about calibration of intermediate logits are thin. For instance, were temperature or bias corrections explored? Is the unembedding shared/tied in the base model? Negative results could partially stem from a miscalibrated logit lens rather than a general limitation.

7) Coarse vs fine stage design choices deserve deeper probing
- Table 3 shows coarse ranking dominates quality. The paper concludes early-exit is unsuitable for coarse ranking. But hybridizing with lightweight learned scoring for coarse stage, or using cross-file attention summaries, could change the tradeoff. As it stands, the work stops short of testing other early-exit-friendly coarse rankers.

8) No evaluation of hybrid systems with system-level optimizations
- Section 4.4 suggests KV reuse or batched scoring might help. The study would be stronger if it tested at least one of these, even in a limited setting, to show whether the negative conclusion is about representation, systems, or both.

9) Related work gaps around recent compression approaches
- The Related Work covers prompt-compression and some code retrieval, but omits several highly relevant recent studies on context compression for repository-level tasks and end-to-end learned compression (see “Potentially Missing Related Work”). This weakens positioning and may overlook stronger efficiency baselines or alternative interpretations of the negative finding.

10) Scope creep in claims
- The conclusion implies a broader representational statement about “final transformer layers encode critical information for code relevance” (Abstract, Section 5). While consistent with Figure 2 and Table 4 for this setup, stronger language should be hedged to this model and pipeline; without multiple models and normalization variants, the claim risks overgeneralization.

Specific engagement with figures/tables:
- Figure 1: The diagram is helpful to see the exact point of early exit and the reliance on the unembedding WU. However, the figure and Section 3.2 do not clarify whether WU is tied or if any learned adapter is used to stabilize intermediate logits, which is known to matter in tuned-lens style methods. This omission may undercut the negative result’s generality.
- Figure 2: The tradeoff curves on RepoQA clearly show the steep quality gain from L=26 to L=28, aligning with Table 4’s 3.83-point jump for just two layers. This strongly supports the paper’s conclusion that shallow exits fail to meet the target region. Still, a similar plot for LCC would help validate if the nonlinearity is consistent across tasks.
- Tables 1 and 2: They underpin the headline failure to meet pre-registered criteria. Table 1 shows ShallowPPL Hybrid (L=20) gets 54.76 ES vs 56.59 for Full AMI with only 1.05× speedup. Table 2 shows 86.00% vs 89.83% with 1.05× speedup. These concise comparisons convincingly reject the target criteria.
- Tables 3 and 4: The ablations are the paper’s strongest contribution. Table 3 isolates the coarse-stage failure; Table 4 quantifies quality–depth nonlinearity. Together they support a nuanced diagnosis rather than a blanket “early-exit never works” message.

## Potentially Missing Related Work
1) Feng et al., “On the Effectiveness of Context Compression for Repository-Level Tasks: An Empirical Investigation,” 2026 — Provides a broad empirical comparison of compression paradigms for repository-level code intelligence. It should be discussed in Section 2.2 to contextualize ShallowPPL’s negative result against a wide panel of compression strategies and used as a reference point when interpreting Tables 1–4.

2) Jia et al., “Compressing Code Context for LLM-based Issue Resolution,” 2026 — Introduces Oracle-guided Code Distillation and SWEzze for minimizing code context in real GitHub issue fixing. Directly relevant to repository-level compression under strict latency and effectiveness constraints. Discuss in Section 2.2 and consider as an alternative baseline family where learned compression and search interact.

3) Li et al., “End-to-End Context Compression at Scale,” 2026 — Presents latent context language models that map long inputs to short latent contexts with strong Pareto improvements. While not code-specific, it is a topically central alternative to early-exit perplexity. Compare in Section 2.1/2.2 and mention in Section 5 as a promising direction distinct from logit-lens truncation.

4) “Information-Theoretic Lower Bounds on Context Compression for Long-Horizon Agents,” 2026 — Offers lower bounds and impossibility results germane to negative findings in compression. Citing in Section 5 could temper claims by noting theoretical limits and provide a principled frame for why aggressive truncation can fail for code relevance.

## Comments Suggestions And Typos
Actionable suggestions:
- Expand systems analysis: Provide profiling of scoring latency into fixed overhead vs per-layer compute. Include experiments with micro-batching and KV cache reuse across the many small forward passes, ideally reporting their impact on Tables 1–4 style metrics. If 1.5× speedup becomes reachable with system changes, that would change the interpretation of the negative result.
- Strengthen calibration of intermediate logits: Report whether WU is tied, what exact LayerNorm is applied, and whether you tested simple calibration strategies (e.g., temperature scaling, bias correction, tuned-lens style linear adapters). If even calibrated lenses fail, the representational conclusion is stronger.
- Broaden model coverage: Replicate key ablations (Table 3 or Table 4) on at least one additional decoder-only code model of a different family or scale. If final-layer reliance persists, the claim about non-approximability becomes more convincing.
- Add uncertainty estimates: For Tables 1–4, include standard deviations or bootstrap CIs for ES/EM and accuracy. For small differences (e.g., Table 1), this will clarify robustness.
- Compare with learned or latent compressors: Add at least one learned compression baseline (e.g., token pruning, latent contexts) to better position the negative result relative to the current efficiency frontier.

Potential typos/clarifications:
- Page 1, Abstract: “exceeding quality thresholds” likely means “exceeding the allowed degradation thresholds.” Consider rewording to avoid confusion.
- Page 3, Section 3.1: Define all symbols on first use consistently; q is the instruction, c is chunk, but B appears without immediate reminder.
- Page 4, Section 3.2, step 2: “Apply the model’s final layer normalization” — please specify whether this is the exact LN module from layer N or a copy; if parameters depend on residual stream statistics at depth N, justify applicability at depth L.
- Tables 1–4: Indicate number of examples per benchmark split and any filtering. Clarify if “Time (s)” is end-to-end compression-only timing and whether generation time differs across methods.
- Figure 2 caption: Consider including the LCC panel’s y-axis labels explicitly in text and add markers for the 1.5× speedup and 1.0-point degradation thresholds on both subplots for symmetry.

Evaluation-shifting criteria for rebuttal:
- Provide profiling plus experiments demonstrating that with KV reuse and batching, the hybrid setting achieves at least ~1.5× speedup with ≤1–1.5 point drop on at least one benchmark, or provide strong evidence that such system optimizations still cannot meet the threshold.
- Show consistent ablation trends on a second model family, reinforcing the representational conclusion.
- Demonstrate that improved calibration or tuned-lens adapters at intermediate layers do not materially close the quality gap in coarse ranking.

## Confidence
3: Reasonably confident but not fully verified: Pretty sure, but there’s a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper’s details, e.g., the math or experimental design.

## Soundness
2.5: Between Poor and Acceptable — Methodologically careful in parts, but limited model scope, sparse statistical reporting, and underdeveloped systems analysis weaken the strength of the negative conclusion.

## Excitement
2.0: Potentially Interesting — The negative result and ablations are informative, but the scope and analysis depth are not yet sufficient for strong excitement.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The study is honest and provides useful diagnostics, yet the central negative conclusion is built on a single model, lacks stronger systems experiments, and omits several relevant contemporaneous baselines and references. With added profiling, broader model coverage, calibration variants, and stronger comparisons, it could become a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The work is an efficiency analysis on code context compression; direct societal risks are minimal. Limitations that should be explicitly acknowledged or expanded:
- Generality across models and toolchains is uncertain; results may be specific to one architecture and inference stack.
- The pre-registered thresholds are not user-validated; different applications may accept different tradeoffs.
- Negative conclusions might discourage early-exit research prematurely; clarifying that KV/batching and hybrid learned rankers remain open avenues would balance the message.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4: Mostly reproducible — Model, datasets, and high-level settings are standard; code is reportedly available. More detail on batching/KV options and lens calibration would further help.

## Datasets
1: No usable datasets submitted.

## Software
4: Useful — If the released code reproduces Tables 1–4 and supports ablations, it should be valuable for others studying compression tradeoffs.