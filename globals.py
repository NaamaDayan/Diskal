from datetime import datetime
from typing import List

import pandas as pd

from constants import TOTAL_REVENUE, SUM, DATE, ORDER_DATE, MONTH, YEAR, PRODUCT_ID, \
    YEAR_MONTH, SALES_ALL_MONTHS, SALES_6_MONTHS, ORDERS_LEFT_TO_SUPPLY, QUANTITY, \
    ORDERS_REMAINING
from gmail_automation import authenticate_gmail, download_attachments, was_downloaded_today, update_last_download_date


def get_previous_12_months_df_by_product(product_ids: List[str]):
    current_date = datetime.now()
    end_date = pd.Timestamp(current_date.year, current_date.month, 1)
    start_date = end_date - pd.DateOffset(years=1)

    full_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    full_range_df = pd.DataFrame(
        [(d.year, d.month, product_id) for d in full_range for product_id in product_ids],
        columns=[YEAR, MONTH, PRODUCT_ID])
    return full_range_df


def get_product_quantities_over_months(df: pd.DataFrame, column_prefix: str = ' נמכר ', column_name: str = QUANTITY):
    grouped_df = df.groupby([MONTH, YEAR, PRODUCT_ID]).sum().reset_index()

    full_range_df = get_previous_12_months_df_by_product(grouped_df[PRODUCT_ID].unique())

    merged_df = pd.merge(full_range_df, grouped_df, on=[YEAR, MONTH, PRODUCT_ID], how='left').fillna(0)
    merged_df['year_month'] = column_prefix + merged_df[YEAR].astype(str) + '-' + merged_df[MONTH].astype(
        str).str.zfill(2)
    quantities_df = merged_df.pivot_table(index=PRODUCT_ID, columns=['year_month'], values=column_name,
                                          fill_value=0)

    return quantities_df


def pre_process_sales_df(sales_df: pd.DataFrame):
    sales_df[TOTAL_REVENUE] = pd.to_numeric(sales_df[TOTAL_REVENUE], errors='coerce')
    sales_df[SUM] = pd.to_numeric(sales_df[SUM], errors='coerce')

    try:
        sales_df[DATE] = pd.to_datetime(sales_df[DATE], format='%d/%m/%y')
    except:
        if 'old_date' in sales_df.columns:
            sales_df.drop('old_date', axis=1, inplace=True)
        sales_df = sales_df.rename({DATE: 'old_date'}, axis=1)
        print (sales_df['old_date'].head())
        sales_df[DATE] = pd.to_datetime(sales_df['old_date'], format='%Y-%d-%m', errors='coerce')
        sales_df[DATE] = sales_df[DATE].fillna(pd.to_datetime(sales_df['old_date'], format='%d/%m/%Y', errors='coerce'))

    sales_df[MONTH] = sales_df[DATE].dt.month
    sales_df[YEAR] = sales_df[DATE].dt.year
    print ("before", len(sales_df))
    sales_df = sales_df[sales_df[DATE].notna()]
    print("after", len(sales_df))
    return sales_df


def pre_process_procurement_bills_df(procurement_bills_df: pd.DataFrame):
    try:
        procurement_bills_df[DATE] = pd.to_datetime(procurement_bills_df[DATE], format='%d/%m/%Y')
    except:
        procurement_bills_df[DATE] = pd.to_datetime(procurement_bills_df[DATE], format='%d/%m/%y',
                                                           errors='coerce')
    procurement_bills_df = procurement_bills_df[procurement_bills_df[DATE] > datetime(2016, 1, 1)]
    procurement_bills_df[MONTH] = procurement_bills_df[DATE].dt.month
    procurement_bills_df[YEAR] = procurement_bills_df[DATE].dt.year
    procurement_bills_df[YEAR_MONTH] = procurement_bills_df[YEAR].astype(str) + '-' + procurement_bills_df[
        MONTH].astype(
        str).str.zfill(2)
    return procurement_bills_df


def update_base_data(base_data_path: str, recent_data: pd.DataFrame, pre_process_caller):
    base_data = pd.read_csv(base_data_path)
    base_data = pd.concat([pre_process_caller(base_data), pre_process_caller(recent_data)])
    base_data = base_data.drop_duplicates()
    base_data.to_csv(base_data_path, index=False)


