# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import os
import tempfile
import dash_bootstrap_components as dbc
import dash_uploader as du

from dash_extensions.enrich import DashProxy, NoOutputTransform, TriggerTransform, MultiplexerTransform


app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    transforms=[NoOutputTransform(), TriggerTransform(), MultiplexerTransform()],
)

# If folder doesn't exist, it will be created later
UPLOAD_DIRECTORY = os.path.join(tempfile.gettempdir(), "SAF2")
du.configure_upload(app, UPLOAD_DIRECTORY)

# !IMPORTANT Keeping the import line here to adapt with dash_uploader config, moving the import above will fail the
# dash uploader configuration
from ansys.solutions.compass.compass.ui.page import layout

app.layout = layout
