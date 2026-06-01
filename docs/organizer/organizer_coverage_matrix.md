# Organizer LITE Coverage Matrix

| Suite | Archivo | Estado | Resultado | Observacion |
| ----- | ------- | ------ | --------- | ----------- |
| API Organizer | `tests/api/test_api_organizer.py` | Estable | 8 passed, 0 skipped, 0 failed | Cubre torneo, categoria, parejas, zonas, matches, pago y negativos basicos. |
| QA Cleanup Organizer | `tests/api/test_api_qa_cleanup_organizer.py` | Estable | 1 passed, 0 skipped, 0 failed | Valida `POST /api/qa/cleanup/organizer` y que borre torneos Organizer. |
| Organizer Smoke | `tests/web/test_organizer_smoke.py` | Estable | 3 passed, 0 skipped, 0 failed | Carga `/organizer`, crea torneo y valida tabs visibles actuales. |
| Tournament Setup Flow | `tests/web/test_organizer_tournament_setup_flow.py` | Estable | 3 passed, 0 skipped, 0 failed | Cubre categoria, parejas, zonas, sorteo y generacion de partidos. |
| Match And Report Flow | `tests/web/test_organizer_match_and_report_flow.py` | Estable | 4 passed, 0 skipped, 0 failed | Resultado, bracket, reporte y Fixture PDF pasan. |
| UI Diagnostics | `tests/web/test_organizer_ui_diagnostics.py` | Debug | 3 passed, 0 skipped, 0 failed | Fuera de suite normal. Genera HTML, Markdown, JSON y screenshots para investigacion. |

## Comando Sanitario Normal

```text
.\scripts\run_health_report.ps1
```

## Comando Debug UI

```text
.\scripts\run_organizer_ui_diagnostics.ps1
```
