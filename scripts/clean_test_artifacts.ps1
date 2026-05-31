$paths = @(
  "artifacts",
  "screenshots",
  "allure-results",
  "allure-report",
  "test-results",
  "playwright-report",
  "videos",
  "traces",
  "downloads",
  ".pytest_cache"
)

foreach ($path in $paths) {
  if (Test-Path $path) {
    Write-Host "Removing $path"
    Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
  }
}

Write-Host "Test artifacts cleaned."
