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


def exec_check_comp(expected_count: int, expected_distance: int) -> str:
    """Return the RouterOS command to display the IP routing table."""
    return "/ip/route/print"


def valid_check_comp(expected_count: int, expected_distance: int) -> str:
    """
    Vérifie le nombre total de routes actives ET la distance administrative
    des routes OSPF sur un routeur MikroTik RouterOS 7.

    Parameters
    ----------
    expected_count : int
        Nombre total de routes actives attendues dans la table.
    expected_distance : int
        Distance administrative attendue pour les routes OSPF (110 pour OSPF).
    """
    _result = global_vars.get_result_dict('_result')
    raw = _result.stdout if hasattr(_result, 'stdout') else str(_result)

    if not raw.strip():
        raise Exception("Empty output from /ip/route/print")

    lines = raw.splitlines()

    # Lignes de routes actives (commencent par des flags dont 'A')
    active_lines = [l for l in lines if re.match(r'^\s*[A-Za-z]*A[A-Za-z]*\s+\d', l)]
    total = len(active_lines)

    # Lignes OSPF
    ospf_lines = [l for l in lines if re.match(r'^\s*[A-Za-z]*o[A-Za-z]*\s+\d', l)]

    errors = []

    if total != expected_count:
        errors.append(f"Nombre de routes actives : attendu {expected_count}, trouvé {total}")

    # Vérifier la distance des routes OSPF
    bad_dist = []
    for line in ospf_lines:
        m = re.search(r'(\d+)\s*$', line.strip())
        if m:
            dist = int(m.group(1))
            if dist != expected_distance:
                bad_dist.append(f"  {line.strip()} → distance {dist}")
    if bad_dist:
        errors.append(
            f"Routes OSPF avec distance ≠ {expected_distance} :\n" + "\n".join(bad_dist)
        )

    if errors:
        raise Exception("\n".join(errors))

    return (f"OK : {total} routes actives, "
            f"{len(ospf_lines)} routes OSPF avec distance {expected_distance}")


def exec_ospf_area(expected_area: str) -> str:
    """Retourne la commande RouterOS pour afficher les aires OSPF."""
    return "/routing/ospf/area/print"


def valid_ospf_area(expected_area: str) -> str:
    """
    Vérifie qu'une aire OSPF avec l'area-id attendu est bien configurée.

    Parameters
    ----------
    expected_area : str
        area-id attendu, ex. '0.0.0.0'
    """
    _result = global_vars.get_result_dict('_result')
    raw = _result.stdout if hasattr(_result, 'stdout') else str(_result)

    if not raw.strip():
        raise Exception("Empty output from /routing/ospf/area/print")

    if expected_area not in raw:
        raise Exception(
            f"Aire OSPF {expected_area} introuvable.\n"
            f"Sortie :\n{raw.strip()}"
        )

    return f"Aire OSPF {expected_area} présente"


def exec_ospf_rid(expected_rid: str) -> str:
    """Retourne la commande RouterOS pour afficher les instances OSPF."""
    return "/routing/ospf/instance/print"


def valid_ospf_rid(expected_rid: str) -> str:
    """
    Vérifie que le router-id OSPF configuré correspond à la valeur attendue.

    Parameters
    ----------
    expected_rid : str
        Router-id attendu, ex. '10.0.0.1'
    """
    _result = global_vars.get_result_dict('_result')
    raw = _result.stdout if hasattr(_result, 'stdout') else str(_result)

    if not raw.strip():
        raise Exception("Empty output from /routing/ospf/instance/print")

    # Cherche le router-id dans la ligne de l'instance active
    m = re.search(r'router-id\s*=?\s*([\d.]+)', raw, re.IGNORECASE)
    if not m:
        # Format tabulaire : le router-id est la 3e colonne après le numéro
        m = re.search(r'^\s*\d+\s+\*?\s*\S+\s+([\d.]+)', raw, re.MULTILINE)
    if not m:
        raise Exception(f"Router-id introuvable dans la sortie :\n{raw.strip()}")

    actual_rid = m.group(1)
    if actual_rid != expected_rid:
        raise Exception(
            f"Router-id incorrect : attendu {expected_rid}, trouvé {actual_rid}"
        )

    return f"Router-id OSPF correct : {actual_rid}"
