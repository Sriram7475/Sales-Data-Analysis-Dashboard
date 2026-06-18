import os
import random
from datetime import datetime
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

def build_date_dimension(start='2023-01-01', end='2023-12-31'):
    dates = pd.date_range(start=start, end=end, freq='D')
    df = pd.DataFrame({'full_date': dates})
    df['date_key'] = df['full_date'].dt.strftime('%Y%m%d').astype(int)
    df['year'] = df['full_date'].dt.year
    df['quarter_label'] = 'Q' + df['full_date'].dt.quarter.astype(str)
    df['month_num'] = df['full_date'].dt.month
    df['month_name'] = df['full_date'].dt.strftime('%b')
    df['month_start'] = df['full_date'].values.astype('datetime64[M]')
    return df[['date_key', 'full_date', 'year', 'quarter_label', 'month_num', 'month_name', 'month_start']]

def build_product_dimension():
    products = [
        (1, 'Laptop Pro 15', 'Electronics', 700, 1100),
        (2, 'Wireless Earbuds', 'Electronics', 35, 79),
        (3, 'Office Chair', 'Furniture', 90, 180),
        (4, 'Standing Desk', 'Furniture', 180, 350),
        (5, 'Blender Max', 'Home Appliances', 40, 95),
        (6, 'Air Fryer XL', 'Home Appliances', 55, 130),
        (7, 'Running Shoes', 'Sportswear', 30, 85),
        (8, 'Yoga Mat', 'Sportswear', 8, 25),
        (9, 'Smart Watch', 'Accessories', 90, 220),
        (10, 'Travel Backpack', 'Accessories', 22, 65),
        (11, 'Water Bottle', 'Accessories', 4, 18),
        (12, 'Desk Lamp', 'Home Decor', 12, 38),
        (13, 'Wall Art Frame', 'Home Decor', 10, 45),
        (14, 'Coffee Maker', 'Home Appliances', 45, 120),
        (15, 'Gaming Mouse', 'Electronics', 15, 55),
    ]
    return pd.DataFrame(products, columns=['product_id', 'product_name', 'category', 'unit_cost', 'unit_price'])

def build_region_dimension():
    regions = [
        (1, 'North', 'USA', 'Avery Johnson'),
        (2, 'South', 'USA', 'Morgan Lee'),
        (3, 'East', 'USA', 'Taylor Smith'),
        (4, 'West', 'USA', 'Jordan Patel'),
    ]
    return pd.DataFrame(regions, columns=['region_id', 'region_name', 'country', 'manager_name'])

def generate_sales(date_dim, product_dim, region_dim, n_rows=12000):
    month_weights = {
        1: 1.05, 2: 1.02, 3: 1.08,
        4: 1.10, 5: 1.12, 6: 1.06,
        7: 0.82, 8: 0.79, 9: 0.76,
        10: 1.04, 11: 1.15, 12: 1.21,
    }
    segment_choices = ['Consumer', 'Corporate', 'Home Office']
    channel_choices = ['Online', 'In-Store']
    region_weights = [0.28, 0.22, 0.26, 0.24]
    product_popularity = np.array([0.08, 0.10, 0.06, 0.04, 0.06, 0.06, 0.09, 0.10, 0.08, 0.07, 0.11, 0.04, 0.03, 0.04, 0.04])
    product_popularity = product_popularity / product_popularity.sum()

    date_rows = date_dim.to_dict('records')
    product_lookup = product_dim.set_index('product_id').to_dict('index')
    region_ids = region_dim['region_id'].tolist()
    product_ids = product_dim['product_id'].tolist()

    sales_records = []
    for i in range(1, n_rows + 1):
        date_row = random.choice(date_rows)
        month_num = date_row['month_num']
        if random.random() > month_weights[month_num] / 1.25:
            date_row = random.choice([d for d in date_rows if d['month_num'] == month_num])

        product_id = int(np.random.choice(product_ids, p=product_popularity))
        region_id = int(np.random.choice(region_ids, p=region_weights))
        product = product_lookup[product_id]

        quantity = int(np.random.choice([1, 2, 3, 4, 5, 6], p=[0.34, 0.26, 0.18, 0.11, 0.07, 0.04]))
        discount_pct = round(float(np.random.choice([0, 0.05, 0.10, 0.15], p=[0.55, 0.23, 0.17, 0.05])), 2)
        unit_price = float(product['unit_price'])

        # Q3 soft demand effect
        seasonal_multiplier = 0.84 if month_num in [7, 8, 9] else 1.0
        promotional_uplift = 1.06 if month_num in [11, 12] else 1.0
        effective_price = unit_price * (1 - discount_pct) * promotional_uplift * seasonal_multiplier
        revenue = round(quantity * effective_price, 2)

        sales_records.append({
            'sales_id': i,
            'order_id': f'ORD-{100000 + i}',
            'date_key': int(date_row['date_key']),
            'product_id': product_id,
            'region_id': region_id,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'revenue': revenue,
            'discount_pct': discount_pct,
            'customer_segment': random.choice(segment_choices),
            'sales_channel': random.choice(channel_choices),
        })

    return pd.DataFrame(sales_records)

def main():
    date_dim = build_date_dimension()
    product_dim = build_product_dimension()
    region_dim = build_region_dimension()
    fact_sales = generate_sales(date_dim, product_dim, region_dim, n_rows=12000)

    date_dim.to_csv(os.path.join(RAW_DIR, 'dim_date.csv'), index=False)
    product_dim.to_csv(os.path.join(RAW_DIR, 'dim_product.csv'), index=False)
    region_dim.to_csv(os.path.join(RAW_DIR, 'dim_region.csv'), index=False)
    fact_sales.to_csv(os.path.join(RAW_DIR, 'fact_sales.csv'), index=False)

    print('Generated raw CSV files:')
    print('-', os.path.join(RAW_DIR, 'dim_date.csv'))
    print('-', os.path.join(RAW_DIR, 'dim_product.csv'))
    print('-', os.path.join(RAW_DIR, 'dim_region.csv'))
    print('-', os.path.join(RAW_DIR, 'fact_sales.csv'))
    print(f'Total sales rows: {len(fact_sales):,}')
    print(f'Total revenue: ${fact_sales["revenue"].sum():,.2f}')

if __name__ == '__main__':
    main()
