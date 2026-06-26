"""Ingest the frozen corpus slice into the chunks table.

Two ingestion paths, one provenance contract (ADR 0001 §4):

1. Tabular sources (ONS WAS, HMRC) — rendered to citable text from the
   EXISTING pipelines' processed outputs (automation/data-pipelines/ writes
   projects/wealthlens-dashboard/data/processed/*.csv). One chunk per table
   section/band, carrying period and units, so a citation can say exactly which
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
  genuine zero in the source still renders as "0", and a sub-microunit non-zero
  keeps its value rather than collapsing to "0".
- The honesty filter is an ALLOWLIST (fail-closed): a row is ingested only when
  its data_source marker is a known-official value (e.g. "live"). Anything else
  — an illustrative fallback, an unrecognised marker, a blank, or a missing
  column — is SKIPPED, so the analyst never cites fabricated or unverified
  figures as official facts. (This mirrors the spend cap's fail-closed posture.)

Entrypoint: `make ingest-slice` (fetch -> chunk -> write -> FTS -> embed),
wired in task H1-09.
"""

from __future__ import annotations

import csv
import logging
import math
import os
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

    ``token_count`` is an approximate whitespace word count. Tabular chunks are
    short, so an exact tokenizer is unnecessary here; the document path (H1-08)
    that targets ~500-token chunks introduces a real tokenizer for that column.
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
    section_noun: str  # what a band is, e.g. "wealth decile", "size-of-gain band"
    value_columns: tuple[ValueColumn, ...]
    # access_date mirrors registries/sources.yml; H1-09 will load it from the
    # registry directly (the analyst has no YAML dep yet — see ADR 0001).
    access_date: date
    # Honesty filter (ALLOWLIST, fail-closed). If set, a row is ingested only
    # when row[honesty_flag_column].strip().lower() is in official_markers;
    # everything else (illustrative/unknown/blank/missing) is skipped. None means
    # the table has no honesty flag (it is wholly official, e.g. ONS WAS / HMRC).
    honesty_flag_column: str | None = None
    official_markers: tuple[str, ...] = ("live", "official")


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
        section_noun="size-of-gain band",
        # Figures are PER BAND (incremental for that size-of-gain band), not
        # cumulative — the "£X+" label is HMRC's own band name (built from the
        # band's lower bound), so the labels say "in this band" to stop a reader
        # treating an incremental band share as an "above £X" cumulative one. The
        # cumulative concentration columns (cumul_*_from_top_pct) are intentionally
        # NOT rendered: on the low bands they round to >100%, which reads as an
        # error. Richer band-range labels + a clean cumulative line are seeded as
        # a follow-up in tasks/inbox.md.
        value_columns=(
            ValueColumn("num_taxpayers_thousands", "taxpayers with gains in this band", suffix=" thousand"),
            ValueColumn("total_gains_millions", "total gains in this band", prefix="£", suffix="m"),
            ValueColumn("share_of_gains_pct", "share of all taxable gains in this band", suffix="%"),
            ValueColumn("share_of_taxpayers_pct", "share of all CGT taxpayers in this band", suffix="%"),
        ),
        access_date=date(2026, 5, 16),  # registries/sources.yml: hmrc-cgt-statistics
    ),
    TableSpec(
        source_id="hmrc-tax-receipts",
        csv_name="tax_composition.csv",
        document_id="hmrc-tax-nic-receipts",
        table_label="UK tax and NIC receipts by tax",
        period="HMRC Tax and NIC Receipts, April 2025 edition",
        section_column="year",
        section_noun="financial year",
        # Only the raw HMRC receipt line items are ingested. The work-vs-wealth
        # split (work_pct/wealth_pct) is OUR editorial derivation, not an HMRC
        # figure, so it is deliberately not cited under the HMRC attribution; it
        # can be derived at answer time.
        value_columns=(
            ValueColumn("income_tax_bn", "Income Tax receipts", prefix="£", suffix="bn"),
            ValueColumn("nics_bn", "National Insurance contributions", prefix="£", suffix="bn"),
            ValueColumn("cgt_bn", "Capital Gains Tax receipts", prefix="£", suffix="bn"),
            ValueColumn("iht_bn", "Inheritance Tax receipts", prefix="£", suffix="bn"),
            ValueColumn("sdlt_bn", "Stamp Duty Land Tax receipts", prefix="£", suffix="bn"),
        ),
        access_date=date(2026, 5, 16),  # registries/sources.yml: hmrc-tax-receipts
        # The dashboard pipeline emits data_source="live" for real receipts and
        # "illustrative"/"unknown" for the fallback; only "live" is ingested.
        honesty_flag_column="data_source",
    ),
)


