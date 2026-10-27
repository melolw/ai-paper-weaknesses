# Preliminary Observations:
N/A

# Expected Review Outcome:
## Paper Summary
This paper defines a fine-grained multimodal, multi-document claim verification task where a textual claim is decomposed into AMR nodes and tuples, and each element is assigned an entailment label with respect to a set of trusted sources that may include text, images, video, and audio. The authors present: (1) a dataset construction pipeline that builds a cross-document, cross-media KG from the NewsStories corpus, textualizes visual and audio content, synthesizes entailed claims via AMR traversal, then manipulates claims via RL to generate contradicted and neutral variants; (2) a hierarchical model that fuses encoders for multiple modalities and a GCN operating on the claim AMR to predict both sample-level and fine-grained labels; and (3) experiments on the new benchmark M3DC and on MOCHEG, with ablations and qualitative analyses.

## Summary Of Strengths
- Task and problem framing: The paper tackles a useful and underexplored setting, namely fine-grained claim verification across multiple documents and modalities, with explicit per-AMR-node and per-tuple labels. This addresses important practical needs in fact-checking where users require pinpointed justifications rather than only sample-level labels.
- Dataset construction pipeline: The cross-document, cross-media KG illustrated in Figure 1 is well-motivated. The claim generation and manipulation flow in Figure 2 is clearly described and shows how entailed claims are produced from KG traversals and then perturbed into neutral or contradicted forms, supporting balanced label coverage.
- Model design: The architecture in Figure 3 reasonably separates modality-specific encoding from graph reasoning on the claim AMR. Using AMR for semantic decomposition is a defensible choice for fine-grained analyses.
- Empirical evaluation: The study considers both sample-level and fine-grained labeling, with results reported per class and macro F1. Tables 2–4 include baselines (FGVE, MOCHEG method, LLaVA-1.5, MiniGPT-v2) and useful ablations across modalities.
- Qualitative visualization: Figure 4 provides a helpful qualitative comparison on a nontrivial claim about a crash cause, clearly indicating how the proposed method concentrates contradictions on the specific “pilot error” substructure while baselines spread errors more diffusely.

## Summary Of Weaknesses
1) Reliability of labels and circularity risks in dataset creation
- The majority of the dataset’s labels are synthetic. Section 3.1.3 uses a reward model to guide claim manipulation and then uses a fine-grained entailment classifier (trained on MNLI, FEVER-NLI, ANLI with FGVE-style constraints) both to score manipulations and eventually to create synthetic labels that also supervise the final verifier (end of Section 3.2.2, “We train our model using cross-entropy loss with labels from the trained fine-grained entailment classifier”). This creates a nontrivial risk of circularity or biasing the evaluation toward the same decision boundaries learned by the reward model. While Table 2 also includes a small human-labeled subset, the scale is just 30 samples per setting, which is too small to validate generalization or to quantify label drift from the synthetic generator. The paper needs a larger and independent human-labeled test set.

2) Human annotation scale and protocol
- The human study is tiny (30 samples) for both sample-level and fine-grained evaluation, given the large scope claimed for M3DC. Inter-annotator agreement is defined as simple percent agreement (Equation 5) without measures that account for class imbalance such as Cohen’s kappa or Krippendorff’s alpha. The fine-grained IAA of 68% in Appendix A.3.1 is difficult to interpret without chance-corrected metrics, confusion breakdown, and per-class agreement. This limits confidence in “human” results reported in Table 2.

3) Equations and modeling details are underspecified or inconsistent
- Equation 3 presents a neighbor-averaging update without any learnable weight matrices or nonlinearity, which does not match the standard GCN formulation cited (Kipf and Welling, 2016) that uses H^(l+1) = σ(Â H^(l) W^(l)). The omission makes it unclear what is actually trained in the node encoder, and how AMR structure influences features.
- Equation 4 defines edge features as concatenated linear transforms of endpoint node features with W_e, while the text mentions W_e and b_e but the bias term does not appear. More importantly, how these edge features feed back into node updates is not specified.
- The total training objective for the model is unclear. Section 3.2.1 says the concatenated multimodal embedding is fed into LongT5 with the GSG objective for pretraining. Section 3.2.2 then describes a two-layer GCN over the claim AMR initialized with features from the multimodal encoder and AMR features. But details like when and how joint training is performed, how gradients flow across modules, and full hyperparameters are missing.

