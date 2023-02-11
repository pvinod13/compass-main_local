# Copyright (c) 2022, Ansys Inc. Unauthorised use, distribution or duplication is prohibited


# from dash._callback_context import context_value
# from dash._utils import AttributeDict
# import pytest
# import report_ids as ids
# from report import add_custom_section


# @pytest.mark.parametrize(
#     "n_clicks, state_container, expected_count",
#     [(0, [], 0), (1, [], 3), (2, ["DummyState", "DummyState", "DummyState"], 6)],
# )
# def test_add_custom_section(n_clicks, state_container, expected_count):
#     context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": f"{ids.ADD_SECTION_BUTTON}.n_clicks"}]}))
#     context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": f"{ids.CONTAINER_CUSTOM_SECTION}.children"}]}))
#     output = add_custom_section(n_clicks, state_container)
#     assert len(output) == expected_count
