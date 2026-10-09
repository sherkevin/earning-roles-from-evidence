#!/usr/bin/env python3
"""Build the numeric expected experiment matrix and verify its arithmetic."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path("/Users/jingwu/work/earning-roles")
ARTICLE = ROOT / "article/aamas2027/expected_experiment_matrix_v4_20261009"
DOCS = ROOT / "docs/paper/aamas2027/expected_experiment_matrix_v4_20261009"
ARTIFACTS = ROOT / "artifacts/aamas2027/expected_experiment_matrix_v4_20261009"
TEX = ARTICLE / "expected_experiment_matrix.tex"
JSON_PATH = DOCS / "expected_results.json"
AUDIT_PATH = DOCS / "numeric_audit.json"
README_PATH = DOCS / "README.md"
LAMBDA = 0.10

SOURCE_URLS = [
    {
        "title": "Strictly Proper Scoring Rules, Prediction, and Estimation",
        "authors": "Gneiting and Raftery",
        "year": 2007,
        "url": "https://doi.org/10.1198/016214506000001437",
        "use": "Brier/log-loss interpretation; proper scoring-rule discipline",
    },
    {
        "title": "On Calibration of Modern Neural Networks",
        "authors": "Guo et al.",
        "year": 2017,
        "url": "https://proceedings.mlr.press/v70/guo17a.html",
        "use": "Calibration as a separate endpoint rather than a substitute for discrimination",
    },
    {
        "title": "A Contextual-Bandit Approach to Personalized News Article Recommendation",
        "authors": "Li et al.",
        "year": 2010,
        "url": "https://doi.org/10.1145/1772690.1772758",
        "use": "Contextual-bandit comparison framing; domain-specific lifts are not transplanted",
    },
    {
        "title": "Doubly Robust Policy Evaluation and Learning",
        "authors": "Dudik, Langford, and Li",
        "year": 2011,
        "url": "https://arxiv.org/abs/1103.4601",
        "use": "Selected-only feedback, propensities, and off-policy evaluation",
    },
    {
        "title": "A Contextual Bandit Bake-off",
        "authors": "Bietti, Agarwal, and Langford",
        "year": 2021,
        "url": "https://jmlr.org/papers/v22/18-863.html",
        "use": "Trade-offs and no universal dominance across contextual-bandit regimes",
    },
    {
        "title": "Open Bandit Dataset and Pipeline",
        "authors": "Saito et al.",
        "year": 2021,
        "url": "https://arxiv.org/abs/2008.07146",
        "use": "Logged bandit feedback and reproducible off-policy evaluation",
    },
    {
        "title": "Riemannian Walk for Incremental Learning",
        "authors": "Chaudhry et al.",
        "year": 2018,
        "url": "https://arxiv.org/abs/1801.10112",
        "use": "Forgetting is distinct from adaptation/recovery",
    },
    {
        "title": "SelectiveNet",
        "authors": "Geifman and El-Yaniv",
        "year": 2019,
        "url": "https://proceedings.mlr.press/v97/geifman19a.html",
        "use": "Coverage and selective risk must be reported jointly",
    },
]

cost_parts = [
    "selection",
    "execution",
    "publish_read",
    "judgment_or_matched_masked_call",
    "assignment_commit",
    "communication",
    "model_api_token_tool",
    "verification",
    "update",
    "queue_retry",
    "repair",
    "state_storage",
    "replay",
]

# The first eight components form the shared 0.87 comparison base required by
# the main paper. Arm-specific update, queue/retry, repair, storage, and replay
# complete the cost. Splitting components does not change the historical totals.
def cost_row(update, queue_retry_total, state_replay_total):
    return [
        0.08, 0.30, 0.10, 0.15, 0.02, 0.04, 0.17, 0.01,
        update,
        round(0.70 * queue_retry_total, 3),
        round(0.30 * queue_retry_total, 3),
        round(0.60 * state_replay_total, 3),
        round(0.40 * state_replay_total, 3),
    ]


cost_templates = {
    "uniform": cost_row(0.00, 0.08, 0.05),
    "no_update": cost_row(0.00, 0.10, 0.05),
    "raw": cost_row(0.04, 0.12, 0.07),
    "terminal": cost_row(0.07, 0.13, 0.08),
    "context": cost_row(0.10, 0.15, 0.10),
    "task_ridge": cost_row(0.14, 0.16, 0.12),
    "matched_composition": cost_row(0.15, 0.16, 0.13),
    "matched_rls": cost_row(0.14, 0.17, 0.13),
    "matched_sgd": cost_row(0.13, 0.16, 0.13),
    "matched_periodic_refit": cost_row(0.16, 0.18, 0.14),
    "pooled": cost_row(0.13, 0.16, 0.12),
    "rare": cost_row(0.16, 0.17, 0.14),
    "public_only": cost_row(0.06, 0.14, 0.11),
    "delayed_only": cost_row(0.08, 0.12, 0.08),
    "history_only": cost_row(0.08, 0.13, 0.08),
}

for key, values in cost_templates.items():
    assert len(values) == len(cost_parts), key


def qcu(quality: float, cost: float) -> float:
    return round(quality - LAMBDA * cost, 3)


def stream_sd_for_halfwidth(half_width: float, n_streams: int = 18) -> float:
    return round(half_width * math.sqrt(n_streams) / 1.96, 6)


def complete_cost_breakdown(total: float):
    base_values = [0.08, 0.30, 0.10, 0.15, 0.02, 0.04, 0.17, 0.01]
    remaining = round(total - sum(base_values), 6)
    variable = [
        round(remaining * 0.35, 6),
        round(remaining * 0.25, 6),
        round(remaining * 0.10, 6),
        round(remaining * 0.18, 6),
    ]
    variable.append(round(remaining - sum(variable), 6))
    return dict(zip(cost_parts, base_values + variable))


def policy(quality: float, cost: float, **kwargs):
    row = {
        "quality": quality,
        "complete_cost": cost,
        "utility": qcu(quality, cost),
        "cost_template_id": f"row_specific_C_{cost:.2f}",
        "cost_breakdown": complete_cost_breakdown(cost),
        "expected_wall_seconds_per_attempt": round(18.0 * cost, 2),
    }
    row.update(kwargs)
    return row


def service_policy(quality, cost, regret, publish_p95, read_p95, update_p95,
                   service_lag_p95, backlog, state_kib, drop_rate, cpu_ms,
                   ram_mib, replay_ms, **kwargs):
    return policy(
        quality,
        cost,
        payoff=quality,
        regret_vs_oracle_0_650=regret,
        publish_p50_ms=round(0.60 * publish_p95, 2),
        publish_p95_ms=publish_p95,
        read_assignment_p50_ms=round(0.60 * read_p95, 2),
        read_assignment_p95_ms=read_p95,
        update_p50_ms=None if update_p95 is None else round(0.60 * update_p95, 2),
        update_p95_ms=update_p95,
        service_lag_p95_ms=service_lag_p95,
        backlog_p95_events=backlog,
        state_kib=state_kib,
        drop_timeout_rate=drop_rate,
        cpu_ms_per_event=cpu_ms,
        gpu_ms_per_event=0.0,
        ram_peak_mib=ram_mib,
        model_calls_per_1000_arrivals=0,
        input_tokens_per_1000_arrivals=0,
        output_tokens_per_1000_arrivals=0,
        tool_calls_per_1000_arrivals=0,
        replay_ms_per_1000_arrivals=replay_ms,
        expected_wall_seconds_per_attempt=round(service_lag_p95 / 1000.0, 4),
        **kwargs,
    )


def policy_safety(quality: float, cost: float, coverage: float, false_attribution_claimed: float):
    return policy(
        quality,
        cost,
        coverage=coverage,
        unknown_rate=round(1.0 - coverage, 3),
        false_attribution_all_attempts=round(coverage * false_attribution_claimed, 4),
        false_attribution_claimed=false_attribution_claimed,
    )


data = {
    "kind": "numeric_expected_experiment_table",
    "version": "expected_v4_20261009",
    "status": "EXPECTED_NOT_OBSERVED",
    "scientific_result": False,
    "benchmark_runs": 0,
    "api_calls": 0,
    "gpu_jobs": 0,
    "canonical_scope": "sole numeric reference for the current main.pdf experiment matrix; never an observed result",
    "provenance": {
        "authoritative_pdf": "artifacts/aamas2027/main.pdf",
        "authoritative_pdf_sha256": "85fdb1f46ce9919de21a28bbd8e51a7b79862de13eec1d7befa98893a0150591",
        "execution_manifest": "docs/paper/aamas2027/EXPERIMENT_MATRIX_EXECUTION_MANIFEST_20261008.md",
        "execution_manifest_sha256": "16f524ce4f559cf877a7b97423355f7816cf5688b7008fb4115eefe0ed8e956e",
        "conditional_direction_guide": "article/aamas2027/guides/v5_20261008/guide_experiment_matrix.tex",
        "conditional_direction_guide_sha256": "e45ae037f4385d7c421f69677ce8c90f36f1cda3f6f0d7054d918b17ff2a9f0b",
        "numeric_mother": "docs/paper/aamas2027/expected_experiment_matrix_v3_20261009/expected_results.json",
        "uncertainty_mother": "docs/paper/aamas2027/guides/v2_20261008/joint_model_spec.json",
    },
    "design": {
        "utility": "U = Y - lambda * C",
        "lambda": LAMBDA,
        "cost_unit": "complete cost per attempted assignment, normalized to matched-uniform mean = 1.00",
        "cost_components": cost_parts,
        "cost_templates": cost_templates,
        "roots": 3,
        "streams_per_root_arm": 6,
        "independent_streams_per_arm": 18,
        "artifactrole_attempts_per_stream": 120,
        "h1_common_heldout_cases_per_stream": 96,
        "h4_mutations_per_owner_stratum_per_stream": 40,
        "peerselect_warmup_arrivals_per_stream": 1000,
        "peerselect_scored_arrivals_per_stream": 5000,
        "hardware_runtime_envelope": {
            "cpu": "4 logical CPU cores allocated per stream",
            "gpu": "none for online selector/update; gpu_ms_per_event = 0",
            "ram_limit_mib": 1024,
            "model_api_token_tool_calls": "0 in PeerSelect; ArtifactRole charged through normalized complete-cost ledger",
            "wall_time": "reported per attempt for ArtifactRole and as end-to-end service lag for PeerSelect",
        },
        "uncertainty_unit": "independently reset stream; episodes within stream are dependent",
        "interval": "expected 95% planning interval from root-stratified paired stream bootstrap",
        "planning_half_width": {
            "single_arm": {
                "brier": 0.008,
                "log_loss_nats": 0.018,
                "ece_10_equal_mass_bins": 0.006,
                "auc": 0.020,
                "quality_or_payoff": 0.012,
                "complete_cost": 0.030,
                "utility": 0.011,
                "rate": 0.015,
                "forgetting": 0.020,
                "recovery_selected_updates": 1.2,
                "nonzero_latency_relative": 0.10,
                "state_kib_relative": 0.10,
            },
            "paired_contrast": {
                "brier": 0.006,
                "log_loss_nats": 0.012,
                "ece_10_equal_mass_bins": 0.004,
                "auc": 0.014,
                "quality_or_payoff": 0.009,
                "complete_cost": 0.020,
                "utility": 0.008,
                "rate": 0.010,
                "forgetting": 0.015,
                "recovery_selected_updates": 0.8,
            },
        },
        "precision_model": {
            "formula": "half_width = 1.96 * assumed_stream_sd / sqrt(18)",
            "single_arm_stream_sd_assumption": {
                name: stream_sd_for_halfwidth(h)
                for name, h in {
                    "brier": 0.008, "log_loss_nats": 0.018,
                    "ece_10_equal_mass_bins": 0.006, "auc": 0.020,
                    "quality_or_payoff": 0.012, "complete_cost": 0.030,
                    "utility": 0.011, "rate": 0.015,
                    "forgetting": 0.020, "recovery_selected_updates": 1.2,
                }.items()
            },
            "paired_stream_sd_assumption": {
                name: stream_sd_for_halfwidth(h)
                for name, h in {
                    "brier": 0.006, "log_loss_nats": 0.012,
                    "ece_10_equal_mass_bins": 0.004, "auc": 0.014,
                    "quality_or_payoff": 0.009, "complete_cost": 0.020,
                    "utility": 0.008, "rate": 0.010,
                    "forgetting": 0.015, "recovery_selected_updates": 0.8,
                }.items()
            },
            "root_stratification": "six streams within each of three structural roots; root-stratified bootstrap is the execution estimator",
            "status": "planning precision assumption, not observed variance",
        },
        "denominators": {
            "H1": "frozen common held-out cohort; missing/invalid/UNKNOWN preserved by the frozen label rule and bounds",
            "H2": "all sealed assignments and attempted outcomes (ITT); per-protocol companion reported separately",
            "H3": "all arrivals and attempted updates, including failed, dropped, timed-out, no-op, and UNKNOWN",
            "H4_false_attribution_all": "all owner-truth-eligible mutation attempts",
            "H4_false_attribution_claimed": "non-UNKNOWN claimed mutation attempts with owner truth",
            "H4_unknown_coverage": "all mutation attempts",
        },
    },
    "correspondence": {
        "RQ1": ["RQ1-I", "RQ1-II"],
        "RQ2": ["RQ2-I", "RQ2-II", "RQ2-III"],
        "RQ3": ["RQ3-I", "RQ3-II"],
        "RQ4": ["RQ4-I", "RQ4-II"],
    },
    "sources": SOURCE_URLS,
    "cells": {},
}

# RQ1-I: development-root signal controls, with producer-contract and later-use targets separated.
data["cells"]["RQ1-I"] = {
    "track": "ArtifactRole/development root",
    "metrics": {
        "brier": "[0,1], lower",
        "log_loss_nats": "[0,infinity), lower",
        "ece_10_equal_mass_bins": "[0,1], lower",
        "auc": "[0,1], higher",
        "judge_weighted_kappa": "[0,1], higher; judgment contract, not a policy rank",
    },
    "target_denominators": {
        "producer_contract_qp": "frozen common held-out producer-contract labels",
        "later_use_y": "frozen common held-out independent later-use labels",
    },
    "judge_weighted_kappa": {"center": 0.78, "expected_95": [0.74, 0.82]},
    "rows": {
        "raw_acceptance": {
            "producer_contract_qp": {"brier": 0.225, "log_loss_nats": 0.637, "ece_10_equal_mass_bins": 0.073, "auc": 0.680},
            "later_use_y": {"brier": 0.232, "log_loss_nats": 0.651, "ece_10_equal_mass_bins": 0.078, "auc": 0.665},
        },
        "terminal_only": {
            "producer_contract_qp": {"brier": 0.220, "log_loss_nats": 0.625, "ece_10_equal_mass_bins": 0.068, "auc": 0.695},
            "later_use_y": {"brier": 0.218, "log_loss_nats": 0.620, "ece_10_equal_mass_bins": 0.066, "auc": 0.704},
        },
        "rare": {
            "producer_contract_qp": {"brier": 0.203, "log_loss_nats": 0.584, "ece_10_equal_mass_bins": 0.055, "auc": 0.738},
            "later_use_y": {"brier": 0.209, "log_loss_nats": 0.596, "ece_10_equal_mass_bins": 0.059, "auc": 0.728},
        },
    },
    "expected_relation": "RARE > terminal-only > raw acceptance on both Qp and Y only in the preregistered informative typed-evidence regime",
}

# RQ1-II: confirmation-root matched-information controls and information counterfactuals.
def prediction_targets(qp, y, eligibility):
    return {"producer_contract_qp": qp, "later_use_y": y, "eligibility": eligibility}


data["cells"]["RQ1-II"] = {
    "track": "ArtifactRole/confirmation root",
    "target_denominators": data["cells"]["RQ1-I"]["target_denominators"],
    "rows": {
        "trace_only": prediction_targets(
            {"brier": 0.216, "log_loss_nats": 0.616, "ece_10_equal_mass_bins": 0.064, "auc": 0.704, "cross_root_score_drop": 0.019},
            {"brier": 0.223, "log_loss_nats": 0.630, "ece_10_equal_mass_bins": 0.068, "auc": 0.694, "cross_root_score_drop": 0.023},
            "REQUIRED_INFORMATION_COUNTERFACTUAL"),
        "count_only": prediction_targets(
            {"brier": 0.213, "log_loss_nats": 0.609, "ece_10_equal_mass_bins": 0.062, "auc": 0.712, "cross_root_score_drop": 0.018},
            {"brier": 0.219, "log_loss_nats": 0.622, "ece_10_equal_mass_bins": 0.066, "auc": 0.702, "cross_root_score_drop": 0.022},
            "REQUIRED_INFORMATION_COUNTERFACTUAL"),
        "j_masked": prediction_targets(
            {"brier": 0.212, "log_loss_nats": 0.606, "ece_10_equal_mass_bins": 0.061, "auc": 0.716, "cross_root_score_drop": 0.018},
            {"brier": 0.218, "log_loss_nats": 0.619, "ece_10_equal_mass_bins": 0.065, "auc": 0.706, "cross_root_score_drop": 0.021},
            "REQUIRED_INFORMATION_COUNTERFACTUAL"),
        "j_permutation": prediction_targets(
            {"brier": 0.213, "log_loss_nats": 0.610, "ece_10_equal_mass_bins": 0.063, "auc": 0.710, "cross_root_score_drop": 0.019},
            {"brier": 0.220, "log_loss_nats": 0.624, "ece_10_equal_mass_bins": 0.067, "auc": 0.700, "cross_root_score_drop": 0.023},
            "REQUIRED_FALSIFIER"),
        "menu_id_permutation": prediction_targets(
            {"brier": 0.214, "log_loss_nats": 0.612, "ece_10_equal_mass_bins": 0.064, "auc": 0.708, "cross_root_score_drop": 0.020},
            {"brier": 0.221, "log_loss_nats": 0.626, "ece_10_equal_mass_bins": 0.068, "auc": 0.698, "cross_root_score_drop": 0.024},
            "REQUIRED_FALSIFIER"),
        "contextual_trust_linear": prediction_targets(
            {"brier": 0.211, "log_loss_nats": 0.604, "ece_10_equal_mass_bins": 0.060, "auc": 0.720, "cross_root_score_drop": 0.020},
            {"brier": 0.217, "log_loss_nats": 0.617, "ece_10_equal_mass_bins": 0.064, "auc": 0.710, "cross_root_score_drop": 0.023},
            "REQUIRED_QUALIFY_BEFORE_RUN"),
        "task_conditioned_ridge": prediction_targets(
            {"brier": 0.207, "log_loss_nats": 0.595, "ece_10_equal_mass_bins": 0.058, "auc": 0.728, "cross_root_score_drop": 0.016},
            {"brier": 0.214, "log_loss_nats": 0.608, "ece_10_equal_mass_bins": 0.062, "auc": 0.717, "cross_root_score_drop": 0.019},
            "REQUIRED_EXPECTED_TARGET_UNEXECUTED"),
        "matched_composition": prediction_targets(
            {"brier": 0.206, "log_loss_nats": 0.592, "ece_10_equal_mass_bins": 0.057, "auc": 0.731, "cross_root_score_drop": 0.015},
            {"brier": 0.213, "log_loss_nats": 0.606, "ece_10_equal_mass_bins": 0.061, "auc": 0.720, "cross_root_score_drop": 0.018},
            "REQUIRED_EXPECTED_TARGET_UNEXECUTED"),
        "rare": prediction_targets(
            {"brier": 0.203, "log_loss_nats": 0.584, "ece_10_equal_mass_bins": 0.055, "auc": 0.738, "cross_root_score_drop": 0.014},
            {"brier": 0.209, "log_loss_nats": 0.596, "ece_10_equal_mass_bins": 0.059, "auc": 0.728, "cross_root_score_drop": 0.017},
            "CANDIDATE_CARD_MUST_BE_FROZEN"),
        "closest_published_adapter": {"eligibility": "NO_GO", "reason": "no faithful adapter currently preserves public fields, candidate menu, timing, selected-only outcomes, future assignment, and complete cost"},
    },
    "expected_relation": "RARE has a deliberately small edge on Qp and Y over modeled same-information controls; a tie or control win is allowed",
}

# RQ2-I: public evidence before a sealed assignment.
data["cells"]["RQ2-I"] = {
    "track": "ArtifactRole/confirmation root",
    "rows": {
        "no_evidence_no_update": policy(0.532, 1.02, assignment_change=0.04, adoption=0.48, rework_rate=0.30),
        "public_evidence_only": policy(0.566, 1.18, assignment_change=0.12, adoption=0.54, rework_rate=0.24),
    },
    "expected_relation": "assignment change is diagnostic; success requires independent future quality/adoption improvement and lower rework under complete-cost reporting",
}

# RQ2-II: 2x2 information x delayed update factorial.
factorial = {
    "00_no_evidence_no_update": policy(0.532, 1.02, assignment_change=0.04),
    "10_public_evidence_only": policy(0.566, 1.18, assignment_change=0.12),
    "01_delayed_update_only": policy(0.570, 1.15, assignment_change=0.13),
    "11_evidence_plus_delayed_update_rare": policy(0.608, 1.34, assignment_change=0.20),
}
iy = round(factorial["11_evidence_plus_delayed_update_rare"]["quality"] - factorial["10_public_evidence_only"]["quality"] - factorial["01_delayed_update_only"]["quality"] + factorial["00_no_evidence_no_update"]["quality"], 3)
ic = round(factorial["11_evidence_plus_delayed_update_rare"]["complete_cost"] - factorial["10_public_evidence_only"]["complete_cost"] - factorial["01_delayed_update_only"]["complete_cost"] + factorial["00_no_evidence_no_update"]["complete_cost"], 3)
iu = round(factorial["11_evidence_plus_delayed_update_rare"]["utility"] - factorial["10_public_evidence_only"]["utility"] - factorial["01_delayed_update_only"]["utility"] + factorial["00_no_evidence_no_update"]["utility"], 3)
data["cells"]["RQ2-II"] = {
    "track": "ArtifactRole/confirmation root",
    "rows": factorial,
    "factorial_interaction": {"quality": iy, "complete_cost": ic, "utility": iu, "identity": "I_U = I_Y - lambda * I_C"},
    "expected_relation": "the positive utility interaction is small; most expected gain is main effects, not universal synergy",
}

# RQ2-III: stable crossover positive regime and sparse negative regime.
data["cells"]["RQ2-III"] = {
    "track": "ArtifactRole/confirmation root",
    "rows": {
        "stable_local_uniform": policy(0.548, 1.00, assignment_change=0.08, max_assignment_share=0.34, minimum_propensity=0.05),
        "stable_nonlocal_global": policy(0.592, 1.25, assignment_change=0.16, max_assignment_share=0.32, minimum_propensity=0.06),
        "stable_same_cost_centralized": policy(0.602, 1.34, assignment_change=0.18, max_assignment_share=0.29, minimum_propensity=0.07),
        "stable_pooled": policy(0.600, 1.28, assignment_change=0.14, max_assignment_share=0.31, minimum_propensity=0.06),
        "stable_rare": policy(0.608, 1.34, assignment_change=0.20, max_assignment_share=0.27, minimum_propensity=0.08),
        "sparse_pooled": policy(0.578, 1.28, assignment_change=0.12, max_assignment_share=0.33, minimum_propensity=0.05),
        "sparse_rare": policy(0.561, 1.34, assignment_change=0.11, max_assignment_share=0.36, minimum_propensity=0.04),
    },
    "expected_relation": "RARE is only slightly above pooled and same-cost centralized under stable crossover; pooled wins in the sparse regime; locality diagnostics remain explicit",
}

# RQ3-I: normal and high-arrival service regimes, including matched updater controls.
data["cells"]["RQ3-I"] = {
    "track": "PeerSelect/development streams",
    "rows": {
        "normal_uniform": service_policy(0.500, 1.00, 0.150, 10.0, 12.0, None, 34.0, 0.0, 8.0, 0.001, 6.0, 64.0, 0.0),
        "normal_no_history": service_policy(0.532, 1.02, 0.118, 11.0, 14.0, None, 38.0, 0.0, 8.0, 0.001, 7.0, 64.0, 0.0),
        "normal_history_only": service_policy(0.565, 1.16, 0.085, 15.0, 24.0, 32.0, 76.0, 0.4, 20.0, 0.004, 16.0, 96.0, 15.0),
        "normal_matched_rls": service_policy(0.600, 1.31, 0.050, 18.0, 42.0, 66.0, 142.0, 0.8, 32.0, 0.005, 29.0, 128.0, 24.0),
        "normal_matched_online_sgd": service_policy(0.598, 1.29, 0.052, 18.0, 40.0, 64.0, 138.0, 0.7, 30.0, 0.005, 27.0, 120.0, 22.0),
        "normal_matched_periodic_refit": service_policy(0.602, 1.35, 0.048, 20.0, 34.0, 120.0, 185.0, 1.5, 64.0, 0.008, 44.0, 256.0, 60.0),
        "normal_rare": service_policy(0.606, 1.34, 0.044, 22.0, 46.0, 68.0, 155.0, 1.0, 36.0, 0.006, 34.0, 160.0, 30.0),
        "high_load_uniform": service_policy(0.500, 1.15, 0.150, 30.0, 38.0, None, 110.0, 0.3, 8.0, 0.020, 18.0, 64.0, 0.0),
        "high_load_rare": service_policy(0.582, 2.25, 0.068, 120.0, 260.0, 480.0, 920.0, 8.0, 36.0, 0.110, 210.0, 192.0, 180.0),
    },
    "n_a": {"peerselect_false_producer_attribution": "N/A: no owner-truth contract", "uniform_full_update_latency": "N/A: no full update path"},
    "expected_relation": "RARE has only a 0.003-0.005 utility edge over matched updaters in the informative normal regime and loses utility plus every service tail under high load",
}

# RQ3-II: delayed/out-of-order correction, gradual drift, and stale-version boundaries.
data["cells"]["RQ3-II"] = {
    "track": "PeerSelect/drift streams",
    "rows": {
        "delayed_with_correction_replay": service_policy(0.607, 1.39, 0.043, 24.0, 48.0, 74.0, 175.0, 1.4, 39.0, 0.010, 40.0, 176.0, 42.0, forgetting=0.110, recovery_selected_updates=6.5, replay_equality=1.00),
        "delayed_without_correction_replay": service_policy(0.580, 1.25, 0.070, 20.0, 40.0, 60.0, 140.0, 0.9, 30.0, 0.012, 30.0, 128.0, 18.0, forgetting=0.170, recovery_selected_updates=9.0, replay_equality=0.86),
        "gradual_drift_frozen_prior": service_policy(0.566, 1.02, 0.084, 12.0, 22.0, None, 50.0, 0.0, 8.0, 0.005, 10.0, 64.0, 0.0, forgetting=0.230, recovery_selected_updates=None, replay_equality=1.00),
        "gradual_drift_matched_rls": service_policy(0.602, 1.31, 0.048, 18.0, 42.0, 66.0, 145.0, 0.9, 32.0, 0.007, 30.0, 128.0, 24.0, forgetting=0.125, recovery_selected_updates=7.0, replay_equality=1.00),
        "gradual_drift_matched_sgd": service_policy(0.599, 1.29, 0.051, 18.0, 40.0, 64.0, 140.0, 0.8, 30.0, 0.007, 28.0, 120.0, 22.0, forgetting=0.135, recovery_selected_updates=7.5, replay_equality=1.00),
        "gradual_drift_periodic_refit": service_policy(0.601, 1.35, 0.049, 20.0, 34.0, 120.0, 188.0, 1.5, 64.0, 0.009, 46.0, 256.0, 60.0, forgetting=0.115, recovery_selected_updates=8.0, replay_equality=1.00),
        "gradual_drift_rare_correction_replay": service_policy(0.607, 1.39, 0.043, 24.0, 48.0, 74.0, 175.0, 1.4, 39.0, 0.010, 40.0, 176.0, 42.0, forgetting=0.110, recovery_selected_updates=6.5, replay_equality=1.00),
        "stale_version_aware_reset": service_policy(0.579, 1.30, 0.071, 18.0, 36.0, 50.0, 120.0, 0.8, 24.0, 0.006, 24.0, 96.0, 20.0, brier=0.224, false_attribution_all_attempts=0.060, recovery_selected_updates=6.0),
        "stale_rare": service_policy(0.557, 1.34, 0.093, 22.0, 46.0, 82.0, 190.0, 1.6, 36.0, 0.012, 38.0, 160.0, 40.0, brier=0.232, false_attribution_all_attempts=0.040, recovery_selected_updates=8.5),
    },
    "expected_relation": "RARE correction/replay improves stability over its ablation but does not dominate matched drift updaters; stale reset clearly wins quality/recovery while RARE retains better attribution safety",
}

# RQ4-I: responsibility mutation matrix. Rates share explicit denominators.
mutations = {
    "producer_only": {"coverage": 0.92, "unknown_rate": 0.08, "false_attribution_all_attempts": 0.010, "unknown_precision": 0.85, "no_op_rate": 0.07, "owner_truth_recall": 0.97},
    "recipient_only": {"coverage": 0.06, "unknown_rate": 0.94, "false_attribution_all_attempts": 0.002, "unknown_precision": 0.99, "no_op_rate": 0.93, "owner_truth_recall": 0.98},
    "sink_only": {"coverage": 0.10, "unknown_rate": 0.90, "false_attribution_all_attempts": 0.003, "unknown_precision": 0.98, "no_op_rate": 0.89, "owner_truth_recall": 0.96},
    "mixed_ownership": {"coverage": 0.18, "unknown_rate": 0.82, "false_attribution_all_attempts": 0.020, "unknown_precision": 0.96, "no_op_rate": 0.80, "owner_truth_recall": 0.92},
    "unknown_owner": {"coverage": 0.04, "unknown_rate": 0.96, "false_attribution_all_attempts": None, "false_attribution_claimed": None, "unknown_precision": 0.99, "no_op_rate": 0.95, "owner_truth_recall": None},
    "resource_failure": {"coverage": 0.30, "unknown_rate": 0.70, "false_attribution_all_attempts": 0.010, "unknown_precision": 0.97, "no_op_rate": 0.68, "owner_truth_recall": 0.90},
}
for row in mutations.values():
    if row.get("false_attribution_all_attempts") is not None:
        row["false_attribution_claimed"] = round(row["false_attribution_all_attempts"] / row["coverage"], 3)
data["cells"]["RQ4-I"] = {
    "track": "ArtifactRole/all qualified roots",
    "rows": mutations,
    "expected_relation": "low conditional attribution error is not sufficient: coverage, UNKNOWN, no-op, and owner-truth recall remain visible at the same operating point",
}

# RQ4-II: leave-one-mechanism-out with the same safety denominators as RQ4-I.
data["cells"]["RQ4-II"] = {
    "track": "ArtifactRole/all qualified roots",
    "rows": {
        "full_rare": policy_safety(0.608, 1.34, 0.08, 0.08),
        "no_evidence_no_update": policy_safety(0.532, 1.02, 0.10, 0.18),
        "minus_ownership_gate": policy_safety(0.588, 1.27, 0.75, 0.24),
        "minus_public_evidence": policy_safety(0.570, 1.15, 0.25, 0.16),
        "minus_delayed_update": policy_safety(0.566, 1.18, 0.45, 0.11),
        "minus_locality": policy_safety(0.600, 1.30, 0.18, 0.10),
        "minus_updater": policy_safety(0.580, 1.20, 0.20, 0.10),
        "minus_selected_only_rule": policy_safety(0.603, 1.31, 0.30, 0.13),
        "minus_correction_replay": policy_safety(0.597, 1.29, 0.28, 0.12),
    },
    "factorial_interaction_utility": iu,
    "expected_relation": "gate removal harms both conditional and all-attempt attribution safety; evidence/update removal lowers cost but loses informative-regime utility; assignment-change rate is never a success endpoint",
}


def all_policy_rows(obj):
    if isinstance(obj, dict):
        if {"quality", "complete_cost", "utility", "cost_breakdown"}.issubset(obj):
            yield obj
        for value in obj.values():
            yield from all_policy_rows(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from all_policy_rows(value)


def audit_data(payload):
    checks = []

    def check(name, condition, detail):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    # Utility arithmetic.
    policy_rows = list(all_policy_rows(payload["cells"]))
    utility_residuals = []
    cost_breakdown_residuals = []
    for row in policy_rows:
        utility_residuals.append(round(row["utility"] - (row["quality"] - LAMBDA * row["complete_cost"]), 12))
        cost_breakdown_residuals.append(round(row["complete_cost"] - sum(row["cost_breakdown"].values()), 12))
    check("utility_identity_all_rows", all(abs(r) <= 0.0005 for r in utility_residuals), {"max_abs_residual": max(abs(r) for r in utility_residuals), "row_count": len(policy_rows)})
    check("cost_breakdown_all_rows", all(abs(r) <= 0.000001 for r in cost_breakdown_residuals), {"max_abs_residual": max(abs(r) for r in cost_breakdown_residuals), "row_count": len(policy_rows)})
    check("wall_time_all_rows", all("expected_wall_seconds_per_attempt" in row for row in policy_rows), {"row_count": len(policy_rows)})

    # Cost template sums.
    cost_sums = {key: round(sum(values), 3) for key, values in cost_templates.items()}
    expected_costs = {"uniform": 1.00, "no_update": 1.02, "raw": 1.10, "terminal": 1.15, "context": 1.22, "task_ridge": 1.29, "matched_composition": 1.31, "matched_rls": 1.31, "matched_sgd": 1.29, "matched_periodic_refit": 1.35, "pooled": 1.28, "rare": 1.34, "public_only": 1.18, "delayed_only": 1.15, "history_only": 1.16}
    check("cost_component_sums", cost_sums == expected_costs, {"computed": cost_sums, "expected": expected_costs})

    # Factorial identity.
    check("factorial_quality", iy == 0.004, {"value": iy})
    check("factorial_cost", ic == 0.030, {"value": ic})
    check("factorial_utility", iu == 0.001, {"value": iu})
    check("factorial_cross_identity", abs(iu - (iy - LAMBDA * ic)) < 1e-12, {"I_U": iu, "I_Y_minus_lambda_I_C": round(iy - LAMBDA * ic, 12)})

    # H4 complementary rates and denominator transforms.
    complements = []
    attribution_transforms = []
    for name, row in mutations.items():
        complements.append((name, round(row["coverage"] + row["unknown_rate"], 12)))
        if row.get("false_attribution_all_attempts") is not None:
            expected = round(row["false_attribution_all_attempts"] / row["coverage"], 3)
            attribution_transforms.append((name, row["false_attribution_claimed"], expected))
    check("rq4i_coverage_plus_unknown", all(total == 1.0 for _, total in complements), complements)
    check("rq4i_false_attribution_denominator_transform", all(actual == expected for _, actual, expected in attribution_transforms), attribution_transforms)
    check("rq4i_sink_only_present", "sink_only" in mutations, sorted(mutations))
    check("rq4i_no_op_visible", all("no_op_rate" in row for row in mutations.values()), {name: row.get("no_op_rate") for name, row in mutations.items()})

    c42 = payload["cells"]["RQ4-II"]["rows"]
    rq42_complements = [(name, round(row["coverage"] + row["unknown_rate"], 12)) for name, row in c42.items()]
    rq42_transforms = [(name, row["false_attribution_all_attempts"], round(row["coverage"] * row["false_attribution_claimed"], 4)) for name, row in c42.items()]
    check("rq4ii_coverage_plus_unknown", all(total == 1.0 for _, total in rq42_complements), rq42_complements)
    check("rq4ii_false_attribution_denominator_transform", all(actual == expected for _, actual, expected in rq42_transforms), rq42_transforms)

    # Directional guards and required comparison completeness.
    c1 = payload["cells"]["RQ1-II"]["rows"]
    required_info_rows = {"trace_only", "count_only", "j_masked", "j_permutation", "menu_id_permutation", "contextual_trust_linear", "task_conditioned_ridge", "matched_composition", "rare", "closest_published_adapter"}
    check("rq1ii_required_counterfactuals_present", required_info_rows.issubset(c1), sorted(c1))
    check("h1_targets_separated", all({"producer_contract_qp", "later_use_y"}.issubset(row) for name, row in c1.items() if name != "closest_published_adapter"), sorted(c1))
    check("informative_qp_positive", c1["rare"]["producer_contract_qp"]["brier"] < c1["matched_composition"]["producer_contract_qp"]["brier"] < c1["task_conditioned_ridge"]["producer_contract_qp"]["brier"] < c1["contextual_trust_linear"]["producer_contract_qp"]["brier"], {k: v.get("producer_contract_qp", {}).get("brier") for k, v in c1.items() if isinstance(v, dict)})
    check("informative_later_use_positive", c1["rare"]["later_use_y"]["brier"] < c1["matched_composition"]["later_use_y"]["brier"] < c1["task_conditioned_ridge"]["later_use_y"]["brier"] < c1["contextual_trust_linear"]["later_use_y"]["brier"], {k: v.get("later_use_y", {}).get("brier") for k, v in c1.items() if isinstance(v, dict)})
    c23 = payload["cells"]["RQ2-III"]["rows"]
    locality_rows = {"stable_local_uniform", "stable_nonlocal_global", "stable_same_cost_centralized", "stable_pooled", "stable_rare"}
    check("rq2iii_locality_controls_present", locality_rows.issubset(c23), sorted(c23))
    stable_delta = round(c23["stable_rare"]["utility"] - c23["stable_pooled"]["utility"], 3)
    sparse_delta = round(c23["sparse_rare"]["utility"] - c23["sparse_pooled"]["utility"], 3)
    check("stable_crossover_small_positive", 0.0 < stable_delta <= 0.008, {"delta": stable_delta})
    check("sparse_clear_negative", sparse_delta <= -0.020, {"delta": sparse_delta})
    c31 = payload["cells"]["RQ3-I"]["rows"]
    updater_rows = {"normal_matched_rls", "normal_matched_online_sgd", "normal_matched_periodic_refit"}
    check("rq3i_matched_updaters_present", updater_rows.issubset(c31), sorted(c31))
    h3_fields = {"publish_p50_ms", "publish_p95_ms", "read_assignment_p50_ms", "read_assignment_p95_ms", "update_p50_ms", "update_p95_ms", "service_lag_p95_ms", "backlog_p95_events", "state_kib", "drop_timeout_rate", "cpu_ms_per_event", "gpu_ms_per_event", "ram_peak_mib", "model_calls_per_1000_arrivals", "input_tokens_per_1000_arrivals", "output_tokens_per_1000_arrivals", "tool_calls_per_1000_arrivals", "replay_ms_per_1000_arrivals"}
    check("rq3i_full_service_fields", all(h3_fields.issubset(row) for row in c31.values()), {"required": sorted(h3_fields), "rows": len(c31)})
    updater_best = max(c31[key]["utility"] for key in updater_rows)
    updater_delta = round(c31["normal_rare"]["utility"] - updater_best, 3)
    check("normal_updater_edge_small", 0.0 < updater_delta <= 0.005, {"rare": c31["normal_rare"]["utility"], "best_updater": updater_best, "delta": updater_delta})
    high_load_delta = round(c31["high_load_rare"]["utility"] - c31["high_load_uniform"]["utility"], 3)
    check("high_load_clear_negative", high_load_delta <= -0.020 and c31["high_load_rare"]["update_p95_ms"] > c31["normal_rare"]["update_p95_ms"], {"delta": high_load_delta, "rare_update_p95": c31["high_load_rare"]["update_p95_ms"]})
    c32 = payload["cells"]["RQ3-II"]["rows"]
    drift_rows = {"gradual_drift_frozen_prior", "gradual_drift_matched_rls", "gradual_drift_matched_sgd", "gradual_drift_periodic_refit", "gradual_drift_rare_correction_replay"}
    check("rq3ii_drift_controls_present", drift_rows.issubset(c32), sorted(c32))
    check("rq3ii_full_service_fields", all(h3_fields.issubset(row) for row in c32.values()), {"required": sorted(h3_fields), "rows": len(c32)})
    stale_delta = round(c32["stale_rare"]["utility"] - c32["stale_version_aware_reset"]["utility"], 3)
    check("stale_clear_negative_safety_positive", stale_delta <= -0.020 and c32["stale_rare"]["false_attribution_all_attempts"] < c32["stale_version_aware_reset"]["false_attribution_all_attempts"], {"delta": stale_delta, "stale_rare": c32["stale_rare"], "reset": c32["stale_version_aware_reset"]})
    check("correction_replay_tradeoff", c32["delayed_with_correction_replay"]["utility"] > c32["delayed_without_correction_replay"]["utility"] and c32["delayed_with_correction_replay"]["update_p95_ms"] > c32["delayed_without_correction_replay"]["update_p95_ms"] and c32["delayed_with_correction_replay"]["replay_equality"] == 1.0, {"with": c32["delayed_with_correction_replay"], "without": c32["delayed_without_correction_replay"]})
    check("drift_no_universal_rare_win", c32["gradual_drift_rare_correction_replay"]["utility"] < c32["gradual_drift_matched_rls"]["utility"], {"rare": c32["gradual_drift_rare_correction_replay"]["utility"], "matched_rls": c32["gradual_drift_matched_rls"]["utility"]})
    check("ownership_gate_safety", c42["full_rare"]["false_attribution_claimed"] < c42["minus_ownership_gate"]["false_attribution_claimed"] and c42["full_rare"]["false_attribution_all_attempts"] < c42["minus_ownership_gate"]["false_attribution_all_attempts"], {"full": c42["full_rare"], "minus_gate": c42["minus_ownership_gate"]})

    # Precision-model reproducibility.
    precision = payload["design"]["precision_model"]
    planning = payload["design"]["planning_half_width"]
    precision_residuals = []
    for group, sd_key in [("single_arm", "single_arm_stream_sd_assumption"), ("paired_contrast", "paired_stream_sd_assumption")]:
        for metric, sd in precision[sd_key].items():
            derived = 1.96 * sd / math.sqrt(payload["design"]["independent_streams_per_arm"])
            precision_residuals.append((group, metric, round(derived - planning[group][metric], 6)))
    check("planning_halfwidth_reproducible", all(abs(residual) <= 0.000001 for _, _, residual in precision_residuals), precision_residuals)

    # Structural correspondence and forbidden placeholders.
    expected_ids = ["RQ1-I", "RQ1-II", "RQ2-I", "RQ2-II", "RQ2-III", "RQ3-I", "RQ3-II", "RQ4-I", "RQ4-II"]
    check("nine_cell_identity", list(payload["cells"].keys()) == expected_ids, list(payload["cells"].keys()))
    serialized = json.dumps(payload, ensure_ascii=False)
    check("no_tbd_placeholder", "TBD" not in serialized and "tbd" not in serialized, "No TBD token in the numeric ledger")
    check("no_ambiguous_plus_minus", "plus-minus" not in serialized and "±" not in serialized, "Expected intervals use explicit definitions/ranges")
    check("scientific_gate_open", payload["scientific_result"] is False and payload["benchmark_runs"] == 0, {"scientific_result": payload["scientific_result"], "benchmark_runs": payload["benchmark_runs"]})

    return {"version": payload["version"], "passed": all(item["passed"] for item in checks), "checks": checks}


def tex_escape(text: str) -> str:
    return (text.replace("\\", r"\textbackslash{}")
                .replace("&", r"\&")
                .replace("%", r"\%")
                .replace("_", r"\_")
                .replace("#", r"\#"))


def n(value, digits=3):
    if value is None:
        return r"\na"
    return f"{value:.{digits}f}"


def row_cells(cells):
    return " & ".join(cells) + r" \\" + "\n"


def build_tex(payload, audit):
    lines = []
    lines.append(r"\documentclass[10pt,a4paper,landscape]{article}")
    lines.append(r"\usepackage[margin=11mm,headheight=15pt]{geometry}")
    lines.append(r"\usepackage[T1]{fontenc}\usepackage{lmodern}")
    lines.append(r"\usepackage{booktabs,array,tabularx,longtable,makecell,xcolor,fancyhdr,draftwatermark,hyperref}")
    lines.append(r"\hypersetup{hidelinks,pdftitle={Numeric Expected Experiment Matrix v4},pdfsubject={Expected not observed},pdfauthor={Earning Roles project}}")
    lines.append(r"\SetWatermarkText{EXPECTED --- NOT OBSERVED}\SetWatermarkColor{red!13}\SetWatermarkAngle{33}\SetWatermarkScale{0.90}")
    lines.append(r"\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\color{red!65!black}\bfseries NUMERIC EXPECTED EXPERIMENT MATRIX v4}\fancyhead[R]{\color{red!65!black}SOLE EXPECTED REFERENCE / NOT RESULTS}\fancyfoot[L]{2026-10-09 / design expectation / not submission evidence}\fancyfoot[R]{\thepage}")
    lines.append(r"\setlength{\parindent}{0pt}\setlength{\parskip}{3pt}\setlength{\tabcolsep}{2.6pt}\renewcommand{\arraystretch}{1.10}")
    lines.append(r"\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}\newcolumntype{Y}{>{\raggedright\arraybackslash}X}")
    lines.append(r"\newcommand{\rare}{\textsc{rare}}\newcommand{\na}{\textsc{n/a}}\newcommand{\nog}{\textsc{no-go}}\newcommand{\ok}{\textsc{pass}}")
    lines.append(r"\begin{document}")
    lines.append(r"{\LARGE\bfseries Numeric Expected Experiment Matrix v4}\hfill{\large\color{red!65!black}\bfseries EXPECTED --- NOT OBSERVED}\par")
    lines.append(r"\textbf{Decision.} This is the sole numerical expectation reference for the experiment matrix in \texttt{artifacts/aamas2027/main.pdf}. It is a falsifiable planning benchmark, not a result. The current PDF prints four RQ rows; its stated confirmation-card expansion is represented here by exactly nine cells (RQ1-I through RQ4-II). Real observations replace expectations and are never edited to match them.")
    lines.append(r"\textbf{Numeric basis.} The historical numeric mother is expected v3; its broken PDF is not reused. Guide v2 supplies the joint/paired uncertainty logic; guide v5 supplies positive and negative regime guards. Public work informs metric discipline and conservative scale only; no external result is treated as protocol-equivalent to ArtifactRole or PeerSelect.")
    lines.append(r"\textbf{Shared design.} Three structural roots $\times$ six independently reset streams per arm ($n=18$). ArtifactRole uses 120 ITT attempts/stream and a frozen 96-case H1 cohort/stream. PeerSelect uses 1,000 warm-up plus 5,000 scored arrivals/stream. $U=Y-0.10C$; $C$ is complete per-attempt cost normalized to matched uniform $=1.00$. Assignment change is diagnostic only.")

    lines.append(r"\section*{1. Current-PDF correspondence and expected direction}")
    lines.append(r"\begin{center}\small\begin{tabularx}{\linewidth}{@{}C{.06\linewidth}L{.14\linewidth}L{.22\linewidth}L{.17\linewidth}Y@{}}\toprule PDF row & Track/unit & Current-PDF contrast & Expanded cells & Expected boundary \\\midrule")
    lines.append(row_cells(["RQ1", "ArtifactRole/root", "RARE/raw/terminal/contextual trust", "RQ1-I, RQ1-II", "Small positive signal only under informative typed evidence; same-information strong controls remain close."]))
    lines.append(row_cells(["RQ2", "ArtifactRole/target", "Evidence+delay/no evidence/delay-only/pooled", "RQ2-I, II, III", "Positive under stable crossover; pooled wins in sparse support; change rate never defines success."]))
    lines.append(row_cells(["RQ3", "PeerSelect/stream", "Updater/uniform/no-history/history-only", "RQ3-I, II", "Payoff may improve normally; RARE loses service and utility under high load; correction buys stability at cost."]))
    lines.append(row_cells(["RQ4", "Both/mutation+drift", "Ownership/correction-replay/leave-one-out", "RQ4-I, II", "Safety requires risk plus coverage/UNKNOWN; stale reset may beat RARE on quality/recovery."]))
    lines.append(r"\bottomrule\end{tabularx}\end{center}")

    # RQ1-I.
    lines.append(r"\section*{2. RQ1---Information value}")
    lines.append(r"\textbf{RQ1-I: development-root signal controls.} Producer-contract $Q_p$ and independent later-use $Y$ use separate frozen common cohorts. Brier, ECE, and log loss are lower-better; AUC is higher-better.")
    labels = {"raw_acceptance": "Raw acceptance", "terminal_only": "Terminal only", "rare": r"\rare{}"}
    for target, target_label in [("producer_contract_qp", "Producer-contract $Q_p$"), ("later_use_y", "Independent later-use $Y$")]:
        lines.append(r"\begin{center}\small\begin{tabular}{llrrrr}\toprule Target & Arm & Brier & Log loss (nats) & ECE & AUC \\\midrule")
        for key, row in payload["cells"]["RQ1-I"]["rows"].items():
            metric = row[target]
            lines.append(row_cells([target_label, labels[key], n(metric["brier"]), n(metric["log_loss_nats"]), n(metric["ece_10_equal_mass_bins"]), n(metric["auc"])]))
        lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"Expected eligible-judgment weighted $\kappa=0.780$ [0.740, 0.820]. This is a judgment-contract diagnostic, not a policy win.")

    # RQ1-II.
    lines.append(r"\textbf{RQ1-II: confirmation-root matched-information controls, counterfactuals, and falsifiers.}")
    rq12_order = [
        ("trace_only", "Trace only"),
        ("count_only", "Count only"),
        ("j_masked", "$J$ masked"),
        ("j_permutation", "$J$ permutation"),
        ("menu_id_permutation", "Menu/ID permutation"),
        ("contextual_trust_linear", "Contextual-trust-linear"),
        ("task_conditioned_ridge", "Task-conditioned ridge"),
        ("matched_composition", "Matched composition"),
        ("rare", r"\rare{}"),
    ]
    for target, target_label in [("producer_contract_qp", "Producer-contract $Q_p$"), ("later_use_y", "Later-use $Y$")]:
        lines.append(r"\begin{center}\scriptsize\begin{tabular}{llrrrrrl}\toprule Target & Arm & Brier & Log loss & ECE & AUC & Cross-root drop & Role/status \\\midrule")
        for key, label in rq12_order:
            row = payload["cells"]["RQ1-II"]["rows"][key]
            metric = row[target]
            if "COUNTERFACTUAL" in row["eligibility"]:
                status = "required counterfactual"
            elif "FALSIFIER" in row["eligibility"]:
                status = "required falsifier"
            elif "UNEXECUTED" in row["eligibility"]:
                status = "expected target; qualify/run"
            else:
                status = "qualify/freeze before run"
            lines.append(row_cells([target_label, label, n(metric["brier"]), n(metric["log_loss_nats"]), n(metric["ece_10_equal_mass_bins"]), n(metric["auc"]), n(metric["cross_root_score_drop"]), status]))
        lines.append(r"Closest published adapter & \multicolumn{6}{c}{\nog{}: no faithful protocol-preserving adapter is currently qualified} & no numeric cell \\")
        lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"On $Q_p$, the RARE Brier edge over matched composition is $-0.003$; on later-use $Y$ it is $-0.004$. Both targets remain close enough for a tie or strong-control win to be an allowed outcome.")

    # RQ2-I.
    lines.append(r"\section*{3. RQ2---Assignment causality and quality--cost utility}")
    lines.append(r"\textbf{RQ2-I: public evidence before sealed target execution.} $Y$ is future independent quality; rework is the fraction requiring rework. Planning half-widths: $Y$ 0.012, $C$ 0.030, $U$ 0.011, rates 0.015.")
    lines.append(r"\begin{center}\small\begin{tabular}{lrrrrrr}\toprule Arm & $Y$ & $C$ & $U$ & Assignment change & Adoption & Rework \\\midrule")
    for key, label in [("no_evidence_no_update", "No evidence/no update"), ("public_evidence_only", "Public evidence only")]:
        row = payload["cells"]["RQ2-I"]["rows"][key]
        lines.append(row_cells([label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["assignment_change"],2), n(row["adoption"],2), n(row["rework_rate"],2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")

    # RQ2-II.
    lines.append(r"\textbf{RQ2-II: matched $2\times2$ public-evidence $\times$ delayed-update factorial.}")
    lines.append(r"\begin{center}\small\begin{tabular}{llrrrr}\toprule Evidence & Delayed update & $Y$ & $C$ & $U$ & Change (diagnostic) \\\midrule")
    fact_order = [
        ("00_no_evidence_no_update", "Masked", "Off"),
        ("10_public_evidence_only", "Visible", "Off"),
        ("01_delayed_update_only", "Masked", "On"),
        ("11_evidence_plus_delayed_update_rare", "Visible", "On"),
    ]
    for key, e, u in fact_order:
        row = payload["cells"]["RQ2-II"]["rows"][key]
        lines.append(row_cells([e, u, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["assignment_change"],2)]))
    lines.append(r"\midrule")
    lines.append(row_cells(["Interaction $I$", "", n(iy), n(ic), n(iu), r"\na"]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(f"Arithmetic is exact at displayed precision: $I_U={iu:.3f}=I_Y-0.10I_C={iy:.3f}-0.10({ic:.3f})$. The near-additive interaction prevents a universal synergy claim.")

    # RQ2-III.
    lines.append(r"\textbf{RQ2-III: local personalization boundary.}")
    lines.append(r"\begin{center}\small\begin{tabular}{llrrrrrr}\toprule Regime & Arm & $Y$ & $C$ & $U$ & Change & Max share & Min propensity \\\midrule")
    rq23_order = [
        ("stable_local_uniform", "Stable crossover", "Local uniform"),
        ("stable_nonlocal_global", "Stable crossover", "Nonlocal/global"),
        ("stable_same_cost_centralized", "Stable crossover", "Same-cost centralized"),
        ("stable_pooled", "Stable crossover", "Pooled"),
        ("stable_rare", "Stable crossover", r"\rare{}"),
        ("sparse_pooled", "Sparse support", "Pooled"),
        ("sparse_rare", "Sparse support", r"\rare{}"),
    ]
    for key, regime, label in rq23_order:
        row = payload["cells"]["RQ2-III"]["rows"][key]
        lines.append(row_cells([regime, label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["assignment_change"],2), n(row["max_assignment_share"],2), n(row["minimum_propensity"],2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"Under stable crossover RARE is only +0.002 vs pooled and +0.006 vs same-cost centralized, while local/nonlocal diagnostics remain explicit. Under sparse support RARE loses pooled utility by 0.023.")

    # RQ3-I.
    lines.append(r"\section*{4. RQ3---Online behavior, load, correction, and drift}")
    lines.append(r"\textbf{RQ3-I: selected-only end-to-end service.} All p50/p95 fields are milliseconds/event from event publication through sealed read/assignment and validated update; service lag is end-to-end wall time including validation, state write, queue/retry, and no-op handling. \na{} means no full update path.")
    rq31_order = [
        ("normal_uniform", "Normal", "Uniform"),
        ("normal_no_history", "Normal", "No history"),
        ("normal_history_only", "Normal", "History only"),
        ("normal_matched_rls", "Normal", "Matched RLS"),
        ("normal_matched_online_sgd", "Normal", "Matched online SGD"),
        ("normal_matched_periodic_refit", "Normal", "Matched periodic refit"),
        ("normal_rare", "Normal", r"\rare{}"),
        ("high_load_uniform", "High load", "Uniform"),
        ("high_load_rare", "High load", r"\rare{}"),
    ]
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{llrrrrrrr}\toprule Regime & Arm & Payoff & $C$ & $U$ & Regret & Backlog p95 & State KiB & Drop/timeout \\\midrule")
    for key, regime, label in rq31_order:
        row = payload["cells"]["RQ3-I"]["rows"][key]
        lines.append(row_cells([regime, label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["regret_vs_oracle_0_650"]), n(row["backlog_p95_events"],1), n(row["state_kib"],1), n(row["drop_timeout_rate"],3)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{llrrrrrrr}\toprule Regime & Arm & Publish p50 & Publish p95 & Read p50 & Read p95 & Update p50 & Update p95 & Service lag p95 \\\midrule")
    for key, regime, label in rq31_order:
        row = payload["cells"]["RQ3-I"]["rows"][key]
        lines.append(row_cells([regime, label, n(row["publish_p50_ms"],1), n(row["publish_p95_ms"],1), n(row["read_assignment_p50_ms"],1), n(row["read_assignment_p95_ms"],1), n(row["update_p50_ms"],1), n(row["update_p95_ms"],1), n(row["service_lag_p95_ms"],1)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{llrrrrrrrr}\toprule Regime & Arm & CPU ms & GPU ms & RAM MiB & Model calls & Input tok. & Output tok. & Tool calls & Replay ms \\\midrule")
    for key, regime, label in rq31_order:
        row = payload["cells"]["RQ3-I"]["rows"][key]
        lines.append(row_cells([regime, label, n(row["cpu_ms_per_event"],1), n(row["gpu_ms_per_event"],1), n(row["ram_peak_mib"],1), n(row["model_calls_per_1000_arrivals"],0), n(row["input_tokens_per_1000_arrivals"],0), n(row["output_tokens_per_1000_arrivals"],0), n(row["tool_calls_per_1000_arrivals"],0), n(row["replay_ms_per_1000_arrivals"],1)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"Normal RARE has only a 0.003 utility edge over the best matched updater; periodic refit is slower. Under high load RARE loses utility to uniform by 0.028 and has worse end-to-end lag, backlog, state, replay, and drop rate. PeerSelect false producer attribution is structurally \na{}.")

    # RQ3-II.
    lines.append(r"\textbf{RQ3-II: correction/replay, gradual drift, and stale-version boundaries.}")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrrr}\toprule Condition & Payoff & $C$ & $U$ & Forgetting & Recovery updates & Update p95 & Backlog p95 & Replay equality \\\midrule")
    for key, label in [("delayed_with_correction_replay", "Delayed: correction+replay"), ("delayed_without_correction_replay", "Delayed: no correction/replay")]:
        row = payload["cells"]["RQ3-II"]["rows"][key]
        lines.append(row_cells([label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["forgetting"],3), n(row["recovery_selected_updates"],1), n(row["update_p95_ms"],1), n(row["backlog_p95_events"],1), n(row["replay_equality"],2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrr}\toprule Gradual-drift arm & Payoff & $C$ & $U$ & Forgetting & Recovery & Update p95 & Backlog \\\midrule")
    drift_order = [
        ("gradual_drift_frozen_prior", "Frozen prior"),
        ("gradual_drift_matched_rls", "Matched RLS"),
        ("gradual_drift_matched_sgd", "Matched SGD"),
        ("gradual_drift_periodic_refit", "Periodic refit"),
        ("gradual_drift_rare_correction_replay", r"\rare{} correction/replay"),
    ]
    for key, label in drift_order:
        row = payload["cells"]["RQ3-II"]["rows"][key]
        lines.append(row_cells([label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["forgetting"],3), n(row["recovery_selected_updates"],1), n(row["update_p95_ms"],1), n(row["backlog_p95_events"],1)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    rq32_service_order = [
        ("delayed_with_correction_replay", "Delayed + correction"),
        ("delayed_without_correction_replay", "Delayed without correction"),
        ("gradual_drift_frozen_prior", "Drift frozen prior"),
        ("gradual_drift_matched_rls", "Drift matched RLS"),
        ("gradual_drift_matched_sgd", "Drift matched SGD"),
        ("gradual_drift_periodic_refit", "Drift periodic refit"),
        ("gradual_drift_rare_correction_replay", "Drift RARE"),
        ("stale_version_aware_reset", "Stale reset"),
        ("stale_rare", "Stale RARE"),
    ]
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrrr}\toprule Condition & Publish p95 & Read p95 & Update p95 & Lag p95 & CPU ms & RAM MiB & Replay ms & Drop \\\midrule")
    for key, label in rq32_service_order:
        row = payload["cells"]["RQ3-II"]["rows"][key]
        lines.append(row_cells([label, n(row["publish_p95_ms"],1), n(row["read_assignment_p95_ms"],1), n(row["update_p95_ms"],1), n(row["service_lag_p95_ms"],1), n(row["cpu_ms_per_event"],1), n(row["ram_peak_mib"],1), n(row["replay_ms_per_1000_arrivals"],1), n(row["drop_timeout_rate"],3)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"\begin{center}\small\begin{tabular}{lrrrrrr}\toprule Stale-version arm & Payoff & $C$ & $U$ & Brier & False attribution (all) & Recovery \\\midrule")
    for key, label in [("stale_version_aware_reset", "Version-aware reset"), ("stale_rare", r"\rare{} under mismatch")]:
        row = payload["cells"]["RQ3-II"]["rows"][key]
        lines.append(row_cells([label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["brier"]), n(row["false_attribution_all_attempts"],3), n(row["recovery_selected_updates"],1)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"Matched RLS has slightly higher drift utility than RARE (0.471 vs 0.468), so updater superiority is not presumed. The stale reset control wins utility by 0.026 and recovery; RARE retains only the safety advantage.")

    # RQ4-I.
    lines.append(r"\section*{5. RQ4---Attribution safety and mechanism boundaries}")
    lines.append(r"\textbf{RQ4-I: responsibility mutations.} Coverage+UNKNOWN=1. False-attribution(all) uses all owner-truth-eligible attempts; false-attribution(claimed) divides the same errors by coverage. No-op remains visible because high abstention cannot manufacture a safety win.")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrr}\toprule Mutation & Coverage & UNKNOWN & FA all & FA claimed & UNKNOWN precision & No-op & Owner-truth recall \\\midrule")
    mutation_labels = {"producer_only": "Producer-only", "recipient_only": "Recipient-only", "sink_only": "Sink-only", "mixed_ownership": "Mixed ownership", "unknown_owner": "Unknown owner", "resource_failure": "Resource failure"}
    for key, row in payload["cells"]["RQ4-I"]["rows"].items():
        lines.append(row_cells([mutation_labels[key], n(row["coverage"],2), n(row["unknown_rate"],2), n(row.get("false_attribution_all_attempts"),3), n(row.get("false_attribution_claimed"),3), n(row["unknown_precision"],2), n(row["no_op_rate"],2), n(row.get("owner_truth_recall"),2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"Recipient-only safety is achieved mainly by abstention (coverage 0.06), so its low all-attempt error is never reported without UNKNOWN 0.94 and conditional error 0.033.")

    # RQ4-II.
    lines.append(r"\textbf{RQ4-II: leave-one-mechanism-out with matched safety denominators.}")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrr}\toprule Variant & $Y$ & $C$ & $U$ & Coverage & UNKNOWN & FA all & FA claimed \\\midrule")
    rq42_labels = {
        "full_rare": r"Full \rare{}",
        "no_evidence_no_update": "No evidence/no update",
        "minus_ownership_gate": "Minus ownership gate",
        "minus_public_evidence": "Minus public evidence",
        "minus_delayed_update": "Minus delayed update",
        "minus_locality": "Minus locality",
        "minus_updater": "Minus updater",
        "minus_selected_only_rule": "Minus selected-only rule",
        "minus_correction_replay": "Minus correction/replay",
    }
    for key, label in rq42_labels.items():
        row = payload["cells"]["RQ4-II"]["rows"][key]
        lines.append(row_cells([label, n(row["quality"]), n(row["complete_cost"],2), n(row["utility"]), n(row["coverage"],2), n(row["unknown_rate"],2), n(row["false_attribution_all_attempts"],4), n(row["false_attribution_claimed"],2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"The ownership gate is the principal safety mechanism: removing it raises coverage to 0.75 but raises all-attempt false attribution from 0.0064 to 0.1800 and claimed-case error from 0.08 to 0.24. No safety ranking is made from a conditional rate alone.")

    # Cost and uncertainty.
    lines.append(r"\section*{6. Shared cost, interval, and denominator contract}")
    lines.append(r"\textbf{Complete-cost arithmetic.} Each total includes selection, execution, publish/read, matched judgment/masked call, assignment commit, communication, model/API/token/tool, verification, update, queue/retry, repair, state storage, and replay. Failed attempts retain observed cost.")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrrrr}\toprule Shared base & Select & Execute & Publish/read & Judgment & Assign & Communicate & Model/API/tool & Verify & Sum \\\midrule Matched base & 0.08 & 0.30 & 0.10 & 0.15 & 0.02 & 0.04 & 0.17 & 0.01 & 0.87 \\\bottomrule\end{tabular}\end{center}")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrr}\toprule Template & Update & Queue/retry & Repair & Storage & Replay & Total $C$ \\\midrule")
    cost_order = ["uniform", "no_update", "raw", "terminal", "context", "task_ridge", "matched_composition", "matched_rls", "matched_sgd", "matched_periodic_refit", "pooled", "rare", "public_only", "delayed_only", "history_only"]
    for key in cost_order:
        vals = cost_templates[key]
        lines.append(row_cells([key.replace("_", r"\_")] + [n(v,3) for v in vals[8:]] + [n(sum(vals),2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"\textbf{Result-row traceability.} Every numeric result row stores a \texttt{cost\_template\_id}, all 13 cost fields, and expected wall seconds. The table below lists every distinct result-row total; the automatic audit recomputes each row from its embedded breakdown.")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrr}\toprule Row-specific ID & Update & Queue/retry & Repair & Storage & Replay & Total $C$ \\\midrule")
    distinct_costs = sorted({row["complete_cost"] for row in all_policy_rows(payload["cells"])})
    for cost in distinct_costs:
        breakdown = complete_cost_breakdown(cost)
        lines.append(row_cells([f"row\_specific\_C\_{cost:.2f}", n(breakdown["update"],3), n(breakdown["queue_retry"],3), n(breakdown["repair"],3), n(breakdown["state_storage"],3), n(breakdown["replay"],3), n(cost,2)]))
    lines.append(r"\bottomrule\end{tabular}\end{center}")
    lines.append(r"Hardware/runtime envelope: four logical CPU cores per stream, no online GPU, 1,024 MiB RAM cap. PeerSelect model/API/token/tool counts are expected zero and are printed in the H3 resource table; ArtifactRole charges them in the normalized ledger. Wall time is stored per row.")

    lines.append(r"\textbf{Expected 95\% planning intervals.} These are not observed confidence intervals and not a common standard deviation. They are root-stratified paired-stream planning ranges. Nonzero latency/state use $\pm10\%$ for single arms.")
    lines.append(r"\begin{center}\scriptsize\begin{tabular}{lrrrrrrrrrr}\toprule Half-width & Brier & Log loss & ECE & AUC & $Y$/payoff & $C$ & $U$ & Rate & Forgetting & Recovery \\\midrule Single arm & 0.008 & 0.018 & 0.006 & 0.020 & 0.012 & 0.030 & 0.011 & 0.015 & 0.020 & 1.2 \\ Paired contrast & 0.006 & 0.012 & 0.004 & 0.014 & 0.009 & 0.020 & 0.008 & 0.010 & 0.015 & 0.8 \\\bottomrule\end{tabular}\end{center}")
    lines.append(r"Precision inputs are explicit and machine-audited: $h=1.96s/\sqrt{18}$, with the single-arm and paired stream-SD assumptions stored metric by metric in the JSON ledger. Recomputed residual is required to be below $10^{-6}$.")
    lines.append(r"\textbf{Denominators.} H1 uses the frozen common held-out cohort. H2 uses all sealed assignments and attempts (ITT), with per-protocol secondary. H3 uses all arrivals/attempted updates including failures, drops, no-ops, timeouts, and UNKNOWN. H4 false-attribution(all) uses all owner-truth-eligible mutations; H4 coverage/UNKNOWN uses all mutation attempts.")

    # Baseline eligibility.
    lines.append(r"\section*{7. Baseline eligibility and scientific boundary}")
    lines.append(r"\begin{center}\small\begin{tabularx}{\linewidth}{@{}L{.25\linewidth}L{.16\linewidth}Y@{}}\toprule Arm/endpoint & Status & Rule \\\midrule")
    eligibility_rows = [
        ("Information counterfactuals/falsifiers", "REQUIRED TARGETS", "Trace/count/J-mask/J-permutation/menu-ID permutation all have expected values and must run on the same cohort and cost contract."),
        ("Contextual-trust-linear", "REQUIRED QUALIFICATION", "Strong same-information control; own history namespace, identical public representation/read cut/menu/budget/cost."),
        ("Task-conditioned ridge", "REQUIRED EXPECTED TARGET", "Numeric expectation is part of the sole reference; the eventual observed comparison is inadmissible until executable and qualified."),
        ("Matched composition", "REQUIRED EXPECTED TARGET", "Required guard against ordinary components explaining the gain; same qualification rule."),
        ("Matched RLS/SGD/periodic refit", "REQUIRED EXPECTED TARGETS", "Updater comparators nested under one information policy; they prevent automatic updater-superiority claims."),
        ("Closest published adapter", "NO-GO", "No faithful drop-in currently preserves the causal unit, timing, selected-only rule, assignment, and complete cost; therefore it has no numeric cell."),
        ("Graph-IPD", "N/A as substitute", "External native-cooperation reference only; cannot fill any nine-cell result without a qualified adapter."),
        ("PeerSelect false attribution", "N/A", "No producer owner-truth contract."),
        ("No-update full update latency", "N/A", "Report its no-op path separately; it cannot be ranked as full update latency."),
    ]
    for arm, status, rule in eligibility_rows:
        lines.append(row_cells([arm, status, rule]))
    lines.append(r"\bottomrule\end{tabularx}\end{center}")

    # Audit and sources.
    passed_count = sum(1 for check in audit["checks"] if check["passed"])
    lines.append(r"\section*{8. Automatic consistency audit}")
    lines.append(f"All {passed_count}/{len(audit['checks'])} automatic checks passed: utility identities, cost-component sums, factorial identities, coverage/UNKNOWN complements, false-attribution denominator transforms, positive/negative regime guards, nine-cell identity, and absence of TBD/ambiguous $\\pm$ placeholders. The scientific evidence gate remains open because this artifact has zero benchmark/API/GPU runs.")
    lines.append(r"\section*{9. Scale-calibration references}")
    lines.append(r"\small Public references inform metric discipline and conservative scale; none supplies a protocol-equivalent RARE effect.\begin{itemize}")
    for source in SOURCE_URLS:
        lines.append(r"\item " + tex_escape(f"{source['authors']} ({source['year']}), {source['title']}. {source['url']}. {source['use']}"))
    lines.append(r"\end{itemize}")
    lines.append(r"\textbf{Final interpretation.} RARE is expected to be modestly better only where typed evidence is informative and task--peer crossover is stable. It is expected to be more expensive, slower, and larger in state; pooled/reset/uniform controls deliberately win in sparse, stale, or high-load regimes. This complete pattern---including losses---is the sole expected benchmark.")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


audit = audit_data(data)
data["automatic_audit"] = {"passed": audit["passed"], "check_count": len(audit["checks"])}

ARTICLE.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)

JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
AUDIT_PATH.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
TEX.write_text(build_tex(data, audit), encoding="utf-8")

readme = f"""# Numeric expected experiment matrix v4 (2026-10-09)

