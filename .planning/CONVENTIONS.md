# Conventions

## Guías de desarrollo (`docs/05_desarrollo/`)

Reglas de escritura establecidas tras UAT de las guías 1–4 (sesión
2026-10-02, workspace `maura-uat`):

1. **Archivo modificado = código completo.** Cuando una guía pide modificar
   un archivo que ya existe (p. ej. registrar un router en `app/main.py`),
   mostrar el archivo final completo tal como queda en ese punto de la
   secuencia — jamás fragmentos sueltos ("agrega esta línea", "el import
   junto a los existentes"). El alumno debe poder reemplazar el archivo
   entero sin inferir dónde va cada pieza.
2. **El estado mostrado es el acumulado.** El archivo completo de una guía
   refleja todo lo construido hasta esa guía (routers registrados, versión
   del contrato, CORS vigente), en el orden canónico de la secuencia.
3. **El build siempre verde (revisada 2026-10-21).** Al terminar CADA
   paso, el proyecto debe compilar (`npm run build` / `tsc -b` en verde).
   Ninguna mini-verificación puede tener como resultado esperado un build
   que falla por el estado del proyecto: prohibido importar o rutear
   (p. ej. en `main.tsx`) un archivo que la guía crea en un paso POSTERIOR.
   Orden seguro: piezas (componentes presentation) → pantalla → cableado
   de rutas (ver guia-10 pasos 3-5 tras el fix D-4). Los prompts
   interactivos de herramientas SÍ se siguen advirtiendo antes de que
   aparezcan. La única caída de build permitida es un experimento puntual
   que la propia guía manda deshacer dentro del mismo paso (como el
   "experimento del compilador" de guia-10 paso 1), dejando el proyecto
   en verde al cerrar el paso.
4. **Instrucciones accionables literales.** Cada acción nombra su objetivo
   con ruta completa (`src/features/catalogo/Catalogo.tsx`), y cuando hay
   que crear varios archivos, van numerados uno por uno con su contenido
   íntegro — no listados compactos con formato flecha que el alumno debe
   descifrar.
