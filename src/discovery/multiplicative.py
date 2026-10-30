"""
Multiplicative & Power Recurrence Discovery Module.
Discovers exact non-linear multiplicative recurrence relations:
a(n) = c * a(n-1)^p * a(n-2)^q
where p, q in {1, 2, 3} and c in Z.

Examples:
- Multiplicative Fibonacci (A000045-like products): a(n) = a(n-1) * a(n-2)
- Multiplicative with scale: a(n) = 2 * a(n-1) * a(n-2)
- Iterated power-products: a(n) = a(n-1)^2 * a(n-2)

Uses exact arbitrary-precision integer arithmetic.
"""

from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class MultiplicativeRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self, max_power: int = 3):
        self.max_power = max_power

    @property
    def name(self) -> str:
        return "multiplicative_recurrence"

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

        # Zero or sign alternation check
        if any(t == 0 for t in terms[:4]):
            return candidates

        for p in range(1, self.max_power + 1):
            for q in range(1, self.max_power + 1):
                # Calculate c from first step: a(2) = c * a(1)^p * a(0)^q
                denom = (terms[1] ** p) * (terms[0] ** q)
                if denom == 0 or terms[2] % denom != 0:
                    continue

                c = terms[2] // denom
                if c == 0:
                    continue

                formula_str = self._format_multiplicative(c, p, q, terms[:2], start_index)
                complexity = float(3.0 + p + q + len(str(abs(c))))

                cand = CandidateFormula(
                    a_number=a_number,
                    method=self.name,
                    formula_str=formula_str,
                    description=f"Multiplicative recurrence a(n) = {c}*a(n-1)^{p}*a(n-2)^{q}",
                    complexity=complexity,
                    terms_tested=N,
                    valid_from_index=start_index,
                    details={"mult_c": c, "pow_p": p, "pow_q": q, "initial_terms": terms[:2]},
                    verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
                )

                is_valid, matched, msg = Verifier.verify_multiplicative_recurrence(
                    candidate=cand,
                    mult_c=c,
                    pow_p=p,
                    pow_q=q,
                    initial_terms=terms[:2],
                    all_terms=terms,
                    start_index=start_index,
                )

                if is_valid:
                    cand.verification_status = VerificationStatus.EXACT_MATCH
                    cand.terms_tested = matched
                    candidates.append(cand)
                    return candidates

        return candidates

    @staticmethod
    def _format_multiplicative(
        c: int,
        p: int,
        q: int,
        initial_terms: List[int],
        start_index: int,
    ) -> str:
        t1 = "a(n-1)" if p == 1 else f"a(n-1)^{p}"
        t2 = "a(n-2)" if q == 1 else f"a(n-2)^{q}"

        if c == 1:
            core = f"{t1} * {t2}"
        elif c == -1:
            core = f"-{t1} * {t2}"
        else:
            core = f"{c} * {t1} * {t2}"

        init_str = f"a({start_index}) = {initial_terms[0]}, a({start_index+1}) = {initial_terms[1]}"
        return f"a(n) = {core}; with {init_str}"

