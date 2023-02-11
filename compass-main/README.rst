#######
COMPASS 🧭
#######
|python| |GH-CI| |black| |pre-commit|

Introduction
============

Information needed.

  * Project name: **compass**
  * Package name: **ansys-solutions-compass**

Installation
============

Prerequisites
-------------

Python version support
~~~~~~~~~~~~~~~~~~~~~~

Officially Python 3.7.1 and 3.8.

Ansys Flagship products
~~~~~~~~~~~~~~~~~~~~~~~

This solution application requires the following Ansys products to be installed. The table below
lists the products and the authorized versions.

.. list-table:: Flagship product required
  :widths: 25 25
  :header-rows: 1

  * - Product
    - Versions

  * - AEDT
    - from R22.1 to latest

  * - WorkBench
    - R23.1

Private PyPI server
~~~~~~~~~~~~~~~~~~~

Access to the PyAnsys private PyPI server and to the Solutions feed within the same server is required. To enable the connection, 
the following personal access tokens (PATs) need to be declared as system environment variables: 

  * PYANSYS_PRIVATE_PYPI_PAT
  * SOLUTIONS_PRIVATE_PYPI_PAT

To create those variables, run the batch script set_PRIVATE_PYPI_PAT_to_env.bat and follow the steps.

Processing time
~~~~~~~~~~~~~~~

The installation process can take a while. About 15 minutes depending on your internet connection.

Starting the solution
---------------------

1. Clone the repository:

  .. code:: bash

    git clone https://github.com/Solution-Applications/compass.git

2. Navigate to the cloned project directory:

  .. code:: bash

    cd compass

3. Run the bat file:

  .. code:: bash

    start_app.bat

.. note::

  * The first time you start the application, the process can take a while as the Python ecosystem required by the solution needs to be setup. 

Testing
=======

Two approaches for testing can be considered: 

  * with tox
  * raw testing

Using tox
---------

This project takes advantage of `tox`_. This tool allows to automate common development tasks (similar to Makefile) but
it is oriented towards Python development. 

As Makefile has rules, `tox`_ has environments. In fact, the tool creates its own virtual environment so anything being
tested is isolated from the project in order to guarantee project's integrity. The following environments commands are
provided:

- **tox -e style**: will check for coding style quality.
- **tox -e py**: checks for unit tests.
- **tox -e py-coverage**: checks for unit testing and code coverage.
- **tox -e doc**: checks for documentation building process.
- **tox -e build**: checks source code build.

Raw testing
-----------

If required, you can always call the style commands (`black`_, `isort`_, `flake8`_...) or unit testing ones (pytest)
from the command line. However, this does not guarantee that your project is being tested in an isolated environment,
which is the reason why tools like `tox`_ exist.

Run the following command:

  .. code:: bash

    pytest -p no:faulthandler --cov=ansys.solutions --cov-report=term --cov-report=xml --cov-report=html -vvv

Code style check
================

The style checks take advantage of pre-commit. Developers are not forced but encouraged to install this tool via:

  .. code:: bash

    python -m pip install pre-commit
        
  .. code:: bash
        
    pre-commit install

Documentation
=============

With tox
---------

Run the following command:

  .. code:: bash

    tox -e doc

Without tox
-----------

Run the following command:

  .. code:: bash

    sphinx-build doc/source doc/build/html --color -vW -bhtml

Build
=====

With tox
---------

Run the following command:

  .. code:: bash

    tox -e build

Without tox
-----------

Using the build module
~~~~~~~~~~~~~~~~~~~~~~

Build the package:

  .. code:: bash

    python -m build

Using poetry
~~~~~~~~~~~~

Build the package:

  .. code:: bash

    poetry build

License 
========

Information needed.


.. BADGES
.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.7-blue
   :target: https://www.python.org/
   :alt: Python
.. |GH-CI| image:: https://github.com/Solution-Applications/compass/actions/workflows/python-package.yml/badge.svg
   :target: https://github.com/Solution-Applications/compass/actions/workflows/python-package.yml
   :alt: GH-CI
.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit

.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
