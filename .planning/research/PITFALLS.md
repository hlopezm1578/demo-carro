# Pitfalls Research

**Domain:** E-commerce educativo de dos tiers (SPA React + API FastAPI en capas) con Webpay Plus sandbox (Transbank) y asistente IA (Google Gemini)
**Researched:** 2026-09-28
**Confidence:** HIGH en hallazgos leídos directamente de documentación oficial (Transbank, FastAPI, Vite, Gemini); MEDIUM en consenso de comunidad (JWT storage, cold starts, hosts estáticos). Desglose por hallazgo en cada sección y en Sources.

> Nota de procedencia: el seam de proveedores clasifica webfetch/websearch como tier LOW (no son proveedores curados); los hallazgos de este archivo provienen mayoritariamente de páginas oficiales leídas directamente durante la investigación (ver Sources). Los pocos puntos que no pudieron verificarse contra fuente primaria están marcados MEDIUM/LOW y con la acción de verificación concreta que la guía debe ejecutar.

## Critical Pitfalls

### Pitfall 1: El `return_url` de Webpay apunta directo a la SPA y los flujos anómalos son invisibles para React

**What goes wrong:**
El flujo normal de Webpay Plus (API 1.1+) retorna al `return_url` por **GET** con `token_ws` en el query string — eso una SPA sí lo puede leer. Pero los flujos anómalos no: en el ambiente de integración, el **pago anulado retorna por POST** (con `TBK_TOKEN`, `TBK_ID_SESION`, `TBK_ORDEN_COMPRA` en el *body* del form), y **ningún JavaScript de página puede leer el body de una navegación POST**. Si el `return_url` apunta a la SPA desplegada en un host estático, el alumno que prueba "anular pago" en el sandbox ve una página en blanco o un error del host, sin saber qué pasó. El caso "error en formulario + volver al sitio" entrega `token_ws` + `TBK_TOKEN` + `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` juntos y exige discriminación server-side.

**Why it happens:**
Los tutoriales típicos de SPA asumen que todo retorno es un GET con query params. La documentación de Transbank es explícita: "A la URL de `return_url` siempre se llega por POST, aunque desde la versión 1.1 del API, en adelante, la redirección es por GET (solo en el caso de pago abortado en el ambiente de integración, el retorno se mantiene por POST)". Los diagramas muestran el happy path y el detalle queda en una nota que los principiantes saltan.

**How to avoid:**
- `return_url` debe apuntar a un **endpoint del backend FastAPI** que acepte **GET y POST**, lea los parámetros de ambos orígenes (query y form), discrimine los 4 flujos documentados (normal: solo `token_ws`; timeout: solo `TBK_ID_SESION` + `TBK_ORDEN_COMPRA`; anulado: `TBK_TOKEN` + `TBK_ID_SESION` + `TBK_ORDEN_COMPRA`; error de formulario: todos juntos) y luego **redirija (303) a una ruta de la SPA** tipo `/orden/{id}?estado=pagado|anulado|timeout`.
- El `commit` ocurre solo en el flujo con `token_ws` (y sin `TBK_TOKEN` acompañando); en el flujo anulado se valida con `transaction.status(TBK_TOKEN)` y **no** se hace commit.
- Correlacionar el retorno con la orden usando el `buy_order`/`session_id` guardados al crear la transacción, nunca confiando solo en el token.
- Ejecutar el **spike del retorno antes de escribir la guía de desarrollo** (PROJECT.md ya lo lista como pendiente): probar en sandbox el pago aprobado, el anulado y el timeout (el formulario de integración expira a los 10 minutos).

**Warning signs:**
- El checkout funciona en el happy path pero "anular" en el sandbox muestra página en blanco o 405 del host estático.
- El código del frontend busca `token_ws` solo con `useSearchParams` (no hay manejo de form POST).
- En el backend solo existe un handler GET para el retorno.

**Phase to address:**
Fase de checkout Webpay — con un **spike previo** a la redacción de la guía de esa fase (es el patrón de mayor riesgo del proyecto).

---

### Pitfall 2: Redirección inicial a Webpay hecha con `window.location` (debe ser un POST con form)

**What goes wrong:**
`transaction.create` devuelve `token` + `url`. El comercio debe redirigir al comprador a esa `url` mediante un **POST de formulario con un input oculto `token_ws`**. Un alumno que hace `window.location.href = url + "?token_ws=" + token` (o un `fetch` seguido de navigate) envía el token por GET: Webpay no lo recibe como espera y el formulario de pago no carga o queda en error.

**Why it happens:**
Es contraintuitivo: la API se llama por REST pero la redirección del pagador es una simulación de formulario clásico. La documentación lo dice ("es redirigido mediante un POST"), pero el patrón SPA empuja a usar navegación programática simple.

**How to avoid:**
- Patrón recomendado para SPA + API: el endpoint `POST /api/checkout` responde con `url` y `token`; el frontend **renderiza un `<form method="POST" action={url}>` con `<input type="hidden" name="token_ws" value={token}>` y lo auto-sube** (`formRef.current.submit()`), o el backend responde directamente un mini-HTML con el form auto-submit.
- Documentar en la guía por qué no funciona un link o `window.location` con query.

