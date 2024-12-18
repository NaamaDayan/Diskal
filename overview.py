import base64
import io
from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output, State
from openpyxl import load_workbook

from constants import CUSTOMER_NAME, PRODUCT_NAME, DATE, TOTAL_REVENUE, SUM, ALL, \
    AGENT_NAME, PRODUCT_ID, MONTH, STYLE_HEADER, STYLE_DATA, STYLE_TABLE, STYLE_CELL, \
    QUANTITY, INVENTORY_QUANTITY, QUANTITY_PROCUREMENT, SUM_PROCUREMENT, ORDER_DATE, SALES_ALL_MONTHS, \
    SALES_6_MONTHS, ORDERS_LEFT_TO_SUPPLY, ON_THE_WAY_STATUS, ORDER_STATUS, ON_THE_WAY, MANUFACTURER, INVENTORY, \
    PROCUREMENT_ORDERS, DAMAGED_INVENTORY, CURRENT_MONTH_SALES, SALES_1_MONTH_BEFORE, \
    SALES_2_MONTH_BEFORE, SALES_3_MONTH_BEFORE, STATUS, LAST_PRICE, MAIN_INVENTORY, TOTAL_SALES_2_YEARS
from globals import sales_df, inventory_df, sales_quantities_df, procurement_bills_df, orders_left_quantities, \
    procurement_df, bills_df


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    if 'xls' in filename:
        df = pd.read_excel(io.BytesIO(decoded))
    else:
        return None

    return df


#
# def get_upload_view():
#     return html.Div([
#         html.H3("העלה לכאן את קובץ זמינות המוצרים לקבלת קובץ מעודכן"),
#         dcc.Upload(
#             id="upload-data",
#             children=html.Div([
#                 'Drag and Drop or ',
#                 html.A('Select Files')
#             ]),
#             style={
#                 'width': '100%',
#                 'height': '60px',
#                 'lineHeight': '60px',
#                 'borderWidth': '1px',
#                 'borderStyle': 'dashed',
#                 'borderRadius': '5px',
#                 'textAlign': 'center',
#                 'margin': '10px'
#             },
#             multiple=False
#         ),
#         dcc.Loading(
#             id="loading",
#             type="circle",
#             children=[html.Div(id='output-data-upload')],
#         ),
#         dcc.Download(id='download-data'),
#     ])

def get_last_7_dates():
    today = datetime.today()
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, -1, -1)]


def get_overview_view():
    return (
        html.Div([
            # get_upload_view(),
            dbc.Row([
                dbc.Col([
                    html.Label("בחר תקופת זמן", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='time-dropdown',
                        options=[{'label': t, 'value': t} for t in get_last_7_dates()],
                        multi=False,
                        value=str(datetime.now().date()),
                    )], width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='sales-by-agent'), width=12),
            ], justify='center'),
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
                dbc.Col(dbc.Card(dbc.CardBody(get_best_products())), width=6),
            ], justify='center'),
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(get_best_customers())), width=6),
                dbc.Col(dbc.Card(dbc.CardBody(get_best_agents())), width=6),
            ], justify='center'),
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(get_dying_products_view())), width=12),
            ], justify='center'),
            html.Br()
        ]))


