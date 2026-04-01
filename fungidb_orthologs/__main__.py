"""Allow: python -m fungidb_orthologs list-organisms ... (uses that interpreter's install)."""

from fungidb_orthologs.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
