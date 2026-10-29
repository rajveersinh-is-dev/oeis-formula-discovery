"""
SQLite database engine for local indexing, eligibility screening, and result persistence.
Uses WAL mode for concurrent, robust, and crash-resilient access.
"""

import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, Iterator, List, Optional
from .parser import OEISRecord


class OEISDatabase:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_schema(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sequences (
                    a_number TEXT PRIMARY KEY,
                    id_number INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    offset_first INTEGER NOT NULL,
                    term_count INTEGER NOT NULL,
                    terms_json TEXT NOT NULL,
                    has_formula INTEGER NOT NULL,
                    is_eligible INTEGER NOT NULL,
                    formulas_json TEXT NOT NULL,
                    comments_json TEXT NOT NULL,
                    keywords_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_sequences_eligible 
                ON sequences(is_eligible, term_count);

                CREATE TABLE IF NOT EXISTS scan_status (
                    a_number TEXT PRIMARY KEY,
                    status TEXT NOT NULL, -- 'pending', 'completed', 'failed', 'timeout'
                    candidates_count INTEGER DEFAULT 0,
                    best_candidate_id TEXT,
                    error_message TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(a_number) REFERENCES sequences(a_number)
                );

                CREATE TABLE IF NOT EXISTS candidates (
                    id TEXT PRIMARY KEY,
                    a_number TEXT NOT NULL,
                    method TEXT NOT NULL,
                    formula_str TEXT NOT NULL,
                    latex_str TEXT,
                    complexity REAL NOT NULL,
                    terms_tested INTEGER NOT NULL,
                    verification_status TEXT NOT NULL, -- 'exact_match', 'symbolically_verified', 'heuristic'
                    details_json TEXT NOT NULL,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(a_number) REFERENCES sequences(a_number)
                );

                CREATE INDEX IF NOT EXISTS idx_candidates_a_num 
                ON candidates(a_number, verification_status);
            """)

    def insert_record(self, record: OEISRecord) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sequences (
                    a_number, id_number, name, offset_first, term_count,
                    terms_json, has_formula, is_eligible, formulas_json,
                    comments_json, keywords_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.a_number,
                record.id_number,
                record.name,
                record.offset_first_term,
                len(record.terms),
                json.dumps(record.terms),
                1 if record.has_explicit_formula else 0,
                1 if record.is_eligible_target else 0,
                json.dumps(record.formulas),
                json.dumps(record.comments),
                json.dumps(record.keywords),
            ))

    def get_record(self, a_number: str) -> Optional[OEISRecord]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM sequences WHERE a_number = ?", (a_number,)).fetchone()
            if not row:
                return None
            return OEISRecord(
                a_number=row["a_number"],
                id_number=row["id_number"],
                name=row["name"],
                offset_first_term=row["offset_first"],
                terms=json.loads(row["terms_json"]),
                formulas=json.loads(row["formulas_json"]),
                comments=json.loads(row["comments_json"]),
                keywords=json.loads(row["keywords_json"]),
            )

    def iter_eligible(self) -> Iterator[OEISRecord]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM sequences WHERE is_eligible = 1 ORDER BY id_number ASC")
            for row in cursor:
                yield OEISRecord(
                    a_number=row["a_number"],
                    id_number=row["id_number"],
                    name=row["name"],
                    offset_first_term=row["offset_first"],
                    terms=json.loads(row["terms_json"]),
                    formulas=json.loads(row["formulas_json"]),
                    comments=json.loads(row["comments_json"]),
                    keywords=json.loads(row["keywords_json"]),
                )

    def record_candidate(self, candidate_dict: dict) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO candidates (
                    id, a_number, method, formula_str, latex_str, complexity,
                    terms_tested, verification_status, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_dict["id"],
                candidate_dict["a_number"],
                candidate_dict["method"],
                candidate_dict["formula_str"],
                candidate_dict.get("latex_str", ""),
                candidate_dict["complexity"],
                candidate_dict["terms_tested"],
                candidate_dict["verification_status"],
                json.dumps(candidate_dict.get("details", {})),
            ))

    def update_scan_status(
        self,
        a_number: str,
        status: str,
        count: int,
        best_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO scan_status (
                    a_number, status, candidates_count, best_candidate_id, error_message
                ) VALUES (?, ?, ?, ?, ?)
            """, (a_number, status, count, best_id, error))

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates database and analysis statistics."""
        with self._get_connection() as conn:
            total_imported = conn.execute("SELECT COUNT(*) FROM sequences").fetchone()[0]
            eligible_count = conn.execute("SELECT COUNT(*) FROM sequences WHERE is_eligible = 1").fetchone()[0]
            analyzed_count = conn.execute("SELECT COUNT(*) FROM scan_status WHERE status = 'completed'").fetchone()[0]
            candidates_total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
            exact_matches = conn.execute("SELECT COUNT(*) FROM candidates WHERE verification_status IN ('exact_match', 'symbolically_verified')").fetchone()[0]

            method_counts = {}
            for row in conn.execute("SELECT method, COUNT(*) FROM candidates GROUP BY method"):
                method_counts[row[0]] = row[1]

            return {
                "total_imported": total_imported,
                "eligible_count": eligible_count,
                "analyzed_count": analyzed_count,
                "candidates_total": candidates_total,
                "exact_matches": exact_matches,
                "method_counts": method_counts,
            }

