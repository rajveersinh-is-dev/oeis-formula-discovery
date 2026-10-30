"""
Deterministic Discovery Orchestrator.
Executes all mathematical methods against parsed OEIS sequences within per-method budgets.
"""

import time
from typing import List, Optional
from ..candidate.model import CandidateFormula
from ..candidate.ranking import CandidateRanker
from ..discovery.asymptotic import AsymptoticGrowthDiscovery
from ..discovery.finite_differences import FiniteDifferenceDiscovery
from ..discovery.generating_function import GeneratingFunctionDiscovery
from ..discovery.holonomic import HolonomicDiscovery
from ..discovery.linear_recurrence import LinearRecurrenceDiscovery
from ..discovery.modular import ModularPatternDiscovery
from ..discovery.nonlinear import NonlinearRecurrenceDiscovery
from ..discovery.quasipolynomial import QuasipolynomialDiscovery
from ..discovery.symbolic_search import SymbolicExpressionDiscovery
from ..discovery.transforms import TransformDiscovery
from ..ingestion.db import OEISDatabase
from ..ingestion.parser import OEISRecord


class DiscoveryEngine:
    def __init__(self, db: Optional[OEISDatabase] = None):
        self.db = db
        self.methods = [
            FiniteDifferenceDiscovery(max_degree=6),
            QuasipolynomialDiscovery(max_period=6, max_degree=4),
            LinearRecurrenceDiscovery(max_order=8),
            HolonomicDiscovery(max_order=4, max_degree=3),
            NonlinearRecurrenceDiscovery(max_degree=3, max_somos_k=6),
            GeneratingFunctionDiscovery(max_degree=6),
            SymbolicExpressionDiscovery(max_depth=3),
            TransformDiscovery(),
            ModularPatternDiscovery(max_modulus=12, max_period=16),
            AsymptoticGrowthDiscovery(),
        ]

    def analyze_sequence(self, record: OEISRecord) -> List[CandidateFormula]:
        """Runs all mathematical methods deterministically against the sequence."""
        all_candidates: List[CandidateFormula] = []
        terms = record.terms
        start_idx = record.offset_first_term

        for method in self.methods:
            try:
                candidates = method.discover(record.a_number, terms, start_idx)
                all_candidates.extend(candidates)
            except Exception:
                # Failure recorded honestly; other methods continue
                continue

        # Rank all discovered candidates
        ranked = CandidateRanker.rank_candidates(all_candidates)

        # Store in database if DB is attached
        if self.db:
            best_id = ranked[0].id if ranked else None
            for c in ranked:
                self.db.record_candidate(c.to_dict())
            self.db.update_scan_status(
                record.a_number,
                status="completed",
                count=len(ranked),
                best_id=best_id,
            )

        return ranked

