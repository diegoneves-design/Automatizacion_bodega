# Análisis del inventario real de la bodega

Estado: **borrador de la etapa de carga (2026-11-15).** Los hallazgos de la sección 5 salen de los totales del importador. Los gráficos del tablero y las demás cifras se agregarán cuando exista el tablero.

Este documento explica cómo se pasó el Excel de la bodega a la base de datos, qué supuestos se hicieron y qué falta confirmar. **No contiene SKU, descripciones de equipos ni textos de ubicación**: el Excel y todo lo generado con datos reales viven solo en `datos_locales/`, que Git ignora.

## 1. Fuente y método

- Archivo del Excel de Oscar con tres hojas, que no se copia ni se versiona (`*.xlsx` y `datos_locales/` están en `.gitignore`):
  - `AFO`: 1.617 equipos (SKU, N.º, descripción, familia, ubicación). Sin SKU repetidos.
  - `AF Extensiones eléctricas`: 319 extensiones con corriente y largo. No trae estado.
  - `Detalle Familias`: catálogo de 30 prefijos con su categoría.
- `herramientas/importar_inventario.py` lee el Excel (ruta por argumento) y escribe en `datos_locales/` los SQL de carga (máximo 300 equipos por archivo) y `reporte_calidad.json` (solo totales).
- Los equipos reales llevan `id_equipo` desde 1000, en el orden de su SKU. Los equipos de demo (501 a 507) no se tocan; si un SKU real coincidiera con uno de demo, el importador se detiene con un mensaje.
- Cada carga actualiza por SKU (`on conflict (sku) do update`), así que se puede repetir sin duplicar. Si el Excel cambia y entran SKU nuevos, los números de `id_equipo` pueden correrse y la carga fallaría por clave repetida en lugar de pisar datos; en ese caso hay que hablar antes de volver a cargar.
- La **familia** es el prefijo de dos letras del SKU (coincide con la columna Familia en las 1.617 filas). La **categoría** sale del catálogo.
- La **capacidad** (`capacidad_valor` y `capacidad_unidad`) se lee con expresiones regulares desde la descripción: BTU/H (con `MBTUH` como miles de BTU/H), TR, m³/h y kW. El punto con tres cifras detrás se entiende como separador de miles (`14.000`) y los demás como decimales (`7.5`, `3,3`).

## 2. Cómo se interpretó la columna Ubicación (supuesto a confirmar)

La hoja AFO no tiene una columna de estado: el estado del equipo se dedujo de la ubicación. Antes de comparar se recortan los espacios y se pasa a mayúsculas, sin distinguir tildes.

| Valor en Ubicación | Estado | Lugar | `situacion_origen` | Equipos |
|---|---|---|---|---|
| BODEGA | disponible | bodega | BODEGA | 860 |
| BODEGA LOS ANGELES | disponible | bodega | BODEGA LOS ANGELES | 36 |
| SHOWROOM | disponible | bodega | SHOWROOM | 3 |
| REPARACIÓN | en mantención | taller | REPARACIÓN | 195 |
| BAJA | fuera de servicio | bodega | BAJA | 194 |
| POR HABILITAR | fuera de servicio | bodega | POR HABILITAR | 72 |
| EN BUSCA | fuera de servicio | bodega | EN BUSCA | 12 |
| FUERA DE NORMA | fuera de servicio | bodega | FUERA DE NORMA | 2 |
| Un número (parece un contrato u orden) | arrendado | cliente | CONTRATO | 231 |
| Cualquier otro texto (nombres de personas o lugares) | arrendado | cliente | CLIENTE | 12 |

Del texto que no coincide con ninguna regla **no se guarda nada**: la base solo recibe la etiqueta `CLIENTE`. Una ubicación vacía detiene el importador (hoy no hay ninguna).

Resultado por estado: 899 disponibles (55,6 %), 243 arrendados (15,0 %), 195 en mantención (12,1 %) y 280 fuera de servicio (17,3 %).

## 3. Calidad de los datos

| Aspecto | Resultado | Qué se hizo |
|---|---|---|
| Categoría: `VENTILACIÓN` y `VENTILACION` | Dos escrituras de la misma categoría | Se unifican en `VENTILACIÓN` |
| Prefijos sin categoría en el catálogo (HU, PA, SF, TI) | 8 equipos | Quedan como `SIN CATEGORÍA` |
| Prefijo VT presente en equipos y ausente del catálogo | 2 equipos | También `SIN CATEGORÍA` (10 equipos sin categoría en total) |
| Prefijos del catálogo sin equipos (SA, SB, SC, SD, SP, SS) | 6 prefijos | Sin efecto; SD corresponde a las extensiones |
| Capacidad no extraída de la descripción | 377 de 1.617 equipos | Quedan en `null` |
| Capacidad extraída | 640 en BTU/H, 517 en m³/h, 66 en kW, 17 en TR | |
| Extensiones con SKU de formato no estándar | 65 de 319 | Se cargan igual; solo se cuentan |
| Extensiones con largo que no se puede convertir a número | 0 de 319 | El largo mezclaba números y texto (`20`, `'20'`, `'07'`); se convierten a entero |

