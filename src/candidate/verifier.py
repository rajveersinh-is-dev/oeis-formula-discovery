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

    @staticmethod
    def verify_holonomic_recurrence(
        candidate: CandidateFormula,
        poly_coeffs: List[List[int]], # [p_0, p_1, ..., p_k] where p_i is [c_0, c_1, ..., c_d]
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies holonomic (P-finite) recurrence:
        sum_{j=0}^k p_j(n) * a(n-j) == 0 for all terms from n = start_index + k to end.
        """
        k = len(poly_coeffs) - 1
        if len(all_terms) <= k:
            return False, 0, f"Insufficient terms ({len(all_terms)}) for order {k} holonomic recurrence"

        # Check initial terms match
        for j in range(k):
            if all_terms[j] != initial_terms[j]:
                return False, j, f"Initial condition mismatch at index {start_index + j}"

        def eval_poly(p: List[int], n_val: int) -> int:
            res = 0
            curr_pow = 1
            for c in p:
                res += c * curr_pow
                curr_pow *= n_val
            return res

        matched = k
        for i in range(k, len(all_terms)):
            n_val = start_index + i
            total = 0
            for j in range(k + 1):
                poly_val = eval_poly(poly_coeffs[j], n_val)
                term_val = all_terms[i - j]
                total += poly_val * term_val

            if total != 0:
                return False, matched, f"Holonomic mismatch at n={n_val}: sum = {total} != 0"
            matched += 1

        return True, matched, "All terms matched holonomic recurrence exactly"

    @staticmethod
    def verify_nonlinear_recurrence(
        candidate: CandidateFormula,
        poly_coeffs: List[int],  # c_0 + c_1*x + ... + c_d*x^d
        initial_term: int,
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies nonlinear recurrence a(n) = P(a(n-1)) across all available terms.
        """
        if not all_terms:
            return False, 0, "Empty term list"

        if all_terms[0] != initial_term:
            return False, 0, f"Initial condition mismatch: expected {all_terms[0]}, got {initial_term}"

        matched = 1
        curr = initial_term

        for i in range(1, len(all_terms)):
            n_val = start_index + i
            # Evaluate P(curr)
            next_val = 0
            pow_x = 1
            for c in poly_coeffs:
                next_val += c * pow_x
                pow_x *= curr

            if next_val != all_terms[i]:
                return False, matched, f"Nonlinear mismatch at n={n_val}: expected {all_terms[i]}, got {next_val}"

            curr = next_val
            matched += 1

        return True, matched, "All terms matched nonlinear recurrence exactly"

    @staticmethod
    def verify_bilinear_recurrence(
        candidate: CandidateFormula,
        order_k: int,
        coeffs: List[int],  # c_1, ..., c_m
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies bilinear Somos recurrence:
        a(n)*a(n-k) == sum_{j=1}^m c_j * a(n-j) * a(n-k+j) for all n >= k.
        """
        if len(all_terms) < order_k:
            return False, 0, f"Insufficient terms ({len(all_terms)}) for order {order_k} bilinear recurrence"

        # Check initial conditions
        for j in range(order_k):
            if all_terms[j] != initial_terms[j]:
                return False, j, f"Initial condition mismatch at index {start_index + j}"

        m = len(coeffs)
        matched = order_k

        for i in range(order_k, len(all_terms)):
            n_val = start_index + i
            lhs = all_terms[i] * all_terms[i - order_k]
            rhs = 0
            for j in range(1, m + 1):
                rhs += coeffs[j - 1] * (all_terms[i - j] * all_terms[i - order_k + j])

            if lhs != rhs:
                return False, matched, f"Bilinear mismatch at n={n_val}: lhs {lhs} != rhs {rhs}"
            matched += 1

        return True, matched, "All terms matched bilinear recurrence exactly"


