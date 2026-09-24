"""Trainable fast-state core for the Stream-JEV proposal.

This module intentionally operates on cached context/candidate embeddings.  It
does not load an LLM or perform network calls.  The event runner is responsible
for selected-only feedback, propensity validation, persistence and delayed
feedback ordering.  The module is a small candidate-permutation-safe scorer
plus a bounded gated state transition that can be meta-trained on short
streams.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Sequence, Tuple

import torch
from torch import Tensor, nn


@dataclass
class NeuralState:
    global_state: Tensor
    local_state: Dict[str, Tensor]


class StreamJEVCore(nn.Module):
    """Small trainable scorer and event-level fast-state transition.

    The encoder is outside this module.  ``context`` and candidate vectors must
    already be cached.  Candidate scores use shared weights and therefore do
    not depend on menu order.  ``update`` changes only the selected candidate
    and the shared regime state.
    """

    def __init__(
        self,
        context_dim: int,
        candidate_dim: int,
        state_dim: int = 32,
        hidden_dim: int = 64,
        max_gate: float = 0.25,
        max_state_norm: float = 10.0,
    ) -> None:
        super().__init__()
        if min(context_dim, candidate_dim, state_dim, hidden_dim) <= 0:
            raise ValueError("dimensions must be positive")
        if not (0.0 < max_gate <= 1.0) or max_state_norm <= 0:
            raise ValueError("invalid stability bounds")
        self.context_dim = context_dim
        self.candidate_dim = candidate_dim
        self.state_dim = state_dim
        self.max_gate = float(max_gate)
        self.max_state_norm = float(max_state_norm)
        pair_dim = context_dim + candidate_dim
        self.base = nn.Sequential(
            nn.Linear(pair_dim, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, 1)
        )
        self.residual = nn.Sequential(
            nn.Linear(pair_dim + 2 * state_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
        )
        # The update cell sees selected context/candidate, both fast states,
        # label, delay and propensity.  It is deliberately low-dimensional.
        update_dim = pair_dim + 2 * state_dim + 3
        self.global_cell = nn.Linear(update_dim, 2 * state_dim)
        self.local_cell = nn.Linear(update_dim, 2 * state_dim)
        self.gate = nn.Linear(update_dim, 2 * state_dim)

    def initial_state(self, device: torch.device | None = None) -> NeuralState:
        zeros = torch.zeros(self.state_dim, device=device)
        return NeuralState(global_state=zeros, local_state={})

    def _local(self, state: NeuralState, candidate_id: str, device: torch.device) -> Tensor:
        value = state.local_state.get(candidate_id)
        if value is None:
            return torch.zeros(self.state_dim, device=device)
        return value

    def score(
        self,
        context: Tensor,
        candidate_ids: Sequence[str],
        candidates: Tensor,
        state: NeuralState,
        posterior_logits: Tensor | None = None,
    ) -> Tensor:
        """Return one logit per candidate; candidate order is irrelevant."""
        if context.shape != (self.context_dim,):
            raise ValueError("context has the wrong shape")
        if candidates.ndim != 2 or candidates.shape[0] != len(candidate_ids):
            raise ValueError("candidate tensor/menu mismatch")
        if candidates.shape[1] != self.candidate_dim:
            raise ValueError("candidate vectors have the wrong dimension")
        if len(set(candidate_ids)) != len(candidate_ids) or not candidate_ids:
            raise ValueError("candidate ids must be unique and non-empty")
        local = torch.stack([
            self._local(state, cid, candidates.device) for cid in candidate_ids
        ])
        global_state = state.global_state.expand(len(candidate_ids), -1)
        context_rep = context.expand(len(candidate_ids), -1)
        pair = torch.cat([context_rep, candidates], dim=-1)
        logits = self.base(pair).squeeze(-1)
        residual_input = torch.cat([pair, global_state, local], dim=-1)
        logits = logits + torch.tanh(global_state.norm(dim=-1)) * self.residual(residual_input).squeeze(-1)
        if posterior_logits is not None:
            if posterior_logits.shape != (len(candidate_ids),):
                raise ValueError("posterior logits have the wrong shape")
            logits = logits + posterior_logits
        return logits

    def update(
        self,
        context: Tensor,
        candidate_id: str,
        candidate: Tensor,
        state: NeuralState,
        label: Tensor | float,
        delay: Tensor | float,
        propensity: Tensor | float,
    ) -> NeuralState:
        """Apply one feedback event to the selected candidate only.

        The gate and state norms are bounded in the transition itself.  The
        caller must still enforce that the event was actually selected and that
        its feedback has arrived.
        """
        if context.shape != (self.context_dim,) or candidate.shape != (self.candidate_dim,):
            raise ValueError("context/candidate has the wrong shape")
        label_t = torch.as_tensor(label, dtype=context.dtype, device=context.device).reshape(())
        delay_t = torch.as_tensor(delay, dtype=context.dtype, device=context.device).reshape(())
        prop_t = torch.as_tensor(propensity, dtype=context.dtype, device=context.device).reshape(())
        if not (bool((label_t >= 0).item()) and bool((label_t <= 1).item())):
            raise ValueError("label must be in [0,1]")
        if not bool((prop_t > 0).item()) or not bool((prop_t <= 1).item()):
            raise ValueError("propensity must be in (0,1]")
        local = self._local(state, candidate_id, context.device)
        update_input = torch.cat([
            context,
            candidate,
            state.global_state,
            local,
            label_t.reshape(1),
            torch.log1p(delay_t).reshape(1),
            torch.clamp(1.0 / prop_t, max=20.0).reshape(1),
        ])
        gate = torch.sigmoid(self.gate(update_input)).clamp(max=self.max_gate)
        g_candidate, g_global = gate.chunk(2)
        new_global = (1.0 - g_global) * state.global_state + g_global * torch.tanh(
            self.global_cell(update_input).chunk(2)[1]
        )
        new_local = (1.0 - g_candidate) * local + g_candidate * torch.tanh(
            self.local_cell(update_input).chunk(2)[1]
        )
        # Norm projection is part of the forward transition and makes the
        # stability guard independent of optimizer settings.
        new_global = self._project(new_global)
        new_local = self._project(new_local)
        next_local = dict(state.local_state)
        next_local[candidate_id] = new_local
        return NeuralState(global_state=new_global, local_state=next_local)

    def _project(self, value: Tensor) -> Tensor:
        norm = value.norm()
        scale = torch.clamp(self.max_state_norm / (norm + 1e-12), max=1.0)
        return value * scale

