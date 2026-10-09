"""Render algebraic boundaries for an explicitly non-empirical research guide.

No sampled observations, API calls, training, estimated ranks or test power.
The config is written before calculations; export the PDF separately.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = "v3_20261008"
DOCS = ROOT / "docs/paper/aamas2027/guides" / VERSION
SOURCE = ROOT / "article/aamas2027/guides" / VERSION
OUT = ROOT / "artifacts/aamas2027" / f"guide_experiment_matrix_{VERSION}"
LOG = ROOT / "experiments/logs/experiment_target_guide_20261008_v3_r2"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    specpath = DOCS / "boundary_spec.json"
    spec = json.loads(specpath.read_text())
    template = SOURCE / "guide_template.tex"
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    if (LOG / "config.json").exists():
        raise RuntimeError("Frozen build already exists; use a new version for revisions.")
    config = {
        "kind": spec["kind"], "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/build_experiment_target_guide_v3.py",
        "python": sys.version,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "worktree_scope": "Existing unrelated edits retained; exact authored sources hashed",
        "code_sha256": digest(Path(__file__)), "spec_sha256": digest(specpath),
        "template_sha256": digest(template),
        "source_sha256": {p: digest(ROOT / p) for p in spec["source_files"]},
        "protected_file_sha256_before": {p: digest(ROOT / p) for p in spec["protected_files"]},
        "new_api_calls": 0, "gpu_jobs": 0, "benchmark_runs": 0,
        "not_observed": True, "empirical_forecast": False,
    }
    dump(LOG / "config.json", config)
    raw = LOG / "raw.jsonl"

    def event(name, payload):
        with raw.open("a") as f:
            f.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "event": name, "payload": payload}) + "\n")

    event("configuration_sealed", {"config_sha256": digest(LOG / "config.json")})
    lam = spec["illustrative_lambda"]
    contrasts = [dict(c, delta_utility=c["delta_quality"] - lam * c["delta_cost"])
                 for c in spec["contrasts"]]
    for contrast in contrasts:
        if abs(contrast["delta_utility"]) < 1e-12:
            contrast["delta_utility"] = 0.0
    by = {c["id"]: c for c in contrasts}
    assert abs(by["B2"]["delta_utility"]) < 1e-12
    assert all(by[i]["delta_utility"] < 0 for i in ["B0", "B3", "B4", "B5"])
    assert all(by[i]["delta_utility"] > 0 for i in ["B1", "B6"])
    v2 = spec["v2_boundary_inputs"]
    alpha = 1 + v2["lambda"] * v2["gamma"] / v2["baseline_cost_c0"]
    threshold = v2["lambda"] / (v2["baseline_cost_c0"] * alpha * v2["d"])
    hlimit = v2["delta_kappa"] / threshold
    bounds = {}
    for name, v in spec["missing_outcome_example"].items():
        if name == "status":
            continue
        lower = (1 - v["unknown_fraction"]) * v["observed_binary_quality"]
        bounds[name] = [lower, lower + v["unknown_fraction"]]
    assert bounds["candidate"][0] < bounds["control"][1]
    assert bounds["control"][0] < bounds["candidate"][1]
    calculations = {
        "kind": "deterministic_algebraic_stress_cases", "not_observed": True,
        "empirical_forecast": False, "method_ranks_supplied": False,
        "estimated_variances_supplied": False, "contrasts": contrasts,
        "v2_boundary": {"alpha": alpha, "kappa_threshold_per_extra_h": threshold,
                        "extra_h_break_even_for_delta_kappa_025": hlimit},
        "unknown_bounds": bounds, "new_api_calls": 0, "gpu_jobs": 0,
    }
    dump(OUT / "boundary_calculations.json", calculations)
    (OUT / "boundary_spec.json").write_bytes(specpath.read_bytes())
    rows = "\n".join(f"{c['id']} & {c['condition']} & {c['delta_quality']:+.3f} & "
                      f"{c['delta_cost']:+.3f} & {c['delta_utility']:+.3f}\\\\"
                      for c in contrasts)
    substitutions = {"@@BOUNDARY_ROWS@@": rows,
                     "@@KAPPA_THRESHOLD@@": f"{threshold:.4f}",
                     "@@H_THRESHOLD@@": f"{hlimit:.3f}",
                     "@@UNKNOWN_CANDIDATE@@": ", ".join(f"{x:.4f}" for x in bounds["candidate"]),
                     "@@UNKNOWN_CONTROL@@": ", ".join(f"{x:.4f}" for x in bounds["control"])}
    tex = template.read_text()
    for key, value in substitutions.items():
        tex = tex.replace(key, value)
    assert "@@" not in tex
    target = SOURCE / "guide_experiment_matrix.tex"
    target.write_text(tex)
    event("algebra_checked", {"calculation_sha256": digest(OUT / "boundary_calculations.json"),
                             "source_sha256": digest(target), "case_count": len(contrasts),
                             "empirical_forecast": False})
    print("Seven algebraic win/tie/loss boundaries checked; no empirical method forecast.")
    print(target)


if __name__ == "__main__":
    main()
