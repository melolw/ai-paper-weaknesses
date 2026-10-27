## Summary
This paper investigates whether the logit lens technique can accelerate perplexity-based code context compression by truncating transformer forward passes at intermediate layers. The authors propose ShallowPPL, which uses early-exit logit lens projections to approximate full-depth AMI (Approximated Mutual Information) scoring in LongCodeZip's two-stage compression pipeline. Evaluated on Long Code Completion (LCC) and RepoQA benchmarks with pre-registered success criteria (≥1.5× speedup, ≤1.0 point quality drop), the hypothesis does not hold: ShallowPPL achieves only 1.05× speedup while exceeding quality thresholds. Ablation studies reveal that coarse function ranking is the primary quality bottleneck and that quality scales nonlinearly with depth, with the last two layers contributing 3.83 percentage points on RepoQA.

The paper represents a responsible negative-result study that honestly tests a plausible efficiency hypothesis and provides diagnostic insights about why it fails. However, several issues weaken the scientific rigor: (1) the basic logit lens (raw unembedding) is used rather than the more reliable Tuned Lens with trained affine probes, potentially conflating projection weakness with intermediate-layer insufficiency; (2) conclusions about "fundamental properties of transformer representations for code" overgeneralize from a single model; (3) tension with recent literature showing intermediate layers can outperform final layers for embedding tasks (Skean et al., 2024/2025) is not addressed; (4) the per-forward-pass overhead explanation for limited speedup lacks profiling evidence.

Overall, the paper has genuine scientific value as a falsification study, but requires claim scoping, a Tuned Lens ablation or limitation acknowledgment, and literature tension discussion before the negative-result conclusion can be considered robust.

## Strengths
1. **Honest negative-result framing.** The paper pre-registers success criteria (≥1.5× speedup, ≤1.0 point quality drop) and openly reports that the hypothesis fails. This falsification-driven approach saves research effort and is scientifically valuable—many efficiency hypotheses go untested or unreported when they fail.

2. **Clean ablation design.** The configuration space exploration (both-shallow, hybrid, coarse-only shallow) and exit-layer sweep (L=14, 20, 24, 26) provide clear diagnostic insights. The finding that hybrid configuration (full coarse + shallow fine) recovers 81% of the quality gap is an actionable takeaway for future work.

3. **Task-specific evaluation.** The paper evaluates on two complementary code benchmarks (LCC and RepoQA) across multiple programming languages, providing stronger evidence than single-benchmark evaluation. The inclusion of a RAG baseline for context is appropriate.

4. **Diagnostic value beyond the negative result.** The identification that coarse function ranking is the primary quality bottleneck and that fine-grained scoring is robust to early-exit once correct functions are selected provides useful guidance for future efficiency research in code compression.

5. **Reproducibility commitment.** The paper states that code is publicly available and specifies the model, evaluation protocol, and implementation framework (vLLM with greedy decoding).

## Weaknesses
1. **Basic logit lens used instead of Tuned Lens (Major).** The paper tests early-exit inference using the raw unembedding matrix (basic logit lens) rather than the Tuned Lens with trained layer-specific affine probes (Belrose et al., 2023). The Tuned Lens paper explicitly states that the basic logit lens is "often brittle" and that the Tuned Lens is "more predictive, reliable and unbiased." By using the weaker variant, the paper cannot distinguish whether the negative result stems from (a) intermediate layers genuinely lacking code relevance signal, or (b) basic logit lens projection being insufficient to extract available signal. This design choice undermines the strength of the "final layers encode critical information that cannot be approximated" conclusion.

2. **Overgeneralized conclusions from single-model evaluation (Major).** Claims such as "final transformer layers encode critical information for code relevance scoring that cannot be approximated by intermediate representations" and "the failure stems from fundamental properties of transformer representations for code" generalize from a single 28-layer model (Qwen2.5-Coder-7B-Instruct) to all transformer representations for code. The findings may not hold for different model families, sizes, or architectures. Recent work (Skean et al., 2024/2025) shows intermediate layers can outperform final layers for embedding tasks, suggesting model- and task-dependent variation.

