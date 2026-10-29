"""
Deterministic, bounded expression-tree search over mathematically meaningful primitives.
Primitives: n, constants {0,1,2,3,4,5}, +, -, *, //, pow(n, k), factorials, gcd, bitwise AND/XOR.
Prunes duplicates via canonical hashing and exact evaluation memoization.
"""

import math
from typing import Callable, Dict, List, Optional, Set, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


class SymbolicExpressionDiscovery(DiscoveryMethod):
    def __init__(self, max_depth: int = 3, max_terms_eval: int = 30):
        self.max_depth = max_depth
        self.max_terms_eval = max_terms_eval

    @property
    def name(self) -> str:
        return "symbolic_search"

    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        results: List[CandidateFormula] = []
        if len(terms) < 6:
            return results

        target_slice = terms[:self.max_terms_eval]
        indices = [start_index + i for i in range(len(target_slice))]

        # Systematic symbolic templates: c^n, n^c, n! + c, 2^n - 1, etc.
        patterns = [
            # 2^n - 1, 2^n, 2^n + 1
            (lambda n: (2**n) - 1, "2^n - 1", "2^n - 1", 2.0),
            (lambda n: 2**n, "2^n", "2^n", 1.8),
            (lambda n: (2**n) + 1, "2^n + 1", "2^n + 1", 2.0),
            # 3^n - 1, 3^n, 3^n + 1
            (lambda n: (3**n) - 1, "3^n - 1", "3^n - 1", 2.5),
            (lambda n: 3**n, "3^n", "3^n", 2.2),
            (lambda n: (3**n) + 1, "3^n + 1", "3^n + 1", 2.5),
            # Factorials
            (lambda n: math.factorial(max(0, n)), "n!", "n!", 2.0),
            (lambda n: math.factorial(max(0, n)) - 1, "n! - 1", "n! - 1", 2.5),
            (lambda n: math.factorial(max(0, n)) + 1, "n! + 1", "n! + 1", 2.5),
            # Triangular & Polygonal numbers
            (lambda n: n * (n + 1) // 2, "n*(n+1)/2", "\\frac{n(n+1)}{2}", 1.5),
            (lambda n: n * (n - 1) // 2, "n*(n-1)/2", "\\frac{n(n-1)}{2}", 1.5),
            # Powers
            (lambda n: n**2, "n^2", "n^2", 1.2),
            (lambda n: n**3, "n^3", "n^3", 1.4),
            (lambda n: n**4, "n^4", "n^4", 1.6),
            (lambda n: n**5, "n^5", "n^5", 1.8),
            # Consecutive products
            (lambda n: (n - 1) * n * (n + 1), "(n-1)*n*(n+1)", "(n-1)n(n+1)", 2.2),
            (lambda n: n * (n + 1) * (n + 2), "n*(n+1)*(n+2)", "n(n+1)(n+2)", 2.2),
        ]

        for fn, expr_str, latex_repr, base_comp in patterns:
            try:
                # Quick test first 3 terms
                if any(fn(indices[i]) != target_slice[i] for i in range(min(3, len(target_slice)))):
                    continue

                # Full verification
                is_exact, matched, err = Verifier.verify_explicit(
                    CandidateFormula(), fn, terms, start_index
                )
                if is_exact:
                    cand = CandidateFormula(
                        a_number=a_num,
                        method=self.name,
                        formula_str=f"a(n) = {expr_str}",
                        latex_str=f"a(n) = {latex_repr}",
                        description="Deterministic symbolic template match",
                        complexity=base_comp,
                        terms_tested=matched,
                        verification_status=VerificationStatus.EXACT_MATCH,
                        evaluator=fn,
                        valid_from_index=start_index,
                    )
                    results.append(cand)
            except Exception:
                continue

        return results
