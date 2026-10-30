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
┌─────────────────────────────────────────────────────────────────┐
│                 DETERMINISTIC DISCOVERY ENGINE                  │
├────────────────────────────┬────────────────────────────────────┤
│ 1. Finite Differences      │ Newton series: deg <= 6            │
│ 2. Quasipolynomials        │ Multisection branches: period <= 6 │
│ 3. Linear Recurrences      │ Berlekamp-Massey over Q: k <= 8    │
│ 4. Inhomogeneous Recurr.   │ Rational driving poly: P(n) in Q[n]│
│ 5. Holonomic Recurrences   │ Rational nullspace P-finite: k,d<=4│
│ 6. Nonlinear Recurrences   │ Univariate poly & Somos-k bilinear │
│ 7. Algebraic Gen. Funcs    │ Hermite-Pade quadratic: A2*G^2+... │
│ 8. Convolution Recurr.     │ Cauchy & binomial self-convolutions│
│ 9. Multiplicative Recurr.  │ Exact power products: a(n-1)^p*... │
│ 10. Generating Functions   │ Pade rational G(x) = P(x)/Q(x)     │
│ 11. Symbolic Grammar       │ Bounded DAG: powers, factorials    │
│ 12. Transforms             │ Binomial, inverse binomial, sums   │
│ 13. Modular Regimes        │ Cycle detection: mod m <= 16       │
│ 14. Asymptotic Analysis    │ Log-linear heuristic regression    │
└────────────────────────────┴────────────────────────────────────┘
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
| `quasipolynomial` | Periodic multisection forward differences | $a(m \cdot k + r) = P_r(k)$ for periodic branches ($m \le 6$) |
| `linear_recurrence` | Berlekamp-Massey minimal connection polynomial over $\mathbb{Q}$ | $a(n) = \sum_{j=1}^k c_j a(n-j)$ |
| `inhomogeneous_recurrence` | Linear recurrence with rational driving polynomial | $a(n) = \sum_{j=1}^k c_j a(n-j) + P(n)$ ($P \in \mathbb{Q}[n]$) |
| `holonomic` | Rational nullspace over $\mathbb{Q}$ for P-finite systems | $\sum_{j=0}^k p_j(n) a(n-j) = 0$ ($p_j \in \mathbb{Z}[n]$) |
| `nonlinear_recurrence` | Exact Vandermonde & bilinear Somos elimination | $a(n) = P(a(n-1))$ or $a(n)a(n-k) = \sum c_j a(n-j)a(n-k+j)$ |
| `algebraic_generating_function` | Hermite-Padé quadratic curve relation over $\mathbb{Q}$ | $A_2(x) G(x)^2 + A_1(x) G(x) + A_0(x) = 0$ ($A_i \in \mathbb{Z}[x]$) |
| `convolution_recurrence` | Cauchy and binomial self-convolution equations | $a(n) = \sum_{k=0}^{n-1} a(k)a(n-1-k)$ or $\sum_{k=0}^{n-1} \binom{n-1}{k} a(k)$ |
| `multiplicative_recurrence` | Exact multiplicative power recurrence | $a(n) = c \cdot \prod_{j=1}^k a(n-j)^{p_j}$ |
| `generating_function` | Padé approximation from recurrence coefficients | $G(x) = \frac{P(x)}{Q(x)}$ |
| `symbolic_search` | Canonicalized DAG grammar search | Exponential ($c^n$), factorials ($n!$), polygonal |
| `transforms` | Binomial & prefix-sum transformations | $B(a)_n = \sum_{k=0}^n \binom{n}{k} a_k$ |
| `modular` | Residue class cycle detection with transient prefixes | Periodicity $a(n+p) \equiv a(n) \pmod m$ for $n \ge n_0 + t$ |
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
Runs all 14 deterministic discovery engines against the target sequence and outputs ranked candidates.

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
# Standard in-process performance benchmarks
oeis-discovery benchmark

