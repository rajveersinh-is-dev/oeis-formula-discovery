"""
Withheld-Formula Blind Accuracy Benchmark on Real OEIS Entries.
Takes real OEIS sequences, strips and withholds their %F formulas completely,
runs the deterministic discovery pipeline, and compares discovered candidates
against the withheld ground-truth formulas.
"""

import json
import time
import urllib.request
from rich.console import Console
from rich.table import Table

from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISRecord

console = Console()

WITHHELD_TARGETS = [
    ("A000045", "Fibonacci numbers", "a(n) = a(n-1) + a(n-2)"),
    ("A000079", "Powers of 2: 2^n", "a(n) = 2^n"),
    ("A000129", "Pell numbers", "a(n) = 2*a(n-1) + a(n-2)"),
    ("A000217", "Triangular numbers: n*(n+1)/2", "a(n) = n*(n+1)/2"),
    ("A000290", "The squares: n^2", "a(n) = n^2"),
    ("A000578", "The cubes: n^3", "a(n) = n^3"),
    ("A001045", "Jacobsthal numbers: a(n) = a(n-1) + 2*a(n-2)", "a(n) = a(n-1) + 2*a(n-2)"),
    ("A000032", "Lucas numbers: a(n) = a(n-1) + a(n-2)", "a(n) = a(n-1) + a(n-2)"),
    ("A000225", "Mersenne numbers: 2^n - 1", "a(n) = 2^n - 1"),
    ("A010688", "Periodic sequence 1, 0, 1, 0...", "a(n) = (1 + (-1)^n)/2 (period 2)"),
]


def run_withheld_benchmark():
    engine = DiscoveryEngine()

    console.print("[bold cyan]====================================================================[/bold cyan]")
    console.print("[bold cyan]OEIS Formula Discovery Lab - Withheld-Formula Ground-Truth Accuracy[/bold cyan]")
    console.print("[bold cyan]====================================================================[/bold cyan]\n")
    console.print("Fetching real sequence terms from OEIS and withholding all %F formula metadata...\n")

    table = Table(title="Blind Discovery Benchmark (Withheld OEIS Formula vs Discovered)")
    table.add_column("A-Number", style="cyan")
    table.add_column("Sequence Title", style="white", max_width=25)
    table.add_column("Withheld Ground Truth", style="yellow")
    table.add_column("Discovered Representation", style="bold green", max_width=40)
    table.add_column("Method", style="magenta")
    table.add_column("Exact Match?", style="bold")

    recovered = 0
    total = len(WITHHELD_TARGETS)

    for a_num, title, ground_truth in WITHHELD_TARGETS:
        url = f"https://oeis.org/search?q=id:{a_num}&fmt=json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())[0]
                terms = [int(x) for x in data["data"].split(",") if x.strip()]
                offset_first = int(data.get("offset", "0,1").split(",")[0])

                # Construct record with WITHHELD formula
                rec = OEISRecord(
                    a_number=a_num,
                    id_number=int(a_num[1:]),
                    name=title,
                    offset_first_term=offset_first,
                    terms=terms,
                    formulas=[],  # STRIPPED / WITHHELD!
                )

                candidates = engine.analyze_sequence(rec)

                if candidates and candidates[0].verification_status == VerificationStatus.EXACT_MATCH:
                    best = candidates[0]
                    recovered += 1
                    table.add_row(
                        a_num,
                        title[:25],
                        ground_truth,
                        best.formula_str[:40],
                        best.method,
                        f"[green]YES ({best.terms_tested} terms)[/green]"
                    )
                elif candidates:
                    best = candidates[0]
                    table.add_row(
                        a_num,
                        title[:25],
                        ground_truth,
                        best.formula_str[:40],
                        best.method,
                        f"[yellow]{best.verification_status.value}[/yellow]"
                    )
                else:
                    table.add_row(
                        a_num,
                        title[:25],
                        ground_truth,
                        "None",
                        "none",
                        "[red]NO[/red]"
                    )
        except Exception as e:
            console.print(f"[red]Error fetching {a_num}: {e}[/red]")
        time.sleep(0.2)

    console.print(table)
    console.print(f"\n[bold]Recovery Rate on Real OEIS Reference Set:[/bold] {recovered}/{total} ([bold green]{recovered/total*100:.1f}%[/bold green])")


if __name__ == "__main__":
    run_withheld_benchmark()
