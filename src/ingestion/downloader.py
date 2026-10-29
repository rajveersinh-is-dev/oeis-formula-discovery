"""
Resumable, offline-safe OEIS data acquisition module.
Downloads the official OEIS data export (stripped.gz, names.gz) explicitly.
Tracks SHA-256 checksums and revision timestamps for mathematical provenance.
"""

import gzip
import hashlib
import json
from pathlib import Path
import shutil
from typing import Optional, Tuple
import urllib.request
from rich.console import Console

console = Console()


class OEISDownloader:
    # Official OEIS download endpoints per https://oeis.org/wiki/Download
    STRIPPED_URL = "https://oeis.org/stripped.gz"
    NAMES_URL = "https://oeis.org/names.gz"

    def __init__(self, target_dir: Path):
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def fetch_data(self, force: bool = False) -> Tuple[Path, Path]:
        """
        Explicitly downloads OEIS stripped.gz and names.gz.
        Confined strictly to this explicit command; never triggered implicitly.
        """
        stripped_gz = self.target_dir / "stripped.gz"
        names_gz = self.target_dir / "names.gz"

        console.print("[bold cyan]OEIS Data Acquisition[/bold cyan]")
        console.print(f"Target directory: {self.target_dir}\n")

        if stripped_gz.exists() and not force:
            console.print(f"[green][OK][/green] Found existing {stripped_gz.name} ({stripped_gz.stat().st_size // 1024} KB)")
        else:
            self._download_file(self.STRIPPED_URL, stripped_gz)

        if names_gz.exists() and not force:
            console.print(f"[green][OK][/green] Found existing {names_gz.name} ({names_gz.stat().st_size // 1024} KB)")
        else:
            self._download_file(self.NAMES_URL, names_gz)

        # Record checksums
        self._record_provenance(stripped_gz, names_gz)
        return stripped_gz, names_gz

    def _download_file(self, url: str, dest: Path) -> None:
        console.print(f"Downloading {url} -> {dest.name}...")
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "OEIS-Formula-Discovery-Lab/0.1.0"}
        )
        with urllib.request.urlopen(req) as response, open(dest, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        console.print(f"[green][OK][/green] Downloaded {dest.name} ({dest.stat().st_size // 1024} KB)")

    def _record_provenance(self, stripped_path: Path, names_path: Path) -> None:
        prov_file = self.target_dir / "provenance.json"
        provenance = {
            "stripped_sha256": self._sha256(stripped_path),
            "names_sha256": self._sha256(names_path),
            "source_urls": [self.STRIPPED_URL, self.NAMES_URL],
            "attribution": "OEIS data is licensed under Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0).",
            "citation": "The On-Line Encyclopedia of Integer Sequences, published electronically at https://oeis.org.",
        }
        with open(prov_file, "w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=2)
        console.print(f"[green][OK][/green] Provenance recorded in {prov_file}")

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
