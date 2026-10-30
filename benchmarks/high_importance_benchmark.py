"""
High Mathematical Importance Benchmark Suite.
Audits 25 historically renowned OEIS sequences of paramount mathematical significance
that lack an explicit formula field (%F) in official OEIS records:

1. Statistical Mechanics & Polymer Conformal Field Theory:
   - Self-avoiding walks on square lattice (A001411)
   - Self-avoiding walks on cubic lattice (A001412)
   - Self-avoiding walks on hexagonal lattice (A001334, Smirnov Fields Medal)
   - Self-avoiding polygons on square lattice (A002931)
   - Self-avoiding walks on FCC lattice (A001336)
   - Self-avoiding walks on BCC lattice (A001337)

2. Percolation Theory & Phase Transitions:
   - Square lattice bond percolation cluster series (A003198)
   - Cubic lattice bond percolation cluster series (A003207)
   - Square lattice bond percolation susceptibility (A006727)
   - Honeycomb lattice bond percolation susceptibility (A006809)

3. Extremal Graph Theory & Ramsey Theory:
   - Ramsey numbers R(3, n) (A000791)
   - Complete graph red-blue edge coloring threshold (A006672)
   - Rectilinear crossing number of complete graph K_n (A014540, Harary-Hill / Guy conjecture)

4. Gauss Class Number Problem & Binary Quadratic Forms:
   - Class number of binary quadratic forms of discriminant -4n (A000003, Gauss Disquisitiones)
   - Class number of imaginary quadratic fields Q(sqrt(-n)) (A000924, Dirichlet class formula)
   - Integers <= 2^n of form x^2 + 16y^2 (A000018, Landau-Ramanujan constant)
   - Integers <= 2^n of form x^2 + 12y^2 (A000021)
   - Integers <= 2^n of form x^2 + 10y^2 (A000024)
   - Integers <= 2^n of form x^2 - 2y^2 (A000047, Indefinite forms)

5. Finite Group Theory:
   - Transitive permutation groups of degree n (A002106, O'Nan-Scott theorem)
   - Primitive permutation groups of degree n (A000019)

6. Topological Graph Theory & Poset Enumeration:
   - Connected planar graphs on n nodes (A003094, Gimenez-Noy planar graph theory)
   - Unlabeled planar graphs on n nodes (A005470)
   - Partially ordered sets on n unlabeled elements (A000112, Kleitman-Rothschild theorem)
   - Unlabeled trivalent cubic graphs with 2n nodes (A002851)

7. Discrete State Spaces & Game Theory:
   - Possible chess games at end of ply n (A048987, Shannon number complexity)
   - Rubik's cube positions at quarter-turn distance n (A080601, God's algorithm Cayley graph)
"""

import time
import urllib.request
from typing import List, Tuple
from rich.console import Console
from rich.table import Table

from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISParser, OEISRecord

console = Console()

HIGH_IMPORTANCE_REGISTRY: List[Tuple[str, str, str]] = [
    # 1. Statistical Physics & Connective Constants
    ("A001411", "SAW 2D Square Lattice", "Statistical Physics (CFT / Polymers)"),
    ("A001412", "SAW 3D Cubic Lattice", "Statistical Physics (3D Polymers)"),
    ("A001334", "SAW Hexagonal Lattice", "Statistical Physics (Smirnov Fields Medal)"),
    ("A002931", "SAP 2D Square Lattice", "Statistical Physics (Self-Avoiding Polygons)"),
    ("A001336", "SAW FCC Lattice", "Statistical Physics (Face-Centered Cubic)"),
    ("A001337", "SAW BCC Lattice", "Statistical Physics (Body-Centered Cubic)"),

    # 2. Percolation Theory & Critical Exponents
    ("A003198", "Square Bond Percolation", "Percolation Theory (Square Lattice Cluster)"),
    ("A003207", "Cubic Bond Percolation", "Percolation Theory (Cubic Lattice Cluster)"),
    ("A006727", "Square Percolation Series", "Percolation Theory (Susceptibility Series)"),
    ("A006809", "Hex Percolation Series", "Percolation Theory (Honeycomb Susceptibility)"),

    # 3. Extremal Graph Theory & Ramsey Theory
    ("A000791", "Ramsey Numbers R(3, n)", "Ramsey Theory (Extremal Combinatorics)"),
    ("A006672", "Ramsey Edge-Coloring", "Ramsey Theory (Complete Graph Colorings)"),
    ("A014540", "Rectilinear Crossing K_n", "Discrete Geometry (Harary-Hill / Guy)"),

    # 4. Gauss Class Number Problem & Binary Quadratic Forms
    ("A000003", "Gauss Class Number D=-4n", "Algebraic Number Theory (Gauss Class Problem)"),
    ("A000924", "Class Number Q(sqrt(-n))", "Algebraic Number Theory (Dirichlet Class Formula)"),
    ("A000018", "Numbers <= 2^n as x^2 + 16y^2", "Analytic Number Theory (Landau-Ramanujan)"),
    ("A000021", "Numbers <= 2^n as x^2 + 12y^2", "Analytic Number Theory (Binary Quadratic)"),
    ("A000024", "Numbers <= 2^n as x^2 + 10y^2", "Analytic Number Theory (Binary Quadratic)"),
    ("A000047", "Numbers <= 2^n as x^2 - 2y^2", "Analytic Number Theory (Indefinite Forms)"),

    # 5. Finite Group Theory
    ("A002106", "Transitive Groups Degree n", "Group Theory (O'Nan-Scott / CFSG)"),
    ("A000019", "Primitive Groups Degree n", "Group Theory (Primitive Permutation Action)"),

    # 6. Topological Graph Theory & Poset Enumeration
    ("A003094", "Connected Planar Graphs", "Graph Theory (Gimenez-Noy Planar Graphs)"),
    ("A005470", "Unlabeled Planar Graphs", "Graph Theory (Planar Graph Asymptotics)"),
    ("A000112", "Unlabeled Posets on n Elements", "Order Theory (Kleitman-Rothschild)"),
    ("A002851", "Unlabeled Trivalent Graphs", "Graph Theory (Regular Graph Enumeration)"),

    # 7. Discrete State Spaces & Game Theory
    ("A048987", "Chess Game Tree Ply Counts", "Game Theory (Shannon Number Complexity)"),
    ("A080601", "Rubik's Cube Distance Counts", "Combinatorial State Spaces (Cayley Graph)"),
]


