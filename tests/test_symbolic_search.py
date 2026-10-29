import pytest
from src.discovery.symbolic_search import SymbolicExpressionDiscovery
from src.candidate.model import VerificationStatus


def test_powers_of_two():
    sd = SymbolicExpressionDiscovery()
    terms = [2**n for n in range(15)]
    cands = sd.discover("A000079", terms, 0)
    assert len(cands) >= 1
    assert any(c.formula_str == "a(n) = 2^n" for c in cands)


def test_mersenne_numbers():
    sd = SymbolicExpressionDiscovery()
    terms = [(2**n) - 1 for n in range(15)]
    cands = sd.discover("A000225", terms, 0)
    assert len(cands) >= 1
    assert any(c.formula_str == "a(n) = 2^n - 1" for c in cands)


def test_factorials():
    import math
    sd = SymbolicExpressionDiscovery()
    terms = [math.factorial(n) for n in range(10)]
    cands = sd.discover("A000142", terms, 0)
    assert len(cands) >= 1
    assert any("n!" in c.formula_str for c in cands)

