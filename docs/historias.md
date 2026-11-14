# Historias de usuario · Automatizacion_bodega

**Conversación:** subjefe de bodega de una empresa de arriendo de equipos, a cargo de la bodega durante 4 meses en total (cuando el jefe de bodega sale de vacaciones), 1 año y 4 meses en la empresa; 10 de octubre de 2026. Es integrante del equipo y respondió una pauta de 15 preguntas. Nos contó que:

- "Me cambian las cosas a último minuto, y las tres áreas: mantenimiento, comercial y operaciones". Pasa al menos dos veces a la semana, y unas siete en temporada alta; se entera "porque me llaman o me mandan un WhatsApp".
- "El error humano al anotar siempre está presente". En sus primeros meses digitó mal un SKU en una orden a Puerto Montt: "el mismo equipo salía en 3 órdenes distintas" y tuvo que hacer un inventario general de los evaporativos.
- "Ir anotando en papel es molesto: en temporada alta termino básicamente armándome un cuaderno".

Detalle completo de la conversación: [docs/entrevistas/entrevista_subjefe_bodega.md](entrevistas/entrevista_subjefe_bodega.md)

**Flujo principal:** el jefe de bodega carga el listado del pedido de venta (PV), lo valida contra el inventario y deja la guía lista para pasarla al ERP. **Historia principal:** HU-01

## HU-01 · Validar el pedido antes de hacer la guía

Como jefe de bodega, quiero validar los productos del pedido contra el inventario antes de hacer la guía, para no despachar un equipo mal digitado o que no está disponible.

- **Escenario principal.** Dado que todos los productos de la orden existen en el inventario y están disponibles, cuando el jefe de bodega presiona "Validar", entonces ve cada producto marcado en verde como "ok" y el botón "Preparar guía" habilitado.
- **Escenario alternativo.** Dado que un SKU del pedido está mal digitado y no existe en el inventario, cuando el jefe de bodega presiona "Validar", entonces ve ese SKU en rojo con el motivo "no existe", el mensaje "Corrige 1 producto para continuar" y el botón "Preparar guía" bloqueado.

## HU-02 · Cargar el listado del pedido de venta

Como jefe de bodega, quiero cargar de una vez el listado de productos del pedido de venta, para no digitar a mano hasta 60 productos por guía.

- **Escenario principal.** Dado que el jefe de bodega pegó un listado de entre 1 y 60 productos, cuando presiona "Cargar pedido", entonces ve "N productos detectados" y pasa a validar el pedido.
- **Escenario alternativo.** Dado que el listado está vacío o tiene más de 60 productos, cuando presiona "Cargar pedido", entonces ve junto al campo cómo corregirlo y no avanza.

## HU-03 · Registrar un cambio de último minuto

Como supervisor de mantenimiento, quiero registrar en el sistema el cambio de un equipo de una orden, para que bodega se entere sin depender de una llamada o un WhatsApp.

- **Escenario principal.** Dado que el supervisor de mantenimiento elige el equipo que sale y el que entra, cuando presiona "Guardar cambio", entonces vuelve a la validación con esa línea destacada, con quién lo cambió y a qué hora.
- **Escenario alternativo.** Dado que falta el equipo que entra, o es igual al que sale o ya está en el pedido, cuando presiona "Guardar cambio", entonces ve el error junto al campo y no se guarda nada.

## HU-04 · Ver los cambios destacados

Como jefe de bodega, quiero ver destacado qué equipo cambió, quién lo cambió y a qué hora, para corregir solo esa línea de la guía y tener respaldo cuando la gente sale más tarde de lo esperado.

- **Escenario principal.** Dado que hay un cambio registrado en la orden, cuando el jefe de bodega ve la validación, entonces la línea cambiada sale destacada con "Cambiado por X a las HH:MM" y la línea anterior se conserva como no vigente.
- **Escenario alternativo.** Dado que la orden no tiene cambios, cuando el jefe de bodega ve la validación, entonces ninguna línea sale destacada.

## HU-05 · Preparar la guía con los productos validados

Como jefe de bodega, quiero preparar la guía solo con los productos validados, para pasarla al ERP sin volver a digitarlos.

- **Escenario principal.** Dado que todos los productos están en verde, cuando el jefe de bodega presiona "Preparar guía", entonces ve la guía solo con las líneas vigentes y "Lista para pasar al ERP".
- **Escenario alternativo.** Dado que algún producto no validó, cuando el jefe de bodega está en la validación, entonces "Preparar guía" está bloqueado y no se llega a la guía.

Wireframes: ver [docs/wireframes/](wireframes/)
