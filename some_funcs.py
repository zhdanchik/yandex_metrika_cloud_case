# -*- coding: utf-8 -*-
import requests
import pandas as pd
from io import StringIO

# Функции (класс) для интеграции с ClickHouse
# Напишем функции для интеграции с ClickHouse: первая функция просто возвращает результат из DataBase, вторая же преобразует его в pandas DataFrame.
# Также напишем сразу удобную функцию для загрузки данных.

class simple_ch_client():
    def __init__(self, CH_HOST, CH_USER, CH_PASS, cacert):
        self.CH_HOST = CH_HOST
        self.CH_USER = CH_USER
        self.CH_PASS = CH_PASS
        self.cacert = cacert

    def get_clickhouse_data(self, query, connection_timeout = 1500):
        r = requests.post(self.CH_HOST, params = {'query': query, 'user': self.CH_USER, 'password':self.CH_PASS}, timeout = connection_timeout, verify=self.cacert)
        if r.status_code == 200:
            return r.text
        else:
            raise ValueError(r.text)

    def get_clickhouse_df(self, query,connection_timeout = 1500):
        data = self.get_clickhouse_data(query, connection_timeout=connection_timeout) 
        df = pd.read_csv(StringIO(data), sep = '\t')
        return df

    def upload(self, table, content, data_format='TabSeparatedWithNames'):
        content = content.encode('utf-8')
        query_dict = {
                'query': 'INSERT INTO {table} FORMAT {data_format} '.format(table=table, data_format=data_format),
                'user': self.CH_USER, 
                'password':self.CH_PASS
            }
        r = requests.post(self.CH_HOST, data=content, params=query_dict, verify=self.cacert)
        result = r.text
        if r.status_code == 200:
            return result
        else:
            raise ValueError(r.text)
            
# Простая функция для построения графиков в plotly 

from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly import graph_objs as go

init_notebook_mode(connected = True)

def plotly_df(df, title = ''):
    data = []
    
    for column in df.columns:
        trace = go.Scatter(
            x = df.index,
            y = df[column],
            mode = 'lines',
            name = column
        )
        data.append(trace)
    
    layout = dict(title = title)
    fig = dict(data = data, layout = layout)
    
    # plotly.offline.plot(fig, filename=filename, show_link = False)
    
    iplot(fig, show_link = False)
    
def highlight_vals(val):
    if (val is None) or (val == ''):
        return ''
    p = 0.5
    if val > 90:
        return 'background-color: rgba(229, 0, 20, %f)' % p
    if val > 80:
        return 'background-color: rgba(231, 25, 43, %f)' % p
    if val > 70:
        return 'background-color: rgba(234, 51, 67, %f)' % p
    if val > 60:
        return 'background-color: rgba(236, 76, 90, %f)' % p
    if val > 50:
        return 'background-color: rgba(239, 102, 114, %f)' % p
    if val > 40:
        return 'background-color: rgba(242, 137, 127, %f)' % p
    if val > 30:
        return 'background-color: rgba(244, 153, 161, %f)' % p
    if val > 20:
        return 'background-color: rgba(247, 178, 184, %f)' % p
    if val > 10:
        return 'background-color: rgba(249, 204, 208, %f)' % p
    return 'background-color: rgba(252, 229, 231, %f)' % p