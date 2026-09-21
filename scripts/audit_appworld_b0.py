from __future__ import annotations
import argparse, hashlib, itertools, json, subprocess
from collections import Counter, defaultdict
from pathlib import Path

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def core_apis(root: Path, task_id: str) -> frozenset[str]:
    apis = load_json(root / "data" / "tasks" / task_id / "ground_truth" / "required_apis.json")
    return frozenset(
        x for x in apis
        if not x.startswith("supervisor.") and not x.endswith(".login")
    )

def load_ids(root: Path, split: str) -> list[str]:
    return [
        x.strip() for x in (root / "data" / "datasets" / f"{split}.txt").read_text().splitlines()
        if x.strip()
    ]

def task_record(root: Path, task_id: str) -> dict:
    base = root / "data" / "tasks" / task_id
    meta = load_json(base / "ground_truth" / "metadata.json")
    tests = load_json(base / "ground_truth" / "test_data.json")
    return {
        "task_id": task_id,
        "family": task_id.rsplit("_", 1)[0],
        "instruction": load_json(base / "specs.json")["instruction"],
        "required_apps": load_json(base / "ground_truth" / "required_apps.json"),
        "core_apis": sorted(core_apis(root, task_id)),
        "difficulty": meta["difficulty"],
        "num_apps": meta["num_apps"],
        "num_apis": meta["num_apis"],
        "num_api_calls": meta["num_api_calls"],
        "no_op_fail": sum(x["label"] == "no_op_fail" for x in tests),
        "no_op_pass": sum(x["label"] == "no_op_pass" for x in tests),
    }
def family_records(tasks: list[dict]) -> dict[str, dict]:
    grouped = defaultdict(list)
    for t in tasks:
        grouped[t["family"]].append(t)
    out = {}
    for family, rows in grouped.items():
        sigs = [frozenset(x["core_apis"]) for x in rows]
        out[family] = {
            "family": family,
            "instances": [x["task_id"] for x in rows],
            "instructions": [x["instruction"] for x in rows],
            "api_intersection": sorted(frozenset.intersection(*sigs)),
            "api_union": sorted(frozenset.union(*sigs)),
            "signature_invariant": len(set(sigs)) == 1,
            "difficulty": sorted(set(x["difficulty"] for x in rows)),
            "num_apps": sorted(set(x["num_apps"] for x in rows)),
            "required_apps": sorted(set().union(*(set(x["required_apps"]) for x in rows))),
            "no_op_fail_min": min(x["no_op_fail"] for x in rows),
            "no_op_fail_max": max(x["no_op_fail"] for x in rows),
        }
    return out

def best_cover(target: frozenset[str], train: dict[str, dict], max_donors: int = 3):
    items = [(f, frozenset(r["api_union"])) for f, r in train.items()]
    candidates = []
    for k in range(1, max_donors + 1):
        for combo in itertools.combinations(items, k):
            union = frozenset().union(*(x[1] for x in combo))
            if target <= union:
                extras = len(union - target)
                overlap = sum(len(x[1] & target) for x in combo)
                candidates.append((extras, k, -overlap, tuple(x[0] for x in combo)))
    return min(candidates) if candidates else None
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--appworld-root", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    root, out = Path(args.appworld_root), Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    split_ids = {s: load_ids(root, s) for s in ["train", "dev", "test_normal", "test_challenge"]}
    split_families = {s: {x.rsplit("_", 1)[0] for x in ids} for s, ids in split_ids.items()}
    train_tasks = [task_record(root, x) for x in split_ids["train"]]
    dev_tasks = [task_record(root, x) for x in split_ids["dev"]]
    train_fam, dev_fam = family_records(train_tasks), family_records(dev_tasks)
    train_api_universe = frozenset().union(
        *(frozenset(x["core_apis"]) for x in train_tasks)
    )
    train_signatures = {
        frozenset(r["api_union"]) for r in train_fam.values()
    }

    candidates = []
    for family, record in dev_fam.items():
        target = frozenset(record["api_union"])
        all_seen = target <= train_api_universe
        single_contains = any(
            target <= frozenset(x["api_union"]) for x in train_fam.values()
        )
        cover = best_cover(target, train_fam)
        row = {
            **record,
            "all_primitives_seen_in_train": all_seen,
            "exact_family_signature_seen_in_train": target in train_signatures,
            "single_train_family_contains_target": single_contains,
            "best_cover": None,
        }
        if cover:
            extras, k, _, donors = cover
            row["best_cover"] = {
                "donors": list(donors), "num_donors": k, "extra_api_count": extras
            }
        row["strict_composition_candidate"] = bool(
            record["signature_invariant"]
            and all_seen
            and not single_contains
            and cover is not None
            and 2 <= cover[1] <= 3
        )
        candidates.append(row)
    strict = [x for x in candidates if x["strict_composition_candidate"]]
    summary = {
        "appworld_commit": subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip(),
        "data_version": (root / "data" / "version.txt").read_text().strip(),
        "train_instances": len(train_tasks),
        "train_families": len(train_fam),
        "dev_instances": len(dev_tasks),
        "dev_families": len(dev_fam),
        "test_normal_instances": len(split_ids["test_normal"]),
        "test_normal_families": len(split_families["test_normal"]),
        "test_challenge_instances": len(split_ids["test_challenge"]),
        "test_challenge_families": len(split_families["test_challenge"]),
        "all_split_family_overlaps_zero": all(
            not (split_families[a] & split_families[b])
            for i, a in enumerate(split_families)
            for b in list(split_families)[i + 1:]
        ),
        "all_train_have_no_op_fail": all(x["no_op_fail"] > 0 for x in train_tasks),
        "all_dev_have_no_op_fail": all(x["no_op_fail"] > 0 for x in dev_tasks),
        "train_api_universe_size": len(train_api_universe),
        "dev_instances_all_primitives_seen": sum(
            frozenset(x["core_apis"]) <= train_api_universe for x in dev_tasks
        ),
        "dev_families_signature_invariant": sum(
            x["signature_invariant"] for x in dev_fam.values()
        ),
        "strict_composition_families": [x["family"] for x in strict],
        "strict_composition_family_count": len(strict),
        "selection_rule": (
            "Dev family has invariant API signature across its three scenarios; "
            "all target primitives occur in train; no single train family contains "
            "the target signature; <=3 train families can cover it."
        ),
        "boundary": (
            "Required-API cover is a structural feasibility proxy, not the final "
            "workflow decomposition. Final slots must be typed subprocedures with "
            "explicit I/O and public runtime checks."
        ),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "train_families.json").write_text(json.dumps(train_fam, indent=2), encoding="utf-8")
    (out / "dev_families.json").write_text(json.dumps(candidates, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    for x in strict:
        print(x["family"], x["best_cover"], "|", x["instructions"][0])

if __name__ == "__main__":
    main()
