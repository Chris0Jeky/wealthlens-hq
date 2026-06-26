"""Lock the tabular-chunk format + data-honesty rules (H1-07, ADR 0001 §4).

Pure-Python: no DB, no model calls, no file IO (the renderer takes already-read
rows). Exercises the deterministic rendering the ingestion + eval harness rely
on. Covers: exact chunk format, full per-type provenance (section + span, no
page), units + period in the text, suppressed cells never fabricated as 0,
genuine zeros preserved, illustrative rows skipped, and number formatting.
"""

from __future__ import annotations

from datetime import date

from wealthlens_analyst.ingest.slice_corpus import (
    TABLE_SPECS,
    Chunk,
    _clean_number,
    render_table_chunks,
)

# The real production specs — testing against these locks the shipped format,
# not a throwaway fixture.
_SPECS = {spec.source_id: spec for spec in TABLE_SPECS}
_WAS = _SPECS["ons-was-wealth"]
_CGT = _SPECS["hmrc-cgt-statistics"]
_RECEIPTS = _SPECS["hmrc-tax-receipts"]


def test_was_chunk_format_is_locked() -> None:
    """The WAS renderer emits the exact citable text + provenance we expect."""
    rows = [
        {"decile": "1st (poorest)", "total_wealth_bn": "13.9"},
        {"decile": "10th (wealthiest)", "total_wealth_bn": "5523.0"},
    ]
    chunks = render_table_chunks(rows, _WAS)

    assert len(chunks) == 2
    first = chunks[0]
    assert isinstance(first, Chunk)
    assert first.source_id == "ons-was-wealth"
    assert first.document_id == "was-total-wealth-by-decile"
    assert first.section == "Total household wealth by decile, Great Britain: 1st (poorest)"
    assert first.span == "decile=1st (poorest)"
    assert first.page is None
    assert first.access_date == date(2026, 5, 30)
    assert first.text == (
        "Total household wealth by decile, Great Britain "
        "(ONS Wealth and Assets Survey, April 2020 to March 2022). "
        "Wealth decile 1st (poorest): aggregate total net wealth £13.9bn."
    )
    assert first.token_count == len(first.text.split()) > 0

    # Thousands separator on the large aggregate; units carried.
    assert "£5,523bn" in chunks[1].text


def test_tabular_provenance_invariants_hold_for_every_chunk() -> None:
    """Every tabular chunk satisfies the per-type rule: section + span, no page."""
    rows = [
        {"decile": "5th", "total_wealth_bn": "652.0"},
        {"decile": "6th", "total_wealth_bn": "955.2"},
    ]
    for chunk in render_table_chunks(rows, _WAS):
        assert chunk.source_id
        assert chunk.document_id
        assert chunk.section  # non-empty
        assert chunk.span  # non-empty
        assert chunk.page is None  # tabular sources have no pages
        assert chunk.text
        assert chunk.token_count > 0


def test_suppressed_cell_is_omitted_not_fabricated() -> None:
    """A blank cell is dropped from the text; it never becomes a fabricated 0.

    Mirrors the real HMRC CGT '£3,000+' band, where the taxpayer count and
    taxpayer-share cells are suppressed but the gains figures are present.
    """
    rows = [
        {
            "gain_band": "£3,000+",
            "num_taxpayers_thousands": "",  # suppressed
            "total_gains_millions": "1.0",
            "share_of_gains_pct": "0.0",  # a GENUINE zero
            "share_of_taxpayers_pct": "",  # suppressed
        }
    ]
    (chunk,) = render_table_chunks(rows, _CGT)

    # Present figures appear (genuine zero preserved as "0%").
    assert "total gains £1m" in chunk.text
    assert "share of total gains 0%" in chunk.text
    # Suppressed figures are absent — and never rendered as a fabricated 0.
    assert "number of taxpayers" not in chunk.text
    assert "share of taxpayers" not in chunk.text
    assert "taxpayers 0" not in chunk.text


