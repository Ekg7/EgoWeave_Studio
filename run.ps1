param(
    [Parameter(Mandatory=$true, Position=0)][string]$VideoPath,
    [Parameter(Mandatory=$true, Position=1)][string]$OutputJson
)

$workspaceRoot = $PSScriptRoot
$env:PYTHONPATH = "$workspaceRoot;$env:PYTHONPATH"
$env:PATH = "$workspaceRoot\tools\node;$workspaceRoot\tools\ffmpeg\bin;" + $env:PATH

python -m inference.cli $VideoPath $OutputJson

