"""
Heuristic Asymptotic Growth Regimes:
- Polynomial: a(n) ~ C * n^d
- Exponential: a(n) ~ C * r^n
Carefully labeled as HEURISTIC; never claimed as exact formula.
"""

import math
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from .base import DiscoveryMethod


class AsymptoticGrowthDiscovery(DiscoveryMethod):
    @property
    def name(self) -> str:
        return "asymptotic"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        valid_terms = [(start_index + i, t) for i, t in enumerate(terms) if t > 0]
        if len(valid_terms) < 10:
            return results

        n_vals = [float(x[0]) for x in valid_terms if x[0] > 0]
        a_vals = [float(x[1]) for x in valid_terms if x[0] > 0]

        if len(n_vals) < 8:
            return results

        # 1. Test Exponential Growth: log(a_n) = alpha * n + beta
        try:
            log_a = [math.log(y) for y in a_vals]
            mean_n = sum(n_vals) / len(n_vals)
            mean_log_a = sum(log_a) / len(log_a)

            cov = sum((n_vals[i] - mean_n) * (log_a[i] - mean_log_a) for i in range(len(n_vals)))
            var_n = sum((n_vals[i] - mean_n)**2 for i in range(len(n_vals)))

            if var_n > 0:
                alpha = cov / var_n
                beta = mean_log_a - alpha * mean_n
                base_r = math.exp(alpha)
                coeff_c = math.exp(beta)

                # Check Pearson r^2
                pred = [alpha * n + beta for n in n_vals]
                ss_res = sum((log_a[i] - pred[i])**2 for i in range(len(log_a)))
                ss_tot = sum((log_a[i] - mean_log_a)**2 for i in range(len(log_a)))
                r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

                if r2 > 0.98 and base_r > 1.01:
                    results.append(CandidateFormula(
                        a_number=a_num,
                        method=self.name,
                        formula_str=f"a(n) ~ {coeff_c:.4f} * ({base_r:.4f})^n [R^2 = {r2:.4f}]",
                        latex_str=f"a(n) \\sim {coeff_c:.4f} \\cdot ({base_r:.4f})^n",
                        description=f"Heuristic exponential asymptotic growth with base {base_r:.4f}",
                        complexity=15.0,
                        terms_tested=len(terms),
                        verification_status=VerificationStatus.HEURISTIC,
                        details={"base": base_r, "coefficient": coeff_c, "r2": r2},
                    ))
        except Exception:
            pass

        return results