3. **Tension with intermediate-layer-superiority literature not addressed (Major).** Skean et al. (2024/2025) demonstrate that intermediate layers consistently outperform final layers across 32 text-embedding tasks, challenging the standard view on final-layer embeddings. The paper's conclusion that final layers are essential for code relevance scoring directly contradicts this finding, yet no discussion of why this tension exists (e.g., perplexity requires token-level probability calibration that embedding similarity does not) is provided.

4. **Per-forward-pass overhead explanation lacks profiling evidence (Minor).** Section 4.4 attributes limited speedup to "per-forward-pass overhead that dominates over layer computation cost" but does not provide timing decomposition data. Without profiling breakdown (layer computation vs. KV cache setup vs. embedding lookup), this remains a plausible hypothesis rather than a verified root cause.

5. **No variance reporting for timing measurements (Minor).** Timing measurements are averaged across 3 seeds, but no variance (std/CV) is reported. Given that speedup claims are in the 1.02-1.19× range, even small timing variance could affect the stability of these estimates.

## Key Issues
| # | Issue | Risk Level | Root Cause | Impact | Evidence Anchor |
|---|-------|------------|------------|--------|-----------------|
| 1 | Basic logit lens used instead of Tuned Lens | Major | Design choice: raw unembedding matrix does not address representational drift as effectively as trained affine probes | Negative result may conflate projection weakness with intermediate-layer insufficiency, weakening the core conclusion | Page 4 - Section 3.2 Method |
| 2 | Conclusions overgeneralize from single model | Major | No evaluation on other model families or sizes | "Fundamental properties of transformer representations for code" claim is unsupported beyond Qwen2.5-Coder-7B | Page 1 - Abstract, Page 6 - Conclusion |
| 3 | Tension with Skean et al. intermediate-layer findings unaddressed | Major | Related Work 2.3 cites Skean et al. but does not reconcile their intermediate-layer-superiority findings with this paper's conclusion | Reader may question why intermediate layers work for embeddings but not for perplexity scoring | Page 2 - Section 2.3 Related Work |
| 4 | Speedup overhead explanation lacks profiling evidence | Minor | No timing decomposition provided for per-forward-pass overhead claim | Root-cause diagnosis is plausible but not verified | Page 6 - Section 4.4 |
| 5 | Timing variance not reported | Minor | Averages across 3 seeds without std/CV | Speedup estimates in 1.02-1.19× range may be unstable | Page 5 - Tables 1-4 |

**Top-1 (Highest Risk):** Issue 1. Using the basic logit lens rather than the Tuned Lens is the most impactful design issue. If the negative result is partly an artifact of suboptimal projection, the paper's central claim—that intermediate representations cannot approximate full-depth AMI scores—is significantly weakened. This is the primary blocker for accepting the paper's conclusions as definitive.

## Actionable Suggestions
1. **Add Tuned Lens baseline or explicit limitation (Must, P0).** Train layer-specific affine probes following Belrose et al. (2023) and evaluate ShallowPPL with Tuned Lens projection. If results remain negative, the conclusion that "intermediate representations lack code relevance signal" is much stronger. If Tuned Lens improves quality, the conclusion should be revised to "basic logit lens projections are insufficient" rather than a broader claim about intermediate representations. If training Tuned Lens is too costly, add one paragraph in Section 3.2 explicitly acknowledging this limitation and bounding the conclusion to "basic logit lens" scope.

2. **Bound all "cannot be approximated" claims to tested conditions (Must, P0).** Replace definitive statements like "final transformer layers encode critical information... that cannot be approximated by intermediate representations" with scoped versions: "for the tested Qwen2.5-Coder-7B-Instruct model, final layers encode information... that is not captured by basic logit lens projections from intermediate representations." Apply this revision to Abstract (Page 1), Contribution C4 (Page 2), Section 4.3 (Page 5), and Conclusion (Page 6).

3. **Add discussion reconciling with Skean et al. intermediate-layer findings (Must, P1).** In Section 2.3 or a new subsection, add 2-3 sentences explaining why Skean et al.'s finding that intermediate layers outperform final layers for embeddings does not contradict this paper's finding for perplexity-based code relevance scoring. A plausible explanation: perplexity requires calibrated token-level probability distributions (achieved through full-depth autoregressive refinement), while embedding similarity relies on representation geometry where intermediate layers may capture richer syntactic-semantic structure. This discussion strengthens the paper's scientific rigor.

