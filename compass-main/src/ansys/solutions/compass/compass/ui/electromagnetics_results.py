# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate

from ansys.saf2.client import UIClient
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)
from ansys.solutions.compass.compass.ui.components import InputRow, OutputRow
from ansys.solutions.compass.compass.solution.definition import CompassSolution
from ansys.solutions.compass.compass.solution.electromagnetics_results_step import (
    ElectromagneticsResultsStep,
)

# =================================================== [Functions] =================================================== #

# TODO: Refactor static/dynamic figure definition to a class
def create_time_series(dff, axis_type, title):
    dff = pd.DataFrame(dff)
    fig = px.scatter(dff, x="Time [ms]", y=dff.iloc[:, 1:].columns)
    fig.update_traces(mode="lines")
    fig.update_xaxes(showgrid=True)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(type="linear" if axis_type == "Linear" else "log")
    fig.update_layout(
        xaxis_title="Time [ms]",
        yaxis_title=title,
        legend=dict(title=None, x=0.99, y=0.99, xanchor="right", yanchor="top"),
    )
    fig.layout.plot_bgcolor = "#FFFFFF"
    fig.layout.paper_bgcolor = "#FFFFFF"
    fig.layout.xaxis.gridcolor = "#DCDCDC"
    fig.layout.yaxis.gridcolor = "#DCDCDC"
    return fig


# ===================================================== [Layout] ==================================================== #


def layout(step: ElectromagneticsResultsStep, electromagnetics_setup_step: ElectromagneticsSetupStep):

    if list(step.result_filenames.keys()) == []:
        step.write_csv_file_basenames_to_dict()

    graph_parameters_card = dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    InputRow(
                                        "dropdown",
                                        "graph-file-name",
                                        "File Name",
                                        "",
                                        step.selected_filename,
                                        list(step.result_filenames.keys()),
                                    ).get(),
                                ],
                                title="Graph Settings",
                                item_id="graph_settings",
                            ),
                            dbc.AccordionItem(
                                [
                                    OutputRow(
                                        "number",
                                        "efficiency",
                                        "Efficiency",
                                        "",
                                        electromagnetics_setup_step.simulation_results["efficiency"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "torque_avg",
                                        "Torque Average",
                                        "N.m",
                                        electromagnetics_setup_step.simulation_results["torque_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "rotor_loss_avg",
                                        "Rotor Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["rotor_loss_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "stator_loss_avg",
                                        "Stator Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["stator_loss_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "pm_i1_loss_avg",
                                        "PM_I1 Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["pm_i1_loss_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "pm_i2_loss_avg",
                                        "PM_I2 Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["pm_i2_loss_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "pm_o1_loss_avg",
                                        "PM_O1 Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["pm_o1_loss_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "pm_o2_loss_avg",
                                        "PM_O2 Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["pm_o2_loss_avg"],
                                    ).get(),
                                    OutputRow(
                                        "number",
                                        "stranded_loss_avg",
                                        "Stranded Loss Average",
                                        "W",
                                        electromagnetics_setup_step.simulation_results["stranded_loss_avg"],
                                    ).get(),
                                ],
                                title="Results Table",
                                item_id="results-table",
                            ),
                        ],
                        active_item=["graph_settings", "results-table"],
                        always_open=True,
                    )
                ],
                style={"display": "inline-block"},
            ),
            html.Div(id="results-message-out", style={"color": "red"}),
        ]
    )

    visualization_card = dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    dcc.Loading(
                                        id="loading-figure",
                                        type="circle",
                                        color="#ffb71b",
                                        children=[dcc.Graph(id=f"magnetics-graph")],
                                    ),
                                ],
                                title="Outputs graph",
                            )
                        ]
                    )
                ]
            )
        ]
    )

    return html.Div(
        [
            dcc.Markdown("""### Electromagnetics Results"""),
            dcc.Markdown(
                """##### Results generated from solving the 2D transient electromagnetics problem.
                """
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(graph_parameters_card, width=6),
                    dbc.Col(visualization_card, width=6),
                ],
                style={"padding": "20px"},
            ),
            dbc.Button(
                dbc.Spinner(children=html.Div(id="submit-loading-output"), size="sm"),
                id={"type": "submit-button", "index": "electromagnetics_results"},
                disabled=False,
                n_clicks=0,
                size="md",
                style={"background-color": "rgba(255, 183, 27, 1)", "border-color": "rgba(255, 183, 27, 1)"},
            ),
        ]
    )


# =================================================== [Callbacks] =================================================== #


@callback(
    Output("magnetics-graph", "figure"),
    Output("results-message-out", "children"),
    Input("graph-file-name", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_output_graph(file_name, pathname):
    project = UIClient[CompassSolution].get_project(pathname)
    step = project.steps.electromagnetics_results_step

    if file_name:
        fig = {"data": []}
        step.selected_filename = file_name
        step.write_content_from_selected_file_to_filereference()
        step.get_result_data()

        fig = create_time_series(step.results, "Linear", file_name)
        return fig, step.alert_message
    else:
        raise PreventUpdate
