import boto3

BUCKET = "car-scraper-vu-bucket"
DATAFRAME_FILE = "output_files/dataframe_html.html"
GRAPH_FILE = "output_files/car_graph.json"

# TODO cache function
def read_s3_file_to_memory(file_path):
    """Reads file to memory from s3
    Args:
        file_path: file location on s3 bucket

    Returns: file contents
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(BUCKET)
    return bucket.Object(file_path).get()["Body"].read().decode("utf-8")


def get_graph_data():
    """Gets graph data from s3 for dash app"""
    return read_s3_file_to_memory(GRAPH_FILE)


def get_dataframe_data():
    """Gets dataframe data from s3 for flask"""
    return read_s3_file_to_memory(DATAFRAME_FILE)

def get_landing_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>My Website</title>
        <link rel="stylesheet" href="./style.css">
        <link rel="icon" href="./favicon.ico" type="image/x-icon">
      </head>
      <body>
        <main>
            <h1>Car price evaluator</h1>
    
            <p>This app reads data from autoplius.lt
                and evaluates car prices using a linear regression model</p>
    
            <p>Visit path <a href="/table"><b>/table</b></a>
                to see table with information about cars and prices </p>
    
            <p>Visit path <a href="/graph"><b>/graph</b></a>
                to see visual car evaluation graph</p>
    
        </main>
        <script src="index.js"></script>
      </body>
    </html>
    """