# QA Strategy

## Alcance Actual

Prioridad progresiva:

1. Happy path estable.
2. Negativos simples.
3. Edge cases básicos.
4. Concurrencia simple.
5. Robustez y cleanup.

Fuera de alcance hasta tener datos QA controlados:

- Torneos complejos.
- Suscripciones reales.
- Caja completa.
- Multi-tenant avanzado.
- API happy paths complejos.

## Web

Los steps Allure representan acciones de negocio:

- Login exitoso.
- Reserva creada.
- Reserva visible en grilla.
- Reserva cancelada.
- Cancha eliminada.

No crear steps técnicos como click, fill, hover, scroll o wait.

Cada screenshot debe tomarse solo después de validar el estado final.

## API

Reporter simple:

- request sanitizado.
- response sanitizado.
- status code.
- payload sin secretos.

No imprimir ni adjuntar `QA_TOKEN`.

## QA API

Base:

`/api/qa`

Auth:

Header `X-QA-Token` desde `.env`.

Reglas:

- No hardcodear tokens.
- No mutar DB directo.
- DB read-only solo para diagnóstico.
