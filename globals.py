from datetime import datetime
from typing import List

import pandas as pd

from constants import TOTAL_REVENUE, SUM, DATE, ORDER_DATE, MONTH, YEAR, PRODUCT_ID, \
    YEAR_MONTH, SALES_ALL_MONTHS, SALES_6_MONTHS, ORDERS_LEFT_TO_SUPPLY, QUANTITY, \
    ORDERS_REMAINING, COST, \
    UNIT_COST, TOTAL_SALES_1_YEARS, INVENTORY_QUANTITY, PRODUCT_NAME, QUANTITY_PROCUREMENT
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
    print(sales_df.shape)
    sales_df[DATE] = sales_df[DATE].apply(parse_date)
    #
    # try:
    #     sales_df[DATE] = pd.to_datetime(sales_df[DATE], format='%d/%m/%y')
    # except:
    #     sales_df[DATE] = pd.to_datetime(sales_df[DATE], format='%d/%m/%Y')

    sales_df[MONTH] = sales_df[DATE].dt.month
    sales_df[YEAR] = sales_df[DATE].dt.year
    print("before", len(sales_df))
    sales_df = sales_df[sales_df[DATE].notna()]
    print("after", len(sales_df))
    return sales_df


def pre_process_movements_df(movements_df: pd.DataFrame):
    movements_df[DATE] = movements_df[DATE].apply(parse_date)
    #
    # try:
    #     movements_df[DATE] = pd.to_datetime(movements_df[DATE], format='%d/%m/%y')
    # except:
    #     movements_df[DATE] = pd.to_datetime(movements_df[DATE], format='%d/%m/%Y')
    #
    movements_df = movements_df[movements_df[DATE].notna()]
    return movements_df


def parse_date(date_str: str):
    for fmt in ('%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d'):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    print("Ecxeption!!!", date_str)
    return None


def pre_process_procurement_bills_df(procurement_bills_df: pd.DataFrame):
    procurement_bills_df[DATE] = procurement_bills_df[DATE].apply(parse_date)
    # try:
    #     procurement_bills_df[DATE] = pd.to_datetime(procurement_bills_df[DATE], format='%d/%m/%Y')
    # except:
    #     procurement_bills_df[DATE] = pd.to_datetime(procurement_bills_df[DATE], format='%d/%m/%y')
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


def get_dying_products_by_n_orders(n_orders_last_year: int):
    all_sales_by_product = sales_df.groupby([PRODUCT_ID, PRODUCT_NAME]).agg({
        UNIT_COST: 'mean',
        COST: 'mean',
        QUANTITY: 'sum'})[[UNIT_COST, COST, QUANTITY]].reset_index()
    dead_products_stats = all_sales_by_product[all_sales_by_product[QUANTITY] <= n_orders_last_year]
    dead_products_stats = dead_products_stats.reset_index().rename({QUANTITY: TOTAL_SALES_1_YEARS}, axis=1)
    products_inventory = inventory_df[[PRODUCT_ID, QUANTITY]].rename({QUANTITY: INVENTORY_QUANTITY},
                                                                     axis=1)
    dead_products_with_inventory_larger_than_ten = pd.merge(dead_products_stats, products_inventory[
        products_inventory[INVENTORY_QUANTITY] > 10],
                                                            how='inner', on=PRODUCT_ID)

    products_procurement = procurement_bills_df.rename({QUANTITY: QUANTITY_PROCUREMENT},
                                                       axis=1)
    # products_procurement = products_procurement[products_procurement['סטטוס שורת הזמנת רכש'].isna()]
    unique_products_procurement = products_procurement.groupby([PRODUCT_ID, PRODUCT_NAME]).agg({
        QUANTITY_PROCUREMENT: 'sum',
        DATE: 'max'})[[QUANTITY_PROCUREMENT, DATE]].reset_index()

    dead_products_with_inventory_and_procurement = pd.merge(dead_products_with_inventory_larger_than_ten,
                                                            unique_products_procurement[
                                                                [PRODUCT_ID, PRODUCT_NAME,
                                                                 QUANTITY_PROCUREMENT, DATE]], how='inner',
                                                            on=[PRODUCT_ID, PRODUCT_NAME])
    dead_products_with_inventory_and_procurement[QUANTITY_PROCUREMENT].fillna(0, inplace=True)
    dead_products_with_inventory_and_procurement.drop('index', axis=1, inplace=True)
    dead_products_with_inventory_and_procurement = dead_products_with_inventory_and_procurement[
        dead_products_with_inventory_and_procurement.columns[::-1]]

    dead_products_with_inventory_and_procurement.sort_values(by=INVENTORY_QUANTITY,
                                                             ascending=False, inplace=True)
    return dead_products_with_inventory_and_procurement


if not was_downloaded_today():
    service = authenticate_gmail()

    products_availability_df = download_attachments(service, subject='זמינות מוצרים')
    products_availability_df.to_csv('data/products_availability.csv', index=False)
    print("after products availability")

    inventory_df = download_attachments(service, subject='נעמה מלאי')
    inventory_df.to_csv('data/נעמה מלאי נוכחי.csv', index=False)
    print("after inventory availability")

    recent_procurement_bills_df = download_attachments(service, subject='נעמה - חשבוניות רכש')
    update_base_data('data/נעמה חשבונית רכש.csv', recent_procurement_bills_df, pre_process_procurement_bills_df)
    print("after bills availability")

    recent_sales_df = download_attachments(service, subject='נעמה תונועות מלאי')
    update_base_data('data/נעמה תנועות מלאי.csv', recent_sales_df, pre_process_movements_df)

    recent_sales_df = download_attachments(service, subject='נעמה מכירות')
    update_base_data('data/נעמה מכירות.csv', recent_sales_df, pre_process_sales_df)

    recent_inventory_by_date_df = download_attachments(service, subject='סה"כ מלאי לתאריך לפי מוצר')
    update_inventory_by_date(recent_inventory_by_date_df)

    update_last_download_date()

print("already downloaded")

inventory_df = pd.read_csv('data/נעמה מלאי נוכחי.csv')
inventory_movements_df = pd.read_csv('data/נעמה תנועות מלאי.csv')

full_products_availability_df = pd.read_csv('data/products_availability.csv')
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

dead_products = get_dying_products_by_n_orders(5)
# compare_sales_data(sales_df, full_products_availability_df)
