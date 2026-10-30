"""
Rational & Bilinear Recurrence Discovery Module.
Discovers exact rational and algebraic difference equations:
1. Riccati / First-Order Rational Recurrence:
   a(n) = (p1*a(n-1) + p0) / (q1*a(n-1) + q0)
2. Lyness & Quadratic Second-Order Rational Recurrences:
   a(n) = (c1*a(n-1) + c0) / a(n-2)          (Lyness / Todd)
   a(n) = (c1*a(n-1)^2 + c2*a(n-1) + c0) / a(n-2)
3. General Bilinear / Affine Somos-type Recurrences:
   a(n)*a(n-k) = sum_{j=1}^m c_j * a(n-j)*a(n-k+j) + sum_{j=1}^{k-1} d_j * a(n-j) + c0
4. Second-Order Rational Fraction:
   a(n) = (p1*a(n-1) + p2*a(n-2) + p0) / (q1*a(n-1) + q2*a(n-2) + q0)

All solvers use exact Fraction linear algebra with 100% exact verification.
"""

from fractions import Fraction
import math
from typing import Any, Dict, List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class RationalRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self, max_order: int = 4):
        self.max_order = max_order

    @property
    def name(self) -> str:
        return "rational_recurrence"

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

        # 1. Search for Lyness-type recurrences: a(n)*a(n-2) = c1*a(n-1) + c0
        lyness_cand = self._discover_lyness(a_number, terms, start_index)
        if lyness_cand:
            candidates.append(lyness_cand)
            return candidates

        # 2. Search for Lyness-quadratic: a(n)*a(n-2) = c1*a(n-1)^2 + c2*a(n-1) + c0
        lyness_q_cand = self._discover_lyness_quadratic(a_number, terms, start_index)
        if lyness_q_cand:
            candidates.append(lyness_q_cand)
            return candidates

        # 3. Search for Riccati recurrence: a(n)*(q1*a(n-1) + q0) = p1*a(n-1) + p0
        riccati_cand = self._discover_riccati(a_number, terms, start_index)
        if riccati_cand:
            candidates.append(riccati_cand)
            return candidates

        # 4. Search for general Bilinear Affine recurrences of order k in [2, max_order]
        for k in range(2, self.max_order + 1):
            bilinear_cand = self._discover_bilinear_affine(a_number, terms, start_index, k)
            if bilinear_cand:
                candidates.append(bilinear_cand)
                return candidates

        # 5. Search for second-order rational fraction
        cand_ord2 = self._discover_rational_order2(a_number, terms, start_index)
        if cand_ord2:
            candidates.append(cand_ord2)
            return candidates

        return candidates

    def _discover_lyness(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n)*a(n-2) = c1*a(n-1) + c0."""
        N = len(terms)
        if N < 6:
            return None

        # Two unknowns: c1, c0
        # n = 2: c1*a(1) + c0 = a(2)*a(0)
        # n = 3: c1*a(2) + c0 = a(3)*a(1)
        A = [
            [Fraction(terms[1]), Fraction(1)],
            [Fraction(terms[2]), Fraction(1)],
        ]
        b = [
            Fraction(terms[2] * terms[0]),
            Fraction(terms[3] * terms[1]),
        ]

        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if det == 0:
            return None

        c1 = (b[0] * A[1][1] - b[1] * A[0][1]) / det
        c0 = (A[0][0] * b[1] - A[1][0] * b[0]) / det

        if c1.denominator != 1 or c0.denominator != 1:
            return None

        c1_int, c0_int = c1.numerator, c0.numerator

        # Trivial check (e.g. all 0)
        if c1_int == 0 and c0_int == 0:
            return None

        params = {"c1": c1_int, "c0": c0_int}
        init_terms = terms[:2]

        rhs_parts = []
        if c1_int == 1:
            rhs_parts.append("a(n-1)")
        elif c1_int == -1:
            rhs_parts.append("-a(n-1)")
        elif c1_int != 0:
            rhs_parts.append(f"{c1_int}*a(n-1)")

        if c0_int > 0:
            rhs_parts.append(f"+ {c0_int}" if rhs_parts else f"{c0_int}")
        elif c0_int < 0:
            rhs_parts.append(f"- {abs(c0_int)}" if rhs_parts else f"{c0_int}")

        rhs_str = " ".join(rhs_parts) if rhs_parts else "0"
        formula_str = f"a(n) = ({rhs_str}) / a(n-2); with a({start_index}) = {terms[0]}, a({start_index + 1}) = {terms[1]}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            description=f"Lyness rational recurrence: a(n)*a(n-2) = {rhs_str}",
            complexity=2.5 + len(str(abs(c1_int))) * 0.2 + len(str(abs(c0_int))) * 0.2,
            terms_tested=N,
            valid_from_index=start_index + 2,
            initial_conditions=init_terms,
            details={"type": "lyness", "params": params},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_rational_recurrence(
            candidate=cand,
            rec_type="lyness",
            params=params,
            initial_terms=init_terms,
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _discover_lyness_quadratic(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n)*a(n-2) = c1*a(n-1)^2 + c2*a(n-1) + c0."""
        N = len(terms)
        if N < 8:
            return None

        # 3 unknowns: c1, c2, c0
        matrix = []
        b_vec = []
        for n in range(2, 5):
            matrix.append([Fraction(terms[n - 1] ** 2), Fraction(terms[n - 1]), Fraction(1)])
            b_vec.append(Fraction(terms[n] * terms[n - 2]))

        sol = self._solve_linear_system(matrix, b_vec)
        if sol is None:
            return None

        c1, c2, c0 = sol
        if any(c.denominator != 1 for c in (c1, c2, c0)):
            return None

        c1_int, c2_int, c0_int = c1.numerator, c2.numerator, c0.numerator
        if c1_int == 0 and c2_int == 0 and c0_int == 0:
            return None

        params = {"c1": c1_int, "c2": c2_int, "c0": c0_int}
        init_terms = terms[:2]

        rhs_parts = []
        if c1_int == 1:
            rhs_parts.append("a(n-1)^2")
        elif c1_int == -1:
            rhs_parts.append("-a(n-1)^2")
        elif c1_int != 0:
            rhs_parts.append(f"{c1_int}*a(n-1)^2")

        if c2_int == 1:
            rhs_parts.append("+ a(n-1)" if rhs_parts else "a(n-1)")
        elif c2_int == -1:
            rhs_parts.append("- a(n-1)" if rhs_parts else "-a(n-1)")
        elif c2_int > 0:
            rhs_parts.append(f"+ {c2_int}*a(n-1)" if rhs_parts else f"{c2_int}*a(n-1)")
        elif c2_int < 0:
            rhs_parts.append(f"- {abs(c2_int)}*a(n-1)" if rhs_parts else f"{c2_int}*a(n-1)")

        if c0_int > 0:
            rhs_parts.append(f"+ {c0_int}" if rhs_parts else f"{c0_int}")
        elif c0_int < 0:
            rhs_parts.append(f"- {abs(c0_int)}" if rhs_parts else f"{c0_int}")

        rhs_str = " ".join(rhs_parts) if rhs_parts else "0"
        formula_str = f"a(n) = ({rhs_str}) / a(n-2); with a({start_index}) = {terms[0]}, a({start_index + 1}) = {terms[1]}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            description=f"Quadratic rational recurrence: a(n)*a(n-2) = {rhs_str}",
            complexity=3.0 + len(str(abs(c1_int))) * 0.2 + len(str(abs(c0_int))) * 0.2,
            terms_tested=N,
            valid_from_index=start_index + 2,
            initial_conditions=init_terms,
            details={"type": "lyness_quadratic", "params": params},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_rational_recurrence(
            candidate=cand,
            rec_type="lyness_quadratic",
            params=params,
            initial_terms=init_terms,
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _discover_riccati(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """Fits Riccati first-order rational: a(n)*(q1*a(n-1) + q0) = p1*a(n-1) + p0."""
        N = len(terms)
        if N < 8:
            return None

        # Form: q1*a(n)*a(n-1) + q0*a(n) - p1*a(n-1) - p0 = 0
        # Unknowns: [q1, q0, -p1, -p0]
        matrix = []
        for n in range(1, min(N, 12)):
            row = [
                Fraction(terms[n] * terms[n - 1]),
                Fraction(terms[n]),
                Fraction(terms[n - 1]),
                Fraction(1),
            ]
            matrix.append(row)

        nulls = self._compute_nullspace(matrix)
        if not nulls:
            return None

        for vec in nulls:
            # Clear denominators
            lcm_v = 1
            for v in vec:
                lcm_v = (lcm_v * v.denominator) // math.gcd(lcm_v, v.denominator)
            int_vec = [int(v * lcm_v) for v in vec]
            g = 0
            for v in int_vec:
                g = math.gcd(g, abs(v))
            if g > 0:
                int_vec = [v // g for v in int_vec]

            q1, q0, neg_p1, neg_p0 = int_vec
            p1 = -neg_p1
            p0 = -neg_p0

            # Denominator must not be identically zero
            if q1 == 0 and q0 == 0:
                continue
            # Numerator must not be identically zero
            if p1 == 0 and p0 == 0:
                continue

            # Standardize sign: q1 > 0 or (q1 == 0 and q0 > 0)
            if q1 < 0 or (q1 == 0 and q0 < 0):
                q1, q0, p1, p0 = -q1, -q0, -p1, -p0

            params = {"q1": q1, "q0": q0, "p1": p1, "p0": p0}
            init_terms = [terms[0]]

            # Format formula
            def fmt_lin(a_c: int, b_c: int) -> str:
                parts = []
                if a_c == 1:
                    parts.append("a(n-1)")
                elif a_c == -1:
                    parts.append("-a(n-1)")
                elif a_c != 0:
                    parts.append(f"{a_c}*a(n-1)")
                if b_c > 0:
                    parts.append(f"+ {b_c}" if parts else f"{b_c}")
                elif b_c < 0:
                    parts.append(f"- {abs(b_c)}" if parts else f"{b_c}")
                return " ".join(parts) if parts else "0"

            num_str = fmt_lin(p1, p0)
            den_str = fmt_lin(q1, q0)
            formula_str = f"a(n) = ({num_str}) / ({den_str}); with a({start_index}) = {terms[0]}"

            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=formula_str,
                description=f"Riccati rational recurrence: a(n) = ({num_str}) / ({den_str})",
                complexity=2.2 + len(str(abs(p1))) * 0.2 + len(str(abs(q1))) * 0.2,
                terms_tested=N,
                valid_from_index=start_index + 1,
                initial_conditions=init_terms,
                details={"type": "riccati", "params": params},
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            is_valid, matched, msg = Verifier.verify_rational_recurrence(
                candidate=cand,
                rec_type="riccati",
                params=params,
                initial_terms=init_terms,
                all_terms=terms,
                start_index=start_index,
            )

            if is_valid:
                cand.verification_status = VerificationStatus.EXACT_MATCH
                cand.terms_tested = matched
                return cand

        return None

    def _discover_bilinear_affine(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        k: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n)*a(n-k) = sum_{j=1}^m c_j * a(n-j)*a(n-k+j) + c0."""
        N = len(terms)
        m = k // 2
        min_terms = k + m + 4
        if N < min_terms:
            return None

        # Unknowns: c_1..c_m and c0 (total m + 1 unknowns)
        matrix = []
        b_vec = []
        for idx in range(m + 1):
            n = k + idx
            row = []
            for j in range(1, m + 1):
                row.append(Fraction(terms[n - j] * terms[n - k + j]))
            row.append(Fraction(1))
            matrix.append(row)
            b_vec.append(Fraction(terms[n] * terms[n - k]))

        sol = self._solve_linear_system(matrix, b_vec)
        if sol is None:
            return None

        if any(c.denominator != 1 for c in sol):
            return None

        int_sol = [c.numerator for c in sol]
        c_coeffs = int_sol[:m]
        c0 = int_sol[m]

        if all(c == 0 for c in c_coeffs) and c0 == 0:
            return None

        params = {"order_k": k, "c_coeffs": c_coeffs, "d_coeffs": [], "c0": c0}
        init_terms = terms[:k]

        rhs_parts = []
        for j, c in enumerate(c_coeffs, 1):
            if k - j == j:
                term_s = f"a(n-{j})^2"
            else:
                term_s = f"a(n-{j})*a(n-{k-j})"
            if c == 1:
                rhs_parts.append(f"+ {term_s}" if rhs_parts else term_s)
            elif c == -1:
                rhs_parts.append(f"- {term_s}" if rhs_parts else f"-{term_s}")
            elif c > 0:
                rhs_parts.append(f"+ {c}*{term_s}" if rhs_parts else f"{c}*{term_s}")
            elif c < 0:
                rhs_parts.append(f"- {abs(c)}*{term_s}" if rhs_parts else f"{c}*{term_s}")

        if c0 > 0:
            rhs_parts.append(f"+ {c0}" if rhs_parts else f"{c0}")
        elif c0 < 0:
            rhs_parts.append(f"- {abs(c0)}" if rhs_parts else f"{c0}")

        rhs_str = " ".join(rhs_parts) if rhs_parts else "0"
        formula_str = f"a(n)*a(n-{k}) = {rhs_str}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            description=f"Bilinear affine recurrence of order {k}: {formula_str}",
            complexity=2.5 + k * 1.5 + sum(abs(c) for c in c_coeffs) * 0.1,
            terms_tested=N,
            valid_from_index=start_index + k,
            initial_conditions=init_terms,
            details={"type": "bilinear_affine", "params": params},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_rational_recurrence(
            candidate=cand,
            rec_type="bilinear_affine",
            params=params,
            initial_terms=init_terms,
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _discover_rational_order2(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
    ) -> Optional[CandidateFormula]:
        """Fits a(n) = (p1*a(n-1) + p2*a(n-2) + p0) / (q1*a(n-1) + q2*a(n-2) + q0)."""
        N = len(terms)
        if N < 10:
            return None

        # q1*a(n)*a(n-1) + q2*a(n)*a(n-2) + q0*a(n) - p1*a(n-1) - p2*a(n-2) - p0 = 0
        # Unknowns: [q1, q2, q0, -p1, -p2, -p0]
        matrix = []
        for n in range(2, min(N, 14)):
            row = [
                Fraction(terms[n] * terms[n - 1]),
                Fraction(terms[n] * terms[n - 2]),
                Fraction(terms[n]),
                Fraction(terms[n - 1]),
                Fraction(terms[n - 2]),
                Fraction(1),
            ]
            matrix.append(row)

        nulls = self._compute_nullspace(matrix)
        if not nulls:
            return None

        for vec in nulls:
            lcm_v = 1
            for v in vec:
                lcm_v = (lcm_v * v.denominator) // math.gcd(lcm_v, v.denominator)
            int_vec = [int(v * lcm_v) for v in vec]
            g = 0
            for v in int_vec:
                g = math.gcd(g, abs(v))
            if g > 0:
                int_vec = [v // g for v in int_vec]

            q1, q2, q0, neg_p1, neg_p2, neg_p0 = int_vec
            p1, p2, p0 = -neg_p1, -neg_p2, -neg_p0

            # Denominator must depend on terms (not a constant denominator, which is purely linear)
            if q1 == 0 and q2 == 0:
                continue
            if p1 == 0 and p2 == 0 and p0 == 0:
                continue
            # Must be truly second-order or rational (not trivial constant)
            if q1 == 0 and q2 == 0 and p1 == 0 and p2 == 0:
                continue

            # Standardize sign
            if q1 < 0 or (q1 == 0 and q2 < 0) or (q1 == 0 and q2 == 0 and q0 < 0):
                q1, q2, q0 = -q1, -q2, -q0
                p1, p2, p0 = -p1, -p2, -p0

            params = {"q1": q1, "q2": q2, "q0": q0, "p1": p1, "p2": p2, "p0": p0}
            init_terms = terms[:2]

            def fmt_ord2(c1_val: int, c2_val: int, c0_val: int) -> str:
                parts = []
                if c1_val == 1:
                    parts.append("a(n-1)")
                elif c1_val == -1:
                    parts.append("-a(n-1)")
                elif c1_val != 0:
                    parts.append(f"{c1_val}*a(n-1)")

                if c2_val == 1:
                    parts.append("+ a(n-2)" if parts else "a(n-2)")
                elif c2_val == -1:
                    parts.append("- a(n-2)" if parts else "-a(n-2)")
                elif c2_val > 0:
                    parts.append(f"+ {c2_val}*a(n-2)" if parts else f"{c2_val}*a(n-2)")
                elif c2_val < 0:
                    parts.append(f"- {abs(c2_val)}*a(n-2)" if parts else f"{c2_val}*a(n-2)")

                if c0_val > 0:
                    parts.append(f"+ {c0_val}" if parts else f"{c0_val}")
                elif c0_val < 0:
                    parts.append(f"- {abs(c0_val)}" if parts else f"{c0_val}")

                return " ".join(parts) if parts else "0"

            num_str = fmt_ord2(p1, p2, p0)
            den_str = fmt_ord2(q1, q2, q0)
            formula_str = (
                f"a(n) = ({num_str}) / ({den_str}); with a({start_index}) = {terms[0]}, a({start_index+1}) = {terms[1]}"
            )

            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=formula_str,
                latex_str=formula_str,
                description=f"Second-order rational recurrence: a(n) = ({num_str}) / ({den_str})",
                complexity=2.8 + len(str(abs(p1) + abs(q1))) * 0.2,
                terms_tested=N,
                valid_from_index=start_index + 2,
                initial_conditions=init_terms,
                details={"type": "rational_order2", "params": params},
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            is_valid, matched, msg = Verifier.verify_rational_recurrence(
                candidate=cand,
                rec_type="rational_order2",
                params=params,
                initial_terms=init_terms,
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
            pivot_row = None
            for row in range(col, n):
                if aug[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row is None:
                return None
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            pv = aug[col][col]
            for j in range(col, n + 1):
                aug[col][j] /= pv
            for row in range(n):
                if row != col and aug[row][col] != 0:
                    factor = aug[row][col]
                    for j in range(col, n + 1):
                        aug[row][j] -= factor * aug[col][j]
        return [aug[i][n] for i in range(n)]

    @staticmethod
    def _compute_nullspace(matrix: List[List[Fraction]]) -> List[List[Fraction]]:
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
