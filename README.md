# CentralTurnos QA Automation

Framework base de automatizacion QA para CentralTurnos usando Python, Pytest, Playwright, Allure y Page Object Model.

## Instalacion

Crear y activar entorno virtual en Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instalar browsers de Playwright:

```powershell
python -m playwright install
```

Copiar variables de entorno:

```powershell
Copy-Item .env.example .env
```

Editar `.env` y configurar `CT_WEB_BASE_URL` para DEV:

```env
CT_WEB_BASE_URL=https://72-60-241-195.nip.io:8443
```

## Ejecucion

Login web:

```powershell
pytest -m web_login
```

Todos los tests web:

```powershell
pytest -m web
pytest tests/web
```

Login web con navegador visible:

```powershell
pytest --headed -m web_login
```

## Datos De Prueba

Los tests no hardcodean credenciales. Los usuarios se cargan desde JSON:

- `tests/web/data/web_users.json`
- `tests/api/data/api_users.json`
- `tests/e2e/data/e2e_users.json`

El login web usa:

```python
user = web_users["users"]["super_admin"]
```

## Estructura

```text
config/          # settings por entorno
tests/
  web/           # pruebas UI
    data/        # datos web
  api/           # pruebas API
    data/        # datos api
  e2e/           # flujos cross-layer
    data/        # datos e2e
pages/           # Page Object Model
api/             # clientes API
utils/           # logging y helpers
```

## Reportes

Generar resultados Allure:

```powershell
pytest --alluredir=reports/allure-results
```

Ver reporte:

```powershell
allure serve reports/allure-results
```
