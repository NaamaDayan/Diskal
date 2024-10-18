import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from constants import CUSTOMER_NAME, PRODUCT_NAME, MONTH, TOTAL_REVENUE, TOTAL_INCOME, DROP_DOWN_STYLE, ALL

print ("before")
df = pd.read_excel('data/all_sales_with_months.xlsx')
# df = pd.read_excel('data/all_sales_partial.xlsx')
df[TOTAL_REVENUE] = pd.to_numeric(df[TOTAL_REVENUE], errors='coerce')
df[TOTAL_INCOME] = pd.to_numeric(df[TOTAL_INCOME], errors='coerce')
df = df[df[CUSTOMER_NAME] != 'בדיקות']
print ("after")

def get_sales_and_orders_view():
    return (
        html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label("בחר לקוח", style={'color': 'white'}),
                    dcc.Dropdown(
                    id='customer-dropdown',
                    options=[{'label': cust, 'value': cust} for cust in df[CUSTOMER_NAME].unique()] + [{'label': 'הכל', 'value': 'all'}],
                    multi=False,
                    value='all',
                    # style=DROP_DOWN_STYLE
                )], width=6),

                dbc.Col([
                    html.Label("בחר מוצר", style={'color': 'white'}),
                    dcc.Dropdown(
                    id='product-dropdown',
                    options=[{'label': prod, 'value': prod} for prod in df[PRODUCT_NAME].unique()] + [{'label': 'הכל', 'value': 'all'}],
                    multi=False,
                    value='all',
                    # style=DROP_DOWN_STYLE
                )], width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='revenue-graph'), width=12),
            ], justify='center'),
            html.Br(),
            dbc.Row([
                dbc.Col(get_best_customers(), width=6),
                dbc.Col(get_best_products(), width=6),
            ], justify='center'),
            html.Br()
        ]))



def get_best_customers():
    popular_customers = df.groupby(CUSTOMER_NAME)[TOTAL_REVENUE].sum().sort_values(ascending=False)[:10].index
    new_df = df.copy()
    new_df[CUSTOMER_NAME] = new_df[CUSTOMER_NAME].apply(lambda x: x if x in popular_customers else 'other')
    revenues_by_customer = new_df.groupby(CUSTOMER_NAME)[TOTAL_REVENUE].sum().reset_index()
    customers_pie_chart = px.pie(revenues_by_customer,
                     values=TOTAL_REVENUE,
                     names=CUSTOMER_NAME,
                     title='לקוחות הכי רווחיים בשנה האחרונה',
                     template='plotly_dark')

    return dcc.Graph(id='customers-pie', figure=customers_pie_chart)


def get_best_products():
    popular_products = df.groupby(PRODUCT_NAME)[TOTAL_REVENUE].sum().sort_values(ascending=False)[:15].index
    revenues_by_product = df[df[PRODUCT_NAME].isin(popular_products)].groupby(PRODUCT_NAME)[TOTAL_REVENUE].sum().reset_index()
    products_pie_chart = px.pie(revenues_by_product,
                     values=TOTAL_REVENUE,
                     names=PRODUCT_NAME,
                     title='מוצרים הכי רווחיים בשנה האחרונה',
                     template='plotly_dark')

    return dcc.Graph(id='product-pie', figure=products_pie_chart)


def register_sales_and_revenue_callbacks(app):
    @app.callback(
        Output('revenue-graph', 'figure'),
        [Input('customer-dropdown', 'value'),
         Input('product-dropdown', 'value')]
    )
    def update_graph(selected_customer, selected_product):
        if selected_customer == ALL and selected_product == ALL:
            filtered_df = df.groupby(MONTH)[[TOTAL_REVENUE, TOTAL_INCOME]].sum().reset_index()
        elif selected_customer == ALL and selected_product != ALL:
            filtered_df = df[df[PRODUCT_NAME] == selected_product].groupby(MONTH)[[TOTAL_REVENUE, TOTAL_INCOME]].sum().reset_index()
        elif selected_customer != ALL and selected_product == ALL:
            filtered_df = df[df[CUSTOMER_NAME] == selected_customer].groupby(MONTH)[[TOTAL_REVENUE, TOTAL_INCOME]].sum().reset_index()
        else:
            filtered_df = df[(df[CUSTOMER_NAME] == selected_customer) & (df[PRODUCT_NAME] == selected_product)]
        filtered_df = filtered_df.sort_values(MONTH)
        filtered_df[MONTH] = filtered_df[MONTH].astype(str)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=filtered_df[MONTH],
            y=filtered_df[TOTAL_REVENUE],
            name=TOTAL_REVENUE,
            marker_color='blue'
        ))
        fig.add_trace(go.Bar(
            x=filtered_df[MONTH],
            y=filtered_df[TOTAL_INCOME],
            name=TOTAL_INCOME,
            marker_color='red'
        ))

        fig.update_layout(
            title='הכנסות ורווחים פר חודש',
            xaxis_title=MONTH,
            yaxis_title='ש"ח',
            barmode='group',
            template='plotly_dark'
        )
        return fig

