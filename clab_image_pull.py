"""
Plugin netlab :
- Force image-pull-policy: if-not-present sur les nœuds routeros7
- Injecte deux erreurs OSPF pédagogiques pour l'examen :
    * Mikrotik2 : area OSPF 0.0.0.1 au lieu de 0.0.0.0
    * Mikrotik3 : router-id 10.0.0.1 (doublon avec Mikrotik1)
"""

from box import Box


def post_transform(topology: Box) -> None:
    for name, node in topology.nodes.items():
        if node.get('device') != 'routeros7':
            continue

        # Force le pull de l'image si absente
        if 'clab' not in node:
            node['clab'] = {}
        node['clab']['image-pull-policy'] = 'if-not-present'

        # Erreur 1 : mauvaise area OSPF sur Mikrotik2
        if name == 'Mikrotik2':
            for intf in node.get('interfaces', []):
                if 'ospf' in intf:
                    intf['ospf']['area'] = '0.0.0.1'
            if 'ospf' in node:
                node['ospf']['area'] = '0.0.0.1'

        # Erreur 2 : router-id dupliqué sur Mikrotik3
        if name == 'Mikrotik3':
            node['router_id'] = '10.0.0.1'