def get_dying_products_by_n_orders(n_orders_last_year: int):
    all_sales_by_product = sales_df.groupby(PRODUCT_ID)[QUANTITY].sum()
    dead_products_stats = all_sales_by_product[all_sales_by_product <= n_orders_last_year]
    dead_products_stats = dead_products_stats.reset_index().rename({QUANTITY: TOTAL_SALES_2_YEARS}, axis=1)
    products_inventory = inventory_df[[PRODUCT_ID, PRODUCT_NAME, QUANTITY]].rename({QUANTITY: INVENTORY_QUANTITY}, axis=1)

    dead_products_with_inventory = pd.merge(dead_products_stats, products_inventory,
                                            how='inner', on=PRODUCT_ID)

    dead_products_with_inventory_larger_than_zero = pd.merge(dead_products_stats, products_inventory[
        products_inventory[INVENTORY_QUANTITY] > 0],
                                                             how='inner', on=PRODUCT_ID)

    products_procurement = procurement_df.rename({QUANTITY: QUANTITY_PROCUREMENT, SUM: SUM_PROCUREMENT}, axis=1)
    products_procurement = products_procurement[products_procurement['סטטוס שורת הזמנת רכש'].isna()]
    unique_products_procurement = products_procurement.groupby([PRODUCT_ID, PRODUCT_NAME]).sum()[
        [SUM_PROCUREMENT, QUANTITY_PROCUREMENT]].reset_index()

    dead_products_with_inventory_and_procurement = pd.merge(dead_products_with_inventory_larger_than_zero,
                                                            unique_products_procurement[
                                                                [PRODUCT_ID, PRODUCT_NAME, SUM_PROCUREMENT,
                                                                 QUANTITY_PROCUREMENT]], how='left', on=[PRODUCT_ID, PRODUCT_NAME])
    dead_products_with_inventory_and_procurement[[QUANTITY_PROCUREMENT, SUM_PROCUREMENT]] = \
    dead_products_with_inventory_and_procurement[[QUANTITY_PROCUREMENT, SUM_PROCUREMENT]].fillna(0)
    dead_products_stats = pd.merge(dead_products_with_inventory, products_procurement[
        [PRODUCT_ID, PRODUCT_NAME, ORDER_DATE, SUM_PROCUREMENT, QUANTITY_PROCUREMENT]], how='inner',
                                   on=PRODUCT_ID)

    return dead_products_with_inventory_and_procurement, dead_products_stats


def get_dying_products_view():
    dead_products_with_inventory_and_procurement, _ = get_dying_products_by_n_orders(0)
    dead_products = dead_products_with_inventory_and_procurement.sort_values(by=INVENTORY_QUANTITY,
                                                                             ascending=False)[:10]
    dead_products = dead_products.rename({QUANTITY_PROCUREMENT: 'כמות הזמנות ספק פתוחות'}, axis=1)
    dead_products = dead_products.melt(id_vars=PRODUCT_NAME,
                                       value_vars=[TOTAL_SALES_2_YEARS, INVENTORY_QUANTITY,
                                                   'כמות הזמנות ספק פתוחות'],
                                       var_name='Feature', value_name='Value')

    fig = px.bar(dead_products, x=PRODUCT_NAME, y='Value', color='Feature', barmode='group',
                 title='מוצרים מתים (לא נמכרו בשנתיים האחרונות)')
    fig.update_layout(xaxis_title='מוצר', yaxis_title='כמות', template='plotly_dark')

    return html.Div([
        # dcc.Store(id="dying-products-data"),
        # dbc.Button("Download Excel File", id="download-button", color="primary"),
        # dcc.Download(id="download-excel"),
        dcc.Graph(id='dying-products-graph', figure=fig)
    ])


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
    popular_products = sales_df.groupby(PRODUCT_NAME)[QUANTITY].sum().sort_values(ascending=False)[:15].index
    revenues_by_product = sales_df[sales_df[PRODUCT_NAME].isin(popular_products)].groupby(PRODUCT_NAME)[
        TOTAL_REVENUE].sum().reset_index()
    products_pie_chart = px.pie(revenues_by_product,
                                values=TOTAL_REVENUE,
                                names=PRODUCT_NAME,
                                title='מוצרים הכי נמכרים בשנה האחרונה',
                                template='plotly_dark')

    return dcc.Graph(id='product-pie', figure=products_pie_chart)


