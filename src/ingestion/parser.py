"""
Robust, streaming parser for OEIS internal format entries.
Handles multi-line fields (%I, %S, %T, %U, %N, %F, %O, %C, %D, %H, %K, %A, %o, %p, %Y).
"""

from dataclasses import dataclass, field
import re
from typing import List, Optional, Tuple


@dataclass
class OEISRecord:
    a_number: str                                      # e.g., "A000045"
    id_number: int                                     # e.g., 45
    name: str = ""                                     # %N description
    offset_first_term: int = 0                         # First parameter of %O
    offset_first_gt_one: int = 1                       # Second parameter of %O
    terms: List[int] = field(default_factory=list)     # Parsed exact integer terms (%S, %T, %U)
    formulas: List[str] = field(default_factory=list)  # %F explicit formulas
    comments: List[str] = field(default_factory=list)  # %C comments
    references: List[str] = field(default_factory=list)# %D references
    links: List[str] = field(default_factory=list)     # %H links
    keywords: List[str] = field(default_factory=list)  # %K keywords
    author: str = ""                                   # %A author
    programs: List[str] = field(default_factory=list)  # %o / %p programs (NEVER executed)
    cross_refs: List[str] = field(default_factory=list)# %Y cross references

    @property
    def has_explicit_formula(self) -> bool:
        """Determines if the record contains any non-empty %F field."""
        return len(self.formulas) > 0 and any(f.strip() for f in self.formulas)

    @property
    def is_eligible_target(self) -> bool:
        """
        Operational eligibility criterion:
        Must have at least 6 terms and no explicit %F formula field.
        """
        return (not self.has_explicit_formula) and len(self.terms) >= 6


class OEISParser:
    """Parses raw OEIS internal format lines into structured OEISRecord objects."""

    RECORD_LINE_RE = re.compile(r"^%([A-Za-z])\s+(A\d{6})\s*(.*)$")

    @classmethod
    def parse_entry_lines(cls, lines: List[str]) -> Optional[OEISRecord]:
        """Parses a contiguous block of OEIS internal format lines for a single sequence."""
        if not lines:
            return None

        current_a_num: Optional[str] = None
        term_strings: List[str] = []
        name_parts: List[str] = []
        formulas: List[str] = []
        comments: List[str] = []
        references: List[str] = []
        links: List[str] = []
        keywords: List[str] = []
        programs: List[str] = []
        cross_refs: List[str] = []
        offset_val = (0, 1)
        author = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = cls.RECORD_LINE_RE.match(line)
            if not m:
                continue

            tag, a_num, payload = m.groups()
            current_a_num = a_num

            if tag in ("S", "T", "U"):
                term_strings.append(payload)
            elif tag == "N":
                name_parts.append(payload)
            elif tag == "F":
                formulas.append(payload)
            elif tag == "C":
                comments.append(payload)
            elif tag == "D":
                references.append(payload)
            elif tag == "H":
                links.append(payload)
            elif tag == "K":
                keywords.extend(k.strip() for k in payload.split(",") if k.strip())
            elif tag == "O":
                offset_val = cls._parse_offset(payload)
            elif tag == "A":
                author = payload
            elif tag in ("o", "p"):
                # Untrusted code: preserved solely for provenance; NEVER executed
                programs.append(payload)
            elif tag == "Y":
                cross_refs.append(payload)

        if not current_a_num:
            return None

        # Parse terms into arbitrary-precision integers
        parsed_terms: List[int] = []
        raw_terms_joined = ",".join(term_strings)
        for part in raw_terms_joined.split(","):
            part = part.strip()
            if part:
                try:
                    parsed_terms.append(int(part))
                except ValueError:
                    # Non-integer term (e.g. malformed or table separator)
                    continue

        id_num = int(current_a_num[1:])
        return OEISRecord(
            a_number=current_a_num,
            id_number=id_num,
            name=" ".join(name_parts),
            offset_first_term=offset_val[0],
            offset_first_gt_one=offset_val[1],
            terms=parsed_terms,
            formulas=formulas,
            comments=comments,
            references=references,
            links=links,
            keywords=keywords,
            author=author,
            programs=programs,
            cross_refs=cross_refs,
        )

    @staticmethod
    def _parse_offset(payload: str) -> Tuple[int, int]:
        parts = [p.strip() for p in payload.split(",") if p.strip()]
        if len(parts) >= 2:
            try:
                return int(parts[0]), int(parts[1])
            except ValueError:
                pass
        elif len(parts) == 1:
            try:
                return int(parts[0]), 1
            except ValueError:
                pass
        return 0, 1

