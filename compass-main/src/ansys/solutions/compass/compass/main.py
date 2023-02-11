# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

from ansys.saf2.runtime import saf_main
from ansys.solutions.compass.compass.solution import definition
from ansys.solutions.compass.compass.ui import app


def main():
    saf_main("compass", definition, app)


if __name__ == "__main__":
    main()
