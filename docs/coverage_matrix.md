# Coverage Matrix

Estado base: QA layer `13 passed`, `1 skipped`; Allure API limpio; Bot WhatsApp fuera de alcance.

| Modulo | Endpoint/flujo | Tipo | Prioridad | Test existente | Estado | Motivo | Proximo paso |
|---|---|---:|---:|---|---|---|---|
| Auth | Login API exitoso | api real | CRIT | `tests/api/test_api_auth.py::test_api_login_success` | covered | Valida token de API real | Mantener smoke |
| Auth | Login API invalido | api real | HIGH | `tests/api/test_api_auth.py::test_api_login_invalid_credentials` | covered | Valida rechazo 401 | Mantener regression |
| Auth | Login web super admin | web | CRIT | `tests/web/test_web_login.py::test_web_login_super_admin` | covered | Login UI basico | Mantener smoke |
| Auth | Login web invalido | web | HIGH | `tests/web/test_auth_negatives.py::test_invalid_login` | covered | Rechazo UI validado | Mantener regression |
| Reservas | QA test-data | qa layer | CRIT | `tests/api/test_api_qa_layer.py::test_qa_layer_test_data` | covered | Datos QA disponibles | Base para nuevos tests |
| Reservas | QA crear reserva | qa layer | CRIT | `tests/api/test_api_qa_layer.py::test_qa_layer_create_booking` | covered | Crea reserva QA con customer limpio | Reusar factory |
| Reservas | QA pago de reserva | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_booking_payment` | covered | Pago aprobado via QA | Expandir validaciones despues |
| Reservas | QA mover reserva a pasado | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_move_booking_to_past` | covered | Estado temporal controlado | Usar para no-show |
| Reservas | QA mover reserva a futuro | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_move_booking_to_future` | covered | Estado temporal controlado | Usar para no-show futuro |
| Reservas | QA cambiar estado de reserva | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_booking_state` | covered | State helper responde OK | Definir estados soportados |
| Reservas | QA cleanup bookings | qa layer | CRIT | `tests/api/test_api_qa_layer.py::test_qa_layer_cleanup_bookings` | skipped | FK `invoices_booking_id_fkey` | Backend debe corregir cleanup |
| Reservas | API real crear reserva tenant activo | api real | CRIT | `tests/api/test_api_bookings.py::test_api_create_booking_active_tenant` | skipped | `POST /api/bookings` timeoutea | Backend debe responder o error controlado |
| Reservas | API real tenant vencido bloquea reserva | api real | HIGH | `tests/api/test_api_bookings.py::test_api_create_booking_expired_tenant_blocked` | blocked | Data inconsistente: `courtId=9001` no existe en tenant `4` | Pedir court valido para tenant vencido |
| Reservas | Web crear reserva simple | web | CRIT | `tests/web/test_create_booking.py::test_create_simple_booking_smoke` | skipped | Web submit depende de `POST /api/bookings`, queda colgado | Desbloquear endpoint normal |
| Reservas | Web detalle desde grilla | web | HIGH | `tests/web/test_view_booking_actions.py::test_view_booking_from_grid_actions` | covered | Abre detalle existente | Mantener smoke |
| Reservas | Web slot ocupado | web | HIGH | `tests/web/test_booking_negatives.py::test_create_booking_occupied_slot` | skipped | Web create bloqueado por endpoint normal | Desbloquear endpoint normal |
| Reservas | Web no-show futuro | web | HIGH | `tests/web/test_booking_negatives.py::test_no_show_future_blocked` | skipped | Web create bloqueado por endpoint normal | Desbloquear endpoint normal |
| Reservas | Web race condition mismo slot | web | HIGH | `tests/web/test_booking_race_condition.py::test_booking_race_condition` | skipped | Web create bloqueado por endpoint normal | Desbloquear endpoint normal |
| Caja | API resumen reservas caja | api real | HIGH | `tests/api/test_api_cash.py::test_api_cash_bookings_summary` | covered | Endpoint responde 200 | Agregar asserts de contrato |
| Caja | QA reset caja por dia | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_cash_reset_day` | covered | Reset puntual funciona con fecha | Usar antes de cash tests |
| Roles/permisos | QA users | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_users` | covered | Lista usuarios QA | Usar para permisos |
| Roles/permisos | Web staff no ve acciones owner criticas | web | HIGH | `tests/web/test_staff_permissions.py::test_staff_permissions_basic` | skipped | Falta password staff en data segura | Pedir password o login helper QA |
| Suscripciones/planes | QA cambiar plan tenant 9001 | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_tenant_change_plan` | covered | Change plan responde OK | Validar efecto visible luego |
| Suscripciones/planes | QA restaurar plan tenant 9001 | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_tenant_restore_plan` | covered | Restore plan responde OK | Usar en cleanup |
| Suscripciones/planes | API tenant vencido | api real | HIGH | `tests/api/test_api_bookings.py::test_api_create_booking_expired_tenant_blocked` | blocked | Falta data coherente de tenant vencido | Pedir tenant/court/customer vencidos |
| Multi-tenant | QA tenants | qa layer | HIGH | `tests/api/test_api_qa_layer.py::test_qa_layer_tenants` | covered | Lista tenants QA | Base para aislamiento |
| Multi-tenant | QA tenant switch data | qa layer | MID | `tests/api/test_api_qa_layer.py::test_qa_layer_tenant_switch_data` | covered | Datos de switch disponibles | Crear tests de aislamiento despues |
| Multi-tenant | Aislamiento real entre tenants | api real | HIGH | N/A | pending | No hay test real aun | Definir tenants y datos esperados |
| Customers | QA reset customer 9003 | qa layer | CRIT | `tests/api/test_api_qa_layer.py::test_qa_layer_reset_customer` | covered | Cleanup puntual funciona | Usar como cleanup principal |
| Customers | CRUD/API customers real | api real | MID | N/A | pending | No hay cliente API dedicado | Relevar endpoints reales |
| Customers | Web customers | web | MID | N/A | pending | No hay test web customers | Definir flujo minimo |
| Torneos | API/Web torneos | web/api real | MID | N/A | pending | Fuera de etapa actual | Pedir datos QA de torneos |
| Reports/predictivo/marketing | Reports | web/api real | LOW | N/A | pending | Sin endpoints/fixtures relevados | Relevar contrato |
| Reports/predictivo/marketing | Predictivo | web/api real | LOW | N/A | pending | Sin endpoints/fixtures relevados | Relevar contrato |
| Reports/predictivo/marketing | Marketing | web/api real | LOW | N/A | pending | Sin endpoints/fixtures relevados | Relevar contrato |
| Web smoke/funcional | Crear cancha | web | HIGH | `tests/web/test_create_court.py::test_create_court` | covered | Crea y elimina cancha | Mantener cleanup |
| Web smoke/funcional | Login home | web | CRIT | `tests/web/test_web_login.py::test_web_login_super_admin` | covered | Login basico | Mantener smoke |
| Web smoke/funcional | Reserva detalle | web | HIGH | `tests/web/test_view_booking_actions.py::test_view_booking_from_grid_actions` | covered | Modal detalle visible | Agregar asserts si cambia UI |

