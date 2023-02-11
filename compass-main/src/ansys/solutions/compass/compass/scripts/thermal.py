# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

import json
import glob
import logging
import os
import shutil

from ansys.mechanical.core import LOG, launch_mechanical
from pathlib import Path

import logging

# =================================================== [Functions] =================================================== #


def check_input(data):

    # validation of inputs
    msg_out = ""
    min_internal_flow_film_coefficient = 10.0
    max_internal_flow_film_coefficient = 100000.0
    min_external_air_film_coefficient = 0.5
    max_external_air_film_coefficient = 70.0

    if data["internal_flow_film_coefficient"] < min_internal_flow_film_coefficient:
        msg_out += (
            "Internal Flow Film Coefficient can't be smaller than " + str(min_internal_flow_film_coefficient) + ".\n"
        )
    elif data["internal_flow_film_coefficient"] > max_internal_flow_film_coefficient:
        msg_out += (
            "Internal Flow Film Coefficient can't be greater than " + str(max_internal_flow_film_coefficient) + ".\n"
        )
    if data["external_air_film_coefficient"] < min_external_air_film_coefficient:
        msg_out += (
            "External Air Film Coefficient can't be smaller than " + str(min_external_air_film_coefficient) + ".\n"
        )
    elif data["external_air_film_coefficient"] > max_external_air_film_coefficient:
        msg_out += (
            "External Air Film Coefficient can't be greater than " + str(max_external_air_film_coefficient) + ".\n"
        )
    if data["ambient_temperature"] == "" or data["ambient_temperature"] == None:
        msg_out += "Please input Ambient Temperature. \n"
    if data["mesh_size"] == "" or data["mesh_size"] == None:
        msg_out += "Please set Mesh Size. \n"

    if msg_out != "":
        msg_out = "Error: " + msg_out

    return msg_out


def prepare_inputs_for_thermal_simu(simu_data, magnetics_results_data):
    simu_params = {}

    # Inputs from Maxwell analysis
    list_of_inputs = [
        "rotor_loss_avg",
        "stator_loss_avg",
        "pm_i1_loss_avg",
        "pm_i2_loss_avg",
        "pm_o1_loss_avg",
        "pm_o2_loss_avg",
        "stranded_loss_avg",
    ]
    for key, val in magnetics_results_data.items():
        if key in list_of_inputs:
            simu_params[key] = "{} [W]".format(val)

    # Inputs from UI
    check_input_msg = check_input(simu_data)
    if check_input_msg != "":
        simu_params["Error Message"] = check_input_msg
        return simu_params

    simu_params.update(simu_data)
    simu_params["external_air_film_coefficient"] = "{} [W m^-2 C^-1]".format(
        simu_params["external_air_film_coefficient"]
    )
    simu_params["internal_flow_film_coefficient"] = "{} [W m^-2 C^-1]".format(
        simu_params["internal_flow_film_coefficient"]
    )
    simu_params["ambient_temperature"] = "{} [C]".format(simu_params["ambient_temperature"])

    return simu_params


def prepare_inputs_for_simu(simu_data, magnetics_results_data):
    simu_params = {}

    # check if maxwell analysis was run
    file_name = get_sat_file(magnetics_results_data)
    if not file_name:
        simu_params["Error Message"] = "Maxwell analysis required. Please launch it first."
        return simu_params

    # Inputs from Maxwell analysis
    list_of_inputs = [
        "rotor_loss_avg",
        "stator_loss_avg",
        "pm_i1_loss_avg",
        "pm_i2_loss_avg",
        "pm_o1_loss_avg",
        "pm_o2_loss_avg",
        "stranded_loss_avg",
    ]
    for key, val in magnetics_results_data.items():
        if key in list_of_inputs:
            simu_params[key] = "{} [W]".format(val)

    # Inputs from UI
    check_input_msg = check_input(simu_data)
    if check_input_msg != "":
        simu_params["Error Message"] = check_input_msg
        return simu_params

    simu_params.update(simu_data)
    simu_params["external_air_film_coefficient"] = "{} [W m^-2 C^-1]".format(
        simu_params["external_air_film_coefficient"]
    )
    simu_params["internal_flow_film_coefficient"] = "{} [W m^-2 C^-1]".format(
        simu_params["internal_flow_film_coefficient"]
    )
    simu_params["ambient_temperature"] = "{} [C]".format(simu_params["ambient_temperature"])

    return simu_params


