"""Species and FungiDB organism mapping for ortholog search."""

# Common FungiDB organism keys and their full display names (for API)
# See https://fungidb.org/common/downloads/Current_Release/
FUNGIDB_ORGANISMS = {
    "AfumigatusA1163": "Aspergillus fumigatus A1163",
    "AfumigatusAf293": "Aspergillus fumigatus Af293",
    "CalbicansSC5314": "Candida albicans SC5314",
    "ScerevisiaeS288C": "Saccharomyces cerevisiae S288C",
    "Spombe972h": "Schizosaccharomyces pombe 972h",
}

# Default reference species for ortholog extraction
DEFAULT_REFERENCE_SPECIES = [
    "CalbicansSC5314",   # Candida albicans
    "ScerevisiaeS288C",  # S. cerevisiae
    "Spombe972h",        # S. pombe
]


def get_fungidb_organism_key(name: str) -> str | None:
    """Resolve a name (e.g. 'A. fumigatus A1163', 'AfumigatusA1163') to FungiDB key."""
    name = (name or "").strip()
    if not name:
        return None
    if name in FUNGIDB_ORGANISMS:
        return name
    key_like = name.replace(" ", "").replace(".", "").lower()
    for key in FUNGIDB_ORGANISMS:
        if key.replace(" ", "").lower() == key_like:
            return key
    return None
