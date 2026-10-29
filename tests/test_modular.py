import pytest
from src.discovery.modular import ModularPatternDiscovery
from src.candidate.model import VerificationStatus


def test_strictly_periodic_sequence():
    md = ModularPatternDiscovery()
    # Sequence with period 3: 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3
    pattern = [1, 2, 3]
    terms = pattern * 5
    cands = md.discover("TEST_MOD", terms, 0)
    assert len(cands) >= 1
    assert any("periodic with period 3" in c.formula_str for c in cands)


def test_alternating_parity():
    md = ModularPatternDiscovery()
    # Alternating 0, 1, 0, 1...
    terms = [n % 2 for n in range(20)]
    cands = md.discover("TEST_PARITY", terms, 0)
    assert len(cands) >= 1
    assert any("periodic with period 2" in c.formula_str for c in cands)

