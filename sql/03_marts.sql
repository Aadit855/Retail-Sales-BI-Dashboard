-- 03_marts.sql
-- Report-ready marts that feed the dashboard. Margin is profit / sales, never an average of row margins.

CREATE OR REPLACE TABLE mart_monthly AS
SELECT
    d.year_month,
    d.year,
    d.month,
    SUM(f.sales)                                     AS sales,
    SUM(f.profit)                                    AS profit,
    SUM(f.profit) / NULLIF(SUM(f.sales), 0)          AS profit_margin,
    COUNT(DISTINCT f.order_id)                       AS orders
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.date_key
GROUP BY ALL
ORDER BY d.year_month;

CREATE OR REPLACE TABLE mart_yearly AS
SELECT
    year,
    SUM(sales)                                       AS sales,
    SUM(profit)                                      AS profit,
    SUM(profit) / NULLIF(SUM(sales), 0)              AS profit_margin,
    SUM(sales) / NULLIF(LAG(SUM(sales)) OVER (ORDER BY year), 0) - 1 AS sales_yoy,
    SUM(orders)                                      AS orders
FROM mart_monthly
GROUP BY year
ORDER BY year;

CREATE OR REPLACE TABLE mart_region_category AS
SELECT
    g.region,
    p.category,
    SUM(f.sales)                                     AS sales,
    SUM(f.profit)                                    AS profit,
    SUM(f.profit) / NULLIF(SUM(f.sales), 0)          AS profit_margin
FROM fact_sales f
JOIN dim_geography g USING (province)
JOIN dim_product p USING (product_name)
GROUP BY ALL;

CREATE OR REPLACE TABLE mart_discount_band AS
SELECT
    CASE
        WHEN discount = 0        THEN '0%'
        WHEN discount <= 0.04    THEN '1-4%'
        WHEN discount <= 0.07    THEN '5-7%'
        WHEN discount <= 0.10    THEN '8-10%'
        ELSE '>10% (few lines)'
    END                                              AS discount_band,
    COUNT(*)                                         AS order_lines,
    SUM(sales)                                       AS sales,
    SUM(profit)                                      AS profit,
    SUM(profit) / NULLIF(SUM(sales), 0)              AS profit_margin,
    AVG((profit < 0)::INT)                           AS loss_line_share
FROM fact_sales
GROUP BY discount_band;
