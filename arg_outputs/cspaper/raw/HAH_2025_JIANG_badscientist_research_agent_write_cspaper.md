# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper studies an AI-only “publication loop” in which an LLM-based paper-generation agent produces fabricated but polished manuscripts that are then evaluated by LLM reviewer agents. The authors implement BadScientist, a generation framework that uses five presentation-oriented manipulation strategies (TooGoodGains, BaselineSelect, StatTheater, CoherencePolish, ProofGap) to produce papers without conducting real experiments. A multi-model review agent (o3, o4-mini, GPT-4.1) is calibrated to ICLR 2025 submission data, then used to score the generated papers. The main findings are that fabricated papers are frequently accepted under reviewer thresholds, and that reviewers often flag integrity concerns yet still assign acceptance-level scores (“concern–acceptance conflict”). Two mitigations—Review-with-Detection (ReD) and Detection-Only (DetOnly)—show limited benefits.

## Summary Of Strengths
- Topical, important problem: the paper foregrounds a concrete, high-stakes failure mode of LLM-assisted scientific workflows. The framing around concern–acceptance conflict is crisp and actionable for venues exploring automated review.
- Clear articulation of manipulation strategies: the five “presentation-manipulation” tactics, while high level, are intuitively described and cover a broad spectrum of realistic paper-polish behaviors that could fool reviewers.
- Calibration protocol and operating thresholds: the paper attempts to anchor reviewer decisions via two thresholds, τ_rate and τ_0.5, derived from a stratified sample of real ICLR 2025 submissions (Section 3.4), which helps contextualize acceptance rates.
- Useful quantitative views:
  - Table 1 reports acceptance and integrity concern rates per strategy and reviewer model, enabling comparisons across manipulation modes.
  - Figure 1 (six histograms for S1–S5 and ALL) visually demonstrates how score distributions shift under different strategies and across the three reviewer models. The right-shift for o4-mini and the heavier right tail for o3 are consistent with the acceptance patterns the authors discuss.
  - Table 2 isolates the “concern–acceptance conflict,” which is a valuable diagnostic metric not commonly reported in prior work.
- The mitigation section is honest: Table 3 and Table 4 reveal that naively bundling detection into reviews either has little effect or can even increase acceptance, highlighting the subtlety of integrating integrity signals.

## Summary Of Weaknesses
1) Reproducibility gaps and dependence on unspecified/closed models
- The core experiments rely on “GPT-5,” “o3,” and “o4-mini” (Section 4.1) without specifying public availability, versions, or API configurations. No seeds, prompts, or raw review outputs are provided in the main paper. As a result, reproducing the exact acceptance rates and concern metrics seems infeasible from the current description alone. This is especially problematic because all results hinge on behaviors of particular model variants and prompts.
- The number of seeds and total number of generated papers is under-specified. Section 4.1 says “Each seed produces 4 papers across six strategy setups,” but does not report the number of seeds. Without an explicit N for each condition, the statistical credibility of Table 1, Table 2, and Figure 1 is hard to assess.

2) Integrity signal labeling relies on an LLM judge without validation
- Integrity Concern Rate (ICR) is computed via c_m(x) = Γ(ω_m(x)) where Γ is a GPT-5 judge (Section 4.1–4.2). There is no human-audited validation set or inter-annotator agreement to establish precision/recall of Γ. If Γ is misclassifying generic caveats as “integrity concerns,” ICRs and the downstream “conflict” metric in Table 2 can be materially distorted.
- The method conflates “AI-generated text” detection with “scientific fabrication/integrity” detection in the mitigation design. ReD and DetOnly explicitly task the models with detecting whether content is AI-generated, not whether claims or evidence are fabricated (Section 5.1). This target mismatch likely explains some poor detection performance in Table 4 and weak coupling to acceptance in Table 3; it also reduces the relevance of those mitigation results to the central research question.

