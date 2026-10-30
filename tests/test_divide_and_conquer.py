"""
Unit tests for Divide-and-Conquer and k-Regular Recurrence Discovery.
"""

from src.candidate.model import VerificationStatus
from src.discovery.divide_and_conquer import DivideAndConquerDiscovery


def test_stern_diatomic_sequence():
    """Stern's diatomic sequence A002487: a(2n) = a(n), a(2n+1) = a(n) + a(n+1)."""
    stern = [0, 1]
    for i in range(2, 40):
        if i % 2 == 0:
            stern.append(stern[i // 2])
        else:
            stern.append(stern[i // 2] + stern[i // 2 + 1])

    discovery = DivideAndConquerDiscovery(bases=[2, 3])
    cands = discovery.discover("A002487", stern, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*n) = a(n)" in best.formula_str
    assert "a(2*n + 1) = a(n) + a(n+1)" in best.formula_str
    assert best.terms_tested == len(stern)


def test_moser_de_bruijn_sequence():
    """Moser-de Bruijn sequence A000695: a(2n) = 4*a(n), a(2n+1) = 4*a(n) + 1."""
    moser = [0]
    for i in range(1, 40):
        if i % 2 == 0:
            moser.append(4 * moser[i // 2])
        else:
            moser.append(4 * moser[i // 2] + 1)

    discovery = DivideAndConquerDiscovery()
    cands = discovery.discover("A000695", moser, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*n) = 4*a(n)" in best.formula_str
    assert "a(2*n + 1) = 4*a(n) + 1" in best.formula_str
    assert best.terms_tested == len(moser)


def test_goulds_sequence():
    """Gould's sequence A001316: a(2n) = a(n), a(2n+1) = 2*a(n)."""
    gould = [1]
    for i in range(1, 40):
        if i % 2 == 0:
            gould.append(gould[i // 2])
        else:
            gould.append(2 * gould[i // 2])

    discovery = DivideAndConquerDiscovery()
    cands = discovery.discover("A001316", gould, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*n) = a(n)" in best.formula_str
    assert "a(2*n + 1) = 2*a(n)" in best.formula_str
    assert best.terms_tested == len(gould)


def test_thue_morse_sequence():
    """Thue-Morse sequence A010060: a(2n) = a(n), a(2n+1) = -a(n) + 1."""
    thue = [0]
    for i in range(1, 40):
        if i % 2 == 0:
            thue.append(thue[i // 2])
        else:
            thue.append(1 - thue[i // 2])

    discovery = DivideAndConquerDiscovery()
    cands = discovery.discover("A010060", thue, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*n) = a(n)" in best.formula_str
    assert "a(2*n + 1) = -a(n) + 1" in best.formula_str


def test_binary_popcount_sequence():
    """Binary Hamming weight A000120: a(2n) = a(n), a(2n+1) = a(n) + 1."""
    popcount = [bin(n).count("1") for n in range(40)]

    discovery = DivideAndConquerDiscovery()
    cands = discovery.discover("A000120", popcount, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*n) = a(n)" in best.formula_str
    assert "a(2*n + 1) = a(n) + 1" in best.formula_str


def test_stern_offset_1():
    """Stern's sequence with offset 1: a(1) = 1, a(2) = 1, a(2n) = a(n), a(2n+1) = a(n) + a(n+1)."""
    stern_1 = [1, 1, 2, 1, 3, 2, 3, 1, 4, 3, 5, 2, 5, 3, 4, 1, 5, 4, 7, 3, 8, 5, 7, 2, 7, 5, 8, 3, 7, 4, 5, 1]
    discovery = DivideAndConquerDiscovery()
    cands = discovery.discover("A002487_1", stern_1, start_index=1)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(2*n) = a(n)" in best.formula_str
    assert "a(2*n + 1) = a(n) + a(n+1)" in best.formula_str


def test_base3_divide_and_conquer():
    """Ternary digital sequence: a(3n) = 2*a(n), a(3n+1) = 2*a(n) + 1, a(3n+2) = 2*a(n) + 2."""
    t = [0]
    for i in range(1, 45):
        r = i % 3
        sub = i // 3
        t.append(2 * t[sub] + r)
    discovery = DivideAndConquerDiscovery(bases=[2, 3])
    cands = discovery.discover("BASE3_DIG", t, start_index=0)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "a(3*n) = 2*a(n)" in best.formula_str


def test_divide_and_conquer_rejection():
    """Primes cannot satisfy divide-and-conquer recurrence."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    discovery = DivideAndConquerDiscovery()
    cands = discovery.discover("A000040", primes, start_index=1)
    assert len(cands) == 0
