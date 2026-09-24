import torch

from neural_fast_state import StreamJEVCore


def test_neural_scorer_is_menu_order_safe_and_state_is_selected_only():
    torch.manual_seed(0)
    model = StreamJEVCore(context_dim=3, candidate_dim=2, state_dim=4, hidden_dim=8)
    context = torch.randn(3)
    candidates = torch.randn(2, 2)
    state = model.initial_state()
    logits_ab = model.score(context, ["a", "b"], candidates, state)
    logits_ba = model.score(context, ["b", "a"], candidates.flip(0), state)
    assert torch.allclose(logits_ab, logits_ba.flip(0))
    next_state = model.update(context, "a", candidates[0], state, 1.0, 0.0, 1.0)
    assert "a" in next_state.local_state
    assert "b" not in next_state.local_state
    assert next_state.global_state.norm() <= model.max_state_norm + 1e-6


def test_neural_gate_and_state_bound_hold_under_extreme_feedback():
    torch.manual_seed(1)
    model = StreamJEVCore(context_dim=2, candidate_dim=2, state_dim=8, hidden_dim=8,
                          max_gate=0.1, max_state_norm=0.5)
    context = torch.full((2,), 1000.0)
    candidate = torch.full((2,), -1000.0)
    state = model.initial_state()
    for _ in range(20):
        state = model.update(context, "x", candidate, state, 1.0, 10000.0, 0.01)
    assert state.global_state.norm() <= 0.500001
    assert state.local_state["x"].norm() <= 0.500001
