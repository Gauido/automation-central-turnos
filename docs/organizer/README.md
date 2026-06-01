# Organizer LITE QA

## Contexto

Organizer LITE es el modulo admin-only de torneos en `/organizer` y `/api/organizer`. Funciona como "papel virtual" para correr torneos manuales desde panel, sin inscripcion publica, Mercado Pago automatico ni bot WhatsApp.

No se baja ninguna rama ni se asume `feature/dev`; estos tests se adaptan al contrato tecnico recibido sobre `data-testid`, cleanup Organizer y exports.

## Suite Normal

La suite normal genera el reporte sanitario/presentable. No ejecuta diagnostics UI ni adjunta dumps HTML/MD/JSON del DOM.

Archivos:

- `tests/api/test_api_organizer.py`
- `tests/api/test_api_qa_cleanup_organizer.py`
- `tests/web/test_organizer_smoke.py`
- `tests/web/test_organizer_tournament_setup_flow.py`
- `tests/web/test_organizer_match_and_report_flow.py`

Comando:

```text
.\scripts\run_health_report.ps1
```

## Suite Debug

La suite debug se usa solo para investigar locators o pantallas nuevas.

Archivo:

- `tests/web/test_organizer_ui_diagnostics.py`

Comando:

```text
.\scripts\run_organizer_ui_diagnostics.ps1
```

## Cobertura Actual

- API Organizer: `8 passed`.
- Web smoke: `3 passed`.
- Web tournament setup flow: `3 passed`.
- Web match/report flow: `4 passed`.
- QA cleanup Organizer: `1 passed`.
- UI diagnostics: `3 passed` fuera del reporte normal.

## Gaps Conocidos

- Organizer Web informa nuevo contrato con 164 `data-testid`; el Page Object prioriza `get_by_test_id()` y conserva fallbacks temporales.
- El label visual `Nombre *` del modal `Nuevo torneo` no esta asociado al input.
- `Podio` no aparece como tab visible actualmente.
- Cleanup Organizer usa `POST /api/qa/cleanup/organizer`; `/api/qa/reset` no limpia tablas `organizer_*`.
- Export Fixture PDF resuelto con modal: `organizer-exports-btn-fixture-pdf-open` y `organizer-exports-btn-download`.
- En Windows puede aparecer warning no bloqueante de `.pytest_cache` con `Acceso denegado`.
