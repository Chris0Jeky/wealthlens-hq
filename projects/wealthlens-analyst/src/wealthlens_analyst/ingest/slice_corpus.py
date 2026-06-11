"""Ingest the frozen corpus slice into the chunks table.

Two ingestion paths, one provenance contract (ADR 0001 §4):

1. Tabular sources (ONS WAS, HMRC) — rendered to citable text from the
   EXISTING pipelines' processed outputs (automation/data-pipelines/ writes
   projects/wealthlens-dashboard/data/processed/*.csv with .meta.json
   provenance sidecars). One chunk per table section/band, carrying year and
   units, so a citation can say exactly which statistic backed a claim.
2. Report documents (IFS/RF PDFs from fetch_documents.py) — page-aware
   extraction, ~500-token heading-anchored chunks with page + span recorded.

Every chunk row carries source_id (registries/sources.yml id), document_id,
section, page, span. Null provenance fails ingestion — enforced, not advised.

Entrypoint: `make ingest-slice` (fetch -> chunk -> write -> FTS -> embed).

Pending: tasks H1-07 (tabular), H1-08 (PDF), H1-09 (integrity gate) in
tasks/hero1-backlog.md.
"""

from __future__ import annotations


def ingest_slice() -> int:
    """Run the full slice ingestion; return the number of chunks written."""
    raise NotImplementedError("H1-07..H1-09: slice ingestion not yet implemented")


def main() -> None:
    """CLI entrypoint for `make ingest-slice`."""
    raise NotImplementedError("H1-09: ingestion CLI not yet implemented")


if __name__ == "__main__":
    main()
