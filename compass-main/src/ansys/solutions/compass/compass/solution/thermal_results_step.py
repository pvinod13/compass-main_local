# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import base64

from ansys.saf2.sdk import StepModel, StepSpec, FileReference, transaction
from ansys.solutions.compass.compass.solution.thermal_setup_step import ThermalSetupStep


class ThermalResultsStep(StepModel):
    part_name: str = None
    visu_type: str = None
    image_file: FileReference = FileReference("Thermal/Current_Result_Image.png")

    @transaction(
        self=StepSpec(download=["part_name", "visu_type"], upload=["image_file"]),
        thermal_setup_step=StepSpec(download=["thermal_result_files"]),
    )
    def get_image(self, thermal_setup_step: ThermalSetupStep):
        for file in thermal_setup_step.thermal_result_files.list_files():
            file_name = file.path.split(".png")[0]
            if self.part_name.replace(" ", "_") in file_name:
                visu_type_prefix = self.visu_type.split(" ")[0]
                if file_name.endswith(visu_type_prefix):
                    encoded_image = base64.b64encode(open(file.path, "rb").read())
                    self.image_file.write_bytes(encoded_image)
                    break
