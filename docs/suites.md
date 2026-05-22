# Suites

## Comandos Allure

Limpiar reportes:

```powershell
Remove-Item -Recurse -Force allure-results, allure-report -ErrorAction SilentlyContinue
```

Suite API:

```powershell
pytest -m api -v --alluredir=allure-results -rs
```

Suite WEB:

```powershell
pytest -m web -v --alluredir=allure-results -rs
```

Suite WEB + API:

```powershell
pytest -m "web or api" -v --alluredir=allure-results -rs
```

Generar reporte:

```powershell
allure generate allure-results -o allure-report --clean
```

Abrir reporte:

```powershell
allure open allure-report
```

Diagnóstico actual:

```powershell
Remove-Item -Recurse -Force allure-results, allure-report -ErrorAction SilentlyContinue; pytest tests/api/test_api_qa_health.py tests/api/test_api_bookings.py::test_api_create_booking_active_tenant tests/api/test_api_cash.py::test_api_cash_bookings_summary tests/web/test_booking_negatives.py tests/web/test_booking_race_condition.py tests/web/test_staff_permissions.py -v -rs --alluredir=allure-results; allure generate allure-results -o allure-report --clean; allure open allure-report
```

## Smoke

```powershell
.\.venv\Scripts\pytest.exe -m smoke -q
```

## Regression

```powershell
.\.venv\Scripts\pytest.exe -m regression -q
```

## QA

Requiere `QA_TOKEN` en `.env`.

```powershell
.\.venv\Scripts\pytest.exe -m qa -q
```

## Web Only

```powershell
.\.venv\Scripts\pytest.exe -m web -q
```

## API Only

```powershell
.\.venv\Scripts\pytest.exe -m api -q
```

## Notas

- Headless por defecto.
- Headed opcional con `--headed`.
- Allure estándar escribe en `allure-results`.
- Artifacts de fallos web se guardan en `artifacts/dom`.
