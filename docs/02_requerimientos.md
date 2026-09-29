# Fase 2 — Documento de Requerimientos: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida:** 2. Análisis de requerimientos
> **Insumo obligatorio:** `01_necesidad_del_cliente.md` (cliente: Maura · Body Splash) — cada requerimiento de este documento **nace de una petición (P), condición (C) o criterio de éxito (CS)** de ese documento. La tabla de trazabilidad (§13) demuestra el hilo.
> **Producto:** Maura · Body Splash — tienda online de body splash artesanal
> **Fecha:** 2026-09-28

---

## 1. Contexto y objetivo

**Maura · Body Splash** es la tienda online del emprendimiento de perfumería
artesanal de Maura. En la primera etapa la tienda publicó el catálogo: una
página de inicio con la identidad de la marca, la grilla de aromas filtrable
por familia y precio, la ficha de cada producto y los datos demo que la pueblan.
En esta segunda etapa la tienda suma las cuentas de clientas y el carro de
compras; el pago llega en la etapa siguiente del proyecto (véase §2).

**Objetivo del sistema:** permitir que cualquier visitante **explore, filtre y
conozca** el catálogo de aromas desde cualquier dispositivo, sobre datos demo
reproducibles — y que cualquier clienta **cree su cuenta, arme su carro y llegue
al checkout con su identidad y su compra listas**.

> **Alcance temporal de este documento:** los requerimientos aquí cubren la
> **etapa 1 y la etapa 2 del proyecto** (cada etapa agrega su parte sin
> renumerar lo anterior: las series RF/RNF/RN/HU continúan). Las peticiones
> P6–P8 del cliente quedan documentadas y trazadas (§13) hacia sus etapas
> futuras — no se olvidan: se calendarizan.

---

## 2. Alcance

**Dentro del alcance de la etapa 1** (lo que pide el cliente, §4 doc 01):
- Página de inicio con la identidad de la marca Maura · Body Splash (P1).
- Catálogo público en grilla, navegable sin cuenta por cualquier visitante (P1, P2).
- Filtros del catálogo por familia aromática y rango de precio (P2).
- Ficha de producto con descripción, precio, familia, notas aromáticas y disponibilidad de stock (P3).
- Datos demo sembrados de forma idempotente, re-ejecutable sin duplicar (P4, CS3).

**Dentro del alcance de la etapa 2** (lo que esta etapa suma al sistema):
- Crear cuenta de clienta con email y contraseña (P5).
- Iniciar sesión y mantener la sesión entre recargas de la página (P5).
- Endpoint de administración protegido por rol — el panel completo llega en la etapa 4 (P5, P7).
- Checkout que exige sesión iniciada y devuelve al checkout tras autenticarse (P5).
- Carro de compras: agregar productos, editar cantidades y vaciarlo (P5).
- Carro que persiste en el navegador y sobrevive los full-page loads (P5).

**Fuera del alcance de las etapas 1 y 2** (peticiones que esperan su etapa, §4 doc 01):
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
| **Visitante (anónimo)** | Cualquier persona que llega a la tienda desde su celular o computador | P1, P2 | Ver la página de inicio, navegar el catálogo, filtrar, abrir fichas de producto y armar su carro sin cuenta |
| **Clienta (con cuenta)** | Una visitante que creó su cuenta con email y contraseña | P5 | Todo lo del visitante, más iniciar sesión, mantener la sesión entre recargas, llegar al checkout protegido y (más adelante) revisar sus pedidos |
| **Admin (dueña)** | Maura, la dueña del emprendimiento, con cuenta de rol administrador | P7 | Todo lo de la clienta, más acceder al endpoint de administración protegido por rol (RF-08); su panel de gestión llega en la etapa 4 |

> La asesora de venta (P8) y el panel completo de la dueña (P7) siguen siendo
> alcances de etapas futuras: aparecen en este documento únicamente en la tabla
> de trazabilidad (§13), para que el hilo quede completo desde hoy. El admin ya
> existe como actor desde esta etapa — vía el rol de su cuenta —, pero su
> herramienta de trabajo (el panel) se construye en la etapa 4.

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

