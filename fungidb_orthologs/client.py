"""
FungiDB API client for ortholog data.

Uses the same record table API as the EuPathDB R package.
"""

from __future__ import annotations

import io
import json

import httpx
import pandas as pd

from fungidb_orthologs.config import FUNGIDB_ORGANISMS

FUNGIDB_BASE = "https://fungidb.org/fungidb"
REPORT_URL = f"{FUNGIDB_BASE}/service/record-types/gene/searches/GenesByTaxonGene/reports/tableTabular"
TIMEOUT = 300  # ortholog table can be large


def _organism_for_api(organism: str) -> str:
    """Use full display name for API if we have it."""
    return FUNGIDB_ORGANISMS.get(organism, organism)


def fetch_ortholog_table(organism: str) -> pd.DataFrame:
    """
    Fetch the OrthologsLite table for a FungiDB organism.

    organism: FungiDB organism key, e.g. "AfumigatusA1163", "CalbicansSC5314".
    Returns DataFrame with columns like GID, ORTHOLOGS_GID, ORTHOLOGS_ORGANISM, ORTHOLOGS_PRODUCT.
    """
    api_organism = _organism_for_api(organism)
    body = {
        "searchConfig": {
            "parameters": {"organism": api_organism},
            "wdkWeight": 10,
        },
        "reportConfig": {
            "tables": ["OrthologsLite"],
            "includeHeader": True,
            "attachmentType": "csv",
        },
    }
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(
            REPORT_URL,
            content=json.dumps(body),
            headers={"Content-Type": "application/json"},
        )
    if r.status_code == 422:
        raise ValueError(
            f"FungiDB returned 422 for organism {organism!r}. "
            "Try the full name or run 'fungidb-orthologs list-genomes' to see valid keys."
        )
    r.raise_for_status()
    csv_text = r.text
    # Handle embedded commas in product descriptions
    df = pd.read_csv(
        io.StringIO(csv_text),
        quoting=1,  # QUOTE_ALL
        on_bad_lines="skip",
    )
    df.columns = (
        df.columns.str.upper()
        .str.replace(r"\.$", "", regex=True)
        .str.replace(".", "_", regex=False)
        .str.replace(" ", "_", regex=False)
    )
    if "GID" not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: "GID"})
    # Normalize to expected column names (API may use ORTHOLOG/ORGANISM vs ORTHOLOGS_GID/ORTHOLOGS_ORGANISM)
    renames = {}
    if "ORTHOLOG" in df.columns and "ORTHOLOGS_GID" not in df.columns:
        renames["ORTHOLOG"] = "ORTHOLOGS_GID"
    if "ORGANISM" in df.columns and "ORTHOLOGS_ORGANISM" not in df.columns:
        renames["ORGANISM"] = "ORTHOLOGS_ORGANISM"
    if "PRODUCT" in df.columns and "ORTHOLOGS_PRODUCT" not in df.columns:
        renames["PRODUCT"] = "ORTHOLOGS_PRODUCT"
    if renames:
        df = df.rename(columns=renames)
    return df


def filter_orthologs_to_references(
    ortholog_df: pd.DataFrame,
    reference_organisms: list[str],
) -> pd.DataFrame:
    """Keep only ortholog rows for the specified reference species."""
    org_col = "ORTHOLOGS_ORGANISM"
    if org_col not in ortholog_df.columns:
        return ortholog_df
    allowed = set(reference_organisms)
    for key in reference_organisms:
        if key in FUNGIDB_ORGANISMS:
            allowed.add(FUNGIDB_ORGANISMS[key])
    return ortholog_df[
        ortholog_df[org_col].astype(str).str.strip().isin(allowed)
    ].copy()


def get_orthologs_for_genes(
    organism: str,
    gene_ids: list[str] | None = None,
    reference_organisms: list[str] | None = None,
) -> pd.DataFrame:
    """
    Get orthologs for an organism, optionally restricted to given gene IDs and reference species.
    """
    from fungidb_orthologs.config import DEFAULT_REFERENCE_SPECIES

    df = fetch_ortholog_table(organism)
    refs = reference_organisms or DEFAULT_REFERENCE_SPECIES
    df = filter_orthologs_to_references(df, refs)
    if gene_ids is not None:
        df = df[df["GID"].astype(str).isin(set(str(g) for g in gene_ids))].copy()
    return df.reset_index(drop=True)
