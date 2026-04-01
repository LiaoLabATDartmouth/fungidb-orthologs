"""
Command-line interface for fungidb-orthologs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_list_genomes(args: argparse.Namespace) -> int:
    """List all available FungiDB genomes."""
    from fungidb_orthologs.genomes import list_genomes

    try:
        genomes = list_genomes()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    for g in genomes:
        print(g)
    print(f"\nTotal: {len(genomes)} genomes", file=sys.stderr)
    return 0


def cmd_list_organisms(args: argparse.Namespace) -> int:
    """List GenesByTaxonGene organism vocabulary (keys and API strings)."""
    from fungidb_orthologs.organisms import list_gene_search_organisms

    try:
        rows = list_gene_search_organisms()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    lines: list[str] = []
    if args.keys_only:
        lines = [k for k, _ in rows]
    elif args.vocabulary_only:
        lines = [t for _, t in rows]
    else:
        lines = ["key\tvocabulary_organism"]
        lines.extend(f"{k}\t{t}" for k, t in rows)

    text = "\n".join(lines) + ("\n" if lines else "")
    out = args.output
    if out:
        Path(out).write_text(text)
        print(f"Wrote {len(rows)} organisms to {out}", file=sys.stderr)
    else:
        sys.stdout.write(text)

    if not out:
        print(f"\nTotal: {len(rows)} organisms (GenesByTaxonGene vocabulary)", file=sys.stderr)
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    """Extract orthologs for a target genome from reference genomes."""
    from fungidb_orthologs.service import get_orthologs_for_genome
    from fungidb_orthologs.service import get_orthologs_by_organism

    target = args.target
    references = args.references
    fasta_path = args.fasta_path
    output = args.output

    if not references:
        print("Error: Specify at least one reference genome with --references", file=sys.stderr)
        return 1

    try:
        if fasta_path:
            path = Path(fasta_path)
            if not path.is_absolute():
                path = Path.cwd() / path
            if not path.exists():
                print(f"Error: FASTA not found: {fasta_path}", file=sys.stderr)
                return 1
            df, organism = get_orthologs_for_genome(
                path,
                references,
                organism=target,
            )
            print(f"Target organism (from FASTA): {organism}", file=sys.stderr)
        else:
            if not target:
                print("Error: Specify --target when not using --fasta", file=sys.stderr)
                return 1
            df = get_orthologs_by_organism(
                target_organism=target,
                reference_organisms=references,
            )
            organism = target

        print(f"Reference genomes: {', '.join(references)}", file=sys.stderr)
        print(f"Ortholog rows: {len(df)}", file=sys.stderr)

        if output:
            Path(output).write_text(df.to_csv(sep="\t", index=False))
            print(f"Wrote {output}", file=sys.stderr)
        else:
            print(df.to_csv(sep="\t", index=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="fungidb-orthologs",
        description="Fetch orthologs from FungiDB for fungal genomes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list-genomes
    p_list = sub.add_parser("list-genomes", help="List all available FungiDB genomes")
    p_list.set_defaults(func=cmd_list_genomes)

    # list-organisms
    p_org = sub.add_parser(
        "list-organisms",
        help="List GenesByTaxonGene organism vocabulary (download keys and API strings)",
    )
    fmt = p_org.add_mutually_exclusive_group()
    fmt.add_argument(
        "--keys-only",
        action="store_true",
        help="Print only download-style keys (one per line)",
    )
    fmt.add_argument(
        "--vocabulary-only",
        action="store_true",
        help="Print only FungiDB vocabulary organism strings (one per line)",
    )
    p_org.add_argument(
        "-o",
        "--output",
        help="Write output to a file instead of stdout",
    )
    p_org.set_defaults(func=cmd_list_organisms)

    # extract
    p_extract = sub.add_parser(
        "extract",
        help="Extract orthologs from target genome to reference genomes",
    )
    p_extract.add_argument(
        "--target",
        "-t",
        help="Target genome (FungiDB organism key, e.g. AfumigatusA1163). Required if --fasta not given.",
    )
    p_extract.add_argument(
        "--references",
        "-r",
        nargs="+",
        help="Reference genomes to extract orthologs from (e.g. CalbicansSC5314 ScerevisiaeS288C Spombe972h)",
    )
    p_extract.add_argument(
        "--fasta",
        "-f",
        dest="fasta_path",
        help="Path to CDS/protein FASTA. If given, target organism can be inferred from locus_tag.",
    )
    p_extract.add_argument(
        "-o",
        "--output",
        help="Write results to TSV file",
    )
    p_extract.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    return args.func(args)
