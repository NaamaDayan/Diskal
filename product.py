import dash_bootstrap_components as dbc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

from constants import PRODUCT_NAME, TOTAL_REVENUE, SUM, \
    QUANTITY, MONTH
from globals import bills_df, procurement_df, orders_df


def get_product_view():
    return (
        html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label("בחר מוצר", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='product-dropdown',
                        options=[{'label': prod, 'value': prod} for prod in bills_df[PRODUCT_NAME].unique()],
                        multi=False,
                        value=bills_df[PRODUCT_NAME].unique()[0],
                    )], width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='price-graph'), width=6),
                dbc.Col(dcc.Graph(id='quantity-graph'), width=6),
            ], justify='center'),
            html.Br(),

        ]))


def register_product_callbacks(app):
    @app.callback(
        [Output('price-graph', 'figure'),
         Output('quantity-graph', 'figure')],
        [Input('product-dropdown', 'value')]
    )
    def update_graph(selected_product):
        sales_over_time = bills_df[(bills_df[PRODUCT_NAME] == selected_product)].groupby(MONTH)[
            [TOTAL_REVENUE, SUM, QUANTITY]].sum().reset_index()
        sales_over_time = sales_over_time.sort_values(MONTH)
        sales_over_time[MONTH] = sales_over_time[MONTH].astype(str)

        orders_over_time = orders_df[(orders_df[PRODUCT_NAME] == selected_product)].groupby(MONTH)[
            [TOTAL_REVENUE, SUM, QUANTITY]].sum().reset_index()
        orders_over_time = orders_over_time.sort_values(MONTH)
        orders_over_time[MONTH] = orders_over_time[MONTH].astype(str)

        procurement_over_time = procurement_df[procurement_df[PRODUCT_NAME] == selected_product].groupby(MONTH)[[
            SUM, QUANTITY]].sum().reset_index()
        procurement_over_time = procurement_over_time.sort_values(MONTH)
        procurement_over_time[MONTH] = procurement_over_time[MONTH].astype(str)

        price_fig = go.Figure()
        price_fig.add_trace(go.Bar(
            x=sales_over_time[MONTH],
            y=sales_over_time[TOTAL_REVENUE],
            name='רווחים בשקלים',
            marker_color='blue'
        ))
        price_fig.add_trace(go.Bar(
            x=sales_over_time[MONTH],
            y=sales_over_time[SUM],
            name='הכנסות בשקלים',
            marker_color='red'
        ))

        price_fig.add_trace(go.Bar(
            x=procurement_over_time[MONTH],
            y=procurement_over_time[SUM],
            name='הוצאות בשקלים',
            marker_color='yellow'
        ))

        price_fig.update_layout(
            title='הכנסות רווחים והזמנות פר חודש',
            xaxis_title=MONTH,
            yaxis_title='ש"ח',
            barmode='group',
            template='plotly_dark'
        )

        quantity_fig = go.Figure()
        quantity_fig.add_trace(go.Bar(
            x=sales_over_time[MONTH],
            y=sales_over_time[QUANTITY],
            name='כמות מכירות בפועל',
            marker_color='blue'
        ))

        quantity_fig.add_trace(go.Bar(
            x=procurement_over_time[MONTH],
            y=procurement_over_time[QUANTITY],
            name='כמות הזמנות מספק',
            marker_color='yellow'
        ))

        quantity_fig.add_trace(go.Bar(
            x=orders_over_time[MONTH],
            y=orders_over_time[QUANTITY],
            name='כמות הזמנות לקוח',
            marker_color='orange'
        ))

        quantity_fig.update_layout(
            title='כמות מכירות והזמנות לאורך זמן',
            xaxis_title=MONTH,
            yaxis_title='כמות',
            barmode='group',
            template='plotly_dark'
        )

        return price_fig, quantity_fig
