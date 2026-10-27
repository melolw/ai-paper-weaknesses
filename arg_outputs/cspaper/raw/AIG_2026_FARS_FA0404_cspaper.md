# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper introduces Hazard-Signature Tombstones (HST), a commit-time “forget lockout” mechanism for LLM agent memory. When records are deleted due to harmful content, the system extracts discrete hazard signatures, stores them as tombstones, and blocks future writes whose hazard signatures exhibit fuzzy set-containment overlap with any tombstone. The work targets paraphrase re-injection attacks where adversaries reinsert semantically equivalent but lexically different content after deletion. On a MemoryGraft-based setup with 10 poisoned seeds and 50 paraphrases, HST reports PRP@3 = 0.0 and perfect benign recall, outperforming ID-based deletion and retrieval-time filtering, with a reported 3% benign false block rate. The paper attributes the gains to higher hazard-signature stability under fuzzy matching versus exact string matching.

## Summary Of Strengths
- Clear threat model and focused contribution: The paper frames paraphrase re-injection as a concrete post-deletion vulnerability in agent memory and proposes a simple, operational policy to prevent index pollution at commit time.
- Conceptual clarity and interpretability: The move from embedding thresholds to discrete hazard signatures is motivated and yields explainable deny decisions. Equation (1) formalizes the controlled tag space, and Equation (3) states the fuzzy set-containment rule unambiguously.
- Strong headline result on the chosen setup: Table 1 shows HST achieving PRP@3 = 0.0 with Benign Recall@3 = 1.0 and complete write blocking (WriteBlockRate = 1.0), while ID-based deletion deteriorates security and retrieval-time exact matching fails to help.
- Useful architectural articulation: Figure 1 lays out the full pipeline from deletion to commit-time lockout and illustrates where semantic denylisting happens relative to the FAISS index. This will help practitioners implement the policy in production memory stacks.
- Diagnostic analysis of retrieval-time backfill limits: Figure 2 provides a concrete look at why retrieval-time fuzzy filtering can still underperform due to slot wasting, helping to support the paper’s claim that commit-time enforcement preserves retrieval capacity.
- Backend-agnostic direction: Appendix Table 2 indicates findings transfer across two embedding backends, reinforcing that the benefits come from commit-time control, not retrieval modeling.

## Summary Of Weaknesses
1) Narrow and synthetic evaluation scope undermines generality
- The entire empirical story rests on one poisoning corpus (MemoryGraft) and paraphrases generated deterministically by a single LLM (DeepSeek-V3.2), with a fixed five-paraphrases-per-seed recipe. This is a constrained adversary. There is no evaluation against stronger or more realistic adversaries, such as distributed stealth injections, cooperative multi-record triggers, or query-only injections evolved over time.
- As a result, it is unclear whether the 0.0 PRP@3 result survives more adaptive paraphrase strategies that aim to manipulate the hazard tagger.

2) Hazard taxonomy is narrow, ad hoc, and domain-specific
- Equation (1) defines a small tag set focused on a “data analysis agent” context. There is no justification for coverage, no ablation on taxonomy granularity, and no guidance on extending to other domains. The paper’s main claim that discrete signatures are stable could be an artifact of a coarse taxonomy.

3) Dependence on a single LLM classifier with temperature=0
- Hazard signatures are produced by DeepSeek-V3.2 with deterministic decoding. The method’s integrity hinges on the classifier’s calibration and invariance to adversarial paraphrase. There is no robustness study across multiple safety classifiers, no inter-annotator reliability against human labels, and no assessment of targeted evasion (e.g., phrasing to flip a specific hazard label on or off).

4) Fuzzy matching rule is underspecified and may be both too permissive and too brittle
- Equation (3) adopts subset/superset containment as the decision criterion. The rule is not parameterized by overlap thresholds (e.g., Jaccard ≥ τ), which would likely be necessary in larger taxonomies to avoid spurious matches. The paper does not analyze failure cases where small overlaps cause unjustified blocks or where near-miss rephrasings avoid containment.
- There is no complexity analysis or scalability discussion for large tombstone sets in long-lived systems.

5) Limited and potentially confounded metrics
- HS-Stability is central to the argument, yet its ground truth is model-dependent. The “stability” comparison between exact and fuzzy matching is tautological without an external notion of correctness. If the classifier flips tags under paraphrase, fuzzy set containment will, by construction, look “stable.”
- PRP@k is reported, but no confidence intervals, runs with different seeds, or statistical significance are provided. With small query counts (12 queries), results could be sensitive to minor ranking noise.

6) Incomplete baselines and weak comparisons
- Table 1 omits any write-path provenance or consensus-based validation baselines; only retrieval-time filtering is considered. Many contemporary defenses emphasize provenance, randomized retrieval smoothing, or trust-aware gating, which are absent. This limits claims that commit-time HST is preferable in practice.
- The “ID-delete makes things worse” result may be specific to the experimental flooding protocol; other operational deletion workflows might include rate limits or moderation steps that change the picture.

