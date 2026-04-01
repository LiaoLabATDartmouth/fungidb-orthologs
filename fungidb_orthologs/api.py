"""
REST API for ortholog lookup from FungiDB.

Run: uvicorn fungidb_orthologs.api:app --reload --port 8000
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from fungidb_orthologs.service import get_orthologs_for_genome

app = FastAPI(
    title="FungiDB ortholog API",
    description="Fetch orthologs from FungiDB for fungal genomes.",
)


class OrthologRequest(BaseModel):
    fasta_path: str = Field(..., description="Path to CDS or protein FASTA")
    organism: Optional[str] = Field(None, description="FungiDB organism key (e.g. AfumigatusA1163)")
    references: list[str] = Field(
        ...,
        min_length=1,
        description="Reference genome keys (at least one), same as CLI --references",
    )


@app.get("/")
def root():
    return {
        "message": "FungiDB ortholog API",
        "docs": "/docs",
        "orthologs": "POST /orthologs or GET /orthologs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/genomes")
def genomes():
    """List available FungiDB genomes."""
    from fungidb_orthologs.genomes import list_genomes
    return {"genomes": list_genomes()}


def _resolve_fasta_path(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.exists():
        raise HTTPException(404, f"FASTA file not found: {path}")
    return p


@app.post("/orthologs")
def post_orthologs(req: OrthologRequest):
    """Get orthologs for genes in the given genome FASTA."""
    try:
        fasta_path = _resolve_fasta_path(req.fasta_path)
        df, organism = get_orthologs_for_genome(
            fasta_path,
            req.references,
            organism=req.organism,
        )
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "organism": organism,
        "fasta_path": str(fasta_path),
        "rows": df.to_dict(orient="records"),
        "count": len(df),
    }


@app.get("/orthologs")
def get_orthologs(
    fasta_path: str,
    references: list[str] = Query(
        ...,
        min_length=1,
        description="Reference genome keys (repeat param for multiple)",
    ),
    organism: Optional[str] = None,
):
    """Get orthologs: pass fasta_path, references (one or more), and optionally organism."""
    try:
        path = _resolve_fasta_path(fasta_path)
        df, org = get_orthologs_for_genome(path, references, organism=organism)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"organism": org, "fasta_path": str(path), "rows": df.to_dict(orient="records"), "count": len(df)}


@app.get("/orthologs/tsv", response_class=PlainTextResponse)
def get_orthologs_tsv(
    fasta_path: str,
    references: list[str] = Query(..., min_length=1),
    organism: Optional[str] = None,
):
    """Same as GET /orthologs but returns TSV."""
    try:
        path = _resolve_fasta_path(fasta_path)
        df, _ = get_orthologs_for_genome(path, references, organism=organism)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(404 if "not found" in str(e).lower() else 400, str(e))
    return df.to_csv(sep="\t", index=False)
