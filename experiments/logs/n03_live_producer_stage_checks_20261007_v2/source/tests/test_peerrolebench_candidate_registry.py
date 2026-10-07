from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_candidate_registry import (  # noqa: E402
    CandidateRegistryEntry,
    candidate_refs,
    registry_digest,
    validate_registry,
)


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def entries():
    return [
        CandidateRegistryEntry("agent-b", "v2", DIGEST_B, "internal/model-b", DIGEST_A),
        CandidateRegistryEntry("agent-a", "v1", DIGEST_A, "internal/model-a", DIGEST_B),
    ]


def test_registry_is_canonical_and_resolves_sidecar_versions():
    ordered = validate_registry(entries(), expected_ids=("agent-a", "agent-b"))
    assert [item.candidate_id for item in ordered] == ["agent-a", "agent-b"]
    assert [ref.key for ref in candidate_refs(("agent-b", "agent-a"), ordered)] == ["agent-b@v2", "agent-a@v1"]
    assert registry_digest(entries()) == registry_digest(list(reversed(entries())))


def test_registry_rejects_duplicates_and_unregistered_ids():
    with pytest.raises(ValueError, match="IDs must be unique"):
        validate_registry(entries() + [entries()[0]])
    with pytest.raises(ValueError, match="not pre-registered"):
        candidate_refs(("agent-c",), entries())


def test_registry_rejects_invalid_or_changed_identity_fields():
    with pytest.raises(ValueError, match="source_digest"):
        CandidateRegistryEntry("agent-a", "v1", "not-a-digest", "internal/model-a", DIGEST_B)
    old = registry_digest(entries())
    changed = [*entries()]
    changed[0] = CandidateRegistryEntry("agent-b", "v3", DIGEST_B, "internal/model-b", DIGEST_A)
    assert registry_digest(changed) != old
