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

$keywordProfiles = @{
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
    foreach ($name in ($keywordProfiles.Keys | Sort-Object)) {
        Write-Host ("  {0}  -  {1}" -f $name, $keywordProfiles[$name].Description)
    }
    exit 0
}

if (-not $keywordProfiles.ContainsKey($Key)) {
    Write-Host "Unknown key: $Key" -ForegroundColor Red
    Write-Host "Run: ./run-keyword.ps1 -List" -ForegroundColor Yellow
    exit 1
}

if ($Headless -and $Headed) {
    Write-Host "Use either -Headless or -Headed, not both." -ForegroundColor Red
    exit 1
}

$selectedRun = $keywordProfiles[$Key]

$pythonExe = Join-Path $root '.venv/Scripts/python.exe'
if (-not (Test-Path $pythonExe)) {
    throw "Python venv executable not found at $pythonExe"
}

$mode = $selectedRun.Mode
$browser = if ($selectedRun.ContainsKey("Browser")) { $selectedRun.Browser } else { "chromium" }
$targetDevice = if ($selectedRun.ContainsKey("TargetDevice")) { $selectedRun.TargetDevice } else { "desktop" }
$viewport = if ($selectedRun.ContainsKey("Viewport")) { $selectedRun.Viewport } else { "1366x768" }
$effectiveTestPath = if ([string]::IsNullOrWhiteSpace($TestPath)) { "src/test/python/tests" } else { $TestPath }

# Decide final headless mode from profile defaults, then apply explicit user override.
$effectiveHeadless = $null
if ($selectedRun.ContainsKey("Headless")) {
    $effectiveHeadless = [bool]$selectedRun.Headless
}
if ($Headless) {
    $effectiveHeadless = $true
}
if ($Headed) {
    $effectiveHeadless = $false
}

# Platform mode
if ($mode -eq 'mobile') {
    $env:IS_MOBILE = 'true'
} else {
    $env:IS_MOBILE = 'false'
}

# Browser mode (used in web mode)
$env:BROWSER = $browser
if ($browser -eq 'chrome') {
    $env:BROWSER_CHANNEL = 'chrome'
} elseif ($browser -eq 'edge') {
    $env:BROWSER_CHANNEL = 'msedge'
} else {
    Remove-Item Env:BROWSER_CHANNEL -ErrorAction SilentlyContinue
}

# Headless override
if ($null -ne $effectiveHeadless) {
    if ($effectiveHeadless) {
        $env:HEADLESS = 'true'
    } else {
        $env:HEADLESS = 'false'
    }
}

# Device / viewport profile (web only)
Remove-Item Env:PLAYWRIGHT_DEVICE -ErrorAction SilentlyContinue
switch ($targetDevice) {
    'desktop' {
        $normalized = $viewport.ToLower().Replace(' ', '')
        if ($normalized -notmatch '^[0-9]+x[0-9]+$') {
            throw "Invalid viewport value '$viewport'. Use WIDTHxHEIGHT like 1920x1080"
        }
        $parts = $normalized.Split('x')
        $env:VIEWPORT_WIDTH = $parts[0]
        $env:VIEWPORT_HEIGHT = $parts[1]
    }
    'iphone13' {
        $env:PLAYWRIGHT_DEVICE = 'iPhone 13'
    }
    'pixel5' {
        $env:PLAYWRIGHT_DEVICE = 'Pixel 5'
    }
    'ipadMini' {
        $env:PLAYWRIGHT_DEVICE = 'iPad Mini'
    }
}

$effectivePytestArgs = @('-v')
if ($PytestArgs) {
    $effectivePytestArgs += ($PytestArgs | Where-Object { $_ -ne '--' })
}

$cmd = @('-m', 'pytest', $effectiveTestPath)
if ($mode -eq 'mobile') {
    $cmd += '--isMobile'
}
if ($effectivePytestArgs) {
    $cmd += $effectivePytestArgs
}

Write-Host ("Using key: {0}" -f $Key) -ForegroundColor Green
Write-Host ("Profile: {0}" -f $selectedRun.Description) -ForegroundColor Green
Write-Host "Running tests with Mode=$mode Browser=$browser TargetDevice=$targetDevice" -ForegroundColor Cyan
if ($env:PLAYWRIGHT_DEVICE) {
    Write-Host "Using Playwright device profile: $($env:PLAYWRIGHT_DEVICE)" -ForegroundColor Cyan
} else {
    Write-Host "Using viewport: $($env:VIEWPORT_WIDTH)x$($env:VIEWPORT_HEIGHT)" -ForegroundColor Cyan
}

& $pythonExe @cmd
exit $LASTEXITCODE
