generé este proyecto con el siguiente prompt en chatgpt:

Necesito que implementes un proyecto completo en Python para editar un YAML generado automáticamente por Pandera.

Contexto:

schema = pa.infer_schema(df)
schema.to_yaml("schema_inferido.yaml")

El YAML inferido por Pandera será editado manualmente desde una GUI. La GUI debe cargar ese YAML, permitir modificar tipos, checks y plantillas predefinidas por columna, y guardar un nuevo YAML corregido. El YAML original nunca debe modificarse ni sobrescribirse.

Usa GTK, no Tkinter.

Requisitos obligatorios:

- Python moderno, idealmente Python >= 3.11.
- GUI con GTK, preferentemente GTK 4 y PyGObject.
- Persistencia con PyYAML.
- Arquitectura hexagonal.
- Código completo, legible, tipado, documentado y extensible.
- No hacer inferencia desde Excel dentro de la GUI.
- No validar Excel dentro de la GUI.
- No generar reporte final.
- No implementar orquestador.
- La GUI solo debe cargar YAML, editarlo y guardar otro YAML.
- Debe existir protección real en la capa de persistencia para impedir sobrescribir el YAML original.
- La operación de guardado debe ser siempre “Guardar como”.

Estructura del proyecto:

pandera_yaml_gtk_editor/
  main.py
  README.md
  requirements.txt

  src/
    _init_.py

    domain/
      _init_.py
      contract.py
      pandera_checks.py
      validation_templates.py

    ports/
      _init_.py
      schema_repository.py

    application/
      _init_.py
      use_cases.py

    adapters/
      _init_.py
      yaml_schema_repository.py
      gtk_gui.py

Responsabilidades:

1. "domain/contract.py"

Debe contener el modelo puro de dominio. No debe importar GTK, YAML, Pandera, pandas ni filesystem.

Debe definir:

ColumnContract
PanderaSchemaContract

"ColumnContract" debe permitir editar:

name
dtype
nullable
required
unique
coerce
regex
checks

Métodos requeridos:

set_check(key, payload)
remove_check(key)
clear_checks()

"PanderaSchemaContract" debe contener:

raw
source_path

Métodos requeridos:

column_names()
get_column(name)
set_global_coerce(value)
set_global_strict(value)
set_unique_column_names(value)
clone_raw()

2. "domain/pandera_checks.py"

Debe definir los tipos y checks editables.

Dtypes disponibles:

PANDERA_DTYPES = [
    "string",
    "str",
    "Int64",
    "int64",
    "Float64",
    "float64",
    "boolean",
    "bool",
    "datetime64[ns]",
    "category",
    "object",
]

Checks manuales disponibles:

CHECK_KEYS = [
    "isin",
    "greater_than_or_equal_to",
    "greater_than",
    "less_than_or_equal_to",
    "less_than",
    "str_matches",
    "str_length",
]

Debe definir:

CheckTemplate
CHECK_TEMPLATES
default_check_payload(check_key: str) -> dict

Los checks deben serializarse así en YAML:

checks:
  isin:
    allowed_values:
      - A
      - B

checks:
  greater_than_or_equal_to:
    min_value: 0

checks:
  greater_than:
    min_value: 0

checks:
  less_than_or_equal_to:
    max_value: 100

checks:
  less_than:
    max_value: 100

checks:
  str_matches:
    pattern: "^\\d{5}$"

checks:
  str_length:
    min_value: 1
    max_value: 50

3. "domain/validation_templates.py"

Debe implementar plantillas predefinidas para validaciones frecuentes. Las plantillas deben ser declarativas, extensibles y fáciles de registrar.

Define:

TemplateParameter
ValidationTemplate
VALIDATION_TEMPLATES
apply_template_to_column(column, template_key, parameter_values, replace_existing_checks=False)

Cada plantilla debe poder definir:

key
label
description
recommended_dtype
default_nullable
default_coerce
default_unique
checks
parameters

La función "apply_template_to_column" debe:

