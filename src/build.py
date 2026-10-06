"""Normalize the raw Superstore CSV, load it into DuckDB, and build the star schema and marts.

The source file is Latin-1 with CR-only line endings, which DuckDB cannot parse directly,
so it is decoded and re-read in Python first. Nothing else about the data is altered here.
"""
import io
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "superstoreSales.csv"
DB = ROOT / "warehouse" / "superstore.duckdb"


def read_raw() -> pd.DataFrame:
    text = RAW.read_bytes().decode("latin-1").replace("\r\n", "\n").replace("\r", "\n")
    return pd.read_csv(io.StringIO(text))


def build(db_path: Path = DB) -> duckdb.DuckDBPyConnection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    raw = read_raw()
    con.register("raw_df", raw)
    con.execute("CREATE OR REPLACE TABLE raw_orders AS SELECT * FROM raw_df")
    for sql_file in ("01_staging.sql", "02_star.sql", "03_marts.sql"):
        con.execute((ROOT / "sql" / sql_file).read_text())
    return con


if __name__ == "__main__":
    con = build()
    n = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    print(f"Built {DB.relative_to(ROOT)} with {n:,} order lines")
