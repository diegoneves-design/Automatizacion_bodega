# Análisis del inventario real de la bodega

Estado: **borrador (2026-11-15).** La carga del inventario ya se ejecutó en Supabase y el Dashboard está construido; falta verlo en la página publicada y confirmar los supuestos con la bodega.

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
- `supabase/dashboard.sql`: la función `inventario_dashboard()` que alimenta el Dashboard (solo lectura; ver la sección 9).

## 5. Primeras lecturas (con los totales del importador)

- El 56 % del inventario está disponible, el 15 % arrendado, el 12 % en reparación y el 17 % fuera de servicio.
- Tres familias concentran el inventario: EC (653), AP (339) y AC (332) suman 1.324 equipos, el **82 %** del total (1.324 de 1.617 = 81,9 %).
- Tasa de arriendo, solo familias con 30 o más equipos (son siete): SE 51,6 %, CI 32,6 %, AC 27,7 %, VA 16,7 %, AP 11,8 %, EC 9,0 % y CE 6,3 %; el promedio general es 15,0 %. Se usa el límite de 30 porque con menos equipos un solo arriendo cambia mucho el porcentaje.
- Hay 72 equipos «por habilitar» (candidatos a recuperarse) y 195 en reparación.

- Modelo más repetido: un solo modelo reúne 362 equipos, el 22,4 % del total (ver la regla de agrupación abajo). Los 10 modelos más repetidos suman 51,8 % del total.
- Extensiones: la corriente más común es 63A (131 de 319, 41 %) y la mayoría mide 10 o 20 m.

### Regla de agrupación por modelo (gráfico 6, Pareto)

El Excel no tiene una columna de modelo. Se toma como **modelo la primera palabra (letras, números y guion) que sigue a la palabra «MODELO» en la descripción**, en mayúsculas. Así, todas las descripciones que nombran el mismo modelo se suman, aunque difieran en la marca, el caudal u otros datos: el modelo mayor reúne 3 variantes de descripción y 362 equipos.

- 1.477 equipos traen la palabra «modelo» y se agrupan en 179 modelos distintos.
- 140 equipos no la traen: no entran al ranking de los diez primeros, pero sí al total sobre el que se calcula el % acumulado.
- Limitación: dos productos distintos con el mismo código de modelo se contarían juntos. La regla vive en `extraerModelo` (`prototipo/js/filtros.js`) y está probada con descripciones ficticias.

### Capacidad por familia (gráfico 11)

Cada vista usa **una sola unidad** y deja elegir entre BTU/H, m³/h y kW; solo aparecen las familias con 15 o más equipos con capacidad en esa unidad. En la vista BTU/H, los equipos con capacidad en TR se convierten con **1 TR = 12.000 BTU/H** y la nota del gráfico dice cuántos se convirtieron (17 con los datos de hoy, todos de la familia AC). La nota también declara cuántos equipos quedaron sin capacidad extraída (377), cuántos tienen otra unidad y cuántos están en familias con menos de 15 equipos.

### Tasa de arriendo (gráfico 3)

Se muestran solo las familias con 30 o más equipos (siete con los datos de hoy). Con menos, el porcentaje es poco confiable. El criterio está escrito en la nota del gráfico.

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
   **Respondida el 24 de noviembre de 2026 por Oscar: sí, el inventario real puede mostrarse en el Dashboard público.** Sigue fuera de lo público todo dato personal de clientes (RUT, dirección, correo y teléfono): `inventario_dashboard()` no los devuelve y los permisos de `clientes` no los exponen.

## 8. Nota de riesgo

La política de lectura de la prueba de concepto es abierta y la clave pública está en el sitio publicado. Quien tenga esa clave puede leer los equipos reales (SKU y descripciones; no hay nombres de personas porque el importador no los guarda). Oscar confirmó el 24 de noviembre de 2026 que el inventario real puede mostrarse en el Dashboard público (pregunta 4 de la sección 7), así que este riesgo queda aceptado. Lo que nunca se publica son los datos personales de clientes (RUT, dirección, correo y teléfono). Antes de un uso real hay que agregar inicio de sesión y cerrar las políticas por rol.

## 9. Dashboard

El Dashboard es una vista más del programa: aparece en el menú junto a Pedidos y desde él se vuelve a Pedidos. `prototipo/dashboard.html` carga una sola vez `inventario_dashboard()` (`supabase/dashboard.sql`) y filtra en memoria. El JSON con los datos reales pesa unos 236 KB.

