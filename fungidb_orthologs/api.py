"""
REST API for ortholog lookup from FungiDB.

Run: uvicorn fungidb_orthologs.api:app --reload --port 8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from fungidb_orthologs.service import get_orthologs_for_genome

app = FastAPI(
    title="FungiDB ortholog API",
    description="Fetch orthologs from FungiDB for fungal genomes.",
)


class OrthologRequest(BaseModel):
    fasta_path: str = Field(..., description="Path to CDS or protein FASTA")
    organism: str | None = Field(None, description="FungiDB organism key (e.g. AfumigatusA1163)")
    references: list[str] | None = Field(
        None,
        description="Reference genomes (default: CalbicansSC5314, ScerevisiaeS288C, Spombe972h)",
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
            organism=req.organism,
            reference_species=req.references,
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
    fasta_path: str | None = None,
    organism: str | None = None,
):
    """Get orthologs: pass fasta_path (and optionally organism)."""
    if not fasta_path:
        raise HTTPException(400, "Provide fasta_path")
    try:
        path = _resolve_fasta_path(fasta_path)
        df, org = get_orthologs_for_genome(path, organism=organism)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"organism": org, "fasta_path": str(path), "rows": df.to_dict(orient="records"), "count": len(df)}


@app.get("/orthologs/tsv", response_class=PlainTextResponse)
def get_orthologs_tsv(fasta_path: str | None = None, organism: str | None = None):
    """Same as GET /orthologs but returns TSV."""
    if not fasta_path:
        raise HTTPException(400, "Provide fasta_path")
    try:
        path = _resolve_fasta_path(fasta_path)
        df, _ = get_orthologs_for_genome(path, organism=organism)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(404 if "not found" in str(e).lower() else 400, str(e))
    return df.to_csv(sep="\t", index=False)
