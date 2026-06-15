## Summary
This paper studies **Draft-and-Continue Self-Consistency (DCS)**, a two-stage variant of self-consistency that (i) samples multiple *draft* chain-of-thoughts up to a token limit, (ii) forms a vote histogram over *interim answers*, and (iii) spends additional continuation tokens only on high-vote branches (with a hedge to cover the 2nd-place answer). The goal is to improve the accuracy–cost trade-off by reallocating test-time compute rather than uniformly sampling full solutions.

Empirically, on **MATH-500 with Qwen2.5-Math-7B-Instruct**, DCS achieves the same reported accuracy as the strongest baselines (76.8%) but **uses more tokens** than uniform self-consistency and is **Pareto-dominated** by confidence-guided early stopping. The paper’s core diagnosis is that the continuation mechanism is largely “switched off” because **~96% of drafts already terminate with a parseable answer under $T_{draft}=1024$**, so continuation rarely changes outcomes (Page 4 - Experiments: Analysis).

As a negative-result note, the topic is valuable and the manuscript is refreshingly direct about failure modes. However, the current draft has several *publication-critical* gaps that reduce decision confidence in the negative conclusion and its generality: (1) the interim-answer parser and “draft complete” definition are not specified (Page 2 - Method: Stage 1 Draft Sampling), (2) comparisons are not budget-matched across methods (Page 3 - Experiments: Baselines), and (3) the key boundary-condition experiment (a $T_{draft}$ sweep / continuation-activation analysis) is missing despite being the paper’s main explanation (Page 3 - Hyperparameters; Page 4 - Analysis). With these fixes, the paper can become a strong, defensible negative result with clear takeaways about when continuation-based branch budgeting is (un)likely to help.

## Strengths
1) **Clear problem and honest negative result (good scientific hygiene).** The paper is explicit that DCS is not Pareto-competitive under the evaluated setting and offers a concrete diagnosis (high draft completion makes continuation mostly irrelevant) (Page 4 - Experiments: Analysis; Page 5 - Conclusion).

2) **Simple, understandable mechanism.** DCS is easy to describe and implement in principle (two-stage draft → interim-answer vote → continue selected branches with a hedge). This makes the negative result interpretable and useful for practitioners who might otherwise try similar ideas (Page 2 - Method: Draft-and-Continue).

3) **Relevant baseline family.** The manuscript compares against (i) greedy CoT, (ii) uniform self-consistency, and (iii) a confidence-guided early stopping method—i.e., the most direct “efficiency” competitors in the self-consistency decoding space (Page 3 - Experiments: Baselines).

4) **Cost reporting beyond accuracy.** Reporting average generated tokens and average calls (not only accuracy) is aligned with the test-time compute literature’s budget-aware emphasis and is necessary for a credible efficiency discussion (Page 4 - Experiments: Evaluation Metrics).

5) **Actionable qualitative takeaway (even before fixes).** The paper’s main insight—that continuation-based branch budgeting only has a chance when the draft budget is materially shorter than typical solution length—is a useful rule-of-thumb for future TTC method design, and aligns with broader budget-aware evaluation perspectives in the literature [8].

6) **Good revision potential.** The core weaknesses (parser definition, matched-budget evaluation, and one key sensitivity sweep) are all fixable with relatively modest additional experimentation and clearer method specification.

## Weaknesses
1) **Reproducibility gap: interim-answer extraction and “draft complete” are undefined.** DCS’s core decision signal is the interim-answer vote histogram, yet the manuscript does not specify the deterministic parser/normalization rules or how NULL drafts are handled beyond a brief description (Page 2 - Method: Stage 1 Draft Sampling). This also makes the reported ~96% draft-completion rate difficult to interpret (what counts as “parseable final answer”?).

2) **Unfair / confounded efficiency comparison due to unmatched budgets.** DCS uses ~10 calls (7 drafts + 3 continuations), while Uniform SC uses 5 calls and Greedy uses 1; CGES is adaptive up to 5 (Page 3 - Experiments: Baselines). Without matched-call or matched-token-cap baselines, efficiency claims can reflect budget mismatch rather than algorithmic merit.

3) **Key mechanism boundary is asserted but not experimentally validated.** The paper’s main explanation is “drafts are too long,” implying DCS might work for smaller $T_{draft}$ or harder/longer tasks (Page 4 - Analysis; Page 5 - Discussion). However, there is no $T_{draft}$ sweep, no continuation-activation analysis, and no length-stratified/harder benchmark test. This leaves the main takeaway as a plausible hypothesis rather than a closed empirical argument.

