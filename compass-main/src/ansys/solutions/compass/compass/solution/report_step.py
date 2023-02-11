# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

from typing import Dict

from ansys.saf2.sdk import StepModel


class ReportStep(StepModel):
    """Provide a place to configure and customize a simulation report."""

    result: Dict = {}