- **Qué devuelve la función:** los equipos reales (id desde 1000) con solo nueve columnas (`id_equipo`, `sku`, `descripcion`, `familia`, `categoria`, `estado`, `situacion_origen`, `capacidad_valor`, `capacidad_unidad`), las extensiones (`sku`, `corriente`, `largo_m`) y la actividad del MVP (órdenes por estado y cambios por motivo). Nunca devuelve nombres de personas, correos, clientes ni textos libres: un motivo de cambio que no sea uno de los tres del prototipo se cuenta como «Otro».
- **Filtros:** clic en una barra, trozo, celda o área aplica el filtro; otro clic lo quita. Entre dimensiones los filtros se suman con «y» (familia AC y fuera de servicio); dentro de una dimensión, con «o» (familia AC o AP). Cada gráfico muestra todos los valores de su propio eje para poder cambiar la selección; los demás filtros sí lo afectan.
- **Extensiones:** son otra lista (no tienen estado), así que los filtros de equipos no las afectan; solo el de corriente.
- **Vistas por rol:** Jefe de bodega (todo), Mantención (en reparación y por habilitar) y Despacho (disponibles, ordenados por familia). Son solo filtros ya armados, no permisos.
- **Enlaces:** los filtros viajan en la dirección (`#estado=fuera_servicio&familia=AC`).
- **Gráfico 12:** la actividad del MVP viene de las órdenes de la demo y no depende de los filtros.
- **Mejora futura:** el detalle de un equipo no indica todavía si aparece en alguna orden del prototipo.
- **Biblioteca:** ECharts 5.5.1, copiada en `prototipo/js/vendor/` con un build propio (640 KB; el completo pesa 1,03 MB).

## 10. Orden de ejecución en Supabase

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

**Para el Dashboard** (después de la carga, no cambia ningún dato): ejecutar `supabase/dashboard.sql` y probar la función:

```sql
select jsonb_array_length(public.inventario_dashboard() -> 'equipos' -> 'filas') as equipos_en_el_dashboard;   -- debe dar 1617
select length(public.inventario_dashboard()::text) as caracteres_del_json;                                   -- unos 240.000 (menos de 600.000)
```

## 11. El Dashboard dentro del MVP (Streamlit): cómo activarlo

El mismo Dashboard de la sección 9 está también como vista del MVP, con el nombre «Dashboard». Se arma con los mismos archivos del prototipo (`prototipo/dashboard.html` entre sus marcadores, `filtros.js`, `graficos.js`, `dashboard.js`, ECharts y los estilos) más lo propio del MVP (`src/dashboard_incrustado/`: el entorno del iframe, el reemplazo de los datos y la distribución ancha). Lo que se corrija en los gráficos se corrige en las dos. El prototipo queda como está.

**Por qué viene apagado.** Muestra el inventario real (SKU, descripciones, estados), y el MVP no tiene inicio de sesión: quien tenga la dirección de la aplicación lo vería. **La pregunta 4 de la sección 7 («¿puede mostrarse el inventario real en una demo pública?») sigue abierta** con Oscar o el jefe de bodega. Hasta tener su respuesta, el hosting público debe dejar la vista apagada.

**Cómo se enciende y se apaga.** Con la variable de entorno `DASHBOARD_INVENTARIO`: solo el valor exacto `1` enciende la vista (vacía, ausente o cualquier otro valor la apaga: no aparece en el menú y `?vista=dashboard` no la abre).

| Dónde | Para encenderla | Para apagarla |
|---|---|---|
| Computador (tu `.env`) | `DASHBOARD_INVENTARIO=1` | borra la línea o déjala vacía |
| Hosting público | En el panel del servicio, agrega la variable de entorno `DASHBOARD_INVENTARIO` con valor `1` y reinicia el servicio | Quita la variable (o déjala vacía) y reinicia |

No es un secreto (no contiene claves), pero es una decisión sobre qué datos se muestran: cámbiala solo cuando la bodega lo haya autorizado, y anótalo aquí. `DATABASE_URL` sí es secreto y va solo en los secretos del hosting.

**De dónde salen los datos.** El servidor llama a `inventario_dashboard()` con el rol limitado `app_mvp` (el permiso lo da `supabase/mvp_rol.sql`) y los guarda en memoria 5 minutos; el botón «Actualizar datos» los vuelve a pedir. La función devuelve solo las nueve columnas de la sección 9 (sin personas, clientes ni textos libres). Los datos viajan dentro de la página y el navegador no usa la clave publicable.

**Lo que no cambia de la nota de riesgo (sección 8).** Con la vista encendida, quien llegue a la aplicación puede leer los equipos reales. Está aceptado solo mientras no se difunda la dirección más allá de quienes participan en la prueba.