4. **Provide timing variance and optionally a simple profiling breakdown (Nice-to-have, P2).** Report mean±std for timing measurements across the 3 seeds to show speedup stability. Optionally, add a simple profiling table showing the percentage of compression time spent in layer computation vs. KV cache initialization vs. embedding lookup, which would directly support or refute the per-forward-pass overhead hypothesis.

5. **Add vLLM and CUDA versions to Appendix A (Nice-to-have, P2).** Include the exact vLLM version and CUDA toolkit version used for experiments, as these affect inference overhead profiles and timing reproducibility.

## Storyline Options + Writing Outlines
### Current Storyline Assessment

The current narrative follows a clear arc: Problem (long code contexts need compression) → Gap (LongCodeZip is expensive) → Hypothesis (intermediate layers can approximate full-depth scoring) → Result (hypothesis fails) → Diagnostic insight. This is appropriate for a negative-result paper. The main improvement area is claim scoping and the addition of literature tension discussion.

### Recommended Storyline Option (Revised Negative-Result Framing)

**Title suggestion:** "ShallowPPL: Why Logit Lens Early-Exit Cannot Accelerate Perplexity-Based Code Context Compression" — this version explicitly signals the negative result in the title, which is more honest and engaging for this paper type.

### Abstract Outline (complete, 5-sentence plan)

- **S1 (Problem + domain):** Long code contexts in repository-level tasks require compression to fit within language model context windows, with perplexity-based AMI scoring achieving strong quality but requiring expensive full forward passes.
- **S2 (Significance/Challenge):** Accelerating this scoring is critical for practical deployment, motivating the hypothesis that intermediate-layer representations could provide sufficient signal at reduced cost.
- **S3 (Gap/Prior limitation):** While intermediate layers have proven useful for interpretability and attention-based retrieval, it remains unclear whether they can support token-level probability calibration needed for perplexity scoring.
- **S4 (Method):** We investigate ShallowPPL, which truncates forward passes at layer $L$ and uses logit lens projections to approximate AMI scores at intermediate transformer layers.
- **S5 (Key result + bounded implication):** Our evaluation with pre-registered success criteria demonstrates that this hypothesis does not hold for the tested model and benchmarks: ShallowPPL achieves only 1.05× speedup while exceeding quality thresholds, with ablation revealing that coarse function ranking is the primary bottleneck and quality scales nonlinearly with depth.

### Introduction Outline (complete, paragraph-by-paragraph plan)

- **P1 (Big Picture + Prior Gap):** Repository-level code tasks require long context processing. Natural language compression methods fail for code due to structural dependencies. Conditional perplexity offers a principled alternative by measuring instruction-context alignment. LongCodeZip operationalizes this through AMI scoring.
- **P2 (Motivation + Research Question):** LongCodeZip requires full forward passes per code chunk, creating a computational bottleneck. Can intermediate-layer representations, successful for interpretability and attention-based retrieval, provide sufficient signal for perplexity-based code relevance scoring at reduced cost? Note that prior methods use different signals (attention vs. logits) and tasks (general text vs. code).
- **P3 (Method + Result Preview):** We test this hypothesis through ShallowPPL, evaluating early-exit logit lens approximations against pre-registered success criteria (≥1.5× speedup, ≤1.0 point quality drop). Results show the hypothesis does not hold under our evaluation: 1.05× speedup with quality exceedance on both benchmarks.
- **P4 (Contribution Summary):** (1) Investigation of ShallowPPL early-exit approach. (2) Rigorous evaluation demonstrating unfavorable quality-speed tradeoffs. (3) Ablation identifying coarse ranking as primary bottleneck and nonlinear depth scaling. (4) Diagnostic insights on why early-exit fails in this setting: per-pass overhead and final-layer information critical for the tested model.

