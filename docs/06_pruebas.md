# Fase 6 — Pruebas: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida: 6. Pruebas**
> **Qué construirás hoy:** nada de código nuevo — el método de pruebas que ya venías usando, ahora con nombre y con su porqué.
> **Al terminar tendrás:** el mapa de cómo se defiende cada pieza de esta tienda: qué capa del método protege qué, y con qué evidencia la comprobaste TÚ.
> **Necesitas:** las guías 1 a 15 construidas (o haberlas recorrido de punta a punta) — este documento nombra lo que ya viviste.
> **Fecha:** 2026-10-01

---

## La divergencia con el hermano mayor, declarada

En demo-cine, la fase de pruebas construyó una suite de pruebas
automáticas: un archivo con 17 pruebas que corre con un solo comando y
grita en rojo cuando alguien rompe una regla. Esta serie tomó otro
camino, y este documento lo declara en vez de esconderlo: **aquí no vas
a escribir una suite nueva**. Lo que esta tienda hizo — y lo que tú
hiciste siguiéndola — fue defender cada pieza en el momento en que
nació: una **mini-verificación** al terminar cada paso, una **Gran
verificación final** al cerrar cada fase, y **verificaciones runtime
contra servicios REALES** (Webpay en su ambiente de integración, la
asesora con TU key). Esta fase del ciclo no añade una herramienta:
**pone nombre al método que ya usaste**, para que puedas ejecutarlo de
nuevo en tu próximo proyecto sabiendo por qué existe cada capa.

¿Y por qué la divergencia? Porque el riesgo de ESTE proyecto nunca fue
solo "el refactor silencioso rompe una regla que nadie defiende" (el
caso de demo-cine): fue **la integración con servicios externos reales**
— credenciales, contratos, redirecciones, maneras de fallar que ningún
doble de prueba reproduce. Un mock de Webpay aprueba siempre; la
integración real, no necesariamente. El método de esta serie apunta su
evidencia a donde estaba el riesgo.

## Los términos de hoy

| Término | Qué es, en una frase |
|---|---|
| **Mini-verificación** | El ✅ que cierra cada paso de cada guía: observable, inmediata, y la corres TÚ antes de seguir al paso siguiente |
| **Gran verificación final** | La tabla de cierre de cada fase: filas numeradas con su columna Origen, incluida la fila fija contrato ↔ `/docs` |
| **Verificación runtime contra servicio real** | La prueba contra la integración viva (Webpay integración, la asesora con TU key) — no contra dobles de prueba |
| **Idempotencia** | Re-ejecutar una operación deja el mismo estado: el seed que restaura el catálogo sin duplicar filas (D-05/D-06/D-07) es EL caso de la serie |
| **Grep del build** | La prueba mecánica de que ningún secreto cruzó al bundle del frontend: buscar la key en `dist/` y no encontrarla |

---

## El método, en una tabla

Cada capa del método defiende algo distinto, y cada fila cita de dónde
nació — la misma trazabilidad que exigimos a todo el corpus:

