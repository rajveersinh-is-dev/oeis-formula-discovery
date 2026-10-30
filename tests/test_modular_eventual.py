"""
Unit tests for Eventual Modular Periodicity.
"""

from src.candidate.model import VerificationStatus
from src.discovery.modular import ModularPatternDiscovery


def test_eventual_periodicity_with_transient():
    """Sequence with transient [5, 9, 4] followed by period [1, 2, 3]: [5, 9, 4, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]."""
    transient = [5, 9, 4]
    cycle = [1, 2, 3]
    terms = list(transient) + cycle * 4  # 15 terms total

    discovery = ModularPatternDiscovery(max_period=6, max_transient=4)
    cands = discovery.discover("TEST_MOD_TRANS", terms, start_index=0)

    assert len(cands) >= 1
    exact_cands = [c for c in cands if c.verification_status == VerificationStatus.EXACT_MATCH]
    assert len(exact_cands) >= 1
    best = exact_cands[0]
    assert best.details["transient"] == 3
    assert best.details["period"] == 3
    assert best.details["pattern"] == [1, 2, 3]

    # Test that evaluator reproduces all terms including transient!
    for i, t in enumerate(terms):
        assert best.evaluator(i) == t

