# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper proposes a theoretical framing of large language models (LLMs) as “procedural libraries,” namely distributions over strings that are made navigable by operators such as prompts and retrieval. The work formalizes: (i) typical-set suppression through concentration results like Shannon–McMillan, (ii) an operator calculus that reduces conditional entropy, (iii) navigability via success probability, hitting time, and energy bounds, and (iv) a decomposition of hallucination risk into coverage, abstention, and conditional error. It also gives complexity-theoretic limits (a SAT-based lower bound), relates retrieval to submodular information acquisition, and reports a small empirical illustration on a 12-item QA toy set. Figures visualize entropy reduction and best-of-N effects, and Table 1 reports metric values for BASE, FEWSHOT, and RAG setups.

## Summary Of Strengths
- Conceptual clarity: The “procedural library” lens is a coherent way to connect information theory and common operator controls in LLMs (prompts, prefix prompts, retrieval). The operator–entropy view is easy to reason about and could be pedagogically useful.
- Clean formal statements: Definitions of typical sets, navigability, and the hallucination risk decomposition are well-scoped. Lemma 2 and Theorem 2 connect best-of-N sampling and Blackwell informativeness to improved success, linking established decision-theory to LLM workflows.
- Limits and calibration: The SAT-based lower bound (Theorem 3) and the abstention-based reliability result (Theorem 5) help set expectations for what can and cannot be guaranteed. The hallucination lower bound in Equation (2) separates structural coverage failures from conditional errors and abstention, providing a useful diagnostic.
- Retrieval as acquisition: Casting RAG as budgeted information acquisition with submodular-style guarantees (Lemma 3 and Corollary 2) aligns with established theory and motivates greedy selection policies.
- Figures and table support the narrative: 
  - Figure 2/5 show the expected increase in hit probability 1 − (1 − p)^N, highlighting how sampling strategies interact with base success rates. 
  - Figure 3/4 visualize the decomposition HR ≥ (1 − c)(1 − α) + cβ; in particular, Figure 4 aligns with the toy experiment’s finding that uncovered error dominates when β ≈ 0.
  - Table 1 reports p_f, NI, and latency for three operator settings, concretely illustrating how the proposed metrics can be computed even in small-scale tests.

## Summary Of Weaknesses
1) Rigor vs. proof sketches. Many core results are given informally or with high-level sketches, often invoking strong idealizations without precise conditions. Examples:
   - Theorem 1 relies on “Shannon-McMillan type property” with “standard approximations” to handle the non-stationary Transformer setting (Page 2). This leaves unclear the exact assumptions under which the exponential concentration bound in Equation (1) is intended to hold. Without a precise technical model or a controlled approximation theorem, it is hard to assess applicability to modern LLMs.
   - Theorem 2 (Blackwell monotonicity, Page 3) asserts improved Bayes risk for “generation+selection,” but the statistical experiment and the decision rule are not fully formalized for the autoregressive setting and selection policy. The mapping from the generative policy with decoding to a standard experiment is left implicit.
   - Theorem 3 (Page 4–5) gives a proof sketch via a SAT reduction. While the intuition is standard, the construction that ensures inverse-polynomial success probability if and only if NP collapses to BPP needs to be spelled out more carefully, including how the prompt encoding and decoding prevent spurious solutions and how per-sample cost remains polynomial under the stated operator model.

2) Novelty positioning. Several results repackage standard information-theoretic facts with LLM-flavored terminology:
   - Lemma 1/Proposition 1 are essentially textbook mutual information identities; Theorem 2 is a direct application of Blackwell’s theorem; Lemma 3/Corollary 2 follow well-known submodular maximization results. The paper would benefit from deeper, LLM-specific theorems that go beyond restating classical principles and from positioning versus the considerable literature connecting information theory, uncertainty, and hallucination in LLMs.

3) Empirical validation is very limited and sometimes counterproductive for claims of practical relevance.
   - Table 1 (Page 6) shows BASE and FEWSHOT both at 1.00 accuracy on a 12-item trivia set; RAG underperforms (0.67). This makes it difficult to assess navigability improvements or entropy-reduction claims under realistic conditions. Furthermore, with p_f(BASE) = 1, NI for FEWSHOT is undefined conceptually; the paper sets NI to 0 by convention, and reports NI(RAG) = −0.41, but this neither validates the framework nor tests operator benefits.
   - Figure 4 mirrors Figure 3 in spirit and mostly restates that with β = 0 the error is due to uncovered items. This is consistent, but the example is too small and too easy to be informative.

4) Measurement choices are underspecified or unconvincing.
   - The “energy per hit” metric is proxied by latency, but Table 1 differences (0.25–0.33s) are small and unaccompanied by environment details or variability (no confidence intervals). This makes Proposition 2’s empirical value hard to judge for real systems.
   - There is no direct estimation of entropy or mutual information to substantiate “operator entropy reduction” beyond the illustrative Figure 1. The paper could at least approximate token-level entropy under prompts or RAG to bridge the theory–practice gap.

