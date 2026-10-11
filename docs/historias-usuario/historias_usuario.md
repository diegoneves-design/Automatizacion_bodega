# Historias de usuario

Grupo 6 · Automatizacion_bodega · Entrega 4

**Estado: Borrador. Hipótesis por validar con la entrevista real.**

Las historias H01 a H07 salen del caso de uso del Avance 2 (emisión automática de guía) y del borrador de trabajo del grupo. Todavía no se han contrastado con un jefe de bodega real, porque la entrevista real aún no se ha hecho. Si una historia no resulta ser un dolor real, se elimina o se cambia.

Dos usuarios: el **jefe de bodega** (principal) y el **encargado de mantenimiento** (secundario, carga el listado y pide los cambios).

Los criterios describen el comportamiento que se busca. El MVP actual no los cumple todos: en cada historia, la línea "En el MVP hoy" lo compara con `src/app.py` y la sección "En qué estado está" del README resume lo pendiente.

## Orden de prioridad

| Prioridad | Historia | Resumen |
|---|---|---|
| 1 | H01 | Cargar el listado de SKU de una orden |
| 2 | H02 | Validar cada SKU contra el inventario |
| 3 | H04 | Emitir la guía cuando la validación no tiene diferencias |
| 4 | H03 | Ver destacados los equipos cambiados a último minuto |
| 5 | H05 | Reemplazar un equipo de una orden a último minuto |
| 6 | H07 | Ver por qué una orden quedó bloqueada |
| 7 | H06 | Consultar el historial de cambios de una orden |

---

## H01 · Cargar el listado de SKU de una orden

**Como** encargado de mantenimiento, **quiero** cargar el listado de SKU de una orden, **para** que bodega no tenga que digitar los equipos a mano.

**Prioridad:** 1

**Criterios de aceptación**
- **Principal.** Dado que el encargado ingresó folio, tipo de movimiento y modalidad, cuando pega el listado y presiona Cargar, entonces ve "Orden cargada" con la cantidad de SKU.
- **Alternativo.** Dado que no ingresó ningún SKU, cuando presiona Cargar, entonces no se carga y se avisa que falta el listado de SKU.

**Revisión INVEST**
- **Independiente:** sí, porque es el punto de partida y no necesita otra historia.
- **Negociable:** sí, porque la forma de entrada (pegar o subir un archivo) puede cambiar según cómo llegue el listado hoy, y eso se confirma en la entrevista.
- **Valiosa:** sí, porque elimina la digitación manual, que es el problema central del Avance 2.
- **Estimable:** sí, porque el MVP ya tiene una vista equivalente.
- **Pequeña:** sí, porque es una pantalla y una acción.
- **Comprobable:** sí, porque se prueba con un listado válido y con uno vacío.

**En el MVP hoy:** existe la vista "Carga masiva" (folio, tipo, modalidad, pegar o subir archivo). Con el listado vacío el botón queda deshabilitado, sin mensaje.

---

## H02 · Validar cada SKU contra el inventario

**Como** jefe de bodega, **quiero** validar cada SKU contra el inventario, **para** detectar antes de despachar los equipos que no existen o no tienen stock.

**Prioridad:** 2

**Criterios de aceptación**
- **Principal.** Dado que la orden tiene listado, cuando el jefe de bodega presiona Validar, entonces ve cada SKU como OK o con su motivo.
- **Alternativo.** Dado que algún SKU no existe, cuando se valida, entonces la orden queda bloqueada y no se puede emitir la guía.

**Revisión INVEST**
- **Independiente:** parcial, porque necesita una orden cargada (H01).
- **Negociable:** sí, porque qué se muestra por SKU (motivo, descripción, estado) puede ajustarse.
- **Valiosa:** sí, porque evita despachar un equipo que no existe o no está disponible.
- **Estimable:** sí, porque el MVP ya cruza el listado con el inventario.
- **Pequeña:** sí, porque es una sola validación.
- **Comprobable:** sí, porque se prueba con un SKU válido, uno inexistente y uno sin stock.