4) **Token-budget accounting is internally confusing.** The method states a budget upper bound $B\,T_{draft}+k\,T_{cont}$ (Page 3 - Method: Final Aggregation), while Table 1 reports a much smaller realized token count (~4,114). The paper should explicitly present expected realized cost and clarify how continuation behaves when drafts terminate early.

5) **Method randomness is not fully controlled.** “Branches within each answer cluster are selected arbitrarily” (Page 2 - Method: Stage 2). This can inject extra variance and may contribute to DCS’s higher observed variance; the selection policy should be deterministic or ablated.

6) **Over-strong generalization / gap statements.** The introduction’s framing that early-stopping methods “fundamentally discard partial reasoning” is overstated given related work on prefix-guided generation and pruning (Page 1 - Introduction). Similarly, “Pareto-dominates” and “dominates two-stage approaches” should be bounded to the tested regime unless frontier curves are provided.

7) **Minor but correctness-affecting presentation issues.** Hyperparameter notation contains visible typos/artifacts (e.g., $T_{cont}=\mathrm{i0 2 4}$) (Page 3 - Hyperparameters). In a short paper, these details disproportionately affect reviewer trust.

## Key Issues
### Ranked Error Board (Top-5)
(Severity | Research-Value Impact | Validity Risk | Fixability | Confidence)

1) **Undefined interim-answer parser + “draft complete” criterion** (Major | High | High | High | High)
- **Anchor:** Page 2 - Method: Stage 1 Draft Sampling.
- **Why it matters:** DCS’s selection signal and the core negative-result diagnosis (~96% completion) depend on parsing; without a precise definition, the main conclusion is not reproducible.
- **Acceptance criterion:** Provide deterministic extraction + normalization + examples; report NULL rate and sensitivity.

2) **Budget-mismatch confounds efficiency claims** (Major | High | High | Medium | High)
- **Anchor:** Page 3 - Experiments: Baselines; Page 4 - Main Results.
- **Why it matters:** DCS uses ~10 calls vs 1/5/≤5 for baselines; “efficiency” deltas can be an artifact.
- **Acceptance criterion:** Add matched-calls and matched-token-cap comparisons; plot accuracy–cost frontiers.

3) **Missing mechanism-boundary validation ($T_{draft}$ sweep / activation / answer-change rates)** (Major | High | Medium | Medium | High)
- **Anchor:** Page 3 - Hyperparameters; Page 4 - Analysis; Page 5 - Discussion.
- **Why it matters:** The paper’s explanation is plausible but currently not a closed experimental argument.
- **Acceptance criterion:** Report continuation activation %, answer-change %, and a $T_{draft}$ sweep under fixed caps.

4) **Token accounting and “budget” definition are inconsistent/unclear** (Major | Medium | Medium | High | Medium)
- **Anchor:** Page 3 - Method: token budget formula; Page 4 - Metrics.
- **Why it matters:** The paper is about efficiency; readers need explicit definitions (generated tokens? include prompts? early termination?).
- **Acceptance criterion:** Define cost precisely; report expected realized cost; reconcile with Table 1.

5) **Method introduces extra randomness (‘arbitrary’ intra-cluster branch selection)** (Major | Medium | Medium | High | Medium)
- **Anchor:** Page 2 - Method: Stage 2.
- **Why it matters:** May explain higher variance and reduces interpretability.
- **Acceptance criterion:** Use deterministic tie-breakers; include an ablation for random vs deterministic selection.


### ASCII Diagram — Paper Structure & Evidence Map
```text
[Goal: Improve SC efficiency by reallocating compute]
   |
   v
[Method: DCS = draft B -> interim vote -> continue k]
   |
   +--> Evidence (current): Table 1 tokens/accuracy; Table 2 draft-complete rate
   |
   +--> Gap A (critical): interim-answer parser + “draft complete” definition missing
   |
   +--> Gap B (critical): budget-matched baselines + frontier curves missing
   |
   +--> Gap C (critical): activation/answer-change + T_draft sweep missing
   v
[Conclusion claim: DCS dominated when drafts already finish]
   |
   v
[Needed to close loop: define parser; match budgets; validate boundary]
```

### ASCII Diagram — Revision Strategy Roadmap
```text
P0 (must, 1–2 days):
  - Define parser + cost accounting
  - Add matched-budget baselines
      -> makes negative result reproducible + fair

P1 (high value, 2–4 days):
  - T_draft sweep + activation/answer-change analysis
      -> turns diagnosis into validated mechanism boundary

P2 (optional, 3–7 days):
  - 1 extra model or harder/longer benchmark
      -> strengthens generality claims
```

