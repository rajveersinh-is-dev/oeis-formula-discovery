"""
Nonlinear & Bilinear Recurrence Discovery Module.
Discovers exact non-linear recurrence relations for sequence families that cannot
be captured by linear or holonomic models:
1. Univariate Polynomial Recurrences:
   a(n) = P(a(n-1)) = c_d * a(n-1)^d + ... + c_1 * a(n-1) + c_0
   e.g. Sylvester's sequence (A000058): a(n) = a(n-1)^2 - a(n-1) + 1
   Fermat-like sequences: a(n) = (a(n-1) - 1)^2 + 1
   Tree height sequences (A001699): a(n) = a(n-1)^2 + 1
2. Bilinear / Somos-type Recurrences:
   a(n) * a(n-k) = sum_{j=1}^m c_j * a(n-j) * a(n-k+j) where m = floor(k / 2)
   e.g. Somos-4 (A006720): a(n)*a(n-4) = a(n-1)*a(n-3) + a(n-2)^2
   Somos-5 (A006721): a(n)*a(n-5) = a(n-1)*a(n-4) + a(n-2)*a(n-3)
   Somos-6 (A006722): a(n)*a(n-6) = a(n-1)*a(n-5) + a(n-2)*a(n-4) + a(n-3)^2

All solvers use exact Fraction arithmetic (Zero floating-point approximations).
"""

