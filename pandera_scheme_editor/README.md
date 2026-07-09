# Pandera YAML GTK Editor

Editor GTK 4 para cargar un YAML generado por `pa.infer_schema(df).to_yaml(...)`, modificar tipos, checks y plantillas por columna, y guardar un nuevo YAML corregido sin sobrescribir el original.

> Esta es la versión de escritorio. También existe una
> [versión web (Django)](../pandera_scheme_editor_web/README.md) con la misma
> lógica de dominio. Ver el [README general](../README.md) para comparar
> ambas.

## Alcance

Este proyecto hace exactamente esto:

- Carga un YAML de esquema Pandera ya inferido.
- Muestra las columnas del YAML.
- Permite editar propiedades de columnas: `dtype`, `nullable`, `required`, `unique`, `coerce`, `regex`.
- Permite crear, editar y eliminar checks manuales soportados, con el dropdown de checks adaptado al `dtype` de la columna seleccionada.
- Permite aplicar plantillas declarativas de validación frecuentes.
- Permite editar propiedades globales: `strict`, `coerce`, `unique_column_names`.
- Guarda siempre con operación “Guardar como”.
- Bloquea desde el repositorio YAML cualquier intento de sobrescribir el archivo original (incluso tras reanudar desde un checkpoint).
- Autoguarda progreso incremental en un archivo `{nombre}-proc.yaml` junto al original, para continuar la depuración en varias sesiones.

Este proyecto deliberadamente **no** hace:

- Inferencia desde Excel dentro de la GUI.
- Validación de Excel dentro de la GUI.
- Reporte final.
- Orquestación de pipelines.
- Dependencia de Pandera para editar el YAML.

## Arquitectura

La estructura sigue arquitectura hexagonal:

```text
pandera_yaml_gtk_editor/
  main.py
  README.md
  requirements.txt

  src/
    __init__.py

    domain/
      __init__.py
      contract.py
      pandera_checks.py
      validation_templates.py

    ports/
      __init__.py
      schema_repository.py

    application/
      __init__.py
      use_cases.py

    adapters/
      __init__.py
      yaml_schema_repository.py
      gtk_gui.py

  examples/
    schema_inferido.yaml
```

También se incluyen archivos `_init_.py` como marcadores de compatibilidad textual, pero los paquetes Python reales usan `__init__.py`.

### Capas

- `domain/contract.py`: modelo puro. No importa GTK, YAML, Pandera, pandas ni filesystem. Edita estructuras Python ya cargadas.
- `domain/pandera_checks.py`: catálogo de dtypes y checks manuales soportados.
- `domain/validation_templates.py`: plantillas declarativas reutilizables.
- `ports/schema_repository.py`: contrato `Protocol` para persistencia.
- `application/use_cases.py`: casos de uso mínimos de carga y guardado.
- `adapters/yaml_schema_repository.py`: persistencia PyYAML y protección anti-sobrescritura del YAML original.
- `adapters/gtk_gui.py`: GUI GTK 4/PyGObject. No contiene persistencia directa ni lógica de dominio compleja.

## Instalación en Linux

### Ubuntu/Debian

GTK y PyGObject dependen de paquetes del sistema. Instálalos primero:

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  python3-gi \
  python3-gi-cairo \
  gir1.2-gtk-4.0 \
  libgtk-4-dev \
  gobject-introspection \
  libgirepository-2.0-dev \
  libcairo2-dev \
  libgirepository1.0-dev \
  pkg-config
```

Crea el entorno virtual desde la raíz del proyecto. En muchas distribuciones conviene usar `--system-site-packages` para que el entorno vea `python3-gi` instalado por `apt`:

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Fedora

```bash
sudo dnf install -y python3 python3-pip python3-gobject gtk4 gobject-introspection-devel cairo-gobject-devel
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

Flujo básico:

1. Pulsa **Cargar YAML inferido**.
2. Selecciona un archivo YAML generado previamente por Pandera.
3. Selecciona una columna en el panel izquierdo.
4. Edita propiedades, checks manuales o aplica una plantilla.
5. Ajusta globales si aplica.
6. Pulsa **Guardar como YAML editado**.
7. Elige una ruta distinta al YAML original.

Si eliges la misma ruta del YAML original, el repositorio lanza:

```text
ValueError: No se permite sobrescribir el YAML original
```

## Guardado incremental entre sesiones (`{nombre}-proc.yaml`)

