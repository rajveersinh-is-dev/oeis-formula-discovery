"""
Modular Product & Euler Transform Generating Function Discovery Module.
Discovers exact infinite product generating functions and Euler transforms:
G(x) = sum_{n >= 0} a(n) * x^n = scale * x^{n_0} * prod_{k=1}^infinity (1 - x^k)^{-c_k}
where c_k are integers that are either constant or periodic modulo M.

Captures fundamental combinatorial, modular, and partition families:
- Partition numbers (A000041): G(x) = prod_{k=1}^inf 1 / (1 - x^k)  (c_k = 1)
- Partitions into distinct parts (A000009): G(x) = prod_{k=1}^inf (1 + x^k) = prod_{k odd} 1 / (1 - x^k) (c_k periodic mod 2: [1, 0])
- Euler's pentagonal series / Dedekind eta: G(x) = prod_{k=1}^inf (1 - x^k)  (c_k = -1)
- Ramanujan's tau function (A000594): G(x) = x * prod_{k=1}^inf (1 - x^k)^24  (c_k = -24)
- First Rogers-Ramanujan identity (A003114): c_k periodic mod 5: [1, 0, 0, 1, 0]
- Second Rogers-Ramanujan identity (A003106): c_k periodic mod 5: [0, 1, 1, 0, 0]
- Jacobi theta functions & McKay-Thompson series

All logarithmic derivative and Mobius inversion algorithms use exact integer arithmetic.
"""

import math
from typing import Dict, List, Optional, Tuple
from ..candidate.model import CandidateFormula, VerificationStatus
from ..candidate.verifier import Verifier
from .base import DiscoveryMethod


def _moebius(n: int) -> int:
    """Computes Mobius function mu(n) exactly."""
    if n == 1:
        return 1
    p = 0
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            temp //= d
            p += 1
            if temp % d == 0:
                return 0
        d += 1
    if temp > 1:
        p += 1
    return -1 if p % 2 else 1


