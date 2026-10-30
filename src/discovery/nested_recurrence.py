"""
Nested & Meta-Fibonacci Recurrence Discovery Module.
Discovers exact non-linear self-referencing recurrence relations where sequence
values index back into the sequence itself (meta-Fibonacci and nested iterations):

1. Additive Two-Shift Meta-Fibonacci:
   a(n) = a(n - a(n-p)) + a(n - a(n-q)) + c
   (e.g. Hofstadter Q-sequence A005185: p=1, q=2, c=0; Hofstadter Q_k: p=1, q=k)
2. Composite-Additive Meta-Fibonacci:
   a(n) = a(a(n-p)) + a(n - a(n-q)) + c
   (e.g. Hofstadter-Conway $10000 sequence A004001: p=1, q=1, c=0)
3. Subtractive Nested Iteration:
   a(n) = n - a^{(d)}(n-p)
   (e.g. Hofstadter G-sequence A005206: d=2, p=1; Hofstadter H-sequence A005374: d=3, p=1)
4. Golomb-type Self-Describing Recurrences:
   a(n) = c + a(n - a^{(d)}(n-p))
   (e.g. Golomb's sequence A001462: c=1, d=2, p=1)

All parameters are explored systematically from first principles and verified across 100% of terms.
"""

from typing import Any, Dict, List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class NestedRecurrenceDiscovery(DiscoveryMethod):
    @property
    def name(self) -> str:
        return "nested_recurrence"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []
        N = len(terms)
        if N < 10:
            return candidates

        # 1. Family: Additive Two-Shift Meta-Fibonacci
        # a(n) = a(n - a(n-p)) + a(n - a(n-q)) + c
        for p in (1, 2):
            for q in range(p, 5):
                for c in (0, 1):
                    cand = self._test_additive_two_shift(a_number, terms, start_index, p, q, c)
                    if cand is not None:
                        candidates.append(cand)
                        return candidates

        # 2. Family: Composite-Additive Meta-Fibonacci
        # a(n) = a(a(n-p)) + a(n - a(n-q)) + c
        for p in (1, 2):
            for q in (1, 2):
                for c in (0, 1):
                    cand = self._test_composite_additive(a_number, terms, start_index, p, q, c)
                    if cand is not None:
                        candidates.append(cand)
                        return candidates

        # 3. Family: Subtractive Nested Iteration
        # a(n) = n - a^(d)(n-p)
        for depth in (2, 3, 4):
            for p in (1, 2):
                cand = self._test_subtractive_iteration(a_number, terms, start_index, depth, p)
                if cand is not None:
                    candidates.append(cand)
                    return candidates

        # 4. Family: Golomb-type
        # a(n) = c + a(n - a^(d)(n-p))
        for c in (1, 2):
            for depth in (2, 3):
                for p in (1, 2):
                    cand = self._test_golomb_type(a_number, terms, start_index, c, depth, p)
                    if cand is not None:
                        candidates.append(cand)
                        return candidates

        return candidates

    def _test_additive_two_shift(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        p: int,
        q: int,
        c: int,
    ) -> Optional[CandidateFormula]:
        k_init = max(p, q)
        if len(terms) <= k_init + 5:
            return None

        p_str = f"a(n-{p})" if p != 1 else "a(n-1)"
        q_str = f"a(n-{q})" if q != 1 else "a(n-1)"
        c_str = f" + {c}" if c > 0 else ""
        form_template = f"a(n) = a(n - {p_str}) + a(n - {q_str}){c_str}"

        params = {"p": p, "q": q, "c": c}
        return self._evaluate_candidate(
            a_number, terms, start_index, "additive_two_shift", k_init, form_template, params
        )

    def _test_composite_additive(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        p: int,
        q: int,
        c: int,
    ) -> Optional[CandidateFormula]:
        for k_init in (max(2, p, q), max(p, q)):
            if len(terms) <= k_init + 5:
                continue

            p_str = f"a(n-{p})" if p != 1 else "a(n-1)"
            q_str = f"a(n-{q})" if q != 1 else "a(n-1)"
            c_str = f" + {c}" if c > 0 else ""
            form_template = f"a(n) = a({p_str}) + a(n - {q_str}){c_str}"

            params = {"p": p, "q": q, "c": c}
            cand = self._evaluate_candidate(
                a_number, terms, start_index, "composite_additive", k_init, form_template, params
            )
            if cand is not None:
                return cand
        return None

    def _test_subtractive_iteration(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        depth: int,
        p: int,
    ) -> Optional[CandidateFormula]:
        k_init = p
        if len(terms) <= k_init + 5:
            return None

        inner = f"a(n-{p})" if p != 1 else "a(n-1)"
        for _ in range(depth - 1):
            inner = f"a({inner})"
        form_template = f"a(n) = n - {inner}"

        params = {"depth": depth, "p": p}
        return self._evaluate_candidate(
            a_number, terms, start_index, "linear_subtractive", k_init, form_template, params
        )

    def _test_golomb_type(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        c: int,
        depth: int,
        p: int,
    ) -> Optional[CandidateFormula]:
        k_init = p
        if len(terms) <= k_init + 5:
            return None

        inner = f"a(n-{p})" if p != 1 else "a(n-1)"
        for _ in range(depth - 1):
            inner = f"a({inner})"
        form_template = f"a(n) = {c} + a(n - {inner})"

        params = {"c": c, "depth": depth, "p": p}
        return self._evaluate_candidate(
            a_number, terms, start_index, "golomb_type", k_init, form_template, params
        )

    def _evaluate_candidate(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        kind: str,
        k_init: int,
        form_template: str,
        params: Dict[str, Any],
    ) -> Optional[CandidateFormula]:
        N = len(terms)
        init_terms = terms[:k_init]
        init_strs = [f"a({start_index + i}) = {terms[i]}" for i in range(k_init)]
        full_formula = f"{form_template}; with {', '.join(init_strs)}"

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=full_formula,
            latex_str=full_formula,
            description=f"Nested meta-Fibonacci recurrence: {form_template}",
            complexity=2.8 + k_init * 0.5 + float(params.get("p", 1) + params.get("q", 1)) * 0.1,
            terms_tested=N,
            valid_from_index=start_index + k_init,
            initial_conditions=init_terms,
            details={"kind": kind, "params": params},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_nested_recurrence(
            candidate=cand,
            recurrence_kind=kind,
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
