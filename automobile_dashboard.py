#!/usr/bin/env python3
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

DATA_URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv'

# Load the data once at startup
data = pd.read_csv(DATA_URL)

app = dash.Dash(__name__)
app.title = 'Automobile Sales Statistics Dashboard'

year_list = sorted(data['Year'].unique())

app.layout = html.Div([
    html.H1('Automobile Sales Statistics Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    html.Div([
        html.Label('Select Statistics:'),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type',
            value='Yearly Statistics',
            style={
                'width': '80%',
                'padding': '3px',
                'fontSize': 20,
                'textAlignLast': 'center'
            }
        )
    ]),
    html.Div([
        dcc.Dropdown(
            id='select-year',
            options=[{'label': str(i), 'value': i} for i in year_list],
            placeholder='Select year'
        )
    ]),
    html.Div(id='output-container', className='chart-grid',
             style={'display': 'flex', 'flexDirection': 'column'})
])


@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def toggle_year_dropdown(report_type):
    return report_type != 'Yearly Statistics'


@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'),
     Input('select-year', 'value')]
)
def update_output(report_type, selected_year):
    if report_type == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                                          title='Average Automobile Sales fluctuation over Recession Period'))

        avg_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        chart2 = dcc.Graph(figure=px.bar(avg_sales, x='Vehicle_Type', y='Automobile_Sales',
                                         title='Average Number of Vehicles Sold by type over Recession Period'))

        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        chart3 = dcc.Graph(figure=px.pie(exp_rec, values='Advertising_Expenditure',
                                         names='Vehicle_Type',
                                         title='Total Expenditure Share by Vehicle Type over Recession Period'))

        unemp_data = recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].mean().reset_index()
        chart4 = dcc.Graph(figure=px.bar(unemp_data, x='Vehicle_Type', y='Automobile_Sales',
                                         color='unemployment_rate',
                                         labels={'unemployment_rate': 'Unemployment Rate',
                                                 'Automobile_Sales': 'Average Automobile Sales'},
                                         title='Effect of Unemployment Rate on Vehicle Type and Sales'))

        return [
            html.Div([chart1, chart2], style={'display': 'flex'}),
            html.Div([chart3, chart4], style={'display': 'flex'})
        ]

    elif report_type == 'Yearly Statistics' and selected_year:
        yearly_data = data[data['Year'] == selected_year]

        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales',
                                          title='Automobile Sales over the years'))

        mas = data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        chart2 = dcc.Graph(figure=px.line(mas, x='Month', y='Automobile_Sales',
                                          title='Total Monthly Automobile Sales'))

        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        chart3 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                                         title=f'Average Vehicles Sold by Vehicle Type in {selected_year}'))

        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        chart4 = dcc.Graph(figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                                         title='Total Advertisement Expenditure for each vehicle'))

        return [
            html.Div([chart1, chart2], style={'display': 'flex'}),
            html.Div([chart3, chart4], style={'display': 'flex'})
        ]
    else:
        return []


if __name__ == '__main__':
    app.run_server(debug=True)
