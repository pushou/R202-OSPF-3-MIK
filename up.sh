#!/bin/bash
# Upgrade containerlab, pré-pull les images absentes, lance netlab up
# puis injecte les erreurs OSPF pédagogiques directement sur les routeurs

echo "[UPGRADE] containerlab"
CLAB_VERSION=$(containerlab version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
REQUIRED="0.74.2"
if [ -z "$CLAB_VERSION" ] || [ "$(printf '%s\n' "$REQUIRED" "$CLAB_VERSION" | sort -V | head -1)" != "$REQUIRED" ]; then
  echo "[UPGRADE] Version actuelle ($CLAB_VERSION) < $REQUIRED, mise à jour..."
  containerlab version upgrade
else
  echo "[UPGRADE] Version actuelle ($CLAB_VERSION) >= $REQUIRED, pas de mise à jour nécessaire"
fi

IMAGES=(
  "registry.iutbeziers.fr/mikrotik_routeros:7.18"
  "wbitt/network-multitool:latest"
)

for img in "${IMAGES[@]}"; do
  if ! docker image inspect "$img" &>/dev/null; then
    echo "[PULL] $img"
    docker image pull "$img"
  fi
done

netlab up "$@"

#echo "[ERRORS] Injection des erreurs OSPF pédagogiques sur les routeurs"

# Vérifier que sshpass est disponible
if ! command -v sshpass &>/dev/null; then
  echo "[ERRORS] sshpass non trouvé, installation..."
  sudo apt-get install -y sshpass 2>/dev/null || sudo dnf install -y sshpass 2>/dev/null || {
    echo "[ERRORS] Impossible d'installer sshpass, abandon"
    exit 1
  }
fi

# Trouver l'inventaire généré par clab (répertoire clab-*/)
#LABDIR=$(ls -d clab-*/ 2>/dev/null | head -1)
#INVENTORY="${LABDIR}nornir-simple-inventory.yml"

# Attendre que l'inventaire soit disponible (max 60s)
#echo "[ERRORS] Attente de l'inventaire clab..."
#for i in $(seq 1 30); do
#  [ -f "$INVENTORY" ] && break
#  sleep 2
#done
#[ -f "$INVENTORY" ] || { echo "[ERRORS] Inventaire $INVENTORY introuvable, abandon"; exit 1; }
#
## Extraire les IPs depuis l'inventaire YAML généré
#MK2_IP=$(python3 -c "import yaml; d=yaml.safe_load(open('$INVENTORY')); print(d['Mikrotik2']['hostname'])")
#MK3_IP=$(python3 -c "import yaml; d=yaml.safe_load(open('$INVENTORY')); print(d['Mikrotik3']['hostname'])")
#echo "[ERRORS] IPs: Mikrotik2=$MK2_IP Mikrotik3=$MK3_IP"
#
## Fonction SSH RouterOS sans vérification de clé hôte (mot de passe admin RouterOS)
#ros_cmd() {
#  local ip=$1; shift
#  local retries=15
#  for i in $(seq 1 $retries); do
#    sshpass -p 'admin' ssh \
#      -o StrictHostKeyChecking=no \
#      -o UserKnownHostsFile=/dev/null \
#      -o ConnectTimeout=5 \
#      admin@"$ip" "$@" && return 0
#    echo "[ERRORS] SSH vers $ip non disponible (tentative $i/$retries), attente 5s..."
#    sleep 5
#  done
#  echo "[ERRORS] Echec SSH vers $ip après $retries tentatives"
#  return 1
#}
#
## Erreur 1 : Mikrotik2 - area OSPF 0.0.0.0 -> 0.0.0.1 (index 0 = seule area)
#echo "[ERRORS] Mikrotik2 : changement area-id 0.0.0.0 -> 0.0.0.1"
#ros_cmd "$MK2_IP" '/routing/ospf/area set 0 area-id=0.0.0.1'
#
## Erreur 2 : Mikrotik3 - router-id dupliqué 10.0.0.3 -> 10.0.0.1 (index 0 = seule instance)
#echo "[ERRORS] Mikrotik3 : router-id 10.0.0.3 -> 10.0.0.1"
#ros_cmd "$MK3_IP" '/routing/ospf/instance set 0 router-id=10.0.0.1'
#
#echo "[ERRORS] Erreurs injectées - netlab validate devrait échouer"
