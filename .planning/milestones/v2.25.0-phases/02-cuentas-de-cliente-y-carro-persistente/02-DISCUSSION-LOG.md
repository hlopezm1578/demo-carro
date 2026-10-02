# Phase 2: Cuentas de cliente y carro persistente - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-29
**Phase:** 2-Cuentas de cliente y carro persistente
**Areas discussed:** Sesión JWT, Cuenta admin, Carro: datos y UX, Checkout fase 2

---

## Sesión JWT

### ¿Arquitectura del token: uno solo de larga vida, o par access + refresh?

| Option | Description | Selected |
|--------|-------------|----------|
| Token único (Recomendado) | Un access token de larga vida que la SPA guarda y manda como Authorization: Bearer. Un solo endpoint de login, sin estado extra — suficiente para una tienda demo. | ✓ |
| Access + refresh | Access corto (15-30 min) + endpoint /refresh. Más fiel a producción, pero agrega endpoint y flujo de renovación que la fase 3 no necesita. | |

**User's choice:** Token único (Recomendado)

### ¿Cuánto dura el access token (claim exp)?

| Option | Description | Selected |
|--------|-------------|----------|
| 7 días (Recomendado) | Sesión cómoda para una tienda; el claim exp se lee claro en jwt.io durante la mini-verificación. | ✓ |
| 1 hora | Expira rápido y obliga a ver el flujo 401 → login varias veces; bueno para demostrar expiración, molesto para el UAT. | |
| 8 horas | Compromiso de jornada. | |

**User's choice:** 7 días (Recomendado)

### ¿Dónde guarda la SPA el token de sesión?

| Option | Description | Selected |
|--------|-------------|----------|
| localStorage (Recomendado) | Store de auth Zustand con middleware persist: sobrevive recargas, cierre de pestaña y los full-page loads de Webpay. El ADR deja dicha la desventaja honesta (XSS). | ✓ |
| sessionStorage | Sobrevive recargas pero muere al cerrar la pestaña — AUTH-02 queda a medias. | |
| Memoria + re-hidratación | Store en memoria re-hidratado al arrancar — más capas sin beneficio sin refresh tokens. | |

**User's choice:** localStorage (Recomendado)

### ¿Qué hace la SPA cuando el token expira (401)?

| Option | Description | Selected |
|--------|-------------|----------|
| Interceptor 401 → login (Recomendado) | lib/api.ts detecta 401, limpia sesión, redirige a /login con "Tu sesión expiró". Se enseña una vez y las fases 3-4 lo heredan. | ✓ |
| Error por pantalla | Cada pantalla muestra el error y la clienta navega a mano — repite manejo de error en cada feature. | |

**User's choice:** Interceptor 401 → login (Recomendado)

---

## Cuenta admin

### ¿Cómo nace el usuario con rol admin?

| Option | Description | Selected |
|--------|-------------|----------|
| Seed + ADMIN_* env (Recomendado) | La siembra idempotente crea/actualiza el admin leyendo ADMIN_EMAIL/ADMIN_PASSWORD del .env — mismo patrón upsert de los 12 SKU, enseña secretos por variable de entorno. | ✓ |
| Credenciales fijas en seed | admin@maura.cl con contraseña demo escrita en la guía — planta un secreto en el código, mal hábito. | |
| Primer registrado = admin | Cero configuración, pero mágico y peligroso al desplegar en fase 5. | |

**User's choice:** Seed + ADMIN_* env (Recomendado)

### ¿La siembra crea también una clienta demo, o solo el admin?

| Option | Description | Selected |
|--------|-------------|----------|
| Admin + clienta demo (Recomendado) | CLIENTE_EMAIL/CLIENTE_PASSWORD con rol cliente: la guía verifica login de ambos roles sin registro previo y el UAT tiene cuentas predecibles. | ✓ |
| Solo admin | La clienta la registra el alumno en la guía — un paso más manual en cada re-verificación. | |

**User's choice:** Admin + clienta demo (Recomendado)

### ¿Qué reglas de contraseña enseña la guía para el registro?

| Option | Description | Selected |
|--------|-------------|----------|
| Largo mínimo 8 (Recomendado) | Sin exigencias de mayúsculas/símbolos — recomendación moderna (NIST), igual que el tutorial oficial de FastAPI. | ✓ |
| Complejidad clásica | 8 + mayúscula + número — familiar, pero enseña la regla que las guías actuales descartaron. | |

**User's choice:** Largo mínimo 8 (Recomendado)

### ¿Cómo maneja el backend emails duplicados en registro y credenciales erróneas en login?

