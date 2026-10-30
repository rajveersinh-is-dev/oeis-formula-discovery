"""
Divide-and-Conquer and k-Regular (Mahler-type) Recurrence Discovery.
Discovers exact functional relations on the base-b digital expansion of the index:
a(b*n + r) = c_{r, 0} * a(n) + c_{r, 1} * a(n+1) + e_r * n + d_r
for r in {0, 1, ..., b-1}, where b in {2, 3, 4, 5}.

Captures fundamental combinatorial, fractal, and digital sequences:
- Stern's diatomic sequence (A002487): a(2n) = a(n), a(2n+1) = a(n) + a(n+1)
- Moser-de Bruijn sequence (A000695): a(2n) = 4*a(n), a(2n+1) = 4*a(n) + 1
- Gould's sequence (A001316): a(2n) = a(n), a(2n+1) = 2*a(n)
- Thue-Morse sequence (A010060): a(2n) = a(n), a(2n+1) = 1 - a(n)
- Josephus problem sequence (A006257): a(2n) = 2*a(n) - 1, a(2n+1) = 2*a(n) + 1
- Binary Hamming weight / Popcount (A000120): a(2n) = a(n), a(2n+1) = a(n) + 1

Supports sequences starting at arbitrary start_index (e.g. 0 or 1).
All algebra is exact over Fractions with zero floating-point operations.
"""

