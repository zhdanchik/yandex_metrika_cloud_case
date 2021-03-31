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

    def get_version(self):
        url = '{host}/?database={db}&query={query}'.format(
                host=self.CH_HOST,
                db='default',
                query='SELECT version()')

        auth = {
                'X-ClickHouse-User': self.CH_USER,
                'X-ClickHouse-Key': self.CH_PASS,
            }

        rs = requests.get(url, headers=auth, verify=self.cacert)
        # 
        rs.raise_for_status()

        print(rs.text)

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

import plotly
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly import graph_objs as go
init_notebook_mode(connected=True)

# Функция для построения воронок в notebook'е

colors = ['#d54936', '#faca34', '#437cba', '#8bc34a', '#795548', '#309688', '#000000', '#40bcd4', '#9e9e9e', '#3ca9f4']

def plot_funnel(phases, values):
    n_phase = len(phases)
    plot_width = 500.

    # height of a section and difference between sections 
    section_h = 100
    section_d = 10

    # multiplication factor to calculate the width of other sections
    unit_width = plot_width / max(values)

    # width of each funnel section relative to the plot width
    phase_w = [int(value * unit_width) for value in values]
    print (phase_w)

    # plot height based on the number of sections and the gap in between them
    height = section_h * n_phase + section_d * (n_phase - 1)
    
    # list containing all the plot shapes
    shapes = []

    # list containing the Y-axis location for each section's name and value text
    label_y = []

    for i in range(n_phase):
            if (i == n_phase-1):
                    points = [phase_w[i] / 2, height, phase_w[i] / 2, height - section_h]
            else:
                    points = [phase_w[i] / 2, height, phase_w[i+1] / 2, height - section_h]

            path = 'M {0} {1} L {2} {3} L -{2} {3} L -{0} {1} Z'.format(*points)

            shape = {
                    'type': 'path',
                    'path': path,
                    'fillcolor': colors[i],
                    'line': {
                        'width': 1,
                        'color': colors[i]
                    }
            }
            shapes.append(shape)

            # Y-axis location for this section's details (text)
            label_y.append(height - (section_h / 2))

            height = height - (section_h + section_d)

    # For phase names
    label_trace = go.Scatter(
        x=[-350]*n_phase,
        y=label_y,
        mode='text',
        text=phases,
        textfont=dict(
            color='rgb(40,40,40)',
            size=15
        )
    )

    # For phase values
    value_trace = go.Scatter(
        x=[350]*n_phase,
        y=label_y,
        mode='text',
        text=values,
        textfont=dict(
            color='rgb(40,40,40)',
            size=15
        )
    )

    data = [label_trace, value_trace]

    layout = go.Layout(
        title="<b>Funnel Chart</b>",
        titlefont=dict(
            size=20,
            color='rgb(0,0,0)'
        ),
        shapes=shapes,
        height=560,
        width=800,
        showlegend=False,
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
        xaxis=dict(
            showticklabels=False,
            zeroline=False,
            showgrid=False,
            range=[-450, 450]
        ),
        yaxis=dict(
            showticklabels=False,
            zeroline=False,
            showgrid=False
        )
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig, show_link=False)

    
# new_funnel
from plotly import graph_objects as go

def plot_new_funnel(phases, values):

    fig = go.Figure(go.Funnel(
        y = phases,
        x = values,
        textposition = "inside",
        textinfo = "value+percent initial",
        opacity = 0.85, marker = {"color": colors[:len(phases)],
                                 },
        connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}})
        )

    fig.show()

# Простая функция для построения графиков в plotly 

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

#-----------Функция для скачивания файла с ЯНждекс.Диска---------

import requests
from urllib.parse import urlencode

def get_file_from_yadisk(file_link, file_name):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    final_url = base_url + urlencode(dict(public_key=file_link))
    response = requests.get(final_url)
    download_url = response.json()['href']
    
    download_response = requests.get(download_url)
    
    if download_response.status_code == 200:
        print('OK <200>')
    else :
        raise(BaseException("Some error while downloading file"))
    
    with open(file_name, 'wb') as f:   # Здесь укажите нужный путь к файлу
        f.write(download_response.content)
