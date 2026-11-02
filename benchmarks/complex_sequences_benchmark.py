"""
Complex & Difficult Sequences Benchmark Suite.
Audits the discovery engine against a curated battery of mathematically formidable,
computationally challenging sequences:
1. Calabi-Yau threefolds & Apéry-like holonomic recurrences (Domb numbers, Franel numbers, Zagier A, Franel 4th powers).
2. Advanced infinite product / Euler transform partitions (MacMahon plane partitions, Rogers-Ramanujan, overpartitions).
3. Higher-order nonlinear bilinear cluster recurrences (Somos-6, Somos-7).
4. High-degree algebraic curves (Cubic Ternary trees, Quartic 4-ary trees).
5. Transcendental continued fraction convergents (Euler's number e numerators and denominators).
"""

import time
from typing import List, Tuple
from rich.console import Console
from rich.table import Table

from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISParser, OEISRecord
from benchmarks.high_importance_benchmark import fetch_oeis_record

console = Console()

COMPLEX_TARGETS: List[Tuple[str, str, str]] = [
    # Holonomic / Calabi-Yau / Apéry-like
    ("A002895", "Domb numbers", "4D Random Walks / Spin Systems (Order 2, Deg 3)"),
    ("A000172", "Franel numbers", "Sum of Cubes of Binomials (Order 2, Deg 2)"),
    ("A005260", "Franel 4th powers", "Sum of 4th Powers of Binomials (Order 2, Deg 3)"),
    ("A002893", "Zagier Apéry-like A", "Calabi-Yau Differential System (Order 2, Deg 2)"),
    ("A005259", "Apéry numbers for zeta(3)", "Irrationality Proof of zeta(3) (Order 2, Deg 3)"),
    
    # Modular Products / Euler Transforms
    ("A000219", "MacMahon plane partitions", "3D Young Tableaux G(x)=prod 1/(1-x^k)^k"),
    ("A003106", "Second Rogers-Ramanujan", "Modular Product mod 5: k in {2, 3} mod 5"),
    ("A015128", "Overpartitions", "Modular Product prod (1+x^k)/(1-x^k)"),
    ("A000594", "Ramanujan tau function", "Weight 12 Cusp Form G(x)=x*prod(1-x^k)^24"),

    # Bilinear Somos Cluster Sequences
    ("A006722", "Somos-6 sequence", "Bilinear Cluster Algebra (Order 6)"),
    ("A006723", "Somos-7 sequence", "Bilinear Cluster Algebra (Order 7)"),

    # High-Degree Algebraic Curves
    ("A001764", "Ternary trees", "Cubic Algebraic Curve: x*G^3 - G + 1 = 0"),
    ("A002293", "4-ary trees", "Quartic Algebraic Curve: x*G^4 - G + 1 = 0"),

    # Continued Fractions
    ("A007676", "Convergents to e (num)", "Continued Fraction [2; 1, 2k, 1]"),
    ("A007677", "Convergents to e (den)", "Continued Fraction Denominators"),
]


def run_complex_sequences_benchmark():
    """Runs discovery benchmark against highly complex and difficult mathematical sequences."""
    console.print("[bold cyan]========================================================================[/bold cyan]")
    console.print("[bold cyan]OEIS Formula Discovery Lab - Extreme Complexity Benchmark Suite[/bold cyan]")
    console.print("[bold cyan]========================================================================[/bold cyan]\n")

    engine = DiscoveryEngine()

    records: List[Tuple[OEISRecord, str, str]] = []
    for a_num, name, domain in COMPLEX_TARGETS:
        try:
            rec = fetch_oeis_record(a_num)
            records.append((rec, name, domain))
        except Exception as e:
            console.print(f"[red]Error fetching {a_num}: {e}[/red]")

    console.print(f"Loaded {len(records)} verified complex target sequences from OEIS.\n")

    # 5 Warmup runs
    console.print("Running 5 Warmup Iterations (Discarded)...")
    if records:
        for _ in range(5):
            _ = engine.analyze_sequence(records[0][0])

    console.print("Executing High-Resolution In-Process Discovery Measurements...\n")

    table = Table(title="Discovery Results on Highly Complex Mathematical Sequences")
    table.add_column("A-Number", style="cyan")
    table.add_column("Sequence Family", style="white", max_width=24)
    table.add_column("Mathematical Domain", style="blue", max_width=28)
    table.add_column("Terms", style="white")
    table.add_column("Discovered Mathematical Formula", style="bold green", max_width=40)
    table.add_column("Method", style="magenta")
    table.add_column("Time (ms)", style="yellow")

    exact_count = 0
    total_time = 0.0

    for rec, name, domain in records:
        t0 = time.perf_counter()
        cands = engine.analyze_sequence(rec)
        t_elapsed = (time.perf_counter() - t0) * 1000.0
        total_time += t_elapsed

        exact_cands = [c for c in cands if c.verification_status == VerificationStatus.EXACT_MATCH]
        if exact_cands:
            exact_count += 1
            best = exact_cands[0]
            formula_display = best.formula_str
            method_display = best.method
        elif cands:
            best = cands[0]
            formula_display = f"[{best.verification_status.value}] {best.formula_str}"
            method_display = best.method
        else:
            formula_display = "No exact candidate found"
            method_display = "none"

        table.add_row(
            rec.a_number,
            name,
            domain,
            str(len(rec.terms)),
            formula_display,
            method_display,
            f"{t_elapsed:.2f}",
        )

    console.print(table)
    console.print(f"\n[bold]Total Sequences Tested:[/] {len(records)}")
    console.print(f"[bold]Exact Mathematical Recoveries:[/] [bold green]{exact_count}/{len(records)} ({exact_count/len(records)*100:.1f}%)[/bold green]")
    avg_time = total_time / len(records) if records else 0.0
    console.print(f"[bold]Average Discovery Runtime:[/] [bold yellow]{avg_time:.2f} ms[/bold yellow]\n")


if __name__ == "__main__":
    run_complex_sequences_benchmark()
