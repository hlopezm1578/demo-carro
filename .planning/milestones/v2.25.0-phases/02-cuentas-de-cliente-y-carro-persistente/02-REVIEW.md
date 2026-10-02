---
phase: 02-cuentas-de-cliente-y-carro-persistente
reviewed: 2026-09-29T21:10:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - docs/04_arquitectura/contrato_api.yaml
  - docs/04_arquitectura/adr/009-jwt-larga-vida-localstorage.md
  - docs/04_arquitectura/adr/010-carro-client-side.md
  - docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md
  - docs/04_arquitectura/README.md
  - docs/02_requerimientos.md
  - docs/03_diseno.md
  - docs/05_desarrollo/guia-05-cuentas-backend.md
  - docs/05_desarrollo/guia-06-sesion-frontend.md
  - docs/05_desarrollo/guia-07-carro.md
  - docs/05_desarrollo/guia-08-checkout.md
  - docs/05_desarrollo/README.md
  - docs/README.md
  - README.md
  - docs/05_desarrollo/guia-04-catalogo.md
findings:
  critical: 1
  warning: 7
  info: 7
  total: 15
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-09-29T21:10:00Z
**Depth:** standard
**Files Reviewed:** 15 (contrato, 3 ADRs, READMEs de arquitectura/docs/raíz, requerimientos, diseño, guías 5-8, línea "Siguiente" de guia-04)
**Status:** issues_found

## Summary

Revisión adversarial de los 15 archivos de la fase 2 (guía-only, D-17): el contrato 0.2.0, los ADRs 009-011, las extensiones de requerimientos/diseño, las guías 5-8 y los índices de estado. El estándar aplicado es el del propio repo: los bloques de código de las guías SON el producto y se revisan como código (trazabilidad RF/HU/RN/ADR/D, copies locked, veracidad técnica de lo enseñado).

**Lo verificado sin hallazgos:** las mitigaciones de los threat models de los 5 planes aterrizaron todas — 401 genérico + hash dummy anti-enumeración por tiempo (T-02-07, guia-05 paso 7), `UsuarioPublico` sin `hashed_password` en ninguna frontera (T-02-08, contrato + schemas + `response_model`), secretos solo por `.env` con placeholders en el `.env.example` y fail-fast sin defaults (T-02-09), rol validado en el servidor con 403 verificable (T-02-10), carro sin precios jamás (T-02-12), guard vendido como UX y no como seguridad (T-02-13), cantidades tapadas al stock en pantalla (T-02-14), XSS de localStorage declarado como costo en ADR-009 (T-02-04) e invariant guide-only intacto (T-02-17: sin `backend/` ni `frontend/` en el repo). El orden de `verify(password, hash)` de pwdlib es correcto en las tres apariciones (helper, servicio, sección de errores); `algorithms=["HS256"]` explícito; `exp`/`iat` timezone-aware con `sub` string; el enum `RolUsuario` con nombre==valor; CORS creciendo a `["GET","POST"]` con preflight verificado; el `partialize` de Zustand en ambos stores; el `String(id)` del `queryKey` compartido ficha↔carro↔checkout; la hidratación tolerante al 404 con fila degradada; el returnTo genérico `state.from` sin hardcodeo; la numeración RF-06..RF-11 / RN-05..RN-09 / HU-05..HU-08 / RNF-05..06 continua y trazada en §13; los READMEs dicen la verdad (8 guías, 11 ADRs, contrato 0.2.0). Los ejemplos de stock/precio citados en las guías (Brisa de Naranja stock 14, Rosa de Río stock 2, $6.990–$12.990) calzan con el seed de la fase 1.

**Problemas:** 1 critical y 7 warnings. El critical rompe el arranque del backend que la guía enseña: los routers de guia-05 importan `Error` desde `app.schemas.usuario`, pero ese módulo (creado en el paso 4 de la propia guía) no define ni re-exporta `Error` — vive en `app/schemas/producto.py` desde la guia-04; el `include_router` revienta con `ImportError` y los pasos 8-11 de guia-05 más todo el flujo de las guías 6-8 quedan bloqueados. Los warnings: un total aritmético erróneo ($26.980; el correcto es $26.970) repetido en 4 lugares como valor esperado de mini-verificaciones; el interceptor 401 puede disparar dentro del propio login en un caso de borde que la guía declara imposible; el diseño afirma que la cantidad guardada "se ajusta sola" al stock y la implementación nunca la corrige (con el badge del navbar contando unidades sin tapar); el `lib/api.ts` rehecho perpetúa el WR-04 abierto de la fase 1 (detail-array del 422); el contrato documenta el 422 del registro con el schema `Error` de detail-string (re-anclaje del WR-02 abierto); un bloque "agrega" de guia-07 re-lista hooks ya existentes y produce redeclaración TS al copiarlo; y un conteo de paths contradictorio (8 vs 7) entre guia-05 y guia-08.

