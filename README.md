# fungidb-orthologs

A pip-installable tool to fetch orthologs from **FungiDB** for fungal genomes. Specify your target genome and the reference genomes from which to extract orthologs (e.g. *Candida albicans*, *Saccharomyces cerevisiae*, *Schizosaccharomyces pombe*).

**Note:** FungiDB only has orthology for genomes already in FungiDB. For truly new genomes not in the database, you would need a local orthology pipeline (e.g. OrthoFinder).

## Prerequisites

- **Python 3.9 or newer** (3.10+ recommended)
- **pip** (Python package installer)

When you install this package with `pip install ...`, the following dependencies are installed automatically:

| Package   | Purpose                    |
|-----------|----------------------------|
| httpx     | HTTP requests to FungiDB   |
| pandas    | Table data and TSV output  |
| biopython | Parse FASTA (locus_tag)    |

**Optional (only if you use the REST API):** `pip install "fungidb-orthologs[api]"` adds FastAPI, Uvicorn, and Pydantic.

**Optional (only if you run tests):** `pip install -e ".[dev]"` adds pytest and pytest-timeout.

## Installation

### For researchers

**Option 1: Install from GitHub**

```bash
pip install git+https://github.com/LiaoLabATDartmouth/fungidb_orthologs.git
```

**Option 2: Clone and install locally**

```bash
git clone https://github.com/LiaoLabATDartmouth/fungidb_orthologs.git
cd fungidb_orthologs
pip install -e .
```

### Optional: API server

```bash
pip install "fungidb-orthologs[api]"
```

### Troubleshooting: `list-organisms` missing or “invalid choice”

`pip` installed the new package, but the name `fungidb-orthologs` on your shell `PATH` may still run a **different, older program** (common on macOS if **Homebrew**’s `/opt/homebrew/bin` comes before pip’s scripts, or if you have several Pythons).

1. **See every candidate on PATH** (zsh/bash):

   ```bash
   type -a fungidb-orthologs
   head -5 "$(which fungidb-orthologs)"
   ```

   If the first hit is not from the `bin` directory of the Python you used for `pip install`, that explains the old `{list-genomes,extract}` menu.

2. **Use the pip-installed CLI under another name** (same code, no name collision):

   ```bash
   fungi-orthologs list-organisms --vocabulary-only
   ```

3. **Or** run via the interpreter you used for `pip install`:

   ```bash
   python -m fungidb_orthologs list-organisms --vocabulary-only
   ```

4. **Fix PATH / remove the impostor:** uninstall an old Homebrew formula if present (`brew list | grep -i fungi`), or put your venv’s `bin` **before** `/opt/homebrew/bin`, or use only a venv for this tool.

5. Prefer a **venv** so `pip install` and the scripts in that venv’s `bin` stay aligned.

## Quick start

### 1. List available genomes

```bash
fungidb-orthologs list-genomes
```

Shows **download index** folder names (~700+), e.g. `AfumigatusA1163`, `CalbicansSC5314`. Not every folder has a gene search entry; see step 1b.

### 1b. List gene-search organisms (GenesByTaxonGene vocabulary)

```bash
fungidb-orthologs list-organisms
```

Prints a TSV with header `key` and `vocabulary_organism`: the short **key** (same style as many `list-genomes` names) and the **exact organism string** FungiDB uses in `GenesByTaxonGene` and in `OrthologsLite` (e.g. `Neurospora crassa OR74A`). Use this when you need the API-facing label or to confirm a genome is queryable via gene search.

```bash
# Only vocabulary strings (one per line)
fungidb-orthologs list-organisms --vocabulary-only

# Only keys (one per line)
fungidb-orthologs list-organisms --keys-only

# Write TSV to a file
fungidb-orthologs list-organisms -o gene_search_organisms.tsv
```

If `fungidb-orthologs` runs an old binary, use **`fungi-orthologs`** (same CLI, different name) or `python -m fungidb_orthologs` (see [Troubleshooting](#troubleshooting-list-organisms-missing-or-invalid-choice)).

### 2. Extract orthologs

References are **never** defaulted: you must pass `-r` / `--references` with at least one genome (see `list-genomes` / `list-organisms`).

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
| `fungidb-orthologs list-genomes` | List download-site genome folder names (~700+) |
| `fungidb-orthologs list-organisms` | List GenesByTaxonGene organism vocabulary (key + API string) |
| `fungi-orthologs …` | Same as above if `fungidb-orthologs` is shadowed on `PATH` |
| `fungidb-orthologs extract` | Extract orthologs from target to reference genomes |

### list-organisms options

| Option | Description |
|--------|-------------|
| `--keys-only` | Print only download-style keys (one per line) |
| `--vocabulary-only` | Print only FungiDB vocabulary organism strings (one per line) |
| `-o`, `--output` | Write to a file instead of stdout |

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
from fungidb_orthologs import (
    list_genomes,
    list_gene_search_organisms,
    get_orthologs_for_genome,
    get_orthologs_by_organism,
)

# Download index folder names
genomes = list_genomes()

# Gene search vocabulary: list of (key, vocabulary_organism_string)
organisms = list_gene_search_organisms()

# By organism key
df = get_orthologs_by_organism(
    target_organism="AfumigatusA1163",
    reference_organisms=["CalbicansSC5314", "ScerevisiaeS288C", "Spombe972h"],
)

# From FASTA (references required; no defaults)
df, organism = get_orthologs_for_genome(
    "query_genomes/A1163_ASM15014v1_cds_from_genomic.fna",
    ["CalbicansSC5314", "ScerevisiaeS288C", "Spombe972h"],
)
```

## REST API (optional)

```bash
pip install "fungidb-orthologs[api]"
uvicorn fungidb_orthologs.api:app --reload --port 8000
```

Then: `POST /orthologs` with JSON including `"fasta_path"`, `"references": ["CalbicansSC5314", ...]` (required), and optional `"organism"`. For GET, pass `fasta_path` and repeat `references` for each reference (e.g. `?references=CalbicansSC5314&references=Spombe972h`).

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