## Priority Revision Plan
| Priority | Action | Effort | Expected Impact |
|----------|--------|--------|-----------------|
| **P0 (Must)** | Add Tuned Lens ablation or explicit limitation paragraph in Section 3.2 | High (if adding experiment) / Low (if text-only limitation) | Resolves the most critical validity risk: whether negative result is due to projection weakness vs. intermediate-layer insufficiency |
| **P0 (Must)** | Bound all "cannot be approximated" and "fundamental properties" claims to tested conditions | Low (text revision across Abstract, Intro, Section 4.3, Conclusion) | Eliminates overgeneralization risk and makes conclusions defensible |
| **P1 (Should)** | Add 2-3 sentence discussion reconciling with Skean et al. intermediate-layer findings | Low (add to Section 2.3 or new subsection) | Addresses literature tension and strengthens scientific rigor |
| **P1 (Should)** | Scope contribution C1 from "propose" to "investigate" and rephrase C4 to bounded claim | Low (text revision in Introduction) | Aligns contribution framing with negative-result narrative |
| **P2 (Nice-to-have)** | Report timing variance (mean±std) across 3 seeds | Low | Improves statistical reliability of speedup estimates |
| **P2 (Nice-to-have)** | Add vLLM and CUDA versions to Appendix A | Low | Improves timing measurement reproducibility |
| **P2 (Nice-to-have)** | Add one sentence in Section 4.4 acknowledging that per-forward-pass overhead explanation is a hypothesis not verified by profiling | Low | Improves objectivity of root-cause attribution |

**Revision Order Recommendation:** Execute P0 items first (Tuned Lens + claim scoping), then P1 (literature discussion + contribution rephrasing), then P2 (reproducibility details). P0 items are publication-critical; P1 items materially improve confidence; P2 items are optional quality improvements.

### ASCII Diagram — Revision Strategy Roadmap

```text
[P0: Tuned Lens ablation or limitation]
    -> [Resolve projection-vs-layer ambiguity]
    -> [Strengthen core negative-result conclusion]

[P0: Claim scoping]
    -> [Bound "cannot be approximated" to tested model]
    -> [Eliminate overgeneralization risk]

[P1: Literature tension discussion]
    -> [Explain why Skean et al. intermediate-layer findings don't contradict perplexity results]
    -> [Improve scientific rigor]

[P1: Contribution rephrasing]
    -> [Align "propose" with "investigate" narrative]
    -> [Improve story coherence]

[P2: Reproducibility details]
    -> [Add variance + versions]
    -> [Improve traceability]
```

## Experiment Inventory & Research Experiment Plan
### (a) Completed Experiment Inventory

| Exp ID | Objective / Hypothesis | Setup (data / split / protocol / baselines) | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|----------------------|---------------------------------------------|---------|--------------|-----------------|-------------------|
| E1 | Main results: ShallowPPL achieves ≥1.5× speedup with ≤1.0 pt quality drop | LCC + RepoQA; Qwen2.5-Coder-7B; vs. RAG (UniXcoder) + Full AMI (LongCodeZip) | ES, EM, AvgAcc, Time, Speedup | ShallowPPL fails both criteria: 1.05× speedup, quality exceeds threshold | Negative result confirmed | Only one model family tested; no variance on timing |
| E2 | Ablation: which compression stage is the bottleneck? | LCC; 5 configs (both-shallow L=14/20, hybrid L=14/20, baseline) | ES, Speedup | Coarse ranking is primary bottleneck; hybrid recovers 81% of quality gap | Stage-level diagnosis validated | No coarse-only shallow config results reported despite being mentioned in Section 3.3 |
| E3 | Exit-layer sweep on RepoQA | RepoQA; L=14, 24, 26, 28; full-depth baseline | AvgAcc, Speedup | Nonlinear quality-depth: last 2 layers contribute 3.83 pp | Nonlinear depth scaling confirmed | L=24 uses "both-shallow" while L=26 uses "hybrid" — config inconsistency between data points |
| E4 | RAG baseline comparison | LCC + RepoQA; UniXcoder embeddings with function-level chunking | ES, EM, AvgAcc, Time | ShallowPPL Hybrid outperforms RAG on quality but is much slower | Perplexity-based scoring superior to embeddings even when degraded | RAG speedup (25.6× on LCC) makes ShallowPPL's 1.05× look worse by comparison; no discussion of whether RAG + perplexity refinement could combine both |

### (b) Research-Theme Gap Diagnosis

The core research-value claim is that intermediate-layer representations are insufficient for perplexity-based code relevance scoring. This claim is **weakly supported** because: (1) only basic logit lens projection was tested, leaving open whether Tuned Lens projections could extract sufficient signal; (2) only one model (Qwen2.5-Coder-7B) was evaluated, limiting generalizability; (3) the tension with Skean et al.'s intermediate-layer-superiority findings for embeddings is not resolved, leaving the boundary between "when intermediate layers work" vs. "when they don't" unclear.

