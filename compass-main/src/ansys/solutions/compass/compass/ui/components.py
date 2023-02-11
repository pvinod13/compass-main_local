# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

import dash_bootstrap_components as dbc

from dash import html, dcc


class Row:
    def __init__(
        self,
        row_input_type,
        row_id,
        row_label_name,
        row_unit="",
        row_default_value=None,
        row_list=[],
        min_value=None,
        max_value=None,
        increment="any",
        disabled=False,
    ):

        if row_input_type == "number":
            input_row = dbc.Row(
                [
                    dbc.Col(html.Label(row_label_name), width=6),
                    dbc.Col(self.number_field(row_id, row_default_value, min_value, max_value, increment), width=4),
                    dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                ]
            )
        elif row_input_type == "number_list":
            nb_items = len(row_list)
            if nb_items == 0 or nb_items > 4:
                print("number of values not supported in Row: " + str(nb_items))
                return None
            if nb_items == 1:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=6),
                        dbc.Col(
                            self.number_field(row_id + "_1", row_list[0], min_value, max_value, increment),
                            width=4,
                        ),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                    ]
                )
            elif nb_items == 2:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=6),
                        dbc.Col(
                            self.number_field(row_id + "_1", row_list[0], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(
                            self.number_field(row_id + "_2", row_list[1], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                    ]
                )
            elif nb_items == 3:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=5),
                        dbc.Col(
                            self.number_field(row_id + "_1", row_list[0], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(
                            self.number_field(row_id + "_2", row_list[1], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(
                            self.number_field(row_id + "_3", row_list[2], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=1),
                    ]
                )
            elif nb_items == 4:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=3),
                        dbc.Col(
                            self.number_field(row_id + "_1", row_list[0], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(
                            self.number_field(row_id + "_2", row_list[1], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(
                            self.number_field(row_id + "_3", row_list[2], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(
                            self.number_field(row_id + "_4", row_list[3], min_value, max_value, increment),
                            width=2,
                        ),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                    ]
                )

        elif row_input_type == "label_list":
            nb_items = len(row_list)
            if nb_items == 0 or nb_items > 4:
                print("number of labels not supported in Row: " + str(nb_items))
                return None
            if nb_items == 1:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=6),
                        dbc.Col(html.Label(row_list[0], style={"textAlign": "center"}), width=4),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                    ]
                )
            elif nb_items == 2:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=6),
                        dbc.Col(html.Label(row_list[0], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_list[1], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                    ]
                )
            elif nb_items == 3:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=5),
                        dbc.Col(html.Label(row_list[0], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_list[1], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_list[2], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=1),
                    ]
                )
            elif nb_items == 4:
                input_row = dbc.Row(
                    [
                        dbc.Col(html.Label(row_label_name), width=3),
                        dbc.Col(html.Label(row_list[0], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_list[1], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_list[2], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_list[3], style={"textAlign": "center"}), width=2),
                        dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=1),
                    ]
                )
        elif row_input_type == "dropdown":
            input_row = dbc.Row(
                [
                    dbc.Col(html.Label(row_label_name, style={"verticalAlign": "middle"}), width=6),
                    dbc.Col(
                        dcc.Dropdown(
                            row_list,
                            row_default_value,
                            id=row_id,
                            style={"textAlign": "left", "width": "-webkit-fill-available"},
                        ),
                        width=4,
                    ),
                    dbc.Col(html.Label(row_unit, style={"textAlign": "left"}), width=2),
                ]
            )
        elif row_input_type == "button":
            input_row = dbc.Row(
                [
                    dbc.Col(html.Label("", style={"verticalAlign": "middle"}), width=6),
                    dbc.Col(
                        dbc.Button(
                            row_label_name,
                            id=row_id,
                            disabled=disabled,
                            color="secondary",
                            style={"width": "-webkit-fill-available"},
                        ),
                        width=4,
                    ),
                    dbc.Col(html.Label("", style={"textAlign": "left"}), width=2),
                ]
            )
        else:
            input_row = dbc.Row([])

        self.input_row = input_row

    def get(self):
        return self.input_row

    def number_field(self, row_id, row_default_value, min_value, max_value, increment):
        return None


class InputRow(Row):
    def __init__(
        self,
        row_input_type,
        row_id,
        row_label_name,
        row_unit="",
        row_default_value=None,
        row_list=[],
        min_value=None,
        max_value=None,
        increment="any",
        disabled=False,
    ):
        Row.__init__(
            self,
            row_input_type,
            row_id,
            row_label_name,
            row_unit,
            row_default_value,
            row_list,
            min_value,
            max_value,
            increment,
            disabled,
        )

    def number_field(self, row_id, row_default_value, min_value, max_value, increment):
        return dcc.Input(
            id=row_id,
            type="number",
            value=row_default_value,
            min=min_value,
            max=max_value,
            step=increment,
            style={"textAlign": "right", "width": "-webkit-fill-available"},
        )


class OutputRow(Row):
    def __init__(
        self,
        row_input_type,
        row_id,
        row_label_name,
        row_unit="",
        row_default_value=None,
        row_list=[],
        min_value=None,
        max_value=None,
        increment="any",
        disabled=False,
    ):
        Row.__init__(
            self,
            row_input_type,
            row_id,
            row_label_name,
            row_unit,
            row_default_value,
            row_list,
            min_value,
            max_value,
            increment,
            disabled,
        )

    def number_field(self, row_id, row_default_value, min_value, max_value, increment):
        return dcc.Input(
            id=row_id,
            type="number",
            value=row_default_value,
            readOnly=True,
            style={"textAlign": "right", "width": "-webkit-fill-available", "color": "gray"},
        )


class AnsysHeader:
    def __init__(self):

        pyansys_logo = "assets/images/pyansys-logo-black-cropped.png"

        # make a reuseable navitem for the different examples
        nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

        # make a reuseable dropdown for the different examples
        dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
            nav=True,
            in_navbar=True,
            label="Menu",
        )

        ansys_header = dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=pyansys_logo, height="30px")),
                                dbc.Col(dbc.NavbarBrand("         ", className="ms-2")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        href="https://docs.pyansys.com/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.Row(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        # dbc.NavItem(dbc.NavLink("Home")),
                                        # dbc.NavItem(dbc.NavLink("Page 1")),
                                        dbc.NavItem(
                                            dbc.NavLink("Permanent Magnet Electric Motor"),
                                            # add an auto margin after page 2 to
                                            # push later links to end of nav
                                            className="me-auto",
                                        ),
                                        dbc.NavItem(dbc.NavLink("Help")),
                                        dbc.NavItem(dbc.NavLink("About")),
                                    ],
                                    # make sure nav takes up the full width for auto
                                    # margin to get applied
                                    className="w-100",
                                ),
                                id="navbar-collapse",
                                is_open=False,
                                navbar=True,
                            ),
                        ],
                        # the row should expand to fill the available horizontal space
                        className="flex-grow-1",
                    ),
                ],
                fluid=True,
            ),
            dark=True,
            color="black",
        )

        self.ansys_header = ansys_header

    def get(self):
        return self.ansys_header
