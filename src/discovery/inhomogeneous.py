"""
Inhomogeneous Linear Recurrence Discovery Module.
Discovers exact recurrence relations driven by a polynomial term:
a(n) = sum_{j=1}^k c_j * a(n-j) + P(n)
where P(n) = sum_{i=0}^d b_i * n^i with b_i in Q (integer-valued polynomial).

Examples:
- Tower of Hanoi (A000225): a(n) = 2*a(n-1) + 1
- Lazy Caterer (A000124): a(n) = a(n-1) + n
- Cake Numbers (A000125): a(n) = a(n-1) + (1/2)*n^2 - (1/2)*n + 1
- Divide-and-conquer comparisons: a(n) = 2*a(n-1) + n

Uses exact rational linear algebra (Gaussian elimination over Fractions).
"""

from fractions import Fraction
import math
from typing import Any, List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class InhomogeneousRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self, max_order: int = 3, max_poly_deg: int = 3):
        self.max_order = max_order
        self.max_poly_deg = max_poly_deg

    @property
    def name(self) -> str:
        return "inhomogeneous_recurrence"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []
        N = len(terms)

        for k in range(1, self.max_order + 1):
            for d in range(0, self.max_poly_deg + 1):
                M = k + (d + 1)  # Number of unknowns: c_1..c_k and b_0..b_d
                min_terms = k + M + 3
                if N < min_terms:
                    continue

                cand = self._fit_inhomogeneous(a_number, terms, start_index, k, d)
                if cand:
                    candidates.append(cand)
                    return candidates  # Return lowest order and degree found

        # Search exponential driving terms: a(n) = sum_{j=1}^k c_j*a(n-j) + b * r^n
        # Dynamically discover candidate bases r from characteristic polynomial roots
        candidate_bases = self._find_candidate_bases(terms)
        for r in candidate_bases:
            if abs(r) < 2:
                continue
            for k in range(1, min(self.max_order + 1, 3)):
                cand_exp = self._fit_exponential(a_number, terms, start_index, k, r)
                if cand_exp:
                    candidates.append(cand_exp)
                    return candidates

        return candidates

    def _find_candidate_bases(self, terms: List[int]) -> List[int]:
        """Finds candidate bases r by finding integer roots of the sequence's minimal annihilating polynomial."""
        from .linear_recurrence import LinearRecurrenceDiscovery
        fallback = [2, -2, 3, -3, 4, -4, 5, -5, 6, 7, 10]
        frac_terms = [Fraction(t) for t in terms]
        coeffs = LinearRecurrenceDiscovery._berlekamp_massey(frac_terms)
        bases = []
        if coeffs and len(coeffs) <= self.max_order + 1 and all(c.denominator == 1 for c in coeffs):
            int_c = [c.numerator for c in coeffs]
            m = len(int_c)
            # Characteristic polynomial: x^m - sum_{j=1}^m c_j * x^{m-j} = 0
            # Root must divide trailing non-zero coefficient
            trailing = int_c[-1]
            if trailing != 0:
                abs_t = abs(trailing)
                divs = []
                limit = min(1000, math.isqrt(abs_t))
                for d in range(1, limit + 1):
                    if abs_t % d == 0:
                        divs.append(d)
                        other = abs_t // d
                        if other <= 1000:
                            divs.append(other)
                # Check each divisor as candidate root
                for div in divs:
                    for sign in (1, -1):
                        r_test = sign * div
                        val = r_test ** m - sum(c * (r_test ** (m - j)) for j, c in enumerate(int_c, 1))
                        if val == 0 and r_test not in bases:
                            bases.append(r_test)

        # Include standard fallback bases
        for b in fallback:
            if b not in bases:
                bases.append(b)
        return bases

    def _fit_inhomogeneous(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        k: int,
        d: int,
    ) -> Optional[CandidateFormula]:
        M = k + (d + 1)
        matrix = []
        b_vec = []

        # System of M equations for n from start_index + k to start_index + k + M - 1
        for row_idx in range(M):
            i = k + row_idx
            n_val = start_index + i
            row = []
            # Recurrence coefficients c_1 .. c_k
            for j in range(1, k + 1):
                row.append(Fraction(terms[i - j]))
            # Polynomial coefficients b_0 .. b_d
            curr_pow = 1
            for p in range(d + 1):
                row.append(Fraction(curr_pow))
                curr_pow *= n_val

            matrix.append(row)
            b_vec.append(Fraction(terms[i]))

        solution = self._solve_linear_system(matrix, b_vec)
        if solution is None:
            return None

        rec_sol = solution[:k]
        poly_sol = solution[k:]

        # Recurrence coefficients must be integers
        if any(c.denominator != 1 for c in rec_sol):
            return None

        # Polynomial coefficients: denominators must divide 24 (covering binomial coefficients binom(n, 2), binom(n, 3))
        lcm_denom = 1
        for b in poly_sol:
            lcm_denom = (lcm_denom * b.denominator) // math.gcd(lcm_denom, b.denominator)

        if 24 % lcm_denom != 0:
            return None

        # Must have at least one non-zero polynomial term (otherwise purely homogeneous)
        if all(c == 0 for c in poly_sol):
            return None

        int_rec = [c.numerator for c in rec_sol]

        # Format formula string
        initial_terms = terms[:k]
        formula_str = self._format_inhomogeneous(int_rec, poly_sol, initial_terms, start_index)
        complexity = float(k * 2.0 + (d + 1) * 1.5 + sum(len(str(abs(c))) for c in int_rec))

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            description=f"Inhomogeneous linear recurrence of order {k} with driving polynomial of degree {d}",
            complexity=complexity,
            terms_tested=len(terms),
            valid_from_index=start_index,
            initial_conditions=initial_terms,
            recurrence_coeffs=int_rec,
            details={
                "order_k": k,
                "poly_degree": d,
                "rec_coeffs": int_rec,
                "poly_coeffs": poly_sol,
                "initial_terms": initial_terms,
            },
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_inhomogeneous_recurrence(
            candidate=cand,
            rec_coeffs=int_rec,
            poly_coeffs=poly_sol,
            initial_terms=initial_terms,
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _fit_exponential(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        k: int,
        r: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n) = sum_{j=1}^k c_j*a(n-j) + b * r^n."""
        M = k + 1
        if len(terms) < k + M + 3:
            return None

        matrix = []
        b_vec = []
        for row_idx in range(M):
            i = k + row_idx
            n_val = start_index + i
            row = []
            for j in range(1, k + 1):
                row.append(Fraction(terms[i - j]))
            row.append(Fraction(r ** n_val))
            matrix.append(row)
            b_vec.append(Fraction(terms[i]))

        solution = self._solve_linear_system(matrix, b_vec)
        if solution is None:
            return None

        if any(c.denominator != 1 for c in solution):
            return None

        int_rec = [c.numerator for c in solution[:k]]
        b_coeff = solution[k].numerator

        if b_coeff == 0:
            return None

        initial_terms = terms[:k]
        rec_parts = []
        for j, c in enumerate(int_rec, 1):
            if c == 1:
                rec_parts.append(f"+ a(n-{j})" if rec_parts else f"a(n-{j})")
            elif c == -1:
                rec_parts.append(f"- a(n-{j})" if rec_parts else f"-a(n-{j})")
            elif c > 0:
                rec_parts.append(f"+ {c}*a(n-{j})" if rec_parts else f"{c}*a(n-{j})")
            elif c < 0:
                rec_parts.append(f"- {abs(c)}*a(n-{j})" if rec_parts else f"{c}*a(n-{j})")

        exp_str = f"{r}^n" if r > 0 else f"({r})^n"
        if b_coeff == 1:
            rec_parts.append(f"+ {exp_str}" if rec_parts else exp_str)
        elif b_coeff == -1:
            rec_parts.append(f"- {exp_str}" if rec_parts else f"-{exp_str}")
        elif b_coeff > 0:
            rec_parts.append(f"+ {b_coeff}*{exp_str}" if rec_parts else f"{b_coeff}*{exp_str}")
        else:
            rec_parts.append(f"- {abs(b_coeff)}*{exp_str}" if rec_parts else f"-{abs(b_coeff)}*{exp_str}")

        rec_str = " ".join(rec_parts)
        init_str = ", ".join(f"a({start_index + i}) = {terms[i]}" for i in range(k))
        formula_str = f"a(n) = {rec_str}; with {init_str}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            description=f"Inhomogeneous linear recurrence of order {k} with exponential driving term {b_coeff}*({r}^n)",
            complexity=float(k * 2.0 + 3.0 + len(str(abs(b_coeff)))),
            terms_tested=len(terms),
            valid_from_index=start_index,
            initial_conditions=initial_terms,
            recurrence_coeffs=int_rec,
            details={"order_k": k, "exp_base": r, "exp_coeff": b_coeff, "rec_coeffs": int_rec},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_inhomogeneous_exponential(
            candidate=cand,
            rec_coeffs=int_rec,
            exp_base=r,
            exp_coeff=b_coeff,
            initial_terms=initial_terms,
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
        """Solves square linear system Ax = b over Fractions using Gaussian elimination."""
        n = len(matrix)
        aug = [list(matrix[i]) + [b[i]] for i in range(n)]

        for col in range(n):
            pivot_row = None
            for row in range(col, n):
                if aug[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row is None:
                return None

            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            pv = aug[col][col]
            for j in range(col, n + 1):
                aug[col][j] /= pv

            for row in range(n):
                if row != col and aug[row][col] != 0:
                    f = aug[row][col]
                    for j in range(col, n + 1):
                        aug[row][j] -= f * aug[col][j]

        return [aug[i][n] for i in range(n)]

    @staticmethod
    def _format_inhomogeneous(
        rec_coeffs: List[int],
        poly_coeffs: List[Any],
        initial_terms: List[int],
        start_index: int,
    ) -> str:
        parts = []

        # Recurrence part
        for j, c in enumerate(rec_coeffs, 1):
            if c == 0:
                continue
            if c == 1:
                parts.append((1, f"a(n-{j})"))
            elif c == -1:
                parts.append((-1, f"a(n-{j})"))
            else:
                parts.append((1 if c > 0 else -1, f"{abs(c)}*a(n-{j})"))

        # Polynomial part
        for p, c in enumerate(poly_coeffs):
            if c == 0:
                continue
            sign = 1 if c > 0 else -1
            abs_c = abs(c)

            if p == 0:
                core = f"{abs_c}"
            elif p == 1:
                if abs_c == 1:
                    core = "n"
                elif abs_c.denominator == 1:
                    core = f"{abs_c.numerator}*n"
                else:
                    core = f"({abs_c})*n"
            else:
                if abs_c == 1:
                    core = f"n^{p}"
                elif abs_c.denominator == 1:
                    core = f"{abs_c.numerator}*n^{p}"
                else:
                    core = f"({abs_c})*n^{p}"
            parts.append((sign, core))

        if not parts:
            rhs = "0"
        else:
            first_sign, first_core = parts[0]
            prefix = "" if first_sign > 0 else "-"
            str_parts = [f"{prefix}{first_core}"]
            for sign, core in parts[1:]:
                op = " + " if sign > 0 else " - "
                str_parts.append(f"{op}{core}")
            rhs = "".join(str_parts)

        k = len(initial_terms)
        init_str = ", ".join(f"a({start_index + j}) = {v}" for j, v in enumerate(initial_terms))
        return f"a(n) = {rhs}; with {init_str}"