| Verificación de la serie | Origen | Qué defiende |
|---|---|---|
| **Mini-verificación por paso** — el ✅ al final de cada paso: los doce `[=]` del seed que converge (guía 3), el `422` de `?familia=vinagre` sin un solo `if` escrito a mano (guía 4), el badge "¡Últimas 2 unidades!" en la ficha de Rosa de Río | Estructura canónica desde la guía 1 (🧠 + código + ✅) | Que **el paso** quedó bien: el error se detecta a un paso de su causa, no a una fase de distancia |
| **Gran verificación final por fase** — la tabla numerada CS/RF (11 filas en la fase 1, 12 en la 2 y la 3, 13 en la 4) con su fila fija **contrato ↔ `/docs`**: comparar UNO A UNO contra `contrato_api.yaml` y probar el botón **Authorize** con las cuentas del seed (la clienta ve 403 donde el admin ve 200) | La fijó la guía 4 (fase 1, fila 11, ADR-007); la replicaron las guías 8, 11 y 15 | Que **el contrato y la fase** quedaron bien: cualquier diferencia es un desvío — o el código corrige, o el contrato se versiona y se aprueba de nuevo; jamás cambia en silencio |
| **Verificación runtime contra servicio real** — los 4 flujos de retorno de Webpay (aprobado, anulado, timeout y error) contra la integración REAL de Transbank; la asesora recomendando aromas reales con TU key de console.groq.com; y el **grep del build**: `GROQ_API_KEY` con **cero coincidencias** en `dist/` (control positivo: "Pregúntale a Maura" SÍ se encuentra) | Fases 3-4: el spike del retorno y ADR-012 (guías 9-11), ADR-018 (guías 14-15, fila 13) | Que **la integración real** funciona — el punto más allá del cual ningún doble de prueba puede testificar |
| **La instancia final** — la Gran verificación de la fase 5 contra el **ambiente desplegado**: los 4 flujos contra tu URL pública, el refresh de rutas sin 404, el contrato ↔ `/docs` público en internet y el grep del build re-corrido en producción | `guia-18-despliegue-cierre.md` la define (DEPL-02) — y **la corres TÚ, en tus cuentas** (D-73) | Que la integración real sigue viva **en internet**: el método completo, de punta a punta, contra el ambiente final |

La última fila es la razón de ser de este documento en el ciclo: el
método no termina en tu computador. La misma tabla que cerró la fase 1
contra `localhost:8000/docs` se corre una última vez contra la tienda
publicada — y esa tabla la define la guía 18 para que tú la ejecutes
con tus propias cuentas de plataforma.

## El porqué de cada capa

🧠 **El desarrollador piensa:** *¿por qué una mini-verificación al final
de CADA paso, y no una gran fase de pruebas al final? Porque el error
más barato de arreglar es el que se detecta a un paso de su causa.
Cuando en la guía 3 el seed imprimió once `[+]` y un `[-]` donde
esperabas doce `[=]`, no necesitaste debugger: el paso anterior era el
culpable y estaba a una pantalla de distancia. Una suite al final del
proyecto te dice que ALGO rompió; la mini-verificación te dice QUÉ paso
lo rompió, que es la información que de verdad ahorra tiempo.*

🧠 **El desarrollador piensa:** *¿por qué la fila contrato ↔ `/docs`
existe en TODAS las fases y no solo al final? Porque el drift entre lo
construido y lo acordado no espera a nadie. El contrato se aprueba
ANTES de codificar (D-15, ADR-007); la fila de cierre compara lo
construido contra esa verdad única fase a fase, y el desvío se detecta
en el momento — no cuando un consumidor externo ya dependía del error.
La regla que aprendiste en la fila 11 de la guía 4 sigue idéntica en la
guía 15: cualquier diferencia es un desvío, jamás un cambio en silencio.*

🧠 **El desarrollador piensa:** *¿por qué runtime real y no mocks?
Porque ya vivimos la prueba en contrario. La documentación de
Transbank decía que el flujo anulado vuelve por POST; el spike de la
fase 3 observó que el runtime habló **GET** — corrección material que
quedó canónica en ADR-012 y que hizo del endpoint un GET+POST que
discrimina por presencia de params. Un mock programado "según la
documentación" habría aprobado el comportamiento documentado y la
clienta real del flujo anulado habría aterrizado en un 405. La
integración real es la única testigo confiable de la integración real
— y cuando la doc y el runtime discrepan, el runtime manda y la
diferencia se documenta.*

Esa es también la lección de la idempotencia como término del método:
el seed se re-ejecuta en cada deploy de la fase 7 (sembrado al build,
ADR-020) precisamente PORQUE es idempotente — el método no es un ritual
de aula: son las propiedades que el despliegue gratuito de la tienda
termina explotando como estrategia.

## 🔧 Errores típicos del método (y su remedio)