Cada vez que aplicas propiedades, checks, plantillas o globales, la GUI autoguarda silenciosamente el progreso en un archivo `{nombre_original}-proc.yaml` junto al YAML original (ej. `schema_inferido.yaml` → `schema_inferido-proc.yaml`). Una etiqueta de estado bajo la barra superior muestra la última ruta guardada o el error, sin interrumpir con diálogos modales.

Al pulsar **Cargar YAML inferido** y elegir un archivo que ya tiene un checkpoint guardado de una sesión anterior, la GUI pregunta:

> ¿Continuar desde el progreso guardado en `{nombre}-proc.yaml`?

- **Sí**: continúa editando el checkpoint (se sigue autoguardando en el mismo archivo).
- **No**: parte de cero desde el YAML original inferido.

El YAML original nunca se modifica por este mecanismo: la protección anti-sobrescritura del repositorio protege tanto la ruta cargada como, si se reanudó desde un checkpoint, el original del que deriva ese checkpoint. El botón **Guardar como YAML editado** sigue siendo la única forma de producir el archivo final, y sigue exigiendo una ruta distinta a la actualmente cargada.

## Menú de checks adaptado al `dtype`

El dropdown de "Checks manuales" sólo ofrece por defecto los checks relevantes para el `dtype` de la columna seleccionada (ej. no ofrece `isin` en columnas `float64` continuas, pero sí en columnas categóricas). Los checks ya activos en la columna nunca se ocultan. El checkbox **Mostrar todos los checks** desactiva el filtro y ofrece la lista completa para casos particulares.

## Ejemplo rápido

Hay un YAML mínimo en:

```text
examples/schema_inferido.yaml
```

Puedes cargarlo desde la GUI y probar:

- `edad`: aplicar plantilla **Edad humana** con reemplazo de checks.
- `sexo`: cambiar `dtype` de `object` a `string`; editar `isin` para agregar `Otro`.
- Globales: activar `strict`, `coerce` y `unique_column_names`.
- Guardar como `examples/schema_editado.yaml` o cualquier otra ruta distinta.

## Checks manuales soportados

```yaml
checks:
  isin:
    allowed_values:
      - A
      - B
```

```yaml
checks:
  greater_than_or_equal_to:
    min_value: 0
```

```yaml
checks:
  greater_than:
    min_value: 0
```

```yaml
checks:
  less_than_or_equal_to:
    max_value: 100
```

```yaml
checks:
  less_than:
    max_value: 100
```

```yaml
checks:
  str_matches:
    pattern: "^\\d{5}$"
```

```yaml
checks:
  str_length:
    min_value: 1
    max_value: 50
```

## Plantillas incluidas

- `human_age`: Edad humana.
- `sex_binary`: Sexo biológico simple.
- `sex_or_gender_extended`: Sexo/género extendido.
- `height_cm`: Talla en cm.
- `weight_kg`: Peso en kg.
- `positive_number`: Número positivo estricto.
- `non_negative_number`: Número positivo o cero.
- `non_negative_integer`: Entero positivo o cero.
- `percentage_0_100`: Porcentaje 0 a 100.
- `proportion_0_1`: Proporción 0 a 1.
- `mexico_postal_code`: Código postal México.
- `mexico_state`: Entidad federativa México.
- `email`: Email.
- `date`: Fecha con límites opcionales.
- `unique_id`: Identificador único con patrón opcional.

## Reglas de plantillas

Al aplicar una plantilla:

- Cambia `dtype`.
- Cambia `nullable` usando la casilla de la GUI.
- Activa `coerce` si la plantilla lo define.
- Cambia `unique` si la plantilla lo define.
- Agrega checks de la plantilla.
- Si **Reemplazar checks existentes** está activado, borra los checks previos.
- Si no está activado, fusiona checks; ante conflicto de misma key gana la plantilla.

## Pruebas manuales mínimas

Usa `examples/schema_inferido.yaml` o un YAML real generado por Pandera y verifica:

