# Fase 2 — Documento de Requerimientos: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida:** 2. Análisis de requerimientos
> **Insumo obligatorio:** `01_necesidad_del_cliente.md` (cliente: Maura · Body Splash) — cada requerimiento de este documento **nace de una petición (P), condición (C) o criterio de éxito (CS)** de ese documento. La tabla de trazabilidad (§13) demuestra el hilo.
> **Producto:** Maura · Body Splash — tienda online de body splash artesanal
> **Fecha:** 2026-09-28

---

## 1. Contexto y objetivo

**Maura · Body Splash** es la tienda online del emprendimiento de perfumería
artesanal de Maura. En esta primera etapa la tienda publica el catálogo: una
página de inicio con la identidad de la marca, la grilla de aromas filtrable
por familia y precio, la ficha de cada producto y los datos demo que la pueblan.
El carro, las cuentas y el pago llegan en las etapas siguientes del proyecto
(véase §2).

**Objetivo del sistema:** permitir que cualquier visitante **explore, filtre y
conozca** el catálogo de aromas desde cualquier dispositivo, sobre datos demo
reproducibles.

> **Alcance temporal de este documento:** los requerimientos aquí cubren la
> **etapa 1 del proyecto** (la que construye esta guía primero). Las peticiones
> P5–P8 del cliente quedan documentadas y trazadas (§13) hacia sus etapas
> futuras — no se olvidan: se calendarizan.

---

## 2. Alcance

**Dentro del alcance de la etapa 1** (lo que pide el cliente, §4 doc 01):
- Página de inicio con la identidad de la marca Maura · Body Splash (P1).
- Catálogo público en grilla, navegable sin cuenta por cualquier visitante (P1, P2).
- Filtros del catálogo por familia aromática y rango de precio (P2).
- Ficha de producto con descripción, precio, familia, notas aromáticas y disponibilidad de stock (P3).
- Datos demo sembrados de forma idempotente, re-ejecutable sin duplicar (P4, CS3).

**Fuera del alcance de la etapa 1** (peticiones que esperan su etapa, §4 doc 01):
- Carro de compras y cuentas de clientas (P5) → **etapa 2**.
- Pago online con Webpay en modo de prueba (P6) → **etapa 3**.
- Panel de administración de productos, stock y pedidos (P7) → **etapa 4**.
- Asesora de venta con recomendación de aromas (P8) → **etapa 4**.

**Fuera del alcance del proyecto** (lo que el cliente NO pide, §6 doc 01):
- Logística de envíos con seguimiento, cobro de dinero real, marketplace
  multi-vendedor, multi-idioma/multi-moneda.

---

## 3. Actores y roles

| Rol | Descripción | Origen | Permisos clave |
|---|---|---|---|
| **Visitante (anónimo)** | Cualquier persona que llega a la tienda desde su celular o computador | P1, P2 | Ver la página de inicio, navegar el catálogo, filtrar y abrir fichas de producto |

> Las clientas con cuenta (P5), la dueña con panel (P7) y la asesora de venta
> (P8) son actores de etapas futuras: aparecen en este documento únicamente en
> la tabla de trazabilidad (§13), para que el hilo quedé completo desde hoy.

---

## 4. Requerimientos funcionales (RF)

### Identidad y catálogo público (soportan P1, P2, C3)
- **RF-01:** El sistema debe mostrar una página de inicio con la identidad de la marca Maura · Body Splash — nombre, frase de marca y las familias aromáticas — con una acción clara hacia el catálogo. *(STORE-01, P1)*
- **RF-02:** El sistema debe mostrar el catálogo en una grilla de tarjetas, cada una con imagen, nombre, familia aromática y precio del producto, navegable sin cuenta. *(STORE-02, P2)*

### Filtros del catálogo (soportan P2, CS1)
- **RF-03:** El sistema debe permitir filtrar el catálogo por familia aromática y por un rango de precio (mínimo y máximo), y debe indicar cuántos aromas quedan a la vista tras filtrar. *(STORE-02, P2, CS1)*

### Ficha de producto (soportan P3, CS2)
- **RF-04:** El sistema debe mostrar una ficha por producto con su descripción, su precio en pesos chilenos, su familia aromática, sus notas aromáticas y su disponibilidad de stock; si el producto no existe, debe decirlo con claridad. *(STORE-03, P3, CS2)*

### Datos demo (soportan P4, CS3)
- **RF-05:** El sistema debe poder sembrar datos demo del catálogo de forma **idempotente**: re-ejecutar la siembra deja el catálogo en el mismo estado conocido, sin duplicar productos. *(STORE-04, P4, CS3)*

---

## 5. Requerimientos no funcionales (RNF)