class ModularProductDiscovery(DiscoveryMethod):
    def __init__(self, max_period: int = 12):
        self.max_period = max_period

    @property
    def name(self) -> str:
        return "modular_product"

    def discover(
        self,
        a_number: str,
        terms: List[int],
        start_index: int = 0,
    ) -> List[CandidateFormula]:
        candidates: List[CandidateFormula] = []
        N = len(terms)
        if N < 12:
            return candidates

        # 1. Locate leading non-zero term offset_n0
        offset_n0 = 0
        while offset_n0 < N and terms[offset_n0] == 0:
            offset_n0 += 1

        if offset_n0 >= N - 8:
            return candidates

        scale = terms[offset_n0]
        if scale == 0:
            return candidates

        # Check if all terms are divisible by scale
        if scale != 1 and scale != -1:
            if any(t % scale != 0 for t in terms[offset_n0:]):
                return candidates

        # Normalized series A(x) with A[0] = 1
        A = [terms[offset_n0 + m] // scale for m in range(N - offset_n0)]
        M = len(A)
        if M < 8 or A[0] != 1:
            return candidates

        # 2. Compute logarithmic derivative coefficients b_1 .. b_{M-1}
        # n * A_n = sum_{k=1}^n b_k * A_{n-k}
        # b_n = n * A_n - sum_{k=1}^{n-1} A_{n-k} * b_k
        b = [0] * M
        for n in range(1, M):
            s = n * A[n]
            for k in range(1, n):
                s -= A[n - k] * b[k]
            b[n] = s

        # 3. Compute exponents c_k via Mobius inversion:
        # m * c_m = sum_{d|m} mu(m // d) * b_d
        c = [0] * M
        for m in range(1, M):
            sm = 0
            d = 1
            while d * d <= m:
                if m % d == 0:
                    sm += _moebius(m // d) * b[d]
                    if d * d != m:
                        other = m // d
                        sm += _moebius(d) * b[other]
                d += 1
            if sm % m != 0:
                # Exponents are not integers -> not an integer Euler product
                return candidates
            c[m] = sm // m

        exponents = c[1:]  # c_1, c_2, ..., c_{M-1}
        K = len(exponents)

        # 4. Check Case A: Constant exponent c_k = C
        cand_const = self._check_constant(a_number, terms, start_index, offset_n0, scale, exponents)
        if cand_const is not None:
            candidates.append(cand_const)
            return candidates

        # 5. Check Case B: Periodic exponents c_k mod P
        cand_per = self._check_periodic(a_number, terms, start_index, offset_n0, scale, exponents)
        if cand_per is not None:
            candidates.append(cand_per)
            return candidates

        return candidates

    def _check_constant(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        offset_n0: int,
        scale: int,
        exponents: List[int],
    ) -> Optional[CandidateFormula]:
        C = exponents[0]
        if C == 0:
            return None
        if not all(val == C for val in exponents):
            return None

        # Build formula string
        prefix_parts = []
        if scale != 1:
            prefix_parts.append(f"{scale}*")
        if offset_n0 > 0:
            x_str = f"x^{offset_n0}" if offset_n0 > 1 else "x"
            prefix_parts.append(f"{x_str}*")
        pfx = "".join(prefix_parts)

        if C == 1:
            prod_str = "prod_{k=1}^inf 1 / (1 - x^k)"
            desc = "Generating function is the partition product prod_{k=1}^inf 1 / (1 - x^k)"
        elif C == -1:
            prod_str = "prod_{k=1}^inf (1 - x^k)"
            desc = "Generating function is the Euler pentagonal product prod_{k=1}^inf (1 - x^k)"
        elif C < 0:
            pow_val = abs(C)
            pow_str = f"^{pow_val}" if pow_val > 1 else ""
            prod_str = f"prod_{{k=1}}^inf (1 - x^k){pow_str}"
            desc = f"Generating function is the modular product prod_{{k=1}}^inf (1 - x^k)^{pow_val}"
        else:
            pow_str = f"^{C}" if C > 1 else ""
            prod_str = f"prod_{{k=1}}^inf 1 / (1 - x^k){pow_str}"
            desc = f"Generating function is the inverse product prod_{{k=1}}^inf 1 / (1 - x^k)^{C}"

        formula_str = f"G(x) = {pfx}{prod_str}"
        latex_str = f"G(x) = {pfx}\\prod_{{k=1}}^\\infty " + ("\\frac{1}{1 - x^k}" if C == 1 else ("(1 - x^k)" if C == -1 else f"(1 - x^k)^{{{-C}}}"))

        cand = CandidateFormula(
            a_number=a_number,
            method=self.name,
            formula_str=formula_str,
            latex_str=latex_str,
            description=desc,
            complexity=2.0 + len(str(abs(C))) * 0.2 + offset_n0 * 0.3,
            terms_tested=len(terms),
            valid_from_index=start_index,
            initial_conditions=terms[:offset_n0 + 1],
            details={"offset_n0": offset_n0, "scale": scale, "exponents": [C], "is_periodic": False, "period": 1},
            verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
        )

        is_valid, matched, msg = Verifier.verify_modular_product(
            candidate=cand,
            offset_n0=offset_n0,
            scale=scale,
            exponents=[C],
            is_periodic=False,
            period=1,
            all_terms=terms,
            start_index=start_index,
        )

        if is_valid:
            cand.verification_status = VerificationStatus.EXACT_MATCH
            cand.terms_tested = matched
            return cand

        return None

    def _check_periodic(
        self,
        a_number: str,
        terms: List[int],
        start_index: int,
        offset_n0: int,
        scale: int,
        exponents: List[int],
    ) -> Optional[CandidateFormula]:
        K = len(exponents)

        for P in (2, 3, 4, 5, 6, 8, 10, 12):
            if P > self.max_period or K < 2 * P + 2:
                continue

            cycle = exponents[:P]
            # Must not be all zero or all identical
            if all(v == 0 for v in cycle) or all(v == cycle[0] for v in cycle):
                continue

            if all(exponents[i] == cycle[i % P] for i in range(K)):
                # Found periodic exponents
                prefix_parts = []
                if scale != 1:
                    prefix_parts.append(f"{scale}*")
                if offset_n0 > 0:
                    x_str = f"x^{offset_n0}" if offset_n0 > 1 else "x"
                    prefix_parts.append(f"{x_str}*")
                pfx = "".join(prefix_parts)

                cycle_str = "[" + ", ".join(str(v) for v in cycle) + "]"
                # Human readable form for special known cases
                if P == 2 and cycle == [1, 0]:
                    prod_str = "prod_{k odd} 1 / (1 - x^k) = prod_{k=1}^inf (1 + x^k)"
                    desc = "Generating function is the distinct-parts partition product"
                elif P == 5 and cycle == [1, 0, 0, 1, 0]:
                    prod_str = "prod_{k=1}^inf 1 / ((1 - x^{5k-4})*(1 - x^{5k-1}))"
                    desc = "Generating function is the first Rogers-Ramanujan modular product"
                elif P == 5 and cycle == [0, 1, 1, 0, 0]:
                    prod_str = "prod_{k=1}^inf 1 / ((1 - x^{5k-3})*(1 - x^{5k-2}))"
                    desc = "Generating function is the second Rogers-Ramanujan modular product"
                else:
                    prod_str = f"prod_{{k=1}}^inf (1 - x^k)^(-c_k) with c_k mod {P} = {cycle_str}"
                    desc = f"Modular product with period-{P} exponent pattern {cycle_str}"

                formula_str = f"G(x) = {pfx}{prod_str}"
                cand = CandidateFormula(
                    a_number=a_number,
                    method=self.name,
                    formula_str=formula_str,
                    latex_str=formula_str,
                    description=desc,
                    complexity=2.2 + P * 0.4 + offset_n0 * 0.3,
                    terms_tested=len(terms),
                    valid_from_index=start_index,
                    initial_conditions=terms[:offset_n0 + 1],
                    details={"offset_n0": offset_n0, "scale": scale, "exponents": cycle, "is_periodic": True, "period": P},
                    verification_status=VerificationStatus.NO_CANDIDATE_FOUND,
                )

                is_valid, matched, msg = Verifier.verify_modular_product(
                    candidate=cand,
                    offset_n0=offset_n0,
                    scale=scale,
                    exponents=cycle,
                    is_periodic=True,
                    period=P,
                    all_terms=terms,
                    start_index=start_index,
                )

                if is_valid:
                    cand.verification_status = VerificationStatus.EXACT_MATCH
                    cand.terms_tested = matched
                    return cand

        return None
