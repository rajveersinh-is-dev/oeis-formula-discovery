import pytest
from src.discovery.generating_function import GeneratingFunctionDiscovery
from src.candidate.model import VerificationStatus


def test_fibonacci_generating_function():
    gf = GeneratingFunctionDiscovery(max_degree=4)
    # Fibonacci: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144
    terms = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    cands = gf.discover("A000045", terms, 0)
    assert len(cands) == 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    # For Fibonacci G(x) = x / (1 - x - x^2)
    assert "x" in best.formula_str
    assert "x^2" in best.formula_str