## Actionable Suggestions
### Must (publication-critical)

1) **Specify interim-answer extraction + normalization + NULL handling (reproducibility package).**
- **Where:** Page 2 - Method: Stage 1 Draft Sampling.
- **Do:** Add an appendix with deterministic extraction rules (regex / priority order), normalization rules (fractions/decimals, whitespace, sign, boxed vs final line), and examples of partial traces.
- **Acceptance criteria:** Given any raw completion, a reader can reproduce $a_i^{draft}$ and whether it is NULL.

2) **Define “draft complete” and continuation behavior in the dominant regime.**
- **Where:** Page 3 - Method: Final Aggregation; Page 4 - Analysis.
- **Do:** State whether completed drafts are continued (and how) vs treated as no-op; report continuation activation rate (non-zero continuation tokens).
- **Acceptance criteria:** Provide a table: activation %, mean continuation tokens conditional on activation, answer-change % conditional on activation.

3) **Add matched-budget evaluations (calls and tokens).**
- **Where:** Page 3 - Experiments: Baselines; Page 4 - Main Results.
- **Do:**
  - Matched-calls: Uniform SC with $n{=}10$ vs DCS ($B{=}7,k{=}3$).
  - Matched-token-cap: run all methods under the same expected generated-token cap.
- **Acceptance criteria:** One accuracy–cost plot with curves (vary $n$ for SC, $\gamma$ for CGES, $T_{draft}$/$k$ for DCS).

4) **Fix token accounting and remove ambiguous budget statements.**
- **Where:** Page 3 - Method/Hyperparameters.
- **Do:** Replace $B\,T_{draft}+k\,T_{cont}$ with a clear “worst-case cap” plus an explicit expected realized cost expression; define whether tokens include prompts.
- **Acceptance criteria:** Table 1’s Avg Tokens can be derived from stated accounting choices.


### Nice-to-have (high value, but not strictly required)

5) **$T_{draft}$ sensitivity sweep to validate the proposed boundary condition.**
- **Where:** Page 3 - Hyperparameters; Page 5 - Discussion.
- **Do:** Sweep $T_{draft}\in\{128,256,512,1024\}$ and keep total cap comparable (adjust $T_{cont}$ or $B,k$). Report completion/activation and accuracy–tokens.

6) **Control method randomness and explain variance.**
- **Where:** Page 2 - Stage 2.
- **Do:** Replace “arbitrary” intra-cluster branch selection with a deterministic rule (sampling order). Add an ablation comparing deterministic vs random tie-breaking.

7) **Strengthen related-work positioning around “partial-trace reuse”.**
- **Where:** Page 1 - Introduction gap; Page 5 - Related Work.
- **Do:** Add a short paragraph contrasting continuation-based budgeting (DCS) vs prefix-guided generation [5] and pruning-based SC [4], and cite the closest works explicitly.


### Copy-ready paragraph fix (recommended insertion)
**Insert after Page 2 - Method: Stage 1 Draft Sampling**

Mentor Revised Version:
DCS relies on a deterministic interim-answer parser to construct the vote histogram. We extract $a_i^{draft}$ by (i) selecting the final occurrence of a “\boxed{\cdot}” answer when present, (ii) otherwise extracting the last numeric expression in the final line, and (iii) normalizing equivalent formats (e.g., fractions vs decimals, whitespace, and sign). If no parseable answer exists, we assign the draft to a NULL bucket and exclude it from continuation selection. We define a draft as “complete” if it emits an explicit final-answer marker before reaching $T_{draft}$; otherwise it is “truncated” and eligible for continuation.


### ASCII Diagram — Experiment Upgrade Plan
```text
P0: Reproducibility + fairness
  - Parser + cost accounting
  - Matched-budget baselines

P1: Validate mechanism boundary
  - T_draft sweep (128..1024)
  - activation % + answer-change %

P2: Generality check
  - 1 harder/longer benchmark or 1 extra model
```

## Storyline Options + Writing Outlines
**Option A — “Negative-result as boundary condition” (recommended)**
- Arc: *Problem (SC is expensive) → Proposed continuation idea (DCS) → Negative result under a common regime → Mechanistic diagnosis (drafts already finish) → Boundary condition for when continuation could help.*
- Why better: matches the paper’s true value (a falsifiable boundary condition) and keeps claims scoped to evidence.

