# Fase 1 — La Necesidad del Cliente: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida:** 1. Necesidad
> **Regla de esta fase:** el documento habla el idioma del CLIENTE. Cero tecnología, cero jerga de sistemas. La traducción a lenguaje técnico recién ocurre en la fase 2 (requerimientos).
> **Fecha:** 2026-09-28

---

## 1. El cliente

**Maura · Body Splash** es un emprendimiento de perfumería artesanal de Santiago.
Su dueña, **Maura** (43, ex técnica dental), hace body splash a mano en lotes
pequeños, con esencias frescas que elige una por una. Hoy vende por Instagram y
WhatsApp, con el catálogo completo en fotos de su celular. Quiere llegar a todo
Chile sin intermediarios: que cada clienta pueda ver sus aromas, elegir el suyo
y pagarlo desde donde esté.

## 2. Cómo funciona hoy (situación actual)

- El catálogo vive en la **galería de fotos del celular**: cuando una clienta
  pregunta "¿qué tienes?", hay que mandarle fotos de frascos una por una.
- Los **pedidos llegan por chat** (Instagram y WhatsApp) y se anotan en el
  cuaderno o en una nota del teléfono, sin ningún orden.
- Los **precios** están en la cabeza de Maura o en una nota suelta: cada tanto
  hay que corregir una cotización a mano.
- No hay **registro de qué aroma prefiere cada clienta**: las recomendaciones
  dependen de la memoria de Maura.
- El **stock** se cuenta a ojo antes de cada lote: recién al despachar descubre
  que prometió frascos que ya no tiene.
- La **vitrina** es el feed de Instagram: el orden del algoritmo decide quién
  ve cada publicación, y las fotos viejas se pierden en el scroll.

## 3. El problema (por qué duele)

| # | Dolor | Consecuencia |
|---|---|---|
| D1 | El catálogo está desordenado en las fotos del celular | Cada consulta se contesta a mano, lento y distinto cada vez; las clientas nuevas se aburren antes de comprar |
| D2 | Los pedidos por chat se pierden o se duplican | Hay clientas que esperan semanas y otras que reciben dos despachos; ventas que se caen solas |
| D3 | No se sabe qué aroma prefiere cada clienta | Maura no puede recomendar ni avisar cuando llega exactamente lo que a alguien le encanta |
| D4 | No se puede vender fuera de la comuna | El negocio no crece más allá de las ferias y del boca a boca de la zona |
| D5 | No hay registro del stock | Maura promete frascos que ya no tiene y los descubre recién al despachar, con la clienta ya avisada |
| D6 | Publicar depende del canal de otros | La vitrina no le pertenece: si el algoritmo decide, sus aromas dejan de verse de un día para otro |

## 4. Lo que el cliente necesita (en sus propias palabras)

> *"Quiero una tienda que sea mía, donde cualquier persona de Chile pueda ver
> mis aromas, elegir la suya y pagarla ahí mismo, sin que yo tenga que estar
> contestando mensajes de madrugada. Y quiero entender qué se está construyendo
> en cada etapa, para no sentir que el proyecto me pasa por encima."*
> — Maura, dueña de Maura · Body Splash

Formalizado como peticiones del cliente:

| # | Petición |
|---|---|
| P1 | Una **tienda online propia**, con el nombre y el estilo de la marca, que se abra desde cualquier dispositivo |
| P2 | El **catálogo ordenado por familias de aroma** (cítricas, florales, frutales y dulces), para que cada clienta encuentre su estilo rápido |
| P3 | Una **ficha por producto** con su descripción, su precio, sus notas aromáticas y su disponibilidad, siempre al día |
| P4 | **Datos de prueba** para poblar la tienda y probarla sin miedo, que se puedan volver a cargar sin repetir productos |
| P5 | **Carro de compras y cuentas** para las clientas, para comprar en varios pasos y revisar sus pedidos |
| P6 | **Pago online con Webpay**, para cobrar con tarjetas como en cualquier tienda chilena |
| P7 | Un **panel de administración** para gestionar productos, stock y pedidos sin depender de nadie |
| P8 | Una **asesora de venta** que recomiende aromas del catálogo a cada clienta, como lo haría Maura en persona |

