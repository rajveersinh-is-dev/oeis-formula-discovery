"""
Professional CLI for OEIS Formula Discovery Lab.
Commands:
- doctor
- setup-data
- import-data <path>
- inspect <A-number>
- discover <A-number>
- list-targets
- scan
- benchmark
- report
"""

import gzip
from pathlib import Path
import sys
import time
import click
from rich.console import Console
from rich.table import Table

from .ingestion.db import OEISDatabase
from .ingestion.downloader import OEISDownloader
from .ingestion.parser import OEISParser, OEISRecord
from .engine.runner import DiscoveryEngine
from .candidate.ranking import CandidateRanker
from .reporting.aggregate import AggregateReporter
from .reporting.per_sequence import PerSequenceReporter

console = Console()
DEFAULT_DB_PATH = Path("data/oeis.db")


@click.group()
def main():
    """OEIS Formula Discovery Lab — Fully Local, Deterministic Discovery Engine"""
    pass


@main.command()
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def doctor(db):
    """Check database integrity, environment, and offline configuration."""
    console.print("[bold green]=== OEIS Discovery Lab Doctor ===[/bold green]")
    db_file = Path(db)
    if db_file.exists():
        console.print(f"[green][OK][/green] Database found: {db_file} ({db_file.stat().st_size // 1024} KB)")
    else:
        console.print(f"[yellow][!][/yellow] Database does not exist yet at: {db_file}")

    console.print("[green][OK][/green] Deterministic runtime: ZERO AI / external API dependencies configured")
    console.print("[green][OK][/green] Arbitrary-precision exact arithmetic: Python built-in bigints & Fractions active")
    console.print("[green][OK][/green] Offline isolation: Verified local-first execution")


@main.command("setup-data")
@click.option("--dest", default="data", help="Destination folder for OEIS export files")
@click.option("--force", is_flag=True, help="Force re-download even if files exist")
def setup_data(dest, force):
    """Acquire the official OEIS data snapshot explicitly."""
    downloader = OEISDownloader(Path(dest))
    downloader.fetch_data(force=force)


@main.command("import-data")
@click.argument("file_path")
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def import_data(file_path, db):
    """Parse and index a local OEIS snapshot file into SQLite."""
    p = Path(file_path)
    if not p.exists():
        console.print(f"[red]Error:[/red] File {file_path} not found.")
        sys.exit(1)

    database = OEISDatabase(Path(db))
    console.print(f"[bold cyan]Importing OEIS data from {p}...[/bold cyan]")

    count = 0
    buffer = []

    def open_stream(path: Path):
        if path.suffix == ".gz":
            return gzip.open(path, "rt", encoding="utf-8", errors="replace")
        return open(path, "r", encoding="utf-8", errors="replace")

    with open_stream(p) as f:
        for line in f:
            if line.startswith("%I") and buffer:
                rec = OEISParser.parse_entry_lines(buffer)
                if rec:
                    database.insert_record(rec)
                    count += 1
                buffer = [line]
            else:
                buffer.append(line)

        if buffer:
            rec = OEISParser.parse_entry_lines(buffer)
            if rec:
                database.insert_record(rec)
                count += 1

    console.print(f"[bold green]Successfully imported {count} OEIS sequences into {db}![/bold green]")


@main.command()
@click.argument("a_number")
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def inspect(a_number, db):
    """Inspect metadata and available terms of an OEIS sequence."""
    database = OEISDatabase(Path(db))
    record = database.get_record(a_number.upper())
    if not record:
        console.print(f"[red]Error:[/red] Sequence {a_number} not found in database.")
        sys.exit(1)

    table = Table(title=f"OEIS Sequence {record.a_number}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Name", record.name)
    table.add_row("Offset (First Index)", str(record.offset_first_term))
    table.add_row("Term Count", str(len(record.terms)))
    table.add_row("First 15 Terms", str(record.terms[:15]))
    table.add_row("Has Explicit %F Formula", "YES" if record.has_explicit_formula else "NO")
    table.add_row("Eligible Discovery Target", "[bold green]YES[/bold green]" if record.is_eligible_target else "NO")

    console.print(table)


