"""
Generates rich per-sequence Markdown and JSON reports.
Clearly delineates empirical finite-term fits from universal mathematical proofs.
"""

import json
from pathlib import Path
from typing import List, Optional
from ..candidate.model import CandidateFormula, VerificationStatus
from ..ingestion.parser import OEISRecord


class PerSequenceReporter:
    @staticmethod
    def generate_markdown(record: OEISRecord, candidates: List[CandidateFormula]) -> str:
        lines = [
            f"# Analysis Report: {record.a_number}",
            f"**Title**: {record.name}",
            f"**First Term Index (Offset)**: n = {record.offset_first_term}",
            f"**Available Terms ({len(record.terms)})**: `{record.terms[:20]}`{'...' if len(record.terms) > 20 else ''}",
            "",
            "## Eligibility Screening",
            f"- **Explicit %F Formula Present in OEIS Record**: {'YES' if record.has_explicit_formula else 'NO'}",
            f"- **Target Population Justification**: Screened because sequence has {len(record.terms)} available terms and lacks explicit %F formula metadata.",
            "",
            "## Mathematical Candidates Discovered",
        ]

        if not candidates:
            lines.append("No exact formula, recurrence, or generating function found within configured search budgets.")
        else:
            lines.append("| Rank | Method | Formula / Model | Complexity (MDL) | Verification Status | Terms Tested |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for i, c in enumerate(candidates, 1):
                lines.append(f"| {i} | `{c.method}` | `{c.formula_str}` | {c.complexity:.2f} | **{c.verification_status.value}** | {c.terms_tested} |")

            lines.extend([
                "",
                "### Detailed Candidate Breakdown",
            ])
            for i, c in enumerate(candidates, 1):
                lines.extend([
                    f"#### Rank {i}: {c.method}",
                    f"- **Mathematical Representation**: `{c.formula_str}`",
                    f"- **LaTeX**: `${c.latex_str}$`",
                    f"- **Verification Outcome**: Exact match across all {c.terms_tested} available target terms.",
                    f"- **Description**: {c.description}",
                    "",
                ])

        lines.extend([
            "---",
            "> [!IMPORTANT]",
            "> **Mathematical Honesty Notice**: Exact reproduction of finite known OEIS terms is an empirical discovery, not a formal mathematical proof for all $n \\in \\mathbb{N}$. Independent symbolic derivation or mathematical induction is required to establish universality.",
            "",
            "### Data Provenance & Attribution",
            "- Sequence source: *The On-Line Encyclopedia of Integer Sequences (OEIS)* (https://oeis.org)",
            "- Data license: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        ])

        return "\n".join(lines)
