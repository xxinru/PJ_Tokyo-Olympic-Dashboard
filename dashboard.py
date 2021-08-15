import dash_table
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
# import plotly.io as pio
# pio.renderers.default = 'browser'  # 圖表直接開啟新分頁顯示

df_result = pd.read_csv('./data/medal_count.csv')
df_winner = pd.read_csv('./data/Award-winning.csv')

# 把 國家名稱 變更為 大家熟悉的國家簡稱
df_result.replace('United States of America', 'United States', inplace=True)
df_result.replace("People's Republic of China", "China", inplace=True)
df_result.replace('Republic of Korea', 'Korea', inplace=True)
df_result.replace('Islamic Republic of Iran', 'Iran', inplace=True)
df_result.replace('United States of America', 'United States', inplace=True)
df_result.replace('Great Britain', ' United Kingdom', inplace=True)
df_result.replace('Czech Republic', 'Czech', inplace=True)
df_result.replace('Hong Kong, China', 'Hong Kong', inplace=True)

df_winner.replace('United States of America', 'United States', inplace=True)
df_winner.replace("People's Republic of China", "China", inplace=True)
df_winner.replace('Republic of Korea', 'Korea', inplace=True)
df_winner.replace('Islamic Republic of Iran', 'Iran', inplace=True)
df_winner.replace('United States of America', 'United States', inplace=True)
df_winner.replace('Great Britain', ' United Kingdom', inplace=True)
df_winner.replace('Czech Republic', 'Czech', inplace=True)
df_winner.replace('Hong Kong, China', 'Hong Kong', inplace=True)


# dash

