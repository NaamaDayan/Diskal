import dash
import dash_bootstrap_components as dbc

from customer import register_customer_callbacks
from overview import register_sales_and_revenue_callbacks, get_overview_view
from product import register_product_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
register_sales_and_revenue_callbacks(app)
register_product_callbacks(app)
register_customer_callbacks(app)

app.layout = dbc.Container(get_overview_view(), fluid=True)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
