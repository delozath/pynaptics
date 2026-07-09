# Plan de tarea en curso — UI web + READMEs

> Este archivo existe para poder retomar la tarea en otra sesión si se interrumpe.
> Se va marcando el avance con [x] conforme se completa cada paso.

## Prompt original del usuario (verbatim)

> excelente, analiza el codigo en la versión web y hazlo más usable por ejemplo con
> menús desplegables y visualemente más atractivo, pero conservando el minimalismo.
> Te faltó generar el markdown README.md de esta versión, en donde incluyas un
> tutorial de instalación, como se usa y además descripción tecnica para los
> desarrolladores. haz lo mismo para readme de la versión gtk (eso es lo único
> que se modifica de esa versión), realiza un readme global para la descripción
> de ambos desarrollos, pero sin tanto detalle solo características generales.
> Analiza mi petición realiza el plan y alamacena en un documento de texto el
> prompt y plan que seguiras en ese plan iran marcando el avance, esto es por si
> no se completa la acción y tengo que retomar, tu sepas el contexto y en qué te
> quedaste. tambien ejecuta sin preguntar

## Contexto previo relevante

- `pandera_scheme_editor/`: versión GTK (arquitectura hexagonal), ya tiene un
  `README.md` completo. Solo se debe **revisar/actualizar ese README**, sin tocar
  código.
- `pandera_scheme_editor_web/`: versión Django (reimplementación de la misma
  lógica de dominio en `pandera_core/`, sin trackear en git aún). Ya se corrigió
  en esta misma sesión un bug de acumulación de checkpoints en
  `schema_editor/views/common.py::load_contract_or_error` (ahora prefiere el
  checkpoint existente sobre el original) y se agregó la vista/ruta
  `resume/discard/` para que "No, partir del original" borre realmente el
  checkpoint. No hay `requirements.txt` ni `README.md` en este proyecto todavía.
- No existe README global en la raíz de `pynaptics-tools/`.

## Plan de ejecución

- [x] 1. Escribir este documento de plan.
- [x] 2. Rediseñar `schema_editor/static/schema_editor/css/style.css`: paleta
      refinada, componente de menú desplegable (`<details>`), chips para checks
      activos, formularios/botones más pulidos, mejor jerarquía visual, modo
      oscuro afinado — conservando el minimalismo (sin frameworks, sin CDN).
- [x] 3. Consolidar acciones de cabecera del editor (`editor_base.html`) en un
      menú desplegable nativo, dejando "Guardar como…" visible como acción
      principal y agrupando "Globales"/"Cambiar archivo" en el desplegable.
- [x] 4. Activar la vista previa instantánea de plantillas en
      `template_picker.html` (los datos `template-data` ya se embebían sin
      usarse) con JS vanilla mínimo en un nuevo `static/schema_editor/js/app.js`,
      con fallback `<noscript>` intacto.
- [x] 5. Crear `pandera_scheme_editor_web/requirements.txt` (Django + PyYAML).
- [ ] 6. Escribir `pandera_scheme_editor_web/README.md` (instalación, tutorial de
      uso, descripción técnica para desarrolladores).
- [ ] 7. Revisar y actualizar `pandera_scheme_editor/README.md` (única
      modificación permitida en esa versión — sin tocar código).
- [ ] 8. Escribir `pynaptics-tools/README.md` global (alto nivel, sin detalle,
      enlaza a ambos proyectos).
- [ ] 9. Verificar la versión web: levantar servidor de desarrollo, recorrer el
      flujo (cargar YAML, editar propiedades/checks/plantillas con preview,
      probar el menú desplegable, guardar como), revisar el HTML/CSS resultante.
- [ ] 10. Limpiar artefactos de prueba generados durante la verificación y dejar
      resumen final al usuario.

## Avance real (se actualiza conforme se ejecuta)

- [x] 1. Plan escrito.
- [x] 2. `style.css` reescrito (paleta, menú `.menu`/`.menu-panel`, chips de
      checks activos, formularios/botones, dark mode).
- [x] 3. `editor_base.html`: acciones agrupadas en `<details class="menu">`
      ("Más" → Globales / Cambiar archivo), "Guardar como…" queda como botón
      primario visible.
- [x] 4. `static/schema_editor/js/app.js` creado; `template_picker.html` tiene
      los ids (`template-description`, `template-nullable-checkbox`) y el
      `<script>` que consume el `template-data` ya embebido.
- [x] 5. `requirements.txt` creado (Django>=5,<6 + PyYAML>=6).
- [x] 6. `pandera_scheme_editor_web/README.md` escrito (instalación, tutorial,
      técnico para desarrolladores).
- [x] 7. `pandera_scheme_editor/README.md`: corregido bloque de instalación
      roto (comandos fuera del fence), agregadas referencias cruzadas a la
      versión web y al README global. Sin tocar código GTK.
- [x] 8. `pynaptics-tools/README.md` global escrito.
- [x] 9. Verificado con `manage.py check` + contra el servidor de desarrollo que
      el usuario ya tenía corriendo en :8000 (no se tocó ese proceso ni su
      `examples/test-proc.yaml`): CSS/JS nuevos se sirven (200), el menú
      desplegable "Más" renderiza en `editor_base.html`, y `template_picker.html`
      trae los ids/script para la vista previa instantánea. Solo se hicieron
      peticiones GET de solo lectura sobre los datos de prueba del usuario.
- [x] 10. Limpieza de cookies/archivos temporales de esta verificación (en
      scratchpad, no en el repo). Tarea completa.

## Notas de avance

(se completa mientras se ejecuta)
