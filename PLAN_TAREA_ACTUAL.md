# Plan de tarea en curso — dtypes canónicos, presanitización, checks inline, save-as

> Tareas anteriores (UI/menú/READMEs; bug de formato de checks + metadata;
> plantilla SI/NO; checks activos inline) completadas. Este archivo ahora
> trackea la última tanda de ajustes.

## Prompt original del usuario (verbatim)

> correcciones: aún aparecen int32, int64, float32, float64, dejar solo las
> opciones que inician con mayúscula, también aparece la opción string
> completa, dejar solo str (verificar en los regresos de las plantillas
> sobre todo). agregar una presanitización del yaml original para que quede
> en el contexto de esta app, ya que depende del render de Pandera a veces
> genera los checks en el mismo nivel del resto de los tag de una variable
> en lugar de que sean subtags del checks. verifica si es posible abrir un
> cuadro de dialogo para dar la ruta y nombre de en donde se guardará el
> archivo ya que la usabilidad actual está limitada. Analiza mi petición,
> prioriza, analiza el código y genera el plan de implementación con
> intervención mínima de código ya que la app es bastante funcional.
> ejecuta los ajustes, evalua, loop de ajustes y evaluación en hasta 2
> ciclos, luego ya no realices más ajustes, genera un log de lo que
> encontraste en tu validación para proceder. Tienes permiso de ejecución
> de comandos.

**Alcance**: versión web únicamente (consistente con toda la conversación
previa). Máximo 2 ciclos de ajuste+evaluación, luego solo reportar.

## Plan (prioridad decidida)

1. Plantillas: 7 plantillas usaban `recommended_dtype="string"` — corregir a
   `"str"` directamente en la fuente (fix más simple y directo).
2. Presanitización en `YamlSchemaRepository.load()`: normalizar dtypes crudos
   (`int64→Int64`, `int32→Int32`, `float64→Float64`, `float32→Float32`,
   `string→str`) y desanidar checks aplanados (sin `checks:` envolvente) en
   `checks:`, solo en memoria — nunca toca el archivo original en disco. Esto
   además resuelve el problema del dropdown de dtype de forma indirecta (ya
   no hay valores crudos en minúscula que `dtype_choices_for` tenga que
   agregar como opción extra).
3. Guardar como: no es viable abrir un diálogo nativo del SO para elegir ruta
   de guardado en el servidor desde una página web plana — los selectores de
   archivo del navegador solo direccionan el filesystem del *cliente*, no el
   del servidor, y usarlos rompería la protección anti-sobrescritura (que
   compara rutas del lado servidor). Alternativa mínima implementada:
   pre-llenar el campo con una ruta sugerida (`<original>_editado.yaml`)
   junto al original.

## Ejecución

- [x] `validation_templates.py`: 7 ocurrencias de `recommended_dtype="string"`
      → `"str"` (reemplazo único, sin tocar nada más).
- [x] `pandera_core/adapters/yaml_schema_repository.py`: agregadas
      `_DTYPE_ALIASES`, `_COLUMN_RESERVED_KEYS`, `_canonicalize_dtype`,
      `_unflatten_checks`, `_sanitize_schema`; invocada desde `load()` justo
      después de `_validate_root`.
- [x] `schema_editor/views/globals_save.py`: `_suggested_destination()` +
      `SaveAsForm(initial=...)` en el GET de `save_as_view`.

## Validación (2 ciclos, límite alcanzado)

**Ciclo 1** (YAML sintético con dtype `int64`/`string`/`float64` crudos +
checks aplanados sin `checks:`, vía repositorio directo y vía HTTP real):
- `edad` (dtype `int64` + 2 checks aplanados sin `checks:`) → cargó como
  `Int64` con ambos checks correctamente movidos a `checks:`.
- `nombre` (dtype `string`) → cargó como `str`; dropdown solo muestra `str`
  (sin duplicado `string`).
- `salario` (dtype `float64`, checks ya anidados normalmente) → cargó como
  `Float64`, checks intactos (sin regresión en el caso ya-correcto).
- Aplicar plantilla `sex_binary` → dtype resultante `str` (no `string`).
- Archivo original en disco confirmado sin modificar.
- "Guardar como" mostró `.../sanitize_test_editado.yaml` precargado.

**Ciclo 2** (casos borde, solo `_sanitize_schema` en aislado): columna sin
`dtype`, `dtype: null`, columna vacía `{}`, checks mixtos (anidados +
aplanados a la vez), dtype fuera del mapa de alias (`Int16`) — todos se
comportan correctamente sin excepciones; ninguno requirió ajuste adicional.

**Sin más ajustes tras estos 2 ciclos**, según lo pedido. Log de hallazgos
entregado en el chat.
