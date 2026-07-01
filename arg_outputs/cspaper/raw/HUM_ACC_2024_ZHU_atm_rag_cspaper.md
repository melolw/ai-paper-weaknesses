# Desk Rejection Assessment:
## Paper Length
Pass ✅.

## Topic Compatibility
Pass ✅. The paper proposes a learning method for robust retrieval‑augmented generation, squarely within NLP topics of Question Answering, Generation, Information Retrieval, and Machine Learning for NLP.

## Minimum Quality
Pass ✅. The submission includes Abstract, Introduction, Related Work, Method (ATM with Attacker/Generator and MITO loss), Experiments, Results with tables and figures, Analyses and Ablations, Conclusion, Limitations, and Ethics Statement. The technical content is sufficiently complete for scholarly review.

## Prompt Injection and Hidden Manipulation Detection
Pass ✅. I did not find any attempts to manipulate the review process or hidden instructions within the provided content.

# Expected Review Outcome:

## Paper Summary
This paper introduces ATM, a two‑agent adversarial tuning scheme to improve the robustness of LLM generators in RAG‑QA. An Attacker LLM fabricates semantically related but misleading passages and applies list permutation; a Generator LLM is trained to answer correctly in the presence of these perturbations. The Attacker is aligned using DPO with rewards derived from the Generator’s perplexity on the gold answer (Equations 5 and 8). The Generator is optimized with a Multi‑agent Iterative Tuning Optimization (MITO) loss that combines standard SFT on attacked contexts and a token‑level KL regularizer between generation distributions under clean and attacked contexts (Equation 9). Experiments on NQ, TriviaQA, WebQuestions, and PopQA show consistent gains over strong RALM baselines, with detailed robustness analyses across fabrication sources, numbers, and ablations.

## Summary Of Strengths
- Clear and focused problem: robustness of RAG generators to fabricated or noisy retrieved text.
- Methodologically coherent multi‑agent setup. The Attacker’s reward is tightly coupled to the Generator via PPL on gold answers (Eq. 5), and the iterative DPO alignment (Eq. 8) is well motivated.
- The Generator objective is explicitly written (Eq. 2) and instantiated by the MITO loss (Eq. 9), which encourages output stability between clean and attacked contexts while still maximizing likelihood on attacked inputs.
- Strong empirical results. Table 1 shows sizable improvements over REAR, Self‑RAG, and RetRobust on three datasets; Table 3 shows generalization to unseen PopQA; Table 4 analyzes the effect of α in Eq. 9; Table 5 ablates the two attack components (fabrication generation and list permutation), quantifying their individual utility. Robustness curves in Figure 4 show graceful degradation as the number of fabricated documents increases.
- Figures are helpful and concrete: Figure 2 visualizes the end‑to‑end ATM workflow; Figure 3 illustrates examples of ATTACKER outputs and permutations, clarifying what “fabrications” look like in practice; Figure 5 clarifies how token‑level losses are computed under attacked vs. clean inputs.
- The paper includes analysis of Attacker strength over iterations (Figure 6) and a case study (Table 7), which support the claim that the attacker becomes more misleading and the training signal is nontrivial.
- Relevance and potential impact: an actionable recipe to harden RAG generators against LLM‑generated misinformation and positional noise.

## Summary Of Weaknesses
1) Objective clarity and theoretical grounding
- Equation 2 defines a high‑level target with a generic dist[·] but does not specify the exact divergence until Eq. 9, and the linkage is only loosely argued. The chosen KL term in Eq. 9 is asymmetric and both distributions come from the same model under two inputs; minimizing KL between two outputs of the same parameterized model can encourage “collapse” without guaranteeing movement toward the clean‑context distribution. While the SFT term on attacked inputs partially addresses this, the paper does not analyze the interaction or provide stability guarantees. A short derivation or discussion connecting Eq. 2 to Eq. 9, and why the particular KL direction was chosen, would strengthen the methodology section. Figure 5 helps with implementation details but does not resolve the conceptual gap.