Entre las familias con capacidad extraída en al menos 15 equipos, solo AC mezcla dos unidades: BTU/H (302 equipos) y TR (17). Eso se resolverá al hacer el gráfico de capacidad.

## 4. Lo que se agregó a la base

- `supabase/inventario.sql`: columnas `familia`, `categoria`, `situacion_origen`, `capacidad_valor` y `capacidad_unidad` (todas opcionales, con restricciones de valores) y la tabla `extensiones_electricas`, con lectura abierta igual que el resto (sin escritura directa).
- `reiniciar_demo()` ahora también restaura los equipos de demo 501 a 507 y **no toca los equipos con id desde 1000**.
- `seed_poc.sql` se detiene si ya existen equipos con id desde 1000, porque borra todos los equipos.

## 5. Primeras lecturas (con los totales del importador)

- El 56 % del inventario está disponible, el 15 % arrendado, el 12 % en reparación y el 17 % fuera de servicio.
- Tres familias concentran el inventario: EC (653), AP (339) y AC (332) suman 1.324 equipos, el **82 %** del total (la cifra preliminar del equipo era 83 %; el cálculo da 81,9 %).
- Tasa de arriendo por familia: AC 27,7 %, AP 11,8 % y EC 9,0 %.
- Hay 72 equipos «por habilitar» (candidatos a recuperarse) y 195 en reparación.

Pendiente de calcular con el tablero: el modelo más repetido y su participación (depende de cómo se defina «modelo» a partir de la descripción), la mediana de largo por corriente y la lectura con filtros.

## 6. Limitaciones

- El estado «arrendado» es un **supuesto**: un valor numérico (o un nombre) en Ubicación se interpreta como un equipo en poder de un cliente.
- No hay fechas ni historial: no se puede medir rotación ni tiempo de arriendo.
- Es una foto de un momento, no una serie.
- Fuera de servicio incluye bajas definitivas y equipos recuperables.
- La capacidad se extrajo de descripciones escritas a mano y puede faltar o estar mal leída.
- Los equipos de demo (501 a 507) conviven con los reales en la misma tabla.

## 7. Preguntas para Oscar o el jefe de bodega

1. ¿Es correcto que un valor numérico en Ubicación signifique «arrendado»? ¿Qué número es (contrato, orden, guía)?
2. ¿Qué significa exactamente POR HABILITAR? ¿Son equipos que se pueden recuperar?
3. ¿BAJA es definitiva, o un equipo dado de baja puede volver?
4. ¿Puede mostrarse el inventario real en una demo pública, o solo con datos de ejemplo?

## 8. Nota de riesgo

La política de lectura de la prueba de concepto es abierta y la clave pública está en el sitio publicado. Quien tenga esa clave puede leer los equipos reales (SKU y descripciones; no hay nombres de personas porque el importador no los guarda). Está aceptado para la prueba de concepto y queda pendiente confirmarlo con Oscar. Antes de un uso real hay que agregar inicio de sesión y cerrar las políticas por rol.

## 9. Orden de ejecución en Supabase

Lo ejecuta Bastián en el editor SQL; la IA no toca Supabase.

1. (Solo si todavía falta) `supabase/seed_poc.sql` con los RUT nuevos y `select public.reiniciar_demo();`. **Debe ir antes de cargar el inventario**: después de la carga, `seed_poc.sql` se detiene a propósito.
2. `supabase/inventario.sql`
3. `supabase/funciones.sql` (trae la nueva `reiniciar_demo`)
4. `datos_locales/carga_inventario_01.sql` a `carga_inventario_06.sql`, uno por uno
5. `datos_locales/carga_extensiones.sql`
6. Verificación:

```sql
select
  (select count(*) from public.equipos where id_equipo >= 1000) as equipos_reales,        -- debe dar 1617
  (select count(*) from public.extensiones_electricas)          as extensiones,           -- debe dar 319
  (select count(*) from public.equipos where id_equipo between 501 and 507) as equipos_demo; -- debe dar 7
```

Después de verificar, `select public.reiniciar_demo();` y una nueva consulta de equipos con id desde 1000 (debe seguir dando 1617).
