$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& py -3 (Join-Path $scriptDir 'install.py') @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
