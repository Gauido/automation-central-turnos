# Organizer LITE Coverage Matrix

| Suite | Archivo | Estado | Resultado | Observacion |
| ----- | ------- | ------ | --------- | ----------- |
| API Organizer | `tests/api/test_api_organizer.py` | Estable | 8 passed, 0 skipped, 0 failed | Cubre torneo, categoria, parejas, zonas, matches, pago y negativos basicos. |
| QA Cleanup Organizer | `tests/api/test_api_qa_cleanup_organizer.py` | Estable | 1 passed, 0 skipped, 0 failed | Valida `POST /api/qa/cleanup/organizer` y que borre torneos Organizer. |
| Organizer Smoke | `tests/web/test_organizer_smoke.py` | Estable | 3 passed, 0 skipped, 0 failed | Carga `/organizer`, crea torneo y valida tabs visibles actuales. |
| Tournament Setup Flow | `tests/web/test_organizer_tournament_setup_flow.py` | Estable | 3 passed, 0 skipped, 0 failed | Cubre categoria, parejas, zonas, sorteo y generacion de partidos. |
| Match And Report Flow | `tests/web/test_organizer_match_and_report_flow.py` | Estable | 4 passed, 0 skipped, 0 failed | Resultado, bracket, reporte y Fixture PDF pasan. |
| API Negatives | `tests/api/test_api_organizer_negatives.py` | Parcial | 3 passed, 1 skipped, 1 xfailed | Refund sin nota, mas de 3 sets y remover pareja con match jugado pasan. Tiebreak 6-6 aceptado por backend queda xfail. Reopen con bracket queda skipped por endpoint bracket no disponible. |
| Web Negatives | `tests/web/test_organizer_negative_cases.py` | Parcial | 3 passed, 1 xfailed | Pareja incompleta, generar partidos sin sorteo y resultado invalido pasan. Sorteo sin parejas queda xfail porque la UI lo permite. |
| API CRUD | `tests/api/test_api_organizer_crud.py` | Parcial | 5 passed, 2 skipped | Torneo update/delete, pair update/delete y delete tournament con hijos pasan. Category update/delete quedan skipped porque listado categorias devuelve 405 para validar. |
| Web CRUD | `tests/web/test_organizer_crud_cases.py` | Parcial | 1 passed, 4 skipped, 1 xfailed | Editar torneo pasa. Delete torneo, edit/delete categoria y edit pair quedan skipped por acciones/inputs no estables. Delete pair queda xfail porque no remueve visible. |
| UI Diagnostics | `tests/web/test_organizer_ui_diagnostics.py` | Debug | 3 passed, 0 skipped, 0 failed | Fuera de suite normal. Genera HTML, Markdown, JSON y screenshots para investigacion. |

## Comando Sanitario Normal

```text
.\scripts\run_health_report.ps1
```

## Comando Debug UI

```text
.\scripts\run_organizer_ui_diagnostics.ps1
```

## Comando Negativos Organizer

```text
.\scripts\run_organizer_negative_tests.ps1
```

## Comando CRUD Organizer

```text
.\scripts\run_organizer_crud_tests.ps1
```
