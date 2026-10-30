"""
Hard Sequences Discovery Benchmark Suite.
Rigorous benchmark on mathematically demanding sequence families:
1. Holonomic / P-finite Sequences (No constant-coefficient recurrence exists!):
   - Catalan numbers (A000108)
   - Motzkin numbers (A001006)
   - Central Delannoy numbers (A001850)
   - Large Schroder numbers (A006318)
   - Subfactorials / Derangements (A000166)
   - Apery numbers for zeta(3) (A005259)
   - Apery numbers for zeta(2) (A005258)
   - Double factorials (A001147)
2. Quasipolynomials (Multisection / periodic polynomial branches):
   - Quarter squares floor(n^2 / 4) (A002620)
   - Coin change for {1, 2}: floor(n/2) + 1 (A004526)
   - Periodic quadratic/linear quasipolynomial of period 3
3. Hard Real-World Sequences Lacking Listed Formulas (%F):
   - Self-avoiding walks in 2D and 3D (A001411, A001412)
   - Combinatorial state spaces (Rubik's cube A080601, Chess ply A048987)
"""

import math
import time
from typing import List, Tuple
from rich.console import Console
from rich.table import Table

from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISRecord

console = Console()


def generate_hard_benchmark_suite() -> List[Tuple[OEISRecord, str]]:
    suite = []

    # 1. Catalan numbers A000108
    cat_terms = [math.comb(2 * n, n) // (n + 1) for n in range(25)]
    suite.append((
        OEISRecord(
            a_number="A000108",
            id_number=108,
            name="Catalan numbers: C(n) = (1/(n+1))*binom(2n, n)",
            offset_first_term=0,
            terms=cat_terms,
        ),
        "Holonomic (Order 1, Degree 1)"
    ))

    # 2. Motzkin numbers A001006
    motzkin_terms = []
    for n in range(25):
        val = sum((math.comb(2 * k, k) // (k + 1)) * math.comb(n, 2 * k) for k in range(n // 2 + 1))
        motzkin_terms.append(val)
    suite.append((
        OEISRecord(
            a_number="A001006",
            id_number=1006,
            name="Motzkin numbers",
            offset_first_term=0,
            terms=motzkin_terms,
        ),
        "Holonomic (Order 2, Degree 1)"
    ))

    # 3. Central Delannoy numbers A001850
    delannoy_terms = []
    for n in range(25):
        val = sum(math.comb(n, k) * math.comb(n + k, k) for k in range(n + 1))
        delannoy_terms.append(val)
    suite.append((
        OEISRecord(
            a_number="A001850",
            id_number=1850,
            name="Central Delannoy numbers",
            offset_first_term=0,
            terms=delannoy_terms,
        ),
        "Holonomic (Order 2, Degree 1)"
    ))

    # 4. Large Schroder numbers A006318
    schroder = [1, 2]
    for n in range(2, 25):
        val = ((6 * n - 3) * schroder[-1] - (n - 2) * schroder[-2]) // (n + 1)
        schroder.append(val)
    suite.append((
        OEISRecord(
            a_number="A006318",
            id_number=6318,
            name="Large Schroder numbers",
            offset_first_term=0,
            terms=schroder,
        ),
        "Holonomic (Order 2, Degree 1)"
    ))

    # 5. Derangements / Subfactorials A000166
    derangements = [1, 0]
    for n in range(2, 22):
        derangements.append((n - 1) * (derangements[-1] + derangements[-2]))
    suite.append((
        OEISRecord(
            a_number="A000166",
            id_number=166,
            name="Subfactorials / Derangements",
            offset_first_term=0,
            terms=derangements,
        ),
        "Holonomic (Order 2, Degree 1)"
    ))

    # 6. Apery numbers for zeta(3) A005259
    apery_z3 = []
    for n in range(25):
        val = sum(math.comb(n, k)**2 * math.comb(n + k, k)**2 for k in range(n + 1))
        apery_z3.append(val)
    suite.append((
        OEISRecord(
            a_number="A005259",
            id_number=5259,
            name="Apery numbers for zeta(3)",
            offset_first_term=0,
            terms=apery_z3,
        ),
        "Holonomic (Order 2, Degree 3)"
    ))

    # 7. Apery numbers for zeta(2) A005258
    apery_z2 = [sum(math.comb(n, k)**2 * math.comb(n + k, k) for k in range(n + 1)) for n in range(25)]
    suite.append((
        OEISRecord(
            a_number="A005258",
            id_number=5258,
            name="Apery numbers for zeta(2)",
            offset_first_term=0,
            terms=apery_z2,
        ),
        "Holonomic (Order 2, Degree 2)"
    ))

    # 8. Double factorials (2n-1)!! A001147
    dfact = [1]
    curr = 1
    for n in range(1, 22):
        curr *= (2 * n - 1)
        dfact.append(curr)
    suite.append((
        OEISRecord(
            a_number="A001147",
            id_number=1147,
            name="Double factorials (2n-1)!!",
            offset_first_term=0,
            terms=dfact,
        ),
        "Holonomic (Order 1, Degree 1)"
    ))

    # 9. Quarter squares A002620
    qsq = [n**2 // 4 for n in range(30)]
    suite.append((
        OEISRecord(
            a_number="A002620",
            id_number=2620,
            name="Quarter squares: floor(n^2 / 4)",
            offset_first_term=0,
            terms=qsq,
        ),
        "Quasipolynomial (Period 2, Deg 2)"
    ))

    # 10. Coin change for {1, 2} A004526
    cchange = [n // 2 + 1 for n in range(25)]
    suite.append((
        OEISRecord(
            a_number="A004526",
            id_number=4526,
            name="Coin change {1, 2}: floor(n/2) + 1",
            offset_first_term=0,
            terms=cchange,
        ),
        "Quasipolynomial (Period 2, Deg 1)"
    ))

    # 11. Period 3 Quasipolynomial
    p3_terms = []
    for n in range(30):
        k = n // 3
        r = n % 3
        if r == 0:
            p3_terms.append(k**2)
        elif r == 1:
            p3_terms.append(2 * k + 1)
        else:
            p3_terms.append(3 * k**2 + 5)
    suite.append((
        OEISRecord(
            a_number="SYN_QP3",
            id_number=9999,
            name="Synthetic period 3 quadratic quasipolynomial",
            offset_first_term=0,
            terms=p3_terms,
        ),
        "Quasipolynomial (Period 3, Deg 2)"
    ))

    # 12. Sylvester's sequence A000058
    sylvester = [2, 3, 7, 43, 1807, 3263443, 10650056950807]
    suite.append((
        OEISRecord(
            a_number="A000058",
            id_number=58,
            name="Sylvester's sequence: a(n) = a(n-1)^2 - a(n-1) + 1",
            offset_first_term=0,
            terms=sylvester,
        ),
        "Nonlinear Recurrence (Degree 2)"
    ))

    # 13. Somos-4 A006720
    somos4 = [1, 1, 1, 1, 2, 3, 7, 23, 59, 314, 1529, 8209, 83313, 620297, 7869898]
    suite.append((
        OEISRecord(
            a_number="A006720",
            id_number=6720,
            name="Somos-4 bilinear sequence",
            offset_first_term=0,
            terms=somos4,
        ),
        "Bilinear Recurrence (Somos-4)"
    ))

    # 14. Self-avoiding walks on square lattice A001411 (Unlisted %F in OEIS)
    saw2d = [1, 4, 12, 36, 100, 284, 780, 2172, 5916, 16268, 44100, 120292, 324932, 881500, 2374444, 6416596, 17245332, 46466676, 124658732, 335116620, 897697164, 2409047612, 6443560484, 17245995004, 46046745156, 123067759508, 328320448108, 877396885276]
    suite.append((
        OEISRecord(
            a_number="A001411",
            id_number=1411,
            name="Self-avoiding walks on square lattice (No %F)",
            offset_first_term=0,
            terms=saw2d,
        ),
        "Open Problem / Connective Constant"
    ))

    # 15. Rubik's cube positions at quarter-turn distance A080601 (Unlisted %F in OEIS)
    rubik = [1, 12, 114, 1068, 10011, 93840, 878880, 8221032, 76787682, 715978168, 6660144988, 61777083040, 571131920874, 5258548999884, 48174548074944, 438604751493776]
    suite.append((
        OEISRecord(
            a_number="A080601",
            id_number=80601,
            name="Rubik's cube quarter-turn distance counts (No %F)",
            offset_first_term=0,
            terms=rubik,
        ),
        "Cayley Graph / Branching Factor"
    ))

    return suite


def run_hard_benchmarks():
    suite = generate_hard_benchmark_suite()
    engine = DiscoveryEngine()

    console.print("[bold cyan]========================================================================[/bold cyan]")
    console.print("[bold cyan]OEIS Formula Discovery Lab - Hard Sequences Benchmark Suite[/bold cyan]")
    console.print("[bold cyan]========================================================================[/bold cyan]\n")

    console.print("Running 5 Warmup Iterations (Discarded)...")
    for _ in range(5):
        for rec, _ in suite[:2]:
            engine.analyze_sequence(rec)

    console.print("Executing High-Resolution In-Process Discovery Measurements...\n")

    table = Table(title="Hard Sequences Benchmark Results (Holonomic, Quasipolynomial & Open Sequences)")
    table.add_column("A-Number", style="cyan")
    table.add_column("Sequence Family", style="white", max_width=25)
    table.add_column("Mathematical Class", style="blue")
    table.add_column("Discovered Representation", style="bold green", max_width=42)
    table.add_column("Method", style="magenta")
    table.add_column("Verification", style="bold")
    table.add_column("Time (ms)", style="yellow")

    total_time = 0.0
    exact_count = 0
    heuristic_count = 0

    for rec, math_class in suite:
        t0 = time.perf_counter()
        candidates = engine.analyze_sequence(rec)
        t_elapsed = (time.perf_counter() - t0) * 1000.0
        total_time += t_elapsed

        best = candidates[0] if candidates else None

        if best and best.verification_status == VerificationStatus.EXACT_MATCH:
            exact_count += 1
            v_status = f"[green]exact_match ({best.terms_tested} terms)[/green]"
            repr_str = best.formula_str
            method_str = best.method
        elif best and best.verification_status == VerificationStatus.HEURISTIC:
            heuristic_count += 1
            v_status = f"[yellow]heuristic ({best.terms_tested} terms)[/yellow]"
            repr_str = best.formula_str
            method_str = best.method
        elif best:
            repr_str = best.formula_str
            method_str = best.method
            v_status = f"[white]{best.verification_status.value}[/white]"
        else:
            repr_str = "None"
            method_str = "none"
            v_status = "[red]no_candidate_found[/red]"

        table.add_row(
            rec.a_number,
            rec.name[:25],
            math_class,
            repr_str[:42],
            method_str,
            v_status,
            f"{t_elapsed:.2f}"
        )

    console.print(table)
    console.print(f"\n[bold]Total Tested:[/bold] {len(suite)}")
    console.print(f"[bold]Exact Mathematical Recoveries:[/bold] {exact_count}/{len(suite)} ([bold green]{exact_count/len(suite)*100:.1f}%[/bold green])")
    console.print(f"[bold]Heuristic Asymptotic Models:[/bold] {heuristic_count}/{len(suite)}")
    console.print(f"[bold]Average Computation Time Per Target:[/bold] {total_time / len(suite):.2f} ms")


if __name__ == "__main__":
    run_hard_benchmarks()
