"""
Unit tests for Rational and Bilinear Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.rational_recurrence import RationalRecurrenceDiscovery


def test_lyness_sequence():
    """Lyness sequence A001601: a(n) = (a(n-1) + 1) / a(n-2)."""
    lyness = [1, 2]
    for n in range(2, 25):
        lyness.append((lyness[-1] + 1) // lyness[-2])

    discovery = RationalRecurrenceDiscovery()
    cands = discovery.discover("A001601", lyness, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1) + 1" in best.formula_str
    assert "a(n-2)" in best.formula_str
    assert best.terms_tested == len(lyness)


def test_lyness_quadratic():
    """Quadratic Lyness recurrence: a(n) = (a(n-1)^2 + 2) / a(n-2)."""
    terms = [1, 1]
    for n in range(2, 16):
        terms.append((terms[-1] ** 2 + 2) // terms[-2])

    discovery = RationalRecurrenceDiscovery()
    cands = discovery.discover("LYNESS_Q", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1)^2" in best.formula_str
    assert "a(n-2)" in best.formula_str


def test_bilinear_affine_3():
    """Bilinear affine order 3 recurrence: a(n)*a(n-3) = a(n-1)*a(n-2) + 1."""
    terms = [1, 1, 1]
    for n in range(3, 16):
        terms.append((terms[-1] * terms[-2] + 1) // terms[-3])
    discovery = RationalRecurrenceDiscovery(max_order=4)
    cands = discovery.discover("BILINEAR_AFFINE_3", terms, start_index=0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n)*a(n-3)" in best.formula_str


def test_somos4_bilinear():
    """Somos-4 recurrence: a(n)*a(n-4) = a(n-1)*a(n-3) + a(n-2)^2."""
    terms = [1, 1, 1, 1]
    for n in range(4, 15):
        terms.append((terms[-1] * terms[-3] + terms[-2] ** 2) // terms[-4])
    discovery = RationalRecurrenceDiscovery(max_order=4)
    cands = discovery.discover("SOMOS4", terms, start_index=0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-2)^2" in best.formula_str


def test_rational_rejection():
    """Non-rational sequences like factorials must be rejected."""
    import math
    facts = [math.factorial(n) for n in range(12)]
    discovery = RationalRecurrenceDiscovery()
    cands = discovery.discover("A000142", facts, start_index=0)
    assert len(cands) == 0
