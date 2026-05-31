# Organizer LITE QA

## Contexto

Organizer LITE es el modulo admin-only de torneos en `/organizer` y `/api/organizer`. Funciona como "papel virtual" para correr torneos manuales desde panel, sin inscripcion publica, Mercado Pago automatico ni bot WhatsApp.

## Suite Normal

La suite normal genera el reporte sanitario/presentable. No ejecuta diagnostics UI ni adjunta dumps HTML/MD/JSON del DOM.

Archivos:

- `tests/api/test_api_organizer.py`
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
- Web match/report flow: `3 passed, 1 skipped`.
- UI diagnostics: `3 passed` fuera del reporte normal.

## Gaps Conocidos

- Organizer Web no expone `data-testid` de forma consistente.
- El label visual `Nombre *` del modal `Nuevo torneo` no esta asociado al input.
- `Podio` no aparece como tab visible actualmente.
- Exports visibles no disparan descarga detectable con `page.expect_download` para `Fixture PDF`.
- Falta contrato claro para exports: descarga real, blob, navegacion, popup o endpoint.
- En Windows puede aparecer warning no bloqueante de `.pytest_cache` con `Acceso denegado`.
