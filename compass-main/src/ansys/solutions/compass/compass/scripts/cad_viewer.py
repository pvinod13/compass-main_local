def render_3d_cad_viewer():
    javascript_callback = """
        function (uri_file, div_id) {
            debugger;
            if (uri_file == null) {
                throw window.dash_clientside.PreventUpdate;
            }
            set3DView(uri_file, div_id);
            return 'Client says ';
        }
        """
    return javascript_callback
