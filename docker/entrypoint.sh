#!/usr/bin/env bash
set -euo pipefail
cd /opt/practice

./setup.sh

if [[ "${EULA:-}" =~ ^([Tt][Rr][Uu][Ee]|1|[Yy][Ee][Ss])$ ]]; then
  echo "eula=true" > server/eula.txt
fi
if ! grep -qs '^eula=true' server/eula.txt; then
  echo "Set EULA=true to accept the Minecraft EULA (https://aka.ms/MinecraftEULA)." >&2
  exit 1
fi

exec ./start.sh
