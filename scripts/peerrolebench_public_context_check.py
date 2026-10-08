"""One offline BGE encoding and existing selection/capture roundtrip; no task API."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MODEL = "BAAI/bge-small-en-v1.5"
REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
REQUEST = ROOT / "experiments/logs/n03_scoped_judgment_prepare_20261007_v2/requests/request_14b794d43a7b52d97bb9.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    model_path = Path.home() / ".cache/huggingface/hub/models--BAAI--bge-small-en-v1.5/snapshots" / REVISION
    env = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "TOKENIZERS_PARALLELISM": "false",
           "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    os.environ.update(env)
    tests = ["tests/test_peerrolebench_public_context.py", "tests/test_peerrolebench_signed_ridge.py",
             "tests/test_peerrolebench_c1_decision_capture.py"]
    files = [str(Path(__file__).relative_to(ROOT)), "scripts/peerrolebench_public_context.py",
             "scripts/peerrolebench_signed_ridge.py", "scripts/peerrolebench_c1_pipe3_bounded_live.py",
             "scripts/peerrolebench_pipe3_runner_v1.py", "scripts/peerrolebench_baseline_policies.py",
             "scripts/peerrolebench_policy_sidecar.py"] + tests
    config = {"schema": "public-context-check-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "command": [sys.executable, *sys.argv], "git_commit": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "python": sys.version, "platform": platform.platform(), "environment_overrides": env,
              "packages": {name: importlib.metadata.version(name) for name in
                           ["numpy", "pytest", "torch", "transformers", "sentence-transformers"]},
              "source_sha256": {p: sha(ROOT / p) for p in files}, "request_path": str(REQUEST.relative_to(ROOT)),
              "request_sha256": sha(REQUEST), "encoder_model": MODEL, "encoder_revision": REVISION,
              "encoder_files": {str(p.relative_to(model_path)): sha(p) for p in model_path.rglob("*") if p.is_file()},
              "seed": 0, "device": "cpu", "api_calls": 0, "gpu_jobs": 0, "reward_updates": 0,
              "recipe": "Task: full prepared public spec+brief. Recipient: stated recipient role/ownership+same brief. Version: public processor source digest, metadata only. Two separately encoded segments concatenated equally.",
              "scope": "Current public-contract representation and synthetic 0-shot selection interface only; no agent execution, historical retrieval, capability or efficacy result.",
              "stop_rule": "Any test, coverage, binding or encoding error stops; no model/prompt substitution."}
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    for name in files:
        dest = out / "source" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    shutil.copyfile(REQUEST, out / "public_request.json")

    def emit(event, **payload):
        with (out / "raw.jsonl").open("a") as stream:
            stream.write(json.dumps({"time_utc": datetime.now(timezone.utc).isoformat(), "event": event, **payload}) + "\n")

    summary = {"scope": config["scope"], "api_calls": 0, "gpu_jobs": 0, "reward_updates": 0, "passed": False}
    started = time.monotonic()
    try:
        command = [sys.executable, "-m", "pytest", "-q", *tests, "--junitxml", str(out / "junit.xml"),
                   "--basetemp", str(out / "pytest_tmp")]
        emit("tests_start", command=command)
        with (out / "pytest.log").open("w") as console:
            result = subprocess.run(command, cwd=ROOT, stdout=console, stderr=subprocess.STDOUT)
        emit("tests_end", returncode=result.returncode)
        if result.returncode:
            raise RuntimeError("targeted software checks failed")
        import numpy as np
        import torch
        from sentence_transformers import SentenceTransformer
        from peerrolebench_public_context import encode_public_context, restore_public_context, SCHEMA_VERSION
        from peerrolebench_baseline_policies import NoUpdatePolicy
        from peerrolebench_pipe3_full_chain_qualification import registry
        from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, make_offer
        from peerrolebench_c1_pipe3_bounded_live import save_decision_capture, load_decision_capture
        from peerrolebench_signed_ridge import DisjointSignedRidgeState
        torch.set_num_threads(1)
        torch.manual_seed(0)
        request = json.loads(REQUEST.read_text())
        public = json.loads(request["messages"][0]["content"].split("\n\nPublic task payload:\n", 1)[1])
        texts = public["public_task_text"]
        task = texts["spec_md"] + "\n" + texts["brief_md"]
        recipient = "Assigned role: recipient. Own processor.py; models.py and sink.py are read-only.\n" + texts["brief_md"]
        declared_version = "public-processor-sha256:" + hashlib.sha256(
            public["public_source_files"]["processor.py"].encode()).hexdigest()
        emit("encoder_load_start", local_files_only=True)
        model = SentenceTransformer(str(model_path), device="cpu", local_files_only=True)
        if getattr(model, "default_prompt_name", None) is not None:
            raise ValueError("unexpected default encoder prompt")
        emit("encode_start", task_chars=len(task), recipient_chars=len(recipient))
        encode_start = time.monotonic()
        z, receipt = encode_public_context(task_contract=task, recipient_contract=recipient,
            recipient_id="peer-a", declared_recipient_version=declared_version, read_cut=0,
            tokenizer=model.tokenizer, encoder=model, encoder_version=MODEL + "@" + REVISION,
            max_seq_length=model.max_seq_length)
        encode_seconds = time.monotonic() - encode_start
        actual_counts = model.tokenize([task, recipient])["attention_mask"].sum(dim=1).tolist()
        if actual_counts != list(receipt["token_counts"].values()):
            raise ValueError("encoder actual tokenization differs from full token counts")
        (out / "context_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        emit("encode_end", dimension=len(z), actual_tokens=actual_counts, wall_seconds=encode_seconds)
        boundary = Pipe3SelectionBoundary(NoUpdatePolicy(), registry())
        keys = tuple(entry.key for entry in boundary.registry)
        bank = DisjointSignedRidgeState(keys, len(z), 1.0)
        offer = make_offer(offer_id="context-check-offer", task_id=public["task_id"], task_index=0,
            role="producer", context_key=receipt["payload_digest"], candidate_keys=keys, public_rows=[],
            evidence_version="empty-history-v1", available_index=0)
        scores = bank.scores(keys, z)
        seal = boundary.choose_and_seal(offer=offer, native_selection_id="context-check-selection",
            selector_id="peer-a", role="producer", base_scores=[scores[k] for k in keys],
            rng=np.random.default_rng(0), state_version=receipt["payload_digest"],
            encoder_version=receipt["encoder_version"], feature_schema=SCHEMA_VERSION,
            policy_version="no-update-context-interface-v1", base_score_version="untrained-disjoint-ridge-v1",
            rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0, read_cut=0, decision_index=0,
            consume_evidence=False, captured_features={key: z for key in keys})
        save_decision_capture(out / "preexecution_capture.json", seal, boundary)
        recovered = load_decision_capture(out / "preexecution_capture.json", ledger_events=boundary.ledger.events,
                                         auxiliary_rows=boundary.auxiliary_manifest_rows)
        restored = restore_public_context(json.loads((out / "context_receipt.json").read_text()),
            expected_payload_digest=seal.decision_sidecar.state_version, read_cut=seal.attestation.read_cut,
            recipient_id=seal.native_selection.selector_id, declared_recipient_version=declared_version,
            encoder_version=seal.decision_sidecar.encoder_version)
        if z != recovered or z != restored or seal.decision_sidecar.context_key != receipt["payload_digest"]:
            raise ValueError("context receipt is not the vector sealed for this selection")
        summary.update(passed=True, token_counts=receipt["token_counts"], dimension=len(z),
            context_digest=receipt["payload_digest"], chosen_key=seal.policy_selection.chosen.key,
            probabilities=list(seal.policy_selection.probabilities), exact_roundtrip=True,
            encode_seconds=encode_seconds, ridge_array_bytes=bank.memory_bytes,
            prior_scores=scores, persistent_updates=bank.total_updates,
            historical_memory_used=False, recipient_implementation_embedded=False,
            recipient_version_scope="public processor file digest only; not full backend identity")
    except Exception as exc:
        summary.update(error_type=type(exc).__name__, error=str(exc))
        (out / "error.txt").write_text(traceback.format_exc())
        emit("failure", error_type=type(exc).__name__, error=str(exc))
    summary["wall_seconds"] = time.monotonic() - started
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    emit("run_end", **summary)
    print(json.dumps(summary))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
