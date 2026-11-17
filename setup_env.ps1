$workspaceRoot = $PSScriptRoot
$env:PATH = "$workspaceRoot\tools\node;$workspaceRoot\tools\ffmpeg\bin;" + $env:PATH
Write-Host "Environment configured: Node.js and FFmpeg added to PATH"

