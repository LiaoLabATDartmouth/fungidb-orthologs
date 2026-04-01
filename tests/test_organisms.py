"""Unit tests for organism key ↔ FungiDB vocabulary mapping."""

from __future__ import annotations

import pytest

from fungidb_orthologs.organisms import (
    clear_organism_cache,
    get_fungidb_organism_key,
    list_gene_search_organisms,
    resolve_to_api_organism,
    term_to_download_key,
)


@pytest.mark.parametrize(
    "term,expected_key",
    [
        ("Neurospora crassa OR74A", "NcrassaOR74A"),
        ("Candida albicans SC5314", "CalbicansSC5314"),
        ("Aspergillus fumigatus A1163", "AfumigatusA1163"),
        ("Aphanomyces astaci strain APO3", "AastaciAPO3"),
        ("Schizosaccharomyces pombe 972h-", "Spombe972h"),
    ],
)
def test_term_to_download_key(term: str, expected_key: str) -> None:
    assert term_to_download_key(term) == expected_key


@pytest.mark.timeout(60)
def test_resolve_ncrassa_from_live_vocabulary() -> None:
    try:
        assert resolve_to_api_organism("NcrassaOR74A") == "Neurospora crassa OR74A"
    finally:
        clear_organism_cache()


def test_get_fungidb_organism_key_roundtrip() -> None:
    try:
        assert get_fungidb_organism_key("Neurospora crassa OR74A") == "NcrassaOR74A"
        assert get_fungidb_organism_key("NcrassaOR74A") == "NcrassaOR74A"
    finally:
        clear_organism_cache()


def test_list_gene_search_organisms_sorted_by_vocabulary(monkeypatch: pytest.MonkeyPatch) -> None:
    import fungidb_orthologs.organisms as org

    def fake_maps() -> tuple[dict[str, str], dict[str, str]]:
        kt = {"Zkey": "Zebra species X", "Akey": "Alpha species Y"}
        tk = {v: k for k, v in kt.items()}
        return kt, tk

    monkeypatch.setattr(org, "_organism_maps", fake_maps)
    rows = list_gene_search_organisms()
    assert rows == [
        ("Akey", "Alpha species Y"),
        ("Zkey", "Zebra species X"),
    ]
