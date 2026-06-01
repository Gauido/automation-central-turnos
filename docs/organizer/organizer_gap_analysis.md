# Organizer LITE Gap Analysis

## Estado De Testabilidad

- Contrato recibido: Organizer Web expone `data-testid` con formato `{modulo}-{seccion}-{tipo}-{accion-o-target}`.
- `pages/organizer_page.py` fue adaptado para priorizar `get_by_test_id()`.
- Se conservan fallbacks por rol/texto mientras se confirma que todos los testids estan disponibles en ambiente.
- Corrida sanitaria 2026-06-01: suite normal paso usando los testids disponibles y fallbacks acotados.
- Modal `Nuevo torneo` tiene label visual no asociado:

```html
<label class="form__label">Nombre *</label>
<input placeholder="Ej: Apertura 2026" class="form__input">
```

Esto impide usar `get_by_label(/Nombre/)`.

- El fallback actual usa selector acotado:

```text
div[role="dialog"] input[placeholder="Ej: Apertura 2026"]
```

## Gaps Funcionales UI

- `Podio` no aparece como tab visible en el detalle actual de Organizer Web.
- `Podio PDF` no aparece visible en exports actuales.
- Exports tienen contrato recibido:
  - abrir modal con `organizer-exports-btn-{kind}-open`;
  - descargar con `organizer-exports-btn-download`.
  - Fixture PDF usa `organizer-exports-btn-fixture-pdf-open`.
- Corrida sanitaria 2026-06-01: Fixture PDF descarga correctamente.

## Cleanup Organizer

- Confirmado por contrato recibido: `POST /api/qa/cleanup/organizer`.
- Alias documentado: `POST /api/qa/organizer/cleanup`.
- `/api/qa/reset` no limpia tablas `organizer_*`.
- Test tecnico: `tests/api/test_api_qa_cleanup_organizer.py`.
- Corrida sanitaria 2026-06-01: cleanup Organizer paso y borro al menos 1 torneo.

## Contratos A Confirmar En Corrida

- Expandir exports a Posiciones PDF, Partidos Excel y Cierre PDF.
- Podio: confirmar si debe existir como tab Web o solo como endpoint/export.

## Warning No Bloqueante

En Windows aparece:

```text
PytestCacheWarning: could not create cache path ... .pytest_cache ... Acceso denegado
```

No bloquea ejecuciones, pero conviene corregir permisos o limpiar `.pytest_cache`.

## Recomendaciones Frontend

- `data-testid="organizer-create-tournament-button"`
- `data-testid="organizer-tournament-name-input"`
- `data-testid="organizer-save-tournament-button"`
- `data-testid="organizer-create-category-button"`
- `data-testid="organizer-save-category-button"`
- `data-testid="organizer-create-pair-button"`
- `data-testid="organizer-pair-player1-input"`
- `data-testid="organizer-pair-player2-input"`
- `data-testid="organizer-save-pair-button"`
- `data-testid="organizer-zones-random-assign-button"`
- `data-testid="organizer-zones-generate-matches-button"`
- `data-testid="organizer-match-result-button"`
- `data-testid="organizer-save-result-button"`
- `data-testid="organizer-build-bracket-button"`
- `data-testid="organizer-exports-btn-fixture-pdf-open"`
- `data-testid="organizer-exports-btn-download"`

## Recomendacion De Accesibilidad

Asociar labels e inputs:

```html
<label for="organizer-tournament-name">Nombre</label>
<input id="organizer-tournament-name" data-testid="organizer-tournament-name-input">
```
