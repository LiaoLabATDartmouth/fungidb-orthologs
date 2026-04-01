"""
Test ortholog extraction: A. fumigatus A1163 → C. albicans, S. cerevisiae, S. pombe.
"""

from __future__ import annotations

import pytest

import pandas as pd

from fungidb_orthologs.client import filter_orthologs_to_references
from fungidb_orthologs.organisms import clear_organism_cache
from fungidb_orthologs.service import get_orthologs_by_organism


def test_filter_ncrassa_or74a_reference_matches_fungidb_display_name():
    """
    OrthologsLite uses vocabulary organism strings (e.g. 'Neurospora crassa OR74A').
    ``list-genomes``-style keys like ``NcrassaOR74A`` must still match after resolution
    from the GenesByTaxonGene vocabulary (fetched once and cached).
    """
    df = pd.DataFrame(
        {
            "GID": ["C1_13700W_A"],
            "ORTHOLOGS_GID": ["NCU04173"],
            "ORTHOLOGS_ORGANISM": ["Neurospora crassa OR74A"],
            "ORTHOLOGS_PRODUCT": ["actin"],
        }
    )
    try:
        out = filter_orthologs_to_references(df, ["NcrassaOR74A"])
        assert len(out) == 1
        assert out.iloc[0]["ORTHOLOGS_GID"] == "NCU04173"
    finally:
        clear_organism_cache()


@pytest.mark.timeout(300)  # FungiDB API can take 1-3 min for large genomes
def test_a1163_orthologs_to_calbicans_scerevisiae_spombe():
    """
    Extract orthologs from Aspergillus fumigatus A1163 to C. albicans, S. cerevisiae, S. pombe.
    """
    target = "AfumigatusA1163"
    references = ["CalbicansSC5314", "ScerevisiaeS288C", "Spombe972h"]

    df = get_orthologs_by_organism(
        target_organism=target,
        reference_organisms=references,
    )

    assert len(df) > 0, "Expected at least some ortholog rows"
    assert "GID" in df.columns
    assert "ORTHOLOGS_GID" in df.columns
    assert "ORTHOLOGS_ORGANISM" in df.columns

    # Check we have orthologs from all three reference species (CSV uses vocabulary strings)
    def _norm_org(o: str) -> str:
        return str(o).strip().rstrip("-").strip()

    orgs = df["ORTHOLOGS_ORGANISM"].astype(str).str.strip().unique()
    expected = {
        _norm_org(x)
        for x in (
            "Candida albicans SC5314",
            "Saccharomyces cerevisiae S288C",
            "Schizosaccharomyces pombe 972h",
        )
    }
    found = {_norm_org(o) for o in orgs}
    assert expected.intersection(found), (
        f"Expected orthologs from C. albicans, S. cerevisiae, S. pombe; got {orgs}"
    )