from fractions import Fraction
from typing import List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class NonlinearRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self, max_degree: int = 3, max_somos_k: int = 6):
        self.max_degree = max_degree
        self.max_somos_k = max_somos_k

    @property
    def name(self) -> str:
        return "nonlinear_recurrence"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []

        # 1. Search for univariate polynomial recurrences a(n) = P(a(n-1))
        poly_cand = self._discover_poly_recurrence(a_number, terms, start_index)
        if poly_cand:
            candidates.append(poly_cand)

        # 2. Search for bilinear Somos recurrences
        somos_cands = self._discover_somos_recurrences(a_number, terms, start_index)
        candidates.extend(somos_cands)

        return candidates

    def _discover_poly_recurrence(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """
        Attempts to fit a(n) = sum_{j=0}^d c_j * a(n-1)^j for d in [2, max_degree].
        Requires at least d + 3 points (at least 2 independent verification points).
        """
        if len(terms) < 5:
            return None

        # Check for duplicate consecutive values that would make Vandermonde singular
        for d in range(2, self.max_degree + 1):
            if len(terms) < d + 3:
                continue

            # Need d + 1 distinct transition pairs to determine degree d uniquely
            xs = [terms[i] for i in range(d + 1)]
            ys = [terms[i + 1] for i in range(d + 1)]

            if len(set(xs)) < d + 1:
                # Repeated inputs, not uniquely determined by standard Vandermonde
                continue

            # Set up Vandermonde system: sum_{j=0}^d c_j * x_i^j = y_i
            # Matrix A: (d+1) x (d+1), vector b: (d+1)
            matrix = []
            for x in xs:
                row = [Fraction(x ** j) for j in range(d + 1)]
                matrix.append(row)
            b = [Fraction(y) for y in ys]

            coeffs = self._solve_linear_system(matrix, b)
            if coeffs is None:
                continue

            # Check if all coefficients are integers
            if any(c.denominator != 1 for c in coeffs):
                continue

            int_coeffs = [c.numerator for c in coeffs]
            # Must be true degree d (highest coefficient != 0)
            if int_coeffs[-1] == 0:
                continue

            # Build candidate formula
            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=self._format_poly_recurrence(int_coeffs, terms[0], start_index),
                description=f"Univariate polynomial recurrence of degree {d}",
                details={
                    "poly_coeffs": int_coeffs,
                    "degree": d,
                    "initial_term": terms[0],
                },
                terms_tested=len(terms),
                valid_from_index=start_index,
                complexity=self._compute_poly_complexity(int_coeffs, d),
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            # Strict verification across 100% of terms
            is_valid, matched, msg = Verifier.verify_nonlinear_recurrence(
                candidate=cand,
                poly_coeffs=int_coeffs,
                initial_term=terms[0],
                all_terms=terms,
                start_index=start_index,
            )

            if is_valid:
                cand.verification_status = VerificationStatus.EXACT_MATCH
                cand.terms_tested = matched
                return cand

        return None

    def _discover_somos_recurrences(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> List[CandidateFormula]:
        """
        Attempts to fit bilinear Somos-k recurrences:
        a(n)*a(n-k) = sum_{j=1}^m c_j * a(n-j) * a(n-k+j) where m = floor(k / 2).
        Requires at least k + m + 3 terms for statistical validity.
        """
        results: List[CandidateFormula] = []

        for k in range(3, self.max_somos_k + 1):
            m = k // 2
            min_terms_required = k + m + 3
            if len(terms) < min_terms_required:
                continue

            # Construct system of m equations from n = k to n = k + m - 1
            matrix = []
            b = []
            valid_system = True

            for row_idx in range(m):
                n = k + row_idx
                lhs = terms[n] * terms[n - k]
                row = []
                for j in range(1, m + 1):
                    pair_prod = terms[n - j] * terms[n - k + j]
                    row.append(Fraction(pair_prod))
                matrix.append(row)
                b.append(Fraction(lhs))

            coeffs = self._solve_linear_system(matrix, b)
            if coeffs is None:
                continue

            # Must all be integers
            if any(c.denominator != 1 for c in coeffs):
                continue

            int_coeffs = [c.numerator for c in coeffs]
            # Must not all be zero
            if all(c == 0 for c in int_coeffs):
                continue

            # Initial terms
            initial_terms = terms[:k]

            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=self._format_somos_recurrence(k, int_coeffs, initial_terms, start_index),
                description=f"Bilinear Somos-{k} recurrence relation",
                details={
                    "type": "somos_bilinear",
                    "order_k": k,
                    "coeffs": int_coeffs,
                    "initial_terms": initial_terms,
                },
                terms_tested=len(terms),
                valid_from_index=start_index,
                complexity=float(k * 2 + sum(abs(c) for c in int_coeffs)),
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            is_valid, matched, msg = Verifier.verify_bilinear_recurrence(
                candidate=cand,
                order_k=k,
                coeffs=int_coeffs,
                initial_terms=initial_terms,
                all_terms=terms,
                start_index=start_index,
            )

            if is_valid:
                cand.verification_status = VerificationStatus.EXACT_MATCH
                cand.terms_tested = matched
                results.append(cand)
                break  # Pick minimal k

        return results

    @staticmethod
    def _solve_linear_system(
        matrix: List[List[Fraction]],
        b: List[Fraction],
    ) -> Optional[List[Fraction]]:
        """
        Solves square linear system Ax = b over Fractions using Gaussian elimination.
        Returns solution vector x, or None if singular.
        """
        n = len(matrix)
        # Augment matrix
        aug = [list(matrix[i]) + [b[i]] for i in range(n)]

        for col in range(n):
            # Pivot
            pivot_row = None
            for row in range(col, n):
                if aug[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row is None:
                return None  # Singular

            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            pivot_val = aug[col][col]
            for j in range(col, n + 1):
                aug[col][j] /= pivot_val

            for row in range(n):
                if row != col and aug[row][col] != 0:
                    factor = aug[row][col]
                    for j in range(col, n + 1):
                        aug[row][j] -= factor * aug[col][j]

        return [aug[i][n] for i in range(n)]

    @staticmethod
    def _format_poly_recurrence(coeffs: List[int], initial_term: int, start_idx: int) -> str:
        """Formats a(n) = P(a(n-1)) into readable mathematical string."""
        terms = []
        d = len(coeffs) - 1
        for p in range(d, -1, -1):
            c = coeffs[p]
            if c == 0:
                continue

            sign = " + " if c > 0 else " - "
            abs_c = abs(c)

            if p == 0:
                core = f"{abs_c}"
            elif p == 1:
                core = "a(n-1)" if abs_c == 1 else f"{abs_c}*a(n-1)"
            else:
                core = f"a(n-1)^{p}" if abs_c == 1 else f"{abs_c}*a(n-1)^{p}"

            terms.append((sign, core))

        if not terms:
            body = "0"
        else:
            first_sign, first_core = terms[0]
            prefix = "" if first_sign == " + " else "-"
            parts = [f"{prefix}{first_core}"]
            for sign, core in terms[1:]:
                parts.append(f"{sign}{core}")
            body = "".join(parts)

        return f"a(n) = {body}; with a({start_idx}) = {initial_term}"

    @staticmethod
    def _format_somos_recurrence(
        k: int,
        coeffs: List[int],
        initial_terms: List[int],
        start_idx: int,
    ) -> str:
        """Formats bilinear recurrence a(n)*a(n-k) = sum c_j * a(n-j)*a(n-k+j)."""
        terms = []
        m = len(coeffs)
        for j in range(1, m + 1):
            c = coeffs[j - 1]
            if c == 0:
                continue

            t1 = f"a(n-{j})"
            t2 = f"a(n-{k-j})"
            prod = f"{t1}^2" if j == k - j else f"{t1}*{t2}"
            sign = " + " if c > 0 else " - "
            abs_c = abs(c)
            core = prod if abs_c == 1 else f"{abs_c}*{prod}"
            terms.append((sign, core))

        if not terms:
            body = "0"
        else:
            first_sign, first_core = terms[0]
            prefix = "" if first_sign == " + " else "-"
            parts = [f"{prefix}{first_core}"]
            for sign, core in terms[1:]:
                parts.append(f"{sign}{core}")
            body = "".join(parts)

        init_str = ", ".join(str(v) for v in initial_terms)
        return f"a(n)*a(n-{k}) = {body}; with a({start_idx}..{start_idx+k-1}) = [{init_str}]"

    @staticmethod
    def _compute_poly_complexity(coeffs: List[int], degree: int) -> float:
        return float(degree * 2.0 + sum(len(str(abs(c))) for c in coeffs))
