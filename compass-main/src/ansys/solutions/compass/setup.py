# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.
import web_app_poc_saf.solution.definition as solution_definition

from setuptools import setup

from ansys.saf2.api.solution import SolutionSingleton

SolutionSingleton.configure(solution_definition)

setup(
    name="web_app_poc_saf",
    version="0.0.1",
    description=f"{SolutionSingleton.display_name} Ansys SAF solution",
    packages=[
        "web_app_poc_saf",
        "web_app_poc_saf/ui",
        "web_app_poc_saf/solution",
    ],
    package_dir={"": "."},
    package_data={"web_app_poc_saf/ui": ["assets/*/*.*", "assets/*.*"]},
    entry_points={"console_scripts": ["web_app_poc_saf_main=web_app_poc_saf.main:main"]},
    install_requires=["dash"],
    python_requires=">=3.7, <3.9",
)
