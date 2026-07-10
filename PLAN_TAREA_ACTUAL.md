# Plan de tarea en curso — bug de formato Pandera + feature de metadata por columna

> Tarea anterior (UI/menú desplegable/READMEs) completada íntegramente — ver
> historial de commits/conversación si se necesita ese contexto. Este archivo
> ahora trackea la tarea nueva.

## Prompt original del usuario (verbatim)

> hay un bug en el formato de los pandera debido a una actualización, mira la
> forma de declarr ahora sobretodo con comparativos numéricos, [YAML de ejemplo
> con `version: 0.24.0`, `strict: filter`, checks como
> `str_matches: '^EMP-\d{4}$'`, `isin: [...]`, `greater_than_or_equal_to:
> 30000.0` directamente bajo `checks:` sin anidar en un sub-dict de parámetro]
> realiza los ajustes la interface web unicamente, agrega un nuevo feature,
> para editar un tag metadata en cada columna para almacenar principalmente la
> unidad de medición y descripción. Esta metadata se agregará al dar clic en
> un boton, por default apareceran cuadros de texto para la metric y para la
> descripción (este es texto largo), se conserva el mecanismo de guardado.
> Analiza mi petición, analiza el código para solventarla, realiza la
> planeación de la intervención, ejecutala, haz las pruebas y no hagas otra
> iteración, genera un reporte para que yo planee las siguientes etapas si
> encuentras bugs graves, si son sencillos sí resuelvelos. Estaré ausente
> entonces ejecuta lo que tengas que ejecutar sin preguntarme. Haz una lista
> de tareas que tengas que realizar, ve marcando tu avance de acuerdo a como
> lo vayas realizando en esa lista.

**Alcance explícito**: solo la versión web (`pandera_scheme_editor_web/`); no
tocar la versión GTK. Una sola pasada (sin iterar de más). Bugs graves →
reportar; bugs simples → resolver directamente.

## Investigación previa a la intervención (hallazgos)

1. **Bug confirmado (el reportado)**: Pandera moderno serializa los checks de
   un solo parámetro (comparadores numéricos `greater_than[_or_equal_to]`/
   `less_than[_or_equal_to]`, `str_matches`, `isin`) como un valor escalar/lista
   directo bajo `checks:` (ej. `greater_than_or_equal_to: 30000.0`), no como
   `{param_name: value}` anidado. Verificado empíricamente con el Pandera
   0.32.1 instalado en este entorno (`schema.to_yaml()` real) y contra el
   código fuente de Pandera (`pandera/io/_flat_checks.py`): los checks con
   exactamente un "stat" se colapsan a escalar/lista; los de más de un stat
   (ej. `str_length`) siguen como dict. Nuestro editor solo sabía leer la
   forma dict — al abrir un check existente en forma escalar para editarlo,
   `check_payload_edit_view` lo trataba como payload vacío (`{}`), mostrando
   el campo en blanco en vez del valor real.
   - **No es un bug de escritura/round-trip**: Pandera's `from_yaml` acepta
     igual de bien la forma dict anidada (confirmado leyendo
     `unflatten_component_checks_dict`/`flat_value_to_list_entry` en el
     código fuente de Pandera) — por eso next el fix también hace que el
     guardado emita la forma escalar/lista moderna para checks de un solo
     campo, en vez de solo tolerar la lectura.
2. **Hallazgo relacionado, NO en el YAML de ejemplo del usuario pero real**:
   Pandera instalado aquí en realidad ya no envuelve los checks bajo una
   clave `checks:` en absoluto — los aplana como hermanos directos de
   `dtype` en la columna. El YAML que pegó el usuario todavía tiene `checks:`
   como clave contenedora. Se reporta como hallazgo para una futura
   iteración (no se implementa soporte para el formato 100% plano sin
   `checks:`, fuera del alcance pedido).
3. **Hallazgo relacionado, no se arregla en esta pasada (no es "sencillo")**:
   `strict: filter` (string, uno de los 3 valores válidos de Pandera) se
   pierde si el usuario visita "Globales" y aplica cambios, porque
   `GlobalsForm`/`set_global_strict` solo maneja booleano. Se deja para
   reporte.
4. Los otros cambios estructurales del YAML de ejemplo (`index:` como lista,
   `checks:` de nivel raíz para reglas multi-columna, `version:`) no tocan
   nada que el dominio actual lea o escriba — pasan intactos (el árbol YAML
   se preserva tal cual salvo lo que se edita explícitamente).