def update_inventory_by_date(recent_inventory_by_date_df: pd.DataFrame):
    inventory_by_date = pd.read_csv('data/inventory_by_date.csv')
    current_month = str(datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    if current_month not in inventory_by_date.columns:
        recent_inventory_by_date_df = \
        recent_inventory_by_date_df.rename({'מק"ט': PRODUCT_ID, 'יתרה': current_month}, axis=1)[
            [PRODUCT_ID, current_month]]
        inventory_by_date = pd.merge(inventory_by_date, recent_inventory_by_date_df, on=PRODUCT_ID)
        inventory_by_date.to_csv('data/inventory_by_date.csv', index=False)


if not was_downloaded_today():
    service = authenticate_gmail()

    # products_availability_df = download_attachments(service, subject='זמינות מוצרים')
    # products_availability_df.to_csv('data/products_availability.csv', index=False)
    # print("after products availability")
    #
    # inventory_df = download_attachments(service, subject='נעמה מלאי')
    # inventory_df.to_csv('data/נעמה מלאי נוכחי.csv', index=False)
    # print("after inventory availability")
    #
    # recent_procurement_bills_df = download_attachments(service, subject='נעמה - חשבוניות רכש')
    # update_base_data('data/נעמה חשבונית רכש.csv', recent_procurement_bills_df, pre_process_procurement_bills_df)
    # print("after bills availability")

    recent_sales_df = download_attachments(service, subject='נעמה מכירות')
    update_base_data('data/נעמה מכירות.csv', recent_sales_df, pre_process_sales_df)
    print("after inventory availability")

    recent_inventory_by_date_df = download_attachments(service, subject='סה"כ מלאי לתאריך לפי מוצר')
    update_inventory_by_date(recent_inventory_by_date_df)

    update_last_download_date()

print("already downloaded")
inventory_df = pd.read_csv('data/נעמה מלאי נוכחי.csv')
products_availability_df = pd.read_csv('data/products_availability.csv')
sales_df = pre_process_sales_df(pd.read_csv('data/נעמה מכירות.csv'))
procurement_bills_df = pre_process_procurement_bills_df(pd.read_csv('data/נעמה חשבונית רכש.csv'))
inventory_by_date_df = pd.read_csv('data/inventory_by_date.csv')
products_family_df = pd.read_csv('data/products_family.csv')

bills_df = pd.read_csv('data/נעמה חשבוניות.csv')
bills_df[TOTAL_REVENUE] = pd.to_numeric(bills_df[TOTAL_REVENUE], errors='coerce')
bills_df[SUM] = pd.to_numeric(bills_df[SUM], errors='coerce')
bills_df = bills_df.rename({DATE: 'old_date'}, axis=1)
bills_df[DATE] = pd.to_datetime(bills_df['old_date'], format='%Y-%d-%m', errors='coerce')
bills_df[DATE] = bills_df[DATE].fillna(pd.to_datetime(bills_df['old_date'], format='%d/%m/%Y', errors='coerce'))
bills_df[MONTH] = bills_df[DATE].dt.month
bills_df[YEAR] = bills_df[DATE].dt.year

orders_df = pd.read_csv('data/נעמה הזמנות.csv')
orders_df[TOTAL_REVENUE] = pd.to_numeric(orders_df[TOTAL_REVENUE], errors='coerce')
orders_df[SUM] = pd.to_numeric(orders_df[SUM], errors='coerce')
orders_df[ORDER_DATE] = pd.to_datetime(orders_df[ORDER_DATE])
orders_df[MONTH] = orders_df[ORDER_DATE].dt.month
orders_df[YEAR] = orders_df[ORDER_DATE].dt.year
orders_df = orders_df[orders_df['סטטוס הזמנה'] != 'טיוטא']

procurement_df = pd.read_csv('data/נעמה הזמנות רכש.csv')
procurement_df[ORDER_DATE] = pd.to_datetime(procurement_df[ORDER_DATE], format='%d/%m/%Y')
procurement_df = procurement_df[procurement_df[ORDER_DATE] > datetime(2016, 1, 1)]
procurement_df[MONTH] = procurement_df[ORDER_DATE].dt.month
procurement_df[YEAR] = procurement_df[ORDER_DATE].dt.year
procurement_df[YEAR_MONTH] = procurement_df[YEAR].astype(str) + '-' + procurement_df[MONTH].astype(
    str).str.zfill(2)

procurement_df[SUM] = pd.to_numeric(procurement_df[SUM], errors='coerce')

# inventory_df = pd.read_csv('data/נעמה מלאי נוכחי.csv')

sales_quantities_df = get_product_quantities_over_months(sales_df)
sales_all_months = sales_quantities_df.sum(axis=1)
sales_6_months = sales_quantities_df[sorted(sales_quantities_df.columns)[-6:]].sum(axis=1)
sales_quantities_df[SALES_ALL_MONTHS] = sales_all_months
sales_quantities_df[SALES_6_MONTHS] = sales_6_months
sales_quantities_df = sales_quantities_df.reset_index()

orders_left_quantities = get_product_quantities_over_months(orders_df, column_prefix=' הזמנות ',
                                                            column_name=ORDERS_REMAINING)
orders_left_quantities[ORDERS_LEFT_TO_SUPPLY] = orders_left_quantities[sorted(orders_left_quantities.columns)[-3:]].sum(
    axis=1)
orders_left_quantities = orders_left_quantities.reset_index()
