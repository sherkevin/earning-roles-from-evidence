"""Offline numerical/representation audit; never runs an agent task or API.

Artificial signed labels test representational capacity, not task performance.
Optional local frozen encoding inspects public contract text coverage only.
"""
from pathlib import Path
import argparse
import datetime
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

ROOT = Path(__file__).resolve().parents[1]
ENCODERS = {
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"),
    "bge": ("BAAI/bge-small-en-v1.5", "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"),
}
FILES = ["scripts/peerrolebench_signed_ridge.py", "scripts/peerrolebench_contextual_ridge_check.py",
         "tests/test_peerrolebench_signed_ridge.py", "tests/test_peerrolebench_disjoint_ridge.py",
         "scripts/peerrolebench_pipe3_public_contract_v2.py", "scripts/peerrolebench_pipe3_material_adapter.py"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--local-encoder", action="store_true")
    parser.add_argument("--encoder", choices=tuple(ENCODERS), default="minilm")
    args = parser.parse_args()
    model_name, revision = ENCODERS[args.encoder]
    model_path = Path.home() / ".cache/huggingface/hub" / ("models--" + model_name.replace("/", "--")) / "snapshots" / revision
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
           "TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
           "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    os.environ.update(env)
    configuration = {"schema": "contextual-ridge-audit-v2", "started_utc": now(),
        "command": sys.argv, "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "platform": platform.platform(), "python": platform.python_version(),
        "hardware": {"device": "cpu", "gpu_used": False}, "environment_overrides": env,
        "seed": 0, "rho": 1.0, "numerical_labels": "authored signed controls, NOT task rewards",
        "tests": FILES[2:4], "candidate_keys": ["agent-a@v1", "agent-b@v1"],
        "source_hashes": {p: sha(ROOT / p) for p in FILES},
        "libraries": {p: importlib.metadata.version(p) for p in ["numpy", "pytest", "torch", "sentence-transformers", "transformers"]},
        "encoder_enabled": args.local_encoder, "encoder_model": model_name,
        "encoder_revision": revision, "encoder_path": str(model_path),
        "encoder_files": {str(p.relative_to(model_path)): sha(p) for p in model_path.rglob("*") if p.is_file()} if args.local_encoder else {},
        "encoder_check": "4 public contract/role texts, batch encoding + repeat first; record truncation, no utility labels",
        "api_calls": 0, "gpu_calls": 0, "scientific_efficacy_experiment": False}
    (out / "config.json").write_text(json.dumps(configuration, indent=2) + "\n")
    for name in FILES:
        dest = out / "source" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    with (out / "raw.jsonl").open("w") as raw:
        def emit(event, **payload):
            raw.write(json.dumps({"timestamp_utc": now(), "event": event, **payload}) + "\n")
            raw.flush()
        emit("configured", config_sha256=sha(out / "config.json"))
        summary = {"status": "RUNNING", "api_calls": 0, "gpu_calls": 0,
                   "scientific_claim_allowed": False}
        try:
            start = time.perf_counter()
            with (out / "pytest.log").open("w") as console:
                tested = subprocess.run([sys.executable, "-m", "pytest", "-q", *FILES[2:4]],
                                        cwd=ROOT, stdout=console, stderr=subprocess.STDOUT)
            emit("pytest", returncode=tested.returncode, wall_seconds=time.perf_counter() - start)
            if tested.returncode:
                raise RuntimeError("focused tests failed; see pytest.log")
            import numpy as np
            from peerrolebench_signed_ridge import SignedRidgeState, DisjointSignedRidgeState
            keys = tuple(configuration["candidate_keys"])
            bank = DisjointSignedRidgeState(keys, 2, 1.0)
            identity, additive = SignedRidgeState(2, 1.0), SignedRidgeState(4, 1.0)
            rows = [(0, [1., 0.], 1.), (1, [1., 0.], -1.),
                    (0, [0., 1.], -1.), (1, [0., 1.], 1.)]
            for index, (chosen, context, target) in enumerate(rows):
                e = np.eye(2)[chosen]
                joined = np.concatenate([context, e]) / np.sqrt(2.)
                bank.update(keys[chosen], context, target)
                identity.update(e, target)
                additive.update(joined, target)
                emit("authored_control_update", index=index, chosen=keys[chosen], context=context,
                     signed_control_target=target, bank_weights={k: bank.weights(k).tolist() for k in keys})
            comparisons = []
            for context in [[1., 0.], [0., 1.]]:
                row = {"context": context, "identity": {k: identity.predict(np.eye(2)[j]) for j, k in enumerate(keys)},
                       "additive": {k: additive.predict(np.concatenate([context, np.eye(2)[j]]) / np.sqrt(2.)) for j, k in enumerate(keys)},
                       "disjoint": bank.scores(keys, context)}
                comparisons.append(row)
                emit("authored_control_prediction", **row)
            assert comparisons[0]["disjoint"][keys[0]] > comparisons[0]["disjoint"][keys[1]]
            assert comparisons[1]["disjoint"][keys[0]] < comparisons[1]["disjoint"][keys[1]]
            summary["authored_control"] = comparisons
            if args.local_encoder:
                import torch
                from sentence_transformers import SentenceTransformer
                from peerrolebench_pipe3_material_adapter import neutral_task_text
                from peerrolebench_pipe3_public_contract_v2 import public_task_text
                torch.set_num_threads(1)
                torch.manual_seed(0)
                texts = []
                for version, builder in [("legacy_public_v1", neutral_task_text), ("public_v2", public_task_text)]:
                    fields = builder("user_analytics")
                    for role in ["producer", "recipient"]:
                        text = f"Assigned role: {role}\n" + fields["spec_md"] + "\n" + fields["brief_md"]
                        texts.append({"id": version + ":" + role, "text": text,
                                      "origin": "deterministic public contract adapter; not a new executed task"})
                (out / "encoder_inputs.json").write_text(json.dumps(texts, indent=2) + "\n")
                emit("encoder_load_start", local_files_only=True, device="cpu")
                start = time.perf_counter()
                model = SentenceTransformer(str(model_path), device="cpu", local_files_only=True)
                model.eval()
                model.requires_grad_(False)
                emit("encoder_loaded", wall_seconds=time.perf_counter() - start, max_seq_length=model.max_seq_length)
                counts = [len(model.tokenizer(row["text"], truncation=False)["input_ids"]) for row in texts]
                for row, count in zip(texts, counts):
                    emit("encoder_input", id=row["id"], tokens_before_truncation=count,
                         max_seq_length=model.max_seq_length, truncated=count > model.max_seq_length)
                start = time.perf_counter()
                vectors = model.encode([r["text"] for r in texts], batch_size=4, normalize_embeddings=True, show_progress_bar=False)
                elapsed = time.perf_counter() - start
                np.save(out / "embeddings.npy", vectors, allow_pickle=False)
                emit("encoder_batch", count=len(texts), dimensions=list(vectors.shape), wall_seconds=elapsed,
                     embeddings_sha256=sha(out / "embeddings.npy"))
                repeat = model.encode([texts[0]["text"]], normalize_embeddings=True, show_progress_bar=False)[0]
                error = float(np.max(np.abs(repeat - vectors[0])))
                summary["encoder"] = {"dimension": int(vectors.shape[1]), "input_count": len(texts),
                    "tokens_before_truncation": counts, "max_seq_length": model.max_seq_length,
                    "truncated_inputs": sum(c > model.max_seq_length for c in counts),
                    "cosine_matrix": (vectors @ vectors.T).tolist(), "repeat_max_abs_error": error,
                    "input_coverage_qualified": not any(c > model.max_seq_length for c in counts),
                    "final_backbone_selected": False, "reward_updates_from_embeddings": 0}
                emit("encoder_summary", **summary["encoder"])
                assert np.isfinite(vectors).all() and error <= 1e-6
            summary.update(status="AUDIT_COMPLETED", finished_utc=now(),
                           source_unchanged=all(sha(ROOT/p) == h for p, h in configuration["source_hashes"].items()))
            emit("completed", status=summary["status"])
        except Exception as exc:
            summary.update(status="FAILED", error=repr(exc), finished_utc=now())
            (out / "failure.txt").write_text(traceback.format_exc())
            emit("failure", error=repr(exc), traceback=traceback.format_exc())
            raise
        finally:
            (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(json.dumps(summary))


if __name__ == "__main__":
    main()
