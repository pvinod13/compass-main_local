# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

from ansys.solutions.compass.compass.report.report_section import ReportSection
from collections import namedtuple

# =================================================== [Functions] =================================================== #


Paragraph = namedtuple("Paragraph", ["Text"])
Image = namedtuple("Image", ["Path", "Caption", "Width", "Height"])


class ReportDTO:
    def __init__(self):
        self.__custom_contents = []
        self.__introduction_section = ReportSection("Introduction", level=1)
        self.__materials_section = ReportSection("Materials", level=1)
        self.__workflow_definition_section = ReportSection("Workflow Definition", level=1)
        self.__maxwell_analysis_section = ReportSection("Maxwell analysis", level=1)
        self.__thermal_analysis_section = ReportSection("Thermal analysis", level=1)
        self.__conclusion_section = ReportSection("Conclusion", level=1)

    @property
    def introduction_section(self):
        return self.__introduction_section

    @property
    def materials_section(self):
        return self.__materials_section

    @property
    def workflow_definition_section(self):
        return self.__workflow_definition_section

    @property
    def maxwell_analysis_section(self):
        return self.__maxwell_analysis_section

    @property
    def thermal_analysis_section(self):
        return self.__thermal_analysis_section

    @property
    def conclusion_section(self):
        return self.__conclusion_section

    @property
    def custom_contents(self):
        return self.__custom_contents

    def add_custom_section(self, title, paragraphs):
        section = ReportSection(title)
        section.add_contents(paragraphs)
        self.__custom_contents.append(section)
