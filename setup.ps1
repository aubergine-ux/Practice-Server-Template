# Downloads Paper and the plugins pinned in versions.lock into server\,
# checks their hashes, and copies in the default configs from defaults\.
# Safe to re-run: matching files are skipped and jars from an older lock are removed.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # the progress bar makes Invoke-WebRequest really slow
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Root = $PSScriptRoot
$Server = Join-Path $Root 'server'
$Defaults = Join-Path $Root 'defaults'
$Lock = Join-Path $Root 'versions.lock'
$Installed = Join-Path $Server '.installed'
$UA = 'practice-server-template/setup (github.com/aubergine-ux/Practice-Server-Template)'

New-Item -ItemType Directory -Force -Path (Join-Path $Server 'plugins') | Out-Null
$wanted = @()

foreach ($line in Get-Content $Lock) {
    if (-not $line -or $line.StartsWith('#')) { continue }
    $dest, $hash, $url = $line -split "`t"
    $algo, $expected = $hash -split ':', 2
    $target = Join-Path $Server $dest
    $wanted += $dest

    if ((Test-Path $target) -and (Get-FileHash $target -Algorithm $algo).Hash -eq $expected) {
        Write-Host "ok          $dest"
        continue
    }

    Write-Host "downloading $dest"
    Invoke-WebRequest -Uri $url -OutFile "$target.part" -UserAgent $UA -UseBasicParsing
    if ((Get-FileHash "$target.part" -Algorithm $algo).Hash -ne $expected) {
        Remove-Item "$target.part"
        throw "$algo mismatch for $dest"
    }
    Move-Item -Force "$target.part" $target
}

if (Test-Path $Installed) {
    foreach ($old in Get-Content $Installed) {
        if ($old -and ($wanted -notcontains $old) -and (Test-Path (Join-Path $Server $old))) {
            Write-Host "removing    $old (no longer in versions.lock)"
            Remove-Item (Join-Path $Server $old)
        }
    }
}
Set-Content -Path $Installed -Value $wanted -Encoding Ascii

# Copy in default configs, but never overwrite anything that already exists -
# once the server has started, server\ holds your real config.
Get-ChildItem $Defaults -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($Defaults.Length + 1)
    $target = Join-Path $Server $rel
    if (-not (Test-Path $target)) {
        New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
        Copy-Item $_.FullName $target
        Write-Host "copied      $rel"
    }
}

Write-Host ""
Write-Host "Done. Start the server with start.bat"
