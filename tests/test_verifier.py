import pytest
from src.candidate.model import CandidateFormula
from src.candidate.verifier import Verifier


def test_verifier_explicit_success():
    terms = [n**2 for n in range(10)]
    is_exact, matched, err = Verifier.verify_explicit(
        CandidateFormula(), lambda n: n**2, terms, 0
    )
    assert is_exact is True
    assert matched == 10
    assert "All terms matched exactly" in err


def test_verifier_explicit_rejection():
    terms = [1, 2, 3, 4, 5]
    is_exact, matched, err = Verifier.verify_explicit(
        CandidateFormula(), lambda n: n + 2, terms, 0
    )
    assert is_exact is False
    assert matched == 0
    assert "Mismatch" in err


def test_verifier_recurrence_success():
    # Fibonacci: 0, 1, 1, 2, 3, 5, 8
    terms = [0, 1, 1, 2, 3, 5, 8]
    coeffs = [1, 1]  # a(n) = a(n-1) + a(n-2)
    initial_terms = [0, 1]
    is_exact, matched, err = Verifier.verify_recurrence(
        CandidateFormula(), coeffs, initial_terms, terms, 0
    )
    assert is_exact is True
    assert matched == 7


def test_verifier_recurrence_rejection():
    # Terms that do not follow recurrence
    terms = [0, 1, 1, 2, 3, 99, 100]
    coeffs = [1, 1]
    initial_terms = [0, 1]
    is_exact, matched, err = Verifier.verify_recurrence(
        CandidateFormula(), coeffs, initial_terms, terms, 0
    )
    assert is_exact is False
    assert "Recurrence mismatch" in err

