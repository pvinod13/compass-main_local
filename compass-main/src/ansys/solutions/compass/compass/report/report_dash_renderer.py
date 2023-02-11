# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

import base64
import pandas as pd

from ansys.solutions.compass.compass.report.report_dto import Image, Paragraph
from ansys.solutions.compass.compass.report.report_section import ReportSection
from ansys.solutions.compass.compass.report.report_table import ReportTable
from dash import html, dash_table

# =================================================== [Functions] =================================================== #


def render_section(section):
    if section.level == 1:
        rendered_section = [html.H2(section.title)]
    elif section.level == 2:
        rendered_section = [html.H3(section.title)]
    else:
        raise NotImplemented()

    if section.contents:
        for content in section.contents:
            if isinstance(content, ReportSection):
                rendered_section.append(render_section(content))
            elif isinstance(content, Paragraph):
                rendered_section.append(html.P(content.Text))
            elif isinstance(content, ReportTable):
                rendered_section.append(__render_table(content))
            elif isinstance(content, Image):
                rendered_section.append(__render_image(content))
            else:
                raise NotImplementedError()

    return html.Div(rendered_section)


def __render_table(table):
    data_frame = pd.DataFrame(data=table.content)
    return dash_table.DataTable(data_frame.to_dict("records"), [{"name": i, "id": i} for i in data_frame.columns])


def __render_image(image):
    print(image.Path)
    with open(image.Path, "rb") as f:
        image_content = f.read()
    return html.Img(src="data:image/png;base64," + base64.b64encode(image_content).decode("utf-8"))
