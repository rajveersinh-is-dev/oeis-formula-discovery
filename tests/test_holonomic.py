import math
import pytest
from src.candidate.model import VerificationStatus
from src.discovery.holonomic import HolonomicDiscovery


def test_catalan_holonomic_recurrence():
    """Catalan numbers A000108: (n+1)*C(n) - 2*(2n-1)*C(n-1) = 0."""
    hd = HolonomicDiscovery()
    catalan = [math.comb(2 * n, n) // (n + 1) for n in range(25)]
    cands = hd.discover("A000108", catalan, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["order"] == 1
    assert best.details["max_degree"] == 1
    # Check that it verified across all 25 terms
    assert best.terms_tested == len(catalan)


def test_motzkin_holonomic_recurrence():
    """Motzkin numbers A001006: (n+2)*M(n) - (2n+1)*M(n-1) - 3(n-1)*M(n-2) = 0."""
    hd = HolonomicDiscovery()
    motzkin = []
    for n in range(25):
        val = sum((math.comb(2 * k, k) // (k + 1)) * math.comb(n, 2 * k) for k in range(n // 2 + 1))
        motzkin.append(val)

    cands = hd.discover("A001006", motzkin, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["order"] == 2
    assert best.details["max_degree"] == 1
    assert best.terms_tested == len(motzkin)


def test_central_delannoy_holonomic():
    """Central Delannoy numbers A001850: n*D(n) - (6n-3)*D(n-1) + (n-1)*D(n-2) = 0."""
    hd = HolonomicDiscovery()
    delannoy = []
    for n in range(25):
        val = sum(math.comb(n, k) * math.comb(n + k, k) for k in range(n + 1))
        delannoy.append(val)

    cands = hd.discover("A001850", delannoy, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["order"] == 2
    assert best.details["max_degree"] == 1


def test_subfactorials_derangements():
    """Derangements A000166: !n = (n-1)*(!(n-1) + !(n-2))."""
    hd = HolonomicDiscovery()
    # Derangements: !0=1, !1=0, !2=1, !3=2, !4=9, !5=44, !6=265, !7=1854, !8=14833
    derangements = [1, 0]
    for n in range(2, 22):
        derangements.append((n - 1) * (derangements[-1] + derangements[-2]))

    cands = hd.discover("A000166", derangements, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH


def test_apery_numbers_zeta3():
    """Apery numbers for zeta(3) A005259: order 2, degree 3 polynomial recurrence."""
    hd = HolonomicDiscovery()
    apery = []
    for n in range(25):
        val = sum(math.comb(n, k)**2 * math.comb(n + k, k)**2 for k in range(n + 1))
        apery.append(val)

    cands = hd.discover("A005259", apery, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["order"] == 2
    assert best.details["max_degree"] == 3
    assert best.terms_tested == len(apery)

