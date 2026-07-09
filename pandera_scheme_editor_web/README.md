# Pandera Schema Editor — versión web (Django)

Editor web para cargar un YAML generado por `pa.infer_schema(df).to_yaml(...)`,
modificar tipos, checks y plantillas por columna, y guardar un nuevo YAML
corregido sin sobrescribir el original. Es la reimplementación web — con Django
y sin JavaScript salvo un realce opcional (progresivo) — de
[`pandera_scheme_editor/`](../pandera_scheme_editor/README.md) (la versión de
escritorio en GTK).

## Alcance

Hace exactamente lo mismo que la versión GTK, más un mecanismo de guardado
incremental afinado para varias sesiones de navegador:

- Carga un YAML de esquema Pandera ya inferido (por ruta del servidor, desde
  un archivo del *workspace*, o subiéndolo).
- Muestra las columnas del YAML en una barra lateral.
- Permite editar propiedades de columna: `dtype`, `nullable`, `required`,
  `unique`, `coerce`, `regex`.
- Permite crear, editar y eliminar checks manuales, con el menú de "agregar
  check" adaptado al `dtype` de la columna (ver más abajo).
- Permite aplicar plantillas declarativas de validación frecuentes, con
  vista previa instantánea de la descripción/parámetros al cambiar de
  plantilla (mejora progresiva: sin JavaScript, sigue funcionando con un botón
  "Ver" que recarga la página).
- Permite editar propiedades globales: `strict`, `coerce`, `unique_column_names`.
- Guarda siempre con operación "Guardar como…"; nunca permite pisar el YAML
  original ni el checkpoint del que se derivó.
- Autoguarda progreso incremental en `{nombre}-proc.yaml` junto al original
  después de cada edición, acumulando todos los cambios de la sesión (no solo
  el último), y ofrece continuar o descartar ese progreso al recargar el
  mismo YAML.

Deliberadamente **no** hace: inferencia ni validación de Excel, reporte final,
orquestación de pipelines, ni depende de Pandera para editar el YAML — mismas
exclusiones que la versión GTK.

Es una herramienta de un solo operador local: no tiene autenticación ni
usuarios, y no está pensada para exponerse más allá de `localhost` (ver
`config/settings.py`).

## Instalación

Requiere Python ≥ 3.11.

```bash
cd pandera_scheme_editor_web
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` solo trae `Django` y `PyYAML` — no hay dependencia de GTK,
pandas ni Pandera en este proyecto.

## Ejecución

