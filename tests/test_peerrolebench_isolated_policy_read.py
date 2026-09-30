from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_isolated_policy_read import read_profiles_isolated  # noqa: E402
from peerrolebench_isolated_policy_read_qualification import offer  # noqa: E402


def test_isolated_reader_returns_digest_bound_trace():
    sealed = offer()
    trace = read_profiles_isolated(sealed, ("profile-a-r1",), read_cut=2)
    assert trace.isolated is True
    assert trace.offer_digest == sealed.offer_digest
    assert trace.profile_ids == ("profile-a-r1",)


def test_isolated_reader_rejects_read_before_profile_available():
    with pytest.raises(ValueError):
        read_profiles_isolated(offer(), ("profile-a-r1",), read_cut=0)
