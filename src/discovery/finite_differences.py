"""
Finite difference analysis, Newton series interpolation, and polynomial discovery over exact integers/rationals.
Detects constant, arithmetic progressions, and exact bounded-degree polynomials.
"""

from fractions import Fraction
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class FiniteDifferenceDiscovery(DiscoveryMethod):
    def __init__(self, max_degree: int = 6):
        self.max_degree = max_degree

    @property
    def name(self) -> str:
        return "finite_differences"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 4:
            return results

        # 1. Check for Constant sequence
        if all(x == terms[0] for x in terms):
            c = terms[0]
            cand = CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str=f"a(n) = {c}",
                latex_str=f"a(n) = {c}",
                description="Constant sequence",
                complexity=1.0,
                terms_tested=len(terms),
                verification_status=VerificationStatus.EXACT_MATCH,
                evaluator=lambda n, val=c: val,
            )
            results.append(cand)
            return results

        # 2. Difference Table Construction
        diff_table: List[List[Fraction]] = [[Fraction(t) for t in terms]]
        deg = 0

        while deg < min(self.max_degree, len(terms) - 2):
            prev_row = diff_table[-1]
            next_row = [prev_row[i+1] - prev_row[i] for i in range(len(prev_row) - 1)]
            diff_table.append(next_row)
            deg += 1

            # Check if current difference row is identically zero
            if all(d == 0 for d in next_row):
                # Degree is deg - 1 polynomial
                actual_deg = deg - 1
                poly_cand = self._build_polynomial_candidate(
                    a_num, diff_table, actual_deg, terms, start_index
                )
                if poly_cand:
                    results.append(poly_cand)
                break

        return results

    def _build_polynomial_candidate(
        self,
        a_num: str,
        diff_table: List[List[Fraction]],
        degree: int,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """
        Builds the explicit polynomial formula via Newton series:
        P(n) = sum_{k=0}^d (Delta^k a(0)) * binom(n - n0, k)
        """
        deltas = [diff_table[k][0] for k in range(degree + 1)]

        def eval_poly(n: int) -> int:
            val = Fraction(0)
            x = n - start_index
            for k, delta in enumerate(deltas):
                if delta == 0:
                    continue
                # binom(x, k)
                binom_val = Fraction(1)
                for j in range(k):
                    binom_val *= Fraction(x - j, j + 1)
                val += delta * binom_val
            if val.denominator != 1:
                raise ValueError("Polynomial evaluated to non-integer")
            return val.numerator

        # Verify against all terms
        is_exact, matched, err = Verifier.verify_explicit(
            CandidateFormula(), eval_poly, terms, start_index
        )
        if not is_exact:
            return None

        # Format readable string
        terms_str = []
        for k, delta in enumerate(deltas):
            if delta != 0:
                if k == 0:
                    terms_str.append(f"{delta}")
                elif k == 1:
                    terms_str.append(f"{delta}*(n - {start_index})")
                else:
                    terms_str.append(f"{delta}*binom(n - {start_index}, {k})")

        formula_repr = " + ".join(terms_str).replace("+ -", "- ")
        complexity = 1.0 + degree * 1.5 + (0.5 if start_index != 0 else 0.0)

        return CandidateFormula(
            a_number=a_num,
            method=self.name,
            formula_str=f"a(n) = {formula_repr}",
            latex_str=f"a(n) = {formula_repr}",
            description=f"Exact polynomial of degree {degree} via Newton forward differences",
            complexity=complexity,
            terms_tested=matched,
            verification_status=VerificationStatus.EXACT_MATCH,
            evaluator=eval_poly,
            valid_from_index=start_index,
        )

