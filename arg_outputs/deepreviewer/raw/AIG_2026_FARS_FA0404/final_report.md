## Summary
This paper introduces Hazard-Signature Tombstones (HST), a commit-time forget lockout policy for LLM agent memory that prevents paraphrased re-injection of deleted harmful content. The method extracts discrete hazard signatures from deleted records using LLM-based classification over a fixed 5-label taxonomy, stores them as tombstone keys, and blocks future writes whose hazard sets exhibit fuzzy set-containment with tombstoned signatures. Evaluated on a paraphrase re-injection benchmark using the MemoryGraft corpus, HST reduces poisoned retrieval proportion from 0.94 (ID-delete baseline) to 0.0 while maintaining perfect benign recall and achieving only 3% false positive rate on the tested benign records.

The core novelty lies in applying distributed-system tombstone concepts to LLM agent memory security with fuzzy semantic matching, shifting defense from retrieval-time filtering to commit-time lockout. The paper makes a compelling case that naive ID-based deletion can worsen poisoning attacks when paraphrased variants flood the index, and that retrieval-time filtering suffers from slot wasting due to index pollution.

Key concerns include: (1) the narrow 5-label hazard taxonomy limits generalizability beyond the data analysis domain, (2) the evaluation uses only one corpus, one paraphrase generator, and single-run results without variance reporting, (3) the related-work section omits recent defenses such as MEMSAD and MemAudit, and (4) the fuzzy set-containment criterion has a partial-overlap evasion gap that could be exploited by adaptive adversaries.

## Strengths
1. **Compelling problem identification.** The paper correctly identifies that naive ID-based deletion in LLM agent memory systems is vulnerable to paraphrase re-injection attacks. The counterintuitive finding that ID-delete worsens the attack (PRP@3 from 0.67 to 0.94) provides strong motivation and is effectively demonstrated.

2. **Novel commit-time defense paradigm.** Applying distributed-system tombstone concepts to LLM agent memory with fuzzy semantic matching represents a genuine conceptual shift from retrieval-time filtering to commit-time lockout. The "slot wasting" argument for why commit-time is superior to retrieval-time is insightful and well-supported by the backfill ablation.

3. **Clean and interpretable method design.** The discrete hazard signature approach with fuzzy set-containment matching (Eq. 3) is mathematically clean, easy to understand, and provides explainability (each blocked write can be traced to specific hazard labels). This is a practical advantage over embedding-based defenses that require threshold calibration.

4. **Well-structured experiments.** The experimental design with four progressively stronger baselines (No-Forget, ID-Delete, Retrieval-Time Exact, Retrieval-Time Fuzzy) provides clear comparative evidence. The backfill ablation (Figure 2) effectively demonstrates the fundamental limitation of retrieval-time filtering.

5. **Candid limitations and future work.** The Conclusion honestly identifies three specific limitations (FPR tuning, LLM call overhead, domain-specific taxonomy) and proposes concrete future directions (adaptive adversaries, efficiency optimization, production integration). This improves the paper's scientific credibility.

## Weaknesses
1. **Narrow hazard taxonomy limits generalizability (Major).** The 5-label hazard taxonomy ({skip validation, remote exec, external upload, force success, disable audit}) is explicitly designed for data analysis agent experiences and may not cover hazards in other domains (e.g., privilege escalation, data exfiltration, social engineering). This means HST is a domain-specific solution rather than a general-purpose defense. The paper does not sufficiently discuss how the taxonomy could be adapted for broader deployment contexts.

2. **Single-run evaluation without variance reporting (Major).** The experiments use deterministic decoding (temperature=0) for paraphrase generation and report single-run results without specifying random seeds or providing mean±std over multiple runs. Since LLM-based paraphrase generation and retrieval results can be sensitive to initialization, the lack of multi-seed reporting limits confidence in the reproducibility of the PRP@3=0.0 result.

3. **Related work omits recent critical defenses (Major).** The Memory Defenses paragraph discusses A-MemGuard and VIGIL but omits recent work such as MEMSAD (gradient-coupled anomaly detection for memory poisoning) and MemAudit (post-hoc causal auditing of poisoned memories). These papers represent the strongest adjacent defense approaches and should be acknowledged to properly position HST's novelty boundary.