5) Overgeneralization risks. Several statements blur idealized guarantees and practical claims.
   - Section 9 states the metrics are “straightforward to estimate in future empirical work,” but the paper sidesteps the difficult parts: estimating MI for retrieval policies, or calibrating conformal abstention in open-ended generation.
   - Corollary 2 discusses greedy retrieval achieving a (1 − 1/e) fraction of maximum entropy reduction. The remark notes submodularity may fail; however, the text and design suggestions sometimes read as if the guarantee were broadly applicable to modern RAG pipelines without concrete proxies and counterexamples.

6) Missing related work undermines positioning on hallucination and limits. The paper does not cite several highly relevant theoretical and empirical analyses that would sharpen and situate the contributions (see “Potentially Missing Related Work” below).

7) Ambiguities in the experimental protocol and metrics.
   - Predicate f and selection policy: In Section 10 the success criterion uses a rule-based normalization and alias matching. The abstention detection (“I don’t know”) is surface-form based, which is fragile. This makes α, β, and c sensitive to prompt wording and string matching.
   - NI depends on p_f(BASE). When p_f(BASE)=1, NI for other operators becomes degenerate. A more robust design would anchor NI to a nontrivial baseline and report uncertainty.

8) Figures are largely illustrative, sometimes redundant.
   - Figure 1 shows bar heights for H(X), H(X|π), H(X|π,C) without units or empirical estimates; it communicates a known inequality but not data. 
   - Figures 2 and 5 both plot 1 − (1 − p)^N; Figure 5 is titled “Analytic” but duplicates Figure 2, adding little beyond the earlier plot. 
   - Figure 3 and Figure 4 both show the decomposition; Figure 4 is labeled “Empirical,” yet it is essentially a stylized plot matching the toy setting. The paper should either provide real measured components (with error bars) or consolidate the visuals.

9) Code correctness and clarity issues in Appendix A.1.
   - There are several syntactic/indentation issues likely preventing the script from running as-is (e.g., malformed get() call return res.get("choices", [{{}})[0]..., indentation under make_fewshot_prompt and alias checks, and mojibake in aliases such as "portuguÃls"). This undermines the claim of plug-and-play reproducibility.
   - Some constants (e.g., temperature, max_tokens) are hard-coded without ablation; the environment dependencies are under-specified.

10) Clarity and consistency issues.
   - On Page 6, “0.25â€¢0.33s” appears to be an encoding artifact and should read “0.25–0.33 s.”
   - Section 9 claims “Although we present no experiments,” yet Section 10 does present a toy experiment; the transition is confusing and should be reconciled.

## Potentially Missing Related Work
1) Kalai et al., “Calibrated Language Models Must Hallucinate,” 2023 — Proves inevitability of some hallucinations under calibration constraints. Directly relevant to Section 5 and Theorem 4; should be cited and contrasted in the limits discussion and after Equation (2).

2) Kalai et al., “Why Language Models Hallucinate,” 2025 — Discusses indistinguishability and evaluation incentives that favor guessing over abstention. Relevant to the abstention–coverage–risk framing; add to Section 5 and Section 9 to connect to evaluation design.

3) Kalavasis et al., “On the Limits of Language Generation: Trade-Offs Between Hallucination and Mode Collapse,” 2024 — Theoretical trade-offs in generation reliability vs. diversity. Relates to navigability and suppression; cite in Sections 3–4 and discuss alongside Theorem 4.

4) Guo et al., “Hallucination is a Consequence of Space-Optimality: A Rate-Distortion Theorem for Membership Testing,” 2026 — An information-theoretic account of hallucinations under capacity constraints. Should be discussed in Section 5 to complement the coverage–abstention–error decomposition with rate–distortion bounds.

5) Kim et al., “Detecting LLM Hallucination Through Layer-wise Information Deficiency,” 2025 — Test-time detection via information flow analysis. Connect to Sections 3 and 8 as an instance of entropy/information-based operators and to the proposed design metrics.

6) “A Protocol-Fixed Information-Theoretic Reporting Framework for Evidence-Weak Hallucination in Large Language Models,” 2026 — Offers a rigorous auditing protocol based on energy/free-energy/KL decompositions. Relevant for Section 8’s measurement agenda and could be used to operationalize Equation (2).

7) Agnimo et al., “Evaluating the Relevance of Uncertainty Estimators for LLM Hallucination,” 2026 — Broad empirical assessment of uncertainty scores for hallucination detection. Add to Section 8 to clarify when entropy-based proxies correlate with risk.

8) “Evaluating large language models for accuracy incentivizes hallucinations,” 2026 — Shows how conventional accuracy metrics penalize abstention and can increase hallucination. Directly supports the paper’s call for abstention-aware metrics; add to Sections 5, 8, and 9.

