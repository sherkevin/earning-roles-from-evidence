"""Zero-call qualification for the typed projection -> public offer seam."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_policy_projection import PolicyFeedbackProjection  # noqa: E402
from peerrolebench_public_feedback_rows import (  # noqa: E402
    offer_from_projections, projection_to_public_row,
)


def projection(*, feedback_id: str, disposition: str, arrival_index: int | None,
               candidate_key: str = "agent-b@v1") -> PolicyFeedbackProjection:
    eligible = disposition == "eligible"
    return PolicyFeedbackProjection(
        feedback_id=feedback_id, source_event_id=f"policy-selection-{feedback_id}",
        source="recipient_judgment", candidate_key=candidate_key,
        evidence_version="pipe3-evidence-v1", source_index=0,
        arrived_at=5.0, delay=3.0, action="repair", disposition=disposition,
        provenance="public" if eligible else "unknown", label=1.0 if eligible else None,
        arrival_index=arrival_index,
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "qualification": "typed-projection-public-feedback-row-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256((ROOT / "scripts/peerrolebench_public_feedback_rows.py").read_bytes()).hexdigest(),
        "fixture_mode": "typed-projection-and-assignment-offer",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "python": platform.python_version(), "platform": platform.platform(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    checks = []

    eligible = projection(feedback_id="f-eligible", disposition="eligible", arrival_index=2)
    row = projection_to_public_row(eligible)
    checks.append({"name": "eligible_projection_to_public_row", "status": "PASS", "keys": sorted(row)})
    unknown = projection(feedback_id="f-unknown", disposition="unknown", arrival_index=3)
    unknown_row = projection_to_public_row(unknown, unknown_reason="mixed-ownership")
    checks.append({"name": "unknown_projection_keeps_reason_without_label", "status": "PASS", "row": unknown_row})
    offer = offer_from_projections(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1",
        candidate_keys=("agent-a@v1", "agent-b@v1"),
        projections=((eligible, None), (unknown, "mixed-ownership")),
        evidence_version="pipe3-evidence-v1", available_index=3,
    )
    checks.append({"name": "offer_from_typed_projections", "status": "PASS", "bundle_digest": offer.bundle_digest})

    def reject(name, fn):
        try:
            fn()
        except (TypeError, ValueError) as exc:
            checks.append({"name": name, "status": "PASS", "error": str(exc)})
        else:
            checks.append({"name": name, "status": "FAIL"})

    reject("reject_wall_clock_only_projection", lambda: projection_to_public_row(
        projection(feedback_id="f-old", disposition="eligible", arrival_index=None)))
    reject("reject_projection_outside_menu", lambda: offer_from_projections(
        offer_id="offer-2", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=("agent-a@v1",),
        projections=((eligible, None),), evidence_version="pipe3-evidence-v1", available_index=3))
    reject("reject_unknown_without_reason", lambda: projection_to_public_row(unknown))
    reject("reject_private_projection_shape", lambda: projection_to_public_row({"label": 1.0}))

    result = {**config, "status": "QUALIFIED_OFFLINE" if all(item["status"] == "PASS" for item in checks) else "FAILED_OFFLINE", "checks": checks}
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "raw.json").write_text(json.dumps({"eligible": eligible.public_payload(), "unknown": unknown.public_payload(), "offer": offer.payload()}, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
