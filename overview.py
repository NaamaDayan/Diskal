import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from constants import MANUFACTURER, SALES_ALL_MONTHS, CURRENT_MONTH_SALES, PRODUCT_ID, SALES_1_MONTH_BEFORE, \
    SALES_2_MONTH_BEFORE, SALES_3_MONTH_BEFORE, PRODUCT_NAME
from sales_and_orders import register_sales_and_revenue_callbacks, get_sales_and_orders_view

# Load Excel data
df = pd.read_excel('data/diskal_stats.xlsx')
df[MANUFACTURER] = df[PRODUCT_ID].str.extract('([A-Za-z]+)')
df[MANUFACTURER] = df[MANUFACTURER].apply(lambda s: s if type(s) == str and len(s) >= 2 else None)
df[SALES_ALL_MONTHS] = df[SALES_1_MONTH_BEFORE] + df[SALES_2_MONTH_BEFORE] + df[SALES_3_MONTH_BEFORE] + df[
    CURRENT_MONTH_SALES]

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)
register_sales_and_revenue_callbacks(app)

# Create the layout with tabs
app.layout = dbc.Container(fluid=True, children=[
    dbc.Tabs([
        dbc.Tab(label='Overview', tab_id='overview-tab'),
        dbc.Tab(label='Sales and Orders', tab_id='sales-tab'),
        dbc.Tab(label='Specific Product', tab_id='product-tab'),
    ], id='tabs', active_tab='overview-tab'),

    # Tab content
    html.Div(id='tabs-content')
])

# Callback to update tab content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'active_tab')
)
def render_content(active_tab):
    if active_tab == 'overview-tab':
        # Create figures for the graphs
        popular_manufacturers = df.groupby(MANUFACTURER)[SALES_ALL_MONTHS].sum().sort_values(ascending=False)[:10].index
        new_df = df.copy()
        new_df[MANUFACTURER] = new_df[MANUFACTURER].apply(lambda x: x if x in popular_manufacturers else 'other')
        sales_by_manufacturer = new_df.groupby(MANUFACTURER)[SALES_ALL_MONTHS].sum().reset_index()
        fig_pie = px.pie(sales_by_manufacturer,
                         values=SALES_ALL_MONTHS,
                         names=MANUFACTURER,
                         title='Sales Share by Manufacturer',
                         template='plotly_dark')

        popular_products = df.nlargest(10, SALES_ALL_MONTHS)
        fig_popular = px.bar(popular_products,
                             x=PRODUCT_NAME,
                             y=SALES_ALL_MONTHS,
                             title='Top 10 Most Popular Products',
                             color=SALES_ALL_MONTHS,
                             template='plotly_dark')

        # Prepare data for sales comparison bar chart
        sales_comparison_data = [
            df[SALES_3_MONTH_BEFORE].sum(),
            df[SALES_2_MONTH_BEFORE].sum(),
            df[SALES_1_MONTH_BEFORE].sum()
        ]
        fig_sales_comparison = px.bar(
            x=['3 Months Before', '2 Months Before', '1 Month Before'],
            y=sales_comparison_data,
            title='Sales Comparison Over Last 3 Months',
            labels={'x': 'Month', 'y': 'Sales'},
            template='plotly_dark'
        )

        # # Prepare data for orders bar chart
        # orders_data = {
        #     'Orders': df['Current Orders'].sum(),  # Placeholder for actual orders column
        #     'Open Orders': df['Open Orders'].sum()  # Placeholder for actual open orders column
        # }
        # fig_orders = px.bar(
        #     x=list(orders_data.keys()),
        #     y=list(orders_data.values()),
        #     title='Orders Overview',
        #     labels={'x': 'Order Type', 'y': 'Count'},
        #     template='plotly_dark'
        # )

        return (
            html.Div([
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='manufacturer-sales-pie', figure=fig_pie), width=6),
                    dbc.Col(dcc.Graph(id='popular-products-bar', figure=fig_popular), width=6)
                ], justify='center'),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='sales-comparison-bar', figure=fig_sales_comparison), width=6),
                    dbc.Col(dcc.Graph(id='orders-bar', figure=fig_sales_comparison), width=6),
                ], justify='center')
        ]))

    elif active_tab == 'sales-tab':
        return get_sales_and_orders_view()

    elif active_tab == 'product-tab':
        return html.Div("Specific Product tab content goes here.")

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
