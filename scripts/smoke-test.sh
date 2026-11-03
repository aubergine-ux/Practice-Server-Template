#!/usr/bin/env bash
# Boots a fresh server and checks that every plugin loads and the maps get built.
# Used by CI, but you can run it locally too. It accepts the Minecraft EULA for
# the test server, so only run it if you're fine with that.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

./setup.sh
cd server
echo "eula=true" > eula.txt
rm -f console.in console.log
mkfifo console.in
tail -f console.in | MEMORY="${MEMORY:-2G}" ../start.sh > console.log 2>&1 &
pid=$!

fail() {
  echo "smoke test failed: $1" >&2
  cat console.log >&2
  echo stop > console.in || true
  exit 1
}

for _ in $(seq 1 150); do
  grep -q 'lobby and arenas are built' console.log && break
  kill -0 $pid 2>/dev/null || fail "server exited early"
  sleep 2
done
grep -q 'lobby and arenas are built' console.log || fail "maps never finished building"

if grep -E 'Error occurred while enabling|Could not load|Failed to load function' console.log; then
  fail "a plugin or function failed to load"
fi
for p in ZonePracticePro OldCombatMechanics FancyNpcs ViaVersion ViaBackwards; do
  grep -q "Enabling $p" console.log || fail "$p never enabled"
done

echo stop > console.in
for _ in $(seq 1 60); do
  kill -0 $pid 2>/dev/null || break
  sleep 1
done
rm -f console.in
echo "smoke test passed"
