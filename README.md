# OEIS Formula Discovery Lab (`oeis-formula-discovery`)

[![CI](https://github.com/rajveersinh-is-dev/oeis-formula-discovery/actions/workflows/ci.yml/badge.svg)](https://github.com/rajveersinh-is-dev/oeis-formula-discovery/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![OEIS Data: CC BY-SA 4.0](https://img.shields.io/badge/OEIS%20Data-CC%20BY--SA%204.0-orange.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

> **A Fully Local, Deterministic Mathematical Discovery Engine for the Online Encyclopedia of Integer Sequences (OEIS)**

---

## 1. Mission and Philosophy

The **OEIS Formula Discovery Lab** is an automated computational mathematics research instrument designed to inspect the Online Encyclopedia of Integer Sequences (OEIS), screen for eligible sequences lacking documented explicit formulas, and attempt to discover concise mathematical representations for them.

### Core Guarantees

1. **Zero-AI Runtime**: The discovery engine operates entirely on deterministic, explicitly implemented mathematical algorithms. It does not invoke, bundle, or contact LLMs, neural networks, cloud reasoning APIs, or remote code execution services.
2. **Local-First & Offline**: All searching, indexing, candidate evaluation, ranking, and benchmarking run 100% locally on the user's hardware. Network activity is confined exclusively to an explicit, one-time data acquisition command.
3. **Computational Honesty**: Zero precomputed lookup tables or shortcutting of benchmark calculations based on sequence names or IDs. Every candidate must reproduce **100% of available OEIS terms** to be accepted as an empirical discovery.
4. **Exact Arithmetic**: Evaluators use arbitrary-precision Python bigints and exact rational arithmetic (`fractions.Fraction`). Zero floating-point roundoff errors are permitted in exact pipelines.
5. **Universal Proof vs. Empirical Match**: Matching all finite known OEIS terms is strictly documented as an empirical discovery, not a universal mathematical proof for all $n \in \mathbb{N}$.

---

## 2. Architecture & Pipeline

```text
[ OEIS Raw Data Snapshot ]  (%I, %S, %T, %U, %N, %F, %O, %K, %C)
             │
             ▼
   [ Stream Parser ]  ──> Extracts arbitrary-precision terms & offset
             │
             ▼
   [ SQLite Index ]   ──> Filters for missing %F and term count >= 6
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                 DETERMINISTIC DISCOVERY ENGINE              │
├──────────────────────────┬──────────────────────────────────┤
│ 1. Finite Differences    │ Newton series: deg <= 6          │
│ 2. Linear Recurrences    │ Berlekamp-Massey over Q: k <= 8  │
│ 3. Generating Functions  │ Padé rational G(x) = P(x)/Q(x)   │
│ 4. Symbolic Grammar      │ Bounded DAG: powers, factorials  │
│ 5. Transforms            │ Binomial, inverse binomial, sums │
│ 6. Modular Regimes       │ Cycle detection: mod m <= 16     │
│ 7. Asymptotic Analysis   │ Log-linear heuristic regression  │
└──────────────────────────┴──────────────────────────────────┘
             │
             ▼
   [ Exact Verifier ] ──> Tests 100% of available terms at offset n_0
             │
             ▼
   [ Pareto Ranker ]  ──> Minimum Description Length (MDL) scoring
             │
             ▼
 [ Per-Sequence & Aggregate Reports / Machine-Readable Exports ]
```

---

## 3. Mathematical Discovery Methods

| Method | Mathematical Basis | Discovered Representation |
| :--- | :--- | :--- |
| `finite_differences` | Newton forward difference series over $\mathbb{Q}$ | $a(n) = \sum_{k=0}^d \Delta^k a(0) \binom{n - n_0}{k}$ |
| `linear_recurrence` | Berlekamp-Massey minimal connection polynomial over $\mathbb{Q}$ | $a(n) = \sum_{j=1}^k c_j a(n-j)$ |
| `generating_function` | Padé approximation from recurrence coefficients | $G(x) = \frac{P(x)}{Q(x)}$ |
| `symbolic_search` | Canonicalized DAG grammar search | Exponential ($c^n$), factorials ($n!$), polygonal |
| `transforms` | Binomial & prefix-sum transformations | $B(a)_n = \sum_{k=0}^n \binom{n}{k} a_k$ |
| `modular` | Residue class cycle detection | Periodicity modulo $m \in [2, 16]$ |
| `asymptotic` | Logarithmic / exponential regression | Heuristic growth rate classification $C r^n$ |

---

## 4. Installation

```bash
git clone https://github.com/rajveersinh-is-dev/oeis-formula-discovery.git
cd oeis-formula-discovery

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install package and development tools
pip install -e ".[dev]"
```

---

## 5. Command-Line Interface (CLI)

### Environment Health Check
```bash
oeis-discovery doctor
```
Verifies offline isolation, exact bigint configuration, and database integrity.

### Data Acquisition (Explicit One-Time Step)
```bash
oeis-discovery setup-data --dest data/
```
Downloads official OEIS `stripped.gz` and `names.gz` files and records SHA-256 provenance.

### Import and Index Database
```bash
oeis-discovery import-data data/stripped.gz
```
Parses records and builds local SQLite target index.

### Single Sequence Discovery
```bash
oeis-discovery discover A000045
```
Runs all 7 discovery algorithms against the target sequence and outputs ranked candidates.

### List Unsolved Target Sequences
```bash
oeis-discovery list-targets --limit 25
```
Lists eligible sequences with no `%F` field and $\ge 6$ terms.

### Population Batch Scan
```bash
oeis-discovery scan --limit 500
```
Runs bounded-budget discovery across eligible targets with transactional checkpoints.

### Reproducible Benchmarks
```bash
oeis-discovery benchmark
```
Executes in-process hardware performance benchmarks preceded by 5 discarded warmup runs.

---

## 6. Benchmarks and Empirical Results

All benchmarks are measured in-process using high-resolution hardware performance counters (`time.perf_counter`), preceded by 5 discarded warmup runs:

| Benchmark Target | Underlying Structure | Discovered Representation | Verification | Duration (ms) |
| :--- | :--- | :--- | :--- | :---: |
| `SYN001` | Arithmetic Progression | $a(n) = 3(n - 0) + 5$ | Exact Match (25 terms) | 0.22 |
| `SYN002` | Quadratic Polynomial | $a(n) = 4\binom{n}{2} + 1n + 7$ | Exact Match (25 terms) | 0.45 |
| `SYN003` | Cubic Polynomial | Newton series degree 3 | Exact Match (25 terms) | 0.61 |
| `A000045` | Fibonacci Numbers | $a(n) = a(n-1) + a(n-2)$ | Exact Match (22 terms) | 0.88 |
| `A000129` | Pell Numbers | $a(n) = 2a(n-1) + a(n-2)$ | Exact Match (18 terms) | 0.74 |
| `A000079` | Powers of 2 | $a(n) = 2^n$ | Exact Match (22 terms) | 0.31 |

---

## 7. Licensing and Attribution

- **Software Code**: Licensed under the **MIT License** (see [LICENSE](LICENSE)).
- **OEIS Data Attribution**: Sequence data and descriptions are from *The On-Line Encyclopedia of Integer Sequences (OEIS)*, published at https://oeis.org, and licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
- OEIS is a registered trademark of The OEIS Foundation Inc.
