# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import time
import dash_bootstrap_components as dbc

from dash import html
from ansys.saf2.client import UIClient
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, dcc, html, State, callback, clientside_callback

from ansys.saf2.client import UIClient
from ansys.saf2.sdk import MethodStatus
from ansys.solutions.compass.compass.solution.definition import CompassSolution
from ansys.solutions.compass.compass.solution.thermal_setup_step import ThermalSetupStep
from ansys.solutions.compass.compass.ui.components import InputRow
from ansys.solutions.compass.compass.scripts.cad_viewer import render_3d_cad_viewer
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)


# =================================================== [Functions] =================================================== #

# TODO: Refactor alert definition to a class
def update_thermal_geometry_alert(step):
    if step.mechanical_version_alert:
        return dbc.Alert(
            step.mechanical_version_alert,
            color="danger",
        )
    elif step.geometry_build_status == "initial":
        return dbc.Alert(
            "3D geometry not yet defined. Generate the geometry to proceed.",
            color="warning",
        )
    elif step.geometry_build_status == "success":
        return dbc.Alert(
            "Geometry generation completed successfully.",
            color="success",
        )
    elif step.geometry_build_status == "failure":
        return dbc.Alert(
            "Geometry generation failed.",
            color="danger",
        )
    else:
        return None


def update_thermal_solve_alert(step):
    if step.mechanical_solve_status == "initial":
        return dbc.Alert(
            "Thermal solve not started.",
            color="warning",
        )
    elif step.mechanical_solve_status == "in-progress":
        return dbc.Alert(
            "Thermal solve is in-progress.",
            color="primary",
        )
    elif step.mechanical_solve_status == "failure":
        return dbc.Alert(
            "Thermal solve failed.",
            color="danger",
        )
    elif step.mechanical_solve_status == "success":
        return dbc.Alert(
            "Thermal solve completed successfully.",
            color="success",
        )
    else:
        return None


# ===================================================== [Layout] ==================================================== #


def layout(step: ThermalSetupStep, electromagnetics_setup_step: ElectromagneticsSetupStep):

    # Initialize parameters on page load
    if not step.selected_mechanical_version:
        step.fetch_available_mechanical_versions()

    thermal_geometry_alert = update_thermal_geometry_alert(step)
    thermal_solve_alert = update_thermal_solve_alert(step)

    user_input_section = dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    InputRow(
                                        "dropdown",
                                        "mechanical-version-selection",
                                        "Mechanical version",
                                        "",
                                        step.selected_mechanical_version,
                                        step.available_mechanical_versions,
                                    ).get(),
                                    InputRow(
                                        "dropdown",
                                        "queue-selection",
                                        "Queue",
                                        "",
                                        step.selected_queue,
                                        step.authorized_queue_options,
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
                                        "dropdown",
                                        "cooling-type-selection",
                                        "Cooling section",
                                        "",
                                        step.cooling_type,
                                        step.cooling_type_options,
                                    ).get(),
                                    html.Br(),
                                    InputRow(
                                        "button",
                                        "generate-3d-geometry-button",
                                        "Generate 3D Geometry",
                                        "",
                                        "",
                                        disabled=False
                                        if electromagnetics_setup_step.generated_geometry_status == "success"
                                        and electromagnetics_setup_step.solve_status == "success"
                                        else True,
                                    ).get(),
                                    dbc.Alert("", id=f"thermal-cad-alert", is_open=False),
                                    dcc.Loading(
                                        id="update-geometry-in-progress",
                                        type="circle",
                                        fullscreen=True,
                                        color="#ffb71b",
                                        style={
                                            "background-color": "rgba(55, 58, 54, 0.1)",  # $ansys-lead "#373a36"
                                        },
                                        children=html.Div(id="update-geometry-in-progress-output"),
                                    ),
                                ],
                                title="Geometry Parameters",
                                item_id="geometry-parameters",
                            ),
                            dbc.AccordionItem(
                                [
                                    InputRow(
                                        "number",
                                        "internal_flow_film_coef",
                                        "Internal Flow Film Coefficient",
                                        "W m^-2 C^-1",
                                        step.internal_flow_film_coef,
                                    ).get(),
                                    InputRow(
                                        "number",
                                        "external_air_film_coef",
                                        "External Air Film Coefficient",
                                        "W m^-2 C^-1",
                                        step.external_air_film_coef,
                                    ).get(),
                                    InputRow(
                                        "number",
                                        "ambient_temperature",
                                        "Ambient Temperature",
                                        "°C",
                                        step.ambient_temperature,
                                    ).get(),
                                    InputRow(
                                        "dropdown",
                                        "mesh-size",
                                        "Mesh Size",
                                        "",
                                        step.mesh_size,
                                        step.mesh_size_options,
                                    ).get(),
                                    html.Br(),
                                    InputRow(
                                        "button",
                                        "launch-simulation-button",
                                        "Launch Simulation",
                                        "",
                                        "",
                                        disabled=False if step.geometry_build_status == "success" else True,
                                    ).get(),
                                    dcc.Loading(
                                        id="wait-mechanical",
                                        type="circle",
                                        fullscreen=True,
                                        color="#ffb71b",  # $ansys-gold
                                        style={
                                            "background-color": "rgba(55, 58, 54, 0.1)",  # $ansys-lead "#373a36"
                                        },
                                        children=html.Div(id="wait-mechanical-output"),
                                    ),
                                ],
                                title="Simulation Parameters",
                                item_id="simulation-parameters",
                            ),
                        ],
                        active_item=["software-hardware-settings", "geometry-parameters", "simulation-parameters"],
                        always_open=True,
                    )
                ],
                style={"display": "inline-block"},
            ),
            html.Div(id="launch-message-out", style={"color": "red"}),
        ]
    )

    viewer_section = dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.Div(
                                        id="thermal-cad-viewer",
                                        style={"width": "100%", "height": "600px", "position": "center"},
                                    ),
                                    html.Div(
                                        id="thermal-geom-data-output",
                                        children=step.uri_file_data,
                                        style={"display": "none"},
                                    ),
                                ],
                                title="Geometry Generated",
                                item_id="thermal-geom-generated",
                            ),
                        ],
                        id="thermal-visu-accordion",
                        active_item="thermal-geom-generated",
                    )
                ]
            ),
        ]
    )

    return html.Div(
        [
            dcc.Markdown("""#### Thermal Simulation Step"""),
            dcc.Markdown("""###### Generate 3D geometry and perform thermal simulation."""),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                id="thermal-geometry-alert",
                                children=[thermal_geometry_alert],
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                id="thermal-solve-alert",
                                children=[thermal_solve_alert],
                            )
                        ],
                        width=6,
                    ),
                ],
                style={"padding": "20px"},
            ),
            dbc.Row(
                [
                    dbc.Col(user_input_section, width=6),
                    dbc.Col(viewer_section, width=6),
                ],
                style={"padding": "20px"},
            ),
            html.Br(),
            dbc.Button(
                dbc.Spinner(children=html.Div(id="submit-loading-output"), size="sm"),
                id={"type": "submit-button", "index": "thermal_setup"},
                disabled=False
                if step.geometry_build_status == "success" and step.mechanical_solve_status == "success"
                else True,
                n_clicks=0,
                size="md",
                style={"background-color": "rgba(255, 183, 27, 1)", "border-color": "rgba(255, 183, 27, 1)"},
            ),
        ]
    )


