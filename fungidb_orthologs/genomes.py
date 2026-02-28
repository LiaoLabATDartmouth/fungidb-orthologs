"""
Fetch the list of all available genomes in FungiDB.

Parses the FungiDB downloads directory listing to get organism keys.
"""

from __future__ import annotations

import re

import httpx

FUNGIDB_DOWNLOADS = "https://fungidb.org/common/downloads/Current_Release/"
TIMEOUT = 30


def list_genomes() -> list[str]:
    """
    Fetch and return all FungiDB organism keys (genome identifiers).

    Returns a sorted list of organism keys, e.g. ['AfumigatusA1163', 'CalbicansSC5314', ...].
    """
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(FUNGIDB_DOWNLOADS)
    r.raise_for_status()
    text = r.text
    # Parse Apache-style HTML listing: <a href="AfumigatusA1163/">AfumigatusA1163/</a>
    pattern = re.compile(r'href="([A-Za-z0-9_.-]+)/"')
    organisms = []
    for m in pattern.finditer(text):
        name = m.group(1)
        if name in ("Parent Directory", "Build_number"):
            continue
        organisms.append(name)
    return sorted(set(organisms))
