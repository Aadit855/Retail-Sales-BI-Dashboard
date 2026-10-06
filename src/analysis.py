"""Compute KPI metrics and write a self-contained HTML dashboard from the marts."""
import json
from pathlib import Path

from build import build

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DASH = ROOT / "dashboard" / "index.html"


def compute(con) -> dict:
    totals = con.execute(
        "SELECT SUM(sales), SUM(profit), SUM(profit)/SUM(sales), COUNT(DISTINCT order_id), COUNT(*) "
        "FROM fact_sales"
    ).fetchone()
    yearly = con.execute(
        "SELECT year, ROUND(sales,2), ROUND(profit,2), ROUND(profit_margin,4), "
        "ROUND(sales_yoy,4) FROM mart_yearly ORDER BY year"
    ).fetchall()
    monthly = con.execute(
        "SELECT year_month, ROUND(sales,2), ROUND(profit,2), ROUND(profit_margin,4) "
        "FROM mart_monthly ORDER BY year_month"
    ).fetchall()
    regions = con.execute(
        "SELECT region, ROUND(sales,2), ROUND(profit,2), ROUND(profit_margin,4) "
        "FROM (SELECT region, SUM(sales) sales, SUM(profit) profit, "
        "SUM(profit)/SUM(sales) profit_margin FROM mart_region_category GROUP BY region) "
        "ORDER BY profit_margin DESC"
    ).fetchall()
    categories = con.execute(
        "SELECT category, ROUND(sales,2), ROUND(profit,2), ROUND(profit_margin,4) "
        "FROM (SELECT category, SUM(sales) sales, SUM(profit) profit, "
        "SUM(profit)/SUM(sales) profit_margin FROM mart_region_category GROUP BY category) "
        "ORDER BY profit DESC"
    ).fetchall()
    discount = con.execute(
        "SELECT discount_band, order_lines, ROUND(profit_margin,4), ROUND(loss_line_share,4) "
        "FROM mart_discount_band ORDER BY discount_band"
    ).fetchall()
    return {
        "total_sales": round(totals[0], 2),
        "total_profit": round(totals[1], 2),
        "profit_margin": round(totals[2], 4),
        "orders": totals[3],
        "order_lines": totals[4],
        "yearly": yearly,
        "monthly": monthly,
        "regions": regions,
        "categories": categories,
        "discount_bands": discount,
    }


def dashboard(metrics: dict) -> str:
    def col(rows, i):
        return json.dumps([r[i] for r in rows])

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Superstore KPI Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{ --ink:#1f2933; --muted:#616e7c; --card:#f5f7fa; --accent:#2a6f97; --bad:#c0392b; }}
  body {{ font-family: system-ui, sans-serif; color: var(--ink); margin: 16px; background:#fff; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color: var(--muted); margin-bottom: 16px; font-size: 14px; }}
  .kpis {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:16px; }}
  .kpi {{ background:var(--card); border-radius:8px; padding:12px; }}
  .kpi .v {{ font-size: 22px; font-weight: 600; }}
  .kpi .l {{ font-size: 12px; color: var(--muted); }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(320px,1fr)); gap:16px; }}
  .card {{ background:#fff; border:1px solid #e4e7eb; border-radius:8px; padding:12px; }}
  .card h2 {{ font-size: 15px; margin: 0 0 8px; }}
  canvas {{ max-height: 280px; }}
</style></head>
<body>
<h1>Superstore sales and profit, 2009–2012</h1>
<div class="sub">Order-line data (Tableau Superstore sample, Canadian regions). Margin = profit ÷ sales.</div>
<div class="kpis">
  <div class="kpi"><div class="v">${metrics['total_sales']:,.0f}</div><div class="l">Sales</div></div>
  <div class="kpi"><div class="v">${metrics['total_profit']:,.0f}</div><div class="l">Profit</div></div>
  <div class="kpi"><div class="v">{metrics['profit_margin']*100:.1f}%</div><div class="l">Profit margin</div></div>
  <div class="kpi"><div class="v">{metrics['orders']:,}</div><div class="l">Orders</div></div>
</div>
<div class="grid">
  <div class="card"><h2>Monthly sales and profit</h2><canvas id="trend"></canvas></div>
  <div class="card"><h2>Profit margin by discount band</h2><canvas id="disc"></canvas></div>
  <div class="card"><h2>Profit margin by region</h2><canvas id="reg"></canvas></div>
  <div class="card"><h2>Profit by category</h2><canvas id="cat"></canvas></div>
</div>
<script>
const M = {json.dumps(metrics['monthly'])};
new Chart(document.getElementById('trend'), {{ type:'line', data:{{
  labels: M.map(r=>r[0]),
  datasets:[{{label:'Sales', data:M.map(r=>r[1]), borderColor:'#2a6f97', tension:.2, pointRadius:0}},
            {{label:'Profit', data:M.map(r=>r[2]), borderColor:'#c0392b', tension:.2, pointRadius:0}}]}},
  options:{{ plugins:{{legend:{{position:'bottom'}}}}, scales:{{x:{{ticks:{{maxTicksLimit:8}}}}}} }} }});
const D = {json.dumps(metrics['discount_bands'])};
new Chart(document.getElementById('disc'), {{ type:'bar', data:{{
  labels: D.map(r=>r[0]),
  datasets:[{{label:'Profit margin', data:D.map(r=>r[2]*100), backgroundColor:D.map(r=>r[2]<0?'#c0392b':'#2a6f97')}}]}},
  options:{{ plugins:{{legend:{{display:false}}}}, scales:{{y:{{title:{{display:true,text:'%'}}}}}} }} }});
const R = {json.dumps(metrics['regions'])};
new Chart(document.getElementById('reg'), {{ type:'bar', data:{{
  labels: R.map(r=>r[0]),
  datasets:[{{label:'Profit margin', data:R.map(r=>r[3]*100), backgroundColor:'#61a5c2'}}]}},
  options:{{ indexAxis:'y', plugins:{{legend:{{display:false}}}}, scales:{{x:{{title:{{display:true,text:'%'}}}}}} }} }});
const C = {json.dumps(metrics['categories'])};
new Chart(document.getElementById('cat'), {{ type:'bar', data:{{
  labels: C.map(r=>r[0]),
  datasets:[{{label:'Profit', data:C.map(r=>r[2]), backgroundColor:'#2a6f97'}}]}},
  options:{{ plugins:{{legend:{{display:false}}}} }} }});
</script>
</body></html>
"""


def main() -> None:
    con = build()
    metrics = compute(con)
    OUT.mkdir(exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
    DASH.parent.mkdir(exist_ok=True)
    DASH.write_text(dashboard(metrics))
    print(json.dumps({k: metrics[k] for k in ("total_sales", "total_profit", "profit_margin", "orders")}, indent=2))
    print("discount bands:", metrics["discount_bands"])


if __name__ == "__main__":
    main()
