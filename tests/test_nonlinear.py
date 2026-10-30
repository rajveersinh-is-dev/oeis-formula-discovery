"""
Unit tests for Nonlinear and Bilinear Recurrence Discovery.
Tests:
- Sylvester's sequence (A000058): a(n) = a(n-1)^2 - a(n-1) + 1
- Tree height sequence (A001699): a(n) = a(n-1)^2 + 1
- Somos-4 (A006720): a(n)*a(n-4) = a(n-1)*a(n-3) + a(n-2)^2
- Somos-5 (A006721): a(n)*a(n-5) = a(n-1)*a(n-4) + a(n-2)*a(n-3)
- Non-matching sequence rejection
"""

from src.candidate.model import VerificationStatus
from src.discovery.nonlinear import NonlinearRecurrenceDiscovery


def test_sylvesters_sequence():
    """Sylvester's sequence A000058: a(n) = a(n-1)^2 - a(n-1) + 1."""
    sylvester = [2, 3, 7, 43, 1807, 3263443, 10650056950807]
    discovery = NonlinearRecurrenceDiscovery(max_degree=3)
    cands = discovery.discover("A000058", sylvester, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1)^2 - a(n-1) + 1" in best.formula_str
    assert best.terms_tested == len(sylvester)


def test_tree_height_recurrence():
    """A001699: a(n) = a(n-1)^2 + 1."""
    terms = [1, 2, 5, 26, 677, 458330, 210066388901]
    discovery = NonlinearRecurrenceDiscovery(max_degree=2)
    cands = discovery.discover("A001699", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1)^2 + 1" in best.formula_str
    assert best.terms_tested == len(terms)


def test_somos_4_recurrence():
    """Somos-4 A006720: a(n)*a(n-4) = a(n-1)*a(n-3) + a(n-2)^2."""
    somos4 = [1, 1, 1, 1, 2, 3, 7, 23, 59, 314, 1529, 8209, 83313, 620297, 7869898]
    discovery = NonlinearRecurrenceDiscovery(max_somos_k=6)
    cands = discovery.discover("A006720", somos4, start_index=0)

    assert len(cands) >= 1
    best = [c for c in cands if c.details.get("type") == "somos_bilinear"][0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n)*a(n-4) = a(n-1)*a(n-3) + a(n-2)^2" in best.formula_str
    assert best.terms_tested == len(somos4)


def test_somos_5_recurrence():
    """Somos-5 A006721: a(n)*a(n-5) = a(n-1)*a(n-4) + a(n-2)*a(n-3)."""
    somos5 = [1, 1, 1, 1, 1, 2, 3, 5, 11, 37, 83, 274, 1217, 6161, 22833]
    discovery = NonlinearRecurrenceDiscovery(max_somos_k=6)
    cands = discovery.discover("A006721", somos5, start_index=0)

    assert len(cands) >= 1
    best = [c for c in cands if c.details.get("type") == "somos_bilinear"][0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n)*a(n-5) = a(n-1)*a(n-4) + a(n-2)*a(n-3)" in best.formula_str
    assert best.terms_tested == len(somos5)


def test_prime_numbers_rejection():
    """Primes cannot satisfy low-degree polynomial map or Somos recurrence."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    discovery = NonlinearRecurrenceDiscovery()
    cands = discovery.discover("A000040", primes, start_index=1)
    assert len(cands) == 0
