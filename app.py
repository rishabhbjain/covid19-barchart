import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
from os.path import isfile

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

fileNamePickle = "allData.pkl"



def loadData(fileName):
    data = pd.read_csv(fileName).drop(['Lat', 'Long','Province/State'], axis=1).melt(id_vars=['Country/Region'], var_name='date').astype({'date':'datetime64[ns]'}, errors='ignore')
    return data


def refreshData():
    allData = loadData("time_series_covid19_confirmed_global.csv")
    allData.to_pickle(fileNamePickle)
    return allData


def allData():
    if not isfile(fileNamePickle):
        refreshData()
    allData = pd.read_pickle(fileNamePickle)
    return allData

countries = allData()['Country/Region'].unique()
countries.sort()


app = dash.Dash(__name__)

server = app.server

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <title>COVID-19 CountryWise Comparision</title>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
       </footer>
    </body>
</html>"""

app.layout = html.Div(
    style={ 'font-family':"Courier New, monospace" },
    children=[
        html.H1('COVID-19 cases'),
        html.Div(className="row", children=[
            html.Div(className="four columns", children=[
                html.H5('Country'),
                dcc.Dropdown(
                    id='country',
                    options=[{'label':c, 'value':c} for c in countries],
                    value='Italy'
                ),
         ]),

        ]),
        dcc.Graph(
            id="plot_cum_metrics",
            config={'displayModeBar': False}
        ),
        dcc.Interval(
            id='interval-component',
            interval=3600*1000, # Refresh data each hour.
            n_intervals=0
        )
    ]
)

def filtered_data(country):
    d = allData()
    data = d.loc[d['Country/Region'] == country].drop('Country/Region', axis=1)
    data = data.groupby("date").sum().reset_index()
    data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
    return data

def barchart(data, yaxisTitle=""):
    print(data)
    figure = go.Figure(data=[
        go.Bar(
            name="metric", x=data.date, y=data.value,
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color= 'rgb(100,140,240)'
        )
    ])
    print("Figure above is cleared")
    figure.update_layout(
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'),
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes(
              title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD',
              tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    print("Figure")
    return figure

@app.callback(
    Output('plot_cum_metrics', 'figure'),
    [Input('country', 'value'), Input('interval-component', 'n_intervals')]
)
def update_plots(country, n):
    data = filtered_data(country)

    barchart_cum = barchart(data, yaxisTitle="Cases")
    return  barchart_cum


if __name__ == '__main__':
    allData()
    app.run_server(debug=True)
