"""
Abstract Base Class for all deterministic sequence discovery modules.
"""

from abc import ABC, abstractmethod
from typing import List
from ..candidate.model import CandidateFormula


class DiscoveryMethod(ABC):
    """Common interface for all mathematical discovery algorithms."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the discovery algorithm."""
        pass

    @abstractmethod
    def discover(self, a_num: str, terms: List[int], start_index: int) -> List[CandidateFormula]:
        """
        Executes deterministic discovery against the provided terms.

        Args:
            a_num: OEIS sequence identifier (e.g., 'A000045')
            terms: List of arbitrary-precision integer sequence terms
            start_index: The OEIS offset (n_0) corresponding to terms[0]

        Returns:
            List of structured CandidateFormula instances found.
        """
        pass

