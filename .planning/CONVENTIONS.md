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
3. **Advertir los errores esperados.** Si un paso produce errores
   transitorios por diseño (imports de archivos que se crean más abajo,
   prompts interactivos de herramientas), el paso debe decirlo ANTES de que
   el alumno los vea: qué aparecerá, por qué, y cuándo desaparece.
4. **Instrucciones accionables literales.** Cada acción nombra su objetivo
   con ruta completa (`src/features/catalogo/Catalogo.tsx`), y cuando hay
   que crear varios archivos, van numerados uno por uno con su contenido
   íntegro — no listados compactos con formato flecha que el alumno debe
   descifrar.