**Warning signs:**
- El botón "pagar" navega a `webpay3gint.transbank.cl` pero muestra error de Transbank o página sin formulario de tarjeta.
- Búsquedas de "token_ws" solo en el retorno, no en la salida.

**Phase to address:**
Fase de checkout Webpay (misma unidad que el Pitfall 1).

---

### Pitfall 3: Doble commit de la transacción (refresh del retorno / reintentos)

**What goes wrong:**
El usuario refresca la página de resultado (o el navegador reintenta el GET/POST al `return_url`) y el handler vuelve a llamar `transaction.commit(token)`. Resultado típico: error de Webpay en el segundo commit y/o una orden procesada dos veces (stock descontado doble, historial duplicado). La documentación oficial no especifica el error exacto del segundo commit (verificar empíricamente en sandbox — MEDIUM), pero sí establece que el resultado queda consultable hasta 7 días vía `transaction.status(token)`, que es la vía correcta de re-verificación.

**Why it happens:**
El endpoint de retorno queda implementado como "recibí token → commit → redirige", sin estado. Cualquier recarga lo re-ejecuta. Los principiantes no consideran que el navegador re-envía la navegación.

**How to avoid:**
- **Idempotencia a nivel aplicación**: antes de hacer commit, verificar si la orden ya tiene resultado guardado; si lo tiene, saltar el commit y redirigir directo al resultado almacenado.
- Persistir el resultado del commit (`response_code`, `status`, `authorization_code`, `amount`) en la orden al momento del commit, dentro de la misma transacción de BD.
- Para recuperaciones: `transaction.status(token)` en vez de re-commit.
- Regla de aprobación documentada: la compra está aprobada solo si `response_code == 0` **y** `status == "AUTHORIZED"`.

**Warning signs:**
- La orden tiene dos filas de pago o el stock bajó de a dos tras una prueba con refresh (F5 en la página de retorno).
- El handler del retorno no consulta el estado de la orden antes de llamar a Transbank.

**Phase to address:**
Fase de checkout Webpay (diseño de la entidad Orden con estado) — el modelo de estados debe quedar definido ahí, antes del panel admin que lo consume.

---

### Pitfall 4: API key de Gemini en el bundle del frontend

**What goes wrong:**
Alguien pone la API key en una variable `VITE_GEMINI_API_KEY` "para probar el asistente rápido" y llama a Gemini desde React. **Toda variable con prefijo `VITE_` se incrusta estáticamente en el bundle** y cualquier visitante la lee en `dist/assets/*.js` o en devtools. La key queda comprometida (y quemada contra los límites del proyecto).

**Why it happens:**
Vite hace que las variables `VITE_` "simplemente funcionen" en el cliente; la nota de seguridad de la doc oficial es fácil de ignorar. En tutoriales de Gemini el quickstart usa la key directo en el cliente de prueba.

**How to avoid:**
- La key vive **solo en el backend** como `GEMINI_API_KEY` (variable de entorno), patrón ya decidido en PROJECT.md. El chat del frontend llama a `POST /api/asistente` del backend FastAPI.
- `.gitignore` con `.env` desde el **primer commit** del repositorio; commitear `.env.example` con nombres y sin valores.
- Verificación incluida en la guía: `grep -r "VITE_" dist/` (o buscar la key en el build) para demostrar que no se filtró.
- Distinguir en la guía: las credenciales públicas de integración de Transbank (código de comercio 597055555532) son deliberadamente públicas y pueden ir en código/config; la Gemini key no.

**Warning signs:**
- Cualquier `import.meta.env.VITE_*` cuyo valor sea un secret.
- Aparecen llamadas `fetch` desde React a `generativelanguage.googleapis.com`.
- Un `.env` trackeado en git (`git ls-files | grep .env` devuelve algo).

**Phase to address:**
Fase de fundaciones (setup del repo, `.gitignore`, `.env.example`, contrato de variables de entorno) y refuerzo explícito en la fase del asistente IA.

---

### Pitfall 5: Token JWT expira a mitad de checkout / almacenamiento elegido sin ADR

**What goes wrong:**
Dos caras del mismo pitfall:
1. El token expira mientras el usuario navega el carro o está en el formulario de Webpay; al volver y crear la orden/historial, la API responde 401 y el alumno no entiende por qué "la app se desloguea sola" (perdiendo el contexto de la compra).
2. La decisión de storage (localStorage vs httpOnly cookie) se toma por copia-pegue de un tutorial, sin explicar el tradeoff — en una guía educativa eso es un fallo pedagógico además de técnico.

**Why it happens:**
Los tutoriales ponen `localStorage.setItem("token", ...)` y listos. El consenso de la industria (Stack Overflow, Security.SE, blogs: ver Sources) es: localStorage es legible por cualquier script (robo por XSS); las cookies httpOnly + Secure + SameSite evitan la lectura desde JS pero introducen riesgo CSRF; el patrón híbrido común es access token corto en memoria + refresh token en cookie httpOnly.