4) Reward definition inconsistency
- The reward in Equation 1 is r(c, ĉ, ŷ) = P(ŷ | p, ĉ) − (Σ_{yi≠ŷ} P(yi | p, ĉ) + ROUGE(c, ĉ)). If the goal is to keep ĉ similar to c, ROUGE should increase the reward, not decrease it by being added within the parentheses that are subtracted. As written, the reward penalizes higher ROUGE, which conflicts with the text “retains as much similarity to the original claim as possible.” This looks like a sign error or a mis-specification that could materially change the manipulator’s behavior.

5) Evidence and modality usage are dominated by text
- Multiple parts (Sections 3.1.1, 3.2.1, Appendix A.5) admit that visual and audio signals are ultimately turned into captions or summaries, with the KG largely textual. In Table 4, adding video and audio changes results only marginally and sometimes worsens performance. This calls into question the robustness of the multimodal setting and whether the benchmark actually requires strong non-textual reasoning. Additional experiments that use raw visual or audio features directly per-claim, or per-KE attribution tracing back to non-textual evidence, would strengthen the multimodality claim.

6) Baseline setup may disadvantage LVLMs and misses stronger comparators
- LVLMs are forced into token-level fine-grained prediction then mapped back to AMR nodes (Appendix A.4). This is a fragile transformation, and the prompts in Table 5–6 operate on a single document at a time with majority voting for multi-document, which can suppress multi-source reasoning. Table 2 shows zero F1 on neutral for LVLMs, which suggests prompt or mapping issues rather than inherent inability. Stronger and more directly comparable multimodal baselines, or at least more careful prompting and ablation on instruction templates, are needed.

7) Sparse dataset statistics, splits, and controls
- The paper claims 400K+ claims (Section 3.1 and Table 1 shows 414,405), but there is limited reporting on train/validation/test splits, class distribution per split, topic overlap between splits, or leakage controls across clusters. Without these, it is difficult to assess whether models are evaluated under realistic generalization.

8) Table-level observations raising questions about claims
- From Table 2 on M3DC, the proposed model’s overall F1 is 0.49 on synthetic fine-grained and 0.39 on human fine-grained, suggesting a nontrivial drop on human data. The text states performance “tracks closely,” but a 0.10 macro-F1 difference at the fine-grained level is substantial on a three-class task. This should be acknowledged and dissected.
- On MOCHEG (Table 3), the proposed model improves fine-grained macro-F1 over LVLMs (0.39 vs 0.23/0.32), but underperforms LVLMs at sample level (0.47 vs 0.53). The discussion attributes this to dataset differences, but additional analyses like calibration, error types, and qualitative audits would help.

9) Ethical and legal considerations are thin
- The dataset construction crawls articles, images, and videos from news sources; the paper does not discuss licensing, rights to redistribute media, or whether only URLs and derived captions are released. Section A.6 focuses on dual-use but not on copyright, privacy in videos, or handling sensitive content. For a resource paper, this is important.

10) Clarity issues and minor inconsistencies
- Table 1 lists “Multi-News” as the source for “Ours,” while Section 3.1 states NewsStories. Clarify the source corpus.
- Several typos and name inconsistencies: “Checma et al.” in Table 1 vs “Cheema et al.” elsewhere; “reftab:misinfo_results” unresolved in Appendix A.3; some figure captions include partially garbled text in the labeling interface.
- Some component choices and hyperparameters are missing: GCN layer sizes, activation functions, dropout, fusion details for ImageBind + LongT5, optimization settings for the graph classifiers, and GSG masking details beyond “top 3 sentences” selection.

11) Claims of fine-grained evaluation vs. evidence attribution
- While the model predicts fine-grained labels over AMR structures, it does not provide explicit evidence grounding per node/edge. Figure 4 shows predicted labels on the graph but not which documents, sentences, frames, or audio segments were decisive. For a verification task, explainability would benefit from evidence attribution.