- Cambiar "dtype".
- Cambiar "nullable".
- Activar "coerce".
- Cambiar "unique" si la plantilla lo define.
- Agregar checks de la plantilla.
- Si "replace_existing_checks=True", borrar checks anteriores.
- Si "replace_existing_checks=False", fusionar checks; si hay conflicto de misma key, gana la plantilla.

Plantillas requeridas:

A. Edad humana

key: human_age
label: Edad humana
dtype: Int64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 0
  less_than_or_equal_to:
    max_value: 100
parámetros:
  min_value default 0
  max_value default 100

B. Sexo biológico simple

key: sex_binary
label: Sexo biológico simple
dtype: string
nullable configurable
coerce: true
checks:
  isin:
    allowed_values: ["F", "M"]

C. Sexo/género extendido

key: sex_or_gender_extended
label: Sexo/género extendido
dtype: string
nullable configurable
coerce: true
checks:
  isin:
    allowed_values: ["F", "M", "Otro", "No especificado"]

D. Talla en centímetros

key: height_cm
label: Talla en cm
dtype: Float64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 30
  less_than_or_equal_to:
    max_value: 250

E. Peso en kilogramos

key: weight_kg
label: Peso en kg
dtype: Float64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 0
  less_than_or_equal_to:
    max_value: 500

F. Número positivo estricto

key: positive_number
label: Número positivo estricto
dtype: Float64
nullable configurable
coerce: true
checks:
  greater_than:
    min_value: 0

G. Número positivo o cero

key: non_negative_number
label: Número positivo o cero
dtype: Float64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 0

H. Entero positivo o cero

key: non_negative_integer
label: Entero positivo o cero
dtype: Int64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 0

I. Porcentaje 0 a 100

key: percentage_0_100
label: Porcentaje 0 a 100
dtype: Float64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 0
  less_than_or_equal_to:
    max_value: 100

J. Proporción 0 a 1

key: proportion_0_1
label: Proporción 0 a 1
dtype: Float64
nullable configurable
coerce: true
checks:
  greater_than_or_equal_to:
    min_value: 0
  less_than_or_equal_to:
    max_value: 1

K. Código postal México

Debe ser string, no entero, para preservar ceros a la izquierda.

key: mexico_postal_code
label: Código postal México
dtype: string
nullable configurable
coerce: true
checks:
  str_matches:
    pattern: "^\\d{5}$"

L. Entidad federativa México

key: mexico_state
label: Entidad federativa México
dtype: string
nullable configurable
coerce: true
checks:
  isin:
    allowed_values:
      - Aguascalientes
      - Baja California
      - Baja California Sur
      - Campeche
      - Chiapas
      - Chihuahua
      - Ciudad de México
      - Coahuila
      - Colima
      - Durango
      - Guanajuato
      - Guerrero
      - Hidalgo
      - Jalisco
      - Estado de México
      - Michoacán
      - Morelos
      - Nayarit
      - Nuevo León
      - Oaxaca
      - Puebla
      - Querétaro
      - Quintana Roo
      - San Luis Potosí
      - Sinaloa
      - Sonora
      - Tabasco
      - Tamaulipas
      - Tlaxcala
      - Veracruz
      - Yucatán
      - Zacatecas

M. Email

key: email
label: Email
dtype: string
nullable configurable
coerce: true
checks:
  str_matches:
    pattern: "^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)+$"

N. Fecha

key: date
label: Fecha
dtype: datetime64[ns]
nullable configurable
coerce: true
checks opcionales:
  greater_than_or_equal_to:
    min_value: fecha mínima si el usuario la define
  less_than_or_equal_to:
    max_value: fecha máxima si el usuario la define

O. Identificador único

key: unique_id
label: Identificador único
dtype: string
nullable: false
coerce: true
unique: true
checks opcionales:
  str_matches:
    pattern: patrón si el usuario lo define

4. "ports/schema_repository.py"

Debe definir un "Protocol":

class SchemaRepository(Protocol):
    def load(self, path: str | Path) -> PanderaSchemaContract:
        ...

    def save_as(
        self,
        contract: PanderaSchemaContract,
        target_path: str | Path,
        *,
        allow_overwrite_source: bool = False,
    ) -> None:
        ...

