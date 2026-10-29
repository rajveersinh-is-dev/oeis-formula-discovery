"""
Rational Generating Function identification via Padé approximation.
G(x) = P(x) / Q(x)
"""

from fractions import Fraction
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from .base import DiscoveryMethod
from .linear_recurrence import LinearRecurrenceDiscovery


class GeneratingFunctionDiscovery(DiscoveryMethod):
    def __init__(self, max_degree: int = 6):
        self.max_degree = max_degree
        self.lin_rec = LinearRecurrenceDiscovery(max_order=max_degree)

    @property
    def name(self) -> str:
        return "generating_function"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 8:
            return results

        # Recurrence coefficients directly specify denominator Q(x) of ordinary GF:
        # Q(x) = 1 - c_1*x - c_2*x^2 - ... - c_k*x^k
        rec_cands = self.lin_rec.discover(a_num, terms, start_index)
        for cand in rec_cands:
            coeffs = cand.recurrence_coeffs
            k = len(coeffs)
            denom_coeffs = [Fraction(1)] + [-Fraction(c) for c in coeffs]

            # Numerator P(x) = (sum_{n=0}^{k-1} a(n) x^n) * Q(x) mod x^k
            a_frac = [Fraction(t) for t in terms[:k]]
            num_coeffs: List[Fraction] = []
            for deg in range(k):
                term_val = Fraction(0)
                for j in range(deg + 1):
                    term_val += a_frac[j] * denom_coeffs[deg - j]
                num_coeffs.append(term_val)

            # Strip trailing zeros
            while len(num_coeffs) > 1 and num_coeffs[-1] == 0:
                num_coeffs.pop()

            # Format P(x) and Q(x)
            def fmt_poly(p_coeffs: List[Fraction]) -> str:
                parts = []
                for p_deg, val in enumerate(p_coeffs):
                    if val != 0:
                        if p_deg == 0:
                            parts.append(f"{val}")
                        elif p_deg == 1:
                            parts.append(f"{val}*x" if val != 1 else "x")
                        else:
                            parts.append(f"{val}*x^{p_deg}" if val != 1 else f"x^{p_deg}")
                return " + ".join(parts).replace("+ -", "- ") if parts else "0"

            p_str = fmt_poly(num_coeffs)
            q_str = fmt_poly(denom_coeffs)
            gf_formula = f"G(x) = ({p_str}) / ({q_str})"

            cand_gf = CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str=gf_formula,
                latex_str=f"G(x) = \\frac{{{p_str}}}{{{q_str}}}",
                description=f"Rational ordinary generating function (order {k})",
                complexity=cand.complexity + 1.0,
                terms_tested=cand.terms_tested,
                verification_status=VerificationStatus.EXACT_MATCH,
                initial_conditions=cand.initial_conditions,
                recurrence_coeffs=cand.recurrence_coeffs,
                details={"P_coeffs": [int(x) for x in num_coeffs], "Q_coeffs": [int(x) for x in denom_coeffs]},
            )
            results.append(cand_gf)

        return results