**Option B — “Budget-aware evaluation lens”**
- Arc: *Problem (TTC papers often compare under mismatched compute) → Define a fair budget metric → Evaluate DCS as a case study → Find that early stopping dominates → Provide guidance for TTC evaluation.*
- Why better: leverages [8] to frame the contribution as “how to evaluate” plus a concrete negative case.

**Option C — “Method-first (engineering note)”**
- Arc: *Define DCS algorithm precisely → Provide reproducibility package → Benchmark → Analyze failure.*
- Why better: if targeting a systems/practice audience; less compelling for research framing.


### Abstract Outline (complete; S1–S5)
S1 (Problem & setting): State that self-consistency improves CoT reasoning but is expensive because it samples multiple full traces.
- Evidence anchor: Page 1 - Abstract (problem statement).

S2 (Gap): State that existing efficiency methods mostly stop/prune sampling; pose the complementary question of reallocating tokens to promising partial traces.
- Evidence anchor: Page 1 - Introduction (early-stopping/pruning motivation).

S3 (Method): Define DCS as two-stage draft sampling ($B$, $T_{draft}$) → interim-answer histogram → continue $k$ selected branches ($T_{cont}$) with hedge allocation.
- Evidence anchor: Page 2 - Method (Stages 1–2).

S4 (Main result): Report the key accuracy and cost outcome on MATH-500 + Qwen2.5-Math-7B-Instruct; state that CGES-LNS yields the same accuracy with fewer tokens.
- Evidence anchor: Page 4 - Main Results (Table 1).

S5 (Diagnosis & bounded implication): Report that ~96% drafts complete within $T_{draft}=1024$, so continuation rarely activates; conclude that continuation-based budgeting is only promising when drafts are short relative to solution length.
- Evidence anchor: Page 4 - Analysis (Table 2) and Page 5 - Discussion.


### Introduction Outline (complete; paragraph-by-paragraph)
**P1 — Stakes + scope + metric definition.**
- Role: Establish why test-time compute matters, then *narrow scope* to self-consistency-style sampling.
- Target claim: “We study budget-aware self-consistency under constraints measured in generated tokens and model calls.”
- Transition: From general TTC to the specific SC family.
- Required evidence: later sections’ reported metrics (Page 4 - Evaluation Metrics).

**P2 — Prior work categories + precise gap.**
- Role: Categorize efficiency approaches (early stopping; pruning; prefix/partial-trace reuse), and state what is missing.
- Target claim: “Prior methods reduce cost by stopping or pruning; fewer methods explicitly allocate extra continuation tokens to selected partial traces based on interim answers.”
- Transition: From “what exists” to “what we test.”
- Required evidence: citations to closest families (use only retrieved refs in final paper revision), e.g., early stopping [1][2], pruning [4][6], prefix-guided [5].

**P3 — DCS proposal + negative result preview + contribution bullets.**
- Role: Describe DCS at high level, preview the negative result, and state the *mechanistic hypothesis* (draft-completion collapse) as something you validate.
- Target claim: “DCS is a probe of continuation-based budgeting; under $T_{draft}=1024$ it is dominated; the key reason is high draft completion.”
- Transition: From question to method to what the paper will show.
- Required evidence: Table 1 + Table 2, and (after revision) a $T_{draft}$ sweep + activation analysis.


### One concrete title tweak (optional but helpful)
Current title is informative but long and slightly opaque (“branch budget-ing”). A clearer title pattern is *Setting + idea + outcome*:
- Suggested: **“Draft-and-Continue Self-Consistency: When Two-Stage Branch Budgeting Fails for MATH Reasoning”**
- Or (more general): **“When Continuation Doesn’t Help: A Negative Result for Two-Stage Budgeting in Self-Consistency”**

## Priority Revision Plan
### P0 (Must) — Make the negative result reproducible and the comparison fair
**Goal:** A reader can re-run DCS and agree that (under the tested regime) it is not Pareto-competitive.

1) **Parser + definitions package (same day).**
- Add: interim-answer extraction rules; normalization; NULL bucket policy; “draft complete” definition; continuation prompting for completed drafts.
- Output: Appendix + one table of parser stats (NULL %, early-answer %, completion %).

2) **Cost accounting cleanup (same day).**
- Define: generated tokens vs prompt tokens; per-call caps; what counts toward “Avg Tokens.”
- Replace: budget upper bound sentence with worst-case cap + expected realized cost.

