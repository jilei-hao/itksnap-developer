# vcpkg x-script downloader (X_VCPKG_ASSET_SOURCES). Fetches through the Windows
# TLS stack, which trusts the institutional firewall's re-signing root CA; vcpkg's
# built-in downloader does not. vcpkg verifies each file's SHA512 afterwards.
# mirror.msys2.org answers non-browser clients with a verification page, so its
# URLs fall back to the canonical repo.msys2.org, which vcpkg itself lists next.
param([string]$Url, [string]$Dst)
$ProgressPreference = 'SilentlyContinue'
$urls = @($Url)
if ($Url -match '^https://mirror\.msys2\.org/') { $urls += ($Url -replace '^https://mirror\.msys2\.org/', 'https://repo.msys2.org/') }
foreach ($u in $urls) {
  try {
    Invoke-WebRequest -Uri $u -OutFile $Dst -UseBasicParsing -ErrorAction Stop
    exit 0
  } catch {
    Write-Host "vcpkg-fetch: $u failed: $($_.Exception.Message)"
    Remove-Item -LiteralPath $Dst -ErrorAction SilentlyContinue
  }
}
exit 1
