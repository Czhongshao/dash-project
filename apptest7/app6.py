import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html
from dash.dependencies import Input, Output
from sqlalchemy import create_engine

# MySQL 连接字符串
mysql_url = 'jdbc:mysql://localhost:3306/onlinetradingsystem?utf8mb4=true&useDefaultPassword=1'
engine = create_engine (mysql_url)

app = dash.Dash (__name__)


def get_current_tables():
    """获取当前数据库中的所有表名"""
    # 执行 SQL 查询以获取当前库中的表名
    query = pd.read_sql_query ("SHOW TABLES", con=engine)
    return [{'label': name[0], 'value': name[0]} for name in query.to_numpy ()]


app.layout = html.Div (
    dbc.Container (
        [
            # 表格下拉菜单
            dbc.Row (
                [
                    dbc.Col (dbc.Button ('更新数据库表名', id='refresh-db', style={'width': '100%'}), width=2),
                    dbc.Col (dbc.Dropdown (id='db-table-names', placeholder='选择库中数据表',
                                           value=get_current_tables ()[0]['value'],
                                           options=get_current_tables ()),
                             width=4
                             ),
                    dbc.Col (dbc.Button ('查询', id='query', style={'width': '100%'}), width=2)
                ]
            ),
            html.Hr (),
            # 查询结果表单
            dbc.Row (
                [
                    dbc.Col (
                        id='query-result'
                    )
                ]
            )
        ],
        style={
            'margin-top': '50px'  # 设置顶部留白区域高度
        }
    )
)


@app.callback (
    Output ('db-table-names', 'options'),
    Input ('refresh-db', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_table_names(n_clicks):
    return get_current_tables ()


@app.callback (
    Output ('query-result', 'children'),
    Input ('query', 'n_clicks'),
    State ('db-table-names', 'value'),
    prevent_initial_call=True
)
def query_data_records(n_clicks, value):
    if not value:
        return dash.no_update

    # 查询指定表的最多前500行数据
    query_result = pd.read_sql_query (
        f'select * from {value} limit 500',
        con=engine
    )

    return html.Div (dbc.Table.from_dataframe (query_result, striped=True),
                     style={'height': '600px', 'overflow': 'auto'})


if __name__ == '__main__':
    app.run_server (debug=True)