### (c) Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls / Baselines | Metrics | Success Criterion | Est. Cost / Time | Expected Quality Gain |
|-------------|------------|----------------|---------------------|---------|-------------------|------------------|----------------------|
| C1: Intermediate layers insufficient for code relevance | Tuned Lens projections (trained affine probes) improve early-exit quality compared to basic logit lens | Train Tuned Lens for layers 14, 20, 24, 26; evaluate ShallowPPL with Tuned Lens on LCC + RepoQA | Basic logit lens (current), Full AMI | ES, EM, AvgAcc, Speedup | If Tuned Lens achieves ≥1.0 point improvement, claim must be repositioned | 1-2 days GPU time on A100 | Resolves projection-vs-layer ambiguity; strengthens or revises core conclusion |
| C2: Coarse ranking is primary bottleneck | Fine-grained early-exit with full-depth coarse ranking achieves acceptable quality at meaningful speedup | Hybrid config with Tuned Lens at L=24 on fine-grained stage; measure end-to-end speedup including coarse stage overhead | Current hybrid (basic logit lens), Full AMI | ES, Speedup, Per-stage timing | Speedup ≥1.2× with quality drop ≤1.0 pt | 1 day | Quantifies practical hybrid efficiency gains |
| C3: Findings generalize beyond Qwen2.5-Coder | Early-exit failure pattern holds across model families | Evaluate ShallowPPL on one additional model (e.g., Llama-3-8B-Instruct or CodeLlama-7B) on LCC | Same baselines | ES, AvgAcc, Speedup | Qualitative pattern consistency (speedup limited, quality drops nonlinearly) | 1-2 days | Bounds or extends generalizability of negative result |

### (d) Traceability

- E (Tuned Lens) → Maps to unresolved Claim C1 (intermediate-layer insufficiency) → Quality gain: resolves major validity risk
- E (Hybrid Tuned Lens) → Maps to unresolved practical utility question → Quality gain: provides actionable efficiency guidance
- E (Multi-model) → Maps to overgeneralization concern in C3 → Quality gain: bounds or extends conclusion scope

### ASCII Diagram — Experiment Upgrade Plan

```text
Stage 1 (P0, this week): Tuned Lens ablation
    -> Train affine probes for L=14,20,24,26
    -> Evaluate on LCC + RepoQA
    -> If quality improves significantly: reposition conclusion
    -> If quality remains poor: strengthen "intermediate layers insufficient" claim

Stage 2 (P1, if P0 confirms): Multi-model generalization
    -> Test ShallowPPL on one additional model family
    -> Confirm/falsify pattern consistency

Stage 3 (P2, polish): Reproducibility additions
    -> Add timing variance, vLLM/CUDA versions, profiling breakdown
```

## Novelty Verification & Related-Work Matrix
### 9A: Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|-------------------|-----|------------|----------------------|
| C1 | ShallowPPL: early-exit logit lens approach to approximate perplexity-based code relevance scoring at intermediate transformer layers | [1], [4] | partially_overlapping | No direct prior work applies logit lens to perplexity scoring for code compression. However, Tuned Lens [1] refines the projection technique, and ILRe [4] uses intermediate layers for context compression (though with attention scores, not perplexity). Residual novelty: first to test this specific mechanism on this specific task. | High | Acknowledge that basic logit lens is a weaker variant than Tuned Lens; scope novelty to "basic logit lens for code AMI scoring" |
| C2 | Rigorous evaluation with pre-registered success criteria demonstrating ShallowPPL fails to achieve favorable quality-speed tradeoffs | [5], [6] | supported | Negative-result falsification with pre-registered criteria is genuinely novel. Prompt compression latency studies [6] focus on end-to-end trade-offs for general text, not on intermediate-layer perplexity approximation for code. | High | None needed; claim is evidence-consistent |
| C3 | Ablation insights: coarse function ranking is primary bottleneck; quality scales nonlinearly with depth (last 2 layers contribute 3.83 pp) | [2], [3] | partially_overlapping | The coarse-vs-fine bottleneck diagnosis is novel for code compression. However, the "last layers matter most" finding partially overlaps with Lee et al. [2] (final layers critical for fine-tuning) and is in tension with Skean et al. [3] (intermediate layers can outperform final layers for embeddings). | Medium | Bound "nonlinear depth scaling" to tested model/task; discuss why it differs from Skean et al.'s embedding findings |

