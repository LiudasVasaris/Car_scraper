import webbrowser

import dash
import flask
import plotly
from dash.dependencies import Input, Output

from logger_webpage import LOGGER
from utilities import get_graph_data


def create_dash_app_graph(requests_pathname_prefix: str) -> dash.Dash:
    """Creates dash application
    Args:
        requests_pathname_prefix (): prefix to access app on server

    Returns: Dash app
    """
    # Create Figure
    def create_figure():
        graph_json = get_graph_data()
        fig = plotly.io.from_json(graph_json)
        fig.update_layout(yaxis_range=[0, 10000], xaxis_range=[0, 10000])
        fig.update_layout(
            dict(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=list(
                            [
                                dict(
                                    args=["visible", "legendonly"],
                                    label="Deselect All",
                                    method="restyle",
                                ),
                                dict(
                                    args=["visible", True],
                                    label="Select All",
                                    method="restyle",
                                ),
                            ]
                        ),
                        pad={"r": 10, "t": 10},
                        showactive=False,
                        x=1,
                        xanchor="right",
                        y=1.1,
                        yanchor="top",
                    ),
                ]
            )
        )
        return fig

    # create server and app
    server = flask.Flask(__name__)
    app = dash.Dash(
        __name__, server=server, requests_pathname_prefix=requests_pathname_prefix
    )
    app.scripts.config.serve_locally = False

    def serve_layout():
        """Allows for refresh each time page is opened"""
        return dash.html.Div(
            [
                dash.dcc.Graph(
                    id="fig",
                    figure=create_figure(),
                    style={"width": "90v", "height": "90vh"},
                ),
                dash.html.Div(id="debug"),
            ]
        )

    app.layout = serve_layout

    @app.callback(
        Output("debug", "children"),
        Input("fig", "clickData"),
    )
    def point_clicked(clickdata):
        if clickdata:
            webbrowser.open_new_tab(clickdata["points"][0]["customdata"][0])

    return app
