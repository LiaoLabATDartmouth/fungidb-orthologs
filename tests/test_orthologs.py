"""
Test ortholog extraction: A. fumigatus A1163 → C. albicans, S. cerevisiae, S. pombe.
"""

from __future__ import annotations

import pytest

from fungidb_orthologs.service import get_orthologs_by_organism


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

    # Check we have orthologs from all three reference species
    orgs = df["ORTHOLOGS_ORGANISM"].astype(str).str.strip().unique()
    ref_names = {"CalbicansSC5314", "ScerevisiaeS288C", "Spombe972h"}
    ref_names_full = {"Candida albicans SC5314", "Saccharomyces cerevisiae S288C", "Schizosaccharomyces pombe 972h"}
    found = set(orgs)
    assert found.intersection(ref_names) or found.intersection(ref_names_full), (
        f"Expected orthologs from C. albicans, S. cerevisiae, S. pombe; got {found}"
    )
