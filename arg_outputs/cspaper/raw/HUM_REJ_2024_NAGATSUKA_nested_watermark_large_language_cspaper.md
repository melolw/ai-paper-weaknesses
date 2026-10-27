# Preliminary Observations:
N/A

# Expected Review Outcome:

## Paper Summary
This paper proposes a nested watermarking scheme for auto-regressive LLMs that embeds two watermarks using two keys, with the second watermark’s favored token set nested inside the first. The generator increases logits for tokens in G1 by δ1 and for those in G2⊂G1 by δ1+δ2, and the detector computes z-scores for counts of G1 and G2 tokens; it can also combine p-values via Fisher’s method. The central claim is that nesting improves detection on short outputs (50–100 tokens) while preserving text quality. Experiments with Llama-2-7b-chat and a GPT-4–generated pseudo-instruction dataset report higher “Embedding Success Ratio” (ESR) than a single-watermark baseline and comparable or slightly better GPT-4 judge-rated text quality.

## Summary Of Strengths
- Problem focus on short-text detection is practically relevant, as many real-world LLM uses produce short outputs where standard watermark tests lose power.
- The nested construction is simple and easy to implement, clearly described by Equations (4)–(6), and the overview in Figure 1 is helpful for readers to grasp the two-level biasing and detection flow.
- Results in Table 2 indicate consistent ESR gains over a single watermark for lengths 50–100, with the largest improvements at the shortest lengths. The “Unified” detector (via combined p-values) shows the strongest results, which aligns with the intuitive value of aggregating signals.
- Preliminary quality comparison in Table 1 provides a fair starting point for selecting a single-watermark bias that trades off ESR against quality; the authors choose a mid-high bias (δ=3.5) for the baseline, which they argue is reasonable for ESR-focused comparison.
- The paper explicitly acknowledges limitations of LLM-as-a-judge and short-text evaluation challenges in Section 6, which is appreciated.

## Summary Of Weaknesses
1) Statistical independence and Fisher’s method. In Section 3.2, the paper uses Fisher’s method to combine p-values from the two watermark tests and states the tests are independent. However, z1 counts tokens in G1 and z2 counts tokens in G2⊂G1, so the statistics are inherently dependent through shared tokens and conditioning on c1. Using Fisher’s method without establishing independence (or using a dependence-robust alternative) is not justified and likely optimistic. This is material, since the strongest ESR gains in Table 2 hinge on the “Unified” metric that relies on Fisher’s combination. Please either provide a theoretical justification for independence or switch to a method valid under dependence (e.g., Brown’s method or a resampling-based combination), and then re-evaluate.

2) ESR definition is incorrect and confusing. In Section 4.2 the paper defines ESR as “equal to the reciprocal of Type II Error,” but then reports ESR as a percentage between 0 and 100 in Table 2. If Type II Error = β, then “reciprocal” would be 1/β, which is not a percentage and would explode as β→0. The text also suggests ESR is “the proportion of successful watermark embeddings in a single attempt,” which is 1−β, not 1/β. This conceptual and terminological error undermines the core metric. Please correct the definition and recompute all reported numbers accordingly. If the intended ESR is 1−β, then rename it to “detection success rate” to avoid confusion.

3) Missing Type I error and ROC analysis. The paper fixes a detection threshold (θ=4) and reports “ESR” on watermarked text only. There is no measurement of false positive rates on non-watermarked text, no ROC or AUC curves by length, and no calibration of θ for short texts. Without Type I error characterization, it is impossible to assess detection reliability. A core expectation for watermarking papers is to characterize both Type I and Type II errors, especially in the short-length regime the paper targets. Please add experiments on human-written or non-watermarked LLM outputs to report FPR vs TPR by length and sensitivity to θ.

4) Limited baselines and positioning. Related work cites classic and recent methods, including Duwak, but omits several directly relevant contemporary watermarks that target robustness/quality trade-offs on short or edited text (see “Potentially Missing Related Work”). The experimental section compares only against a single-key biasing baseline with a few δ settings. There is no comparison against adaptive/semantic watermarks or certified schemes, which weakens claims of practical advantage. Adding at least one adaptive/semantic baseline would materially strengthen the paper.

5) Threat model and security claims are underdeveloped. The Introduction and Section 4.4 suggest the nested scheme preserves partial detectability if the first key is compromised. There is no explicit threat model, no analysis of a key-compromise scenario, and no experiments simulating an adversary with knowledge of s1, partial token editing, or paraphrasing attacks. Given prior work shows paraphrasing can defeat detectors, the lack of adversarial evaluation is a serious gap for a watermark whose claimed benefit includes added robustness/security.

6) Unclear details of group construction and hyperparameters. Section 3.1 defines r1=H(wt−n,s1) and r2=H(wt−m,s2), but does not specify n,m (or how they are chosen), the hash function class, how r1 and r2 map to token groups, and the exact nesting ratio of G2 within G1. The text states G1’s size ratio to R1 is γ:(1−γ), and Equation (8) uses the same γ for G2 within G1, but the method never clarifies whether G2’s size is also γ·|G1| or follows a different ratio. Reproducibility requires precise group-construction rules, including seed control, sampling temperature/top-p settings, and treatment of special tokens.