---

## Critical Issues

### CR-01: Los routers de guia-05 importan `Error` desde `app.schemas.usuario` — ese módulo no define `Error`: la API no arranca

**File:** `docs/05_desarrollo/guia-05-cuentas-backend.md:608` (routers/auth.py) y `docs/05_desarrollo/guia-05-cuentas-backend.md:705` (routers/admin.py); el módulo incompleto se crea en `guia-05:241-278` (paso 4) y la única definición existente de `Error` vive en `app/schemas/producto.py` (`guia-04-catalogo.md:81`)
**Issue:** El paso 8 enseña `from app.schemas.usuario import Error, RegistroCreate, Token, UsuarioPublico` (línea 608) y `from app.schemas.usuario import Error` (línea 705). Pero el `schemas/usuario.py` que el paso 4 construye define solo `RegistroCreate`, `UsuarioPublico` y `Token` — ni clase `Error` ni re-export. `Error` existe únicamente en `app/schemas/producto.py` (guia-04, paso 1). Al seguir la guía, el alumno copia los routers, registra `app.include_router(auth.router)` y la aplicación muere al importar con `ImportError: cannot import name 'Error' from 'app.schemas.usuario'`. Consecuencia en cascada: fallan las mini-verificaciones de los pasos 8 y 9, el seed del paso 10 no puede correr contra una API caída… en realidad el seed sí corre (no importa los routers), pero los pasos 11, toda la guía 6 (login/registro contra la API), la 7 y la 8 quedan inoperables. Es exactamente el tipo de defecto que el UAT delegado en `maura-uat` debería haber atrapado; si allá se corrigió localmente sin tocar la guía, el defecto sigue vivo para el alumno (regla de AGENTS.md: fix en los dos lugares).
**Fix:** Corregir el import en ambos routers de la guía 5 para traer `Error` desde su módulo real (opción mínima):
```python
from app.schemas.producto import Error
from app.schemas.usuario import RegistroCreate, Token, UsuarioPublico
```
o, más limpio a largo plazo (los ADRs 009-011 sumarán más errores de auth): mover `Error` a un módulo común (`app/schemas/comun.py`) y actualizar las guías 4 y 5 para importarlo desde ahí — dejando dicho en el prose por qué un schema de error no pertenece a un dominio de negocio.

---

## Warnings

### WR-01: El total de ejemplo es aritméticamente erróneo — $26.980 donde la suma real es $26.970 — y es el valor esperado de dos mini-verificaciones

**File:** `docs/03_diseno.md:613` y `docs/03_diseno.md:656` (wireframes de carro y checkout); `docs/05_desarrollo/guia-07-carro.md:583` y `docs/05_desarrollo/guia-08-checkout.md:324` (mini-verificaciones)
**Issue:** Las líneas de los ejemplos son 2 × Brisa de Naranja ($7.990 → $15.980, correcto) + 1 × Rosa de Río ($10.990, correcto). La suma es $26.970, pero los cuatro lugares imprimen `Total $26.980`. La guia-07 ordena "compárala a mano: 2 × $7.990 + 1 × $10.990 = $26.980" y la guia-8 exige que el total del checkout calce con el del carro "al peso (… = $26.980 en ambos lados)": la app correcta del alumno mostrará $26.970 en ambas pantallas y no calzará con el número de la guía — el alumno concluirá que su hidratación o su `Math.min` está mal y "corregirá" código sano. La regla del alumno #1 (no saltarse mini-verificaciones) convierte este typo numérico en un bloqueo didáctico.
**Fix:** Reemplazar `$26.980` por `$26.970` en los cuatro lugares (`03_diseno.md:613`, `03_diseno.md:656`, `guia-07:583`, `guia-08:324`). Verificar de paso que ningún otro total derivado del seed arrastra el mismo cálculo.

### WR-02: El interceptor 401 sí puede disparar dentro del propio login — la inmunidad prometida (Pitfall 5 / T-02-11) no está garantizada por el código

