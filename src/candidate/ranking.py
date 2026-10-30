"""
Scores candidates by mathematical generality, parsimony, and structure.
Hierarchy:
1. Concise explicit polynomial / hypergeometric formulas
2. Low-order exact linear recurrences
3. Compact combinatorial transforms
4. Rational generating functions
5. Modular / finite-state patterns
6. Heuristic asymptotic models
"""

from typing import List
from .model import CandidateFormula, VerificationStatus


class CandidateRanker:
    # Method base penalty (lower is preferred)
    METHOD_PRIORITY = {
        "finite_differences": 1.0,
        "symbolic_search": 1.5,
        "quasipolynomial": 1.8,
        "linear_recurrence": 2.0,
        "divide_and_conquer": 2.02,
        "q_series": 2.03,
        "interleaved_recurrence": 2.04,
        "modular_product": 2.045,
        "inhomogeneous_recurrence": 2.05,
        "continued_fraction": 2.07,
        "rational_recurrence": 2.08,
        "nonlinear_recurrence": 2.1,
        "nested_recurrence": 2.12,
        "algebraic_generating_function": 2.15,
        "convolution_recurrence": 2.2,
        "multiplicative_recurrence": 2.25,
        "holonomic": 2.3,
        "generating_function": 2.5,
        "transforms": 3.0,
        "modular": 4.0,
        "asymptotic": 10.0,
    }

    @classmethod
    def score_candidate(cls, c: CandidateFormula) -> float:
        """
        Calculates an explainable ranking score.
        Lower score is better.
        """
        # Status penalty
        if c.verification_status == VerificationStatus.SYMBOLICALLY_VERIFIED:
            status_penalty = 0.0
        elif c.verification_status == VerificationStatus.EXACT_MATCH:
            status_penalty = 1.0
        elif c.verification_status == VerificationStatus.HEURISTIC:
            status_penalty = 50.0
        else:
            status_penalty = 1000.0

        base_method_cost = cls.METHOD_PRIORITY.get(c.method, 5.0)

        # Minimum Description Length score component
        complexity_score = c.complexity

        # Bonus for testing over large number of terms
        term_confidence_discount = min(5.0, c.terms_tested * 0.1)

        total_score = status_penalty + (base_method_cost * 2.0) + complexity_score - term_confidence_discount
        return max(0.1, total_score)

    @classmethod
    def rank_candidates(cls, candidates: List[CandidateFormula]) -> List[CandidateFormula]:
        """Ranks candidates from most mathematically desirable to least."""
        # Filter out unevaluable or non-matching candidates
        valid = [c for c in candidates if c.verification_status in (
            VerificationStatus.EXACT_MATCH,
            VerificationStatus.SYMBOLICALLY_VERIFIED,
            VerificationStatus.HEURISTIC,
        )]

        return sorted(valid, key=cls.score_candidate)

