"""
Machine-readable and human-readable export routines (JSON, CSV, Markdown).
"""

import csv
import json
from pathlib import Path
from typing import List
from ..candidate.model import CandidateFormula


class ResultExporter:
    @staticmethod
    def export_json(candidates: List[CandidateFormula], out_path: Path) -> None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        data = [c.to_dict() for c in candidates]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def export_csv(candidates: List[CandidateFormula], out_path: Path) -> None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "id", "a_number", "method", "formula_str", "latex_str",
            "complexity", "terms_tested", "verification_status"
        ]
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for c in candidates:
                writer.writerow(c.to_dict())

