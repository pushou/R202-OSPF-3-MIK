"""
Validation plugin for MikroTik RouterOS 7 devices.
Provides OSPF route count checks based on '/ip/route/print' output.
"""

import re
import typing

from netsim.data import global_vars


def exec_ospf_route_count(expected_count: int) -> str:
    """Return the RouterOS command to display the IP routing table."""
    return "/ip/route/print"


def valid_ospf_route_count(expected_count: int) -> str:
    """
    Validate the number of OSPF routes on a MikroTik RouterOS 7 device.

    Parses the output of '/ip/route/print' and counts lines whose flag
    column contains 'o' (OSPF), e.g. 'DAo'.

    Parameters
    ----------
    expected_count : int
        Number of OSPF routes expected on this router.
    """
    _result = global_vars.get_result_dict('_result')
    raw = _result.stdout if hasattr(_result, 'stdout') else str(_result)

    if not raw.strip():
        raise Exception("Empty output from /ip/route/print")

    # Lines with OSPF flag start with optional whitespace, then flag chars
    # that include lowercase 'o', followed by whitespace and an IP address.
    ospf_lines = [
        line for line in raw.splitlines()
        if re.match(r'^\s*[A-Za-z]*o[A-Za-z]*\s+\d', line)
    ]

    count = len(ospf_lines)
    if count != expected_count:
        raise Exception(
            f"Expected {expected_count} OSPF routes, found {count}.\n"
            "OSPF routes detected:\n" + "\n".join(ospf_lines)
        )

    return f"Found exactly {expected_count} OSPF routes as expected"
