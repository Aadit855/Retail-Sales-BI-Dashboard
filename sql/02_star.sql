-- 02_star.sql
-- Star schema: one fact table at order-line grain, with date, product, customer, and geography dimensions.

CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(d AS DATE)                                  AS date_key,
    EXTRACT(year FROM d)::INT                        AS year,
    EXTRACT(quarter FROM d)::INT                     AS quarter,
    EXTRACT(month FROM d)::INT                       AS month,
    strftime(d, '%Y-%m')                             AS year_month
FROM generate_series(
    (SELECT MIN(order_date) FROM stg_order_lines),
    (SELECT MAX(order_date) FROM stg_order_lines),
    INTERVAL 1 DAY
) AS t(d);

CREATE OR REPLACE TABLE dim_product AS
SELECT DISTINCT
    sub_category,
    category,
    product_name
FROM stg_order_lines;

CREATE OR REPLACE TABLE dim_customer AS
SELECT DISTINCT
    customer_name,
    customer_segment
FROM stg_order_lines;

CREATE OR REPLACE TABLE dim_geography AS
SELECT DISTINCT
    province,
    region
FROM stg_order_lines;

CREATE OR REPLACE TABLE fact_sales AS
SELECT
    row_id,
    order_id,
    order_date,
    ship_date,
    product_name,
    customer_name,
    province,
    order_priority,
    ship_mode,
    quantity,
    unit_price,
    sales,
    discount,
    profit,
    shipping_cost
FROM stg_order_lines;