def _clean_number(raw: str | None) -> str | None:
    """Parse one CSV cell into a display number, or None if it is not usable.

    Returns None for blank/missing/non-numeric/non-finite cells so the caller
    OMITS them — a suppressed cell must never become a fabricated 0. A genuine
    "0" parses to "0"; a sub-microunit non-zero keeps its value rather than
    rounding to "0". Float-repr noise (100.10000000000001) is rounded away,
    thousands separators in the input are tolerated, and thousands separators are
    added to the output for readability.
    """
    if raw is None:
        return None
    text = raw.strip().replace(",", "")  # tolerate thousands separators in the source
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    rounded = round(value, 6)  # strip float-repr noise
    if rounded == 0 and value != 0:
        # Genuine sub-microunit non-zero: keep significant figures rather than
        # collapse to "0", which would assert a zero the source did not have.
        return f"{value:g}"
    if rounded == int(rounded):
        return f"{int(rounded):,}"
    return f"{rounded:,}"


def _statement(column: ValueColumn, value: str) -> str:
    """Render one "<label> <prefix><value><suffix>" statistic fragment."""
    return f"{column.label} {column.prefix}{value}{column.suffix}"


def _capitalise_first(text: str) -> str:
    """Upper-case only the first character (str.capitalize lower-cases the rest,
    which would mangle an acronym section_noun like 'IHT band')."""
    return text[:1].upper() + text[1:]


def render_table_chunks(rows: Iterable[Mapping[str, str]], spec: TableSpec) -> list[Chunk]:
    """Render one processed tabular source into citable chunks (one per band).

    Each chunk's text states the table, the period, the band, and every
    available statistic with its units. Missing cells are omitted (never
    fabricated as 0); rows that are not from a known-official data_source are
    skipped (fail-closed). ``span`` is disambiguated if a band label repeats.
    """
    chunks: list[Chunk] = []
    skipped_unofficial = 0
    seen_bands: dict[str, int] = {}
    for row in rows:
        band = (row.get(spec.section_column) or "").strip()
        if not band:
            continue  # not a data row (blank band label)

        if spec.honesty_flag_column is not None:
            marker = (row.get(spec.honesty_flag_column) or "").strip().lower()
            if marker not in spec.official_markers:
                skipped_unofficial += 1
                continue

        statements = [
            _statement(vc, value)
            for vc in spec.value_columns
            if (value := _clean_number(row.get(vc.column))) is not None
        ]
        if not statements:
            continue  # every value in this row was missing/suppressed

        # span pins the exact row; disambiguate if a band label ever repeats so
        # two chunks never share (source_id, document_id, span).
        occurrence = seen_bands.get(band, 0) + 1
        seen_bands[band] = occurrence
        span = f"{spec.section_column}={band}"
        if occurrence > 1:
            span = f"{span}#{occurrence}"

        text = (
            f"{spec.table_label} ({spec.period}). "
            f"{_capitalise_first(spec.section_noun)} {band}: "
            f"{'; '.join(statements)}."
        )
        chunks.append(
            Chunk(
                source_id=spec.source_id,
                document_id=spec.document_id,
                section=f"{spec.table_label}: {band}",
                page=None,
                span=span,
                text=text,
                token_count=len(text.split()),
                access_date=spec.access_date,
            )
        )

    if skipped_unofficial:
        logger.warning(
            "tabular source %s: skipped %d row(s) whose %s was not in %s (not ingested as citable official facts)",
            spec.source_id,
            skipped_unofficial,
            spec.honesty_flag_column,
            spec.official_markers,
        )
    return chunks


def _find_repo_root() -> Path:
    """Locate the repo root (the dir holding both registries/ and projects/).

    WEALTHLENS_REPO_ROOT overrides the search, for non-editable installs where
    the package no longer sits inside the checked-out tree. Otherwise we walk up
    from this module (reliable under the editable install, same approach as the
    sim registry loaders).
    """
    override = os.environ.get("WEALTHLENS_REPO_ROOT")
    if override:
        return Path(override)
    for parent in Path(__file__).resolve().parents:
        if (parent / "registries").is_dir() and (parent / "projects").is_dir():
            return parent
    raise RuntimeError(
        "could not locate repo root (no ancestor has both registries/ and projects/); "
        "set WEALTHLENS_REPO_ROOT to override"
    )


def collect_tabular_chunks(processed_dir: Path | None = None) -> list[Chunk]:
    """Read every tabular-source CSV and render its chunks.

    ``processed_dir`` defaults to the dashboard pipeline output directory. A CSV
    that is absent (the processed outputs are gitignored build artifacts) is
    skipped with a warning rather than failing — the write path (H1-09) decides
    whether an empty slice is acceptable. Files are read as utf-8-sig so a BOM
    (e.g. from a spreadsheet export) does not corrupt the first column header.
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
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
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