def get_top_k_products_table():
    n_products = sales_df[PRODUCT_NAME].nunique()
    popular_products = sales_df.groupby(PRODUCT_NAME)[TOTAL_REVENUE].sum().sort_values(
        ascending=False).reset_index()[: int(0.2 * n_products)][PRODUCT_NAME].values
    popular_products_df = sales_df[sales_df[PRODUCT_NAME].isin(popular_products)][
        [PRODUCT_ID, PRODUCT_NAME, TOTAL_REVENUE]].sort_values(TOTAL_REVENUE,
                                                               ascending=False)
    revenue_ratio = popular_products_df[TOTAL_REVENUE].sum() / sales_df[TOTAL_REVENUE].sum()
    popular_products_df = popular_products_df[[PRODUCT_NAME]].drop_duplicates()
    return html.Div([html.Label(f" 20 אחוז מהמוצרים שמכניסים 70 אחוז מהרווח", style={'color': 'white'}),
                     dash_table.DataTable(
                         data=popular_products_df.to_dict('records'),
                         columns=[{'name': col, 'id': col} for col in popular_products_df.columns],
                         page_size=10,
                         style_data=STYLE_DATA,
                         style_table=STYLE_TABLE,
                         style_cell=STYLE_CELL,
                         style_header=STYLE_HEADER,
                         style_data_conditional=[],
                         sort_action="native",
                         filter_action='native'
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


def get_updated_products_data(uploaded_products_df: pd.DataFrame):
    inventory_by_warehouse = \
        inventory_df.pivot_table(index=PRODUCT_ID, columns=['תאור מחסן'], values='כמות', fill_value=0).reset_index()

    on_the_way_orders = procurement_bills_df[
        (procurement_bills_df[ON_THE_WAY_STATUS] == 'עומד לבוא') & (procurement_bills_df[ORDER_STATUS] != 'סגורה')]
    on_the_way_orders = on_the_way_orders.groupby(PRODUCT_ID)[QUANTITY].sum().reset_index().rename(
        {QUANTITY: ON_THE_WAY}, axis=1)

    updated_products_data = pd.merge(uploaded_products_df,
                                     sales_quantities_df, on=PRODUCT_ID,
                                     how='left')
    updated_products_data = pd.merge(updated_products_data, orders_left_quantities[[ORDERS_LEFT_TO_SUPPLY, PRODUCT_ID]],
                                     on=PRODUCT_ID, how='left')

    updated_products_data = pd.merge(updated_products_data, inventory_by_warehouse, on=PRODUCT_ID, how='left')
    # updated_products_data = pd.merge(updated_products_data, revenue_ratio_df, on=PRODUCT_ID, how='left')

    updated_products_data = pd.merge(updated_products_data, on_the_way_orders, on=PRODUCT_ID, how='left')
    updated_products_data[INVENTORY] = updated_products_data[MAIN_INVENTORY]

    columns = [PRODUCT_ID, PRODUCT_NAME, MANUFACTURER, STATUS, INVENTORY, PROCUREMENT_ORDERS, ON_THE_WAY,
               SALES_ALL_MONTHS,
               SALES_6_MONTHS, CURRENT_MONTH_SALES, SALES_1_MONTH_BEFORE, SALES_2_MONTH_BEFORE, SALES_3_MONTH_BEFORE,
               LAST_PRICE, DAMAGED_INVENTORY]
    return updated_products_data[columns]


def register_sales_and_revenue_callbacks(app):
    @app.callback(
        Output('sales-by-agent', 'figure'),
        [Input('time-dropdown', 'value')]
    )
    def update_graph(selected_date: datetime):
        filtered_bills_df = bills_df[bills_df[DATE] == datetime.strptime(selected_date, '%Y-%m-%d')]
        filtered_bills_df = filtered_bills_df.groupby(AGENT_NAME)[[SUM]].sum().reset_index().sort_values(SUM, ascending=False)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=filtered_bills_df[AGENT_NAME],
            y=filtered_bills_df[SUM],
            name=SUM,
            marker_color='green'
        ))

        fig.update_layout(
            title='מכירות פר סוכן',
            xaxis_title=DATE,
            yaxis_title='ש"ח',
            barmode='group',
            template='plotly_dark'
        )
        return fig

    @app.callback(
        Output('revenue-graph', 'figure'),
        [Input('customer-dropdown', 'value'),
         Input('agent-dropdown', 'value'),
         Input('product-dropdown', 'value')]
    )
    def update_graph(selected_customer, selected_agent, selected_product):
        filtered_sales_df = sales_df
        filtered_procurement_bills_df = procurement_bills_df
        if selected_product != ALL:
            filtered_sales_df = filtered_sales_df[filtered_sales_df[PRODUCT_NAME] == selected_product]
            filtered_procurement_bills_df = filtered_procurement_bills_df[
                filtered_procurement_bills_df[PRODUCT_NAME] == selected_product]
        if selected_agent != ALL:
            filtered_sales_df = filtered_sales_df[filtered_sales_df[AGENT_NAME] == selected_agent]
        if selected_customer != ALL:
            filtered_sales_df = filtered_sales_df[filtered_sales_df[CUSTOMER_NAME] == selected_customer]
        filtered_sales_df = filtered_sales_df.groupby(MONTH)[[TOTAL_REVENUE, SUM]].sum().reset_index().sort_values(
            MONTH)
        filtered_procurement_bills_df = filtered_procurement_bills_df.groupby(MONTH)[
            [SUM]].sum().reset_index().sort_values(MONTH)

        filtered_sales_df[MONTH] = filtered_sales_df[MONTH].astype(str)
        filtered_procurement_bills_df[MONTH] = filtered_procurement_bills_df[MONTH].astype(str)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=filtered_sales_df[MONTH],
            y=filtered_sales_df[TOTAL_REVENUE],
            name=TOTAL_REVENUE,
            marker_color='green'
        ))
        fig.add_trace(go.Bar(
            x=filtered_sales_df[MONTH],
            y=filtered_sales_df[SUM],
            name='הכנסות (שח)',
            marker_color='blue'
        ))

        fig.update_layout(
            title='הכנסות ורווחים פר חודש',
            xaxis_title=DATE,
            yaxis_title='ש"ח',
            barmode='group',
            template='plotly_dark'
        )
        return fig

    @app.callback(
        Output('output-data-upload', 'children'),
        Output('download-data', 'data'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def upload_file(contents, filename):
        if contents is None:
            return "No file uploaded.", None
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        uploaded_products_df = pd.read_excel(io.BytesIO(decoded))
        updated_products_data = get_updated_products_data(uploaded_products_df)

        # Save the modified DataFrame to an Excel file with RTL layout
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            updated_products_data.to_excel(writer, index=False, sheet_name='Sheet1')

        output.seek(0)
        workbook = load_workbook(output)
        sheet = workbook['Sheet1']
        sheet.sheet_view.rightToLeft = True

        final_output = io.BytesIO()
        workbook.save(final_output)
        final_output.seek(0)

        return "הקובץ הועלה בהצלחה! הורדנו למחשב את הקובץ המעודכן", dcc.send_bytes(final_output.getvalue(),
                                                                                   "updated_" + filename)

    # @app.callback(
    #     Output("download-excel", "data"),
    #     Input("download-button", "n_clicks"),
    #     Input("dying-products-data", "data"),
    #     prevent_initial_call=True
    # )
    # def download_excel(n_clicks, data):
    #     # Retrieve stored data from dcc.Store
    #     # data = callback_context.triggered[0]["prop_id"].split(".")[0]
    #     dead_products_with_inventory_and_procurement = pd.read_json(
    #         data["dead_products_with_inventory_and_procurement"])
    #     dead_products_stats = pd.read_json(data["dead_products_stats"])
    #
    #     # Create Excel file
    #     buffer = io.BytesIO()
    #     with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    #         dead_products_with_inventory_and_procurement.to_excel(writer, sheet_name='מוצרים מתים שהוזמנו והם במלאי',
    #                                                               index=False)
    #         dead_products_stats.to_excel(writer, sheet_name="כל המוצרים המתים", index=False)
    #     buffer.seek(0)
    #
    #     return dcc.send_bytes(buffer.getvalue(), filename="מוצרים מתים.xlsx")