### 9B: Related-Work Taxonomy Matrix

| Taxonomy Layer | Branch / Leaf | Representative Papers [n] | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|---------------|--------------------------|-------------------|-------------------------|-------------------|
| Root: Efficient Context Processing | Branch 1: Intermediate Representation Methods | | Intermediate layers contain useful signal | This paper tests whether that signal suffices for perplexity-based ranking | Medium: Skean [3] shows intermediate layers CAN outperform final layers for embeddings |
| | Leaf 1.1: Logit Lens / Projection Methods | [1] | Raw or trained projection can decode intermediate states | Tuned Lens [1] uses trained affine probes; this paper uses raw unembedding | High: using weaker projection may explain failure |
| | Leaf 1.2: Attention-Based Retrieval | [4] | Attention scores from designated layer can identify relevant tokens | ILRe [4] uses attention, not perplexity; targets general text, not code | Low: different signal mechanism |
| Root: Efficient Context Processing | Branch 2: Prompt Compression Efficiency | | Compression should preserve quality while reducing latency | This paper targets acceleration of scoring, not compression algorithm design | Low |
| | Leaf 2.1: Perplexity-Based Compression | [7] | Conditional perplexity measures relevance | Perception Compressor [7] also uses perplexity but with full forward passes | Low: shares scoring paradigm but not efficiency mechanism |
| | Leaf 2.2: Latency Trade-off Studies | [6] | Compression overhead may cancel decoding gains | Kummer et al. [6] measures end-to-end latency; this paper measures scoring speedup | Low: complementary but different focus |
| Root: Efficient Context Processing | Branch 3: Layer Importance Analysis | | Different layers encode different information | This paper finds final layers critical for code relevance scoring | Medium: contradicts/tensions with Skean et al. [3] |
| | Leaf 3.1: Final-Layer Criticality | [2] | Final layers need fine-tuning for downstream tasks | Lee et al. [2] shows final layers matter for fine-tuning; consistent with this paper's depth finding | Low: consistent direction |
| | Leaf 3.2: Intermediate-Layer Superiority | [3] | Intermediate layers outperform final layers for embeddings | Skean et al. [3] finds opposite pattern for embeddings; tension needs explanation | High: unresolved contradiction |

### 9C: Head-to-Head Comparison Matrix

| Ref [n] | Problem / Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|---------|------------------|-------------|------------------------|-----------------|-------------------------|
| [1] Tuned Lens | Intermediate state decoding for LLMs | Trained affine probes per layer | Uses intermediate layer representations | Tuned Lens trains probes; this paper uses raw unembedding. Tuned Lens targets interpretability; this paper targets compression efficiency. | High: suggests basic logit lens may be suboptimal projection choice |
| [3] Layer by Layer | Intermediate layer quality for embeddings | Info-theory + geometry metrics across 32 tasks | Investigates intermediate vs. final layer quality | Focuses on embedding similarity; this paper focuses on perplexity-based probability calibration. Finds intermediate layers CAN be superior. | High: creates tension with paper's conclusion; requires discussion |
| [4] ILRe | Context compression via intermediate layers | Attention scores from designated layer | Uses intermediate representations for context compression | Uses attention scores, not perplexity. Targets general text. Achieves speedups. | Medium: shows intermediate layers CAN work for compression, but with different signal |
| [6] Prompt Compression in the Wild | End-to-end latency trade-offs | Large-scale timing profiling across models/hardware | Measures compression overhead vs. decoding speedup | Focuses on general prompt compression; this paper focuses on scoring acceleration. | Low: complementary perspective on overhead |

### Contribution-level Novelty Conclusion

C1 is **partially_overlapping**: the specific combination of basic logit lens early-exit for perplexity-based code AMI scoring has not been directly tested before, but the building blocks (logit lens, intermediate representations, AMI scoring) all exist in prior work. The residual novelty is in the targeted application and the negative-result falsification.

C2 is **supported**: the rigorous negative evaluation with pre-registered criteria is genuinely novel and scientifically valuable.

