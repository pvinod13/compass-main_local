from ansys.discovery.core.discovery import Discovery


def prepare_inputs_for_geom(sat_file_path, template_file):
    inputs_for_simu = {}

    # TODO: if limitation about args being only str is no more, change that
    inputs_for_simu["dci"] = str(135)
    inputs_for_simu["dso"] = str(198)
    inputs_for_simu["sat_file_path"] = sat_file_path
    inputs_for_simu["scdoc_file_path"] = template_file

    return inputs_for_simu


def generate_cad(geom_params, cad_script):
    try:
        pid = -1
        client = Discovery()
        pid, port = client.session.start(space_claim=True, headless=True)
        client.documents.open(geom_params["scdoc_file_path"])
        result = client.application.run_script_file(cad_script, geom_params)
        client.session.stop(pid)
        return result

    except Exception as e:

        result = "Error: Exception raised. "
        result += getattr(e, "details", repr(e))

        if client is not None and pid != -1:
            client.session.stop(pid)

        return result