## Comments Suggestions And Typos
Actionable suggestions:
- Provide full proofs or move beyond sketches for key theorems:
  - Theorem 1: State precise assumptions for a Transformer-generated sequence under which an AEP-type concentration bound like Equation (1) holds. For example, adopt a finite-order Markov or mixing process abstraction with a bounded context window and prove the exponential tail under that model. 
  - Theorem 2: Formalize the statistical experiment induced by generation and selection. Make clear how the decoding policy maps to a decision rule and how the Blackwell comparison applies to operators with appended context and retrieval signals.
  - Theorem 3: Give a complete reduction with encoding, sampling policy, and stopping rule, and show that per-sample complexity is polynomial and that inverse-polynomial success would imply NP ⊆ BPP. Clarify how spurious outputs are excluded.

- Strengthen the empirical component:
  - Replace the 12-item trivia with at least one established benchmark (e.g., TruthfulQA, MMLU subsets). Report multiple runs with error bars. Provide a nontrivial baseline with p_f < 1 so that NI and best-of-N curves are informative.
  - For Figure 1, estimate entropy or per-token negative log-likelihood under each operator using logprobs, rather than using illustrative bars. For retrieval, approximate ΔH via compression gain or language-model MI proxies.
  - For Equation (2), directly estimate c, α, and β with clearer operational definitions. For α, use a classifier over multiple abstention templates; for c, use passage-level annotations rather than string inclusion; for β, have independent human or rule-based adjudication.

- Clarify measurement and environment:
  - Report compute environment, model endpoints, and variance in latency. If you rely on a hosted API, state the region, throttling behavior, and any caching effects.
  - Justify the energy proxy and, where possible, complement it with token-level throughput or cost estimates.

- Refine figures and table usage:
  - Consolidate Figures 2 and 5 or differentiate them by adding empirical curves measured from a real task against the theoretical 1 − (1 − p)^N. 
  - In Figure 3/4, plot the actually measured components with confidence intervals instead of stylized blocks; otherwise, keep only the theoretical diagram.
  - In Table 1, explain the negative NI for RAG and discuss how NI should be interpreted when p_f(BASE)=1. Consider reporting Δp_f or odds ratios in such degenerate cases.

- Literature positioning:
  - Integrate the missing works listed above to situate the contribution relative to existing impossibility results and recent information-theoretic takes on hallucination. Make explicit what is new beyond these.

Typos/bugs and minor issues:
- Page 6: “0.25â€¢0.33s” appears to be a rendering artifact; should be “0.25–0.33 s.”
- Section 9: “Although we present no experiments” conflicts with Section 10. Reconcile wording.
- Appendix A.1 code: 
  - Likely syntax error at return res.get("choices", [{{}})[0]...; stray braces. 
  - Indentation errors in make_fewshot_prompt and in the alias loop.
  - Mojibake in aliases (e.g., “portuguÃls,” “hãCCo”). Replace with correct Unicode or ASCII. 
  - Several functions lack error handling for API failures.
  - Consider parameterizing temperature, max_tokens, and k with command-line flags; log seeds and retry logic.

What could change my evaluation:
- Providing rigorous proofs or a precise modeling framework for Theorems 1–3 with all assumptions stated.
- Empirical validation on harder datasets demonstrating operator-induced entropy reduction, improvements in navigability (including best-of-N), and a measured c/α/β decomposition with robust estimators.
- A concrete retrieval utility proxy with evidence of approximate submodularity and an ablation against greedy vs. non-greedy selection.

## Confidence
4 Quite sure after careful checking: I checked the main technical points and cross-referenced figures/tables with claims. Some proofs are sketches, but the gaps are evident.

## Soundness
3 Acceptable: The high-level claims are reasonable and consistent with known theory, but many results rely on sketches and idealizations, and the empirical validation is too small to support practical takeaways.

## Excitement
2.5 Between potentially interesting and interesting: The conceptual lens is neat and could be useful pedagogically, but the paper needs stronger theory and experiments to be compelling for the main track.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. The framing is coherent and several lemmas connect well-known principles to LLM practice, but key theorems are only sketched, empirical validation is very limited and sometimes degenerate (Table 1 with p_f=1 for BASE), and related work on hallucination limits is missing. With stronger proofs, richer experiments, and improved positioning, this could be a solid Findings paper.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper’s Limitations section acknowledges the toy nature of the empirical study and suggests testing on harder benchmarks, which is appropriate. The societal discussion emphasizes abstention and retrieval to reduce hallucination risk, which is positive. Additional considerations that would strengthen the section:
- Fairness and multilingual exposure: whether the navigability metrics and abstention policies generalize across languages or disadvantage low-resource settings.
- Dual use: how increasing navigability could facilitate harmful content generation without adequate safeguards.
- Transparency: if adopting abstention, communicate coverage trade-offs to users to avoid over-trust.

## Ethical concerns
None.

## Needs Ethics Review
No.

## Reproducibility
4 Mostly reproducible: The toy dataset and code are provided, but code has minor bugs and the reliance on a hosted API without a fixed environment introduces variance.

## Datasets
2 Documentary: The tiny QA set is included mainly for illustration and has limited independent value.

## Software
3 Potentially useful.: The script is helpful as a starting point but needs fixes and more robust logging to be broadly useful.