"""
Strict, unyielding verification layer.
Rejects any candidate that does not reproduce 100% of available OEIS terms exactly.
Ensures zero silent floating-point conversions.
"""

from typing import Callable, List, Tuple
from .model import CandidateFormula, VerificationStatus


class Verifier:
    @staticmethod
    def verify_explicit(
        candidate: CandidateFormula,
        eval_fn: Callable[[int], int],
        terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies f(n) == terms[n - start_index] for all available terms.
        Returns: (is_exact, terms_matched, error_msg)
        """
        if not terms:
            return False, 0, "Empty term list"

        matched = 0
        for i, target_val in enumerate(terms):
            n = start_index + i
            try:
                computed_val = eval_fn(n)
                if not isinstance(computed_val, int):
                    return False, matched, f"Evaluator returned non-integer {type(computed_val)} at n={n}"
                if computed_val != target_val:
                    return False, matched, f"Mismatch at n={n}: expected {target_val}, got {computed_val}"
                matched += 1
            except Exception as e:
                return False, matched, f"Evaluation exception at n={n}: {str(e)}"

        return True, matched, "All terms matched exactly"

    @staticmethod
    def verify_recurrence(
        candidate: CandidateFormula,
        coeffs: List[int], # a(n) = c_1*a(n-1) + ... + c_k*a(n-k)
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies linear recurrence a(n) = sum_{j=1}^k c_j * a(n-j) across all remaining terms.
        """
        k = len(coeffs)
        if len(all_terms) < k:
            return False, 0, f"Insufficient terms ({len(all_terms)}) for order {k} recurrence"

        # Check initial conditions
        for j in range(k):
            if all_terms[j] != initial_terms[j]:
                return False, j, f"Initial condition mismatch at index {start_index + j}"

        # Test subsequent terms
        matched = k
        history = list(initial_terms)

        for i in range(k, len(all_terms)):
            next_val = sum(c * history[-j] for j, c in enumerate(coeffs, 1))
            if next_val != all_terms[i]:
                return False, matched, f"Recurrence mismatch at n={start_index + i}: expected {all_terms[i]}, got {next_val}"
            history.append(next_val)
            matched += 1

        return True, matched, "All terms matched recurrence exactly"
