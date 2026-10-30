"""
Unit tests for Modular Product & Euler Transform Discovery Module.
"""

from src.candidate.model import VerificationStatus
from src.discovery.modular_product import ModularProductDiscovery


def test_partition_numbers_modular_product():
    """A000041: Partition numbers G(x) = prod_{k=1}^inf 1 / (1 - x^k)."""
    partitions = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231, 297, 385, 490, 627, 792, 1002]
    discovery = ModularProductDiscovery()
    cands = discovery.discover("A000041", partitions, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "prod_{k=1}^inf 1 / (1 - x^k)" in best.formula_str
    assert best.terms_tested == len(partitions)


def test_distinct_partitions_modular_product():
    """A000009: Partitions into distinct parts G(x) = prod_{k=1}^inf (1 + x^k)."""
    distinct = [1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 27, 32, 38, 46, 54, 64, 76, 89, 104, 122]
    discovery = ModularProductDiscovery()
    cands = discovery.discover("A000009", distinct, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "distinct" in best.description or "c_k mod 2" in best.formula_str
    assert best.terms_tested == len(distinct)


def test_ramanujan_tau_product():
    """A000594: Ramanujan tau function G(x) = x * prod_{k=1}^inf (1 - x^k)^24."""
    # Sequence with leading zero at index 0, tau(1) = 1
    tau = [0, 1, -24, 252, -1472, 4830, -6048, -16744, 84480, -113643, -115920, 534612, -370944, -577738, 401856, 1217160]
    discovery = ModularProductDiscovery()
    cands = discovery.discover("A000594", tau, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "(1 - x^k)^24" in best.formula_str
    assert best.terms_tested == len(tau)


def test_rogers_ramanujan_first():
    """A003114: First Rogers-Ramanujan identity."""
    # True expansion of prod_{k=1}^inf 1 / ((1 - x^{5k-4})(1 - x^{5k-1}))
    N = 30
    dp = [0] * (N + 1)
    dp[0] = 1
    for k in range(1, N + 1):
        for p in (5 * k - 4, 5 * k - 1):
            if p <= N:
                for i in range(p, N + 1):
                    dp[i] += dp[i - p]

    discovery = ModularProductDiscovery()
    cands = discovery.discover("A003114", dp, start_index=0)

    assert len(cands) >= 1
    best = cands[0]
    assert best.verification_status == VerificationStatus.EXACT_MATCH
    assert "Rogers-Ramanujan" in best.description or "5k-4" in best.formula_str
    assert best.terms_tested == len(dp)
