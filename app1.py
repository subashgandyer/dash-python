import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import datetime 
from pandas import DataFrame, to_datetime, to_timedelta
import numpy as np

def yearmonth(cols):
    month=cols[0]
    year=cols[1]
    return '{}-{}'.format(month, year)

def dayofweek(datestamp):
    return ['Mon', 'Tue', 'Wed','Thur','Fri','Sat','Sun'][datestamp.weekday()]

def monthname(datestamp):
    return ['Jan', 'Feb', 'Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][datestamp.month-1]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


sleep_df = pd.read_csv('sleep.csv')
sleep_df.drop(['Unnamed: 0', 'extra_data', 'has_sleep_data',
       'com.samsung.health.sleep.comment', 'com.samsung.health.sleep.datauuid',
       'com.samsung.health.sleep.custom', 'original_wake_up_time',
       'com.samsung.health.sleep.deviceuuid',
       'com.samsung.health.sleep.update_time', 'original_bed_time',
       'com.samsung.health.sleep.pkg_name', 'original_efficiency'],\
              axis=1, inplace=True)
sleep_df = sleep_df.rename(columns={"com.samsung.health.sleep.end_time": "end_time",\
                           "com.samsung.health.sleep.start_time": "start_time",\
                           "com.samsung.health.sleep.time_offset": "time_offset",\
                            "com.samsung.health.sleep.create_time": "create_time",
                           "quality":"sleep_quality", "efficiency": "sleep_efficiency"})

for i, ts in enumerate (sleep_df.start_time):
    sleep_df.start_time[i]=datetime.datetime.fromtimestamp(ts/1000)
    
for i, ts in enumerate (sleep_df.end_time):
    sleep_df.end_time[i]=datetime.datetime.fromtimestamp(ts/1000)
    
for i, ts in enumerate (sleep_df.create_time):
    sleep_df.create_time[i]=datetime.datetime.fromtimestamp(ts/1000)

sleep_df.start_time = pd.to_datetime(sleep_df.start_time)
sleep_df.end_time = pd.to_datetime(sleep_df.end_time)

#Create a new column for sleep duration
sleep_df["total_sleep_duration"] = abs((sleep_df.end_time-sleep_df.start_time)/np.timedelta64(1,'h'))

sleep_df['Day'] = sleep_df['create_time'].apply(lambda datestamp: datestamp.day)
sleep_df['Year'] = sleep_df['create_time'].apply(lambda datestamp: datestamp.year)


#Functions to get days of the week and months as strings instead of indexes 
#(0-6 and 0-12 respectively)

sleep_df['Weekday'] = sleep_df['create_time'].apply(lambda datestamp: dayofweek(datestamp)) 
sleep_df['MonthName'] = sleep_df['create_time'].apply(lambda datestamp: monthname(datestamp))

#Keeping the month as an index to construct the yearmonth column below:

sleep_df['Month'] = sleep_df['create_time'].apply(lambda datestamp: datestamp.month)

#Function to get a combined 'YearMonth' column


sleep_df['YearMonth'] = sleep_df[['Month', 'Year']].apply(lambda cols: yearmonth(cols),\
                                                                    axis=1)

sleep_df["localized_time"] = sleep_df["start_time"].dt.tz_localize("CET")

sleep_df["localized_time"] = sleep_df["localized_time"].dt.time


utc_time={"time_offset": ['UTC-0400', 'UTC-0500', 'UTC-0700', 'UTC-0800', 'UTC+0200'],
    "places": ["Halifax(Atlantic)", "Toronto(Eastern)", "Calcary(Mountain)", " Vancouver(Pacific)", "Europe"]}
places_traveled=pd.DataFrame(data=utc_time)


#Create a new column for sleep duration
sleep_df["total_sleep_duration"] = abs((sleep_df.end_time-sleep_df.start_time)/np.timedelta64(1,'h'))

sleep_df = pd.merge(sleep_df, places_traveled, how='left')

eff_sleep_mean = (sleep_df.groupby(sleep_df.start_time.dt.day_name()).sleep_efficiency.mean()*sleep_df.groupby(sleep_df.start_time.dt.day_name()).total_sleep_duration.mean())/100
eff_sleep_std = (sleep_df.groupby(sleep_df.start_time.dt.day_name()).sleep_efficiency.std()*sleep_df.groupby(sleep_df.start_time.dt.day_name()).total_sleep_duration.std())/100


# Dash components display go here ...
app.layout = html.Div([
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                go.Box(
                    # x=sleep_df.start_time.dt.day_name(),
                    y=sleep_df.sleep_efficiency*sleep_df.total_sleep_duration/100,
                    text='Days of week',
                    # mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in sleep_df.start_time.dt.day_name()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Day of Week'},
                yaxis={'title': 'Total Sleep Duration (hrs)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)