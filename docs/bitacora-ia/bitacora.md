# Bitácora de uso de IA

Grupo 6 · Automatizacion_bodega

Cada entrada registra un encargo real a un agente de IA (Claude) y el criterio con que se revisó la respuesta. Lo que importa es cómo se revisó, no qué herramienta se usó.

Encargos de esta bitácora hechos por Bastián Vargas el 2026-10-02, a partir de la pauta de entrega de la Unidad 1. Ambos encargos se hicieron sobre la rama `feature/estructura-entrega`, que sale de `dev`.

---

## Encargo 1. Ordenar el repositorio según la pauta de entrega

**Objetivo.** Dejar el repositorio con la estructura mínima pedida: `src/`, `docs/` (con `unidad1`, `bitacora-ia`, `datos`), `.gitignore`, `.env.example` y un README con cinco títulos.

**Instrucción entregada.**
- Contexto: repositorio `Automatizacion_bodega`, MVP en Streamlit y SQLite, con `app.py` en la raíz, tests, Dockerfile y CI.
- Intención: cumplir la estructura de la pauta sin romper lo que ya funciona.
- Restricciones: no borrar código funcional, no agregar dependencias, no subir claves.
- Verificación: que los 18 tests sigan pasando y que Dockerfile y CI apunten a las rutas nuevas.

**Respuesta obtenida.** El agente propuso mover `app.py` a `src/`, actualizar Dockerfile, CI y tests, crear `.env.example`, reescribir el README con los cinco títulos, y copiar el Avance 2 a `docs/unidad1/`. También movió el bloque de "contexto para agentes" que estaba dentro del README a un `CLAUDE.md`, para que el README quede legible para alguien ajeno al equipo.

**Qué se aceptó y qué se corrigió.**
- Aceptado: mover el código a `src/` y ajustar las rutas en tests, Dockerfile y CI.
- Aceptado: `.env.example` solo con nombres de variables, sin valores, y `.env` en `.gitignore`.
- Corregido: el agente agregó la variable `BODEGA_DB_PATH` al código para que `.env.example` no listara variables inventadas; se revisó que el valor por defecto siga siendo `bodega.db`.
- Corregido: la sección "En qué estado está" del README se contrastó con el código real. Por ejemplo, la guía hoy sale en texto plano (no PDF) y se emite aunque un SKU no valide; el README lo dice así.

**Cómo se verificó.** Se ejecutó `pytest`: 18 tests pasan después del cambio. Se buscó `app.py` en todo el repositorio para confirmar que ninguna ruta quedó apuntando al archivo antiguo. Se revisó el diff completo antes de hacer el commit.

---

## Encargo 2. Primer borrador de la estructura de datos

**Objetivo.** Armar `docs/datos/estructura_datos.md`: diagrama de la base, campos con tipo, claves, cardinalidades, campos obligatorios y dos registros de ejemplo por tabla.

**Instrucción entregada.**
- Contexto: caso de uso del Avance 2 (emisión automática de guía) y las tres tablas SQLite que ya tiene el MVP.
- Intención: derivar las tablas desde los sustantivos del caso de uso, con claves primarias y externas y cardinalidad (1:N, N:1, 1:1).
- Restricciones: una columna guarda una sola variable; las claves externas van en el lado "muchos"; no crear la base en Supabase todavía.
- Verificación: que cada fila de ejemplo respete los tipos y los campos obligatorios, y que el diagrama sea Mermaid para que GitHub lo dibuje.

**Respuesta obtenida.** Un modelo de seis tablas: `USUARIO`, `EQUIPO`, `ORDEN`, `ORDEN_ITEM`, `GUIA` y `CAMBIO`, más el diagrama Mermaid y las tablas de ejemplo.

**Qué se aceptó y qué se corrigió.**
- Aceptado: separar `ordenes` del MVP en `ORDEN` y `ORDEN_ITEM`, porque hoy el folio, el tipo y la modalidad se repiten en cada SKU.
- Aceptado: agregar `USUARIO` y `GUIA`, que el Avance 2 menciona (cuentas y permisos, guía en PDF) y que el MVP aún no guarda.
- Corregido: en el MVP `ordenes.sku` no está declarada como clave externa hacia `inventario`; en el modelo nuevo sí lo es (`ORDEN_ITEM.sku` → `EQUIPO.sku`).
- Corregido: `CAMBIO` tiene dos claves externas hacia `EQUIPO` (`sku_original` y `sku_nuevo`); se dejó explícito en la tabla de cardinalidad.
- Corregido: `pdf_url` y `motivo` quedaron como opcionales y cada uno tiene un ejemplo con el campo vacío, para no declarar obligatorio algo que queda vacío.

**Cómo se verificó.** Se comparó cada campo con las columnas reales de `src/app.py`. Se revisó fila por fila que los ejemplos no dejen vacío ningún campo obligatorio ni mezclen tipos. Se comprobó que cada clave externa de los ejemplos apunta a un registro que existe (por ejemplo, `id_usuario` 2 existe en `USUARIO`).
