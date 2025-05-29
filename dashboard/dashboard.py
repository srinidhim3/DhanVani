import dash
from dash import dcc, html, Input, Output
from dash import dash_table
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import plotly.express as px

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Function to fetch data from the database
def fetch_data():
    conn = sqlite3.connect("data/db.sqlite")
    df = pd.read_sql_query("SELECT * FROM raw_articles", conn)
    conn.close()
    return df


# Layout of the app
app.layout = dbc.Container(
    [
        dbc.NavbarSimple(
            brand="DhanVani - Financial News Sentiment Engine",
            color="primary",
            dark=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Filters"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label("Sentiment Label"),
                                                        dcc.Dropdown(
                                                            id="sentiment-filter",
                                                            options=[
                                                                {
                                                                    "label": "Positive",
                                                                    "value": "positive",
                                                                },
                                                                {
                                                                    "label": "Neutral",
                                                                    "value": "neutral",
                                                                },
                                                                {
                                                                    "label": "Negative",
                                                                    "value": "negative",
                                                                },
                                                            ],
                                                            multi=False,
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label("Source"),
                                                        dcc.Dropdown(
                                                            id="source-filter",
                                                            options=[
                                                                {
                                                                    "label": "Economic Times",
                                                                    "value": "Economic Times",
                                                                },
                                                            ],
                                                            multi=False,
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label("Published Date"),
                                                        dcc.Input(
                                                            id="date-filter",
                                                            type="text",
                                                            placeholder="YYYY-MM-DD",
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        )
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row([
            dbc.Col([dcc.Graph(id='sentiment-pie-chart')], width=6),
            dbc.Col([dcc.Graph(id='articles-bar-chart')], width=6)
        ])
    ]
)


# Callback to update the charts based on filters
@app.callback(
    [Output("sentiment-pie-chart", "figure"), Output("articles-bar-chart", "figure")],
    [
        Input("sentiment-filter", "value"),
        Input("source-filter", "value"),
        Input("date-filter", "value"),
    ],
)
def update_charts(sentiment_filter, source_filter, date_filter):
    df = fetch_data()

    if sentiment_filter:
        df = df[df["sentiment_label"] == sentiment_filter]
    if source_filter:
        df = df[df["source"] == source_filter]
    if date_filter:
        df = df[df["published"].str.startswith(date_filter)]

    # Sentiment Pie Chart
    sentiment_counts = df["sentiment_label"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    pie_chart = px.pie(
        sentiment_counts,
        names="sentiment",
        values="count",
        title="Sentiment Distribution",
    )

    # Articles Bar Chart
    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    articles_per_day = (
        df.groupby(df["published"].dt.date).size().reset_index(name="count")
    )
    bar_chart = px.bar(
        articles_per_day, x="published", y="count", title="Number of Articles per Day"
    )

    return pie_chart, bar_chart


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