| Código | Categoría | Descripción | Origen |
|---|---|---|---|
| RNF-01 | Usabilidad | La tienda es usable desde el celular: nada exige pantalla ancha y los controles (filtros, enlaces) tienen tamaño táctil suficiente | C3, C4, CS4 |
| RNF-02 | Rendimiento | La tienda responde rápido en modo local de desarrollo: la primera carga del catálogo muestra los datos ya sembrados, sin esperas largas | P3, CS1 |
| RNF-03 | Operación | Todo el recorrido de esta etapa funciona **sin cuenta**: landing, catálogo y fichas son públicos para el visitante | §2 alcance (P1) |
| RNF-04 | Mantenibilidad | Los datos demo son **reproducibles**: cargarlos dos veces deja el catálogo idéntico (sin duplicados), y el catálogo de esta etapa es de solo lectura — nadie modifica datos desde la tienda | P4, CS3, RN-04 |

---

## 6. Reglas de negocio (RN)

- **RN-01:** La familia aromática de un producto pertenece a una lista cerrada de cuatro valores: `citricas`, `florales`, `frutales` o `dulces`, escritos **sin acentos** en el intercambio de datos; la pantalla muestra la etiqueta con acento ("Cítricas"). Cualquier otro valor se rechaza. *(P2; origen técnico: los acentos en los filtros viajan por la dirección de la página y la ensucian — detalle resuelto en la fase 3.)*
- **RN-02:** El precio es un **entero en pesos chilenos (CLP)**, sin decimales, dentro del rango **$6.990–$12.990** del catálogo demo. *(P3, C4)*
- **RN-03:** La imagen de cada producto es un **archivo local** del proyecto, referenciado como `/products/{sku}.jpg`; la tienda no depende de fotos alojadas en servicios externos. *(P2, P3)*
- **RN-04:** El catálogo de esta etapa es de **solo lectura**: la tienda solo consulta productos; crear, editar y desactivar llegan con el panel de administración de la etapa 4. *(§2 alcance)*

---

## 7. Historias de usuario (con criterios de aceptación Gherkin)

### HU-01 — Explorar el catálogo
*Como* visitante, *quiero* ver el catálogo de aromas en una grilla, *para* recorrer lo que hay sin necesidad de una cuenta.
- **Dado** que estoy en la página del catálogo,
  **Cuando** la cargo desde mi celular,
  **Entonces** veo todos los productos activos en tarjetas con imagen, nombre, familia y precio en pesos chilenos.

### HU-02 — Filtrar por familia y precio
*Como* visitante, *quiero* acotar el catálogo por familia aromática y rango de precio, *para* encontrar mi estilo de aroma rápido.
- **Dado** que estoy en el catálogo,
  **Cuando** elijo la familia "Cítricas" y acoto el precio entre $6.990 y $9.990,
  **Entonces** solo quedan a la vista aromas cítricos dentro de ese rango, y el contador dice cuántos son.
- **Dado** que filtré y ningún aroma cumple,
  **Cuando** la grilla queda vacía,
  **Entonces** veo un mensaje que explica el caso y una acción para limpiar los filtros.

### HU-03 — Ver la ficha de un producto
*Como* visitante, *quiero* abrir la ficha de un aroma, *para* conocer sus notas y saber si hay stock antes de decidir.
- **Dado** que seleccioné un producto del catálogo,
  **Cuando** se abre su ficha,
  **Entonces** veo su imagen, nombre, familia, precio, descripción, notas aromáticas y disponibilidad ("N unidades disponibles" o "Agotado").
- **Dado** que un enlace apunta a un producto que no existe,
  **Cuando** abro ese enlace,
  **Entonces** veo un mensaje claro de producto no encontrado y una forma de volver al catálogo.

### HU-04 — Sembrar los datos demo
*Como* desarrollador de la guía, *quiero* sembrar el catálogo demo las veces que sea necesario, *para* trabajar y probar siempre sobre el mismo estado conocido.
- **Dado** un catálogo vacío,
  **Cuando** ejecuto la siembra de datos demo,
  **Entonces** el catálogo queda poblado con los doce aromas de las cuatro familias.
- **Dado** un catálogo ya sembrado,
  **Cuando** vuelvo a ejecutar la siembra,
  **Entonces** no se duplica ningún producto: cada aroma existente se actualiza a su valor conocido y el conteo sigue siendo doce. *(CS3, RNF-04)*

---

## 8. Modelo de datos preliminar (insumo para la fase de diseño)

| Entidad | Atributos clave | Relaciones |
|---|---|---|
| **Producto** | id, sku (único), nombre, descripcion, precio (entero CLP, RN-02), stock, familia (lista cerrada de 4 valores, RN-01), notas aromáticas (lista), activo, imagen (ruta local, RN-03) | Sin relaciones en esta etapa; las cuentas y pedidos de las etapas 2 y 3 se conectarán a esta entidad |

> *La decisión de datos más importante de esta etapa: el **sku** es la clave
> natural estable del catálogo demo — la siembra idempotente (RF-05) se apoya
> en él para actualizar sin duplicar. Se desarrolla en la fase de diseño (03).*

---

## 9. Procesos principales (insumo para DFD en diseño)