## 5. Objetivos del cliente (de negocio, no técnicos)

- **O1:** Vender a todo Chile sin intermediarios ni comisiones de marketplace.
- **O2:** Tener una vitrina siempre disponible y ordenada, que sea de la marca y no del algoritmo.
- **O3:** Dedicar menos horas a contestar mensajes repetidos y más a hacer body splash.
- **O4:** Conocer su negocio: qué se vende, qué queda y qué prefieren las clientas.

## 6. Lo que el cliente NO pide (gestión de expectativas)

- Logística de envíos con seguimiento por etiqueta (se despacha, pero el
  seguimiento no es parte del sistema).
- Cobrar dinero real desde el primer día: la tienda parte operando en **modo de
  prueba** para aprender sin riesgo; el cobro real se evalúa más adelante.
- Venderle lugar a otros emprendedores (marketplace): la tienda es solo de Maura.
- Atender en otros idiomas o vender en otras monedas: las clientas están en
  Chile, hablan español y pagan en pesos.

Dejar esto por escrito evita el clásico "¿y si le agregamos…?" a mitad del proyecto.

## 7. Condiciones y restricciones del cliente

| # | Condición |
|---|---|
| C1 | **Presupuesto mínimo:** todo en planes gratuitos o de prueba mientras el proyecto aprende a caminar; sin tarjetas de crédito de por medio |
| C2 | **Personal:** Maura sola, sin equipo técnico; el proyecto se construye en etapas cortas que ella pueda revisar |
| C3 | **Equipamiento:** todo se maneja desde el celular y un notebook; nada que exija una oficina ni máquinas especiales |
| C4 | **Mercado:** clientas chilenas — español, pesos chilenos y medios de pago locales |

## 8. Criterios de éxito (cómo sabe el cliente que quedó resuelto)

| # | Criterio | Cómo se verifica |
|---|---|---|
| CS1 | Una visitante puede filtrar el catálogo por familia y por precio | Navegando la tienda: elegir una familia, acotar el precio y comprobar que solo quedan los aromas que corresponden |
| CS2 | La ficha de cada producto muestra sus notas aromáticas y su disponibilidad | Abriendo un producto cualquiera del catálogo y revisando que notas y stock aparezcan siempre |
| CS3 | Los datos de prueba se cargan sin duplicar | Cargando los datos demo dos veces seguidas y contando: el catálogo queda igual, sin aromas repetidos |
| CS4 | La tienda se abre desde cualquier dispositivo | Probando en el celular, en el notebook y en otro navegador: la tienda funciona en todos |
| CS5 | Maura entiende el estado de su proyecto en cada etapa | Al cierre de cada etapa, Maura revisa el documento de esa fase, pregunta lo que no entienda y firma |

## 9. Aprobación de la fase

| Rol | Nombre | Decisión | Fecha |
|---|---|---|---|
| Cliente (dueña) | Maura — Maura · Body Splash | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |
| Equipo de desarrollo | ______________ | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |

> *En el ciclo de vida formal, la necesidad se **aprueba y se firma** antes de
> analizar nada: es el primer hito del proyecto.*

---

> **Nota para la clase:** este documento es el insumo directo de la fase 2
> (`02_requerimientos.md`): cada petición (P), condición (C) y criterio de
> éxito (CS) se traducirá allí a requerimientos funcionales y no funcionales
> numerados, y la tabla de trazabilidad permitirá recorrer el hilo completo —
> ningún requerimiento "aparece de la nada" y ninguna petición queda olvidada.
> Las peticiones P5–P8 no se olvidan: se construyen en las etapas siguientes,
> y la trazabilidad de la fase 2 lo deja dicho explícitamente.