## Plan de ejecución

- [x] 1. Confirmar el bug empíricamente (Pandera real instalado + código
      fuente de Pandera) y decidir alcance de la corrección.
- [ ] 2. `pandera_core/domain/payload_fields.py`: agregar `normalize_payload`
      (lectura: escalar/lista → dict de campos nombrados) y `collapse_payload`
      (escritura: dict de un solo campo → escalar/lista, igual que el
      Pandera moderno; checks multi-campo como `str_length` se quedan dict).
- [ ] 3. `pandera_core/domain/contract.py`: `ColumnContract.set_check` acepta
      cualquier valor serializable (no solo dict) — quitar el cast forzado
      `dict(payload)`.
- [ ] 4. `schema_editor/views/checks.py`: usar `normalize_payload` al abrir el
      editor de un check existente; usar `collapse_payload` al guardar
      (agregar y editar).
- [ ] 5. Feature de metadata — dominio: `ColumnContract.metadata` (property),
      `set_metadata(unit, description)`, `clear_metadata()` en `contract.py`.
      Se guarda como `metadata: {unit: ..., description: ...}` en la columna;
      Pandera ignora claves desconocidas al leer (verificado en su código
      fuente), así que no rompe compatibilidad.
- [ ] 6. `ColumnMetadataForm` (unit + description/Textarea) en `forms.py`.
- [ ] 7. Nueva vista `schema_editor/views/metadata.py`
      (`metadata_save_view`, `metadata_delete_view`), reutilizando
      `load_contract_or_error`/`save_checkpoint` (mismo mecanismo de guardado
      que todo lo demás).
- [ ] 8. Rutas nuevas en `urls.py`.
- [ ] 9. `_metadata_panel.html` (nuevo, con `<details>` nativo: botón
      "Agregar/Editar metadata" que revela los dos cuadros de texto; abierto
      por defecto si ya hay metadata) + incluir en `column_detail.html` + CSS
      `.disclosure` en `style.css`.
- [ ] 10. Probar con un YAML que reproduzca el formato del usuario (checks
      escalares numéricos, `isin` como lista, `str_matches` como string) vía
      el flujo HTTP real: leer, editar, guardar, agregar/editar/eliminar
      metadata, checkpoint y save-as intactos.
- [ ] 11. Reporte final (bugs graves encontrados vs. resueltos; qué quedó
      fuera de alcance a propósito).

## Avance real

- [x] 2. `normalize_payload`/`collapse_payload` agregados en `payload_fields.py`.
- [x] 3. `ColumnContract.set_check` acepta `Any` (dict, escalar o lista).
- [x] 4. `checks.py` normaliza al leer/editar y colapsa al escribir (agregar y
      editar). Confirmado con pruebas HTTP reales: `greater_than_or_equal_to`,
      `isin`, `str_matches` muestran su valor real al editar y se reescriben
      en forma escalar/lista; `str_length` (multi-campo) se mantiene como dict.
- [x] 5-9. Feature de metadata completa: dominio, form, vista, rutas,
      plantilla + CSS. Probado: agregar, ver precargado con `<details open>`,
      editar, eliminar — todo vía checkpoint automático existente.
- [x] 10. Probado end-to-end contra un servidor real con un YAML que
      reproduce exactamente el ejemplo del usuario. Además se hizo
      round-trip real contra Pandera 0.32.1 instalado (`DataFrameSchema.
      from_yaml`) sobre el archivo que nuestra herramienta genera — carga
      correctamente y reconstruye los `Check` esperados.
  - **Hallazgo grave, fuera de nuestro control**: el YAML de ejemplo del
    usuario, TAL CUAL (antes de que nuestra herramienta lo toque), ya falla
    al cargarlo con `pandera.DataFrameSchema.from_yaml()` en la versión de
    Pandera instalada aquí (0.32.1) con `KeyError: 'options'`, causado por el
    bloque `checks:` de nivel raíz (`name`/`check_fn` como lambda-string) —
    aislado y confirmado que NO es el `index:` ni nada que edite nuestra
    herramienta. Nuestro dominio nunca lee/escribe ese bloque (pasa intacto),
    así que no es algo que podamos arreglar desde el editor; ver reporte.
- [x] 11. Reporte final entregado en el chat.

Tarea completa.