4. **Partial-overlap evasion gap in fuzzy set-containment (Major).** The fuzzy set-containment criterion (Eq. 3) blocks writes when their hazard sets are subsets or supersets of tombstoned signatures. However, it does not block writes with partial overlap that satisfy neither subset relation. An adaptive adversary could generate paraphrases that distribute harmful intent across different hazard categories, producing sets that overlap but evade containment checks. This limitation is not discussed.

5. **Scope overclaiming on "complete poisoned elimination" (Minor).** The phrase "complete poisoned elimination" is used in the abstract, contributions, and conclusion without consistent scope qualification. The result holds for 50 paraphrases from one generator (DeepSeek-V3.2) on one corpus (MemoryGraft) with one embedding backend. Broader claims about general applicability are not validated and could mislead readers about deployment readiness.

## Key Issues
| Issue | Risk Level | Root Cause | Recommended Fix | Expected Benefit | Priority |
|---|---|---|---|---|---|
| Narrow hazard taxonomy limits generalizability | Major | 5-label taxonomy designed only for data analysis domain | Discuss taxonomy adaptation strategy and bound scope claims | Prevents overclaiming; guides future extension work | P0 |
| Single-run evaluation without variance reporting | Major | No random seed specified; no multi-seed std reported | Add seed info; report mean±std over ≥3 runs if feasible | Improves reproducibility and statistical confidence | P0 |
| Related work omits MEMSAD and MemAudit | Major | Incomplete literature coverage in Memory Defenses paragraph | Add 1-2 sentences positioning HST vs. these defenses | Strengthens novelty boundary and reviewer confidence | P1 |
| Partial-overlap evasion gap in Eq. (3) | Major | Set-containment does not handle partial overlap cases | Acknowledge limitation; propose Jaccard or min-overlap check | Closes potential adversarial evasion path | P1 |
| Scope overclaiming on "complete elimination" | Minor | Results bounded to one corpus/paraphrase generator | Add "on evaluated benchmark" qualifier consistently | Maintains scientific defensibility | P2 |

**Ranking rationale:** The top two issues (P0) directly affect the validity and reproducibility of the core experimental claims. The narrow taxonomy (P0) limits the research value of the method beyond the evaluated domain. The single-run evaluation (P0) prevents readers from assessing result stability. Issues 3-4 (P1) affect novelty positioning and method robustness. Issue 5 (P2) is a writing precision concern that does not change scientific content.

## Actionable Suggestions
1. **Bound the hazard taxonomy scope (Section 3.2).** Add one paragraph discussing the domain-specific nature of the 5-label taxonomy and how it could be extended for other domains. For example: "This taxonomy is tailored to the MemoryGraft evaluation domain. Broader taxonomies covering hazards such as privilege escalation, data exfiltration, and social engineering would be required for general-purpose agent memory security, and we discuss this adaptation challenge in Section 5."

2. **Add reproducibility details (Section 4.1).** Specify the random seed used for paraphrase generation and retrieval experiments. If multi-seed runs are feasible, report mean±std over ≥3 seeds for PRP@3 and Benign Recall@3. If not, explicitly note the single-run limitation: "All reported results are from a single deterministic run; multi-seed variance analysis is left to future work."

3. **Expand Related Work (Section 2, Memory Defenses paragraph).** Add 1-2 sentences acknowledging MEMSAD (Gowda, 2026) and MemAudit (Tan et al., 2026), then explicitly differentiate HST's commit-time lockout approach from their detection/auditing paradigms. This strengthens the novelty boundary.

4. **Acknowledge the partial-overlap evasion gap (Section 3.5).** After Eq. (3), add one paragraph: "One limitation of set-containment matching is that it does not block writes whose hazard sets partially overlap with tombstones without satisfying subset relations. An adaptive adversary could potentially exploit this gap by distributing harmful intent across different hazard categories. Future work may explore complementary checks such as Jaccard similarity thresholds or minimum overlap counts."

5. **Consistently qualify "complete elimination" claims.** In the abstract, contributions (C3), and conclusion, add "on the evaluated benchmark" or "on the tested corpus" to the phrase "complete poisoned elimination" to prevent scope overgeneralization.

