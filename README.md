# Retail Sales KPI Dashboard

**Author:** Aadit Vora

**Role focus:** BI · **Tools:** SQL (DuckDB star schema), Python, HTML dashboard (Chart.js), pytest

> **Business question:** Where is the business making money, and where are sales volume and profit pulling in different directions?

Source: Tableau Superstore order-line sample (8,399 lines, order dates 2009–2012, Canadian provinces as regions). The dataset is a teaching sample, not a real company's data.

## Headline results

| Metric | Value |
|---|---:|
| Sales | **$14.92M** |
| Profit | **$1.52M** |
| Profit margin (profit ÷ sales) | **10.2%** |
| Orders | 5,496 |

**Year over year (sales):** 2010 **−15.7%**, 2011 **−3.2%**, 2012 **+8.2%**. Profit margin slid from 11.1% in 2011 to 9.2% in 2012.

**Furniture is 35% of sales ($5.18M) but earns a 2.3% margin.** Technology (14.8%) and Office Supplies (13.8%) carry the profit.

**Discounts erode profit.** Margin falls from 12.6% on undiscounted lines to 7.9% at 8–10% discount. The share of loss-making lines rises from 46% to 56%.

| Discount band | Order lines | Profit margin | Loss-making lines |
|---|---:|---:|---:|
| 0% | 756 | 12.6% | 46% |
| 1–4% | 3,120 | 12.4% | 47% |
| 5–7% | 2,230 | 8.6% | 52% |
| 8–10% | 2,288 | 7.9% | 56% |
| >10% (5 lines, too few to read) | 5 | n/a | 80% |

Regions: Nunavut has a 2.4% margin on $116K of sales. Northwest Territories has the highest margin at 12.6%.

## Recommendation

1. Review pricing on Furniture. It is the largest category by sales and near break-even on profit.
2. Set a discount guardrail at about 5%. Above that, margin drops sharply and more lines lose money.
3. Track margin, not just sales, as the headline KPI. Sales growth in 2012 came with lower margin.

## Dashboard

Open `dashboard/index.html` in a browser. It is self-contained apart from Chart.js, loaded from a CDN. It shows four KPI tiles and four charts: monthly trend, discount band margin, regional margin, and category profit.

## Method

- `src/build.py` decodes the source (Latin-1 with CR-only line endings, which DuckDB cannot parse) and loads it.
- `sql/01_staging.sql` types the columns and parses dates explicitly.
- `sql/02_star.sql` builds the star schema: `fact_sales` at order-line grain, with date, product, customer, and geography dimensions.
- `sql/03_marts.sql` builds the reporting marts. Margin is always profit ÷ sales, never an average of row margins.
- `tests/test_pipeline.py` checks that sales reconcile to source, the monthly mart reconciles to the fact, keys are unique, and every line is in a discount band.

## Limitations

- Eight thousand lines is a small sample. The discount band above 10% has only 5 lines, so it is not used in the recommendation.
- Descriptive only. Margin differences by category or region do not show cause.
- The source is a sample, and the data ends in 2012.

## Reproduce

```bash
python -m pip install -r requirements.txt
python src/download.py      # downloads and verifies by SHA-256
python src/analysis.py      # builds the warehouse, writes outputs/metrics.json and dashboard/index.html
python -m pytest -q         # 9 tests
```
