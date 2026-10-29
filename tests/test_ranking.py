import pytest
from src.candidate.model import CandidateFormula, VerificationStatus
from src.candidate.ranking import CandidateRanker


def test_ranking_priority():
    # Explicit polynomial vs heuristic asymptotic
    cand_poly = CandidateFormula(
        id="c1",
        method="finite_differences",
        formula_str="a(n) = n^2",
        complexity=2.0,
        terms_tested=20,
        verification_status=VerificationStatus.EXACT_MATCH,
    )

    cand_asymp = CandidateFormula(
        id="c2",
        method="asymptotic",
        formula_str="a(n) ~ n^2",
        complexity=15.0,
        terms_tested=20,
        verification_status=VerificationStatus.HEURISTIC,
    )

    ranked = CandidateRanker.rank_candidates([cand_asymp, cand_poly])
    assert ranked[0].id == "c1"  # Polynomial outranks heuristic asymptotic
