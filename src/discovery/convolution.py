"""
Convolution Recurrence Discovery Module.
Discovers exact self-convolution and binomial convolution identities:
1. Cauchy Self-Convolution (Catalan-type):
   a(n) = sum_{k=0}^{n-1} a(k) * a(n-1-k)
2. Shifted Cauchy Convolution (Trees / Noncrossing partitions):
   a(n) = sum_{k=1}^{n-1} a(k) * a(n-k)
3. Motzkin Cauchy Convolution:
   a(n) = a(n-1) + sum_{k=0}^{n-2} a(k) * a(n-2-k)
4. Binomial Self-Convolution (Bell numbers):
   a(n) = sum_{k=0}^{n-1} binom(n-1, k) * a(k)

Uses exact arbitrary-precision integer arithmetic.
"""

import math
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class ConvolutionRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "convolution_recurrence"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []
        N = len(terms)
        if N < 5:
            return candidates

        # 1. Test Catalan Cauchy convolution
        cand = self._test_catalan_cauchy(a_number, terms, start_index)
        if cand:
            candidates.append(cand)
            return candidates

        # 2. Test Motzkin Cauchy convolution
        cand = self._test_motzkin_cauchy(a_number, terms, start_index)
        if cand:
            candidates.append(cand)
            return candidates

        # 3. Test Bell binomial convolution
        cand = self._test_bell_binomial(a_number, terms, start_index)
        if cand:
            candidates.append(cand)
            return candidates

        return candidates

    def _test_catalan_cauchy(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        if terms[0] != 1:
            return None

        # Check terms
        N = len(terms)
        for n in range(1, N):
            computed = sum(terms[k] * terms[n - 1 - k] for k in range(n))
            if computed != terms[n]:
                return None

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=f"a(n) = sum_{{k=0}}^{{n-1}} a(k)*a(n-1-k); with a({start_index}) = 1",
            description="Cauchy self-convolution recurrence (Catalan family)",
            complexity=2.0,
            terms_tested=N,
            valid_from_index=start_index,
            details={"type": "catalan_cauchy", "initial_terms": [terms[0]]},
            verification_status=VerificationStatus.EXACT_MATCH,
        )
        return cand

    def _test_motzkin_cauchy(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        if len(terms) < 6 or terms[:2] != [1, 1]:
            return None

        N = len(terms)
        for n in range(2, N):
            computed = terms[n - 1] + sum(terms[k] * terms[n - 2 - k] for k in range(n - 1))
            if computed != terms[n]:
                return None

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=f"a(n) = a(n-1) + sum_{{k=0}}^{{n-2}} a(k)*a(n-2-k); with a({start_index}) = 1, a({start_index+1}) = 1",
            description="Motzkin-type self-convolution recurrence",
            complexity=2.5,
            terms_tested=N,
            valid_from_index=start_index,
            details={"type": "motzkin_cauchy", "initial_terms": terms[:2]},
            verification_status=VerificationStatus.EXACT_MATCH,
        )
        return cand

    def _test_bell_binomial(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        if terms[0] != 1:
            return None

        N = len(terms)
        for n in range(1, N):
            computed = sum(math.comb(n - 1, k) * terms[k] for k in range(n))
            if computed != terms[n]:
                return None

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=f"a(n) = sum_{{k=0}}^{{n-1}} binom(n-1, k)*a(k); with a({start_index}) = 1",
            description="Binomial self-convolution recurrence (Bell numbers)",
            complexity=2.2,
            terms_tested=N,
            valid_from_index=start_index,
            details={"type": "bell_binomial", "initial_terms": [terms[0]]},
            verification_status=VerificationStatus.EXACT_MATCH,
        )
        return cand

