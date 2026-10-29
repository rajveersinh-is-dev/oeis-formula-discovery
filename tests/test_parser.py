import pytest
from src.ingestion.parser import OEISParser, OEISRecord

SAMPLE_OEIS_FIBONACCI = """
%I A000045 M0692 N0256
%S A000045 0,1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584,4181,
%T A000045 6765,10946,17711,28657,46368,75025,121393,196418,317811,514229,
%U A000045 832040,1346269,2178309,3524578,5702887,9227465,14930352
%N A000045 Fibonacci numbers: F(n) = F(n-1) + F(n-2) with F(0) = 0 and F(1) = 1.
%D A000045 M. Abramowitz and I. A. Stegun, eds., Handbook of Mathematical Functions.
%H A000045 N. J. A. Sloane, Fibonacci Numbers and the Golden Ratio
%F A000045 F(n) = ((1+sqrt(5))^n - (1-sqrt(5))^n)/(2^n*sqrt(5)).
%O A000045 0,4
%K A000045 core,nonn,easy
%A A000045 N. J. A. Sloane, 1964
"""

SAMPLE_OEIS_NO_FORMULA = """
%I A999999
%S A999999 1,4,9,16,25,36,49,64,81,100,121,144,169
%N A999999 Hypothetical sequence with no explicit %F field.
%C A999999 Test entry for discovery engine.
%O A999999 1,2
%K A999999 nonn
"""


def test_parse_fibonacci():
    lines = SAMPLE_OEIS_FIBONACCI.strip().split("\n")
    rec = OEISParser.parse_entry_lines(lines)
    assert rec is not None
    assert rec.a_number == "A000045"
    assert rec.offset_first_term == 0
    assert rec.offset_first_gt_one == 4
    assert len(rec.terms) == 37
    assert rec.terms[:7] == [0, 1, 1, 2, 3, 5, 8]
    assert rec.has_explicit_formula is True
    assert rec.is_eligible_target is False  # Ineligible because %F exists


def test_parse_no_formula():
    lines = SAMPLE_OEIS_NO_FORMULA.strip().split("\n")
    rec = OEISParser.parse_entry_lines(lines)
    assert rec is not None
    assert rec.a_number == "A999999"
    assert rec.offset_first_term == 1
    assert rec.terms == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169]
    assert rec.has_explicit_formula is False
    assert rec.is_eligible_target is True   # Eligible target!


def test_parse_negative_terms():
    lines = [
        "%I A000000",
        "%S A000000 -5,-3,-1,1,3,5,7,9",
        "%N A000000 Arithmetic sequence with negative terms",
        "%O A000000 0,1",
    ]
    rec = OEISParser.parse_entry_lines(lines)
    assert rec is not None
    assert rec.terms == [-5, -3, -1, 1, 3, 5, 7, 9]

