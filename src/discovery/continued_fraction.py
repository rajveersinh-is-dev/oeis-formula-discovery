"""
Continued Fraction Convergent & Variable Recurrence Discovery Module.
Discovers exact 3-term continued fraction relations:
a(n) = q(n) * a(n-1) + s * a(n-2)
where s in {1, -1} and the partial quotient sequence q(n) is:
1. Arithmetic progression: q(n) = alpha*n + beta (e.g. Bessel convergents A001517)
2. Periodic sequence: q(n) is periodic of period p in [2, 6] (quadratic irrationals)
3. Quasipolynomial / multisection partial quotients:
   e.g. Convergents to e (A007676, A007677) where q(n) has period 3 with linear step:
   q(3k) = 2*(k+1), q(3k+1) = 1, q(3k+2) = 1.

All calculations use exact arbitrary-precision integer arithmetic.
"""

from typing import Callable, Dict, List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class ContinuedFractionDiscovery(DiscoveryMethod):
    def __init__(self, max_period: int = 6):
        self.max_period = max_period

    @property
    def name(self) -> str:
        return "continued_fraction"

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

        for s_sign in (1, -1):
            cand = self._test_sign(a_number, terms, start_index, s_sign)
            if cand is not None:
                candidates.append(cand)
                break  # Prefer s = +1 (standard continued fraction)

        return candidates

    def _test_sign(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        s_sign: int,
    ) -> Optional[CandidateFormula]:
        N = len(terms)
        # Compute partial quotients q(n) = (a(n) - s*a(n-2)) / a(n-1) for n >= 2
        quotients: List[int] = []

        for i in range(2, N):
            prev1 = terms[i - 1]
            prev2 = terms[i - 2]
            if prev1 == 0:
                return None
            num = terms[i] - s_sign * prev2
            if num % prev1 != 0:
                return None
            quotients.append(num // prev1)

        # Skip if all quotients are equal (handled by standard linear recurrence)
        if all(q == quotients[0] for q in quotients):
            return None

        # 1. Test if q(n) is an arithmetic progression: q(n) = alpha*n + beta
        cand_ap = self._test_arithmetic_progression(a_number, terms, start_index, s_sign, quotients)
        if cand_ap is not None:
            return cand_ap

        # 2. Test if q(n) is purely periodic of period p in [2, max_period]
        cand_per = self._test_periodic(a_number, terms, start_index, s_sign, quotients)
        if cand_per is not None:
            return cand_per

        # 3. Test if q(n) is a quasipolynomial / multisection progression of period p in [2, 4]
        cand_qp = self._test_quasipolynomial(a_number, terms, start_index, s_sign, quotients)
        if cand_qp is not None:
            return cand_qp

        return None

    def _test_arithmetic_progression(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        s_sign: int,
        quotients: List[int],
    ) -> Optional[CandidateFormula]:
        """Checks if q(n) = alpha*n + beta."""
        if len(quotients) < 4:
            return None

        alpha = quotients[1] - quotients[0]
        if alpha == 0:
            return None

        for idx in range(2, len(quotients)):
            if quotients[idx] - quotients[idx - 1] != alpha:
                return None

        # n corresponding to quotients[0] is start_index + 2
        n0 = start_index + 2
        beta = quotients[0] - alpha * n0

        def q_fn(n_val: int) -> int:
            return alpha * n_val + beta

        sign_str = "+ " if s_sign == 1 else "- "
        if beta == 0:
            q_str = f"{alpha}*n" if alpha != 1 else "n"
        elif beta > 0:
            q_str = f"{alpha}*n + {beta}" if alpha != 1 else f"n + {beta}"
        else:
            q_str = f"{alpha}*n - {abs(beta)}" if alpha != 1 else f"n - {abs(beta)}"

        formula_str = (
            f"a(n) = ({q_str})*a(n-1) {sign_str}a(n-2); "
            f"with a({start_index}) = {terms[0]}, a({start_index + 1}) = {terms[1]}"
        )

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            description=f"Continued fraction convergent with arithmetic partial quotients: q(n) = {q_str}",
            complexity=2.2 + abs(alpha) * 0.2,
            terms_tested=len(terms),
            valid_from_index=start_index + 2,
            initial_conditions=terms[:2],
            details={"type": "continued_fraction_ap", "alpha": alpha, "beta": beta, "s_sign": s_sign},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_continued_fraction(
            candidate=cand,
            s_sign=s_sign,
            quotient_fn=q_fn,
            initial_terms=terms[:2],
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _test_periodic(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        s_sign: int,
        quotients: List[int],
    ) -> Optional[CandidateFormula]:
        """Checks if q(n) is purely periodic with period p."""
        for p in range(2, min(self.max_period + 1, len(quotients) // 2 + 1)):
            if len(quotients) < 2 * p + 2:
                continue

            cycle = quotients[:p]
            if all(quotients[i] == cycle[i % p] for i in range(len(quotients))):
                def q_fn(n_val: int) -> int:
                    idx = (n_val - start_index - 2) % p
                    return cycle[idx]

                sign_str = "+ " if s_sign == 1 else "- "
                cycle_str = "[" + ", ".join(str(c) for c in cycle) + "]"
                formula_str = (
                    f"a(n) = q(n)*a(n-1) {sign_str}a(n-2) with periodic q(n) = {cycle_str}; "
                    f"with a({start_index}) = {terms[0]}, a({start_index + 1}) = {terms[1]}"
                )

                cand = CandidateFormula(
                    a_number=a_number,
                    method=self.name,
                    formula_str=formula_str,
                    description=f"Continued fraction with period-{p} partial quotients: {cycle_str}",
                    complexity=2.5 + p * 0.5,
                    terms_tested=len(terms),
                    valid_from_index=start_index + 2,
                    initial_conditions=terms[:2],
                    details={"type": "continued_fraction_periodic", "period": p, "cycle": cycle, "s_sign": s_sign},
                    verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
                )

                is_valid, matched, msg = Verifier.verify_continued_fraction(
                    candidate=cand,
                    s_sign=s_sign,
                    quotient_fn=q_fn,
                    initial_terms=terms[:2],
                    all_terms=terms,
                    start_index=start_index,
                )

                if is_valid:
                    cand.verification_status = VerificationStatus.EXACT_MATCH
                    cand.terms_tested = matched
                    return cand

        return None

    def _test_quasipolynomial(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        s_sign: int,
        quotients: List[int],
    ) -> Optional[CandidateFormula]:
        """Checks if q(n) is a quasipolynomial (e.g. periodic branches with linear steps, like e convergents)."""
        for p in (2, 3, 4):
            if len(quotients) < 3 * p:
                continue

            # For each branch r in 0..p-1: check if it's constant or arithmetic progression
            branch_models = []
            valid_branches = True

            for r in range(p):
                branch = quotients[r::p]
                if len(branch) < 3:
                    valid_branches = False
                    break

                diffs = [branch[i + 1] - branch[i] for i in range(len(branch) - 1)]
                if all(d == 0 for d in diffs):
                    # Constant branch: branch[k] = c0
                    c0 = branch[0]
                    branch_models.append(("const", c0, 0))
                elif all(d == diffs[0] for d in diffs):
                    # Arithmetic progression: branch[k] = diffs[0]*k + branch[0]
                    step = diffs[0]
                    c0 = branch[0]
                    branch_models.append(("ap", c0, step))
                else:
                    valid_branches = False
                    break

            if not valid_branches:
                continue

            # Must have at least one non-constant branch to distinguish from purely periodic
            if all(kind == "const" for kind, _, _ in branch_models):
                continue

            def q_fn(n_val: int) -> int:
                idx = n_val - start_index - 2
                k = idx // p
                r = idx % p
                kind, c0, step = branch_models[r]
                if kind == "const":
                    return c0
                return c0 + step * k

            branch_desc = []
            for r, (kind, c0, step) in enumerate(branch_models):
                if kind == "const":
                    branch_desc.append(f"q({p}k+{r})={c0}")
                else:
                    branch_desc.append(f"q({p}k+{r})={step}k+{c0}")

            sign_str = "+ " if s_sign == 1 else "- "
            desc_str = ", ".join(branch_desc)
            formula_str = (
                f"a(n) = q(n)*a(n-1) {sign_str}a(n-2) with [{desc_str}]; "
                f"with a({start_index}) = {terms[0]}, a({start_index + 1}) = {terms[1]}"
            )

            cand = CandidateFormula(
                a_number=a_number,
                method=self.name,
                formula_str=formula_str,
                description=f"Continued fraction convergent with quasipolynomial partial quotients of period {p}: {desc_str}",
                complexity=2.8 + p * 0.6,
                terms_tested=len(terms),
                valid_from_index=start_index + 2,
                initial_conditions=terms[:2],
                details={"type": "continued_fraction_quasipolynomial", "period": p, "branches": branch_models, "s_sign": s_sign},
                verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
            )

            is_valid, matched, msg = Verifier.verify_continued_fraction(
                candidate=cand,
                s_sign=s_sign,
                quotient_fn=q_fn,
                initial_terms=terms[:2],
                all_terms=terms,
                start_index=start_index,
            )

            if is_valid:
                cand.verification_status = VerificationStatus.EXACT_MATCH
                cand.terms_tested = matched
                return cand

        return None
