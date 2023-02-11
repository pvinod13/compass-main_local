# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import os

from typing import Dict

from ansys.saf2.sdk import StepModel, StepSpec, FileReference, transaction
from ansys.solutions.compass.compass.solution.electromagnetics_setup_step import (
    ElectromagneticsSetupStep,
)
from ansys.solutions.compass.compass.scripts.maxwell2D import post_process_result


class ElectromagneticsResultsStep(StepModel):
    results: Dict = {}
    selected_filename: str = None
    result_filenames: Dict[str, str] = {}
    alert_message: str = None
    result_file: FileReference = FileReference("Electromagnetics/result_file.csv")

    @transaction(
        self=StepSpec(upload=["result_filenames"]),
        electromagnetics_setup_step=StepSpec(download=["result_files"]),
    )
    def write_csv_file_basenames_to_dict(self, electromagnetics_setup_step: ElectromagneticsSetupStep):
        for file in electromagnetics_setup_step.result_files.list_files():
            base_name = os.path.basename(file.path)
            file_name = base_name.rsplit("_Sinusoidal_")[1]
            file_name = os.path.splitext(file_name)[0]
            self.result_filenames[file_name] = base_name

    @transaction(
        self=StepSpec(download=["selected_filename", "result_filenames"], upload=["result_file", "alert_message"]),
        electromagnetics_setup_step=StepSpec(download=["result_files"]),
    )
    def write_content_from_selected_file_to_filereference(self, electromagnetics_setup_step: ElectromagneticsSetupStep):
        selected_file = (
            electromagnetics_setup_step.result_files.project_path
            / "Electromagnetics"
            / "Example.pyaedt"
            / "Sinusoidal"
            / self.result_filenames[self.selected_filename]
        )

        if selected_file.exists():
            self.alert_message = None
            self.result_file.write_bytes(selected_file.read_bytes())
        else:
            self.alert_message = "Error: File name not found."

    @transaction(self=StepSpec(download=["result_file"], upload=["results"]))
    def get_result_data(self):
        self.results = post_process_result(self.result_file.path)
