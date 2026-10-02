# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.25.0 — Guía Completa

**Shipped:** 2026-10-02
**Phases:** 5 | **Plans:** 29 | **Sessions:** 5 días de ejecución (2026-09-28 → 2026-10-02, 284 commits)

### What Was Built
- Guía educativa completa del ciclo de vida del software para la tienda de body splash de
  MAURA: docs 01-08 del ciclo, 18 guías de desarrollo paso a paso, 20 ADRs y contrato API
  0.4.0 — las 8 filas del recorrido en ✅ Listo en las tres portadas.
- Recorrido e-commerce operativo de punta a punta: catálogo con filtros, carro persistente,
  cuentas JWT, checkout Webpay Plus sandbox con los 4 flujos de retorno discriminados,
  órdenes con stock atómico, panel admin con máquina de estados y asistente IA (Groq,
  mini-RAG sobre el catálogo real, API key solo backend).
- Despliegue free tier enseñado de punta a punta (Vercel Hobby + Render Free, ADRs
  019/020) con triple congelado de URLs/CORS y seed idempotente contra disco efímero.

### What Worked
- **API-first por fase (D-15):** contrato + ADRs aprobados ANTES de redactar guías, con docs
  02/03 en paralelo por archivos disjuntos — las 5 fases cerraron sin rework de contrato.
- **Spike antes de firmar (D-38/D-41):** el retorno de Webpay se corroboró runtime antes de
  escribir contrato/ADRs/guías — la corrección material (anulado llega por GET) se firmó con
  evidencia, no con supuestos.
- **UAT delegado al agente (maura-uat):** las guías se ejecutan literales en un taller
  aparte con la regla "fix en los dos lugares" (guía + taller) — 4 fases de UAT runtime sin
  cuello de botella del usuario y con bugs corregidos donde viven.
- **Decisiones numeradas con evidencia (D-01..D-73):** cada decisión cita su fuente (probe
  runtime, doc oficial, README del SDK a versión pinneada) — el swap Gemini→Groq y el cierre
  D-73 fueron auditables línea a línea.
- **Gates documentales replicables:** conteos de guías/ADRs, cadena Siguiente
  grep-verificada e invariant guide-only (`git ls-files` vacío) cantados en cada cierre de
  fase contra corpus verificado.

### What Was Inefficient
- **Corrección de alcance a mitad de la fase 1 (D-17):** el backend se construyó primero y
  se retiró (commits 364dee6/de0253e) cuando el usuario corrigió el alcance a guide-only —
  los planes 01-03..01-07 se reemplazaron por planes docs-only. El descubrimiento tardío
  costó una replanificación completa de la fase.
- **Muro de billing de Google descubierto en UAT (fase 4):** el rework Gemini→Groq
  (D-63..D-68, 3 planes R1-R3 + re-verificación) nació de un 402 real con keys nuevas — la
  investigación inicial no probó la EMISIÓN de keys, solo la API. Probar la cuenta desde el
  día 1 lo habría evitado.
- **Vocabulario de estados entre artefactos:** `04-UAT.md` quedó con `status: pass` mientras
  las demás fases usaban `complete` — el falso positivo del audit-open del cierre recién lo
  destapó. Los scanners son exigentes con el vocabulario del frontmatter.
- **Staleness estructural de verificaciones:** el modelo guide-only comparte corpus
  (READMEs de estado, series de docs/02-03), así que cada fase re-stalea las verificaciones
  anteriores por diseño — el cierre requirió override documentado en vez de verified_closeout.

### Patterns Established
- Estructura canónica de guía (blockquote/terminos/pasos con piensa+mini-verificación/error
  evitado/cierre) y la "Gran verificación final" como fila contrato ↔ /docs por fase.
- Regla de fixes en dos lugares (guía + taller maura-uat) — autorizada por el usuario como
  política persistente.
- Supersede con cuerpo byte-intacto (ADR-017 → ADR-018) para reworks que preservan historia.
- Series sin renumerar: cada fase EXTiende RF/RN/HU/pantallas/decisiones en vez de insertar.

### Key Lessons
1. Verificar la EMISIÓN de credenciales (no solo la API) antes de construir guías alrededor
   de un servicio externo — el costo real de un proveedor se descubre al crear la key.
2. En repos guide-only con corpus compartido, el digest de verificación por fase caduca por
   diseño — o se re-verifica todo al cierre, o se documenta el override con la razón.
3. El frontmatter de los artefactos de planning es un contrato con los scanners: un status
   fuera de vocabulario (`pass` vs `complete`) bloquea gates de cierre.
4. Delegar el UAT al agente con taller separado y regla de espejo convierte la verificación
   en un subproducto de la ejecución — 4 fases de UAT runtime sin esperar al usuario.

### Cost Observations
- Model mix: no medido por modelo (model_profile inherit; subagentes gsd-* estándar)
- Sessions: ejecución continua 2026-09-28 → 2026-10-02 (284 commits, 29 planes, ~59 tareas)
- Notable: la fase más cara fue la 4 (8 planes: 5 + 3 de rework Groq) y la 3 incluyó un spike
  de 60 min que amortizó todo el riesgo del retorno de Webpay

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v2.25.0 | 5 días continuos | 5 | Primer milestone: establece formato guide-only, UAT delegado y API-first por fase |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v2.25.0 | UAT delegado runtime por fase (fases 1-4 construidas en taller; fase 5 cierre documental D-73) + SECURITY por fase (threats_open 0) | n/a (repo guide-only) | 0 |

### Top Lessons (Verified Across Milestones)

1. *(primer milestone — pendiente de validación cruzada)*
2. *(primer milestone — pendiente de validación cruzada)*