3) **Budget-matched baselines (1–2 days).**
- Add: Uniform SC with $n{=}10$; DCS variant matching $\le 5$ calls; matched-token-cap setting.
- Output: one frontier plot (accuracy vs expected tokens) with curves.


### P1 (High priority) — Validate the paper’s own failure-mode hypothesis
**Goal:** Turn “drafts are too long” from a plausible story into verified mechanism.

4) **$T_{draft}$ sweep under fixed caps (2–4 days).**
- Sweep: $T_{draft}\in\{128,256,512,1024\}$.
- Control: keep total expected tokens comparable by adjusting $T_{cont}$ and/or $B,k$.
- Report: completion %, activation %, answer-change %, accuracy, tokens.

5) **Continuation-effect decomposition (1–2 days).**
- Report: conditional accuracy on cases where continuation activates vs not.
- Report: how often continuation flips the final answer (and whether flips improve correctness).


### P2 (Nice-to-have) — Strengthen generality and related-work positioning
**Goal:** Support bounded general claims (or limit claims appropriately).

6) **One extra setting (3–7 days).**
- Option: one harder/longer benchmark or a length-stratified MATH subset; or one additional model.

7) **Related-work tightening (same day).**
- Add: explicit comparison to prefix-guided SC and pruning-based SC; soften over-strong “discard partial reasoning” language.


