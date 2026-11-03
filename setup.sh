#!/usr/bin/env bash
# Downloads Paper and the plugins pinned in versions.lock into server/,
# checks their hashes, and copies in the default configs from defaults/.
# Safe to re-run: matching files are skipped and jars from an older lock are removed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SERVER="$ROOT/server"
LOCK="$ROOT/versions.lock"
INSTALLED="$SERVER/.installed"   # files this script manages, used to clean up old versions
UA="minecraft-duels-template/setup (github.com)"

command -v curl >/dev/null || { echo "error: curl is required" >&2; exit 1; }

hash_of() { # <algo> <file>
  case "$1" in
    sha256) sha256sum "$2" | cut -d' ' -f1 ;;
    sha512) sha512sum "$2" | cut -d' ' -f1 ;;
    *) echo "error: unsupported hash '$1'" >&2; exit 1 ;;
  esac
}

mkdir -p "$SERVER/plugins"
wanted=()

while IFS=$'\t' read -r dest hash url; do
  [[ -z "$dest" || "$dest" == \#* ]] && continue
  algo="${hash%%:*}"
  expected="${hash#*:}"
  target="$SERVER/$dest"
  wanted+=("$dest")

  if [[ -f "$target" && "$(hash_of "$algo" "$target")" == "$expected" ]]; then
    echo "ok          $dest"
    continue
  fi

  echo "downloading $dest"
  curl -fsSL -A "$UA" -o "$target.part" "$url"
  actual="$(hash_of "$algo" "$target.part")"
  if [[ "$actual" != "$expected" ]]; then
    rm -f "$target.part"
    echo "error: $algo mismatch for $dest" >&2
    exit 1
  fi
  mv "$target.part" "$target"
done <"$LOCK"

if [[ -f "$INSTALLED" ]]; then
  while read -r old; do
    [[ -n "$old" ]] || continue
    if [[ ! " ${wanted[*]} " == *" $old "* && -f "$SERVER/$old" ]]; then
      echo "removing    $old (no longer in versions.lock)"
      rm -f "$SERVER/$old"
    fi
  done <"$INSTALLED"
fi
printf '%s\n' "${wanted[@]}" >"$INSTALLED"

# Copy in default configs, but never overwrite anything that already exists -
# once the server has started, server/ holds your real config.
(cd "$ROOT/defaults" && find . -type f) | while read -r f; do
  f="${f#./}"
  if [[ ! -e "$SERVER/$f" ]]; then
    mkdir -p "$(dirname "$SERVER/$f")"
    cp "$ROOT/defaults/$f" "$SERVER/$f"
    echo "copied      $f"
  fi
done

echo
echo "Done. Start the server with ./start.sh"
