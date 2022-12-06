import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse

from dash_app_graph import create_dash_app_graph
from utilities import get_dataframe_data, get_landing_page

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def landing_page():
    return get_landing_page()


@app.get("/table", response_class=HTMLResponse)
def get_status():
    return get_dataframe_data()


# A bit odd, but the only way I've been able to get prefixing of the Dash app
# to work is by allowing the Dash/Flask app to prefix itself, then mounting
# it to root
dash_app_graph = create_dash_app_graph(requests_pathname_prefix="/graph/")
app.mount("/graph", WSGIMiddleware(dash_app_graph.server))


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
