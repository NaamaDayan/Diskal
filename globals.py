from datetime import datetime

import pandas as pd

from constants import TOTAL_REVENUE, CUSTOMER_NAME, SUM, DATE, ORDER_DATE, MONTH, YEAR, PRODUCT_ID, \
    TOTAL_ORDERS_THIS_YEAR, YEAR_MONTH, SALES_ALL_MONTHS, SALES_6_MONTHS, ORDERS_LEFT_TO_SUPPLY


# stats_df = pd.read_excel('data/זמינות מוצרים.xlsx')
# stats_df[MANUFACTURER] = stats_df[PRODUCT_ID].str.extract('([A-Za-z]+)')
# stats_df[MANUFACTURER] = stats_df[MANUFACTURER].apply(lambda s: s if type(s) == str and len(s) >= 2 else None)
# stats_df[SALES_ALL_MONTHS] = stats_df[SALES_1_MONTH_BEFORE] + stats_df[SALES_2_MONTH_BEFORE] + stats_df[SALES_3_MONTH_BEFORE] + stats_df[
#     CURRENT_MONTH_SALES]


def get_product_sold_quantities_over_months():
    grouped_df = bills_df.groupby([MONTH, YEAR, PRODUCT_ID]).agg(
        {'כמות בהזמנה': 'sum', 'יתרה בהזמנה': 'sum', '% רווח למחיר + סיכום': 'sum'}).reset_index()

    current_date = datetime.now()
    end_date = pd.Timestamp(current_date.year, current_date.month, 1)
    start_date = end_date - pd.DateOffset(years=1)

    full_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    full_range_df = pd.DataFrame(
        [(d.year, d.month, product) for d in full_range for product in grouped_df[PRODUCT_ID].unique()],
        columns=[YEAR, MONTH, PRODUCT_ID])

    merged_df = pd.merge(full_range_df, grouped_df, on=[YEAR, MONTH, PRODUCT_ID], how='left').fillna(0)
    merged_df['year_month_orders'] = ' כמות בהזמנה ' + merged_df[YEAR].astype(str) + '-' + merged_df[MONTH].astype(
        str).str.zfill(2)
    orders_quantities = merged_df.pivot_table(index=PRODUCT_ID, columns=['year_month_orders'], values='כמות בהזמנה',
                                              fill_value=0)

    orders_left_quantities = merged_df.pivot_table(index=PRODUCT_ID, columns=['year_month_orders'], values='יתרה בהזמנה',
                                              fill_value=0)
    orders_quantities[TOTAL_ORDERS_THIS_YEAR] = orders_quantities.sum(axis=1)

    merged_df['year_month_sales'] = ' נמכר ' + merged_df[YEAR].astype(str) + '-' + merged_df[MONTH].astype(
        str).str.zfill(2)
    merged_df['נמכר'] = merged_df['כמות בהזמנה'] - merged_df['יתרה בהזמנה']
    sales_quantities = merged_df.pivot_table(index=PRODUCT_ID, columns=['year_month_sales'], values='נמכר',
                                             fill_value=0)

    sales_quantities[SALES_ALL_MONTHS] = sales_quantities.sum(axis=1)
    sales_quantities[SALES_6_MONTHS] = sales_quantities[sorted(sales_quantities.columns)[-6:]].sum(axis=1)
    orders_left_quantities[ORDERS_LEFT_TO_SUPPLY] = orders_left_quantities[sorted(orders_left_quantities.columns)[-3:]].sum(axis=1)
    revenue_ratio_df = merged_df.groupby(PRODUCT_ID)['% רווח למחיר + סיכום'].mean().reset_index().rename(
        {'% רווח למחיר + סיכום': 'אחוז רווח ביחס למחיר (ממוצע השנה)'}, axis=1)

    return orders_quantities.reset_index(), sales_quantities.reset_index(), orders_left_quantities.reset_index(), revenue_ratio_df


bills_df = pd.read_csv('data/נעמה חשבוניות.csv')
bills_df[TOTAL_REVENUE] = pd.to_numeric(bills_df[TOTAL_REVENUE], errors='coerce')
bills_df[SUM] = pd.to_numeric(bills_df[SUM], errors='coerce')
bills_df = bills_df.rename({DATE: 'old_date'}, axis=1)
bills_df[DATE] = pd.to_datetime(bills_df['old_date'], format='%Y-%d-%m', errors='coerce')
bills_df[DATE] = bills_df[DATE].fillna(pd.to_datetime(bills_df['old_date'], format='%d/%m/%Y', errors='coerce'))
bills_df[MONTH] = bills_df[DATE].dt.month
bills_df[YEAR] = bills_df[DATE].dt.year
bills_df = bills_df[bills_df[TOTAL_REVENUE] > 0]
bills_df = bills_df[bills_df[SUM] > 0]
bills_df = bills_df[bills_df[CUSTOMER_NAME] != 'בדיקות']

orders_df = pd.read_csv('data/נעמה הזמנות.csv')
orders_df[TOTAL_REVENUE] = pd.to_numeric(orders_df[TOTAL_REVENUE], errors='coerce')
orders_df[SUM] = pd.to_numeric(orders_df[SUM], errors='coerce')
orders_df = orders_df[orders_df[CUSTOMER_NAME] != 'בדיקות']
orders_df[ORDER_DATE] = pd.to_datetime(orders_df[ORDER_DATE])
orders_df[MONTH] = orders_df[ORDER_DATE].dt.month

procurement_df = pd.read_csv('data/נעמה הזמנות רכש.csv')
procurement_df[ORDER_DATE] = pd.to_datetime(procurement_df[ORDER_DATE], format='%d/%m/%Y')
procurement_df = procurement_df[procurement_df[ORDER_DATE] > datetime(2016, 1, 1)]
procurement_df[MONTH] = procurement_df[ORDER_DATE].dt.month
procurement_df[YEAR] = procurement_df[ORDER_DATE].dt.year
procurement_df[YEAR_MONTH] = procurement_df[YEAR].astype(str) + '-' + procurement_df[MONTH].astype(
    str).str.zfill(2)

procurement_df[SUM] = pd.to_numeric(procurement_df[SUM], errors='coerce')

inventory_df = pd.read_csv('data/נעמה מלאי נוכחי.csv')
orders_quantities_df, sales_quantities_df, orders_left_df, revenue_ratio_df = get_product_sold_quantities_over_months()