| Síntoma | Causa | Remedio |
|---|---|---|
| La fila de la Gran verificación quedó marcada… y no la corrido | Marcar es más fácil que comprobar | La fila se marca solo si TÚ la comprobaste — desmárcala y corre la verificación; el hábito vale más que la tabla completa |
| "El checkout está roto", culpé al código… y el backend estaba detenido | Verificar con el servicio caído | `/api/salud` primero: el estado del servicio se comprueba antes de juzgar al código — es la primera mini-verificación de toda la serie |
| El grep del build no encontró NADA de nada — ni la key ni el control positivo | El grep se corrió contra un `dist/` viejo o el build ni compiló | Control positivo SIEMPRE antes de celebrar el cero: "Pregúntale a Maura" SÍ debe aparecer en `dist/`; si no aparece, el grep no está mirando el bundle regenerado (guía 15, fila 13) |
| Verifiqué solo el pago aprobado — "el resto es lo mismo" | Confianza en el happy path | Los 4 flujos existen porque NO son lo mismo: el anulado llega con otros params (y por GET, ADR-012), el timeout deja la orden PENDING "en curso" — cada flujo defiende una rama distinta del retorno |

---

## ✅ Verificación de la fase

Lo que debe ser cierto al terminar de leer este documento — sin correr
nada, contra lo que ya viviste:

| # | Verificación | Origen |
|---|---|---|
| 1 | Puedes nombrar las tres capas del método (mini-verificación por paso, Gran verificación final por fase, verificación runtime contra servicio real) y qué defiende cada una | Este documento, §El método |
| 2 | Reconoces en las guías que ya construiste al menos un ejemplo real de cada capa — y puedes señalar en qué guía estaba | Guías 1 a 15 |
| 3 | Puedes explicar la divergencia con el hermano mayor: qué eligió demo-cine para esta fase, qué eligió esta serie, y por qué el riesgo del proyecto decidió el método | §La divergencia, D-71 |
| 4 | Sabes qué falta: la instancia final del método contra el ambiente desplegado la define la guía 18 y la corres TÚ en tus cuentas | DEPL-02, D-73 |

---

## 📝 Punto de control (respóndelas sin mirar el documento)

1. La mini-verificación va al final de cada paso y no en una fase de
   pruebas al final del proyecto: ¿qué información te da la una que la
   otra no? (estructura canónica desde la guía 1)
2. La fila contrato ↔ `/docs` apareció en las cuatro tablas de cierre de
   las fases 1 a 4: ¿qué drift detecta, qué obliga hacer con cualquier
   diferencia, y por qué el botón Authorize la completa? (ADR-007,
   guía 4 fila 11)
3. La documentación de Transbank decía POST y el runtime habló GET:
   ¿dónde quedó registrada la corrección, cómo se diseñó el endpoint
   para quedar inmune, y qué habría aprobado un mock programado "según
   la doc"? (ADR-012, spike de la fase 3)

## Lo que acabas de aprender

- El método de pruebas de esta serie, con nombre: tres capas
  (mini-verificación / Gran verificación final / verificación runtime)
  que defiende tres cosas distintas (el paso, el contrato y la fase, la
  integración real)
- Por qué la divergencia con demo-cine no es una omisión: el riesgo de
  ESTE proyecto (integraciones reales) decidió el método
- La fila contrato ↔ `/docs` como detector de drift en el momento —
  ADR-007, la evidencia formal de cierre de cada fase
- El caso doc-vs-runtime del spike (POST dicho, GET observado) como el
  argumento definitivo contra los mocks — ADR-012
- La idempotencia del seed como propiedad que el despliegue gratuito
  explota después (ADR-020): el método de pruebas se convierte en
  estrategia de persistencia
- Los errores típicos del propio método (marcar sin correr, culpar al
  código con el servicio caído, el grep sin control positivo, el happy
  path como única muestra) — porque también el que verifica puede
  verificarse mal

**Siguiente:** [07_despliegue.md](07_despliegue.md) — la fase que
materializa P1 ("que se abra desde cualquier dispositivo") y congela el
`return_url` que Webpay exige. Y donde la instancia final de este
método — la verificación contra el ambiente desplegado — queda definida.
