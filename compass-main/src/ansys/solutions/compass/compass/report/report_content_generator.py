# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

import os

from ansys.solutions.compass.compass.report.report_dto import Image, Paragraph, ReportDTO
from ansys.solutions.compass.compass.report.report_section import ReportSection
from ansys.solutions.compass.compass.report.report_table import ReportTable
from pathlib import Path

# =================================================== [Functions] =================================================== #


def get_report_dto(global_data):
    report_dto = ReportDTO()
    report_dto.introduction_section.add_contents(
        Paragraph(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
                Praesent vehicula risus nec diam bibendum, convallis efficitur \
                arcu bibendum. Mauris hendrerit mi varius rutrum dictum. Etiam eu \
                varius odio, id interdum est. Mauris accumsan finibus risus sit \
                amet congue. Maecenas id libero diam. Orci varius natoque penatibus \
                et magnis dis parturient montes, nascetur ridiculus mus. Donec varius, \
                ante non tincidunt pharetra, nulla sem efficitur ipsum, at volutpat augue massa vitae lacus. \
                Fusce accumsan felis nec libero bibendum laoreet. Suspendisse elementum urna nec iaculis finibus. \
                Pellentesque vehicula egestas felis, eu facilisis dui blandit at. Ut risus elit, \
                consectetur a augue non, suscipit sagittis felis. Proin ut mauris lacinia, iaculis ligula ac, \
                vehicula tortor. Proin at vulputate odio. Donec quis justo facilisis, rhoncus leo nec, ullamcorper risus."
        ),
        Paragraph(
            "Sed egestas sodales mi nec ultricies. Proin ante odio, \
                accumsan a iaculis sed, cursus vitae mi. Fusce mi ex, \
                laoreet sed velit eget, euismod dignissim justo. Curabitur sed tempus dui. \
                Nam non lectus rhoncus enim condimentum pretium. Nam vitae mollis neque, \
                vel convallis neque. Nullam semper massa a nisl consectetur, ut pharetra sem ornare."
        ),
    )
    report_dto.materials_section.add_contents(Paragraph("A"), Paragraph("B"))

    inputs_section = ReportSection("Inputs", level=2)
    inputs_section.add_contents(Paragraph("The user inputs are given in the table below."))

    inputs = dict(
        Description=["Small Holes Diameter Dsho", "Big Hole Diameter Dbho", "Distance between Rotor Lam and PM_O"],
        Value=[0, 0, 0],
        Unit=["mm", "mm", "mm"],
    )
    table = ReportTable("Geometry parameters of the Maxwell analysis", inputs)
    inputs_section.add_contents(table)

    report_dto.maxwell_analysis_section.add_contents(inputs_section)

    model_section = ReportSection("Model", level=2)
    model_section.add_contents(Paragraph("A first paragraph..."))
    image_path = os.path.join(Path(__file__).parent.parent.absolute(), "ui", "assets", "Graphics", "magnetics2d.png")
    model_section.add_contents(Image(image_path, Caption="test 1", Width=10, Height=7))

    report_dto.maxwell_analysis_section.add_contents(model_section)

    return report_dto