# =================================================== [Callbacks] =================================================== #


@callback(
    Output("thermal-geometry-alert", "children"),
    Output("update-geometry-in-progress-output", "children"),
    Output("launch-simulation-button", "disabled"),
    Output("thermal-geom-data-output", "children"),
    Output("thermal-visu-accordion", "active_item"),
    Input("generate-3d-geometry-button", "n_clicks"),
    State("cooling-type-selection", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_geometry_and_alert_on_click(n_clicks, cooling_type, pathname):
    project = UIClient[CompassSolution].get_project(pathname)
    thermal_step = project.steps.thermal_setup_step

    if n_clicks:
        active_item = "thermal-geom-generated"
        thermal_step.cooling_type = cooling_type
        thermal_step.write_geometry_template_to_filereference()
        thermal_step.write_scdm_script_file_to_filereference()

        thermal_step.generate_geometry()
        while thermal_step.get_long_running_method_state("generate_geometry").status == MethodStatus.Running:
            time.sleep(1)

        if thermal_step.geometry_build_status == "success":
            return (
                dbc.Alert(
                    "3D geometry generation completed successfully",
                    color="success",
                ),
                True,
                False,  # Launch simulation button is enabled (disabled = False) when the thermal geometry is generated
                thermal_step.uri_file_data,
                active_item,
            )
        elif thermal_step.geometry_build_status == "failure":
            return (
                dbc.Alert(
                    "3D geometry generation failed.",
                    color="danger",
                ),
                True,
                True,
                thermal_step.uri_file_data,
                active_item,
            )
    else:
        raise PreventUpdate


@callback(
    Output("thermal-solve-alert", "children"),
    Output("wait-mechanical-output", "children"),
    Output({"type": "submit-button", "index": "thermal_setup"}, "disabled"),
    Input("launch-simulation-button", "n_clicks"),
    State("url", "pathname"),
    State("mesh-size", "value"),
    State("queue-selection", "value"),
    State("internal_flow_film_coef", "value"),
    State("external_air_film_coef", "value"),
    State("ambient_temperature", "value"),
)
def launch_simulation_on_click(
    n_clicks, pathname, mesh_size, queue, internal_flow_film_coef, external_air_film_coef, ambient_temperature
):
    project = UIClient[CompassSolution].get_project(pathname)
    thermal_step = project.steps.thermal_setup_step

    if n_clicks:
        thermal_step.mesh_size = mesh_size
        thermal_step.selected_queue = queue
        thermal_step.internal_flow_film_coef = internal_flow_film_coef
        thermal_step.external_air_film_coef = external_air_film_coef
        thermal_step.ambient_temperature = ambient_temperature

        thermal_step.write_mechanical_script_file_to_filereference()
        thermal_step.write_materials_file_to_filereference()

        thermal_step.launch_thermal_simulation()
        while thermal_step.get_long_running_method_state("launch_thermal_simulation").status == MethodStatus.Running:
            time.sleep(5)

        if thermal_step.mechanical_solve_status == "success":
            return (
                dbc.Alert(
                    "Thermal analysis completed successfully",
                    color="success",
                ),
                True,
                False,
            )
        elif thermal_step.mechanical_solve_status == "failure":
            return (
                dbc.Alert(
                    "Thermal analysis failed",
                    color="danger",
                ),
                True,
                False,
            )
    else:
        raise PreventUpdate


clientside_callback(
    render_3d_cad_viewer(),
    Output("thermal-cad-alert", "children"),
    Input("thermal-geom-data-output", "children"),
    State("thermal-cad-viewer", "id"),
)
