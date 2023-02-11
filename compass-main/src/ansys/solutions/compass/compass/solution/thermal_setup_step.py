# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import json

from pathlib import Path
from typing import Dict, List

from ansys.saf2.sdk import StepModel, StepSpec, FileReference, FileGroupReference, transaction, long_running
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)
from ansys.solutions.compass.compass.scripts.generate_cad import prepare_inputs_for_geom, generate_cad
from ansys.solutions.compass.compass.scripts.thermal import (
    prepare_inputs_for_thermal_simu,
    launch_mechanical_simulation,
)
from ansys.solutions.compass.compass.scripts.session_setup import get_product_version_numbers


class ThermalSetupStep(StepModel):
    uri_file_data: str = ""
    output_from_scdm: str = None
    geom_inputs: Dict = {}
    thermal_results = {
        "windings": {"Minimum": "", "Average": "", "Maximum": ""},
        "housings": {"Minimum": "", "Average": "", "Maximum": ""},
        "teeth": {"Minimum": "", "Average": "", "Maximum": ""},
        "shaft": {"Minimum": "", "Average": "", "Maximum": ""},
        "stator": {"Minimum": "", "Average": "", "Maximum": ""},
        "pm": {"Minimum": "", "Average": "", "Maximum": ""},
        "all_bodies": {"Minimum": "", "Average": "", "Maximum": ""},
        "bearings": {"Minimum": "", "Average": "", "Maximum": ""},
        "rotor": {"Minimum": "", "Average": "", "Maximum": ""},
    }
    selected_mechanical_version: str = None
    available_mechanical_versions: List[str] = []
    authorized_mechanical_versions: List[str] = ["2023.1"]
    mechanical_version_alert: str = None
    geometry_build_status: str = "initial"  # Possible status: initial, in-progress, failure, success
    mechanical_solve_status: str = "initial"  # Possible status: initial, in-progress, failure, success
    cooling_type: str = "Water Jacket"
    cooling_type_options: List[str] = ["Water Jacket", "None"]
    internal_flow_film_coef: float = 200
    external_air_film_coef: float = 10
    ambient_temperature: float = 15
    mesh_size: str = "Coarse"
    mesh_size_options: List[str] = ["Fine", "Coarse"]
    selected_queue: str = "Local"
    authorized_queue_options: List[str] = ["Local", "HPC"]
    num_cpus: int = 1
    max_cpu: int = 1000
    mechanical_simulation_result: str = None
    geometry_template = FileReference("Thermal/geometry_template_3d.scdoc")
    scdm_script_to_run = FileReference("Thermal/scdm_generate_cad.py")
    generated_geometry = FileReference("Thermal/generated_geometry.scdoc")
    mechanical_script_to_run = FileReference("Thermal/mechanical_script.py")
    materials_file = FileReference("Thermal/Materials.xml")
    thermal_result_files = FileGroupReference("Thermal/*.png")
    thermal_results_serialized = FileReference("Thermal/thermal-results.json")

    @transaction(
        self=StepSpec(
            download=["authorized_mechanical_versions"],
            upload=["available_mechanical_versions", "selected_mechanical_version", "mechanical_version_alert"],
        )
    )
    def fetch_available_mechanical_versions(self):
        available_products = get_product_version_numbers()
        if not available_products["Workbench"]:
            self.mechanical_version_alert = "Mechanical is not installed."

        if self.authorized_mechanical_versions:
            self.available_mechanical_versions = [
                mechanical_version
                for mechanical_version in available_products["Workbench"]
                if mechanical_version in self.authorized_mechanical_versions
            ]  # Checks if at least one of the installed mechanical versions matches the requirements
            if not self.available_mechanical_versions:
                self.mechanical_version_alert = "At least one of these versions is required for Mechanical: "
                for mechanical_version in self.authorized_mechanical_versions:
                    self.mechanical_version_alert += "%s " % (mechanical_version)
                return
        else:
            self.available_mechanical_versions = available_products["Workbench"]

        self.selected_mechanical_version = self.available_mechanical_versions[
            0
        ]  # Selected mechanical version set arbitrarily

    @transaction(self=StepSpec(upload=["geometry_template"]))
    def write_geometry_template_to_filereference(self):
        """Upload geometry 3D template file to local project directory"""
        original_geom_template_file = (
            Path(__file__).parent.absolute().parent / "scripts" / "assets" / "Leaf360_for_script.scdoc"
        )
        self.geometry_template.write_bytes(original_geom_template_file.read_bytes())

    @transaction(self=StepSpec(upload=["scdm_script_to_run"]))
    def write_scdm_script_file_to_filereference(self):
        """Upload SCDM script file to local project directory"""
        original_scdm_script_file = (
            Path(__file__).parent.absolute().parent / "scripts" / "assets" / "scdm_generate_cad.py"
        )
        self.scdm_script_to_run.write_bytes(original_scdm_script_file.read_bytes())

    @transaction(self=StepSpec(upload=["mechanical_script_to_run"]))
    def write_mechanical_script_file_to_filereference(self):
        """Upload mechanical script file to local project directory"""
        original_mechanical_script_file = (
            Path(__file__).parent.absolute().parent / "scripts" / "assets" / "mechanical_script.py"
        )
        self.mechanical_script_to_run.write_bytes(original_mechanical_script_file.read_bytes())

    @transaction(self=StepSpec(upload=["materials_file"]))
    def write_materials_file_to_filereference(self):
        """Upload materials file to local project directory"""
        original_material_file = Path(__file__).parent.absolute().parent / "scripts" / "assets" / "Materials.xml"
        self.materials_file.write_bytes(original_material_file.read_bytes())

    @transaction(
        self=StepSpec(
            download=["cooling_type_options", "cooling_type", "geometry_template", "scdm_script_to_run"],
            upload=["geometry_build_status", "geom_inputs", "generated_geometry", "uri_file_data"],
        ),
        electromagnetics_setup_step=StepSpec(download=["sat_file"]),
    )
    @long_running
    def generate_geometry(self, electromagnetics_setup_step: ElectromagneticsSetupStep):
        if self.cooling_type not in self.cooling_type_options:
            raise Exception("Cooling type value not valid")

        self.geom_inputs = prepare_inputs_for_geom(
            electromagnetics_setup_step.sat_file.path, self.geometry_template.path
        )
        output_from_scdm = generate_cad(self.geom_inputs, self.scdm_script_to_run.path)

        if output_from_scdm == None:
            self.uri_file_data = ""
        elif output_from_scdm.startswith("Error"):
            self.uri_file_data = ""
        else:
            self.uri_file_data = output_from_scdm

        self.geometry_build_status = "success"

    @transaction(
        self=StepSpec(
            download=[
                "generated_geometry",
                "mechanical_script_to_run",
                "materials_file",
                "internal_flow_film_coef",
                "external_air_film_coef",
                "ambient_temperature",
                "mesh_size",
            ],
            upload=[
                "mechanical_simulation_result",
                "mechanical_solve_status",
                "thermal_result_files",
                "thermal_results_serialized",
                "thermal_results",
            ],
        ),
        electromagnetics_setup_step=StepSpec(
            download=["simulation_results"],
        ),
    )
    @long_running
    def launch_thermal_simulation(self, electromagnetics_setup_step: ElectromagneticsSetupStep):
        geometry_file = self.generated_geometry.path
        mechanical_script = self.mechanical_script_to_run.path
        materials_file = self.materials_file.path
        simulation_input_parameters = {}
        simulation_input_parameters["internal_flow_film_coefficient"] = self.internal_flow_film_coef
        simulation_input_parameters["external_air_film_coefficient"] = self.external_air_film_coef
        simulation_input_parameters["ambient_temperature"] = self.ambient_temperature
        simulation_input_parameters["mesh_size"] = self.mesh_size

        aedt_results = electromagnetics_setup_step.simulation_results
        simu_param_for_mech = prepare_inputs_for_thermal_simu(simulation_input_parameters, aedt_results)

        self.mechanical_simulation_result, self.mechanical_solve_status = launch_mechanical_simulation(
            geometry_file, mechanical_script, materials_file, simu_param_for_mech, Path(geometry_file).parent.absolute()
        )

        with open(self.thermal_results_serialized.path) as jsonDataFile:
            self.thermal_results = json.load(jsonDataFile)

        # Reshape thermal results object
        for item, subitems in self.thermal_results.items():
            for subitem in ["Minimum", "Maximum", "Average"]:
                self.thermal_results[item][subitem] = str(round(float(subitems[subitem].split(" [C]")[0]), 2))