### Cuentas de clientas (soportan P5)
- **RF-06:** El sistema debe permitir crear una cuenta de clienta con un email y una contraseña; si el email ya tiene cuenta, debe rechazar el registro con un mensaje claro que invite a iniciar sesión. *(AUTH-01, P5)*
- **RF-07:** El sistema debe permitir iniciar sesión con email y contraseña, y mantener la sesión iniciada entre recargas de la página — incluidas las recargas completas del navegador. *(AUTH-02, P5)*
- **RF-08:** El sistema debe ofrecer un endpoint de administración protegido por rol: las cuentas con rol admin acceden y las cuentas cliente reciben un rechazo de permiso; el rol viaja en la sesión desde el primer inicio. *(AUTH-03, P5)*
- **RF-09:** El sistema debe exigir sesión iniciada para ver el checkout; si la clienta llega sin sesión, debe llevarla a iniciar sesión y devolverla al checkout (o a la página de donde venía) tras autenticarse. *(AUTH-04, P5)*

### Carro de compras (soporta P5)
- **RF-10:** El sistema debe permitir agregar productos al carro desde la ficha, editar las cantidades de cada aroma y vaciar el carro por completo. *(CART-01, P5)*
- **RF-11:** El sistema debe hacer que el carro persista en el navegador del cliente: sobrevive recargas y cierres del navegador, sin exigir cuenta. *(CART-02, P5)*

---

## 5. Requerimientos no funcionales (RNF)

| Código | Categoría | Descripción | Origen |
|---|---|---|---|
| RNF-01 | Usabilidad | La tienda es usable desde el celular: nada exige pantalla ancha y los controles (filtros, enlaces) tienen tamaño táctil suficiente | C3, C4, CS4 |
| RNF-02 | Rendimiento | La tienda responde rápido en modo local de desarrollo: la primera carga del catálogo muestra los datos ya sembrados, sin esperas largas | P3, CS1 |
| RNF-03 | Operación | Todo el recorrido de esta etapa funciona **sin cuenta**: landing, catálogo y fichas son públicos para el visitante | §2 alcance (P1) |
| RNF-04 | Mantenibilidad | Los datos demo son **reproducibles**: cargarlos dos veces deja el catálogo idéntico (sin duplicados), y el catálogo de esta etapa es de solo lectura — nadie modifica datos desde la tienda | P4, CS3, RN-04 |
| RNF-05 | Seguridad | Las contraseñas se transforman (hash) **solo en el servidor**, con un algoritmo moderno de hash lento (Argon2); el secreto que firma las sesiones vive en una variable de entorno del backend — jamás en el código ni escrito en la guía | P5, RN-05..RN-07 |
| RNF-06 | Almacenamiento | La sesión iniciada y el carro de compras persisten en el **propio navegador del cliente** (localStorage): sobreviven recargas y cierres del navegador sin depender del servidor | P5, CART-02, RF-11 |

---

## 6. Reglas de negocio (RN)

