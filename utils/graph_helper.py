"""
Helper functions to handle graphs
"""
from collections import defaultdict


def convert_list_to_defaultdict(temp_list: list) -> defaultdict:
    """_summary_

    Returns:
        defaultdict: _description_
    """

    d = defaultdict(list)

    for k, v in temp_list:
        d[k].append(v)

    return d
