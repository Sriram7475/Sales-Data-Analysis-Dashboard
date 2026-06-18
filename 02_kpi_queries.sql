/*==============================================================
  Advanced KPI Queries - CTEs, Window Functions, Multi-table Joins
==============================================================*/

/* 1. Monthly revenue, orders, units, AOV */
WITH monthly_sales AS (
    SELECT
        d.[year],
        d.month_num,
        d.month_name,
        SUM(f.revenue) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders,
        SUM(f.quantity) AS total_units
    FROM dbo.fact_sales f
    INNER JOIN dbo.dim_date d
        ON f.date_key = d.date_key
    GROUP BY d.[year], d.month_num, d.month_name
)
SELECT
    [year],
    month_num,
    month_name,
    total_revenue,
    total_orders,
    total_units,
    CAST(total_revenue / NULLIF(total_orders, 0) AS DECIMAL(12,2)) AS avg_order_value
FROM monthly_sales
ORDER BY [year], month_num;

/* 2. Monthly trend with previous month and growth rate */
WITH monthly_revenue AS (
    SELECT
        d.[year],
        d.month_num,
        CONCAT(d.[year], '-', RIGHT('00' + CAST(d.month_num AS VARCHAR(2)), 2)) AS year_month,
        SUM(f.revenue) AS revenue
    FROM dbo.fact_sales f
    INNER JOIN dbo.dim_date d
        ON f.date_key = d.date_key
    GROUP BY d.[year], d.month_num
)
SELECT
    year_month,
    revenue,
    LAG(revenue) OVER (ORDER BY [year], month_num) AS previous_month_revenue,
    CAST(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY [year], month_num))
        / NULLIF(LAG(revenue) OVER (ORDER BY [year], month_num), 0)
        AS DECIMAL(10,2)
    ) AS mom_growth_pct
FROM monthly_revenue
ORDER BY [year], month_num;

/* 3. Category contribution and ranking */
WITH category_sales AS (
    SELECT
        p.category,
        SUM(f.revenue) AS category_revenue,
        SUM(f.quantity) AS total_units
    FROM dbo.fact_sales f
    INNER JOIN dbo.dim_product p
        ON f.product_id = p.product_id
    GROUP BY p.category
)
SELECT
    category,
    category_revenue,
    total_units,
    CAST(100.0 * category_revenue / SUM(category_revenue) OVER() AS DECIMAL(10,2)) AS revenue_share_pct,
    DENSE_RANK() OVER(ORDER BY category_revenue DESC) AS revenue_rank
FROM category_sales
ORDER BY revenue_rank;

/* 4. Regional quarterly performance */
SELECT
    r.region_name,
    d.quarter_label,
    SUM(f.revenue) AS revenue,
    COUNT(DISTINCT f.order_id) AS orders_count,
    SUM(f.quantity) AS units_sold
FROM dbo.fact_sales f
INNER JOIN dbo.dim_region r
    ON f.region_id = r.region_id
INNER JOIN dbo.dim_date d
    ON f.date_key = d.date_key
GROUP BY r.region_name, d.quarter_label
ORDER BY r.region_name, d.quarter_label;

/* 5. Top products by revenue */
SELECT TOP 10
    p.product_name,
    p.category,
    SUM(f.revenue) AS total_revenue,
    SUM(f.quantity) AS total_units,
    COUNT(DISTINCT f.order_id) AS total_orders
FROM dbo.fact_sales f
INNER JOIN dbo.dim_product p
    ON f.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC;

/* 6. Quarter-over-quarter revenue comparison */
WITH quarterly_revenue AS (
    SELECT
        d.[year],
        d.quarter_label,
        CASE d.quarter_label
            WHEN 'Q1' THEN 1
            WHEN 'Q2' THEN 2
            WHEN 'Q3' THEN 3
            WHEN 'Q4' THEN 4
        END AS quarter_num,
        SUM(f.revenue) AS revenue
    FROM dbo.fact_sales f
    INNER JOIN dbo.dim_date d
        ON f.date_key = d.date_key
    GROUP BY d.[year], d.quarter_label
)
SELECT
    [year],
    quarter_label,
    revenue,
    LAG(revenue) OVER (ORDER BY [year], quarter_num) AS previous_quarter_revenue,
    CAST(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY [year], quarter_num))
        / NULLIF(LAG(revenue) OVER (ORDER BY [year], quarter_num), 0)
        AS DECIMAL(10,2)
    ) AS qoq_growth_pct
FROM quarterly_revenue
ORDER BY [year], quarter_num;

/* 7. Region + category matrix for Power BI heat map */
SELECT
    r.region_name,
    p.category,
    SUM(f.revenue) AS revenue,
    SUM(f.quantity) AS units_sold
FROM dbo.fact_sales f
INNER JOIN dbo.dim_region r
    ON f.region_id = r.region_id
INNER JOIN dbo.dim_product p
    ON f.product_id = p.product_id
GROUP BY r.region_name, p.category
ORDER BY r.region_name, revenue DESC;