```bash
python manage.py migrate --run-syncdb   # crea db.sqlite3 (solo backend de sesiones, ver abajo)
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en el navegador.

### Variables de entorno opcionales

| Variable | Uso | Default |
|---|---|---|
| `DJANGO_DEBUG` | `1` para modo debug | `1` |
| `DJANGO_SECRET_KEY` | clave de firma de sesiones/CSRF | clave de desarrollo insegura |
| `SCHEMA_EDITOR_WORKSPACE_DIR` | carpeta que alimenta el selector "archivos del workspace" y donde se guardan los YAML subidos | `<proyecto>/examples/` |

### Sobre `db.sqlite3`

`django.contrib.sessions` está en `INSTALLED_APPS` únicamente para poder
mostrar los mensajes flash (los avisos de "Propiedades aplicadas", "Check
eliminado", etc.). Esa app necesita una tabla, y Django la respalda por
defecto con SQLite — de ahí el archivo que aparece al correr `migrate`. Si
prefieres no tener ese archivo, en `config/settings.py` cambia:

```python
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
```

y las sesiones viajan firmadas en la cookie sin necesitar base de datos ni
`migrate`.

## Tutorial de uso

1. **Cargar un YAML** — en la pantalla inicial, llena *una* de las tres
   opciones (tienen prioridad: archivo subido > ruta escrita > archivo del
   workspace) y pulsa **Cargar**.
2. **Progreso previo** — si ese YAML ya tiene un checkpoint guardado de una
   sesión anterior (`{nombre}-proc.yaml`), se pregunta si continuar desde ahí
   o partir del original. Elegir "partir del original" borra ese checkpoint
   de forma permanente.
3. **Editar una columna** — selecciónala en la barra lateral. Desde ahí:
   - **Propiedades de columna**: cambia `dtype` y las casillas, luego
     "Aplicar propiedades".
   - **Checks manuales**: el menú desplegable de "agregar check" solo ofrece
     los checks relevantes al `dtype` actual (p. ej. oculta `isin` en columnas
     `float64` continuas, pero lo ofrece en `int64`/texto/categóricas); el
     enlace "Mostrar todos los checks" quita ese filtro. Cada check activo se
     puede abrir para editar su payload o eliminar.
   - **Plantillas predefinidas →**: elige una plantilla del desplegable (la
     descripción y los parámetros se actualizan al instante), ajusta
     parámetros/`nullable`/"Reemplazar checks existentes", y "Aplicar
     plantilla a columna".
4. **Globales del esquema** — desde el menú **Más** en la cabecera: `strict`,
   `coerce`, `unique_column_names` a nivel raíz del YAML.
5. **Guardar como…** — botón primario en la cabecera. Pide una ruta destino
   distinta al original (y distinta al checkpoint); si intentas reutilizar
   cualquiera de las dos, la operación se rechaza con un error inline.
6. **Cambiar archivo** — desde el menú **Más**, vuelve a la pantalla de carga
   sin perder el checkpoint autoguardado del archivo actual.

Cada edición (propiedades, checks, plantillas, globales) se autoguarda de
inmediato en el checkpoint — no hay un botón de "guardar progreso" separado;
"Guardar como…" es exclusivamente para producir el YAML final en la ruta que
elijas.

## Descripción técnica (para desarrolladores)

### Capas

```text
pandera_scheme_editor_web/
  manage.py
  requirements.txt
  config/                   # settings, urls, wsgi/asgi de Django
  pandera_core/              # dominio hexagonal, sin Django ni HTTP
    domain/
      contract.py            # ColumnContract / PanderaSchemaContract (puro)
      pandera_checks.py       # dtypes, checks, relevant_check_keys_for_dtype
      validation_templates.py # plantillas declarativas + apply_template_to_column
      payload_fields.py       # forma de los payloads de cada check
    ports/
      schema_repository.py    # Protocol de persistencia
    application/
      use_cases.py            # SchemaEditorUseCases
    adapters/
      yaml_schema_repository.py  # PyYAML + protección anti-sobrescritura + checkpoints
      parsing.py               # parse_scalar/parse_list_text/format_value/format_list
  schema_editor/              # app Django: el adaptador web
    urls.py
    forms.py
    dynamic_fields.py          # specs de campos dinámicos (checks y parámetros de plantilla)
    context_processors.py
    views/
      common.py                # helpers compartidos por toda vista (ver más abajo)
      load.py                   # carga inicial + resume/discard de checkpoint
      columns.py                # detalle de columna + propiedades
      checks.py                 # agregar/editar/eliminar checks manuales
      template_editor.py        # selector y aplicación de plantillas
      globals_save.py           # globales del esquema + guardar como
    templates/schema_editor/
    static/schema_editor/{css,js}/