- **RN-01:** La familia aromática de un producto pertenece a una lista cerrada de cuatro valores: `citricas`, `florales`, `frutales` o `dulces`, escritos **sin acentos** en el intercambio de datos; la pantalla muestra la etiqueta con acento ("Cítricas"). Cualquier otro valor se rechaza. *(P2; origen técnico: los acentos en los filtros viajan por la dirección de la página y la ensucian — detalle resuelto en la fase 3.)*
- **RN-02:** El precio es un **entero en pesos chilenos (CLP)**, sin decimales, dentro del rango **$6.990–$12.990** del catálogo demo. *(P3, C4)*
- **RN-03:** La imagen de cada producto es un **archivo local** del proyecto, referenciado como `/products/{sku}.jpg`; la tienda no depende de fotos alojadas en servicios externos. *(P2, P3)*
- **RN-04:** El catálogo de esta etapa es de **solo lectura**: la tienda solo consulta productos; crear, editar y desactivar llegan con el panel de administración de la etapa 4. *(§2 alcance)*
- **RN-05:** La contraseña de una cuenta debe tener un **largo mínimo de 8 caracteres, sin reglas de composición obligatoria**: no se exige mayúscula, número ni símbolo. La recomendación actual en seguridad (NIST) privilegia la **longitud sobre la complejidad**: las reglas de composición producen contraseñas predecibles ("Clave2026!") y frustran a las clientas más de lo que frenan a un atacante, mientras que cada carácter extra multiplica el costo de adivinar la contraseña por fuerza bruta. *(P5; decisión de la etapa 2 — D-25.)*
- **RN-06:** El login fallido responde siempre con un mismo error genérico (401, "Credenciales incorrectas") **sin revelar si el email tiene cuenta**, mientras que el registro con un email ya usado responde con claridad que ese email ya tiene cuenta (409). La asimetría es deliberada: saber si un email existe no le sirve a quien se está registrando (el sistema se lo dice), pero sí a quien está intentando entrar en cuenta ajena (el sistema calla). *(P5; decisión de la etapa 2 — D-26.)*
- **RN-07:** El hash de la contraseña **jamás cruza la frontera de la API**: se calcula y se guarda en el servidor al crear la cuenta, y ninguna respuesta del sistema lo incluye — ni al perfil de la clienta, ni a la administración, ni por error. *(P5, RNF-05.)*
- **RN-08:** El carro guarda **solo identificadores de producto y cantidades**; el nombre y el precio que se muestran se consultan siempre al catálogo vigente. Un precio guardado en el carro sería un precio viejo esperando el momento de engañar a la clienta (y a la tienda). *(P5; decisión de la etapa 2 — D-27.)*
- **RN-09:** Las cantidades visibles del carro se **tapan al stock vigente**: la pantalla nunca muestra (ni deja confirmar) más unidades de las que hay disponibles. Es la primera barrera contra la sobreventa en pantalla; la barrera definitiva — el backend que valida al crear la orden — llega en la etapa 3. *(P5; decisión de la etapa 2 — D-30.)*

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

### HU-05 — Crear una cuenta
*Como* clienta, *quiero* crear una cuenta con mi email y una contraseña, *para* guardar mis datos de compra y llegar al checkout con mi identidad lista.
- **Dado** que estoy en la pantalla de registro con un email que aún no tiene cuenta,
  **Cuando** envío el formulario con un email válido y una contraseña de al menos 8 caracteres (RN-05),
  **Entonces** mi cuenta se crea con rol de clienta y el sistema me lleva a iniciar sesión.
- **Dado** que el email con el que intento registrarme ya tiene cuenta,
  **Cuando** envío el formulario de registro,
  **Entonces** el sistema me responde con claridad que ese email ya tiene cuenta y me invita a iniciar sesión (RN-06).

### HU-06 — Iniciar sesión y mantener la sesión
*Como* clienta, *quiero* iniciar sesión con mi email y contraseña, *para* que la tienda sepa quién soy hasta que yo decida cerrar la sesión.
- **Dado** que tengo una cuenta y estoy en la pantalla de login,
  **Cuando** ingreso mis credenciales correctas,
  **Entonces** inicio sesión y el sistema me devuelve a la página donde iba (si venía de una protegida).
- **Dado** que ya inicié sesión,
  **Cuando** recargo la página o cierro y vuelvo a abrir el navegador,
  **Entonces** sigo con la sesión iniciada, sin volver a escribir mis credenciales (RF-07).
- **Dado** que envío el login con una contraseña incorrecta (o un email sin cuenta),
  **Cuando** el sistema valida las credenciales,
  **Entonces** recibo siempre el mismo mensaje genérico de credenciales incorrectas, sin pistas sobre si el email existe (RN-06).

### HU-07 — Armar un carro que me acompaña
*Como* visitante, *quiero* agregar aromas al carro desde su ficha, editar cantidades y vaciarlo cuando quiera, *para* comprar en varios pasos sin perder lo que elegí.
- **Dado** que estoy en la ficha de un aroma con stock disponible,
  **Cuando** presiono "Agregar al carro",
  **Entonces** el contador del carro aumenta y el aroma queda guardado con su cantidad.
