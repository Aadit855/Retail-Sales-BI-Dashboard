-- 01_staging.sql
-- Typed order lines. Grain: one row per Row ID (an order line, not an order).
-- Dates are parsed explicitly from the source's US-style m/d/Y text.

CREATE OR REPLACE TABLE stg_order_lines AS
SELECT
    CAST("Row ID" AS INTEGER)                              AS row_id,
    "Order ID"                                             AS order_id,
    strptime("Order Date", '%m/%d/%Y')::DATE               AS order_date,
    strptime("Ship Date", '%m/%d/%Y')::DATE                AS ship_date,
    "Order Priority"                                       AS order_priority,
    "Ship Mode"                                            AS ship_mode,
    "Customer Name"                                        AS customer_name,
    "Customer Segment"                                     AS customer_segment,
    "Province"                                             AS province,
    "Region"                                               AS region,
    "Product Category"                                     AS category,
    "Product Sub-Category"                                 AS sub_category,
    "Product Name"                                         AS product_name,
    CAST("Order Quantity" AS INTEGER)                      AS quantity,
    CAST("Unit Price" AS DOUBLE)                           AS unit_price,
    CAST(Sales AS DOUBLE)                                  AS sales,
    CAST(Discount AS DOUBLE)                               AS discount,
    CAST(Profit AS DOUBLE)                                 AS profit,
    CAST("Shipping Cost" AS DOUBLE)                        AS shipping_cost
FROM raw_orders;
