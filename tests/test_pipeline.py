"""Reconciliation and metric checks. Run from the project root: python -m pytest -q"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analysis import compute  # noqa: E402
from build import build, read_raw  # noqa: E402


@pytest.fixture(scope="module")
def con(tmp_path_factory):
    return build(tmp_path_factory.mktemp("wh") / "test.duckdb")


def test_row_count_matches_source(con):
    assert con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0] == len(read_raw()) == 8399


def test_row_id_is_unique(con):
    assert con.execute("SELECT COUNT(*) - COUNT(DISTINCT row_id) FROM fact_sales").fetchone()[0] == 0


def test_sales_reconcile_to_source(con):
    source_sales = read_raw()["Sales"].sum()
    fact_sales = con.execute("SELECT SUM(sales) FROM fact_sales").fetchone()[0]
    assert fact_sales == pytest.approx(source_sales, rel=1e-9)


def test_monthly_mart_reconciles_to_fact(con):
    fact = con.execute("SELECT SUM(profit) FROM fact_sales").fetchone()[0]
    mart = con.execute("SELECT SUM(profit) FROM mart_monthly").fetchone()[0]
    assert mart == pytest.approx(fact, rel=1e-9)


def test_all_order_dates_parse(con):
    assert con.execute("SELECT COUNT(*) FROM fact_sales WHERE order_date IS NULL").fetchone()[0] == 0


def test_dimension_keys_are_unique(con):
    assert con.execute(
        "SELECT COUNT(*) - COUNT(DISTINCT product_name) FROM dim_product"
    ).fetchone()[0] == 0
    assert con.execute(
        "SELECT COUNT(*) - COUNT(DISTINCT province) FROM dim_geography"
    ).fetchone()[0] == 0


def test_margin_is_ratio_of_totals(con):
    metrics = compute(con)
    total_sales, total_profit = con.execute(
        "SELECT SUM(sales), SUM(profit) FROM fact_sales"
    ).fetchone()
    assert metrics["profit_margin"] == pytest.approx(total_profit / total_sales, abs=1e-4)


def test_discount_bands_cover_every_line(con):
    assert con.execute(
        "SELECT SUM(order_lines) FROM mart_discount_band"
    ).fetchone()[0] == 8399


def test_yoy_present_for_later_years(con):
    yoy = dict((r[0], r[1]) for r in con.execute("SELECT year, sales_yoy FROM mart_yearly").fetchall())
    assert yoy[2009] is None
    assert yoy[2010] is not None
