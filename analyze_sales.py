import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style='whitegrid')

def load_data():
    dim_date = pd.read_csv(os.path.join(RAW_DIR, 'dim_date.csv'), parse_dates=['full_date', 'month_start'])
    dim_product = pd.read_csv(os.path.join(RAW_DIR, 'dim_product.csv'))
    dim_region = pd.read_csv(os.path.join(RAW_DIR, 'dim_region.csv'))
    fact_sales = pd.read_csv(os.path.join(RAW_DIR, 'fact_sales.csv'))
    return dim_date, dim_product, dim_region, fact_sales

def build_sales_model(dim_date, dim_product, dim_region, fact_sales):
    sales = fact_sales.merge(dim_date, on='date_key', how='left')                              .merge(dim_product, on='product_id', how='left')                              .merge(dim_region, on='region_id', how='left')
    sales['order_revenue_rank'] = sales['revenue'].rank(method='dense', ascending=False)
    return sales

def export_kpis(sales):
    monthly = sales.groupby(['year', 'month_num', 'month_name'], as_index=False).agg(
        total_revenue=('revenue', 'sum'),
        total_orders=('order_id', 'nunique'),
        total_units=('quantity', 'sum')
    )
    monthly['avg_order_value'] = monthly['total_revenue'] / monthly['total_orders']
    monthly = monthly.sort_values(['year', 'month_num'])
    monthly['previous_month_revenue'] = monthly['total_revenue'].shift(1)
    monthly['mom_growth_pct'] = ((monthly['total_revenue'] - monthly['previous_month_revenue']) / monthly['previous_month_revenue']) * 100

    category = sales.groupby('category', as_index=False).agg(
        total_revenue=('revenue', 'sum'),
        total_units=('quantity', 'sum'),
        total_orders=('order_id', 'nunique')
    ).sort_values('total_revenue', ascending=False)
    category['revenue_share_pct'] = (category['total_revenue'] / category['total_revenue'].sum()) * 100
    category['revenue_rank'] = category['total_revenue'].rank(method='dense', ascending=False).astype(int)

    regional = sales.groupby(['region_name', 'quarter_label'], as_index=False).agg(
        total_revenue=('revenue', 'sum'),
        total_orders=('order_id', 'nunique'),
        total_units=('quantity', 'sum')
    )

    top_products = sales.groupby(['product_name', 'category'], as_index=False).agg(
        total_revenue=('revenue', 'sum'),
        total_units=('quantity', 'sum'),
        total_orders=('order_id', 'nunique')
    ).sort_values('total_revenue', ascending=False).head(10)

    quarterly = sales.groupby(['year', 'quarter_label'], as_index=False).agg(
        revenue=('revenue', 'sum')
    )
    quarter_order = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
    quarterly['quarter_num'] = quarterly['quarter_label'].map(quarter_order)
    quarterly = quarterly.sort_values(['year', 'quarter_num'])
    quarterly['previous_quarter_revenue'] = quarterly['revenue'].shift(1)
    quarterly['qoq_growth_pct'] = ((quarterly['revenue'] - quarterly['previous_quarter_revenue']) / quarterly['previous_quarter_revenue']) * 100

    monthly.to_csv(os.path.join(PROCESSED_DIR, 'monthly_kpis.csv'), index=False)
    category.to_csv(os.path.join(PROCESSED_DIR, 'category_performance.csv'), index=False)
    regional.to_csv(os.path.join(PROCESSED_DIR, 'regional_performance.csv'), index=False)
    top_products.to_csv(os.path.join(PROCESSED_DIR, 'top_products.csv'), index=False)
    quarterly.to_csv(os.path.join(PROCESSED_DIR, 'quarterly_performance.csv'), index=False)

    return monthly, category, regional, top_products, quarterly

def generate_visuals(monthly, category, quarterly):
    plt.figure(figsize=(11, 5))
    sns.lineplot(data=monthly, x='month_name', y='total_revenue', marker='o', sort=False)
    plt.title('Monthly Revenue Trend')
    plt.xlabel('Month')
    plt.ylabel('Revenue')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_revenue_trend.png'), dpi=200)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(data=category, x='category', y='total_revenue', hue='category', legend=False)
    plt.title('Revenue by Product Category')
    plt.xlabel('Category')
    plt.ylabel('Revenue')
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'category_revenue.png'), dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.barplot(data=quarterly, x='quarter_label', y='revenue', hue='quarter_label', legend=False)
    plt.title('Quarterly Revenue Comparison')
    plt.xlabel('Quarter')
    plt.ylabel('Revenue')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'quarterly_revenue.png'), dpi=200)
    plt.close()

def summarize_insight(quarterly):
    q = quarterly[['quarter_label', 'revenue']].copy()
    q = q.sort_values('quarter_label')
    q3 = float(q.loc[q['quarter_label'] == 'Q3', 'revenue'].iloc[0])
    strongest_non_q3 = float(q.loc[q['quarter_label'] != 'Q3', 'revenue'].max())
    dip_pct = ((strongest_non_q3 - q3) / strongest_non_q3) * 100
    return round(dip_pct, 2)

def main():
    dim_date, dim_product, dim_region, fact_sales = load_data()
    sales = build_sales_model(dim_date, dim_product, dim_region, fact_sales)
    monthly, category, regional, top_products, quarterly = export_kpis(sales)
    generate_visuals(monthly, category, quarterly)
    dip_pct = summarize_insight(quarterly)

    print('Processed datasets saved to:', PROCESSED_DIR)
    print('Charts saved to:', OUTPUT_DIR)
    print(f'Total rows analyzed: {len(sales):,}')
    print(f'Total revenue: ${sales["revenue"].sum():,.2f}')
    print(f'Q3 revenue dip vs strongest quarter: {dip_pct}%')

if __name__ == '__main__':
    main()