**How to avoid:**
- **Decisión explícita con ADR** (el formato del proyecto ya usa ADRs): para una guía educativa con sandbox, `localStorage` con **access tokens de vida corta** es defendible por simplicidad, documentando el tradeoff XSS; la alternativa cookie httpOnly implica CORS con `allow_credentials` + CSRF, más compleja.
- Manejar el 401 de forma graceful: interceptor/respuesta que distinga "checkout no requiere auth" (pago como invitado) o re-login que **preserve el carro** (carro en BD o en localStorage separado del token).
- Expiración del token coherentemente mayor al tiempo razonable de una sesión de prueba sandbox (recordar: el formulario de integración de Webpay permite hasta 10 minutos antes del timeout).

**Warning signs:**
- 401s intermitentes tras ~15–30 minutos de uso o justo al volver de Webpay.
- El carro vive solo en estado de React (se pierde en el full-page load que impone la redirección de Webpay — ver Pitfall 12).
- No existe ADR de storage del token.

**Phase to address:**
Fase de cuentas JWT + historial (ADR y expiración); la preservación del carro se resuelve en la fase de carro/checkout.

---

### Pitfall 6: CORS mal configurado (wildcard con credentials, defaults restrictivos, origen olvidado tras deploy)

**What goes wrong:**
Escenario 1: se copia `allow_origins=["*"]` con `allow_credentials=True` — según la doc oficial de FastAPI eso no es válido (wildcards y credentials son incompatibles; orígenes, métodos y headers deben listarse explícitos). Escenario 2: no se toca nada y los defaults de `CORSMiddleware` (métodos solo GET, headers vacíos) bloquean el `POST /api/login` con `Authorization` desde Vite. Escenario 3, el más común en proyectos de alumnos: **funciona en local (`http://localhost:5173`) y explota al desplegar**, porque el origen de producción nunca se agregó a la lista.

**Why it happens:**
CORS solo se manifiesta con el browser abierto; el backend "funciona" probado con curl. Y el origen cambia entre desarrollo y producción, así que la configuración correcta en local es incorrecta después del deploy.

**How to avoid:**
- Orígenes desde variable de entorno del backend (`CORS_ORIGINES` con local + producción), no hardcodeados.
- Config explícita: `allow_origins=[lista]`, `allow_credentials=True` solo si se usan cookies, `allow_methods=["*"]` solo si no hay credentials (o listarlos), `allow_headers` explícitos.
- En la guía: mostrar el error real de CORS en la consola del navegador y cómo leerlo — es contenido pedagógico valioso.
- Checklist de deploy: actualizar orígenes al dominio real del frontend.

**Warning signs:**
- Errores "blocked by CORS policy" en consola del navegador (y ausentes en curl).
- `Access-Control-Allow-Origin: *` junto con `withCredentials`.
- La lista de orígenes tiene `localhost` pero no el dominio del deploy.

**Phase to address:**
Fase de fundaciones (config base con Vite local) y verificación obligatoria en la fase de despliegue.

---

### Pitfall 7: Código bloqueante dentro de `async def` (SQLAlchemy sync, SDK de Transbank, Gemini) congela el event loop

**What goes wrong:**
FastAPI corre los endpoints `async def` directamente en el event loop. Si dentro llamas a SQLAlchemy **sincrónico** o al SDK de Transbank (basado en `requests`, bloqueante) o a cualquier librería sin `await`, **todo el servidor deja de responder** mientras dura esa llamada — con Gemini hablando de segundos por respuesta, el chat del asistente congela la tienda completa cada vez que alguien pregunta algo.

**Why it happens:**
La regla oficial de FastAPI es poco visible para principiantes: los endpoints `def` (sin async) corren en un threadpool externo; los `async def` con I/O bloqueante no. El alumno ve ejemplos `async def` en todos lados y asume que es "lo moderno" siempre.

**How to avoid:**
- Regla simple para la guía: si la librería no soporta `await` → endpoint con `def` plano. FastAPI lo manda al threadpool automáticamente.
- Alternativa: mantener `async def` y delegar el bloqueo con `anyio.to_thread.run_sync(...)` / `run_in_executor` — más avanzado, mostrar como nota.
- Si se usa SQLAlchemy async (con aiosqlite/asyncpg), mantener consistente: nunca sesión sync dentro de async def.
- Nota adicional de la doc oficial: las funciones utilitarias propias **no** reciben tratamiento de threadpool, solo path operations y dependencias.

**Warning signs:**
- Mientras el asistente responde, otras pestañas/requests a la API quedan cargando.
- `async def` en un endpoint que importa `Session` de SQLAlchemy sync o llama al SDK Transbank.
- Latencia de la API proporcional al tráfico del chat.

**Phase to address:**
Fase de fundaciones/backend en capas (convención sync/async del proyecto) y refuerzo obligatorio en la fase del asistente IA.

---

### Pitfall 8: Backend "en capas" que termina en fat routers o con lógica de negocio en los repositorios

**What goes wrong:**
Sin una convención temprana, los routers FastAPI acumulan todo: validación, consultas SQLAlchemy, llamadas a Transbank, reglas de stock y armado de respuestas. O el extremo opuesto: el "repositorio" termina conteniendo las reglas de negocio (cuándo confirmar una orden, cuándo descontar stock) y el service es un pasamanos. En una guía educativa cuyo objetivo pedagógico explícito es la arquitectura en capas, cualquiera de los dos desvíos invalida el aprendizaje.