app = dash.Dash(__name__,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server


# 有幾個Output，return就要有幾個值
# 有幾個imput，函式就要有幾個輸入值


@app.callback(
    [Output(component_id='choropleth', component_property='figure'),
     Output(component_id='sunburst', component_property='figure')],
    Input(component_id='select_calculate', component_property='value'))
def update_graph(select_calculate):
    fig = px.choropleth(df_result,
                        locations='Country',
                        locationmode='country names',
                        color=select_calculate,
                        projection='kavrayskiy7',  # 地圖投影的方式
                        scope='world',
                        title='Olympic Medal Count around world',
                        hover_name="Country",  # column to add to hover information
                        labels={select_calculate: select_calculate},
                        color_continuous_scale=px.colors.sequential.Reds)

    fig2 = px.sunburst(df_result,
                       path=['Continent', 'Country'],
                       values='Total_Medal',
                       title='面積越大->獎牌越多、顏色越紅->金牌比例越高',
                       color='Gold_Medal',
                       color_continuous_scale='Reds')

    return fig, fig2


# bar
@app.callback(
    Output(component_id='bar', component_property='figure'),
    Input(component_id='datatable-interactivity', component_property='derived_virtual_data'))
def update_bar(all_rows_data):
    df_showTable = pd.DataFrame(all_rows_data)

    fig3 = px.bar(df_showTable.loc[:9, :],
                  x=['Gold_Medal', 'Silver_Medal', 'Bronze_Medal'],
                  y='Country',
                  # text='Total_Medal',
                  # color_continuous_scale='Reds',
                  title='The top10 most successful countries',
                  #labels={"value": "Total_Medal", "variable": "medal"}
                  )
    return fig3


@app.callback(
    Output(component_id='pie_chart', component_property='figure'),
    Input(component_id='select_sport', component_property='value'))
def update_pie(select_sport):

    df_sport = df_winner[df_winner['Sport'] == select_sport]
    df_sport = df_sport.groupby('Country', as_index=False)[['Medal']].count()

    fig4 = px.pie(df_sport,
                  names='Country',
                  values='Medal',
                  title='Which country dominates which sport in the Olympics!',
                  color_discrete_sequence=px.colors.sequential.RdBu)
    fig4.update_traces(textposition='inside', textinfo='label+value',
                       hole=.5)
    fig4.update_layout(annotations=[dict(text='medalTotal='+str(df_sport['Medal'].sum()),
                                         x=0.5, y=0.5, font_size=14, showarrow=False)])
    return fig4


# bar country sport

@app.callback(
    Output(component_id='bar_sport', component_property='figure'),
    Input(component_id='select_country', component_property='value'))
def update_pie(select_country):

    df_Country = df_winner[df_winner['Country'].isin(select_country)]
    df_Country = df_Country.groupby(['Country', 'Sport'], as_index=False)[
        ['Medal']].count()
    df_Country.sort_values('Medal', ascending=False, inplace=True)

    fig5 = px.bar(df_Country,
                  x='Medal',
                  y='Country',
                  color='Country',
                  text='Sport',
                  title='Olympic medals each country won per sports.',
                  color_discrete_sequence=px.colors.sequential.RdBu)
    fig5.update_traces(textposition='inside')

    return fig5


# app Layout
# components 互動性裝置
# 更多互動性裝置參考：https://dash.plotly.com/dash-core-components

app.layout = html.Div([
    # 第一行
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {'name': i, 'id': i, 'hideable': True}
                    if i == 'Rank_by_Total'  # url Continent'                                 #date欄位可被隱藏
                    else{'name': i, 'id': i}
                    for i in df_result.columns],
                data=df_result.to_dict('records'),
                editable=False,
                filter_action='native',                             # none 沒有filter欄位
                sort_action='native',
                sort_mode='single',                                 # 'single' or 'multi'
                column_selectable='multi',
                row_selectable='multi',
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                page_action='native',
                page_current=0,
                page_size=10,
                style_cell={'minWidth': 95, 'maxWidth': 95, 'Width': 95,  # 固定欄寬
                            'backgroundColor': 'rgb(252,234,234)'},
                style_cell_conditional=[  # 文字置中
                    {'if': {'column_id': c}, 'textAlign': 'center'}
                    for c in df_result.columns],
                style_header={'backgroundColor': 'rgb(126,25,25)',  # 表頭 紅底白字
                              'color': 'white'},
                style_data={'backgroundColor': 'rgb(253,244,244)',
                            'color': 'rgb(70,70,72)'})  # 內文 粉白底黑字
        ], className='six columns'),

        html.Div([
            dcc.Graph(id='bar')
        ], className='six columns'),
    ], className='row'),

    html.Br(),


    # 第二行
    html.Div([
        html.Div([
            html.P('Summer Olympic Medal Count By Country',
                   style={'text-aligh': 'center'}),
            dcc.Dropdown(
                id='select_calculate',
                value='Total_Medal',
                options=[
                    {'label': 'Total_Medal', 'value': 'Total_Medal'},
                    {'label': 'Gold_Medal', 'value': 'Gold_Medal'},
                ])
        ], className='six columns'),

        html.Div([

        ], className='six columns'),
    ], className='row'),


    # 第三行
    html.Div([
        html.Div([
            dcc.Graph(id='choropleth', figure={}),
        ], className='six columns'),

        html.Div([
            dcc.Graph(id='sunburst', figure={}),
        ], className='six columns')
    ], className='row'),


    # 第四行
    html.Div([
        html.Div([
            html.P('Sport:'),
            dcc.Dropdown(
                id='select_sport',
                value='judo',
                options=[
                    {'label': i, 'value': i} for i in df_winner.Sport.unique()])
        ], className='six columns'),

        html.Div([
            html.P('Country:'),
            dcc.Dropdown(
                id='select_country',
                value=['Chinese Taipei', 'Japan', 'Korea', 'China'],
                multi=True,
                options=[
                    {'label': i, 'value': i} for i in df_winner.Country.unique()])
        ], className='six columns')
    ], className='row'),



    # 第五行
    html.Div([
        html.Div([
            dcc.Graph(id='pie_chart'),
        ], className='six columns'),

        html.Div([
            dcc.Graph(id='bar_sport'),
        ], className='six columns')
    ], className='row')

])

if __name__ == '__main__':
    app.run_server(debug=True)  # jupyter notebook add ', use_reloader=False'