1. Cargar YAML Pandera real.
2. Ver columnas en el panel izquierdo.
3. Cambiar `dtype` de `object` a `string`.
4. Cambiar `dtype` de `int64` a `Int64`.
5. Activar `coerce` en columna.
6. Activar `strict` global.
7. Editar `isin` agregando un valor.
8. Agregar límites min/max manualmente.
9. Agregar regex manualmente.
10. Aplicar plantilla **Edad humana**.
11. Aplicar plantilla **Código postal México**.
12. Aplicar plantilla **Entidad federativa México**.
13. Aplicar plantilla **Peso en kg**.
14. Aplicar plantilla **Talla en cm**.
15. Aplicar plantilla **Número positivo o cero**.
16. Guardar como otro YAML.
17. Confirmar que el YAML original no cambió.
18. Confirmar que intentar guardar sobre el original lanza `ValueError` desde `YamlSchemaRepository`.
19. Seleccionar una columna `float64` y una `object`/`string`: confirmar que el dropdown de checks cambia (numérico continuo oculta `isin`; categórico lo muestra) y que "Mostrar todos los checks" revela la lista completa.
20. Aplicar cualquier acción y confirmar que aparece `{nombre}-proc.yaml` junto al original con la etiqueta de estado actualizada; cerrar y volver a cargar el mismo original para confirmar el diálogo de reanudación.

## Verificación por consola de la protección anti-sobrescritura

Desde la raíz del proyecto:

```bash
python - <<'PY'
from pathlib import Path
from src.adapters.yaml_schema_repository import YamlSchemaRepository
from src.application.use_cases import SchemaEditorUseCases
from src.domain.validation_templates import apply_template_to_column

repo = YamlSchemaRepository()
use_cases = SchemaEditorUseCases(repo)
contract = use_cases.load_contract(Path("examples/schema_inferido.yaml"))

edad = contract.get_column("edad")
apply_template_to_column(
    edad,
    "human_age",
    {"nullable": False, "min_value": 0, "max_value": 100},
    replace_existing_checks=True,
)
contract.set_global_strict(True)
contract.set_global_coerce(True)
contract.set_unique_column_names(True)

use_cases.save_contract_as(contract, Path("examples/schema_editado.yaml"))
print("Guardado correcto en examples/schema_editado.yaml")

try:
    use_cases.save_contract_as(contract, Path("examples/schema_inferido.yaml"))
except ValueError as exc:
    print(type(exc).__name__, str(exc))
PY
```

Salida esperada:

```text
Guardado correcto en examples/schema_editado.yaml
ValueError No se permite sobrescribir el YAML original
```

## Verificación por consola del guardado incremental y su protección

Este script simula dos sesiones: la primera guarda un checkpoint, la segunda reanuda desde ese checkpoint y confirma que el YAML original sigue protegido.

```bash
python - <<'PY'
from pathlib import Path
from src.adapters.yaml_schema_repository import YamlSchemaRepository
from src.application.use_cases import SchemaEditorUseCases
from src.domain.validation_templates import apply_template_to_column

repo = YamlSchemaRepository()
use_cases = SchemaEditorUseCases(repo)
original = Path("examples/schema_inferido.yaml")

# Sesión 1: cargar el original y autoguardar progreso.
contract = use_cases.load_contract(original)
apply_template_to_column(contract.get_column("edad"), "human_age", {}, replace_existing_checks=True)
checkpoint_path = use_cases.save_checkpoint(contract)
print("Checkpoint guardado en:", checkpoint_path)

# Sesión 2 (simulada): reanudar desde el checkpoint.
resumed = use_cases.load_contract(checkpoint_path)
try:
    use_cases.save_contract_as(resumed, original)
except ValueError as exc:
    print(type(exc).__name__, str(exc))
PY
```

Salida esperada:

```text
Checkpoint guardado en: .../examples/schema_inferido-proc.yaml
ValueError No se permite sobrescribir el YAML original
```

## Notas técnicas

- El YAML se guarda con `yaml.safe_dump(..., sort_keys=False, allow_unicode=True)`.
- El repositorio resuelve rutas absolutas antes de comparar origen y destino.
- La comparación anti-sobrescritura vive en `adapters/yaml_schema_repository.py`, no en la GUI.
- El dominio preserva claves Pandera desconocidas porque edita el árbol YAML original en vez de reconstruirlo desde cero.
- La versión web reutiliza este mismo diseño de dominio (`domain/`, `ports/`, `application/`) bajo el nombre `pandera_core`, cambiando solo el adaptador de interfaz (Django en vez de GTK). Ver [`pandera_scheme_editor_web/README.md`](../pandera_scheme_editor_web/README.md#descripción-técnica-para-desarrolladores) para el detalle de esa capa. La GUI GTK mantiene un único contrato vivo en memoria mientras el proceso corre; la versión web, al ser sin estado entre requests, resuelve esto releyendo el checkpoint más reciente en cada petición — una diferencia de arquitectura, no de dominio.
