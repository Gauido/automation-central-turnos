# Organizer LITE - Health Report

## Fecha

2026-06-01

## Suites Ejecutadas

| Suite | Archivo | Resultado |
|---|---|---|
| API Organizer | `tests/api/test_api_organizer.py` | 8 passed |
| QA Cleanup Organizer | `tests/api/test_api_qa_cleanup_organizer.py` | 1 passed |
| Organizer Smoke | `tests/web/test_organizer_smoke.py` | 3 passed |
| Tournament Setup Flow | `tests/web/test_organizer_tournament_setup_flow.py` | 3 passed |
| Match And Report Flow | `tests/web/test_organizer_match_and_report_flow.py` | 4 passed |

## Resultado Global

- Passed: 19
- Skipped: 0
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
- Cleanup especifico Organizer.
- Export Fixture PDF por modal y descarga real.

## Gaps Conocidos

- Page Object prioriza `data-testid`; mantiene fallbacks porque no todos los IDs del contrato estan confirmados visualmente en todos los ambientes.
- Label visual `Nombre *` no asociado al input.
- `Podio` no aparece como tab visible actualmente.
- Expandir exports a Posiciones PDF, Partidos Excel y Cierre PDF.
- Negativo API: resultado `6-6` aceptado por backend, esperado HTTP 400.
- Negativo API: reopen zona con bracket queda skipped porque build-bracket no esta disponible para ese setup.
- Negativo Web: sortear zonas sin parejas suficientes queda permitido por UI.

## Suite Negativa

Comando:

```text
.\scripts\run_organizer_negative_tests.ps1
```

Resultado actual:

```text
6 passed
1 skipped
2 xfailed
0 failed
```

## Suite CRUD

Comando:

```text
.\scripts\run_organizer_crud_tests.ps1
```

Resultado actual:

```text
6 passed
6 skipped
1 xfailed
0 failed
```

Gaps CRUD:

- API categorias no se puede validar por listado porque responde 405.
- Web no expone acciones estables para delete torneo, edit/delete categoria ni edit pair.
- Web delete pair no remueve la pareja visible.

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
19 passed
0 skipped
0 failed
```

Warnings no bloqueantes:

```text
PytestCacheWarning: no pudo crear .pytest_cache\v\cache por Acceso denegado en Windows.
```

Verificacion Allure:

```text
No se detectaron attachments HTML, diagnostics MD/JSON ni suite UI diagnostics en la corrida normal.
```
