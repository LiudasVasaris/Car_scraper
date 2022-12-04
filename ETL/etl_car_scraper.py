import datetime
import os
from typing import Tuple, List, Iterable

import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

from logger import LOGGER

BUCKET = "car-scraper-vu-bucket"
FOLDER = "output_files"


def scan_full_table(table) -> pd.DataFrame:
    """Preforms full scan of table in DynamoDB
    Args:
        table: dynamoDB table

    Returns:
        Pandas Dataframe with scanned table data
    """
    response = table.scan()
    yield from response["Items"]
    while response.get("LastEvaluatedKey"):
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        yield from response["Items"]


def extract_data() -> pd.DataFrame:
    """Extraction of raw data"""
    client_dynamo = boto3.resource("dynamodb")
    table = client_dynamo.Table("car_table")

    table_parts = list(scan_full_table(table))
    data = pd.DataFrame(table_parts)

    return data


def one_hot_encode(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """One hot encodes in the given list
    Args:
        df: df to encode
        columns: list of categorical columns to encode

    Returns: One hot encoded DataFrame
    """
    return pd.get_dummies(df, columns=columns)


def train_linear_model(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """Returns trained model, to find given target value
    Args:
        df: df for training
        target: target column to predict from df

    Returns: df with expected car values, and model
    """
    train_df = df.copy()
    model = LinearRegression()
    y = train_df[target]
    x = train_df.drop(columns=target, axis=1)

    model.fit(x, y)
    train_df["price_pred"] = model.predict(x)
    return train_df


def feature_transform_and_normalization(
    df: pd.DataFrame, features_to_norm: Iterable[str], date_features: List[str]
) -> Tuple[pd.DataFrame, dict]:

    transformed_df = df.copy()
    # Change feature types
    for feature in features_to_norm:
        if feature in date_features:
            transformed_df[feature] = (
                datetime.datetime.today()
                - pd.to_datetime(transformed_df[feature], format="%Y-%m")
            ).dt.days
        else:
            transformed_df[feature] = pd.to_numeric(
                transformed_df[feature], errors="raise"
            )
    # Standardize features
    scaler_dict = pd.DataFrame(
        [transformed_df.mean(numeric_only=True), transformed_df.std(numeric_only=True)],
        index=["mean", "std"],
    ).to_dict()
    for feature in features_to_norm:
        transformed_df[feature] = (
            transformed_df[feature] - scaler_dict[feature]["mean"]
        ) / scaler_dict[feature]["std"]

    return transformed_df, scaler_dict


def scale_back_price(trained_df, scalar_dict):
    df = trained_df.copy()
    df["true_price"] = (
        df["price"] * scalar_dict["price"]["std"] + scalar_dict["price"]["mean"]
    ).round()
    df["predicted_price"] = (
        (df["price_pred"] * scalar_dict["price"]["std"] + scalar_dict["price"]["mean"])
        .round()
        .clip(lower=0)
    )
    return df[["true_price", "predicted_price"]]


def transform_data(df: pd.DataFrame):
    """Transformation of raw data
    Args:
        df: DataFrame with raw data

    Returns:
    """
    features_to_use = [
        "docs",
        "steering_wheel",
        "consumption_road",
        "consumption_city",
        "consumption_mixed",
        "wheel_drive",
        "fuel",
        "brand",
        "kw",
        "doors",
        "milage",
        "defects",
        "year",
        "price",
        "engine",
        "body",
        "transmission",
    ]
    features_to_encode = [
        "steering_wheel",
        "wheel_drive",
        "fuel",
        "brand",
        "doors",
        "defects",
        "body",
        "transmission",
    ]
    features_to_normalize = set(features_to_use) - set(features_to_encode)

    norm_df, normalization_params = feature_transform_and_normalization(
        df, features_to_normalize, ["docs", "year"]
    )
    one_hot_df = one_hot_encode(norm_df[features_to_use], features_to_encode)

    return one_hot_df, normalization_params


def create_graph(final_df):
    scale_min = final_df.min(numeric_only=True).min()
    scale_max = final_df.max(numeric_only=True).max()
    fig = px.scatter(
        final_df,
        x="true_price",
        y="predicted_price",
        color="brand",
        hover_data=["model", "year", "docs"],
        custom_data=["url"],
    )
    fig.update_layout(
        yaxis_range=[scale_min, scale_max], xaxis_range=[scale_min, scale_max]
    )
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=scale_max,
        y1=scale_max,
        fillcolor="green",
        name="x=y",
    )

    fig = go.Figure(fig.data, fig.layout)

    return fig


def create_dataframe_html(dataframe: pd.DataFrame):
    main_cols = [
        "brand",
        "model",
        "year",
        "engine",
        "kw",
        "fuel",
        "milage",
        "docs",
        "transmission",
        "defects",
        "true_price",
        "predicted_price",
        "price_dif",
        "url",
    ]
    other_cols = list(set(dataframe.columns) - set(main_cols))
    df_to_use = dataframe[main_cols + other_cols]

    table_html = df_to_use.to_html(table_id="table", render_links=True, escape=False)
    html = f"""
    <html>
    <header>
        <link href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css" rel="stylesheet">
    </header>
    <body>
    {table_html}
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready( function () {{
            $('#table').DataTable({{
                // paging: true,    
                // scrollY: 400,
            }});
        }});
    </script>
    </body>
    </html>
    """
    return html


def prepare_final_df(initial_df, output_df):
    final_df = initial_df.join(output_df)
    final_df = final_df.astype({"true_price": "int", "predicted_price": "int"})
    final_df["price_dif"] = final_df["predicted_price"] - final_df["true_price"]
    return final_df.drop(columns="price").sort_values("price_dif", ascending=False)


def load_data(plotly_graph, dataframe_content):
    s3 = boto3.client("s3")
    graph_file = "car_graph.json"
    df_file = "dataframe_html.html"

    os.makedirs("tmp", exist_ok=True)

    # Write to temp memory
    plotly_graph.write_json(f"tmp/{graph_file}")
    open(f"tmp/{df_file}", "w", encoding="utf-8").write(dataframe_content)

    s3.upload_file(f"./tmp/{graph_file}", BUCKET, f"{FOLDER}/{graph_file}")
    s3.upload_file(f"./tmp/{df_file}", BUCKET, f"{FOLDER}/{df_file}")


def run_etl():
    LOGGER.info("ETL started")

    LOGGER.info("Extracting data")
    df = extract_data()

    LOGGER.info("Transforming data")
    transformed, scalar_dict = transform_data(df)
    trained_df = train_linear_model(transformed.fillna(0), "price")
    output_df = scale_back_price(trained_df, scalar_dict)
    final_df = prepare_final_df(df, output_df)

    graph = create_graph(final_df)
    df_html = create_dataframe_html(final_df)

    LOGGER.info("Loading data")
    load_data(graph, df_html)

    LOGGER.info("ETL finished")


if __name__ == "__main__":
    run_etl()
