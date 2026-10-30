"""Benchmark suite package."""

__all__ = [
    "run_benchmarks",
    "run_withheld_benchmark",
    "run_unlisted_audit",
    "run_hard_benchmarks",
    "run_high_importance_benchmark",
]


def __getattr__(name: str):
    if name == "run_benchmarks":
        from .suite import run_benchmarks
        return run_benchmarks
    if name == "run_withheld_benchmark":
        from .withheld_benchmark import run_withheld_benchmark
        return run_withheld_benchmark
    if name == "run_unlisted_audit":
        from .unlisted_audit import run_unlisted_audit
        return run_unlisted_audit
    if name == "run_hard_benchmarks":
        from .hard_sequences_benchmark import run_hard_benchmarks
        return run_hard_benchmarks
    if name == "run_high_importance_benchmark":
        from .high_importance_benchmark import run_high_importance_benchmark
        return run_high_importance_benchmark
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
