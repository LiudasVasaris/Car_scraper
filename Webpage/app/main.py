import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dash_app_graph import create_dash_app_graph
from utilities import get_dataframe_data

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/table", response_class=HTMLResponse)
def get_status():
    return get_dataframe_data()


# A bit odd, but the only way I've been able to get prefixing of the Dash app
# to work is by allowing the Dash/Flask app to prefix itself, then mounting
# it to root
dash_app_graph = create_dash_app_graph(requests_pathname_prefix="/graph/")
app.mount("/graph", WSGIMiddleware(dash_app_graph.server))


if __name__ == "__main__":
    uvicorn.run(app, port=80)
