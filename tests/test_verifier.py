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


def test_verifier_inhomogeneous_recurrence():
    # Tower of Hanoi: a(n) = 2*a(n-1) + 1, a(1) = 1
    terms = [1, 3, 7, 15, 31, 63]
    cand = CandidateFormula()
    is_exact, matched, _ = Verifier.verify_inhomogeneous_recurrence(
        cand, rec_coeffs=[2], poly_coeffs=[1], initial_terms=[1], all_terms=terms, start_index=1
    )
    assert is_exact is True
    assert matched == 6

    # Rejection on bad term
    bad_terms = [1, 3, 7, 15, 32, 63]
    is_exact, matched, err = Verifier.verify_inhomogeneous_recurrence(
        cand, rec_coeffs=[2], poly_coeffs=[1], initial_terms=[1], all_terms=bad_terms, start_index=1
    )
    assert is_exact is False
    assert "Inhomogeneous mismatch" in err


def test_verifier_algebraic_generating_function():
    # Catalan: 1, 1, 2, 5, 14, 42; x*G^2 - G + 1 = 0 => A2=[0, 1], A1=[-1], A0=[1]
    terms = [1, 1, 2, 5, 14, 42]
    cand = CandidateFormula()
    is_exact, matched, _ = Verifier.verify_algebraic_generating_function(
        cand, poly_a2=[0, 1], poly_a1=[-1], poly_a0=[1], all_terms=terms, start_index=0
    )
    assert is_exact is True
    assert matched == 6

    # Rejection on mismatch
    bad_terms = [1, 1, 2, 5, 15, 42]
    is_exact, matched, err = Verifier.verify_algebraic_generating_function(
        cand, poly_a2=[0, 1], poly_a1=[-1], poly_a0=[1], all_terms=bad_terms, start_index=0
    )
    assert is_exact is False
    assert "Algebraic generating function mismatch" in err


def test_verifier_convolution_recurrence():
    cand = CandidateFormula()
    # Catalan Cauchy
    catalan = [1, 1, 2, 5, 14, 42, 132]
    is_exact, matched, _ = Verifier.verify_convolution_recurrence(
        cand, "catalan_cauchy", [1], catalan, 0
    )
    assert is_exact is True
    assert matched == 7

    # Motzkin Cauchy
    motzkin = [1, 1, 2, 4, 9, 21, 51]
    is_exact, matched, _ = Verifier.verify_convolution_recurrence(
        cand, "motzkin_cauchy", [1, 1], motzkin, 0
    )
    assert is_exact is True
    assert matched == 7

    # Bell binomial
    bell = [1, 1, 2, 5, 15, 52, 203]
    is_exact, matched, _ = Verifier.verify_convolution_recurrence(
        cand, "bell_binomial", [1], bell, 0
    )
    assert is_exact is True
    assert matched == 7

    # Rejection on corrupted sequence
    bad_catalan = [1, 1, 2, 5, 14, 40, 132]
    is_exact, matched, err = Verifier.verify_convolution_recurrence(
        cand, "catalan_cauchy", [1], bad_catalan, 0
    )
    assert is_exact is False
    assert "Convolution mismatch" in err


def test_verifier_multiplicative_recurrence():
    cand = CandidateFormula()
    # a(n) = a(n-1) * a(n-2)
    terms = [2, 3, 6, 18, 108, 1944]
    is_exact, matched, _ = Verifier.verify_multiplicative_recurrence(
        cand, mult_c=1, pow_p=1, pow_q=1, initial_terms=[2, 3], all_terms=terms, start_index=0
    )
    assert is_exact is True
    assert matched == 6

    # Rejection
    bad_terms = [2, 3, 6, 18, 109, 1944]
    is_exact, matched, err = Verifier.verify_multiplicative_recurrence(
        cand, mult_c=1, pow_p=1, pow_q=1, initial_terms=[2, 3], all_terms=bad_terms, start_index=0
    )
    assert is_exact is False
    assert "Multiplicative mismatch" in err


