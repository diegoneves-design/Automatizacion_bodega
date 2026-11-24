# Línea base: cómo se hace hoy una guía a mano

Grupo 6 · Automatizacion_bodega

El indicador de éxito del proyecto (Avance 2) es el **porcentaje de guías emitidas sin errores ni reprocesos**, pero hoy no sabemos cuánto vale. El README lo deja pendiente: medir cuánto demoran hoy las guías y cuántas se rehacen. Sin esa medida no se puede decir que la prueba de concepto mejora algo. Este documento deja escrito **cómo se mide**, antes de medir.

No reemplaza la entrevista (`docs/entrevistas/`), que son cifras que contó una persona de memoria («de 10 a 15 minutos», «al menos dos cambios por semana»). Aquí se **cronometra y se cuenta** con guías reales.

## 1. Quién mide, a quién y qué no se guarda

- **Quién mide.** Una persona del equipo, junto al jefe de bodega o a alguien de su mismo cargo en otra empresa del rubro. Quien mide observa y cronometra; no ayuda ni corrige.
- **Qué se observa.** El proceso de armar la guía, no a la persona. Se le dice así antes de empezar.
- **Qué no se guarda.** Nombres de personas, nombres de clientes, números reales de orden o de guía, correos ni teléfonos. Cada guía medida es un código (M01, M02…) y en las observaciones se escribe «el cliente», «el supervisor», no sus nombres. La herramienta de cálculo se niega a leer filas que parezcan llevar un correo o un teléfono.
- **Dónde queda el archivo.** El CSV con mediciones reales **no se sube al repositorio**: se guarda en la carpeta del curso en Drive (acceso restringido) o en `datos-medicion/`, que git ignora. Al repositorio solo llega el resumen de la sección 6.
- **Permiso.** Si la empresa pide una autorización formal, se pide al profesor el certificado que acredita el carácter académico de la actividad (indicando la organización y la persona a quien se dirige), igual que para la prueba de usuarios.

## 2. Qué se mide en cada guía

Una **guía medida** es una guía de despacho o de retiro armada a mano en el ERP a partir del listado que llegó, con su cronómetro. Una fila del CSV por guía.

| Columna | Qué se anota | Cómo se mide |
|---|---|---|
| `id_medicion` | Código de la medición | M01, M02… en el orden en que se miden |
| `fecha` | Día de la medición | AAAA-MM-DD |
| `tipo_movimiento` | `despacho` o `retiro` | El de la guía |
| `n_productos` | Cantidad de productos de la guía | Contar las líneas de la guía final (de 1 a 60, el máximo del ERP) |
| `tiempo_armado` | Tiempo de armado | Cronómetro en `mm:ss` (por ejemplo `12:30`). **Empieza** cuando la persona abre el listado y comienza a armar. **Termina** cuando la guía queda emitida en el ERP. Se **pausa** mientras espera una respuesta de otra área o atiende otra cosa, y eso se anota en observaciones |
| `n_cambios_ultimo_minuto` | Cambios de último minuto de esa orden | Cuántos cambios llegaron para esa orden después de empezar a armar la guía y antes del despacho, venga de la persona o del área que venga. Puede ser 0 |
| `error_detectado` | `si` o `no` | Si se detectó algún error en la guía (un SKU mal escrito, una cantidad, una descripción) en cualquier momento antes del despacho, **aunque se haya corregido sin rehacer la guía** |
| `se_rehizo` | `si` o `no` | Si hubo que volver a armar o volver a emitir la guía, completa o en parte, antes del despacho |
| `causa` | Una de la lista de abajo | Solo si `error_detectado` o `se_rehizo` es `si`; si ambos son `no`, se deja vacía |
| `observaciones` | Texto corto, sin nombres | Pausas, accesorios genéricos, algo raro de esa guía |

**Causas** (lista cerrada, para poder contarlas):

| Causa | Cuándo se usa |
|---|---|
| `sku_mal_digitado` | Un código escrito mal o que no existe |
| `cambio_ultimo_minuto` | Un área pidió cambiar un equipo cuando la guía ya estaba en curso o emitida |
| `producto_sin_stock` | Un equipo que no estaba disponible |
| `cantidad_incorrecta` | La cantidad de un producto no coincidía |
| `datos_del_cliente` | Un dato del cliente o de la orden estaba mal |
| `otro` | Cualquier otra, explicada en observaciones |

Si una guía tuvo más de una causa, se anota la que más pesó y las otras en observaciones.

## 3. Cuántas mediciones

