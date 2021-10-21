
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pygsheets
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'  # 圖表直接開啟新分頁顯示


# connect googleSheet
gc = pygsheets.authorize(
    service_account_file='./python-google-sheet-6143cf97ae4e.json')
survey_url = 'https://docs.google.com/spreadsheets/d/17AeIQBghiK_91AHkfsVY0HLj-4-son5O2PpF0563Wfw/edit#gid=0'
sh = gc.open_by_url(survey_url)


# # Olympic Medal Count

olympic_website = 'https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/medal-standings.htm'
r = requests.get(olympic_website)
web_content = r.text
soup = BeautifulSoup(web_content, 'html.parser')

df_Result = pd.DataFrame(columns=['Rank', 'Country', 'Gold_Medal',
                         'Silver_Medal', 'Bronze_Medal', 'Total_Medal', 'Rank_by_Total', 'url'])

# climbing table
rowHead = soup.find('table', 'table').find_all('tr')[0]  # 這是表頭
rows = soup.find('table', 'table').find_all('tr')[1:]  # 排除表頭

for row in rows:
    Rank = int(row.find_all('td')[0].text)
    Country = row.find_all('td')[1].text.strip()
    Gold_Medal = int(row.find_all('td')[2].text[1:])
    Silver_Medal = int(row.find_all('td')[3].text[1:])
    Bronze_Medal = int(row.find_all('td')[4].text[1:])
    Total_Medal = int(row.find_all('td')[5].text)
    url = row.find_all('td')[5].a['href'].split(
        '/', 3)[3][35:]  # 以/做字串分割，切割3次共4段，取第4段
    Rank_by_Total = int(row.find_all('td')[6].text[1:])
    i = {'Rank': Rank, 'Country': Country, 'Gold_Medal': Gold_Medal,
         'Silver_Medal': Silver_Medal, 'Bronze_Medal': Bronze_Medal, 'Total_Medal': Total_Medal,
         'Rank_by_Total': Rank_by_Total, 'url': url}
    df_Result = df_Result.append(i, ignore_index=True)

#ROC is Russia
df_Result.replace("ROC", "Russia", inplace=True)


# # combine country & continent

# 讀取 country_continent 工作表
ws = sh.worksheet_by_title('country_continent')
val = ws.get_values('A2', 'C300')

df2 = pd.DataFrame(
    val, columns=['Continent_Name', 'Continent_Code', 'Country'])
df_continent = df2.loc[:, ['Country', 'Continent_Name']]

# df_continent 轉為 dict
# key:Country_Name  value:Continent_Name
df_continent = df_continent.set_index('Country').T.to_dict('list')

# df_Result 國家 對應 df_continent 洲名
# 若遇到 奧運國家名稱 跟 國家列表名稱不一樣，需手動更改「國家列表」名稱
df_Result['Continent'] = df_Result['Country'].apply(lambda x: df_continent[x])
df_Result['Continent'] = df_Result['Continent'].map(lambda x: str(x)[2:-2])
df_Result.head()


# # Award-winning info

def awardWinner(country, url):
    url_country = 'https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-'+url
    r = requests.get(url_country)
    web_content = r.text
    soup = BeautifulSoup(web_content, 'lxml')  # html.parser'
    df = pd.DataFrame(
        columns=['Country', 'ID', 'Winner', 'Sport', 'Event', 'Medal', 'Winner_info'])

    # climbing table
    rows = soup.find('table', 'table').tbody.find_all('tr')
    for row in rows:
        Country = country
        ID = row.find_all('td')[0].div['country']
        winner = row.find_all('td')[0].text.strip()  # .strip() 刪除多於空白
        sport = row.find_all('td')[0].a['href'].split(
            '/', 6)[5]  # 以/做字串分割，切割6次共7段，取第6段
        event = row.find_all('td')[2].text[1:]
        medal = int(row.find_all('td')[3].img['alt'])
        winner_info = row.find_all('td')[0].a['href'].split(
            '/', 5)[5]  # 以/做字串分割，切割5次共6段，取第6段
        i = {'Country': Country, 'ID': ID, 'Winner': winner,
             'Sport': sport, 'Event': event, 'Medal': medal, 'Winner_info': winner_info}
        df = df.append(i, ignore_index=True)
    return df


df_winner = pd.DataFrame(
    columns=['Country', 'ID', 'Winner', 'Sport', 'Event', 'Medal', 'Winner_info'])


for i in range(len(df_Result.loc[:])):
    df_winner = pd.concat(
        [df_winner, awardWinner(
            df_Result.loc[i].at['Country'], df_Result.loc[i].at['url'])],
        ignore_index=True)

df_winner.head()

# output result
df2.to_csv('./data/continet.csv', index=False)
df_Result.to_csv('./data/medal_count.csv', index=False)
df_winner.to_csv('./data/Award-winning.csv', index=False)
