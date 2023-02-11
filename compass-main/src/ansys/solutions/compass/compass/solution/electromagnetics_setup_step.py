# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import os
import base64

from pathlib import Path
from typing import List, Dict

import ansys.solutions.compass.compass.scripts.maxwell2D as maxwell2D
from ansys.saf2.sdk import StepModel, StepSpec, FileReference, FileGroupReference, transaction, long_running
from ansys.solutions.compass.compass.scripts.session_setup import get_product_version_numbers


class ElectromagneticsSetupStep(StepModel):
    project_name: str = "Example.aedt"
    design_name: str = "Sinusoidal"
    setup_name: str = "MySetupAuto"
    solution_type: str = "TransientXY"
    motor_prop = {
        "DiaGap": "%umm" % 132,
        "DiaStatorYoke": "%umm" % (198),
        "DiaStatorInner": "%umm" % (132),
        "DiaRotorLam": "%umm" % (130),
        "DiaShaft": "%.3fmm" % (44.45),
        "DiaOuter": "%umm" % (198),
        "Airgap": "%.3fmm" % (1),
        "SlotNumber": "%u" % (48),
        "SlotType": "%s" % (3),
        "DiaSmallHoles": "%.3fmm" % (5.1),
        "DiaBigHole": "%.3fmm" % (9.88),
        "L_Drl_PM_O": "%.3fmm" % (2.28),
    }
    simulation_results: Dict[str, str] = {
        "efficiency": "",
        "stator_loss_avg": "",
        "rotor_loss_avg": "",
        "pm_i1_loss_avg": "",
        "pm_i2_loss_avg": "",
        "pm_o1_loss_avg": "",
        "pm_o2_loss_avg": "",
        "stranded_loss_avg": "",
        "torque_avg": "",
    }
    selected_aedt_version: str = None
    available_aedt_versions: List[str] = []
    authorized_aedt_versions: List[str] = ["2022.1", "2022.2", "2023.1"]
    aedt_version_alert: str = None
    selected_wb_version: str = None
    available_wb_versions: List[str] = []
    generated_geometry_status: str = "initial"  # Possible status: initial, in-progress, failure, success
    solve_status: str = "initial"  # Possible status: initial, in-progress, failure, success
    selected_queue: str = "Local"
    authorized_queues: List[str] = ["Local", "AWS", "other..."]
    num_cpus: int = 1
    max_cpus: int = 1000
    sketch_2d: FileReference = FileReference("Electromagnetics/Geometry.jpg")
    aedt_file: FileReference = FileReference("Electromagnetics/Example.aedt")
    sat_file: FileReference = FileReference("Electromagnetics/my_geom.sat")
    result_files = FileGroupReference("Electromagnetics/Example.pyaedt/Sinusoidal/*.csv")

    @transaction(
        self=StepSpec(
            download=["authorized_aedt_versions"],
            upload=["available_aedt_versions", "selected_aedt_version", "aedt_version_alert"],
        )
    )
    def fetch_available_aedt_versions(self):
        available_products = get_product_version_numbers()
        if not available_products["AEDT"]:
            self.aedt_version_alert = "Maxwell is not installed."

        # Check if at least one of the installed aedt versions matches the requirements
        if self.authorized_aedt_versions:
            self.available_aedt_versions = [
                aedt_version
                for aedt_version in available_products["AEDT"]
                if aedt_version in self.authorized_aedt_versions
            ]
            if not self.available_aedt_versions:
                self.aedt_version_alert = "At least one of these versions is required for AEDT: "
                for aedt_version in self.authorized_aedt_versions:
                    self.aedt_version_alert += "%s " % (aedt_version)
                return
        else:
            self.available_aedt_versions = available_products["AEDT"]

        self.selected_aedt_version = self.available_aedt_versions[0]  # Selected aedt version is selected arbitrarily

    @transaction(
        self=StepSpec(
            download=[
                "selected_aedt_version",
                "project_name",
                "design_name",
                "setup_name",
                "solution_type",
                "motor_prop",
            ],
            upload=["sketch_2d", "aedt_file", "sat_file", "generated_geometry_status"],
        )
    )
    def generate_geometry(self):
        """Generate the 2D geometry model of the electric motor."""

        Path(self.sketch_2d.path).parent.mkdir(parents=True, exist_ok=True)

        maxwell2D.generate_geometry(
            self.motor_prop,
            self.selected_aedt_version,
            os.path.splitext(self.project_name)[0],
            self.design_name,
            self.setup_name,
            self.solution_type,
            Path(self.sketch_2d.path).parent,
        )

        encoded_image = base64.b64encode(open(self.sketch_2d.path, "rb").read())
        self.sketch_2d.write_bytes(encoded_image)
        self.generated_geometry_status = "success"

    @transaction(
        self=StepSpec(
            download=[
                "selected_aedt_version",
                "project_name",
                "design_name",
                "setup_name",
                "solution_type",
                "aedt_file",
            ],
            upload=["solve_status", "simulation_results", "result_files"],
        )
    )
    @long_running
    def run_maxwell_solve(self):
        """Run Maxwell to solve the 2D transient electromagnetics problem."""

        self.simulation_results = maxwell2D.run_maxwell_solve(
            self.selected_aedt_version,
            os.path.splitext(self.project_name)[0],
            self.design_name,
            self.setup_name,
            self.solution_type,
            Path(self.aedt_file.path).parent,
        )

        if self.simulation_results:
            self.solve_status = "success"
        else:
            self.solve_status = "failure"
