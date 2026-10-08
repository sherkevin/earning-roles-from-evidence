"""Zero-call qualification for the replaceable public-profile generator seam.

This checks admissibility, lineage-bound digest construction, cost accounting,
and rejection of UNKNOWN/private inputs.  It is not a profile-quality or
role-learning experiment.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_metateam_profile_qualification import digest, profile  # noqa: E402
from peerrolebench_profile_generator import (  # noqa: E402
    DeterministicPublicProfileGenerator,
    PublicProfileGenerationRequest,
)


def request(projection=None) -> ProfileGenerationRequest:
    selection = SimpleNamespace(
        candidates=(SimpleNamespace(key="agent-a@v1"), SimpleNamespace(key="agent-b@v1")),
        chosen_index=0, protocol_event_id="selection-0", event_id="decision-0", task_index=0,
    )
    feedback = SimpleNamespace(
        selection_event_id="selection-0", source_event_id="judgment-0",
        delivery_id="delivery-0", producer_id="agent-a", producer_version="v1",
        recipient_id="agent-r", protocol_event_id="judgment-0", sidecar_digest="a" * 64,
    )
    if projection is None:
        projection = SimpleNamespace(
            source="recipient_judgment", candidate_key="agent-a@v1", source_event_id="judgment-0",
            disposition="eligible", provenance="public", arrival_index=2,
            public_payload=lambda: {
                "feedback_id": "feedback-0", "source_event_id": "judgment-0",
                "source": "recipient_judgment", "candidate_key": "agent-a@v1",
                "evidence_version": "evidence-v1", "source_index": 2, "arrival_index": 2,
                "arrived_at": 2.0, "delay": 0.0, "action": "use", "disposition": "eligible",
                "provenance": "public", "label": 1.0,
            },
        )
    return PublicProfileGenerationRequest(
        selection=selection, feedback_sidecar=feedback, public_projection=projection,
        attribution_gate=SimpleNamespace(eligible=True, gate_digest="b" * 64,
                                         sidecar_digest="a" * 64, protocol_event_id="judgment-0"),
        profile_id="profile-a-r1", profile_revision=1, profile=profile().profile,
        parser_version="fixture-parser-v1", model_config_digest=digest("model"),
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=False, exist_ok=False)
    script = Path(__file__).resolve()
    config = {
        "qualification": "public-profile-generator-seam-v1",
        "script": str(script.relative_to(ROOT)),
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "generator": "deterministic-public-profile-fixture-v1",
        "fixture_mode": "deterministic_public_only",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "python": platform.python_version(), "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    checks = []
    generated = DeterministicPublicProfileGenerator().generate(request())
    checks.append({
        "name": "eligible_public_input_generates_profile",
        "status": "PASS",
        "source_input_digest": generated.profile.source_input_digest,
        "profile_digest": generated.profile.profile_digest,
    })
    checks.append({
        "name": "receipt_cost_and_claim_boundary",
        "status": "PASS" if generated.receipt.real_api_calls == 0
        and generated.receipt.gpu_jobs == 0
        and generated.receipt.scientific_claim_allowed is False
        and generated.receipt.cost_usd == 0.0 else "FAIL",
    })

    def rejected(name, projection):
        try:
            DeterministicPublicProfileGenerator().generate(request(projection))
        except ValueError as exc:
            checks.append({"name": name, "status": "PASS", "error": str(exc)})
        else:
            checks.append({"name": name, "status": "FAIL"})

    rejected("unknown_does_not_generate_profile", SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-a@v1", source_event_id="judgment-0",
        disposition="unknown", provenance="unknown", arrival_index=2,
        public_payload=lambda: {"feedback_id": "feedback-0", "source": "recipient_judgment"},
    ))
    rejected("private_terminal_field_rejected", SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-a@v1", source_event_id="judgment-0",
        disposition="eligible", provenance="public", arrival_index=2,
        public_payload=lambda: {"feedback_id": "feedback-0", "terminal_score": 1.0},
    ))
    rejected("unselected_candidate_rejected", SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-b@v1", source_event_id="judgment-0",
        disposition="eligible", provenance="public", arrival_index=2,
        public_payload=lambda: {"feedback_id": "feedback-0", "source": "recipient_judgment",
                                "candidate_key": "agent-b@v1"},
    ))
    raw = {"profile": generated.profile.payload(), "receipt": generated.receipt.__dict__, "checks": checks}
    (out_dir / "raw.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result = {
        **config,
        "status": "QUALIFIED_OFFLINE" if all(c["status"] == "PASS" for c in checks) else "FAILED_OFFLINE",
        "checks": checks,
        "remaining_gates": [
            "replace deterministic fixture with a separately metered public-only generator",
            "bind generator request to PIPE3 responsibility gate digest in live runner",
            "qualify profile predictive value on independent later assignments",
        ],
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({k: result[k] for k in ("status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    raise SystemExit(result["status"] != "QUALIFIED_OFFLINE")
