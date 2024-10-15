from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px
import os

app = Dash(__name__)


product_stats = pd.read_excel('diskal_stats.xlsx')
# Create a basic bar chart using Plotly
fig = px.bar(product_stats.head(50), x='תאור מוצר', y='נמכר בחודש הקודם', title='Product Sales Statistics')

app.layout = html.Div(children=[
    html.H1(children='Store Product Dashboard'),
    dcc.Graph(id='sales-graph', figure=fig)
])

if __name__ == '__main__':
    app.run_server()
