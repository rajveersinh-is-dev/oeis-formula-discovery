"""
Algebraic Generating Function Discovery Module (Hermite-Padé Approximants).
Discovers exact algebraic curve equations satisfied by generating functions:
sum_{j=0}^D A_j(x) * G(x)^j = 0
where A_j(x) are integer polynomials in x.

Captures iconic non-rational combinatorial sequence families:
- Catalan numbers (A000108): x*G(x)^2 - G(x) + 1 = 0
- Motzkin numbers (A001006): x^2*G(x)^2 + (x - 1)*G(x) + 1 = 0
- Large Schröder numbers (A006318): x*G(x)^2 + (x - 1)*G(x) + 1 = 0
- Ternary trees / 3-Catalan numbers (A001764): x*G(x)^3 - G(x) + 1 = 0
- 4-ary trees / 4-Catalan numbers (A002293): x*G(x)^4 - G(x) + 1 = 0
- Noncrossing trees, polygon triangulations, planar maps

All linear algebra is solved exactly over Fractions (Zero floating-point).
"""

from fractions import Fraction
import math
from typing import List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class AlgebraicGeneratingFunctionDiscovery(DiscoveryMethod):
    def __init__(self, max_degree: int = 4):
        self.max_degree = max_degree

    @staticmethod
    def _generate_configs(D: int, max_total_deg: int) -> List[Tuple[int, ...]]:
        """Dynamically generates all degree profiles (d_D, ..., d_0) ordered by parsimony."""
        results: List[Tuple[int, ...]] = []

        def backtrack(idx: int, rem_sum: int, current: List[int]):
            if idx == D + 1:
                if sum(current) == total_deg:
                    results.append(tuple(current))
                return
            max_d = 3 if idx == 0 else 2
            for d in range(min(rem_sum, max_d) + 1):
                backtrack(idx + 1, rem_sum - d, current + [d])

        for total_deg in range(1, max_total_deg + 1):
            backtrack(0, total_deg, [])
        results.sort(key=lambda cfg: (sum(cfg), max(cfg)))
        return results

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

        max_D = min(self.max_degree, 4)

        # Compute G(x)^j = sum g_{j, n} x^n for j = 0 .. max_D
        G_powers: List[List[int]] = [[0] * N for _ in range(max_D + 1)]
        G_powers[0][0] = 1
        for i in range(N):
            G_powers[1][i] = terms[i]

        for j in range(2, max_D + 1):
            prev = G_powers[j - 1]
            curr = G_powers[j]
            for i in range(N):
                ai = terms[i]
                if ai != 0:
                    for k in range(N - i):
                        curr[i + k] += ai * prev[k]

        # Search configurations grouped by degree in G(x) from D=2 to max_D
        for D in range(2, max_D + 1):
            max_total = 4 if D == 2 else (3 if D == 3 else 2)
            configs = self._generate_configs(D, max_total)

            for cfg in configs:
                M = sum(d + 1 for d in cfg)
                if N < M + 4:
                    continue

                cand = self._fit_algebraic(a_number, terms, G_powers, start_index, cfg)
                if cand:
                    candidates.append(cand)
                    return candidates  # Return lowest degree representation

        return candidates

    def _fit_algebraic(
        self,
        a_number: str,
        a: List[int],
        G_powers: List[List[int]],
        start_index: int,
        deg_profile: Tuple[int, ...],
    ) -> Optional[CandidateFormula]:
        D = len(deg_profile) - 1
        M = sum(d + 1 for d in deg_profile)
        num_eqs = min(len(a), M + 4)
        rows: List[List[Fraction]] = []

        for n in range(num_eqs):
            row: List[Fraction] = []
            for j in range(D, -1, -1):
                deg_j = deg_profile[D - j]
                gj = G_powers[j]
                for p in range(deg_j + 1):
                    val = gj[n - p] if n >= p else 0
                    row.append(Fraction(val))
            rows.append(row)

        nulls = self._compute_rational_nullspace(rows)
        if not nulls:
            return None

        # Pick first valid non-trivial null vector
        for null_vec in nulls:
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

            # Split into polynomial coefficients: A_D(x), ..., A_0(x)
            polys_desc: List[List[int]] = []
            offset = 0
            for d in deg_profile:
                polys_desc.append(int_vec[offset : offset + d + 1])
                offset += d + 1

            # polys_desc is [A_D, A_{D-1}, ..., A_0]
            poly_AD = polys_desc[0]
            poly_A0 = polys_desc[-1]

            # A_D(x) must not be identically zero
            if all(c == 0 for c in poly_AD):
                continue
            # A_0(x) must not be identically zero (otherwise G(x) is a factor)
            if all(c == 0 for c in poly_A0):
                continue

            # Standardize sign: make A_0 constant term > 0 if non-zero,
            # else first non-zero of A_0 > 0, else leading of A_D > 0
            sign_flip = False
            first_nonzero_a0 = next((c for c in poly_A0 if c != 0), 0)
            if first_nonzero_a0 < 0:
                sign_flip = True
            elif first_nonzero_a0 == 0:
                last_nonzero_ad = next((c for c in reversed(poly_AD) if c != 0), 0)
                if last_nonzero_ad < 0:
                    sign_flip = True

            if sign_flip:
                polys_desc = [[-c for c in p] for p in polys_desc]
                int_vec = [-v for v in int_vec]

            # Convert to [A_0, A_1, ..., A_D] for verifier
            polys_asc = list(reversed(polys_desc))

            formula_str = self._format_general_equation(polys_desc)
            complexity = float((sum(deg_profile) + D) * 1.8 + sum(len(str(abs(c))) for c in int_vec))

            details = {
                "poly_coeffs": polys_asc,
                "degree_G": D,
            }
            if D == 2:
                details["poly_a2"] = polys_desc[0]
                details["poly_a1"] = polys_desc[1]
                details["poly_a0"] = polys_desc[2]
            elif D >= 3:
                details["poly_a2"] = polys_asc[2] if len(polys_asc) > 2 else [0]
                details["poly_a1"] = polys_asc[1] if len(polys_asc) > 1 else [0]
                details["poly_a0"] = polys_asc[0]

            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=formula_str,
                description=f"Algebraic generating function of degree {D} in G(x): {formula_str}",
                complexity=complexity,
                terms_tested=len(a),
                valid_from_index=start_index,
                details=details,
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            is_valid, matched, msg = Verifier.verify_algebraic_generating_function(
                candidate=cand,
                poly_coeffs=polys_asc,
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
    def _format_general_equation(cls, polys_desc: List[List[int]]) -> str:
        """Formats sum_{j=0}^D A_j(x) * G(x)^j = 0."""
        D = len(polys_desc) - 1
        parts = []

        for idx, poly in enumerate(polys_desc):
            j = D - idx
            s = cls._format_poly(poly)
            if s in ("0", ""):
                continue

            if j == 0:
                if s.startswith("-"):
                    parts.append(f"- {s[1:]}")
                else:
                    parts.append(f"+ {s}")
            elif j == 1:
                if s == "1":
                    parts.append("+ G(x)")
                elif s == "-1":
                    parts.append("- G(x)")
                elif s == "x" or s.startswith("x^"):
                    parts.append(f"+ {s}*G(x)")
                elif s == "-x":
                    parts.append("- x*G(x)")
                elif "+" in s or "-" in s:
                    parts.append(f"+ ({s})*G(x)")
                else:
                    parts.append(f"+ {s}*G(x)")
            else:
                g_str = f"G(x)^{j}"
                if s == "1":
                    parts.append(f"+ {g_str}")
                elif s == "-1":
                    parts.append(f"- {g_str}")
                elif s == "x" or s.startswith("x^"):
                    parts.append(f"+ {s}*{g_str}")
                elif s == "-x":
                    parts.append(f"- x*{g_str}")
                elif "+" in s or "-" in s:
                    parts.append(f"+ ({s})*{g_str}")
                else:
                    parts.append(f"+ {s}*{g_str}")

        eq_lhs = " ".join(parts).replace("+ -", "- ")
        if eq_lhs.startswith("+ "):
            eq_lhs = eq_lhs[2:]

        return f"{eq_lhs} = 0"