This is the sole numerical expectation reference for the experiment matrix in `artifacts/aamas2027/main.pdf`.
It is `EXPECTED_NOT_OBSERVED`, not an empirical result and not evidence that the benchmark/baseline gate has closed.

## Construction

- Structure: current `main.pdf` four-row matrix expanded to the nine execution cells in `EXPERIMENT_MATRIX_EXECUTION_MANIFEST_20261008.md`.
- Numeric mother: expected v3 JSON (the v3 PDF is broken and is not reused).
- Uncertainty logic: guide v2 paired/root sensitivity model.
- Direction guards: guide v5, including deliberate sparse, stale, and high-load losses.
- Utility: `U = Y - 0.10 * C`; matched uniform complete cost is `1.00`.

## Files

- Source: `article/aamas2027/expected_experiment_matrix_v4_20261009/expected_experiment_matrix.tex`
- Values: `docs/paper/aamas2027/expected_experiment_matrix_v4_20261009/expected_results.json`
- Automatic audit: `docs/paper/aamas2027/expected_experiment_matrix_v4_20261009/numeric_audit.json`
- PDF: `artifacts/aamas2027/expected_experiment_matrix_v4_20261009/expected_experiment_matrix.pdf`

## Status

Automatic numeric audit: `{audit['passed']}` ({sum(1 for item in audit['checks'] if item['passed'])}/{len(audit['checks'])} checks).
Scientific evidence gate: `OPEN` by design; benchmark runs = 0.
"""
README_PATH.write_text(readme, encoding="utf-8")

if not audit["passed"]:
    failed = [item for item in audit["checks"] if not item["passed"]]
    raise SystemExit("Numeric audit failed: " + json.dumps(failed, ensure_ascii=False))

print(json.dumps({
    "tex": str(TEX),
    "json": str(JSON_PATH),
    "audit": str(AUDIT_PATH),
    "automatic_audit_passed": audit["passed"],
    "check_count": len(audit["checks"]),
}, indent=2))
