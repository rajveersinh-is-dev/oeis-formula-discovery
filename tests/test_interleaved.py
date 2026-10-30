"""
Unit tests for Interleaved and Multisection Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.interleaved import InterleavedRecurrenceDiscovery


def test_interleaved_geometric_progressions():
    """Interleaved powers of 2 and 3: a(2k) = 2^k, a(2k+1) = 3^k."""
    terms = []
    for k in range(16):
        terms.append(2**k)
        terms.append(3**k)

    discovery = InterleavedRecurrenceDiscovery(periods=[2, 3])
    cands = discovery.discover("INTERLEAVED_2_3", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*k) = 2*a(2*(k-1))" in best.formula_str
    assert "a(2*k + 1) = 3*a(2*(k-1) + 1)" in best.formula_str
    assert best.terms_tested == len(terms)


def test_interleaved_period_3():
    """Interleaved branches of period 3."""
    terms = []
    for k in range(12):
        terms.append(2 * k + 1)       # branch 0: step 2 (LR: 2*s(k-1) - s(k-2))
        terms.append(2**k)            # branch 1: geometric 2^k
        terms.append(3**k)            # branch 2: geometric 3^k

    discovery = InterleavedRecurrenceDiscovery(periods=[2, 3])
    cands = discovery.discover("INTERLEAVED_P3", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(3*k)" in best.formula_str
    assert "a(3*k + 1)" in best.formula_str
    assert "a(3*k + 2)" in best.formula_str


def test_interleaved_offset_1():
    """Interleaved sequence starting at index 1: odd terms are 2^k, even terms are 3^k."""
    # a(1) = 2, a(2) = 3, a(3) = 4, a(4) = 9, a(5) = 8, a(6) = 27
    terms = []
    for k in range(1, 16):
        terms.append(2**k)
        terms.append(3**k)

    discovery = InterleavedRecurrenceDiscovery(periods=[2])
    cands = discovery.discover("INTERLEAVED_OFFSET_1", terms, start_index=1)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    # Even index a(2k) is 3^k: a(2*k) = 3*a(2*(k-1))
    assert "a(2*k) = 3*a(2*(k-1))" in best.formula_str
    # Odd index a(2k+1) is 2^k: a(2*k + 1) = 2*a(2*(k-1) + 1)
    assert "a(2*k + 1) = 2*a(2*(k-1) + 1)" in best.formula_str


def test_interleaved_rejection():
    """Pure prime sequence cannot satisfy interleaved linear recurrence."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    discovery = InterleavedRecurrenceDiscovery()
    cands = discovery.discover("A000040", primes, start_index=1)
    assert len(cands) == 0
