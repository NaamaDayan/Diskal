import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output

from customer import get_customer_view, register_customer_callbacks
from overview import register_sales_and_revenue_callbacks, get_overview_view
from product import get_product_view, register_product_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)
register_sales_and_revenue_callbacks(app)
register_product_callbacks(app)
register_customer_callbacks(app)

app.layout = html.Div([dbc.Container(fluid=True, children=[
    dbc.Tabs([
        dbc.Tab(label='מבט על', tab_id='overview-tab'),
        dbc.Tab(label='חיפוש לפי לקוח', tab_id='customer-tab'),
        dbc.Tab(label='חיפוש לפי מוצר', tab_id='product-tab'),
    ], id='tabs', active_tab='overview-tab'),

    # Tab content
    html.Div(id='tabs-content')
])], dir='rtl')


@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'active_tab')
)
def render_content(active_tab):
    if active_tab == 'overview-tab':
        return get_overview_view()

    elif active_tab == 'customer-tab':
        return get_customer_view()

    elif active_tab == 'product-tab':
        return get_product_view()


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
