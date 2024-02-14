import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go

# Read Data
covid_clean_data = pd.read_csv("covid_19_clean_complete.csv")
country_wise_data = pd.read_csv("country_wise_latest.csv")
day_wise_data = pd.read_csv("day_wise.csv")
full_grouped_data = pd.read_csv("full_grouped.csv")
worldometer_data = pd.read_csv("worldometer_data.csv")

print("covid_data: ", covid_clean_data.shape)
print("check nulls in covid_data: ")
print(covid_clean_data.isnull().sum())
print("get info of covid_data: ")
print(covid_clean_data.info)
print("get statistics and description of covid_data: ")
print(covid_clean_data.describe().T)

covid_clean_data = covid_clean_data.drop(columns=['Province/State'])

print("country_wise_data: ", country_wise_data.shape)
print("check nulls in country_wise_data: ")
print(country_wise_data.isnull().sum())
print("get info of country_wise_data: ")
print(country_wise_data.info)
print("get statistics and description of country_wise_data: ")
print(country_wise_data.describe().T)

print("worldometer_data: ", worldometer_data.shape)
print("check nulls in worldometer_data: ")
print(worldometer_data.isnull().sum())
print("get info of worldometer_data: ")
print(worldometer_data.info)
print("get statistics and description of worldometer_data: ")
print(worldometer_data.describe().T)

worldometer_data_num_cols = ['NewCases', 'NewDeaths', 'NewRecovered', 'Serious,Critical', 'TotalDeaths', 'Tests/1M pop',
                             'Deaths/1M pop', 'Tot Cases/1M pop', 'TotalTests', 'ActiveCases', 'TotalRecovered']
median_values = worldometer_data[worldometer_data_num_cols].median()
worldometer_data[worldometer_data_num_cols] = worldometer_data[worldometer_data_num_cols].fillna(median_values)

region_mode = worldometer_data['WHO Region'].mode()[0]
continent_mode = worldometer_data['Continent'].mode()[0]
population_mode = worldometer_data['Population'].mode()[0]

worldometer_data['WHO Region'] = worldometer_data['WHO Region'].fillna(region_mode)
worldometer_data['Continent'] = worldometer_data['Continent'].fillna(continent_mode)
worldometer_data['Population'] = worldometer_data['Population'].fillna(population_mode)

print(worldometer_data.isnull().sum())

print("day_wise_data: ", day_wise_data.shape)
print("check nulls in day_wise_data: ")
print(day_wise_data.isnull().sum())
print("get info of day_wise_data: ")
print(day_wise_data.info)
print("get statistics and description of day_wise_data: ")
print(day_wise_data.describe().T)

print("full_grouped_data: ", full_grouped_data.shape)
print("check nulls in full_grouped_data: ")
print(full_grouped_data.isnull().sum())
print("get info of full_grouped_data: ")
print(full_grouped_data.info)
print("get statistics and description of full_grouped_data: ")
print(full_grouped_data.describe().T)

# changing the format of date
full_grouped_data["Date"] = pd.to_datetime(full_grouped_data["Date"], format="%Y-%m-%d")
print(full_grouped_data.info())
day_wise_data["Date"] = pd.to_datetime(day_wise_data["Date"], format="%Y-%m-%d")
print(day_wise_data.info())

# Check Duplication
print(covid_clean_data.duplicated().sum())
print(full_grouped_data.duplicated().sum())
print(day_wise_data.duplicated().sum())
print(worldometer_data.duplicated().sum())
print(country_wise_data.duplicated().sum())

# Merge Data for Data Integrity
commons = ['WHO Region', 'Recovered', 'Country/Region', 'Deaths', 'Active', 'Confirmed']
merged_covid_country = pd.merge(covid_clean_data, country_wise_data, on=commons, how='inner')
print(merged_covid_country.head())

total_confirmed = merged_covid_country['Confirmed'].sum()
total_Recovered = merged_covid_country['Recovered'].sum()
total_Deaths = merged_covid_country['Deaths'].sum()
total_Active = merged_covid_country['Active'].sum()

total_new_confirmed = merged_covid_country['New cases'].sum()
total_new_Recovered = merged_covid_country['New recovered'].sum()
total_new_Deaths = merged_covid_country['New deaths'].sum()

# Group and melt the DataFrame
case_time = full_grouped_data.groupby('Date')[['Confirmed', 'Recovered', 'Deaths', 'Active']].sum().reset_index()
case_time = case_time.melt(id_vars="Date", value_vars=['Confirmed', 'Recovered', 'Deaths', 'Active'],
                           var_name='Case', value_name='Count')

