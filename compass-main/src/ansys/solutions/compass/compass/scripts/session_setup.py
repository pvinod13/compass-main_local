# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

# ==================================================== [Imports] ==================================================== #

import os

from typing import Dict

# =================================================== [Functions] =================================================== #


def get_product_version_numbers() -> Dict[str, str]:
    """Get list of Ansys flagship products available on the machine."""

    products = {"AEDT": [], "Workbench": []}

    for envvar in os.environ:
        if envvar.startswith("ANSYS"):
            pieces = envvar.split("_")
            product = ""
            version = ""

            if len(pieces) == 2:
                if pieces[0] == "ANSYSEM":
                    version = pieces[1].replace("ROOT", "")
                    product = "AEDT"
                elif pieces[1] == "DIR":
                    version = pieces[0].replace("ANSYS", "")
                    if version and version.isdigit():
                        product = "Workbench"

            if product:
                version = "20" + version[:-1] + "." + version[-1]
                products[product].append(version)

    products["AEDT"].sort(reverse=True)
    products["Workbench"].sort(reverse=True)

    return products
