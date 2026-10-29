import pytest
from src.discovery.finite_differences import FiniteDifferenceDiscovery
from src.candidate.model import VerificationStatus


def test_constant_sequence():
    fd = FiniteDifferenceDiscovery()
    terms = [7, 7, 7, 7, 7, 7, 7]
    cands = fd.discover("TEST01", terms, 0)
    assert len(cands) == 1
    assert cands[0].formula_str == "a(n) = 7"
    assert cands[0].verification_status == VerificationStatus.EXACT_MATCH


def test_linear_polynomial():
    fd = FiniteDifferenceDiscovery()
    terms = [3 * n + 5 for n in range(15)]
    cands = fd.discover("TEST02", terms, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.evaluator(10) == 35


def test_quadratic_polynomial():
    fd = FiniteDifferenceDiscovery()
    terms = [n**2 + 3 * n + 5 for n in range(15)]
    cands = fd.discover("TEST03", terms, 0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.evaluator(10) == 10**2 + 3 * 10 + 5


def test_offset_handling():
    fd = FiniteDifferenceDiscovery()
    # Sequence defined starting from n = 3: a(n) = n^2
    start_n = 3
    terms = [n**2 for n in range(start_n, start_n + 15)]
    cands = fd.discover("TEST04", terms, start_n)
    assert len(cands) >= 1
    best = cands[0]
    assert best.evaluator(10) == 100