2) Reward design for the Attacker
- The reward r(q, d′) in Eq. 7 uses PPL of the gold answer conditional on the single fabricated document {d′} rather than on the mixed list D′ that the Generator actually consumes. This may over‑estimate the harmfulness of a fabricated snippet that becomes less influential in a mixed list. It also ignores interactions between multiple fabrications and order. The paper should justify this design choice or compare to a reward that accounts for the full attacked list (including permutation), since the list‑level effect is central to ATM.

3) Baseline comparability and missing controls
- Several baselines use different backbones or sizes (e.g., Self‑RAG 13B and RetRobust 13B vs. ATM on Llama2‑7B), which clouds fairness despite ATM still performing well. The paper should report a matched‑backbone comparison wherever possible, or add a note quantifying size effects.  
- A simple, highly relevant control is missing: training the same Generator with randomly generated fabrications or with adversarially chosen irrelevant passages but without Attacker DPO, and with/without the KL term. Table 5 partially ablates attacks but does not include a strong “random/no‑attacker” data augmentation baseline. This is important to show the added value of adversarial preference alignment versus generic noise‑augmented SFT.

4) Evaluation design details and transparency
- The construction of the evaluation benchmark fixes 10 documents (5 retrieved + 5 fabricated). While practical, it bakes in a particular corruption rate and may not reflect real‑world mixtures. Figure 4 varies the number of fabrications but always keeps total documents at 10; it would help to also vary total K to confirm the trends across context lengths.  
- The paper states Mixtral 8×7B generates test‑time fabrications by default, while the Attacker used during training is a Mistral 7B model. It is not fully clear which model produces the “various generators” in Table 2 for each test condition, whether they also permute lists, and whether any of these overlap with the Attacker used during training. Please clarify and ensure isolation between training and test perturbation models.  
- Some model names and iteration tags are inconsistent across tables (“ATM7B‑Inr2”, “ATM7B‑Inre2”, “Iter2”), which makes it harder to track which runs correspond to which settings.

5) Limited analysis of position sensitivity
- The work claims mitigation of “Lost in the Middle” via list permutation, yet there is no direct measurement of position sensitivity or an evaluation that isolates LP’s contribution beyond Table 5. A controlled test that fixes document content but varies positions would make this claim more convincing.

6) Reproducibility gaps
- Important training details are still missing or scattered: learning rates, batch sizes, optimizer settings, stopping criteria for both DPO and MITO, and exact values of β in Eq. 8 and α in Eq. 9 per experiment. Appendix D.3 lists infrastructure and training stack, but not full hyperparameters. It is unclear whether code and the constructed evaluation benchmark will be released. As a result, reproducibility is moderate rather than easy.

7) Metric choice and qualitative validity
- All metrics are EM/Subspan‑EM/F1 on short‑form QA. While standard, the claim of “resisting fabrications” could be further supported by human judgments of factuality under adversarial contexts, or by error taxonomy on failure cases to confirm the defense is against targeted misleading content rather than generic noise.

8) Potential overfitting to fabricated style
- The Attacker is steered using examples drawn from top‑ranked retrieved passages (Appendix A.1), and the Generator adapts to these particular fabrication styles. Although Table 2 varies generator sources, additional evidence that ATM is robust to very different fabrication distributions or to adversarial poisoning of retrieval indices would broaden the claim.

9) Minor notation and exposition issues
- Equation 3 uses the concatenation operator ⊕ with a footnote marker “1”, but the footnote content is not present in the main text; clarify how long contexts are truncated and how documents are delimited.  
- Algorithm 1, line 8 indexes D_{i,j} when computing PPL for A_i|Q_i, D_{i,j}; D_{i,j} appears to reference a single fabricated document, but the symbol D elsewhere denotes lists. A notational cleanup would help.