**En el MVP hoy:** el Validador marca cada SKU como `OK`, `SIN STOCK DISPONIBLE` o `SKU NO EXISTE EN INVENTARIO` y permite descargar el CSV. No bloquea la orden.

---

## H04 · Emitir la guía cuando la validación no tiene diferencias

**Como** jefe de bodega, **quiero** emitir la guía automáticamente cuando la validación no tiene diferencias, **para** respaldar el movimiento sin volver a digitar.

**Prioridad:** 3

**Criterios de aceptación**
- **Principal.** Dado que todos los SKU quedaron OK, cuando presiona Emitir guía, entonces ve la guía con su número y puede descargarla.
- **Alternativo.** Dado que la orden está bloqueada, cuando intenta emitir, entonces no se genera y se indica qué SKU corregir.

**Revisión INVEST**
- **Independiente:** no, porque depende de H02: sin validación no se sabe si se puede emitir.
- **Negociable:** sí, porque el formato de la guía (texto o PDF) se puede discutir.
- **Valiosa:** sí, porque deja el respaldo formal del movimiento sin digitar.
- **Estimable:** parcial, porque falta definir el formato final y si la guía se integra con el sistema de facturación, lo que está por validar.
- **Pequeña:** sí, si se limita a emitir y descargar.
- **Comprobable:** sí, porque se prueba con una orden sin diferencias y con una bloqueada.

**En el MVP hoy:** la guía se genera en texto plano al cargar la orden y se puede descargar. No tiene número de guía, no es PDF y se emite aunque algún SKU no valide.

---

## H03 · Ver destacados los equipos cambiados a último minuto

**Como** jefe de bodega, **quiero** ver destacados los equipos cambiados a último minuto con su fecha y hora, **para** saber qué cambió sin revisar la orden completa.

**Prioridad:** 4

**Criterios de aceptación**
- **Principal.** Dado que mantenimiento reemplazó un equipo, cuando el jefe abre el detalle, entonces ve el equipo destacado con fecha, hora y responsable.
- **Alternativo.** Dado que no hubo cambios, cuando abre el detalle, entonces no aparece ningún destacado.

**Revisión INVEST**
- **Independiente:** parcial, porque los cambios nacen en H05 y se muestran en la validación (H02).
- **Negociable:** sí, porque la forma de destacar (color, texto, ícono) se puede elegir.
- **Valiosa:** sí, porque el caso de uso del Avance 2 pide destacar los cambios de último minuto con fecha y hora.
- **Estimable:** sí, porque el registro de cambios ya existe.
- **Pequeña:** sí, porque es una marca visual sobre datos que ya se guardan.
- **Comprobable:** sí, porque se prueba con una orden con cambios y otra sin cambios.

**En el MVP hoy:** el Validador no destaca los cambios. Los cambios se ven solo en el registro de la vista "Ajuste de última hora".

---

## H05 · Reemplazar un equipo de una orden a último minuto

**Como** encargado de mantenimiento, **quiero** reemplazar un equipo de una orden a último minuto, **para** que la guía refleje lo que sale y el cambio quede con responsable.

**Prioridad:** 5

**Criterios de aceptación**
- **Principal.** Dado que hay un equipo no disponible, cuando reemplaza el SKU y confirma, entonces la orden queda con el nuevo equipo y el cambio queda registrado.
- **Alternativo.** Dado que el SKU nuevo no existe, cuando confirma, entonces se rechaza y se mantiene el equipo original.

**Revisión INVEST**
- **Independiente:** parcial, porque necesita una orden cargada (H01).
- **Negociable:** sí, porque quién puede autorizar el cambio se define con la entrevista.
- **Valiosa:** sí, porque evita rehacer la guía a mano cuando cambia un equipo.
- **Estimable:** sí, porque el MVP ya tiene esta vista.
- **Pequeña:** sí, porque es un reemplazo por vez.
- **Comprobable:** sí, porque se prueba con un SKU nuevo válido y con uno inexistente.

**En el MVP hoy:** la vista "Ajuste de última hora" reemplaza el SKU, archiva el original y registra responsable, fecha y hora (el motivo es opcional). El SKU nuevo se elige de la lista del inventario, así que no se puede escribir uno inexistente.