6. **Add cross-reference in Introduction (Page 1).** In the paragraph discussing retrieval-time filtering limitations, reference the empirical evidence from Section 4.5: "reducing effective capacity even when filtered from final results—as we quantify in Section 4.5, where up to 94% of retrieval slots are wasted without aggressive backfill."

## Storyline Options + Writing Outlines
The current introduction follows a clear arc: Big Picture (agent memory) -> Gap (paraphrase re-injection) -> Solution (HST) -> Evidence preview. This structure is effective and does not require major reordering. The primary improvements are scope qualification, claim bounding, and cross-referencing.

## Priority Revision Plan
Revisions should be executed in three stages, prioritizing validity-critical and novelty-positioning changes over writing polish.

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1: Main Comparison | HST outperforms retrieval-time and ID-delete baselines on paraphrase re-injection | MemoryGraft corpus (100 benign + 10 poisoned); 50 paraphrases (DeepSeek-V3.2, temp=0); 4 baselines; BGE-M3 embeddings; k=3 | PRP@3, Benign Recall@3, WriteBlockRate, BenignFalseBlock, HS-Stability | HST: PRP@3=0.0, Recall=1.0, FPR=0.03 | Yes, on evaluated benchmark | Single corpus, single paraphrase generator, single-run |
| E2: Backfill Ablation | Retrieval-time filtering suffers from slot wasting even with aggressive backfill | Same setup as E1; B-exact and B-fuzzy with δ=0, δ=6 | Results recovered per query (avg) | δ=0: 0.17 results; δ=6: 1.0 results; HST: 3.0 results | Yes, supports commit-time advantage | Only tests δ=0 and δ=6 |
| E3: Embedding Ablation | HST advantage is retrieval-backend-agnostic | Same setup as E1; Qwen3-Embedding-4B (2560-dim) instead of BGE-M3 | PRP@3, Benign Recall@3 | Condition ordering C > B > A preserved; identical PRP@3=0.0 for B and C | Yes, across two backends | Only two embedding models tested |

## Novelty Verification & Related-Work Matrix
The manuscript makes three core contribution claims (C1-C3) related to the paraphrase re-injection problem, the hazard-signature stability, and the commit-time elimination performance.

## References
[1] A-MemGuard: A Proactive Defense Framework for LLM-Based Agent Memory 2510.02373

[2] MEMSAD: Gradient-Coupled Anomaly Detection for Memory Poisoning in Retrieval-Augmented Agents 2605.03482

[3] MemAudit: Post-hoc Auditing of Poisoned Agent Memory via Causal Attribution and Structural Anomaly Detection 2605.23723

[4] Memory Poisoning Attack and Defense on Memory Based LLM-Agents 2601.05504

[5] A Survey on the Security of Long-Term Memory in LLM Agents: Toward Mnemonic Sovereignty 2604.16548

## Scores
**Final Score:** 6/10

The paper introduces a novel commit-time defense paradigm for LLM agent memory security, with a clean mathematical formulation and compelling empirical results. The core idea of applying distributed-system tombstones with fuzzy semantic matching is conceptually sound, and the "slot wasting" argument for why commit-time is superior to retrieval-time filtering is insightful.

However, the score is reduced due to three categories of concerns: (1) the narrow 5-label hazard taxonomy limits generalizability beyond the data analysis domain, (2) the single-run evaluation without variance reporting limits reproducibility confidence, and (3) the omission of recent critical defenses (MEMSAD, MemAudit) weakens the novelty positioning. The partial-overlap evasion gap in Eq. (3) is also a methodological robustness concern that should be acknowledged.

The paper's research value lies in its conceptual shift from retrieval-time to commit-time defense and its clear demonstration of index pollution mechanics. If the authors address the reproducibility and related-work gaps, the contribution would be substantially stronger.

**Post-Revision Target:** [7, 8]/10

This interval assumes the authors: (1) add scope qualification to "complete elimination" claims, (2) provide reproducibility details (seeds, multi-run variance if feasible), (3) expand related work to include MEMSAD and MemAudit with clear differentiation, and (4) acknowledge the partial-overlap evasion gap as a limitation. These fixes are feasible and would materially improve the paper's defensibility without requiring new experiments.