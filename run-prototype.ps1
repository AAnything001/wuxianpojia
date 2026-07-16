# PROTOTYPE launcher — throw this directory away after a design wins.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 4173
$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
    Start-Process -FilePath python -ArgumentList '-m','http.server',$port,'--directory',$root -WindowStyle Hidden | Out-Null
    Start-Sleep -Milliseconds 800
}
Start-Process "http://127.0.0.1:$port/index.html?variant=A"
