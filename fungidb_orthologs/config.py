"""Defaults and optional organism overrides for FungiDB ortholog lookup."""

from __future__ import annotations

# Optional ``download_key -> api_organism_string`` entries when auto-resolution
# from the GenesByTaxonGene vocabulary is wrong or missing for a genome.
# Normally empty: keys from ``list-genomes`` are resolved via ``organisms.py``.
ORGANISM_OVERRIDES: dict[str, str] = {}