**File:** `docs/05_desarrollo/guia-06-sesion-frontend.md:230` (`if (res.status === 401 && token)`) con el flujo de `Login.tsx` en `guia-06:375-380` y `guia-06:429-431`; la invariant declarada está en `guia-06:189-196` y `guia-06:876-879`
**Issue:** La guía afirma: "El login se envía sin token (la pantalla redirige si ya hay sesión, paso 6), así que su 401 nunca lleva Bearer y nunca entra acá". Eso solo es cierto si el formulario del login nunca se muestra con un token en el store — pero `Login.tsx` muestra el formulario cuando `verificar` falla por **error de red** (comentario de la propia guía, líneas 429-431: "Error de red — backend caído: mostramos el formulario, sin pérdida"), y en ese estado el token sigue en el store. Si el alumno envía entonces credenciales incorrectas (backend ya recuperado), `pedir()` adjunta el Bearer del token viejo, la API responde 401 por credenciales incorrectas, y `res.status === 401 && token` es verdadero: el interceptor borra la sesión y expulsa a `/login?expirada=1` con el aviso ámbar "Tu sesión expiró…" — exactamente el comportamiento que el Pitfall 5 y la mitigación T-02-11 ("no dispara en el propio login") declaran imposible. La protección descansa en un invariant de estado de UI que el código no garantiza.
**Fix:** Hacer verdadero el invariant en `lib/api.ts` en vez de confiar en el estado de la pantalla: que `apiPostForm` (o un flag de `pedir`) no adjunte nunca `Authorization` para el login — p. ej. `pedir<T>(ruta, init, { sinAuth: true })` usado por `apiPostForm`, o `headers.delete("Authorization")` dentro de `apiPostForm`. Alternativa: en `Login.tsx`, si `verificar` falla por red, llamar `cerrarSesion()` antes de mostrar el formulario. Ajustar el prose para describir la garantía real elegida.

### WR-03: El diseño afirma que la cantidad guardada "se ajusta sola" al stock — la implementación nunca la corrige y el badge del navbar cuenta unidades sin tapar

**File:** `docs/03_diseno.md:139-142` (decisión 10 de §2.3) y `docs/03_diseno.md:621-624` (§4.7 pantalla 6); implementación en `docs/05_desarrollo/guia-07-carro.md:291-293` (solo display `Math.min`) y `docs/05_desarrollo/guia-07-carro.md:676-679` (badge reduce sobre `i.cantidad`)
**Issue:** Dos pasajes del diseño prometen ajuste persistido: "el carro ajusta la cantidad guardada si el stock bajó mientras el aroma esperaba" (§2.3.10) y "la cantidad guardada se ajusta sola si el stock bajó" (§4.7). La guia-07 implementa solo el tapado **en pantalla** (`enPantalla = Math.min(cantidad, stock)`) — el store conserva la cantidad vieja indefinidamente (la propia mini-verificación del paso 8 lo demuestra: editan a mano 5, recargan, la fila muestra 2… y `maura-carro` sigue valiendo 5). Consecuencia visible de la divergencia: el badge del navbar reduce las cantidades **guardadas** (5), mientras la fila y el total cobran la tapada (2) — dos números de "cuánto llevo" que se contradicen en la misma pantalla. El ADR-010 dice "se tapan al stock vigente en pantalla" (correcto con la implementación); son los dos pasajes de `03_diseno` los que sobreprometen, y el badge queda del lado inconsistente en cualquier lectura.
**Fix:** Elegir un lado y alinear los tres puntos: (a) hacer verdad el diseño con write-back — al hidratar `/carro`, si `cantidad > stock`, llamar `cambiarCantidad(producto_id, stock)` (el badge y el store quedan consistentes con lo mostrado), o (b) corregir los dos pasajes de `03_diseno` a "la cantidad **mostrada** se tapa al stock; la guardada se corrige al editar o al confirmar la compra (etapa 3)". En ambos casos, el badge debe contar la misma cantidad que la pantalla muestra.

### WR-04: El `lib/api.ts` rehecho por la guia-06 perpetúa el defecto abierto WR-04 de la fase 1 — el `detail` array del 422 asignado a un string

