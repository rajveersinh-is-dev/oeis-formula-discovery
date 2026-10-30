"""
Unit tests for Multiplicative Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.multiplicative import MultiplicativeRecurrenceDiscovery


def test_fibonacci_multiplicative_recurrence():
    """a(n) = a(n-1) * a(n-2) with a(0)=2, a(1)=3."""
    # 2, 3, 6, 18, 108, 1944, 209952, 408146688
    terms = [2, 3]
    for _ in range(8):
        terms.append(terms[-1] * terms[-2])

    discovery = MultiplicativeRecurrenceDiscovery(max_power=2)
    cands = discovery.discover("SYN_MULT", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1) * a(n-2)" in best.formula_str
    assert best.terms_tested == len(terms)


def test_multiplicative_with_scale():
    """a(n) = 2 * a(n-1) * a(n-2) with a(0)=1, a(1)=1."""
    # 1, 1, 2, 4, 16, 128, 4096, 1048576
    terms = [1, 1]
    for _ in range(7):
        terms.append(2 * terms[-1] * terms[-2])

    discovery = MultiplicativeRecurrenceDiscovery(max_power=2)
    cands = discovery.discover("SYN_MULT2", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "2 * a(n-1) * a(n-2)" in best.formula_str
    assert best.terms_tested == len(terms)

