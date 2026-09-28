# End-to-end check for upstream PR 241: launch ITK-SNAP.exe with APPDATA pointing at a
# directory whose name contains non-ASCII characters, optionally open an image whose file
# name is non-ASCII, close the main window normally (so preferences are saved), and report
# what ended up on disk. Pure-ASCII source: non-ASCII names are built from code points so
# that Windows PowerShell 5.1 cannot misread this file.
param(
  [Parameter(Mandatory)] [string] $Exe,
  [Parameter(Mandatory)] [string] $Label,
  [switch] $AsciiAppData,
  [switch] $OpenImage,
  [int] $WaitSec = 25
)

$ErrorActionPreference = 'Stop'
$SP = Split-Path -Parent $MyInvocation.MyCommand.Path
$u = [char]0x00FC; $nihon = [string][char]0x65E5 + [char]0x672C   # u-umlaut, "Nihon"
$suffix = if ($AsciiAppData) { 'ascii' } else { "M${u}ller_$nihon" }
$appdata = Join-Path $SP "e2e_${Label}_appdata_$suffix"
if (Test-Path -LiteralPath $appdata) { Remove-Item -LiteralPath $appdata -Recurse -Force }
New-Item -ItemType Directory -Path $appdata | Out-Null

$argsList = @()
$img = $null
if ($OpenImage) {
  $img = Join-Path $appdata "Br${u}cke_$nihon.gipl.gz"
  Copy-Item -LiteralPath 'C:\dev\itksnap-developer\itksnap\Testing\TestData\MRIcrop-orig.gipl.gz' -Destination $img
  $argsList = @('-g', "`"$img`"")
}

# Snapshot of the scratchpad before, to spot mis-named (mojibake) siblings afterwards
$before = @(Get-ChildItem -LiteralPath $SP -Directory | ForEach-Object Name)

$env:APPDATA = $appdata
$env:PATH = 'C:\tk\Qt\6.9.3\msvc2022_64\bin;' + $env:PATH
$out = Join-Path $SP "e2e_${Label}_stdout.txt"; $err = Join-Path $SP "e2e_${Label}_stderr.txt"
$startArgs = @{ FilePath = $Exe; PassThru = $true; RedirectStandardOutput = $out; RedirectStandardError = $err }
if ($argsList.Count) { $startArgs.ArgumentList = $argsList }
$p = Start-Process @startArgs

"== [$Label] exe: $Exe"
"   APPDATA: $appdata"
if ($img) { "   image:   $img" }

Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$AEq = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$TC = [System.Windows.Automation.Condition]::TrueCondition
$title = ''
for ($i = 0; $i -lt $WaitSec; $i++) {
  Start-Sleep -Seconds 1
  $p.Refresh()
  if ($p.HasExited) { break }
  if ($p.MainWindowTitle) { $title = $p.MainWindowTitle }
  if ($title -like '*failed to start*') { break }
  # Decline the first-run "Allow Automatic Update Checks?" prompt (fresh APPDATA => first run)
  try {
    $pc = New-Object System.Windows.Automation.PropertyCondition($AEq::ProcessIdProperty, $p.Id)
    foreach ($w in $AEq::RootElement.FindAll($TS::Children, $pc)) {
      foreach ($d in $w.FindAll($TS::Descendants, $TC)) {
        if ($d.Current.ControlType.ProgrammaticName -eq 'ControlType.Window' -and $d.Current.Name) {
          # Any modal dialog: record its text and buttons, then dismiss it with a neutral button
          $kids = $d.FindAll($TS::Descendants, $TC)
          $btns = $kids | Where-Object { $_.Current.ControlType.ProgrammaticName -eq 'ControlType.Button' }
          $texts = $kids | Where-Object { $_.Current.ControlType.ProgrammaticName -eq 'ControlType.Text' -and $_.Current.Name } | ForEach-Object { $_.Current.Name }
          "   dialog '$($d.Current.Name)' at ${i}s: text: " + ($texts -join ' / ')
          "     buttons: " + (($btns | ForEach-Object { $_.Current.Name }) -join ' | ')
          $pick = $btns | Where-Object { $_.Current.Name -match '^&?(No|OK|Close|Cancel)$|^Don|^Not now' } | Select-Object -First 1
          if ($pick) { $pick.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); "     -> clicked '$($pick.Current.Name)'" }
        }
      }
    }
  } catch {}
}
"   window title after ${i}s: '$title'"

# All top-level windows of the process (an image-load error shows up as a second window)
try {
  Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
  $AE0 = [System.Windows.Automation.AutomationElement]
  $c0 = New-Object System.Windows.Automation.PropertyCondition($AE0::ProcessIdProperty, $p.Id)
  $wins = $AE0::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $c0)
  foreach ($w in $wins) {
    "   top-level window: '$($w.Current.Name)'"
    foreach ($t in $w.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
      if ($t.Current.ControlType.ProgrammaticName -match 'Window|Text' -and $t.Current.Name) { "     child: [$($t.Current.ControlType.ProgrammaticName)] $($t.Current.Name)" }
    }
  }
} catch { "   (window listing failed: $_)" }

if (-not $p.HasExited -and $title -like '*failed to start*') {
  # Read the error box through UI Automation, expanding "Show Details..." first
  try {
    Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
    $AE = [System.Windows.Automation.AutomationElement]
    $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty, $p.Id)
    $win = $AE::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Children, $cond)
    $all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($e in $all) {
      if ($e.Current.Name -like 'Show Details*') {
        $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep 1
      }
    }
    $all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($e in $all) {
      $n = $e.Current.Name
      $v = $null
      try { $v = $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
      if ($n -or $v) { "   dialog: [$($e.Current.ControlType.ProgrammaticName)] $n $v" }
    }
  } catch { "   (UI Automation read failed: $_)" }
  Stop-Process -Id $p.Id -Force
  $p.WaitForExit()
  "   RESULT: REFUSED TO START (dialog closed by script)"
} elseif (-not $p.HasExited) {
  [void]$p.CloseMainWindow()
  if (-not $p.WaitForExit(30000)) { Stop-Process -Id $p.Id -Force; "   (had to kill after CloseMainWindow)" }
  "   RESULT: STARTED; exit code after CloseMainWindow = $($p.ExitCode)"
} else {
  "   RESULT: EXITED ON ITS OWN; exit code = $($p.ExitCode)"
}

"   stderr tail:"; Get-Content -LiteralPath $err -Tail 5 -ErrorAction SilentlyContinue | ForEach-Object { "     $_" }
"   files under APPDATA:"
Get-ChildItem -LiteralPath $appdata -Recurse | ForEach-Object { "     " + $_.FullName.Substring($appdata.Length) }

$prefs = Join-Path $appdata 'itksnap.org\ITK-SNAP\UserPreferences.xml'
if (Test-Path -LiteralPath $prefs) {
  $bytes = [System.IO.File]::ReadAllBytes($prefs)
  $text = [System.Text.Encoding]::UTF8.GetString($bytes)
  "   UserPreferences.xml: $($bytes.Length) bytes; mentions image (UTF-8 decode): $([bool]($img -and $text.Contains((Split-Path -Leaf $img))))"
  $hist = ($text -split "`n" | Where-Object { $_ -match 'gipl' } | Select-Object -First 2)
  foreach ($h in $hist) { "     " + $h.Trim() }
}

$after = @(Get-ChildItem -LiteralPath $SP -Directory | ForEach-Object Name)
$new = $after | Where-Object { $before -notcontains $_ }
"   new directories in scratchpad (mojibake check): " + ($(if ($new) { $new -join ', ' } else { 'none' }))
