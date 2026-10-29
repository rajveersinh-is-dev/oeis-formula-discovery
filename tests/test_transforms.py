import pytest
from src.discovery.transforms import TransformDiscovery
from src.candidate.model import VerificationStatus


def test_binomial_transform_of_one():
    td = TransformDiscovery()
    # Binomial transform of constant 1: 1, 2, 4, 8, 16, 32, 64, 128
    terms = [2**n for n in range(12)]
    cands = td.discover("A000079", terms, 0)
    assert len(cands) >= 1
    assert any("sum_{k=0}^n binom(n, k)" in c.formula_str for c in cands)


def test_partial_sums():
    td = TransformDiscovery()
    # Partial sums of constant difference d=4 starting at a0=2: 2, 6, 10, 14, 18
    terms = [2 + 4 * n for n in range(10)]
    cands = td.discover("TEST_PS", terms, 0)
    assert len(cands) >= 1

