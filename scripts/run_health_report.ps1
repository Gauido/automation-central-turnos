$env:REPORT_MODE = "normal"

.\scripts\clean_test_artifacts.ps1

.\.venv\Scripts\pytest.exe `
  tests/api/test_api_organizer.py `
  tests/web/test_organizer_smoke.py `
  tests/web/test_organizer_tournament_setup_flow.py `
  tests/web/test_organizer_match_and_report_flow.py `
  -v `
  --headed `
  --alluredir=allure-results `
  --clean-alluredir

if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

allure generate allure-results --clean -o allure-report
