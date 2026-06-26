"""Ingest the frozen corpus slice into the chunks table.

Two ingestion paths, one provenance contract (ADR 0001 §4):

1. Tabular sources (ONS WAS, HMRC) — rendered to citable text from the
   EXISTING pipelines' processed outputs (automation/data-pipelines/ writes
   projects/wealthlens-dashboard/data/processed/*.csv). One chunk per table
   section/band, carrying year and units, so a citation can say exactly which
   statistic backed a claim. Implemented here (task H1-07).
2. Report documents (IFS/RF PDFs from fetch_documents.py) — page-aware
   extraction, ~500-token heading-anchored chunks with page + span recorded.
   Pending task H1-08.

Every chunk row carries source_id (registries/sources.yml id), document_id,
section, page, span. The per-type rule (tabular: section + span, no page;
document: page + span) is enforced at write time (task H1-09); the renderers
here always emit conformant chunks.

Data-honesty guardrails baked into the tabular renderer:
- A missing/suppressed cell is OMITTED, never rendered as a fabricated 0. A
  genuine zero in the source still renders as "0".
- Rows flagged as illustrative (a data_source marker the dashboard pipelines
  set when they fall back to non-official figures) are SKIPPED, so the analyst
  never cites fabricated statistics as official facts.

Entrypoint: `make ingest-slice` (fetch -> chunk -> write -> FTS -> embed),
wired in task H1-09.
"""

from __future__ import annotations

import csv
import logging
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Chunk:
    """A corpus chunk with ingestion-time provenance (mirrors the chunks table).

    The provenance fields map 1:1 onto the chunks columns (migration
    0001_chunks). For tabular chunks ``section`` and ``span`` are always set and
    ``page`` is always None; the write path (H1-09) enforces that per-type rule.
    """

    source_id: str  # registries/sources.yml id — the citation root
    document_id: str  # stable id of the table/document within the source
    section: str | None
    page: int | None
    span: str | None
    text: str
    token_count: int
    access_date: date


@dataclass(frozen=True)
class ValueColumn:
    """One statistic column to render, with its human label and units.

    ``prefix``/``suffix`` carry their own spacing so the rendered figure reads
    naturally: a currency column uses prefix="£", suffix="bn" ("£13.9bn"); a
    percentage uses suffix="%" ("0.7%"); a word unit uses a leading-space suffix
    (" thousand" -> "61 thousand").
    """

    column: str
    label: str
    prefix: str = ""
    suffix: str = ""


@dataclass(frozen=True)
class TableSpec:
    """How to render one processed tabular source into citable chunks."""

    source_id: str
    csv_name: str  # processed CSV under projects/wealthlens-dashboard/data/processed/
    document_id: str
    table_label: str  # human table name, used in the chunk text and section
    period: str  # the period/edition the table covers, surfaced in every citation
    section_column: str  # the column whose value names each band/section
    section_noun: str  # what a band is, e.g. "wealth decile", "gain band"
    value_columns: tuple[ValueColumn, ...]
    # access_date mirrors registries/sources.yml; H1-09 will load it from the
    # registry directly (the analyst has no YAML dep yet — see ADR 0001).
    access_date: date
    # Rows whose honesty_flag_column value is an illustrative marker are skipped
    # (never ingested as citable facts). None means "no honesty flag on this table".
    honesty_flag_column: str | None = None
    illustrative_markers: tuple[str, ...] = ("illustrative",)


# The frozen tabular slice: the analyst_corpus tabular sources in
# registries/sources.yml, each mapped to its existing processed pipeline output.
TABLE_SPECS: tuple[TableSpec, ...] = (
    TableSpec(
        source_id="ons-was-wealth",
        csv_name="ons_wealth_by_decile.csv",
        document_id="was-total-wealth-by-decile",
        table_label="Total household wealth by decile, Great Britain",
        period="ONS Wealth and Assets Survey, April 2020 to March 2022",
        section_column="decile",
        section_noun="wealth decile",
        value_columns=(ValueColumn("total_wealth_bn", "aggregate total net wealth", prefix="£", suffix="bn"),),
        access_date=date(2026, 5, 30),  # registries/sources.yml: ons-was-wealth
    ),
    TableSpec(
        source_id="hmrc-cgt-statistics",
        csv_name="hmrc_cgt_concentration.csv",
        document_id="hmrc-cgt-size-of-gain",
        table_label="Capital Gains Tax by size of gain",
        period="HMRC Capital Gains Tax statistics, 2025 edition",
        section_column="gain_band",
        section_noun="gain band",
        value_columns=(
            ValueColumn("num_taxpayers_thousands", "number of taxpayers", suffix=" thousand"),
            ValueColumn("total_gains_millions", "total gains", prefix="£", suffix="m"),
            ValueColumn("share_of_gains_pct", "share of total gains", suffix="%"),
            ValueColumn("share_of_taxpayers_pct", "share of taxpayers", suffix="%"),
        ),
        access_date=date(2026, 5, 16),  # registries/sources.yml: hmrc-cgt-statistics
    ),
    TableSpec(
        source_id="hmrc-tax-receipts",
        csv_name="tax_composition.csv",
        document_id="hmrc-tax-nic-receipts",
        table_label="UK tax receipts, taxes on work vs taxes on wealth",
        period="HMRC Tax and NIC Receipts, April 2025 edition",
        section_column="year",
        section_noun="financial year",
        value_columns=(
            ValueColumn("income_tax_bn", "Income Tax", prefix="£", suffix="bn"),
            ValueColumn("nics_bn", "National Insurance contributions", prefix="£", suffix="bn"),
            ValueColumn("cgt_bn", "Capital Gains Tax", prefix="£", suffix="bn"),
            ValueColumn("iht_bn", "Inheritance Tax", prefix="£", suffix="bn"),
            ValueColumn("sdlt_bn", "Stamp Duty Land Tax", prefix="£", suffix="bn"),
            ValueColumn("work_pct", "share from taxes on work", suffix="%"),
            ValueColumn("wealth_pct", "share from taxes on wealth", suffix="%"),
        ),
        access_date=date(2026, 5, 16),  # registries/sources.yml: hmrc-tax-receipts
        # The dashboard pipeline currently emits illustrative figures here; those
        # rows are skipped so the analyst never cites them as official HMRC data.
        honesty_flag_column="data_source",
    ),
)