### ASCII Diagram — Revision Strategy Roadmap
```text
[Reproducibility missing] -> [Add parser + cost definitions] -> [Readers can verify DCS]

[Budget mismatch] -> [Matched calls/tokens baselines + frontier plot] -> [Fair efficiency claim]

[Boundary hypothesis untested] -> [T_draft sweep + activation/flip analysis] -> [Mechanistic negative result]

[Generality unclear] -> [1 extra setting] -> [Bounded but stronger takeaway]
```

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup (data/split/protocol/baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|---|---|---|---|---|---|---|
| E1 | Test whether DCS improves SC efficiency by continuing high-vote branches | MATH-500; Qwen2.5-Math-7B-Instruct; DCS vs Greedy CoT vs Uniform SC (n=5) vs CGES-LNS (b_max=5, γ=0.95) (Page 3–4) | Exact-match accuracy; avg generated tokens; avg calls; mean±std over 3 seeds (Page 4) | DCS accuracy 76.8% matches best baselines but uses more tokens than Uniform SC (+19.6%) and CGES-LNS (+109%) (Page 4) | Negative result under this regime | Budgets/calls not matched; no frontier curve; CGES-LNS details not specified |
| E2 | Diagnose why DCS fails (continuation rarely matters) | Same as E1; diagnostic stats for DCS across seeds (Table 2) | Fallback %; Draft Complete %; avg tokens | ~96.3% draft-complete; fallback ~3.7% (Page 4) | Hypothesis: drafts already finish under $T_{draft}$, collapsing continuation | “Draft complete” depends on parser/termination definition; no activation/answer-change analysis |


### Research-Theme Gap Diagnosis
- **New knowledge:** The paper aims to produce a boundary condition for continuation-based budgeting (“when drafts already finish, continuation is wasted”). This is promising, but currently under-validated because the key boundary-variable ($T_{draft}$) is not swept.
- **Reproducibility:** The most important missing piece is the interim-answer parser + completion criterion; without it, Table 2 is not independently checkable.
- **Impact on practice:** Practitioners care about “tokens vs calls vs latency.” The paper reports tokens/calls but lacks matched-budget fairness and latency/cost modeling.


### Proposed Research Experiments (P0/P1/P2)

#### P0-E1 — Matched-budget baselines (calls + token caps)
- **Target Claim:** “DCS is Pareto-dominated by CGES-LNS (and worse than Uniform SC) under equal budgets.”
- **Hypothesis:** Under matched calls/tokens, DCS will remain non-competitive at $T_{draft}=1024$.
- **Minimal Design:** Add Uniform SC with n=10; add a DCS variant with total calls ≤5; run a matched-token-cap setting where all methods are constrained to the same expected generated tokens.
- **Controls/Baselines:** Greedy; Uniform SC (n=5,10); CGES-LNS (vary γ); DCS variants.
- **Metrics:** Accuracy; expected tokens; calls; optionally latency proxy.
- **Success Criterion:** Conclusion does not change under fair budgets; frontier plot shows DCS dominated at tested regime.
- **Estimated Cost/Time:** 1–2 days.
- **Expected Paper-Quality Gain:** High (removes confound; strengthens negative result).

#### P1-E1 — $T_{draft}$ sweep with fixed total caps
- **Target Claim:** “Continuation helps only when drafts are short relative to solution length.”
- **Hypothesis:** As $T_{draft}$ decreases, draft completion falls and continuation activation rises; DCS may improve (or still fail), but the boundary becomes measurable.
- **Minimal Design:** Sweep $T_{draft}\in\{128,256,512,1024\}$; adjust $T_{cont}$ or $(B,k)$ to keep expected-token budget comparable.
- **Controls/Baselines:** Uniform SC curve (vary n); CGES curve (vary γ).
- **Metrics:** Draft completion %; continuation activation %; answer-change %; accuracy vs tokens.
- **Success Criterion:** Provide a clear threshold regime (e.g., completion < 70%) where continuation becomes meaningfully active.
- **Estimated Cost/Time:** 2–4 days.
- **Expected Paper-Quality Gain:** High (turns diagnosis into validated boundary condition).

#### P1-E2 — Continuation causal effect decomposition
- **Target Claim:** “Continuation rarely changes answers in the current regime; overhead dominates.”
- **Hypothesis:** Conditional on activation, answer-change is rare and/or not helpful.
- **Minimal Design:** For each problem, record whether continuation consumed tokens, whether final answer changed vs Stage-1 vote, and whether the change improved correctness.
- **Controls/Baselines:** A ‘no-continue’ ablation (stage-1 majority vote only) under same $B,T_{draft}$.
- **Metrics:** Activation %, flip %, flip-improves %, flip-hurts %.
- **Success Criterion:** Mechanistic explanation is numerically supported.
- **Estimated Cost/Time:** 1–2 days.
- **Expected Paper-Quality Gain:** Medium–High.

#### P2-E1 — One extra setting for generality (choose one)
- **Target Claim:** “The boundary condition generalizes beyond one model/dataset.”
- **Hypothesis:** Draft completion depends on model + benchmark difficulty; DCS may activate more on longer-horizon settings.
- **Minimal Design:** Either (i) run on one harder/longer benchmark or length-stratified MATH subset, or (ii) run one additional math-reasoning model.
- **Controls/Baselines:** Same as main.
- **Metrics:** Same + completion/activation.
- **Success Criterion:** Show whether the negative result is regime-specific.
- **Estimated Cost/Time:** 3–7 days.
- **Expected Paper-Quality Gain:** Medium.


### ASCII Diagram — Experiment Upgrade Plan
```text
P0: Fairness
  Matched calls/tokens -> frontier plot

P1: Mechanism boundary
  T_draft sweep -> completion/activation
  activation -> answer-change -> correctness effect

P2: Generality
  1 extra benchmark/model -> verify boundary transfer
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board
| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|---|---|---|---|---|---|---|
| C1 | **DCS method:** two-stage self-consistency that samples drafts, votes on interim answers, then continues high-vote branches with a hedge allocation (Page 2 - Method) | [5][6][9][4] | partially_overlapping | Prior work already uses *partial-trace signals* to guide/weight/prune self-consistency (prefix-guided sampling, hypothesis pruning, regeneration-based reliability, thought pruning). DCS’s specific novelty is the *interim-answer histogram + continuation-of-existing-drafts + hedge rule*, but the overall “use early signals to allocate later compute” axis is well populated. | Medium | Frame DCS as a **minimal continuation-based baseline** and focus the contribution on (i) the explicit continuation formulation (vs resampling/pruning) and (ii) the negative-result boundary condition rather than claiming a new paradigm. |
| C2 | **Empirical study / negative result:** on MATH-500 + Qwen2.5-Math-7B-Instruct, DCS matches accuracy but increases tokens; CGES-LNS Pareto-dominates (Page 4 - Main Results) | [2][1][8] | supported | The specific measurement that this continuation-based budgeting instantiation is not competitive under the evaluated regime is new (though it should be strengthened by matched-budget settings). Prior work provides baselines and evaluation perspective, but not this DCS case study. | Medium | Tighten to “in the evaluated setting” and add matched-budget curves so the negative result becomes a robust, reusable reference point. |
| C3 | **Mechanistic diagnosis:** high draft completion (~96% at $T_{draft}=1024$) causes continuation to rarely activate, so DCS collapses to SC+overhead (Page 4 - Analysis; Page 5 - Discussion) | [3][10][8] | partially_overlapping | Related work already documents redundancy/answer convergence/overthinking under larger compute budgets and motivates early exit. Your diagnosis is a concrete instantiation for DCS, but the general phenomenon is not unique. | Medium | Position as: “**DCS is an empirical probe** of when continuation helps; we quantify a regime where it cannot help because drafts already terminate,” and support it with activation/answer-change analyses and a $T_{draft}$ sweep. |


### (9B) Related-Work Taxonomy Matrix
| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---|---|---|---|---|---|
| Root | Test-time compute for SC-style LLM reasoning | [8][7] | Compare methods under compute budgets (tokens/calls/latency proxies) | This paper is a single-method case study; needs matched-budget evaluation | Risk: “dominance” claims are fragile without budget-aware curves |
| Branch 1 | Early stopping / adaptive halting |  | Answer-level signals can indicate “enough samples/steps” | DCS continues instead of halting | Medium overlap in “use early signals” axis |
| Leaf 1.1 | Vote-entropy / window stopping | [1] | Vote distribution stabilizes early | DCS reallocates compute rather than stopping | Low–Medium |
| Leaf 1.2 | Bayesian confidence posterior stopping | [2] | Confidence can be treated as evidence for answers | DCS uses interim answers (not token-prob confidence posteriors) | Medium |
| Leaf 1.3 | Answer-convergence stopping | [3] | Answers converge before full reasoning ends | DCS attempts to exploit interim answers by continuing branches | Medium |
| Branch 2 | Pruning / selection among hypotheses during SC |  | Intermediate structure reveals redundancy | DCS selects a few drafts to continue; pruning methods remove redundant ones | Medium |
| Leaf 2.1 | Thought-similarity pruning | [4] | Similar “thoughts” imply redundant computation | DCS does not compute similarity; uses interim-answer votes | Medium |
| Leaf 2.2 | Confidence+coverage pruning | [6] | A subset of hypotheses covers diversity while preserving confidence | DCS keeps fixed $B$ drafts then continues $k$ | Medium |
| Branch 3 | Prefix / partial-trace reuse |  | Partial traces contain reusable information | DCS is closest here | High |
| Leaf 3.1 | Prefix-guided resampling (prefix enhancement) | [5] | A good prefix can guide later generation | DCS continues *existing drafts* rather than resampling from a selected prefix | High overlap risk (closest neighbor) |
| Leaf 3.2 | Regeneration-based prefix reliability weighting | [9] | Correct traces reproduce answers under regeneration more often | DCS uses interim-answer vote + continuation budget rather than regeneration frequency weights | High overlap risk |
| Branch 4 | Compute-scaling / redundancy analyses |  | More compute can have diminishing/negative returns | This paper’s diagnosis should connect to these with concrete activation stats | Medium |
| Leaf 4.1 | Budget-aware evaluation frameworks | [8] | Fairness requires compute normalization | Current paper still lacks matched budgets | High risk to claims until fixed |
| Leaf 4.2 | Fair TTC evaluation protocol | [7] | Standardized prompting/extraction improves comparability | Your parser definition is currently missing | Medium |
| Leaf 4.3 | Overthinking / diminishing returns | [10] | Extra tokens can reduce marginal utility | Supports your “drafts too long” narrative | Low–Medium |


### (9C) Head-to-Head Comparison Matrix
| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---|---|---|---|---|---|
| [5] | Efficient SC-style inference | Use early confidence/answers to pick a promising **prefix** and guide later branches | Early-stage signal steers later compute | Prefix-guided **resampling** vs DCS **continuation of existing drafts** | Raises overlap risk for C1; related-work positioning must be explicit |
| [9] | Reliability/efficiency for SC-style CoT | **Truncate + regenerate** to measure prefix-consistency reliability; reweight votes | Uses partial traces + continuation/regeneration | DCS allocates tokens via interim-answer vote; not regeneration-frequency weighting | Another close neighbor; pushes C1 toward partially_overlapping |
| [6] | Token-efficient SC | Periodically prune hypotheses using confidence + coverage (set cover) | Uses intermediate signals to allocate compute | Pruning reduces hypothesis count; DCS keeps drafts then continues k | Overlap in goal; DCS needs clearer differentiation |
| [4] | Efficient SC | Thought-level similarity pruning of redundant chains | Uses intermediate structure to reduce wasted compute | Similarity-based pruning vs vote-based continuation | Overlap in “reuse intermediate info” axis |
| [2] | Efficient SC | Bayesian posterior over answers; stop when posterior mass high | Budget-aware decision to stop sampling | DCS continues instead of halting; also uses different signals | Strong baseline that motivates matched-budget evaluation |
| [1] | Efficient SC | Window/vote-entropy early stopping | Stops when votes converge | DCS reallocates tokens to continuations | Supports baseline selection; not a novelty threat |
| [3] | Efficient CoT | Stop when answer converges; learn-to-stop variants | Recognizes redundancy in long CoT | DCS’s diagnosis echoes redundancy findings | Makes C3 partially_overlapping |
| [8] | Budget-aware evaluation | Shows complex strategies often look good only because they spend more compute | Budget normalization emphasis | DCS should be evaluated as an allocation policy under fixed budgets | Supports revisions; increases scrutiny of current “Pareto” wording |
| [10] | Compute scaling analysis | Overthinking at high budgets; diminishing returns | “More tokens can hurt / waste” | DCS is a concrete case where extra stage adds overhead | Supports discussion but does not validate your mechanism without activation stats |


#### Contribution-level Novelty Conclusion
Overall, **C1 is partially overlapping** with existing partial-trace reuse / pruning / prefix-guided self-consistency methods, so the paper should avoid broad novelty claims and instead emphasize the specific continuation-based instantiation and hedged allocation rule. **C2 is supported** as a new empirical case study/negative result on DCS (but must be strengthened by matched-budget curves). **C3 is partially overlapping** with prior redundancy/early-exit insights; its value is strongest when presented as a *quantified boundary condition* for continuation-based budgeting, backed by activation and answer-change analyses.


### ASCII Diagram — Related-Work Taxonomy Tree (Layered)
```text
Related Work Taxonomy (Root: Test-time compute for SC-style reasoning)
├── Branch 1: Early stopping / adaptive halting
│   ├── Leaf 1.1: Vote-entropy / window stopping [1]
│   ├── Leaf 1.2: Bayesian confidence posterior stopping [2]
│   └── Leaf 1.3: Answer-convergence stopping [3]
├── Branch 2: Hypothesis pruning within SC
│   ├── Leaf 2.1: Thought-similarity pruning [4]
│   └── Leaf 2.2: Confidence+coverage pruning [6]
├── Branch 3: Prefix / partial-trace reuse
│   ├── Leaf 3.1: Prefix-guided resampling (prefix enhancement) [5]
│   └── Leaf 3.2: Regenerate-from-prefix reliability weighting [9]
└── Branch 4: Budget-aware evaluation & compute-scaling analyses
    ├── Leaf 4.1: Budget-aware evaluation frameworks [8]
    ├── Leaf 4.2: Fair TTC evaluation protocol [7]
    └── Leaf 4.3: Overthinking / diminishing returns analyses [10]

Position of this paper (DCS):
- Closest to Branch 3 (partial-trace reuse), but allocates compute by continuing a subset of *existing drafts*
  selected via interim-answer voting (not by resampling from a shared prefix or by pruning).
- Primary value (as written) is a boundary-condition negative result: continuation adds overhead when drafts already terminate.
```

## References
[1] Escape Sky-high Cost: Early-stopping Self-Consistency for Multi-step Reasoning 2401.10480

[2] CGES: Confidence-Guided Early Stopping for Efficient and Accurate Self-Consistency 2511.02603

[3] Answer Convergence as a Signal for Early Stopping in Reasoning 2506.02536

[4] Slim-SC: Thought Pruning for Efficient Scaling with Self-Consistency 2509.13990

[5] Path-Consistency with Prefix Enhancement for Efficient Inference in LLMs 2409.01281

[6] Confidence-Weighted Token Set Cover for Early Hypothesis Pruning in Self-Consistency 2508.03979

[7] FEval-TTC: Fair Evaluation Protocol for Test-Time Compute 2511.01203

[8] Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies 2406.06461

[9] Reliable Chain-of-Thought via Prefix Consistency 2605.07654

[10] When More Thinking Hurts: Overthinking in LLM Test-Time Compute Scaling 2604.10739

## Scores
Final Score: **4.5/10**.

Post-Revision Target: **[6.5, 7.5]/10**.

Rationale (score-driving factors):
- **Research value / insight:** The negative-result direction is useful, but currently under-validated because the key boundary condition (draft length vs solution length) is not experimentally swept.
- **Novelty:** The continuation-based instantiation has partial overlap with prefix/partial-trace reuse and pruning families; novelty is acceptable if repositioned as a minimal baseline + boundary-condition study.
- **Soundness / reproducibility:** Missing interim-answer parser and budget-matched comparisons are major issues for a compute-efficiency paper.
- **Fixability:** High—most deficits can be addressed with clear definitions plus a small set of targeted experiments and plots.