7) Risk of circularity between hazard signatures and evaluation
- The same hazard schema underpins both the deny decisions and the retrieval-time filtering baselines. Without an independent measurement of “poisonedness,” improvements may be partially explained by alignment between the decision rule and the evaluation probe, rather than robust security improvements.

8) Reproducibility gaps and missing operational details
- Although a code URL is provided, the paper does not enumerate prompt templates, the exact JSON schema, or the signature post-processing rules. The “3% false positive” is reported without specifying which benign cases were blocked or whether human adjudication confirmed they were truly benign.

9) Figure and table interpretation gaps
- Figure 2 attributes the 3× improvement to commit-time prevention, but it compares “B with backfill δ=6” to “C = 3.00,” without exploring intermediate δ or alternative retrieval pipelines. A more thorough sweep would clarify how far retrieval-time remedies can be pushed before hitting diminishing returns.
- Table 2 shows minor differences for ID-delete across embeddings, but it does not report false positive rates or write-block rates per backend, so backend-agnostic claims are only partly supported.

10) Security framing lacks adaptive adversaries and evasion analysis
- The paper does not probe attacks designed to misclassify hazard signatures (e.g., prompt-injection-like phrasing that reframes “remote_exec” as “sanitized subprocess”). Without targeted evasion tests, the advertised stability may not hold in the face of active attackers.

Figure-specific comment
- Figure 1 effectively communicates the three-stage pipeline and, importantly, highlights where commit-time lockout interposes before index insertion. However, it also exposes a design assumption: that a single-pass LLM hazard classifier is sufficiently reliable to gate writes. The figure would benefit from showing optional consensus or provenance layers that could harden this step.
- Figure 2’s bars are central to the slot-waste claim. Yet, the y-axis aggregates “Avg. Results per Query” without error bars or distributional statistics. The visual supports the narrative, but as presented, it may overstate robustness of the finding.

Table-specific comment
- Table 1 is the linchpin. It demonstrates the failure of exact matching and the success of fuzzy matching at both retrieval- and commit-time. Still, since the same classifier creates hazard signatures used to compute HS-Stability, the table risks conflating classifier-induced variance with actual robustness. It would be more convincing to include a human-adjudicated “is poisoned” label for a random subset, or to compute PRP with a classifier trained independently of the one generating tombstone tags.
- Table 2 is useful for sanity checking retrieval-backend dependence; however, there is no reporting of false-positive or write-block statistics across backends, which would be important for understanding end-to-end operational variance.

## Potentially Missing Related Work
1) Karamchandani et al., “Your Agent’s Memories Are Not Its Own: Forged Reasoning Attacks on LLM Agent Memory and Defenses,” 2026 — Targets poisoning of stored rationales and proposes SENTINEL. Directly relevant as an attack surface distinct from simple experience records; should be discussed in Related Work and compared conceptually to HST’s commit-time denylisting, including whether HST signatures can capture rationale forgeries.

2) Dash et al., “From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents,” 2026 — Offers a taxonomy and MPBench. The taxonomy can situate paraphrase re-injection among broader classes, and MPBench could serve as an additional evaluation suite. Add to Section 2 and consider as an alternative benchmark in Section 4.

3) Sunil et al., “Memory Poisoning Attack and Defense on Memory Based LLM-Agents,” 2026 — Proposes input/output moderation and trust-aware sanitization as defenses. These are relevant write-path or gatekeeping baselines that should be included alongside HST in Table 1.

4) Yan et al., “MemIncept: Steering LLM Agents via Cooperative Stealthy Memory Injections,” 2026 — Presents coordinated multi-record attacks with benign-looking content. Important for testing whether fuzzy hazard-signature containment still works when hazards are distributed across records. Discuss in Section 2 and propose as a harder adversary in Section 4.

5) Ouyang et al., “MemLineage: Lineage-Guided Enforcement for LLM Agent Memory,” 2026 — Introduces provenance and chain-of-custody constraints. This is a complementary defense class that should be contrasted with HST’s semantic approach in Section 2 and possibly included as a conceptual baseline.

6) Sharma et al., “SMSR: Certified Defence Against Runtime Memory Poisoning in Persistent LLM Agent Systems,” 2026 — Combines signed memory with smoothed retrieval, offering formal robustness bounds. Important comparative point on guarantees vs. heuristic semantic tombstones. Cite after Section 3.5 and discuss tradeoffs.

7) Wu et al., “Forget to Improve: On-Device LLM-Agent Continual Learning via Budget-Curated Memory,” 2026 — Studies budgeted forgetting that can reduce poisoning. Relevant to extending HST with resource-aware policies. Discuss in Limitations/Future Work.

