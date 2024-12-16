import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine

postgres_url = 'postgresql://postgres:666666@localhost:3306/Dash'
engine = create_engine(postgres_url)

app = dash.Dash(__name__)

app.layout = html.Div(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Button('更新数据库信息', id='refresh-db', style={'width': '100%'}), width=2),
                    dbc.Col(dcc.Dropdown(id='db-table-names', placeholder='选择库中数据表', style={'width': '100%'}), width=4),
                    dbc.Col(dbc.Button('查询', id='query', style={'width': '100%'}), width=1)
                ]
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        id='query-result'
                    )
                ]
            )
        ],
        style={
            'margin-top': '50px'
        }
    )
)

@app.callback(
    Output('db-table-names', 'options'),
    Input('refresh-db', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_table_names(n_clicks):
    try:
        table_names = pd.read_sql_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", con=engine)
        return [{'label': name, 'value': name} for name in table_names['table_name']]
    except Exception as e:
        print(e)
        return [{'label': '无法连接到数据库', 'value': ''}]

@app.callback(
    Output('query-result', 'children'),
    Input('query', 'n_clicks'),
    State('db-table-names', 'value'),
    prevent_initial_call=True
)
def query_data_records(n_clicks, value):
    try:
        if value:
            query_result = pd.read_sql_query(f'SELECT * FROM {value} LIMIT 500', con=engine)
            return html.Div(dbc.Table.from_dataframe(query_result, striped=True), style={'height': '600px', 'overflow': 'auto'})
        else:
            return dash.no_update
    except Exception as e:
        print(e)
        return html.Div("查询失败，请检查表名是否正确。")

if __name__ == '__main__':
    app.run_server(debug=True)