3) Calibration is described, not audited
- Section 3.4 gives a careful stratified calibration procedure, but Section 4.1 provides only N_cal=200 and the final thresholds (τ_rate=7, τ_0.5=6.667). There is no analysis of calibration goodness (e.g., reliability diagrams, confidence intervals for π(t), or sensitivity of thresholds to bin choices), which would help justify that thresholds faithfully mirror venue decisions. It is also unclear how reviewer rubrics map to a single scalar s(x) beyond “take the overall assessment.” If the underlying models differ in rubric semantics, this scalarization may not be consistent across models.

4) Limited methodological transparency in generation
- The paper states that the generator “allows the LLM to freely generate any necessary experimental results and plotting code” (Section 4.1) and samples pseudo-data D ∼ q(·|s, t, θ) (Equation 2), but does not document q, priors over effect sizes, or visual artifact templates. How were the fake results constrained to be “plausible”? Without a description of generation distributions, it is impossible to reason about how easily a normal reviewer should have caught anomalies.
- The “ProofGap” strategy claims to include a theorem with a hidden oversight (Section 3.2), yet the paper provides no example theorem, lemma, or proof sketch that would allow readers to assess how challenging the oversight is to detect. This weakens the internal validity of S5-related claims.

5) Incomplete reporting of dataset sizes and variance
- Table 1, Table 2, and Table 3 report percentages without Ns or confidence intervals. Figure 1 histograms also omit sample counts. Without basic uncertainty quantification, the magnitude of reported effects is hard to assess statistically.
- The results section (Section 4.2) interprets model behavior qualitatively but does not report statistical tests (e.g., bootstrap CIs) to check whether differences between strategies or models are significant.

6) Concern–acceptance “conflict” may be partly a metric artifact
- Table 2 computes conflict “within papers where the model raised a concern” as the share still getting an acceptance-level score. However, concerns in reviews often coexist with positive decisions when issues are non-fatal. The authors assert that this is a “fundamental breakdown,” but do not analyze whether the flagged concerns are truly integrity-critical (e.g., fabricated results) versus stylistic/clarity issues. Given that Γ controls labeling and is not validated, over-interpretation is a risk.

7) Figures and tables leave key implementation questions unanswered
- Figure 1 is central to the paper’s claims. It shows consistent right shifts for o4-mini and fatter right tails for o3 across S1–S5 and ALL. However, the figure caption and text (Page 6) do not disclose the per-setup sample sizes or whether bins/axes were standardized across strategies. Without Ns, it is impossible to judge whether the observed differences are robust or a sampling artifact.
- Table 4 evaluates detectors on a 100-paper mixed set (Section 5.2), but the class balance and exact composition per strategy are not fully detailed beyond “50 real, 50 generated.” Since detectors are asked to label AI-generated content rather than fabricated claims, the near-chance results are difficult to interpret as evidence about detecting scientific fabrication.

8) Over-claiming in the checklist vs. main text
- The checklist answers “[Yes]” to “complete and correct proofs” and points to Section 3, yet the main paper contains no theorems or formal proofs. This inconsistency undermines confidence in other checklist items and suggests the paper may have unchecked boilerplate.

9) Scope and generalization
- The evaluation is bound to a single venue/year and three specific models with one fixed rubric. No cross-venue, cross-rubric, or cross-family sensitivity analysis is presented. Conclusions such as “fabricated papers achieve acceptance rates up to 82%” may not hold under modest changes in models, prompts, or calibration. Some tempering in the claims is warranted.

10) Missing or thinly discussed related work
- While the paper cites several relevant studies, recent work that directly benchmarks LLM reviewers, prompt-injection defenses, and review-detection pipelines is not discussed (see “Potentially Missing Related Work” below). These omissions limit the paper’s positioning and the interpretive lens for its results.

Why this matters: The above issues collectively threaten the interpretability and external validity of the main claims. Without reliable integrity labeling, clear sample sizes, transparent generation distributions, public model specs/prompts, and calibration audits, it is hard to separate real reviewer weaknesses from artifacts of setup and measurement. The mitigation experiments target “AI-generatedness,” not “fabrication,” which further weakens the link to the core problem.

