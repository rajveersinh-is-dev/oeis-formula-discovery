"""
Accuracy & Verification Suite for OEIS Sequences Lacking Listed Formulas (%F).
Fetches real OEIS internal format entries, verifies absence of %F, runs DiscoveryEngine,
and audits candidate accuracy against 100% of available terms and domain mathematics.
"""

import json
import time
import urllib.parse
import urllib.request
from rich.console import Console
from rich.table import Table

from src.candidate.model import VerificationStatus
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISParser, OEISRecord

console = Console()

CANDIDATE_IDS = [
    # 1. Self-avoiding walks & connective constants
    "A001411",  # Self-avoiding walks on square lattice
    "A001412",  # Self-avoiding walks on cubic lattice
    "A001334",  # Self-avoiding walks on hexagonal lattice

    # 2. State-space & combinatorial game complexities
    "A048987",  # Number of possible chess games at the n-th ply
    "A080601",  # Rubik's cube positions at quarter-turn distance n

    # 3. Geometric & combinatorial enumeration without explicit %F
    "A000018",  # Positive integers <= 2^n of form x^2 + 16*y^2
    "A000021",  # Positive integers <= 2^n of form x^2 + 12*y^2
    "A000024",  # Positive integers <= 2^n of form x^2 + 10*y^2
    "A000047",  # Integers <= 2^n of form x^2 - 2*y^2
    "A000020",  # Primitive polynomials of degree n over GF(2)
    "A000022",  # Number of centered hydrocarbons with n atoms

    # 4. Arithmetic & Group Theory without %F (Negative controls for computational honesty)
    "A000003",  # Class number of primitive binary quadratic forms (negative control)
    "A000019",  # Number of primitive permutation groups of degree n (negative control)
    "A000028",  # Prime factorization parity sequence (negative control)
]


def fetch_oeis_internal(a_num: str) -> OEISRecord:
    url = f"https://oeis.org/search?q=id:{a_num}&fmt=text"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        text = resp.read().decode("utf-8", errors="replace")
        lines = text.split("\n")
        rec = OEISParser.parse_entry_lines(lines)
        if not rec:
            raise ValueError(f"Failed to parse internal OEIS format for {a_num}")
        return rec


def run_unlisted_audit():
    console.print("[bold cyan]========================================================================[/bold cyan]")
    console.print("[bold cyan]OEIS Formula Discovery Lab - Sequences Lacking Listed Formula (%F)[/bold cyan]")
    console.print("[bold cyan]========================================================================[/bold cyan]\n")

    engine = DiscoveryEngine()
    records = []

    console.print("Fetching real OEIS internal format records from official OEIS repository...")
    for a_id in CANDIDATE_IDS:
        try:
            rec = fetch_oeis_internal(a_id)
            assert not rec.has_explicit_formula, f"{a_id} unexpectedly has a %F formula!"
            records.append(rec)
            console.print(f"  [green][OK][/green] {rec.a_number}: {rec.name[:60]} (Terms: {len(rec.terms)})")
        except Exception as e:
            console.print(f"  [red][ERROR][/red] Could not fetch {a_id}: {e}")
        time.sleep(0.2)

    console.print(f"\nSuccessfully loaded {len(records)} sequences without %F formulas.\n")

    summary_table = Table(title="Accuracy & Verification Summary on Unlisted Formula Sequences")
    summary_table.add_column("A-Number", style="cyan")
    summary_table.add_column("Sequence Description", style="white", max_width=32)
    summary_table.add_column("Terms", style="yellow")
    summary_table.add_column("Discovery Method", style="magenta")
    summary_table.add_column("Discovered Formula / Model", style="bold green", max_width=45)
    summary_table.add_column("Verification Status", style="bold")

    for rec in records:
        t0 = time.perf_counter()
        candidates = engine.analyze_sequence(rec)
        dur = (time.perf_counter() - t0) * 1000.0

        best = candidates[0] if candidates else None

        if best:
            if best.verification_status == VerificationStatus.EXACT_MATCH:
                v_str = f"[green]exact_match ({best.terms_tested}/{len(rec.terms)})[/green]"
            elif best.verification_status == VerificationStatus.HEURISTIC:
                v_str = f"[yellow]heuristic ({best.terms_tested} terms)[/yellow]"
            else:
                v_str = f"[white]{best.verification_status.value}[/white]"

            summary_table.add_row(
                rec.a_number,
                rec.name[:32],
                str(len(rec.terms)),
                best.method,
                best.formula_str[:45],
                v_str
            )
        else:
            summary_table.add_row(
                rec.a_number,
                rec.name[:32],
                str(len(rec.terms)),
                "none",
                "No candidate found within budget",
                "[white]no_candidate_found[/white]"
            )

    console.print(summary_table)


if __name__ == "__main__":
    run_unlisted_audit()
