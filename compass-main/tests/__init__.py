import sys

from ansys.solutions.compass.compass.report import report_ids

sys.modules["report_ids"] = sys.modules["ansys.solutions.compass.compass.report.report_ids"]

from ansys.solutions.compass.compass.report import report_dto

sys.modules["report_dto"] = sys.modules["ansys.solutions.compass.compass.report.report_dto"]

from ansys.solutions.compass.compass.ui import app

sys.modules["app"] = sys.modules["ansys.solutions.compass.compass.ui.app"]

from ansys.solutions.compass.compass.ui import report

sys.modules["report"] = sys.modules["ansys.solutions.compass.compass.ui.report"]
