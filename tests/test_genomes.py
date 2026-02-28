"""Test list_genomes and genome parser."""

from __future__ import annotations

import pytest

from fungidb_orthologs.genomes import list_genomes
from fungidb_orthologs.genome_parser import get_gene_ids_from_fasta, infer_fungidb_organism_from_fasta


@pytest.mark.timeout(30)
def test_list_genomes():
    """List all FungiDB genomes."""
    genomes = list_genomes()
    assert len(genomes) > 100
    assert "AfumigatusA1163" in genomes
    assert "CalbicansSC5314" in genomes
    assert "ScerevisiaeS288C" in genomes
    assert "Spombe972h" in genomes


def test_parse_a1163_fasta():
    """Parse A1163 FASTA and extract gene IDs."""
    from pathlib import Path

    fasta = Path(__file__).resolve().parent.parent / "query_genomes" / "A1163_ASM15014v1_cds_from_genomic.fna"
    if not fasta.exists():
        pytest.skip("Query genome FASTA not found")
    ids = get_gene_ids_from_fasta(fasta)
    assert len(ids) > 0
    assert any("AFUB_" in i for i in ids[:20])
    org = infer_fungidb_organism_from_fasta(fasta)
    assert org == "AfumigatusA1163"
