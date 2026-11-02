"""
Tests for Extreme Complexity Benchmark Suite.
"""

from benchmarks.complex_sequences_benchmark import COMPLEX_TARGETS


def test_complex_targets_registry_integrity():
    """Verifies that all complex targets have valid OEIS IDs and domains."""
    assert len(COMPLEX_TARGETS) >= 15
    for a_num, name, domain in COMPLEX_TARGETS:
        assert a_num.startswith("A")
        assert len(a_num) == 7
        assert len(name) > 0
        assert len(domain) > 0
