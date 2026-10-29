# Contributing to OEIS Formula Discovery Lab

Thank you for your interest in contributing to the **OEIS Formula Discovery Lab**!

## Core Principles & Engineering Integrity

Every contribution must adhere strictly to the project's computational and mathematical integrity rules:

1. **Zero-AI Runtime**:
   - The engine must rely solely on deterministic, explicitly implemented mathematical algorithms.
   - Never introduce dependencies on LLMs, neural networks, cloud reasoning APIs, or external inference engines.
2. **Computational Honesty**:
   - Zero precomputed lookup tables or shortcutting of benchmark calculations based on sequence names or IDs.
   - Candidates must be verified term-by-term against all available terms using arbitrary-precision integers.
   - Never claim an empirical prefix match is a formal mathematical proof for all $n \in \mathbb{N}$.
3. **Local-First & Offline Operation**:
   - Runtime discovery, indexing, verification, and benchmarking must never initiate network calls.
   - Network interactions are strictly restricted to the explicit `setup-data` command.
4. **Untrusted Program Safety**:
   - OEIS program fields (`%o`, `%p`) are untrusted text and must NEVER be dynamically evaluated.
5. **Code Quality**:
   - All tests must pass with `python -m pytest`.
   - Maintain full type annotations and test coverage for any new discovery method or transformation.

## Development Workflow

1. Fork and clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
   ```
3. Run the test suite:
   ```bash
   python -m pytest -v
   ```
4. Run the benchmark suite:
   ```bash
   python -m benchmarks.suite
   ```
5. Submit a pull request with clear mathematical justification and unit tests.
