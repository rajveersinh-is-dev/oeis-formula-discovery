"""
Unit tests for Convolution Recurrence Discovery.
"""

import math
from src.candidate.model import VerificationStatus
from src.discovery.convolution import ConvolutionRecurrenceDiscovery


def test_catalan_cauchy_convolution():
    """Catalan numbers satisfy a(n) = sum_{k=0}^{n-1} a(k)*a(n-1-k)."""
    cat = [math.comb(2 * n, n) // (n + 1) for n in range(16)]
    discovery = ConvolutionRecurrenceDiscovery()
    cands = discovery.discover("A000108", cat, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(k)*a(n-1-k)" in best.formula_str
    assert best.terms_tested == len(cat)


def test_motzkin_cauchy_convolution():
    """Motzkin numbers satisfy a(n) = a(n-1) + sum_{k=0}^{n-2} a(k)*a(n-2-k)."""
    motzkin = [1, 1]
    for n in range(2, 16):
        val = motzkin[-1] + sum(motzkin[k] * motzkin[n - 2 - k] for k in range(n - 1))
        motzkin.append(val)

    discovery = ConvolutionRecurrenceDiscovery()
    cands = discovery.discover("A001006", motzkin, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1)" in best.formula_str
    assert "a(n-2-k)" in best.formula_str
    assert best.terms_tested == len(motzkin)


def test_bell_binomial_convolution():
    """Bell numbers satisfy a(n) = sum_{k=0}^{n-1} binom(n-1, k)*a(k)."""
    # B(0)=1, B(1)=1, B(2)=2, B(3)=5, B(4)=15, B(5)=52, B(6)=203, B(7)=877, B(8)=4140
    bell = [1]
    for n in range(1, 14):
        val = sum(math.comb(n - 1, k) * bell[k] for k in range(n))
        bell.append(val)

    discovery = ConvolutionRecurrenceDiscovery()
    cands = discovery.discover("A000110", bell, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "binom(n-1, k)" in best.formula_str
    assert best.terms_tested == len(bell)
