$env:REPORT_MODE = "normal"
if (-not $env:ATTACH_TEST_CONTEXT) {
  $env:ATTACH_TEST_CONTEXT = "true"
}

.\scripts\clean_test_artifacts.ps1

.\.venv\Scripts\pytest.exe `
  tests/api/test_api_organizer_negatives.py `
  tests/web/test_organizer_negative_cases.py `
  -v `
  -o cache_dir=test-results/pytest-cache `
  --cache-clear `
  --alluredir=allure-results `
  --clean-alluredir

if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

allure generate allure-results --clean -o allure-report
