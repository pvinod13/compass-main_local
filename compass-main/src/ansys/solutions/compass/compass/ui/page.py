# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import dash
import dash_bootstrap_components as dbc
import ansys.solutions.compass.compass.ui.electromagnetics_setup as electromagnetics_setup
import ansys.solutions.compass.compass.ui.electromagnetics_results as electromagnetics_results
import ansys.solutions.compass.compass.ui.thermal_setup as thermal_setup
import ansys.solutions.compass.compass.ui.thermal_results as thermal_results
import ansys.solutions.compass.compass.ui.report as report


from ansys.saf2.client import UIClient
from dash_iconify import DashIconify
from dash_extensions.enrich import dcc, html, Input, Output, State, callback, callback_context, ALL
from ansys_dash_treeview import AnsysDashTreeview

from ansys.solutions.compass.compass.solution.definition import CompassSolution


# ===================================================== [Layout] ==================================================== #

step_list = [
    {
        "key": "electromagnetics",
        "text": "Electromagnetics",
        "depth": 0,
    },
    {
        "key": "electromagnetics_setup",
        "text": "Setup",
        "depth": 1,
    },
    {
        "key": "electromagnetics_results",
        "text": "Results",
        "depth": 1,
    },
    {
        "key": "thermal",
        "text": "Thermal",
        "depth": 0,
    },
    {
        "key": "thermal_setup",
        "text": "Setup",
        "depth": 1,
    },
    {
        "key": "thermal_results",
        "text": "Results",
        "depth": 1,
    },
    {
        "key": "report",
        "text": "Report",
        "depth": 0,
    },
]


layout = html.Div(
    [
        # represents the browser address bar and doesn't render anything
        dcc.Location(id="url", refresh=False),
        html.Img(src=r"/assets/Graphics/ansys-solutions-horizontal-logo.png"),
        # here we are rendering the step in its non-persisted form
        # just to initialize the layout so the callbacks can function
        # you could avoid this by suppressing callback errors - that's your call!
        html.Div(id="return-to-portal"),
        dbc.Row(
            children=[
                dbc.Col(
                    AnsysDashTreeview(
                        id="navigation_tree",
                        items=step_list,
                        children=[
                            DashIconify(icon="bi:caret-right-square-fill"),
                            DashIconify(icon="bi:caret-down-square-fill"),
                        ],
                        style={"showButtons": True, "focusColor": "#ffb71b", "itemHeight": "32"},  # Ansys gold
                    ),
                    width=2,
                    style={"background-color": "rgba(242, 242, 242, 0.6)"},  # Ansys grey
                ),
                dbc.Col(html.Div(id="page-content", style={"padding-right": "4%", "padding-top": "1%"}), width=10),
            ],
        ),
    ]
)

# =================================================== [Callbacks] =================================================== #


@callback(
    Output("return-to-portal", "children"),
    Input("url", "pathname"),
)
def return_to_portal(pathname):
    """Display Solution Portal when back-to-portal button gets selected."""
    portal_ui_url = UIClient.get_portal_ui_url()
    children = (
        []
        if portal_ui_url is None
        else [
            html.P(
                className="back-link",
                children=[
                    html.A(
                        href=portal_ui_url,
                        children=dbc.Button(
                            "Back to Projects",
                            id="return-button",
                            className="me-2",
                            n_clicks=0,
                            style={"background-color": "rgba(0, 0, 0, 1)", "border-color": "rgba(0, 0, 0, 1)"},
                        ),
                    )
                ],
            )
        ]
    )
    return children


@callback(
    Output("page-content", "children"),
    Output("outofdate-step-alert", "children"),
    Output("outofdate-step-alert", "is_open"),
    Output("thermal-geom-data-output", "children"),
    [
        Input("url", "pathname"),
        Input("navigation_tree", "focus"),
    ],
    prevent_initial_call=True,
)
def display_page(pathname, value):
    """
    This callback is essential for initializing the step based on the persisted
    state of the project when the browser first displays the project to the user
    given the project's URL
    """
    # Get project
    project = UIClient[CompassSolution].get_project(pathname)
    th_setup_step = project.steps.thermal_setup_step
    # Get the ID of the event triggering the callback
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    # Initialize error message
    error_message = None

    if triggered_id == "url":
        return (
            electromagnetics_setup.layout(project.steps.electromagnetics_setup_step),
            error_message,
            bool(error_message),
            th_setup_step.uri_file_data,
        )

    if triggered_id == "navigation_tree":
        if value is None:
            page_layout = html.H1("Welcome!")
        elif value == "electromagnetics_setup":
            page_layout = electromagnetics_setup.layout(project.steps.electromagnetics_setup_step)
        elif value == "electromagnetics_results":
            page_layout = electromagnetics_results.layout(
                project.steps.electromagnetics_results_step, project.steps.electromagnetics_setup_step
            )
        elif value == "thermal_setup":
            page_layout = thermal_setup.layout(
                project.steps.thermal_setup_step, project.steps.electromagnetics_setup_step
            )
        elif value == "thermal_results":
            page_layout = thermal_results.layout(project.steps.thermal_results_step, project.steps.thermal_setup_step)
        elif value == "report":
            page_layout = report.layout(project.steps.report_step, project.steps.electromagnetics_setup_step)

    return page_layout, error_message, bool(error_message), th_setup_step.uri_file_data


@callback(
    Output("navigation_tree", "focusRequested"),
    Output("submit-loading-output", "children"),
    Output("outofdate-step-alert", "children"),
    Output("outofdate-step-alert", "is_open"),
    Output("thermal-geom-data-output", "children"),
    Input({"type": "submit-button", "index": ALL}, "n_clicks"),
    [Input({"type": "btn-group", "index": ALL}, "value")],
    State("url", "pathname"),
    prevent_initial_call=True,
)
def submit_home_action(n_clicks, value, pathname):
    """Callback to update focusrequested from the step"""
    project = UIClient[CompassSolution].get_project(pathname)
    th_setup_step = project.steps.thermal_setup_step

    # Get callback context
    ctx = dash.callback_context
    # Information needed
    result = dash.no_update
    button = ["Continue"]
    error_message = None

    if ctx.triggered_id and n_clicks[0] or ctx.triggered_id and value:
        # Get the ID of the event triggering the callback
        triggered_index = ctx.triggered_id.get("index")
        if triggered_index == "electromagnetics_setup":
            result = "electromagnetics_results"
        elif triggered_index == "electromagnetics_results":
            result = "thermal_setup"
        elif triggered_index == "thermal_setup":
            result = "thermal_results"
        elif triggered_index == "thermal_results":
            result = "report"

    return result, button, error_message, bool(error_message), th_setup_step.uri_file_data
