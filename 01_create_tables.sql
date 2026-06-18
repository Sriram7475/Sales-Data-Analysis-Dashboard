/*==============================================================
  Sales Data Analysis Dashboard - MS SQL Server Schema
==============================================================*/

IF OBJECT_ID('dbo.fact_sales', 'U') IS NOT NULL DROP TABLE dbo.fact_sales;
IF OBJECT_ID('dbo.dim_date', 'U') IS NOT NULL DROP TABLE dbo.dim_date;
IF OBJECT_ID('dbo.dim_product', 'U') IS NOT NULL DROP TABLE dbo.dim_product;
IF OBJECT_ID('dbo.dim_region', 'U') IS NOT NULL DROP TABLE dbo.dim_region;

CREATE TABLE dbo.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    [year] INT NOT NULL,
    quarter_label VARCHAR(2) NOT NULL,
    month_num INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    month_start DATE NOT NULL
);

CREATE TABLE dbo.dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE dbo.dim_region (
    region_id INT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    manager_name VARCHAR(100) NOT NULL
);

CREATE TABLE dbo.fact_sales (
    sales_id INT PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    date_key INT NOT NULL,
    product_id INT NOT NULL,
    region_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    discount_pct DECIMAL(5,2) NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    sales_channel VARCHAR(30) NOT NULL,
    CONSTRAINT FK_fact_sales_date FOREIGN KEY (date_key) REFERENCES dbo.dim_date(date_key),
    CONSTRAINT FK_fact_sales_product FOREIGN KEY (product_id) REFERENCES dbo.dim_product(product_id),
    CONSTRAINT FK_fact_sales_region FOREIGN KEY (region_id) REFERENCES dbo.dim_region(region_id)
);

CREATE INDEX IX_fact_sales_date_key ON dbo.fact_sales(date_key);
CREATE INDEX IX_fact_sales_product_id ON dbo.fact_sales(product_id);
CREATE INDEX IX_fact_sales_region_id ON dbo.fact_sales(region_id);
CREATE INDEX IX_fact_sales_order_id ON dbo.fact_sales(order_id);
