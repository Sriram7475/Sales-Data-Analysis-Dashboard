# Sales Data Analysis Dashboard

End-to-end portfolio project demonstrating **SQL, Python, Pandas, Power BI, and MS SQL Server** for retail sales analytics.

## Project Overview
This project simulates a retail sales analytics workflow for **10,000+ transaction rows**. It covers:
- relational data modeling for sales analysis
- advanced SQL using **CTEs, window functions, and multi-table joins**
- Python + Pandas KPI preparation and validation
- Power BI-ready datasets and suggested DAX measures
- business insight discovery, including a **Q3 revenue dip (~23%)** caused by seasonal demand shifts

## Tech Stack
- SQL / MS SQL Server
- Python
- Pandas
- Power BI
- Matplotlib / Seaborn

## Repository Structure
```
sales-data-analysis-dashboard/
├── data/
│   ├── raw/
│   └── processed/
├── output/
├── powerbi/
│   ├── dax_measures.txt
│   └── dashboard_layout.md
├── scripts/
│   ├── analyze_sales.py
│   └── generate_sample_data.py
├── sql/
│   ├── 01_create_tables.sql
│   └── 02_kpi_queries.sql
├── .gitignore
├── README.md
└── requirements.txt
```

## Business Problem
Manual spreadsheet reporting is slow and error-prone. This project creates a reusable analytics pipeline that prepares clean KPI tables for dashboarding and supports decisions around revenue trends, product mix, and regional performance.

## Dataset Design
The synthetic dataset includes:
- **fact_sales**: transaction grain sales records
- **dim_date**: calendar attributes
- **dim_product**: category and product metadata
- **dim_region**: regional hierarchy and manager assignments

The generator intentionally introduces seasonal softness in Q3 to mimic realistic business behavior.

## Key Dashboard Views
1. KPI cards: Revenue, Orders, Units, Avg Order Value
2. Monthly revenue trend line
3. Revenue by product category bar chart
4. Regional revenue heat map / filled map
5. Top products table
6. Quarterly performance comparison

## Core Insight
Analysis identifies a revenue decline of roughly **23% in Q3** relative to stronger quarters, supporting recommendations for:
- pre-season inventory balancing
- targeted promotions in underperforming regions
- category-specific campaign timing

## Setup
### 1) Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Generate sample data
```bash
python scripts/generate_sample_data.py
```

### 4) Run Python KPI pipeline
```bash
python scripts/analyze_sales.py
```

## MS SQL Server Usage
1. Create a database, for example `RetailSalesDB`
2. Run `sql/01_create_tables.sql`
3. Import CSV files from `data/raw/` into the matching tables
4. Run `sql/02_kpi_queries.sql`
5. Connect Power BI to SQL Server or directly to the processed CSV outputs

## Power BI Build Steps
- Load `data/processed/monthly_kpis.csv`
- Load `data/processed/category_performance.csv`
- Load `data/processed/regional_performance.csv`
- Load `data/processed/top_products.csv`
- Add measures from `powerbi/dax_measures.txt`
- Follow layout guidance in `powerbi/dashboard_layout.md`

## Resume-Ready Summary
Queried and aggregated 10,000+ rows of retail sales transaction data using advanced SQL, including CTEs, window functions, and multi-table joins, to produce structured KPI datasets. Built an interactive Power BI dashboard with six visuals covering monthly revenue trends, category breakdowns, and regional performance. Identified an approximately 23% Q3 revenue dip linked to seasonal demand shifts, informing inventory and promotional recommendations.

## Suggested Git Commands
```bash
git init
git add .
git commit -m "Initial commit - sales data analysis dashboard"
```
