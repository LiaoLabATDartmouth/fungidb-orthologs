"""
FungiDB ortholog extraction tool.

Fetch orthologs from FungiDB for fungal genomes. Supports listing available genomes,
specifying target and reference organisms, and extracting orthologs via CLI or API.
"""

__version__ = "0.1.0"

from fungidb_orthologs.client import get_orthologs_for_genes
from fungidb_orthologs.genomes import list_genomes
from fungidb_orthologs.service import get_orthologs_for_genome

__all__ = [
    "get_orthologs_for_genes",
    "get_orthologs_for_genome",
    "list_genomes",
]
