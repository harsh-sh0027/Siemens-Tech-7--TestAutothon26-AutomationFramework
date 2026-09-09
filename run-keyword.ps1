param(
    [string]$Key = "chrome",
    [switch]$List,
    [switch]$Headless,
    [switch]$Headed,
    [string]$TestPath,
    [string[]]$PytestArgs
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$profiles = @{
    chrome = @{
        Description = "Web Chrome desktop 1366x768 headed"
        Mode = "web"
        Browser = "chrome"
        TargetDevice = "desktop"
        Viewport = "1366x768"
        Headless = $false
    }
    chrome_headless = @{
        Description = "Web Chrome desktop 1366x768 headless"
        Mode = "web"
        Browser = "chrome"
        TargetDevice = "desktop"
        Viewport = "1366x768"
        Headless = $true
    }
    firefox = @{
        Description = "Web Firefox desktop 1920x1080 headless"
        Mode = "web"
        Browser = "firefox"
        TargetDevice = "desktop"
        Viewport = "1920x1080"
        Headless = $true
    }
    webkit = @{
        Description = "Web WebKit desktop 1440x900 headless"
        Mode = "web"
        Browser = "webkit"
        TargetDevice = "desktop"
        Viewport = "1440x900"
        Headless = $true
    }
    edge = @{
        Description = "Web Edge desktop 1366x768 headless"
        Mode = "web"
        Browser = "edge"
        TargetDevice = "desktop"
        Viewport = "1366x768"
        Headless = $true
    }
    iphone13 = @{
        Description = "Web Chrome emulation iPhone 13 headless"
        Mode = "web"
        Browser = "chrome"
        TargetDevice = "iphone13"
        Headless = $true
    }
    pixel5 = @{
        Description = "Web Chrome emulation Pixel 5 headless"
        Mode = "web"
        Browser = "chrome"
        TargetDevice = "pixel5"
        Headless = $true
    }
    ipad = @{
        Description = "Web Chrome emulation iPad Mini headless"
        Mode = "web"
        Browser = "chrome"
        TargetDevice = "ipadMini"
        Headless = $true
    }
    mobile = @{
        Description = "Native mobile Appium run"
        Mode = "mobile"
    }
}

if ($List) {
    Write-Host "Available keywords:" -ForegroundColor Cyan
    foreach ($name in ($profiles.Keys | Sort-Object)) {
        Write-Host ("  {0}  -  {1}" -f $name, $profiles[$name].Description)
    }
    exit 0
}

if (-not $profiles.ContainsKey($Key)) {
    Write-Host "Unknown key: $Key" -ForegroundColor Red
    Write-Host "Run: ./run-keyword.ps1 -List" -ForegroundColor Yellow
    exit 1
}

if ($Headless -and $Headed) {
    Write-Host "Use either -Headless or -Headed, not both." -ForegroundColor Red
    exit 1
}

$selectedRun = $profiles[$Key]

$scriptParams = @{
    Mode = $selectedRun.Mode
}

if ($selectedRun.ContainsKey("Browser")) {
    $scriptParams.Browser = $selectedRun.Browser
}
if ($selectedRun.ContainsKey("TargetDevice")) {
    $scriptParams.TargetDevice = $selectedRun.TargetDevice
}
if ($selectedRun.ContainsKey("Viewport")) {
    $scriptParams.Viewport = $selectedRun.Viewport
}
if ($selectedRun.ContainsKey("Headless")) {
    if ($selectedRun.Headless) {
        $scriptParams.Headless = $true
    } else {
        $scriptParams.Headed = $true
    }
}
if (-not [string]::IsNullOrWhiteSpace($TestPath)) {
    $scriptParams.TestPath = $TestPath
}

# User preference overrides profile default headed/headless behavior.
if ($Headless) {
    $scriptParams.Remove("Headed") | Out-Null
    $scriptParams.Headless = $true
}
if ($Headed) {
    $scriptParams.Remove("Headless") | Out-Null
    $scriptParams.Headed = $true
}

$effectivePytestArgs = @("-v")
if ($PytestArgs) {
    $effectivePytestArgs += $PytestArgs
}
$scriptParams.PytestArgs = $effectivePytestArgs

Write-Host ("Using key: {0}" -f $Key) -ForegroundColor Green
Write-Host ("Profile: {0}" -f $selectedRun.Description) -ForegroundColor Green

& "$root/run-tests.ps1" @scriptParams
exit $LASTEXITCODE