- **Mínimo: 5 guías.** Es lo que pide el protocolo, y la herramienta avisa si hay menos.
- **Mejor: 10**, y que entre ellas haya al menos un retiro y una guía de más de 30 productos.
- **Cómo se eligen.** Las **siguientes guías que se armen**, en orden, sin escoger las fáciles ni las difíciles. Elegirlas sería hacer trampa a favor de la solución.
- **Temporada.** La bodega tiene temporada alta (más guías y más cambios). Se anota la fecha de cada medición para poder decir, al informar, en qué época se midió.

## 4. Paso a paso

1. **Antes.** Explicar a la persona que se mide el proceso y no a ella, que no se anotan nombres y que puede pedir parar cuando quiera. Tener el cronómetro y el CSV (`docs/plantillas/linea_base_registro.csv`) abiertos.
2. **Durante cada guía.** Poner el cronómetro cuando abre el listado. Pausarlo en las esperas. Anotar en una hoja, sin interrumpir, cada error que aparezca y cada cambio que llegue. Pararlo cuando la guía queda emitida.
3. **Después de cada guía.** Preguntar solo hechos: «¿hubo que rehacerla?», «¿por qué?», «¿llegó algún cambio mientras la armaba?». No sugerir respuestas.
4. **Al terminar.** Completar la fila de cada guía el mismo día, mientras se recuerda, y guardar el CSV fuera del repositorio.
5. **Calcular.** Desde la raíz del repositorio:
   ```
   py herramientas/calcular_linea_base.py datos-medicion/linea_base.csv
   py herramientas/calcular_linea_base.py datos-medicion/linea_base.csv --md
   ```
   La segunda forma imprime la tabla «Antes» lista para pegar en la sección 6.

## 5. El indicador, definido exactamente

> **Porcentaje de guías emitidas sin errores ni reprocesos** = (guías con `error_detectado = no` **y** `se_rehizo = no`) ÷ (guías medidas) × 100

- Se cuenta **por guía**, no por producto: una guía de 50 productos con un solo SKU mal escrito cuenta como una guía con error.
- Una guía que se rehizo **no cumple**, aunque la segunda versión salga perfecta.
- Una guía con un error que se corrigió sin rehacerla **tampoco cumple** (`error_detectado = si`).
- Un cambio de último minuto que obligó a rehacer la guía **no cumple** (`se_rehizo = si`, `causa = cambio_ultimo_minuto`). Un cambio que se absorbió antes de emitir, sin error ni rehacer, **sí cumple**, pero queda contado en `n_cambios_ultimo_minuto`.
- Con pocas guías el porcentaje salta mucho (con 5, cada guía vale 20 puntos). Se informa siempre junto al número de guías: «60 % (3 de 5)», nunca solo «60 %».

Otras cifras que calcula la herramienta: mediana del tiempo de armado (la mediana, no el promedio, porque una guía muy larga distorsiona el promedio), segundos por producto, porcentaje de guías rehechas, cambios de último minuto por guía y las causas más frecuentes.

## 6. Resultados: antes y con la prueba de concepto

**Antes (a mano).** Se completa con la salida de `--md`. Hoy está vacía porque todavía no se midió.

| Indicador | Antes (a mano) | Con la prueba de concepto | Cómo se obtiene «con la prueba de concepto» |
|---|---|---|---|
| Guías medidas | | | Participantes de la prueba de usuarios que completan la tarea |
| Tiempo por guía (mediana) | | | Minutos de la tarea 1 en la planilla de la prueba (`docs/kit-prueba/planilla_registro.csv`) |
| Guías rehechas | | | Personas que tuvieron que volver atrás para cumplir la tarea |
| Guías emitidas sin errores ni reprocesos | | | Personas que completan la tarea 2 sin ayuda y detectan solas el SKU inexistente |
| Cambios de último minuto por guía | | | La tarea 2 trae un cambio: no se mide con la prueba de concepto, se declara |
| Causas más frecuentes | | | Lo que anota la planilla de la prueba como «entorpece» o «bloquea» |

**Por qué esta comparación es orientativa y no una prueba de que mejora.**
- La prueba de concepto no emite la guía oficial: la guía se sigue emitiendo en el ERP. Lo que se compara es **armar y validar** el pedido, no todo el proceso.
- En la prueba de usuarios cada persona trabaja con pedidos de 4 productos y datos de ejemplo, y las guías reales tienen decenas. El tiempo por producto sirve más que el tiempo total.
- La persona de la prueba usa la herramienta por primera vez; a mano lleva años de práctica.
- Son muestras de 5 o 10: sirven para ver un orden de magnitud y para decidir qué corregir, no para dar un porcentaje preciso.

## 7. Qué falta

Todo lo anterior está **escrito, no ejecutado**. Falta hacer las mediciones con el jefe de bodega o alguien de su mismo cargo, completar el CSV, correr la herramienta y pegar la tabla «Antes». Cuando eso pase, se actualiza la fila correspondiente del README.