df_target_recover = (full_grouped_data.groupby('Country/Region')[['Recovered', 'Deaths', 'Confirmed']]
                     .sum().reset_index())
print(df_target_recover.sort_values(by='Recovered', ascending=False).head())

# grouping country/region wise confirmations
confirmed_cases = pd.DataFrame(merged_covid_country.groupby('Country/Region')['Confirmed'].sum())

confirmed_cases['Country/Region'] = confirmed_cases.index
df_confirmedcases = confirmed_cases[['Country/Region', 'Confirmed']]


def update_coronavirus_map():
    fig = px.choropleth(merged_covid_country,
                        locations="Country/Region",
                        locationmode='country names',
                        color="Confirmed",
                        hover_name="Country/Region",
                        hover_data=["Confirmed"],
                        color_continuous_scale="Purples")

    return fig


# Calculate daily trends and daily changes in cases
daily_trends = full_grouped_data.groupby('Date')[['Confirmed', 'Recovered', 'Deaths']].sum().reset_index()
daily_trends['NewConfirmed'] = daily_trends['Confirmed'].diff()
daily_trends['NewRecovered'] = daily_trends['Recovered'].diff()
daily_trends['NewDeaths'] = daily_trends['Deaths'].diff()

# Create line charts for daily trends
fig_daily_trends = go.Figure()
fig_daily_trends.add_trace(go.Scatter(x=daily_trends['Date'], y=daily_trends['Confirmed'], mode='lines',
                                      name='Confirmed', line=dict(color='#AC87C5')))
fig_daily_trends.add_trace(go.Scatter(x=daily_trends['Date'], y=daily_trends['Recovered'], mode='lines',
                                      name='Recovered', line=dict(color='#E0AED0')))
fig_daily_trends.add_trace(go.Scatter(x=daily_trends['Date'], y=daily_trends['Deaths'], mode='lines',
                                      name='Deaths', line=dict(color='#944E63')))
fig_daily_trends.update_layout(title='Daily Trends of Confirmed, Recovered, and Death Cases',
                               xaxis_title='Date', yaxis_title='Number of Cases')

# Create line charts for daily changes
fig_daily_changes = go.Figure()
fig_daily_changes.add_trace(go.Scatter(x=daily_trends['Date'], y=daily_trends['NewConfirmed'], mode='lines',
                                       name='New Confirmed', line=dict(color='#AC87C5')))
fig_daily_changes.add_trace(go.Scatter(x=daily_trends['Date'], y=daily_trends['NewRecovered'], mode='lines',
                                       name='New Recovered', line=dict(color='#E0AED0')))
fig_daily_changes.add_trace(go.Scatter(x=daily_trends['Date'], y=daily_trends['NewDeaths'], mode='lines',
                                       name='New Deaths', line=dict(color='#944E63')))
fig_daily_changes.update_layout(title='Daily Changes in Confirmed, Recovered, and Death Cases',
                                xaxis_title='Date', yaxis_title='Daily Change')

app = dash.Dash(__name__)

