#!/bin/bash
# Rebuild and restart the Choreboard container.
# DATA_DIR is where the chore config lives; it is bind-mounted so the
# container stays disposable. Override it if you keep data elsewhere.
set -euo pipefail

cd "$(dirname "$0")"
DATA_DIR="${CHOREBOARD_DATA:-$HOME/choreboard-data}"
mkdir -p "$DATA_DIR"

docker stop choreboard 2>/dev/null || true
docker rm choreboard 2>/dev/null || true

docker build -t choreboard .
docker run -d \
  --name choreboard \
  --restart unless-stopped \
  -p 8090:8090 \
  -v "$DATA_DIR":/data \
  choreboard

echo "Choreboard rebuilt. Data dir: $DATA_DIR"
