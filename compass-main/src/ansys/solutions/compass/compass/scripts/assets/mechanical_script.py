# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

import os
import json
import clr
import logging
import tempfile

clr.AddReference("System.Collections")
# from System.Collections.Generic import List

mech_log_temp_dir = tempfile.mkdtemp(prefix="mech-logs-")
mech_log_file = os.path.join(mech_log_temp_dir, "mechanical.log")

logging.basicConfig(
    filename=mech_log_file,
    filemode="w",
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

logging.info("Started")

# =================================================== [Functions] =================================================== #


def launch_thermal_simulation(simu_parameters=None):

    simu_parameters = get_inputs(simu_parameters)
    current_analysis = ExtAPI.DataModel.Project.Model.AddSteadyStateThermalAnalysis()
    directory = ExtAPI.DataModel.Project.ProjectDirectory
    file_path_modified = os.path.join(directory, "generated_geometry.scdoc")
    import_geometry(file_path_modified)

    create_contacts()

    material_file = os.path.join(directory, "Materials.xml")
    set_materials(material_file)

    create_mesh(simu_parameters)
    logging.info("after meshing")
    set_analysis_settings(current_analysis)
    set_loads(current_analysis, simu_parameters)
    set_results(current_analysis)
    current_analysis.Solve(True)
    logging.info("after solving")
    check_solution_status(current_analysis)
    result = export_results(current_analysis)
    # Serialize the result dictionary
    with open(os.path.join(directory, "thermal-results.json"), "w") as file:
        file.write(result)
    return result


def get_inputs(simu_parameters):

    global input_simu_parameters

    if simu_parameters != None:
        return simu_parameters
    try:
        if input_simu_parameters != None:
            print("Info: global simu_parameters are used")
            return input_simu_parameters
    except:
        pass

    # Debug purpose
    logging.info("Debug: simu_parameters couldn't be found and default values are used")
    simu_parameters = {}
    simu_parameters["external_air_film_coefficient"] = "5 [W m^-2 C^-1]"
    simu_parameters["internal_flow_film_coefficient"] = "100 [W m^-2 C^-1]"
    simu_parameters["ambient_temperature"] = "22 [C]"
    simu_parameters["mesh_size"] = "Coarse"
    simu_parameters["rotor_loss_avg"] = "60 [W]"
    simu_parameters["stator_loss_avg"] = "300 [W]"
    simu_parameters["pm_i1_loss_avg"] = "0.5 [W]"
    simu_parameters["pm_i2_loss_avg"] = "0.51 [W]"
    simu_parameters["pm_o1_loss_avg"] = "2.4 [W]"
    simu_parameters["pm_o2_loss_avg"] = "2.7 [W]"
    simu_parameters["stranded_loss_avg"] = "1300 [W]"
    return simu_parameters


def import_geometry(geometry_file):
    geometry_import = Model.GeometryImportGroup.AddGeometryImport()
    geometry_import_format = Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
    geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
    geometry_import_preferences.ProcessNamedSelections = True
    geometry_import_preferences.NamedSelectionKey = ""
    geometry_import_preferences.ProcessMaterialProperties = False
    geometry_import.Import(geometry_file, geometry_import_format, geometry_import_preferences)


def set_analysis_settings(analysis):

    ExtAPI.DataModel.Project.UnitSystem = UserUnitSystemType.StandardMKS
    if analysis.AnalysisType == AnalysisType.Static:
        pass
    elif analysis.AnalysisType == AnalysisType.Transient:
        step_end_time = [
            Quantity("0.1 [s]"),
            Quantity("10.1 [s]"),
            Quantity("8000.1 [s]"),
            Quantity("8010.1 [s]"),
            Quantity("20000 [s]"),
        ]
        initial_time_step = [
            Quantity("0.05 [s]"),
            Quantity("0.1 [s]"),
            Quantity("0.1 [s]"),
            Quantity("0.1 [s]"),
            Quantity("0.1 [s]"),
        ]
        minimum_time_step = [
            Quantity("0.05 [s]"),
            Quantity("0.1 [s]"),
            Quantity("0.1 [s]"),
            Quantity("0.1 [s]"),
            Quantity("0.1 [s]"),
        ]
        maximum_time_step = [
            Quantity("0.1 [s]"),
            Quantity("5 [s]"),
            Quantity("500 [s]"),
            Quantity("10 [s]"),
            Quantity("2000 [s]"),
        ]
        time_integration = [False, True, True, True, True]
        auto_time_stepping = [
            AutomaticTimeStepping.On,
            AutomaticTimeStepping.On,
            AutomaticTimeStepping.On,
            AutomaticTimeStepping.On,
            AutomaticTimeStepping.On,
        ]
        settings = analysis.AnalysisSettings
        settings.NumberOfSteps = len(step_end_time)
        for current_step_number in range(settings.NumberOfSteps - 1, -1, -1):
            settings.CurrentStepNumber = current_step_number + 1
            settings.StepEndTime = step_end_time[current_step_number]
            settings.AutomaticTimeStepping = auto_time_stepping[current_step_number]
            settings.TimeIntegration = time_integration[current_step_number]
            settings.InitialTimeStep = initial_time_step[current_step_number]
            settings.MinimumTimeStep = minimum_time_step[current_step_number]
            settings.MaximumTimeStep = maximum_time_step[current_step_number]


def set_loads(analysis, simu_parameters):

    logging.info("Setting loads")
    logging.info("simu parameters ---> {0}".format(simu_parameters))

    model_scale = 1.0

    if analysis.AnalysisType == AnalysisType.Static:

        #################### Initial Temperature #######################
        analysis.Children[0].InitialTemperatureValue = Quantity(simu_parameters["ambient_temperature"])

        #################### Internal heat generation #######################
        set_internal_heat(analysis, "Stator", "B_Stator", Quantity(simu_parameters["stator_loss_avg"]), model_scale)
        set_internal_heat(analysis, "Rotor", "B_Rotor", Quantity(simu_parameters["rotor_loss_avg"]), model_scale)
        set_internal_heat(analysis, "PM_I1", "B_PM_I1", Quantity(simu_parameters["pm_i1_loss_avg"]), model_scale)
        set_internal_heat(analysis, "PM_I2", "B_PM_I2", Quantity(simu_parameters["pm_i2_loss_avg"]), model_scale)
        set_internal_heat(analysis, "PM_O1", "B_PM_O1", Quantity(simu_parameters["pm_o1_loss_avg"]), model_scale)
        set_internal_heat(analysis, "PM_O2", "B_PM_O2", Quantity(simu_parameters["pm_o2_loss_avg"]), model_scale)
        set_internal_heat(
            analysis, "Windings", "B_Windings", Quantity(simu_parameters["stranded_loss_avg"]), model_scale
        )

        #################### Convection #######################
        # Convection for external air
        convection_external_air = analysis.AddConvection()
        convection_external_air.Name = "Convection_external_air"
        convection_external_air.Location = get_named_selection_by_name("F_External_Air")
        convection_external_air_values = Quantity(simu_parameters["external_air_film_coefficient"])
        convection_external_air.FilmCoefficient.Output.SetDiscreteValue(0, convection_external_air_values)

        # Convection for internal flow
        convection_internal_flow = analysis.AddConvection()
        convection_internal_flow.Name = "Convection_internal_flow"
        convection_internal_flow.Location = get_named_selection_by_name("F_Internal_Flow")
        convection_internal_flow_values = Quantity(simu_parameters["internal_flow_film_coefficient"])
        convection_internal_flow.FilmCoefficient.Output.SetDiscreteValue(0, convection_internal_flow_values)

    elif analysis.AnalysisType == AnalysisType.Transient:
        # internal heat generation
        internal_heat_generation = analysis.AddInternalHeatGeneration()
        internal_heat_generation.Name = "Internal Heat Generation"
        internal_heat_generation.Location = get_named_selection_by_name("B_Windings")
        step_end_time = [
            Quantity("0.1 [s]"),
            Quantity("10.1 [s]"),
            Quantity("8000.1 [s]"),
            Quantity("8010.1 [s]"),
            Quantity("20000 [s]"),
        ]
        internal_heat_generation.Magnitude.Inputs[0].DiscreteValues = step_end_time
        internal_heat_generation_values = [
            Quantity("0 [W m^-3]"),
            Quantity("2E+6 [W m^-3]"),
            Quantity("2E+6 [W m^-3]"),
            Quantity("0 [W m^-3]"),
            Quantity("0 [W m^-3]"),
        ]
        internal_heat_generation.Magnitude.Output.DiscreteValues = internal_heat_generation_values
        # Convection for external air
        convection_external_air = analysis.AddConvection()
        convection_external_air.Name = "Convection_external_air"
        convection_external_air.Location = get_named_selection_by_name("F_External_Air")
        step_end_time = [
            Quantity("0.1 [s]"),
            Quantity("10.1 [s]"),
            Quantity("8000.1 [s]"),
            Quantity("8010.1 [s]"),
            Quantity("20000 [s]"),
        ]
        convection_external_air.FilmCoefficient.Inputs[0].DiscreteValues = step_end_time
        convection_external_air_values = [
            Quantity("5 [W m^-2 C^-1]"),
            Quantity("5 [W m^-2 C^-1]"),
            Quantity("5 [W m^-2 C^-1]"),
            Quantity("5 [W m^-2 C^-1]"),
            Quantity("5 [W m^-2 C^-1]"),
        ]
        convection_external_air.FilmCoefficient.Output.DiscreteValues = convection_external_air_values
        # Convection for internal flow
        convection_internal_flow = analysis.AddConvection()
        convection_internal_flow.Name = "Convection_internal_flow"
        convection_internal_flow.Location = get_named_selection_by_name("F_Internal_Flow")
        step_end_time = [
            Quantity("0.1 [s]"),
            Quantity("10.1 [s]"),
            Quantity("8000.1 [s]"),
            Quantity("8010.1 [s]"),
            Quantity("20000 [s]"),
        ]
        convection_internal_flow.FilmCoefficient.Inputs[0].DiscreteValues = step_end_time
        convection_internal_flow_values = [
            Quantity("100 [W m^-2 C^-1]"),
            Quantity("100 [W m^-2 C^-1]"),
            Quantity("100 [W m^-2 C^-1]"),
            Quantity("100 [W m^-2 C^-1]"),
            Quantity("100 [W m^-2 C^-1]"),
        ]
        convection_internal_flow.FilmCoefficient.Output.DiscreteValues = convection_internal_flow_values

    logging.info("Setting loads completed!")


def set_internal_heat(analysis, prefix, named_selection_name, loss, model_scale):

    internal_heat_generation = analysis.AddInternalHeatGeneration()
    internal_heat_generation.Name = prefix + " Internal Heat Generation"
    named_selection = get_named_selection_by_name(named_selection_name)
    internal_heat_generation.Location = named_selection
    volume = get_volume_of_named_selection(named_selection) * model_scale
    value = loss / volume
    internal_heat_generation_values = value
    internal_heat_generation.Magnitude.Output.SetDiscreteValue(0, internal_heat_generation_values)


def create_contacts():
    connections = Model.AddConnections()
    connection_group = connections.AddConnectionGroup()
    connection_group.CreateAutomaticConnections()


def create_mesh(simu_params):

    logging.info("Creating mesh...")
    logging.info("simu parameters ---> {0}".format(simu_params))

    mesh_sizing = [
        Quantity(2e-4, "m"),
        Quantity(2e-3, "m"),
        Quantity(3e-3, "m"),
        Quantity(5e-3, "m"),
        Quantity(7.5e-3, "m"),
    ]
    mesh_div = [30]

    if simu_params["mesh_size"] == "Medium":
        pass
    elif simu_params["mesh_size"] == "Fine":
        for ind, val in enumerate(mesh_sizing):
            mesh_sizing[ind] = val / 2
        for ind, val in enumerate(mesh_div):
            mesh_div[ind] = val * 2

    elif simu_params["mesh_size"] == "Coarse":
        for ind, val in enumerate(mesh_sizing):
            mesh_sizing[ind] = val * 2
        for ind, val in enumerate(mesh_div):
            mesh_div[ind] = val / 2

    mesh = Model.Mesh
    # sizing
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("B_Windings")
    current_sizing.ElementSize = mesh_sizing[4]
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("B_PM")
    current_sizing.ElementSize = mesh_sizing[3]
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("B_All_Shaft")
    current_sizing.ElementSize = mesh_sizing[3]
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("E_PM")
    current_sizing.ElementSize = mesh_sizing[1]
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("B_Bearings")
    current_sizing.ElementSize = mesh_sizing[2]
    # face meshing
    current_meshing = mesh.AddFaceMeshing()
    current_meshing.Location = get_named_selection_by_name("F_Bearings_Mesh")
    # sizing
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("B_Housings")
    current_sizing.ElementSize = mesh_sizing[4]
    current_sizing = mesh.AddSizing()
    current_sizing.Location = get_named_selection_by_name("B_Stator")
    current_sizing.ElementSize = mesh_sizing[4]
    # sweep methods
    teeth_ids = get_named_selection_by_name("B_Tooth").Location.Ids
    teeth_faces_ids = get_named_selection_by_name("F_Tooth").Location.Ids
    sweep_body_faces_dict = {}
    tolerance = 1e-6
    for tooth_id in teeth_ids:
        for curr_face_id in teeth_faces_ids:
            curr_face = DataModel.GeoData.GeoEntityById(curr_face_id)
            if curr_face.Bodies[0].Id == tooth_id:
                tooth_face = curr_face
                break
        tooth_face_id = tooth_face.Id
        tooth = DataModel.GeoData.GeoEntityById(tooth_id)
        for face in tooth.Faces:
            if face.Id != tooth_face_id and abs(face.Area - tooth_face.Area) < tolerance:
                sweep_body_faces_dict[tooth_id] = [tooth_face_id, face.Id]
                break
    for body_id, face_ids in sweep_body_faces_dict.items():
        current_method = mesh.AddAutomaticMethod()
        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        selection.Ids = [body_id]
        current_method.Location = selection
        current_method.Method = MethodType.Sweep
        current_method.SourceTargetSelection = 2
        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        selection.Ids = [face_ids[0]]
        current_method.SourceLocation = selection
        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        selection.Ids = [face_ids[1]]
        current_method.TargetLocation = selection
        current_method.FreeFaceMeshType = 2
        current_method.SweepNumberDivisions = mesh_div[0]
    # inflations
    inflation_face_edges_dict = {}
    for face_id in teeth_faces_ids:
        face = DataModel.GeoData.GeoEntityById(face_id)
        inflation_face_edges_dict[face_id] = [edge.Id for edge in face.Edges]
    for face_id, edge_ids in inflation_face_edges_dict.items():
        inflation = mesh.AddInflation()
        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        selection.Ids = [face_id]
        inflation.Location = selection
        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        selection.Ids = edge_ids
        inflation.BoundaryLocation = selection
        inflation.InflationOption = 1
        inflation.FirstLayerHeight = mesh_sizing[0]
        inflation.MaximumLayers = 2

    logging.info("Create mesh completed")


def set_materials(geometry_materials=None):
    # TODO: geometry_materials should be an input
    import_materials_file(geometry_materials)
    assign_materials()


def assign_materials(geometry_materials=None):
    # let's assume we have a dict: geometry_materials["location"] = "material_name"
    # TODO: geometry_materials should be an input
    geometry_materials = {}
    geometry_materials["magnets"] = "n30uh"
    geometry_materials["bearings"] = "Steel bearing"
    geometry_materials["shaft"] = "Steel 1008"
    geometry_materials["stator"] = "m_350_50A"
    geometry_materials["windings"] = "Copper Alloy_axial_windings"
    geometry_materials["end_windings"] = "Copper Alloy_end_windings"
    geometry_materials["housings"] = "Aluminum Alloy"
    geometry_materials["rotor_core"] = "Steel 1008"  # in Maxwell it's same as stator. TODO: verify
    geometry_materials[
        "outer_housing"
    ] = "Steel 1008"  # in thermal analysis... I was expecting "Alluminoy Alloy". TODO: verify
    geometry_materials["air_gap"] = "Air Gap"
    geometry_materials["insulation"] = "Insulation"
    # magnets
    add_material_assignement(get_named_selection_by_name("B_PM"), geometry_materials["magnets"])
    add_material_assignement(get_named_selection_by_name("B_Bearings"), geometry_materials["bearings"])
    add_material_assignement(get_named_selection_by_name("B_All_Shaft"), geometry_materials["shaft"])
    add_material_assignement(get_named_selection_by_name("B_Stator"), geometry_materials["stator"])
    add_material_assignement(get_named_selection_by_name("B_Tooth"), geometry_materials["stator"])
    add_material_assignement(get_named_selection_by_name("B_Housings"), geometry_materials["housings"])
    add_material_assignement(get_named_selection_by_name("B_Rotor"), geometry_materials["rotor_core"])
    add_material_assignement(get_named_selection_by_name("B_Air_Gap"), geometry_materials["air_gap"])
    add_material_assignement(get_named_selection_by_name("B_Insulation"), geometry_materials["insulation"])
    # uppermount == outer_housing
    selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    selIds = [ExtAPI.DataModel.GetObjectsByName("Uppermount")[0].Children[0].GetGeoBody().Id]
    selection.Ids = selIds
    add_material_assignement(selection, geometry_materials["outer_housing"])
    add_material_assignement(get_named_selection_by_name("B_Coil"), geometry_materials["windings"])
    # for Windings ends we need another material as it is orthotropic
    windings_ids = get_named_selection_by_name("B_Windings").Location.Ids
    coil_ids = get_named_selection_by_name("B_Coil").Location.Ids
    end_winding_ids = list(set(windings_ids) - set(coil_ids))
    selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    selection.Ids = end_winding_ids
    add_material_assignement(selection, geometry_materials["end_windings"])


def add_material_assignement(selection, material_name):
    material_assignment = Model.Materials.AddMaterialAssignment()
    material_assignment.Location = selection
    material_assignment.Material = material_name
    Tree.Refresh()


def import_materials_file(materials_file):
    """TODO - no official API. Here is an undocumented way that will work on windows. 23R1 will have this feature"""
    material_file = materials_file.replace("\\", "\\\\")
    script = 'DS.Tree.Projects.Item(1).LoadEngrDataLibraryFromFile("' + material_file + '");'
    ExtAPI.Application.ScriptByName("jscript").ExecuteCommand(script)


def get_material_file():
    material_file = os.path.join(r"C:\Test", "Materials.xml")
    return material_file
    analysis = ExtAPI.DataModel.AnalysisList[0]
    working_directory = analysis.WorkingDir
    user_directory = os.path.dirname(working_directory)
    for i in range(4):
        user_directory = os.path.dirname(user_directory)


def get_named_selection_by_name(ns_name):
    """
    Get the named selection of name nsName
    :param ns_name: string of the named selection
    :return named_selection: the named selection object
    """
    try:
        # named_selections = DataModel.Project.GetChildren(DataModelObjectCategory.NamedSelection, True)
        named_selections = DataModel.Project.Model.NamedSelections
        for named_selection in named_selections.Children:
            if named_selection.Name == ns_name:
                return named_selection
        return None
    except:
        return None


def get_volume_of_named_selection(named_selection):
    """
    Get the named selection's volume
    :param named_selection: the named selection
    :return volume: volume of named_selection
    """
    try:
        volume_value = 0.0
        for entity in named_selection.Entities:
            volume_value += entity.Volume
        return Quantity(volume_value, "m^3")
    except:
        return Quantity(0.0, "m^3")


def set_results(analysis):
    logging.info("Setting results...")
    temp = analysis.Solution.AddTemperature()
    temp.Name = "All_Bodies"
    create_temperature_result(analysis, "Rotor", "B_Rotor")
    create_temperature_result(analysis, "Stator", "B_Stator")
    create_temperature_result(analysis, "PM", "B_PM")
    create_temperature_result(analysis, "Windings", "B_Windings")
    create_temperature_result(analysis, "Teeth", "B_Tooth")
    create_temperature_result(analysis, "Shaft", "B_Shaft")
    create_temperature_result(analysis, "Bearings", "B_Bearings")
    create_temperature_result(analysis, "Housings", "B_Housings")
    logging.info("Setting results completed!")


def create_temperature_result(analysis, name, named_selection_name):
    temp = analysis.Solution.AddTemperature()
    temp.Name = name
    named_selection = get_named_selection_by_name(named_selection_name)
    if named_selection.Entities.Count > 0:
        temp.Location = get_named_selection_by_name(named_selection_name)
    else:
        logging.info("Named selection is empty in create_temperature_result")


def export_results(analysis):

    # TODO: it might be possible to export .avz when bug opened 723749 is resolved

    results = {}
    create_section_planes()

    for result in analysis.Solution.Children:
        if result.GetType() == Ansys.ACT.Automation.Mechanical.SolutionInformation:
            continue

        result.Activate()
        result_details = {
            "Minimum": str(result.Minimum),
            "Maximum": str(result.Maximum),
            "Average": str(result.Average),
        }
        results[result.Name.lower()] = result_details

        export_images(result)

    json_text = json.dumps(results)
    return json_text


def create_section_planes():
    # TODO: bug opened 723749 (issue 2). for now on let's not consider this feature
    return
    try:
        Plane = Ansys.Mechanical.Graphics.SectionPlane()
        Plane.Center = Ansys.Mechanical.Graphics.Point([0, 0, 0], "m")
        Plane.Direction = Ansys.ACT.Math.Vector3D(1, 0, 0)
        Plane.Name = "YZ"
        Plane.Active = False
        ExtAPI.Graphics.SectionPlanes.Add(Plane)

        Plane = Ansys.Mechanical.Graphics.SectionPlane()
        Plane.Center = Ansys.Mechanical.Graphics.Point([0, 0, 0], "m")
        Plane.Direction = Ansys.ACT.Math.Vector3D(0, 1, 0)
        Plane.Name = "XZ"
        Plane.Active = False
        ExtAPI.Graphics.SectionPlanes.Add(Plane)

    except:
        logging.info("Error in create_section_planes()")


def export_images(result):
    # TODO: section plane creation not functional: bug opened 723749 (issue 2).
    #  for now on let's not consider this feature: lines starting by "section_plane" commented
    try:
        directory = ExtAPI.DataModel.Project.ProjectDirectory

        # ISO
        ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
        ExtAPI.Graphics.Camera.SetFit()
        Graphics.Redraw()
        # setting2d = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        ExtAPI.Graphics.ExportImage(os.path.join(directory, result.Name + "_ISO.png"))

        # YZ
        # section_plane = [sp for sp in ExtAPI.Graphics.SectionPlanes if sp.Name == "YZ"][0]
        # section_plane.Active = True
        ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Left)
        ExtAPI.Graphics.Camera.SetFit()
        Graphics.Redraw()
        # setting2d = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        ExtAPI.Graphics.ExportImage(os.path.join(directory, result.Name + "_YZ.png"))
        # section_plane.Active = False

        # XZ
        # section_plane = [sp for sp in ExtAPI.Graphics.SectionPlanes if sp.Name == "XZ"][0]
        # section_plane.Active = True
        ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Bottom)
        ExtAPI.Graphics.Camera.SetFit()
        Graphics.Redraw()
        # setting2d = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
        ExtAPI.Graphics.ExportImage(os.path.join(directory, result.Name + "_XZ.png"))
        # section_plane.Active = False

    except:
        logging.info("Error in export_images()")