**Why it happens:**
FastAPI no impone estructura: un archivo `main.py` con routers gigantes "funciona". La presión de avanzar hace que la lógica se agregue donde ya estaba el código.

**How to avoid:**
- Estructura de referencia definida en la fase de diseño (ADR): `routers/` (HTTP: parseo de request, status codes, serialización) → `services/` (lógica de negocio: ciclo de vida de la orden, reglas de stock, orquestación de Transbank/Gemini, transacciones de BD) → `repositories/` (solo acceso a datos, sin reglas).
- Inyección de la sesión de BD como dependencia FastAPI (`Depends(get_db)`), commits en el service, no en el repositorio.
- Test de arquitectura simple que la guía puede incluir: los routers no importan SQLAlchemy directamente; los repositories no importan `transbank` ni `google.genai`.

**Warning signs:**
- `from sqlalchemy import ...` dentro de un router.
- Un service que solo hace `return self.repo.x(...)`.
- Reglas de negocio (estados de orden, validación de stock) probables solo vía HTTP.

**Phase to address:**
Fase de fundaciones/diseño (ADR de arquitectura en capas + esqueleto de carpetas), se aplica transversalmente desde el primer endpoint.

---

### Pitfall 9: Race condition de stock — oversell con SELECT-then-UPDATE

**What goes wrong:**
Dos checkouts simultáneos sobre la última unidad: ambos leen `stock = 1`, ambos pasan el check `if stock >= cantidad`, ambos hacen `UPDATE ... stock = stock - 1`. Resultado: stock negativo o dos órdenes por una unidad (oversell). En SQLite la ventana existe igual (serializa escrituras pero no corrige la lógica leer-verificar-escribir); además el patrón `BEGIN` diferido + upgrade de lock puede terminar en `SQLITE_BUSY`.

**Why it happens:**
Es el patrón que surge naturalmente del código legible, y en pruebas de un solo usuario nunca falla — solo aparece con concurrencia, que la guía de pruebas debe provocar a propósito.

**How to avoid:**
- Decremento condicional atómico: `UPDATE productos SET stock = stock - :qty WHERE id = :id AND stock >= :qty` y verificar **filas afectadas** (`result.rowcount`): 0 = sin stock → rechazar la orden.
- Con SQLite, secuencias leer-verificar-escribir dentro de `BEGIN IMMEDIATE` (toma el write lock de inmediato y evita `SQLITE_BUSY` en el upgrade); configurar `busy_timeout` igual.
- Si la guía usa PostgreSQL: `SELECT ... FOR UPDATE` (o `SKIP LOCKED`) en la fila del producto.
- Momento del descuento: decidir y documentar (descuento al confirmar el commit de Webpay es lo simple; reservas con expiración es lo correcto para carros abandonados — out of scope para el sandbox, mencionar como evolución).
- Prueba incluida en la guía: script que dispara N checkouts concurrentes contra la última unidad y verifica que solo uno pase.

**Warning signs:**
- Stock negativo visible en el panel admin.
- El check de stock vive en Python (`if producto.stock < qty: raise`) en vez de en el WHERE del UPDATE.
- No hay ninguna prueba concurrente.

**Phase to address:**
Fase de checkout/órdenes (decremento en el service) con verificación en la fase de pruebas; el panel admin (fase posterior) lo hace visible.

---

### Pitfall 10: Asistente que alucina productos (recomendaciones no fundamentadas en el catálogo real)

**What goes wrong:**
El chat de Gemini recomienda body splash "Vainilla Nocturna 200ml" que no existe en el catálogo, con precios inventados. El alumno no distingue respuesta correcta de alucinación porque el modelo suena seguro; la dueña de la PYME (caso ficticio) vendería productos inexistentes.

**Why it happens:**
Un LLM sin el catálogo en el contexto responde desde su conocimiento general + invención. La doc oficial de text generation no aborda alucinación de datos propios; la mitigación (entregar el catálogo en el prompt) es responsabilidad de quien integra.

**How to avoid:**
- **Mini-RAG prompt-based** (decisión ya en PROJECT.md): inyectar el catálogo real (id, nombre, descripción, precio, stock) en el prompt de cada consulta.
- `system_instruction` explícita: "Eres el vendedor de esta tienda. Recomienda SOLO productos de la lista entregada, usando exactamente sus ids/nombres/precios. Si nada encaja, dilo y sugiere lo más cercano. No inventes productos ni precios."
- **Validación posterior en el backend**: si la respuesta del asistente referencia ids de producto, verificar contra la BD antes de renderizar links/tarjetas en el frontend (los id válidos vienen del catálogo inyectado; todo lo demás se muestra como texto plano).
- Temperatura baja para respuestas de catálogo.
- Prueba en la guía: preguntar por una fragancia que no existe y verificar que el asistente NO la inventa.

**Warning signs:**
- Respuestas con nombres/precios que no calzan con el catálogo (probar preguntando por algo inexistente).
- El prompt al modelo no incluye el catálogo, solo la pregunta del usuario.
- El frontend renderiza cualquier producto que el modelo nombre sin validar contra la API.

