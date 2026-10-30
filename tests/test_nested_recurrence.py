"""
Unit tests for Nested and Meta-Fibonacci Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.nested_recurrence import NestedRecurrenceDiscovery


def test_hofstadter_q_sequence():
    """Hofstadter Q-sequence A005185: a(n) = a(n - a(n-1)) + a(n - a(n-2))."""
    q = [1, 1]
    for n in range(3, 35):
        q.append(q[n - 1 - q[-1]] + q[n - 1 - q[-2]])

    discovery = NestedRecurrenceDiscovery()
    cands = discovery.discover("A005185", q, start_index=1)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n - a(n-1)) + a(n - a(n-2))" in best.formula_str
    assert best.terms_tested == len(q)


def test_hofstadter_conway_sequence():
    """Hofstadter-Conway $10000 sequence A004001: a(n) = a(a(n-1)) + a(n - a(n-1))."""
    conway = [1, 1]
    for n in range(3, 35):
        conway.append(conway[conway[-1] - 1] + conway[n - 1 - conway[-1]])

    discovery = NestedRecurrenceDiscovery()
    cands = discovery.discover("A004001", conway, start_index=1)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(a(n-1)) + a(n - a(n-1))" in best.formula_str
    assert best.terms_tested == len(conway)


def test_hofstadter_g_sequence():
    """Hofstadter G-sequence A005206: a(n) = n - a(a(n-1))."""
    g = [0]
    for n in range(1, 35):
        g.append(n - g[g[-1]])

    discovery = NestedRecurrenceDiscovery()
    cands = discovery.discover("A005206", g, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "n - a(a(n-1))" in best.formula_str
    assert best.terms_tested == len(g)


def test_hofstadter_q3_sequence():
    """Generalized Hofstadter Q_3 sequence: a(n) = a(n - a(n-1)) + a(n - a(n-3))."""
    q3 = [1, 1, 1]
    for n in range(4, 30):
        t1 = q3[n - 1 - q3[-1]]
        t2 = q3[n - 1 - q3[-3]]
        q3.append(t1 + t2)

    discovery = NestedRecurrenceDiscovery()
    cands = discovery.discover("Q3", q3, start_index=1)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(n - a(n-3))" in best.formula_str


def test_nested_rejection():
    """Fibonacci numbers do not satisfy nested self-index recurrences."""
    fib = [0, 1]
    for _ in range(25):
        fib.append(fib[-1] + fib[-2])

    discovery = NestedRecurrenceDiscovery()
    cands = discovery.discover("A000045", fib, start_index=0)
    assert len(cands) == 0
