$env:REPORT_MODE = "debug"

.\scripts\clean_test_artifacts.ps1

.\.venv\Scripts\pytest.exe `
  tests/web/test_organizer_ui_diagnostics.py `
  -v `
  --headed `
  --alluredir=allure-results `
  --clean-alluredir

if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

allure generate allure-results --clean -o allure-report
