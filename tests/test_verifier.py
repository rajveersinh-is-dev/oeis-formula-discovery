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


def test_verifier_rational_recurrence():
    cand = CandidateFormula()
    # Lyness: a(n) = (a(n-1) + 1) / a(n-2)
    terms = [1, 2, 3, 2, 1, 1, 2, 3, 2, 1]
    is_exact, matched, _ = Verifier.verify_rational_recurrence(
        cand, "lyness", {"c1": 1, "c0": 1}, [1, 2], terms, 0
    )
    assert is_exact is True
    assert matched == 10

    # Bad terms
    bad = [1, 2, 3, 2, 1, 99, 2, 3, 2, 1]
    is_exact, matched, err = Verifier.verify_rational_recurrence(
        cand, "lyness", {"c1": 1, "c0": 1}, [1, 2], bad, 0
    )
    assert is_exact is False
    assert "Rational mismatch" in err


def test_verifier_divide_and_conquer():
    cand = CandidateFormula()
    # Stern's diatomic
    stern = [0, 1, 1, 2, 1, 3, 2, 3, 1, 4, 3, 5]
    rules = [
        {"c0": 1, "c1": 0, "e": 0, "d": 0},
        {"c0": 1, "c1": 1, "e": 0, "d": 0},
    ]
    is_exact, matched, _ = Verifier.verify_divide_and_conquer(
        cand, 2, rules, [0, 1], stern, 0
    )
    assert is_exact is True
    assert matched == 12

    # Bad term
    bad_stern = [0, 1, 1, 2, 1, 99, 2, 3, 1, 4, 3, 5]
    is_exact, matched, err = Verifier.verify_divide_and_conquer(
        cand, 2, rules, [0, 1], bad_stern, 0
    )
    assert is_exact is False
    assert "Divide-and-conquer mismatch" in err


def test_verifier_interleaved_recurrence():
    cand = CandidateFormula()
    # a(2k) = 2^k, a(2k+1) = 3^k
    terms = [1, 1, 2, 3, 4, 9, 8, 27]
    branch_recs = [[2], [3]]
    is_exact, matched, _ = Verifier.verify_interleaved_recurrence(
        cand, 2, branch_recs, [1, 1], terms, 0
    )
    assert is_exact is True
    assert matched == 8

    # Bad term
    bad = [1, 1, 2, 3, 5, 9, 8, 27]
    is_exact, matched, err = Verifier.verify_interleaved_recurrence(
        cand, 2, branch_recs, [1, 1], bad, 0
    )
    assert is_exact is False
    assert "Interleaved mismatch" in err


def test_verifier_continued_fraction():
    cand = CandidateFormula()
    # Bessel: a(n) = n*a(n-1) + a(n-2), a(0)=1, a(1)=1
    terms = [1, 1, 3, 10, 43, 225]
    is_exact, matched, _ = Verifier.verify_continued_fraction(
        cand, 1, lambda n: n, [1, 1], terms, 0
    )
    assert is_exact is True
    assert matched == 6

    # Bad
    bad = [1, 1, 3, 10, 44, 225]
    is_exact, matched, err = Verifier.verify_continued_fraction(
        cand, 1, lambda n: n, [1, 1], bad, 0
    )
    assert is_exact is False
    assert "Continued fraction mismatch" in err


def test_verifier_nested_recurrence():
    cand = CandidateFormula()
    # Hofstadter Q: 1, 1, 2, 3, 3, 4, 5, 5
    q = [1, 1, 2, 3, 3, 4, 5, 5]
    is_exact, matched, _ = Verifier.verify_nested_recurrence(
        cand, "hofstadter_q", {}, [1, 1], q, 1
    )
    assert is_exact is True
    assert matched == 8

    # Bad
    bad_q = [1, 1, 2, 3, 3, 9, 5, 5]
    is_exact, matched, err = Verifier.verify_nested_recurrence(
        cand, "hofstadter_q", {}, [1, 1], bad_q, 1
    )
    assert is_exact is False
    assert "Nested recurrence mismatch" in err


def test_verifier_inhomogeneous_exponential():
    cand = CandidateFormula()
    # a(n) = 2*a(n-1) + 3^n, a(0)=1
    terms = [1, 5, 19, 65, 211]
    is_exact, matched, _ = Verifier.verify_inhomogeneous_exponential(
        cand, [2], 3, 1, [1], terms, 0
    )
    assert is_exact is True
    assert matched == 5

    # Bad
    bad = [1, 5, 19, 66, 211]
    is_exact, matched, err = Verifier.verify_inhomogeneous_exponential(
        cand, [2], 3, 1, [1], bad, 0
    )
    assert is_exact is False
    assert "Inhomogeneous exponential mismatch" in err


def test_verifier_modular_product():
    from src.candidate.model import CandidateFormula
    from src.candidate.verifier import Verifier
    cand = CandidateFormula()
    # Partition numbers: G(x) = prod_{k=1}^inf 1 / (1 - x^k)
    partitions = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30]
    is_exact, matched, _ = Verifier.verify_modular_product(
        cand, 0, 1, [1], False, 1, partitions, 0
    )
    assert is_exact is True
    assert matched == 10

    # Bad
    bad = [1, 1, 2, 3, 5, 99, 11, 15, 22, 30]
    is_exact, matched, err = Verifier.verify_modular_product(
        cand, 0, 1, [1], False, 1, bad, 0
    )
    assert is_exact is False
    assert "Modular product mismatch" in err


def test_verifier_q_series():
    from fractions import Fraction
    from src.candidate.model import CandidateFormula
    from src.candidate.verifier import Verifier
    cand = CandidateFormula()
    # a(n) = (2^n - 1)*a(n-1), a(0) = 1
    terms = [1, 1, 3, 21, 315]
    is_exact, matched, _ = Verifier.verify_q_series(
        cand, 2, Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0), 1, [1], terms, 0
    )
    assert is_exact is True
    assert matched == 5

    # Bad
    bad = [1, 1, 3, 22, 315]
    is_exact, matched, err = Verifier.verify_q_series(
        cand, 2, Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0), 1, [1], bad, 0
    )
    assert is_exact is False
    assert "q-series mismatch" in err



