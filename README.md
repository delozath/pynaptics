# pynaptics-tools

Herramientas internas para editar esquemas de [Pandera](https://pandera.readthedocs.io/)
inferidos automáticamente (`pa.infer_schema(df).to_yaml(...)`). Ambas
herramientas resuelven el mismo problema — corregir a mano un YAML inferido
sin arriesgar el original — con la misma lógica de dominio, en dos interfaces
distintas.

## Proyectos

### [`pandera_scheme_editor/`](pandera_scheme_editor/README.md) — versión de escritorio (GTK)

Aplicación GTK 4 / PyGObject de un solo archivo ejecutable (`python main.py`).
Ideal para uso local rápido sin levantar un servidor.

### [`pandera_scheme_editor_web/`](pandera_scheme_editor_web/README.md) — versión web (Django)

Misma funcionalidad servida como app web local (`python manage.py runserver`).
Pensada para un solo operador en `localhost` (sin autenticación), útil cuando
se prefiere trabajar desde el navegador o en un entorno sin GTK disponible.

## Características comunes a ambas

- Cargan un YAML de esquema Pandera ya inferido; nunca lo sobrescriben.
- Edición por columna: `dtype`, `nullable`, `required`, `unique`, `coerce`,
  `regex`.
- Checks manuales (`isin`, comparaciones numéricas, `str_matches`,
  `str_length`), con el menú de checks disponibles adaptado al `dtype` de la
  columna seleccionada.
- 15 plantillas de validación predefinidas (edad, sexo/género, talla, peso,
  porcentajes, código postal y estado de México, email, fecha, identificador
  único, etc.).
- Edición de propiedades globales del esquema (`strict`, `coerce`,
  `unique_column_names`).
- Guardado siempre como "Guardar como…" hacia una ruta distinta al original,
  con protección explícita contra sobrescribirlo.
- Autoguardado incremental en `{nombre}-proc.yaml` para continuar la
  depuración en varias sesiones, con opción de reanudar o partir de cero.

## Diferencias principales

| | GTK | Web |
|---|---|---|
| Interfaz | Escritorio (GTK 4) | Navegador (Django) |
| Cómo se ejecuta | `python main.py` | `python manage.py runserver` |
| Estado en memoria | Un contrato vivo mientras corre el proceso | Sin estado entre peticiones; relee el checkpoint más reciente en cada una |
| Multiusuario | No aplica (proceso local) | No soportado; un solo operador local, sin autenticación |

Cada subproyecto tiene su propio `README.md` con instalación, tutorial de uso
y descripción técnica detallada.
