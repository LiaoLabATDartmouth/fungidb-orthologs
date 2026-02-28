# fungidb-orthologs

A pip-installable tool to fetch orthologs from **FungiDB** for fungal genomes. Specify your target genome and the reference genomes from which to extract orthologs (e.g. *Candida albicans*, *Saccharomyces cerevisiae*, *Schizosaccharomyces pombe*).

**Note:** FungiDB only has orthology for genomes already in FungiDB. For truly new genomes not in the database, you would need a local orthology pipeline (e.g. OrthoFinder).

## Installation

### For lab members

**Option 1: Install from GitHub** (after pushing to your lab's repo)

```bash
pip install git+https://github.com/YOUR-LAB-ORG/fungidb-orthologs.git
```

**Option 2: Clone and install locally**

```bash
git clone https://github.com/YOUR-LAB-ORG/fungidb-orthologs.git
cd fungidb-orthologs
pip install -e .
```

Replace `YOUR-LAB-ORG` with your lab's GitHub organization or username.

### Optional: API server

```bash
pip install "fungidb-orthologs[api]"
```

## Quick start

### 1. List available genomes

```bash
fungidb-orthologs list-genomes
```

Shows all ~700+ FungiDB genomes (e.g. `AfumigatusA1163`, `CalbicansSC5314`, `ScerevisiaeS288C`, `Spombe972h`).

### 2. Extract orthologs

**By organism key** (no FASTA needed):

```bash
fungidb-orthologs extract \
  --target AfumigatusA1163 \
  --references CalbicansSC5314 ScerevisiaeS288C Spombe972h \
  -o orthologs.tsv
```

**From a FASTA file** (organism inferred from locus_tag):

```bash
fungidb-orthologs extract \
  --fasta query_genomes/A1163_ASM15014v1_cds_from_genomic.fna \
  --references CalbicansSC5314 ScerevisiaeS288C Spombe972h \
  -o orthologs.tsv
```

## Usage

| Command | Description |
|---------|-------------|
| `fungidb-orthologs list-genomes` | List all available FungiDB genomes |
| `fungidb-orthologs extract` | Extract orthologs from target to reference genomes |

### Extract options

| Option | Description |
|--------|-------------|
| `--target`, `-t` | Target genome (FungiDB organism key). Required if `--fasta` not given. |
| `--references`, `-r` | Reference genomes (one or more). **Required.** |
| `--fasta`, `-f` | Path to CDS/protein FASTA. Organism can be inferred from locus_tag. |
| `-o`, `--output` | Write results to TSV file. |

### Example: A1163 → C. albicans, S. cerevisiae, S. pombe

```bash
fungidb-orthologs extract \
  -t AfumigatusA1163 \
  -r CalbicansSC5314 ScerevisiaeS288C Spombe972h \
  -o a1163_orthologs.tsv
```

## Python API

```python
from fungidb_orthologs import list_genomes, get_orthologs_for_genome, get_orthologs_by_organism

# List genomes
genomes = list_genomes()

# By organism key
df = get_orthologs_by_organism(
    target_organism="AfumigatusA1163",
    reference_organisms=["CalbicansSC5314", "ScerevisiaeS288C", "Spombe972h"],
)

# From FASTA
df, organism = get_orthologs_for_genome(
    "query_genomes/A1163_ASM15014v1_cds_from_genomic.fna",
    reference_species=["CalbicansSC5314", "ScerevisiaeS288C", "Spombe972h"],
)
```

## REST API (optional)

```bash
pip install "fungidb-orthologs[api]"
uvicorn fungidb_orthologs.api:app --reload --port 8000
```

Then: `POST /orthologs` with `{"fasta_path": "...", "organism": "AfumigatusA1163"}` or `GET /orthologs?fasta_path=...`

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v --timeout=300
```

The ortholog test hits the FungiDB API and can take 1–2 minutes.

## Data source

Orthology data comes from **FungiDB** (OrthoMCL), via the record table API (`OrthologsLite`).

## License

MIT
