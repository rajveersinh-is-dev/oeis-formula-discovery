import pytest
from src.discovery.linear_recurrence import LinearRecurrenceDiscovery
from src.candidate.model import VerificationStatus


def test_fibonacci_recurrence():
    lr = LinearRecurrenceDiscovery(max_order=5)
    # Fibonacci: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144
    terms = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    cands = lr.discover("A000045", terms, 0)
    assert len(cands) == 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.recurrence_coeffs == [1, 1]  # a(n) = a(n-1) + a(n-2)


def test_pell_recurrence():
    lr = LinearRecurrenceDiscovery(max_order=5)
    # Pell: 0, 1, 2, 5, 12, 29, 70, 169, 408, 985, 2378
    terms = [0, 1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741]
    cands = lr.discover("A000129", terms, 0)
    assert len(cands) == 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert best.recurrence_coeffs == [2, 1]  # a(n) = 2*a(n-1) + a(n-2)