**File:** `docs/05_desarrollo/guia-06-sesion-frontend.md:234-241` (bloque "Reemplaza `lib/api.ts` completo"); alcanzable ahora también desde el 422 del registro (`guia-05:620-625`)
**Issue:** La guia-06 reemplaza `lib/api.ts` completo y conserva verbatim `if (cuerpo?.detail) mensaje = cuerpo.detail;` — el defecto registrado como WR-04 y aún `open` en `01-REVIEW-DISPOSITION.md`: el 422 real de FastAPI trae `detail` como **array** de objetos, la asignación degrada `mensaje` a array y `new ApiError(mensaje, …)` coerciona a `"[object Object]"`. Era el momento natural de cerrarlo (reescritura completa del archivo) y no se cerró; además la fase añade un camino nuevo hasta él (registro con contraseña de 7 caracteres → 422 con detail-array). Hoy ninguna pantalla nueva muestra `ApiError.message` (usan copies fijas por status), pero el patrón queda enseñado por segunda vez como si fuera correcto y las fases 3-4 lo heredarán.
**Fix:** Aplicar la normalización en el `pedir()` de la guia-06 (y dejarla como lección: "el detail puede ser string o array según el código de error"):
```typescript
const cuerpo = await res.json();
const detalle = cuerpo?.detail;
if (typeof detalle === "string") mensaje = detalle;
else if (Array.isArray(detalle) && detalle[0]?.msg) mensaje = detalle[0].msg;
```

### WR-05: El contrato y la guia-05 documentan el 422 del registro con el schema `Error` (`detail` string) — el 422 real trae `detail` como array (re-anclaje del WR-02 abierto)

**File:** `docs/04_arquitectura/contrato_api.yaml:304-309` (422 del registro referenciando `Error`); `docs/05_desarrollo/guia-05-cuentas-backend.md:620-625` (`responses={…, 422: {"model": Error}}`)
**Issue:** El contrato declara el 422 de `/api/auth/registro` con el schema `Error` (`detail: string`), y la guia-05 declara `422: {"model": Error}` en la firma — con lo cual `/docs` muestra el 422 con forma `Error` y la fila 12 de la Gran verificación (contrato ↔ `/docs`) pasa sin detectar nada. Pero el cuerpo 422 real que FastAPI produce es `{"detail": [{loc, msg, type}, …]}`: la documentación que la fase consagra como "fuente de la verdad" describe mal el cuerpo real del error más frecuente del endpoint (contraseña corta, email mal formado). Es el mismo defecto del WR-02 de fase 1 (open), ahora extendido al endpoint nuevo de la fase.
**Fix:** La opción barata y honesta: nota de desvío conocido en el prose de guia-05 paso 8 ("el 422 real trae `detail` como array de validación; el contrato lo simplifica como `Error` — desvío documentado"). La opción correcta: versionar el contrato con un schema `ValidationError` (`detail` como array de `{loc, msg, type}`) para las 422 y referenciarlo desde todos los 422 (productos y registro).

### WR-06: El bloque "agrega" de guia-07 paso 2 re-lista hooks que ya existen en `FichaProducto` — copiarlo tal cual produce error de redeclaración de TypeScript

**File:** `docs/05_desarrollo/guia-07-carro.md:150-161` (bloque del paso 2); los hooks preexistentes en `docs/05_desarrollo/guia-04-catalogo.md:815-816`
**Issue:** El paso 2 instruye "Dentro del componente, junto a los otros hooks (arriba, antes de los `return`…):" y muestra un bloque de 5 líneas donde las dos primeras — `const { id } = useParams();` y `const navigate = useNavigate();` — son los hooks **ya existentes** de la ficha de la guia-04 (líneas 815-816), no líneas nuevas. Solo `agregar`, `productoId` y `enCarro` son adiciones. El alumno que copia el bloque completo (el gesto que toda la serie enseña) obtiene `Cannot redeclare block-scoped variable 'id'`/`'navigate'` y un build roto, sin que la guía le advierta cuáles líneas son contexto y cuáles código nuevo. Las demás guías de la fase marcan la diferencia correctamente (p. ej. "agrega el import junto a los existentes" mostrando solo lo nuevo).
**Fix:** Reducir el bloque a las tres líneas nuevas y dejar las existentes como referencia textual: "(debajo de los `useParams`/`useNavigate` que ya tienes desde la guia-4, agrega:)" seguido de `const agregar…`, `const productoId…`, `const enCarro…`.

### WR-07: Conteo de paths contradictorio — guia-05 habla de "los 8 paths" y el contrato/guia-08 de 7

