"""
Residue periodicity and modular pattern discovery.
Detects:
- Strict periodicity mod m (for m in 2..16)
- Eventual periodicity
- Parity bit sequences
"""

from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from .base import DiscoveryMethod


class ModularPatternDiscovery(DiscoveryMethod):
    def __init__(self, max_modulus: int = 16, max_period: int = 24):
        self.max_modulus = max_modulus
        self.max_period = max_period

    @property
    def name(self) -> str:
        return "modular"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 12:
            return results

        # 1. Exact Global Periodicity (without modulo)
        p = self._find_exact_period(terms)
        if p is not None:
            period_pattern = terms[:p]
            results.append(CandidateFormula(
                a_number=a_num,
                method=self.name,
                formula_str=f"a(n) is periodic with period {p}: {period_pattern}",
                latex_str=f"a(n) \\equiv a(n \\pmod{{{p}}})",
                description=f"Exactly periodic sequence with fundamental period {p}",
                complexity=1.5 + p * 0.3,
                terms_tested=len(terms),
                verification_status=VerificationStatus.EXACT_MATCH,
                evaluator=lambda n, pat=period_pattern, s0=start_index: pat[(n - s0) % len(pat)],
                valid_from_index=start_index,
                details={"period": p, "pattern": period_pattern},
            ))

        # 2. Residue Periodicity Modulo Small Integers
        for m in range(2, self.max_modulus + 1):
            res_terms = [t % m for t in terms]
            p_mod = self._find_exact_period(res_terms)
            if p_mod is not None and p_mod < len(terms) // 2:
                res_pattern = res_terms[:p_mod]
                results.append(CandidateFormula(
                    a_number=a_num,
                    method=self.name,
                    formula_str=f"a(n) = {res_pattern}[(n - {start_index}) mod {p_mod}] (mod {m})",
                    latex_str=f"a(n) \\pmod{{{m}}} \\text{{ has period }} {p_mod}",
                    description=f"Residue class modulo {m} is periodic with period {p_mod}",
                    complexity=3.0 + p_mod * 0.2,
                    terms_tested=len(terms),
                    verification_status=VerificationStatus.HEURISTIC,  # Modular congruence is partial characterization
                    details={"modulus": m, "period": p_mod, "pattern": res_pattern},
                ))

        return results

    def _find_exact_period(self, seq: List[int]) -> Optional[int]:
        n = len(seq)
        for p in range(1, min(self.max_period, n // 2) + 1):
            if all(seq[i] == seq[i % p] for i in range(n)):
                return p
        return None

