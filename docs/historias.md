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

## HU-03 · Registrar un cambio de último minuto

Como supervisor de mantenimiento, comercial u operaciones, quiero registrar en el sistema el cambio de un equipo de una orden, para que bodega se entere sin depender de una llamada o un WhatsApp.

## HU-04 · Ver los cambios destacados

Como jefe de bodega, quiero ver destacado qué equipo cambió, quién lo cambió y a qué hora, para corregir solo esa línea de la guía y tener respaldo cuando la gente sale más tarde de lo esperado.

## HU-05 · Dejar lista la guía

Como jefe de bodega, quiero que la guía quede lista con los productos validados, para pasarla al ERP sin volver a digitarlos.

Wireframes: ver [docs/wireframes/](wireframes/)
