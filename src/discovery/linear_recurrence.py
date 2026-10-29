"""
Exact linear recurrence discovery using Berlekamp-Massey algorithm over rational numbers Q.
Finds minimal order recurrences of form: a(n) = c_1*a(n-1) + ... + c_k*a(n-k)
"""

from fractions import Fraction
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class LinearRecurrenceDiscovery(DiscoveryMethod):
    def __init__(self, max_order: int = 8):
        self.max_order = max_order

    @property
    def name(self) -> str:
        return "linear_recurrence"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 8:
            return results

        # Run Berlekamp-Massey over Fraction
        frac_terms = [Fraction(t) for t in terms]
        coeffs = self._berlekamp_massey(frac_terms)

        if not coeffs:
            return results

        k = len(coeffs)
        if k == 0 or k > self.max_order:
            return results

        # Check that we have enough terms to justify the recurrence (at least 2*k + 2)
        if len(terms) < 2 * k + 2:
            return results

        # Convert rational coefficients to integer if possible
        if not all(c.denominator == 1 for c in coeffs):
            return results  # Only integer linear recurrences supported in base pipeline

        int_coeffs = [c.numerator for c in coeffs]
        initial_conditions = terms[:k]

        # Verify against 100% of available terms
        is_exact, matched, err = Verifier.verify_recurrence(
            CandidateFormula(), int_coeffs, initial_conditions, terms, start_index
        )

        if not is_exact:
            return results

        # Format recurrence: a(n) = c1*a(n-1) + c2*a(n-2) ...
        terms_repr = []
        for j, c in enumerate(int_coeffs, 1):
            if c == 1:
                terms_repr.append(f"a(n-{j})")
            elif c == -1:
                terms_repr.append(f"-a(n-{j})")
            elif c > 0:
                terms_repr.append(f"{c}*a(n-{j})")
            elif c < 0:
                terms_repr.append(f"- {abs(c)}*a(n-{j})")

        rec_str = " + ".join(terms_repr).replace("+ - ", "- ")
        init_str = ", ".join(f"a({start_index + i}) = {val}" for i, val in enumerate(initial_conditions))
        full_formula = f"a(n) = {rec_str}; with {init_str}"

        cand = CandidateFormula(
            a_number=a_num,
            method=self.name,
            formula_str=full_formula,
            latex_str=full_formula,
            description=f"Exact homogeneous linear recurrence of order {k}",
            complexity=2.0 + k * 1.2 + sum(len(str(abs(c))) * 0.2 for c in int_coeffs),
            terms_tested=matched,
            verification_status=VerificationStatus.EXACT_MATCH,
            initial_conditions=initial_conditions,
            recurrence_coeffs=int_coeffs,
            valid_from_index=start_index + k,
            details={"order": k, "coefficients": int_coeffs},
        )
        results.append(cand)
        return results

    @staticmethod
    def _berlekamp_massey(s: List[Fraction]) -> Optional[List[Fraction]]:
        """
        Exact Berlekamp-Massey algorithm for sequences over Q.
        Returns the minimal linear recurrence connection polynomial C(x) = 1 - c_1 x - ... - c_k x^k.
        Coefficients returned are [c_1, c_2, ..., c_k].
        """
        n = len(s)
        b = [Fraction(1)]
        c = [Fraction(1)]
        l = 0
        m = 1
        b_scalar = Fraction(1)

        for i in range(n):
            # Compute discrepancy d
            d = s[i]
            for j in range(1, l + 1):
                d += c[j] * s[i - j]

            if d == 0:
                m += 1
            else:
                t = list(c)
                factor = d / b_scalar
                pad = [Fraction(0)] * m
                sub = pad + [factor * x for x in b]

                # c = c - sub
                new_len = max(len(c), len(sub))
                c.extend([Fraction(0)] * (new_len - len(c)))
                for idx in range(len(sub)):
                    c[idx] -= sub[idx]

                if 2 * l <= i:
                    l = i + 1 - l
                    b = t
                    b_scalar = d
                    m = 1
                else:
                    m += 1

        # Truncate trailing zeros
        while len(c) > 1 and c[-1] == 0:
            c.pop()

        # Recurrence: a(n) = sum_{j=1}^k (-c[j]) * a(n-j)
        if len(c) <= 1:
            return None
        return [-coeff for coeff in c[1:]]