## Cubierto

- Auth API y Web basico.
- QA layer principal para tenants, users, test-data, customer reset, bookings, payments, state, move past/future, cash reset, plan change/restore y tenant-switch-data.
- Caja API resumen basico.
- Web smoke de login, cancha y detalle de reserva.
- Allure API centralizado, sin secretos y sin duplicados.

## Falta Automatizar

- CRUD real de customers.
- Multi-tenant real con aislamiento.
- Suscripcion vencida con data coherente.
- Caja completa: pagos, cierres, filtros y totales.
- Torneos basicos cuando haya datos QA.
- Reports, predictivo y marketing.
- Web customers y permisos completos.

## Bloqueado Por Backend/Data

- `POST /api/qa/cleanup/bookings`: FK `invoices_booking_id_fkey`.
- `POST /api/qa/reset`: FK `invoices_booking_id_fkey`.
- `POST /api/bookings`: `ReadTimeout`.
- Tenant vencido: `courtId=9001` no existe para tenant `4`.
- Staff web: falta password seguro para `qa-staff@botturnos.test`.

## Proximos 5 Tests Recomendados

1. API real: booking activo cuando `POST /api/bookings` deje de timeoutear.
2. API real: tenant vencido con `tenant_id`, `court_id` y customer coherentes.
3. API cash: resumen despues de crear booking y payment por QA layer.
4. Web staff permissions con password staff disponible.
5. API customers: reset/customer + lectura/validacion de customer limpio.

## Pedidos Minimos Para Companero

- Corregir FK en `/api/qa/reset` y `/api/qa/cleanup/bookings`.
- Corregir timeout de `POST /api/bookings`.
- Pasar `courtId` valido para tenant vencido `4`, o nuevo tenant vencido QA completo.
- Pasar password seguro para `qa-staff@botturnos.test` via `.env` o test data protegido.
- Confirmar endpoints reales de customers, torneos, reports, predictivo y marketing.
