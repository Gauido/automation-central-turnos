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

## Gaps Detectados Por Negativos

- API resultado/tiebreak: `PUT/POST /api/organizer/matches/{mid}/result` acepta set `6-6`; esperado HTTP 400.
- API bracket/reopen: `build-bracket` no queda disponible en el ambiente actual para validar reapertura de zona con bracket; test skipped controlado.
- Web zonas: Organizer Web permite sortear zonas sin parejas suficientes; esperado bloqueo o validacion visible.

## Negativos Cubiertos

- Refund negativo sin nota devuelve HTTP 400.
- Resultado con mas de 3 sets devuelve HTTP 400.
- Remover pareja de zona con partido jugado devuelve HTTP 409.
- Pareja incompleta en UI no se crea.
- Generar partidos sin sorteo previo queda bloqueado/validado en UI.
- Resultado invalido desde UI queda bloqueado/validado.

## Gaps Detectados Por CRUD

- API categorias: `GET /api/organizer/tournaments/{id}/categories` devuelve 405 en el ambiente actual, impidiendo validar update/delete por listado.
- Web delete torneo: no hay accion estable visible/testeable para eliminar torneo.
- Web edit categoria: no hay accion estable visible/testeable para editar categoria.
- Web delete categoria: no hay accion estable visible/testeable para eliminar categoria.
- Web edit pair: la accion detectada no abre formulario con inputs editables estables.
- Web delete pair: la accion detectada no remueve la pareja visible; queda xfail hasta confirmar contrato UI/backend.

## CRUD Cubierto

- API editar torneo.
- API eliminar torneo.
- API editar pareja.
- API eliminar pareja antes de sorteo.
- API eliminar torneo con datos asociados.
- Web editar torneo.

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