def _clean_number(raw: str | None) -> str | None:
    """Parse one CSV cell into a display number, or None if it is not usable.

    Returns None for blank/missing/non-numeric/non-finite cells so the caller
    OMITS them — a suppressed cell must never become a fabricated 0. A genuine
    "0" parses to "0". Float-repr noise (100.10000000000001) is rounded away,
    and thousands separators are added for readability.
    """
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    value = round(value, 6)
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,}"


def _statement(column: ValueColumn, value: str) -> str:
    """Render one "<label> <prefix><value><suffix>" statistic fragment."""
    return f"{column.label} {column.prefix}{value}{column.suffix}"


def render_table_chunks(rows: Iterable[Mapping[str, str]], spec: TableSpec) -> list[Chunk]:
    """Render one processed tabular source into citable chunks (one per band).

    Each chunk's text states the table, the period, the band, and every
    available statistic with its units. Missing cells are omitted (never
    fabricated as 0); illustrative-flagged rows are skipped entirely.
    """
    chunks: list[Chunk] = []
    skipped_illustrative = 0
    for row in rows:
        band = (row.get(spec.section_column) or "").strip()
        if not band:
            continue  # not a data row (blank band label)

        if spec.honesty_flag_column is not None:
            flag = (row.get(spec.honesty_flag_column) or "").strip().lower()
            if flag in spec.illustrative_markers:
                skipped_illustrative += 1
                continue

        statements = [
            _statement(vc, value)
            for vc in spec.value_columns
            if (value := _clean_number(row.get(vc.column))) is not None
        ]
        if not statements:
            continue  # every value in this row was missing/suppressed

        text = f"{spec.table_label} ({spec.period}). {spec.section_noun.capitalize()} {band}: {'; '.join(statements)}."
        chunks.append(
            Chunk(
                source_id=spec.source_id,
                document_id=spec.document_id,
                section=f"{spec.table_label}: {band}",
                page=None,
                span=f"{spec.section_column}={band}",
                text=text,
                token_count=len(text.split()),
                access_date=spec.access_date,
            )
        )

    if skipped_illustrative:
        logger.warning(
            "tabular source %s: skipped %d illustrative row(s) (not ingested as citable facts)",
            spec.source_id,
            skipped_illustrative,
        )
    return chunks


def _find_repo_root() -> Path:
    """Walk up from this module to the repo root (where registries/ + projects/ live).

    The editable install keeps the package in the checked-out tree, so resolving
    repo-relative paths by walking up is reliable (same approach as the sim
    registry loaders).
    """
    for parent in Path(__file__).resolve().parents:
        if (parent / "registries").is_dir() and (parent / "projects").is_dir():
            return parent
    raise RuntimeError("could not locate repo root (no ancestor has both registries/ and projects/)")


def collect_tabular_chunks(processed_dir: Path | None = None) -> list[Chunk]:
    """Read every tabular-source CSV and render its chunks.

    ``processed_dir`` defaults to the dashboard pipeline output directory. A CSV
    that is absent (the processed outputs are gitignored build artifacts) is
    skipped with a warning rather than failing — the write path (H1-09) decides
    whether an empty slice is acceptable.
    """
    if processed_dir is None:
        processed_dir = _find_repo_root() / "projects" / "wealthlens-dashboard" / "data" / "processed"

    chunks: list[Chunk] = []
    for spec in TABLE_SPECS:
        csv_path = processed_dir / spec.csv_name
        if not csv_path.is_file():
            logger.warning(
                "tabular source %s: %s not found, skipping (regenerate via the pipeline)",
                spec.source_id,
                csv_path.name,
            )
            continue
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rendered = render_table_chunks(rows, spec)
        logger.info("tabular source %s: %d chunk(s) from %d row(s)", spec.source_id, len(rendered), len(rows))
        chunks.extend(rendered)
    return chunks


def ingest_slice() -> int:
    """Run the full slice ingestion; return the number of chunks written.

    Tabular rendering is available via collect_tabular_chunks() (H1-07); the PDF
    path (H1-08) and the write/FTS/embed wiring (H1-09) complete this.
    """
    raise NotImplementedError("H1-08/H1-09: PDF chunking + write/FTS/embed wiring not yet implemented")


def main() -> None:
    """CLI entrypoint for `make ingest-slice`."""
    raise NotImplementedError("H1-09: ingestion CLI not yet implemented")


if __name__ == "__main__":
    main()