8) Wang et al., “Unveiling Privacy Risks in LLM Agent Memory,” 2025 — Addresses memory extraction risks and shows how memory design affects leakage. Relevant for discussing the privacy implications of storing persistent tombstones. Add to Section 2 and the societal impact discussion.

9) Xiong et al., “How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior,” 2025 — Characterizes how deletion/addition reshapes agent behavior. Relevant for discussing the potential performance side effects of aggressive commit-time blocks. Add to Section 2 and Discussion.

10) “An Empirical Study of Memory Poisoning Defenses for LLM Agents,” 2026 — Benchmarks multiple defenses; HST should be positioned against such comparative frameworks. Add to Section 2 and consider aligning metrics/experimental setup.

## Comments Suggestions And Typos
Actionable suggestions:
- Stronger adversary evaluation
  - Include adaptive paraphrase attacks targeted to flip or obscure specific hazard tags, cooperative multi-record injections, and query-only injections evolving over multiple sessions. Report PRP@k and Benign Recall@k under these settings.
- Classifier diversity and reliability
  - Evaluate hazard-signature extraction with multiple LLMs and, for a subset, human adjudication to estimate precision/recall of hazard labels. Report inter-rater agreement and show how HS-Stability varies with classifier choice.
- Taxonomy analysis
  - Provide a principled process for building the hazard schema. Run ablations on taxonomy granularity and include overlap-threshold variants of Equation (3), such as Jaccard ≥ τ, to examine false positive/negative tradeoffs.
- Statistical rigor and ablations
  - Add confidence intervals over multiple random query sets and multiple paraphrase seeds. Extend Figure 2 to sweep δ more finely and report where retrieval-time filtering saturates. Include cost/latency overhead for commit-time checks.
- Independent poisonedness measurement
  - Avoid circularity by evaluating PRP with a detector independent of the one that produced tombstone tags. Alternatively, use human labels on a stratified sample to validate Table 1’s core claims.
- Operational considerations
  - Discuss scalability, tombstone expiration, and remediation pathways for false positives. Analyze worst-case growth in tombstone sets and the impact on throughput.

Typos and minor issues:
- Section 4.1: “data analysis agent” context could be clarified earlier when introducing the hazard taxonomy in Section 3.2.
- Table 1 caption: consider clarifying that BenignFalseBlock is measured against the benign set and whether human adjudication validated those cases.
- Throughout: occasionally inconsistent hyphenation for “backfill” and “write-path;” standardize.

Criteria that could raise my score:
- Adding at least two stronger adversary settings with convincing results, plus classifier-diversity experiments with either human adjudication or an independent detector validating PRP reductions.
- A taxonomy ablation with thresholded set-overlap variants and a clear false-positive analysis on benign corpora from a different domain.
- Inclusion of at least one provenance- or trust-aware baseline and one randomized retrieval defense, compared on the same setup in Table 1.

## Confidence
4: Quite sure after careful checking; unlikely I missed something that would overturn the evaluation.

## Soundness
3: Acceptable. The study supports its main claims on a limited setup, but breadth and robustness are insufficient for a strong rating.

## Excitement
2.5: Between potentially interesting and interesting. The idea is straightforward and practically relevant, but the current empirical scope limits excitement.

## Overall Assessment
2.5 Borderline Findings: The work has promise and a clean, implementable idea with clear diagrams and quantitative evidence on a single setup, but it needs broader, stronger evaluation, better baselines, and robustness analysis before main-track consideration.

## Best Paper Justification
N/A

## Limitations And Societal Impact
- The paper briefly notes false positives and overhead. Additional impacts to discuss:
  - Privacy and persistence: tombstones store semantic summaries of harmful content, which may itself encode sensitive behavior; retention policies and access controls should be specified.
  - Chilling effects and user agency: commit-time blocks based on fuzzy set overlap may suppress legitimate, safety-critical variation if the taxonomy is coarse or mis-specified.
  - Domain transfer risk: applying a data-analysis-centric schema to other domains could misclassify benign patterns, especially in multilingual or low-resource contexts.
  - Dual use: detailed denylisting approaches could be probed by adversaries to reverse-engineer hazard schemas, which might facilitate evasive paraphrases unless multiple layers of defense are applied.

Constructive suggestion: include a privacy section describing tombstone storage, retention, and access policies; quantify cost–benefit tradeoffs for false positives across domains; and outline a layered defense strategy that combines HST with provenance and runtime verification.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: Key components are described, and a code link is provided. Still, precise prompts, label post-processing, and adjudication details should be fully enumerated.

## Datasets
1 No usable datasets submitted: The paper reuses MemoryGraft; no new dataset is provided.

## Software
3 Potentially useful: The approach is simple and code is reportedly available, which can aid reproduction and extension, though packaging and documentation details are not described.