**Phase to address:**
Fase del asistente IA (diseño del prompt + validación); el contrato de datos del catálogo viene de la fase de catálogo.

---

### Pitfall 11: Latencia y rate limits de Gemini degradan el chat (429 en clases, respuesta congelada)

**What goes wrong:**
1. **Latencia**: una llamada no streamed al modelo tarda segundos con la burbuja congelada; el usuario repite el click y encadena más llamadas.
2. **429 RESOURCE_EXHAUSTED**: los límites son **por proyecto** (no por API key) y se miden en RPM/TPM/RPD; en un curso con 20 alumnos usando la misma key del mismo proyecto, el free tier se agota y el asistente falla en plena demostración. La doc oficial ya no publica los números por modelo: hay que verlos en `aistudio.google.com/rate-limit` (pendiente ya anotado en PROJECT.md).
3. **Riesgo de superficie de API cambiante**: la doc de streaming hoy documenta `client.interactions.create(stream=True)` con eventos `step.delta`, tratando `client.models.generate_content_stream` como superficie anterior — verificar contra la referencia del SDK `google-genai` vigente (2.25.0, 2026-09-22) antes de fijar el material (MEDIUM: leído de doc oficial vía fetch asistido, requiere confirmación contra la referencia del SDK).

**Why it happens:**
Los quickstarts muestran la llamada bloqueante y nadie lee la página de rate limits. El free tier parece "infinito" hasta que 30 requests simultáneos en un laboratorio lo queman.

**How to avoid:**
- **Streaming** para el chat (SSE del backend al frontend): primera palabra visible rápido, percepción de fluidez; estado de "escribiendo..." y deshabilitar el botón mientras responde.
- **Cada alumno crea su propia API key/proyecto** en Google AI Studio (gratuita, sin tarjeta) — decisión pedagógica clave que además enseña el manejo de credenciales; la key nunca se comparte.
- Manejo explícito de errores: 429 → mensaje amable "el asistente está saturado, reintenta en un momento" (y backoff corto); timeout del lado del backend; nunca dejar un `fetch` sin catch.
- Confirmar RPM/RPD vigentes logueado en AI Studio al momento de escribir la fase, y dejarlo anotado en la guía como "límites al día de escritura" (los números cambian).
- Verificar la superficie de API del SDK al escribir la fase (interactions vs models) y fijar la versión exacta de `google-genai` en requirements.

**Warning signs:**
- El endpoint del chat no es SSE/streamed y la burbuja espera la respuesta completa.
- Errores 429 en logs durante pruebas en paralelo.
- Material de la guía que nombra métodos del SDK sin verificar contra la referencia de la versión fijada.

**Phase to address:**
Fase del asistente IA (streaming + manejo de errores + instrucción de key propia por alumno); la confirmación de límites es tarea de investigación de esa fase (o del spike previo).

---

### Pitfall 12: El carro vive solo en memoria de React y muere en cada full-page load

**What goes wrong:**
La redirección a Webpay es un POST de formulario fuera de la SPA (Pitfall 2) y el retorno re-carga la SPA completa (Pitfall 1). Si el carro está solo en estado de React (Context/Zustand en memoria), al partir a Webpay y volver la SPA se remonta desde cero y **el carro aparece vacío** justo después de pagar.

**Why it happens:**
En la navegación SPA normal (react-router) el estado sobrevive, así que el bug no aparece hasta la primera prueba real del flujo de pago — el único momento donde la app sufre navegaciones full-page.

**How to avoid:**
- Carro persistido en `localStorage` (id/vistas) o, mejor pedagógicamente, carro server-side en la BD asociado a sesión/usuario, restaurado por la SPA al montar.
- La prueba UAT de la fase checkout debe incluir explícitamente: llenar carro → pagar → volver de Webpay → el carro refleja el estado post-compra.

**Warning signs:**
- No hay hidratación del carro al montar la app (`useState([])` inicial sin restore).
- Las pruebas del carro solo navegan dentro de la SPA.

