from datetime import datetime

import pandas as pd
from google.type.calendar_period_pb2 import MONTH

from constants import TOTAL_REVENUE, CUSTOMER_NAME, SUM, DATE, ORDER_DATE

# stats_df = pd.read_excel('data/זמינות מוצרים.xlsx')
# stats_df[MANUFACTURER] = stats_df[PRODUCT_ID].str.extract('([A-Za-z]+)')
# stats_df[MANUFACTURER] = stats_df[MANUFACTURER].apply(lambda s: s if type(s) == str and len(s) >= 2 else None)
# stats_df[SALES_ALL_MONTHS] = stats_df[SALES_1_MONTH_BEFORE] + stats_df[SALES_2_MONTH_BEFORE] + stats_df[SALES_3_MONTH_BEFORE] + stats_df[
#     CURRENT_MONTH_SALES]

sales_df = pd.read_csv('data/נעמה חשבוניות.csv')
sales_df[TOTAL_REVENUE] = pd.to_numeric(sales_df[TOTAL_REVENUE], errors='coerce')
sales_df[SUM] = pd.to_numeric(sales_df[SUM], errors='coerce')

sales_df[DATE] = pd.to_datetime(sales_df[DATE])
sales_df[MONTH] = sales_df[DATE].dt.month
sales_df = sales_df[sales_df[TOTAL_REVENUE] > 0]
sales_df = sales_df[sales_df[SUM] > 0]
sales_df = sales_df[sales_df[CUSTOMER_NAME] != 'בדיקות']

orders_df = pd.read_csv('data/נעמה הזמנות.csv')
orders_df[TOTAL_REVENUE] = pd.to_numeric(orders_df[TOTAL_REVENUE], errors='coerce')
orders_df[SUM] = pd.to_numeric(orders_df[SUM], errors='coerce')
orders_df = orders_df[orders_df[CUSTOMER_NAME] != 'בדיקות']
orders_df[ORDER_DATE] = pd.to_datetime(orders_df[ORDER_DATE])
orders_df[MONTH] = orders_df[ORDER_DATE].dt.month

procurement_df = pd.read_csv('data/נעמה חשבונית רכש.csv')
procurement_df[DATE] = pd.to_datetime(procurement_df[DATE])
procurement_df = procurement_df[procurement_df[DATE] > datetime(2016, 1, 1)]
procurement_df[MONTH] = procurement_df[DATE].dt.month
procurement_df[SUM] = pd.to_numeric(procurement_df[SUM], errors='coerce')