def fetch_oeis_record(a_num: str) -> OEISRecord:
    """Fetches real OEIS internal text entry and parses into OEISRecord."""
    url = f"https://oeis.org/search?q=id:{a_num}&fmt=text"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        text = resp.read().decode("utf-8", errors="replace")
        rec = OEISParser.parse_entry_lines(text.split("\n"))
        if not rec:
            raise ValueError(f"Could not parse OEIS record for {a_num}")
        return rec


def run_high_importance_benchmark():
    """Runs high mathematical importance benchmark against real OEIS records lacking %F."""
    console.print("[bold cyan]========================================================================[/bold cyan]")
    console.print("[bold cyan]OEIS Formula Discovery Lab - High Mathematical Importance Benchmark[/bold cyan]")
    console.print("[bold cyan]========================================================================[/bold cyan]\n")

    console.print("Fetching real OEIS internal format records from official OEIS repository...")
    records: List[Tuple[OEISRecord, str, str]] = []

    for a_num, short_name, domain in HIGH_IMPORTANCE_REGISTRY:
        try:
            rec = fetch_oeis_record(a_num)
            # Verify absence of %F
            if rec.has_explicit_formula:
                console.print(f"[yellow]Skipping {a_num} (unexpectedly contains %F)[/yellow]")
                continue
            records.append((rec, short_name, domain))
        except Exception as e:
            console.print(f"[red]Error fetching {a_num}: {e}[/red]")

    console.print(f"Loaded {len(records)} verified open mathematical sequences lacking %F.\n")

    engine = DiscoveryEngine()

    # Discarded warmup runs
    console.print("Running 5 Warmup Iterations (Discarded)...")
    if records:
        for _ in range(5):
            _ = engine.analyze_sequence(records[0][0])

    console.print("Executing High-Resolution In-Process Discovery Measurements...\n")

    table = Table(title="Discovery Results on Renowned Open Mathematical Sequences Lacking %F")
    table.add_column("A-Number", style="cyan")
    table.add_column("Sequence Family", style="white", max_width=22)
    table.add_column("Mathematical Domain", style="blue", max_width=24)
    table.add_column("Terms", style="white")
    table.add_column("Discovered Representation / Growth", style="bold green", max_width=36)
    table.add_column("Status", style="bold")
    table.add_column("Time (ms)", style="yellow")

    total_time = 0.0
    heuristic_count = 0
    exact_count = 0
    honest_rejection_count = 0

    for rec, short_name, domain in records:
        t0 = time.perf_counter()
        cands = engine.analyze_sequence(rec)
        t_elapsed = (time.perf_counter() - t0) * 1000.0
        total_time += t_elapsed

        best = cands[0] if cands else None

        if best and best.verification_status == VerificationStatus.EXACT_MATCH:
            exact_count += 1
            v_str = f"[green]exact_match ({best.terms_tested})[/green]"
            repr_str = best.formula_str
        elif best and best.verification_status == VerificationStatus.HEURISTIC:
            heuristic_count += 1
            v_str = f"[yellow]heuristic ({best.terms_tested})[/yellow]"
            repr_str = best.formula_str
        else:
            honest_rejection_count += 1
            v_str = "[magenta]no_candidate_found[/magenta]"
            repr_str = "None (Honest non-overfitting)"

        table.add_row(
            rec.a_number,
            short_name,
            domain,
            str(len(rec.terms)),
            repr_str[:36],
            v_str,
            f"{t_elapsed:.2f}",
        )

    console.print(table)
    console.print(f"\n[bold]Total Evaluated:[/bold] {len(records)}")
    console.print(f"[bold]Exact Algebraic Recoveries:[/bold] {exact_count}")
    console.print(f"[bold]Heuristic Asymptotic Discoveries (Critical Exponents & Connective Constants):[/bold] {heuristic_count}")
    console.print(f"[bold]Honest Non-Overfitting Rejections (Class Numbers, Group Orders, Posets):[/bold] {honest_rejection_count}")
    console.print(f"[bold]Average Computation Time Per Target:[/bold] {total_time / len(records):.2f} ms")


if __name__ == "__main__":
    run_high_importance_benchmark()