**Phase to address:**
Fase de carro (persistencia) + verificación en fase checkout (el full-page load es lo que lo expone).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Todo el backend en `main.py` con routers gordos | Avance rápido del primer endpoint | Refactor forzoso al llegar a Transbank/Gemini; guía pierde el objetivo pedagógico de capas | Nunca en este proyecto (el objetivo ES la arquitectura en capas) |
| Carro en memoria de React | Menos una tabla/endpoints | Carro se pierde en el flujo Webpay (full-page loads) | Nunca si hay checkout con redirección externa |
| Validación de stock solo en Python (SELECT then UPDATE) | Código legible, funciona en pruebas de 1 usuario | Oversell bajo concurrencia | Nunca en el path de compra; aceptable en pantalla admin de edición manual |
| Sin manejo de estado en la orden (string libre) | Menos un enum/tabla de estados | Dobles commits imposibles de detectar; panel admin ambiguo | Nunca; definir estados desde la fase checkout |
| Llamada a Gemini sin streaming | Menos código SSE | Chat percibido como roto (segundos congelados) | Prototipo interno de 1 día, no en material de la guía |
| `print` en vez de logging | Rapidez | Imposible depurar el retorno de Webpay en el host desplegado | Primeros minutos de un spike; la guía enseña `logging` desde la fase fundaciones |
| Tests solo manuales vía UI | Avance de fases rápido | Pitfalls de concurrencia y doble commit nunca se detectan | Puntual en fases tempranas; la fase de pruebas debe automatizar los flujos Webpay |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Transbank Webpay Plus | `return_url` apuntando a la ruta de la SPA (los flujos anómalos llegan por POST que el JS no puede leer) | `return_url` → endpoint backend GET+POST que discrimina los 4 flujos, commitea y redirige 303 a la SPA |
| Transbank Webpay Plus | Redirigir al pagador con GET/link en vez de form POST con `token_ws` oculto | Renderizar y auto-subir un `<form method="POST">` con el token |
| Transbank Webpay Plus | Re-llamar `commit` tras refresh o reintento | Idempotencia: guardar resultado en la orden; recuperar con `transaction.status(token)` (disponible 7 días) |
| Transbank Webpay Plus | Aprobar solo con `response_code == 0` | Aprobar solo con `response_code == 0` **y** `status == "AUTHORIZED"` |
| Transbank Webpay Plus | Asumir que anulado = llamar commit con TBK_TOKEN | Anulado: validar con `status(TBK_TOKEN)`, nunca commit; informar al usuario |
| Transbank Webpay Plus | `amount` con decimales / no coincidir con el total de la orden | `amount` entero (pesos) calculado server-side desde la BD, nunca desde el cliente |
| Google Gemini | Key en `VITE_*` / llamada desde el frontend | Key solo backend (`GEMINI_API_KEY`); frontend → `POST /api/asistente` |
| Google Gemini | Prompt sin catálogo → productos inventados | Catálogo real inyectado en el prompt + system instruction restrictiva + validación de ids contra BD |
| Google Gemini | Una key compartida por todo el curso (límites por proyecto) | Key propia por alumno desde AI Studio; manejar 429 con mensaje y retry |
| Google Gemini | Asumir la superficie de API del SDK por memoria de tutoriales | Verificar métodos vigentes contra la referencia de `google-genai` fijado en requirements (la superficie cambió recientemente) |
| FastAPI ↔ SPA | `allow_origins=["*"]` con credentials / defaults sin tocar / origen de producción olvidado | Lista explícita de orígenes desde env (local + producción); re-verificar tras deploy |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| I/O bloqueante dentro de `async def` (SQLAlchemy sync, SDK Transbank, Gemini) | Toda la API se congela mientras responde el chat o el commit | Endpoints `def` planos para librerías sync (threadpool) o async consistente | Desde el primer request concurrente — inmediato en una clase |
| Chat no streamed | Burbuja congelada 3–10 s; clicks repetidos | SSE/streaming + estado "escribiendo..." | Siempre (latencia de LLM) |
| `SQLITE_BUSY` bajo escritura concurrente (checkout + admin a la vez) | Error 500 intermitente en checkout | `BEGIN IMMEDIATE`, `busy_timeout`, transacciones cortas | Con 2+ escritores simultáneos |
| N+1 en catálogo/historial | Carga lenta de listas | `selectinload`/joins desde la fase de catálogo | Decenas de filas (historial de pedidos) |
| Cold start del host free tier (ej. Render free: spin-down tras 15 min, primera request 30–60 s) | Demo de clase empieza con la API "caída" | Elegir plataforma conscientemente, keep-alive, o mostrar el spinner y avisar en la guía | Tras 15 min de inactividad (siempre en una demo) |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Gemini API key en `VITE_*` o en código frontend | Key pública en el bundle, uso abusivo del proyecto | Key solo backend; `grep` al build en la guía; `.env` en `.gitignore` desde el commit 1 |
| `.env` commiteado a git | Fuga de secrets en el historial (difícil de revertir) | `.gitignore` inicial + `.env.example`; si ocurre, rotar la key (no basta borrar el archivo) |
| JWT sin expiración o eterno en localStorage | Token robado usable indefinidamente | Expiración corta; documentar tradeoff en ADR |
| Monto del pago calculado/confiado desde el frontend | Usuario manipula el total antes de crear la transacción | Recalcular total server-side desde BD al crear la transacción |
| `return_url` sin validación de correlación con la orden | Confusion de orden/respuesta entre sesiones | Correlacionar `buy_order`/`session_id` guardados en BD; unicidad de `buy_order` |
| SQL armado por concatenación en filtros de catálogo | Inyección SQL | SQLAlchemy expressions/parameters siempre; el repository es el único lugar con SQL |
| Panel admin sin protección de rol | Cualquier usuario autenticado edita stock/pedidos | Rol en el JWT + dependencia `require_admin` en los routers del panel |
| Voucher/respuesta de Transbank confiada sin commit | Estado de pago falso en la orden | El estado de la orden solo cambia con el resultado del `commit` (o `status`) server-side |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Carro vacío al volver de Webpay | Comprador pagó y "perdió" su compra visible | Carro persistido + página de resultado con detalle de la orden |
| Pantalla en blanco en pago anulado/timeout | Usuario cree que la compra se hizo o que la app se rompió | Rutas SPA de resultado con estados explícitos: pagado / anulado / expirado (los 4 flujos mapeados a mensajes) |
| 401 inesperado al volver del pago | "Me deslogueó la app" | 401 graceful, checkout como invitado o re-login que preserva el carro |
| Burbuja de chat sin feedback durante la generación | Usuario re-envía la pregunta | Streaming + indicador de escritura + botón deshabilitado |
| Asistente recomienda productos sin stock | Frustración al intentar comprar | Incluir stock en el catálogo del prompt e instrucción de no ofrecer agotados |
| Error de CORS recién después del deploy | "En mi computador funcionaba" | Checklist de deploy con orígenes; sección de la guía que enseña a leer el error de consola |

