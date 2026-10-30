import pytest
from src.candidate.model import VerificationStatus
from src.discovery.quasipolynomial import QuasipolynomialDiscovery


def test_quarter_squares():
    """Quarter squares A002620: floor(n^2 / 4). Quasipolynomial of period 2."""
    qd = QuasipolynomialDiscovery()
    terms = [n**2 // 4 for n in range(30)]
    cands = qd.discover("A002620", terms, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["period"] == 2
    assert best.details["max_degree"] == 2
    assert best.terms_tested == len(terms)
    # Check evaluator
    assert best.evaluator(10) == 10**2 // 4 == 25
    assert best.evaluator(11) == 11**2 // 4 == 30


def test_floor_division_linear_quasipoly():
    """Linear quasipolynomial: floor(n / 2) + 1."""
    qd = QuasipolynomialDiscovery()
    terms = [n // 2 + 1 for n in range(25)]
    cands = qd.discover("TEST_QP_LIN", terms, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["period"] == 2
    assert best.details["max_degree"] == 1


def test_period_3_quasipolynomial():
    """Period 3 quasipolynomial:
    a(3k) = k^2, a(3k+1) = 2*k + 1, a(3k+2) = 3*k^2 + 5.
    """
    qd = QuasipolynomialDiscovery()
    terms = []
    for n in range(30):
        k = n // 3
        r = n % 3
        if r == 0:
            terms.append(k**2)
        elif r == 1:
            terms.append(2 * k + 1)
        else:
            terms.append(3 * k**2 + 5)

    cands = qd.discover("TEST_QP_P3", terms, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.details["period"] == 3
    assert best.details["max_degree"] == 2

