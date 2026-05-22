# Test Data Strategy

## IDs QA Base

- `tenant_id`: `9001`
- `court_id`: `9001`
- `customer_clean_id`: `9003`

## Factories

Usar `utils/qa_factories.py`:

- `create_booking_payload()`
- `create_customer_payload()`
- `create_payment_payload()`
- `booking_time_generator()`
- `future_date_generator()`

## Cleanup Policy

Usar `/reset` solo al inicio de una suite QA controlada.

Usar `/cleanup/bookings` para limpiar reservas creadas por un test puntual.

Usar `/reset-customer/{id}` para tests que consumen límites por cliente, como:

- slot ocupado.
- race condition.
- no-show futuro.
- máximo de reservas activas.

## Datos Dedicados

Preferir customers QA dedicados por tipo de test:

- customer limpio para creación simple.
- customer aislado para concurrencia.
- customer con límites preconfigurados para reglas de negocio.

## Pendiente

Activar tests dependientes cuando exista `QA_TOKEN` y `/test-data` confirme payloads vigentes.