Sharp figure- and table-specific comments
- Figure 1 convincingly illustrates how AMR trees from text, image captions, and audio summaries are linked into a cross-media KG with coreference edges. This supports the dataset’s intent. However, because visual and audio evidence are textualized, the KG nodes labeled “visual data” still represent text, which weakens the novelty of multimodal grounding.
- Figure 2 is central to the data pipeline; it clearly shows the switch from an entailed claim to a contradicted claim by inserting “74 individuals” and “5 people injured.” This nicely demonstrates fine-grained manipulation but also highlights a risk: the manipulator might introduce unrealistic phrasings that become dataset artifacts detectable by models.
- Figure 3 presents the full architecture, but as noted, the mathematical details in Equations 3–4 do not fully align with the diagram or standard GCN updates. The paper should reconcile these.
- Table 2 is the keystone results table for M3DC. The near-zero LVLM neutral F1 and the sizable gap between synthetic and human fine-grained scores suggest that the benchmark and prompting pipeline may be inducing artifacts. Reporting confidence intervals and per-class supports would help interpret differences.
- Table 4 ablations show video improves results but audio slightly hurts. This supports the claim that text dominates, but the paper should probe why audio is detrimental and whether this is due to the specific textualization or encoder alignment.

## Potentially Missing Related Work
1) Braun et al., “DEFAME: Dynamic Evidence-based FAct-checking with Multimodal Experts,” 2025 — Proposes a modular LVLM-based fact-checking pipeline with joint textual and visual reasoning and a new benchmark. It is a directly comparable systems-level approach to multimodal fact-checking. Should be discussed in Related Work and compared in Section 4.3, as it could offer a strong LVLM baseline configuration more faithful to multi-document evidence than the token-to-AMR mapping used here.

2) Wang et al., “MFC-Bench: Benchmarking Multimodal Fact-Checking with Large Vision-Language Models,” 2025 — Introduces a large benchmark and systematic LVLM evaluation for multimodal news claims. Relevant to Section 2 and as an evaluation baseline; discuss in Related Works and, if feasible, include as an external testbed in Section 4.

3) Kakizaki et al., “MAFT: Multimodal Automated Fact-Checking via Textualization,” 2025 — Uses explicit textualization of images, video, and audio before applying LMs, architecturally analogous to this paper’s textualization of non-text modalities. It should be cited in Section 2 and contrasted with this work’s ImageBind + LongT5 fusion in Section 3.2.1.

4) Xu et al., “MMM-Fact: A Multimodal, Multi-Domain Fact-Checking Dataset with Multi-Level Retrieval Difficulty,” 2025 — A large multimodal dataset for cross-document, cross-modal verification. It should be referenced in Section 2.1 and considered as an external evaluation target in Section 4 to test generalization beyond M3DC and MOCHEG.

5) Rothermel et al., “VeriTaS: The First Dynamic Benchmark for Multimodal Automated Fact-Checking,” 2026 — A dynamic benchmark for multimodal claims. Add to Section 2 and discuss applicability as a robustness testbed in Discussion.

6) Yu et al., “Knowledge Debugger: Diagnosis of Knowledge Inconsistency with Multimodal Graph,” 2026 — A graph-based framework for detecting inconsistencies across multimodal graphs, conceptually close to the AMR-GNN approach here. Cite in Section 2.2 and compare with the GCN formulation around Equations 3–4.

7) GC2MFND: “Multi-Granularity Conflict and Domain-Guided Calibration for Multimodal Fake News Detection,” 2026 — Explicit modeling of local and global conflict features in multimodal misinformation. Cite in Section 2.2 and discuss alignment with the paper’s fine-grained inconsistency detection goals.

## Comments Suggestions And Typos
Actionable questions and suggestions
1) Address Equation 1 and Equation 3–4 issues: 
- Please clarify whether ROUGE is intended to increase or decrease the reward in Equation 1. If the current sign is a typo, provide corrected results or a sensitivity study. 
- For Equations 3–4, specify the complete GCN formulation with weight matrices, activation functions, and how edge features influence node updates. If you use a variant (e.g., edge-conditioned GCN), state it explicitly and cite accordingly. Include full hyperparameters.

2) Expand and harden the human-labeled evaluation:
- Increase the human-annotated test set beyond 30 samples, provide chance-corrected agreement (e.g., κ), and release label guidelines. If scale is infeasible now, at least include a second independent human-labeled split for M3DC and report performance with confidence intervals.

3) Strengthen evidence attribution and explainability:
- For several claims, show which sentences, images, frames, or audio segments contribute to each AMR node/edge decision. An attention-over-evidence plot or top-k evidence snippets per label would substantiate the fine-grained reasoning story.