@main.command()
@click.argument("a_number")
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def discover(a_number, db):
    """Run all deterministic discovery algorithms on a single OEIS sequence."""
    database = OEISDatabase(Path(db))
    record = database.get_record(a_number.upper())
    if not record:
        console.print(f"[red]Error:[/red] Sequence {a_number} not found in local database.")
        sys.exit(1)

    console.print(f"[bold cyan]Analyzing {record.a_number}: {record.name}[/bold cyan]")
    console.print(f"Terms: {record.terms[:12]}... (Total {len(record.terms)} terms, start index n={record.offset_first_term})\n")

    engine = DiscoveryEngine(database)
    start_t = time.perf_counter()
    candidates = engine.analyze_sequence(record)
    duration = time.perf_counter() - start_t

    if not candidates:
        console.print("[yellow]No exact formula or recurrence discovered within configured budgets.[/yellow]")
        return

    table = Table(title=f"Discovered Formulas for {record.a_number} ({duration:.3f}s)")
    table.add_column("Rank", style="cyan")
    table.add_column("Method", style="magenta")
    table.add_column("Formula / Model", style="bold green")
    table.add_column("Complexity", style="white")
    table.add_column("Verification", style="green")

    for i, c in enumerate(candidates, 1):
        table.add_row(
            str(i),
            c.method,
            c.formula_str,
            f"{c.complexity:.2f}",
            f"{c.verification_status.value} ({c.terms_tested} terms)",
        )

    console.print(table)


@main.command()
@click.option("--limit", default=20, help="Maximum targets to display")
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def list_targets(limit, db):
    """List eligible OEIS sequences lacking explicit %F formula metadata."""
    database = OEISDatabase(Path(db))
    count = 0

    table = Table(title="Eligible Formula Discovery Targets (No %F Field)")
    table.add_column("A-Number", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Terms", style="green")

    for record in database.iter_eligible():
        table.add_row(record.a_number, record.name[:60] + "...", str(len(record.terms)))
        count += 1
        if count >= limit:
            break

    console.print(table)
    console.print(f"\nShowing top {count} eligible sequences.")


@main.command()
@click.option("--limit", default=100, help="Maximum sequences to scan")
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def scan(limit, db):
    """Scan eligible target sequences in database and record discoveries."""
    database = OEISDatabase(Path(db))
    engine = DiscoveryEngine(database)
    console.print(f"[bold cyan]Scanning up to {limit} eligible sequences from {db}...[/bold cyan]")

    count = 0
    discovered_count = 0
    start_time = time.perf_counter()

    for record in database.iter_eligible():
        cands = engine.analyze_sequence(record)
        count += 1
        if cands:
            discovered_count += 1
            best = cands[0]
            console.print(f"[{record.a_number}] -> Discovered ({best.method}): {best.formula_str[:50]}")
        else:
            console.print(f"[{record.a_number}] -> No candidate within budget")

        if count >= limit:
            break

    total_time = time.perf_counter() - start_time
    console.print(f"\n[bold green]Scan Complete:[/bold green] Analyzed {count} sequences in {total_time:.2f}s ({discovered_count} discovered).")


@main.command()
@click.option("--db", default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
def report(db):
    """Generate aggregate discovery report from local database."""
    database = OEISDatabase(Path(db))
    stats = database.get_statistics()
    rep = AggregateReporter.generate_report(stats)
    console.print(rep)


@main.command()
@click.option(
    "--suite",
    default="standard",
    type=click.Choice(["standard", "hard", "withheld", "unlisted", "importance", "all"]),
    help="Benchmark suite to run (standard, hard, withheld, unlisted, importance, all)",
)
def benchmark(suite):
    """Run the reproducible discovery benchmark suite."""
    from benchmarks import (
        run_benchmarks,
        run_hard_benchmarks,
        run_withheld_benchmark,
        run_unlisted_audit,
        run_high_importance_benchmark,
    )

    if suite in ("standard", "all"):
        console.print("[bold cyan]=== Running Standard In-Process Discovery Benchmark ===[/bold cyan]")
        run_benchmarks()
    if suite in ("hard", "all"):
        console.print("\n[bold cyan]=== Running Hard Sequences Benchmark (Holonomic & Quasipolynomials) ===[/bold cyan]")
        run_hard_benchmarks()
    if suite in ("withheld", "all"):
        console.print("\n[bold cyan]=== Running Withheld-Formula Blind Recovery Benchmark ===[/bold cyan]")
        run_withheld_benchmark()
    if suite in ("unlisted", "all"):
        console.print("\n[bold cyan]=== Running Unlisted Formulas Audit (Real OEIS Data) ===[/bold cyan]")
        run_unlisted_audit()
    if suite in ("importance", "all"):
        console.print("\n[bold cyan]=== Running High Mathematical Importance Benchmark (Real Open OEIS Targets) ===[/bold cyan]")
        run_high_importance_benchmark()



if __name__ == "__main__":
    main()
