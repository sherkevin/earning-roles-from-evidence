import json

for method in ["fixed_static_roles", "fixed_self_claim"]:
    path = f"artifacts/round2_gpt41mini_fullval/run_20260414_135408/{method}/_ckpt_preds.jsonl"
    try:
        preds = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    except FileNotFoundError:
        print(f"{method}: not found"); continue
    f1s = [p.get("answer_f1", 0.0) for p in preds]
    zero_f1 = sum(1 for f in f1s if f == 0.0)
    mean_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    print(f"{method}: {len(preds)} samples, F1=0 count={zero_f1} ({100*zero_f1/len(preds):.1f}%), mean_f1={mean_f1:.4f}")

# Check raw_model_outputs for gpt-5.1 occurrence counts
for method in ["fixed_static_roles", "fixed_self_claim"]:
    path = f"artifacts/round2_gpt41mini_fullval/run_20260414_135408/{method}/raw_model_outputs.jsonl"
    try:
        total = err = 0
        for line in open(path, encoding="utf-8"):
            if not line.strip(): continue
            total += 1
            if "gpt-5.1" in line or "not supported" in line:
                err += 1
        print(f"{method} raw_outputs: {total} entries, gpt-5.1 errors={err} ({100*err/total:.1f}%)")
    except FileNotFoundError:
        print(f"{method} raw_outputs: not found")
