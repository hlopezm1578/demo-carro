# Fase 8 — Mantenimiento: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida: 8. Mantenimiento**
> **Qué construirás hoy:** nada de código nuevo — construirás **la disciplina**: mantener vivo lo construido cuando el mundo de afuera cambia.
> **Al terminar tendrás:** el mapa de cómo crece esto sin romper el ciclo: los diferidos con sus puertas, el camino de crecimiento de la persistencia y la guía viva.
> **Necesitas:** el ciclo recorrido — las guías 1 a 18 y los documentos de las fases 1 a 7.
> **La idea de fondo:** el desarrollo termina; el software no. Esta fase es, en tiempo y dinero, la más larga de la vida de cualquier sistema real.
> **Fecha:** 2026-10-01

---

## La guía viva: todo "a la fecha" caduca

Este documento mira hacia adelante, y lo primero que debe decir de sí mismo
es que **ya está viejo en el momento en que lo lees** — no por falsa
modestia, sino por diseño: la guía cita cifras de terceros "a la fecha", y
los terceros cambian sin avisarnos. Los límites del free tier de Render
(spin-down, horas mensuales), los rate limits de Groq (30 RPM / 1.000 RPD
para `openai/gpt-oss-120b`, según
[console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits),
a la fecha), el default de Python con que Render crea servicios nuevos
(hoy 3.14.3, por encima del techo 3.12 del SDK de Transbank): todo eso son
fotografías, no leyes.

🧠 **El desarrollador piensa:** *y esta serie no habla de oído: ya vivió un
mantenimiento adaptativo completo, con fecha y con ADRs. El 2026-10-01,
Google pasó a exigir cuenta de facturación para crear API keys nuevas y la
key del proyecto devolvió un 402 real (créditos agotados) — el paso del
alumno "key gratis sin tarjeta" quedó imposible. La respuesta no fue abrir
el editor: fue **re-firmar la decisión antes de reescribir la guía**. El
[ADR-017](04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md)
quedó **Superseded por el
[ADR-018](04_arquitectura/adr/018-asistente-ia-groq-structured-outputs.md)**
(Groq: key gratis sin tarjeta, límites públicos citables), y recién después
se reescribió la mitad de integración de la guía 14, se ajustaron los
docs 02/03, los READMEs y el contrato — que quedó agnóstico del proveedor
(D-66) para que la próxima migración no lo vuelva a tocar. Esa es la
disciplina D-15 aplicada al mantenimiento: **primero la evidencia y la
decisión firmada; después la reescritura.** El swap de proveedor es el caso
real de mantenimiento que esta guía ya vivió; cualquier otro cambio futuro
sigue el mismo rito.*

La lección del caso no es "Gemini mal, Groq bien": es que **firmar con
evidencia no evita que un tercero cambie de política — lo documenta**. Y
que las huellas del cambio quedan a la vista y trazables: el ADR viejo no
se borra, se marca Superseded con su fecha; el nuevo cita la evidencia que
lo motivó; la guía se reescribe una sola vez, sobre la decisión ya firmada.

## Los términos de hoy

| Término | Qué es, en una frase |
|---|---|
| **Mantenimiento correctivo** | Arreglar lo que se rompió (bugs reportados) |
| **Mantenimiento adaptativo** | Ajustar a lo que cambió alrededor: una librería, un límite, la política de un proveedor — el swap Gemini→Groq es EL caso |
| **Mantenimiento perfectivo** | Mejorar lo que funciona (rendimiento, experiencia) |
| **Mantenimiento preventivo** | Evitar lo que va a romperse: pagar deuda técnica documentada |
| **Upgrade path** | El camino documentado por el que esto crece sin reescribirse: el swap a PostgreSQL es el nuestro |
| **Supersede** | La mecánica del ADR que reemplaza a otro sin borrarlo: el viejo queda "Superseded por…" con fecha y con su cuerpo intacto |
| **"A la fecha"** | La etiqueta honesta de toda cifra de un tercero: cierta el día que se citó, no una promesa |

🧠 **El desarrollador piensa:** *la clasificación es la ISO/IEC 14764, y esta
tienda ya acumuló los cuatro tipos — documentados: correctivo (los fixes de
guía corregidos en ambos lugares, guía y taller), adaptativo (el swap de
proveedor), perfectivo (el umbral de stock bajo como constante, la caché
por prefijo), preventivo (el contrato agnóstico D-66, el modelo aislado en
una constante D-64). Repasarla con ejemplos propios es la mejor forma de
aprenderla.*