def launch_mechanical_simulation(geometry_file, mechanical_script, materials_file, simu_parameters, working_directory):

    # logging.basicConfig(filename=r'C:\Users\iazehaf\Documents\launch_mechanical_simulation.log', filemode='w', level=logging.DEBUG)

    results = {}
    msg_out = ""

    LOG.setLevel(logging.DEBUG)
    mechanical = launch_mechanical(loglevel="DEBUG", cleanup_on_exit=True, batch=False, version="231")

    # Debug
    # logging.basicConfig(filename=r'C:\Users\iazehaf\Documents\thermal.log', filemode='w', level=logging.DEBUG)

    try:
        mechanical.run_python_script("ExtAPI.DataModel.Project.New()")
        directory = mechanical.run_python_script("ExtAPI.DataModel.Project.ProjectDirectory")
        mechanical.upload(file_name=geometry_file, file_location_destination=directory, chunk_size=1024 * 1024)
        mechanical.upload(file_name=materials_file, file_location_destination=directory, chunk_size=1024 * 1024)

        mechanical.run_python_script("global input_simu_parameters")
        mechanical.run_python_script("input_simu_parameters = " + json.dumps(simu_parameters))

        results = mechanical.run_python_script_from_file(mechanical_script, enable_logging=True)

        transaction_directory = Path(geometry_file).resolve().parents[0]

        mechanical.download(glob.glob("*.png"), target_dir=transaction_directory, chunk_size=1024 * 1024)

        msg_out = "success"

        if results != None and results != "":
            results = json.loads(results)

        mechanical.exit(force=True)

    except:
        mechanical.exit(force=True)
        msg_out = "failure"
        pass

    # Transfer result images to working directory
    # logging.info('Transfer result images to working directory')
    for file in glob.glob(os.path.join(directory, "*.png")):
        shutil.copy(file, os.path.join(working_directory, os.path.basename(file)))
    # logging.info('Done')

    # Transfer thermal results object to working directory
    # logging.info('Transfer thermal results object to working directory')
    shutil.copy(
        os.path.join(directory, "thermal-results.json"), os.path.join(working_directory, "thermal-results.json")
    )
    # logging.info('Done')

    return results, msg_out


# Debug
# geometry_file = r"C:\Users\iazehaf\AppData\Local\Temp\AnsysMech8986\Project_Mech_Files\generated_geometry.scdoc"
# mechanical_script = r"C:\Users\iazehaf\AppData\Local\Temp\AnsysMech8986\Project_Mech_Files\mechanical_script.py"
# materials_file = r"C:\Users\iazehaf\AppData\Local\Temp\AnsysMech8986\Project_Mech_Files\Materials.xml"
# simu_parameters = {
#     'stator_loss_avg': '307.52 [W]',
#     'rotor_loss_avg': '52.29 [W]',
#     'pm_i1_loss_avg': '0.71 [W]',
#     'pm_i2_loss_avg': '0.71 [W]',
#     'pm_o1_loss_avg': '3.32 [W]',
#     'pm_o2_loss_avg': '6.00 [W]',
#     'stranded_loss_avg': '1306.46 [W]',
#     'internal_flow_film_coefficient': '200.0 [W m^-2 C^-1]',
#     'external_air_film_coefficient': '10.0 [W m^-2 C^-1]',
#     'ambient_temperature': '15.0 [C]',
#     'mesh_size': 'Coarse'
# }
# working_directory = r"C:\Users\iazehaf\AppData\Local\Temp\saf_8lwp2uw0"
# a,b = launch_mechanical_simulation(geometry_file, mechanical_script, materials_file, simu_parameters, working_directory)

# print(a)
# print(b)
