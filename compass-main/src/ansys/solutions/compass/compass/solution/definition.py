# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

from ansys.saf2.sdk import Solution, StepsModel
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)
from ansys.solutions.compass.compass.solution.electromagnetics_results_step import (
    ElectromagneticsResultsStep,
)
from ansys.solutions.compass.compass.solution.thermal_setup_step import ThermalSetupStep
from ansys.solutions.compass.compass.solution.thermal_results_step import ThermalResultsStep
from ansys.solutions.compass.compass.solution.report_step import ReportStep


class Steps(StepsModel):
    electromagnetics_setup_step: ElectromagneticsSetupStep
    electromagnetics_results_step: ElectromagneticsResultsStep
    thermal_setup_step: ThermalSetupStep
    thermal_results_step: ThermalResultsStep
    report_step: ReportStep


class CompassSolution(Solution):
    display_name = "Compass"
    steps: Steps