def save_mechdb(file_path):
    file_path_modified = file_path.replace("\\", "\\\\")
    # we are working with iron python 2.7 on mechanical side
    # use python 2.7 style formatting
    script = "%s" % file_path_modified
    script = 'DS.Script.doStandaloneFileSaveAs("%s");' % script
    ExtAPI.Application.ScriptByName("jscript").ExecuteCommand(script)
    logging.info("save_mechdb finished")


def save_mechdb2(file_path):
    ExtAPI.DataModel.Project.Subject = file_path
    ExtAPI.DataModel.Project.Save(file_path)
    logging.info("save_mechdb2 finished")


def check_solution_status(analysis):
    logging.info("analysis status: " + str(analysis.ObjectState))
    logging.info("solution status: " + str(analysis.Solution.ObjectState))


def save_mechdb(file_path):
    file_path_modified = file_path.replace("\\", "\\\\")
    # we are working with iron python 2.7 on mechanical side
    # use python 2.7 style formatting
    script = "%s" % file_path_modified
    script = 'DS.Script.doStandaloneFileSaveAs("%s");' % script
    logging.info(script)
    ExtAPI.Application.ScriptByName("jscript").ExecuteCommand(script)
    logging.info("save_mechdb finished")


def save_mechdb2(file_path):
    # logging.info("opening " + file_path)
    ExtAPI.DataModel.Project.Subject = file_path
    ExtAPI.DataModel.Project.Save(file_path)
    # logging.info"opened " + file_path )
    logging.info("save_mechdb2 finished")


def check_solution_status(analysis):
    logging.info("analysis status: " + str(analysis.ObjectState))
    logging.info("solution status: " + str(analysis.Solution.ObjectState))


# =================================================== [Execution] =================================================== #

launch_thermal_simulation()

logging.info("Finished")
