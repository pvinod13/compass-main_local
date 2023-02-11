# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import os
import time
import base64
import dash_bootstrap_components as dbc

from pathlib import Path
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, dcc, html, State, callback

from ansys.saf2.client import UIClient
from ansys.saf2.sdk import MethodStatus
from ansys.solutions.compass.compass.solution.definition import CompassSolution
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)
from ansys.solutions.compass.compass.ui.components import InputRow


# =================================================== [Functions] =================================================== #


def make_number_within_range(value, min_value, max_value):
    if isinstance(value, float):
        value = round(value)
    if value < min_value:
        value = min_value
    elif value > max_value:
        value = max_value
    return value


# TODO: Refactor alert definition to a class
def update_em_geometry_alert(step):
    """Returns an Alert component to notify the user on the status of the generated geometry."""
    if step.aedt_version_alert:
        return dbc.Alert(
            step.aedt_version_alert,
            color="danger",
        )
    elif step.generated_geometry_status == "initial":
        return dbc.Alert(
            "Geometry undefined. Generate the geometry to proceed.",
            color="warning",
        )
    elif step.generated_geometry_status == "success":
        return dbc.Alert(
            "Geometry generation completed successfully.",
            color="success",
        )
    elif step.generated_geometry_status == "failure":
        return dbc.Alert(
            "Geometry generation failed.",
            color="danger",
        )
    else:
        return None


def update_em_solve_alert(step):
    """Return an Alert component with the corresponding messsage to notify the user on the status of the EM solve."""
    if step.solve_status == "initial":
        return dbc.Alert(
            "Maxwell solve not started.",
            color="warning",
        )
    elif step.solve_status == "success":
        return dbc.Alert(
            "Maxwell solve completed successfully.",
            color="success",
        )
    elif step.solve_status == "failure":
        return dbc.Alert(
            "Maxwell solve failed.",
            color="danger",
        )
    else:
        return None


# ===================================================== [Layout] ==================================================== #


def layout(step: ElectromagneticsSetupStep):
    """Page content associated to the electromagnetics setup step"""

    # Initialize parameters on page load
    if not step.selected_aedt_version:
        step.fetch_available_aedt_versions()

    geom_build_alert = update_em_geometry_alert(step)
    aedt_solve_alert = update_em_solve_alert(step)

    encoded_image = base64.b64encode(
        open(os.path.join(Path(__file__).parent.absolute(), "assets", "Graphics", "magnetics2d.png"), "rb").read()
    )

    inputs_card = dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    InputRow(
                                        "dropdown",
                                        "aedt-version-selection",
                                        "AEDT version",
                                        "",
                                        step.selected_aedt_version,
                                        step.available_aedt_versions,
                                    ).get(),
                                    InputRow(
                                        "dropdown",
                                        "queue-selection",
                                        "Queue",
                                        "",
                                        step.selected_queue,
                                        step.authorized_queues,
                                    ).get(),
                                    InputRow(
                                        "number",
                                        "cpus-selection",
                                        "Number of CPUs",
                                        "",
                                        step.num_cpus,
                                        min_value=0,
                                        max_value=1000,
                                        increment=1,
                                    ).get(),
                                ],
                                title="Software/Hardware Settings",
                                item_id="software-hardware-settings",
                            ),
                            dbc.AccordionItem(
                                [
                                    InputRow(
                                        "number",
                                        "dia_small_holes",
                                        "Small Holes Diameter Dsho",
                                        "mm",
                                        float(step.motor_prop["DiaSmallHoles"].strip("mm")),
                                        min_value=0,
                                        max_value=5.5,
                                    ).get(),
                                    InputRow(
                                        "number",
                                        "dia_big_hole",
                                        "Big Hole Diameter Dbho",
                                        "mm",
                                        float(step.motor_prop["DiaBigHole"].strip("mm")),
                                        min_value=0,
                                        max_value=17.0,
                                    ).get(),
                                    InputRow(
                                        "number",
                                        "l_drl_pm_o",
                                        "Distance between Rotor Lam and PM_O",
                                        "mm",
                                        float(step.motor_prop["L_Drl_PM_O"].strip("mm")),
                                        min_value=1.78,
                                        max_value=10.0,
                                    ).get(),
                                    html.Br(),
                                    InputRow(
                                        "button",
                                        "generate-2d-geometry-button",
                                        "Generate 2D Geometry",
                                        "",
                                        "",
                                        disabled=False,
                                    ).get(),
                                    html.Br(),
                                    InputRow(
                                        "button",
                                        "launch-aedt-button",
                                        "Launch Simulation",
                                        "",
                                        "",
                                        disabled=False if step.generated_geometry_status == "success" else True,
                                    ).get(),
                                    dcc.Loading(
                                        id="wait-geometry",
                                        type="circle",
                                        fullscreen=True,
                                        color="#ffb71b",  # $ansys-gold
                                        style={
                                            "background-color": "rgba(55, 58, 54, 0.1)",  # $ansys-lead "#373a36"
                                        },
                                        children=html.Div(id="wait-geometry-output"),
                                    ),
                                    dcc.Loading(
                                        id="wait-aedt",
                                        type="circle",
                                        fullscreen=True,
                                        color="#ffb71b",  # $ansys-gold
                                        style={
                                            "background-color": "rgba(55, 58, 54, 0.1)",  # $ansys-lead "#373a36"
                                        },
                                        children=html.Div(id="wait-aedt-output"),
                                    ),
                                ],
                                title="Geometry Parameters",
                                item_id="geometry-parameters",
                            ),
                        ],
                        active_item=["software-hardware-settings", "geometry-parameters"],
                        always_open=True,
                    ),
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
                                    dbc.CardImg(
                                        id="input-geometry-sketch",
                                        src="data:image/png;base64,{}".format(encoded_image.decode()),
                                    ),
                                ],
                                title="Geometry Parameters Sketch",
                                item_id="input-geometry-placeholder",
                            ),
                            dbc.AccordionItem(
                                [
                                    dbc.CardImg(
                                        id="output-geometry-sketch",
                                        src="data:image/png;base64,{}".format(encoded_image.decode()),
                                    ),
                                ],
                                title="Geometry Generated",
                                item_id="output-geometry-placeholder",
                            ),
                        ],
                        id="visu-accordion",
                        active_item="input-geometry-placeholder",
                    )
                ]
            )
        ]
    )

    return html.Div(
        [
            dcc.Markdown("""### Electromagnetics Setup"""),
            dcc.Markdown(
                """##### Generate the 2D geometry model of the electrical motor and solve the 2D transient electromagnetics problem.
                """
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                id="em-build-alert",
                                children=[geom_build_alert],
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                id="em-solve-alert",
                                children=[aedt_solve_alert],
                            )
                        ],
                        width=6,
                    ),
                ],
                style={"padding": "20px"},
            ),
            dbc.Row(
                [
                    dbc.Col(inputs_card, width=6),
                    dbc.Col(visualization_card, width=6),
                ],
                style={"padding": "20px"},
            ),
            html.Br(),
            dbc.Button(
                dbc.Spinner(children=html.Div(id="submit-loading-output"), size="sm"),
                id={"type": "submit-button", "index": "electromagnetics_setup"},
                disabled=False
                if step.generated_geometry_status == "success" and step.solve_status == "success"
                else True,
                n_clicks=0,
                size="md",
                style={"background-color": "rgba(255, 183, 27, 1)", "border-color": "rgba(255, 183, 27, 1)"},
            ),
        ]
    )


