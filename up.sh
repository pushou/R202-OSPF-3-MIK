#!/bin/bash
# Upgrade containerlab, pré-pull les images absentes, lance netlab up
# puis injecte les erreurs OSPF pédagogiques directement sur les routeurs

echo "[UPGRADE] netlab"
pip3 install --upgrade networklab --break-system-packages
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


# Vérifier que sshpass est disponible
if ! command -v sshpass &>/dev/null; then
  echo "[ERRORS] sshpass non trouvé, installation..."
  sudo apt-get install -y sshpass 2>/dev/null || sudo dnf install -y sshpass 2>/dev/null || {
    echo "[ERRORS] Impossible d'installer sshpass, abandon"
    exit 1
  }
fi