- **Dado** que tengo aromas en el carro,
  **Cuando** recargo la página o vuelvo en otra visita,
  **Entonces** mi carro sigue igual: lo que guardé no se pierde (RF-11).
- **Dado** que quiero editar lo que llevaba,
  **Cuando** cambio cantidades, quito un aroma o vacío el carro,
  **Entonces** el carro y su total se actualizan al momento — y vaciar exige una confirmación en dos pasos, porque borra todo de una vez.

### HU-08 — Llegar al checkout con mi sesión
*Como* clienta, *quiero* que el checkout exija sesión iniciada, *para* que mi pedido quede asociado a mi cuenta.
- **Dado** que llego al checkout sin sesión iniciada,
  **Cuando** intento ver el resumen de mi pedido,
  **Entonces** el sistema me lleva a iniciar sesión recordando a dónde iba.
- **Dado** que estoy en el login porque el checkout me lo pidió,
  **Cuando** completo mis credenciales correctamente,
  **Entonces** vuelvo automáticamente al checkout con mi resumen listo para el pago (que llega en la etapa siguiente).

---

## 8. Modelo de datos preliminar (insumo para la fase de diseño)

| Entidad | Atributos clave | Relaciones |
|---|---|---|
| **Producto** | id, sku (único), nombre, descripcion, precio (entero CLP, RN-02), stock, familia (lista cerrada de 4 valores, RN-01), notas aromáticas (lista), activo, imagen (ruta local, RN-03) | Sin relaciones en esta etapa; los pedidos de la etapa 3 se conectarán a esta entidad (las cuentas de la etapa 2 viven sin relaciones: el carro es del navegador, no de la base de datos) |
| **Usuario** | id, email (único), hash de la contraseña (jamás en respuestas, RN-07), rol cliente/admin (RF-08) | Sin relaciones en esta etapa; los pedidos de la etapa 3 conectarán usuarios con productos |

> *La decisión de datos más importante de esta etapa: el **sku** es la clave
> natural estable del catálogo demo — la siembra idempotente (RF-05) se apoya
> en él para actualizar sin duplicar. Se desarrolla en la fase de diseño (03).*
>
> *La decisión equivalente de la etapa 2: el **email** es la clave natural de
> las cuentas — la siembra de credenciales demo se apoya en él igual que la del
> catálogo en el sku.*

---

## 9. Procesos principales (insumo para DFD en diseño)

1. **Explorar el catálogo:** visitante → abre la tienda → página de inicio → catálogo → grilla completa.
2. **Filtrar el catálogo:** visitante → elige familia y/o rango de precio → el sistema acota la grilla y cuenta los resultados.
3. **Ver la ficha:** visitante → selecciona un producto → el sistema muestra descripción, notas y disponibilidad (o producto no encontrado).
4. **Sembrar datos demo (proceso interno):** desarrollador → ejecuta la siembra → el sistema crea o actualiza cada producto por sku → catálogo en estado conocido.
5. **Crear cuenta:** clienta → completa el registro (email y contraseña) → el sistema valida (RN-05), guarda la cuenta y la lleva a iniciar sesión (HU-05).
6. **Iniciar sesión:** clienta/admin → envía credenciales → el sistema verifica contra el hash guardado y entrega una sesión que persiste en el navegador (HU-06).
7. **Armar y editar el carro:** visitante → agrega desde la ficha, edita cantidades, quita o vacía → el carro persiste en su navegador solo con ids y cantidades (HU-07).
8. **Ver el checkout protegido:** clienta → pide el resumen del pedido → el sistema exige sesión y la devuelve al checkout tras autenticarse (HU-08).

---

## 10. Entradas del sistema (formularios y validaciones)

