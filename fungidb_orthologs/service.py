"""
Orchestrates ortholog lookup: parse genome FASTA, call FungiDB, return orthologs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from fungidb_orthologs.organisms import get_fungidb_organism_key
from fungidb_orthologs.client import get_orthologs_for_genes
from fungidb_orthologs.genome_parser import get_gene_ids_from_fasta, infer_fungidb_organism_from_fasta


def get_orthologs_for_genome(
    fasta_path: Union[str, Path],
    reference_species: list[str],
    organism: Optional[str] = None,
) -> tuple[pd.DataFrame, str]:
    """
    Get orthologs for all genes in a genome FASTA.

    If organism is None, tries to infer from FASTA (e.g. AFUB_ -> AfumigatusA1163).
    ``reference_species`` must be a non-empty list of reference organism keys (``extract -r``).
    Returns (ortholog DataFrame, organism key used).
    """
    if not reference_species:
        raise ValueError(
            "reference_species is required: pass at least one reference genome."
        )

    fasta_path = Path(fasta_path)
    if not fasta_path.exists():
        raise FileNotFoundError(f"Genome FASTA not found: {fasta_path}")

    org_key = None
    if organism:
        org_key = get_fungidb_organism_key(organism) or organism
    if org_key is None:
        org_key = infer_fungidb_organism_from_fasta(fasta_path)
    if org_key is None:
        raise ValueError(
            "Could not determine FungiDB organism. "
            "Provide organism= (e.g. 'AfumigatusA1163') or use a FASTA with recognizable locus_tag. "
            "Run 'fungidb-orthologs list-genomes' to see available genomes."
        )

    gene_ids = get_gene_ids_from_fasta(fasta_path)
    df = get_orthologs_for_genes(
        organism=org_key,
        reference_organisms=reference_species,
        gene_ids=gene_ids if gene_ids else None,
    )
    return df, org_key


def get_orthologs_by_organism(
    target_organism: str,
    reference_organisms: list[str],
    gene_ids: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Get orthologs for a target organism (by FungiDB key) from specified reference organisms.
    No FASTA needed - use when you know the organism key.
    """
    if not reference_organisms:
        raise ValueError(
            "reference_organisms is required: pass at least one reference genome."
        )
    return get_orthologs_for_genes(
        organism=target_organism,
        reference_organisms=reference_organisms,
        gene_ids=gene_ids,
    )
