"""
Parse query genome FASTA to extract gene IDs for ortholog lookup.
"""

from __future__ import annotations

import re
from pathlib import Path

from Bio import SeqIO


def parse_locus_tag(header: str) -> str | None:
    """Extract locus_tag from a FASTA header if present."""
    m = re.search(r"\[locus_tag=([^\]]+)\]", header, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    parts = header.split()
    if parts:
        first = parts[0].lstrip(">")
        if first and not first.startswith("|"):
            return first
    return None


def get_gene_ids_from_fasta(fasta_path: str | Path) -> list[str]:
    """Read a CDS or protein FASTA and return a list of gene IDs."""
    path = Path(fasta_path)
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {path}")
    ids = []
    for rec in SeqIO.parse(path, "fasta"):
        gid = parse_locus_tag(rec.description) or parse_locus_tag(rec.id) or rec.id
        if gid:
            ids.append(gid)
    return ids


def infer_fungidb_organism_from_fasta(fasta_path: str | Path) -> str | None:
    """Heuristic: infer FungiDB organism from FASTA headers or filename."""
    path = Path(fasta_path)
    if not path.exists():
        return None
    name = path.stem.upper()
    if "A1163" in name and ("ASM15014" in name or "FUMIGATUS" in name or "AFUB" in name):
        return "AfumigatusA1163"
    if "AF293" in name or "AFUMIGATUS" in name:
        return "AfumigatusAf293"
    prefixes_to_organism = {
        "AFUB_": "AfumigatusA1163",
        "AFUA_": "AfumigatusAf293",
        "CAAL_": "CalbicansSC5314",
        "SPBC": "Spombe972h",
        "SPAC": "Spombe972h",
    }
    for rec in SeqIO.parse(path, "fasta"):
        gid = parse_locus_tag(rec.description) or parse_locus_tag(rec.id) or rec.id
        if not gid:
            continue
        for prefix, org in prefixes_to_organism.items():
            if gid.upper().startswith(prefix):
                return org
        break
    return None