**File:** `docs/05_desarrollo/guia-05-cuentas-backend.md:1057` ("los 8 paths") vs `docs/05_desarrollo/guia-08-checkout.md:383` ("los 7 paths") y el contrato real (7 `paths:`: salud, productos, productos/{id}, registro, login, perfil, admin/estado)
**Issue:** El paréntesis de cierre de guia-05 anuncia la Gran verificación final como "la comparación completa contrato ↔ `/docs` — los 8 paths, tags y schemas". El contrato 0.2.0 define 7 paths y la fila 12 de guia-08 manda a comparar "los 7 paths". El alumno que haga el cierre contando encontrará 7 y un número distinto citado por la guía anterior — ruido de desconfianza en el mecanismo que la fase usa como evidencia formal de cierre (ADR-007).
**Fix:** Corregir `guia-05:1057` a "los 7 paths". De paso, `guia-05:762` dice "los 4 paths del contrato 0.2.0" refiriéndose a los 4 **nuevos** — conviene "los 4 paths nuevos del contrato 0.2.0" para no sumar ambigüedad.

---

## Info

### IN-01: Comentarios que referencian `authHeaders()` — una función que no existe en el código enseñado

**File:** `docs/05_desarrollo/guia-06-sesion-frontend.md:332` (prose del paso 6) y `docs/05_desarrollo/guia-06-sesion-frontend.md:389` (comentario dentro de `Login.tsx`)
**Issue:** "el token entra al store PRIMERO (para que `authHeaders()` ya pueda adjuntarlo)" y el comentario "// Token primero: desde esta línea authHeaders() ya lo adjunta." citan un helper `authHeaders()` que vivía en el Pattern 4 de `02-RESEARCH.md` pero que el `lib/api.ts` final no define (el token se adjunta inline en `pedir()` con `useAuthStore.getState()`). El alumno buscará `authHeaders()` y no la encontrará.
**Fix:** Reemplazar ambas referencias por el mecanismo real: "para que `pedir()` ya pueda adjuntarlo" / "// desde esta línea, `pedir()` encuentra el token en el store".

### IN-02: Typos que degradan el material dictado

**File:** `docs/05_desarrollo/guia-05-cuentas-backend.md:153` ("la app se nieza a partir" → "niega"), `guia-05:446` (comentario de código "Lista EXPLÍPITA" → "EXPLÍCITA" — queda dentro del archivo que el alumno copia), `guia-05:778` ("la consuela muestra" → "la consola"), `docs/05_desarrollo/guia-07-carro.md:374` ("se revuelve volviendo a la ficha" → "se repone volviendo a la ficha")
**Issue:** Cuatro typos; uno de ellos viaja dentro de un bloque de código copiable.
**Fix:** Corrección directa en las cuatro líneas.

### IN-03: Snippets de rutas que re-listan rutas ya declaradas — duplicados silenciosos si se copian como "agregar"

**File:** `docs/05_desarrollo/guia-07-carro.md:603-609` (muestra `/login` y `/registro` junto a la nueva `/carro`) y `docs/05_desarrollo/guia-08-checkout.md:272-281` (muestra `/carro` y `*` junto al bloque `RequireAuth`)
**Issue:** Ambos pasos dicen "junto a las existentes" y muestran mezcladas líneas existentes y nuevas. React Router no falla con rutas duplicadas (gana la primera coincidencia), así que el resultado **funciona**, pero deja entradas muertas en el mapa de rutas y enseña una ambigüedad que WR-06 muestra sí rompe en su variante TypeScript.
**Fix:** Mostrar solo la línea nueva (o el bloque nuevo) y nombrar textualmente dónde va, como hace guia-06 paso 9 con el listado completo de reemplazo.

### IN-04: RNF-06 nombra `localStorage` en el documento de requerimientos, que el propio diseño difiere a la fase 4

**File:** `docs/02_requerimientos.md:113` (RNF-06: "en el **propio navegador del cliente** (localStorage)") vs `docs/03_diseno.md:198-203` ("el mecanismo concreto (localStorage) se elige y documenta en la fase 4")
**Issue:** El doc 02 se autodefine como contrato de QUÉ "jamás de CÓMO" (nota final de §14), pero su RNF nuevo fija el mecanismo de almacenamiento, contradictoriamente con la nota del diseño que reserva esa decisión para la arquitectura. No produce bugs; sí debilita la lección de separación de fases que la serie enseña.
**Fix:** Redactar RNF-06 como "…persisten en el propio navegador del cliente, sin depender del servidor" y dejar `localStorage` donde ya está bien citado (ADR-009/010).