| Option | Description | Selected |
|--------|-------------|----------|
| 409 registro / 401 genérico (Recomendado) | Registro duplicado → 409 claro; login fallido → 401 genérico sin revelar si el email existe. Asimetría deliberada, explicada en la guía. | ✓ |
| Genérico en ambos | Máxima anti-enumeración — patrón de producción con envío de emails que esta guía sin correo no puede cumplir de verdad. | |

**User's choice:** 409 registro / 401 genérico (Recomendado)

---

## Carro: datos y UX

### ¿Qué estructura guarda el carro en localStorage?

| Option | Description | Selected |
|--------|-------------|----------|
| Solo ids + cantidad (Recomendado) | [{producto_id, cantidad}]; la vista se hidrata desde la API — precio siempre vigente, prepara CART-03. | ✓ |
| Snapshot con precio | Render instantáneo sin red, pero el precio puede quedar viejo — staleness que fase 3 corrige de todos modos. | |

**User's choice:** Solo ids + cantidad (Recomendado)

### ¿Qué forma tiene la UI del carro?

| Option | Description | Selected |
|--------|-------------|----------|
| Página /carro + badge (Recomendado) | Ruta /carro con edición, vaciar y CTA; icono con contador en navbar. Mobile-first, sin estado de drawer. | ✓ |
| Drawer (mini-cart) | Abre al agregar sin salir del catálogo — más lógica de overlay que compite con el contenido pedagógico. | |
| Ambos | Badge + drawer + página: experiencia de tienda real al costo de guiar dos componentes donde uno enseña lo mismo. | |

**User's choice:** Página /carro + badge (Recomendado)

### ¿Dónde vive el botón "Agregar al carro"?

| Option | Description | Selected |
|--------|-------------|----------|
| Solo en la ficha (Recomendado) | La ficha es donde hay stock visible y se decide la compra; la grilla queda limpia como en la fase 1. | ✓ |
| Ficha + catálogo | Agregar en un clic desde la grilla — recarga las tarjetas y agrega el caso borde de agregar sin ver el stock. | |

**User's choice:** Solo en la ficha (Recomendado)

### ¿Las cantidades del carro se limitan al stock visible en fase 2?

| Option | Description | Selected |
|--------|-------------|----------|
| Tope = stock vigente (Recomendado) | Ficha y carro limitan al stock de la hidratación; CART-03 queda como segunda barrera en fase 3, no como único muro. | ✓ |
| Sin tope hasta fase 3 | El alumno experimenta primero la sobreventa que la solución enseña a evitar. | |

**User's choice:** Tope = stock vigente (Recomendado)

---

## Checkout fase 2

### ¿Qué muestra la ruta protegida /checkout mientras llega Webpay en fase 3?

| Option | Description | Selected |
|--------|-------------|----------|
| Resumen del pedido (Recomendado) | Líneas, cantidades, subtotal y total hidratado, CTA deshabilitado con nota "el pago llega en la etapa siguiente". Fase 3 solo agrega Webpay. | ✓ |
| Guard mínimo | El botón solo demuestra login → vuelta, sin página propia — fase 3 arranca la pantalla desde cero. | |

**User's choice:** Resumen del pedido (Recomendado)

### ¿Cómo vuelve el usuario al checkout tras iniciar sesión?

| Option | Description | Selected |
|--------|-------------|----------|
| returnTo genérico (Recomendado) | El guard guarda la ruta destino y el login devuelve a ella — patrón enseñado una vez, reutilizado por el panel admin de fase 4. | ✓ |
| Destino fijo | Login siempre aterriza en la home y se redirige una segunda vez — el usuario pierde contexto y el patrón se re-escribe en fase 4. | |

**User's choice:** returnTo genérico (Recomendado)

### ¿Qué superficie admin protegida construye la fase 2 para verificar AUTH-03?

| Option | Description | Selected |
|--------|-------------|----------|
| Endpoint demo mínimo (Recomendado) | /api/admin/estado con conteos triviales, protegido por rol: 403 verificable para la clienta sin adelantar el panel de fase 4. | ✓ |
| Solo claim, sin endpoint | El rol viaja en el token pero no hay dónde probarlo — AUTH-03 queda verificado solo por inspección. | |

**User's choice:** Endpoint demo mínimo (Recomendado)

---

## Claude's Discretion

- Claims exactos del token y forma del login (OAuth2 form-encoded vs JSON) — resolver contra el tutorial oficial de FastAPI.
- Nombres/estructura exacta de endpoints nuevos en `contrato_api.yaml`.
- Qué ADRs escribe la fase (desde ADR-009) y numeración RF/HU/RN nueva en `02_requerimientos.md`.
- Partición en sub-guías `guia-05+`, copy de pantallas y estados vacíos (bajo los tokens de `01-UI-SPEC.md`).
- Integración del estado de sesión en el navbar y valores demo del `.env.example`.

## Deferred Ideas

None — discussion stayed within phase scope
