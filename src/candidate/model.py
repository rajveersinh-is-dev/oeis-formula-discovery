"""
Structured Candidate representation with mathematical properties, description length, and verification provenance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid


class VerificationStatus(str, Enum):
    EXACT_MATCH = "exact_match"
    SYMBOLICALLY_VERIFIED = "symbolically_verified"
    PARTIALLY_MATCHED = "partially_matched"
    HEURISTIC = "heuristic"
    NO_CANDIDATE_FOUND = "no_candidate_found"
    SEARCH_INCOMPLETE = "search_incomplete"


@dataclass
class CandidateFormula:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    a_number: str = ""
    method: str = ""                       # e.g., 'finite_differences', 'linear_recurrence', 'generating_function'
    formula_str: str = ""                  # Human and parser readable formula, e.g. "a(n) = 2*a(n-1) + 1"
    latex_str: str = ""                    # LaTeX representation
    description: str = ""                  # Detailed mathematical explanation
    complexity: float = 0.0                # Minimum Description Length / tree complexity score
    terms_tested: int = 0
    verification_status: VerificationStatus = VerificationStatus.NO_CANDIDATE_FOUND
    evaluator: Optional[Callable[[int], int]] = None # Exact callable f(n) -> a(n)
    initial_conditions: List[int] = field(default_factory=list)
    recurrence_coeffs: List[int] = field(default_factory=list)
    valid_from_index: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "a_number": self.a_number,
            "method": self.method,
            "formula_str": self.formula_str,
            "latex_str": self.latex_str,
            "description": self.description,
            "complexity": self.complexity,
            "terms_tested": self.terms_tested,
            "verification_status": self.verification_status.value,
            "initial_conditions": self.initial_conditions,
            "recurrence_coeffs": self.recurrence_coeffs,
            "valid_from_index": self.valid_from_index,
            "details": self.details,
        }