5. "adapters/yaml_schema_repository.py"

Debe implementar "SchemaRepository" usando PyYAML.

"load" debe:

- Resolver la ruta absoluta.
- Leer con "yaml.safe_load".
- Verificar que la raíz sea "dict".
- Verificar que exista ""columns"".
- Verificar que ""columns"" sea "dict".
- Devolver "PanderaSchemaContract(raw=raw, source_path=path_resuelto)".

"save_as" debe:

- Guardar con "yaml.safe_dump".
- Usar "sort_keys=False".
- Usar "allow_unicode=True".
- Crear directorios destino si faltan.
- Prohibir sobrescribir el YAML original.

Regla crítica:

if target_path == contract.source_path and not allow_overwrite_source:
    raise ValueError("No se permite sobrescribir el YAML original")

6. "application/use_cases.py"

Debe definir:

SchemaEditorUseCases

Con métodos:

load_contract(path)
save_contract_as(contract, target_path)

"save_contract_as" debe llamar al repositorio con "allow_overwrite_source=False".

7. "adapters/gtk_gui.py"

Debe implementar la GUI con GTK 4 / PyGObject.

La GUI debe ser solo adaptador. No debe contener lógica de persistencia directa ni lógica de dominio compleja.

Ventana principal:

Barra superior:
  - botón “Cargar YAML inferido”
  - botón “Guardar como YAML editado”
  - label con ruta del YAML original cargado

Panel izquierdo:
  - lista de columnas

Panel derecho:
  - editor de propiedades de columna
  - editor manual de checks
  - editor de plantillas predefinidas
  - editor de propiedades globales

Editor de propiedades de columna:

- nombre readonly
- dtype como dropdown
- nullable checkbox
- required checkbox
- unique checkbox
- coerce checkbox
- botón “Aplicar propiedades”

Editor manual de checks:

- dropdown de checks disponibles
- botón “Agregar/activar check”
- lista de checks activos
- botón “Eliminar check seleccionado”
- editor dinámico del payload del check
- botón “Aplicar check editado”

Editor de plantillas:

- dropdown de plantillas disponibles
- descripción de la plantilla seleccionada
- editor dinámico de parámetros
- checkbox nullable
- checkbox “Reemplazar checks existentes”
- botón “Aplicar plantilla a columna”

Comportamiento de plantillas:

- Si “Reemplazar checks existentes” está activado:
  - borrar checks previos
  - aplicar solo checks de la plantilla
- Si está desactivado:
  - fusionar checks
  - si una key ya existe, reemplazar esa key con la plantilla

Editor de propiedades globales:

- strict checkbox
- coerce checkbox
- unique_column_names checkbox
- botón “Aplicar globales”

Aplicar globales sobre el root del YAML:

contract.raw["strict"] = bool(value)
contract.raw["coerce"] = bool(value)
contract.raw["unique_column_names"] = bool(value)

8. Helpers de parseo

Implementar en un módulo adecuado o dentro del adaptador GUI:

parse_scalar(value: str) -> Any
parse_list_text(text: str) -> list[Any]
format_value(value: Any) -> str
format_list(values: Any) -> str

"parse_scalar" debe convertir:

""        -> None
"null"    -> None
"None"    -> None
"true"    -> True
"false"   -> False
"123"     -> 123
"12.5"    -> 12.5
"'A'"     -> "A"
"A"       -> "A"

Usar "ast.literal_eval" con fallback a string.

"parse_list_text" debe aceptar:

A
B
C

y devolver:

["A", "B", "C"]

También debe aceptar:

["A", "B", "C"]

9. YAML de entrada de ejemplo

schema_type: dataframe
version: 0.0.1
columns:
  edad:
    title: null
    description: null
    dtype: int64
    nullable: false
    checks:
      greater_than_or_equal_to:
        min_value: 18.0
      less_than_or_equal_to:
        max_value: 90.0
    unique: false
    coerce: false
    required: true
    regex: false
  sexo:
    title: null
    description: null
    dtype: object
    nullable: false
    checks:
      isin:
        allowed_values:
          - F
          - M
    unique: false
    coerce: false
    required: true
    regex: false