## "Looks Done But Isn't" Checklist

- [ ] **Checkout:** solo se probó el pago aprobado — verificar anulada ("anular" en sandbox), timeout del formulario (10 min en integración) y refresh de la página de retorno.
- [ ] **Checkout:** monto enviado a Transbank no recalculado server-side — verificar que el `amount` del `create` sale de la BD, no del payload del cliente.
- [ ] **Órdenes:** sin estados diferenciados (pendiente/pagada/anulada/expirada) — verificar que el refresh del retorno no produce segundo commit ni doble descuento.
- [ ] **Checkout en desarrollo:** StrictMode (React 18) monta los efectos dos veces — verificar que "pagar" no dispara dos `transaction.create` (deshabilitar el botón al primer click / guard de submit).
- [ ] **Stock:** nunca se probó concurrencia — verificar script de N checkouts sobre la última unidad: exactamente 1 pasa.
- [ ] **Asistente:** nunca se preguntó por algo inexistente — verificar que no inventa productos/precios y que los links que renderiza existen en la BD.
- [ ] **Asistente:** sin manejo de 429/timeout — verificar respuesta amable del chat con la key saturada y con la API caída.
- [ ] **Auth:** expiración no probada en flujo real — verificar token vencido a mitad de checkout no rompe el cierre de la compra.
- [ ] **Admin:** edición de stock no respeta el decremento condicional — verificar que admin no puede dejar stock negativo.
- [ ] **Deploy:** solo se probó la ruta raíz — verificar refresh en `/orden/123`, `/catalogo`, `/login` (fallback a index.html) y POST del retorno anulado aceptado por el backend.
- [ ] **Secrets:** nunca se inspeccionó el build — verificar que la Gemini key no aparece en `dist/` ni en el repo (`git log -p | grep -i key`).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| return_url apuntando a la SPA | MEDIUM | Agregar endpoint de retorno en el backend (GET+POST), commitear ahí y redirigir 303 a la ruta SPA de resultado; el contrato de Transbank no cambia |
| Doble commit ya ocurrido | LOW | Corregir estado de la orden desde `transaction.status(token)` (ventana de 7 días); agregar idempotencia; reverificar stock |
| Gemini key filtrada en bundle/repo | LOW | Rotar la key en AI Studio (gratuita), mover a backend, purgar `.env` del tracking (`git rm --cached`) |
| Fat router consolidado | HIGH | Refactor capa por capa: extraer service primero (comportamiento), luego repository; en guía educativa conviene re-ordenar la fase antes que refactorizar a mitad |
| Oversell ya ocurrido en datos | LOW | Corregir stock manual vía admin; cambiar a UPDATE condicional; agregar prueba de concurrencia |
| CORS roto tras deploy | LOW | Agregar origen de producción a la lista (env var) y redeploy; verificar preflight desde el navegador |
| Event loop bloqueado por el chat | MEDIUM | Mover endpoint del asistente a `def`/threadpool o async consistente; se nota y arregla rápido con pruebas concurrentes |
| Carro perdido en retorno de Webpay | MEDIUM | Persistir carro (localStorage/BD) e hidratar al montar; tocar el estado global del frontend |
| Asistente alucinando | LOW | Reforzar system instruction + inyectar catálogo + validar ids contra BD; iterar prompts con casos de prueba negativos |

## Pitfall-to-Phase Mapping

Fases referenciales derivadas de los requisitos activos de PROJECT.md (fundaciones → catálogo/carro → checkout Webpay → cuentas JWT → panel admin → asistente IA → pruebas → despliegue). El roadmap debe ajustar nombres y orden, manteniendo las dependencias indicadas.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1 Retorno Webpay → SPA (POST invisible) | Fase checkout — **spike previo obligatorio** | UAT en sandbox de los 4 flujos: aprobado, anulado, timeout, error-form; página de resultado correcta en todos |
| P2 Redirección inicial por form POST | Fase checkout | Formulario auto-submit llega al formulario de tarjeta de Webpay sandbox |
| P3 Doble commit | Fase checkout (modelo de orden con estados) | F5 en el retorno no genera segundo commit ni doble descuento |
| P4 API key en frontend | Fase fundaciones + refuerzo en fase IA | `grep` de la key en `dist/` y en el historial git sin resultados |
| P5 JWT storage/expiry | Fase cuentas JWT (ADR) | Token vencido a mitad de checkout no rompe el flujo; ADR escrito |
| P6 CORS | Fase fundaciones + verificación en despliegue | Requests del navegador desde Vite local y desde el dominio de producción sin errores de consola |
| P7 Bloqueo del event loop | Fase fundaciones (convención sync/async) + fase IA | Durante una respuesta del chat, otros endpoints responden normal |
| P8 Fat routers / capas | Fase fundaciones/diseño (ADR + esqueleto) | Routers sin imports de SQLAlchemy; repositories sin imports de transbank/google-genai |
| P9 Race de stock | Fase checkout + fase de pruebas | Script concurrente sobre última unidad: exactamente una orden aprobada |
| P10 Alucinaciones | Fase asistente IA | Pregunta por producto inexistente: no lo inventa; links solo a ids válidos |
| P11 Latencia/429 Gemini | Fase asistente IA (+ confirmar límites en spike/investigación de fase) | Chat streamedeado desde la primera palabra; 429 muestra mensaje amable; cada alumno con key propia |
| P12 Carro no persistente | Fase carro + verificación en checkout | Volver de Webpay con la orden reflejada y el carro consistente |