4) Revisit LVLM baselines:
- Provide a more faithful multi-document LVLM baseline that reasons jointly over documents, and test stronger instruction-tuned models. At minimum, supplement Table 2 with prompt ablations and report per-class supports and CIs to interpret the near-zero neutral F1.

5) Clarify dataset construction and rights:
- Specify precisely what is released: URLs, derived captions, AMRs, and labels, or original media. Describe licensing and redistribution policy. Add a section on copyright and privacy vetting, including removal protocols for takedown or sensitive content.

6) Multimodality diagnostics:
- Extend Table 4 with per-class changes and show cases where visual or audio truly flip a decision relative to text only. Consider a controlled subset where visual or audio evidence is required by construction to test that the system can leverage them.

7) Splits and leakage controls:
- Report exact train/dev/test sizes, class distributions, topic-level partitioning, and leakage checks across clusters. Add an out-of-topic evaluation to probe robustness.

Typos and inconsistencies
- Table 1: “Checma et al.” → “Cheema et al.”
- Table 1 lists “Multi-News” as the source for “Ours,” while Section 3.1 states NewsStories. Please reconcile.
- Several figure captions in Appendix A.3–A.4 contain garbled placeholder text and unresolved references like “reftab:misinfo_results.” 
- Minor grammatical issues throughout; a careful proofreading pass would help.

Criteria that could change my score
- Corrected equations and a clearer, reproducible model description.
- Expanded human-labeled test set with rigorous IAA and confidence intervals, showing consistent gains over strong LVLM baselines.
- Stronger evidence attribution demonstrating genuine multimodal, multi-document reasoning.
- Clearer dataset release plan with legal and ethical safeguards.

## Confidence
4 Quite sure after careful checking: I tried to check the important points carefully. It’s unlikely, though conceivable, that I missed something that should affect my ratings.

## Soundness
2.5 Between Poor and Acceptable: Useful ideas, but key methodological specifications are missing or inconsistent, synthetic labeling risks circularity, and evaluation on human labels is too small to be conclusive.

## Excitement
3.0 Interesting: The problem and framing are compelling, and the pipeline is thoughtfully designed, but execution details and evaluation gaps temper enthusiasm.

## Overall Assessment
2.5 Borderline Findings: The paper may meet minimal standards but requires improvements before being accepted to Findings. While the task is timely and the overall system is thoughtfully composed, the combination of synthetic-label circularity, small human-labeled evaluation, unclear or inconsistent equations, and limited evidence that non-text modalities are truly needed undermines readiness for the main track. With clearer modeling details, stronger human evaluations, improved baselines, and firmer ethical considerations, this could become a solid contribution.

## Best Paper Justification
N/A

## Limitations And Societal Impact
The paper acknowledges that most evidence is textualized and that genuine news articles may be inconsistent across sources (Appendix A.5). However, the societal section focuses mainly on dual-use. Additional concerns include:
- Copyright and redistribution rights for crawled images and videos; clarity on release format is required.
- Potential biases from synthetic claim manipulation that may produce linguistic artifacts detectable by models, which could misrepresent performance on real claims.
- Limited coverage of accessibility for different languages or communities, given NewsStories’ domain.
- Risk of automating judgments on sensitive topics without robust evidence attribution.

Concrete suggestions:
- Include a licensing and takedown policy.
- Audit synthetic claims for stylistic artifacts and report their prevalence.
- Provide demographic or topical breakdowns and discuss generalization beyond English-language news.
- Emphasize human-in-the-loop use with transparent evidence highlighting.

## Ethical concerns
The dataset construction scrapes and processes third-party media. The paper does not clearly state the legal basis for redistribution, nor whether any personal data in videos is handled appropriately. Evidence attribution is limited, which may encourage overreliance on black-box predictions in sensitive contexts. These concerns should be addressed before any public release.

## Needs Ethics Review
Yes

## Reproducibility
3 Reproducible with difficulty: Many components are described, but important training specifics and exact equations are incomplete or inconsistent. The complex pipeline, reliance on several large pretrained systems, and lack of clear splits and leakage controls hinder easy reproduction.

## Datasets
3 Potentially useful: If released with clear legal status and splits, the dataset could be valuable. The dominance of textualized modalities and synthetic labels, plus small human annotations, currently limits immediate impact.

## Software
3 Potentially useful.: Code for the pipeline and model would be helpful, but reproducibility depends on clarifying missing details and ensuring dependencies and prompts are provided.