C3 is **partially_overlapping**: the coarse-vs-fine bottleneck diagnosis is novel for code compression, but the nonlinear depth scaling finding partially overlaps with layer-importance literature and is in tension with Skean et al.'s intermediate-layer-superiority results. The claim requires scoping to the tested model and task.

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
Efficient Context Processing (Root)
├── Branch 1: Intermediate Representation Methods
│   ├── Leaf 1.1: Logit Lens / Projection Methods [1]
│   │   └── Value: Trained affine probes outperform raw unembedding
│   └── Leaf 1.2: Attention-Based Retrieval [4]
│       └── Value: Intermediate attention scores enable context compression
├── Branch 2: Prompt Compression Efficiency
│   ├── Leaf 2.1: Perplexity-Based Compression [7]
│   │   └── Value: Perplexity measures relevance; full forward passes required
│   └── Leaf 2.2: Latency Trade-off Studies [6]
│       └── Value: Compression overhead may cancel decoding gains
└── Branch 3: Layer Importance Analysis
    ├── Leaf 3.1: Final-Layer Criticality [2]
    │   └── Value: Final layers essential for downstream task adaptation
    └── Leaf 3.2: Intermediate-Layer Superiority [3]
        └── Value: Intermediate layers outperform final layers for embeddings

[This Paper Position: Branch 1 Leaf 1.1 + Branch 3, testing whether basic
 logit lens early-exit can approximate perplexity scoring for code compression.
 Negative result: intermediate layers insufficient for this specific task/signal.]
```

## References
[1] Eliciting Latent Predictions from Transformers with the Tuned Lens 2303.08112

[2] What Would Elsa Do? Freezing Layers During Transformer Fine-Tuning 1911.03090

[3] Layer by Layer: Uncovering Hidden Representations in Language Models 2502.02013

[4] Ilre: Intermediate layer retrieval for context compression in causal language models 2508.17892

[5] On the Effectiveness of Context Compression for Repository-Level Tasks: An Empirical Investigation 2604.13725

[6] Prompt Compression in the Wild: Measuring Latency, Rate Adherence, and Quality for Faster LLM Inference 2604.02985

[7] Perception Compressor: A Training-Free Prompt Compression Framework in Long Context Scenarios 2409.19272

## Scores
Final Score: 5.5/10

The paper presents a scientifically valuable negative-result study that honestly tests a plausible efficiency hypothesis and provides useful diagnostic insights. The pre-registered evaluation protocol, clean ablation design, and task-specific evaluation on code benchmarks are strengths. However, the core conclusion is weakened by three factors: (1) using the basic logit lens instead of the Tuned Lens conflates projection weakness with intermediate-layer insufficiency; (2) conclusions overgeneralize from a single model to "fundamental properties of transformer representations for code"; (3) tension with intermediate-layer-superiority literature (Skean et al.) is unaddressed. These issues reduce confidence in the negative-result conclusion until P0 revisions are completed.

Post-Revision Target: [7.0, 8.0]/10

If the authors add a Tuned Lens ablation (or explicitly acknowledge this limitation and bound conclusions to "basic logit lens"), scope all claims to tested conditions, and add the literature tension discussion, the paper would present a robust and valuable falsification study with clear scientific contribution. The diagnostic insights about coarse ranking being the primary bottleneck and the nonlinear depth scaling pattern are actionable findings that benefit the field regardless of the final verdict on intermediate-layer sufficiency.

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|------|-----------------|-----------------|-------------------------|
| Page 1 (Abstract + Intro P1-P3) | 4 | Covered | — |
| Page 2 (Contributions + Related Work 2.1-2.3) | 3 | Partially covered | Section 2.1 (Prompt Compression) and 2.2 (Code Context Compression) are non-substantive literature survey paragraphs without method-specific claims affecting conclusions |
| Page 3 (Method 3.1 Background) | 1 | Covered | — |
| Page 4 (Method 3.2-3.3 ShallowPPL + Config Space) | 1 | Covered | — |
| Page 5 (Experiments 4.2-4.3 Main Results + Ablation) | 1 | Covered | — |
| Page 6 (Section 4.4 + Conclusion) | 2 | Covered | — |
| Page 7 (References) | 0 | Skipped | Non-substantive reference list |
| Page 8 (Appendix A Implementation Details) | 1 | Covered | — |

**Total annotations: 12** (within recommended range 12-25). Main-body density: 1-4 per substantive page. Appendix: 1 annotation on the single substantive appendix page.