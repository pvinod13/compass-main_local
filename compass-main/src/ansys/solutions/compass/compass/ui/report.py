# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import ansys.solutions.compass.compass.report.report_ids as ids
import dash_bootstrap_components as dbc

from dash import html
from dash_extensions.enrich import Input, Output, dcc, html, State, callback

from ansys.saf2.client import UIClient
from ansys.solutions.compass.compass.report.report_content_generator import get_report_dto
from ansys.solutions.compass.compass.report.report_dash_renderer import render_section
from ansys.solutions.compass.compass.report.report_export_document import export_document
from ansys.solutions.compass.compass.solution.definition import CompassSolution
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)
from ansys.solutions.compass.compass.solution.report_step import ReportStep
from ansys.solutions.compass.compass.scripts.utils import get_date


# =================================================== [Functions] =================================================== #


# ===================================================== [Layout] ==================================================== #


def layout(step: ReportStep, em_setup_step: ElectromagneticsSetupStep) -> html.Div:
    """Page content associated to the report step"""

    # Temporary
    global_data = {
        "efficiency": "92.01",
        "CoreLoss(Stator) [mW]": "384.70",
        "CoreLoss(Rotor) [mW]": "55.40",
        "SolidLoss(PM_I1) [mW]": "0.71",
        "SolidLoss(PM_I1_1) [mW]": "0.73",
        "SolidLoss(PM_O1) [mW]": "3.65",
        "SolidLoss(PM_O1_1) [mW]": "5.17",
        "StrandedLoss [mW]": "1306.46",
        "Moving1.Torque [NewtonMeter]": "57.86",
    }
    # ?????
    report_dto = get_report_dto(em_setup_step.simulation_results)

    return html.Div(
        [
            dcc.Markdown("""### Report"""),
            dcc.Markdown(
                """##### Put together simulation outputs from EM and Thermal steps
            """
            ),
            html.Br(),
            html.H1("Report", style={"textAlign": "center"}),
            html.H2(get_date(), style={"textAlign": "center"}),
            html.Button("Export", id=ids.EXPORT_BUTTON, n_clicks=0),
            html.Div(id="test2"),
            html.Div(id="test"),
            render_section(report_dto.introduction_section),
            render_section(report_dto.materials_section),
            render_section(report_dto.maxwell_analysis_section),
            html.Div(id=ids.CONTAINER_CUSTOM_SECTION, children=[]),
            html.Button("Add section", id=ids.ADD_SECTION_BUTTON, n_clicks=0),
        ]
    )


# =================================================== [Callbacks] =================================================== #


@callback(
    Output(ids.CONTAINER_CUSTOM_SECTION, "children"),
    Input(ids.ADD_SECTION_BUTTON, "n_clicks"),
    State(ids.CONTAINER_CUSTOM_SECTION, "children"),
)
def add_custom_section(n_clicks, previous_custom_content):
    if n_clicks == 0:
        return []
    new_custom_content = [
        html.Div(html.H2("Custom section " + str(n_clicks))),
        dbc.Row(
            [
                dbc.Col([html.Div(html.P("Section title"))], width=1),
                dbc.Col(
                    [
                        html.Div(
                            dbc.Input(
                                id=ids.CUSTOM_SECTION_TITLE_ID + str(n_clicks),
                                placeholder="Type your section title here",
                                type="text",
                            )
                        )
                    ],
                    width=5,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Div(html.P("Section content"))], width=1),
                dbc.Col(
                    [
                        html.Div(
                            dbc.Textarea(
                                id=ids.CUSTOM_SECTION_CONTENT_ID + str(n_clicks),
                                placeholder="Type your section content here",
                                style={"width": "100%", "height": 250},
                            )
                        )
                    ],
                    width=5,
                ),
            ]
        ),
    ]
    return previous_custom_content + new_custom_content


@callback(
    Output("test", "children"),
    Input(ids.EXPORT_BUTTON, "n_clicks"),
    State(ids.CONTAINER_CUSTOM_SECTION, "children"),
    State("url", "pathname"),
)
def export(n_clicks, previous_custom_content, pathname):
    project = UIClient[CompassSolution].get_project(pathname)
    step = project.steps.electromagnetics_setup_step

    report_dto = get_report_dto(step.aedt_results)
    file = export_document(report_dto)
    return [dcc.Download(data=dcc.send_file(file))]
