"""
Quasipolynomial (Ehrhart polynomial / Periodic polynomial) Discovery.
Detects sequences where a(n) is given by a different polynomial depending on the residue class n mod m.
a(m*k + r) = P_r(k) for r in {0, 1, ..., m-1}.
"""

from fractions import Fraction
from typing import Callable, List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class QuasipolynomialDiscovery(DiscoveryMethod):
    def __init__(self, max_period: int = 6, max_degree: int = 4):
        self.max_period = max_period
        self.max_degree = max_degree
        self.periods = [2, 3, 4, 6]

    @property
    def name(self) -> str:
        return "quasipolynomial"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 12:
            return results

        for m in self.periods:
            if m > self.max_period:
                continue

            # Check that each residue class has at least 5 terms
            if len(terms) < m * 5:
                continue

            cand = self._test_period(a_num, terms, start_index, m)
            if cand is not None:
                results.append(cand)
                # Found minimal fundamental quasipolynomial period
                break

        return results

    def _test_period(
        self,
        a_num: str,
        terms: List[int],
        start_index: int,
        m: int
    ) -> Optional[CandidateFormula]:
        poly_deltas_by_residue: List[List[Fraction]] = []
        poly_degrees: List[int] = []

        for r in range(m):
            sub_terms = [terms[idx] for idx in range(r, len(terms), m)]
            if len(sub_terms) < 4:
                return None

            diff_table: List[List[Fraction]] = [[Fraction(t) for t in sub_terms]]
            deg = 0
            found_poly = False

            while deg < min(self.max_degree, len(sub_terms) - 2):
                prev_row = diff_table[-1]
                next_row = [prev_row[i + 1] - prev_row[i] for i in range(len(prev_row) - 1)]
                diff_table.append(next_row)
                deg += 1

                if all(d == 0 for d in next_row):
                    actual_deg = deg - 1
                    deltas = [diff_table[k][0] for k in range(actual_deg + 1)]
                    poly_deltas_by_residue.append(deltas)
                    poly_degrees.append(actual_deg)
                    found_poly = True
                    break

            if not found_poly:
                return None

        # If all polynomials across all residues are identical and deg <= 0 or matching,
        # check if this is not just a standard single polynomial
        max_deg = max(poly_degrees)

        def eval_quasipoly(n: int) -> int:
            x = n - start_index
            k = x // m
            r = x % m
            deltas = poly_deltas_by_residue[r]
            val = Fraction(0)
            for j, delta in enumerate(deltas):
                if delta == 0:
                    continue
                binom_val = Fraction(1)
                for step in range(j):
                    binom_val *= Fraction(k - step, step + 1)
                val += delta * binom_val

            if val.denominator != 1:
                raise ValueError("Quasipolynomial evaluated to non-integer")
            return val.numerator

        # Verify against 100% of all available terms
        is_exact, matched, err = Verifier.verify_explicit(
            CandidateFormula(),
            eval_quasipoly,
            terms,
            start_index
        )

        if not is_exact or matched < len(terms):
            return None

        # Build readable representation
        branches = []
        for r in range(m):
            deltas = poly_deltas_by_residue[r]
            terms_str = []
            for j, delta in enumerate(deltas):
                if delta != 0:
                    if j == 0:
                        terms_str.append(f"{delta}")
                    elif j == 1:
                        terms_str.append(f"{delta}*k")
                    else:
                        terms_str.append(f"{delta}*binom(k, {j})")
            branch_expr = " + ".join(terms_str).replace("+ -", "- ") if terms_str else "0"
            branches.append(f"{branch_expr} if n={m}*k+{r}")

        formula_str = f"a(n) = [ {'; '.join(branches)} ] with k=(n-{start_index})//{m}"
        latex_str = f"a(n) \\text{{ is a quasipolynomial of period }} {m} \\text{{ and max degree }} {max_deg}"

        complexity = 2.0 + (m * 0.8) + (max_deg * 1.5)

        return CandidateFormula(
            a_number=a_num,
            method=self.name,
            formula_str=formula_str,
            latex_str=latex_str,
            description=f"Exact quasipolynomial with period {m} and maximum degree {max_deg}",
            complexity=complexity,
            terms_tested=matched,
            verification_status=VerificationStatus.EXACT_MATCH,
            evaluator=eval_quasipoly,
            valid_from_index=start_index,
            details={
                "period": m,
                "max_degree": max_deg,
                "poly_degrees": poly_degrees
            }
        )

