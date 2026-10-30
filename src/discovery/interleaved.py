"""
Interleaved & Multisection Linear Recurrence Discovery Module.
Discovers exact multisection recurrences where each residue class modulo m
follows a distinct linear recurrence or geometric progression:
a(m*k + r) = sum_{j=1}^{o_r} c_{r, j} * a(m*(k - j) + r)
for r in {0, 1, ..., m-1}, where m in {2, 3, 4}.

Captures:
- Interleaved geometric progressions: a(2k) = 2^k, a(2k+1) = 3^k
- Interleaved Fibonacci / Lucas branches
- Parity-dependent recurrences: a(2k) = 2*a(2k-2), a(2k+1) = 5*a(2k-1)
- Multi-branch combinatorial structures

All algorithms use exact Berlekamp-Massey over Fractions and 100% term verification.
"""

from fractions import Fraction
from typing import List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class InterleavedRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self, periods: Optional[List[int]] = None, max_branch_order: int = 3):
        self.periods = periods if periods is not None else [2, 3, 4]
        self.max_branch_order = max_branch_order

    @property
    def name(self) -> str:
        return "interleaved_recurrence"

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

        for m in self.periods:
            if N < m * 5:
                continue

            cand = self._test_period(a_number, terms, start_index, m)
            if cand is not None:
                candidates.append(cand)
                break  # Minimal period

        return candidates

    def _test_period(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        m: int,
    ) -> Optional[CandidateFormula]:
        N = len(terms)
        branch_recurrences: List[List[int]] = []

        for r in range(m):
            i0 = (r - (start_index % m)) % m
            sub_terms = [terms[idx] for idx in range(i0, N, m)]
            if len(sub_terms) < 5:
                return None

            frac_terms = [Fraction(t) for t in sub_terms]
            coeffs = self._berlekamp_massey(frac_terms)
            if not coeffs:
                return None

            order = len(coeffs)
            if order == 0 or order > self.max_branch_order:
                return None

            if len(sub_terms) < 2 * order + 2:
                return None

            if not all(c.denominator == 1 for c in coeffs):
                return None

            int_coeffs = [c.numerator for c in coeffs]
            branch_recurrences.append(int_coeffs)

        # Disallow trivial identical order 1 identical coefficient case (standard geometric)
        if all(len(rec) == 1 and rec[0] == branch_recurrences[0][0] for rec in branch_recurrences):
            # Check if initial terms across branches also match standard single recurrence
            c = branch_recurrences[0][0]
            if all(terms[i] == c * terms[i - 1] for i in range(1, min(N, 6))):
                return None  # Prefer standard linear recurrence

        # Compute max terms needed for initial conditions
        max_init_offset = 0
        for r, rec in enumerate(branch_recurrences):
            i0 = (r - (start_index % m)) % m
            offset = i0 + (len(rec) - 1) * m
            if offset > max_init_offset:
                max_init_offset = offset

        num_init = max(m, max_init_offset + 1)
        if N <= num_init:
            return None

        init_terms = terms[:num_init]

        # Format formula
        branch_strs = []
        for r, rec in enumerate(branch_recurrences):
            lhs = f"a({m}*k + {r})" if r > 0 else f"a({m}*k)"
            rhs_parts = []
            for j, c in enumerate(rec, 1):
                prev_str = f"a({m}*(k-{j}) + {r})" if r > 0 else f"a({m}*(k-{j}))"
                if c == 1:
                    rhs_parts.append(f"+ {prev_str}" if rhs_parts else prev_str)
                elif c == -1:
                    rhs_parts.append(f"- {prev_str}" if rhs_parts else f"-{prev_str}")
                elif c > 0:
                    rhs_parts.append(f"+ {c}*{prev_str}" if rhs_parts else f"{c}*{prev_str}")
                else:
                    rhs_parts.append(f"- {abs(c)}*{prev_str}" if rhs_parts else f"{c}*{prev_str}")
            rhs_str = " ".join(rhs_parts) if rhs_parts else "0"
            branch_strs.append(f"{lhs} = {rhs_str}")

        init_strs = [f"a({start_index + i}) = {terms[i]}" for i in range(num_init)]
        full_formula = f"{'; '.join(branch_strs)}; with {', '.join(init_strs)}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=full_formula,
            latex_str=full_formula,
            description=f"Interleaved multisection recurrence of period {m}",
            complexity=2.0 + m * 1.5 + sum(len(rec) for rec in branch_recurrences) * 0.8,
            terms_tested=N,
            valid_from_index=start_index + num_init,
            initial_conditions=init_terms,
            details={"period": m, "branch_recurrences": branch_recurrences},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_interleaved_recurrence(
            candidate=cand,
            period=m,
            branch_recurrences=branch_recurrences,
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
    def _berlekamp_massey(s: List[Fraction]) -> Optional[List[Fraction]]:
        from .linear_recurrence import LinearRecurrenceDiscovery
        return LinearRecurrenceDiscovery._berlekamp_massey(s)
