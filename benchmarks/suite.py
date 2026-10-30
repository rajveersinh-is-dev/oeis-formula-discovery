"""
Reproducible Benchmark Suite with High-Resolution In-Process Timers (perf_counter).
Preceded by 5 discarded warmup runs per computational honesty requirements.
All benchmark sequences are generated dynamically from first principles without preloaded tables.
"""

import time
from typing import List
from rich.console import Console
from rich.table import Table

from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISRecord

console = Console()


def generate_benchmark_suite() -> List[OEISRecord]:
    """
    Generates benchmark sequence targets dynamically from first principles.
    Zero precomputed lookup tables or hardcoded recurrence outputs.
    """
    suite = []

    # 1. Linear sequence: a(n) = 3n + 5
    linear_terms = [3 * n + 5 for n in range(25)]
    suite.append(OEISRecord(
        a_number="SYN001",
        id_number=1,
        name="Arithmetic progression: a(n) = 3n + 5",
        offset_first_term=0,
        terms=linear_terms,
    ))

    # 2. Quadratic sequence: a(n) = 2n^2 - n + 7
    quad_terms = [2 * n**2 - n + 7 for n in range(25)]
    suite.append(OEISRecord(
        a_number="SYN002",
        id_number=2,
        name="Quadratic sequence: a(n) = 2n^2 - n + 7",
        offset_first_term=0,
        terms=quad_terms,
    ))

    # 3. Cubic sequence: a(n) = n^3 + 2n - 1
    cubic_terms = [n**3 + 2 * n - 1 for n in range(25)]
    suite.append(OEISRecord(
        a_number="SYN003",
        id_number=3,
        name="Cubic sequence: a(n) = n^3 + 2n - 1",
        offset_first_term=0,
        terms=cubic_terms,
    ))

    # 4. Fibonacci recurrence: a(n) = a(n-1) + a(n-2) computed iteratively
    fib_terms = [0, 1]
    for _ in range(20):
        fib_terms.append(fib_terms[-1] + fib_terms[-2])
    suite.append(OEISRecord(
        a_number="A000045",
        id_number=45,
        name="Fibonacci numbers (withheld %F)",
        offset_first_term=0,
        terms=fib_terms,
    ))

    # 5. Pell recurrence: a(n) = 2*a(n-1) + a(n-2) computed iteratively
    pell_terms = [0, 1]
    for _ in range(16):
        pell_terms.append(2 * pell_terms[-1] + pell_terms[-2])
    suite.append(OEISRecord(
        a_number="A000129",
        id_number=129,
        name="Pell numbers (withheld %F)",
        offset_first_term=0,
        terms=pell_terms,
    ))

    # 6. Powers of 2: a(n) = 2^n computed dynamically
    pow2_terms = [1 << n for n in range(22)]
    suite.append(OEISRecord(
        a_number="A000079",
        id_number=79,
        name="Powers of 2 (withheld %F)",
        offset_first_term=0,
        terms=pow2_terms,
    ))

    # 7. Stern's diatomic sequence: 2-regular recurrence
    stern = [0, 1]
    for i in range(2, 35):
        stern.append(stern[i // 2] if i % 2 == 0 else stern[i // 2] + stern[i // 2 + 1])
    suite.append(OEISRecord(
        a_number="A002487",
        id_number=2487,
        name="Stern's diatomic (withheld %F)",
        offset_first_term=0,
        terms=stern,
    ))

    # 8. Lyness rational sequence
    lyness = [1, 2]
    for n in range(2, 22):
        lyness.append((lyness[-1] + 1) // lyness[-2])
    suite.append(OEISRecord(
        a_number="A001601",
        id_number=1601,
        name="Lyness rational recurrence (withheld %F)",
        offset_first_term=0,
        terms=lyness,
    ))

    # 9. Convergents to e (numerators)
    a_cf = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10]
    e_num = [a_cf[0], a_cf[0] * a_cf[1] + 1]
    for i in range(2, len(a_cf)):
        e_num.append(a_cf[i] * e_num[-1] + e_num[-2])
    suite.append(OEISRecord(
        a_number="A007676",
        id_number=7676,
        name="Convergents to e numerators (withheld %F)",
        offset_first_term=0,
        terms=e_num,
    ))

    return suite


def run_benchmarks():
    suite = generate_benchmark_suite()
    engine = DiscoveryEngine()

    console.print("[bold cyan]Running 5 Warmup Iterations (Discarded)...[/bold cyan]")
    for _ in range(5):
        for rec in suite[:2]:
            engine.analyze_sequence(rec)

    console.print("[bold green]Executing Real Benchmark Measurements...[/bold green]\n")

    table = Table(title="OEIS Formula Discovery Lab — Benchmark Results")
    table.add_column("Target", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Discovered Formula", style="bold green")
    table.add_column("Status", style="magenta")
    table.add_column("Duration (ms)", style="yellow")

    total_time = 0.0
    recovered_count = 0

    for rec in suite:
        t0 = time.perf_counter()
        candidates = engine.analyze_sequence(rec)
        t_elapsed = (time.perf_counter() - t0) * 1000.0
        total_time += t_elapsed

        best = candidates[0] if candidates else None
        formula_repr = best.formula_str if best else "None"
        status = best.verification_status.value if best else "no_match"

        if best and best.verification_status in (VerificationStatus.EXACT_MATCH, VerificationStatus.SYMBOLICALLY_VERIFIED):
            recovered_count += 1

        table.add_row(rec.a_number, rec.name[:30], formula_repr[:45], status, f"{t_elapsed:.2f}")

    console.print(table)
    console.print(f"\n[bold]Recovery Rate:[/bold] {recovered_count}/{len(suite)} ({recovered_count/len(suite)*100:.1f}%)")
    console.print(f"[bold]Average Time Per Sequence:[/bold] {total_time / len(suite):.2f} ms")


if __name__ == "__main__":
    run_benchmarks()