Detailed figure/table engagement:
- Figure 2 effectively communicates the training loop: retrieval → Attacker’s fabrication and permutation → DPO update with PPL‑based rewards → Generator MITO update toward the Golden Answer. This visualization substantiates the iterative, coupled optimization claim and clarifies data flow that is only tersely described in Section 4.2.  
- Figure 3 shows concrete examples of fabricated passages and a permutation sketch; these qualitatively demonstrate semantic closeness yet factual divergence, supporting the paper’s assertion that fabrications are challenging.  
- Figure 5 is instrumental to understanding the MITO implementation, especially the left‑padding alignment for token‑level KL. However, it also surfaces a concern: because both distributions in KL are produced by the same model, gradients propagate through both branches. The paper should state whether one branch is detached to avoid degenerate minimization; otherwise the KL term could shrink trivially.  
- Table 1 is central: ATM7B‑Iter2 outperforms RetRobust13B and Self‑RAG13B on NQ/TriviaQA/WebQ across EM/F1, suggesting the adversarial process matters beyond scale. Reporting confidence intervals or multiple seeds would further substantiate these gains.  
- Table 4 demonstrates sensitivity to α, showing that α in [0.1, 0.2] is most stable; α=0.5 destabilizes training. This nicely connects to the earlier concern that the KL trade‑off can hurt if over‑weighted.  
- Table 5 shows both attack components contribute; removing fabrication generation is most harmful (−4.51 F1), which supports the necessity of the Attacker beyond mere shuffling.

## Potentially Missing Related Work
1) Tran et al., “Adversarial Robustness in Visual RAG: Exploring Multi‑Image Grounding with Top‑k Retrieval,” 2026 — studies adversarial corruption in RAG under multimodal settings; relevant for framing broader robustness and could be discussed in Section 2.2 as an extension avenue and in Section 5 to motivate more challenging evaluations.
2) Xiao et al., “MASS‑RAG: Multi‑Agent Synthesis Retrieval‑Augmented Generation,” 2026 — multi‑agent RAG architecture oriented to evidence synthesis; compare against ATM’s adversarial multi‑agent design in Related Work and discuss complementary strengths in Section 6.
3) Nguyen et al., “MA‑RAG: Multi‑Agent Retrieval‑Augmented Generation via Collaborative Chain‑of‑Thought Reasoning,” 2025 — cooperative multi‑agent alternative; cite in Section 2 and discuss as a contrasting setup to adversarial tuning.
4) Pang et al., “PRA‑RAG: Provably Robust Aggregation in Retrieval‑Augmented Generation against Retrieval Corruption,” 2025 — offers theoretical robustness guarantees at aggregation; should be contrasted with ATM’s empirical adversarial training in Section 2.2 and possibly as a baseline concept in Section 5.
5) Chen et al., “ShieldRAG: Safeguarding Retrieval‑Augmented Generation from Untrusted Knowledge Bases,” 2025 — focuses on defenses against untrusted KBs; include in Section 2.2 and discuss joint applicability with ATM.
6) Baban et al., “Optimizing Retrieval‑Augmented Generation with Multi‑Agent Hybrid Retrieval,” 2025 — retrieval‑side multi‑agent optimization; discuss in Related Work as complementary to generator‑side training and in future work about joint optimization with retrievers.
7) Xiao et al., “RAGentA: Multi‑Agent Retrieval‑Augmented Generation for Attributed Question Answering,” 2025 — agent‑based decomposition with attribution; relevant to robustness and should be mentioned in Section 2.
8) Zhang et al., “Beyond Semantic Relevance: Counterfactual Risk Minimization for Robust Retrieval‑Augmented Generation,” 2026 — proposes a different training paradigm for robustness; comparing objectives would sharpen the positioning of MITO in Section 4.
9) Xiao et al., “Adversarial Yet Cooperative: Multi‑Perspective Reasoning in Retrieval‑Augmented Language Models,” 2026 — adversarial reasoning loop over retrieved evidence; compare interaction dynamics and training signals in Section 2.2.

