"""
Residue periodicity and modular pattern discovery.
Detects:
- Strict global periodicity (without modulo)
- Eventual periodicity with transient prefix (pre-period)
- Residue periodicity modulo m (for m in 2..16)
- Parity bit sequences and residue state cycles
"""

from typing import List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from .base import DiscoveryMethod


class ModularPatternDiscovery(DiscoveryMethod):
    def __init__(self, max_modulus: int = 16, max_period: int = 24, max_transient: int = 6):
        self.max_modulus = max_modulus
        self.max_period = max_period
        self.max_transient = max_transient

    @property
    def name(self) -> str:
        return "modular"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 10:
            return results

        # 1. Exact Global Eventual Periodicity (Pure or with transient)
        eventual = self._find_eventual_period(terms)
        if eventual is not None:
            t, p = eventual
            transient_terms = terms[:t]
            periodic_pattern = terms[t : t + p]

            if t == 0:
                formula_str = f"a(n) is periodic with period {p}: {periodic_pattern}"
                desc = f"Exactly periodic sequence with fundamental period {p}"
            else:
                formula_str = (
                    f"a(n) is eventually periodic for n >= {start_index + t} "
                    f"with period {p}: {periodic_pattern}; transient prefix: {transient_terms}"
                )
                desc = f"Eventually periodic sequence with transient length {t} and period {p}"

            def eval_fn(n: int, t_val=t, p_val=p, s0=start_index, tr=transient_terms, pat=periodic_pattern) -> int:
                idx = n - s0
                if idx < t_val:
                    return tr[idx]
                return pat[(idx - t_val) % p_val]

            results.append(CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str=formula_str,
                latex_str=f"a(n) \\text{{ periodic for }} n \\ge {start_index + t} \\pmod{{{p}}}",
                description=desc,
                complexity=1.5 + (t * 0.2) + (p * 0.3),
                terms_tested=len(terms),
                verification_status=VerificationStatus.EXACT_MATCH,
                evaluator=eval_fn,
                valid_from_index=start_index,
                details={"transient": t, "period": p, "pattern": periodic_pattern, "transient_terms": transient_terms},
            ))

        # 2. Residue Periodicity Modulo Small Integers
        for m in range(2, self.max_modulus + 1):
            res_terms = [t_val % m for t_val in terms]
            res_eventual = self._find_eventual_period(res_terms)
            if res_eventual is not None:
                t_res, p_res = res_eventual
                if p_res < len(terms) // 2:
                    res_pattern = res_terms[t_res : t_res + p_res]
                    if t_res == 0:
                        f_str = f"a(n) = {res_pattern}[(n - {start_index}) mod {p_res}] (mod {m})"
                    else:
                        f_str = f"a(n) = {res_pattern}[(n - {start_index + t_res}) mod {p_res}] (mod {m}) for n >= {start_index + t_res}"

                    results.append(CandidateFormula(
                        a_number=a_num,
                        method=self.name,
                        formula_str=f_str,
                        latex_str=f"a(n) \\pmod{{{m}}} \\text{{ has period }} {p_res}",
                        description=f"Residue class modulo {m} is periodic with period {p_res} (transient {t_res})",
                        complexity=3.0 + (t_res * 0.1) + (p_res * 0.2),
                        terms_tested=len(terms),
                        verification_status=VerificationStatus.HEURISTIC,
                        details={"modulus": m, "transient": t_res, "period": p_res, "pattern": res_pattern},
                    ))

        return results

    def _find_eventual_period(self, seq: List[int]) -> Optional[Tuple[int, int]]:
        """
        Finds minimal (transient_t, period_p) such that seq[i] == seq[t + ((i - t) % p)] for all i >= t.
        Requires at least 2 full periods after transient: n - t >= 2 * p.
        """
        n = len(seq)
        for t in range(0, min(self.max_transient + 1, n // 3)):
            rem_len = n - t
            for p in range(1, min(self.max_period, rem_len // 2) + 1):
                if all(seq[i] == seq[t + ((i - t) % p)] for i in range(t, n)):
                    return t, p
        return None
