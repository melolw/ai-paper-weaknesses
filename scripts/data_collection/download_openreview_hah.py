"""
download_openreview_hah.py
==========================
Downloads reviews for the 43 new HAH papers from the OpenReview API
and saves them in the existing openreview JSON format.

Requirements:
    pip install openreview-py

Usage:
    python scripts/data_collection/download_openreview_hah.py

Writes to: arg_outputs/openreview/raw/<paper_id>_openreview.json
Skips papers that already have a non-empty file.
"""

import json
import time
from pathlib import Path

import openreview

SCRIPT_DIR = Path(__file__).parent
RAW_DIR    = (SCRIPT_DIR / "../../arg_outputs/openreview/raw").resolve()

PAPERS = {
    "HAH_2025_YOO_ingroup_bias":                     "SF7BjKnqdh",
    "HAH_2025_TAN_ai_self_recognition":              "7TzkOum3Nu",
    "HAH_2025_BAI_persona_prompting":                "sVaRgmH8FE",
    "HAH_2025_JUNG_parameter_vs_testtime_scaling":   "wU35L1GZud",
    "HAH_2025_HYUN_diverse_inference_arc":           "295UNarKmq",
    "HAH_2025_TERRAGNI_simulating_twosided_job_marketplaces": "pjpkEHH5YS",
    "HAH_2025_FONG_impact_reduced_towing_fees": "I7meDPJFy8",
    "HAH_2025_JIANG_badscientist_research_agent_write": "7MPstNz66e",
    "HAH_2025_SRIVASTAVA_echo_multiagent_ai_system": "4nrWtE6oZ9",
    "HAH_2025_ABIR_multitarget_parallel_drug_discovery": "AhFsKmuaCb",
    "HAH_2025_KHAN_psyspace_simulating_emergent_psychological": "WAbHXkmBIn",
    "HAH_2025_CHOI_thermodynamic_guardrails_bond_graphbased": "hreVjQIgyt",
    "HAH_2025_ZHANG_visible_yet_unreadable_systematic": "if6RZty9HK",
    "HAH_2025_LIN_llmdriven_discovery_highentropy_catalysts": "Ka1WYEwLdC",
    "HAH_2025_JAYASEKARA_simulating_strategic_reasoning_digital": "L4arZChBJD",
    "HAH_2025_HOLLAND_mechsci_scaling_clinical_science": "rgpgukbeVf",
    "HAH_2025_GREISEN_reasoning_models_outperform_standard": "yXYEbPQp8x",
    "HAH_2025_ZUO_multillm_multiprompt_strategies_covid19": "zYDXTzql3n",
    "HAH_2025_CHANG_magellan_guided_mcts_latent": "wVn3uPvm9W",
    "HAH_2025_YANG_beyond_adam_aiauthored_discovery": "vUJOhgV3zh",
    "HAH_2025_PEI_behavioral_fingerprinting_large_language": "s4gTj3fOIo",
    "HAH_2025_HUANG_aiassisted_exploratory_causal_modeling": "neQWbqbgSs",
    "HAH_2025_BRONIKOWSKI_scalable_oversight_multiagent_systems": "l5Wrcgyobp",
    "HAH_2025_TAO_sustainable_investment_decisionmaking_office": "hjEsIk0Nux",
    "HAH_2025_LIU_uncertaintyaware_roleswitching_debate_improving": "heYWeCpOlS",
    "HAH_2025_GUO_endocrine_unity_diversity_crosstissue": "h40Nyr36om",
    "HAH_2025_SHEN_multiagent_social_simulation_experimental": "emsnDnmtYP",
    "HAH_2025_BASU_feasibilityguided_fair_adaptive_reinforcement": "d7Uvmmpo0z",
    "HAH_2025_HO_decontextualization_everywhere_systematic_audit": "cK8YYMc65B",
    "HAH_2025_LONGHITANO_transit_timing_variations_exoplanet": "Yja2KMahOL",
    "HAH_2025_KOPETZKY_borges_library_procedural_universes": "X0rpsv88au",
    "HAH_2025_LEWIS_architectural_immune_system_framework": "ShWjvhAZGs",
    "HAH_2025_HO_unitmath_unitaware_numerical_reasoning": "OG8sFxeNHv",
    "HAH_2025_SZWARCFITER_small_detours_deliver_big": "NDpRTCW3sM",
    "HAH_2025_WANG_survival_useful_evolutionary_boids": "N7Kh0K33Dk",
    "HAH_2025_WU_towards_automatic_evaluation_selection": "MIjY6VNtY0",
    "HAH_2025_KIANG_mentormind_riskaware_constraintgrounded_advice": "LqukdleDgU",
    "HAH_2025_BERMEJO_qitt_multiscale_substructure_cosmological": "LENY7OWxmN",
    "HAH_2025_LI_coalignment_rethinking_alignment_bidirectional": "G5jK2OMT2q",
    "HAH_2025_DESHPANDE_hardwareconditioned_generative_channel_modeling": "ExGHHgTM2p",
    "HAH_2025_WEHR_educational_attainment_cognitive_profile": "EWYarfMZU2",
    "HAH_2025_KONG_mind_guarding_mind_framework": "E2XBNokxDy",
    "HAH_2025_XIA_green_design_energyguided_reranking": "BxscqmB9Rs",
    "HAH_2025_TREHAN_consistency_confound_stronger_alignment": "B6ZrLXou3u",
    "HAH_2025_LIU_ivtfuse_efficient_visionlanguage_guided": "71C5p8pm6s",
    "HAH_2025_XU_selfspec_modelauthored_specifications_reliable": "6pr7BUGkLp",
    "HAH_2025_BRONIKOWSKI_stylistic_contrastive_learning_humanlike": "0fo0d9Tbey",
    "HAH_2025_VALENTINI_aifirst_proof_concept_simulating": "0d3Nloe9pB",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_reviewer_id(signatures) -> str:
    flat = []
    for s in (signatures or []):
        if isinstance(s, list):
            flat.extend(str(x) for x in s)
        else:
            flat.append(str(s))
    for sig in flat:
        parts = sig.split("/")
        for part in reversed(parts):
            if part.startswith("Reviewer_"):
                return part
    return flat[0].split("/")[-1] if flat else "Reviewer_unknown"


def extract_field(content: dict, *keys: str) -> str:
    for key in keys:
        val = content.get(key)
        if val is None:
            continue
        if isinstance(val, dict):
            val = val.get("value", "")
        if val:
            return str(val).strip()
    return ""


def is_ai_reviewer(signatures, content: dict) -> bool:
    score = content.get("ai_review_score")
    if score is not None:
        val = score.get("value", 0) if isinstance(score, dict) else score
        if val and val != 0:
            return True
    flat = []
    for s in (signatures or []):
        if isinstance(s, list):
            flat.extend(str(x) for x in s)
        else:
            flat.append(str(s))
    sig_str = " ".join(flat).lower()
    return any(x in sig_str for x in ("_ai_", "paperreview", "llm_reviewer", "airev"))

def convert_note(note) -> dict:
    c = note.content if isinstance(note.content, dict) else {}
    return {
        "reviewer_id":              extract_reviewer_id(note.signatures),
        "review_type":              "ai" if is_ai_reviewer(note.signatures, c) else "human",
        "summary":                  extract_field(c, "summary", "paper_summary"),
        "strengths_and_weaknesses": extract_field(c, "strengths_and_weaknesses") or extract_field(c, "weaknesses"),
        "questions":                extract_field(c, "questions", "questions_and_suggestions", "limitations"),
        "rating":                   extract_field(c, "overall", "rating", "overall_assessment", "recommendation"),
        "confidence":               extract_field(c, "confidence"),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net",
        username="melissa.loew@stud.tu-darmstadt.de",
        password="nQw^Sm98wZH.KhM"
    )

    total = len(PAPERS)
    done = skipped = 0
    failed = []

    for i, (paper_id, forum_id) in enumerate(PAPERS.items(), 1):
        out_path = RAW_DIR / f"{paper_id}_openreview.json"

        # Re-download even if file exists (to fix field mapping)
        # Comment this block back in once all files are correctly populated:
        # if out_path.exists():
        #     existing = json.loads(out_path.read_text())
        #     if existing.get("reviews"):
        #         print(f"  [SKIP] {paper_id}")
        #         skipped += 1
        #         continue

        print(f"  [{i}/{total}] {paper_id} ({forum_id})", end=" ... ", flush=True)

        try:
            notes   = client.get_notes(forum=forum_id)
            reviews = []
            for note in notes:
                invs = getattr(note, "invitations", None) or [getattr(note, "invitation", "") or ""]
                flat_invs = []
                for i in invs:
                    if isinstance(i, list):
                        flat_invs.extend(str(x) for x in i)
                    else:
                        flat_invs.append(str(i))
                inv = " ".join(flat_invs).lower()
                if any(x in inv for x in ("official_review", "review")):
                    reviews.append(convert_note(note))

            out = {
                "paper_id":   paper_id,
                "source":     "openreview",
                "review_url": f"https://openreview.net/forum?id={forum_id}",
                "venue":      "Agents4Science",
                "reviews":    reviews,
            }
            out_path.write_text(
                json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"{len(reviews)} review(s)")
            done += 1

        except Exception as e:
            print(f"ERROR: {e}")
            failed.append((paper_id, str(e)))

        time.sleep(0.5)

    print(f"\nDone: {done} downloaded, {skipped} skipped, {len(failed)} failed")
    if failed:
        print("Failed:")
        for p, e in failed:
            print(f"  {p}: {e}")


if __name__ == "__main__":
    main()