## Comments Suggestions And Typos
Actionable questions and suggestions:
- Please clarify the exact implementation of the KL term in Eq. 9: which branch is detached in backpropagation, if any? If neither is detached, explain why trivial minimization is avoided. Consider experimenting with a stop‑gradient on the clean branch to anchor attacked outputs to clean distributions.  
- Justify the document‑level reward design for the Attacker (Eq. 7). Provide an ablation where reward is computed over the full attacked list D′, and optionally include a diversity‑promoting regularizer to avoid mode collapse of fabrications.  
- Add a “random/no‑attacker” augmentation baseline: same training set size and same KL term, but fabrications created by sampling irrelevant or shuffled content without DPO. This would isolate the value of adversarial preference alignment.  
- Provide matched‑backbone comparisons wherever possible (e.g., a RetRobust‑7B or Self‑RAG‑7B implementation under your retrieval and prompting), and report variability or confidence intervals for key results in Table 1.  
- Include a position‑sensitivity evaluation that holds content fixed and systematically varies positions, to directly substantiate the “LP mitigates Lost in the Middle” claim beyond Table 5.  
- Clean up notation and labels: unify “Iter”/“Inr”/“Inre”, and ensure Equation 3’s footnote about ⊕ and truncation rules appears in the main paper.  
- Release code, evaluation scripts, and the fabricated‑document benchmark or provide precise generation seeds/prompts. This would raise the reproducibility rating.

Typos and minor issues:
- In multiple places: “a Adversarial Tuning” → “an Adversarial Tuning”.  
- Section 5.2: “$\mathrm{ATM}_{7\mathrm{B - Ber2}}$” appears to be a typo for “Iter2”.  
- Tables 1, 2, 3: inconsistent naming “Inr”, “Inre”, “Iter”.  
- Figure 5 caption: “loss‑masked and attention‑masked” reads oddly; consider “masked from loss and attention”.

Criteria that could change my score upward during rebuttal:
- Provide matched‑size baselines and a strong random‑augmentation control, together with clear hyperparameters and training details.  
- Clarify KL implementation and show that stopping gradients or alternative divergences produce similar or better gains.  
- Add the position‑sensitivity experiment and full‑list reward ablation for the Attacker.

## Confidence
4: Quite sure after careful checking. I examined the methodology, equations, figures, tables, and experiments carefully; some implementation specifics remain unclear but do not change the overall assessment.

## Soundness
3.5: Between Acceptable and Strong. The method is coherent and empirically supported, though some design choices (KL coupling and reward scope) would benefit from deeper analysis and additional controls.

## Excitement
3.5: Between interesting and exciting. The adversarial multi‑agent angle for robust RAG is timely and practically relevant.

## Overall Assessment
4: Conference. Solid contribution with a clear idea, nontrivial engineering, and convincing empirical gains. Some methodological clarity and evaluation fairness issues remain, but they are addressable and do not undercut the central claims.

## Best Paper Justification
N/A.

## Limitations And Societal Impact
The paper acknowledges training cost. Additional points:  
- Dual‑use: the Attacker constitutes a capable misinformation generator. Mitigations could include releasing red‑teaming‑only checkpoints, filters, or access controls.  
- Bias/fairness: fabricated content might disproportionately target specific entities or demographics; the paper should discuss safeguards and how datasets avoid toxic or defaming generations.  
- Over‑reliance on Wikipedia‑centric retrieval risks underrepresenting low‑resource knowledge; consider multilingual or domain‑specific robustness in future work.

## Ethical concerns
None beyond the dual‑use risks noted; the ethics statement addresses the intention, but more explicit guidance on safe release and misuse prevention would be welcome.

## Needs Ethics Review
No.

## Reproducibility
3.5: Mostly reproducible to reproducible with some difficulty. Many components and prompts are described, but full hyperparameters, seeds, and code/benchmark availability are unclear.

## Datasets
3: Potentially useful. The constructed benchmark with fabricated documents could be useful if released with generation scripts and seeds.

## Software
3: Potentially useful. If ATM code and training pipelines are released, they would be of practical interest; current text does not confirm availability.