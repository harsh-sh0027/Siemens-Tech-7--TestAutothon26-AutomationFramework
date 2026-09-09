param(
    [ValidateSet('web','mobile')]
    [string]$Mode = 'web',

    [ValidateSet('chromium','chrome','firefox','webkit','edge')]
    [string]$Browser = 'chromium',

    [string]$BrowserChannel,

    [ValidateSet('desktop','iphone13','pixel5','ipadMini')]
    [string]$TargetDevice = 'desktop',

    [string]$Viewport = '1366x768',

    [switch]$Headless,
    [switch]$Headed,

    [string]$TestPath = 'src/test/python/tests',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$pythonExe = Join-Path $root '.venv/Scripts/python.exe'
if (-not (Test-Path $pythonExe)) {
    throw "Python venv executable not found at $pythonExe"
}

# Platform mode
if ($Mode -eq 'mobile') {
    $env:IS_MOBILE = 'true'
} else {
    $env:IS_MOBILE = 'false'
}

# Browser mode (used in web mode)
$env:BROWSER = $Browser
if ($Browser -eq 'chrome') {
    if ([string]::IsNullOrWhiteSpace($BrowserChannel)) {
        $env:BROWSER_CHANNEL = 'chrome'
    } else {
        $env:BROWSER_CHANNEL = $BrowserChannel
    }
} elseif ($Browser -eq 'edge') {
    if ([string]::IsNullOrWhiteSpace($BrowserChannel)) {
        $env:BROWSER_CHANNEL = 'msedge'
    } else {
        $env:BROWSER_CHANNEL = $BrowserChannel
    }
} elseif (-not [string]::IsNullOrWhiteSpace($BrowserChannel)) {
    $env:BROWSER_CHANNEL = $BrowserChannel
} else {
    Remove-Item Env:BROWSER_CHANNEL -ErrorAction SilentlyContinue
}

# If a passthrough pytest option was accidentally bound to BrowserChannel,
# move it back into pytest args.
if (-not [string]::IsNullOrWhiteSpace($BrowserChannel) -and $BrowserChannel.StartsWith('--')) {
    if (-not $PytestArgs) {
        $PytestArgs = @()
    }
    $PytestArgs = @($BrowserChannel) + $PytestArgs
    Remove-Item Env:BROWSER_CHANNEL -ErrorAction SilentlyContinue
}

if ($PytestArgs) {
    $PytestArgs = $PytestArgs | Where-Object { $_ -ne '--' }
}

# Headless override
if ($Headless -and $Headed) {
    throw 'Use either -Headless or -Headed, not both.'
}
if ($Headless) {
    $env:HEADLESS = 'true'
} elseif ($Headed) {
    $env:HEADLESS = 'false'
}

# Device / viewport profile (web only)
Remove-Item Env:PLAYWRIGHT_DEVICE -ErrorAction SilentlyContinue
switch ($TargetDevice) {
    'desktop' {
        $normalized = $Viewport.ToLower().Replace(' ', '')
        if ($normalized -notmatch '^[0-9]+x[0-9]+$') {
            throw "Invalid -Viewport value '$Viewport'. Use WIDTHxHEIGHT like 1920x1080"
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

$cmd = @('-m', 'pytest', $TestPath)
if ($Mode -eq 'mobile') {
    $cmd += '--isMobile'
}
if ($PytestArgs) {
    $cmd += $PytestArgs
}

Write-Host "Running tests with Mode=$Mode Browser=$Browser TargetDevice=$TargetDevice" -ForegroundColor Cyan
if ($env:PLAYWRIGHT_DEVICE) {
    Write-Host "Using Playwright device profile: $($env:PLAYWRIGHT_DEVICE)" -ForegroundColor Cyan
} else {
    Write-Host "Using viewport: $($env:VIEWPORT_WIDTH)x$($env:VIEWPORT_HEIGHT)" -ForegroundColor Cyan
}

& $pythonExe @cmd
exit $LASTEXITCODE