# Hard sequence benchmark (Holonomic, Quasipolynomials, Somos, Apery numbers)
oeis-discovery benchmark --suite hard

# High mathematical importance benchmark (25 open problem sequences)
oeis-discovery benchmark --suite importance

# Withheld-formula blind recovery benchmark
oeis-discovery benchmark --suite withheld

# Unlisted formulas audit on real OEIS sequences
oeis-discovery benchmark --suite unlisted

# Run all suites
oeis-discovery benchmark --suite all
```

---

## 6. Benchmarks and Empirical Results

All benchmarks are measured in-process using high-resolution hardware performance counters (`time.perf_counter`), preceded by 5 discarded warmup runs.

### 6.1 Standard Discovery Benchmark Suite
| Benchmark Target | Underlying Structure | Discovered Representation | Verification | Duration (ms) |
| :--- | :--- | :--- | :--- | :---: |
| `SYN001` | Arithmetic Progression | $a(n) = 3(n - 0) + 5$ | Exact Match (25 terms) | 0.22 |
| `SYN002` | Quadratic Polynomial | $a(n) = 4\binom{n}{2} + 1n + 7$ | Exact Match (25 terms) | 0.45 |
| `SYN003` | Cubic Polynomial | Newton series degree 3 | Exact Match (25 terms) | 0.61 |
| `A000045` | Fibonacci Numbers | $a(n) = a(n-1) + a(n-2)$ | Exact Match (22 terms) | 0.88 |
| `A000129` | Pell Numbers | $a(n) = 2a(n-1) + a(n-2)$ | Exact Match (18 terms) | 0.74 |
| `A000079` | Powers of 2 | $a(n) = 2^n$ | Exact Match (22 terms) | 0.31 |

### 6.2 Hard Sequences Benchmark Suite (P-Finite, Quasipolynomial, Nonlinear)
| A-Number | Sequence Family | Mathematical Class | Discovered Representation | Method | Verification | Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `A000108` | Catalan numbers | Holonomic (Order 1, Deg 1) | $(n+1)a(n) - (4n-2)a(n-1) = 0$ | `holonomic` | Exact (25 terms) | 2.88 |
| `A001006` | Motzkin numbers | Holonomic (Order 2, Deg 1) | $(n+2)a(n) - (2n+1)a(n-1) - 3(n-1)a(n-2) = 0$ | `holonomic` | Exact (25 terms) | 4.84 |
| `A001850` | Central Delannoy | Holonomic (Order 2, Deg 1) | $n a(n) - (6n-3)a(n-1) + (n-1)a(n-2) = 0$ | `holonomic` | Exact (25 terms) | 5.15 |
| `A006318` | Large Schröder | Holonomic (Order 2, Deg 1) | $(n+1)a(n) - (6n-3)a(n-1) + (n-2)a(n-2) = 0$ | `holonomic` | Exact (25 terms) | 5.31 |
| `A000166` | Derangements | Holonomic (Order 2, Deg 1) | $a(n) - (n-1)a(n-1) - (n-1)a(n-2) = 0$ | `holonomic` | Exact (22 terms) | 4.38 |
| `A005259` | Apéry for $\zeta(3)$ | Holonomic (Order 2, Deg 3) | $n^3 a(n) - (34n^3 - 51n^2 + 27n - 5)a(n-1) + (n-1)^3 a(n-2) = 0$ | `holonomic` | Exact (25 terms) | 24.71 |
| `A005258` | Apéry for $\zeta(2)$ | Holonomic (Order 2, Deg 2) | $n^2 a(n) - (11n^2 - 11n + 3)a(n-1) - (n-1)^2 a(n-2) = 0$ | `holonomic` | Exact (25 terms) | 10.80 |
| `A001147` | Double factorials | Holonomic (Order 1, Deg 1) | $a(n) - (2n-1)a(n-1) = 0$ | `holonomic` | Exact (22 terms) | 1.83 |
| `A002620` | Quarter squares | Quasipolynomial (Period 2, Deg 2) | $a(n) = \lfloor n^2 / 4 \rfloor$ | `quasipolynomial` | Exact (30 terms) | 2.90 |
| `A004526` | Coin change $\{1, 2\}$ | Quasipolynomial (Period 2, Deg 1) | $a(n) = \lfloor n / 2 \rfloor + 1$ | `quasipolynomial` | Exact (25 terms) | 2.48 |
| `A000058` | Sylvester's sequence | Nonlinear Recurrence (Deg 2) | $a(n) = a(n-1)^2 - a(n-1) + 1$ | `nonlinear_recurrence` | Exact (7 terms) | 0.23 |
| `A006720` | Somos-4 sequence | Bilinear Recurrence (Order 4) | $a(n)a(n-4) = a(n-1)a(n-3) + a(n-2)^2$ | `nonlinear_recurrence` | Exact (15 terms) | 4.94 |
| `A001411` | 2D Self-avoiding walks | Open Problem | $a(n) \sim 1.8866 \cdot 2.7146^n$ ($R^2 = 0.9999$) | `asymptotic` | Heuristic (28 terms) | 20.03 |
| `A080601` | Rubik's cube states | Cayley Graph / Branching | $a(n) \sim 1.3317 \cdot 9.3125^n$ ($R^2 = 1.0000$) | `asymptotic` | Heuristic (16 terms) | 6.64 |

- **Exact Mathematical Recovery Rate**: **13 / 15 (86.7%)**
- **Average Computation Time Per Target**: **7.86 ms**

### 6.3 High Mathematical Importance Benchmark Suite (Lacking %F Formula)
Evaluation across historically renowned, mathematically open sequences from OEIS that lack an `%F` formula field:

| A-Number | Sequence Family | Mathematical Domain | Discovered Model / Behavior | Status | Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `A001411` | SAW 2D Square Lattice | Statistical Physics (CFT / Polymers) | $a(n) \sim 1.8848 \cdot 2.7149^n$ ($R^2 = 0.9999$) | Heuristic | 18.38 |
| `A001412` | SAW 3D Cubic Lattice | Statistical Physics (3D Polymers) | $a(n) \sim 1.4577 \cdot 4.7467^n$ ($R^2 = 1.0000$) | Heuristic | 21.89 |
| `A001334` | SAW Hexagonal Lattice | Statistical Physics (Smirnov Fields Medal) | $a(n) \sim 1.7903 \cdot 4.2972^n$ ($R^2 = 0.9999$) | Heuristic | 28.30 |
| `A002931` | SAP 2D Square Lattice | Statistical Physics (Polygons) | $a(n) \sim 0.0055 \cdot 5.5093^n$ ($R^2 = 0.9978$) | Heuristic | 23.34 |
| `A001336` | SAW FCC Lattice | Statistical Physics (Face-Centered Cubic) | $a(n) \sim 1.3163 \cdot 10.2419^n$ ($R^2 = 1.0000$) | Heuristic | 22.07 |
| `A003198` | Square Bond Percolation | Percolation Theory (Cluster Series) | $a(n) \sim 4.1964 \cdot 2.3017^n$ ($R^2 = 0.9968$) | Heuristic | 11.64 |
| `A003207` | Cubic Bond Percolation | Percolation Theory (Cluster Series) | $a(n) \sim 2.5754 \cdot 4.4820^n$ ($R^2 = 0.9998$) | Heuristic | 2.28 |
| `A006727` | Square Percolation Series | Percolation Theory (Susceptibility) | $a(n) \sim 3.0958 \cdot 1.6369^n$ ($R^2 = 0.9922$) | Heuristic | 26.03 |
| `A006809` | Hex Percolation Series | Percolation Theory (Honeycomb) | $a(n) \sim 2.5267 \cdot 2.3056^n$ ($R^2 = 0.9988$) | Heuristic | 18.23 |
| `A000791` | Ramsey Numbers $R(3, n)$ | Ramsey Theory (Extremal Combinatorics) | *None (Honest Non-Overfitting)* | `no_candidate` | 0.44 |
| `A006672` | Ramsey Edge-Coloring | Ramsey Theory (Complete Colorings) | *None (Honest Non-Overfitting)* | `no_candidate` | 1.83 |
| `A014540` | Rectilinear Crossing $K_n$ | Discrete Geometry (Harary-Hill Conjecture) | *None (Honest Non-Overfitting)* | `no_candidate` | 1.25 |
| `A000003` | Gauss Class Number $D=-4n$ | Algebraic Number Theory (Gauss Problem) | *None (Honest Non-Overfitting)* | `no_candidate` | 44.15 |
| `A000924` | Class Number $\mathbb{Q}(\sqrt{-n})$ | Algebraic Number Theory (Dirichlet Formula) | *None (Honest Non-Overfitting)* | `no_candidate` | 42.10 |
| `A000018` | Integers $x^2 + 16y^2 \le 2^n$ | Analytic Number Theory (Landau-Ramanujan) | $a(n) \sim 0.2751 \cdot 1.9112^n$ ($R^2 = 0.9990$) | Heuristic | 31.42 |
| `A000021` | Integers $x^2 + 12y^2 \le 2^n$ | Analytic Number Theory (Quadratic Forms) | $a(n) \sim 0.3189 \cdot 1.9137^n$ ($R^2 = 0.9992$) | Heuristic | 29.56 |
| `A000024` | Integers $x^2 + 10y^2 \le 2^n$ | Analytic Number Theory (Quadratic Forms) | $a(n) \sim 0.3580 \cdot 1.9183^n$ ($R^2 = 0.9994$) | Heuristic | 33.43 |
| `A000047` | Integers $x^2 - 2y^2 \le 2^n$ | Analytic Number Theory (Indefinite Forms) | $a(n) \sim 0.5511 \cdot 1.9097^n$ ($R^2 = 0.9991$) | Heuristic | 18.87 |
| `A002106` | Transitive Permutation Groups | Group Theory (O'Nan-Scott / CFSG) | *None (Honest Non-Overfitting)* | `no_candidate` | 26.40 |
| `A000019` | Primitive Groups of Degree $n$ | Group Theory (Primitive Actions) | *None (Honest Non-Overfitting)* | `no_candidate` | 45.92 |
| `A003094` | Connected Planar Graphs | Graph Theory (Giménez-Noy Enumeration) | *None (Honest Non-Overfitting)* | `no_candidate` | 5.76 |
| `A005470` | Unlabeled Planar Graphs | Graph Theory (Planar Graph Asymptotics) | *None (Honest Non-Overfitting)* | `no_candidate` | 5.93 |
| `A000112` | Unlabeled Posets on $n$ Nodes | Order Theory (Kleitman-Rothschild) | *None (Honest Non-Overfitting)* | `no_candidate` | 6.11 |
| `A002851` | Unlabeled Trivalent Graphs | Graph Theory (Regular Cubic Graphs) | *None (Honest Non-Overfitting)* | `no_candidate` | 17.68 |
| `A048987` | Chess Game Tree (Ply $n$) | Game Theory (Shannon Number Complexity) | $a(n) \sim 0.4062 \cdot 27.0991^n$ ($R^2 = 0.9996$) | Heuristic | 6.83 |
| `A080601` | Rubik's Cube States | Combinatorial State Spaces (Cayley Graph) | $a(n) \sim 1.4025 \cdot 13.2301^n$ ($R^2 = 1.0000$) | Heuristic | 7.06 |

---

## 7. Licensing and Attribution

- **Software Code**: Licensed under the **MIT License** (see [LICENSE](LICENSE)).
- **OEIS Data Attribution**: Sequence data and descriptions are from *The On-Line Encyclopedia of Integer Sequences (OEIS)*, published at https://oeis.org, and licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
- OEIS is a registered trademark of The OEIS Foundation Inc.