def test_row_with_every_value_missing_yields_no_chunk() -> None:
    """If a band has no usable figures at all, it produces no chunk (no empty cite)."""
    rows = [
        {
            "gain_band": "£0+",
            "num_taxpayers_thousands": "",
            "total_gains_millions": "",
            "share_of_gains_pct": "",
            "share_of_taxpayers_pct": "",
        }
    ]
    assert render_table_chunks(rows, _CGT) == []


def test_blank_band_label_is_skipped() -> None:
    """Rows with no section label (e.g. spreadsheet footers) are not chunked."""
    rows = [
        {"decile": "", "total_wealth_bn": "1.0"},
        {"decile": "   ", "total_wealth_bn": "2.0"},
        {"decile": "1st (poorest)", "total_wealth_bn": "13.9"},
    ]
    chunks = render_table_chunks(rows, _WAS)
    assert len(chunks) == 1
    assert chunks[0].span == "decile=1st (poorest)"


def test_illustrative_rows_are_not_ingested() -> None:
    """data_source=illustrative rows are skipped; genuine rows still render."""
    rows = [
        {
            "year": "2023-24",
            "income_tax_bn": "270.0",
            "nics_bn": "180.0",
            "cgt_bn": "15.0",
            "iht_bn": "7.5",
            "sdlt_bn": "12.0",
            "work_pct": "92.9",
            "wealth_pct": "7.1",
            "data_source": "illustrative",
        },
        {
            "year": "2024-25",
            "income_tax_bn": "280.0",
            "nics_bn": "185.0",
            "cgt_bn": "16.0",
            "iht_bn": "8.0",
            "sdlt_bn": "13.0",
            "work_pct": "92.5",
            "wealth_pct": "7.5",
            "data_source": "official",  # not an illustrative marker
        },
    ]
    chunks = render_table_chunks(rows, _RECEIPTS)
    # The illustrative row is dropped; only the genuine row survives.
    assert len(chunks) == 1
    assert chunks[0].span == "year=2024-25"
    assert "Income Tax £280bn" in chunks[0].text
    assert "share from taxes on wealth 7.5%" in chunks[0].text


def test_real_tax_composition_is_all_illustrative_today() -> None:
    """The shipped tax_composition data is illustrative, so it yields no chunks.

    Guards the mission rule: the analyst must not cite fabricated figures as
    official HMRC receipts. When the pipeline emits real data this test updates.
    """
    rows = [
        {"year": "2018-19", "income_tax_bn": "191.0", "data_source": "illustrative"},
        {"year": "2023-24", "income_tax_bn": "270.0", "data_source": "illustrative"},
    ]
    assert render_table_chunks(rows, _RECEIPTS) == []


def test_clean_number_formatting_and_missing() -> None:
    """Number cleaning: noise rounded, thousands grouped, missing -> None."""
    assert _clean_number("13.9") == "13.9"
    assert _clean_number("5523.0") == "5,523"  # integral -> grouped int
    assert _clean_number("2645.0") == "2,645"
    assert _clean_number("100.10000000000001") == "100.1"  # float-repr noise rounded
    assert _clean_number("0.0") == "0"  # genuine zero preserved
    assert _clean_number("") is None  # blank -> omit
    assert _clean_number("   ") is None
    assert _clean_number(None) is None
    assert _clean_number("n/a") is None  # non-numeric -> omit
    assert _clean_number("inf") is None  # non-finite -> omit


def test_table_specs_are_wellformed() -> None:
    """Each shipped spec is usable: unique ids, real CSV names, value columns."""
    source_ids = [spec.source_id for spec in TABLE_SPECS]
    assert len(source_ids) == len(set(source_ids))  # unique
    for spec in TABLE_SPECS:
        assert spec.csv_name.endswith(".csv")
        assert spec.value_columns  # at least one statistic to render
        assert spec.section_column
        assert isinstance(spec.access_date, date)
