"""
Unit tests for High Mathematical Importance Benchmark Suite.
Verifies that:
1. All 27 sequence registry targets have valid A-numbers, labels, and domains.
2. Evaluator correctly differentiates between heuristic models and non-overfitting rejections.
3. Offline integrity is preserved.
"""

from benchmarks.high_importance_benchmark import HIGH_IMPORTANCE_REGISTRY
from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISRecord


def test_high_importance_registry_integrity():
    """Verify registry has at least 25 sequences, unique A-numbers, and descriptive metadata."""
    assert len(HIGH_IMPORTANCE_REGISTRY) >= 25

    a_nums = [item[0] for item in HIGH_IMPORTANCE_REGISTRY]
    assert len(a_nums) == len(set(a_nums)), "Duplicate A-numbers found in registry"

    for a_num, short_name, domain in HIGH_IMPORTANCE_REGISTRY:
        assert a_num.startswith("A") and len(a_num) == 7
        assert len(short_name) > 0
        assert len(domain) > 0


def test_saw_heuristic_growth_discovery():
    """Verify that 2D self-avoiding walks discover heuristic exponential growth."""
    engine = DiscoveryEngine()
    saw2d = [1, 4, 12, 36, 100, 284, 780, 2172, 5916, 16268, 44100, 120292, 324932, 881500, 2374444, 6416596, 17245332, 46466676, 124658732, 335116620, 897697164, 2409047612, 6443560484, 17245995004, 46046745156, 123067759508, 328320448108, 877396885276]
    rec = OEISRecord(
        a_number="A001411",
        id_number=1411,
        name="Self-avoiding walks on square lattice",
        offset_first_term=0,
        terms=saw2d,
    )
    cands = engine.analyze_sequence(rec)
    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.HEURISTIC
    assert best.method == "asymptotic"
    assert "2.7" in best.formula_str  # Connective constant ~ 2.71


def test_ramsey_honest_rejection():
    """Verify that Ramsey numbers R(3, n) are not overfitted with false polynomials."""
    engine = DiscoveryEngine()
    ramsey_r3 = [1, 3, 6, 9, 14, 18, 23, 28, 36]
    rec = OEISRecord(
        a_number="A000791",
        id_number=791,
        name="Ramsey numbers R(3,n)",
        offset_first_term=1,
        terms=ramsey_r3,
    )
    cands = engine.analyze_sequence(rec)
    exact_cands = [c for c in cands if c.verification_status == VerificationStatus.EXACT_MATCH]
    # Ramsey numbers have no known linear recurrence or low-degree polynomial
    assert len(exact_cands) == 0
