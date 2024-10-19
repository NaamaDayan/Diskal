import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output

from constants import CUSTOMER_NAME, PRODUCT_NAME, DATE, TOTAL_REVENUE, SUM, ALL, \
    AGENT_NAME, PRODUCT_ID, MONTH
from globals import sales_df


def get_overview_view():
    return (
        html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label("בחר לקוח", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='customer-dropdown',
                        options=[{'label': cust, 'value': cust} for cust in sales_df[CUSTOMER_NAME].unique()] + [
                            {'label': 'הכל', 'value': 'all'}],
                        multi=False,
                        value='all',
                    )], width=4),

                dbc.Col([
                    html.Label("בחר מוצר", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='product-dropdown',
                        options=[{'label': prod, 'value': prod} for prod in sales_df[PRODUCT_NAME].unique()] + [
                            {'label': 'הכל', 'value': 'all'}],
                        multi=False,
                        value='all',
                    )], width=4),

                dbc.Col([
                    html.Label("בחר סוכן", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='agent-dropdown',
                        options=[{'label': prod, 'value': prod} for prod in sales_df[AGENT_NAME].unique()] + [
                            {'label': 'הכל', 'value': 'all'}],
                        multi=False,
                        value='all',
                    )], width=4),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='revenue-graph'), width=12),
            ], justify='center'),
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(get_top_k_products_table())), width=6),
                dbc.Col(get_best_products(), width=6),
            ], justify='center'),
            html.Br(),
            dbc.Row([
                dbc.Col(get_best_customers(), width=6),
                dbc.Col(get_best_agents(), width=6),
            ], justify='center'),
            html.Br()
        ]))


def get_best_customers():
    popular_customers = sales_df.groupby(CUSTOMER_NAME)[TOTAL_REVENUE].sum().sort_values(ascending=False)[:10].index
    new_df = sales_df.copy()
    new_df[CUSTOMER_NAME] = new_df[CUSTOMER_NAME].apply(lambda x: x if x in popular_customers else 'other')
    revenues_by_customer = new_df.groupby(CUSTOMER_NAME)[TOTAL_REVENUE].sum().reset_index()
    customers_pie_chart = px.pie(revenues_by_customer,
                                 values=TOTAL_REVENUE,
                                 names=CUSTOMER_NAME,
                                 title='לקוחות הכי רווחיים בשנה האחרונה',
                                 template='plotly_dark')

    return dcc.Graph(id='customers-pie', figure=customers_pie_chart)


def get_best_products():
    popular_products = sales_df.groupby(PRODUCT_NAME)[TOTAL_REVENUE].sum().sort_values(ascending=False)[:15].index
    revenues_by_product = sales_df[sales_df[PRODUCT_NAME].isin(popular_products)].groupby(PRODUCT_NAME)[
        TOTAL_REVENUE].sum().reset_index()
    products_pie_chart = px.pie(revenues_by_product,
                                values=TOTAL_REVENUE,
                                names=PRODUCT_NAME,
                                title='מוצרים הכי רווחיים בשנה האחרונה',
                                template='plotly_dark')

    return dcc.Graph(id='product-pie', figure=products_pie_chart)


def get_top_k_products_table():
    n_products = sales_df[PRODUCT_NAME].nunique()
    popular_products = sales_df.groupby(PRODUCT_NAME)[TOTAL_REVENUE].sum().sort_values(
        ascending=False).reset_index()[: int(0.2 * n_products)][PRODUCT_NAME].values
    popular_products_df = sales_df[sales_df[PRODUCT_NAME].isin(popular_products)][[PRODUCT_ID, PRODUCT_NAME, TOTAL_REVENUE]].sort_values(TOTAL_REVENUE,
        ascending=False)
    revenue_ratio = popular_products_df[TOTAL_REVENUE].sum() / sales_df[TOTAL_REVENUE].sum()
    popular_products_df = popular_products_df[[PRODUCT_NAME]].drop_duplicates()
    return html.Div([html.Label(f" 20 אחוז מהמוצרים שמכניסים 70 אחוז מהרווח", style={'color': 'white'}),
                     dash_table.DataTable(
                         data=popular_products_df.to_dict('records'),
                         columns=[{'name': col, 'id': col} for col in popular_products_df.columns],
                         page_size=10,
                         style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                         style_table={"overflowX": "hidden",  "width": "100%"},
                         style_cell={
                             # "overflow": "hidden",
                             "textOverflow": "ellipsis",
                             "maxWidth": 0,
                             'textAlign': 'right',
                             'direction': 'rtl'
                         },
                         style_header={
                             "backgroundColor": "rgb(30, 30, 30)",
                             "color": "white",
                             'direction': 'rtl'
                         }
                     )])


def get_best_agents():
    popular_agents = sales_df.groupby(AGENT_NAME)[TOTAL_REVENUE].sum().sort_values(ascending=False)[:15].index
    revenues_by_agent = sales_df[sales_df[AGENT_NAME].isin(popular_agents)].groupby(AGENT_NAME)[
        TOTAL_REVENUE].sum().reset_index()
    agents_pie_chart = px.pie(revenues_by_agent,
                              values=TOTAL_REVENUE,
                              names=AGENT_NAME,
                              title='סוכנים שהרוויחו הכי הרבה בשנה האחרונה',
                              template='plotly_dark')

    return dcc.Graph(id='product-pie', figure=agents_pie_chart)


def register_sales_and_revenue_callbacks(app):
    @app.callback(
        Output('revenue-graph', 'figure'),
        [Input('customer-dropdown', 'value'),
         Input('agent-dropdown', 'value'),
         Input('product-dropdown', 'value')]
    )
    def update_graph(selected_customer, selected_agent, selected_product):
        filtered_sales_df = sales_df
        if selected_product != ALL:
            filtered_sales_df = filtered_sales_df[filtered_sales_df[PRODUCT_NAME] == selected_product]
        if selected_agent != ALL:
            filtered_sales_df = filtered_sales_df[filtered_sales_df[AGENT_NAME] == selected_agent]
        if selected_customer != ALL:
            filtered_sales_df = filtered_sales_df[filtered_sales_df[CUSTOMER_NAME] == selected_customer]
        filtered_sales_df = filtered_sales_df.groupby(MONTH)[[TOTAL_REVENUE, SUM]].sum().reset_index().sort_values(MONTH)
        filtered_sales_df[MONTH] = filtered_sales_df[MONTH].astype(str)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=filtered_sales_df[MONTH],
            y=filtered_sales_df[TOTAL_REVENUE],
            name=TOTAL_REVENUE,
            marker_color='blue'
        ))
        fig.add_trace(go.Bar(
            x=filtered_sales_df[MONTH],
            y=filtered_sales_df[SUM],
            name=SUM,
            marker_color='red'
        ))

        fig.update_layout(
            title='הכנסות ורווחים פר חודש',
            xaxis_title=DATE,
            yaxis_title='ש"ח',
            barmode='group',
            template='plotly_dark'
        )
        return fig