### IN-05: El índice del README de arquitectura cita ADRs que no tratan la decisión enlazada

**File:** `docs/04_arquitectura/README.md:116` (fila de `pwdlib[argon2]`: "decisión completa" enlazando a ADR-009 y ADR-011)
**Issue:** Ni ADR-009 ni ADR-011 mencionan pwdlib ni el hashing de contraseñas (verificado por grep: cero ocurrencias). El enlace de la columna "Por qué (decisión completa)" promete contenido que el ADR destino no tiene — pequeña mentira de trazabilidad en el repo cuya moneda es la trazabilidad.
**Fix:** Quitar el enlace de esa fila (la justificación real es el stack/tutorial oficial), o agregar una línea sobre el hashing al ADR-011 si se quiere mantener la cita.

### IN-06: El contrato declara `format: email` en el `username` del login — validación que el endpoint no aplica

**File:** `docs/04_arquitectura/contrato_api.yaml:329-333`
**Issue:** `username` lleva `format: email`, pero `OAuth2PasswordRequestForm` no valida formato: un `username` sin formato de correo produce 401 genérico (credencial que no calza), no 422. En OpenAPI `format` es informativo, pero en un documento presentado como "fuente de la verdad de la interfaz" sugiere una validación inexistente — y el doc 10 de requerimientos sí dice "Email con formato válido" para el login (`02_requerimientos.md:248`).
**Fix:** Bajar a `type: string` con la descripción actual ("OAuth2 llama username a este campo; transporta el email"), o mover la expectativa de formato explícitamente al cliente (el espejo honesto que la guia-06 sí implementa con su regex).

### IN-07: `int(user_id)` fuera del `try` en `get_current_user` — un `sub` no numérico firmado produciría 500 en vez del 401 genérico

**File:** `docs/05_desarrollo/guia-05-cuentas-backend.md:453`
**Issue:** `usuario = UsuarioRepository(db).por_id(int(user_id))` está fuera del bloque que captura `InvalidTokenError`. Un token con `sub` no numérico (p. ej. `"abc"`) pasaría la verificación de firma y reventaría con `ValueError` → 500. Hoy es inalcanzable sin el `SECRET_KEY` (nadie más puede firmar), así que no es explotable — pero contradice la premisa del propio módulo ("captura toda la jerarquía de errores de token") y enseña el patrón incompleto a futuros `sub` compuestos.
**Fix:** Mover la conversión dentro del `try` (envolviéndola) o validar antes: `if user_id is None or not user_id.isdigit(): raise credentials_exception`.

---

_La re-ejecución post-fix de las mini-verificaciones afectadas (CR-01 en especial) corresponde al flujo de fix de este review y al UAT delegado en `D:/Repos/maura-uat`, con la regla de corregir en los dos lugares._

_Reviewed: 2026-09-29T21:10:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

## Fix Log

_Appended by gsd-code-fixer — 2026-09-29T18:16:11Z (iteration 1). Scope: critical +
warning (8/8 fixed, 0 skipped). Report: `02-REVIEW-FIX.md`._

- **CR-01** fixed (a1983ff) — routers de guia-05 importan `Error` desde `app.schemas.producto` (vive ahí desde la guia-04); backend arranca.
- **WR-01** fixed (b6474a7) — total $26.980 → $26.970 en 03_diseno (×2), guia-07 y guia-08.
- **WR-02** fixed (6fcad69) — guard por construcción: `apiPostForm` viaja `sinAuth`, el login jamás lleva Bearer y su 401 nunca dispara el interceptor (requires human verification).
- **WR-03** fixed (d22e080) — write-back al hidratar en `Carro.tsx`: la cantidad guardada se ajusta al stock y el badge cuenta lo que la pantalla muestra; 03_diseno queda verdadero sin editar (requires human verification).
- **WR-04** fixed (f3cf4d4) — `lib/api.ts` de guia-06 normaliza el `detail` string/array del 422 (cierra el WR-04 open de fase 1).
- **WR-05** fixed (b8db43b) — desvío del 422 real (detail array) documentado en el contrato y en prose de guia-05.
- **WR-06** fixed (5fe42d9) — bloque de guia-07 paso 2 reducido a las líneas nuevas (sin redeclarar hooks de guia-04).
- **WR-07** fixed (e9c2491) — "los 8 paths" → "los 7 paths" en guia-05; además "los 4 paths nuevos" para desambiguar.

_Info findings (IN-01..IN-07) quedan abiertos fuera del scope de este fix._
