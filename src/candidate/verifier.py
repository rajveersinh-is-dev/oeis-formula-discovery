"""
Strict, unyielding verification layer.
Rejects any candidate that does not reproduce 100% of available OEIS terms exactly.
Ensures zero silent floating-point conversions.
"""

from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional, Tuple
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

    @staticmethod
    def verify_inhomogeneous_recurrence(
        candidate: CandidateFormula,
        rec_coeffs: List[int],  # c_1, ..., c_k for a(n-1)...a(n-k)
        poly_coeffs: List[int],  # b_0 + b_1*n + ... + b_d*n^d
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies inhomogeneous recurrence:
        a(n) == sum_{j=1}^k c_j * a(n-j) + sum_{i=0}^d b_i * n^i
        """
        k = len(rec_coeffs)
        if len(all_terms) < k:
            return False, 0, f"Insufficient terms ({len(all_terms)}) for order {k} recurrence"

        for j in range(k):
            if all_terms[j] != initial_terms[j]:
                return False, j, f"Initial condition mismatch at index {start_index + j}"

        def eval_poly(p: List[Any], n_val: int) -> Optional[int]:
            res = Fraction(0)
            curr_pow = Fraction(1)
            for c in p:
                res += Fraction(c) * curr_pow
                curr_pow *= n_val
            if res.denominator != 1:
                return None
            return res.numerator

        matched = k
        for i in range(k, len(all_terms)):
            n_val = start_index + i
            expected = all_terms[i]
            rec_part = sum(c * all_terms[i - j] for j, c in enumerate(rec_coeffs, 1))
            poly_part = eval_poly(poly_coeffs, n_val)
            if poly_part is None:
                return False, matched, f"Polynomial driving term produced non-integer at n={n_val}"
            computed = rec_part + poly_part
            if computed != expected:
                return False, matched, f"Inhomogeneous mismatch at n={n_val}: expected {expected}, got {computed}"
            matched += 1

        return True, matched, "All terms matched inhomogeneous recurrence exactly"

    @staticmethod
    def verify_algebraic_generating_function(
        candidate: CandidateFormula,
        poly_a2: Optional[List[int]] = None,  # A_2(x)
        poly_a1: Optional[List[int]] = None,  # A_1(x)
        poly_a0: Optional[List[int]] = None,  # A_0(x)
        all_terms: Optional[List[int]] = None,
        start_index: int = 0,
        poly_coeffs: Optional[List[List[int]]] = None,  # [A_0(x), A_1(x), ..., A_D(x)]
    ) -> Tuple[bool, int, str]:
        """
        Verifies algebraic generating function:
        sum_{j=0}^D A_j(x) * G(x)^j == 0 (mod x^N).
        Supports arbitrary degree D in G(x) and backwards-compatible with (poly_a2, poly_a1, poly_a0).
        """
        if all_terms is None:
            all_terms = []
        N = len(all_terms)
        if N < 4:
            return False, 0, f"Insufficient terms ({N}) to verify algebraic generating function"

        if poly_coeffs is not None:
            polys = poly_coeffs
        else:
            p0 = poly_a0 if poly_a0 is not None else [0]
            p1 = poly_a1 if poly_a1 is not None else [0]
            p2 = poly_a2 if poly_a2 is not None else [0]
            polys = [p0, p1, p2]

        D = len(polys) - 1
        # Compute G(x)^j for j = 0 .. D up to length N via Cauchy convolution
        G_powers: List[List[int]] = [[0] * N for _ in range(D + 1)]
        G_powers[0][0] = 1
        if D >= 1:
            for i in range(N):
                G_powers[1][i] = all_terms[i]

        for j in range(2, D + 1):
            prev = G_powers[j - 1]
            curr = G_powers[j]
            for i in range(N):
                ai = all_terms[i]
                if ai != 0:
                    for k in range(N - i):
                        curr[i + k] += ai * prev[k]

        # Verify [x^n] = 0 for all n = 0..N-1
        for n in range(N):
            val = 0
            for j in range(D + 1):
                p = polys[j]
                for deg, c in enumerate(p):
                    if n >= deg:
                        val += c * G_powers[j][n - deg]

            if val != 0:
                return False, n, f"Algebraic generating function mismatch at degree {n}: residual = {val} != 0"

        return True, N, "All terms matched algebraic generating function exactly"

    @staticmethod
    def verify_convolution_recurrence(
        candidate: CandidateFormula,
        conv_type: str,
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies Cauchy self-convolution or Catalan-type recurrence.
        """
        import math
        N = len(all_terms)
        if N < 3:
            return False, 0, "Insufficient terms for convolution"

        if conv_type == "catalan_cauchy":
            # a(n) = sum_{k=0}^{n-1} a(k)*a(n-1-k) for n >= 1
            if all_terms[0] != initial_terms[0]:
                return False, 0, f"Initial mismatch: {all_terms[0]} != {initial_terms[0]}"
            matched = 1
            for n in range(1, N):
                expected = all_terms[n]
                computed = sum(all_terms[k] * all_terms[n - 1 - k] for k in range(n))
                if computed != expected:
                    return False, matched, f"Convolution mismatch at index {n}: expected {expected}, got {computed}"
                matched += 1
            return True, matched, "All terms matched Cauchy convolution exactly"

        elif conv_type == "motzkin_cauchy":
            # a(n) = a(n-1) + sum_{k=0}^{n-2} a(k)*a(n-2-k) for n >= 2
            if all_terms[:2] != initial_terms[:2]:
                return False, 0, "Initial conditions mismatch"
            matched = 2
            for n in range(2, N):
                expected = all_terms[n]
                computed = all_terms[n - 1] + sum(all_terms[k] * all_terms[n - 2 - k] for k in range(n - 1))
                if computed != expected:
                    return False, matched, f"Motzkin convolution mismatch at index {n}: expected {expected}, got {computed}"
                matched += 1
            return True, matched, "All terms matched Motzkin convolution exactly"

        elif conv_type == "bell_binomial":
            # a(n) = sum_{k=0}^{n-1} binom(n-1, k) * a(k) for n >= 1
            if all_terms[0] != initial_terms[0]:
                return False, 0, "Initial mismatch"
            matched = 1
            for n in range(1, N):
                expected = all_terms[n]
                computed = sum(math.comb(n - 1, k) * all_terms[k] for k in range(n))
                if computed != expected:
                    return False, matched, f"Binomial convolution mismatch at index {n}: expected {expected}, got {computed}"
                matched += 1
            return True, matched, "All terms matched binomial convolution exactly"

        return False, 0, f"Unknown convolution type: {conv_type}"

    @staticmethod
    def verify_multiplicative_recurrence(
        candidate: CandidateFormula,
        mult_c: int,
        pow_p: int,
        pow_q: int,
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies multiplicative recurrence:
        a(n) == mult_c * (a(n-1)^pow_p) * (a(n-2)^pow_q) for n >= 2.
        """
        N = len(all_terms)
        if N < 3:
            return False, 0, "Insufficient terms for multiplicative recurrence"

        if all_terms[:2] != initial_terms[:2]:
            return False, 0, "Initial conditions mismatch"

        matched = 2
        for n in range(2, N):
            expected = all_terms[n]
            computed = mult_c * (all_terms[n - 1] ** pow_p) * (all_terms[n - 2] ** pow_q)
            if computed != expected:
                return False, matched, f"Multiplicative mismatch at index {n}: expected {expected}, got {computed}"
            matched += 1

        return True, matched, "All terms matched multiplicative recurrence exactly"

    @staticmethod
    def verify_rational_recurrence(
        candidate: CandidateFormula,
        rec_type: str,
        params: Dict[str, Any],
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies exact rational and bilinear recurrences across 100% of terms.
        """
        N = len(all_terms)
        k = len(initial_terms)
        if N <= k:
            return False, 0, "Insufficient terms for rational recurrence"

        if all_terms[:k] != initial_terms:
            return False, 0, "Initial conditions mismatch"

        matched = k
        history = list(initial_terms)

        for i in range(k, N):
            n_val = start_index + i
            if rec_type == "riccati":
                # a(n) * (q1 * a(n-1) + q0) = p1 * a(n-1) + p0
                prev = history[-1]
                denom = params["q1"] * prev + params["q0"]
                num = params["p1"] * prev + params["p0"]
                if denom == 0 or num % denom != 0:
                    return False, matched, f"Riccati division error or non-integer at n={n_val}"
                computed = num // denom
            elif rec_type == "lyness":
                # a(n) * a(n-2) = c1 * a(n-1) + c0
                prev1 = history[-1]
                prev2 = history[-2]
                if prev2 == 0:
                    return False, matched, f"Zero division by a(n-2) at n={n_val}"
                num = params["c1"] * prev1 + params["c0"]
                if num % prev2 != 0:
                    return False, matched, f"Non-integer division in Lyness at n={n_val}"
                computed = num // prev2
            elif rec_type == "lyness_quadratic":
                # a(n) * a(n-2) = c1 * a(n-1)^2 + c2 * a(n-1) + c0
                prev1 = history[-1]
                prev2 = history[-2]
                if prev2 == 0:
                    return False, matched, f"Zero division by a(n-2) at n={n_val}"
                num = params["c1"] * (prev1 ** 2) + params.get("c2", 0) * prev1 + params["c0"]
                if num % prev2 != 0:
                    return False, matched, f"Non-integer division in Lyness quadratic at n={n_val}"
                computed = num // prev2
            elif rec_type == "bilinear_affine":
                # a(n) * a(n-k) = sum c_j * a(n-j)*a(n-k+j) + sum d_j * a(n-j) + c0
                order_k = params["order_k"]
                denom = history[-order_k]
                if denom == 0:
                    return False, matched, f"Zero division by a(n-{order_k}) at n={n_val}"
                num = params.get("c0", 0)
                for j, c in enumerate(params.get("c_coeffs", []), 1):
                    num += c * history[-j] * history[-order_k + j]
                for j, d in enumerate(params.get("d_coeffs", []), 1):
                    num += d * history[-j]
                if num % denom != 0:
                    return False, matched, f"Non-integer division in bilinear affine at n={n_val}"
                computed = num // denom
            elif rec_type == "rational_order2":
                # a(n) * (q1*a(n-1) + q2*a(n-2) + q0) = p1*a(n-1) + p2*a(n-2) + p0
                prev1 = history[-1]
                prev2 = history[-2]
                denom = params["q1"] * prev1 + params["q2"] * prev2 + params["q0"]
                num = params["p1"] * prev1 + params["p2"] * prev2 + params["p0"]
                if denom == 0 or num % denom != 0:
                    return False, matched, f"Zero division or non-integer in order 2 rational at n={n_val}"
                computed = num // denom
            else:
                return False, matched, f"Unknown rational recurrence type: {rec_type}"

            if computed != all_terms[i]:
                return False, matched, f"Rational mismatch at n={n_val}: expected {all_terms[i]}, got {computed}"

            history.append(computed)
            matched += 1

        return True, matched, "All terms matched rational recurrence exactly"

    @staticmethod
    def verify_divide_and_conquer(
        candidate: CandidateFormula,
        base: int,
        rules: List[Dict[str, int]],
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies divide-and-conquer / k-regular recurrence:
        a(b*n + r) = c0*a(n) + c1*a(n+1) + e*n + d for r in {0, ..., b-1}.
        Handles arbitrary start_index (e.g. 0 or 1).
        """
        N = len(all_terms)
        k = len(initial_terms)
        if N <= k:
            return False, 0, "Insufficient terms for divide-and-conquer"

        if all_terms[:k] != initial_terms:
            return False, 0, "Initial conditions mismatch"

        matched = k
        for i in range(k, N):
            n_math = start_index + i
            n_sub = n_math // base
            r = n_math % base
            rule = rules[r]
            c0 = rule.get("c0", 0)
            c1 = rule.get("c1", 0)
            e = rule.get("e", 0)
            d = rule.get("d", 0)

            idx_sub = n_sub - start_index
            if idx_sub < 0 or idx_sub >= i:
                return False, matched, f"Out of bounds or forward reference for a({n_sub}) at index {i}"

            val = c0 * all_terms[idx_sub]
            if c1 != 0:
                idx_sub1 = (n_sub + 1) - start_index
                if idx_sub1 < 0 or idx_sub1 >= i:
                    return False, matched, f"Out of bounds or forward reference for a({n_sub + 1}) at index {i}"
                val += c1 * all_terms[idx_sub1]

            val += e * n_sub + d
            if val != all_terms[i]:
                return False, matched, f"Divide-and-conquer mismatch at n={n_math}: expected {all_terms[i]}, got {val}"
            matched += 1

        return True, matched, "All terms matched divide-and-conquer recurrence exactly"

    @staticmethod
    def verify_interleaved_recurrence(
        candidate: CandidateFormula,
        period: int,
        branch_recurrences: List[List[int]],
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies multisection interleaved linear recurrence:
        a(m*k + r) = sum_{j=1}^o c_{r, j} * a(m*(k-j) + r).
        Correctly aligns residue classes with mathematical index (start_index + i) % period.
        """
        N = len(all_terms)
        k = len(initial_terms)
        if N <= k:
            return False, 0, "Insufficient terms for interleaved recurrence"

        if all_terms[:k] != initial_terms:
            return False, 0, "Initial conditions mismatch"

        matched = k
        for i in range(k, N):
            n_val = start_index + i
            r = n_val % period
            rec = branch_recurrences[r]
            expected = all_terms[i]
            computed = 0
            for j, c in enumerate(rec, 1):
                prev_idx = i - j * period
                if prev_idx < 0:
                    return False, matched, f"Index out of range for branch {r} at index {i}"
                computed += c * all_terms[prev_idx]

            if computed != expected:
                return False, matched, f"Interleaved mismatch at n={n_val} (residue {r}): expected {expected}, got {computed}"
            matched += 1

        return True, matched, "All terms matched interleaved recurrence exactly"

    @staticmethod
    def verify_continued_fraction(
        candidate: CandidateFormula,
        s_sign: int,
        quotient_fn: Callable[[int], int],
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies continued fraction 3-term recurrence:
        a(n) = q(n) * a(n-1) + s_sign * a(n-2) for n >= start_index + 2.
        """
        N = len(all_terms)
        if N < 4:
            return False, 0, "Insufficient terms for continued fraction"

        if all_terms[:2] != initial_terms[:2]:
            return False, 0, "Initial conditions mismatch"

        matched = 2
        for i in range(2, N):
            n_val = start_index + i
            q_val = quotient_fn(n_val)
            expected = all_terms[i]
            computed = q_val * all_terms[i - 1] + s_sign * all_terms[i - 2]
            if computed != expected:
                return False, matched, f"Continued fraction mismatch at n={n_val}: expected {expected}, got {computed}"
            matched += 1

        return True, matched, "All terms matched continued fraction recurrence exactly"

    @staticmethod
    def verify_nested_recurrence(
        candidate: CandidateFormula,
        recurrence_kind: str,
        params: Dict[str, Any],
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies parametric nested and meta-Fibonacci recurrences:
        1. additive_two_shift / hofstadter_q: a(n) = a(n - a(n-p)) + a(n - a(n-q)) + c
        2. composite_additive / hofstadter_conway: a(n) = a(a(n-p)) + a(n - a(n-q)) + c
        3. linear_subtractive / hofstadter_g / hofstadter_h: a(n) = n - a^(depth)(n-p)
        4. golomb_type / golomb: a(n) = c + a(n - a^(depth)(n-p))
        """
        N = len(all_terms)
        k = len(initial_terms)
        if N <= k:
            return False, 0, "Insufficient terms for nested recurrence"

        if all_terms[:k] != initial_terms:
            return False, 0, "Initial conditions mismatch"

        matched = k
        history = list(initial_terms)

        for i in range(k, N):
            n_val = start_index + i

            def get_a(m: int) -> Optional[int]:
                offset = m - start_index
                if 0 <= offset < len(history):
                    return history[offset]
                return None

            if recurrence_kind in ("additive_two_shift", "hofstadter_q"):
                p = params.get("p", 1)
                q = params.get("q", 2)
                c = params.get("c", 0)
                q1 = get_a(n_val - p)
                q2 = get_a(n_val - q)
                if q1 is None or q2 is None:
                    return False, matched, f"Out of range inner term at n={n_val}"
                t1 = get_a(n_val - q1)
                t2 = get_a(n_val - q2)
                if t1 is None or t2 is None:
                    return False, matched, f"Out of range outer term at n={n_val}"
                computed = t1 + t2 + c

            elif recurrence_kind in ("composite_additive", "hofstadter_conway"):
                p = params.get("p", 1)
                q = params.get("q", 1)
                c = params.get("c", 0)
                prev_p = get_a(n_val - p)
                prev_q = get_a(n_val - q)
                if prev_p is None or prev_q is None:
                    return False, matched, f"Out of range inner term at n={n_val}"
                t1 = get_a(prev_p)
                t2 = get_a(n_val - prev_q)
                if t1 is None or t2 is None:
                    return False, matched, f"Out of range outer term at n={n_val}"
                computed = t1 + t2 + c

            elif recurrence_kind in ("linear_subtractive", "hofstadter_g", "hofstadter_h"):
                d = params.get("depth", 2 if recurrence_kind == "hofstadter_g" else 3)
                p = params.get("p", 1)
                curr = get_a(n_val - p)
                if curr is None:
                    return False, matched, f"Out of range nested term at step 1 at n={n_val}"
                for step in range(2, d + 1):
                    curr = get_a(curr)
                    if curr is None:
                        return False, matched, f"Out of range nested term at step {step} at n={n_val}"
                computed = n_val - curr

            elif recurrence_kind in ("golomb_type", "golomb"):
                c = params.get("c", 1)
                d = params.get("depth", 2)
                p = params.get("p", 1)
                curr = get_a(n_val - p)
                if curr is None:
                    return False, matched, f"Out of range nested term at step 1 at n={n_val}"
                for step in range(2, d + 1):
                    curr = get_a(curr)
                    if curr is None:
                        return False, matched, f"Out of range nested term at step {step} at n={n_val}"
                p3 = get_a(n_val - curr)
                if p3 is None:
                    return False, matched, f"Out of range outer term at n={n_val}"
                computed = c + p3

            else:
                return False, matched, f"Unknown nested recurrence kind: {recurrence_kind}"

            if computed != all_terms[i]:
                return False, matched, f"Nested recurrence mismatch at n={n_val}: expected {all_terms[i]}, got {computed}"

            history.append(computed)
            matched += 1

        return True, matched, "All terms matched nested recurrence exactly"

    @staticmethod
    def verify_modular_product(
        candidate: CandidateFormula,
        offset_n0: int,
        scale: int,
        exponents: List[int],
        is_periodic: bool,
        period: int,
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies exact modular products and Euler transform generating functions:
        G(x) = scale * x^{offset_n0} * prod_{k=1}^infinity (1 - x^k)^{-c_k}.
        Computed via logarithmic derivative recurrence n*A_n = sum_{k=1}^n b_k * A_{n-k}
        where b_n = sum_{d|n} d * c_d.
        """
        N = len(all_terms)
        if N <= offset_n0 + 3:
            return False, 0, "Insufficient terms for modular product"

        # Check leading zeros up to offset_n0
        for i in range(offset_n0):
            if all_terms[i] != 0:
                return False, i, f"Expected 0 at index {i}, got {all_terms[i]}"

        # Base term at offset_n0
        if all_terms[offset_n0] != scale:
            return False, offset_n0, f"Expected leading scale {scale} at index {offset_n0}, got {all_terms[offset_n0]}"

        A = [all_terms[offset_n0 + m] for m in range(N - offset_n0)]
        M = len(A)

        # Precompute b_n for n = 1 .. M-1
        def get_c(k: int) -> int:
            if is_periodic:
                return exponents[(k - 1) % period]
            return exponents[0]

        b = [0] * M
        for m in range(1, M):
            sm = 0
            d = 1
            while d * d <= m:
                if m % d == 0:
                    sm += d * get_c(d)
                    if d * d != m:
                        other = m // d
                        sm += other * get_c(other)
                d += 1
            b[m] = sm

        matched = offset_n0 + 1
        for n in range(1, M):
            # n * A_n = sum_{k=1}^n b_k * A_{n-k}
            rhs = sum(b[k] * A[n - k] for k in range(1, n + 1))
            if rhs % n != 0 or (rhs // n) != A[n]:
                return False, matched, f"Modular product mismatch at n={n} (global index {offset_n0 + n}): expected {A[n]}, computed {rhs // n if rhs % n == 0 else rhs / n}"
            matched += 1

        return True, matched, "All terms matched modular product expansion exactly"

    @staticmethod
    def verify_q_series(
        candidate: CandidateFormula,
        base_q: int,
        c1: Fraction,
        c0: Fraction,
        d1: Fraction,
        d0: Fraction,
        const_e: Fraction,
        order: int,
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies exact q-series recurrence:
        a(n) = (c1*q^n + c0)*a(n-1) + (d1*q^n + d0)*a(n-2) + const_e.
        """
        N = len(all_terms)
        if N <= order:
            return False, 0, "Insufficient terms for q-series recurrence"

        if all_terms[:order] != initial_terms[:order]:
            return False, 0, "Initial conditions mismatch"

        matched = order
        for i in range(order, N):
            n_val = start_index + i
            q_pow = Fraction(base_q ** n_val)
            prev1 = Fraction(all_terms[i - 1])
            prev2 = Fraction(all_terms[i - 2]) if order >= 2 else Fraction(0)

            computed_frac = (c1 * q_pow + c0) * prev1 + (d1 * q_pow + d0) * prev2 + const_e
            if computed_frac.denominator != 1:
                return False, matched, f"Non-integer result in q-series at n={n_val}"

            computed = computed_frac.numerator
            if computed != all_terms[i]:
                return False, matched, f"q-series mismatch at n={n_val}: expected {all_terms[i]}, got {computed}"
            matched += 1

        return True, matched, "All terms matched q-series recurrence exactly"

    @staticmethod
    def verify_inhomogeneous_exponential(
        candidate: CandidateFormula,
        rec_coeffs: List[int],
        exp_base: int,
        exp_coeff: int,
        initial_terms: List[int],
        all_terms: List[int],
        start_index: int,
    ) -> Tuple[bool, int, str]:
        """
        Verifies recurrence with exponential driving term:
        a(n) = sum_{j=1}^k c_j * a(n-j) + exp_coeff * (exp_base^n).
        """
        k = len(rec_coeffs)
        if len(all_terms) <= k:
            return False, 0, "Insufficient terms"
        if all_terms[:k] != initial_terms:
            return False, 0, "Initial conditions mismatch"
        matched = k
        for i in range(k, len(all_terms)):
            n_val = start_index + i
            rec_part = sum(c * all_terms[i - j] for j, c in enumerate(rec_coeffs, 1))
            exp_part = exp_coeff * (exp_base ** n_val)
            computed = rec_part + exp_part
            if computed != all_terms[i]:
                return False, matched, f"Inhomogeneous exponential mismatch at n={n_val}: expected {all_terms[i]}, got {computed}"
            matched += 1
        return True, matched, "All terms matched inhomogeneous exponential recurrence exactly"




