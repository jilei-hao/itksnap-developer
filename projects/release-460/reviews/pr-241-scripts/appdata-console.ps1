# Console-only check: run an executable that constructs SystemInterface (e.g. logic_api_test.exe)
# with APPDATA pointing at a non-ASCII directory, then list what was created, by wide name.
param([Parameter(Mandatory)] [string] $Exe, [Parameter(Mandatory)] [string] $Label)
$SP = Split-Path -Parent $MyInvocation.MyCommand.Path
$u = [char]0x00FC; $nihon = [string][char]0x65E5 + [char]0x672C
$root = Join-Path $SP "console_$Label"
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
New-Item -ItemType Directory -Path $root | Out-Null
$appdata = Join-Path $root "appdata_M${u}ller_$nihon"
New-Item -ItemType Directory -Path $appdata | Out-Null
$env:APPDATA = $appdata
$env:PATH = 'C:\tk\Qt\6.9.3\msvc2022_64\bin;' + $env:PATH
"== [$Label] $Exe"
"   APPDATA = $appdata"
$out = & $Exe 2>&1 | Out-String
"   exit code: $LASTEXITCODE"
"   output: " + ($out.Trim() -split "`r?`n" | Select-Object -Last 4) -join ' | '
"   everything under $root (name + UTF-16 code units of non-ASCII chars):"
Get-ChildItem -LiteralPath $root -Recurse | ForEach-Object {
  $rel = $_.FullName.Substring($root.Length)
  $codes = ($rel.ToCharArray() | Where-Object { [int]$_ -gt 127 } | ForEach-Object { 'U+{0:X4}' -f [int]$_ }) -join ' '
  "     $rel   [$codes]"
}
