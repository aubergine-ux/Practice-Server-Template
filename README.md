# practice-server-template

Template for a PvP practice / duels server on Paper 26.x. Clients from 1.20 up can join (ViaVersion + ViaBackwards).

Still being put together, expect things to move around.

## Quick start

Needs Java 25+, `curl` and `bash`.

```sh
./setup.sh    # downloads paper + plugins into server/, checks hashes
./start.sh    # asks you to accept the EULA the first time
```

Heap defaults to 4G, change it with `MEMORY=6G ./start.sh`.

## How it's laid out

- `manifest.txt` - which Paper version and plugins to install
- `versions.lock` - exact download URLs and hashes, generated from the manifest
- `defaults/` - starter configs, copied into `server/` only if they don't exist yet
- `server/` - the actual server, ignored by git

To bump versions or add a plugin, edit `manifest.txt` and run `./scripts/update-lock.sh` (needs `jq`), then `./setup.sh` again.

Plugin jars aren't committed, setup pulls them from Modrinth / PaperMC so each plugin's own license applies.
