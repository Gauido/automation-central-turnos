# Organizer LITE - Health Report

## Fecha

2026-05-31

## Suites Ejecutadas

| Suite | Archivo | Resultado |
|---|---|---|
| API Organizer | `tests/api/test_api_organizer.py` | 8 passed |
| Organizer Smoke | `tests/web/test_organizer_smoke.py` | 3 passed |
| Tournament Setup Flow | `tests/web/test_organizer_tournament_setup_flow.py` | 3 passed |
| Match And Report Flow | `tests/web/test_organizer_match_and_report_flow.py` | 3 passed, 1 skipped |

## Resultado Global

- Passed: 17
- Skipped: 1
- Failed: 0

## Cobertura Funcional Validada

- Creacion de torneo por API.
- Creacion de categoria por API.
- Creacion de parejas por API.
- Sorteo de zonas por API.
- Generacion de partidos por API.
- Registro de pago manual por API.
- Validaciones negativas API.
- Carga web de Organizer.
- Creacion web de torneo.
- Creacion web de categoria.
- Creacion web de parejas.
- Creacion web de zonas.
- Sorteo aleatorio web.
- Generacion de partidos web.
- Carga de resultado 6-3 / 6-4.
- Llaves/bracket.
- Reporte economico.

## Gaps Conocidos

- No hay `data-testid` en Organizer Web de forma consistente.
- Label visual `Nombre *` no asociado al input.
- `Podio` no aparece como tab visible actualmente.
- Exports visibles, pero `page.expect_download` no detecta descarga para Fixture PDF.
- Falta contrato claro de exports: descarga real, blob, navegacion, popup o endpoint.

## Suite Normal

La suite normal excluye `tests/web/test_organizer_ui_diagnostics.py`.

No adjunta HTML, diagnostics MD/JSON ni dumps de DOM. API conserva request/response sanitizados.

## Resultado De Ejecucion

Comando:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\run_health_report.ps1
```

Resultado:

```text
17 passed
1 skipped
0 failed
```

Skip:

```text
tests/web/test_organizer_match_and_report_flow.py::test_organizer_exports_available
El boton de exportacion fixture_pdf no disparo descarga detectable.
```

Warnings no bloqueantes:

```text
PytestCacheWarning: no pudo crear .pytest_cache\v\cache por Acceso denegado en Windows.
```

Verificacion Allure:

```text
No se detectaron attachments HTML, diagnostics MD/JSON ni suite UI diagnostics en la corrida normal.
```