country_options = [{'label': country, 'value': country} for country in df_target_recover['Country/Region']]

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H3("Coronavirus Outbreak Global Cases Monitor", style={"margin-bottom": "0px", 'color': 'white'}),
                html.H5(
                    "This dashboard offers real-time COVID-19 data and visualizations for a comprehensive "
                    "overview of the global situation.",
                    style={"margin-top": "0px", 'color': '#FFD1E3'}),
            ])
        ], className="one-half column", id="title"),
    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

    html.Div([
        html.Div([
            html.H6(children='Confirmed Cases',
                    style={'textAlign': 'center', 'color': 'white'}),
            html.P(total_confirmed,
                   style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 40}),
            html.P('new:  ' + f"{total_new_confirmed}",
                   style={'textAlign': 'center', 'color': '#FFD1E3', 'fontSize': 15, 'margin-top': '-18px'})
        ], className="card_container three columns"),

        html.Div([
            html.H6(children='Death Cases',
                    style={'textAlign': 'center', 'color': 'white'}),
            html.P(total_Deaths,
                   style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 40}),
            html.P('new:  ' + f"{total_new_Deaths}",
                   style={'textAlign': 'center', 'color': '#FFD1E3', 'fontSize': 15, 'margin-top': '-18px'})
        ], className="card_container three columns"),

        html.Div([
            html.H6(children='Recovered Cases',
                    style={'textAlign': 'center', 'color': 'white'}),
            html.P(total_Recovered,
                   style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 40}),
            html.P('new:  ' + f"{total_new_Recovered}",
                   style={'textAlign': 'center', 'color': '#FFD1E3', 'fontSize': 15, 'margin-top': '-18px'})
        ], className="card_container three columns"),

        html.Div([
            html.H6(children='Active Cases',
                    style={'textAlign': 'center', 'color': 'white'}),
            html.P(total_Active,
                   style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 40})
        ], className="card_container three columns"),
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='country_dropdown',
                options=country_options,
                placeholder='Select a country...',
                value='Afghanistan'
            ),
        ], className="card_container twelve columns"),
    ], className="row"),

    html.Div([
        html.Div(id='selected_country_label')
    ], className="row"),

    html.Div([
        html.Div(id='selected_country_stats')
    ], className="row"),
    html.Div([
        html.Div(id='visualization1', className="vis1"),
        html.Div(id='visualization2', className="vis2"),
    ], className="row_container"),
    html.Div([
        dcc.Graph(figure=fig_daily_trends, className='daily_trends'),
        dcc.Graph(figure=fig_daily_changes, className='daily_changes')
    ], className="daily"),
    html.Div([
        html.Div([
            html.P('Latest Coronavirus Outbreak Map', className='fix_label',
                   style={'color': 'white', 'text-align': 'center', 'margin-bottom': '15px'}),
            dcc.Graph(id="map", figure=update_coronavirus_map())
        ], className="create_container1 twelve columns"),
    ], className="row flex-display"),

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})


def generate_pie_chart(country_data, selected_country):
    labels = ['Confirmed', 'Recovered', 'Deaths']
    values = [country_data['Confirmed'].sum(), country_data['Recovered'].sum(), country_data['Deaths'].sum()]
    colors = ['#AC87C5', '#E0AED0', '#FFE5E5']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
    fig.update_layout(title_text=f'Distribution of Cases in {selected_country}')
    return dcc.Graph(figure=fig)


def generate_time_series_plot(country_data, selected_country):
    country_data = country_data.groupby('Date').sum().reset_index()
    colors = ['#1F2544', '#561C24', '#D04848']
    fig = go.Figure([go.Bar(x=country_data['Date'], y=country_data['Confirmed'], name='Confirmed',
                            marker=dict(color=colors[0])),
                     go.Bar(x=country_data['Date'], y=country_data['Recovered'], name='Recovered',
                            marker=dict(color=colors[1])),
                     go.Bar(x=country_data['Date'], y=country_data['Deaths'], name='Deaths',
                            marker=dict(color=colors[2]))
                     ]
                    )
    fig.update_layout(title_text=f'Trend of Cases in {selected_country}', xaxis_title='Date',
                      yaxis_title='Number of Cases')
    return dcc.Graph(figure=fig)


@app.callback(
    [Output('selected_country_label', 'children'),
     Output('selected_country_stats', 'children'),
     Output('visualization1', 'children'),
     Output('visualization2', 'children')],
    [Input('country_dropdown', 'value')]
)
def update_country_stats(selected_country):
    if selected_country:
        merged_data = pd.merge(df_target_recover, full_grouped_data[['Country/Region', 'Date']],
                               on='Country/Region', how='left')
        country_data = merged_data[merged_data['Country/Region'] == selected_country]
        latest_date = country_data['Date'].max()
        country_latest_data = country_data[country_data['Date'] == latest_date]

        total_confirmed = country_latest_data['Confirmed'].sum()
        total_deaths = country_latest_data['Deaths'].sum()
        total_recovered = country_latest_data['Recovered'].sum()

        label = html.P(f"Statistics for: {selected_country}",
                       style={'textAlign': 'center', 'color': '#FFD1E3', 'fontSize': 20})

        total_confirmed_text = html.P(f"Confirmed Cases: {total_confirmed:,}",
                                      style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 20})
        total_deaths_text = html.P(f"Death Cases: {total_deaths:,}",
                                   style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 20})
        total_recovered_text = html.P(f"Recovered Cases: {total_recovered:,}",
                                      style={'textAlign': 'center', 'color': '#A367B1', 'fontSize': 20})

        pie_chart = generate_pie_chart(country_latest_data, selected_country)
        time_series_plot = generate_time_series_plot(country_data, selected_country)

        return label, [total_confirmed_text, total_deaths_text, total_recovered_text], pie_chart, time_series_plot
    else:
        return [], [], [], []


if __name__ == '__main__':
    app.run_server(debug=True)
