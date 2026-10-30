"""
Unit tests for Inhomogeneous Linear Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.inhomogeneous import InhomogeneousRecurrenceDiscovery


def test_tower_of_hanoi_recurrence():
    """Tower of Hanoi A000225: a(n) = 2*a(n-1) + 1."""
    # a(1)=1, a(2)=3, a(3)=7, a(4)=15, a(5)=31, a(6)=63, a(7)=127, a(8)=255
    terms = [2**n - 1 for n in range(1, 15)]
    discovery = InhomogeneousRecurrenceDiscovery(max_order=2, max_poly_deg=1)
    cands = discovery.discover("A000225", terms, start_index=1)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "2*a(n-1)" in best.formula_str
    assert "1" in best.formula_str
    assert best.terms_tested == len(terms)


def test_lazy_caterer_recurrence():
    """Lazy Caterer sequence A000124: a(n) = a(n-1) + n."""
    # a(0)=1, a(1)=2, a(2)=4, a(3)=7, a(4)=11, a(5)=16, a(6)=22, a(7)=29
    terms = [(n * (n + 1)) // 2 + 1 for n in range(15)]
    discovery = InhomogeneousRecurrenceDiscovery(max_order=2, max_poly_deg=1)
    cands = discovery.discover("A000124", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1)" in best.formula_str
    assert "n" in best.formula_str
    assert best.terms_tested == len(terms)


def test_cake_numbers_recurrence():
    """Cake numbers A000125: a(n) = a(n-1) + n*(n-1)/2 + 1."""
    terms = [(n**3 + 5 * n + 6) // 6 for n in range(15)]
    discovery = InhomogeneousRecurrenceDiscovery(max_order=1, max_poly_deg=2)
    cands = discovery.discover("A000125", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n-1)" in best.formula_str
    assert best.terms_tested == len(terms)


def test_exponential_driving_term():
    """Inhomogeneous recurrence with exponential driving term: a(n) = 2*a(n-1) + 3^n."""
    terms = [1]
    for n in range(1, 16):
        terms.append(2 * terms[-1] + 3**n)

    discovery = InhomogeneousRecurrenceDiscovery(max_order=2, max_poly_deg=2)
    cands = discovery.discover("EXP_INHOM", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "^n" in best.formula_str
    assert best.terms_tested == len(terms)


def test_dynamic_exponential_driving_term_7():
    """Inhomogeneous recurrence with base-7 driving term: a(n) = 3*a(n-1) + 7^n."""
    terms = [1]
    for n in range(1, 16):
        terms.append(3 * terms[-1] + 7**n)

    discovery = InhomogeneousRecurrenceDiscovery(max_order=2, max_poly_deg=2)
    cands = discovery.discover("EXP_INHOM_7", terms, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "7^n" in best.formula_str or "3^n" in best.formula_str