---

## H07 · Ver por qué una orden quedó bloqueada

**Como** encargado de mantenimiento, **quiero** ver por qué una orden quedó bloqueada, **para** corregir el SKU sin depender de que bodega me avise.

**Prioridad:** 6

**Criterios de aceptación**
- **Principal.** Dado que la orden quedó bloqueada, cuando el encargado abre su orden, entonces ve los SKU con problema y el motivo.
- **Alternativo.** Dado que el usuario no cargó esa orden, cuando intenta abrirla, entonces no se le muestra.

**Revisión INVEST**
- **Independiente:** no, porque depende de H02 (el bloqueo) y de cuentas y permisos, que están pendientes.
- **Negociable:** sí, porque cómo se avisa y qué se ve puede cambiar.
- **Valiosa:** parcial, porque es hipótesis que mantenimiento hoy no sabe en qué estado queda su orden; se confirma en la entrevista.
- **Estimable:** parcial, porque requiere un manejo de usuarios que todavía no está definido.
- **Pequeña:** sí, porque es una vista de lectura.
- **Comprobable:** sí, porque se prueba con una orden bloqueada y con la de otro usuario.

**En el MVP hoy:** no existe. No hay cuentas ni permisos, y el Validador muestra los problemas de cualquier folio.

---

## H06 · Consultar el historial de cambios de una orden

**Como** jefe de bodega, **quiero** consultar el historial de cambios de una orden, **para** reconstruir quién cambió qué equipo y cuándo.

**Prioridad:** 7

**Criterios de aceptación**
- **Principal.** Dado que la orden tuvo cambios, cuando abre el historial, entonces ve la lista por fecha con el equipo anterior, el nuevo, la fecha, la hora y el responsable.
- **Alternativo.** Dado que la orden no tuvo cambios, cuando abre el historial, entonces ve "Sin cambios registrados".

**Revisión INVEST**
- **Independiente:** no, porque depende de H05: sin cambios no hay historial.
- **Negociable:** sí, porque el orden y los filtros se pueden ajustar.
- **Valiosa:** parcial, porque sirve para auditar y reconstruir; cuánto se usa en la práctica se confirma en la entrevista.
- **Estimable:** sí, porque el MVP ya guarda el registro.
- **Pequeña:** sí, porque es una lista de lectura.
- **Comprobable:** sí, porque se prueba con una orden con cambios y otra sin cambios.

**En el MVP hoy:** la vista "Ajuste de última hora" muestra el registro de todos los folios juntos, del más reciente al más antiguo, y dice "Sin cambios registrados todavía" si está vacío. No se filtra por orden.

---

## Historias candidatas (sin validar)

**Estado: sin validar.** Estas historias salieron de un ensayo de entrevista con personajes ficticios, no de un usuario real. Son hipótesis: se validarán con la entrevista real y, si resultan ser un dolor real, se les asignará prioridad y criterios. Hasta entonces no tienen ni uno ni otro.

- **H08.** **Como** bodeguero, **quiero** marcar cada línea como verificada al cargar, **para** dejar constancia del doble control.
- **H09.** **Como** jefe de bodega, **quiero** registrar accesorios sin código por tipo y cantidad, **para** evitar reclamos.
- **H10.** **Como** jefe de bodega, **quiero** adjuntar una foto de la carga a la orden, **para** tener respaldo.
- **H11.** **Como** jefe de bodega, **quiero** ver las órdenes del día ordenadas por hora de salida, **para** priorizar en los peaks.
- **H12.** **Como** jefe de bodega, **quiero** comparar un retiro contra el despacho original, **para** detectar faltantes.
- **H13.** **Como** persona del área comercial, **quiero** ver el estado de una orden sin llamar a bodega, **para** informar al cliente.
- **H14.** **Como** persona de planificación de mantenimiento, **quiero** saber si bodega vio mi cambio, **para** no quedar esperando.
- **H15.** **Como** jefe de bodega, **quiero** que el sistema acepte listados desordenados y los limpie, **para** no frenar las urgencias.
