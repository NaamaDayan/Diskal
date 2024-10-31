import dash_bootstrap_components as dbc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

from constants import CUSTOMER_NAME, PRODUCT_NAME, TOTAL_REVENUE, SUM, ALL, MONTH
from globals import orders_df



def get_customer_view():
    return (
        html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label("בחר לקוח", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='customer-dropdown',
                        options=[{'label': cust, 'value': cust} for cust in orders_df[CUSTOMER_NAME].unique()],
                        multi=False,
                        value=orders_df[CUSTOMER_NAME].unique()[0],
                    )], width=6),

                dbc.Col([
                    html.Label("בחר מוצר", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='product-dropdown',
                        options=[{'label': prod, 'value': prod} for prod in orders_df[PRODUCT_NAME].unique()] + [
                            {'label': 'הכל', 'value': 'all'}],
                        multi=False,
                        value='all',
                    )], width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='customer-graph'), width=12),
            ], justify='center'),
            html.Br(),
            dbc.Row([
                dbc.Col(get_best_products(), width=6),
            ], justify='center'),
            html.Br()
        ]))


def get_best_products():
    popular_products = orders_df.groupby(PRODUCT_NAME)[TOTAL_REVENUE].sum().sort_values(ascending=False)[:15].index
    revenues_by_product = orders_df[orders_df[PRODUCT_NAME].isin(popular_products)].groupby(PRODUCT_NAME)[
        TOTAL_REVENUE].sum().reset_index()
    products_pie_chart = px.pie(revenues_by_product,
                                values=TOTAL_REVENUE,
                                names=PRODUCT_NAME,
                                title='מוצרים הכי רווחיים בשנה האחרונה',
                                template='plotly_dark')

    return dcc.Graph(id='product-pie', figure=products_pie_chart)


def register_customer_callbacks(app):
    @app.callback(
        Output('customer-graph', 'figure'),
        [Input('customer-dropdown', 'value'),
         Input('product-dropdown', 'value')]
    )
    def update_graph(selected_customer, selected_product):
        if selected_product == ALL:
            filtered_df = orders_df[orders_df[CUSTOMER_NAME] == selected_customer].groupby(MONTH)[
                [TOTAL_REVENUE, SUM]].sum().reset_index()
        else:
            filtered_df = orders_df[(orders_df[CUSTOMER_NAME] == selected_customer) &
                                   (orders_df[PRODUCT_NAME] == selected_product)].groupby(MONTH)[
                [TOTAL_REVENUE, SUM]].sum().reset_index()
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
            y=filtered_df[SUM],
            name=SUM,
            marker_color='red'
        ))

        fig.update_layout(
            title='הכנסות ורווחים לאורך זמן',
            xaxis_title=MONTH,
            yaxis_title='ש"ח',
            barmode='group',
            template='plotly_dark'
        )
        return fig