1. **Explorar el catálogo:** visitante → abre la tienda → página de inicio → catálogo → grilla completa.
2. **Filtrar el catálogo:** visitante → elige familia y/o rango de precio → el sistema acota la grilla y cuenta los resultados.
3. **Ver la ficha:** visitante → selecciona un producto → el sistema muestra descripción, notas y disponibilidad (o producto no encontrado).
4. **Sembrar datos demo (proceso interno):** desarrollador → ejecuta la siembra → el sistema crea o actualiza cada producto por sku → catálogo en estado conocido.

---

## 10. Entradas del sistema (formularios y validaciones)

| Entrada | Actor | Validaciones clave |
|---|---|---|
| Filtro por familia | Visitante | Familia ∈ {citricas, florales, frutales, dulces} (RN-01); cualquier otro valor se rechaza |
| Rango de precio | Visitante | Enteros ≥ 0; mínimo no mayor que el máximo efectivo de resultados esperados |
| Enlace a ficha | Visitante | Identificador de producto existente y activo; si no, pantalla de no encontrado (HU-03) |

## 11. Salidas del sistema

| Salida | Audiencia | Medio |
|---|---|---|
| Página de inicio de marca | Visitante | Pantalla web responsiva (C3, C4) |
| Catálogo en grilla con filtros | Visitante | Pantalla web responsiva |
| Ficha de producto | Visitante | Pantalla web responsiva |
| Datos del catálogo para la propia tienda | La tienda (consumo interno) | Documento de intercambio JSON descrito por contrato (fase 4) |

## 12. Pantallas principales (insumo para prototipado)

1. **Inicio (landing):** identidad de marca, frase, presentación de las familias y acción hacia el catálogo.
2. **Catálogo:** barra de filtros (familia + rango de precio) y grilla de tarjetas con contador de resultados.
3. **Ficha de producto:** imagen grande, datos completos, notas aromáticas y disponibilidad.

---

## 13. Trazabilidad: necesidad → requerimiento

El hilo completo del ciclo de vida. **Ninguna petición queda sin requerimiento y ningún requerimiento nace de la nada.**

| Necesidad (doc 01) | Se convierte en | Se verifica con |
|---|---|---|
| P1 Tienda online propia | RF-01, RF-02, RNF-03 | HU-01, CS4 |
| P2 Catálogo ordenado por familias | RF-02, RF-03, RN-01, RN-03 | HU-01, HU-02, CS1 |
| P3 Ficha completa por producto | RF-04, RN-02 | HU-03, CS2 |
| P4 Datos de prueba sin duplicar | RF-05, RNF-04 | HU-04, CS3 |
| P5 Carro y cuentas | *(sin requerimiento en esta etapa — etapa 2: CART-01..03, AUTH-01..04 del requisitos v1)* | Etapa 2 |
| P6 Pago online con Webpay | *(sin requerimiento en esta etapa — etapa 3: PAY-01..04)* | Etapa 3 |
| P7 Panel de administración | *(sin requerimiento en esta etapa — etapa 4: ADMN-01..04)* | Etapa 4 |
| P8 Asesora de venta | *(sin requerimiento en esta etapa — etapa 4: AIAS-01..03)* | Etapa 4 |
| C1 Presupuesto mínimo | RNF-04 (estado reproducible sin pagar servicios); el resto se resuelve en la fase 4 (arquitectura gratuita) | Fase 4 |
| C2 Maura sola, etapas revisables | Estructura por fases del propio proyecto (docs/README.md, regla del proyecto) | CS5 |
| C3 Celular y notebook | RNF-01 | HU-01, CS4 |
| C4 Clientas chilenas | RN-02 (CLP), RNF-01 | HU-01, HU-03 |
| CS1 Filtrar por familia y precio | RF-03 | HU-02 |
| CS2 Ficha con notas y disponibilidad | RF-04 | HU-03 |
| CS3 Siembra sin duplicar | RF-05, RNF-04 | HU-04 |
| CS4 Tienda desde cualquier dispositivo | RF-01, RNF-01 | Verificación de la etapa en el navegador |
| CS5 Maura entiende cada etapa | Documento por fase con aprobación y firmas (docs/README.md) | Firma de cada fase |

---

## 14. Aprobación de la fase

| Rol | Nombre | Decisión | Fecha |
|---|---|---|---|
| Analista | ______________ | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |
| Cliente (validación de requerimientos) | Maura — Maura · Body Splash | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |

> **Nota para la clase:** este documento es el contrato de QUÉ hace el sistema
> (en esta etapa), jamás de CÓMO se construye. El CÓMO lógico arranca en la
> fase 3 (`03_diseno.md`): modelo de datos detallado, diagramas de procesos
> (DFD) y prototipo de pantallas; sigue en la fase 4 con las decisiones de
> arquitectura (ADRs) y el contrato del intercambio de datos. Misma estructura
> que el proyecto hermano demo-cine: los alumnos pueden contrastar ambos
> documentos y ver la misma mecánica de trazabilidad en un dominio distinto.
