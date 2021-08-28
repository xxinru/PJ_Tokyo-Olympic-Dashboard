import dash_table
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
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

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.LITERA],
                )
server = app.server


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
                        #title='Olympic medal count around world',
                        hover_name="Country",  # column to add to hover information
                        labels={select_calculate: select_calculate},
                        color_continuous_scale=px.colors.sequential.Reds)

    fig2 = px.sunburst(df_result,
                       path=['Continent', 'Country'],
                       values='Total_Medal',
                       #title='The larger area, the more medals.\nThe deeper color, the more gold medals.',
                       color='Gold_Medal',
                       color_continuous_scale='Reds')

    return fig, fig2


@app.callback(
    Output(component_id='barChart', component_property='figure'),
    Input(component_id='select_continent', component_property='value'))
def update_bar(select_continent):
    if select_continent == 'World':
        df_continent = df_result
        df_continent.sort_values('Gold_Medal')
    else:
        df_continent = df_result[df_result['Continent'] == select_continent]
        df_continent.sort_values('Gold_Medal')

    fig3 = px.bar(df_continent.head(10).iloc[::-1],
                  x=['Gold_Medal', 'Silver_Medal', 'Bronze_Medal'],
                  y='Country',
                  labels={'value': 'Medal Count'},
                  color_discrete_map={
                      'Gold_Medal': '#ffd700',
                      'Silver_Medal': '#d3d3d3',
                      'Bronze_Medal': '#CD853F'}
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
                  #title='Which country dominates which sport in the Olympics!',
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
                  #title='Olympic medals each country won per sports.',
                  color_discrete_sequence=px.colors.sequential.RdBu)
    fig5.update_traces(textposition='inside')

    return fig5


card_country = [
    dbc.CardHeader(
        html.H5("Country", className='text-center')),
    dbc.CardBody(
        html.H4("193", className="card-title text-center"))
]

card_athlete = [
    dbc.CardHeader(
        html.H5("Athlete", className='text-center')),
    dbc.CardBody(
        html.H4("11,321", className="card-title text-center"))
]

card_sport = [
    dbc.CardHeader(
        html.H5("Sport", className='text-center')),
    dbc.CardBody(
        html.H4("33", className="card-title text-center"))
]

card_quantity = [
    dbc.CardHeader(
        html.H5("Games Quantity", className='text-center')),
    dbc.CardBody(
        html.H4("339", className="card-title text-center"))
]


card_medal = [
    dbc.CardHeader(
        html.H5("Olympic Medal", className='text-center')),
    dbc.CardBody(
        html.H4("1,080", className="card-title text-center"))
]

app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1('2020 Summer Olympic in Tokyo',
                        className='text-center '),
                width=12)
    ]),

    dbc.Row([
        dbc.Col(html.Br())
    ]),

    dbc.Row([
        dbc.Col(dbc.Card(card_country, color="light"),
                width={'size': 2, 'offset': 1}),
        dbc.Col(dbc.Card(card_athlete, color="light"), width=2),
        dbc.Col(dbc.Card(card_sport, color="light"), width=2),
        dbc.Col(dbc.Card(card_quantity, color="light"), width=2),
        dbc.Col(dbc.Card(card_medal, color="light"), width=2),
    ]),

    dbc.Row([
        dbc.Col(html.Br())
    ]),

    dbc.Row([
        dbc.Col(html.H4('The top10 most successful countries.'),
                width={'size': 'auto', 'offset': 1})
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='select_continent',
                value='World',
                options=[
                    {'label': 'World', 'value': 'World'},
                    {'label': 'Asia', 'value': 'Asia'},
                    {'label': 'Europe', 'value': 'Europe'},
                    {'label': 'North America', 'value': 'North America'},
                    {'label': 'South America', 'value': 'South America'},
                    {'label': 'Africa', 'value': 'Africa'},
                    {'label': 'Oceania', 'value': 'Oceania'}]),
            width={'size': 4, 'offset': 1})
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='barChart'),
                width={'size': 8, 'offset': 2})
    ]),


    dbc.Row([
        dbc.Col(html.H4('Olympic medal count around world'),
                width={'size': 'auto', 'offset': 1})
    ]),


    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='select_calculate',
                value='Total_Medal',
                options=[
                    {'label': 'Total_Medal', 'value': 'Total_Medal'},
                    {'label': 'Gold_Medal', 'value': 'Gold_Medal'}]),
            width={'size': 4, 'offset': 1}),
        dbc.Col(
            html.P(
                'The larger area, the more medals. The deeper color, the more gold medals.'),
            width={'size': 5, 'offset': 2})
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='choropleth', figure={}),
                width=6),

        dbc.Col(dcc.Graph(id='sunburst', figure={}),
                width=6)
    ]),

    dbc.Row([
        dbc.Col(html.H4('Which country dominates the sport.'),
                width={'size': 5, 'offset': 1}),
        dbc.Col(html.H4('How each country performed in the Olympics.'),
                width={'size': 5, 'offset': 1}),
    ]),


    dbc.Row([
        dbc.Col([
            html.P('Sport:'),
            dcc.Dropdown(
                id='select_sport',
                value='judo',
                options=[
                    {'label': i, 'value': i} for i in sorted(df_winner.Sport.unique())])],
            width={'size': 4, 'offset': 1}),

        dbc.Col([
            html.P('Country:'),
            dcc.Dropdown(
                id='select_country',
                value=['Chinese Taipei', 'Japan', 'Korea', 'China'],
                multi=True,
                options=[
                    {'label': i, 'value': i} for i in sorted(df_winner.Country.unique())])],
            width={'size': 4, 'offset': 2})
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='pie_chart'),
                width=6),
        dbc.Col(dcc.Graph(id='bar_sport'),
                width=6)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
