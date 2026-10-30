"""
q-Series & Basic Hypergeometric Recurrence Discovery Module.
Discovers exact q-difference and basic hypergeometric recurrence relations:
1. First-order q-difference equations:
   a(n) = (c1 * q^n + c0) * a(n-1) + const_e
   - q-powers: a(n) = q^n * a(n-1) (a(n) = q^{n(n+1)/2})
   - q-factorials [n]_q! (A005329): a(n) = (q^n - 1) * a(n-1)
2. Second-order q-recurrences:
   a(n) = (c1 * q^n + c0) * a(n-1) + (d1 * q^n + d0) * a(n-2)
   - q-Fibonacci / Schur polynomials: a(n) = a(n-1) + q^{n-2} * a(n-2)
   - q-orthogonal polynomials and Rogers-Ramanujan convergent recurrences

The base q is discovered dynamically from successive ratio differences Delta R(n),
or explored over candidate digital bases q in {2, 3, -2, 4, 5}.
All linear algebra is exact over Fractions with zero floating-point operations.
"""

from fractions import Fraction
import math
from typing import Any, Dict, List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class QSeriesDiscovery(DiscoveryMethod):
    def __init__(self, bases: Optional[List[int]] = None):
        self.bases = bases if bases is not None else [2, 3, -2, 4, 5]

    @property
    def name(self) -> str:
        return "q_series"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []
        N = len(terms)
        if N < 8:
            return candidates

        # 1. Dynamic ratio discovery for first-order q-dilation: a(n) = (c1*q^n + c0)*a(n-1)
        cand_ratio = self._discover_dynamic_ratio(a_number, terms, start_index)
        if cand_ratio is not None:
            candidates.append(cand_ratio)
            return candidates

        # 2. Search first-order affine: a(n) = c1*q^n*a(n-1) + c0*a(n-1) + e
        for q in self.bases:
            cand_ord1 = self._fit_order1_affine(a_number, terms, start_index, q)
            if cand_ord1 is not None:
                candidates.append(cand_ord1)
                return candidates

        # 3. Search second-order q-difference: a(n) = (c1*q^n + c0)*a(n-1) + (d1*q^n + d0)*a(n-2)
        for q in self.bases:
            cand_ord2 = self._fit_order2(a_number, terms, start_index, q)
            if cand_ord2 is not None:
                candidates.append(cand_ord2)
                return candidates

        return candidates

    def _discover_dynamic_ratio(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """Dynamically identifies q from Delta R_{n+1} / Delta R_n where R_n = a(n)/a(n-1)."""
        N = len(terms)
        if N < 6:
            return None

        # Check zero denominators
        if any(terms[i] == 0 for i in range(N - 1)):
            return None

        R = [Fraction(terms[i], terms[i - 1]) for i in range(1, N)]
        dR = [R[i] - R[i - 1] for i in range(1, len(R))]

        # If dR is identically zero, this is standard geometric (handled by linear recurrence)
        if all(d == 0 for d in dR):
            return None

        if len(dR) < 3 or dR[0] == 0:
            return None

        q_frac = dR[1] / dR[0]
        if q_frac.denominator != 1 or abs(q_frac.numerator) < 2:
            return None

        q = q_frac.numerator
        # Verify that dR[i] / dR[i-1] == q for all remaining steps
        for i in range(2, len(dR)):
            if dR[i - 1] == 0 or dR[i] / dR[i - 1] != Fraction(q):
                return None

        # Extract c1 and c0
        # dR[0] corresponds to n = start_index + 2:
        # R_2 - R_1 = c1 * q^{start_index + 1} * (q - 1)
        n1 = start_index + 1
        denom = Fraction(q ** n1 * (q - 1))
        if denom == 0:
            return None
        c1 = dR[0] / denom
        c0 = R[0] - c1 * Fraction(q ** (start_index + 1))

        if c1.denominator != 1 or c0.denominator != 1:
            return None

        c1_int = c1.numerator
        c0_int = c0.numerator

        # Format formula
        if c1_int == 1 and c0_int == 0:
            mult_str = f"({q}^n)"
        elif c1_int == 1 and c0_int == -1:
            mult_str = f"({q}^n - 1)"
        elif c1_int == 1 and c0_int > 0:
            mult_str = f"({q}^n + {c0_int})"
        elif c1_int == 1 and c0_int < 0:
            mult_str = f"({q}^n - {abs(c0_int)})"
        elif c0_int == 0:
            mult_str = f"({c1_int}*{q}^n)"
        elif c0_int > 0:
            mult_str = f"({c1_int}*{q}^n + {c0_int})"
        else:
            mult_str = f"({c1_int}*{q}^n - {abs(c0_int)})"

        formula_str = f"a(n) = {mult_str}*a(n-1); with a({start_index}) = {terms[0]}"
        desc = f"First-order q-difference equation with base q={q}: {formula_str}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            latex_str=formula_str,
            description=desc,
            complexity=2.0 + len(str(abs(q))) * 0.2 + len(str(abs(c1_int))) * 0.2,
            terms_tested=N,
            valid_from_index=start_index + 1,
            initial_conditions=terms[:1],
            details={"order": 1, "base_q": q, "c1": c1, "c0": c0, "d1": Fraction(0), "d0": Fraction(0), "e": Fraction(0)},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_q_series(
            candidate=cand,
            base_q=q,
            c1=c1,
            c0=c0,
            d1=Fraction(0),
            d0=Fraction(0),
            const_e=Fraction(0),
            order=1,
            initial_terms=terms[:1],
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _fit_order1_affine(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        q: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n) = c1*q^n*a(n-1) + c0*a(n-1) + const_e."""
        N = len(terms)
        if N < 7:
            return None

        # 3 unknowns: c1, c0, e
        matrix = []
        b_vec = []
        for i in range(1, 4):
            n_val = start_index + i
            q_pow = Fraction(q ** n_val)
            prev = Fraction(terms[i - 1])
            matrix.append([q_pow * prev, prev, Fraction(1)])
            b_vec.append(Fraction(terms[i]))

        sol = self._solve_linear_system(matrix, b_vec)
        if sol is None or any(c.denominator != 1 for c in sol):
            return None

        c1, c0, const_e = sol
        # Skip if c1 == 0 (standard linear/inhomogeneous recurrence)
        if c1 == 0:
            return None

        formula_str = (
            f"a(n) = ({c1.numerator}*{q}^n + {c0.numerator})*a(n-1) + {const_e.numerator}; "
            f"with a({start_index}) = {terms[0]}"
        )

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            latex_str=formula_str,
            description=f"First-order affine q-recurrence with base q={q}",
            complexity=2.2 + len(str(abs(q))) * 0.2,
            terms_tested=N,
            valid_from_index=start_index + 1,
            initial_conditions=terms[:1],
            details={"order": 1, "base_q": q, "c1": c1, "c0": c0, "d1": Fraction(0), "d0": Fraction(0), "e": const_e},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_q_series(
            candidate=cand,
            base_q=q,
            c1=c1,
            c0=c0,
            d1=Fraction(0),
            d0=Fraction(0),
            const_e=const_e,
            order=1,
            initial_terms=terms[:1],
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _fit_order2(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        q: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n) = (c1*q^n + c0)*a(n-1) + (d1*q^n + d0)*a(n-2)."""
        N = len(terms)
        if N < 8:
            return None

        # 4 unknowns: c1, c0, d1, d0
        matrix = []
        b_vec = []
        for i in range(2, 6):
            n_val = start_index + i
            q_pow = Fraction(q ** n_val)
            prev1 = Fraction(terms[i - 1])
            prev2 = Fraction(terms[i - 2])
            matrix.append([q_pow * prev1, prev1, q_pow * prev2, prev2])
            b_vec.append(Fraction(terms[i]))

        sol = self._solve_linear_system(matrix, b_vec)
        if sol is None or any(c.denominator != 1 for c in sol):
            return None

        c1, c0, d1, d0 = sol
        # Must involve q (at least one of c1 or d1 non-zero)
        if c1 == 0 and d1 == 0:
            return None

        # Format formula
        parts = []
        if c1 != 0 and c0 != 0:
            parts.append(f"({c1.numerator}*{q}^n + {c0.numerator})*a(n-1)")
        elif c1 != 0:
            parts.append(f"({c1.numerator}*{q}^n)*a(n-1)")
        elif c0 != 0:
            parts.append(f"{c0.numerator}*a(n-1)")

        if d1 != 0 and d0 != 0:
            parts.append(f"({d1.numerator}*{q}^n + {d0.numerator})*a(n-2)")
        elif d1 != 0:
            parts.append(f"({d1.numerator}*{q}^n)*a(n-2)")
        elif d0 != 0:
            parts.append(f"{d0.numerator}*a(n-2)")

        rhs_str = " + ".join(parts)
        formula_str = (
            f"a(n) = {rhs_str}; with a({start_index}) = {terms[0]}, a({start_index + 1}) = {terms[1]}"
        )

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            latex_str=formula_str,
            description=f"Second-order q-recurrence with base q={q}: {formula_str}",
            complexity=2.5 + len(str(abs(q))) * 0.2,
            terms_tested=N,
            valid_from_index=start_index + 2,
            initial_conditions=terms[:2],
            details={"order": 2, "base_q": q, "c1": c1, "c0": c0, "d1": d1, "d0": d0, "e": Fraction(0)},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_q_series(
            candidate=cand,
            base_q=q,
            c1=c1,
            c0=c0,
            d1=d1,
            d0=d0,
            const_e=Fraction(0),
            order=2,
            initial_terms=terms[:2],
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    @staticmethod
    def _solve_linear_system(
        matrix: List[List[Fraction]],
        b: List[Fraction],
    ) -> Optional[List[Fraction]]:
        n = len(matrix)
        aug = [list(matrix[i]) + [b[i]] for i in range(n)]

        for col in range(n):
            pivot = None
            for row in range(col, n):
                if aug[row][col] != 0:
                    pivot = row
                    break
            if pivot is None:
                return None

            aug[col], aug[pivot] = aug[pivot], aug[col]
            pv = aug[col][col]
            for j in range(col, n + 1):
                aug[col][j] /= pv

            for row in range(n):
                if row != col and aug[row][col] != 0:
                    f = aug[row][col]
                    for j in range(col, n + 1):
                        aug[row][j] -= f * aug[col][j]

        return [aug[i][n] for i in range(n)]
