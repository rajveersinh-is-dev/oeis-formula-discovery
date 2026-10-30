"""
Unit tests for Algebraic Generating Function Discovery (Hermite-Padé).
"""

import math
from src.candidate.model import VerificationStatus
from src.discovery.algebraic_gf import AlgebraicGeneratingFunctionDiscovery


def test_catalan_algebraic_generating_function():
    """Catalan numbers A000108: x*G(x)^2 - G(x) + 1 = 0."""
    cat = [math.comb(2 * n, n) // (n + 1) for n in range(16)]
    discovery = AlgebraicGeneratingFunctionDiscovery(max_degree=2)
    cands = discovery.discover("A000108", cat, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "G(x)^2" in best.formula_str
    assert "G(x)" in best.formula_str
    assert best.details["poly_a2"] == [0, 1]  # x
    assert best.details["poly_a1"] == [-1]    # -1
    assert best.details["poly_a0"] == [1]     # 1


def test_motzkin_algebraic_generating_function():
    """Motzkin numbers A001006: x^2*G(x)^2 + (x - 1)*G(x) + 1 = 0."""
    motzkin = [1, 1]
    for n in range(2, 18):
        val = motzkin[-1] + sum(motzkin[k] * motzkin[n - 2 - k] for k in range(n - 1))
        motzkin.append(val)

    discovery = AlgebraicGeneratingFunctionDiscovery(max_degree=2)
    cands = discovery.discover("A001006", motzkin, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "G(x)^2" in best.formula_str
    assert best.details["poly_a2"] == [0, 0, 1]  # x^2
    assert best.details["poly_a1"] == [-1, 1]    # -1 + x
    assert best.details["poly_a0"] == [1]        # 1


def test_large_schroder_algebraic_generating_function():
    """Large Schröder numbers A006318: x*G(x)^2 + (x - 1)*G(x) + 1 = 0."""
    # S(0)=1, S(1)=2, S(2)=6, S(3)=22, S(4)=90, S(5)=394, S(6)=1806
    schroder = [1, 2, 6, 22, 90, 394, 1806, 8558, 41586, 206098, 1037718]
    discovery = AlgebraicGeneratingFunctionDiscovery(max_degree=2)
    cands = discovery.discover("A006318", schroder, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "G(x)^2" in best.formula_str


def test_ternary_trees_algebraic_generating_function():
    """Ternary trees / 3-Catalan A001764: x*G(x)^3 - G(x) + 1 = 0."""
    t3 = [math.comb(3 * n, n) // (2 * n + 1) for n in range(16)]
    discovery = AlgebraicGeneratingFunctionDiscovery(max_degree=4)
    cands = discovery.discover("A001764", t3, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "G(x)^3" in best.formula_str
    assert "x*G(x)^3 - G(x) + 1 = 0" in best.formula_str
    assert best.terms_tested == len(t3)


def test_4ary_trees_algebraic_generating_function():
    """4-ary trees / 4-Catalan A002293: x*G(x)^4 - G(x) + 1 = 0."""
    t4 = [math.comb(4 * n, n) // (3 * n + 1) for n in range(16)]
    discovery = AlgebraicGeneratingFunctionDiscovery(max_degree=4)
    cands = discovery.discover("A002293", t4, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "G(x)^4" in best.formula_str
    assert "x*G(x)^4 - G(x) + 1 = 0" in best.formula_str
    assert best.terms_tested == len(t4)

