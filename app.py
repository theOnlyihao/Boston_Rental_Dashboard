"""
author: yihao
"""

import pandas as pd
import numpy as np
# import requests
# import csv
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.express as px

"""
This part of the code is used to use api to get the raw data
"""
# url = "https://realty-mole-property-api.p.rapidapi.com/rentalListings"

# querystring = {"city": "Boston", "state": "MA", "limit": "500"}

# headers = {
#     "X-RapidAPI-Key": "a1835bffc9msha6535bd3ed59d78p1a2967jsn085084e39768",
#     "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
# }

# response = requests.request("GET", url, headers=headers, params=querystring)

# csvheader = [
#     'Date', 'Days on Market (DOM)', 'Property_Type', 'Price', 'Address', 'Zip_Code']

# # print(response.text)
# myjson = response.json()
# data = []

# for x in myjson:
#     rental = [x['listedDate'], x['daysOnMarket'], x['propertyType'],
#               x['price'], x['formattedAddress'], x['zipCode']]
#     data.append(rental)

# # save data to csv file
# with open('boston_rental.csv', 'w', encoding='UTF8', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(csvheader)
#     writer.writerows(data)

bos_rental = pd.read_csv(
    "https://github.com/theOnlyihao/Boston_Rental_Dashboard/blob/main/boston_rental.csv")
bos_rental['Date'] = pd.to_datetime(bos_rental['Date'])
bos_rental['Date'] = bos_rental.Date.dt.strftime("%Y-%m-%d")
# bos_rental['Date'] = pd.to_datetime(bos_rental['Date'])
bos_rental['Zip_Code'] = bos_rental['Zip_Code'].apply(
    lambda x: '0' + str(x) if x < 10000 else str(x))
bos_rental.sort_values("Days on Market (DOM)", inplace=True)

# get the plots
chart1 = px.pie(bos_rental,
                values=bos_rental.groupby('Zip_Code')[
                    'Property_Type'].count(),
                names=bos_rental.sort_values(
                    'Zip_Code')['Zip_Code'].unique(),
                title='Real Estate Rental Numbers Based on Zip in Boston, MA',
                # text=bos_rental.groupby('Property_Type')[
                #     'Property_Type'].count(),
                height=600
                )

chart1.update(layout=dict(title=dict(x=0.5)))

chart2 = px.bar(
    bos_rental,
    x=bos_rental.sort_values('Zip_Code')['Zip_Code'].unique(),
    y=bos_rental.groupby('Zip_Code')['Price'].agg("mean"),
    labels={"x": "Zip Code", "y": "Average Price (USD)"},
    color=bos_rental.groupby('Zip_Code')['Price'].agg("mean"),
    color_continuous_scale=px.colors.sequential.Sunset,
    text=bos_rental.groupby('Zip_Code')['Price'].agg("mean").round(0),
    title="Average Price in each area in Boston, MA by zip code"
    # orientation="h"
)

chart2.update_layout(
    title=dict(x=0.5),  # set title in the center
    margin=dict(l=50, r=20, t=60, b=20),  # set margin of the chart
    paper_bgcolor="white"  # set the background color of the chart
)

chart2.update_xaxes(tickangle=-45)

chart2.update_traces(texttemplate="%{text:.2s}")


# def generate_table(dataframe, max_rows=10):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ])

# stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                # html.P(children="🏠", style={
                #        'fontSize': "30px", 'textAlign': 'center'}, className="header-emoji"),
                html.H1(
                    children="Boston Real Estate Rental Info", style={
                        'color': '#FFFFFF',
                        'font-size': '48px',
                        'font-weight': 'bold',
                        'text-align': 'center',
                        'margin': '0 auto'},
                    className="header-title",
                ),
                html.P(
                    children="This Dashboard is used to display the average rental price in each area (by zipcode)"
                    " and the number of rental real estates in Boston, MA",
                    # className="header-description",
                    style={'textAlign': 'center', 'color': '#FFFFFF',
                           'margin': '4px auto',
                           'text-align': 'center',
                           'max-width': '384px'}
                ),
            ],
            className="header",
            style={
                'background-color': '#d58b30',
                'height': '288px',
                'padding': '16px 0 0 0',
            }
        ),

        html.Div(
            children=[
                html.P(
                    children="You need to choose the property type that list below to check"
                    " the price and real eastate numbers that listed on market in each area",
                    style={'textAlign': 'center'}
                ),
                html.Div(children='Property type list:',
                         style={'textAlign': 'left'}),
                dcc.Dropdown(
                    id='property-filter',
                    options=[
                        {'label': Property, 'value': Property}
                        for Property in bos_rental.Property_Type.unique()
                    ],
                    value='Apartment',
                    clearable=False,
                    className='dropdown',
                ),
            ],
            className='menu',
        ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='pie',
                        figure=chart1,
                    ),
                    style={'width': '50%', 'display': 'inline-block'},
                ),
                html.Div(
                    children=dcc.Graph(
                        id='bar',
                        figure=chart2
                    ),
                    style={'width': '50%', 'display': 'inline-block'},
                ),
            ],
        ),

        html.Div(
            dash_table.DataTable(
                bos_rental.to_dict(orient='records'), [
                    {"name": i, "id": i} for i in bos_rental.columns],
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['Date', 'Region']
                ],

                style_as_list_view=True,
                id='table',
                page_size=10,

            ),
            style={'fontSize': '11', 'width': '99%',
                   'display': 'inline-block', 'overflowY': 'scroll'}
        ),

    ]
)


@ app.callback(
    Output("pie", "figure"),
    [
        Input("property-filter", "value"),
    ],
)
def update_pie(property_type):
    # property_filter = True  # get all categories if category is empty

    # if property_type:
    #     property_filter = (bos_rental.Property_Type == property_type)

    mask = (
        (bos_rental.Property_Type == property_type)
        # & property_filter
    )

    filtered_data = bos_rental.loc[mask, :]

    pie_chart_figure = px.pie(filtered_data,
                              values=filtered_data.groupby(
                                  'Zip_Code')['Property_Type'].count(),
                              names=filtered_data.sort_values(
                                  'Zip_Code')['Zip_Code'].unique(),
                              title='Real Estate Rental Numbers Based on Zip in Boston, MA',
                              height=600,
                              hole=.5)
    pie_chart_figure.update_traces(hoverinfo='label+percent', textinfo='value')
    pie_chart_figure.update(layout=dict(title=dict(x=0.5)))

    return pie_chart_figure


@ app.callback(
    # [
    Output("bar", "figure"),
    # Output("bar", "figure")
    # ],
    [
        Input("property-filter", "value"),
    ],
)
def update_bar(property_type):

    # category_filter = True  # get all categories if category is empty

    # if property_type:
    #     category_filter = (bos_rental.Property_Type == property_type)

    mask = (
        (bos_rental.Property_Type == property_type)
        # & category_filter
    )

    filtered_data = bos_rental.loc[mask, :]

    bar_fig = px.bar(
        filtered_data,
        x=filtered_data.sort_values('Zip_Code')['Zip_Code'].unique(),
        y=filtered_data.groupby('Zip_Code')['Price'].agg("mean"),
        labels={"x": "Zip Code", "y": "Average Price (USD)"},
        color=filtered_data.groupby('Zip_Code')['Price'].agg("mean"),
        color_continuous_scale=px.colors.sequential.Sunset,
        text=filtered_data.groupby('Zip_Code')['Price'].agg("mean").round(0),
        title="Average Price in each area in Boston, MA by zip code"
    )
    bar_fig.update_layout(
        title=dict(x=0.5), margin=dict(l=50, r=20, t=60, b=20), paper_bgcolor="white"
    )
    bar_fig.update_xaxes(tickangle=-45)

    bar_fig.update_traces(texttemplate="%{text:.2s}")

    # pie_chart_figure = px.pie(data_frame=filtered_data,
    #                           values=filtered_data['Property_Type'].unique(),
    #                           names='Zip_Code')

    return bar_fig  # pie_chart_figure


@app.callback(
    [Output("table", "data")],
    [
        Input("property-filter", "value"),
    ],
)
def update_table(property_type):
    filtered_data = bos_rental[bos_rental.Property_Type == property_type]
    return [filtered_data.to_dict(orient='record')]


if __name__ == "__main__":
    app.run_server(debug=True)
