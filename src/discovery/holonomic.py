"""
Exact Holonomic (P-finite / D-finite) Recurrence Discovery.
Discovers polynomial-coefficient recurrences of the form:
sum_{i=0}^R p_i(n) * a(n-i) = 0
where p_i(n) are polynomials with integer coefficients.
Solves exact rational nullspace systems over Q, clears denominators, and verifies across 100% of available terms.
"""

from fractions import Fraction
import math
from typing import List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class HolonomicDiscovery(DiscoveryMethod):
    def __init__(self, max_order: int = 4, max_degree: int = 3):
        self.max_order = max_order
        self.max_degree = max_degree

        # Candidate order (R) and polynomial degree (D) configurations ordered by parsimony
        self.configurations: List[Tuple[int, int]] = [
            (1, 1),
            (1, 2),
            (2, 1),
            (2, 2),
            (3, 1),
            (2, 3),
            (3, 2),
            (4, 1),
        ]

    @property
    def name(self) -> str:
        return "holonomic"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 10:
            return results

        # Try configurations in increasing order of complexity
        for R, D in self.configurations:
            if R > self.max_order or D > self.max_degree:
                continue

            num_unknowns = (R + 1) * (D + 1)
            # Require at least 4 overdetermining equations
            min_terms_required = R + num_unknowns + 4
            if len(terms) < min_terms_required:
                continue

            candidate = self._search_order_degree(a_num, terms, start_index, R, D)
            if candidate is not None:
                results.append(candidate)
                # Once a minimal order and degree recurrence is found, don't keep searching higher redundant orders
                break

        return results

    def _search_order_degree(
        self,
        a_num: str,
        terms: List[int],
        start_index: int,
        R: int,
        D: int
    ) -> Optional[CandidateFormula]:
        cols = (R + 1) * (D + 1)
        matrix: List[List[Fraction]] = []

        # Build linear system from prefix of terms
        max_eqs = min(len(terms) - R, cols + 8)
        for t in range(max_eqs):
            n_val = start_index + R + t
            row: List[Fraction] = []
            for shift in range(R + 1):
                term_val = terms[R + t - shift]
                pow_n = 1
                for deg in range(D + 1):
                    row.append(Fraction(pow_n * term_val))
                    pow_n *= n_val
            matrix.append(row)

        null_basis = self._get_nullspace_basis(matrix, len(matrix), cols)
        if not null_basis:
            return None

        # Look for a non-trivial solution vector where p_0(n) != 0 and p_R(n) != 0
        for vec in null_basis:
            # Check p_0 coefficients (indices 0..D) and p_R coefficients (indices R*(D+1)..(R+1)*(D+1)-1)
            p0_raw = vec[:D + 1]
            pR_raw = vec[R * (D + 1):(R + 1) * (D + 1)]

            if all(c == 0 for c in p0_raw) or all(c == 0 for c in pR_raw):
                continue

            # Clear denominators to integer vector
            int_vec = self._to_coprime_integers(vec)
            if int_vec is None:
                continue

            # Reshape into polynomials [p_0, p_1, ..., p_R]
            poly_coeffs: List[List[int]] = []
            for shift in range(R + 1):
                p_c = int_vec[shift * (D + 1):(shift + 1) * (D + 1)]
                # Strip trailing zeros
                while len(p_c) > 1 and p_c[-1] == 0:
                    p_c.pop()
                poly_coeffs.append(p_c)

            # Ensure leading coefficient of p_0 is positive
            if poly_coeffs[0][-1] < 0:
                poly_coeffs = [[-c for c in p] for p in poly_coeffs]

            # Require that at least one polynomial has degree >= 1
            if all(len(p) <= 1 for p in poly_coeffs):
                # Pure constant-coefficient recurrence; handled by linear_recurrence module
                continue

            # Check that actual order is R (i.e. p_R is not identically 0)
            if not any(c != 0 for c in poly_coeffs[-1]):
                continue

            # Exact verification against 100% of all available terms
            initial_terms = terms[:R]
            is_exact, matched, err = Verifier.verify_holonomic_recurrence(
                CandidateFormula(),
                poly_coeffs,
                initial_terms,
                terms,
                start_index
            )

            if not is_exact or matched < len(terms):
                continue

            # Format formula string and LaTeX string
            formula_str, latex_str = self._format_recurrence(poly_coeffs, initial_terms, start_index)
            actual_max_deg = max(len(p) - 1 for p in poly_coeffs)

            total_bits = sum(len(str(abs(c))) for p in poly_coeffs for c in p)
            complexity = 3.0 + (R * 1.5) + (actual_max_deg * 1.2) + (total_bits * 0.05)

            return CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str=formula_str,
                latex_str=latex_str,
                description=f"Exact holonomic (P-finite) recurrence of order {R} and polynomial degree {actual_max_deg}",
                complexity=complexity,
                terms_tested=matched,
                verification_status=VerificationStatus.EXACT_MATCH,
                initial_conditions=initial_terms,
                valid_from_index=start_index + R,
                details={
                    "order": R,
                    "max_degree": actual_max_deg,
                    "polynomial_coefficients": poly_coeffs
                }
            )

        return None

    @staticmethod
    def _get_nullspace_basis(matrix: List[List[Fraction]], rows: int, cols: int) -> List[List[Fraction]]:
        """Exact Gauss-Jordan elimination to RREF over Q to extract nullspace basis."""
        mat = [list(r) for r in matrix]
        pivot_row = 0
        pivots = {}

        for col in range(cols):
            sel = None
            for r in range(pivot_row, rows):
                if mat[r][col] != 0:
                    sel = r
                    break
            if sel is None:
                continue

            mat[pivot_row], mat[sel] = mat[sel], mat[pivot_row]
            pv = mat[pivot_row][col]
            mat[pivot_row] = [x / pv for x in mat[pivot_row]]

            for r in range(rows):
                if r != pivot_row and mat[r][col] != 0:
                    factor = mat[r][col]
                    mat[r] = [mat[r][c] - factor * mat[pivot_row][c] for c in range(cols)]

            pivots[col] = pivot_row
            pivot_row += 1

        null_basis = []
        free_cols = [c for c in range(cols) if c not in pivots]
        for fc in free_cols:
            vec = [Fraction(0)] * cols
            vec[fc] = Fraction(1)
            for pc, pr in pivots.items():
                vec[pc] = -mat[pr][fc]
            null_basis.append(vec)

        return null_basis

    @staticmethod
    def _to_coprime_integers(vec: List[Fraction]) -> Optional[List[int]]:
        """Clears denominators and divides by gcd to produce minimal integer vector."""
        if all(x == 0 for x in vec):
            return None

        # Compute LCM of denominators
        lcm_denom = 1
        for x in vec:
            d = x.denominator
            lcm_denom = (lcm_denom * d) // math.gcd(lcm_denom, d)

        int_vec = [int(x * lcm_denom) for x in vec]

        # Divide by overall GCD
        common_gcd = 0
        for val in int_vec:
            common_gcd = math.gcd(common_gcd, abs(val))

        if common_gcd > 0:
            int_vec = [val // common_gcd for val in int_vec]

        return int_vec

    @staticmethod
    def _format_poly(coeffs: List[int], var: str = "n") -> str:
        """Formats polynomial list [c_0, c_1, ...] into human readable polynomial string."""
        while len(coeffs) > 1 and coeffs[-1] == 0:
            coeffs = coeffs[:-1]
        if not coeffs or (len(coeffs) == 1 and coeffs[0] == 0):
            return "0"

        terms = []
        for deg in range(len(coeffs) - 1, -1, -1):
            c = coeffs[deg]
            if c == 0:
                continue
            if deg == 0:
                terms.append(f"{c}")
            elif deg == 1:
                if c == 1:
                    terms.append(var)
                elif c == -1:
                    terms.append(f"-{var}")
                else:
                    terms.append(f"{c}*{var}")
            else:
                if c == 1:
                    terms.append(f"{var}^{deg}")
                elif c == -1:
                    terms.append(f"-{var}^{deg}")
                else:
                    terms.append(f"{c}*{var}^{deg}")

        res = terms[0]
        for t in terms[1:]:
            if t.startswith("-"):
                res += " - " + t[1:]
            else:
                res += " + " + t
        return res

    def _format_recurrence(
        self,
        poly_coeffs: List[List[int]],
        initial_terms: List[int],
        start_index: int
    ) -> Tuple[str, str]:
        """Formats polynomial recurrence as text and LaTeX."""
        terms_str = []
        latex_terms = []

        for shift, poly in enumerate(poly_coeffs):
            if all(c == 0 for c in poly):
                continue
            poly_str = self._format_poly(poly)

            if shift == 0:
                arg = "a(n)"
                arg_ltx = "a(n)"
            else:
                arg = f"a(n-{shift})"
                arg_ltx = f"a(n-{shift})"

            if poly == [1]:
                terms_str.append(arg)
                latex_terms.append(arg_ltx)
            elif poly == [-1]:
                terms_str.append(f"-{arg}")
                latex_terms.append(f"-{arg_ltx}")
            else:
                terms_str.append(f"({poly_str})*{arg}")
                latex_terms.append(f"({poly_str}) {arg_ltx}")

        formula_body = " + ".join(terms_str).replace("+ -", "- ") + " = 0"
        latex_body = " + ".join(latex_terms).replace("+ -", "- ") + " = 0"

        init_parts = [f"a({start_index + i}) = {val}" for i, val in enumerate(initial_terms)]
        init_str = "; with " + ", ".join(init_parts) if init_parts else ""

        return formula_body + init_str, latex_body