checks: null
index: null
dtype: null
coerce: false
strict: false
name: null
ordered: false
unique: null
report_duplicates: all
unique_column_names: false
add_missing_columns: false
title: null
description: null

10. YAML editado esperado

schema_type: dataframe
version: 0.0.1
columns:
  edad:
    title: null
    description: null
    dtype: Int64
    nullable: false
    checks:
      greater_than_or_equal_to:
        min_value: 0
      less_than_or_equal_to:
        max_value: 100
    unique: false
    coerce: true
    required: true
    regex: false
  sexo:
    title: null
    description: null
    dtype: string
    nullable: false
    checks:
      isin:
        allowed_values:
          - F
          - M
          - Otro
    unique: false
    coerce: true
    required: true
    regex: false
  codigo_postal:
    title: null
    description: null
    dtype: string
    nullable: true
    checks:
      str_matches:
        pattern: "^\\d{5}$"
    unique: false
    coerce: true
    required: true
    regex: false
checks: null
index: null
dtype: null
coerce: true
strict: true
name: null
ordered: false
unique: null
report_duplicates: all
unique_column_names: true
add_missing_columns: false
title: null
description: null

11. Pruebas mínimas

Incluir instrucciones o pruebas manuales para verificar:

1. Cargar YAML Pandera real.
2. Ver columnas.
3. Cambiar dtype object -> string.
4. Cambiar dtype int64 -> Int64.
5. Activar coerce en columna.
6. Activar strict global.
7. Editar isin agregando un valor.
8. Agregar límites min/max manualmente.
9. Agregar regex manualmente.
10. Aplicar plantilla Edad humana.
11. Aplicar plantilla Código postal México.
12. Aplicar plantilla Entidad federativa México.
13. Aplicar plantilla Peso kg.
14. Aplicar plantilla Talla cm.
15. Aplicar plantilla Positivo o cero.
16. Guardar como otro YAML.
17. Confirmar que el YAML original no cambió.
18. Confirmar que intentar guardar sobre el original lanza ValueError desde el repositorio YAML.

12. Calidad esperada

La solución debe seguir buenas prácticas:

- Tipado explícito.
- Dataclasses donde aplique.
- Código modular.
- Funciones pequeñas.
- Bajo acoplamiento.
- Separación clara de responsabilidades.
- Documentación breve en clases y funciones con lógica importante.
- Sin lógica de dominio dentro de la GUI.
- Sin acceso directo al filesystem fuera del adaptador YAML.
- Sin dependencia de GTK en dominio o aplicación.
- Sin dependencia de YAML en dominio.
- Sin dependencia de Pandera para editar el YAML.

13. Entrega requerida

Entrega el proyecto completo:

- Código completo de todos los archivos.
- README.
- requirements.txt.
- Instrucciones de instalación en Linux.
- Instrucciones para ejecutar.
- Explicación corta de arquitectura.
- Ejemplo de uso.

No incluyas inferencia desde Excel, validación del Excel, reporte final ni orquestador.


Ahora como tu eres experto en programación necesito que lo revises para optimizarlo y verifiques que hace lo que requiero.

Te tocará implementar las nuevas features, que son una interfaz inicial más usable en cuanto el tamaño de las columnas ya que esta inicialmente desproporcionada. lo siguiente es que los menus deben ser adaptables por ejemplo no mostrar los isin si son variables numericas continuas, pero si si son categóricas (analiza los casos más frecuentes), verificar si se pueden almacenar parcialmente el archivo yaml para irlo dejando depurado y poderlo terminar en varias sesiones, si no está así realizarlo, en un archivo con fname-proc.yaml donde fname es el nombre del archivo original.

Realiza las siguientes tareas:
- revisa el prompt
- analiza el código
- verifica el cumplimiento
- corrige los fallos y bugs
- verifica la corrección
- analiza las nuevas features
- planea la integración de las nuevas features
- agrega las nuevas features
- verifica funcionamiento de las nuevas features
- termina