# =================================================== [Callbacks] =================================================== #


@callback(
    Output("em-build-alert", "children"),
    Output("wait-geometry-output", "children"),
    Output("launch-aedt-button", "disabled"),
    Output("output-geometry-sketch", "src"),
    Output("visu-accordion", "active_item"),
    Input("generate-2d-geometry-button", "n_clicks"),
    State("aedt-version-selection", "value"),
    State("queue-selection", "value"),
    State("cpus-selection", "value"),
    State("dia_small_holes", "value"),
    State("dia_big_hole", "value"),
    State("l_drl_pm_o", "value"),
    State("url", "pathname"),
)
def generate_geometry(n_clicks, aedt_version, queue, nbr_of_cpu, dia_small_holes, dia_big_hole, l_drl_pm_o, pathname):
    """Use input values defined in the page to generate the geometry of the motor."""
    project = UIClient[CompassSolution].get_project(pathname)
    step = project.steps.electromagnetics_setup_step

    if n_clicks:
        step.aedt_version = aedt_version
        step.selected_queue = queue
        step.num_cpus = make_number_within_range(nbr_of_cpu, 1, step.max_cpus)
        step.motor_prop["DiaSmallHoles"] = "%.3fmm" % (dia_small_holes)
        step.motor_prop["DiaBigHole"] = "%.3fmm" % (dia_big_hole)
        step.motor_prop["L_Drl_PM_O"] = "%.3fmm" % (l_drl_pm_o)

        step.generate_geometry()

        if step.generated_geometry_status == "success":
            return (
                dbc.Alert(
                    "Geometry generation completed successfully.",
                    color="success",
                ),
                True,
                False,
                "data:image/png;base64,{}".format(step.sketch_2d.read_bytes().decode()),
                "output-geometry-placeholder",
            )
        elif step.generated_geometry_status == "failure":
            return (
                dbc.Alert(
                    "Geometry generation failed.",
                    color="danger",
                ),
                True,
                True,
                None,
                "input-geometry-placeholder",
            )
    else:
        raise PreventUpdate


@callback(
    Output("em-solve-alert", "children"),
    Output("wait-aedt-output", "children"),
    Output({"type": "submit-button", "index": "electromagnetics_setup"}, "disabled"),
    Input("launch-aedt-button", "n_clicks"),
    State("url", "pathname"),
)
def run_maxwell_solve(n_clicks, pathname):
    """Collect inputs for electromagnetics results step"""
    project = UIClient[CompassSolution].get_project(pathname)
    step = project.steps.electromagnetics_setup_step

    if n_clicks:
        step.solve_status == "in-progress"
        step.run_maxwell_solve()
        while step.get_long_running_method_state("run_maxwell_solve").status == MethodStatus.Running:
            time.sleep(5)
        if step.solve_status == "success":
            return (
                dbc.Alert(
                    "Maxwell solve completed successfully.",
                    color="success",
                ),
                True,
                False,
            )
        elif step.solve_status == "failure":
            return (
                dbc.Alert(
                    "Maxwell solve failed.",
                    color="danger",
                ),
                True,
                True,
            )
    else:
        raise PreventUpdate
