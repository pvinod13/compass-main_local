# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

import base64
import os
import logging
import tempfile

scdm_log_temp_dir = tempfile.mkdtemp(prefix="scdm-logs-")
scdm_log_file = os.path.join(scdm_log_temp_dir, "scdm.log")

logging.basicConfig(
    filename=scdm_log_file,
    filemode="w",
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

logging.info("Started")

global result

# =================================================== [Functions] =================================================== #


def generate_3d_cad(params):
    try:
        global result
        result = "starting"
        coil_inner_diameter = float(params["dci"])
        result = "coil_inner_diameter done"
        stator_outer_diameter = float(params["dso"])
        result = "stator_outer_diameter done"
        # let's assume I'm working in the scdm file without the shaft/coil/stator/rotor etc
        update_parameters(coil_inner_diameter, stator_outer_diameter)
        result = "update_parameters done"
        result = import_maxwell_file(params["sat_file_path"])
        if result != "success":
            return "Error: " + str(result)
        result = "import_maxwell_file done"
        delete_unused_bodies()
        result = "delete_unused_bodies done"
        split_geometry()
        result = "split_geometry"
        move_sketch()
        result = "move_sketch done"
        revolve_sketch()
        result = "revolve_sketch done"
        create_2d_named_selections()
        result = "create_2d_named_selections done"
        extrude_sketch()
        result = "extrude_sketch done"
        merge_bodies()
        result = "merge_bodies done"
        create_3d_named_selections()
        result = "create_3d_named_selections done"
        ViewHelper.SetViewMode(InteractionMode.Solid, None)

        # save and return
        current_document_directory = os.path.dirname(DocumentHelper.GetActiveDocument().Path)
        scdoc_path = os.path.join(current_document_directory, "generated_geometry.scdoc")
        DocumentSave.Execute(scdoc_path)
        uri_file = get_uri_file(scdoc_path)
        return uri_file

    except:
        result = "Error after: " + str(result)
        return result


def open_scdoc_file(file_path):
    DocumentOpen.Execute(file_path, None)


def update_parameters(coil_inner_diameter, stator_outer_diameter):
    options = OffsetFaceOptions()

    selection = Selection.CreateByGroups(SelectionType.Primary, "solid_housing_inner")
    OffsetFaces.SetRadius(selection, MM(stator_outer_diameter / 2), options)

    selection = Selection.CreateByGroups(SelectionType.Primary, "endwinding_1_inner")
    OffsetFaces.SetRadius(selection, MM(coil_inner_diameter / 2), options)

    selection = Selection.CreateByGroups(SelectionType.Primary, "endwinding_2_inner")
    OffsetFaces.SetRadius(selection, MM(coil_inner_diameter / 2), options)

    selection = Selection.CreateByGroups(SelectionType.Primary, "solid_outer_housing_outer")
    OffsetFaces.SetRadius(selection, MM(stator_outer_diameter / 2), options)

    # don't know how to param this: so commented now
    # selection = Selection.CreateByGroups(SelectionType.Primary, "endwinding_1_outer")
    # OffsetFaces.SetRadius(selection, MM(120), options)
    # selection = Selection.CreateByGroups(SelectionType.Primary, "endwinding_2_outer")
    # OffsetFaces.SetRadius(selection, MM(120), options)


def import_maxwell_file(geom_file_path):
    try:
        res = ""
        if os.path.exists(geom_file_path):
            DocumentInsert.Execute(geom_file_path)
            res = "success"
        else:
            res = "geom_file_path NOT found: " + str(geom_file_path)
        return res

    except:
        return "error in import_maxwell_file"


def delete_unused_bodies():
    list_of_names = ["Region", "Inner_Band", "Band", "Outer_Band", "slot_IM1", "slot_OM1", "slot_IM1_1", "slot_OM1_1"]
    delete_bodies(list_of_names)


def suppress_bodies():
    list_of_names = ["Region", "Inner_Band", "Band", "Outer_Band", "slot_IM1", "slot_OM1", "slot_IM1_1", "slot_OM1_1"]
    hide_bodies(list_of_names)
    suppress_bodies_for_physics(list_of_names)


def delete_bodies(list_of_names):
    for body in GetRootPart().GetAllBodies():
        if body.GetName() in list_of_names:
            selection = Selection.Create(body)
            Delete.Execute(selection)


def hide_bodies(list_of_names):
    for body in GetRootPart().GetAllBodies():
        if body.GetName() in list_of_names:
            selection = Selection.Create(body)
            visibility = VisibilityType.Hide
            inSelectedView = False
            faceLevel = False
            ViewHelper.SetObjectVisibility(selection, visibility, inSelectedView, faceLevel)


def suppress_bodies_for_physics(list_of_names):
    for body in GetRootPart().GetAllBodies():
        if body.GetName() in list_of_names:
            selection = Selection.Create(body)
            suppress = True
            ViewHelper.SetSuppressForPhysics(selection, suppress)


def move_sketch():
    x_translation = 0
    y_translation = 0
    z_translation = -55
    imported_component = GetRootPart().Components[-1]
    selection = Selection.Create(imported_component)
    direction = Move.GetDirection(selection)
    options = MoveOptions()
    Move.Translate(selection, direction, MM(z_translation), options, None)

    anchorPoint = Point.Create(MM(x_translation), MM(y_translation), MM(z_translation))
    axis = Line.Create(anchorPoint, Direction.DirZ)
    options = MoveOptions()
    Move.Rotate(selection, axis, DEG(-22.5), options, None)


def revolve_sketch():
    imported_component = GetRootPart().Components[-1]
    selection = Selection.Create(imported_component)

    data = CircularPatternData()
    global_coordinate_system = GetRootPart().CoordinateSystems[0]
    anchor = Selection.Create(global_coordinate_system)
    axis = Move.GetAxis(anchor, HandleAxis.Z)
    axis_Z = global_coordinate_system.Axes[2].Shape.Geometry.Direction
    axis = Selection.Create(global_coordinate_system.Axes[2])
    data.CircularAxis = axis
    data.RadialDirection = Direction.Create(0, 0, 0)
    data.CircularCount = 8
    data.CircularAngle = DEG(360)
    Pattern.CreateCircular(selection, data, None)


def extrude_sketch():
    rotor_length = 150
    stator_extra_length = 5
    coil_extra_length = 10
    component = GetRootPart().Components[-1]
    component = component.Components[0]  # we need only to modify one body as they are linked by the revolution

    # stator
    stator = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Stator")][0]
    move_body(stator, stator_extra_length)
    extrude_body(stator, -(rotor_length + 2 * stator_extra_length))

    # stator teeth
    stator_teeth = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Tooth")]
    for tooth in stator_teeth:
        move_body(tooth, stator_extra_length)
        extrude_body(tooth, -(rotor_length + 2 * stator_extra_length))

    # coils
    list_of_coils = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Coil")]
    for coil in list_of_coils:
        move_body(coil, coil_extra_length)
        extrude_body(coil, -(rotor_length + 2 * coil_extra_length))

    # PM, shaft & rotor
    list_of_pms = [body for body in component.GetAllBodies() if body.GetName().StartsWith("PM_")]
    for pm in list_of_pms:
        extrude_body(pm, -rotor_length)
    shaft = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Shaft")][0]
    extrude_body(shaft, -rotor_length)
    rotor = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Rotor")][0]
    extrude_body(rotor, -rotor_length)

    # Air Gap and Insulation
    list_of_insulations = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Insulation")]
    for insulation in list_of_insulations:
        extrude_body(insulation, -rotor_length)
    air_gap = [body for body in component.GetAllBodies() if body.GetName().StartsWith("Air_Gap")][0]
    extrude_body(air_gap, -rotor_length)


def extrude_faces(faces, value, body_name):
    for face in faces:
        selection = FaceSelection.Create(face)
        options = ExtrudeFaceOptions()
        options.ExtrudeType = ExtrudeType.Add
        result = ExtrudeFaces.Execute(selection, MM(value), options)
        rename_bodies(result.CreatedBodies, body_name)


def extrude_body(body, value):
    body_name = body.GetName()
    for face in body.Faces:
        selection = FaceSelection.Create(face)
        options = ExtrudeFaceOptions()
        options.ExtrudeType = ExtrudeType.ForceIndependent
        result = ExtrudeFaces.Execute(selection, MM(value), options)
        rename_bodies(result.CreatedBodies, body_name)


def move_body(body, value):
    selection = Selection.Create(body)
    direction = Move.GetDirection(selection)
    options = MoveOptions()
    Move.Translate(selection, direction, MM(value), options, None)


def rename_bodies(bodies, body_name):
    for body in bodies:
        body.SetName(body_name)


def get_bodies_by_names(body_names):
    bodies = []
    all_bodies = GetRootPart().GetAllBodies()
    for body in all_bodies:
        if body.GetName() in body_names:
            bodies.append(body)
    return bodies


def create_2d_named_selections():
    rename_bodies(GetRootPart().GetAllBodies("PM_I1_1"), "PM_I2")
    rename_bodies(GetRootPart().GetAllBodies("PM_O1_1"), "PM_O2")

    list_starting_names = [
        "Tooth",
        "Rotor",
        "Stator",
        "PM_",
        "PM_I1",
        "PM_I2",
        "PM_O1",
        "PM_O2",
        "Coil",
        "Shaft",
        "Insulation",
        "Air_Gap",
    ]
    create_named_selections("edge", list_starting_names)
    create_named_selections("face", list_starting_names)


def create_3d_named_selections():
    list_starting_names = [
        "Tooth",
        "Rotor",
        "Stator",
        "PM_",
        "PM_I1",
        "PM_I2",
        "PM_O1",
        "PM_O2",
        "Coil",
        "Shaft",
        "Insulation",
        "Air_Gap",
    ]
    create_named_selections("body", list_starting_names)

    # other selections:
    named_selection_name = "B_Windings"
    solid_endwindings = get_bodies_by_names("solid_endwindings")
    solid_endwindings_selection = Selection.Create(solid_endwindings)
    selection = Selection.CreateByObjects(
        [Selection.CreateByGroups(SelectionType.Primary, "B_Coil"), solid_endwindings_selection]
    )
    named_selection = NamedSelection.Create(selection, Selection())
    named_selection.CreatedNamedSelection.Name = named_selection_name

    named_selection_name = "B_All_Shaft"
    solid_shafts = get_bodies_by_names("solid_shaft")
    solid_shafts_selection = Selection.Create(solid_shafts)
    selection = Selection.CreateByObjects(
        [Selection.CreateByGroups(SelectionType.Primary, "B_Shaft"), solid_shafts_selection]
    )
    named_selection = NamedSelection.Create(selection, Selection())
    named_selection.CreatedNamedSelection.Name = named_selection_name

    named_selection_name = "B_Bearings"
    solid_bearings = get_bodies_by_names("solid_bearings")
    solid_bearings_selection = Selection.Create(solid_bearings)
    named_selection = NamedSelection.Create(solid_bearings_selection, Selection())
    named_selection.CreatedNamedSelection.Name = named_selection_name

    named_selection_name = "B_Housings"
    all_bodies = GetRootPart().GetAllBodies()
    solid_housings = list(all_bodies)[:3]
    solid_housings_selection = Selection.Create(solid_housings)
    named_selection = NamedSelection.Create(solid_housings_selection, Selection())
    named_selection.CreatedNamedSelection.Name = named_selection_name


def create_named_selections(selection_type, list_starting_names):
    for named_selection_name in list_starting_names:

        selection = []
        if named_selection_name.EndsWith("_"):
            named_selection_name = named_selection_name[:-1]

        bodies = [
            body
            for body in GetRootPart().GetAllBodies(named_selection_name)
            if body.GetName().StartsWith(named_selection_name)
        ]
        if selection_type == "body":
            selection = bodies
        elif selection_type == "face":
            for body in bodies:
                for face in body.Faces:
                    selection.append(face)
        elif selection_type == "edge":
            for body in bodies:
                for edge in body.Edges:
                    selection.append(edge)
        else:
            return None

        if len(selection) > 0:
            named_selection = NamedSelection.Create(Selection.Create(selection), Selection())
            prefix = selection_type[0].ToUpper()
            named_selection_name = prefix + "_" + named_selection_name
            named_selection.CreatedNamedSelection.Name = named_selection_name


def distance_to_point(iPoint, iGeometryShape):
    result_point = iGeometryShape.ProjectPoint(iPoint).Point
    return distance_between_vectors(result_point, iPoint)


def distance_between_vectors(vect1, vect2):
    distance_between_points = math.pow(vect1.X - vect2.X, 2)
    distance_between_points += math.pow(vect1.Y - vect2.Y, 2)
    distance_between_points += math.pow(vect1.Z - vect2.Z, 2)
    return math.sqrt(distance_between_points)


def split_geometry():
    """
    A. create solids for thermal conductivity
    B. split solids for thermal conductivity and split teeth from stator
    get all points of Stator face, sort it by radius in a dict
    then keep the third smallest radius where a circle is created
    which is used to split the Stator to get the teeth, detached from stator body
    :return: None
    """

    #### A. create solids for thermal conductivity

    # first create target_surface btw outer rotor and outer stator
    rotor = get_bodies_by_names("Rotor")[0]
    rotor_outer_edge = get_greater_radius_edge(rotor)

    stator = get_bodies_by_names("Stator")[0]
    stator_outer_edge = get_greater_radius_edge(stator)

    selection = EdgeSelection.Create(rotor_outer_edge)
    direction = MoveImprintEdges.GetImprintDirection(
        EdgeSelection.Create(rotor_outer_edge), FaceSelection.Create(rotor_outer_edge.Faces[0]), False
    )
    options = MoveImprintEdgeOptions()
    options.ExtrudeType = ExtrudeType.ForceIndependent
    options.Mode = MoveImprintEdgeMode.ExtrudeFull
    outer_value = stator_outer_edge.Shape.Geometry.Radius
    MoveImprintEdges.Execute(selection, direction, M(outer_value), options)
    nb_bodies = GetRootPart().Components[-1].GetAllBodies().Count
    target_surface = GetRootPart().Components[-1].GetAllBodies()[nb_bodies - 1]

    # create imprint on voids
    targets = BodySelection.Create(target_surface)
    bodies_collection = GetRootPart().GetAllBodies("Coil")
    bodies_collection.Add(stator)
    tools = BodySelection.Create(bodies_collection)
    options = MakeSolidsOptions()
    options.MakeAllRegions = True
    Combine.Intersect(targets, tools, options)

    rotor_outer_edge_geom = rotor_outer_edge.Shape.Geometry
    faces_to_delete = []
    for face in target_surface.Faces:
        found_face = False
        for edge in face.Edges:
            if edge.Shape.Geometry.IsCoincident(rotor_outer_edge_geom):
                found_face = True
                break
        if found_face == False:
            faces_to_delete.append(face)

    selection = FaceSelection.Create(faces_to_delete)
    result = Delete.Execute(selection)

    ### B. split teeth from stator
    points = []
    for edge in stator.Edges:
        for point in [edge.Shape.StartPoint] + [edge.Shape.EndPoint]:
            if point not in points:
                points.append(point)

    global_coordinate_system = GetRootPart().CoordinateSystems[0]
    origin = global_coordinate_system.Frame.Origin

    tolerance = 1e-6
    points_by_radius = {}
    for point in points:
        radius_exists = False
        curr_dist = distance_between_vectors(origin, point)

        for radius in points_by_radius.keys():
            if abs(radius - curr_dist) < tolerance:
                radius_exists = True
                curr_dist = radius
                break
        if radius_exists:
            points_by_radius[curr_dist] += [point]
        else:
            points_by_radius[curr_dist] = [point]

    all_radius = points_by_radius.keys()
    all_radius.sort()
    second_radius = all_radius[1]  # to split between air gap and isolation around coils
    third_radius = all_radius[2]  # to split teeth from stator

    # split between air gap and isolation around coils
    sectionPlane = Plane.PlaneXY
    ViewHelper.SetSketchPlane(sectionPlane, None)
    origin = Point2D.Origin
    created_circle = SketchCircle.Create(origin, M(second_radius)).CreatedCurves[0]

    target_face = target_surface.Faces[0]

    selection = Selection.Create(target_face, created_circle)
    target = Selection.Create(target_face)
    direction = Selection.Empty()
    ProjectToSolid.Execute(selection, target, direction)

    selection = Selection.Create(created_circle)
    Delete.Execute(selection)

    # detach
    face_to_detach = None
    for face in target_surface.Faces:
        for edge in face.Edges:
            if edge.Shape.Geometry.IsCoincident(rotor_outer_edge_geom):
                face_to_detach = face
                break
        if face_to_detach is not None:
            break

    selection = Selection.Create(face_to_detach)
    DetachFaces.Execute(selection)

    nb_new_components = GetRootPart().Components[-1].GetAllBodies().Count
    nb_coils = 7  # TODO: hardcoded
    last_bodies = GetRootPart().Components[-1].Content.Bodies[nb_new_components - nb_coils : nb_new_components]

    ind = 0
    for body in last_bodies:
        air_gap_found = False
        for edge in body.Edges:
            if edge.Shape.Geometry.IsCoincident(rotor_outer_edge_geom):
                air_gap_found = True
        if air_gap_found:
            body.SetName("Air_Gap")
        else:
            ind += 1
            body.SetName("Insulation_" + str(ind))

    # split teeth from stator
    sectionPlane = Plane.PlaneXY
    ViewHelper.SetSketchPlane(sectionPlane, None)
    origin = Point2D.Origin
    created_circle = SketchCircle.Create(origin, M(third_radius)).CreatedCurves[0]

    stator_face = stator.Faces[0]

    selection = Selection.Create(stator_face, created_circle)
    target = Selection.Create(stator_face)
    direction = Selection.Empty()
    ProjectToSolid.Execute(selection, target, direction)

    selection = Selection.Create(created_circle)
    Delete.Execute(selection)

    # detach teeth from stator body
    nb_components = GetRootPart().Components[-1].GetAllBodies().Count
    stator = get_bodies_by_names("Stator")[0]
    teeth_faces = stator.Faces[1:]
    selection = Selection.Create(teeth_faces)
    DetachFaces.Execute(selection)
    nb_new_components = GetRootPart().Components[-1].GetAllBodies().Count
    bodies = GetRootPart().Components[-1].GetAllBodies()
    teeth_bodies = bodies.GetRange(nb_components, nb_new_components - nb_components)
    for index, tooth in enumerate(teeth_bodies):
        tooth.SetName("Tooth_" + str(index + 1))


def merge_bodies():
    """
    merge teeth split in 2 by construction (in symmetry plane)
    :return: None
    """
    teeth_bodies = [body for body in GetRootPart().GetAllBodies("Tooth") if body.GetName().StartsWith("Tooth")]
    selection = Selection.Create(teeth_bodies)
    ComponentHelper.MoveBodiesToComponent(selection, None)

    GetRootPart().Components[-1].SetName("Teeth")

    teeth = GetRootPart().Components[-1]
    max_tooth_nb = len(teeth.GetBodies()) / 8
    teeth_to_merge = []
    for body in teeth.GetBodies():
        if body.GetName() == "Tooth_1" or body.GetName() == "Tooth_" + str(max_tooth_nb):
            teeth_to_merge += [body]

    nb_ = 0
    tolerance = 1e-6
    teeth_merged = []
    for tooth_1 in teeth_to_merge:
        if tooth_1 in teeth_merged:
            continue
        for tooth_2 in teeth_to_merge:
            if tooth_2 in teeth_merged:
                continue
            if tooth_1 != tooth_2:
                if tooth_1.Shape.GetClosestSeparation(tooth_2.Shape).Distance < tolerance:
                    teeth_merged.append(tooth_1)
                    teeth_merged.append(tooth_2)

    for ind_couple in range(len(teeth_merged) / 2):
        ind = ind_couple * 2
        couple = teeth_merged[ind : ind + 2]
        targets = Selection.Create(couple)
        if targets.Count > 1:
            Combine.Merge(targets, None)


def get_greater_radius_edge(body):
    external_edge = None
    greater_radius = -1
    for edge in body.Edges:
        current_geometry = edge.Shape.Geometry
        if current_geometry.GetType() == Circle:
            radius = current_geometry.Radius
            if radius > greater_radius:
                greater_radius = radius
                external_edge = edge

    return external_edge


def get_uri_file(file_name):
    with open(file_name, "rb") as f:
        tmp = f.read()
    uri = "data:application/octet-stream;base64," + base64.b64encode(tmp).decode("utf-8")
    return uri


# TODO: modify that when pyDisco changes this way to work

# params = {}
# params["dci"] =  2*67.5
# params["dso"] = 2*99
# params["sat_file_path"] = r"C:\Users\rlejeune\OneDrive - ANSYS, Inc\Documents\01_WORK\03_PLATFORM\06_WebAppPoC\01_USE_CASE\LEAF\SCDM_Projs\my_geom.sat"
# params["scdoc_file_path"] = "./assets/Leaf360_for_script.scdoc"

# Spaceclaim convention:
# inputs/output are of base type and must be serializable
# inputs values must be of type string
# inputs sent from run_script_file are stored in argsDict
# output is defined in global "result" variable and returned automatically

# =================================================== [Execution] =================================================== #

result = generate_3d_cad(argsDict)

logging.info("Finished!")
