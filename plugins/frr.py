"""
FRR validation plugin for netlab
Validates RIP and other FRR configurations
"""

def show_rip_routes() -> str:
    """Return the show command to get RIP routes in JSON format"""
    return "ip route json"


def valid_rip_routes() -> bool:
    """
    Validate that RIP routes are present in the output
    Checks for at least one route with protocol='rip'
    """
    global _result
    
    # Check if data is a dictionary with routes
    if not isinstance(_result.default, dict):
        raise Exception("Invalid route data format")
    
    # Look for at least one RIP route
    rip_routes = []
    for prefix, routes_list in _result.default.items():
        if isinstance(routes_list, list):
            for route in routes_list:
                if isinstance(route, dict) and route.get('protocol') == 'rip':
                    rip_routes.append({
                        'prefix': prefix,
                        'metric': route.get('metric'),
                        'distance': route.get('distance')
                    })
    
    if not rip_routes:
        raise Exception("No RIP routes found in routing table")
    
    # Verify RIP routes have correct distance (120 for RIPv2)
    for route in rip_routes:
        if route['distance'] != 120:
            raise Exception(
                f"RIP route {route['prefix']} has incorrect distance: "
                f"{route['distance']} (expected 120)"
            )
    
    print(f"✓ Found {len(rip_routes)} RIP routes with correct distance")
    return True


def valid_rip_route_count(expected_count: int) -> bool:
    """
    Validate a specific number of RIP routes
    """
    global _result
    
    if not isinstance(_result.default, dict):
        raise Exception("Invalid route data format")
    
    rip_routes = []
    for prefix, routes_list in _result.default.items():
        if isinstance(routes_list, list):
            for route in routes_list:
                if isinstance(route, dict) and route.get('protocol') == 'rip':
                    rip_routes.append(prefix)
    
    if len(rip_routes) != expected_count:
        raise Exception(
            f"Expected {expected_count} RIP routes, found {len(rip_routes)}: "
            f"{rip_routes}"
        )
    
    print(f"✓ Found exactly {expected_count} RIP routes as expected")
    return True


def valid_rip_prefix(prefix: str) -> bool:
    """
    Validate that a specific prefix is learned via RIP
    """
    global _result
    
    if not isinstance(_result.default, dict):
        raise Exception("Invalid route data format")
    
    if prefix not in _result.default:
        raise Exception(f"Prefix {prefix} not found in routing table")
    
    routes = _result.default[prefix]
    if not isinstance(routes, list):
        raise Exception(f"Invalid route format for {prefix}")
    
    rip_route = None
    for route in routes:
        if isinstance(route, dict) and route.get('protocol') == 'rip':
            rip_route = route
            break
    
    if not rip_route:
        raise Exception(f"Prefix {prefix} is not learned via RIP")
    
    print(f"✓ Prefix {prefix} is learned via RIP (metric: {rip_route.get('metric')})")
    return True