from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class DivideAndConquerDiscovery(DiscoveryMethod):
    def __init__(self, bases: Optional[List[int]] = None):
        self.bases = bases if bases is not None else [2, 3, 4, 5]

    @property
    def name(self) -> str:
        return "divide_and_conquer"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []
        N = len(terms)
        if N < 12:
            return candidates

        for base in self.bases:
            cand = self._search_base(a_number, terms, start_index, base)
            if cand is not None:
                candidates.append(cand)
                break  # Pick minimal base

        return candidates

    def _search_base(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        base: int,
    ) -> Optional[CandidateFormula]:
        N = len(terms)
        branch_rules: List[Dict[str, int]] = []
        needed_initial = base

        for r in range(base):
            rule = self._solve_branch(terms, start_index, base, r)
            if rule is None:
                return None
            branch_rules.append(rule)

        # Check that the discovered system is not trivial (e.g. not all identical constant)
        if all(rule.get("c0", 0) == 1 and rule.get("c1", 0) == 0 and rule.get("d", 0) == 0 and rule.get("e", 0) == 0 for rule in branch_rules):
            return None

        # Build human-readable formula
        formula_parts = []
        for r, rule in enumerate(branch_rules):
            lhs = f"a({base}*n + {r})" if r > 0 else f"a({base}*n)"
            rhs_parts = []
            c0 = rule.get("c0", 0)
            c1 = rule.get("c1", 0)
            e = rule.get("e", 0)
            d = rule.get("d", 0)

            if c0 != 0:
                if c0 == 1:
                    rhs_parts.append("a(n)")
                elif c0 == -1:
                    rhs_parts.append("-a(n)")
                else:
                    rhs_parts.append(f"{c0}*a(n)")

            if c1 != 0:
                if c1 == 1:
                    rhs_parts.append("+ a(n+1)" if rhs_parts else "a(n+1)")
                elif c1 == -1:
                    rhs_parts.append("- a(n+1)" if rhs_parts else "-a(n+1)")
                elif c1 > 0:
                    rhs_parts.append(f"+ {c1}*a(n+1)" if rhs_parts else f"{c1}*a(n+1)")
                else:
                    rhs_parts.append(f"- {abs(c1)}*a(n+1)" if rhs_parts else f"{c1}*a(n+1)")

            if e != 0:
                if e == 1:
                    rhs_parts.append("+ n" if rhs_parts else "n")
                elif e == -1:
                    rhs_parts.append("- n" if rhs_parts else "-n")
                elif e > 0:
                    rhs_parts.append(f"+ {e}*n" if rhs_parts else f"{e}*n")
                else:
                    rhs_parts.append(f"- {abs(e)}*n" if rhs_parts else f"{e}*n")

            if d != 0 or not rhs_parts:
                if not rhs_parts:
                    rhs_parts.append(str(d))
                elif d > 0:
                    rhs_parts.append(f"+ {d}")
                else:
                    rhs_parts.append(f"- {abs(d)}")

            formula_parts.append(f"{lhs} = {' '.join(rhs_parts)}")

        init_strs = [f"a({start_index + i}) = {terms[i]}" for i in range(needed_initial)]
        full_formula = f"{'; '.join(formula_parts)}; with {', '.join(init_strs)}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=full_formula,
            latex_str=full_formula,
            description=f"Divide-and-conquer recurrence in base {base}",
            complexity=2.0 + base * 1.5,
            terms_tested=N,
            valid_from_index=start_index,
            initial_conditions=terms[:needed_initial],
            details={"base": base, "rules": branch_rules},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_divide_and_conquer(
            candidate=cand,
            base=base,
            rules=branch_rules,
            initial_terms=terms[:needed_initial],
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _solve_branch(self, terms: List[int], start_index: int, base: int, r: int) -> Optional[Dict[str, int]]:
        """Finds integer coefficients for a(base*n + r) = c0*a(n) + c1*a(n+1) + e*n + d."""
        def get_a(n_val: int) -> Optional[int]:
            idx = n_val - start_index
            if 0 <= idx < len(terms):
                return terms[idx]
            return None

        # Build valid sample pairs (n, target) where target = a(base*n + r)
        samples = []
        n_cand = max(start_index, 0)
        # Avoid n=0 if r=0 because base*0 + 0 = 0 (same term)
        while True:
            t_idx = base * n_cand + r
            val_target = get_a(t_idx)
            val_n = get_a(n_cand)
            if val_target is None or val_n is None:
                break
            # Don't use identity sample where target is n_cand itself
            if t_idx > n_cand:
                samples.append((n_cand, val_n, val_target))
            n_cand += 1

        if len(samples) < 4:
            return None

        # Model 1: Scalar a(base*n + r) = c0*a(n) + d
        sol_scalar = self._fit_scalar_model(samples, get_a, base, r)
        if sol_scalar is not None:
            return sol_scalar

        # Model 2: Coupled a(base*n + r) = c0*a(n) + c1*a(n+1) + d
        sol_coupled = self._fit_coupled_model(samples, get_a, base, r)
        if sol_coupled is not None:
            return sol_coupled

        # Model 3: Affine index a(base*n + r) = c0*a(n) + e*n + d
        sol_affine = self._fit_affine_model(samples, get_a, base, r)
        if sol_affine is not None:
            return sol_affine

        return None

    def _fit_scalar_model(
        self,
        samples: List[Tuple[int, int, int]],
        get_a: Any,
        base: int,
        r: int,
    ) -> Optional[Dict[str, int]]:
        # Find 2 non-collinear samples
        s1 = samples[0]
        s2 = None
        for s in samples[1:]:
            if s[1] != s1[1]:
                s2 = s
                break
        if s2 is None:
            # Check if all targets are constant d
            if all(s[2] == s1[2] for s in samples):
                return {"c0": 0, "c1": 0, "e": 0, "d": s1[2]}
            return None

        # Solve 2x2 system:
        # c0 * a(n1) + d = a(b*n1 + r)
        # c0 * a(n2) + d = a(b*n2 + r)
        A = [
            [Fraction(s1[1]), Fraction(1)],
            [Fraction(s2[1]), Fraction(1)],
        ]
        b = [Fraction(s1[2]), Fraction(s2[2])]
        sol = self._solve_2x2(A, b)
        if sol is None or sol[0].denominator != 1 or sol[1].denominator != 1:
            return None

        c0, d = sol[0].numerator, sol[1].numerator
        for n_cand, a_n, a_target in samples:
            if c0 * a_n + d != a_target:
                return None

        return {"c0": c0, "c1": 0, "e": 0, "d": d}

    def _fit_coupled_model(
        self,
        samples: List[Tuple[int, int, int]],
        get_a: Any,
        base: int,
        r: int,
    ) -> Optional[Dict[str, int]]:
        # Need samples that also have a(n+1) available
        coupled_samples = []
        for n_cand, a_n, a_target in samples:
            a_next = get_a(n_cand + 1)
            if a_next is not None and base * n_cand + r > n_cand + 1:
                coupled_samples.append((n_cand, a_n, a_next, a_target))

        if len(coupled_samples) < 5:
            return None

        # Build 3x3 system using first 3 linearly independent rows
        matrix = []
        b_vec = []
        for n_cand, a_n, a_next, a_target in coupled_samples:
            matrix.append([Fraction(a_n), Fraction(a_next), Fraction(1)])
            b_vec.append(Fraction(a_target))
            if len(matrix) == 3:
                sol = self._solve_3x3(matrix, b_vec)
                if sol is not None:
                    break
                matrix.pop()
                b_vec.pop()

        if len(matrix) < 3:
            return None

        sol = self._solve_3x3(matrix, b_vec)
        if sol is None or any(c.denominator != 1 for c in sol):
            return None

        c0, c1, d = sol[0].numerator, sol[1].numerator, sol[2].numerator
        for n_cand, a_n, a_next, a_target in coupled_samples:
            if c0 * a_n + c1 * a_next + d != a_target:
                return None

        return {"c0": c0, "c1": c1, "e": 0, "d": d}

    def _fit_affine_model(
        self,
        samples: List[Tuple[int, int, int]],
        get_a: Any,
        base: int,
        r: int,
    ) -> Optional[Dict[str, int]]:
        if len(samples) < 5:
            return None

        matrix = []
        b_vec = []
        for n_cand, a_n, a_target in samples:
            matrix.append([Fraction(a_n), Fraction(n_cand), Fraction(1)])
            b_vec.append(Fraction(a_target))
            if len(matrix) == 3:
                sol = self._solve_3x3(matrix, b_vec)
                if sol is not None:
                    break
                matrix.pop()
                b_vec.pop()

        if len(matrix) < 3:
            return None

        sol = self._solve_3x3(matrix, b_vec)
        if sol is None or any(c.denominator != 1 for c in sol):
            return None

        c0, e, d = sol[0].numerator, sol[1].numerator, sol[2].numerator
        for n_cand, a_n, a_target in samples:
            if c0 * a_n + e * n_cand + d != a_target:
                return None

        return {"c0": c0, "c1": 0, "e": e, "d": d}

    @staticmethod
    def _solve_2x2(A: List[List[Fraction]], b: List[Fraction]) -> Optional[List[Fraction]]:
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if det == 0:
            return None
        x = (b[0] * A[1][1] - b[1] * A[0][1]) / det
        y = (A[0][0] * b[1] - A[1][0] * b[0]) / det
        return [x, y]

    @staticmethod
    def _solve_3x3(A: List[List[Fraction]], b: List[Fraction]) -> Optional[List[Fraction]]:
        aug = [list(A[i]) + [b[i]] for i in range(3)]
        for col in range(3):
            pivot = None
            for row in range(col, 3):
                if aug[row][col] != 0:
                    pivot = row
                    break
            if pivot is None:
                return None
            aug[col], aug[pivot] = aug[pivot], aug[col]
            pv = aug[col][col]
            for j in range(col, 4):
                aug[col][j] /= pv
            for row in range(3):
                if row != col and aug[row][col] != 0:
                    factor = aug[row][col]
                    for j in range(col, 4):
                        aug[row][j] -= factor * aug[col][j]
        return [aug[0][3], aug[1][3], aug[2][3]]
