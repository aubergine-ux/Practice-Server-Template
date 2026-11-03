#!/usr/bin/env bash
# Starts the server. Override the heap size with: MEMORY=6G ./start.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/server"
MEMORY="${MEMORY:-4G}"

if [[ ! -f server.jar ]]; then
  echo "server.jar not found - run ./setup.sh first" >&2
  exit 1
fi

if ! grep -qs '^eula=true' eula.txt; then
  echo "You must accept the Minecraft EULA to run a server: https://aka.ms/MinecraftEULA"
  read -r -p "Do you accept it? [y/N] " answer
  [[ "$answer" =~ ^[Yy] ]] || exit 1
  echo "eula=true" >eula.txt
fi

# JVM flags recommended by PaperMC for this version (fill.papermc.io)
exec java -Xms"$MEMORY" -Xmx"$MEMORY" \
  -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled \
  -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC \
  -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 \
  -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 \
  -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 \
  -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 \
  -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32 \
  -jar server.jar --nogui "$@"