---

## El hilo hacia atrás: cada diferido recorre el ciclo COMPLETO

Lo que queda pendiente vive con ID propio en la sección v2 de
`REQUIREMENTS.md` — no es una lista de deseos difusa: cada ítem es una
puerta con su ciclo completo por delante. La regla que toda la serie
entrenó: **un cambio de pedido no empieza en el código — empieza en la
fase 1.** El ejemplo trabajado, el diferido más pedido por cualquier
tienda real:

### PAY-05 — guest checkout (comprar sin cuenta)

| Fase | Documento a tocar | El cambio |
|---|---|---|
| 1 | [01_necesidad_del_cliente.md](01_necesidad_del_cliente.md) | nueva petición de Maura con su cita (la clienta que quiere comprar sin registrarse) |
| 2 | [02_requerimientos.md](02_requerimientos.md) | RF y RN nuevas del checkout sin cuenta — y AUTH-04 ("el checkout requiere sesión") se revierte CON su porqué escrito, no en silencio |
| 3 | [03_diseno.md](03_diseno.md) | el flujo sin cuenta: pantallas nuevas y el DFD del pedido anónimo — ¿a nombre de quién nace la orden, dónde ve el voucher? |
| 4 | [04_arquitectura/](04_arquitectura/README.md) | **contrato 1.x aprobado ANTES de codificar** (D-15): el schema del checkout y el ownership del pedido cambian — más el ADR nuevo que firme la decisión |
| 5 | [05_desarrollo/](05_desarrollo/README.md) | una guía nueva de checkout — la serie se extiende; las guías construidas no se re-editan |

¿Por qué el rodeo por cinco documentos si el código son veinte líneas?
Porque **cada documento es un contrato con alguien**: el checkout actual
exige sesión (AUTH-04), el contrato promete ese flujo, la Gran verificación
final lo defiende. Cambiar el código directo deja tres documentos
mintiendo — y los documentos que mienten son peores que los que no existen.

### El resto del mapa v2 (con su primera puerta)

| Diferido (REQUIREMENTS v2) | La puerta que abre primero | Lo que el ciclo exigirá |
|---|---|---|
| **STORE-05** — búsqueda por texto | Diseño: el buscador cuando el catálogo supere ~30 SKU | el filtro vive en la URL (`?q=`): RN nueva + contrato del parámetro |
| **ORDR-03** — email de confirmación | Arquitectura: un TERCER servicio externo (SMTP) | ADR nuevo del proveedor, con la misma vara free-sin-tarjeta (D-63/D-69) |
| **ADMN-05** — refund desde el panel | Arquitectura: la API de anulación de Webpay | ADR nuevo + contrato: la transición que hoy no existe (PAID es terminal, RN-15) |
| **STAKE-01** — reviews y calificaciones | Requerimientos: la clienta opina | modelo nuevo + contrato; y la conversación de moderación (ADR del contenido de usuarias) |
| **STAKE-02** — wishlist | Diseño: la lista de deseos | ¿almacén del navegador o cuenta? — la decisión documentada, como el carro (fase 2) |
| **STAKE-03** — cupones de descuento | Requerimientos: el descuento | toca el recalculo del backend (CART-03): contrato + ADR — el precio ya no sale solo del catálogo |
| **STAKE-04** — gráficos en métricas | Arquitectura: una librería de gráficos | ADR de dependencia frontend; ADMN-04 se extiende (hoy es tarjetas y tabla a propósito) |

Ninguno de estos ítems está "en alcance": el mapa v2 existe exactamente
para que el cierre no los prometa. Implementarlos sería scope creep del
cierre — la tabla dice qué puerta abrir el día que se decida abrir, no que
estén abiertas.

## Cómo crece esto: el upgrade path de la persistencia

La decisión más consciente que el cierre deja tomada es la persistencia
([ADR-020](04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md),
firmando la decisión D-70): SQLite efímero + seed idempotente al build, con
el trade-off declarado —
el catálogo siempre revive; el historial de pedidos no sobrevive un ciclo.
Cuando una tienda real no pueda aceptar eso, el camino documentado es
**PostgreSQL en free tier (Neon): cambiar la `DATABASE_URL` del dashboard
y el driver a `psycopg`** — las guías no se reescriben, se extienden; el
resto del stack (modelos, repositorios, servicios) ya está aislado de la
URL de conexión por diseño. Ese día, además, la conversación de clase
escribiría su propio hilo hacia atrás: ADR nuevo (supersede al 020 con su
fecha), `DATABASE_URL` documentada, guía nueva de migración.

