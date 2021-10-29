import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize app object
app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

###### Data ######
# CO2 data
df_co2 = pd.read_csv('D:/ITI/Courses/Data_Visualization/Project_Final/Data/co2_v2.csv')

# Temperature data
temperature_df = pd.read_csv('D:/ITI/Courses/Data_Visualization/Project_Final/Data/Temperature.csv')
data_country = temperature_df.groupby(['Year', 'Country'])['AvgTemperature'].mean().reset_index()
data_region = temperature_df.groupby(['Year', 'Region'])['AvgTemperature'].mean().reset_index()
data_global = temperature_df.groupby(['Year'])['AvgTemperature'].mean().reset_index()

###### Figures ######
# SunBurst for all continents and countries
sunBurst = px.sunburst(df_co2, 
           color='Co2_Emission',
           values='Co2_Emission',
           path=['Continent', 'Country'],
           height=600,
           hover_name='Country',
           title='Co2 Emissions Contribution of Countries and Regions')

# Ten Most Countries Emitting Co2
x2 = df_co2.groupby(['Country']).mean().sort_values(by='Co2_Emission', ascending=False).iloc[:10]
co2_most = px.bar(x2.reset_index().iloc[::-1], 
                x='Co2_Emission', 
                y='Country', 
                title='Ten Most Countries Emitting Co2', 
                template='seaborn',
                hover_name='Country',
                orientation='h',
                height=600,
            )

# Co2 data figures
# country_co2 = px.line(df_co[df_co['Country']==country], 
#                     x="Year", 
#                     y="Co2_Emission", 
#                     title='Co2_Emission in ' + country)

###### Variables ######
colors = {'header':'#130a7b', 'backgd':'#f5f5dc'}

reg_dict = [{'label':i, 'value':i} for i in df_co2['Region'].unique()]
reg_dict.append({'label':'None', 'value':'None'})

###### Layout ######
app.layout = html.Div(children=[

            html.H2('Global Warming Insights', style={'textAlign':'center',
                                            'color':colors['header']}),

            html.H5('1995 - 2017', style={'textAlign':'center',
                                            'color':colors['header']}),
            
            html.Div(children=[
                html.Div(children=[
                    html.Label('Select Region:', 
                            style={'textAlign':'center'}),

                    dcc.Dropdown(
                        id='dropdown1',
                        options=reg_dict,
                        value=None
                        )
                ], className='six columns'),
                
                html.Div(children=[
                    html.Label('Select Country:', 
                            style={'textAlign':'center'}),

                    dcc.Dropdown(
                            id='countries_dropdown',
                            options=[],
                            value=None
                            )
                ], className='six columns')
            ], className='row'
            ), 
            
            html.Div(children=[
                html.Div(children=[
                    dcc.Graph(
                            id='co2_emission',
                            figure={}
                            )
                    ], className='six columns'),

                html.Div(children=[
                dcc.Graph(
                        id='graph1',
                        figure={}
                        )
                    ], className='six columns')
            ], className='row'
            ),

            html.Div(children=[
                

                html.Div(children=[
                dcc.Graph(
                        id='most_countries_co2',
                        figure=co2_most
                        )
                    ], className='six columns'), 
                html.Div(children=[
                    dcc.Graph(
                            id='all_countries_co2',
                            figure=sunBurst
                            )
                    ], className='six columns')
            ], className='row'
            )
    ]
)

# Callbacks
# For Dependent dropdown
@app.callback(
    Output('countries_dropdown', 'options'),
    Input('dropdown1', 'value'),
)
def get_countries_option(dropdown1):
    df = df_co2[df_co2.Region == dropdown1]
    return [{'label':i, 'value':i} for i in df['Country'].unique()]
    
# For Co2 line plot with years  
@app.callback(
    Output(component_id='co2_emission', component_property='figure'),
    Input(component_id='countries_dropdown', component_property='value'),
    Input(component_id='dropdown1', component_property='value')
)
def CountriesCo2Emission(countries_dropdown, dropdown1):
    
    if countries_dropdown == None and (dropdown1 == None or dropdown1 == 'None'):
        co2_emission = px.line(df_co2.groupby(['Year']).mean().reset_index(),
                        x="Year", 
                        y="Co2_Emission", 
                        title='Global Co2_Emission mean over years (1995 : 2017)')

    elif countries_dropdown == None and dropdown1 != None:
        x = df_co2.groupby(['Region', 'Year']).mean().reset_index()
        co2_emission = px.line(x[x['Region'] == dropdown1],
                        x="Year", 
                        y="Co2_Emission", 
                        title='Co2_Emission mean in ' + dropdown1 + ' over years (1995 : 2017)')
    
    else:
        co2_emission = px.line(df_co2[df_co2['Country'] == countries_dropdown], 
                        x="Year", 
                        y="Co2_Emission", 
                        title='Co2_Emission in ' + countries_dropdown + ' over years (1995 : 2017)')

    return co2_emission

# For Temperature
@app.callback(
    Output(component_id='graph1', component_property='figure'),
    Input(component_id='countries_dropdown', component_property='value'),
    Input(component_id='dropdown1', component_property='value')
)
def update_my_region_figure(countries_dropdown, dropdown1):
    if countries_dropdown == None and (dropdown1 == None or dropdown1 == 'None'):
        fig = px.line(data_global, x='Year', y = 'AvgTemperature', title='Tempretature globally')

    elif countries_dropdown == None and dropdown1 != None:
        df_updated = data_region[data_region.Region == dropdown1]
        fig = px.line(df_updated, x='Year', y = 'AvgTemperature', title='Tempretature OF ' + dropdown1)
    
    elif countries_dropdown != None:
        df_updated = data_country[data_country.Country == countries_dropdown]
        fig =  px.line(df_updated, x='Year', y = 'AvgTemperature', title='Tempretature OF ' + countries_dropdown)

    return fig


app.run_server()