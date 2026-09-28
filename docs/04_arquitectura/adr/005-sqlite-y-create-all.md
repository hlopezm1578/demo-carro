# ADR-005 — SQLite con create_all + seed idempotente (Alembic diferido)

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo persistir el almacén D1 del diseño (§3.2) en la fase 1 — motor, creación de tablas y camino de crecimiento

## Contexto

La fase 1 guarda una sola entidad (PRODUCTO, diseño §2) con datos demo
reproducibles: la siembra es idempotente por sku (RF-05, RNF-04) y re-ejecutarla
restaura el estado conocido. La clienta exige presupuesto mínimo (C1) y la guía
debe funcionar en el notebook de cualquier alumno sin instalar servidores. Las
cuentas y pedidos que SÍ harán valiosos los datos llegan recién en las etapas 2
y 3.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. PostgreSQL desde el inicio** | Concurrencia y tipos reales de producción desde el día 1 | Exige un servidor (local o nube) antes de tener más que 12 filas demo; frena la primera guía |
| **B. SQLite con `create_all` + seed idempotente** | Cero instalación: un archivo; el ORM abstrae el motor; la BD demo es desechable y resembrable | Sin migraciones versionadas al inicio; no simula la concurrencia de un motor real |
| **C. MySQL** | Motor muy difundido | Vetado para este proyecto (What NOT to Use): sin ventaja en este alcance y agrega un servidor que administrar; no es el camino de crecimiento documentado |

## Decisión

**Opción B.** La fase 1 usa **SQLite** con `Base.metadata.create_all` al
arrancar + el script de siembra idempotente: la BD es desechable y la siembra
la devuelve siempre al estado canónico de 12 aromas.

**Advertencia honesta (hay que enseñarla explícita):** `create_all` **no
altera tablas ya creadas** — crea las que faltan y no toca las existentes. Por
eso **Alembic (migraciones versionadas) entra diferido**: recién cuando un
cambio de schema toque datos existentes — las cuentas de la etapa 2 o los
pedidos de la etapa 3. Hasta ese momento, cambiar el modelo implica borrar el
archivo de BD y resembrar (aceptable solo porque los datos no importan aún).

**Camino de crecimiento:** pasar a PostgreSQL (o cualquier motor) es cambiar
una sola línea — la URL de SQLAlchemy en `Settings` (`DATABASE_URL`). El
código de modelos, repositorios y servicios no cambia: esa es la ventaja del
ORM (ADR-001).

## Consecuencias

**Positivas**
- La primera guía del backend corre en cualquier máquina sin instalar nada: el motor es un archivo.
- La siembra restaura el estado demo tras cualquier prueba — reproducibilidad total (CS3, RNF-04).
- La demo en vivo de "cambiar la URL y cambiar de motor" es la lección de abstracción del ORM.

**Negativas (honestas)**
- Sin migraciones versionadas al inicio: mientras la BD sea desechable se vive borrando y resembrando; el día que los datos importen, ese hábito se paga — por eso Alembic tiene fecha de entrada definida.
- SQLite no ejercita concurrencia ni tipos específicos de Postgres: un código que funciona en aula puede fallar bajo carga real — aceptable en la etapa de catálogo de solo lectura (RN-04).

## Para conversar en clase

1. ¿Qué cambia el día que los datos dejan de ser desechables? (pista: una clienta registrada no se re-siembra).
2. ¿Por qué la siembra hace upsert por sku y no borra y reinserta todo? (pista: qué pasa con los pedidos de la etapa 3 que apuntan a productos, y con los ids).
3. Nombren una prueba que pasaría en PostgreSQL y podría fallar (o engañar) en SQLite. ¿Cómo la detectarían temprano?
