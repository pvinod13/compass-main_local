# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import dash_bootstrap_components as dbc

from dash import html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import dcc, html, Input, Output, State, callback

from ansys.saf2.client import UIClient
from ansys.solutions.compass.compass.solution.definition import CompassSolution
from ansys.solutions.compass.compass.solution.thermal_results_step import ThermalResultsStep
from ansys.solutions.compass.compass.solution.thermal_setup_step import ThermalSetupStep
from ansys.solutions.compass.compass.ui.components import InputRow, OutputRow

# ===================================================== [Layout] ==================================================== #


def layout(step: ThermalResultsStep, thermal_setup_step: ThermalSetupStep):

    graph_parameters_card = dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # TODO: time computation
                                    OutputRow(
                                        "label_list", "all_bodies", "Temperature", "", None, ["Min", "Max", "Average"]
                                    ).get(),
                                    html.Br(),
                                    OutputRow(
                                        "number_list",
                                        "all_bodies",
                                        "All Bodies",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["all_bodies"]["Minimum"],
                                            thermal_setup_step.thermal_results["all_bodies"]["Maximum"],
                                            thermal_setup_step.thermal_results["all_bodies"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "rotor",
                                        "Rotor",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["rotor"]["Minimum"],
                                            thermal_setup_step.thermal_results["rotor"]["Maximum"],
                                            thermal_setup_step.thermal_results["rotor"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "stator",
                                        "Stator",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["stator"]["Minimum"],
                                            thermal_setup_step.thermal_results["stator"]["Maximum"],
                                            thermal_setup_step.thermal_results["stator"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "pm",
                                        "PM",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["pm"]["Minimum"],
                                            thermal_setup_step.thermal_results["pm"]["Maximum"],
                                            thermal_setup_step.thermal_results["pm"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "windings",
                                        "Windings",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["windings"]["Minimum"],
                                            thermal_setup_step.thermal_results["windings"]["Maximum"],
                                            thermal_setup_step.thermal_results["windings"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "teeth",
                                        "Teeth",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["teeth"]["Minimum"],
                                            thermal_setup_step.thermal_results["teeth"]["Maximum"],
                                            thermal_setup_step.thermal_results["teeth"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "shaft",
                                        "Shaft",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["shaft"]["Minimum"],
                                            thermal_setup_step.thermal_results["shaft"]["Maximum"],
                                            thermal_setup_step.thermal_results["shaft"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "bearings",
                                        "Bearings",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["bearings"]["Minimum"],
                                            thermal_setup_step.thermal_results["bearings"]["Maximum"],
                                            thermal_setup_step.thermal_results["bearings"]["Average"],
                                        ],
                                    ).get(),
                                    OutputRow(
                                        "number_list",
                                        "housings",
                                        "Housings",
                                        "°C",
                                        row_list=[
                                            thermal_setup_step.thermal_results["housings"]["Minimum"],
                                            thermal_setup_step.thermal_results["housings"]["Maximum"],
                                            thermal_setup_step.thermal_results["housings"]["Average"],
                                        ],
                                    ).get(),
                                    html.Div(id="results-button-alert", style={"color": "red"}),
                                ],
                                title="Results",
                                item_id="results-accordion",
                            )
                        ],
                        active_item=["results-accordion"],
                        always_open=True,
                    )
                ],
                style={"display": "inline-block"},
            ),
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
                                    InputRow(
                                        "dropdown",
                                        "part-name",
                                        "Part Selection",
                                        "",
                                        "All Bodies",
                                        [
                                            "All Bodies",
                                            "Rotor",
                                            "Stator",
                                            "PM",
                                            "Windings",
                                            "Teeth",
                                            "Shaft",
                                            "Bearings",
                                            "Housings",
                                        ],
                                    ).get(),
                                    InputRow(
                                        "dropdown",
                                        "visu-type",
                                        "Type of Visualization",
                                        "",
                                        "ISO Image",
                                        ["ISO Image", "YZ Image", "XZ Image", "3D Result"],
                                    ).get(),
                                    html.Br(),
                                    dbc.CardImg(id="results-image", src=""),
                                    dbc.Alert("", id="results-visu-alert", is_open=False),
                                ],
                                title="Output Visualization",
                                item_id="output-visu-accordion",
                            )
                        ],
                        active_item=["output-visu-accordion"],
                        always_open=True,
                    )
                ]
            )
        ]
    )

    return html.Div(
        [
            dcc.Markdown("""### Thermal Results"""),
            dcc.Markdown(
                """##### Results generated from solving the 2D transient thermal problem.
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
            html.Br(),
            dbc.Button(
                dbc.Spinner(children=html.Div(id="submit-loading-output"), size="sm"),
                id={"type": "submit-button", "index": "thermal_results"},
                disabled=False,
                n_clicks=0,
                size="md",
                style={"background-color": "rgba(255, 183, 27, 1)", "border-color": "rgba(255, 183, 27, 1)"},
            ),
        ]
    )


# =================================================== [Callbacks] =================================================== #


@callback(
    Output("results-image", "src"),
    Output("results-visu-alert", "children"),
    Input("part-name", "value"),
    Input("visu-type", "value"),
    State("url", "pathname"),
)
def update_result_image_and_alert_in_visualization_card(part_name, visu_type, pathname):
    project = UIClient[CompassSolution].get_project(pathname)
    step = project.steps.thermal_results_step

    if part_name is None or visu_type is None or project.steps.thermal_setup_step.mechanical_solve_status != "success":
        raise PreventUpdate
    else:
        msg_out = ""
        visu = None
        if visu_type == "3D Result":
            pass  # TODO
        else:
            step.part_name = part_name
            step.visu_type = visu_type
            step.get_image()
            visu = "data:image/png;base64,{}".format(step.image_file.read_bytes().decode())

        return visu, msg_out