Y lo vetado sigue vetado: **pagos reales en producción** y **Stripe**
viven en el Out of Scope de `REQUIREMENTS.md` con su razón (Stripe no
opera para comercios registrados en Chile; la guía opera solo en
sandbox/integración con credenciales públicas). El crecimiento del
sistema no abre esas puertas: el free tier puede crecer (PostgreSQL,
búsqueda, un SMTP), pero la tienda sigue siendo sandbox — cruzar a dinero
real no es un upgrade, es otro proyecto con otras reglas.

---

## ✅ Verificación de la fase

Lo que debe ser cierto al terminar de leer este documento:

| # | Verificación | Origen |
|---|---|---|
| 1 | Puedes nombrar los cuatro tipos de mantenimiento con un ejemplo real de ESTA serie para cada uno | §La guía viva, §Los términos (ISO/IEC 14764) |
| 2 | Puedes recorrer el hilo hacia atrás de PAY-05 de memoria: qué documento toca cada fase y por qué el código va al final | §El hilo hacia atrás, AUTH-04, D-15 |
| 3 | Sabes citar el caso real de mantenimiento adaptativo vivido: qué motivó el swap, qué ADR supersede a cuál, y qué se reescribió después de firmar | ADR-017 → ADR-018 (2026-10-01), D-63..D-68 |
| 4 | Puedes explicar el upgrade path de la persistencia y qué NO forma parte de él (pagos reales, Stripe — Out of Scope) | ADR-020, REQUIREMENTS v2/Out of Scope |

---

## 📝 Punto de control (respóndelas sin mirar el documento)

1. El swap Gemini→Groq: ¿qué se firmó primero y qué se reescribió
   después — y por qué ese orden es la diferencia entre mantenimiento y
   improvisación? (ADR-017/ADR-018, D-15 aplicado al mantenimiento)
2. Tu clienta pide comprar sin cuenta (PAY-05): nombra, en orden, los
   cinco documentos que tocas antes de abrir el editor — y el requerimiento
   v1 que se revierte con su porqué escrito. (hilo hacia atrás, AUTH-04)
3. "Cambiar la `DATABASE_URL` y el driver": ¿qué es literalmente cierto de
   esa frase, qué piezas silenciosas arrastra, y qué sigue vetado pase lo
   que pase con el crecimiento? (ADR-020, Out of Scope)

## Lo que acabas de aprender

- Los cuatro tipos de mantenimiento (ISO/IEC 14764) con ejemplos reales de
  esta serie — incluido el adaptativo vivido: el swap de proveedor con
  mecánica supersede
- El rito del mantenimiento documental: evidencia → decisión firmada
  (ADR) → reescritura — nunca al revés
- El hilo hacia atrás: cada diferido de REQUIREMENTS v2 recorre el ciclo
  completo (necesidad → requerimientos → diseño → ADR/contrato → guía)
  antes de tocar código
- El upgrade path de la persistencia (PostgreSQL = `DATABASE_URL` +
  `psycopg`, guías que se extienden) y lo vetado que sigue vetado
- La guía viva: toda cifra de un tercero lleva su "a la fecha", y caduca

---

## El ciclo se cierra (y se reabre)

Con las ocho fases recorridas, el proyecto queda **vivo y documentado**:
cada decisión con su porqué (20 ADRs), cada regla con su defensa (la
Gran verificación final de cada fase), cada evolución futura con su puerta
abierta y su ID. Lo que queda en el mapa son los diferidos que conversamos:
el **guest checkout** (PAY-05) para la clienta sin cuenta, el **refund**
desde el panel (ADMN-05) con la API de anulación de Webpay, las
**reviews, la wishlist, los cupones y los gráficos** (STAKE-01..04), la
**búsqueda** cuando el catálogo crezca (STORE-05) y el **email** de
confirmación (ORDR-03) — y el día que la tienda deje de ser sandbox, el
**PostgreSQL** que le gane al disco efímero (ADR-020).

> La pregunta de cierre del curso, para llevar a casa: *¿qué tendría que
> pasarle a esta tienda — clientas, pedidos, dinero — para que abrir cada
> una de esas puertas deje de ser capricho y pase a ser necesidad?* Quien
> sabe responderla no memorizó el ciclo de vida: **lo piensa**.

El índice de todo el recorrido vive en [docs/README.md](README.md) — la
tabla de las ocho fases, con el estado de cada una.
