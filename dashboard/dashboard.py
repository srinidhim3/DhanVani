import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import plotly.express as px
from wordcloud import WordCloud
import base64
from io import BytesIO

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

API_URL = "http://localhost:8000/articles"

def fetch_data(sentiment=None, source=None, published=None):
    params = {}
    if sentiment:
        params["sentiment_label"] = sentiment
    if source:
        params["source"] = source
    if published:
        params["published"] = published

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        print("API error:", e)
        return pd.DataFrame()

app.layout = dbc.Container([
    dbc.NavbarSimple(brand="DhanVani - Financial News Sentiment Engine", color="primary", dark=True),

    dbc.Card([
        dbc.CardHeader("Filters"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Sentiment"),
                    dcc.Dropdown(
                        id="sentiment-filter",
                        options=[
                            {"label": "All", "value": ""},
                            {"label": "Positive", "value": "positive"},
                            {"label": "Neutral", "value": "neutral"},
                            {"label": "Negative", "value": "negative"},
                        ],
                        value="",
                        placeholder="Select Sentiment",
                        clearable=False,
                        multi=False,
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Source"),
                    dcc.Dropdown(
                        id="source-filter",
                        options=[
                            {"label": "All", "value": ""},
                            {"label": "Economic Times", "value": "Economic Times"},
                            {"label": "Moneycontrol", "value": "Moneycontrol"},
                        ],
                        value="",
                        placeholder="Select Source",
                        clearable=False,
                        multi=False,
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Published Date"),
                    dcc.Input(
                        id="date-filter",
                        type="text",
                        placeholder="YYYY-MM-DD"
                    ),
                ], width=4),
            ])
        ])
    ], className="my-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='sentiment-pie-chart'), width=6),
        dbc.Col(dcc.Graph(id='articles-bar-chart'), width=6),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H5("Article Table"),
            dash_table.DataTable(
                id='news-table',
                columns=[
                    {"name": "published", "id": "published"},
                    {"name": "source", "id": "source"},
                    {"name": "sentiment", "id": "sentiment_label"},
                    {"name": "title", "id": "title"},
                    {"name": "url", "id": "url"},
                ],
                page_size=10,
                style_cell={"textAlign": "left", "whiteSpace": "normal", "height": "auto"},
                style_table={"overflowX": "auto"},
                style_header={"fontWeight": "bold"},
            )
        ])
    ]),

    dbc.Row([
    dbc.Col([
        html.H4("Frequent Words in News Articles"),
        html.Img(id='wordcloud-image', style={"width": "50%", "height": "auto"})
    ], width=12)
])

], fluid=True)


@app.callback(
    [Output("sentiment-pie-chart", "figure"),
     Output("articles-bar-chart", "figure"),
     Output("news-table", "data"),
     Output("wordcloud-image", "src")],
    [
        Input("sentiment-filter", "value"),
        Input("source-filter", "value"),
        Input("date-filter", "value"),
    ],
)
def update_charts(sentiment, source, date):
    df = fetch_data()

    if sentiment and sentiment != "":
        df = df[df["sentiment_label"] == sentiment]
    if source and source != "":
        df = df[df["source"] == source]
    if date:
        df = df[df["published"].str.startswith(date)]


    if df.empty:
        pie = px.pie(title="No Data Available")
        bar = px.bar(title="No Data Available")
        return pie, bar, []

    # Pie Chart: Sentiment Distribution
    all_sentiments = ["positive", "neutral", "negative"]
    sentiment_counts = df["sentiment_label"].value_counts().reindex(all_sentiments, fill_value=0).reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    # Pie chart with soothing colors
    color_map = {
        "positive": "#82ca9d",  # soft green
        "neutral": "#a9a9a9",   # soft gray
        "negative": "#f08080",  # soft red
    }
    pie = px.pie(
        sentiment_counts,
        names="sentiment",
        values="count",
        title="Sentiment Distribution",
        color="sentiment",
        color_discrete_map=color_map
    )

    # Bar Chart: Articles per Day
    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    articles_per_day = df.groupby(df["published"].dt.date).size().reset_index(name="count")
    bar = px.bar(
        articles_per_day,
        x="published",
        y="count",
        title="Number of Articles per Day"
    )

    # Word Cloud
    text = " ".join(df["title"].dropna().tolist())
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="viridis"  # Soothing color map
    ).generate(text)

    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    encoded_img = base64.b64encode(img.read()).decode()
    wordcloud_src = f"data:image/png;base64,{encoded_img}"


    return pie, bar, df.to_dict("records"), wordcloud_src

if __name__ == "__main__":
    app.run(debug=True)