7) Ambiguous comparison setup in Table 1. The preliminary experiment chooses δ=3.5 for the baseline because higher δ improves ESR, even though Table 1 shows quality deterioration versus δ=3.0. However, Table 1 only reports “win/lose/tie” for text quality and does not report ESR for these δ values. Selecting δ=3.5 to favor ESR while showing only quality numbers risks cherry-picking. Please report ESR and Type I errors for each δ side by side with quality to justify this choice rigorously.

8) Overreliance on LLM-as-a-judge without human evaluation or linguistic analysis. Given the high tie rates and the paper’s own caveats in Section 6, the paper should add at least a small-scale human evaluation or heuristic linguistic metrics that measure fluency and semantic adequacy. Reporting confidence intervals for the GPT-4 win rates in Table 2 would also help.

9) Scope and generality. Experiments use a single model (Llama-2-7b-chat) and a single GPT-4–generated pseudo-instruction dataset. There is no evaluation across models, domains, or languages, nor any mixed-source localization experiment. This limits generalization and makes it hard to assess deployment readiness outside the demonstrated setting.

10) Figure-level insight is limited. Figure 1 gives a clear process illustration, but the paper does not present figures that expose operating characteristics central to the claims, such as:
- z1/z2 distributions by length for watermarked vs. non-watermarked text,
- ROC curves for single vs. nested at different lengths, or
- sensitivity of detection to γ, δ1, δ2.
Such plots would provide direct evidence supporting the core thesis that nesting helps short-segment detection.

11) Notational clarity and minor technical gaps. Equations (5)–(6) define adjusted probabilities for G1\G2 and G2 respectively, but there is no explicit expression for tokens in R1, although it is implied by Equation (4). It would help to state the full piecewise definition of p̂t for clarity and to verify Dtotal normalization. Also, clarify whether sampling uses the adjusted distribution directly or with additional constraints (e.g., top-k, nucleus sampling). 

12) Reproducibility. The dataset is privately generated and not stated to be released; implementation details are insufficient for replication. No code link is mentioned. This is a barrier for ARR/ACL standards.

References to figures/tables/equations:
- Figure 1 usefully illustrates the nested detection pipeline, including visual marking of first-level (light green) versus second-level (deep green) tokens; however, it does not quantify distributional separation or Type I/II error behavior. Adding detection-threshold plots or length-vs-TPR overlays next to Figure 1 would substantiate the paper’s central claim more convincingly.
- Table 1 compares text quality at different δ for the single watermark, but it omits ESR/Type I error at those δ settings. Since δ trades off quality against detection, this table should be extended to include detection metrics to make the baseline choice defensible.
- Table 2 is the main results table. The “Unified” ESR relies on Fisher’s method, which, given dependence between tests, likely inflates performance. Also, without FPR on non-watermarked text, it is impossible to assess whether the gains come at the cost of higher false positives. These omissions limit the weight we can give to the improvements reported.

## Potentially Missing Related Work
1) Liu et al., “A Semantic Invariant Robust Watermark for Large Language Models,” 2024 — Proposes context-aware conditioning that improves robustness to paraphrasing; directly relevant to short-text robustness. Should be discussed in Section 2 and compared experimentally where possible.
2) Liu et al., “Adaptive Text Watermark for Large Language Models,” 2024 — Perturbs only high-entropy distributions and adapts scaling by semantics; pertinent baseline for quality-preserving watermarking on short texts. Add to Related Work and, if feasible, as a baseline in Section 4 (Table 2).
3) Feng et al., “A Certified Robust Watermark For Large Language Models,” 2024 — Provides provable robustness via randomized smoothing; useful contrast for the security/robustness claims in Section 4.4. Cite in Related Work and discuss after Equation (8)/(10) regarding statistical guarantees.
4) Zhao et al., “Efficiently Identifying Watermarked Segments in Mixed-Source Texts,” 2025 — Focuses on segment localization; complementary to this paper’s short-segment detection. Discuss in Related Work and consider as an evaluation setting extension.
5) Chen et al., “Selective Disclosure Watermarking for Large Language Models,” 2026 — Hierarchical payload with access control; conceptually close to multi-key nesting. Discuss in Related Work; contrast with multi-level detection claims in Section 4.4.
6) Wang et al., “Building Intelligence Identification System via Large Language Model Watermarking: A Survey and Beyond,” 2024 — Survey framing watermarking as identification; helpful for situating metrics like ROC/TPR/FPR and system-level deployment considerations. Add to Section 2 to contextualize evaluation.
7) Liu et al., “A Survey of Text Watermarking in the Era of Large Language Models,” 2024 — Comprehensive survey of metrics/threat models; use to motivate missing adversarial/paraphrase evaluations and standardized protocols in Section 4.
8) Xu et al., “TokenMark: A Modality-Agnostic Watermark for Pre-trained Transformers,” 2024 — Model-level watermark with token-level perturbations; contrast in Section 2 to clarify this paper’s scope as output watermarking and whether ideas might extend to model watermarking spaces.
9) Anonymous, “CATMark: A Context-Aware Thresholding Framework for Robust Cross-Task Watermarking in Large Language Models,” 2025 — Dynamic thresholding across heterogeneous tasks; relevant to the fixed-threshold choice θ=4 and short-text calibration. Discuss in Related Work and consider adaptive-threshold analysis in Section 4.2–4.4.

