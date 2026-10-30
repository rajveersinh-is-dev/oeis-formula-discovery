"""
Algebraic Generating Function Discovery Module (Hermite-Padé Approximants).
Discovers exact algebraic curve equations satisfied by generating functions:
A_2(x) * G(x)^2 + A_1(x) * G(x) + A_0(x) = 0
where A_i(x) are integer polynomials in x.

Captures iconic non-rational combinatorial sequence families:
- Catalan numbers (A000108): x*G(x)^2 - G(x) + 1 = 0  => G(x) = (1 - sqrt(1 - 4x))/(2x)
- Motzkin numbers (A001006): x^2*G(x)^2 + (x - 1)*G(x) + 1 = 0
- Large Schröder numbers (A006318): x*G(x)^2 + (x - 1)*G(x) + 1 = 0
- Noncrossing trees & polygon triangulations

All linear algebra is solved exactly over Fractions (Zero floating-point).
"""

from fractions import Fraction
import math
from typing import List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class AlgebraicGeneratingFunctionDiscovery(DiscoveryMethod):
    def __init__(self, max_degree: int = 2):
        self.max_degree = max_degree

    @property
    def name(self) -> str:
        return "algebraic_generating_function"

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

        # Compute G(x)^2 = sum b(n) x^n
        b = [0] * N
        for i in range(N):
            ai = terms[i]
            if ai != 0:
                for j in range(N - i):
                    b[i + j] += ai * terms[j]

        # Search degree configurations (d2, d1, d0)
        # Order by total degree for parsimony
        configs = [
            (1, 0, 0),  # x*G^2 - G + 1 = 0 (Catalan)
            (1, 1, 0),  # Large Schroder
            (2, 1, 0),  # Motzkin
            (2, 2, 0),
            (2, 2, 1),
        ]

        for d2, d1, d0 in configs:
            if d2 > self.max_degree or d1 > self.max_degree:
                continue

            M = (d2 + 1) + (d1 + 1) + (d0 + 1)
            if N < M + 4:
                continue

            cand = self._fit_algebraic(a_number, terms, b, start_index, d2, d1, d0)
            if cand:
                candidates.append(cand)
                break  # Return lowest degree representation

        return candidates

    def _fit_algebraic(
        self,
        a_number: str,
        a: List[int],
        b: List[int],
        start_index: int,
        d2: int,
        d1: int,
        d0: int,
    ) -> Optional[CandidateFormula]:
        N = len(a)
        M = (d2 + 1) + (d1 + 1) + (d0 + 1)

        # Build equations for n = 0 .. M + 2
        num_eqs = min(N, M + 3)
        rows: List[List[Fraction]] = []

        for n in range(num_eqs):
            row = []
            # A_2(x) coefficients c_{2, 0} .. c_{2, d2}
            for deg in range(d2 + 1):
                row.append(Fraction(b[n - deg] if n >= deg else 0))
            # A_1(x) coefficients c_{1, 0} .. c_{1, d1}
            for deg in range(d1 + 1):
                row.append(Fraction(a[n - deg] if n >= deg else 0))
            # A_0(x) coefficients c_{0, 0} .. c_{0, d0}
            for deg in range(d0 + 1):
                row.append(Fraction(1 if n == deg else 0))
            rows.append(row)

        nulls = self._compute_rational_nullspace(rows)
        if not nulls:
            return None

        # Pick first non-trivial null vector
        for null_vec in nulls:
            # Clear denominators to integers
            lcm_val = 1
            for val in null_vec:
                lcm_val = (lcm_val * val.denominator) // math.gcd(lcm_val, val.denominator)

            int_vec = [int(val * lcm_val) for val in null_vec]

            # Divide by gcd
            gcd_val = 0
            for v in int_vec:
                gcd_val = math.gcd(gcd_val, abs(v))
            if gcd_val > 0:
                int_vec = [v // gcd_val for v in int_vec]

            poly_a2 = int_vec[: d2 + 1]
            poly_a1 = int_vec[d2 + 1 : d2 + 1 + d1 + 1]
            poly_a0 = int_vec[d2 + 1 + d1 + 1 :]

            # A_2(x) must not be zero (otherwise purely linear/rational)
            if all(c == 0 for c in poly_a2):
                continue
            # A_1(x) or A_0(x) must not be zero
            if all(c == 0 for c in poly_a0) and all(c == 0 for c in poly_a1):
                continue

            # Standardize sign: A_0 constant term > 0 if non-zero, else highest A_2 > 0
            if poly_a0 and poly_a0[0] < 0:
                poly_a2 = [-c for c in poly_a2]
                poly_a1 = [-c for c in poly_a1]
                poly_a0 = [-c for c in poly_a0]

            formula_str = self._format_algebraic_equation(poly_a2, poly_a1, poly_a0)
            complexity = float((d2 + d1 + d0 + 2) * 1.8 + sum(len(str(abs(c))) for c in int_vec))

            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=formula_str,
                description=f"Algebraic generating function quadratic in G(x): {formula_str}",
                complexity=complexity,
                terms_tested=len(a),
                valid_from_index=start_index,
                details={
                    "poly_a2": poly_a2,
                    "poly_a1": poly_a1,
                    "poly_a0": poly_a0,
                },
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            is_valid, matched, msg = Verifier.verify_algebraic_generating_function(
                candidate=cand,
                poly_a2=poly_a2,
                poly_a1=poly_a1,
                poly_a0=poly_a0,
                all_terms=a,
                start_index=start_index,
            )

            if is_valid:
                cand.verification_status = VerificationStatus.EXACT_MATCH
                cand.terms_tested = matched
                return cand

        return None

    @staticmethod
    def _compute_rational_nullspace(matrix: List[List[Fraction]]) -> List[List[Fraction]]:
        """Computes basis vectors for right nullspace of matrix over Fractions."""
        r = len(matrix)
        c = len(matrix[0])
        A = [list(matrix[i]) for i in range(r)]

        lead = 0
        pivots = []
        for col in range(c):
            pivot_row = None
            for row in range(lead, r):
                if A[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row is None:
                continue

            A[lead], A[pivot_row] = A[pivot_row], A[lead]
            pv = A[lead][col]
            for j in range(c):
                A[lead][j] /= pv

            for i in range(r):
                if i != lead and A[i][col] != 0:
                    f = A[i][col]
                    for j in range(c):
                        A[i][j] -= f * A[lead][j]

            pivots.append(col)
            lead += 1
            if lead == r:
                break

        free_cols = [j for j in range(c) if j not in pivots]
        null_vectors = []

        for free in free_cols:
            vec = [Fraction(0)] * c
            vec[free] = Fraction(1)
            for i, p in enumerate(pivots):
                vec[p] = -A[i][free]
            null_vectors.append(vec)

        return null_vectors

    @staticmethod
    def _format_poly(poly: List[int]) -> str:
        """Formats polynomial in x."""
        terms = []
        for p, c in enumerate(poly):
            if c == 0:
                continue
            if p == 0:
                core = f"{abs(c)}"
            elif p == 1:
                core = "x" if abs(c) == 1 else f"{abs(c)}*x"
            else:
                core = f"x^{p}" if abs(c) == 1 else f"{abs(c)}*x^{p}"
            terms.append((1 if c > 0 else -1, core))

        if not terms:
            return "0"

        first_sign, first_core = terms[0]
        prefix = "" if first_sign > 0 else "-"
        parts = [f"{prefix}{first_core}"]
        for sign, core in terms[1:]:
            parts.append(f" + {core}" if sign > 0 else f" - {core}")
        return "".join(parts)

    @classmethod
    def _format_algebraic_equation(
        cls,
        poly_a2: List[int],
        poly_a1: List[int],
        poly_a0: List[int],
    ) -> str:
        s2 = cls._format_poly(poly_a2)
        s1 = cls._format_poly(poly_a1)
        s0 = cls._format_poly(poly_a0)

        parts = []
        # A_2(x)*G(x)^2
        if s2 not in ("0", ""):
            if s2 == "1":
                parts.append("G(x)^2")
            elif s2 == "x" or s2.startswith("x^"):
                parts.append(f"{s2}*G(x)^2")
            elif "+" in s2 or "-" in s2:
                parts.append(f"({s2})*G(x)^2")
            else:
                parts.append(f"{s2}*G(x)^2")

        # A_1(x)*G(x)
        if s1 not in ("0", ""):
            if s1 == "1":
                parts.append("+ G(x)")
            elif s1 == "-1":
                parts.append("- G(x)")
            elif s1 == "x" or s1.startswith("x^"):
                parts.append(f"+ {s1}*G(x)")
            elif s1 == "-x":
                parts.append("- x*G(x)")
            elif "+" in s1 or "-" in s1:
                parts.append(f"+ ({s1})*G(x)")
            else:
                parts.append(f"+ {s1}*G(x)")

        # A_0(x)
        if s0 not in ("0", ""):
            if s0.startswith("-"):
                parts.append(f"- {s0[1:]}")
            else:
                parts.append(f"+ {s0}")

        eq_lhs = " ".join(parts).replace("+ -", "- ")
        if eq_lhs.startswith("+ "):
            eq_lhs = eq_lhs[2:]

        return f"{eq_lhs} = 0"
