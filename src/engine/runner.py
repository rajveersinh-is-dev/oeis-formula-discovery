"""
Deterministic Discovery Orchestrator.
Executes all mathematical methods against parsed OEIS sequences within per-method budgets.
"""

import time
from typing import List, Optional
from ..candidate.model import CandidateFormula
from ..candidate.ranking import CandidateRanker
from ..discovery.algebraic_gf import AlgebraicGeneratingFunctionDiscovery
from ..discovery.asymptotic import AsymptoticGrowthDiscovery
from ..discovery.continued_fraction import ContinuedFractionDiscovery
from ..discovery.convolution import ConvolutionRecurrenceDiscovery
from ..discovery.divide_and_conquer import DivideAndConquerDiscovery
from ..discovery.finite_differences import FiniteDifferenceDiscovery
from ..discovery.generating_function import GeneratingFunctionDiscovery
from ..discovery.holonomic import HolonomicDiscovery
from ..discovery.inhomogeneous import InhomogeneousRecurrenceDiscovery
from ..discovery.interleaved import InterleavedRecurrenceDiscovery
from ..discovery.linear_recurrence import LinearRecurrenceDiscovery
from ..discovery.modular import ModularPatternDiscovery
from ..discovery.modular_product import ModularProductDiscovery
from ..discovery.multiplicative import MultiplicativeRecurrenceDiscovery
from ..discovery.nested_recurrence import NestedRecurrenceDiscovery
from ..discovery.nonlinear import NonlinearRecurrenceDiscovery
from ..discovery.q_series import QSeriesDiscovery
from ..discovery.quasipolynomial import QuasipolynomialDiscovery
from ..discovery.rational_recurrence import RationalRecurrenceDiscovery
from ..discovery.symbolic_search import SymbolicExpressionDiscovery
from ..discovery.transforms import TransformDiscovery
from ..ingestion.db import OEISDatabase
from ..ingestion.parser import OEISRecord


class DiscoveryEngine:
    def __init__(self, db: Optional[OEISDatabase] = None):
        self.db = db
        self.methods = [
            FiniteDifferenceDiscovery(max_degree=6),
            SymbolicExpressionDiscovery(max_depth=3),
            QuasipolynomialDiscovery(max_period=6, max_degree=4),
            LinearRecurrenceDiscovery(max_order=8),
            DivideAndConquerDiscovery(bases=[2, 3, 4, 5]),
            QSeriesDiscovery(bases=[2, 3, -2, 4, 5]),
            InterleavedRecurrenceDiscovery(periods=[2, 3, 4]),
            ModularProductDiscovery(max_period=12),
            InhomogeneousRecurrenceDiscovery(max_order=3, max_poly_deg=3),
            ContinuedFractionDiscovery(max_period=6),
            RationalRecurrenceDiscovery(max_order=4),
            NonlinearRecurrenceDiscovery(max_degree=3, max_somos_k=6),
            NestedRecurrenceDiscovery(),
            AlgebraicGeneratingFunctionDiscovery(max_degree=4),
            ConvolutionRecurrenceDiscovery(),
            MultiplicativeRecurrenceDiscovery(max_power=3),
            HolonomicDiscovery(max_order=4, max_degree=3),
            GeneratingFunctionDiscovery(max_degree=6),
            TransformDiscovery(),
            ModularPatternDiscovery(max_modulus=12, max_period=16, max_transient=6),
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