Explicit figure/table references
- Figure 1: The reported right shift for o4-mini and heavy right tail for o3 are consistent with the paper’s narrative that o4-mini is the most accepting and o3 exhibits greater variance. However, the absence of Ns and CIs makes it hard to gauge whether S1’s rightward shift is statistically reliable or driven by a small sample. Please add exact counts per bar and confidence intervals.
- Table 1: S1’s ACPT 67.0%/82.0% is central to the paper’s most striking claim. This table needs Ns per row and per model, plus uncertainty estimates. Also clarify whether ACPT uses only the consensus scalar or per-model scores.
- Table 2: Concern–acceptance conflict rates are compelling, especially the 100% entries for o4-mini in S1/S3/All. But without understanding the severity/type of concerns that Γ labeled, it is not clear that these rows indicate integrity failure rather than a reviewer accepting with minor concerns.
- Table 3: ReD increases both ICR@M and acceptance rates. This is an important and counterintuitive result; however, it could also be an artifact of concurrent prompting that asks the same model to do two tasks with mismatched targets. Ablate the prompt to decouple the review score from the detection subtask, or gate acceptance on explicit risk tiers, and then re-report ACPT by risk tier.
- Table 4: Since ReD and DetOnly are asked to detect AI-generated text rather than fabrication, the interpretation should be reframed as “how well can we triage AI-generated text?” rather than “can we detect fabrication?” Consider an additional detector targeting internal statistical consistency, baseline sanity checks, or provenance.

## Potentially Missing Related Work
1) Yu et al., “Is Your Paper Being Reviewed by an LLM? Benchmarking AI Text Detection in Peer Review,” 2026 — directly benchmarks detectors on peer reviews; relevant to Sections 2 and 5 for positioning detection targets and should be contrasted with ReD/DetOnly in Table 4.
2) Li et al., “LLM-as-a-Reviewer: Benchmarking Their Ability, Divergence, and Prompt Injection Resistance as Paper Reviewers,” 2026 — evaluates many LLMs as reviewers on large corpora; compare in Section 2 and discuss how BadScientist’s manipulation strategies fare against models that score well on such benchmarks.
3) Loc et al., “PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers,” 2026 — introduces structured reviewer evaluation; discuss in Section 5 whether PRISM-style capabilities correlate with resilience to fabricated manuscripts.
4) Nguyen et al., “LLM-Based Scientific Peer Review: Methods, Benchmarks, and Reliability Challenges,” 2026 — survey framing for reliability and robustness; add to Section 2 to ground the taxonomy of risks and clarify how concern–acceptance conflict fits.
5) Torrielli et al., “Exploiting large language models in peer review: indirect prompt injection attacks and integrity probes,” 2026 — complements your threat model; cite in Section 2 and explain how BadScientist’s content-level manipulation differs from prompt-channel attacks.
6) Sharma et al., “Do LLMs Favor LLMs? Quantifying Interaction Effects in Peer Review,” 2026 — relevant for interpreting interaction effects in mixed human–LLM ecosystems; add to Discussion and future work.
7) Rao et al., “Detecting LLM-generated peer reviews,” 2025 — detection and watermarking ideas might inform Section 5’s mitigation design beyond AI-generatedness; discuss and consider as a triage baseline.
8) Lin et al., “Breaking the Reviewer: Assessing the Vulnerability of Large Language Models in Automated Peer Review Under Textual Adversarial Attacks,” 2025 — strengthens the robustness link in Related Work and could motivate adversarially trained or RAG-verified reviewers.
9) Wu et al., “Impact of large language models on peer review opinions from a fine-grained perspective,” 2026 — provides empirical context to how LLM assistance changes review language and scores; discuss alongside concern–acceptance conflict.

