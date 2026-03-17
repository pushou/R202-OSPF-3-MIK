"""
FRR Validation Plugin for netlab
Validates RIP and other FRR configurations
"""

import typing
from box import Box


def show_rip_routes() -> str:
    """Return the show command to get RIP routes in JSON format"""
    return "ip route json"


def valid_rip_routes(**kwargs) -> typing.Union[bool, str]:
    """
    Validate that RIP routes are present in the output
    Checks for at least one route with protocol='rip'
    """
    global _result
    
    # _result contains the parsed JSON directly (not wrapped in .default)
    data = _result
    
    if not isinstance(data, dict):
        raise Exception("Invalid route data format - expected dictionary")
    
    # Look for RIP routes
    rip_routes = []
    for prefix, routes_list in data.items():
        if isinstance(routes_list, list):
            for route in routes_list:
                # Handle both dict and Box objects
                try:
                    protocol = route.get('protocol') if hasattr(route, 'get') else route['protocol']
                    if protocol == 'rip':
                        rip_routes.append({
                            'prefix': prefix,
                            'metric': route.get('metric') if hasattr(route, 'get') else route['metric'],
                            'distance': route.get('distance') if hasattr(route, 'get') else route['distance']
                        })
                except (KeyError, TypeError, AttributeError):
                    continue
    
    if not rip_routes:
        raise Exception("No RIP routes found in routing table")
    
    # Verify all RIP routes have correct distance (120 for RIPv2)
    for route in rip_routes:
        if route['distance'] != 120:
            raise Exception(
                f"RIP route {route['prefix']} has incorrect distance: "
                f"{route['distance']} (expected 120)"
            )
    
    return f"Found {len(rip_routes)} RIP routes with correct distance (120)"


def valid_rip_route_count(expected_count: int, **kwargs) -> typing.Union[bool, str]:
    """
    Validate a specific number of RIP routes
    """
    global _result
    
    data = _result
    if not isinstance(data, dict):
        raise Exception("Invalid route data format")
    
    rip_routes = []
    for prefix, routes_list in data.items():
        if isinstance(routes_list, list):
            for route in routes_list:
                try:
                    protocol = route.get('protocol') if hasattr(route, 'get') else route['protocol']
                    if protocol == 'rip':
                        rip_routes.append(prefix)
                except (KeyError, TypeError, AttributeError):
                    continue
    
    if len(rip_routes) != expected_count:
        raise Exception(
            f"Expected {expected_count} RIP routes, found {len(rip_routes)}: "
            f"{rip_routes}"
        )
    
    return f"Found exactly {expected_count} RIP routes as expected"


def valid_rip_prefix(prefix: str, **kwargs) -> typing.Union[bool, str]:
    """
    Validate that a specific prefix is learned via RIP
    """
    global _result
    
    data = _result
    if not isinstance(data, dict):
        raise Exception("Invalid route data format")
    
    if prefix not in data:
        raise Exception(f"Prefix {prefix} not found in routing table")
    
    routes = data[prefix]
    if not isinstance(routes, list):
        raise Exception(f"Invalid route format for {prefix}")
    
    rip_route = None
    for route in routes:
        try:
            protocol = route.get('protocol') if hasattr(route, 'get') else route['protocol']
            if protocol == 'rip':
                rip_route = route
                break
        except (KeyError, TypeError, AttributeError):
            continue
    
    if not rip_route:
        raise Exception(f"Prefix {prefix} is not learned via RIP")
    
    metric = rip_route.get('metric') if hasattr(rip_route, 'get') else rip_route['metric']
    return f"Prefix {prefix} is learned via RIP (metric: {metric})"


def show_ospf_route_count() -> str:
    """Return the command to get the IP route table on RouterOS (MikroTik)"""
    return "/ip/route/print"


def valid_ospf_route_count(expected_count: int, **kwargs) -> typing.Union[bool, str]:
    """
    Validate the number of OSPF routes on a MikroTik RouterOS device.

    Parses the output of '/ip/route/print' and counts lines containing the
    OSPF flag ('o'). In MikroTik output, OSPF routes are flagged with 'o'
    (e.g. 'DAo').

    Parameters
    ----------
    expected_count : int
        Number of OSPF routes expected on this router.
    """
    global _result

    # _result may be a Box or a plain string
    if hasattr(_result, 'default'):
        raw = str(_result.default)
    else:
        raw = str(_result)

    if not raw.strip():
        raise Exception("Empty output from /ip/route/print")

    # Count lines that carry an OSPF route flag (contain lowercase 'o' in the
    # flags column, i.e. the line starts with optional whitespace then flag
    # characters that include 'o' followed by at least one space and an IP
    # prefix).
    import re
    ospf_lines = [
        line for line in raw.splitlines()
        if re.match(r'^\s*[A-Za-z]*o[A-Za-z]*\s+\d', line)
    ]

    count = len(ospf_lines)
    if count != expected_count:
        raise Exception(
            f"Expected {expected_count} OSPF routes, found {count}.\n"
            f"OSPF routes detected:\n" + "\n".join(ospf_lines)
        )

    return f"Found exactly {expected_count} OSPF routes as expected"


def show_rip_neighbor(neighbor_id: str) -> str:
    """Return command to check for specific RIP neighbor"""
    return "ip rip neighbor json"


def valid_rip_neighbor(neighbor_id: str, **kwargs) -> typing.Union[bool, str]:
    """
    Validate presence of RIP neighbor
    """
    global _result
    
    data = _result
    if not isinstance(data, dict):
        raise Exception("Invalid RIP neighbor data format")
    
    if neighbor_id not in data:
        raise Exception(f"RIP neighbor {neighbor_id} not found")
    
    return f"RIP neighbor {neighbor_id} is active"
