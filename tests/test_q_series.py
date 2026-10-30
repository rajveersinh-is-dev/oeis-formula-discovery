"""
Unit tests for q-Series and Basic Hypergeometric Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.q_series import QSeriesDiscovery


def test_q_factorials_discovery():
    """A005329: [n]_2! q-factorial sequence: a(n) = (2^n - 1)*a(n-1)."""
    t = [1]
    for n in range(1, 14):
        t.append(t[-1] * (2 ** n - 1))

    discovery = QSeriesDiscovery()
    cands = discovery.discover("A005329", t, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "2^n - 1" in best.formula_str
    assert best.terms_tested == len(t)


def test_q_powers_dilation():
    """a(n) = 3^n * a(n-1) generating 3^{n(n+1)/2}."""
    t = [1]
    for n in range(1, 10):
        t.append(t[-1] * (3 ** n))

    discovery = QSeriesDiscovery()
    cands = discovery.discover("Q_POW3", t, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "3^n" in best.formula_str


def test_second_order_q_fibonacci():
    """q-Fibonacci / Schur recurrence: a(n) = a(n-1) + 2^n * a(n-2)."""
    t = [1, 1]
    for n in range(2, 12):
        t.append(t[-1] + (2 ** n) * t[-2])

    discovery = QSeriesDiscovery()
    cands = discovery.discover("Q_FIB", t, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "2^n" in best.formula_str