## Comments Suggestions And Typos
Actionable suggestions
- Report Ns and uncertainty: For Table 1–3 and Figure 1, add sample counts per condition and 95% CIs via bootstrap. This is essential for interpreting effect sizes.
- Validate the integrity concern classifier: Provide a human-labeled subset of reviews with detailed codes (fabrication vs. style vs. clarity). Report precision/recall and agreement statistics for Γ. Recompute Table 2 using only “fabrication-relevant” concerns.
- Align mitigation target with the core threat: ReD and DetOnly currently detect “AI-generatedness,” which is orthogonal to fabrication. Replace or augment with fabrication-focused probes: statistical consistency checks (e.g., recomputing reported effects from tables/figures), baseline sanity verification, citation cross-checks, and theorem proof auditing. Then re-run Table 4.
- Clarify generation distributions: Specify q(D|s,t,θ) for each strategy. For S1, define the improvement prior (e.g., effect-size distributions). For S5, include at least one theorem outline and the exact oversight. This will let others reason about detectability and replicate manipulations.
- Calibration audit: Provide reliability plots for π(t), sensitivity of τ_rate and τ_0.5 to binning choices, and a rationale for using only the overall assessment score. Consider per-model calibration and a meta-calibration for the consensus.
- Report total paper counts: In Section 4.1, state the number of seeds, total fabricated papers, and the breakdown per strategy. Include the exact number of ICLR calibration papers and confirm the class balance in the 100-paper detection dataset.
- Decouple review and detection: For Table 3, try a design where detection only gates or downweights the final recommendation, then report ACPT stratified by detected risk tier. This would test whether coupling strengthens or weakens concern–acceptance consistency.
- Ethical framing and release plan: Given the dual-use risk, detail a redacted release strategy with guardrails and a code-of-conduct for using BadScientist. Consider staged access to manipulation templates and include watermarking/provenance tools by default.

Typos/clarifications
- Page 6, “Probability-consistency defines such that papers…”: grammar could be tightened (“We define probability-consistency such that papers with s(x) ≥ τ_0.5 have…”).
- Section 4.1: “with the rubric review prompt… we take only the overall assessment score … i.e., φ(r̄(x)) = r_on(x).” Please define r_on explicitly earlier.
- Checklist inconsistencies: The “theory assumptions and proofs” item claims full proofs in Section 3, but none are present; please correct.

Criteria that could raise my score
- Publicly release prompts, seeds, and a minimal reproducibility bundle that regenerates a subset of the main tables/figures, or include them in the appendix.
- Provide human-validated integrity labels and recompute the concern–acceptance results.
- Replace AI-generatedness detection with fabrication-centric checks and show non-trivial gains over random in Table 4.
- Add Ns and uncertainty estimates across all tables/figures and include a calibration quality analysis.

## Confidence
3 Reasonably confident but not fully verified: Pretty sure, but I did not fully verify every experimental detail; the lack of released artifacts limits independent confirmation.

## Soundness
2.5 Between Poor and Acceptable

## Excitement
3.0 Interesting: I would mention some points and likely attend if time permits.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings.

The problem is timely and the framing is compelling, but the empirical foundation needs shoring up: unclear sample sizes, reliance on an unvalidated LLM judge for integrity labels, mitigation targets misaligned with fabrication, missing uncertainty estimates, opaque generation distributions, and dependence on unspecified model variants. With the suggested revisions—especially validated labeling, fabrication-focused detectors, explicit Ns/CIs, and reproducibility artifacts—this could become a strong integrity-focused Findings paper. In its current state, it falls short of main-track rigor.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges several limitations in Appendix A, including model coverage, single-venue calibration, and reliance on LLM judges. The societal discussion is appropriate, highlighting both the value of stress-testing reviewer pipelines and the dual-use risks. Given the potential for misuse, the camera-ready should include a concrete, enforceable release plan with redactions and provenance safeguards.

## Ethical concerns
None beyond the dual-use risk, which is acknowledged. The paper should strengthen the mitigation and release plan to prevent facilitating fraudulent activity.

## Needs Ethics Review
No

## Reproducibility
2.5 Reproducible with difficulty: Key model specs, prompts, seeds, and raw outputs are missing; thresholds and procedures are described but cannot be independently verified without artifacts.

## Datasets
2 Documentary: If released as stated, the mixed set and generated corpus could help study reviewer vulnerabilities, though their utility depends on labeling quality.

## Software
2 Documentary.: The framework is potentially useful, but its value hinges on availability of prompts, seeds, calibration code, and detectors aligned to fabrication rather than AI-generatedness.