## Comments Suggestions And Typos
Actionable requests that could change my assessment:
- Fix the ESR definition and recompute all values. If ESR is intended to be “one-shot detection success” then it is 1−β, not 1/β. Update Table 2 accordingly and clarify terminology in Section 4.2.
- Address dependence between the two tests. Either justify independence rigorously or replace Fisher’s method with a dependence-aware combination (e.g., Brown’s method) and re-run the unified analysis in Table 2. Report the marginal Type I/II errors for each watermark and for the combined decision rule.
- Report Type I error and ROC/AUC. Add evaluations on non-watermarked text to measure FPR by length and provide ROC curves for single vs nested (for each length). This is crucial to substantiate the paper’s detection claims for short segments.
- Expand baselines. Include at least one adaptive/semantic watermark baseline and, if possible, a certified watermark for robustness contrast. Revisit Table 2 to include these baselines with both detection and quality metrics.
- Add adversarial evaluations. Measure robustness to paraphrase/synonym substitutions and minor edits. Also simulate “first key compromised” scenarios to test the security claim in Section 4.4. Even small-scale controlled experiments would materially strengthen the paper.
- Improve reproducibility. Specify all implementation details: hash function family, mapping from r1/r2 to token sets, n and m, G2’s size fraction relative to G1, sampling settings, seeds, tokenization and special tokens, and release the pseudo-instruction prompts. Provide code or pseudocode for group construction and detection.
- Figures and diagnostics. Add plots of z1/z2 distributions for watermarked vs non-watermarked text, ROC curves by length, and sensitivity analyses for γ, δ1, δ2, and nesting depth (>2). These would turn the conceptual overview of Figure 1 into empirically grounded evidence.

Typos/clarity:
- Section 1: “as the number tokens in the text decreases” → “as the number of tokens …”
- Section 3.1: Clarify whether γ applies identically to G1 vs R1 and to G2 vs G1; currently ambiguous.
- Section 3.2: “two independent tests” — either remove “independent” or justify, given G2⊂G1.
- Section 4.1: “1,000 samples of an English instructions” → “1,000 samples of English instructions.”
- Table 2 header: consider aligning column labels more clearly; the double use of “diff.” for different comparisons can be confusing.

Criteria for score change:
- If the ESR definition is corrected, Fisher’s combination is fixed for dependence, and full Type I/II/ROC analyses with non-watermarked baselines are added, I would consider raising Soundness and Overall Assessment by one full step.
- Adding at least one adaptive/semantic baseline and a paraphrase robustness evaluation would further raise my assessment toward main conference.
- If code and prompts are released and implementation details clarified, I would increase Reproducibility.

## Confidence
4: Quite sure after careful checking — I checked the important points carefully, including equations, tables, and claims about Fisher’s method and ESR. It is unlikely I missed something that would overturn my evaluation.

## Soundness
2.5: Between Poor and Acceptable — Core ideas are reasonable, but there are significant methodological and statistical issues (ESR definition error, unjustified independence for Fisher’s method, missing Type I error/ROC analysis) and limited baselines.

## Excitement
2.5: Between potentially interesting and interesting — Short-text detection is worthwhile and the nested design is intuitively appealing, but the current empirical and statistical gaps limit excitement.

## Overall Assessment
2.5 Borderline Findings: The paper has promise but requires substantial revisions before acceptance. While the nested construction is clear and results are suggestive, the incorrect ESR definition, unjustified use of Fisher’s method under dependence, lack of Type I error/ROC reporting, narrow baselines, and missing adversarial evaluation collectively prevent a confident recommendation. With these issues addressed and reproducibility improved, the work could reach Findings or better.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section is candid about LLM-as-a-judge biases and short-text evaluation difficulty. Additional societal impact discussion would be helpful, for example: risks of false positives on human texts when thresholds are tuned for short outputs, potential misuse scenarios around watermark removal via paraphrasing, and implications of multi-key schemes for privacy and access control if different verifiers hold different keys. Including an explicit failure-mode analysis with who might be harmed by false positives/negatives would strengthen the discussion.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
2.5: Reproducible with difficulty — Several essential implementation details are missing; the dataset is private; no code is provided. With clarified group construction, seeds, and released prompts/code, this could improve to 4.

## Datasets
1: No usable datasets submitted.

## Software
1: No usable software released.