| Entrada | Actor | Validaciones clave |
|---|---|---|
| Filtro por familia | Visitante | Familia ∈ {citricas, florales, frutales, dulces} (RN-01); cualquier otro valor se rechaza |
| Rango de precio | Visitante | Enteros ≥ 0; mínimo no mayor que el máximo efectivo de resultados esperados |
| Enlace a ficha | Visitante | Identificador de producto existente y activo; si no, pantalla de no encontrado (HU-03) |
| Formulario de registro | Clienta (nueva) | Email con formato válido; contraseña de mínimo 8 caracteres, sin composición obligatoria (RN-05); email ya registrado → rechazo claro que invita a iniciar sesión (RN-06) |
| Formulario de login | Clienta / Admin | Email con formato válido; contraseña; credenciales incorrectas → mensaje genérico sin revelar si el email existe (RN-06) |

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
3. **Ficha de producto:** imagen grande, datos completos, notas aromáticas, disponibilidad y (desde la etapa 2) la acción de agregar al carro.
4. **Inicio de sesión (login):** tarjeta con email y contraseña, avisos de sesión expirada y de cuenta creada, y retorno a la página protegida de donde vino la clienta.
5. **Registro de cuenta:** tarjeta con email y contraseña (mínimo 8 a la vista), validación en pantalla y rechazo claro si el email ya tiene cuenta.
6. **Carro:** filas por aroma con edición de cantidades, quitar y vaciar en dos pasos, y panel de resumen con el total y la acción de finalizar la compra.
7. **Checkout (protegido):** resumen del pedido con líneas y total hidratados con precios vigentes, subtítulo con la cuenta activa y la acción de pago deshabilitada hasta la etapa siguiente.

---

## 13. Trazabilidad: necesidad → requerimiento

El hilo completo del ciclo de vida. **Ninguna petición queda sin requerimiento y ningún requerimiento nace de la nada.**

| Necesidad (doc 01) | Se convierte en | Se verifica con |
|---|---|---|
| P1 Tienda online propia | RF-01, RF-02, RNF-03 | HU-01, CS4 |
| P2 Catálogo ordenado por familias | RF-02, RF-03, RN-01, RN-03 | HU-01, HU-02, CS1 |
| P3 Ficha completa por producto | RF-04, RN-02 | HU-03, CS2 |
| P4 Datos de prueba sin duplicar | RF-05, RNF-04 | HU-04, CS3 |
| P5 Carro y cuentas | RF-06..RF-09 (cuentas: AUTH-01..04), RF-10, RF-11 (carro: CART-01..02), RNF-05, RNF-06, RN-05..RN-09 | HU-05, HU-06, HU-07, HU-08 |
| P6 Pago online con Webpay | *(sin requerimiento en esta etapa — etapa 3: CART-03 y PAY-01..04)* | Etapa 3 |
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

**Etapa 1 — catálogo público (documentada el 2026-09-28):**

| Rol | Nombre | Decisión | Fecha |
|---|---|---|---|
| Analista | ______________ | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |
| Cliente (validación de requerimientos) | Maura — Maura · Body Splash | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |

**Etapa 2 — cuentas de clientas y carro persistente (documentada el 2026-09-29):**

| Rol | Nombre | Decisión | Fecha |
|---|---|---|---|
| Analista | ______________ | ☐ Aprobado ☐ Con observaciones | 2026-09-29 |
| Cliente (validación de requerimientos) | Maura — Maura · Body Splash | ☐ Aprobado ☐ Con observaciones | 2026-09-29 |

> **Nota para la clase:** este documento es el contrato de QUÉ hace el sistema
> (en esta etapa), jamás de CÓMO se construye. El CÓMO lógico arranca en la
> fase 3 (`03_diseno.md`): modelo de datos detallado, diagramas de procesos
> (DFD) y prototipo de pantallas; sigue en la fase 4 con las decisiones de
> arquitectura (ADRs) y el contrato del intercambio de datos. Misma estructura
> que el proyecto hermano demo-cine: los alumnos pueden contrastar ambos
> documentos y ver la misma mecánica de trazabilidad en un dominio distinto.
