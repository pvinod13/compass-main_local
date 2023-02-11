# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""
"""

# ==================================================== [Imports] ==================================================== #

import os

from datetime import date

# =================================================== [Functions] =================================================== #


def find_elements(lst1, lst2):
    """Finds the elements in list lst1 with indexes in lst2"""
    return [lst1[i] for i in lst2]


def find_n_largest(input_len_list, n_largest_edges):
    """Finds the n_largest_edges largest elements in list input_len_list"""
    tmp = list(input_len_list)
    copied = list(input_len_list)
    copied.sort()  # sort list so that largest elements are on the far right
    index_list = []
    for n in range(1, n_largest_edges + 1):  # get index of the Nth largest element
        index_list.append(tmp.index(copied[-n]))
        tmp[tmp.index(copied[-n])] = 0  # index can only get the first occurrence, that solves the problem
    return index_list


def get_file_by_extension(file_directory, extension):
    """Get file by extension"""
    found_files = []
    for file in os.listdir(file_directory):
        filename, file_extension = os.path.splitext(file)
        if file_extension == extension:
            found_files.append(file)

    return found_files


def get_date():
    """Gets today's date.

    Returns:
        str: date
    """
    today = date.today()
    return today.strftime("%d/%m/%Y")
