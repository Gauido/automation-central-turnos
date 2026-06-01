# Organizer LITE Test Strategy

## Enfoque

La estrategia es API primero y Web incremental. API valida contratos y reglas basicas contra `/api/organizer`. Web valida que el panel `/organizer` permita operar el flujo real sin depender de flujos publicos, Mercado Pago, WhatsApp ni legacy tournaments.

## API Primero

La suite API crea datos reales de Organizer LITE y valida:

- status esperado;
- ids generados;
- arrays no vacios;
- estados esperados;
- request/response sanitizados en Allure;
- negativos de reglas basicas.

No mezcla endpoints legacy `/api/Tournaments` con torneos creados por `/api/organizer`.

Los tests que crean datos Organizer usan cleanup especifico:

- `POST /api/qa/cleanup/organizer`
- alias documentado: `POST /api/qa/organizer/cleanup`

`POST /api/qa/reset` no limpia tablas `organizer_*`, por lo que no debe usarse como limpieza de Organizer.

## Suite Normal Vs Debug

### Suite Normal

Se usa para reporte sanitario/presentable.

- Ejecuta `tests/api/test_api_organizer.py`.
- Ejecuta `tests/api/test_api_qa_cleanup_organizer.py`.
- Ejecuta `tests/web/test_organizer_smoke.py`.
- Ejecuta `tests/web/test_organizer_tournament_setup_flow.py`.
- Ejecuta `tests/web/test_organizer_match_and_report_flow.py`.
- No ejecuta UI diagnostics.
- No adjunta HTML ni diagnostics del DOM.
- Usa steps, screenshots y request/response API sanitizados.

### Suite Debug/Diagnostics

Se usa para investigar locators o pantallas nuevas.

- Ejecuta `tests/web/test_organizer_ui_diagnostics.py`.
- Usa `utils/dom_discovery.py`.
- Puede adjuntar HTML, diagnostics MD/JSON y DOM dumps.
- No se usa para reportes finales.

El modo se controla con `REPORT_MODE`:

- `REPORT_MODE=normal`
- `REPORT_MODE=debug`

## Page Objects

El Page Object principal es `pages/organizer_page.py`.

Contiene acciones de:

- abrir Organizer;
- crear torneo;
- abrir tabs;
- crear categoria;
- crear parejas;
- crear zonas;
- sortear;
- generar partidos;
- cargar resultado;
- abrir llaves/reporte;
- detectar exports.

## Prioridad De Locators

1. `data-testid`
2. `get_by_role`
3. `get_by_label`
4. `get_by_placeholder`
5. selector tecnico acotado al contenedor actual

No usar XPath globales largos.

El Page Object prioriza los `data-testid` recibidos para torneo, tabs, categorias, parejas, zonas, resultados, bracket y exports. Los fallbacks quedan solo para compatibilidad con ambientes donde algun testid todavia no este disponible.

## Exports

El contrato Web de exports es:

1. abrir modal con `organizer-exports-btn-{kind}-open`;
2. descargar con `organizer-exports-btn-download`.

El primer caso automatizado es `organizer-exports-btn-fixture-pdf-open` para Fixture PDF.

## Manejo De Bloqueos

Si una pantalla no expone locator estable:

- ejecutar `tests/web/test_organizer_ui_diagnostics.py`;
- adjuntar screenshot/HTML/diagnostics solo en `REPORT_MODE=debug`;
- documentar gap;
- usar `pytest.skip()` controlado si no se puede avanzar sin fragilidad.
