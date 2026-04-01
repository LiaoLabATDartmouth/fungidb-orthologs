"""
Resolve FungiDB download-style organism keys to API / OrthologsLite organism strings.

``list-genomes`` returns folder names (e.g. ``NcrassaOR74A``). The gene search and
ortholog table use the same labels as the ``organism`` vocabulary in
``GenesByTaxonGene`` (e.g. ``Neurospora crassa OR74A``). We fetch that vocabulary
once and map keys using the same rules FungiDB uses for download directory names.
"""

from __future__ import annotations

import functools
import re
from typing import Optional

import httpx

from fungidb_orthologs.config import ORGANISM_OVERRIDES

GENES_BY_TAXON_GENE_URL = (
    "https://fungidb.org/fungidb/service/record-types/gene/searches/GenesByTaxonGene"
)
TIMEOUT = 60


def term_to_download_key(term: str) -> str:
    """
    Derive the download-site / list-genomes style key from a vocabulary organism term.

    Examples:
        "Neurospora crassa OR74A" -> "NcrassaOR74A"
        "Aphanomyces astaci strain APO3" -> "AastaciAPO3"
        "Schizosaccharomyces pombe 972h-" -> "Spombe972h"
    """
    parts = term.split()
    if len(parts) < 2:
        return re.sub(r"[^A-Za-z0-9.]", "", term)
    genus, species = parts[0], parts[1]
    rest = [p for p in parts[2:] if p.lower() != "strain"]
    strain = "".join(rest).rstrip("-")
    return genus[0] + species + strain


def _iter_vocab_leaf_terms(vocab_children: list) -> list[str]:
    terms: list[str] = []
    stack: list = list(vocab_children)
    while stack:
        node = stack.pop()
        ch = node.get("children") or []
        if not ch:
            d = node.get("data") or {}
            term = d.get("term")
            if term and term not in ("@@fake@@", "Fungi") and " " in str(term):
                terms.append(str(term))
        else:
            stack.extend(reversed(ch))
    return terms


@functools.lru_cache(maxsize=1)
def _organism_maps() -> tuple[dict[str, str], dict[str, str]]:
    """
    Build (download_key -> api_organism_string, api_organism_string -> download_key).

    ``ORGANISM_OVERRIDES`` from config is merged last so maintainers can fix edge cases.
    """
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(GENES_BY_TAXON_GENE_URL)
    r.raise_for_status()
    data = r.json()
    params = data["searchData"]["parameters"]
    orgp = next(p for p in params if p.get("name") == "organism")
    vocab = orgp.get("vocabulary") or {}
    raw_terms = _iter_vocab_leaf_terms(vocab.get("children", []))

    key_to_term: dict[str, str] = {}
    for t in raw_terms:
        k = term_to_download_key(t)
        key_to_term[k] = t

    key_to_term.update(ORGANISM_OVERRIDES)

    term_to_key: dict[str, str] = {}
    for k, t in key_to_term.items():
        term_to_key[t] = k

    return key_to_term, term_to_key


def clear_organism_cache() -> None:
    """Drop cached vocabulary (for tests)."""
    _organism_maps.cache_clear()


def list_gene_search_organisms() -> list[tuple[str, str]]:
    """
    Return organisms in the GenesByTaxonGene ``organism`` vocabulary.

    Each item is ``(download_key, vocabulary_organism_string)``, sorted by
    vocabulary string (then key). ``download_key`` is the same style as
    ``list-genomes`` folder names when FungiDB follows the usual naming pattern;
    ``ORGANISM_OVERRIDES`` entries are included.
    """
    key_to_term, _ = _organism_maps()
    return sorted(key_to_term.items(), key=lambda kv: (kv[1].lower(), kv[0]))


def resolve_to_api_organism(identifier: str) -> str:
    """
    Map a ``list-genomes`` key (or an API organism string) to the exact string
    FungiDB expects in gene search / tables.

    If ``identifier`` already looks like a full organism label (contains a space),
    it is returned trimmed. Otherwise the GenesByTaxonGene vocabulary is used.
    """
    s = (identifier or "").strip()
    if not s:
        return s
    if " " in s:
        return s
    key_to_term, _ = _organism_maps()
    return key_to_term.get(s, s)


def get_fungidb_organism_key(name: str) -> Optional[str]:
    """
    Resolve a user-provided label to a download-style organism key when possible.

    Accepts either a key already in the vocabulary map or the exact API organism string.
    """
    name = (name or "").strip()
    if not name:
        return None
    key_to_term, term_to_key = _organism_maps()
    if name in key_to_term:
        return name
    if name in term_to_key:
        return term_to_key[name]
    key_like = name.replace(" ", "").replace(".", "").lower()
    for key in key_to_term:
        if key.replace(" ", "").lower() == key_like:
            return key
    return None
