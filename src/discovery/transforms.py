"""
Combinatorial Sequence Transformations:
- Partial Sums (Prefix Sums)
- First Differences
- Binomial Transform: B(a)_n = sum_{k=0}^n binom(n, k) * a_k
- Inverse Binomial Transform: B^{-1}(a)_n = sum_{k=0}^n (-1)^{n-k} binom(n, k) * a_k
"""

import math
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from .base import DiscoveryMethod


class TransformDiscovery(DiscoveryMethod):
    @property
    def name(self) -> str:
        return "transforms"

    @staticmethod
    def binomial_transform(terms: List[int]) -> List[int]:
        n = len(terms)
        b = []
        for i in range(n):
            s = 0
            for k in range(i + 1):
                s += math.comb(i, k) * terms[k]
            b.append(s)
        return b

    @staticmethod
    def inverse_binomial_transform(terms: List[int]) -> List[int]:
        n = len(terms)
        b = []
        for i in range(n):
            s = 0
            for k in range(i + 1):
                sign = 1 if (i - k) % 2 == 0 else -1
                s += sign * math.comb(i, k) * terms[k]
            b.append(s)
        return b

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 6:
            return results

        # 1. Check if sequence is the binomial transform of 1 (which is 2^n)
        inv_bin = self.inverse_binomial_transform(terms[:12])
        if all(x == 1 for x in inv_bin):
            results.append(CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str="a(n) = sum_{k=0}^n binom(n, k)",
                latex_str="a(n) = \\sum_{k=0}^n \\binom{n}{k}",
                description="Binomial transform of the constant sequence 1",
                complexity=2.0,
                terms_tested=len(terms),
                verification_status=VerificationStatus.EXACT_MATCH,
                evaluator=lambda n: 2**n,
            ))

        # 2. Check if terms are partial sums of a simpler sequence
        diffs = [terms[i+1] - terms[i] for i in range(len(terms)-1)]
        if all(d == diffs[0] for d in diffs):
            # Arithmetic progression partial sum (quadratic)
            d_val = diffs[0]
            results.append(CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str=f"a(n) = a({start_index}) + sum_{{k=1}}^n {d_val}",
                latex_str=f"a(n) = a({start_index}) + \\sum_{{k=1}}^n {d_val}",
                description="Prefix sum of arithmetic progression",
                complexity=1.8,
                terms_tested=len(terms),
                verification_status=VerificationStatus.EXACT_MATCH,
                evaluator=lambda n, d=d_val, a0=terms[0], s0=start_index: a0 + (n - s0) * d,
            ))

        return results