```

`pandera_core` es, deliberadamente, el mismo tipo de núcleo de dominio que
`pandera_scheme_editor/src/` en la versión GTK (mismo contrato, mismos checks,
mismas plantillas) — el adaptador que cambia es la capa de arriba (`gtk_gui.py`
allá, `schema_editor/` aquí). `pandera_core` no importa Django, HTTP ni GTK.

### El parámetro `?src=` en vez de sesión

El YAML en edición viaja como `?src=` en la URL (ver
`schema_editor.context_processors.working_src`), no en la sesión de Django:
así cada pestaña/ventana es autónoma sobre qué archivo edita. Toda vista
dentro del editor (columnas, checks, plantillas, globales, guardar-como) pasa
por `views/common.py::load_contract_or_error`, el único punto de entrada que
resuelve `?src=` a un contrato cargado.

### Acumulación de checkpoints entre requests

Cada request Django es sin estado: no hay un contrato en memoria persistente
entre una edición y la siguiente, a diferencia de la GUI GTK (que sí mantiene
un contrato vivo mientras el proceso corre). Por eso
`load_contract_or_error` **prefiere el checkpoint existente sobre el YAML
original** cada vez que ya hay uno guardado para ese `src` — si no lo hiciera,
cada edición recargaría el original intacto y el autoguardado solo reflejaría
el último cambio, perdiendo los anteriores de la misma sesión. La única
excepción intencional es la pantalla "Progreso encontrado"
(`views/load.py::resume_confirm_view`/`discard_checkpoint_view`), que resuelve
la ruta explícitamente para poder ofrecer "continuar" o "partir del original"
sin que esa preferencia interfiera; elegir "partir del original" borra el
checkpoint en disco para que no reaparezca en la siguiente navegación.

### Protección anti-sobrescritura

Vive en `pandera_core/adapters/yaml_schema_repository.py`
(`YamlSchemaRepository.save_as`), no en las vistas: compara la ruta destino
resuelta contra el YAML de origen del contrato **y** contra
`compute_original_path(...)` (el original del que deriva un checkpoint), así
que ninguna de las dos rutas puede pisarse desde "Guardar como…", sin importar
si el contrato en memoria vino del original o de un checkpoint.

### Menús adaptados al `dtype`

`pandera_core/domain/pandera_checks.py::relevant_check_keys_for_dtype`
concentra esa regla: numéricos continuos (`float64`) no ofrecen `isin` por
defecto (rara vez son categóricos); numéricos discretos (`int64`) sí lo
mantienen (suelen codificar categorías); texto/categóricos ofrecen
`isin`/`str_matches`/`str_length`; fecha ofrece solo los checks de rango. Un
`dtype` no reconocido cae de vuelta a la lista completa, para nunca ocultar un
check válido por accidente. El filtro es solo de UI: un check ya activo nunca
se oculta, y "Mostrar todos los checks" lo desactiva por completo.

### JavaScript

Un único archivo, `static/schema_editor/js/app.js`, y solo para una cosa: la
vista previa instantánea del selector de plantillas
(`template_picker.html`), leyendo el JSON ya embebido en la página
(`#template-data`) para actualizar descripción/parámetros/`nullable` sin
recargar. Es mejora progresiva pura — con JS deshabilitado, el `<noscript>`
de esa misma página muestra un botón que logra lo mismo con una recarga
normal, y el servidor siempre reconstruye los specs desde el `template_key`
recibido en el POST, nunca confía en lo que mostró el GET.

### Pruebas manuales sugeridas

No hay suite automatizada todavía (`schema_editor/tests/` y
`pandera_core/tests/` están vacíos). Para verificar manualmente tras un
cambio:

1. Cargar un YAML Pandera real; ver columnas en la barra lateral.
2. Cambiar `dtype` de `object` a `string`/`str`, y de `int64` a `Int64`.
3. Seleccionar una columna `float64` y confirmar que `isin` no aparece en el
   desplegable de "agregar check"; seleccionar una `object`/`category` y
   confirmar que sí aparece junto con `str_matches`/`str_length`; usar
   "Mostrar todos los checks" y confirmar que aparecen todos.
4. Agregar/editar/eliminar un check manual (rango, `isin`, regex).
5. Abrir "Plantillas predefinidas", cambiar el `<select>` varias veces y
   confirmar que la descripción y los parámetros se actualizan sin recargar;
   aplicar una plantilla (p. ej. `human_age`) y confirmar el YAML resultante.
6. Activar `strict`/`coerce`/`unique_column_names` en Globales.
7. Editar dos columnas distintas sin volver a la pantalla de carga entre una y
   otra; confirmar que `{nombre}-proc.yaml` acumula **ambos** cambios.
8. Recargar el mismo YAML original: debe aparecer la pantalla de progreso.
   Elegir "Sí, continuar" debe retomar exactamente donde quedó. Elegir "No,
   partir del original" debe borrar el checkpoint y mostrar los valores
   originales; navegar después sin editar no debe resucitarlo.
9. "Guardar como…" hacia una ruta nueva: debe producir el YAML esperado.
   Intentarlo hacia el original o hacia el checkpoint debe fallar con "No se
   permite sobrescribir el YAML original", mostrado inline en el formulario.
