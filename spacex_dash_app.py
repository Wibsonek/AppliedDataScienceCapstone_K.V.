# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import dash_table

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Creating list with launch sites for the drop down list
launch_sites_ar = spacex_df['Launch Site'].unique()

#Creating the options for the drop down 
options_drop_down_ar = [{'label': i, 'value': i} for i in launch_sites_ar]
options_drop_down_ar.insert(0,{'label': 'All Sites', 'value': 'ALL'})



# Creating default charts
default_pie_chart = px.pie(spacex_df, values='class', names='Launch Site', title='Total Success Launches by Site')
default_scatter_chart = px.scatter(spacex_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    dcc.Dropdown(
                                        id='site_dropdown'
                                        , options=options_drop_down_ar
                                        , value='ALL'
                                        , placeholder="Select a Launch Site here"
                                        , searchable=True
                                        , style={'width':'80%', 'padding':'3px', 'font-size':'20px', 'text-align-last':'center'}
                                    )
                                ])

                                , html.Br()

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                , html.Div(
                                    dcc.Graph(id='success-pie-chart', figure=default_pie_chart)
                                )
                                , html.Br()
                                , html.Div(['Initial View - ALL'], id='callback_test')
                                , html.Br()

                                , html.P("Payload range (Kg):")

                                # TASK 3: Add a slider to select payload range
                                , dcc.RangeSlider(
                                    id='payload-slider'
                                    , min=0
                                    , max=10000
                                    , step=100
                                    , value=[min_payload, max_payload]
                                    , marks={
                                        0: '0'
                                        , 2500: '2500'
                                        , 5000: '5000'
                                        , 7500: '7500'
                                        , 10000: '10000'
                                    }
                                )

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                , html.Div(
                                    dcc.Graph(
                                        id='success-payload-scatter-chart'
                                        , figure=default_scatter_chart
                                    )
                                ),

                            ])
        

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure')
    , Input(component_id='site_dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(
            filtered_df
            , values='class'
            , names= 'Launch Site'
            , title = 'Total Success Launches By Site'
        )
        return fig

    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_df = filtered_df.groupby(['Launch Site', 'class']).size().reset_index()
        filtered_df.rename(columns={0:'class count'}, inplace=True)
        fig = px.pie(
            filtered_df
            , values='class count'
            , names= 'class'
            , title = f'Total Success Launches for Site {entered_site}'
        )    
        return fig 


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure')
    , [
        Input(component_id='site_dropdown', component_property='value')
        , Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(entered_site, slider_range):

    filtered_df = spacex_df
    
    #add mask for the slider
    low, high = slider_range
    mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df[mask]
            , x='Payload Mass (kg)'
            , y='class'
            , color='Booster Version Category'
        )
        return fig
    else:
        filtered_df = filtered_df[mask]
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_df = filtered_df.groupby(['Launch Site', 'Payload Mass (kg)', 'Booster Version Category','class']).size().reset_index()
        filtered_df.rename(columns={0:'class count'}, inplace=True)
        fig = px.scatter(
            filtered_df
            , x='Payload Mass (kg)'
            , y='class'
            , color='Booster Version Category'
        )
        return fig 


# Run the app
if __name__ == '__main__':
    app.run_server()


    #Questions:

    #1: Which site has the largest successful launches?
    # VAFB SLC-4E with 9600 kg
    #2: Which site has the highest launch success rate?
    # CCAFS SLC-40 with 42.9%
    #3: Which payload range(s) has the highest launch success rate?
    # 2 - 4 kg*10^3
    #4: Which payload range(s) has the lowest launch success rate?
    # 6 - 8 and kg * 10^3
    #5: Which F9 Booster version (v1.0, v1.1, FT, B4, B5, etc.) has the highest launch success rate?
    # FT with 14 to 7