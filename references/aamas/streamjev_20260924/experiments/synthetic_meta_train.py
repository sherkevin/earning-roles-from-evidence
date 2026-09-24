"""Small synthetic stream falsification test for the trainable fast state.

This is deliberately not a paper benchmark.  It tests one narrow claim: after
a hidden regime switch, a selected-only feedback update can recover faster than
the same scorer with its fast state disabled.  All predictions and sampled
feedback are written to JSONL by the caller in the experiment log.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from neural_fast_state import StreamJEVCore


def run_episode(model, train: bool, horizon: int = 50, switch_at: int = 20, trace=None):
    # No context signal reveals the regime; only selected outcomes can reveal it.
    context = torch.zeros(4)
    candidates = torch.eye(3, 3)
    p_before = torch.tensor([0.82, 0.18, 0.18])
    p_after = torch.tensor([0.18, 0.82, 0.18])
    state = model.initial_state()
    pending = []
    losses, rewards, post_switch_rewards = [], [], []
    for t in range(horizon):
        if train:
            arrived = [event for event in pending if event["arrival"] == t]
            pending = [event for event in pending if event["arrival"] != t]
            for event in arrived:
                state = model.update(
                    context, event["candidate_id"], candidates[event["action"]], state,
                    label=event["label"], delay=event["delay"], propensity=event["propensity"],
                )
                if trace is not None:
                    trace.append({"t": t, "event_type": "feedback_arrived", **event})
        truth = p_before if t < switch_at else p_after
        ids = ["a", "b", "c"]
        logits = model.score(context, ids, candidates, state)
        probs = torch.softmax(logits, dim=-1)
        oracle = int(torch.argmax(truth).item())
        losses.append(-torch.log(probs[oracle] + 1e-8))
        action = int(torch.multinomial(probs.detach(), 1).item())
        label = float(torch.bernoulli(truth[action]).item())
        rewards.append(label)
        if t >= switch_at:
            post_switch_rewards.append(label)
        delay = float(t % 4)
        feedback = {
            "source_t": t,
            "candidate_id": ids[action],
            "action": action,
            "label": label,
            "delay": delay,
            "propensity": float(probs[action].detach().item()),
            # A zero-delay label becomes visible at the next decision boundary.
            "arrival": t + max(1, int(delay)),
        }
        if train:
            pending.append(feedback)
        if trace is not None:
            trace.append({"t": t, "event_type": "decision", "action": action,
                          "candidate_id": ids[action], "label_hidden": True,
                          "propensity": feedback["propensity"], "feedback_arrival": feedback["arrival"]})
    return torch.stack(losses).mean(), float(np.mean(rewards)), float(np.mean(post_switch_rewards))


def main(out_dir: str):
    random.seed(7)
    np.random.seed(7)
    torch.manual_seed(7)
    model = StreamJEVCore(context_dim=4, candidate_dim=3, state_dim=8, hidden_dim=32,
                          max_gate=0.25, max_state_norm=4.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-3)
    train_rows = []
    event_rows = []
    for episode in range(160):
        optimizer.zero_grad(set_to_none=True)
        trace = []
        loss, reward, post = run_episode(model, train=True, trace=trace)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        train_rows.append({"episode": episode, "loss": float(loss.detach()), "reward": reward, "post_switch_reward": post})
        event_rows.extend({"episode": episode, **row} for row in trace)

    # Compare the trained model with and without applying the event update.
    eval_adapt, eval_frozen = [], []
    for episode in range(80):
        _, reward, post = run_episode(model, train=True)
        eval_adapt.append({"reward": reward, "post_switch_reward": post})
        _, reward, post = run_episode(model, train=False)
        eval_frozen.append({"reward": reward, "post_switch_reward": post})
    result = {
        "experiment_id": "synthetic_meta_train_20260924",
        "seed": 7,
        "train_episodes": 160,
        "eval_episodes": 80,
        "horizon": 50,
        "switch_at": 20,
        "adaptive_mean_reward": float(np.mean([r["reward"] for r in eval_adapt])),
        "adaptive_post_switch_reward": float(np.mean([r["post_switch_reward"] for r in eval_adapt])),
        "frozen_mean_reward": float(np.mean([r["reward"] for r in eval_frozen])),
        "frozen_post_switch_reward": float(np.mean([r["post_switch_reward"] for r in eval_frozen])),
        "interpretation": "Synthetic hidden-regime smoke only; it tests adaptation direction, not real-data quality.",
    }
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "synthetic_meta_train_20260924_raw.jsonl").write_text(
        "\n".join(json.dumps(r) for r in event_rows) + "\n", encoding="utf-8"
    )
    (out / "synthetic_meta_train_20260924_episode_metrics.jsonl").write_text(
        "\n".join(json.dumps(r) for r in train_rows) + "\n", encoding="utf-8"
    )
    (out / "synthetic_meta_train_20260924_results.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main("references/aamas/streamjev_20260924/experiments/logs")
