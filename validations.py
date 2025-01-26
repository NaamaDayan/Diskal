import pandas as pd

from constants import DATE, PRODUCT_ID, QUANTITY, SALES_3_MONTH_BEFORE, CURRENT_MONTH_SALES, SALES_2_MONTH_BEFORE, \
    SALES_1_MONTH_BEFORE


def compare_sales_data(sales_df: pd.DataFrame, products_availability_df: pd.DataFrame):
    current_month = sales_df[DATE].dt.to_period('M').max()
    sales_df['month_period'] = sales_df[DATE].dt.to_period('M')

    aggregated_sales = (
        sales_df.groupby([PRODUCT_ID, 'month_period'])[QUANTITY]
            .sum()
            .reset_index()
            .pivot(index=PRODUCT_ID, columns='month_period', values=QUANTITY)
            .fillna(0)
    )
    relevant_months = [(current_month - i).start_time for i in range(3, -1, -1)]
    aggregated_sales.columns = aggregated_sales.columns.to_timestamp()
    monthly_sales = aggregated_sales[relevant_months].reset_index()
    monthly_sales.columns = [PRODUCT_ID, SALES_3_MONTH_BEFORE, SALES_2_MONTH_BEFORE, SALES_1_MONTH_BEFORE,
                             CURRENT_MONTH_SALES]

    comparison_df = pd.merge(
        products_availability_df,
        monthly_sales,
        on=PRODUCT_ID,
        suffixes=('_availability', '_sales')
    )

    for column in [SALES_3_MONTH_BEFORE, SALES_2_MONTH_BEFORE, SALES_1_MONTH_BEFORE,
                   CURRENT_MONTH_SALES]:
        comparison_df[f'mismatch_{column}'] = (
                comparison_df[f'{column}_availability'] != comparison_df[f'{column}_sales']
        )

    mismatches = comparison_df[
        [f'mismatch_{col}' for col in
         [SALES_3_MONTH_BEFORE, SALES_2_MONTH_BEFORE, SALES_1_MONTH_BEFORE,
          CURRENT_MONTH_SALES]]].any(axis=1)

    mismatched_rows = comparison_df[mismatches]

    print(mismatched_rows)
