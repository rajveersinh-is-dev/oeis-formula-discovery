"""
Unit tests for Continued Fraction Convergent Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.continued_fraction import ContinuedFractionDiscovery


def test_bessel_continued_fraction():
    """Bessel / tan(1) convergents A001517: a(n) = n*a(n-1) + a(n-2)."""
    bessel = [1, 1]
    for n in range(2, 20):
        bessel.append(n * bessel[-1] + bessel[-2])

    discovery = ContinuedFractionDiscovery()
    cands = discovery.discover("A001517", bessel, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "n" in best.formula_str
    assert "a(n-1)" in best.formula_str
    assert "a(n-2)" in best.formula_str
    assert best.terms_tested == len(bessel)


def test_e_convergents_numerators():
    """Numerators of convergents to e (A007676)."""
    a_cf = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12]
    p = [a_cf[0], a_cf[0] * a_cf[1] + 1]
    for i in range(2, len(a_cf)):
        p.append(a_cf[i] * p[-1] + p[-2])

    discovery = ContinuedFractionDiscovery()
    cands = discovery.discover("A007676", p, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "q(3k+0)=2k+2" in best.formula_str
    assert best.terms_tested == len(p)


def test_e_convergents_denominators():
    """Denominators of convergents to e (A007677)."""
    a_cf = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12]
    q = [1, a_cf[1]]
    for i in range(2, len(a_cf)):
        q.append(a_cf[i] * q[-1] + q[-2])

    discovery = ContinuedFractionDiscovery()
    cands = discovery.discover("A007677", q, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "q(3k+0)=2k+2" in best.formula_str
    assert best.terms_tested == len(q)


def test_periodic_continued_fraction():
    """Continued fraction with period 2 partial quotients [1, 3, 1, 3, ...]."""
    cycle = [1, 3]
    terms = [1, 2]
    for i in range(2, 20):
        q = cycle[(i - 2) % 2]
        terms.append(q * terms[-1] + terms[-2])

    discovery = ContinuedFractionDiscovery()
    cands = discovery.discover("CF_PER2", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "[1, 3]" in best.formula_str


def test_continued_fraction_rejection():
    """Squares n^2 cannot be formed by continued fraction quotients with a(n-1) dividing a(n)-a(n-2)."""
    squares = [n**2 for n in range(1, 25)]
    discovery = ContinuedFractionDiscovery()
    cands = discovery.discover("A000290", squares, start_index=1)
    assert len(cands) == 0
