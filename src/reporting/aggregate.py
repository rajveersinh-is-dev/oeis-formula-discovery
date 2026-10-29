"""
Aggregate report generator over the entire scanned population.
"""

import json
from pathlib import Path
from typing import Any, Dict


class AggregateReporter:
    @staticmethod
    def generate_report(stats: Dict[str, Any]) -> str:
        lines = [
            "# OEIS Formula Discovery Lab — Population Scan Summary",
            "",
            "## Database Metrics",
            f"- **Total Sequences Imported**: {stats.get('total_imported', 0)}",
            f"- **Eligible Target Sequences (No %F field, >=6 terms)**: {stats.get('eligible_count', 0)}",
            f"- **Sequences Analyzed**: {stats.get('analyzed_count', 0)}",
            "",
            "## Discovery Yield by Method",
        ]

        method_counts = stats.get("method_counts", {})
        if method_counts:
            for method, count in method_counts.items():
                lines.append(f"- **{method}**: {count}")
        else:
            lines.append("- *No candidates recorded yet.*")

        lines.extend([
            "",
            "## Verification & Integrity Breakdown",
            f"- **Exact Term-by-Term Matches**: {stats.get('exact_matches', 0)}",
            f"- **Candidates Total**: {stats.get('candidates_total', 0)}",
            "",
            "---",
            "Report generated locally by `oeis-formula-discovery`. Zero AI services utilized.",
        ])
        return "\n".join(lines)