**Orden de fases que estos pitfalls refuerzan:**
- El **spike de retorno Webpay** debe ocurrir antes de redactar la guía de checkout (P1/P2 dependen de su resultado; PROJECT.md ya lo exige).
- La fase de **cuentas JWT** después del checkout permite empezar con checkout de invitado y añadir auth sin bloquear la integración de pago; pero el ADR de storage (P5) conviene decidirlo en fundaciones para no re-escribir el cliente HTTP después.
- La fase **IA** necesita las capas (P7/P8) y el catálogo (P10) ya estables — dejarla al final del desarrollo es correcto.
- La fase de **despliegue** verifica P6 (CORS producción), P12 (fallback SPA) y documenta el cold start del host elegido.

## Sources

Fuentes oficiales (leídas directamente durante la investigación; contenido de confianza HIGH):
- Transbank Developers — Documentación Webpay Plus (flujo completo, 4 flujos de retorno, `token_ws`/`TBK_TOKEN`/`TBK_ID_SESION`/`TBK_ORDEN_COMPRA`, timeout 4/10 min, commit con `response_code==0` y `status==AUTHORIZED`, status 7 días): https://www.transbankdevelopers.cl/documentacion/webpay-plus — leída dos veces por vías independientes durante esta investigación.
- FastAPI — CORS Middleware (wildcards vs credentials, defaults): https://fastapi.tiangolo.com/tutorial/cors/
- FastAPI — Concurrency / async def vs def (threadpool, bloqueo del event loop): https://fastapi.tiangolo.com/async/
- Vite — Env Variables and Modes (advertencia oficial sobre `VITE_` expuesto al cliente): https://vite.dev/guide/env-and-mode
- Google — Gemini API Rate Limits (límites por proyecto, RPM/TPM/RPD, 429, números solo en AI Studio): https://ai.google.dev/gemini-api/docs/rate-limits
- Google — Gemini API Text Generation (`system_instruction`, contexto propio en prompt): https://ai.google.dev/gemini-api/docs/text-generation
- Google — Gemini API Streaming (superficie actual `interactions.create(stream=True)`; verificar contra referencia del SDK): https://ai.google.dev/gemini-api/docs/streaming

Consenso de comunidad (confianza MEDIUM; múltiples fuentes independientes coincidentes):
- JWT storage localStorage vs httpOnly: https://stackoverflow.com/questions/44133536/is-it-safe-to-store-a-jwt-in-localstorage-with-reactjs , https://security.stackexchange.com/questions/209204/sending-and-storing-jwt-in-spa , https://www.syncfusion.com/blogs/post/secure-jwt-storage-best-practices , https://blog.openreplay.com/cookies-vs-localstorage-jwt-auth
- Race de stock / SQLite: https://www.sqlite.org/ (serialización de escrituras, BEGIN IMMEDIATE), patrón UPDATE condicional con rowcount (múltiples blogs/foros coincidentes)
- SPA 404 en hosts estáticos: fixes estándar `_redirects` (Netlify) / `vercel.json` rewrites / `.htaccess`, múltiples fuentes coincidentes
- Cold starts Render free (spin-down 15 min, 30–60 s primera request): comparativos de hosting 2024–2026, fuentes múltiples coincidentes

Puntos sin verificación primaria (marcados MEDIUM en el texto; la guía debe verificar):
- Comportamiento/error exacto del segundo `commit` con el mismo token (no documentado; verificar empíricamente en sandbox).
- Números vigentes RPM/RPD del free tier de Gemini (la doc oficial deriva a `aistudio.google.com/rate-limit`; confirmar logueado al escribir la fase).
- Métodos exactos del SDK `google-genai` 2.25.0 para streaming (superficie de API en transición; verificar contra la referencia del SDK).
- Restricciones de formato de `buy_order`/`session_id`/`amount` (longitud máxima, unicidad, enteros): no re-verificadas en esta pasada contra la referencia del SDK — confirmar en https://www.transbankdevelopers.cl/referencia/webpay-plus al redactar la fase checkout.

---
*Pitfalls research for: e-commerce educativo SPA React + FastAPI con Webpay sandbox y Gemini*
*Researched: 2026-09-28*
